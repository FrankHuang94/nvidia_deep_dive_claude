#!/usr/bin/env python3
"""Citation integrity:
  - sources/registry/*.csv parse, ids unique, url/title present
  - every [S…] cited in content resolves to the registry
  - every data/*.csv has a source_id column whose ids all resolve, and a valid confidence column
  - bibliography.md, glossary.md and normalised pages are fresh (delegates to the build scripts' --check)
  - every content page has a '## 🎯 Corp Dev Lens' and a '## 📚 Sources' section (pages with status >= drafted)
"""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ANY_CITE_RE, REPO, SOURCES_HEADING, is_content, md_files, read_registry, rel, split_code  # noqa: E402
from common_visuals import manifest, unit_files  # noqa: E402

CONF = {"confirmed", "reported", "estimate", "speculative"}


def main(argv):
    errors: list[str] = []
    reg, reg_errors = read_registry()
    errors += reg_errors
    # cited ids resolve
    for p in md_files():
        if not is_content(p):
            continue
        text = p.read_text(encoding="utf-8").split("\n" + SOURCES_HEADING)[0]
        for seg, code in split_code(text):
            if code:
                continue
            for m in ANY_CITE_RE.finditer(seg):
                sid = f"S{m.group(1)}"
                if sid not in reg:
                    errors.append(f"{rel(p)}: citation {sid} not in sources/registry")
    # data csvs
    for f in sorted((REPO / "data").glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            cols = reader.fieldnames or []
            if "source_id" not in cols:
                errors.append(f"{rel(f)}: missing source_id column")
                continue
            for n, row in enumerate(reader, start=2):
                ids = [s for s in re.split(r"[;,\s]+", (row.get("source_id") or "").strip()) if s]
                if not ids:
                    errors.append(f"{rel(f)}:{n}: empty source_id")
                for sid in ids:
                    if sid not in reg:
                        errors.append(f"{rel(f)}:{n}: source_id {sid} not in registry")
                if "confidence" in cols:
                    c = (row.get("confidence") or "").strip().lower()
                    if c not in CONF:
                        errors.append(f"{rel(f)}:{n}: confidence {c!r} not in {sorted(CONF)}")
    # required end sections on drafted+ units
    m = manifest()
    enforce = set(m.get("enforce_statuses", []))
    for u in m["units"]:
        if u.get("status") not in enforce:
            continue
        for f in unit_files(u):
            t = f.read_text(encoding="utf-8")
            if "## 🎯 Corp Dev Lens" not in t and u.get("type") != "synthesis":
                errors.append(f"{rel(f)}: missing '## 🎯 Corp Dev Lens' section")
            if SOURCES_HEADING not in t:
                errors.append(f"{rel(f)}: missing '{SOURCES_HEADING}' section")
    # freshness of generated files
    build = REPO / "scripts" / "build"
    for script in ("bibliography.py", "glossary.py", "normalize.py"):
        r = subprocess.run([sys.executable, str(build / script), "--check"], capture_output=True, text=True)
        if r.returncode != 0:
            errors.append(r.stdout.strip() or r.stderr.strip())
    if errors:
        print(f"check_citations: {len(errors)} problem(s)")
        for e in errors[:300]:
            print("  ✗", e)
        return 1
    print(f"check_citations: OK ({len(reg)} sources in registry)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
