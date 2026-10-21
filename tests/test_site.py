import importlib.util
import json
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


if __name__=='__main__':unittest.main()
