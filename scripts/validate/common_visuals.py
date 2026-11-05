"""Visual / word / source counting shared by check_visuals.py and stats.py."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build"))
from common import (ANY_CITE_RE, REPO, SOURCES_HEADING, fence_mask, fenced_blocks, is_content,  # noqa: E402,F401
                    load_yaml, md_files, rel, split_code)

IMG_MD_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG_HTML_RE = re.compile(r"<img\s+[^>]*>", re.I)
ATTR_RE = lambda name: re.compile(name + r"\s*=\s*\"([^\"]*)\"", re.I)  # noqa: E731


def chart_catalog() -> dict[str, dict]:
    p = REPO / "assets" / "charts" / "catalog.json"
    if not p.exists():
        return {}
    return {m["id"]: m for m in json.loads(p.read_text(encoding="utf-8"))}


def page_stats(path: Path, catalog: dict[str, dict] | None = None) -> dict:
    catalog = catalog if catalog is not None else chart_catalog()
    text = path.read_text(encoding="utf-8")
    body = text.split("\n" + SOURCES_HEADING)[0]
    images = []  # (alt, target, line)
    # blank out code (fenced + inline) but keep line structure, so code samples are never counted
    nocode = "".join(("\n" * seg.count("\n")) if code else seg for seg, code in split_code(body))
    for n, line in enumerate(nocode.split("\n"), start=1):
        for m in IMG_MD_RE.finditer(line):
            images.append((m.group(1).strip(), m.group(2), n))
        for m in IMG_HTML_RE.finditer(line):
            tag = m.group(0)
            src = ATTR_RE("src").search(tag)
            alt = ATTR_RE("alt").search(tag)
            images.append(((alt.group(1) if alt else "").strip(), src.group(1) if src else "", n))
    # mermaid + tables + words (skip code for words)
    mermaid = len(fenced_blocks(body, "mermaid"))
    tables = 0
    lines = body.split("\n")
    mask = fence_mask(lines)
    i = 0
    while i < len(lines):
        ln = lines[i]
        if mask[i]:
            i += 1
            continue
        if ln.strip().startswith("|") and i + 1 < len(lines) and \
                re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
            cols = ln.strip().strip("|").count("|") + 1
            j = i + 2
            rows = 0
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows += 1
                j += 1
            if rows >= 2 and cols >= 2:
                tables += 1
            i = j
            continue
        i += 1
    prose = []
    for seg, code in split_code(body):
        if code:
            continue
        seg = re.sub(r"<!--.*?-->", " ", seg, flags=re.S)
        seg = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", seg)
        seg = re.sub(r"\]\([^)]*\)", "]", seg)
        seg = re.sub(r"<[^>]+>", " ", seg)
        seg = re.sub(r"\[\[S\d+\]\]|\[S\d+\]", " ", seg)
        prose.append(seg)
    words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.\-/%$×~]*", " ".join(prose)))
    cited = set()
    for seg, code in split_code(body):
        if not code:
            cited.update(f"S{m.group(1)}" for m in ANY_CITE_RE.finditer(seg))
    charts, diagrams, other_imgs = set(), set(), set()
    data_charts = set()
    for alt, target, _ in images:
        name = Path(target.split("#")[0]).name
        if "assets/charts/" in target:
            charts.add(name)
            cid = name.rsplit(".", 1)[0]
            if catalog.get(cid, {}).get("kind", "data") == "data" and cid in catalog:
                data_charts.add(name)
        elif "assets/diagrams/" in target:
            diagrams.add(name)
        else:
            other_imgs.add(target)
    return {
        "path": rel(path), "images": images, "charts": charts, "data_charts": data_charts,
        "diagrams": diagrams, "other_images": other_imgs, "mermaid": mermaid, "tables": tables,
        "words": words, "cited": cited,
    }


def unit_files(unit: dict) -> list[Path]:
    files: list[Path] = []
    for p in unit.get("paths", []):
        full = REPO / p
        if full.is_dir():
            files += sorted(full.rglob("*.md"))
        elif full.exists():
            files.append(full)
    return files


def unit_stats(unit: dict, catalog=None) -> dict:
    catalog = catalog if catalog is not None else chart_catalog()
    agg = {"files": 0, "words": 0, "charts": set(), "data_charts": set(), "diagrams": set(),
           "mermaid": 0, "tables": 0, "cited": set(), "other_images": set()}
    for f in unit_files(unit):
        s = page_stats(f, catalog)
        agg["files"] += 1
        agg["words"] += s["words"]
        agg["mermaid"] += s["mermaid"]
        agg["tables"] += s["tables"]
        for k in ("charts", "data_charts", "diagrams", "cited", "other_images"):
            agg[k] |= s[k]
    agg["visuals"] = len(agg["charts"]) + len(agg["diagrams"]) + agg["mermaid"] + agg["tables"] + len(agg["other_images"])
    agg["data_share"] = (len(agg["data_charts"]) / agg["visuals"]) if agg["visuals"] else 0.0
    return agg


def manifest() -> dict:
    return load_yaml(REPO / "docs" / "manifest.yml")
