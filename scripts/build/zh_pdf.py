#!/usr/bin/env python3
"""Build print-ready PDFs of the simplified-Chinese reference translation (zh-CN/).

Five volumes (A4, CJK typography, cover, table of contents with page numbers, chapter page breaks):
  vol1 总览与基础 · vol2 第 02–07 层 · vol3 第 08–13 层 · vol4 第 14–19 章 · vol5 案例研究与附录
For print: Mermaid diagrams are pre-rendered to SVG; chart alt text becomes a Chinese caption; GitHub
callouts become boxes; <details> blocks are expanded; citations become small superscripts; per-page
source lists are replaced by one bibliography appendix (English, as in the original).

Usage: zh_pdf.py [vol1 vol2 ...]      (default: all)   Output: zh-CN/pdf/*.pdf
Requires: markdown, markdown-callouts, pypdf, Node + Playwright Chromium, Noto CJK fonts.
"""
from __future__ import annotations

import hashlib
import html as htmllib
import json
import re
import subprocess
import sys
from pathlib import Path

import markdown
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO, fenced_blocks, read_registry  # noqa: E402

ZH = REPO / "zh-CN"
OUT = ZH / "pdf"
BUILD = REPO / ".zh_pdf_build"
AS_OF = "2026-11-05"
TITLE = "英伟达全栈深度研究"
SUBTITLE = "NVIDIA 如何在 AI 训练与推理中变得不可或缺 —— 逐层解析"

LAYER_DIRS = ["02-gpu-silicon", "03-memory-packaging-supply-chain", "04-cpu-grace-vera",
              "05-scale-up-nvlink-nvswitch", "06-scale-out-scale-across-networking",
              "07-dpu-supernic-storage-security", "08-systems-racks-ai-factories",
              "09-cuda-and-system-software", "10-libraries-cuda-x", "11-inference-and-ai-software",
              "12-orchestration-and-cloud-services", "13-ecosystem-gtm-and-capital"]
STRATEGY_TAIL = ["competition.md", "history-and-how-built.md", "roadmap.md", "value-chain-and-corp-dev.md"]


def folder_order(folder: Path) -> list[Path]:
    """index.md first, then sub-pages in the order index.md links them, strategy pages last."""
    files = {p.name: p for p in folder.glob("*.md")}
    order = ["index.md"] if "index.md" in files else []
    if "index.md" in files:
        for m in re.finditer(r"\]\(([^)#\s]+\.md)", files["index.md"].read_text(encoding="utf-8")):
            name = Path(m.group(1)).name
            if name in files and name not in order and name not in STRATEGY_TAIL and \
                    (folder / name).resolve() == (folder / m.group(1)).resolve():
                order.append(name)
    order += sorted(n for n in files if n not in order and n not in STRATEGY_TAIL)
    order += [n for n in STRATEGY_TAIL if n in files]
    return [files[n] for n in order]


def volumes():
    z = lambda p: ZH / p  # noqa: E731
    vols = [
        ("vol1-overview-primers", "卷一 · 总览与基础", "导读、执行摘要、速查表、英伟达飞轮与五篇入门",
         [[z("README.md")], [z("00-executive-summary.md")], [z("CHEATSHEET.md")], [z("01-the-nvidia-flywheel.md")]]
         + [[p] for p in sorted((ZH / "primers").glob("P*.md"))]),
        ("vol2-layers-02-07", "卷二 · 芯片、内存与互联", "第 02–07 层：GPU、内存与封装、CPU、纵向扩展、横向扩展网络、DPU 与网卡",
         [folder_order(ZH / "layers" / d) for d in LAYER_DIRS[:6]]),
        ("vol3-layers-08-13", "卷三 · 系统、软件与生态", "第 08–13 层：系统与机架、CUDA、软件库、推理软件、云服务、生态与资本",
         [folder_order(ZH / "layers" / d) for d in LAYER_DIRS[6:]]),
        ("vol4-cross-cutting", "卷四 · 跨层专题", "第 14–19 章：经济学、竞争格局、发展史、路线图、看空情景、对高通的启示",
         [[z("cross-cutting/14-training-vs-inference-economics.md")],
          folder_order(ZH / "cross-cutting" / "15-competitive-landscape"),
          [z("cross-cutting/16-how-nvidia-built-it-timeline.md")], [z("cross-cutting/17-roadmap-2025-2028.md")],
          [z("cross-cutting/18-vulnerabilities-and-bear-case.md")], [z("cross-cutting/19-implications-for-qualcomm.md")]]),
        ("vol5-case-studies-appendix", "卷五 · 案例研究与附录", "七个案例研究、术语表与参考文献",
         [[p] for p in sorted((ZH / "case-studies").glob("CS*.md"))] + [[z("glossary.md")]]),
    ]
    return [(k, t, s, [[p for p in grp if p.exists()] for grp in groups]) for k, t, s, groups in vols]


