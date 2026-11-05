"""Layer 03 (memory, packaging and supply chain) STRATEGY charts: competition, history, roadmap,
value chain.

Data: hbm_and_packaging.csv, financials.csv and the layer's own files l03_rack_memory.csv,
l03_memory_verdicts.csv, l03_hbm_share_2026.csv, l03_cowos_outlook.csv, l03_memory_roadmap.csv,
l03_value_chain_margins.csv (documented in data/README.md, "Layer 03 strategy").
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, VERDICT_COLORS, entity_color, load, register,
                   sources_of)

SUPPLIER_COLORS = {"SK hynix": "#104281", "Samsung": "#3987E5", "Micron": "#9EC5F4"}  # as ch_memory.py
LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}


def _margins(fig, **over):
    """Chart.save() hard-codes left/right margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _ids(*frames) -> list[str]:
    out: list[str] = []
    for f in frames:
        for s in sources_of(f):
            if s not in out:
                out.append(s)
    return out


# ------------------------------------------------------------------------------------------
# 1. Competition: rack-level HBM bandwidth and capacity after the Rubin revision
# ------------------------------------------------------------------------------------------
@register
def rack_hbm_after_rubin_revision():
    d = load("l03_rack_memory.csv")
    launch = d[d.spec_version.str.startswith("launch")].iloc[0]
    rows = d[~d.spec_version.str.startswith("launch")].copy()
    rows["label"] = rows.system
    rows = rows.sort_values("hbm_bandwidth_tbs")
    helios = rows[rows.vendor == "AMD"].iloc[0]
    vr = rows[(rows.vendor == "NVIDIA") & (rows.system == "Vera Rubin NVL72")].iloc[0]
    c = Chart(
        id="03-rack-hbm-after-rubin-revision",
        title=(f"After the Rubin cut, Helios leads rack HBM bandwidth ({helios.hbm_bandwidth_tbs:,.0f} vs "
               f"{vr.hbm_bandwidth_tbs:,.0f} TB/s) and capacity (1.5x)"),
        subtitle="HBM bandwidth (TB/s) and capacity (TB) per rack-scale system; outline = Vera Rubin launch target (CES 2026)",
        alt=(f"Two horizontal bar charts of HBM per rack-scale system. Bandwidth: AMD Helios {helios.hbm_bandwidth_tbs:,.0f} TB/s "
             f"(72 x 19.6 TB/s), Vera Rubin NVL72 {vr.hbm_bandwidth_tbs:,.0f} TB/s after the Sep-Oct 2026 revision (launch target "
             f"{launch.hbm_bandwidth_tbs:,.0f}), Huawei CloudMatrix 384 about 1,229 TB/s across 16 racks, AWS Trn3 UltraServer 706, "
             "GB300 NVL72 576 and a Google Ironwood 64-chip cube 472 TB/s. Capacity: CloudMatrix 49.2 TB, Helios 31.1 TB, "
             "Vera Rubin, Trn3 and GB300 20.7 TB each, Ironwood cube 12.3 TB."),
        data=["l03_rack_memory.csv"], chapters=["03", "15", "08"],
        source="vendor specifications; per-chip x count where marked (repo calc)",
        source_ids=sources_of(d),
    )
    fig, axes = c.figure_grid(1, 2, width=12.0, height=6.0, sharey=True)
    y = np.arange(len(rows))

    def col(r):
        if r.vendor == "NVIDIA":
            return NV if "Rubin" in r.system else GEN_PAST
        return entity_color(r.vendor)

    colors = [col(r) for r in rows.itertuples()]
    ax = axes[0]
    ax.barh(y, rows.hbm_bandwidth_tbs, color=colors, height=0.62, zorder=3)
    vr_i = list(rows.system).index("Vera Rubin NVL72")
    ax.barh(vr_i, launch.hbm_bandwidth_tbs, height=0.62, facecolor="none", edgecolor=NV_DARK, linestyle="--",
            linewidth=1.4, zorder=4)
    ax.annotate(f"launch target {launch.hbm_bandwidth_tbs:,.0f}", (launch.hbm_bandwidth_tbs, vr_i),
                xytext=(4, 9), textcoords="offset points", fontsize=8.3, color=NV_DARK)
    for yi, v in zip(y, rows.hbm_bandwidth_tbs):
        ax.text(v + 20, yi - 0.12, f"{v:,.0f}", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, rows.label)
    ax.set_xlim(0, 1950)
    ax.set_xlabel("HBM bandwidth per system (TB/s)")
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax2 = axes[1]
    ax2.barh(y, rows.hbm_capacity_tb, color=colors, height=0.62, zorder=3)
    for yi, v in zip(y, rows.hbm_capacity_tb):
        ax2.text(v + 0.6, yi, f"{v:.1f}", va="center", fontsize=9, color=INK["title"])
    ax2.set_xlim(0, 58)
    ax2.set_xlabel("HBM capacity per system (TB)")
    ax2.grid(axis="x", color=INK["grid"])
    ax2.grid(axis="y", visible=False)
    ax2.text(0.98, 0.03, "CloudMatrix 384 spans 16 racks;\nIronwood cube is one 64-chip unit\nof a 9,216-chip domain",
             transform=ax2.transAxes, ha="right", va="bottom", fontsize=8.3, color=INK["muted"])
    _margins(fig, left=0.19, right=0.98, wspace=0.08)
    c.save(fig, list(axes), legend=False, top=0.82, bottom=0.14)


