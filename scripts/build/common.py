"""Shared helpers for build and validation scripts (stdlib + PyYAML only, so CI stays light)."""
from __future__ import annotations

import csv
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

EXCLUDE_DIRS = {"node_modules", ".git", ".site_src", "site", "__pycache__", ".venv", "venv"}
# Markdown files that are meta/specification documents rather than content pages. They are
# link-checked but not citation-normalised and not counted toward visual quotas.
META_PREFIXES = ("docs/", "assets/", ".github/", "sources/", "scripts/", "diagrams/", "data/")
GENERATED = {"sources/bibliography.md", "glossary.md"}

CITE_RE = re.compile(r"(?<!\[)\[S(\d{1,6})\](?!\(|\])")
LINKED_CITE_RE = re.compile(r"\[\[S(\d{1,6})\]\]\(([^)]*)\)")
ANY_CITE_RE = re.compile(r"\[S(\d{1,6})\]")
SOURCES_HEADING = "## 📚 Sources"
SOURCES_MARKER = ("<!-- Auto-generated from the [S…] citations on this page by `make build`. "
                  "Edit sources/registry/*.csv, not this list. -->")
REGISTRY_FIELDS = ["id", "title", "publisher", "author", "date", "url", "accessed", "type", "notes"]


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO).as_posix()


def md_files(include_meta: bool = True) -> list[Path]:
    out: list[Path] = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDE_DIRS)
        for f in sorted(files):
            if f.endswith(".md"):
                p = Path(root) / f
                r = rel(p)
                if not include_meta and (r.startswith(META_PREFIXES) or r in GENERATED):
                    continue
                out.append(p)
    return out


def is_content(path: Path) -> bool:
    r = rel(path)
    return not (r.startswith(META_PREFIXES) or r in GENERATED)


def split_code(text: str):
    """Yield (segment, is_code) pieces of a Markdown document, where code = fenced blocks and
    inline code spans. Used so transformations never touch code or Mermaid sources."""
    lines = text.split("\n")
    buf: list[str] = []
    in_fence = False
    fence = ""
    pieces: list[tuple[str, bool]] = []

    def flush(is_code: bool):
        if buf:
            pieces.append(("\n".join(buf), is_code))
            buf.clear()

    for i, line in enumerate(lines):
        stripped = line.lstrip()
        m = re.match(r"^(```+|~~~+)", stripped)
        if not in_fence and m:
            flush(False)
            in_fence, fence = True, m.group(1)[:3]
            buf.append(line)
            continue
        if in_fence:
            buf.append(line)
            if stripped.startswith(fence) and stripped.strip() == stripped.strip()[0] * len(stripped.strip()):
                in_fence = False
                flush(True)
            continue
        buf.append(line)
    flush(in_fence)
    # re-join with newlines between pieces
    result: list[tuple[str, bool]] = []
    for idx, (seg, code) in enumerate(pieces):
        tail = "\n" if idx < len(pieces) - 1 else ""
        if code:
            result.append((seg + tail, True))
        else:
            # split inline code spans
            parts = re.split(r"(`+[^`\n]*?`+)", seg + tail)
            for part in parts:
                if not part:
                    continue
                result.append((part, part.startswith("`") and part.endswith("`") and len(part) > 1))
    return result


def fenced_blocks(text: str, lang: str | None = None):
    """Return list of (start_line_no, info, body) for fenced code blocks."""
    out = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^\s*(```+|~~~+)\s*([\w\-]*)", lines[i])
        if m:
            fence, info = m.group(1), m.group(2)
            start = i
            body = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(fence[:3]):
                body.append(lines[i])
                i += 1
            if lang is None or info == lang:
                out.append((start + 1, info, "\n".join(body)))
        i += 1
    return out


def read_registry() -> tuple[dict[str, dict], list[str]]:
    """Read sources/registry/*.csv -> ({'S12': row}, errors)."""
    reg: dict[str, dict] = {}
    errors: list[str] = []
    d = REPO / "sources" / "registry"
    for f in sorted(d.glob("*.csv")):
        with f.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            missing = [c for c in ("id", "title", "publisher", "date", "url", "accessed") if c not in (reader.fieldnames or [])]
            if missing:
                errors.append(f"{rel(f)}: missing columns {missing}")
                continue
            for n, row in enumerate(reader, start=2):
                sid = (row.get("id") or "").strip()
                if not re.fullmatch(r"S\d{1,6}", sid):
                    errors.append(f"{rel(f)}:{n}: bad id {sid!r}")
                    continue
                if sid in reg:
                    errors.append(f"{rel(f)}:{n}: duplicate id {sid} (also in {reg[sid]['_file']})")
                    continue
                if not (row.get("url") or "").strip():
                    errors.append(f"{rel(f)}:{n}: {sid} has no url")
                if not (row.get("title") or "").strip():
                    errors.append(f"{rel(f)}:{n}: {sid} has no title")
                row = {k: (v or "").strip() for k, v in row.items() if k}
                row["_file"] = rel(f)
                reg[sid] = row
    return reg, errors


def relpath_to(target: str, from_file: Path) -> str:
    """Relative link from from_file's directory to repo-root-relative target."""
    target_path = REPO / target.lstrip("/")
    return Path(os.path.relpath(target_path, from_file.parent)).as_posix()


def github_slug(text: str) -> str:
    s = re.sub(r"<[^>]+>", "", text)          # strip html
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # links -> text
    s = s.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s, flags=re.UNICODE)
    return s.replace(" ", "-")


def anchors_in(text: str) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    in_code = False
    for line in text.split("\n"):
        if re.match(r"^\s*(```|~~~)", line):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", line)
        if m:
            base = github_slug(m.group(2))
            n = counts.get(base, 0)
            anchors.add(base if n == 0 else f"{base}-{n}")
            counts[base] = n + 1
    for m in re.finditer(r"<a\s+(?:id|name)=\"([^\"]+)\"", text):
        anchors.add(m.group(1))
    return anchors


def load_yaml(path: Path):
    import yaml  # PyYAML
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)
