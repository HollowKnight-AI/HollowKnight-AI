"""Two structurally different public homepages from one explicitly public data file.

vCard markup/CSS/interaction adapted from codewithsadee (MIT, 2022).
GitHub masthead, repo/topic/post card markup adapted from GitHub (MIT, 2019).
Original sources and licenses are kept in vendor/. See DESIGN.md for provenance.
"""
import html
import json
import hashlib
from pathlib import Path
import re

def e(value):
    return html.escape(str(value), quote=True)

def art(row, cls):
    if row.get('image'):
        return f'<figure class="{cls}"><img src="{e(row["image"])}" alt="{e(row["title"])}" loading="lazy"></figure>'
    return f'<figure class="{cls} letter-art {e(row["kind"])}" aria-hidden="true"><b>{e(row["symbol"])}</b><span>HOLLOWKNIGHT-AI / OPEN NOTEBOOK</span></figure>'

def chrome(look):
    other='github' if look=='vcard' else 'vcard'
    url='github.html?style=github' if other=='github' else 'index.html?style=vcard'
    label='GitHub · 项目与笔记' if other=='github' else 'vCard · 名片与作品'
    return f'<div class="home-tools"><a class="switch-look" data-look-link href="{url}">切换为 {label} ⇄</a><a href="notebook.html">档案阅读版 ↗</a><a href="feed.xml">RSS ↗</a><label class="home-search-label">搜索公开档案<input id="home-search" type="search" placeholder="文章、知识、经历…" autocomplete="off"></label></div><div id="home-results" aria-live="polite"></div>'

def head(look, assets):
    css=['home.css'] + (['vcard.css','vcard-adapt.css'] if look=='vcard' else ['github.css'])
    links=''.join(f'<link rel="stylesheet" href="home-assets/{x}?v={assets[x]}">' for x in css)
    js=('<script defer src="home-assets/vcard.js?v='+assets['vcard.js']+'"></script>' if look=='vcard' else '')
    return '<!doctype html><html lang="zh-CN" data-home-look="'+look+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="王鑫烨的公开个人主页：理论物理、AI for Science、学习与生活记录"><title>王鑫烨 · '+('名片与作品' if look=='vcard' else '项目与笔记')+'</title>'+links+js+'<script defer src="home-assets/home.js?v='+assets['home.js']+'"></script><link rel="alternate" type="application/rss+xml" title="公开记录" href="feed.xml"></head><body>'

def timeline(title, rows):
    items=''.join(f'<li class="timeline-item"><h4 class="h4 timeline-item-title">{e(r["title"])}</h4><span>{e(r["date"])}</span><p class="timeline-text">{e(r["description"])}</p></li>' for r in rows)
    return f'<section class="timeline"><div class="title-wrapper"><span class="icon-box" aria-hidden="true">▤</span><h3 class="h3">{title}</h3></div><ol class="timeline-list">{items}</ol></section>'

