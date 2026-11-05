#!/usr/bin/env python3
"""Normalise content Markdown so authors can write simple tokens and GitHub still renders links.

Transformations (never inside fenced code or inline code):
  1. Root-relative links  ](/assets/charts/x.svg)  ->  ](../../assets/charts/x.svg)
     (also <img src="/..."> and <a href="/...">)
  2. Glossary scheme      [HBM](glossary:hbm)     ->  [HBM](../../glossary.md#hbm)
  3. Citations            [S2031]                 ->  [[S2031]](../../sources/bibliography.md#s2031)
  4. Regenerates everything after the '## 📚 Sources' heading from the citations on the page.

Usage: normalize.py [--check] [files...]   (--check: exit 1 if any file would change)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CITE_RE, ANY_CITE_RE, SOURCES_HEADING, SOURCES_MARKER, REPO, is_content,  # noqa: E402
                    md_files, read_registry, rel, relpath_to, split_code)

LINK_ROOT_RE = re.compile(r"(\]\()(/[^/)\s][^)\s]*)")
HTML_ROOT_RE = re.compile(r"((?:src|href)=\")(/[^/\"][^\"]*)")
GLOSS_RE = re.compile(r"(\]\()glossary:([a-z0-9\-]+)\)")


def transform_text(seg: str, path: Path) -> str:
    seg = LINK_ROOT_RE.sub(lambda m: m.group(1) + relpath_to(m.group(2), path), seg)
    seg = HTML_ROOT_RE.sub(lambda m: m.group(1) + relpath_to(m.group(2), path), seg)
    gl = relpath_to("glossary.md", path)
    seg = GLOSS_RE.sub(lambda m: f"{m.group(1)}{gl}#{m.group(2)})", seg)
    bib = relpath_to("sources/bibliography.md", path)
    seg = CITE_RE.sub(lambda m: f"[[S{m.group(1)}]]({bib}#s{m.group(1)})", seg)
    return seg


def sources_block(cited: list[str], registry: dict[str, dict], path: Path) -> str:
    bib = relpath_to("sources/bibliography.md", path)
    lines = [SOURCES_HEADING, "", SOURCES_MARKER, ""]
    if not cited:
        lines.append("_No citations on this page yet._")
    for sid in cited:
        row = registry.get(sid)
        if not row:
            lines.append(f"- **{sid}** — ⚠️ not found in sources/registry (fix before publishing)")
            continue
        title = row.get("title", "").replace("|", "/")
        pub = row.get("publisher", "")
        author = row.get("author", "")
        date = row.get("date", "")
        url = row.get("url", "")
        who = f"{pub}" + (f" ({author})" if author else "")
        lines.append(f"- [**{sid}**]({bib}#{sid.lower()}) {who}, *{title}*, {date}. [Link]({url})")
    return "\n".join(lines) + "\n"


def normalize(path: Path, registry: dict[str, dict]) -> str:
    text = path.read_text(encoding="utf-8")
    head, sep, _tail = text.partition("\n" + SOURCES_HEADING)
    body = head if sep else text
    out = "".join(seg if code else transform_text(seg, path) for seg, code in split_code(body))
    if sep:
        cited: list[str] = []
        for seg, code in split_code(out):
            if code:
                continue
            for m in ANY_CITE_RE.finditer(seg):
                sid = f"S{m.group(1)}"
                if sid not in cited:
                    cited.append(sid)
        cited.sort(key=lambda s: int(s[1:]))
        out = out.rstrip("\n") + "\n\n" + sources_block(cited, registry, path)
    return out


def main(argv: list[str]) -> int:
    check = "--check" in argv
    files = [Path(a).resolve() for a in argv if not a.startswith("--")]
    if not files:
        files = [p for p in md_files() if is_content(p)]
    registry, _ = read_registry()
    changed = []
    for p in files:
        if not is_content(p):
            continue
        new = normalize(p, registry)
        if new != p.read_text(encoding="utf-8"):
            changed.append(rel(p))
            if not check:
                p.write_text(new, encoding="utf-8")
    if check and changed:
        print("normalize: these files are not normalised (run `make build`):")
        for c in changed:
            print("  -", c)
        return 1
    print(f"normalize: {'checked' if check else 'processed'} {len(files)} files, "
          f"{len(changed)} {'would change' if check else 'updated'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