# ------------------------------------------------------------------------------------------
# 2. Competition: layer-specific verdict heatmap
# ------------------------------------------------------------------------------------------
DIMS = ["Memory per accelerator", "Bandwidth per accelerator", "Rack HBM bandwidth", "CoWoS / HBM allocation",
        "Supplier relationships", "Independence from CoWoS+HBM"]
DIM_SHORT = ["Memory per\naccelerator", "Bandwidth per\naccelerator", "Rack HBM\nbandwidth", "CoWoS / HBM\nallocation",
             "Supplier\nrelationships", "Independence\nfrom CoWoS+HBM"]


@register
def memory_supply_verdict_heatmap():
    d = load("l03_memory_verdicts.csv")
    comps = list(dict.fromkeys(d.competitor))
    beh_alloc = (d[(d.dimension == "CoWoS / HBM allocation")].verdict_vs_nvidia == "behind").sum()
    c = Chart(
        id="03-memory-supply-verdict-heatmap",
        title=f"AMD and Qualcomm out-pack Rubin per chip; all {beh_alloc} HBM-based rivals trail NVIDIA on supply access",
        subtitle="Challenger's position vs NVIDIA's 2026 flagship (Rubin / Vera Rubin NVL72) on six memory-system dimensions",
        alt=("Heatmap of six challengers against six memory-system dimensions. AMD leads on memory per accelerator (432 vs 288 GB), "
             "is at parity on per-GPU and rack bandwidth (19.6 vs 19.2 TB/s; 1,411 vs 1,400 TB/s) but is behind on CoWoS and HBM "
             "allocation (about 105k vs 595k wafers). Google TPU, AWS Trainium and Huawei are behind on per-chip memory and allocation; "
             "Qualcomm's LPDDR design leads on capacity (768 GB) and independence from CoWoS and HBM but is behind on bandwidth; "
             "SRAM start-ups lead on on-chip bandwidth and independence but trail on capacity."),
        data=["l03_memory_verdicts.csv"], chapters=["03", "15"],
        source="repo analysis (analyst judgement)",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=12.5, height=6.6)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(DIMS):
            r = d[(d.competitor == comp) & (d.dimension == dim)]
            if r.empty:
                continue
            r = r.iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            ax.text(j + 0.5, i + 0.36, LETTER[r.verdict_vs_nvidia], ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color=INK["title"])
            ax.text(j + 0.5, i + 0.68, str(r.cell_label), ha="center", va="center", fontsize=8.2, color=INK["title"])
    ax.set_xlim(0, len(DIMS))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(DIMS)) + 0.5)
    ax.set_xticklabels(DIM_SHORT, fontsize=9)
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(len(comps)) + 0.5)
    ax.set_yticklabels(comps, fontsize=9.5)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    labels = {"leads": "L = challenger leads", "parity": "P = parity", "behind": "B = behind NVIDIA",
              "different": "D = different approach"}
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in labels.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.22, right=0.985)
    c.save(fig, ax, legend=False, top=0.78, bottom=0.10)