# ---------------------------------------------------------------------------------------------
# Markdown -> print HTML
# ---------------------------------------------------------------------------------------------
MD_EXT = ["tables", "fenced_code", "attr_list", "md_in_html", "sane_lists", "github-callouts"]


def file_url(p: Path) -> str:
    return "file://" + str(p.resolve())


def strip_md(s: str) -> str:
    s = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", s)
    s = re.sub(r"\[\[S\d+\]\]\([^)]*\)", "", s)
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    return re.sub(r"[*_`<>]", "", s).strip()


def to_html(path: Path, mermaid_jobs: dict) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    # drop the per-page reference note (stated once in the preface) and the per-page source list
    text = re.sub(r"^> \[!NOTE\]\n> 本页为英文原文的简体中文参考译文[^\n]*\n", "", text, flags=re.M)
    text = re.split(r"\n## 📚 (?:来源|Sources)", text)[0]
    title = strip_md(next((l[2:] for l in text.split("\n") if l.startswith("# ")), path.stem))
    # Mermaid -> pre-rendered SVG image
    for _line, info, body in fenced_blocks(text, "mermaid"):
        h = hashlib.sha1(body.encode("utf-8")).hexdigest()[:16]
        mermaid_jobs[h] = body
    def mmd(m):
        h = hashlib.sha1(m.group(1).encode("utf-8")).hexdigest()[:16]
        return f'\n<figure class="mmd"><img src="{file_url(BUILD / "mmd" / (h + ".svg"))}" alt=""></figure>\n'
    text = re.sub(r"^```mermaid\n(.*?)\n```\s*$", mmd, text, flags=re.M | re.S)
    # <details> -> always-open boxes
    text = re.sub(r"<details>\s*", '<div class="details" markdown="1">\n', text)
    text = re.sub(r"<summary>(.*?)</summary>", r'<p class="summary">\1</p>', text, flags=re.S)
    text = text.replace("</details>", "</div>")
    # citations -> superscripts
    text = re.sub(r"\[\[S(\d+)\]\]\([^)]*\)", r'<sup class="c">S\1</sup>', text)
    text = re.sub(r"</sup>\s*<sup class=\"c\">", ",", text)
    # images: block images become figures with the (translated) alt text as caption
    def img_block(m):
        alt, src = m.group(1), m.group(2)
        p = (path.parent / src.split("#")[0]).resolve()
        cap = htmllib.escape(alt)
        return f'\n<figure><img src="{file_url(p)}" alt=""><figcaption>{cap}</figcaption></figure>\n'
    text = re.sub(r"^\s*!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)\s*$", img_block, text, flags=re.M)
    def img_inline(m):
        p = (path.parent / m.group(2).split("#")[0]).resolve()
        return f'<img class="inl" src="{file_url(p)}" alt="">'
    text = re.sub(r"!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)", img_inline, text)
    def html_src(m):
        src = m.group(1)
        if src.startswith(("http", "file:")):
            return m.group(0)
        return f'src="{file_url((path.parent / src).resolve())}"'
    text = re.sub(r'src="([^"]+)"', html_src, text)
    text = re.sub(r"<a\s+href=\"[^\"]*\"[^>]*>", "", text)
    text = re.sub(r"</a>", "", text)
    # remaining links -> plain text (print)
    text = re.sub(r"(?<!!)\[((?:[^\[\]]|\[[^\]]*\])+)\]\([^)\s]+(?:\s+\"[^\"]*\")?\)", r"\1", text)
    body = markdown.markdown(text, extensions=MD_EXT, output_format="html5")
    for en, zh in (("Note", "注"), ("Tip", "提示"), ("Important", "重要"), ("Warning", "注意"), ("Caution", "警示")):
        body = body.replace(f'<p class="admonition-title">{en}</p>', f'<p class="admonition-title">{zh}</p>')
    return title, body


