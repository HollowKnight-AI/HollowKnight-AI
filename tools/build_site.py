#!/usr/bin/env python3
"""Build a public-only digital garden from an explicit list of public Markdown files."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from email.utils import format_datetime
import html
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import xml.etree.ElementTree as ET

import markdown

REPOSITORY = 'HollowKnight-AI/HollowKnight-AI'
BASE_URL = 'https://hollowknight-ai.github.io/HollowKnight-AI/'
ROOT_PAGES = {'README.md', 'ABOUT.md', 'NOW.md', 'PROJECTS.md', 'JOURNAL.md', 'AI_CONTEXT.md', 'WORK_WITH_ME.md', 'USE_WITH_AI.md', 'GUIDE.md', 'CHANGELOG.md', 'LICENSE.md'}


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, text):
        self.parts.append(text)


def valid_source(root, source):
    if not isinstance(source, str) or '\\' in source or source.startswith('/') or '..' in PurePosixPath(source).parts:
        raise ValueError('公开来源路径无效')
    if source not in ROOT_PAGES and not re.fullmatch(r'notes/[a-zA-Z0-9_-]+\.md', source):
        raise ValueError('来源不在公开文件范围：' + source)
    p = (root / source).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError('公开文件缺失或路径越界：' + source)
    return p


def output_name(source):
    return 'index.html' if source == 'README.md' else source.removesuffix('.md') + '.html'


def local_target(source, href, selected):
    if re.match(r'^[a-z][a-z0-9+.-]*:|^//|^#', href, re.I):
        return href, None
    path, _, anchor = href.partition('#')
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
    if target in selected:
        relative = posixpath.relpath(output_name(target), posixpath.dirname(output_name(source)) or '.')
        return relative + ('#' + anchor if anchor else ''), target
    return 'https://github.com/' + REPOSITORY + '/blob/main/' + target + ('#' + anchor if anchor else ''), None


def build(root, destination=None):
    root = Path(root).resolve()
    destination = (Path(destination) if destination else root / 'docs').resolve()
    if not destination.is_relative_to(root) or destination == root:
        raise ValueError('网站输出必须位于公开仓库的子目录内')
    if (root / 'MEMORY.md').exists() or (root / 'metadata/records').exists():
        raise ValueError('检测到私密档案结构；禁止在此处生成公开网站')
    config = json.loads((root / 'site.json').read_text(encoding='utf-8-sig'))
    if config.get('repository') != REPOSITORY:
        raise ValueError('网站只为指定的公开仓库构建')
    pages = config['pages']
    if not pages or len({p['source'] for p in pages}) != len(pages):
        raise ValueError('公开页面清单为空或有重复')
    selected = {p['source'] for p in pages}
    if 'README.md' not in selected:
        raise ValueError('公开页面需要首页')
    asset_versions = {name: hashlib.sha256((root / 'site-assets' / name).read_text(encoding='utf8').encode('utf8')).hexdigest()[:12] for name in ('style.css', 'site.js')}
    compiled, edges = {}, []
    for page in pages:
        source = page['source']
        raw = valid_source(root, source).read_text(encoding='utf-8-sig')
        if re.search(r'https?://github\.com/[^\s)]+/Life-Vault|github_pat_|gh[pousr]_[A-Za-z0-9]{20,}', raw, re.I):
            raise ValueError('公开正文含私人仓库入口或疑似凭据：' + source)
        body = markdown.markdown(raw, extensions=['tables', 'fenced_code', 'footnotes', 'toc', 'sane_lists'])
        def rewrite(match):
            href = html.unescape(match.group(1))
            new, target = local_target(source, href, selected)
            if target and target != source:
                edges.append({'source': source, 'target': target})
            return 'href="' + html.escape(new, quote=True) + '"'
        body = re.sub(r'href="([^"]+)"', rewrite, body)
        parser = PlainText()
        parser.feed(body)
        compiled[source] = dict(page, body=body, text=' '.join(parser.parts))
    writes = {}
    for source, page in compiled.items():
        depth = len(PurePosixPath(output_name(source)).parts) - 1
        prefix = '../' * depth
        nav = ''.join('<a' + (' class="active"' if p['source'] == source else '') + ' href="' + prefix + output_name(p['source']) + '">' + html.escape(p['title']) + '</a>' for p in pages)
        incoming = sorted({edge['source'] for edge in edges if edge['target'] == source})
        backlinks = '<section class="backlinks"><h2>哪些页面链接到这里</h2>' + (''.join('<a href="' + prefix + output_name(s) + '">' + html.escape(compiled[s]['title']) + '</a>' for s in incoming) or '<p>暂时没有其他页面链接到这里。</p>') + '</section>'
        graph = '<section class="connections"><h2>档案之间的联系</h2><div id="graph"></div></section>' if source == 'README.md' else ''
        template = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="王鑫烨的公开个人档案、学习与思考"><title>' + html.escape(page['title']) + ' · 王鑫烨</title><link rel="stylesheet" href="' + prefix + 'style.css?v=' + asset_versions['style.css'] + '"><link rel="alternate" type="application/rss+xml" title="公开记录" href="' + prefix + 'feed.xml"><script defer src="' + prefix + 'site.js?v=' + asset_versions['site.js'] + '" data-prefix="' + prefix + '"></script></head><body><aside><p class="eyebrow">AN OPEN NOTEBOOK</p><a class="brand" href="' + prefix + 'index.html">王鑫烨<span>理论物理 · AI · 记录</span></a><nav>' + nav + '</nav><a class="repo" href="https://github.com/' + REPOSITORY + '">GitHub ↗</a></aside><main><header><label>搜索公开档案<input id="search" type="search" placeholder="知识、文章、项目…"></label><a href="' + prefix + 'feed.xml">RSS ↗</a></header><div id="results" aria-live="polite"></div><article>' + page['body'] + '</article>' + backlinks + graph + '<footer>持续修改，逐步生长。<a href="https://github.com/' + REPOSITORY + '/blob/main/' + source + '">查看原文与修订历史 ↗</a></footer></main></body></html>'
        writes[output_name(source)] = template
    search = [{'source': s, 'title': p['title'], 'path': output_name(s), 'text': p['text']} for s,p in compiled.items()]
    writes['search.json'] = json.dumps(search, ensure_ascii=False, indent=2)
    writes['graph.json'] = json.dumps({'nodes': [{'id': s, 'title': p['title'], 'path': output_name(s)} for s,p in compiled.items()],
                                      'edges': list({(e['source'],e['target']): e for e in edges}.values())}, ensure_ascii=False, indent=2)
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    ET.SubElement(channel, 'title').text = '王鑫烨 · 公开记录'
    ET.SubElement(channel, 'link').text = BASE_URL
    ET.SubElement(channel, 'description').text = '学习、实践和想法的公开记录。'
    for source, page in compiled.items():
        if not source.startswith('notes/'):
            continue
        entry = ET.SubElement(channel, 'item')
        ET.SubElement(entry, 'title').text = page['title']
        ET.SubElement(entry, 'link').text = BASE_URL + output_name(source)
        ET.SubElement(entry, 'guid', isPermaLink='true').text = BASE_URL + output_name(source)
        ET.SubElement(entry, 'description').text = page['text'][:400]
        if page.get('published'):
            d = datetime.fromisoformat(page['published']).replace(tzinfo=timezone.utc)
            ET.SubElement(entry, 'pubDate').text = format_datetime(d)
    writes['feed.xml'] = '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(rss, encoding='unicode')
    writes['.nojekyll'] = ''
    for name in ('style.css', 'site.js'):
        writes[name] = (root / 'site-assets' / name).read_text(encoding='utf8')
    # Validate and render every page before creating output files.
    for relative in writes:
        if not (destination / relative).resolve().is_relative_to(destination):
            raise ValueError('网站输出存在越界链接，已停止')
    for relative, content in writes.items():
        p = destination / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding='utf8')
    return {'pages': len(pages), 'files': len(writes), 'destination': str(destination), 'hosting_enabled': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    print(json.dumps(build(args.root), ensure_ascii=False, indent=2))