def vcard(data, assets):
    p=data['profile']
    # The upstream sidebar-info, contacts-list, navbar, service, timeline,
    # project-list and blog card structures are retained with personal data.
    sidebar=f'''<aside class="sidebar" data-sidebar><div class="sidebar-info"><figure class="avatar-box"><img src="{e(p['avatar'])}" alt="王鑫烨的 GitHub 头像" width="150" height="150"></figure><div class="info-content"><h1 class="name">{e(p['name'])}</h1><p class="title">{e(p['role'])}</p></div><button class="info_more-btn" type="button" data-sidebar-btn aria-label="联系与背景" aria-expanded="false"><span>联系与背景</span><span aria-hidden="true">⌄</span></button></div><div class="sidebar-info_more"><div class="separator"></div><ul class="contacts-list"><li class="contact-item"><span class="icon-box" aria-hidden="true">＠</span><div class="contact-info"><p class="contact-title">学校邮箱</p><a class="contact-link" href="mailto:{e(p['email'])}">{e(p['email'])}</a></div></li><li class="contact-item"><span class="icon-box" aria-hidden="true">⌘</span><div class="contact-info"><p class="contact-title">GitHub</p><a class="contact-link" href="https://github.com/{e(p['login'])}">{e(p['login'])} ↗</a></div></li><li class="contact-item"><span class="icon-box" aria-hidden="true">▤</span><div class="contact-info"><p class="contact-title">当前阶段</p><p class="contact-link">天津大学 · 应用物理本科</p></div></li><li class="contact-item"><span class="icon-box" aria-hidden="true">↗</span><div class="contact-info"><p class="contact-title">下一站 · 2027 拟入学</p><p class="contact-link">中科院物理所 · 已推免</p></div></li></ul><div class="separator"></div><a class="sidebar-ai" href="AI_CONTEXT.html">让 AI 了解我 ↗</a></div></aside>'''
    tabs=[('关于我','about'),('履历','resume'),('作品','portfolio'),('记录','blog')]
    nav='<nav class="navbar" aria-label="名片分栏"><ul class="navbar-list">'+''.join(f'<li class="navbar-item"><button type="button" class="navbar-link'+(' active' if i==0 else '')+f'" data-nav-link data-section="{key}" aria-pressed="'+('true' if i==0 else 'false')+'">'+title+'</button></li>' for i,(title,key) in enumerate(tabs))+'</ul></nav>'
    services=''.join(f'<li class="service-item"><div class="service-icon-box" aria-hidden="true">{e(r["symbol"])}</div><div class="service-content-box"><h4 class="h4 service-item-title">{e(r["name"])}</h4><p class="service-item-text">{e(r["description"])}</p></div></li>' for r in data['interests'])
    about=f'<article class="about active" data-page="关于我" data-section="about"><header><h2 class="h2 article-title">关于我</h2></header><section class="about-text"><p class="intro-eyebrow">PHYSICS, CURIOSITY & EVERYDAY LIFE</p><h3 class="personal-heading">把好奇，留在生活里。</h3><p>{e(p["intro"])}</p><p>{e(p["statement"])}</p><div class="home-cta"><a href="ABOUT.html">完整介绍 ↗</a><a href="NOW.html">近期状态 ↗</a></div></section><section class="service"><h3 class="h3 service-title">我在关注</h3><ul class="service-list">{services}</ul></section><section class="featured-journey"><a href="notes/2026-10-15-taishan.html"><img src="{e(data["projects"][2]["image"])}" alt="泰山山间建筑与岩壁" loading="lazy"><div><span>一段最近的旅程</span><h3 class="h3">泰山之旅</h3><p>2026.10.15—10.16 · 玩得很开心 ↗</p></div></a></section></article>'
    tools=''.join('<li>'+e(x)+'</li>' for x in data['tools'])
    resume='<article class="resume" data-page="履历" data-section="resume"><header><h2 class="h2 article-title">履历</h2></header>'+timeline('教育背景',data['education'])+timeline('科研与实践',data['experience'])+f'<section class="skill"><h3 class="h3 skills-title">接触与使用的工具</h3><ul class="tool-chips">{tools}</ul><p class="honest-note">据申请阶段简历整理；不以百分比推测熟练程度。</p><div class="home-cta"><a href="notes/2026-10-21-baoyan-cv.html">查看简历、PDF 与 LaTeX 源码 ↗</a><a href="PROJECTS.html">完整科研与实践记录 ↗</a></div></section></article>'
    categories=['全部','数字档案','学业与履历','旅行']
    filters='<ul class="filter-list">'+''.join('<li class="filter-item"><button type="button" data-filter-btn class="'+('active' if i==0 else '')+'">'+cat+'</button></li>' for i,cat in enumerate(categories))+'</ul><div class="filter-select-box"><button class="filter-select" type="button" data-select aria-expanded="false"><span class="select-value" data-selecct-value>全部</span><span>⌄</span></button><ul class="select-list">'+''.join('<li class="select-item"><button type="button" data-select-item>'+cat+'</button></li>' for cat in categories)+'</ul></div>'
    projects=''.join(f'<li class="project-item active" data-filter-item data-category="{e(r["category"])}"><a href="{e(r["url"])}">{art(r,"project-img")}<h3 class="project-title">{e(r["title"])}</h3><p class="project-category">{e(r["category"])}</p></a></li>' for r in data['projects'])
    portfolio='<article class="portfolio" data-page="作品" data-section="portfolio"><header><h2 class="h2 article-title">作品与公开资料</h2></header><section class="projects">'+filters+'<ul class="project-list">'+projects+'</ul><p class="honest-note">已公开的实际材料；论文和计算代码尚未提供，不列为已发表成果。</p></section></article>'
    posts=''.join(f'<li class="blog-post-item"><a href="{e(r["url"])}">{art(r,"blog-banner-box")}<div class="blog-content"><div class="blog-meta"><p class="blog-category">{e(r["category"])}</p><span class="dot"></span><time>{e(r["date"])}</time></div><h3 class="h3 blog-item-title">{e(r["title"])}</h3><p class="blog-text">{e(r["description"])}</p></div></a></li>' for r in data['posts'])
    blog='<article class="blog" data-page="记录" data-section="blog"><header><h2 class="h2 article-title">记录与思考</h2></header><section class="blog-posts"><ul class="blog-posts-list">'+posts+'</ul></section><div class="home-cta"><a href="JOURNAL.html">完整记录索引 ↗</a><a href="feed.xml">订阅 RSS ↗</a></div></article>'
    return head('vcard',assets)+chrome('vcard')+'<main>'+sidebar+'<div class="main-content">'+nav+about+resume+portfolio+blog+'</div></main>'+footer()+'</body></html>'