CSS = """
@page { size: A4; }
html { font-size: 10.3pt; }
body { font-family: 'Noto Serif CJK SC', 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', serif; line-height: 1.68;
       color: #141414; text-align: justify; }
h1, h2, h3, h4, .cover, .toc, figcaption, table, .admonition-title, .summary
       { font-family: 'Noto Sans CJK SC', 'WenQuanYi Zen Hei', sans-serif; }
h1 { font-size: 19pt; line-height: 1.3; margin: 0 0 0.6em; padding-bottom: 0.25em; border-bottom: 2.5pt solid #5F9E00;
     color: #0b0b0b; text-align: left; }
section.ch { page-break-before: always; }
h2 { font-size: 13.5pt; color: #3F6B00; margin: 1.3em 0 0.45em; page-break-after: avoid; text-align: left; }
h3 { font-size: 11.5pt; margin: 1.1em 0 0.35em; page-break-after: avoid; text-align: left; }
h4 { font-size: 10.5pt; margin: 1em 0 0.3em; page-break-after: avoid; }
p { margin: 0.45em 0; orphans: 2; widows: 2; }
sub { font-size: 8pt; color: #666; }
ul, ol { margin: 0.4em 0 0.4em 1.4em; padding: 0; }
li { margin: 0.18em 0; }
sup.c { font-size: 5.8pt; color: #9a9a9a; font-family: 'Noto Sans CJK SC', sans-serif; vertical-align: super; line-height: 0; }
table { border-collapse: collapse; width: 100%; font-size: 7.9pt; line-height: 1.42; margin: 0.6em 0; text-align: left; }
thead { display: table-header-group; }
th { background: #eef5e3; font-weight: 700; }
th, td { border: 0.5pt solid #c7c7c7; padding: 2.5pt 4pt; vertical-align: top; }
tr { page-break-inside: avoid; }
figure { margin: 0.7em 0 0.9em; page-break-inside: avoid; text-align: center; }
figure img { max-width: 100%; max-height: 118mm; }
figure.mmd img { max-width: 100%; max-height: 118mm; }
figcaption { font-size: 7.8pt; color: #555; text-align: left; line-height: 1.45; margin-top: 0.3em;
             border-left: 2pt solid #A9CC73; padding-left: 5pt; }
img.inl { max-width: 60mm; max-height: 40mm; }
code { font-family: 'Noto Sans Mono CJK SC', 'DejaVu Sans Mono', monospace; font-size: 8.3pt; background: #f3f3f1; padding: 0 2pt; }
pre { white-space: pre-wrap; font-size: 7.8pt; line-height: 1.4; background: #f6f6f4; padding: 5pt 7pt; border-radius: 3pt; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
blockquote { margin: 0.6em 0; padding: 2pt 9pt; border-left: 2.5pt solid #c3c2b7; color: #333; }
.admonition { margin: 0.7em 0; padding: 4pt 9pt 5pt; border-left: 3pt solid #2A78D6; background: #f4f8fd;
              page-break-inside: avoid; border-radius: 0 3pt 3pt 0; }
.admonition p { margin: 0.3em 0; }
.admonition-title { font-weight: 700; font-size: 8.5pt; text-transform: uppercase; margin: 0.1em 0 0.2em !important; color: #555; }
.admonition.tip { border-color: #5F9E00; background: #f3f8ec; }
.admonition.important { border-color: #6250D6; background: #f4f2fd; }
.admonition.warning, .admonition.caution { border-color: #C98500; background: #fdf7ea; }
.details { margin: 0.7em 0; padding: 3pt 9pt 5pt; border: 0.6pt dashed #a5a5a5; border-radius: 3pt; font-size: 9.4pt; background: #fbfbfa; }
.details .summary { font-weight: 700; color: #3F6B00; margin: 0.2em 0; }
hr { border: none; border-top: 0.5pt solid #ccc; margin: 1em 0; }
.mk { font-size: 1pt; line-height: 1pt; height: 1pt; margin: 0; overflow: hidden; color: #ffffff; }
/* cover */
.cover { height: 250mm; display: flex; flex-direction: column; justify-content: center; text-align: left; }
.cover .band { height: 6pt; width: 60mm; background: #5F9E00; margin-bottom: 14mm; }
.cover .t1 { font-size: 30pt; font-weight: 700; line-height: 1.25; }
.cover .t2 { font-size: 13pt; color: #444; margin-top: 5mm; }
.cover .vol { font-size: 20pt; font-weight: 700; color: #3F6B00; margin-top: 22mm; }
.cover .vsub { font-size: 11pt; color: #555; margin-top: 3mm; }
.cover .meta { font-size: 9pt; color: #777; margin-top: 30mm; line-height: 1.8; }
.preface { page-break-before: always; font-size: 9.6pt; }
.preface h2 { margin-top: 0; }
/* toc */
.toc { page-break-before: always; }
.toc h2 { font-size: 16pt; color: #0b0b0b; margin: 0 0 0.8em; }
.toc .e { display: flex; align-items: baseline; font-size: 10pt; margin: 0.18em 0; }
.toc .e.l1 { font-weight: 700; margin-top: 0.7em; font-size: 10.5pt; }
.toc .e.l2 { padding-left: 1.6em; font-size: 9.4pt; color: #333; }
.toc .e .t { flex: 0 1 auto; }
.toc .e .d { flex: 1 1 auto; border-bottom: 0.6pt dotted #aaa; margin: 0 0.4em; transform: translateY(-0.25em); }
.toc .e .n { flex: 0 0 auto; font-variant-numeric: tabular-nums; min-width: 2.2em; text-align: right; }
/* appendices */
.glossary .gcols { column-count: 2; column-gap: 7mm; }
.glossary ul { font-size: 8.4pt; line-height: 1.5; list-style: none; margin: 0; }
.glossary li { break-inside: avoid; margin-bottom: 0.3em; }
.glossary h2 { font-size: 12pt; margin: 0.5em 0 0.25em; break-after: avoid; }
.bib { column-count: 2; column-gap: 6mm; font-size: 6.8pt; line-height: 1.35; font-family: 'Noto Sans CJK SC', sans-serif; }
.bib p { margin: 0 0 0.25em; break-inside: avoid; text-align: left; }
.bib b { color: #3F6B00; }
"""


