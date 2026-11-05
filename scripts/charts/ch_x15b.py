"""Chapter 15 part B (competitive landscape: custom-ASIC houses, Intel, Qualcomm, inference start-ups, China).

Owner: chapter-15b agent. Data: data/x15_*.csv (this chapter) plus competitor_matrix.csv,
competitor_accelerators.csv, cs6_china_parts.csv and gpu_product_specs.csv (read-only).
Chart ids are prefixed "15-".
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import (Chart, GEN_PAST, INK, NV, VERDICT_COLORS, entity_color, load, register, sources_of)

CH = ["15"]
PINK = entity_color("broadcom")
QC = entity_color("qualcomm")
HW = entity_color("huawei")
INTEL = entity_color("intel")
GRAY = entity_color("startups")
LIGHT = entity_color("other")


def _widen(fig, **over):
    """Chart.save() hard-codes left/right margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _bar_label(ax, x, y, text, color=None, ha="left", dx=4, fontsize=8.5, weight="normal"):
    ax.annotate(text, (x, y), xytext=(dx if ha == "left" else -dx, 0), textcoords="offset points",
                ha=ha, va="center", fontsize=fontsize, color=color or INK["text"], fontweight=weight)


# --------------------------------------------------------------------------------------
# Custom-ASIC houses
# --------------------------------------------------------------------------------------
@register
def broadcom_ai_revenue_guidance():
    df = load("x15_custom_silicon_scale.csv")
    d = df[df.chart_group == "broadcom_trajectory"].copy()
    b = d[d.company == "Broadcom"].set_index("period").value_usd_b
    n = d[d.company == "NVIDIA"].set_index("period").value_usd_b
    ratio = b["FY2027"] / n["FY2026"]
    c = Chart(
        id="15-broadcom-ai-revenue-guidance",
        title=(f"Broadcom's AI revenue rose ~{b['FY2026'] / b['FY2023']:.0f}× to ~${b['FY2026']:.0f}B; "
               f"its FY2027 goal is ~{ratio:.0%} of NVIDIA's FY2026 DC"),
        subtitle="US$ B per fiscal year, aligned by calendar year (Broadcom FY ends ~Nov; NVIDIA FY ends late Jan, so NVIDIA FY2026 ≈ CY2025)",
        alt=(f"Grouped bar chart aligned by calendar year. Broadcom AI semiconductor revenue: ${b['FY2023']:.1f}B (FY2023), "
             f"${b['FY2024']:.1f}B (FY2024), ${b['FY2025']:.1f}B (FY2025), about ${b['FY2026']:.0f}B in FY2026 (Q4 guided), "
             f"a management target of about ${b['FY2027']:.0f}B for FY2027 and a 'line of sight' to about ${b['FY2028']:.0f}B in FY2028 (hatched). "
             f"NVIDIA data-center revenue: ${n['FY2024']:.1f}B (FY2024), ${n['FY2025']:.1f}B (FY2025) and ${n['FY2026']:.1f}B (FY2026); "
             f"NVIDIA booked ${n['H1 FY2027']:.0f}B in the first half of FY2027 alone. Broadcom's FY2027 target equals about {ratio:.0%} of NVIDIA's FY2026 data-center revenue."),
        data=["x15_custom_silicon_scale.csv"], chapters=CH + ["02", "18"],
        source="Broadcom and NVIDIA filings and calls", source_ids=sources_of(d),
        note="Hatched = management target / aspiration, not reported revenue",
    )
    fig, ax = c.figure(12, 6.0)
    years = ["CY2023", "CY2024", "CY2025", "CY2026", "CY2027", "CY2028"]
    bfy = ["FY2023", "FY2024", "FY2025", "FY2026", "FY2027", "FY2028"]
    nfy = ["FY2024", "FY2025", "FY2026"]
    x = np.arange(len(years))
    w = 0.38
    bv = [b[f] for f in bfy]
    bars = ax.bar(x - w / 2, bv, w, color=PINK, label="Broadcom AI semiconductor revenue (FY)")
    for i, p in enumerate(bars.patches):
        if bfy[i] in ("FY2027", "FY2028"):
            p.set_hatch("///")
            p.set_alpha(0.7)
        lab = f"${bv[i]:.0f}B" if bv[i] >= 10 else f"${bv[i]:.1f}B"
        tag = {"FY2026": " (Q4 guided)", "FY2027": " target", "FY2028": " aspiration"}.get(bfy[i], "")
        ax.annotate(f"{bfy[i]}\n{lab}{tag}", (p.get_x() + p.get_width() / 2, bv[i]), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, color=INK["text"])
    nv = [n[f] for f in nfy]
    nb = ax.bar(x[:3] + w / 2, nv, w, color=NV, label="NVIDIA data-center revenue (FY)")
    for i, p in enumerate(nb.patches):
        ax.annotate(f"{nfy[i]}\n${nv[i]:.0f}B", (p.get_x() + p.get_width() / 2, nv[i]), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, color=NV_TXT)
    ax.annotate(f"NVIDIA booked ${n['H1 FY2027']:.0f}B of\ndata-center revenue in\nH1 FY2027 alone", (x[3], 150),
                ha="center", va="bottom", fontsize=8, color=NV_TXT, style="italic")
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylim(0, 255)
    ax.legend(loc="upper left")
    c.save(fig, ax, ylabel="US$ B per fiscal year", xlabel="Calendar year the fiscal year mostly covers", legend=False)


NV_TXT = "#3F6B00"


