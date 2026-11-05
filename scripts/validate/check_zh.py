#!/usr/bin/env python3
"""Structural parity check between the English pages and the simplified-Chinese reference translation.

For every English content page it checks that a zh-CN counterpart exists, and that the translation keeps
the same skeleton: headings, tables, images, Mermaid blocks, <details> blocks, admonitions (+1 for the
inserted reference-translation NOTE), the multiset of citation tokens, and the Sources list (same S-ids,
same titles). It also flags zh-CN pages with no English original. Exit 1 on any error.

Usage: check_zh.py [-v]
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build"))
from common import REPO, fence_mask, fenced_blocks, md_files, is_content  # noqa: E402

ZH = REPO / "zh-CN"
ZH_ONLY = {"TRANSLATION_NOTES.md", "pdf/README.md"}
NOT_TRANSLATED = {"PROGRESS.md", "CHANGELOG.md", "QA_LOG.md"}
CITE = re.compile(r"\[S(\d{1,6})\]")
SRC_EN = re.compile(r"^## 📚 Sources\s*$", re.M)
SRC_ZH = re.compile(r"^## 📚 来源（Sources）\s*$", re.M)
LINK_TARGET = re.compile(r"\]\([^)]*\)")


def body_and_sources(text: str, zh: bool):
    m = (SRC_ZH if zh else SRC_EN).search(text)
    if not m:
        return text, None
    return text[:m.start()], text[m.end():]


def skeleton(text: str) -> dict:
    lines = text.split("\n")
    mask = fence_mask(lines)
    prose = [l for l, c in zip(lines, mask) if not c]
    return {
        "headings": sum(1 for l in prose if re.match(r"^#{1,6}\s", l)),
        "tables": sum(1 for l in prose if re.match(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", l)),
        "images": sum(len(re.findall(r"!\[", l)) for l in prose),
        "mermaid": len(fenced_blocks(text, "mermaid")),
        "details": sum(len(re.findall(r"<details", l)) for l in prose),
        "admonitions": sum(1 for l in prose if re.match(r"^\s*>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", l)),
    }


def sources_entries(src: str | None) -> list[str]:
    if src is None:
        return []
    out = []
    for line in src.split("\n"):
        if re.match(r"^\s*[-*\d]", line):
            out.append(LINK_TARGET.sub("]()", line.strip()))
    return out


def main(argv) -> int:
    verbose = "-v" in argv
    errors: list[str] = []
    warnings: list[str] = []
    en_pages = [p for p in md_files(include_meta=False) if is_content(p)
                and p.relative_to(REPO).as_posix() not in NOT_TRANSLATED]
    for en in en_pages:
        rel = en.relative_to(REPO).as_posix()
        zh = ZH / rel
        if not zh.exists():
            errors.append(f"{rel}: no zh-CN translation")
            continue
        et, zt = en.read_text(encoding="utf-8"), zh.read_text(encoding="utf-8")
        eb, es = body_and_sources(et, False)
        zb, zs = body_and_sources(zt, True)
        if (es is None) != (zs is None):
            errors.append(f"zh-CN/{rel}: Sources section {'missing' if zs is None else 'unexpected'}")
        ek, zk = skeleton(eb), skeleton(zb)
        ek["admonitions"] += 1  # the inserted reference-translation NOTE
        for key in ek:
            if ek[key] != zk[key]:
                errors.append(f"zh-CN/{rel}: {key} {zk[key]} vs English {ek[key]}")
        ec, zc = CITE.findall(eb), CITE.findall(zb)
        if Counter(ec) != Counter(zc):
            missing = sorted((Counter(ec) - Counter(zc)).elements())
            extra = sorted((Counter(zc) - Counter(ec)).elements())
            errors.append(f"zh-CN/{rel}: citations differ (missing {missing[:8]}, extra {extra[:8]})")
        elif ec != zc and verbose:
            warnings.append(f"zh-CN/{rel}: citation order differs (same set)")
        if sources_entries(es) != sources_entries(zs):
            errors.append(f"zh-CN/{rel}: Sources list differs from English")
        if "本页为英文原文的简体中文参考译文" not in zt:
            errors.append(f"zh-CN/{rel}: reference-translation NOTE missing")
    # The glossary is generated from docs/glossary/*.csv; check the translated copy keeps every anchor.
    eg, zg = REPO / "glossary.md", ZH / "glossary.md"
    if not zg.exists():
        errors.append("glossary.md: no zh-CN translation")
    else:
        ea = re.findall(r'<a id="([^"]+)"', eg.read_text(encoding="utf-8"))
        za = re.findall(r'<a id="([^"]+)"', zg.read_text(encoding="utf-8"))
        if ea != za:
            errors.append(f"zh-CN/glossary.md: term anchors differ ({len(za)} vs English {len(ea)})")
    en_rels = {p.relative_to(REPO).as_posix() for p in en_pages} | {"glossary.md"}
    for zh in sorted(ZH.rglob("*.md")):
        r = zh.relative_to(ZH).as_posix()
        if r not in en_rels and r not in ZH_ONLY:
            errors.append(f"zh-CN/{r}: no English original (stray file?)")
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"check_zh: {'OK' if not errors else 'FAILED'} ({len(en_pages)} English pages, "
          f"{len(errors)} error(s), {len(warnings)} warning(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