def github(data, assets):
    p=data['profile']
    # Adapted from upstream masthead.html and sidebar branch of _layouts/home.html.
    masthead=f'<aside class="gh-masthead"><img src="{e(p["avatar"])}" class="circle mb-3" width="150" height="150" alt="王鑫烨的 GitHub 头像"><h1 class="mb-2 lh-condensed">{e(p["name"])}</h1><p class="mb-3 f4 text-gray">{e(p["role"])}</p><div class="f4 mb-6"><a href="https://github.com/{e(p["login"])}">@{e(p["login"])}</a><a class="gh-email" href="mailto:{e(p["email"])}">{e(p["email"])}</a></div><nav class="gh-page-nav" aria-label="公开档案"><a href="#projects">公开项目</a><a href="#interests">关注主题</a><a href="#posts">文章与记录</a><a href="ABOUT.html">关于我 ↗</a><a href="AI_CONTEXT.html">AI 背景摘要 ↗</a></nav><p class="gh-updated">档案更新 {e(data["updated"])}</p></aside>'
    # repo-card.html: retain upstream component/flex/typography markup; remove
    # unavailable star/fork metrics and Liquid substitutions. No made-up counts.
    repos=''
    for r in data['projects']:
        repos+=f'<div class="github-component d-flex flex-column flex-justify-between height-full text-left border border-gray-light bg-white rounded-1 p-3"><div><div class="d-flex flex-justify-between flex-items-start mb-1"><h3 class="f4 lh-condensed mb-1"><a href="{e(r["url"])}"><span aria-hidden="true">▤ </span>{e(r["title"])}</a></h3></div><div class="text-gray mb-2 ws-normal">{e(r["description"])}</div></div><div class="d-flex f6"><span class="repo-language-color" aria-hidden="true"></span><span class="mr-3" itemprop="programmingLanguage">{e(r["language"])}</span><span class="gh-category">{e(r["category"])}</span></div></div>'
    # topic-card.html: preserve the linked # placeholder branch and component
    # hierarchy; symbols supplied by our shared data replace the generic #.
    topics=''.join(f'<a href="{e(r["url"])}" class="github-component position-relative hover-grow height-full no-underline d-flex flex-column flex-justify-center text-center border border-gray-light rounded-1 bg-white p-5"><div class="bg-blue-light f4 text-gray-light text-bold rounded-1 flex-shrink-0 text-center mx-auto mb-3 topic-symbol">{e(r["symbol"])}</div><p class="f3 lh-condensed text-center link-gray-dark mb-0 mt-1">{e(r["name"])}</p><p class="f5 text-gray text-center mb-0 mt-1">{e(r["description"])}</p></a>' for r in data['interests'])
    # post-card.html: same compact date + title component, with an excerpt.
    thoughts=''.join(f'<div class="height-full text-left border border-gray-light bg-white rounded-1 p-3"><div class="d-flex flex-justify-between flex-items-start mb-1"><h3 class="f4 lh-condensed mb-1"><a href="{e(r["url"])}">{e(r["title"])}</a></h3></div><div class="text-gray mb-2 ws-normal">{e(r["date"])}</div><p class="f5 text-gray">{e(r["description"])}</p></div>' for r in data['posts'])
    overview=f'<section class="gh-intro"><p class="gh-eyebrow">AN OPEN NOTEBOOK</p><h2>你好，我是鑫烨。</h2><p>{e(p["intro"])}</p><p>{e(p["statement"])}</p><div class="gh-quick-links"><a href="notes/2026-10-21-baoyan-cv.html">简历与源码 ↗</a><a href="NOW.html">近期状态 ↗</a><a href="notebook.html">全部公开档案 ↗</a></div></section>'
    content=overview+'<section id="projects" class="gh-section"><div class="gh-section-heading"><h2>公开项目与资料</h2><a href="PROJECTS.html">科研与实践 ↗</a></div><div class="gh-project-grid">'+repos+'</div></section><section id="interests" class="gh-section"><h2>我的关注</h2><div class="gh-topic-grid">'+topics+'</div></section><section id="posts" class="gh-section"><div class="gh-section-heading"><h2>文章与记录</h2><a href="JOURNAL.html">所有记录 ↗</a></div><div class="gh-post-grid">'+thoughts+'</div></section><section class="gh-ai-callout"><span>⌘</span><div><h2>给下一位 AI 的共同起点</h2><p>背景、协作偏好、Markdown 原文与修订历史。</p><a href="AI_CONTEXT.html">读取背景摘要 ↗</a> · <a href="https://github.com/HollowKnight-AI/HollowKnight-AI/blob/main/HANDOFF.md">接手说明 ↗</a></div></section>'
    return head('github',assets)+chrome('github')+'<main class="gh-layout">'+masthead+'<div class="gh-content">'+content+'</div></main>'+footer()+'</body></html>'