def cover(vol_title: str, vol_sub: str) -> str:
    return f"""<section class="cover"><div class="band"></div>
<div class="t1">{TITLE}</div><div class="t2">{SUBTITLE}</div>
<div class="vol">{vol_title}</div><div class="vsub">{vol_sub}</div>
<div class="meta">简体中文参考译文 · 仅供参考，如有出入以英文原文为准<br>数据与图表截至 {AS_OF} · 仅使用公开信息<br>
英文原版：github.com/FrankHuang94/nvidia_deep_dive_claude</div></section>"""


PREFACE = f"""<section class="preface"><h2>阅读说明</h2>
<p>本册为英文研究资料库《NVIDIA Full-Stack Deep Dive》的<b>简体中文参考译文</b>，仅供参考；如与英文原文存在任何出入，以英文原文为准。全书共五册，可分册打印。</p>
<ul>
<li><b>图表</b>：数据图表与架构图保留英文原版（由仓库中的 CSV 数据生成）；每张图下方的灰色文字为中文图注，概括该图的结论与关键数字。Mermaid 示意图已译为中文。</li>
<li><b>引用</b>：正文中的灰色上标（如 <sup class="c">S2031</sup>）为来源编号，完整书目见卷五附录“参考文献”（保留英文原题）。</li>
<li><b>可信度标记</b>：🟢 已确认（公司官方公布）· 🟡 有报道（可信媒体或分析机构）· 🔴 推测（推断、传闻或本资料库的分析）；“估计”表示估算值。</li>
<li><b>对比标记</b>：🟩 领先 · 🟨 持平 · 🟥 落后 · 🟦 路线不同。</li>
<li><b>三层阅读深度</b>：每页以“⚡ 要点速览”开篇；正文“原理解析”含“算例”；虚线框为“🔧 技术细节”；页末“🎯 企业发展视角”列出供企业发展团队思考的问题。</li>
<li><b>时效</b>：数据截至 {AS_OF}；英伟达 2027 财年第三季度财报（2026-11-17）与 GTC DC 大会（2026-12-01）晚于此日期。</li>
<li><b>公开信息</b>：本资料库仅使用公开信息；涉及高通的内容均以问题与选项的形式呈现，不构成建议。</li>
</ul></section>"""


