"""NVIDIA financial charts (Agent A4): revenue mix, networking, margins, R&D, supply commitments,
customer concentration, guidance, cash returns, and peer / hyperscaler comparisons.

Data: data/financials.csv (long), data/peer_financials.csv (long, company column first)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, axis_break, entity_color, label_bars, load,
                   register, sources_of)

FIN = "financials.csv"
PEER = "peer_financials.csv"
GRAY_GAMING = "#7A7A7A"
GRAY_OTHER = "#C3C2B7"
RED = "#C4314B"   # diverging-scale red (misses / negative)


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def _fin() -> pd.DataFrame:
    return load(FIN)


def _wide(df: pd.DataFrame, ptype: str, metrics: list[str]) -> pd.DataFrame:
    d = df[(df.period_type == ptype) & (df.metric.isin(metrics))]
    w = d.pivot_table(index=["period", "period_end"], columns="metric", values="value", aggfunc="first")
    w = w.reset_index().sort_values("period_end").set_index("period")
    return w


def _conf(df: pd.DataFrame, ptype: str, metric: str) -> dict:
    d = df[(df.period_type == ptype) & (df.metric == metric)]
    return dict(zip(d.period, d.confidence))


def _rows(df: pd.DataFrame, ptype: str, metrics: list[str], periods=None) -> pd.DataFrame:
    d = df[(df.period_type == ptype) & (df.metric.isin(metrics))]
    if periods is not None:
        d = d[d.period.isin(list(periods))]
    return d


def _qlabel(p: str) -> str:
    """'Q1FY24' -> 'Q1\nFY24' (fiscal year shown only on Q1 to keep the axis quiet)."""
    q, fy = p[:2], p[2:]
    return f"{q}\n{fy}" if q == "Q1" else q


def _qticks(ax, periods, every: int = 1, fontsize: float = 8.5):
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels([_qlabel(p) if i % every == 0 or p.startswith("Q1") else "" for i, p in enumerate(periods)],
                       fontsize=fontsize)


def _below(axes) -> None:
    """Draw gridlines under bars/areas (per-axes; never touch global rcParams)."""
    for a in (axes if isinstance(axes, (list, tuple)) else [axes]):
        a.set_axisbelow(True)


def _next_q(p: str) -> str:
    q, fy = int(p[1]), int(p[4:])
    return f"Q{q + 1}FY{fy}" if q < 4 else f"Q1FY{fy + 1}"


# --------------------------------------------------------------------------------------
# 1. Quarterly revenue mix (stacked area)
# --------------------------------------------------------------------------------------
@register
def revenue_mix_stacked_area():
    df = _fin()
    mets = ["revenue_total", "revenue_data_center", "revenue_dc_compute", "revenue_dc_networking", "revenue_gaming",
            "revenue_edge_computing"]
    w = _wide(df, "Q", mets)
    w = w[w.index.str.match(r"Q\dFY(2[3-9])")]
    w = w[w.revenue_total.notna()]
    periods = list(w.index)
    x = np.arange(len(periods))
    tot = w.revenue_total.values
    dc = w.revenue_data_center.values
    comp = w.revenue_dc_compute.values
    net = w.revenue_dc_networking.values
    gam = w.revenue_gaming.values
    netconf = _conf(df, "Q", "revenue_dc_networking")
    est = np.array([netconf.get(p) == "estimate" for p in periods])

    first, last = periods[0], periods[-1]
    s0, s1 = dc[0] / tot[0] * 100, dc[-1] / tot[-1] * 100
    c = Chart(
        id="01-revenue-mix-stacked-area",
        title=f"Data Center went from {s0:.0f}% to {s1:.0f}% of NVIDIA's quarterly revenue in {len(periods) - 1} quarters",
        subtitle=(f"Revenue by market platform, US$ B per quarter, {first[:2]} {first[2:]}–{last[:2]} {last[2:]}; "
                  "networking split back-calculated for FY2024 and Q2 FY2027"),
        alt=(f"Stacked area chart of NVIDIA quarterly revenue by segment from {first} to {last}. Data Center rose from "
             f"${dc[0]:.1f}B ({s0:.0f}% of ${tot[0]:.1f}B) to ${dc[-1]:.1f}B ({s1:.0f}% of ${tot[-1]:.1f}B); networking reached "
             f"about ${net[-1]:.1f}B a quarter while gaming and other segments stayed below $8B combined."),
        data=[FIN], chapters=["01", "00", "13"],
        source="NVIDIA 8-K, CFO commentary, 10-Q",
        source_ids=sources_of(_rows(df, "Q", mets, periods)),
        note="Hatched = estimate",
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    split = ~np.isnan(comp)
    i_split = int(np.argmax(split))            # first quarter with a compute/networking split
    edge_start = int(np.argmax(np.isnan(gam) & ~np.isnan(tot))) if np.isnan(gam).any() else len(periods)
    # --- Data Center not split (FY2023) ---
    seg = slice(0, i_split + 1)
    ax.fill_between(x[seg], 0, dc[seg], color=GEN_PAST, lw=0, label="Data Center (split not disclosed)")
    # --- compute / networking ---
    seg = slice(i_split, len(periods))
    ax.fill_between(x[seg], 0, comp[seg], color=NV, lw=0, label="Data Center compute")
    ax.fill_between(x[seg], comp[seg], dc[seg], color=NV_DARK, lw=0, label="Data Center networking")
    # hatch estimated stretches (both bands, since the split is what is estimated)
    for i in range(i_split, len(periods)):
        if est[i]:
            lo, hi = max(i - 0.5, i_split), min(i + 0.5, len(periods) - 1)
            xs = np.array([lo, hi])
            ax.fill_between(xs, np.interp(xs, x, np.nan_to_num(comp)), np.interp(xs, x, dc),
                            facecolor="none", hatch="///", edgecolor="#FFFFFF", lw=0)
    # --- Gaming and other (to Q4 FY2026), then Edge Computing combined ---
    seg = slice(0, edge_start)
    ax.fill_between(x[seg], dc[seg], dc[seg] + gam[seg], color=GRAY_GAMING, lw=0, label="Gaming")
    ax.fill_between(x[seg], dc[seg] + gam[seg], tot[seg], color=GRAY_OTHER, lw=0, label="ProViz, Automotive, OEM & other")
    if edge_start < len(periods):
        seg = slice(edge_start - 1, len(periods))
        ax.fill_between(x[seg], dc[seg], tot[seg], color="#A9A89F", lw=0, hatch="..",
                        edgecolor="#FFFFFF", label="Edge Computing (gaming + other, combined from Q1 FY2027)")
    ax.plot(x, tot, color=INK["title"], lw=1.0)
    ax.set_xlim(0, len(periods) - 1 + 2.4)
    ax.set_ylim(0, tot.max() * 1.08)
    _qticks(ax, periods)
    xr = x[-1] + 0.15
    ax.annotate(f"Total ${tot[-1]:.1f}B", (xr, tot[-1] + 3), va="center", fontsize=9, color=INK["title"], fontweight="bold")
    ax.annotate(f"Edge ${tot[-1] - dc[-1]:.1f}B", (xr, (tot[-1] + dc[-1]) / 2 - 1), va="center", fontsize=8.5,
                color=INK["text"], fontweight="bold")
    ax.annotate(f"Networking\n~${net[-1]:.1f}B (est.)", (xr, (comp[-1] + dc[-1]) / 2 - 3), va="center", fontsize=8.5,
                color=NV_DARK, fontweight="bold")
    ax.annotate(f"Compute\n~${comp[-1]:.1f}B (est.)", (xr, comp[-1] / 2), va="center", fontsize=8.5, color=NV,
                fontweight="bold")
    ax.annotate("ChatGPT-driven\nH100 ramp", (periods.index("Q2FY24"), dc[periods.index("Q2FY24")]),
                xytext=(periods.index("Q2FY24") - 1.6, tot.max() * 0.45), fontsize=8.5, color=INK["text"],
                arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.legend(loc="upper left", fontsize=8.5)
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter", ylabel="Revenue (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 2. Annual revenue by segment, FY2016–FY2026
# --------------------------------------------------------------------------------------
@register
def annual_revenue_by_segment():
    df = _fin()
    mets = ["revenue_total", "revenue_data_center", "revenue_gaming", "revenue_pro_visualization",
            "revenue_automotive", "revenue_oem_other"]
    w = _wide(df, "FY", mets)
    w["other"] = w.revenue_total - w.revenue_data_center - w.revenue_gaming
    est_fy = {p for p, cf in _conf(df, "FY", "revenue_gaming").items() if cf == "estimate"}
    p0, p1 = w.index[0], w.index[-1]
    s0 = w.revenue_data_center.iloc[0] / w.revenue_total.iloc[0] * 100
    s1 = w.revenue_data_center.iloc[-1] / w.revenue_total.iloc[-1] * 100
    c = Chart(
        id="00-annual-revenue-by-segment",
        title=f"Data Center grew from {s0:.0f}% of NVIDIA revenue in {p0} to {s1:.0f}% in {p1}",
        subtitle="Revenue by market platform, US$ B per fiscal year (FY ends late Jan); FY2026 gaming/other = sum of quarters",
        alt=(f"Stacked bar chart of NVIDIA annual revenue by segment {p0}–{p1}: Data Center rose from "
             f"${w.revenue_data_center.iloc[0]:.2f}B ({s0:.0f}%) to ${w.revenue_data_center.iloc[-1]:.1f}B ({s1:.0f}%) "
             f"while gaming grew from ${w.revenue_gaming.iloc[0]:.1f}B to about ${w.revenue_gaming.iloc[-1]:.0f}B; "
             f"total revenue went from ${w.revenue_total.iloc[0]:.1f}B to ${w.revenue_total.iloc[-1]:.0f}B."),
        data=[FIN], chapters=["00", "01", "16"],
        source="NVIDIA 10-K filings", source_ids=sources_of(_rows(df, "FY", mets)),
        note="Hatched = estimate",
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    xl = [p.replace("FY20", "FY") for p in w.index]
    x = np.arange(len(w))
    b1 = ax.bar(x, w.revenue_data_center, color=NV, width=0.68, label="Data Center")
    b2 = ax.bar(x, w.revenue_gaming, bottom=w.revenue_data_center, color=GRAY_GAMING, width=0.68, label="Gaming")
    b3 = ax.bar(x, w.other, bottom=w.revenue_data_center + w.revenue_gaming, color=GRAY_OTHER, width=0.68,
                label="ProViz, Automotive, OEM & other")
    for bars in (b2, b3):
        for i, p in enumerate(w.index):
            if p in est_fy:
                bars.patches[i].set_hatch("///")
    for i, (t, d) in enumerate(zip(w.revenue_total, w.revenue_data_center)):
        ax.annotate(f"${t:,.0f}B" if t >= 10 else f"${t:.1f}B", (i, t), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=8.5, color=INK["title"])
        if t > 40:
            ax.annotate(f"DC {d / t * 100:.0f}%", (i, d / 2), ha="center", va="center", fontsize=8, color="#FFFFFF",
                        fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(xl)
    ax.set_ylim(0, w.revenue_total.max() * 1.1)
    ax.legend(loc="upper left")
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal year", ylabel="Revenue (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 3. Networking revenue and share of Data Center
# --------------------------------------------------------------------------------------
@register
def networking_revenue_and_share():
    df = _fin()
    mets = ["revenue_dc_networking", "revenue_data_center"]
    w = _wide(df, "Q", mets).dropna()
    periods = list(w.index)
    conf = _conf(df, "Q", "revenue_dc_networking")
    est = [conf.get(p) == "estimate" for p in periods]
    share = w.revenue_dc_networking / w.revenue_data_center * 100
    base_p = next(p for p, e in zip(periods, est) if not e)
    mult = w.revenue_dc_networking.iloc[-1] / w.revenue_dc_networking[base_p]
    c = Chart(
        id="06-networking-revenue-and-share",
        title=(f"NVIDIA networking revenue rose {mult:.1f}× in two years to ~${w.revenue_dc_networking.iloc[-1]:.1f}B "
               f"a quarter (~{share.iloc[-1]:.0f}% of DC)"),
        subtitle="Left: Data Center networking revenue, US$ B per quarter. Right: networking as % of Data Center revenue",
        alt=(f"Two-panel chart. Left: NVIDIA quarterly networking revenue from ${w.revenue_dc_networking.iloc[0]:.1f}B "
             f"(est.) in {periods[0]} to about ${w.revenue_dc_networking.iloc[-1]:.1f}B in {periods[-1]}, {mult:.1f} times "
             f"{base_p}. Right: networking share of Data Center fell to {share.min():.0f}% during the Blackwell compute ramp "
             f"then rose to about {share.iloc[-1]:.0f}% as NVLink, Spectrum-X and InfiniBand scaled."),
        data=[FIN], chapters=["06", "13", "CS1"],
        source="NVIDIA CFO commentary, 10-Q, calls", source_ids=sources_of(_rows(df, "Q", mets, periods)),
        note="Hatched / hollow = estimate",
    )
    fig, axes = c.figure_grid(1, 2, width=11.0, height=5.6, gridspec_kw={"width_ratios": [1.35, 1]})
    ax, ax2 = axes
    x = np.arange(len(periods))
    bars = ax.bar(x, w.revenue_dc_networking, color=[GEN_PAST if e else NV_DARK for e in est], width=0.7)
    for b, e in zip(bars.patches, est):
        if e:
            b.set_hatch("///")
    for i in (0, periods.index(base_p), len(periods) - 1):
        ax.annotate(f"${w.revenue_dc_networking.iloc[i]:.1f}B" + (" est." if est[i] else ""),
                    (i, w.revenue_dc_networking.iloc[i]), xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=8.5, color=INK["title"])
    _qticks(ax, periods, fontsize=8)
    ax.set_ylabel("Networking revenue (US$ B)")
    ax.set_xlabel("NVIDIA fiscal quarter")
    ax.set_ylim(0, w.revenue_dc_networking.max() * 1.15)
    ax2.plot(x, share, color=NV_DARK, lw=2, zorder=2)
    ax2.scatter(x, share, s=42, zorder=3, facecolor=["#FFFFFF" if e else NV_DARK for e in est], edgecolor=NV_DARK, lw=1.6)
    for i in (int(np.argmin(share.values)), len(periods) - 1, 0):
        ax2.annotate(f"{share.iloc[i]:.0f}%", (i, share.iloc[i]), xytext=(0, 7), textcoords="offset points", ha="center",
                     fontsize=8.5, color=INK["title"])
    _qticks(ax2, periods, fontsize=8)
    ax2.set_ylim(0, max(30, share.max() * 1.25))
    ax2.set_ylabel("Networking share of Data Center (%)")
    ax2.set_xlabel("NVIDIA fiscal quarter")
    _below([ax, ax2])
    c.save(fig, [ax, ax2], legend=False)


# --------------------------------------------------------------------------------------
# 4. Gross margin trend
# --------------------------------------------------------------------------------------
@register
def gross_margin_trend():
    df = _fin()
    mets = ["gross_margin_gaap_pct", "gross_margin_nongaap_pct", "gross_margin_nongaap_ex_h20_pct"]
    w = _wide(df, "Q", mets)
    w = w[w.index.str.match(r"Q\dFY(2[3-9])")]
    periods = list(w.index)
    x = np.arange(len(periods))
    g = w.gross_margin_gaap_pct
    i_low = int(np.nanargmin(g.values[:6]))
    i_h20 = periods.index("Q1FY26")
    c = Chart(
        id="13-gross-margin-trend",
        title=f"Gross margin climbed from {g.iloc[i_low]:.1f}% to ~{g.iloc[-1]:.0f}%, broken only by the H20 write-down",
        subtitle=(f"GAAP and non-GAAP gross margin, % of revenue, {periods[0][:2]} {periods[0][2:]}–{periods[-1][:2]} "
                  f"{periods[-1][2:]}; from Q1 FY2027 non-GAAP includes stock-based comp"),
        alt=(f"Line chart of NVIDIA quarterly gross margin: GAAP margin bottomed at {g.iloc[i_low]:.1f}% in {periods[i_low]} "
             f"(gaming inventory charges), rose above 75% during the Hopper ramp, dropped to {g.iloc[i_h20]:.1f}% in Q1 FY2026 "
             f"because of a $4.5B H20 export-control charge (71.3% non-GAAP excluding it), and was about {g.iloc[-1]:.0f}% "
             f"in {periods[-1]}."),
        data=[FIN], chapters=["13", "14", "18", "CS6"],
        source="NVIDIA 8-K releases", source_ids=sources_of(_rows(df, "Q", mets, periods)),
        note="Axis starts at 35% (break marked)",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    ax.plot(x, w.gross_margin_nongaap_pct, color=GEN_PAST, lw=2, marker="o", ms=5, label="Non-GAAP")
    ax.plot(x, g, color=NV, lw=2.2, marker="o", ms=6, label="GAAP")
    exh = w.gross_margin_nongaap_ex_h20_pct.dropna()
    for p, v in exh.items():
        i = periods.index(p)
        ax.scatter([i], [v], marker="D", s=46, facecolor="#FFFFFF", edgecolor=NV_DARK, zorder=4,
                   label="Non-GAAP excl. H20 charge")
    ax.annotate("Q1 FY2026: $4.5B H20 export-licence\ncharge → 60.5% GAAP", (i_h20, g.iloc[i_h20]),
                xytext=(i_h20 - 6.2, 47), fontsize=8.5, color=INK["text"],
                arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.annotate("Q2 FY2023: gaming channel\ncorrection, inventory charges", (i_low, g.iloc[i_low]),
                xytext=(i_low + 1.0, 40.0), fontsize=8.5, color=INK["text"],
                arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.annotate(f"{g.iloc[-1]:.0f}%", (x[-1], g.iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center",
                fontsize=9, color=NV_DARK, fontweight="bold")
    ax.set_ylim(35, 85)
    ax.set_xlim(-0.5, len(periods) - 0.2)
    axis_break(ax)
    _qticks(ax, periods)
    ax.legend(loc="lower right")
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter", ylabel="Gross margin (% of revenue)", legend=False)


# --------------------------------------------------------------------------------------
# 5. R&D expense trend (+ intensity)
# --------------------------------------------------------------------------------------
@register
def rd_expense_trend():
    df = _fin()
    mets = ["rd_expense", "revenue_total"]
    w = _wide(df, "FY", mets).dropna()
    w["pct"] = w.rd_expense / w.revenue_total * 100
    mult = w.rd_expense.iloc[-1] / w.rd_expense.iloc[0]
    c = Chart(
        id="13-rd-expense-trend",
        title=(f"R&D spend rose {mult:.0f}× to ${w.rd_expense.iloc[-1]:.1f}B ({w.index[-1]}) while falling to "
               f"{w.pct.iloc[-1]:.0f}% of revenue"),
        subtitle="Left: GAAP research and development expense, US$ B per fiscal year. Right: R&D as % of revenue",
        alt=(f"Two-panel chart of NVIDIA R&D. Left: R&D expense grew from ${w.rd_expense.iloc[0]:.2f}B in {w.index[0]} to "
             f"${w.rd_expense.iloc[-1]:.1f}B in {w.index[-1]}, about {mult:.0f} times. Right: R&D intensity fell from "
             f"{w.pct.iloc[0]:.0f}% of revenue to {w.pct.iloc[-1]:.1f}% because revenue grew even faster."),
        data=[FIN], chapters=["13", "16", "09"],
        source="NVIDIA 10-K filings", source_ids=sources_of(_rows(df, "FY", mets)),
    )
    fig, axes = c.figure_grid(1, 2, width=11.0, height=5.6, gridspec_kw={"width_ratios": [1.4, 1]})
    ax, ax2 = axes
    xl = [p.replace("FY20", "FY") for p in w.index]
    x = np.arange(len(w))
    bars = ax.bar(x, w.rd_expense, color=[GEN_PAST] * (len(w) - 1) + [NV], width=0.66)
    label_bars(ax, bars, fmt="{:,.1f}", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(xl, fontsize=8.5)
    ax.set_ylabel("R&D expense (US$ B)")
    ax.set_xlabel("NVIDIA fiscal year")
    ax.set_ylim(0, w.rd_expense.max() * 1.12)
    ax2.plot(x, w.pct, color=NV_DARK, marker="o", ms=6)
    for i in (0, int(np.argmax(w.pct.values)), len(w) - 1):
        ax2.annotate(f"{w.pct.iloc[i]:.0f}%", (i, w.pct.iloc[i]), xytext=(0, 7), textcoords="offset points",
                     ha="center", fontsize=8.5, color=INK["title"])
    ax2.set_xticks(x)
    ax2.set_xticklabels(xl, fontsize=8, rotation=90)
    ax2.set_ylim(0, w.pct.max() * 1.25)
    ax2.set_ylabel("R&D as % of revenue")
    ax2.set_xlabel("NVIDIA fiscal year")
    _below([ax, ax2])
    c.save(fig, [ax, ax2], legend=False)


# --------------------------------------------------------------------------------------
# 6. R&D vs peers
# --------------------------------------------------------------------------------------
@register
def rd_expense_vs_peers():
    df = _fin()
    pf = load(PEER)
    pr = pf[pf.metric == "rd_expense"].copy()
    pr["year"] = pr.period_end.str[:4].astype(int)
    nv = df[(df.period_type == "FY") & (df.metric == "rd_expense")].copy()
    nv["year"] = nv.period_end.str[:4].astype(int) - 1      # FY ends late Jan -> calendar year before
    years = sorted(pr.year.unique())
    nv = nv[nv.year.isin(years)]
    comps = ["Intel", "AMD", "Broadcom"]
    vals = {k: [pr[(pr.company == k) & (pr.year == y)].value.sum() or np.nan for y in years] for k in comps}
    vals["NVIDIA"] = [nv[nv.year == y].value.sum() or np.nan for y in years]
    yl = years[-1]
    c = Chart(
        id="13-rd-expense-vs-peers",
        title=(f"NVIDIA's {yl} R&D (${vals['NVIDIA'][-1]:.1f}B) passed AMD and Broadcom, still below "
               f"Intel's ${vals['Intel'][-1]:.1f}B"),
        subtitle="GAAP R&D expense, US$ B per year; NVIDIA FY2023–FY2025 shown as 2022–2024, Broadcom FY ends ~Nov",
        alt=(f"Grouped bar chart of R&D expense {years[0]}–{yl}: NVIDIA rose from ${vals['NVIDIA'][0]:.1f}B to "
             f"${vals['NVIDIA'][-1]:.1f}B, AMD ${vals['AMD'][-1]:.1f}B, Broadcom ${vals['Broadcom'][-1]:.1f}B "
             f"(incl. VMware) and Intel ${vals['Intel'][-1]:.1f}B in {yl}; NVIDIA's FY2026 R&D of $18.5B is not shown."),
        data=[FIN, PEER], chapters=["13", "15", "19"],
        source="company 10-K filings",
        source_ids=sources_of(pd.concat([pr, nv])),
    )
    fig, ax = c.figure(width=10, height=5.6)
    order = ["Intel", "AMD", "Broadcom", "NVIDIA"]
    width = 0.2
    x = np.arange(len(years))
    for j, k in enumerate(order):
        bars = ax.bar(x + (j - 1.5) * width, vals[k], width=width * 0.92, color=entity_color(k), label=k)
        label_bars(ax, bars, fmt="{:.1f}", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylim(0, max(max(v) for v in vals.values()) * 1.15)
    ax.legend(loc="upper left", ncol=4)
    _below(ax)
    c.save(fig, ax, xlabel="Calendar year (approx.)", ylabel="R&D expense (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 7. Purchase obligations vs inventory
# --------------------------------------------------------------------------------------
@register
def purchase_obligations_over_time():
    df = _fin()
    mets = ["purchase_obligations", "inventory", "revenue_total"]
    w = _wide(df, "Q", mets)
    w = w[w.purchase_obligations.notna()]
    periods = list(w.index)
    x = np.arange(len(periods))
    ratio = w.purchase_obligations / w.revenue_total
    last = periods[-1]
    pre = ratio[["Q1FY23", "Q2FY23"]].max()
    c = Chart(
        id="03-purchase-obligations-over-time",
        title=(f"Supply commitments hit ${w.purchase_obligations.iloc[-1]:.0f}B: {ratio.iloc[-1]:.1f}× quarterly revenue "
               f"vs ~{pre:.1f}× before the 2022 bust"),
        subtitle="Left: purchase/supply commitments vs inventory, US$ B at quarter end. Right: commitments ÷ that quarter's revenue",
        alt=(f"Two-panel chart. Left: NVIDIA purchase obligations rose from ${w.purchase_obligations.iloc[0]:.1f}B in "
             f"{periods[0]} to ${w.purchase_obligations.iloc[-1]:.0f}B in {last} while inventory reached "
             f"${w.inventory.iloc[-1]:.1f}B. Right: commitments were about {pre:.1f} times quarterly revenue before the "
             f"FY2023 inventory write-downs and are now {ratio.iloc[-1]:.1f} times, mostly memory and capacity for Rubin."),
        data=[FIN], chapters=["03", "18", "13"],
        source="NVIDIA 10-Q/10-K", source_ids=sources_of(_rows(df, "Q", mets, periods)),
        note="Definition widened from Q3 FY2026",
    )
    fig, axes = c.figure_grid(1, 2, width=11.0, height=5.6, gridspec_kw={"width_ratios": [1.35, 1]})
    ax, ax2 = axes
    ax.plot(x, w.purchase_obligations, color=NV, marker="o", ms=5, label="Purchase / supply commitments")
    inv = w.inventory
    ax.plot(x[inv.notna().values], inv.dropna(), color=GRAY_GAMING, marker="s", ms=4.5, label="Inventory")
    for i in (len(periods) - 1, len(periods) - 2, len(periods) - 3):
        ax.annotate(f"${w.purchase_obligations.iloc[i]:.0f}B", (i, w.purchase_obligations.iloc[i]), xytext=(-6, 6),
                    textcoords="offset points", ha="right", fontsize=8.5, color=NV_DARK, fontweight="bold")
    ax.annotate(f"${inv.iloc[-1]:.0f}B", (x[-1], inv.iloc[-1]), xytext=(4, 8), textcoords="offset points",
                fontsize=8.5, color=GRAY_GAMING)
    _qticks(ax, periods, fontsize=7.5)
    ax.set_ylabel("US$ B at quarter end")
    ax.set_xlabel("NVIDIA fiscal quarter")
    ax.set_ylim(0, w.purchase_obligations.max() * 1.12)
    ax.legend(loc="upper left")
    ax2.bar(x, ratio, color=[RED if p in ("Q1FY23", "Q2FY23") else NV for p in periods], width=0.7)
    for i in (periods.index("Q2FY23"), len(periods) - 1):
        ax2.annotate(f"{ratio.iloc[i]:.1f}×", (i, ratio.iloc[i]), xytext=(0, 3), textcoords="offset points", ha="center",
                     fontsize=8.5, color=INK["title"])
    ax2.annotate("pre-bust\n(FY2023)", (periods.index("Q1FY23"), ratio["Q1FY23"]), xytext=(1.5, ratio.max() * 0.75),
                 fontsize=8, color=RED, arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    _qticks(ax2, periods, fontsize=7.5)
    ax2.set_ylim(0, ratio.max() * 1.2)
    ax2.set_ylabel("Commitments ÷ quarterly revenue (×)")
    ax2.set_xlabel("NVIDIA fiscal quarter")
    _below([ax, ax2])
    c.save(fig, [ax, ax2], legend=False)


# --------------------------------------------------------------------------------------
# 8. Customer concentration
# --------------------------------------------------------------------------------------
@register
def customer_concentration_over_time():
    df = _fin()
    mets = [f"customer_{k}_pct_revenue" for k in "abcd"]
    d = df[df.metric.isin(mets)].copy()
    w = d.pivot_table(index=["period", "period_type", "period_end"], columns="metric", values="value").reset_index()
    w = w.sort_values(["period_end", "period_type"]).reset_index(drop=True)
    w["label"] = [f"{p} (full year)" if t == "FY" else p for p, t in zip(w.period, w.period_type)]
    w["total"] = w[mets].sum(axis=1)
    w["n"] = w[mets].notna().sum(axis=1)
    first, last = w.iloc[0], w.iloc[-1]
    c = Chart(
        id="13-customer-concentration-over-time",
        title=(f"Customers at ≥10% of revenue rose from {first.n} ({first.total:.0f}%) in {first.period} to "
               f"{last.n} ({last.total:.0f}%) in {last.period}"),
        subtitle="Share of revenue per disclosed direct customer, %; letters are not the same company across periods; mostly OEMs/ODMs",
        alt=(f"Stacked bar chart of NVIDIA's disclosed direct customers above 10% of revenue: {first.n} customer at "
             f"{first.total:.0f}% in {first.period}, {int(w.loc[w.period == 'FY2025', 'n'].iloc[0])} customers at "
             f"{w.loc[w.period == 'FY2025', 'total'].iloc[0]:.0f}% in FY2025, and {last.n} customers totalling "
             f"{last.total:.0f}% in {last.period}; most are OEMs/ODMs building for hyperscalers."),
        data=[FIN], chapters=["13", "18"],
        source="NVIDIA 10-K/10-Q", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.8)
    x = np.arange(len(w))
    bottom = np.zeros(len(w))
    cols = [SEQ_BLUE[7], SEQ_BLUE[5], SEQ_BLUE[3], SEQ_BLUE[1]]
    for m, col, k in zip(mets, cols, "ABCD"):
        v = w[m].fillna(0).values
        bars = ax.bar(x, v, bottom=bottom, color=col, width=0.62, label=f"Customer {k}", edgecolor="#FFFFFF", lw=0.8)
        for i, (vv, b) in enumerate(zip(v, bottom)):
            if vv > 0:
                ax.annotate(f"{vv:.0f}%", (i, b + vv / 2), ha="center", va="center", fontsize=8.5,
                            color="#FFFFFF" if col in cols[:2] else INK["title"])
        bottom += v
    for i, t in enumerate(w.total):
        ax.annotate(f"{t:.0f}%", (i, t), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9.5,
                    fontweight="bold", color=INK["title"])
    ax.set_xticks(x)
    ax.set_xticklabels([lab.replace(" (full year)", "\n(full year)") for lab in w.label], fontsize=8.8)
    ax.set_ylim(0, w.total.max() * 1.15)
    ax.legend(loc="upper left")
    _below(ax)
    c.save(fig, ax, xlabel="Reporting period", ylabel="Share of NVIDIA revenue (%)", legend=False)


# --------------------------------------------------------------------------------------
# 9. Quarterly revenue and guidance
# --------------------------------------------------------------------------------------
def _guidance_frame(df):
    w = _wide(df, "Q", ["revenue_total", "guidance_next_q_revenue"])
    g = w.guidance_next_q_revenue.dropna()
    guided = {_next_q(p): v for p, v in g.items()}
    w = w[w.index.str.match(r"Q\dFY(2[3-9])")]
    periods = list(w.index) + [p for p in guided if p not in w.index]
    actual = [w.revenue_total.get(p, np.nan) for p in periods]
    guide = [guided.get(p, np.nan) for p in periods]
    return periods, np.array(actual, dtype=float), np.array(guide, dtype=float)


@register
def quarterly_revenue_and_guidance():
    df = _fin()
    periods, actual, guide = _guidance_frame(df)
    i0 = int(np.nanargmin(actual))
    nxt = periods[-1]
    c = Chart(
        id="00-quarterly-revenue-and-guidance",
        title=(f"Quarterly revenue rose from ${actual[i0]:.1f}B to ${np.nanmax(actual):.1f}B in "
               f"{int(np.nanargmax(actual)) - i0} quarters; the {nxt[:2]} {nxt[2:]} guide is ${guide[-1]:.0f}B"),
        subtitle="NVIDIA revenue per fiscal quarter (bars) and the guidance midpoint issued one quarter earlier (markers), US$ B",
        alt=(f"Bar chart of NVIDIA quarterly revenue from {periods[0]} to {periods[-2]} with guidance markers: revenue fell to "
             f"${actual[i0]:.1f}B in {periods[i0]} and then rose to ${np.nanmax(actual):.1f}B; actual revenue landed above "
             f"the guidance midpoint in every quarter since Q1 FY2024, and the outlook for {nxt} is ${guide[-1]:.0f}B ±2%."),
        data=[FIN], chapters=["00", "13"],
        source="NVIDIA 8-K releases",
        source_ids=sources_of(_rows(df, "Q", ["revenue_total", "guidance_next_q_revenue"])),
        note="Hatched = guidance only",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(periods))
    bars = ax.bar(x, np.nan_to_num(actual), color=NV, width=0.66, label="Actual revenue")
    for i, a in enumerate(actual):
        if np.isnan(a):
            bars.patches[i].set_height(guide[i])
            bars.patches[i].set_facecolor(GEN_PAST)
            bars.patches[i].set_hatch("///")
            ax.annotate(f"${guide[i]:.0f}B\nguide", (i, guide[i]), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=8.5, color=NV_DARK, fontweight="bold")
    ax.scatter(x, guide, marker="_", s=260, lw=2.4, color=INK["title"], zorder=4, label="Guidance midpoint (prior quarter)")
    for i in (i0, len(periods) - 2):
        ax.annotate(f"${actual[i]:.1f}B", (i, actual[i]), xytext=(0, 4), textcoords="offset points", ha="center",
                    fontsize=8.5, color=INK["title"])
    miss = periods.index("Q2FY23")
    ax.annotate("Q2 FY2023: missed\nguide by 17%", (miss, guide[miss]), xytext=(miss + 1.2, 35), fontsize=8.5,
                color=INK["text"], arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    _qticks(ax, periods)
    ax.set_ylim(0, np.nanmax(guide) * 1.15)
    ax.legend(loc="upper left")
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter", ylabel="Revenue (US$ B)", legend=False)


@register
def guidance_beat_history():
    df = _fin()
    periods, actual, guide = _guidance_frame(df)
    m = ~np.isnan(actual) & ~np.isnan(guide)
    p = [pp for pp, mm in zip(periods, m) if mm]
    beat = (actual[m] / guide[m] - 1) * 100
    streak = 0
    for b in beat[::-1]:
        if b > 0:
            streak += 1
        else:
            break
    avg = beat[-streak:].mean()
    worst = beat.min()
    c = Chart(
        id="13-guidance-beat-history",
        title=f"NVIDIA beat its revenue-guide midpoint {streak} quarters running, by +{avg:.1f}% on average",
        subtitle="Actual quarterly revenue vs the guidance midpoint issued the prior quarter, % difference",
        alt=(f"Bar chart of NVIDIA's revenue surprise versus its own guidance midpoint from {p[0]} to {p[-1]}: a {worst:.0f}% "
             f"miss in Q2 FY2023 during the gaming correction, then {streak} consecutive beats averaging {avg:.1f}%, the largest "
             f"+{beat.max():.0f}% in {p[int(np.argmax(beat))]}."),
        data=[FIN], chapters=["13", "18"],
        source="NVIDIA 8-K releases",
        source_ids=sources_of(_rows(df, "Q", ["revenue_total", "guidance_next_q_revenue"])),
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    x = np.arange(len(p))
    bars = ax.bar(x, beat, color=[NV if b > 0 else RED for b in beat], width=0.66)
    for i, b in enumerate(beat):
        ax.annotate(f"{b:+.0f}%", (i, b), xytext=(0, 3 if b > 0 else -11), textcoords="offset points", ha="center",
                    fontsize=8, color=INK["title"])
    ax.axhline(0, color=INK["base"], lw=1)
    _qticks(ax, p)
    ax.set_ylim(min(beat) * 1.25, max(beat) * 1.25)
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter (reported)", ylabel="Actual vs guidance midpoint (%)", legend=False)


# --------------------------------------------------------------------------------------
# 10. Free cash flow and shareholder returns
# --------------------------------------------------------------------------------------
@register
def free_cash_flow_and_buybacks():
    df = _fin()
    mets = ["free_cash_flow", "shareholder_returns"]
    allq = _wide(df, "Q", ["revenue_total"])
    allq = allq[allq.index.str.match(r"Q\dFY(2[3-9])")]
    w = _wide(df, "Q", mets).reindex(allq.index)
    periods = list(w.index)
    both = w.dropna()
    tf, tr = both.free_cash_flow.sum(), both.shareholder_returns.sum()
    c = Chart(
        id="13-free-cash-flow-and-buybacks",
        title=f"NVIDIA returned ${tr:.0f}B of ${tf:.0f}B free cash flow ({tr / tf * 100:.0f}%) to shareholders since FY2023",
        subtitle="Free cash flow (operating cash flow − capex) vs repurchases + dividends, US$ B per quarter; n/a = not in dataset",
        alt=(f"Grouped bar chart of NVIDIA quarterly free cash flow and shareholder returns {periods[0]}–{periods[-1]}: "
             f"over the {len(both)} quarters with both figures, free cash flow totalled ${tf:.0f}B and returns ${tr:.0f}B "
             f"({tr / tf * 100:.0f}%); free cash flow reached ${w.free_cash_flow.max():.1f}B in "
             f"{w.free_cash_flow.idxmax()} and returns ${w.shareholder_returns.max():.0f}B in {w.shareholder_returns.idxmax()}."),
        data=[FIN], chapters=["13"],
        source="NVIDIA 8-K releases, 10-Q", source_ids=sources_of(_rows(df, "Q", mets, periods)),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(periods))
    b1 = ax.bar(x - 0.19, w.free_cash_flow, width=0.36, color=NV, label="Free cash flow")
    b2 = ax.bar(x + 0.19, w.shareholder_returns, width=0.36, color=GRAY_GAMING, label="Buybacks + dividends")
    for i, p in enumerate(periods):
        if np.isnan(w.free_cash_flow.iloc[i]):
            ax.annotate("n/a", (i - 0.19, 0.5), ha="center", fontsize=7, color=INK["muted"], rotation=90)
        if np.isnan(w.shareholder_returns.iloc[i]):
            ax.annotate("n/a", (i + 0.19, 0.5), ha="center", fontsize=7, color=INK["muted"], rotation=90)
    i = int(np.nanargmax(w.free_cash_flow.values))
    ax.annotate(f"${w.free_cash_flow.iloc[i]:.1f}B", (i - 0.19, w.free_cash_flow.iloc[i]), xytext=(0, 3),
                textcoords="offset points", ha="center", fontsize=8.5, color=NV_DARK, fontweight="bold")
    _qticks(ax, periods)
    ax.set_ylim(0, np.nanmax(w.free_cash_flow.values) * 1.15)
    ax.legend(loc="upper left")
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter", ylabel="US$ B per quarter", legend=False)


# --------------------------------------------------------------------------------------
# 11. Operating leverage
# --------------------------------------------------------------------------------------
@register
def operating_leverage():
    df = _fin()
    mets = ["operating_income", "net_income", "revenue_total", "rd_expense"]
    w = _wide(df, "FY", mets).dropna()
    om = w.operating_income / w.revenue_total * 100
    nm = w.net_income / w.revenue_total * 100
    rd = w.rd_expense / w.revenue_total * 100
    c = Chart(
        id="13-operating-leverage",
        title=(f"Operating margin rose from {om.iloc[0]:.0f}% to {om.iloc[-1]:.0f}% in ten years as R&D fell to "
               f"{rd.iloc[-1]:.0f}% of revenue"),
        subtitle="GAAP operating margin, net margin and R&D expense as % of revenue, by fiscal year",
        alt=(f"Line chart of NVIDIA margins {w.index[0]}–{w.index[-1]}: operating margin rose from {om.iloc[0]:.0f}% to "
             f"{om.iloc[-1]:.0f}% (peak {om.max():.0f}% in {om.idxmax()}), dipping to {om['FY2023']:.0f}% in FY2023; net "
             f"margin reached {nm.iloc[-1]:.0f}%; R&D fell from {rd.iloc[0]:.0f}% to {rd.iloc[-1]:.0f}% of revenue."),
        data=[FIN], chapters=["13", "14"],
        source="NVIDIA 10-K filings", source_ids=sources_of(_rows(df, "FY", mets)),
    )
    fig, ax = c.figure(width=10, height=5.6)
    xl = [p.replace("FY20", "FY") for p in w.index]
    x = np.arange(len(w))
    for s, col, lab in ((om, NV, "Operating margin"), (nm, GEN_PAST, "Net margin"), (rd, GRAY_GAMING, "R&D % of revenue")):
        ax.plot(x, s, color=col, marker="o", ms=5, label=lab)
        ax.annotate(f"{lab} {s.iloc[-1]:.0f}%", (x[-1], s.iloc[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=col if col != GEN_PAST else NV_DARK, fontweight="bold")
    ax.annotate("FY2023: Arm write-off +\ninventory charges", (list(w.index).index("FY2023"), om["FY2023"]),
                xytext=(4.2, 45), fontsize=8.5, color=INK["text"], arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.set_xticks(x)
    ax.set_xticklabels(xl)
    ax.set_xlim(-0.4, len(w) + 1.9)
    ax.set_ylim(0, 75)
    _below(ax)
    c.save(fig, ax, xlabel="NVIDIA fiscal year", ylabel="% of revenue", legend=False)


# --------------------------------------------------------------------------------------
# 12. Hyperscaler capex
# --------------------------------------------------------------------------------------
@register
def hyperscaler_capex_trend():
    pf = load(PEER)
    d = pf[pf.metric == "capex"].copy()
    d["year"] = d.period_end.str[:4].astype(int)
    comps = ["Amazon", "Alphabet", "Meta", "Microsoft", "Oracle"]
    trio = ["Alphabet", "Amazon", "Meta"]
    t22 = d[(d.year == 2022) & d.company.isin(trio)].value.sum()
    t26 = d[(d.year == 2026) & d.company.isin(trio)].value.sum()
    # QA 2026-11-05: the 2026 points are the FIRST (Jan–Feb 2026) guides; say so and show the latest guide
    # midpoint from the layer-12 guidance tracker so the chart is not read as the current outlook.
    gd = load("l12_hyperscaler_capex_guidance.csv")
    gd = gd[gd.company.isin(trio) & (gd.period == "CY2026")].copy()
    gd["mid"] = (gd.capex_low_usd_b + gd.capex_high_usd_b) / 2
    latest = gd.sort_values("guidance_date").groupby("company").mid.last()
    t26_latest = latest.sum()
    c = Chart(
        id="18-hyperscaler-capex-trend",
        title=(f"Alphabet, Amazon and Meta first guided ~${t26:.0f}B of 2026 capex, {t26 / t22:.1f}× their ${t22:.0f}B "
               f"in 2022; guides have since risen to ~${t26_latest:.0f}B"),
        subtitle=("Capex, US$ B per fiscal year; 2026 = first guidance (Jan–Feb 2026); dashed/hollow = outlook or unverified; "
                  "MSFT FY ends Jun (ex-leases), Oracle May"),
        alt=(f"Line chart of hyperscaler capital expenditure 2022–2026: Alphabet, Amazon and Meta together rise from "
             f"${t22:.0f}B in 2022 to about ${t26:.0f}B in their first 2026 guides (Amazon ~$200B, Alphabet ~$180B midpoint, "
             f"Meta ~$125B midpoint), since raised to about ${t26_latest:.0f}B by October 2026; Microsoft reached "
             f"${d[(d.company == 'Microsoft')].value.max():.0f}B in FY2025 and Oracle guided about $50B for FY2026."),
        data=[PEER, "l12_hyperscaler_capex_guidance.csv"], chapters=["18", "13", "08"],
        source="company 10-Ks and outlooks", source_ids=sources_of(d) + [x for x in sources_of(gd) if x not in sources_of(d)],
        note=f"Latest 2026 guide midpoints (Jul–Oct 2026): Big 3 ~${t26_latest:.0f}B",
    )
    fig, ax = c.figure(width=10, height=5.8)
    color = {"Oracle": "#B5B5B5"}
    marks = {"Amazon": "o", "Alphabet": "s", "Meta": "^", "Microsoft": "D", "Oracle": "v"}
    for k in comps:
        s = d[d.company == k].sort_values("year")
        col = color.get(k, entity_color(k))
        solid = s[s.confidence == "confirmed"]
        ax.plot(solid.year, solid.value, color=col, marker=marks[k], ms=6, lw=2)
        tail = s[s.year >= solid.year.max()]
        ax.plot(tail.year, tail.value, color=col, lw=2, ls="--")
        rep = s[s.confidence != "confirmed"]
        ax.scatter(rep.year, rep.value, marker=marks[k], s=48, facecolor="#FFFFFF", edgecolor=col, lw=1.6, zorder=3)
        lx, ly = s.year.iloc[-1], s.value.iloc[-1]
        ax.annotate(f"{k} ${ly:.0f}B", (lx, ly), xytext=(7, 0), textcoords="offset points", va="center", fontsize=9,
                    color=col if k != "Oracle" else INK["text"], fontweight="bold")
    ax.set_xticks(range(2022, 2027))
    ax.set_xlim(2021.8, 2026.9)
    ax.set_ylim(0, d.value.max() * 1.1)
    _below(ax)
    c.save(fig, ax, xlabel="Fiscal year", ylabel="Capital expenditure (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 13. NVIDIA vs peers: data-center revenue
# --------------------------------------------------------------------------------------
@register
def nvidia_vs_peers_dc_revenue():
    df = _fin()
    pf = load(PEER)
    nv = df[(df.period_type == "FY") & (df.metric == "revenue_data_center")].copy()
    nv["year"] = nv.period_end.str[:4].astype(int) - 1
    nv["company"] = "NVIDIA"
    p = pf[(pf.period_type == "FY") & pf.metric.isin(["revenue_data_center", "revenue_ai_semiconductor", "revenue_dcai"])].copy()
    p["year"] = p.period_end.str[:4].astype(int)
    p.loc[p.company == "Marvell", "year"] -= 1          # Marvell FY ends ~Feb 1
    years = [2022, 2023, 2024, 2025]
    allr = pd.concat([nv, p])
    allr = allr[allr.year.isin(years)]
    names = {"NVIDIA": "NVIDIA Data Center", "AMD": "AMD Data Center", "Broadcom": "Broadcom AI semis",
             "Intel": "Intel DCAI", "Marvell": "Marvell data center"}
    order = ["Intel", "AMD", "Marvell", "Broadcom", "NVIDIA"]
    v = {k: [allr[(allr.company == k) & (allr.year == y)].value.sum() or np.nan for y in years] for k in order}
    nv25, amd25, avgo25 = v["NVIDIA"][-1], v["AMD"][-1], v["Broadcom"][-1]
    c = Chart(
        id="18-nvidia-vs-peers-dc-revenue",
        title=f"NVIDIA's data-center revenue (${nv25:.0f}B) is ~{nv25 / amd25:.0f}× AMD's and ~{nv25 / avgo25:.0f}× Broadcom's AI revenue",
        subtitle="Data-center / AI revenue, US$ B per year (NVIDIA and Marvell FY mapped to prior calendar year; Intel scope changed 2024)",
        alt=(f"Grouped bar chart of data-center revenue 2022–2025: NVIDIA rose from ${v['NVIDIA'][0]:.0f}B to ${nv25:.0f}B; "
             f"AMD Data Center from ${v['AMD'][0]:.1f}B to ${amd25:.1f}B; Broadcom AI semiconductors reached ${avgo25:.1f}B; "
             f"Intel DCAI fell from ${v['Intel'][0]:.1f}B to ${v['Intel'][2]:.1f}B (partly re-segmentation); Marvell data "
             f"center ${v['Marvell'][2]:.1f}B."),
        data=[FIN, PEER], chapters=["18", "15"],
        source="company filings", source_ids=sources_of(allr),
        note="Intel DCAI = mostly Xeon CPUs",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    width = 0.16
    x = np.arange(len(years))
    for j, k in enumerate(order):
        bars = ax.bar(x + (j - 2) * width, v[k], width=width * 0.92, color=entity_color(k), label=names[k])
        for b, val in zip(bars.patches, v[k]):
            if not np.isnan(val):
                ax.annotate(f"{val:.0f}" if val >= 10 else f"{val:.1f}", (b.get_x() + b.get_width() / 2, val),
                            xytext=(0, 2), textcoords="offset points", ha="center", fontsize=7.5,
                            color=INK["title"], fontweight="bold" if k == "NVIDIA" else "normal")
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    ax.set_ylim(0, nv25 * 1.12)
    ax.legend(loc="upper left")
    _below(ax)
    c.save(fig, ax, xlabel="Calendar year (approx.)", ylabel="Revenue (US$ B)", legend=False)