@register
def asic_house_revenue_scale():
    df = load("x15_custom_silicon_scale.csv")
    d = df[df.chart_group == "field_scale"].copy().sort_values("value_usd_b")
    bro = d[d.company == "Broadcom"].value_usd_b.iloc[0]
    mrv = d[d.company == "Marvell"].value_usd_b.iloc[0]
    alc = d[d.company == "Alchip"].value_usd_b.iloc[0]
    c = Chart(
        id="15-asic-house-revenue-scale",
        title=(f"Broadcom's ~${bro:.0f}B AI year is ~{bro / mrv:.0f}× Marvell's data-center run-rate and "
               f"~{bro / alc:.0f}× Alchip's whole revenue"),
        subtitle="Latest annual (or annualised) revenue figure per custom-silicon house, US$ B (log scale); bases differ and are labelled",
        alt=("Horizontal log-scale bar chart of custom-silicon revenue scale: Broadcom about $58B of AI semiconductor revenue "
             "in FY2026 (custom XPUs about 73% of it); Marvell about $8.7B data-center revenue annualised from its Q2 FY2027 quarter; "
             "MediaTek a $2B AI-ASIC revenue target for 2026; GUC about $1.07B total 2025 revenue (NT$34.1B converted); Alchip "
             "$0.99B total 2025 revenue; and Qualcomm at least $1B of FY2027 custom-silicon revenue from two hyperscalers (target). "
             "Broadcom is roughly seven times Marvell and almost 60 times Alchip."),
        data=["x15_custom_silicon_scale.csv"], chapters=CH + ["02", "13", "19"],
        source="company results, guidance and press reports", source_ids=sources_of(d),
        note="Hatched = target or repo estimate (annualised / FX-converted)",
    )
    fig, ax = c.figure(10.5, 5.4)
    names = list(d.company)
    vals = list(d.value_usd_b)
    cols = [entity_color(nm) if nm in ("Broadcom", "Marvell", "Qualcomm") else LIGHT for nm in names]
    y = np.arange(len(names))
    bars = ax.barh(y, vals, color=cols, height=0.6)
    for i, (p, conf, basis, per) in enumerate(zip(bars.patches, d.confidence, d.basis, d.period)):
        if conf == "estimate" or "target" in basis:
            p.set_hatch("///")
            p.set_alpha(0.75)
        lbl = {"ai_semiconductor_revenue": "AI semis", "data_center_revenue_annualised": "data center, annualised",
               "ai_asic_revenue_target": "AI-ASIC target", "total_revenue": "total revenue",
               "custom_silicon_revenue_floor": "custom silicon, floor target"}[d.metric.iloc[i]]
        _bar_label(ax, vals[i], i, f"${vals[i]:.2g}B · {per} {lbl}", fontsize=8.5)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xscale("log")
    ax.set_xlim(0.5, 600)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    _widen(fig, left=0.11, right=0.97)
    c.save(fig, ax, xlabel="US$ B", logx=True)


@register
def asic_breakeven():
    p = load("x15_asic_breakeven.csv").set_index("parameter")
    price = p.loc["merchant_price_per_gpu", "value"]
    unit = p.loc["asic_unit_cost", "value"]
    fixed = (p.loc["chip_nre", "value"] + p.loc["software_and_systems_team", "value"]) * 1e9
    cases = [("base", p.loc["asic_relative_throughput_base", "value"], "-"),
             ("low", p.loc["asic_relative_throughput_low", "value"], "--"),
             ("high", p.loc["asic_relative_throughput_high", "value"], ":")]
    be = {k: fixed / (price - unit / r) for k, r, _ in cases}
    c = Chart(
        id="15-asic-breakeven-volume",
        title=(f"Est.: a custom ASIC repays ~${fixed / 1e9:.1f}B of fixed cost after ~{be['base'] / 1e3:.0f}k GPU-equivalents; "
               f"at half a GPU's speed it needs ~{be['low'] / 1e3:.0f}k"),
        subtitle="Repo model: cumulative cost (US$ B) to deploy N GPU-equivalents of capacity, merchant GPU vs custom ASIC (NRE + team + unit cost)",
        alt=(f"Line chart of a repo break-even model. Buying merchant GPUs costs ${price / 1e3:.0f}K each, so cost rises in a straight line "
             f"from zero. A custom ASIC starts with ${fixed / 1e9:.2f}B of fixed cost (a ~$0.59B 3 nm design and a ~$0.6B software and systems team) "
             f"and costs ${unit / 1e3:.0f}K per chip. If each chip does 70% of a GPU's useful work, the lines cross at about {be['base'] / 1e3:.0f}k "
             f"GPU-equivalents; at 50% the crossover moves to about {be['low'] / 1e3:.0f}k; at 90% it falls to about {be['high'] / 1e3:.0f}k. "
             "Only buyers deploying hundreds of thousands of accelerators clear the bar comfortably."),
        data=["x15_asic_breakeven.csv"], chapters=CH + ["14", "18", "19"],
        source="repo model; inputs from Epoch AI, NVIDIA CEO remarks, IBS/Silicon Analysts", source_ids=sources_of(load("x15_asic_breakeven.csv")),
        note="Illustrative model (speculative inputs); excludes power, networking and opportunity cost",
    )
    fig, ax = c.figure(10.5, 5.9)
    xs = np.linspace(0, 400_000, 401)
    ax.plot(xs / 1e3, price * xs / 1e9, color=NV, lw=2.4, label=f"Merchant GPU at ${price / 1e3:.0f}K")
    for k, r, ls in cases:
        ys = (fixed + unit / r * xs) / 1e9
        ax.plot(xs / 1e3, ys, color=PINK, lw=2.0 if k == "base" else 1.6, ls=ls,
                label=f"Custom ASIC, {r:.0%} of GPU throughput per chip")
        bx = be[k]
        ax.scatter([bx / 1e3], [price * bx / 1e9], color=PINK, s=40, zorder=4)
        off = {"base": (8, -14), "low": (6, -14), "high": (-8, 10)}[k]
        ax.annotate(f"break-even ~{bx / 1e3:.0f}k", (bx / 1e3, price * bx / 1e9), xytext=off,
                    textcoords="offset points", fontsize=8.5, color=INK["text"], ha="right" if k == "high" else "left")
    ax.axhline(fixed / 1e9, color=INK["base"], lw=1, ls="-")
    ax.annotate(f"Fixed cost ${fixed / 1e9:.2f}B (design NRE + team)", (300, fixed / 1e9), xytext=(0, 4),
                textcoords="offset points", fontsize=8.5, color=INK["muted"])
    ax.set_xlim(0, 400)
    ax.set_ylim(0, 14.5)
    ax.legend(loc="upper left")
    c.save(fig, ax, xlabel="GPU-equivalents deployed (thousands)", ylabel="Cumulative cost, US$ B", legend=False)


