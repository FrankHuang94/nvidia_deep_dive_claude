#!/usr/bin/env python3
"""Check that every internal link and image in every Markdown file resolves (file + anchor).

External http(s) links are not fetched (use --external to HEAD-check them, slow).
Content pages must be normalised: no root-relative '/x' links and no 'glossary:' links remain.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build"))
from common import REPO, anchors_in, is_content, md_files, rel, split_code  # noqa: E402

LINK_RE = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_RE = re.compile(r"<(?:img|a)\s+[^>]*?(?:src|href)=\"([^\"]+)\"", re.I)


def main(argv):
    errors = []
    anchor_cache: dict[Path, set[str]] = {}
    n_links = 0
    for p in md_files():
        text = p.read_text(encoding="utf-8")
        for seg, code in split_code(text):
            if code:
                continue
            for m in list(LINK_RE.finditer(seg)) + list(HTML_RE.finditer(seg)):
                target = m.group(1).strip("<>")
                n_links += 1
                if re.match(r"^(https?:|mailto:|ftp:)", target):
                    continue
                if target.startswith("glossary:") or (target.startswith("/") and not target.startswith("//")):
                    if is_content(p):
                        errors.append(f"{rel(p)}: unnormalised link '{target}' (run `make build`)")
                    continue
                path_part, _, anchor = target.partition("#")
                dest = p if not path_part else (p.parent / unquote(path_part)).resolve()
                if not dest.exists():
                    errors.append(f"{rel(p)}: broken link -> {target}")
                    continue
                if anchor and dest.suffix == ".md":
                    if dest not in anchor_cache:
                        anchor_cache[dest] = anchors_in(dest.read_text(encoding="utf-8"))
                    if anchor not in anchor_cache[dest] and anchor.lower() not in anchor_cache[dest]:
                        errors.append(f"{rel(p)}: missing anchor -> {target}")
    if errors:
        print(f"check_links: {len(errors)} problem(s) in {n_links} links")
        for e in errors[:200]:
            print("  ✗", e)
        return 1
    print(f"check_links: OK ({n_links} links checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