def bibliography_html() -> str:
    reg, _ = read_registry()
    rows = []
    for sid in sorted(reg, key=lambda s: int(s[1:])):
        r = reg[sid]
        bits = [f"<b>{sid}</b>", htmllib.escape(r.get("publisher", "")), f"<i>{htmllib.escape(r.get('title', ''))}</i>",
                htmllib.escape(r.get("date", ""))]
        rows.append("<p>" + " · ".join(b for b in bits if b and b != "<i></i>") + "</p>")
    return ('<div class="mk">@@BIB@@</div><h1>附录 · 参考文献（Bibliography）</h1>'
            '<p style="font-size:8.5pt;color:#555">按来源编号排列；书目信息保留英文原文。完整链接见仓库 sources/bibliography.md。</p>'
            f'<div class="bib">{"".join(rows)}</div>')


def build_volume(key, vol_title, vol_sub, groups, mermaid_jobs) -> Path:
    sections, toc = [], []
    n = 0
    for grp in groups:
        for i, path in enumerate(grp):
            n += 1
            title, body = to_html(path, mermaid_jobs)
            marker = f"@@CH{n:03d}@@"
            if path.name == "glossary.md":
                # one two-column flow for all letters (so a letter heading never ends a page alone);
                # the on-screen "jump to" line has no use on paper
                body = re.sub(r"<p>跳转：.*?</p>", "", body, count=1, flags=re.S)
                k = body.find("<h2>")
                body = f'<div class="glossary">{body[:k]}<div class="gcols">{body[k:]}</div></div>'
            # The page-number marker sits outside the H1 so it stays out of the PDF bookmarks.
            sections.append(f'<section class="ch"><div class="mk">{marker}</div>{body}</section>')
            toc.append((1 if i == 0 else 2, title, marker))
    if key.startswith("vol5"):
        sections.append(f'<section class="ch">{bibliography_html()}</section>')
        toc.append((1, "附录 · 参考文献（Bibliography）", "@@BIB@@"))
    return sections, toc


def render(key, vol_title, vol_sub, sections, toc, pages: dict | None) -> Path:
    def toc_html():
        rows = []
        for lvl, title, marker in toc:
            num = str(pages.get(marker, "")) if pages else "000"
            rows.append(f'<div class="e l{lvl}"><span class="t">{htmllib.escape(title)}</span>'
                        f'<span class="d"></span><span class="n">{num}</span></div>')
        return f'<section class="toc"><h2>目录</h2>{"".join(rows)}</section>'
    doc = (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{TITLE} · {vol_title}</title>'
           f"<style>{CSS}</style></head><body>{cover(vol_title, vol_sub)}{PREFACE}{toc_html()}"
           f'{"".join(sections)}</body></html>')
    html_path = BUILD / f"{key}.html"
    html_path.write_text(doc, encoding="utf-8")
    pdf_path = BUILD / f"{key}.pdf"
    subprocess.run(["node", str(REPO / "scripts/build/print_pdf.cjs"), str(html_path), str(pdf_path),
                    f"{TITLE} · {vol_title}"], check=True)
    return pdf_path


def page_numbers(pdf: Path, markers: list[str]) -> dict:
    found = {}
    reader = PdfReader(str(pdf))
    for i, page in enumerate(reader.pages, start=1):
        t = page.extract_text() or ""
        for m in markers:
            if m not in found and m in t:
                found[m] = i
    return found