# --------------------------------------------------------------------------------------
# Intel
# --------------------------------------------------------------------------------------
@register
def latest_quarter_dc_revenue():
    df = load("x15_dc_revenue_benchmarks.csv")
    d = df[df.chart_group == "latest_quarter"].copy().sort_values("value_usd_b")
    nv = d[d.entity == "NVIDIA"].value_usd_b.iloc[0]
    it = d[d.entity == "Intel"].value_usd_b.iloc[0]
    bro = d[d.entity == "Broadcom"].value_usd_b.iloc[0]
    c = Chart(
        id="15-latest-quarter-dc-revenue",
        title=(f"Intel's data-center segment (${it:.1f}B a quarter) is ~{it / nv:.0%} of NVIDIA's and "
               f"under half of Broadcom's AI revenue"),
        subtitle="Latest reported quarter of data-center (or AI) revenue per vendor, US$ B; segment definitions differ and are labelled",
        alt=(f"Horizontal bar chart of the latest reported quarter: NVIDIA data center ${nv:.1f}B (Q2 FY2027, to July 2026); "
             f"Broadcom AI semiconductors ${bro:.1f}B (Q3 FY2026, to August 2026); Intel Data Center and AI segment ${it:.1f}B "
             "(Q3 2026, to September 2026, mostly Xeon CPUs, +78% y/y); AMD data center $6.7B (Q2 2026, EPYC plus Instinct); "
             f"Marvell data center $2.2B (Q2 FY2027). Intel's segment is about {it / nv:.0%} of NVIDIA's."),
        data=["x15_dc_revenue_benchmarks.csv"], chapters=CH + ["04", "18"],
        source="company results", source_ids=sources_of(d),
    )
    fig, ax = c.figure(10.5, 5.0)
    y = np.arange(len(d))
    cols = [entity_color(e) for e in d.entity]
    ax.barh(y, d.value_usd_b, color=cols, height=0.6)
    lbl = {"data_center_revenue": "data center", "ai_semiconductor_revenue": "AI semiconductors",
           "dcai_segment_revenue": "Data Center & AI segment"}
    for i, (_, r) in enumerate(d.iterrows()):
        _bar_label(ax, r.value_usd_b, i, f"${r.value_usd_b:.1f}B · {lbl[r.metric]} · {r.period}", fontsize=8.5)
    ax.set_yticks(y)
    ax.set_yticklabels(d.entity)
    ax.set_xlim(0, 135)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    _widen(fig, left=0.10, right=0.97)
    c.save(fig, ax, xlabel="US$ B in the quarter")


SHORT_AX = {"Peak compute": "Compute", "Memory capacity & bandwidth": "Memory", "Scale-up fabric": "Scale-up",
            "Scale-out networking": "Scale-out", "Software ecosystem": "Software", "Rack-scale systems": "Racks",
            "Supply access (CoWoS/HBM)": "Supply", "Cost/TCO": "Cost/TCO", "Merchant availability": "Merchant"}
LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}


def _profile(comp: str, chart_id: str, title: str, alt_tail: str, chapters: list[str]):
    import matplotlib.pyplot as plt
    df = load("competitor_matrix.csv")
    sub = df[df.competitor.isin([comp, "NVIDIA"])]
    cap = sub[sub.dimension_type == "capability"]
    axes_names = list(cap[cap.competitor == "NVIDIA"].dimension)
    nvc = cap[cap.competitor == "NVIDIA"].set_index("dimension").score_0_5.reindex(axes_names).values
    cc = cap[cap.competitor == comp].set_index("dimension").score_0_5.reindex(axes_names).values
    lay = sub[sub.dimension_type == "layer"]
    layers = sorted(lay.dimension.unique())
    lc = lay[lay.competitor == comp].set_index("dimension").reindex(layers)
    ln = lay[lay.competitor == "NVIDIA"].set_index("dimension").score_0_5.reindex(layers)
    counts = lc.verdict_vs_nvidia.value_counts().to_dict()
    col = entity_color(comp)
    alt = (f"Two-panel chart. Left: radar of {comp} versus NVIDIA on nine capability axes, averaging {cc.mean():.1f} versus "
           f"{nvc.mean():.1f} of 5 (" + "; ".join(f"{SHORT_AX[a]} {int(v)} vs {int(nv)}" for a, v, nv in zip(axes_names, cc, nvc)) +
           f"). Right: {comp}'s score in each of NVIDIA's 12 stack layers with its verdict: " +
           ", ".join(f"{k} {v}" for k, v in counts.items()) + ". " + alt_tail)
    c = Chart(
        id=chart_id, title=title,
        subtitle="Repo scores 0-5 (analyst judgement, sourced): capability radar (left) and per-layer score with verdict vs NVIDIA (right)",
        alt=alt, data=["competitor_matrix.csv"], chapters=chapters,
        source="repo analysis (competitor_matrix.csv)", source_ids=sources_of(sub)[:12],
        note="Analyst judgement (speculative); L/P/B/D = leads / parity / behind / different approach",
    )
    fig = plt.figure(figsize=(12, 6.4))
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)
    n = len(axes_names)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    ang_c = ang + ang[:1]
    ax1.plot(ang_c, list(nvc) + [nvc[0]], color=NV, lw=1.8, ls="--", label="NVIDIA reference")
    ax1.fill(ang_c, list(cc) + [cc[0]], color=col, alpha=0.28)
    ax1.plot(ang_c, list(cc) + [cc[0]], color=col, lw=2.2, label=comp)
    ax1.scatter(ang, cc, color=col, s=18, zorder=3)
    ax1.set_ylim(0, 5)
    ax1.set_yticks([1, 2, 3, 4, 5])
    ax1.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=7, color=INK["muted"])
    ax1.set_xticks(ang)
    ax1.set_xticklabels([SHORT_AX[a] for a in axes_names], fontsize=8.5, color=INK["text"])
    ax1.grid(color=INK["grid"], lw=0.7)
    ax1.spines["polar"].set_color(INK["base"])
    ax1.set_title(f"{comp}: avg {cc.mean():.1f} vs NVIDIA {nvc.mean():.1f}", fontsize=10.5, fontweight="bold",
                  color=INK["title"], pad=22)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, fontsize=8.5, frameon=False)
    y = np.arange(len(layers))[::-1]
    for yi, lname in zip(y, layers):
        r = lc.loc[lname]
        ax2.barh(yi, r.score_0_5, color=VERDICT_COLORS[r.verdict_vs_nvidia], height=0.66, edgecolor=INK["base"], lw=0.6)
        ax2.annotate(LETTER[r.verdict_vs_nvidia], (r.score_0_5, yi), xytext=(4, 0), textcoords="offset points",
                     va="center", fontsize=8.5, fontweight="bold", color=INK["text"])
        ax2.scatter([ln.loc[lname]], [yi], marker="D", color=NV, s=30, zorder=4)
    ax2.set_yticks(y)
    ax2.set_yticklabels([lname for lname in layers], fontsize=8.2)
    ax2.set_xlim(0, 5.6)
    ax2.set_xlabel("Score 0-5 (green diamond = NVIDIA)")
    ax2.grid(axis="x", color=INK["grid"])
    ax2.grid(axis="y", visible=False)
    ax2.tick_params(length=0)
    ax2.legend(handles=[Patch(facecolor=VERDICT_COLORS[k], edgecolor=INK["base"], label=f"{LETTER[k]} = {k}")
                        for k in ("leads", "parity", "behind", "different")] +
               [Line2D([0], [0], marker="D", color="w", markerfacecolor=NV, markersize=7, label="NVIDIA")],
               loc="upper center", bbox_to_anchor=(0.42, -0.1), ncol=5, fontsize=7.8, frameon=False)
    _widen(fig, left=0.04, right=0.98, wspace=0.62)
    c.save(fig, [ax1, ax2], legend=False, top=0.76, bottom=0.17)


