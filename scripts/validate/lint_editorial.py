#!/usr/bin/env python3
"""Editorial linter (advisory): checks each content page against the writing standard.

Per page it reports: Executive Take present + bullet count (5–8), worked examples (> [!TIP] …
"Worked example"), Under-the-hood <details> blocks, glossary links, citations, confidence tags,
Corp Dev Lens items (3–6), Sources section last, terminology violations (STYLE_GUIDE §1),
unsourced superlatives, and long direct quotes (> 15 words).

Usage: lint_editorial.py [paths...] [--unit ID] [--strict]
  --strict exits 1 when a page has a structural ERROR (used for drafted+ units in QA).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ANY_CITE_RE, REPO, SOURCES_HEADING, is_content, md_files, rel, split_code  # noqa: E402
from common_visuals import manifest, unit_files  # noqa: E402

TERMS = [  # (regex, preferred)
    (r"\bHBM3e\b", "HBM3E"), (r"\bHBM-4\b", "HBM4"), (r"\bNVL-(72|144|576|36|8)\b", "NVL72 (no hyphen)"),
    (r"\bNVLink(\d)\b", "NVLink N (space)"), (r"\bFY(\d{2})\b(?!\d)", "FY20NN"), (r"\bPFLOP/s\b", "PFLOPS"),
    (r"\bTFLOP/s\b", "TFLOPS"), (r"\bGB200-NVL72\b", "GB200 NVL72"), (r"\bInfiniband\b", "InfiniBand"),
    (r"\bNvidia\b", "NVIDIA"), (r"\bCoWoS-l\b", "CoWoS-L"),
]
SUPERLATIVES = r"\b(unmatched|unrivall?ed|unparalleled|best-in-class|world'?s (?:best|fastest|most)|dominant|dominates|undisputed|insurmountable|revolutionary|game-?changing)\b"


def section(text: str, heading_re: str) -> str:
    m = re.search(heading_re, text, flags=re.M)
    if not m:
        return ""
    rest = text[m.end():]
    n = re.search(r"^## ", rest, flags=re.M)
    return rest[: n.start()] if n else rest


def lint(path: Path) -> tuple[list[str], list[str], dict]:
    text = path.read_text(encoding="utf-8")
    errors, warns = [], []
    prose = "".join(seg for seg, code in split_code(text) if not code)
    body = prose.split("\n" + SOURCES_HEADING)[0]
    exec_take = section(text, r"^## ⚡ The Executive Take\s*$")
    bullets = len(re.findall(r"^\s*[-*] ", exec_take, flags=re.M))
    tips = len(re.findall(r"^> \[!TIP\]\s*\n> \*\*Worked example", text, flags=re.M))
    details = len(re.findall(r"<summary>🔧 Under the hood", text))
    gloss = len(re.findall(r"\]\([^)]*glossary\.md#", body)) + len(re.findall(r"\]\(glossary:", body))
    cites = len(ANY_CITE_RE.findall(body))
    conf = len(re.findall(r"[🟢🟡🔴]", body))
    lens = section(text, r"^## 🎯 Corp Dev Lens\s*$")
    lens_items = len(re.findall(r"^\s*(?:\d+\.|[-*]) ", lens, flags=re.M))
    headings = re.findall(r"^## (.+)$", text, flags=re.M)
    stats = dict(bullets=bullets, tips=tips, details=details, gloss=gloss, cites=cites, conf=conf, lens=lens_items)
    if not exec_take:
        errors.append("missing '## ⚡ The Executive Take'")
    elif not 5 <= bullets <= 8:
        warns.append(f"Executive Take has {bullets} bullets (want 5–8)")
    if tips == 0:
        errors.append("no '> [!TIP]' + '**Worked example' block")
    if details == 0:
        warns.append("no '🔧 Under the hood' <details> block")
    if not lens:
        errors.append("missing '## 🎯 Corp Dev Lens'")
    elif not 3 <= lens_items <= 6:
        warns.append(f"Corp Dev Lens has {lens_items} items (want 3–6)")
    if not headings or not headings[-1].startswith("📚 Sources"):
        errors.append("'## 📚 Sources' is not the last H2")
    if gloss == 0:
        warns.append("no glossary links")
    if cites < 5:
        warns.append(f"only {cites} citations")
    for rx, pref in TERMS:
        for m in re.finditer(rx, body):
            warns.append(f"terminology: '{m.group(0)}' → {pref}")
    for m in re.finditer(SUPERLATIVES, body, flags=re.I):
        line = body[max(0, m.start() - 80): m.end() + 80]
        if not ANY_CITE_RE.search(line):
            warns.append(f"unsourced superlative: '{m.group(0)}'")
    for m in re.finditer(r"[\"“]([^\"”\n]{0,400})[\"”]", body):
        if len(m.group(1).split()) > 15:
            warns.append(f"quote longer than 15 words: “{m.group(1)[:50]}…”")
    return errors, warns, stats


def main(argv):
    strict = "--strict" in argv
    files: list[Path] = []
    if "--unit" in argv:
        uid = argv[argv.index("--unit") + 1]
        for u in manifest()["units"]:
            if str(u["id"]) == uid:
                files = unit_files(u)
    else:
        files = [Path(a).resolve() for a in argv if not a.startswith("--")] or \
                [p for p in md_files() if is_content(p)]
    n_err = 0
    for p in files:
        if not is_content(p) or "Status: planned" in p.read_text(encoding="utf-8")[:400]:
            continue
        errors, warns, s = lint(p)
        n_err += len(errors)
        flag = "✗" if errors else ("!" if warns else "✓")
        print(f"{flag} {rel(p)}  bullets={s['bullets']} tips={s['tips']} details={s['details']} "
              f"gloss={s['gloss']} cites={s['cites']} conf={s['conf']} lens={s['lens']}")
        for e in errors:
            print("    ERROR", e)
        for w in warns[:12]:
            print("    warn ", w)
        if len(warns) > 12:
            print(f"    … {len(warns) - 12} more warnings")
    return 1 if (strict and n_err) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
