"""Market-share charts: AI accelerator revenue share, merchant vs custom ASIC, custom-ASIC partner revenue,
AI back-end network InfiniBand vs Ethernet (chapters 15, 06, 13). Owner: Phase-1 agent A6.

Data: data/market_share.csv. Shares are repo calculations from vendor-reported revenue; 2026E rows and
third-party estimates are hatched and labelled.
"""
from __future__ import annotations

import numpy as np

from style import Chart, INK, NV, entity_color, hatch_future, load, register, sources_of

DATA = "market_share.csv"


def _ids(*frames):
    out = []
    for f in frames:
        for sid in sources_of(f):
            if sid not in out:
                out.append(sid)
    return out


def _margins(fig, **over):
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


@register
def ai_accelerator_market_share():
    df = load(DATA)
    d = df[df.segment == "ai_accelerator_revenue_share"].copy()
    rev = df[(df.segment == "ai_datacenter_vendor_revenue") & df.metric.isin(
        ["data_center_revenue", "data_center_gpu_revenue", "ai_semiconductor_revenue", "ai_revenue", "other_accelerator_revenue"])]
    years = ["2023", "2024", "2025", "2026E"]
    ents = ["NVIDIA", "AMD", "Custom ASIC (Broadcom + Marvell)", "Other (Intel Gaudi, startups)"]
    colors = [NV, entity_color("AMD"), entity_color("Broadcom"), entity_color("other")]
    tot = {y: rev[rev.year == y].value.sum() for y in years}
    nv23 = d[(d.year == "2023") & (d.entity == "NVIDIA")].value.iloc[0]
    nv25 = d[(d.year == "2025") & (d.entity == "NVIDIA")].value.iloc[0]
    cu25 = d[(d.year == "2025") & (d.entity.str.startswith("Custom"))].value.iloc[0]
    c = Chart(
        id="15-ai-accelerator-market-share",
        title=(f"NVIDIA kept ~{nv25:.0f}% of AI silicon revenue in 2025 while the pool grew {tot['2025'] / tot['2023']:.1f}x from 2023"),
        subtitle="Share of vendor-reported AI data-center revenue (NVIDIA DC, AMD Instinct, Broadcom AI, Marvell AI), %; labels = pool US$ B",
        alt=(f"Stacked 100% bars of AI data-center silicon revenue share by vendor. NVIDIA {nv23:.0f}% in 2023 and {nv25:.0f}% in 2025; "
             f"custom ASIC partners (Broadcom and Marvell) about {cu25:.0f}% in 2025; AMD 1-4%. The pool grew from about "
             f"${tot['2023']:.0f}B in 2023 to ${tot['2025']:.0f}B in 2025 and an estimated ${tot['2026E']:.0f}B in 2026 (hatched)."),
        data=[DATA], chapters=["15", "00", "13", "18"],
        source="vendor filings; repo calculation", source_ids=_ids(d, rev),
        note="Est.; hatched = 2026E scenario",
    )
    fig, ax = c.figure(width=11, height=6.0)
    x = np.arange(len(years))
    bottom = np.zeros(len(years))
    for ent, col in zip(ents, colors):
        vals = np.array([d[(d.year == y) & (d.entity == ent)].value.iloc[0] for y in years])
        bars = ax.bar(x, vals, bottom=bottom, color=col, width=0.6, edgecolor="#FFFFFF", linewidth=0.8, label=ent)
        hatch_future(bars, [y.endswith("E") for y in years])
        for xi, v, b in zip(x, vals, bottom):
            if v >= 2.5:
                ax.text(xi, b + v / 2, f"{v:.0f}%", ha="center", va="center", fontsize=9,
                        color="#FFFFFF" if ent != ents[-1] else INK["title"], fontweight="bold")
        bottom += vals
    for xi, y in zip(x, years):
        ax.text(xi, 101.5, f"${tot[y]:.0f}B", ha="center", va="bottom", fontsize=9, color=INK["text"])
    ax.set_xticks(x)
    ax.set_xticklabels(["2023", "2024", "2025", "2026E\n(scenario)"])
    ax.set_ylim(0, 110)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.11), ncol=4, fontsize=8.8, frameon=False)
    c.save(fig, ax, ylabel="Share of AI data-center silicon revenue (%)", legend=False, bottom=0.2)