@register
def intel_profile():
    _profile("Intel", "15-intel-capability-profile",
             "Intel trails NVIDIA in 10 of 12 layers; only its CPU is at parity and its packaging is a different route",
             "Intel's only parity layer is the CPU (Xeon as AI host) and its packaging (EMIB, Foveros) is scored as a "
             "different approach; accelerators, scale-up, racks and software are behind.",
             CH + ["04", "03"])


@register
def qualcomm_profile():
    _profile("Qualcomm", "15-qualcomm-capability-profile",
             "Qualcomm averages 2.7 of 5 vs NVIDIA's 4.7; it out-scores NVIDIA only on claimed cost per token",
             "Public information only: Qualcomm's LPDDR-based design scores on memory capacity and on independence from "
             "CoWoS and HBM, its cost claim is a vendor claim, and scale-up, software and racks are early.",
             CH + ["19", "11"])


# --------------------------------------------------------------------------------------
# Qualcomm (public information only)
# --------------------------------------------------------------------------------------
@register
def qualcomm_dc_roadmap_timeline():
    import matplotlib.pyplot as plt
    df = load("x15_qualcomm_dc_timeline.csv")
    lanes = ["Customers & partners", "Connectivity & software", "AI accelerators", "Server CPUs"]
    lane_y = {nm: i for i, nm in enumerate(lanes)}
    df["d"] = pd.to_datetime(df.date.apply(lambda s: s + "-15" if len(s) == 7 else s))
    n_moves = int(((df.d >= "2025-05-01") & (df.status != "roadmap")).sum())
    c = Chart(
        id="15-qualcomm-dc-roadmap-timeline",
        title=f"Qualcomm's datacenter push: {n_moves} public moves since May 2025; accelerator volume is a 2026–28 target",
        subtitle="Public announcements only, by lane; filled = shipped / closed / signed, hollow = announced roadmap, × = exit",
        alt=("Timeline of Qualcomm's public datacenter moves in four lanes. Before 2025: Centriq 2400 server CPU (Nov 2017), the unit wound "
             "down (2018), NUVIA bought for $1.4B (2021) and the Cloud AI 100 Ultra card (2023). Since May 2025: NVLink Fusion CPU "
             "partnership and HUMAIN MoU (May 2025); AI200 and AI250 unveiled with HUMAIN's 200 MW plan (Oct 2025); Ventana (RISC-V) "
             "and Alphawave (~$2.4B) acquisitions (Dec 2025); Investor Day with the Dragonfly C1000 CPU for Meta, the AI300 accelerator "
             "and the Modular deal (Jun 2026); Modular closed at $3.9B (Jul 2026); a multi-generation AWS custom inference-silicon and "
             "1.6T optics deal backed by a $4B warrant (Sep 2026). Roadmap: AI200 in 2026 (no volume shipment confirmed by Nov 2026), "
             "AI250 in 2027, AI300 and C1000 deployments in 2028."),
        data=["x15_qualcomm_dc_timeline.csv"], chapters=CH + ["19", "04"],
        source="Qualcomm releases, filings and press coverage (public information only)", source_ids=sources_of(df),
        note="Public information only; dates of roadmap items are company targets",
    )
    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12.5, 6.6), gridspec_kw=dict(width_ratios=[1, 3.1]), sharey=True)
    status_style = {
        "shipped": dict(marker="o", facecolor=None, edge=None),
        "closed": dict(marker="o", facecolor=None, edge=None),
        "signed": dict(marker="s", facecolor=None, edge=None),
        "announced": dict(marker="D", facecolor=None, edge=None),
        "roadmap": dict(marker="D", facecolor="#FFFFFF", edge=None),
        "exited": dict(marker="X", facecolor=None, edge=None),
    }
    for ax in (axl, axr):
        for nm, yv in lane_y.items():
            ax.axhline(yv, color=INK["grid"], lw=6, zorder=0, solid_capstyle="butt")
        for _, r in df.iterrows():
            st = status_style[r.status]
            yv = lane_y[r.lane]
            fc = QC if st["facecolor"] is None else st["facecolor"]
            ax.scatter([r.d], [yv], marker=st["marker"], s=70, facecolor=fc, edgecolor=QC, linewidth=1.6, zorder=3)
            edge = r.d.year in (2023, 2024)
            ax.annotate(r.label.replace("\\n", "\n"), (r.d, yv), xytext=(6 if edge else 0, int(r.label_dy)),
                        textcoords="offset points", ha="right" if edge else "center",
                        va="bottom" if r.label_dy > 0 else "top", fontsize=7.4, color=INK["text"])
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color=INK["grid"], lw=0.6)
        ax.tick_params(length=0)
    axl.set_xlim(pd.Timestamp("2017-01-01"), pd.Timestamp("2024-09-30"))
    axr.set_xlim(pd.Timestamp("2024-12-01"), pd.Timestamp("2029-03-31"))
    axl.set_yticks(list(lane_y.values()))
    axl.set_yticklabels(lanes, fontsize=9)
    axl.set_ylim(-0.7, 3.75)
    import matplotlib.dates as mdates
    axl.xaxis.set_major_locator(mdates.YearLocator(2))
    axl.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    axr.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    axr.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    for lab in axr.get_xticklabels():
        lab.set_fontsize(8)
    axr.axvline(pd.Timestamp("2026-11-05"), color=INK["muted"], lw=1, ls="--")
    axr.annotate("as of 2026-11-05", (pd.Timestamp("2026-11-05"), 3.62), xytext=(3, 0), textcoords="offset points",
                 fontsize=7.5, color=INK["muted"], va="center")
    axl.set_title("2017–2024: first attempt", fontsize=9.5, color=INK["muted"], loc="left")
    axr.set_title("2025–2028: second attempt (expanded scale)", fontsize=9.5, color=INK["muted"], loc="left")
    axr.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=QC, markeredgecolor=QC, markersize=7, label="shipped / closed"),
                        Line2D([0], [0], marker="s", color="w", markerfacecolor=QC, markeredgecolor=QC, markersize=7, label="deal signed"),
                        Line2D([0], [0], marker="D", color="w", markerfacecolor=QC, markeredgecolor=QC, markersize=7, label="announced"),
                        Line2D([0], [0], marker="D", color="w", markerfacecolor="#FFFFFF", markeredgecolor=QC, markersize=7, label="roadmap target"),
                        Line2D([0], [0], marker="X", color="w", markerfacecolor=QC, markeredgecolor=QC, markersize=8, label="exit")],
               loc="lower right", fontsize=7.6, frameon=False, ncol=5, bbox_to_anchor=(1.0, -0.2))
    _widen(fig, left=0.145, right=0.98, wspace=0.04)
    c.save(fig, [axl, axr], legend=False, top=0.83, bottom=0.17)


