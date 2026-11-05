#!/usr/bin/env python3
"""Rewrite the alt text of every embedded catalog chart (![alt](…/assets/charts/<id>.svg)) to the alt text
registered with the chart in assets/charts/catalog.json, so embeds never drift from the chart they show.
Usage: sync_alt.py [--check] [files...]"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import REPO, is_content, md_files, rel, split_code  # noqa: E402

EMBED = re.compile(r"!\[((?:[^\[\]]|\[[^\]]*\])*)\]\(([^)\s]*assets/charts/([A-Za-z0-9\-]+)\.svg)\)")


def main(argv):
    check = "--check" in argv
    cat = {m["id"]: m for m in json.loads((REPO / "assets/charts/catalog.json").read_text())}
    files = [Path(a).resolve() for a in argv if not a.startswith("--")] or [p for p in md_files() if is_content(p)]
    changed = []
    for p in files:
        text = p.read_text(encoding="utf-8")

        def fix(m):
            cid = m.group(3)
            alt = cat.get(cid, {}).get("alt")
            if not alt:
                return m.group(0)
            alt = alt.replace("[", "(").replace("]", ")")
            return f"![{alt}]({m.group(2)})"
        out = "".join(seg if code else EMBED.sub(fix, seg) for seg, code in split_code(text))
        if out != text:
            changed.append(rel(p))
            if not check:
                p.write_text(out, encoding="utf-8")
    if check and changed:
        print("sync_alt: embeds with stale alt text (run `make build`):", *changed, sep="\n  - ")
        return 1
    print(f"sync_alt: {len(changed)} file(s) {'would change' if check else 'updated'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