def fix_outline(pdf: Path) -> None:
    """Chromium prefixes the bookmark title of a heading that starts a new page with a copy of its first
    line ("TitleTitle", or "Line1Line1Line2" when the heading wraps); strip that prefix."""
    from pypdf import PdfWriter
    from pypdf.generic import NameObject, TextStringObject
    writer = PdfWriter(clone_from=str(pdf))
    outlines = writer._root_object.get("/Outlines")
    stack = [outlines.get_object().get("/First")] if outlines else []
    while stack:
        node = stack.pop()
        while node is not None:
            item = node.get_object()
            t = str(item.get("/Title", ""))
            for k in range(4, len(t) // 2 + 1):
                if t[k:].startswith(t[:k]):
                    item[NameObject("/Title")] = TextStringObject(t[k:])
                    break
            if "/First" in item:
                stack.append(item["/First"])
            node = item.get("/Next")
    with pdf.open("wb") as fh:
        writer.write(fh)


def write_index() -> Path:
    """Write zh-CN/pdf/README.md from the PDFs on disk (page counts, sizes, chapter start pages)."""
    rows, details = [], []
    for key, vol_title, vol_sub, _ in volumes():
        pdf = OUT / f"NVIDIA-deep-dive-zh-{key}.pdf"
        if not pdf.exists():
            continue
        reader = PdfReader(str(pdf))
        n_pages, size = len(reader.pages), pdf.stat().st_size / 1e6
        rows.append(f"| **{vol_title}** | [{pdf.name}]({pdf.name}) | {vol_sub} | {n_pages} | {size:.1f} MB |")
        items = [(x.title, reader.get_destination_page_number(x) + 1) for x in reader.outline
                 if not isinstance(x, list) and x.title not in ("阅读说明", "目录")]
        details.append(f"<details><summary>{vol_title} — 各章起始页</summary>\n\n"
                       + "\n".join(f"- {t} …… 第 {pg} 页" for t, pg in items) + "\n\n</details>")
    text = f"""# 打印版 PDF（简体中文参考译文）

> [!NOTE]
> 以下 PDF 由 `zh-CN/` 中的简体中文参考译文生成，仅供参考；如与英文原文有任何出入，以[英文原文](../../README.md "English original")为准。

全书分五册，均为 A4 版式，可分册打印。每册包含封面、阅读说明、带页码的目录、页眉（书名与册名）和页脚页码，并带 PDF 书签，便于在屏幕上跳转。

| 册 | 文件 | 内容 | 页数 | 大小 |
|---|---|---|---|---|
{chr(10).join(rows)}

## 打印建议

- **纸张与缩放**：A4，选择“实际大小”或 100% 缩放（页边距约 15–17 mm）；可双面打印。
- **彩色或黑白**：图表采用色盲友好配色，建议彩色打印；黑白打印时，部分图表中不同系列的区分度会降低。
- **图表与图注**：数据图表保留英文原版，每张图下方的灰色文字为中文图注，概括该图的结论与关键数字。
- **引用**：正文中的灰色上标（如 S2031）为来源编号，完整书目见卷五附录“参考文献”。
- **数据时效**：截至 {AS_OF}。

## 各册目录

{chr(10).join(details)}

## 重新生成

在仓库根目录运行 `make zh-pdf`（或 `python3 scripts/build/zh_pdf.py [vol1 …]`）。需要 Chromium（Playwright）、
Noto CJK 字体以及 `npm ci` 安装的 Mermaid 渲染工具；中间文件写入 `.zh_pdf_build/`（不纳入版本库）。
"""
    out = OUT / "README.md"
    out.write_text(text, encoding="utf-8")
    return out


def main(argv):
    want = [a for a in argv if not a.startswith("-")]
    if "--index-only" in argv:
        print(f"wrote {write_index().relative_to(REPO)}")
        return 0
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    for key, vol_title, vol_sub, groups in volumes():
        if want and not any(key.startswith(w) for w in want):
            continue
        jobs: dict = {}
        sections, toc = build_volume(key, vol_title, vol_sub, groups, jobs)
        jf = BUILD / f"{key}-mermaid.json"
        jf.write_text(json.dumps([{"id": k, "code": v} for k, v in jobs.items()]), encoding="utf-8")
        subprocess.run(["node", str(REPO / "scripts/build/mermaid_render.mjs"), str(jf), str(BUILD / "mmd")], check=True)
        first = render(key, vol_title, vol_sub, sections, toc, None)
        pages = page_numbers(first, [m for _, _, m in toc])
        final = render(key, vol_title, vol_sub, sections, toc, pages)
        fix_outline(final)
        target = OUT / f"NVIDIA-deep-dive-zh-{key}.pdf"
        target.write_bytes(final.read_bytes())
        n_pages = len(PdfReader(str(target)).pages)
        size = target.stat().st_size / 1e6
        missing = [t for _, t, m in toc if m not in pages]
        results.append((key, vol_title, n_pages, size, len(toc), missing))
        print(f"{key}: {n_pages} pages, {size:.1f} MB, {len(toc)} chapters, toc misses: {len(missing)}")
    print(f"wrote {write_index().relative_to(REPO)}")
    (BUILD / "results.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