@register
def qualcomm_dc_revenue_targets():
    df = load("x15_dc_revenue_benchmarks.csv")
    d = df[df.chart_group == "annual_scale"].copy()
    nv = d[d.entity == "NVIDIA"].value_usd_b.iloc[0]
    q29 = d[(d.entity == "Qualcomm") & (d.period == "FY2029 target")].value_usd_b.iloc[0]
    amd = d[d.entity == "AMD"].value_usd_b.iloc[0]
    c = Chart(
        id="15-qualcomm-dc-revenue-targets",
        title=(f"Qualcomm's ${q29:.0f}B FY2029 datacenter goal is ~{q29 / nv:.0%} of NVIDIA's FY2026 data-center revenue"),
        subtitle="US$ B per year: reported data-center / AI revenue vs Qualcomm's public targets (hatched); public information only",
        alt=(f"Horizontal bar chart: NVIDIA data-center revenue ${nv:.1f}B in FY2026; Broadcom AI semiconductor revenue about $58B in FY2026; "
             f"AMD data-center revenue about ${amd:.1f}B in 2025; Qualcomm's public targets of ${q29:.0f}B of datacenter revenue by FY2029 "
             f"and $5B in FY2027 (hatched). The FY2029 goal equals about {q29 / nv:.0%} of NVIDIA's FY2026 data-center revenue."),
        data=["x15_dc_revenue_benchmarks.csv"], chapters=CH + ["19"],
        source="company filings, calls and Investor Day materials", source_ids=sources_of(d),
        note="Hatched = company target, not reported revenue",
    )
    fig, ax = c.figure(10.5, 4.8)
    d = d.iloc[::-1]
    y = np.arange(len(d))
    bars = ax.barh(y, d.value_usd_b, color=[entity_color(e) for e in d.entity], height=0.6)
    for i, (p, (_, r)) in enumerate(zip(bars.patches, d.iterrows())):
        if "target" in r.basis:
            p.set_hatch("///")
            p.set_alpha(0.75)
        _bar_label(ax, r.value_usd_b, i, f"${r.value_usd_b:.0f}B · {r.period}", fontsize=8.8)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{e} (target)" if "target" in b else e for e, b in zip(d.entity, d.basis)])
    ax.set_xlim(0, 230)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    _widen(fig, left=0.11, right=0.97)
    c.save(fig, ax, xlabel="US$ B per year")