def footer():
    return '<footer class="home-footer"><span>王鑫烨 · 一份持续修改的公开档案</span><span>Based on <a href="https://github.com/github/personal-website">GitHub personal-website</a> & <a href="https://github.com/codewithsadee/vcard-personal-portfolio">vCard</a> · <a href="design.html">代码来源与许可</a></span></footer>'

def render(root, compiled):
    root=Path(root)
    raw=(root/'site-home.json').read_text(encoding='utf8')
    data=json.loads(raw)
    if data.get('repository')!='HollowKnight-AI/HollowKnight-AI' or re.search(r'Life-Vault|github_pat_|gh[pousr]_[A-Za-z0-9]{20,}',raw,re.I):
        raise ValueError('主页资料必须来自明确的公开范围')
    allowed={v['path'] for v in ({'path':('index.html' if s=='README.md' else s.removesuffix('.md')+'.html')} for s in compiled)}
    for row in data['projects']+data['posts']+data['interests']:
        url=row['url']
        if url not in allowed and url!='https://github.com/HollowKnight-AI/HollowKnight-AI':
            raise ValueError('主页入口尚未列入公开构建：'+url)
    writes={}
    for path in (root/'site-assets/home').iterdir():
        if path.is_file():writes['home-assets/'+path.name]=path.read_text(encoding='utf8')
    versions={Path(p).name:hashlib.sha256(c.encode('utf8')).hexdigest()[:12] for p,c in writes.items()}
    writes['index.html']=vcard(data,versions)
    writes['github.html']=github(data,versions)
    writes['home-data.json']=json.dumps(data,ensure_ascii=False,indent=2)
    return writes
