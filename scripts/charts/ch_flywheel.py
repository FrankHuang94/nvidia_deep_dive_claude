"""Chapter 01 - the NVIDIA flywheel: quantifying each reinforcing loop.

Data: data/financials.csv and data/acquisitions_investments.csv (Phase 1) and
data/01_flywheel_ecosystem.csv (NVIDIA-reported developer-ecosystem counts). Revenue, R&D, gross
margin, purchase-obligation and networking charts already exist in the catalog (ids 00-, 03-, 06-,
13-) and are embedded by the chapter rather than duplicated here.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, label_bars, load, register,
                   sources_of)

CH = ["01"]


def _fin():
    return load("financials.csv")


def _qkey(p: str):
    # 'Q3FY26' -> (26, 3)
    return int(p[-2:]), int(p[1])


def _fy(df, metric):
    d = df[(df.period_type == "FY") & (df.metric == metric)].copy()
    return d.sort_values("period_end")


def _q(df, metric):
    d = df[(df.period_type == "Q") & (df.metric == metric)].copy()
    d["k"] = d.period.map(_qkey)
    return d.sort_values("k")


def _qlabel(p: str) -> str:
    return f"Q{p[1]}\nFY{p[-2:]}"


# --------------------------------------------------------------------------------------
@register
def cuda_developers():
    eco = load("01_flywheel_ecosystem.csv")
    d = eco[eco.metric == "cuda_registered_developers"].copy()
    d["t"] = pd.to_datetime(d.date.astype(str).where(d.date.astype(str).str.len() > 4, d.date.astype(str) + "-06"),
                            format="%Y-%m")
    d = d.sort_values("t")
    first, last = d.iloc[0], d.iloc[-1]
    dl = eco[eco.metric == "cuda_downloads_cumulative"]
    c = Chart(
        id="01-cuda-developers",
        title=f"CUDA developers tripled from {first.value:.0f}M ({first.date}) to ~{last.value:.0f}M, then NVIDIA's count went flat",
        subtitle="Registered CUDA developers as cited by NVIDIA in keynotes, blogs and earnings calls, millions",
        alt=(f"Line chart of NVIDIA-reported CUDA developers: {first.value:.0f} million in {first.date}, 3 million in early "
             f"2022, 4 million in mid 2023, 5 million in mid 2024 and about 6 million in March 2025, with the same "
             f"~6 million cited again in March 2026; cumulative CUDA downloads reached about 40 million by 2023."),
        data=["01_flywheel_ecosystem.csv"], chapters=CH + ["09", "10"],
        source="NVIDIA keynotes, blogs and earnings calls", source_ids=sources_of(pd.concat([d, dl])),
    )
    fig, ax = c.figure(width=10, height=5.6)
    ax.plot(d.t, d.value, color=NV, lw=2.4, marker="o", ms=8, zorder=3)
    for _, r in d.iterrows():
        if r.date in ("2025-02",):
            continue
        ax.annotate(f"{r.value:g}M", (r.t, r.value), xytext=(0, 9), textcoords="offset points", ha="center",
                    fontsize=9, color=NV_DARK, fontweight="bold")
    ax.annotate("Same ~6M cited at\nGTC 2025 and GTC 2026", (d.t.iloc[-1], last.value), xytext=(-150, -55),
                textcoords="offset points", fontsize=8.8, color=INK["text"],
                arrowprops=dict(arrowstyle="-", color=INK["muted"]))
    for _, r in dl.iterrows():
        pass
    ax.text(d.t.iloc[0], 6.6, "Cumulative CUDA downloads: ~33M (Mar 2022) → ~40M (May 2023)", fontsize=8.8,
            color=INK["text"])
    ax.set_ylim(0, 7.2)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    c.save(fig, ax, xlabel="Date of NVIDIA statement", ylabel="Registered CUDA developers (millions)")


# --------------------------------------------------------------------------------------
CATEGORY = {
    "CoreWeave capacity backstop": "Neoclouds & capacity",
    "Intel": "Suppliers & platform partners",
    "Wayve (LOI)": "AI labs & model builders",
    "Enfabrica": "Acquihire + licence",
    "Lambda GPU lease-back": "Neoclouds & capacity",
    "xAI (2025 raise)": "AI labs & model builders",
    "Poolside": "AI labs & model builders",
    "Nokia": "Suppliers & platform partners",
    "Anthropic": "AI labs & model builders",
    "Synopsys": "Suppliers & platform partners",
    "Groq": "Acquihire + licence",
    "CoreWeave (2026)": "Neoclouds & capacity",
    "OpenAI (2026 round)": "AI labs & model builders",
}
CAT_COLORS = {
    "AI labs & model builders": SEQ_BLUE[6],
    "Neoclouds & capacity": SEQ_BLUE[3],
    "Suppliers & platform partners": "#7A7A7A",
    "Acquihire + licence": NV,
}


@register
def capital_deployment():
    df = load("acquisitions_investments.csv")
    df["d"] = pd.to_datetime(df.announce_date.astype(str).str.slice(0, 7), format="%Y-%m", errors="coerce")
    sel = df[(df.d >= "2025-09-01") & df.amount_usd_m.notna() & (df.amount_usd_m >= 400)
             & (df.status != "superseded") & df.counterparty.isin(CATEGORY.keys())].copy()
    sel["cat"] = sel.counterparty.map(CATEGORY)
    sel = sel.sort_values("amount_usd_m")
    total = sel.amount_usd_m.sum() / 1000
    fin = _fin()
    ni = float(fin[(fin.period == "FY2026") & (fin.metric == "net_income")].value.iloc[0])
    by_cat = sel.groupby("cat").amount_usd_m.sum() / 1000
    c = Chart(
        id="01-capital-deployment",
        title=f"~${total:.0f}B pledged to labs, neoclouds and partners in six months: ~{total/ni:.0%} of FY2026 net income",
        subtitle="Announced equity stakes, licences and capacity backstops ≥ $0.4B, Sep 2025–Feb 2026, US$ B (hatched = 'up to' or press-reported)",
        alt=(f"Horizontal bar chart of NVIDIA's largest commitments from September 2025 to February 2026 totalling about "
             f"${total:.0f}B: OpenAI about $30B, Groq licence about $20B, Anthropic up to $10B, CoreWeave backstop $6.3B, "
             f"Intel $5B and others; AI labs account for about ${by_cat.get('AI labs & model builders', 0):.0f}B. "
             f"The total equals about {total/ni:.0%} of FY2026 net income of ${ni:.0f}B."),
        data=["acquisitions_investments.csv", "financials.csv"], chapters=CH + ["13", "18"],
        source="NVIDIA, partner releases and filings; press reports", source_ids=sources_of(sel),
    )
    fig, ax = c.figure(width=10.5, height=6.2)
    y = np.arange(len(sel))
    cols = [CAT_COLORS[k] for k in sel.cat]
    bars = ax.barh(y, sel.amount_usd_m / 1000, color=cols, height=0.66, zorder=2)
    for b, basis, conf in zip(bars.patches, sel.amount_basis, sel.confidence):
        if basis in ("up-to", "reported") or conf == "reported":
            b.set_hatch("//")
    names = [n.replace(" (LOI)", " (letter of intent)") for n in sel.counterparty]
    for i, (v, basis, nm) in enumerate(zip(sel.amount_usd_m / 1000, sel.amount_basis, names)):
        lab = f"${v:.1f}B" if v < 10 else f"${v:.0f}B"
        if basis == "up-to":
            lab = "up to " + lab
        ax.annotate(f"{nm}  {lab}", (v, i), xytext=(5, 0), textcoords="offset points", va="center", fontsize=8.8,
                    color=INK["title"])
    ax.set_yticks([])
    ax.set_xlim(0, sel.amount_usd_m.max() / 1000 * 1.55)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    from matplotlib.patches import Patch
    handles = [Patch(color=CAT_COLORS[k], label=f"{k} (${by_cat.get(k, 0):.0f}B)") for k in CAT_COLORS if k in by_cat]
    ax.legend(handles=handles, loc="lower right", fontsize=9)
    c.save(fig, ax, xlabel="Announced amount (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
@register
def loop_engines():
    """FY2024 -> FY2026 growth multiple of each loop's engine metric (one bar per loop)."""
    fin = _fin()
    eco = load("01_flywheel_ecosystem.csv")

    def fy(metric, p):
        return float(fin[(fin.period == p) & (fin.metric == metric) & (fin.period_type == "FY")].value.iloc[0])

    dev = eco[eco.metric == "cuda_registered_developers"].set_index("date")
    rows = [
        ("②/④ Supply & capacity commitments (scale + capital loops)", fy("purchase_obligations", "FY2024"),
         fy("purchase_obligations", "FY2026"), SEQ_BLUE[6]),
        ("③ Full stack: data-center networking revenue", fy("revenue_dc_networking", "FY2024"),
         fy("revenue_dc_networking", "FY2026"), SEQ_BLUE[4]),
        ("Hub: total revenue", fy("revenue_total", "FY2024"), fy("revenue_total", "FY2026"), NV),
        ("② Scale / R&D: R&D expense", fy("rd_expense", "FY2024"), fy("rd_expense", "FY2026"), SEQ_BLUE[3]),
        ("① Developers: registered CUDA developers", float(dev.loc["2023-05", "value"]),
         float(dev.loc["2025-03", "value"]), GEN_PAST),
    ]
    rows = sorted(rows, key=lambda r: r[2] / r[1])
    mult = {r[0]: r[2] / r[1] for r in rows}
    hi, lo = rows[-1], rows[0]
    used = pd.concat([
        fin[(fin.period_type == "FY") & fin.period.isin(["FY2024", "FY2026"]) &
            fin.metric.isin(["purchase_obligations", "revenue_dc_networking", "revenue_total", "rd_expense"])],
        eco[eco.metric == "cuda_registered_developers"]])
    c = Chart(
        id="01-loop-engines",
        title=f"Since FY2024 commitments grew {mult[hi[0]]:.1f}× but CUDA developers only {mult[lo[0]]:.1f}×",
        subtitle="Growth multiple FY2024 → FY2026 of each loop's engine metric (developers: May 2023 → Mar 2025 NVIDIA statements)",
        alt=(f"Horizontal bar chart of growth multiples from FY2024 to FY2026: supply and capacity commitments "
             f"{mult[rows[-1][0]]:.1f} times (${rows[-1][1]:.1f}B to ${rows[-1][2]:.1f}B), networking revenue and total "
             f"revenue about {mult['③ Full stack: data-center networking revenue']:.1f} and "
             f"{mult['Hub: total revenue']:.1f} times, R&D {mult['② Scale / R&D: R&D expense']:.1f} times and registered "
             f"CUDA developers {mult[lo[0]]:.1f} times, so the capital and supply loops are now growing fastest."),
        data=["financials.csv", "01_flywheel_ecosystem.csv"], chapters=CH + ["13"],
        source="NVIDIA 10-K filings, CFO commentary and keynotes", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    y = np.arange(len(rows))
    ax.barh(y, [r[2] / r[1] for r in rows], color=[r[3] for r in rows], height=0.5, zorder=2)
    for i, r in enumerate(rows):
        ax.text(0.03, i + 0.32, r[0], ha="left", va="bottom", fontsize=9.2, color=INK["title"], fontweight="bold")
    for i, r in enumerate(rows):
        unit = "M" if "developers" in r[0] else "B"
        pre = "" if unit == "M" else "$"
        ax.annotate(f"{r[2]/r[1]:.1f}×  ({pre}{r[1]:,.1f}{unit} → {pre}{r[2]:,.1f}{unit})", (r[2] / r[1], i),
                    xytext=(5, 0), textcoords="offset points", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks([])
    ax.set_ylim(-0.5, len(rows) - 0.2)
    ax.axvline(1, color=INK["base"], lw=1)
    ax.set_xlim(0, max(r[2] / r[1] for r in rows) * 1.45)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="Growth multiple, FY2024 → FY2026 (×; vertical line = no growth)", legend=False)
