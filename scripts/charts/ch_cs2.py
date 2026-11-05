"""Case study CS2 (CUDA: the 15-year bet) charts: gross margin and R&D intensity through the CUDA years, and
Data Center revenue per registered CUDA developer.

Owner: CS2 case-study agent. Data: data/cs2_cuda_trough.csv (FY2007-FY2015, documented in data/README.md),
the shared data/financials.csv (FY2016 onwards) and data/software_ecosystem.csv (developer counts).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from style import GEN_PAST, INK, NV, NV_DARK, Chart, load, register, sources_of

TROUGH = "cs2_cuda_trough.csv"
FIN = "financials.csv"
ECO = "software_ecosystem.csv"

MILESTONES = [  # (fiscal year in which the event fell, label)
    (2008, "CUDA 1.0\n(Jun 2007)"),
    (2013, "AlexNet\n(Dec 2012)"),
    (2015, "cuDNN\n(Oct 2014)"),
    (2017, "DGX-1\n(Apr 2016)"),
]
MILESTONE_SOURCES = ["S525", "S9530", "S9531", "S310"]


def _annual():
    old = load(TROUGH)
    fin = load(FIN)
    new = fin[(fin.period_type == "FY") & fin.metric.isin(["revenue_total", "gross_margin_gaap_pct", "rd_expense"])]
    new = new[new.period.str[2:].astype(int) >= 2016]
    df = pd.concat([old, new], ignore_index=True)
    df["fy"] = df.period.str[2:].astype(int)
    wide = df.pivot_table(index="fy", columns="metric", values="value", aggfunc="first").sort_index()
    wide["rd_pct"] = wide.rd_expense / wide.revenue_total * 100
    return wide, old, new


@register
def cs2_margin_and_rd_through_cuda_years():
    wide, old, new = _annual()
    gm = wide.gross_margin_gaap_pct
    trough_fy = int(gm.loc[2008:2012].idxmin())
    recover_fy = int(gm[(gm.index > 2008) & (gm >= gm.loc[2008])].index.min())
    rd = wide.rd_pct
    c = Chart(
        id="CS2-margin-and-rd-through-cuda-years",
        title=(f"Gross margin fell from {gm.loc[2008]:.1f}% to {gm.loc[trough_fy]:.1f}% after CUDA 1.0 and took until "
               f"FY{recover_fy} to recover"),
        subtitle="NVIDIA GAAP gross margin and R&D as % of revenue by fiscal year, FY2007–FY2026, with CUDA milestones",
        alt=(f"Two-panel line chart, FY2007 to FY2026. Top: NVIDIA's GAAP gross margin was {gm.loc[2007]:.1f}% in FY2007 and "
             f"{gm.loc[2008]:.1f}% in FY2008, the year CUDA 1.0 shipped, then fell to {gm.loc[2009]:.1f}% in FY2009 (including a "
             f"$196M packaging-defect charge and the recession) and {gm.loc[2010]:.1f}% in FY2010, regained the FY2008 level only "
             f"in FY{recover_fy} ({gm.loc[recover_fy]:.1f}%), and reached {gm.loc[2025]:.1f}% in FY2025. Bottom: R&D rose from "
             f"{rd.loc[2008]:.0f}% of revenue in FY2008 to {rd.loc[2010]:.0f}% in FY2010 and a peak of {rd.max():.0f}% in "
             f"FY{int(rd.idxmax())}, then fell to {rd.loc[2026]:.0f}% in FY2026 as revenue outgrew spending. Milestones marked: "
             "CUDA 1.0 (FY2008), AlexNet (FY2013), cuDNN (FY2015), DGX-1 (FY2017)."),
        data=[TROUGH, FIN], chapters=["CS2", "09", "16"],
        source="NVIDIA 10-Ks",
        source_ids=sources_of(old) + sources_of(new) + MILESTONE_SOURCES,
        note="Some FY2007–15 values recalled",
    )
    fig, (ax1, ax2) = c.figure_grid(2, 1, width=10.5, height=7.2, sharex=True,
                                    gridspec_kw={"height_ratios": [1.35, 1]})
    x = wide.index.values
    ax1.plot(x, gm.values, color=NV, marker="o", lw=2.2, ms=6, zorder=3)
    ax1.fill_between(x, gm.values, gm.loc[2008], where=(gm.values < gm.loc[2008]) & (x >= 2008),
                     color="#F4C7C3", alpha=0.7, interpolate=True, zorder=1, label="Below FY2008 margin")
    ax1.axhline(gm.loc[2008], color=INK["base"], lw=1, ls="--")
    for fy in (2008, trough_fy, recover_fy, 2025):
        ax1.annotate(f"{gm.loc[fy]:.1f}%", (fy, gm.loc[fy]), xytext=(0, 9 if fy != trough_fy else -16),
                     textcoords="offset points", ha="center", fontsize=9, color=NV_DARK, fontweight="bold")
    ax1.set_ylim(25, 85)
    ax1.set_ylabel("GAAP gross margin (%)")
    for fy, lab in MILESTONES:
        for a in (ax1, ax2):
            a.axvline(fy, color=INK["muted"], lw=0.9, ls=":", zorder=0)
        ax1.text(fy, 83, lab, ha="center", va="top", fontsize=8, color=INK["text"])
    bars = ax2.bar(x, rd.values, color=[GEN_PAST if v < 2016 else NV for v in x], width=0.7)
    for fy in (2008, 2010, int(rd.idxmax()), 2026):
        ax2.annotate(f"{rd.loc[fy]:.0f}%", (fy, rd.loc[fy]), xytext=(0, 2), textcoords="offset points",
                     ha="center", va="bottom", fontsize=8.5, color=INK["title"])
    ax2.set_ylim(0, rd.max() * 1.25)
    ax2.set_ylabel("R&D (% of revenue)")
    ax2.set_xticks(x[::2])
    ax2.set_xticklabels([f"FY{v}" for v in x[::2]], fontsize=8.8)
    ax1.legend(loc="lower right", fontsize=8.5)
    _ = bars
    ax2.set_xlabel("Fiscal year (ends late January)")
    c.save(fig, [ax1, ax2], legend=False, top=0.86, bottom=0.12)


@register
def cs2_dc_revenue_per_developer():
    eco = load(ECO)
    fin = load(FIN)
    dev = eco[eco.metric.eq("cuda_registered_developers")].copy()
    dev["year"] = dev.date.astype(str).str[:4].astype(int)
    # one point per calendar year: the latest count published that year
    dev = dev.sort_values("date").groupby("year").tail(1)
    dc = fin[(fin.period_type == "FY") & fin.metric.eq("revenue_data_center")].copy()
    dc["fy"] = dc.period.str[2:].astype(int)
    rows = []
    for _, r in dev.iterrows():
        fy = r.year + 1  # NVIDIA FY(N+1) covers ~calendar year N
        m = dc[dc.fy == fy]
        if m.empty:
            continue
        rows.append((r.year, fy, float(r.value), float(m.value.iloc[0]), r.confidence))
    df = pd.DataFrame(rows, columns=["year", "fy", "devs", "dc_b", "conf"])
    df = df[df.year >= 2020]
    df["per_dev_k"] = df.dc_b * 1e9 / df.devs / 1e3
    first, last = df.iloc[0], df.iloc[-1]
    mult = last.per_dev_k / first.per_dev_k
    used_dev = eco[eco.metric.eq("cuda_registered_developers") & eco.date.astype(str).str[:4].astype(int).isin(df.year)]
    used_dc = fin[(fin.period_type == "FY") & fin.metric.eq("revenue_data_center") & fin.period.isin([f"FY{v}" for v in df.fy])]
    c = Chart(
        id="CS2-dc-revenue-per-cuda-developer",
        title=(f"Each CUDA developer now 'carries' ~${last.per_dev_k:.0f}K of Data Center revenue, "
               f"~{mult:.0f}× FY{int(first.fy)}"),
        subtitle="NVIDIA Data Center revenue in fiscal year N+1 ÷ CUDA registered developers stated in calendar year N, US$ thousands",
        alt=(f"Bar chart of NVIDIA Data Center revenue per registered CUDA developer: about ${first.per_dev_k:.1f}K in FY{int(first.fy)} "
             f"({first.devs / 1e6:.0f}M developers, ${first.dc_b:.1f}B), rising each year to about ${last.per_dev_k:.0f}K in "
             f"FY{int(last.fy)} ({last.devs / 1e6:.0f}M developers, ${last.dc_b:.1f}B), roughly {mult:.0f} times higher. Revenue "
             "grew far faster than the developer count, which plateaued at about 6M; the ratio is an indicator of how much "
             "spending rides on the ecosystem, not a causal measure."),
        data=[ECO, FIN], chapters=["CS2", "09", "13"],
        source="NVIDIA developer counts and 10-Ks; repo calc.",
        source_ids=sources_of(used_dev) + sources_of(used_dc) + ["S22009"],
        note="Indicator, not causal",
    )
    fig, ax = c.figure(width=10.0, height=5.6)
    xl = [f"FY{int(r.fy)}\n({r.devs / 1e6:g}M devs)" for _, r in df.iterrows()]
    xs = np.arange(len(df))
    ax.bar(xs, df.per_dev_k, color=[GEN_PAST] * (len(df) - 1) + [NV], width=0.62, edgecolor=NV_DARK, linewidth=0.6)
    for xi, (_, r) in zip(xs, df.iterrows()):
        ax.annotate(f"${r.per_dev_k:.1f}K", (xi, r.per_dev_k), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9.5, color=INK["title"], fontweight="bold")
        ax.text(xi, r.per_dev_k / 2 if r.per_dev_k > 8 else r.per_dev_k + 4, f"DC ${r.dc_b:.0f}B",
                ha="center", va="center", fontsize=8.3, color="#FFFFFF" if r.per_dev_k > 8 else INK["text"])
    ax.set_xticks(xs)
    ax.set_xticklabels(xl, fontsize=9)
    ax.set_ylim(0, df.per_dev_k.max() * 1.15)
    c.save(fig, ax, ylabel="Data Center revenue per developer (US$ K)", legend=False, bottom=0.16)