# ------------------------------------------------------------------------------------------
# 3. History: commitments vs revenue vs CoWoS capacity (indexed)
# ------------------------------------------------------------------------------------------
@register
def commitments_vs_cowos_and_revenue():
    f = load("financials.csv")
    q = f[(f.period_type == "Q") & (f.metric.isin(["purchase_obligations", "revenue_total"]))].copy()
    q["date"] = pd.to_datetime(q.period_end)
    q = q[q.date >= "2024-01-01"]
    po = q[q.metric == "purchase_obligations"].sort_values("date")
    rev = q[q.metric == "revenue_total"].sort_values("date")
    h = load("hbm_and_packaging.csv")
    cw = h[(h.record_type == "cowos_capacity") & (h.metric == "capacity")].copy()
    cw["date"] = pd.to_datetime(cw.period.astype(str) + "-12-31")
    cw = cw.sort_values("date")
    po_x = po.value.iloc[-1] / po.value.iloc[0]
    rev_x = rev.value.iloc[-1] / rev.value.iloc[0]
    cw_x = cw.value.iloc[-1] / cw.value.iloc[0]
    c = Chart(
        id="03-commitments-vs-cowos-and-revenue",
        title=(f"NVIDIA's supply commitments grew {po_x:.0f}x since end-2023, vs {rev_x:.1f}x for revenue "
               f"and ~{cw_x:.0f}x for CoWoS"),
        subtitle="Index, end-2023 = 1: NVIDIA commitments and quarterly revenue (filings); CoWoS year-end capacity (dashed, Est.)",
        alt=(f"Log-scale index chart from end-2023 = 1. NVIDIA's purchase and supply commitments rose from ${po.value.iloc[0]:.1f}B "
             f"(January 2024) to ${po.value.iloc[-1]:.0f}B (July 2026), {po_x:.0f} times; quarterly revenue rose from "
             f"${rev.value.iloc[0]:.1f}B to ${rev.value.iloc[-1]:.1f}B, {rev_x:.1f} times; estimated TSMC CoWoS capacity rose from "
             f"about {cw.value.iloc[0]:.0f}k to {cw.value.iloc[-1]:.0f}k wafers per month by end-2026, about {cw_x:.0f} times. "
             "Commitments outgrew physical packaging capacity because they now include multi-year memory and capacity contracts "
             "at much higher memory prices."),
        data=["financials.csv", "hbm_and_packaging.csv"], chapters=["03", "13", "18"],
        source="NVIDIA filings; analyst CoWoS estimates",
        source_ids=_ids(po, rev, cw),
    )
    fig, ax = c.figure(width=11.5, height=6.0)
    ax.plot(po.date, po.value / po.value.iloc[0], color=NV, lw=2.4, marker="o", markersize=6, zorder=4)
    ax.plot(rev.date, rev.value / rev.value.iloc[0], color=INK["text"], lw=2.0, marker="s", markersize=5.5, zorder=3)
    ax.plot(cw.date, cw.value / cw.value.iloc[0], color="#256ABF", lw=2.0, ls="--", marker="D", markersize=6,
            markerfacecolor="white", zorder=3)
    ax.annotate(f"Supply commitments {po_x:.1f}x\n(${po.value.iloc[-1]:.0f}B, Q2 FY2027)",
                (po.date.iloc[-1], po_x), xytext=(8, -2), textcoords="offset points", fontsize=9, color=NV_DARK,
                fontweight="bold", va="center")
    ax.annotate(f"CoWoS capacity {cw_x:.1f}x\n(~{cw.value.iloc[-1]:.0f}k wafers/month, Est.)",
                (cw.date.iloc[-1], cw_x), xytext=(8, 4), textcoords="offset points", fontsize=9, color="#256ABF",
                fontweight="bold", va="center")
    ax.annotate(f"Quarterly revenue {rev_x:.1f}x\n(${rev.value.iloc[-1]:.1f}B)",
                (rev.date.iloc[-1], rev_x), xytext=(8, -12), textcoords="offset points", fontsize=9,
                color=INK["text"], fontweight="bold", va="center")
    ax.set_yscale("log")
    ax.set_ylim(0.8, 25)
    ax.set_yticks([1, 2, 5, 10, 20])
    ax.set_xlim(pd.Timestamp("2023-11-01"), pd.Timestamp("2027-02-15"))
    _margins(fig, right=0.76)
    c.save(fig, ax, ylabel="Index, end-2023 = 1", logy=True, legend=False)


