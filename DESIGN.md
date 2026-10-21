# 两种入口，同一份公开档案

本人的公开主页提供两套结构不同的视图；顶部链接可以随时切换。

| | GitHub · 项目与笔记 | vCard · 名片与作品 |
| --- | --- | --- |
| 主要组织 | 个人侧栏、纵向分节 | 侧边名片、独立分栏导航 |
| 突出内容 | 项目资料、关注主题、文章列表、AI 入口 | 自我介绍、履历时间线、作品分类、图文记录 |
| 典型交互 | 锚点索引、项目/主题/文章链接 | 移动端展开资料、分栏切换、桌面与移动分类筛选 |
| 共同功能 | 两版共享资料、搜索公开档案、文章阅读版、简历与源文件、相册、RSS | 同左 |

数据维护在 `site-home.json`，每版由 `tools/render_homes.py` 单独生成 HTML。不同的组织方式是为了呈现不同侧重点，不增加未经本人确认的经历、成果或工具熟练度。文章详情共用原有阅读版式。

## 实际使用了哪些开源代码

### GitHub personal-website

来源：[github/personal-website](https://github.com/github/personal-website)，MIT，Copyright (c) 2019 GitHub。

- 侧栏布局与资料结构由 `_layouts/home.html`、`_includes/masthead.html` 适配。
- repo/topic/post 三类组件的 HTML 层级、工具类、标题、描述和元信息结构由 `_includes/repo-card.html`、`topic-card.html`、`post-card.html` 适配到 Python 构建函数。
- Liquid 动态变量改为构建时从同一份公开 JSON 读取；省略未取得实时数据的 Star/Fork 数字。项目语言来自已公开材料类型；主题图标不需要外部服务。
- 本地 CSS 提供所用 Primer 工具类的等效样式，未加载远端 Primer，也未引入旧 Ruby/Jekyll 依赖。项目本身已归档，适配代码继续由本站维护。

原始参考文件保存在 [vendor/github](https://github.com/HollowKnight-AI/HollowKnight-AI/tree/main/vendor/github)。[完整上游许可](licenses/github-personal-website.txt)。

### vCard personal portfolio

来源：[codewithsadee/vcard-personal-portfolio](https://github.com/codewithsadee/vcard-personal-portfolio)，MIT，Copyright (c) 2022 codewithsadee。

- 原始 `assets/css/style.css` 完整保留并实际作为 `home-assets/vcard.css` 加载；本地调整另存 `vcard-adapt.css`。
- 原始 JS 的移动侧栏展开、作品分类选择与过滤、分栏导航代码实际移植到 `vcard.js`。移除没有使用的客户评价弹层及联系表单逻辑，All 本地化为“全部”；本站补充 URL 锚点、可访问状态、风格偏好和搜索。
- 保留并适配 sidebar、contacts、navbar、service、timeline、project、blog 的 HTML 结构与类名；资料全部替换成本人的已公开内容。
- 不使用样例人物、客户评价、虚构作品、技能百分比、Google 地图及外部字体/Ionicons 脚本。头像使用本人 GitHub 的公开头像；旅行图片引用已经公开的原件。

原始参考文件保存在 [vendor/vcard](https://github.com/HollowKnight-AI/HollowKnight-AI/tree/main/vendor/vcard)。[完整上游许可](licenses/vcard-personal-portfolio.txt)。

## 许可边界

上述 MIT 许可适用于原项目软件；本站的个人文字、照片、简历及其原有许可仍依各自说明。引用开源模板不等于可以擅自发布私人资料。页面不接触私人仓库、聊天记录或登录凭证。
