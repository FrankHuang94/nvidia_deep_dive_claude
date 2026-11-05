#!/usr/bin/env python3
"""Alt-text check and visual-quota counter.

- Every image embed must have alt text (>= 15 characters, not a filename).
- For each unit in docs/manifest.yml whose status is in `enforce_statuses`, enforce the visual
  quota (and words + data-chart share for layers).
- With --final, also enforce the repository-wide visual total.
Usage: check_visuals.py [--final] [--unit ID] [--quiet]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_visuals import (chart_catalog, is_content, manifest, md_files, page_stats,  # noqa: E402
                            rel, unit_stats)


def main(argv):
    final = "--final" in argv
    only = argv[argv.index("--unit") + 1] if "--unit" in argv else None
    quiet = "--quiet" in argv
    catalog = chart_catalog()
    errors: list[str] = []
    warnings: list[str] = []
    # 1. alt text on every content page
    for p in md_files():
        s = page_stats(p, catalog)
        for alt, target, line in s["images"]:
            if len(alt) < 15 or alt.lower().endswith((".svg", ".png", ".jpg")):
                errors.append(f"{rel(p)}:{line}: image '{target}' needs descriptive alt text (>=15 chars)")
    # 2. quotas
    m = manifest()
    q = m["quotas"]
    enforce = set(m.get("enforce_statuses", []))
    total = 0
    rows = []
    for u in m["units"]:
        if only and str(u["id"]) != only:
            continue
        st = unit_stats(u, catalog)
        total += st["visuals"]
        quota = q.get(u["type"], {})
        need_v = quota.get("visuals", 0)
        need_w = quota.get("words", 0)
        need_share = quota.get("data_share", 0)
        status = u.get("status", "planned")
        enforced = status in enforce
        flag = []
        if st["visuals"] < need_v:
            flag.append(f"visuals {st['visuals']}<{need_v}")
        if need_w and st["words"] < need_w:
            flag.append(f"words {st['words']}<{need_w}")
        if need_share and st["data_share"] < need_share:
            flag.append(f"data-chart share {st['data_share']:.0%}<{need_share:.0%}")
        rows.append((str(u["id"]), status, st["words"], st["visuals"], len(st["data_charts"]), st["data_share"], flag))
        if flag:
            (errors if enforced else warnings).append(f"unit {u['id']} ({status}): " + ", ".join(flag))
    if final and total < q.get("repo_total", 0):
        errors.append(f"repo total visuals {total} < {q['repo_total']}")
    if not quiet:
        print(f"{'unit':<8}{'status':<11}{'words':>7}{'visuals':>9}{'data':>6}{'share':>7}  flags")
        for uid, status, w, v, d, share, flag in rows:
            print(f"{uid:<8}{status:<11}{w:>7}{v:>9}{d:>6}{share:>7.0%}  {'; '.join(flag) if flag else 'ok'}")
        print(f"repo total visuals (counted in manifest units): {total}")
    for w in warnings[:0]:
        print("warn:", w)
    if errors:
        print(f"\ncheck_visuals: {len(errors)} error(s)")
        for e in errors:
            print("  ✗", e)
        return 1
    print("check_visuals: OK (quotas enforced for statuses: " + ", ".join(sorted(enforce)) + ")")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
