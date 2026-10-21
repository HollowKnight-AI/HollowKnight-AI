# 保研申请简历归档

2026-10-21 收到本人提供的 PDF 和 Awesome-CV LaTeX 项目，并获准公开。原材料的具体制作日期未知。

## 文件入口

- `resume-public.pdf`：公开 PDF。按本人于 2026-10-21 的确认，将社团累计服务人次更正为 **1200 人次**；未改动其他履历内容。收到的旧 PDF 仅在本地保留，不公开上传。
- `source-original.zip`：收到的原始源码压缩包，按字节保留。
- `source/`：从原 ZIP 安全解压的全部 33 个文件，方便浏览与修改。包括字体、模板类文件和模板示例，内容未改写。
- `manifest.json`：来源、阶段、文件哈希、已知差异及更正记录。
- [面向阅读与 AI 的履历摘要](../../notes/2026-10-21-baoyan-cv.md)。

简历中的“至今”、申请意向和论文进度均是历史表述，不能自动视为当前情况。当前教育状态见仓库 NOW.md。

## 主文件与可编辑内容

**这份中文简历的主文件是 `source/resume.tex`。** 它依次引入：

1. `resume/education.tex`：教育背景、成绩、奖项。
2. `cv/skills.tex`：本人填写的专业技能。
3. `resume/experience.tex`：本人填写的科研与实习经历。
4. `resume/committees.tex`：本人填写的校园经历，源码为 1200 人次。

`source/cv.tex` 与 `source/coverletter.tex` 是模板示例。其作者资料、岗位、奖项和联系方式不属于本人；未启用的其他示例段落也不能并入个人档案。包内的 `profile.png` 不作为本人头像使用。

## 编译说明

原项目在文件头指定 XeLaTeX，使用 `awesome-cv.cls`、`xeCJK`、Fandol 中文字体及相关 LaTeX 包。保留 `fonts/` 的相对目录。在已经具备对应 TeX 环境的情况下，可在 `source/` 运行：

```text
xelatex -no-shell-escape -interaction=nonstopmode -halt-on-error resume.tex
```

本次仅归档与核对，没有重新编译 LaTeX，也未声称源码能够逐字复现提供的 PDF。PDF 的人次修订采用直接更正，已检查页面显示与可提取文本。

## 已知版本差异

| 项目 | PDF 记载 | LaTeX 源码记载 | 摘要处理 |
| --- | --- | --- | --- |
| 社团服务人次 | 公开版已按本人确认更正为 1200 | 1200 | 统一采用 1200 人次 |
| 王景导师职称 | 教授 | 副教授 | 仅写导师姓名，不推断当前职称 |
| 基金题名中的用字 | 杂志散射 | 杂质散射 | 摘要用基金编号定位，原件各自保留 |

其他经历与学业数据据本人提供的材料整理，未进行外部独立核实。没有将“拟投 PRB”改写成已投稿、录用或发表。

## 模板来源与许可

原项目来源标注为 [posquit0/Awesome-CV](https://github.com/posquit0/Awesome-CV)。原始 README、作者署名与源文件许可声明均保留：`awesome-cv.cls` 标注 LPPL 1.3c，主模板文件标注 CC BY-SA 4.0。字体等第三方文件保留原件并遵循各自许可；本仓库的原创文字许可不覆盖这些第三方模板与字体。