# ------------------------------------------------------------------------------------------
# 4. History / competition: HBM supplier share shift 2025 -> 2026
# ------------------------------------------------------------------------------------------
@register
def hbm_share_shift_2025_2026():
    h = load("hbm_and_packaging.csv")
    old = h[(h.record_type == "hbm_market_share") & (h.period.isin(["2025-Q2", "2025-Q3"])) & h.supplier.notna()]
    old = old.rename(columns={"value": "share_pct"})[["period", "supplier", "share_pct", "confidence", "source_id"]]
    new = load("l03_hbm_share_2026.csv")
    act = pd.concat([old, new[new.kind == "actual"][["period", "supplier", "share_pct", "confidence", "source_id"]]])
    fc = new[new.kind == "forecast"].iloc[0]
    periods = ["2025-Q2", "2025-Q3", "2026-Q1", "2026-Q2"]
    labels = ["Q2 2025", "Q3 2025", "Q1 2026", "Q2 2026"]
    sam0 = act[(act.period == "2025-Q2") & (act.supplier == "Samsung")].share_pct.iloc[0]
    sam1 = act[(act.period == "2026-Q2") & (act.supplier == "Samsung")].share_pct.iloc[0]
    skh0 = act[(act.period == "2025-Q2") & (act.supplier == "SK hynix")].share_pct.iloc[0]
    skh1 = act[(act.period == "2026-Q2") & (act.supplier == "SK hynix")].share_pct.iloc[0]
    c = Chart(
        id="03-hbm-share-shift-2025-2026",
        title=(f"Samsung's HBM share nearly doubled to {sam1:.0f}% in a year; SK hynix fell from {skh0:.0f}% "
               f"to {skh1:.0f}%"),
        subtitle="Share of HBM revenue by supplier, % (Counterpoint Research); hatched bar = forecast for Samsung in Q4 2026",
        alt=(f"Stacked 100% bar chart of HBM revenue share. Q2 2025: SK hynix {skh0:.0f}%, Micron 21%, Samsung {sam0:.0f}%. Q3 2025: "
             f"57/21/22. Q1 2026: SK hynix 58%, Samsung 21%, Micron 21%. Q2 2026: SK hynix {skh1:.0f}%, Samsung {sam1:.0f}%, Micron 18%. "
             f"A hatched bar shows the forecast of about {fc.share_pct:.0f}% for Samsung in Q4 2026 (KB Securities, echoed by Samsung)."),
        data=["hbm_and_packaging.csv", "l03_hbm_share_2026.csv"], chapters=["03", "18"],
        source="Counterpoint Research; KB Securities forecast",
        source_ids=_ids(act, new),
    )
    fig, ax = c.figure(width=11.0, height=5.9)
    x = np.arange(len(periods))
    bottom = np.zeros(len(periods))
    for s in ["SK hynix", "Samsung", "Micron"]:
        vals = np.array([act[(act.period == p) & (act.supplier == s)].share_pct.iloc[0] for p in periods], dtype=float)
        ax.bar(x, vals, bottom=bottom, color=SUPPLIER_COLORS[s], width=0.6, zorder=2, edgecolor="white", linewidth=0.8)
        for xi, v, bt in zip(x, vals, bottom):
            ax.text(xi, bt + v / 2, f"{s}\n{v:.0f}%", ha="center", va="center", fontsize=8.6,
                    color="white" if s != "Micron" else INK["title"], fontweight="bold")
        bottom += vals
    xf = len(periods) + 0.35
    b = ax.bar([xf], [fc.share_pct], color=SUPPLIER_COLORS["Samsung"], width=0.5, zorder=2, edgecolor="white",
               hatch="///", alpha=0.75)
    ax.text(xf, fc.share_pct / 2, f"Samsung\n~{fc.share_pct:.0f}%\n(forecast)", ha="center", va="center", fontsize=8.6,
            color="white", fontweight="bold")
    ax.text(xf, fc.share_pct + 3, "others n/a", ha="center", fontsize=8, color=INK["muted"])
    ax.axvline(len(periods) - 0.4, color=INK["base"], lw=1, ls=":")
    ax.set_xticks(list(x) + [xf], labels + ["Q4 2026F"])
    ax.set_ylim(0, 102)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.text(1.5, 103.5, "Q4 2025 and Q3 2026 splits not used (not found in the cited sources)", ha="center",
            fontsize=8.2, color=INK["muted"])
    c.save(fig, ax, ylabel="Share of HBM revenue", legend=False)


