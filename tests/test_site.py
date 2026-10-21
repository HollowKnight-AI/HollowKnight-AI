import importlib.util
import json
import re
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('build_site',ROOT/'tools/build_site.py')
site=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(site)


class SiteTests(unittest.TestCase):
    def setUp(self):
        parent=ROOT/'work'
        parent.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'site-assets').mkdir()
        for f in ('style.css','site.js'):
            (self.root/'site-assets'/f).write_text('',encoding='utf8')
        (self.root/'README.md').write_text('# 首页\n[文章](notes/test.md)',encoding='utf8')
        (self.root/'notes').mkdir()
        (self.root/'notes/test.md').write_text('# 测试文章\n[首页](../README.md)\n中文搜索内容',encoding='utf8')
        self.config={'repository':site.REPOSITORY,'pages':[{'source':'README.md','title':'首页'},{'source':'notes/test.md','title':'测试文章','published':'2026-10-21'}]}
        self.write_config()

    def write_config(self):
        (self.root/'site.json').write_text(json.dumps(self.config),encoding='utf8')

    def test_links_backlinks_search_and_feed(self):
        result=site.build(self.root)
        self.assertFalse(result['hosting_enabled'])
        home=(self.root/'docs/index.html').read_text(encoding='utf8')
        article=(self.root/'docs/notes/test.html').read_text(encoding='utf8')
        self.assertIn('href="notes/test.html"',home)
        self.assertIn('href="../index.html"',article)
        self.assertIn('哪些页面链接到这里',article)
        data=json.loads((self.root/'docs/search.json').read_text(encoding='utf8'))
        self.assertIn('中文搜索内容',data[1]['text'])
        feed=(self.root/'docs/feed.xml').read_text(encoding='utf8')
        self.assertIn('测试文章',feed)
        before={p.relative_to(self.root/'docs'):p.read_bytes() for p in (self.root/'docs').rglob('*') if p.is_file()}
        site.build(self.root)
        after={p.relative_to(self.root/'docs'):p.read_bytes() for p in (self.root/'docs').rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_refuses_private_repository(self):
        (self.root/'MEMORY.md').write_text('private',encoding='utf8')
        with self.assertRaises(ValueError):site.build(self.root)
        self.assertFalse((self.root/'docs').exists())

    def test_asset_updates_change_only_the_affected_asset_url(self):
        site.build(self.root)
        home=(self.root/'docs/index.html').read_text(encoding='utf8')
        css=lambda text:re.search(r'href="([^"]*style\.css\?v=[^"]+)"',text).group(1)
        js=lambda text:re.search(r'src="([^"]*site\.js\?v=[^"]+)"',text).group(1)
        before_css,before_js=css(home),js(home)
        (self.root/'site-assets/style.css').write_text('.travel-gallery{display:grid}',encoding='utf8')
        site.build(self.root)
        updated=(self.root/'docs/index.html').read_text(encoding='utf8')
        article=(self.root/'docs/notes/test.html').read_text(encoding='utf8')
        self.assertNotEqual(before_css,css(updated))
        self.assertEqual(before_js,js(updated))
        self.assertEqual('../'+css(updated),css(article))
        self.assertEqual('.travel-gallery{display:grid}',(self.root/'docs/style.css').read_text(encoding='utf8'))

    def test_refuses_escaping_or_unlisted_sources(self):
        for source in ('../private.md','metadata/records/a.md','MEMORY.md'):
            self.config['pages'][1]['source']=source
            self.write_config()
            with self.assertRaises(ValueError):site.build(self.root)
        self.assertFalse((self.root/'docs').exists())

    def test_refuses_private_links_before_output(self):
        (self.root/'notes/test.md').write_text('https://github.com/HollowKnight-AI/Life-Vault/blob/main/private.md',encoding='utf8')
        with self.assertRaises(ValueError):site.build(self.root)
        self.assertFalse((self.root/'docs').exists())


class DualHomeTests(unittest.TestCase):
    def setUp(self):
        import shutil
        parent=ROOT/'work'
        parent.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        shutil.copytree(ROOT/'site-assets/home',self.root/'site-assets/home')
        self.data=json.loads((ROOT/'site-home.json').read_text(encoding='utf8'))
        self.compiled={p['source']:p for p in json.loads((ROOT/'site.json').read_text(encoding='utf8'))['pages']}
        spec=importlib.util.spec_from_file_location('render_homes',ROOT/'tools/render_homes.py')
        self.homes=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.homes)

    def render(self):
        (self.root/'site-home.json').write_text(json.dumps(self.data,ensure_ascii=False),encoding='utf8')
        return self.homes.render(self.root,self.compiled)

    def test_two_distinct_structures_share_actual_data_and_upstream_css(self):
        out=self.render()
        self.assertIn('data-page="履历"',out['index.html'])
        self.assertNotIn('data-page="履历"',out['github.html'])
        self.assertIn('gh-project-grid',out['github.html'])
        self.assertIn('data-filter-item',out['index.html'])
        self.assertEqual(out['home-assets/vcard.css'],(ROOT/'vendor/vcard/assets/css/style.css').read_text(encoding='utf8'))
        for row in self.data['projects']:
            for name in ('index.html','github.html'):
                self.assertIn(row['url'],out[name])
        self.assertNotIn('Richard hanrick',out['index.html'])
        self.assertNotIn('1200%',out['index.html'])

    def test_one_data_revision_updates_both_views_and_escapes_markup(self):
        self.data['profile']['intro']='共享数据修订 <script>不可执行</script>'
        out=self.render()
        for name in ('index.html','github.html'):
            self.assertIn('共享数据修订 &lt;script&gt;',out[name])
            self.assertNotIn('<script>不可执行</script>',out[name])
        self.assertEqual(json.loads(out['home-data.json'])['profile']['intro'],self.data['profile']['intro'])

    def test_private_content_or_unpublished_link_cannot_enter_homepages(self):
        self.data['profile']['intro']='https://github.com/HollowKnight-AI/Life-Vault'
        with self.assertRaises(ValueError):self.render()
        self.data['profile']['intro']='公开简介'
        self.data['posts'][0]['url']='notes/not-published.html'
        with self.assertRaises(ValueError):self.render()


if __name__=='__main__':unittest.main()