# --------------------------------------------------------------------------------------
# Inference start-ups
# --------------------------------------------------------------------------------------
@register
def startup_valuation_marks():
    df = load("x15_startup_marks.csv")
    df["d"] = pd.to_datetime(df.date.apply(lambda s: s + "-15" if len(s) == 7 else s))
    c = Chart(
        id="15-startup-valuation-marks",
        title="AI-chip start-up marks re-rated 2–5× in 2026; Graphcore's exit came at ~1/5 of its 2020 value",
        subtitle="Disclosed or reported valuation marks per company, US$ B (log scale); lines join marks of the same company",
        alt=("Log-scale timeline of AI-chip start-up valuation marks. Cerebras $8.1B (Sep 2025), ~$23B (Feb 2026) and ~$40B at its May 2026 IPO; "
             "Groq $6.9B (Sep 2025) then a ~$20B NVIDIA licence-and-team deal (Dec 2025); Etched >$5B (Jan 2026) then $10.3B (Jul 2026); "
             "Tenstorrent ~$2.7B (Dec 2024) then $6.2B (Oct 2026); Positron ~$1B (Feb 2026) then $5B (Sep 2026); SambaNova $5B (2021), a ~$1.6B "
             "Intel offer including debt (Dec 2025, stalled) and a reported ~$11B Series F (Jul 2026, conflicting reports); d-Matrix $2B (Nov 2025); "
             "Lightmatter $4.4B (Oct 2024); Graphcore $2.77B (2020) sold to SoftBank for ~$0.6B (2024); Celestial AI acquired by Marvell for $3.25B upfront (Feb 2026)."),
        data=["x15_startup_marks.csv"], chapters=CH + ["02", "11", "13", "19"],
        source="funding announcements, IPO filings and press reports", source_ids=sources_of(df),
        note="Marks are not like-for-like (round, IPO, deal, offer); dotted marker = conflicting report",
    )
    fig, ax = c.figure(11, 6.4)
    marker = {"private round": "o", "IPO": "s", "licence + acquihire": "D", "acquisition": "D",
              "acquisition offer (stalled)": "X"}
    label_dy = {"Cerebras": (7, 6), "Groq": (-9, 8), "Etched": (7, -10), "Tenstorrent": (7, -2), "SambaNova": (7, 10),
                "Positron": (7, -10), "d-Matrix": (-7, 9), "Lightmatter": (7, 8), "Graphcore": (7, -6),
                "Celestial AI": (7, -11)}
    for comp, g in df.groupby("company", sort=False):
        g = g.sort_values("d")
        ax.plot(g.d, g.value_usd_b, color=GRAY, lw=1.6, alpha=0.8, zorder=2)
        for _, r in g.iterrows():
            fc = entity_color(r.acquirer) if isinstance(r.acquirer, str) and r.acquirer else GRAY
            ec = fc
            if r.confidence == "speculative":
                fc = "#FFFFFF"
                ec = GRAY
            ax.scatter([r.d], [r.value_usd_b], marker=marker[r.mark_type], s=58, facecolor=fc, edgecolor=ec,
                       linewidth=1.5, zorder=3, linestyle=":" if r.confidence == "speculative" else "-")
        last = g.iloc[-1]
        txt = f"{comp} ${last.value_usd_b:.3g}B"
        dx, dy = label_dy.get(comp, (7, 0))
        ax.annotate(txt, (last.d, last.value_usd_b), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.5, color=INK["title"], va="center", fontweight="bold", ha="left" if dx > 0 else "right")
    ax.set_yscale("log")
    ax.set_ylim(0.4, 70)
    ax.set_xlim(pd.Timestamp("2020-07-01"), pd.Timestamp("2027-06-30"))
    ax.legend(handles=[Line2D([0], [0], marker="o", color="w", markerfacecolor=GRAY, markersize=7, label="private round"),
                       Line2D([0], [0], marker="s", color="w", markerfacecolor=GRAY, markersize=7, label="IPO"),
                       Line2D([0], [0], marker="X", color="w", markerfacecolor=GRAY, markersize=8, label="offer (not completed)"),
                       Line2D([0], [0], marker="D", color="w", markerfacecolor=NV, markersize=7, label="exit to NVIDIA"),
                       Line2D([0], [0], marker="D", color="w", markerfacecolor=entity_color("marvell"), markersize=7, label="exit to Marvell"),
                       Line2D([0], [0], marker="D", color="w", markerfacecolor=LIGHT, markersize=7, label="exit to SoftBank")],
              loc="upper left", fontsize=8, ncol=2)
    c.save(fig, ax, ylabel="Valuation mark, US$ B", logy=True, xlabel="Date of mark", legend=False)