@register
def merchant_vs_custom_slope():
    df = load(DATA)
    d = df[df.segment == "merchant_vs_custom"].copy()
    rev = d[d.metric == "share_of_vendor_revenue"]
    units = d[d.metric == "share_of_ai_server_shipments"]
    m23 = rev[(rev.year == "2023") & (rev.entity == "Merchant GPU/accelerator")].value.iloc[0]
    m26 = rev[(rev.year == "2026E") & (rev.entity == "Merchant GPU/accelerator")].value.iloc[0]
    c23 = rev[(rev.year == "2023") & (rev.entity == "Custom ASIC")].value.iloc[0]
    c26 = rev[(rev.year == "2026E") & (rev.entity == "Custom ASIC")].value.iloc[0]
    cu = units[units.entity == "Custom ASIC"].value.iloc[0]
    c = Chart(
        id="15-merchant-vs-custom-asic-share",
        title=(f"Custom ASICs reach only ~{c26:.0f}% of AI silicon revenue by 2026E, but perhaps ~{cu:.0f}% of units"),
        subtitle="Merchant (NVIDIA, AMD, Intel) vs custom ASIC (Broadcom, Marvell) share, %, 2023 vs 2026E; revenue basis vs unit basis",
        alt=(f"Slope chart: merchant GPUs and accelerators fall from {m23:.0f}% to about {m26:.0f}% of AI data-center silicon revenue "
             f"between 2023 and 2026E while custom ASICs rise from {c23:.0f}% to about {c26:.0f}%. On a unit basis, TrendForce-type "
             f"estimates put ASIC-based servers near {cu:.0f}% of 2026 AI server shipments, because custom chips are far cheaper per unit."),
        data=[DATA], chapters=["15", "13", "19"],
        source="vendor filings; TrendForce (as recalled)", source_ids=sources_of(d),
        note="2026E = Est.",
    )
    fig, ax = c.figure(width=11, height=6.0)
    for ent, col in [("Merchant GPU/accelerator", NV), ("Custom ASIC", entity_color("Broadcom"))]:
        v0 = rev[(rev.year == "2023") & (rev.entity == ent)].value.iloc[0]
        v1 = rev[(rev.year == "2026E") & (rev.entity == ent)].value.iloc[0]
        ax.plot([0, 1], [v0, v1], color=col, lw=2.4, marker="o", markersize=9)
        ax.annotate(f"{v0:.1f}%", (0, v0), xytext=(-10, 0), textcoords="offset points", ha="right", va="center",
                    fontsize=10, color=col, fontweight="bold")
        ax.annotate(f"{v1:.1f}% (Est.)  {ent}, revenue", (1, v1), xytext=(10, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=10, color=col, fontweight="bold")
    for ent, col in [("Merchant GPU/accelerator", NV), ("Custom ASIC", entity_color("Broadcom"))]:
        vu = units[units.entity == ent].value.iloc[0]
        ax.scatter([1], [vu], s=120, facecolor="#FFFFFF", edgecolor=col, linewidth=2, hatch="///", zorder=4)
        ax.annotate(f"{vu:.0f}% (Est.)  {ent}, AI server units", (1, vu), xytext=(10, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=9.5, color=col, style="italic")
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["2023", "2026E"])
    ax.set_xlim(-0.35, 2.15)
    ax.set_ylim(0, 100)
    ax.spines["bottom"].set_visible(True)
    _margins(fig, left=0.09, right=0.97)
    c.save(fig, ax, ylabel="Share (%)", legend=False)


@register
def ib_vs_ethernet():
    df = load(DATA)
    d = df[(df.segment == "ai_backend_network_switch_share") & (df.metric == "share_of_ai_backend_switch_spend")].copy()
    sx = df[(df.segment == "ai_backend_network_switch_share") & (df.metric == "annualized_revenue_run_rate")]
    years = ["2023", "2024", "2025", "2027E"]
    ib = [d[(d.year == y) & (d.entity == "InfiniBand")].value.iloc[0] for y in years]
    eth = [d[(d.year == y) & (d.entity == "Ethernet")].value.iloc[0] for y in years]
    c = Chart(
        id="06-ib-vs-ethernet-ai-backend-share",
        title="Ethernet likely overtook InfiniBand in AI back-end networks in 2025 (directional Est.)",
        subtitle="Share of AI back-end (GPU-to-GPU scale-out) switch spending, %; directional estimates — every bar is an estimate",
        alt=(f"Stacked 100% bars of AI back-end network switch spending: InfiniBand about {ib[0]:.0f}% in 2023 falling to about "
             f"{ib[2]:.0f}% in 2025 and {ib[3]:.0f}% in 2027E, with Ethernet rising from {eth[0]:.0f}% to {eth[3]:.0f}%. Values are "
             "directional estimates consistent with Dell'Oro commentary, not verified figures. NVIDIA itself drives much of the "
             f"shift: Spectrum-X Ethernet passed a ${sx.value.iloc[0]:.0f}B annualized run-rate in 2025."),
        data=[DATA], chapters=["06", "15"],
        source="Dell'Oro commentary (directional); NVIDIA", source_ids=_ids(d, sx),
        note="Hatched = speculative estimate",
    )
    fig, ax = c.figure(width=11, height=5.8)
    x = np.arange(len(years))
    b1 = ax.bar(x, ib, color=NV, width=0.6, edgecolor="#FFFFFF", label="InfiniBand (NVIDIA Quantum)")
    b2 = ax.bar(x, eth, bottom=ib, color=entity_color("Broadcom"), width=0.6, edgecolor="#FFFFFF",
                label="Ethernet (Spectrum-X, Broadcom/Arista/Cisco, white box)")
    hatch_future(b1, [True] * len(years))
    hatch_future(b2, [True] * len(years))
    for xi, a, b in zip(x, ib, eth):
        ax.text(xi, a / 2, f"~{a:.0f}%", ha="center", va="center", color="#FFFFFF", fontsize=10, fontweight="bold")
        ax.text(xi, a + b / 2, f"~{b:.0f}%", ha="center", va="center", color="#FFFFFF", fontsize=10, fontweight="bold")
    ax.axhline(50, color=INK["text"], lw=0.8, ls=":")
    ax.set_xticks(x)
    ax.set_xticklabels(["2023", "2024", "2025", "2027E"])
    ax.set_ylim(0, 100)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.09), ncol=2, fontsize=9, frameon=False)
    c.save(fig, ax, ylabel="Share of AI back-end switch spend (%)", legend=False, bottom=0.18)


