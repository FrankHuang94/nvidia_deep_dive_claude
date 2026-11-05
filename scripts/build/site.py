#!/usr/bin/env python3
"""Assemble the optional MkDocs site: copy content Markdown + assets into .site_src/ (MkDocs cannot
use the repo root as docs_dir), so `mkdocs build` can render it with interactive charts."""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO, md_files, rel  # noqa: E402

DST = REPO / ".site_src"


def main():
    if DST.exists():
        shutil.rmtree(DST)
    DST.mkdir()
    for p in md_files():
        r = rel(p)
        if r.startswith(("node_modules/", ".github/")):
            continue
        out = DST / ("index.md" if r == "README.md" else r)
        out.parent.mkdir(parents=True, exist_ok=True)
        text = p.read_text(encoding="utf-8").replace("](README.md", "](index.md")
        out.write_text(text, encoding="utf-8")
    for d in ("assets", "data"):
        if (REPO / d).exists():
            shutil.copytree(REPO / d, DST / d, dirs_exist_ok=True)
    print(f"site: assembled {DST.relative_to(REPO)}")


if __name__ == "__main__":
    main()