# --------------------------------------------------------------------------------------
# China
# --------------------------------------------------------------------------------------
@register
def ascend_vs_nvidia_china_parts():
    import matplotlib.pyplot as plt
    ca = load("competitor_accelerators.csv")
    cs = load("cs6_china_parts.csv")
    gp = load("gpu_product_specs.csv")
    rows = []
    for prod in ["H20", "H200"]:
        r = cs[cs["product"] == prod].iloc[0]
        rows.append(dict(name=f"NVIDIA {prod}", who="NVIDIA", tflops=r.dense_tflops_used, basis="FP8", bw=r.memory_bw_tbs,
                         gb=r.memory_gb, status=("licence req. Apr 2025" if prod == "H20" else "licensed, 25% levy"), future=False))
    for prod, yr in [("Ascend 910B", 2023), ("Ascend 910C", 2025), ("Ascend 950PR", 2026), ("Ascend 950DT", 2026),
                     ("Ascend 960", 2027), ("Ascend 970", 2028)]:
        r = ca[ca["product"] == prod].iloc[0]
        fp8 = r.fp8_tflops_dense
        has8 = pd.notna(fp8)
        rows.append(dict(name=f"Huawei {prod}", who="Huawei", tflops=fp8 if has8 else r.bf16_tflops_dense,
                         basis="FP8" if has8 else "FP16", bw=r.memory_bandwidth_tbs, gb=r.memory_capacity_gb,
                         status=str(yr), future=prod in ("Ascend 950DT", "Ascend 960", "Ascend 970")))
    rub = gp[gp["product"].str.startswith("Rubin (")].iloc[0]
    rows.append(dict(name="NVIDIA Rubin", who="NVIDIA", tflops=rub.fp8_tflops_dense, basis="FP8", bw=rub.memory_bandwidth_tbs,
                     gb=rub.memory_capacity_gb, status="2026, not licensed", future=False))
    d = pd.DataFrame(rows)
    get = lambda nm, col: float(d[d.name == nm][col].iloc[0])  # noqa: E731
    a950 = get("Huawei Ascend 950PR", "tflops")
    h20 = get("NVIDIA H20", "tflops")
    h200 = get("NVIDIA H200", "tflops")
    a970 = get("Huawei Ascend 970", "tflops")
    rub_f = get("NVIDIA Rubin", "tflops")
    c = Chart(
        id="15-ascend-vs-nvidia-china-parts",
        title=(f"Ascend 950: ~{a950 / h20:.1f}× an H20's FP8 compute, ~half an H200's; "
               f"Ascend 970 (2028) trails Rubin ~{rub_f / a970:.1f}×"),
        subtitle="Per chip: dense TFLOPS (FP8; FP16 where no FP8, log scale), memory bandwidth (TB/s) and capacity (GB); hatched = not yet shipping",
        alt=("Three-panel bar chart comparing Huawei Ascend chips with the NVIDIA parts China can or could buy. Dense compute: H20 "
             f"{h20:.0f} TFLOPS FP8, H200 {h200:.0f}, Ascend 910B {get('Huawei Ascend 910B', 'tflops'):.0f} FP16, 910C {get('Huawei Ascend 910C', 'tflops'):.0f} FP16, "
             f"950PR and 950DT {a950:.0f} FP8, 960 {get('Huawei Ascend 960', 'tflops'):.0f}, 970 {a970:.0f} (2028) and Rubin {rub_f:.0f}. Memory bandwidth: "
             f"H20 {get('NVIDIA H20', 'bw'):.1f} TB/s, H200 {get('NVIDIA H200', 'bw'):.1f}, 910C {get('Huawei Ascend 910C', 'bw'):.1f}, 950PR {get('Huawei Ascend 950PR', 'bw'):.1f}, "
             f"950DT {get('Huawei Ascend 950DT', 'bw'):.1f}, 960 {get('Huawei Ascend 960', 'bw'):.1f}, 970 {get('Huawei Ascend 970', 'bw'):.1f}, Rubin {get('NVIDIA Rubin', 'bw'):.1f}. "
             f"Capacity: H20 96 GB, H200 141, 950PR 128, 950DT 144, 960 and 970 288, Rubin 288. Huawei's roadmap closes the capacity gap by 2027 "
             "but not the compute or bandwidth gap."),
        data=["competitor_accelerators.csv", "cs6_china_parts.csv", "gpu_product_specs.csv"], chapters=CH + ["CS6", "02", "03"],
        source="Huawei Connect 2025 roadmap, NVIDIA specs, SemiAnalysis H20 leak",
        source_ids=["S163", "S164", "S26003", "S32002", "S90006", "S90042"],
        note="Hatched = announced / roadmap; Ascend dense-vs-sparse basis not always stated by Huawei",
    )
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 6.2), sharey=True, gridspec_kw=dict(width_ratios=[1.25, 1, 1]))
    d = d.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(d))
    cols = [NV if w == "NVIDIA" else HW for w in d.who]
    for ax, col, xl, fmt in [(axs[0], "tflops", "Dense TFLOPS (log scale)", "{:,.0f}"),
                             (axs[1], "bw", "Memory bandwidth, TB/s", "{:.1f}"),
                             (axs[2], "gb", "Memory capacity, GB", "{:,.0f}")]:
        bars = ax.barh(y, d[col], color=cols, height=0.62)
        for i, (p, fut) in enumerate(zip(bars.patches, d.future)):
            if fut:
                p.set_hatch("///")
                p.set_alpha(0.72)
            v = d[col].iloc[i]
            suffix = f" {d.basis.iloc[i]}" if col == "tflops" and d.basis.iloc[i] == "FP16" else ""
            _bar_label(ax, v, i, fmt.format(v) + suffix, fontsize=7.8)
        ax.set_xlabel(xl, fontsize=9)
        ax.grid(axis="x", color=INK["grid"])
        ax.grid(axis="y", visible=False)
        ax.tick_params(length=0)
    axs[0].set_xscale("log")
    axs[0].set_xlim(100, 90000)
    axs[1].set_xlim(0, 25)
    axs[2].set_xlim(0, 380)
    axs[0].set_yticks(y)
    axs[0].set_yticklabels([f"{nm}\n({st})" for nm, st in zip(d.name, d.status)], fontsize=8)
    axs[0].legend(handles=[Patch(facecolor=NV, label="NVIDIA"), Patch(facecolor=HW, label="Huawei")], loc="upper right", fontsize=8)
    _widen(fig, left=0.15, right=0.98, wspace=0.12)
    c.save(fig, list(axs), legend=False, logx=False, top=0.84, bottom=0.14)


