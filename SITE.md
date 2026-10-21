# 公开网站

本站由公开 Markdown 文件生成。内容范围在 `site.json` 明确列出；不读取任何私人档案。借鉴数字花园的搜索、反向链接、关系图与 RSS，保留原 Markdown 和 Git 历史作为维护入口。

## 更新流程（由 AI 操作）

1. 按本人明确的公开意图，整理公开文章，放到 `notes/`，更新 JOURNAL.md。只选择本人允许公开的内容与图片。
2. 在 `site.json` 添加该篇的路径、标题及明确的发布日期。
3. 在本公开仓库的检出中运行：

```text
python -m pip install -r site-requirements.txt
python tools/build_site.py
python -m unittest discover -s tests -v
python -m http.server 8766 --bind 127.0.0.1 --directory docs
```

4. 检查生成的 `docs/` 内容、搜索索引、反向链接和 RSS，再连同文章提交。此目录全部为公开内容，不能把私人资料作为构建输入。

## 托管

网站已于 2026-10-21 部署并核验：[打开公开档案](https://hollowknight-ai.github.io/HollowKnight-AI/)。GitHub Pages 使用 `main` 分支的 `/docs` 目录；提交生成页面后，部署任务会自动更新网站。若页面未更新，请先检查仓库 Actions 中的 Pages 部署结果。

当前有全文关键词搜索、反向链接、可点击的关联图、RSS、代码块、表格与手机布局。公式源码会保留；浏览器中的专业数学排版和语义搜索尚未接入。

若删除公开页面，应同时删除 `site.json` 中对应项和 `docs/` 中旧的生成页面；普通文件删除不清除 Git 历史。程序不会自行清空目录。


## 两套公开首页

- 默认 `index.html?style=vcard`：vCard 名片、真实履历时间线、作品分类筛选和图文记录分栏。
- `github.html?style=github`：GitHub personal-website 的侧栏资料、repo/topic/post 卡片与纵向笔记索引。
- 顶部可随时切换。浏览器记住访客上次选择；明确带 style 参数的分享链接优先，不强制对方采用自己的设置。
- `site-home.json` 是两版共用的公开数据；`tools/render_homes.py` 构建不同 HTML。新增记录先维护原文与 `site.json`，再同步公开主页摘要，不将未发布材料塞入清单。
- 原 Markdown 首页保留为 `notebook.html`，全部旧文章 URL 不变，搜索、关联图与 RSS 保留。详文采用共用阅读版式，主页结构按两种风格独立组织。
- 实际移植与来源、改动、MIT 许可见 [DESIGN.md](DESIGN.md)，原始上游文件保留在 `vendor/`。私密资料不得作为主页数据或构建输入。
