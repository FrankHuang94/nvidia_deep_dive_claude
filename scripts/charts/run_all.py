#!/usr/bin/env python3
"""Regenerate every chart: imports each scripts/charts/ch_*.py module, runs its @register builders,
then writes assets/charts/catalog.json + CATALOG.md.  Usage: run_all.py [substring-filter]"""
from __future__ import annotations

import importlib
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import style  # noqa: E402


def main(argv):
    filt = argv[0] if argv else None
    failures = []
    for mod_path in sorted(HERE.glob("ch_*.py")):
        name = mod_path.stem
        before = len(style.BUILDERS)
        try:
            importlib.import_module(name)
        except Exception:
            failures.append((name, traceback.format_exc()))
            continue
        for fn in style.BUILDERS[before:]:
            if filt and filt not in fn.__name__ and filt not in name:
                continue
            try:
                fn()
            except Exception:
                failures.append((f"{name}.{fn.__name__}", traceback.format_exc()))
    if not filt:
        # keep catalog complete: include charts registered this run only (full run)
        style.write_catalog()
    else:
        # partial run: merge with the existing catalog
        import json
        cat_path = style.OUT_SVG / "catalog.json"
        old = json.loads(cat_path.read_text()) if cat_path.exists() else []
        new_ids = {c.id for c in style.REGISTRY}
        keep = [m for m in old if m["id"] not in new_ids]
        merged = keep + [c.to_meta() for c in style.REGISTRY]

        class _C:  # minimal shim so write_catalog() can be reused
            def __init__(self, m):
                self.m = m
                self.id = m["id"]

            def to_meta(self):
                return self.m
        style.REGISTRY[:] = [_C(m) for m in merged]
        style.write_catalog()
    print(f"charts: {len(style.REGISTRY)} in catalog; {len(failures)} failure(s)")
    for name, tb in failures:
        print(f"\n✗ {name}\n{tb}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