@register
def china_ai_chip_vendor_revenue():
    import matplotlib.pyplot as plt
    df = load("x15_china_vendors.csv")
    hw = df[df.company == "Huawei"].set_index("period").value
    h1 = df[(df.period == "H1 2026")].sort_values("value")
    tot = h1.value.sum()
    c = Chart(
        id="15-china-ai-chip-vendor-revenue",
        title=(f"Huawei expects ~${hw['CY2026E']:.0f}B of AI-chip sales in 2026; China's four listed challengers booked "
               f"~{tot:.0f}B yuan in H1"),
        subtitle="Left: Huawei AI-chip revenue, US$ B (FT report). Right: H1 2026 revenue of listed vendors, CNY B, with y/y growth",
        alt=(f"Two-panel bar chart. Left: Huawei's AI-chip revenue was about ${hw['CY2025']:.1f}B in 2025 and the company expects about "
             f"${hw['CY2026E']:.0f}B in 2026 (+60%, hatched, as reported by the FT). Right: first-half 2026 revenue of China's listed AI-chip makers: "
             "Hygon 9.1B yuan (+67%, CPUs and DCU accelerators combined), Cambricon 6.0B yuan (+108%), Moore Threads 1.7B yuan (+147%) "
             f"and MetaX about 1.3B yuan (reports conflict; another gives 0.95B), about {tot:.0f}B yuan in total."),
        data=["x15_china_vendors.csv"], chapters=CH + ["CS6", "13"],
        source="company results and press reports", source_ids=sources_of(df),
        note="Hatched = expectation or conflicting report; Hygon includes CPUs",
    )
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5.4), gridspec_kw=dict(width_ratios=[1, 2.1]))
    xs = [0, 1]
    vals = [hw["CY2025"], hw["CY2026E"]]
    bars = a1.bar(xs, vals, color=HW, width=0.55)
    bars.patches[1].set_hatch("///")
    bars.patches[1].set_alpha(0.75)
    for x, v, lab in zip(xs, vals, ["2025", "2026E (+60%)"]):
        a1.annotate(f"${v:.1f}B\n{lab}", (x, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=8.5)
    a1.set_xticks(xs)
    a1.set_xticklabels(["2025", "2026E"])
    a1.set_ylim(0, 15)
    a1.set_ylabel("US$ B")
    a1.set_title("Huawei Ascend (not listed)", fontsize=9.5, color=HW, loc="left", fontweight="bold")
    y = np.arange(len(h1))
    bars2 = a2.barh(y, h1.value, color=LIGHT, height=0.6, edgecolor=INK["base"], linewidth=0.6)
    for i, (p, (_, r)) in enumerate(zip(bars2.patches, h1.iterrows())):
        if r.confidence == "speculative":
            p.set_hatch("///")
        g = f", +{r.yoy_growth_pct:.0f}% y/y" if pd.notna(r.yoy_growth_pct) else " (reports conflict)"
        _bar_label(a2, r.value, i, f"{r.value:.1f}B yuan{g}", fontsize=8.5)
    a2.set_yticks(y)
    a2.set_yticklabels([f"{cmp}" + (" (CPU + DCU)" if cmp == "Hygon" else "") for cmp in h1.company])
    a2.set_xlim(0, 13.5)
    a2.set_xlabel("CNY B, H1 2026")
    a2.grid(axis="x", color=INK["grid"])
    a2.grid(axis="y", visible=False)
    a2.set_title("Listed vendors, H1 2026", fontsize=9.5, color=INK["text"], loc="left", fontweight="bold")
    _widen(fig, left=0.07, right=0.97, wspace=0.42)
    c.save(fig, [a1, a2], legend=False)


@register
def china_advanced_node_capacity():
    df = load("x15_smic_capacity.csv")
    c = Chart(
        id="15-china-advanced-node-capacity",
        title="2027 estimates of China's 7 nm-class capacity: ~18k–100k wafers a month; Ascend needs ≤20k",
        subtitle="Thousand wafers per month: SMIC advanced-node capacity or output by estimator and year (targets hollow)",
        alt=("Dot-and-line chart of estimates for China's 7 nm-class wafer capacity. SemiAnalysis (conservative): SMIC 7 nm-and-below capacity "
             "about 45k wafers a month at end-2025, 60k in 2026 and 80k in 2027, and Huawei's Ascend needing at most about 20k. Nikkei via "
             "TrendForce: output of fewer than 20k wafers a month in early 2026 with a government goal of about 100k within one to two years "
             "(hollow). Morgan Stanley: about 18k AI-chip wafers a month at best by 2027 because of low yields. Fab capacity is not the only "
             "constraint: HBM supply binds first."),
        data=["x15_smic_capacity.csv"], chapters=CH + ["CS6", "03"],
        source="SemiAnalysis, Nikkei via TrendForce, Morgan Stanley via Wccftech", source_ids=sources_of(df),
        note="Estimates use different scopes (total capacity, output, AI-chip wafers); not additive",
    )
    fig, ax = c.figure(11.5, 5.6)
    sa = df[(df.estimator == "SemiAnalysis") & (df.metric == "capacity")]
    ax.plot(sa.year, sa.value_k_wpm, color="#256ABF", marker="o", lw=2, label="SemiAnalysis: SMIC 7 nm-class capacity")
    for _, r in sa.iterrows():
        ax.annotate(f"{r.value_k_wpm:.0f}k", (r.year, r.value_k_wpm), xytext=(0, 8), textcoords="offset points",
                    ha="center", fontsize=8.5, color="#256ABF")
    req = df[df.metric == "ascend_requirement"].iloc[0]
    ax.axhline(req.value_k_wpm, color=HW, lw=1.4, ls="--")
    ax.annotate("SemiAnalysis: Ascend needs at most ~20k", (2025.02, req.value_k_wpm), xytext=(0, 4),
                textcoords="offset points", fontsize=8.5, color=HW)
    nk = df[df.estimator.str.startswith("Nikkei")]
    o = nk[nk.metric == "output"].iloc[0]
    t = nk[nk.metric == "target"].iloc[0]
    ax.scatter([o.year], [o.value_k_wpm], marker="s", s=60, color="#104281", zorder=4, label="Nikkei: actual output (< value)")
    ax.scatter([t.year], [t.value_k_wpm], marker="s", s=70, facecolor="#FFFFFF", edgecolor="#104281", linewidth=1.8, zorder=4,
               label="Nikkei: government goal")
    ax.plot([o.year, t.year], [o.value_k_wpm, t.value_k_wpm], color="#104281", lw=1.2, ls=":")
    ax.annotate("< 20k output\n(early 2026)", (o.year, o.value_k_wpm), xytext=(10, 8), textcoords="offset points",
                fontsize=8.5, color="#104281")
    ax.annotate("~100k goal\n(within 1-2 yrs)", (t.year, t.value_k_wpm), xytext=(-10, -4), textcoords="offset points",
                fontsize=8.5, color="#104281", ha="right")
    ms = df[df.estimator == "Morgan Stanley"].iloc[0]
    ax.scatter([ms.year], [ms.value_k_wpm], marker="v", s=70, color=INK["text"], zorder=4, label="Morgan Stanley: AI-chip wafers at best")
    ax.annotate("~18k AI-chip\nwafers (MS)", (ms.year, ms.value_k_wpm), xytext=(8, -2), textcoords="offset points",
                fontsize=8.5, color=INK["text"], va="top")
    ax.set_xticks([2025, 2026, 2027])
    ax.set_xticklabels(["2025", "2026", "2027"])
    ax.set_xlim(2024.85, 2027.35)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper left", fontsize=8.5)
    c.save(fig, ax, ylabel="Thousand wafers per month", xlabel="Year", legend=False)