# ------------------------------------------------------------------------------------------
# 5. Roadmap: memory per accelerator by vendor, 2024-2028
# ------------------------------------------------------------------------------------------
@register
def memory_roadmap_by_vendor():
    d = load("l03_memory_roadmap.csv")
    base = d[d.variant == "base"].copy()
    ru = base[base["product"] == "Rubin Ultra"].iloc[0]
    alt = d[d.variant == "alt-report"].iloc[0]
    lt = d[d.variant == "launch-target"].iloc[0]
    c = Chart(
        id="03-memory-roadmap-by-vendor",
        title=("2026 flagships converge at ~19-20 TB/s; Rubin Ultra (1 TB HBM4E) targets the capacity lead "
               "in 2027"),
        subtitle="Memory per accelerator package by year: capacity (GB, left) and bandwidth (TB/s, right); hollow = roadmap or estimate",
        alt=("Two line charts of memory per accelerator, 2024-2028. Capacity: NVIDIA B200 180 GB, B300 288, Rubin 288, Rubin Ultra "
             f"{ru.capacity_gb:,.0f} GB announced for 2027 (a report says {alt.capacity_gb:.0f} GB); AMD MI325X 256, MI355X 288, MI455X 432; "
             "Google Trillium 32 and Ironwood 192; AWS Trainium2 96, Trainium3 144, Trainium4 about 288 (estimate); Huawei 910C 128, "
             "950DT 144, 960 and 970 288. Bandwidth: Rubin 19.2 TB/s (launch target 22), MI455X 19.6, Trainium4 about 19.6 (estimate), "
             "Ironwood 7.37, Huawei 950DT 4.0 rising to 14.4 in 2028, Rubin Ultra about 32 TB/s."),
        data=["l03_memory_roadmap.csv"], chapters=["03", "15", "17"],
        source="vendor roadmaps; Trainium4 = repo Est.",
        source_ids=sources_of(d),
    )
    fig, axes = c.figure_grid(1, 2, width=12.8, height=6.2)
    vendors = ["Huawei", "AWS", "Google", "AMD", "NVIDIA"]
    for ax, col, unit in ((axes[0], "capacity_gb", "GB"), (axes[1], "bandwidth_tbs", "TB/s")):
        for v in vendors:
            s = base[(base.vendor == v) & base[col].notna()].sort_values("year")
            if s.empty:
                continue
            color = entity_color(v)
            ax.plot(s.year, s[col], color=color, lw=2.6 if v == "NVIDIA" else 2.0, zorder=4 if v == "NVIDIA" else 3)
            for r in s.itertuples():
                hollow = r.status == "roadmap" or r.confidence == "estimate"
                ax.scatter(r.year, getattr(r, col), s=60, color="white" if hollow else color, edgecolor=color,
                           linewidth=2, zorder=5)
            last = s.iloc[-1]
            name = {"NVIDIA": "NVIDIA", "AMD": "AMD", "Google": "Google TPU", "AWS": "AWS Trainium",
                    "Huawei": "Huawei Ascend"}[v]
            dy = {"capacity_gb": {"AWS": 10, "Huawei": -10, "Google": 0, "AMD": 0, "NVIDIA": 0},
                  "bandwidth_tbs": {"AWS": -10, "Huawei": 0, "Google": 0, "AMD": 10, "NVIDIA": 0}}[col][v]
            ax.annotate(f"{name} {last[col]:,.4g}", (last.year, last[col]), xytext=(7, dy), textcoords="offset points",
                        fontsize=8.6, color=color, fontweight="bold", va="center")
        ax.set_xticks([2024, 2025, 2026, 2027, 2028])
        ax.set_xlim(2023.7, 2029.3)
        ax.set_ylabel(f"Memory {'capacity' if unit == 'GB' else 'bandwidth'} per accelerator ({unit})")
        ax.set_xlabel("Year of availability (announced / roadmap)")
    # extras: Rubin launch target and Rubin Ultra 768 GB report
    axes[1].scatter(lt.year, lt.bandwidth_tbs, marker="D", s=50, color="white", edgecolor=NV_DARK, linewidth=1.6, zorder=6)
    axes[1].annotate(f"Rubin launch target {lt.bandwidth_tbs:.0f}", (lt.year, lt.bandwidth_tbs), xytext=(-8, 8),
                     textcoords="offset points", ha="right", fontsize=8.3, color=NV_DARK)
    axes[0].scatter(alt.year, alt.capacity_gb, marker="v", s=60, color="white", edgecolor=NV_DARK, linewidth=1.6, zorder=6)
    axes[0].annotate(f"reported {alt.capacity_gb:.0f} GB option", (alt.year, alt.capacity_gb), xytext=(-8, -2),
                     textcoords="offset points", ha="right", va="center", fontsize=8.3, color=NV_DARK)
    axes[0].set_ylim(0, 1150)
    axes[1].set_ylim(0, 36)
    _margins(fig, left=0.07, right=0.96, wspace=0.32)
    c.save(fig, list(axes), legend=False, top=0.84, bottom=0.13)


