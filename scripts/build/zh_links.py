#!/usr/bin/env python3
"""Rewrite links in the simplified-Chinese reference translation (zh-CN/) so they resolve.

Translators copy every link target verbatim from the English page, i.e. relative to the English file's
location. This script resolves each target and rewrites it relative to the zh-CN file:
  - `EN:<path>`                → relative link to the English original (titled "English original")
  - a content page with a zh-CN counterpart → the Chinese page (heading anchors that do not exist in
                                 the Chinese page are dropped; <a id> anchors such as glossary slugs are kept)
  - anything else (assets/, sources/bibliography.md, data/, docs/) → the shared English file
Idempotent: safe to run repeatedly.  Usage: zh_links.py [--check]
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO, anchors_in, split_code  # noqa: E402

ZH = REPO / "zh-CN"
LINK = re.compile(r"(!?\[(?:[^\[\]]|\[[^\]]*\])*\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
HTML = re.compile(r"((?:src|href)=\")([^\"]+)(\")")
_anchor_cache: dict[Path, set[str]] = {}


def anchors(p: Path) -> set[str]:
    if p not in _anchor_cache:
        _anchor_cache[p] = anchors_in(p.read_text(encoding="utf-8")) if p.exists() else set()
    return _anchor_cache[p]


def rel(target: Path, from_file: Path) -> str:
    return Path(os.path.relpath(target, from_file.parent)).as_posix()


def resolve(target: str, zh_file: Path, en_file: Path, title: str) -> tuple[str, str]:
    if re.match(r"^(https?:|mailto:|ftp:|#)", target):
        if target.startswith("#") and target[1:] not in anchors(zh_file):
            return "", title  # drop dangling same-page anchor (caller keeps link text)
        return target, title
    if target.startswith("EN:"):
        return rel(REPO / target[3:], zh_file), ' "English original"'
    path_part, _, anchor = target.partition("#")
    zh_dest = (zh_file.parent / path_part).resolve()
    en_dest = (en_file.parent / path_part).resolve()
    dest = zh_dest if zh_dest.exists() else en_dest if en_dest.exists() else None
    if dest is None:
        return target, title
    english_original = 'English original' in title
    try:
        relpath = dest.relative_to(REPO).as_posix()
    except ValueError:
        return target, title
    if not english_original and not relpath.startswith("zh-CN/") and dest.suffix == ".md":
        counterpart = ZH / relpath
        if counterpart.exists():
            dest = counterpart
    if anchor and dest.suffix == ".md" and anchor not in anchors(dest) and anchor.lower() not in anchors(dest):
        anchor = ""  # Chinese headings have different slugs; keep the page link
    return rel(dest, zh_file) + (f"#{anchor}" if anchor else ""), title


def process(zh_file: Path) -> str:
    en_file = REPO / zh_file.relative_to(ZH)
    text = zh_file.read_text(encoding="utf-8")

    def fix_md(m):
        new, title = resolve(m.group(2), zh_file, en_file, m.group(3)[:-1])
        if new == "":  # dangling same-page anchor: keep the text only
            label = m.group(1)[1:-2] if m.group(1).startswith("[") else m.group(1)
            return label if not m.group(1).startswith("!") else m.group(0)
        return f"{m.group(1)}{new}{title})"

    def fix_html(m):
        new, _ = resolve(m.group(2), zh_file, en_file, "")
        return f"{m.group(1)}{new or m.group(2)}{m.group(3)}"

    out = []
    for seg, code in split_code(text):
        if code:
            out.append(seg)
        else:
            seg = LINK.sub(fix_md, seg)
            seg = HTML.sub(fix_html, seg)
            out.append(seg)
    return "".join(out)


def main(argv):
    check = "--check" in argv
    changed = []
    only = [Path(a).resolve() for a in argv if not a.startswith("--")]
    for p in sorted(ZH.rglob("*.md")):
        if "pdf" in p.relative_to(ZH).parts[:1]:
            continue
        if only and p.resolve() not in only:
            continue
        new = process(p)
        if new != p.read_text(encoding="utf-8"):
            changed.append(p.relative_to(REPO).as_posix())
            if not check:
                p.write_text(new, encoding="utf-8")
                _anchor_cache.pop(p, None)
    print(f"zh_links: {len(changed)} file(s) {'would change' if check else 'updated'}")
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