@register
def custom_asic_revenue_trend():
    df = load(DATA)
    q = df[(df.segment == "custom_asic_partner_revenue") & (df.entity == "Broadcom")].copy().sort_values("year")
    a = df[(df.segment == "ai_datacenter_vendor_revenue") & df.entity.isin(["Broadcom", "Marvell"]) &
           df.metric.isin(["ai_semiconductor_revenue", "ai_revenue"])].copy()
    first, last_act = q.iloc[0], q[q.year == "2025-Q4"].iloc[0]
    guide = q[q.year == "2026-Q1"].iloc[0]
    b25 = a[(a.entity == "Broadcom") & (a.year == "2025")].value.iloc[0]
    m25 = a[(a.entity == "Marvell") & (a.year == "2025")].value.iloc[0]
    c = Chart(
        id="15-custom-asic-revenue-trend",
        title=(f"Broadcom's AI revenue rose {last_act.value / first.value:.1f}x in two years to ${last_act.value:.1f}B a quarter; "
               f"Marvell's is ~1/{round(b25 / m25)} the size"),
        subtitle="Left: Broadcom AI semiconductor revenue by fiscal quarter (US$ B). Right: annual AI revenue, Broadcom vs Marvell (US$ B)",
        alt=(f"Two panels. Left: Broadcom quarterly AI semiconductor revenue climbs from ${first.value:.1f}B in fiscal Q1 2024 to "
             f"${last_act.value:.1f}B in fiscal Q4 2025, with Q1 2026 guidance of ${guide.value:.1f}B hatched. Right: annual AI revenue, "
             "Broadcom about $3.8B (2023), $12.2B (2024), $20.2B (2025), ~$45B (2026E scenario) vs Marvell $0.55B, $1.5B, $2.5B, "
             "~$3.5B (2026E). Broadcom's figure includes AI Ethernet networking as well as custom XPUs such as Google's TPU."),
        data=[DATA], chapters=["15", "13", "19"],
        source="Broadcom, Marvell earnings releases", source_ids=_ids(q, a),
        note="Hatched = guidance or Est.",
    )
    fig, (ax1, ax2) = c.figure_grid(1, 2, width=12, height=5.8, gridspec_kw=dict(width_ratios=[1.35, 1]))
    labels = [f"Q{y[-1]}\nFY{y[2:4]}" for y in q.year]
    bars = ax1.bar(np.arange(len(q)), q.value, color=entity_color("Broadcom"), width=0.65)
    hatch_future(bars, [y == "2026-Q1" for y in q.year])
    for b, v in zip(bars, q.value):
        ax1.text(b.get_x() + b.get_width() / 2, v + 0.12, f"{v:.1f}", ha="center", va="bottom", fontsize=8.5, color=INK["text"])
    ax1.set_xticks(np.arange(len(q)))
    ax1.set_xticklabels(labels, fontsize=8.5)
    ax1.set_ylabel("Broadcom AI revenue per quarter (US$ B)")
    ax1.set_ylim(0, q.value.max() * 1.15)
    ax1.text(len(q) - 1, guide.value * 0.5, "guide", ha="center", rotation=90, fontsize=8.5, color=INK["title"])
    years = ["2023", "2024", "2025", "2026E"]
    w = 0.38
    for i, (ent, col) in enumerate([("Broadcom", entity_color("Broadcom")), ("Marvell", entity_color("Marvell"))]):
        vals = [a[(a.entity == ent) & (a.year == y)].value.iloc[0] for y in years]
        bb = ax2.bar(np.arange(4) + (i - 0.5) * w, vals, width=w, color=col, label=ent)
        hatch_future(bb, [y.endswith("E") for y in years])
        for b, v in zip(bb, vals):
            ax2.text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v:.1f}" if v < 10 else f"{v:.0f}", ha="center", va="bottom",
                     fontsize=8.5, color=INK["text"])
    ax2.set_xticks(np.arange(4))
    ax2.set_xticklabels(["2023", "2024", "2025", "2026E"])
    ax2.set_ylabel("Annual AI revenue (US$ B)")
    ax2.legend(loc="upper left", fontsize=9, frameon=False)
    _margins(fig, left=0.07, right=0.98, wspace=0.25)
    c.save(fig, [ax1, ax2], legend=False, bottom=0.15)