# ------------------------------------------------------------------------------------------
# 6. Roadmap: CoWoS capacity outlook to 2028
# ------------------------------------------------------------------------------------------
@register
def cowos_capacity_outlook():
    d = load("l03_cowos_outlook.csv").sort_values("year_end")
    first, last = d.iloc[0], d.iloc[-1]
    c = Chart(
        id="03-cowos-capacity-outlook-2028",
        title=(f"Reported plans would take CoWoS to ~{last.mid_k_wpm:.0f}k wafers/month by 2028, "
               f"~{last.mid_k_wpm / first.mid_k_wpm:.0f}x end-2023"),
        subtitle="TSMC CoWoS capacity at year end, k wafers/month: midpoint and range of press-reported estimates (all Est.)",
        alt=("Bar chart with ranges of estimated TSMC CoWoS capacity at year end: 2023 about 15k wafers per month (13-15k), "
             "2024 about 35k (32-40k), 2025 about 75k (65-80k), 2026 about 120k (105-130k), 2027 projected 170-200k and 2028 "
             "projected about 260k, roughly 17 times end-2023. All figures are analyst or press estimates; TSMC does not disclose "
             "CoWoS capacity in wafers."),
        data=["l03_cowos_outlook.csv"], chapters=["03", "18"],
        source="analyst and press estimates",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=11.0, height=5.9)
    x = np.arange(len(d))
    proj = (d.kind == "projection").values
    bars = ax.bar(x, d.mid_k_wpm, color=["#256ABF" if not p else "#86B6EF" for p in proj], width=0.6, zorder=2,
                  hatch="//", edgecolor="white")
    lo = d.mid_k_wpm - d.low_k_wpm
    hi = d.high_k_wpm - d.mid_k_wpm
    ax.errorbar(x, d.mid_k_wpm, yerr=[lo, hi], fmt="none", ecolor=INK["title"], elinewidth=1.3, capsize=5, zorder=3)
    for xi, r in zip(x, d.itertuples()):
        rng = f"{r.low_k_wpm:.0f}-{r.high_k_wpm:.0f}k" if r.low_k_wpm != r.high_k_wpm else f"~{r.mid_k_wpm:.0f}k"
        ax.text(xi, r.high_k_wpm + 6, rng, ha="center", fontsize=9, color=INK["title"], fontweight="bold")
    ax.set_xticks(x, [f"End-{int(y)}" for y in d.year_end])
    ax.set_ylim(0, 300)
    handles = [Patch(facecolor="#256ABF", hatch="//", edgecolor="white", label="Estimate of capacity in place"),
               Patch(facecolor="#86B6EF", hatch="//", edgecolor="white", label="Projection (reported plans)")]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    c.save(fig, ax, ylabel="CoWoS capacity (k wafers per month)", legend=False)


