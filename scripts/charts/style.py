"""Shared plotting helper: every chart in the repo goes through this module.

Usage (inside a chart module in scripts/charts/, e.g. ch_gpu.py):

    from style import Chart, load, entity_color, NV, GEN_PAST, hatch_future, register

    @register
    def flops_by_precision():
        c = Chart(
            id="02-flops-by-precision-log",
            title="Peak FP4 compute per GPU rose ~X× from Hopper to Rubin",   # takeaway, not topic
            subtitle="Dense peak PFLOPS per GPU package by number format (log scale)",
            alt="Log-scale line chart: dense PFLOPS per GPU ... (state takeaway + key numbers)",
            data=["gpu_product_specs.csv"],
            chapters=["02", "17"],
            source="NVIDIA datasheets and keynotes",
            source_ids=["S101", "S102"],
        )
        df = load("gpu_product_specs.csv")
        fig, ax = c.figure()
        ...draw with matplotlib...
        c.save(fig, ax, ylabel="PFLOPS (log scale)", logy=True)
        c.save_plotly(plotly_figure)   # optional interactive twin

Rules enforced here (see docs/STYLE_GUIDE.md): takeaway title, subtitle, unit-labeled axes,
source + as-of footer, LOG SCALE badge, white background, deterministic SVG output, alt text
registered for the Markdown embed and the chart catalog.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
OUT_SVG = REPO / "assets" / "charts"
OUT_HTML = REPO / "assets" / "interactive"

# The "as of" date stamped on every chart. Bump it on a data refresh (or set CHART_ASOF).
AS_OF = os.environ.get("CHART_ASOF", "2026-11-05")

# --------------------------------------------------------------------------------------
# Palette (fixed per entity; validated - see docs/STYLE_GUIDE.md section 5)
# --------------------------------------------------------------------------------------
NV = "#5F9E00"          # NVIDIA green (deepened for contrast on white)
NV_DARK = "#3F6B00"     # NVIDIA text/outline
GEN_PAST = "#A9CC73"    # tint for past NVIDIA generations
ENTITY_COLORS = {
    "nvidia": NV,
    "amd": "#C4314B",
    "google": "#2A78D6",
    "aws": "#C98500",
    "microsoft": "#0F9FB0",
    "meta": "#6250D6",
    "broadcom": "#E0609A",
    "huawei": "#9B3C9E",
    "intel": "#4FA3E0",
    "qualcomm": "#3C4FC4",
    "marvell": "#B0651A",
    "startups": "#7A7A7A",
    "other": "#B5B5B5",
}
ALIASES = {
    "nvda": "nvidia", "tpu": "google", "google tpu": "google", "alphabet": "google",
    "amazon": "aws", "trainium": "aws", "inferentia": "aws", "maia": "microsoft", "msft": "microsoft",
    "mtia": "meta", "avgo": "broadcom", "ascend": "huawei", "gaudi": "intel", "qcom": "qualcomm",
    "mrvl": "marvell", "cerebras": "startups", "groq": "startups", "sambanova": "startups",
    "tenstorrent": "startups", "d-matrix": "startups", "etched": "startups", "startup": "startups",
    "cambricon": "other", "industry": "other",
}
INK = {
    "title": "#0B0B0B",
    "text": "#52514E",
    "muted": "#898781",
    "grid": "#E1E0D9",
    "base": "#C3C2B7",
    "bg": "#FFFFFF",
}
SEQ_BLUE = ["#CDE2FB", "#9EC5F4", "#86B6EF", "#5598E7", "#3987E5", "#256ABF", "#1C5CAB", "#104281"]
DIVERGING = ("#256ABF", "#F0EFEC", "#C4314B")
VERDICT_COLORS = {"leads": "#B7E1A1", "parity": "#FBE6A2", "behind": "#F4C7C3", "different": "#C6DAF7"}
VERDICT_EMOJI = {"leads": "🟩", "parity": "🟨", "behind": "🟥", "different": "🟦"}
CONF_LABEL = {"confirmed": "🟢 Confirmed", "reported": "🟡 Reported", "estimate": "Est.",
              "speculative": "🔴 Speculative"}


def entity_color(name: str) -> str:
    """Fixed color for a company/entity name (case-insensitive, with aliases)."""
    key = str(name).strip().lower()
    key = ALIASES.get(key, key)
    if key in ENTITY_COLORS:
        return ENTITY_COLORS[key]
    for k, v in ENTITY_COLORS.items():
        if key.startswith(k):
            return v
    for alias, k in ALIASES.items():
        if alias in key:
            return ENTITY_COLORS[k]
    return ENTITY_COLORS["other"]


# --------------------------------------------------------------------------------------
# Matplotlib defaults
# --------------------------------------------------------------------------------------
def _setup_mpl() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "svg.fonttype": "path",          # text rendered as paths: identical everywhere
        "svg.hashsalt": "nvda-deep-dive",  # deterministic ids -> no git churn
        "figure.facecolor": INK["bg"],
        "axes.facecolor": INK["bg"],
        "savefig.facecolor": INK["bg"],
        "axes.edgecolor": INK["base"],
        "axes.labelcolor": INK["text"],
        "axes.labelsize": 10,
        "axes.titlesize": 15,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": INK["grid"],
        "grid.linewidth": 0.7,
        "grid.linestyle": "-",
        "xtick.color": INK["text"],
        "ytick.color": INK["text"],
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "lines.linewidth": 2.0,
        "lines.markersize": 7,
        "hatch.color": "#FFFFFF",
        "hatch.linewidth": 1.0,
        "text.parse_math": False,        # '$' is a currency sign here, never mathtext
    })


_setup_mpl()

_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def _plain_log(value, _pos=None) -> str:
    """Format log-axis ticks as plain numbers: 0.01, 0.1, 1, 10, 100, 1k, 10k, 1M, 1B, 1T; values
    beyond 10^15 or below 10^-3 as powers of ten with superscripts (e.g. 10²⁶)."""
    import math
    if value <= 0:
        return ""
    exp = math.floor(math.log10(value) + 1e-9)
    if exp >= 15 or exp < -3:
        mant = value / 10 ** exp
        base = f"10{str(exp).translate(_SUP)}"
        return base if abs(mant - 1) < 1e-6 else f"{mant:g}×{base}"
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
        if value >= div:
            return f"{value / div:g}{suf}"
    return f"{value:g}"


from matplotlib.ticker import FuncFormatter, NullFormatter  # noqa: E402

PLAIN_LOG = FuncFormatter(_plain_log)
NULL_FMT = NullFormatter()


# --------------------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------------------
def load(name: str, **kw) -> pd.DataFrame:
    """Load a CSV from data/ (no comment lines; the data dictionary lives in data/README.md)."""
    path = DATA / name
    return pd.read_csv(path, **kw)


def sources_of(df: pd.DataFrame) -> list[str]:
    """Unique source ids used by the rows of a dataframe (column 'source_id', ';'-separated)."""
    ids: list[str] = []
    if "source_id" not in df.columns:
        return ids
    for cell in df["source_id"].dropna().astype(str):
        for sid in re.split(r"[;,\s]+", cell):
            if sid and sid not in ids:
                ids.append(sid)
    return ids


# --------------------------------------------------------------------------------------
# Chart object
# --------------------------------------------------------------------------------------
REGISTRY: list["Chart"] = []
BUILDERS: list[Callable[[], None]] = []


def register(fn: Callable[[], None]) -> Callable[[], None]:
    """Decorator: mark a function as a chart builder (run by run_all.py)."""
    BUILDERS.append(fn)
    return fn


@dataclass
class Chart:
    id: str
    title: str
    subtitle: str
    alt: str
    data: list[str]
    chapters: list[str]
    source: str
    source_ids: list[str] = field(default_factory=list)
    kind: str = "data"          # "data" = generated from data/*.csv (counts toward the 40% rule)
    asof: str = AS_OF
    note: str | None = None      # optional extra footer note (e.g. "Hatched = estimate")
    has_html: bool = False

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z\-]+", self.id):
            raise ValueError(f"bad chart id {self.id!r}")
        if len(self.alt) < 40:
            raise ValueError(f"{self.id}: alt text must state the takeaway (>= 40 chars)")
        if not self.title or len(self.title.split()) < 4:
            raise ValueError(f"{self.id}: title must be a takeaway sentence")

    # ---- matplotlib ------------------------------------------------------------------
    def figure(self, width: float = 10.0, height: float = 5.8, **subplot_kw):
        fig, ax = plt.subplots(figsize=(width, height), **subplot_kw)
        return fig, ax

    def figure_grid(self, nrows: int, ncols: int, width: float = 11.0, height: float = 6.5, **kw):
        fig, axes = plt.subplots(nrows, ncols, figsize=(width, height), **kw)
        return fig, axes

    def save(self, fig, ax=None, *, xlabel: str | None = None, ylabel: str | None = None,
             logy: bool = False, logx: bool = False, legend: bool | str = "auto",
             top: float | None = None, bottom: float | None = None) -> Path:
        """Apply chrome (title, subtitle, labels, footer, badges) and write the SVG."""
        axes = [ax] if ax is not None and not isinstance(ax, (list, tuple)) else (ax or [])
        try:
            import numpy as np  # local import
            if hasattr(ax, "flat"):
                axes = list(np.ravel(ax))
        except Exception:  # pragma: no cover
            pass
        main = axes[0] if axes else None
        if main is not None:
            if xlabel is not None:
                main.set_xlabel(xlabel)
            if ylabel is not None:
                main.set_ylabel(ylabel)
            if logy:
                if main.get_yscale() != "log":
                    main.set_yscale("log")
                if ylabel and "log" not in ylabel.lower():
                    main.set_ylabel(f"{ylabel} (log scale)")
            if logx:
                if main.get_xscale() != "log":
                    main.set_xscale("log")
                if xlabel and "log" not in xlabel.lower():
                    main.set_xlabel(f"{xlabel} (log scale)")
            if legend == "auto":
                handles, labels = main.get_legend_handles_labels()
                if len([lab for lab in labels if not lab.startswith("_")]) >= 2:
                    main.legend(loc="best")
            for a in axes:
                if a.name == "rectilinear":
                    a.tick_params(length=0)
        # Plain tick labels on every log axis (mathtext is disabled, so matplotlib's default
        # LogFormatterSciNotation would print raw '$\\mathdefault{10^{2}}$' strings).
        from matplotlib.ticker import LogFormatter
        for a in fig.get_axes():
            if a.name != "rectilinear":
                continue
            for axis, scale, getl, setl in ((a.yaxis, a.get_yscale(), a.get_ylabel, a.set_ylabel),
                                            (a.xaxis, a.get_xscale(), a.get_xlabel, a.set_xlabel)):
                if scale != "log":
                    continue
                # only replace matplotlib's default formatter; respect a module's own formatter
                if isinstance(axis.get_major_formatter(), LogFormatter):
                    axis.set_major_formatter(PLAIN_LOG)
                    axis.set_minor_formatter(NULL_FMT)
                lab = getl()
                if lab and "log" not in lab.lower():  # STYLE_GUIDE 6.5: log scales are always labelled
                    setl(f"{lab} (log scale)")
        # Title block: shrink (never wrap) long titles/subtitles so they cannot collide.
        w_in = fig.get_size_inches()[0]
        t_fs = max(10.0, min(14.5, 14.5 * (8.3 * w_in) / max(len(self.title), 1)))
        s_fs = max(8.0, min(10.5, 10.5 * (11.6 * w_in) / max(len(self.subtitle), 1)))
        fig.text(0.012, 0.985, self.title, ha="left", va="top", fontsize=t_fs, fontweight="bold",
                 color=INK["title"])
        fig.text(0.012, 0.925, self.subtitle, ha="left", va="top", fontsize=s_fs, color=INK["text"])
        if logy or logx:
            fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5,
                     fontweight="bold", color="#FFFFFF",
                     bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))
        # Footer
        ids = " ".join(f"[{s}]" for s in self.source_ids[:6])
        more = " …" if len(self.source_ids) > 6 else ""
        foot = f"Source: data from {self.source} {ids}{more}; chart by repo · As of {self.asof}"
        f_fs = max(6.0, min(8.2, 8.2 * (14.5 * w_in) / max(len(foot), 1)))  # shrink, never clip
        fig.text(0.012, 0.012, foot, ha="left", va="bottom", fontsize=f_fs, color=INK["muted"])
        if self.note:  # own line above the source footer, so long footers never collide with it
            fig.text(0.988, 0.040, self.note, ha="right", va="bottom", fontsize=8.2,
                     color=INK["muted"], style="italic")
        fig.subplots_adjust(top=top or 0.84, bottom=(bottom or 0.13) + (0.03 if self.note else 0.0), left=0.08, right=0.97)
        OUT_SVG.mkdir(parents=True, exist_ok=True)
        out = OUT_SVG / f"{self.id}.svg"
        fig.savefig(out, format="svg", metadata={"Date": None, "Creator": "nvidia-deep-dive"})
        plt.close(fig)
        REGISTRY.append(self)
        return out

    # ---- plotly (interactive twin, and static export for sankey/treemap) --------------
    def plotly_layout(self, pfig, height: int = 560) -> None:
        pfig.update_layout(
            template="plotly_white",
            height=height,
            font=dict(family="DejaVu Sans, Arial, sans-serif", size=12, color=INK["text"]),
            title=dict(text=f"<b>{self.title}</b><br><span style='font-size:12px'>{self.subtitle}</span>",
                       x=0.01, xanchor="left", font=dict(size=16, color=INK["title"])),
            paper_bgcolor=INK["bg"], plot_bgcolor=INK["bg"],
            margin=dict(l=60, r=30, t=90, b=70),
        )
        ids = " ".join(f"[{s}]" for s in self.source_ids[:6])
        pfig.add_annotation(text=f"Source: data from {self.source} {ids}; chart by repo · As of {self.asof}",
                            xref="paper", yref="paper", x=0, y=-0.13, showarrow=False,
                            font=dict(size=10, color=INK["muted"]), xanchor="left")

    def save_plotly(self, pfig, *, static: bool = False, height: int = 560, width: int = 1000) -> None:
        """Write assets/interactive/<id>.html (plotly.js from CDN). If static=True, also write
        the SVG via kaleido (use for sankey/treemap that matplotlib draws poorly)."""
        self.plotly_layout(pfig, height=height)
        OUT_HTML.mkdir(parents=True, exist_ok=True)
        pfig.write_html(OUT_HTML / f"{self.id}.html", include_plotlyjs="cdn", full_html=True,
                        config={"displaylogo": False})
        self.has_html = True
        if static:
            os.environ.setdefault("BROWSER_PATH", "/opt/pw-browsers/chromium")
            OUT_SVG.mkdir(parents=True, exist_ok=True)
            pfig.write_image(OUT_SVG / f"{self.id}.svg", format="svg", width=width, height=height)
            if self not in REGISTRY:
                REGISTRY.append(self)

    def to_meta(self) -> dict:
        return {
            "id": self.id, "title": self.title, "subtitle": self.subtitle, "alt": self.alt,
            "data": self.data, "chapters": self.chapters, "source": self.source,
            "source_ids": self.source_ids, "kind": self.kind, "asof": self.asof,
            "svg": f"assets/charts/{self.id}.svg",
            "html": f"assets/interactive/{self.id}.html" if self.has_html else None,
        }


# --------------------------------------------------------------------------------------
# Small drawing helpers shared by chart modules
# --------------------------------------------------------------------------------------
def hatch_future(bar_container, mask: Iterable[bool], hatch: str = "///") -> None:
    """Hatch bars that are roadmap/estimate (mask True)."""
    for patch, m in zip(bar_container.patches, mask):
        if m:
            patch.set_hatch(hatch)
            patch.set_alpha(0.75)


def label_bars(ax, bars, fmt: str = "{:,.0f}", inside: bool = False, fontsize: float = 8.5,
               color: str | None = None) -> None:
    """Value labels on top of bars (use selectively)."""
    for b in bars:
        h = b.get_height()
        if h is None or h != h:  # NaN
            continue
        y = h * (0.5 if inside else 1.0)
        ax.annotate(fmt.format(h), (b.get_x() + b.get_width() / 2, y), ha="center",
                    va="center" if inside else "bottom", fontsize=fontsize,
                    color=color or INK["text"], xytext=(0, 0 if inside else 2),
                    textcoords="offset points")


def end_label(ax, x, y, text: str, color: str, dx: float = 4, fontsize: float = 9) -> None:
    """Direct label at a line end (preferred over legends for <= 4 series)."""
    ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points", va="center",
                fontsize=fontsize, color=color, fontweight="bold")


def axis_break(ax, where: str = "y") -> None:
    """Draw a visible axis-break marker when an axis does not start at zero."""
    d = 0.012
    kw = dict(transform=ax.transAxes, color=INK["text"], clip_on=False, lw=1.2)
    if where == "y":
        ax.plot((-d, +d), (0.02 - d, 0.02 + d), **kw)
        ax.plot((-d, +d), (0.04 - d, 0.04 + d), **kw)


def write_catalog() -> None:
    """Write assets/charts/catalog.json and CATALOG.md from the registry."""
    OUT_SVG.mkdir(parents=True, exist_ok=True)
    metas = sorted((c.to_meta() for c in REGISTRY), key=lambda m: m["id"])
    # de-duplicate by id (last wins)
    dedup = {m["id"]: m for m in metas}
    metas = [dedup[k] for k in sorted(dedup)]
    (OUT_SVG / "catalog.json").write_text(json.dumps(metas, indent=2, ensure_ascii=False) + "\n")
    lines = [
        "# Chart catalog",
        "",
        "Auto-generated by `make charts` from `scripts/charts/`. Every chart is built from `data/*.csv`.",
        "Embed a chart with its registered alt text, e.g. "
        "`![<alt>](/assets/charts/<id>.svg)` (links are normalised by `make build`).",
        "",
        f"Total charts: **{len(metas)}**",
        "",
        "| Chart | Takeaway title | Chapters | Data | Interactive |",
        "|---|---|---|---|---|",
    ]
    for m in metas:
        html = f"[html](../interactive/{m['id']}.html)" if m["html"] else "—"
        lines.append(f"| [`{m['id']}`]({m['id']}.svg) | {m['title']} | {', '.join(m['chapters'])} | "
                     f"{', '.join(m['data'])} | {html} |")
    lines.append("")
    lines.append("## Alt text (copy verbatim into embeds)")
    lines.append("")
    for m in metas:
        lines.append(f"- **{m['id']}**: {m['alt']}")
    (OUT_SVG / "CATALOG.md").write_text("\n".join(lines) + "\n")
