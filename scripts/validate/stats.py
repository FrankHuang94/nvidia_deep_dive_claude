#!/usr/bin/env python3
"""Compute per-unit stats (words, visuals, data charts, sources) and write them into PROGRESS.md
between <!-- STATS:START --> and <!-- STATS:END -->. Usage: stats.py [--write]"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_visuals import REPO, chart_catalog, manifest, unit_stats  # noqa: E402


def table() -> str:
    m = manifest()
    cat = chart_catalog()
    rows = ["| Unit | Title | Phase | Status | Words | Visuals | Charts (data) | Diagrams | Mermaid | Tables | Data-chart share | Sources | QA |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    tw = tv = ts = 0
    all_cited: set[str] = set()
    for u in m["units"]:
        s = unit_stats(u, cat)
        tw += s["words"]
        tv += s["visuals"]
        all_cited |= s["cited"]
        share = f"{s['data_share']:.0%}" if s["visuals"] else "—"
        rows.append(f"| {u['id']} | {u['title']} | {u.get('phase','')} | {u.get('status','planned')} | {s['words']:,} | "
                    f"{s['visuals']} | {len(s['charts'])} ({len(s['data_charts'])}) | {len(s['diagrams'])} | {s['mermaid']} | "
                    f"{s['tables']} | {share} | {len(s['cited'])} | {u.get('qa','pending')} |")
    rows.append(f"| **Total** | | | | **{tw:,}** | **{tv}** | | | | | | **{len(all_cited)}** unique | |")
    rows.append("")
    rows.append(f"Charts in library (`assets/charts/catalog.json`): **{len(cat)}**. "
                "Visual = chart/diagram image, Mermaid block, or table with ≥ 2 rows (unique per unit).")
    return "\n".join(rows)


def main(argv):
    t = table()
    if "--write" in argv:
        p = REPO / "PROGRESS.md"
        s = p.read_text(encoding="utf-8")
        a, b = "<!-- STATS:START -->", "<!-- STATS:END -->"
        if a in s and b in s:
            pre, rest = s.split(a, 1)
            _, post = rest.split(b, 1)
            p.write_text(pre + a + "\n" + t + "\n" + b + post, encoding="utf-8")
            print("stats: PROGRESS.md updated")
        else:
            print("stats: markers not found in PROGRESS.md")
    else:
        print(t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