# ------------------------------------------------------------------------------------------
# 7. Value chain: margin ladder
# ------------------------------------------------------------------------------------------
ROLE_COLORS = {"HBM / DRAM maker": "#104281", "GPU and system designer": NV, "connectivity silicon (PCIe/CXL)": "#7A7A7A",
               "foundry + CoWoS packaging": "#3987E5", "test equipment": "#86B6EF", "EMS / rack ODM": "#B5B5B5",
               "rack ODM (Est.)": "#B5B5B5"}


@register
def value_chain_margins():
    d = load("l03_value_chain_margins.csv").sort_values("margin_pct")
    mu = d[d.company == "Micron"].iloc[0]
    nv = d[d.company == "NVIDIA"].iloc[0]
    c = Chart(
        id="03-value-chain-margins",
        title=(f"Memory makers now out-earn NVIDIA: Micron's gross margin {mu.margin_pct:.1f}% vs NVIDIA's "
               f"{nv.margin_pct:.1f}%; ODMs ~2%"),
        subtitle="Latest margin by company in the AI-rack supply chain, %; hatched = operating margin (gross is higher) or estimate",
        alt=("Horizontal bar chart of margins: Micron 86.8% GAAP gross margin (fiscal Q4 2026), SK hynix about 80% operating margin "
             "(Q3 2026), NVIDIA 75.0% gross (Q2 FY2027), Astera Labs about 72% gross (guidance), TSMC 66.4% gross (Q3 2026), "
             "Advantest 51.9% operating (FY2026 forecast), Foxconn about 6.3% gross (Q2 2025) and rack ODMs an estimated 2.7% "
             "(GB300 NVL72) and 1.9% (Vera Rubin NVL72) gross margin on the rack."),
        data=["l03_value_chain_margins.csv"], chapters=["03", "13", "18"],
        source="company results; ODM = Morgan Stanley Est.",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=12.0, height=6.0)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        op = r.metric == "operating"
        ax.barh(yi, r.margin_pct, color=ROLE_COLORS.get(r.role, "#B5B5B5"), height=0.64, zorder=3,
                hatch="//" if (op or r.confidence == "estimate") else None, edgecolor="white")
        lab = f"{r.margin_pct:.1f}%  {'operating' if op else 'gross'} · {r.period}"
        ax.text(r.margin_pct + 1.0, yi, lab, va="center", fontsize=8.6, color=INK["title"])
    ax.set_yticks(y, [f"{r.company}\n({r.role})" for r in d.itertuples()], fontsize=8.6)
    ax.set_xlim(0, 125)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.27, right=0.98)
    c.save(fig, ax, xlabel="Margin (%)", legend=False)
