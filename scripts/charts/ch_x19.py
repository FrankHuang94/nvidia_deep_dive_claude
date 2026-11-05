"""Chapter 19 (implications for Qualcomm; public information only).

Owner: chapter-19 agent. Data: data/x19_*.csv (this chapter) plus competitor_matrix.csv (read-only).
Chart ids are prefixed "19-". Every Qualcomm data point comes from public announcements, filings or press
coverage; scores are the repo's judgement and are labelled as such.
"""
from __future__ import annotations

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from style import (Chart, INK, NV, SEQ_BLUE, VERDICT_COLORS, entity_color, load, register, sources_of)

CH = ["19"]
QC = entity_color("qualcomm")
AMD = entity_color("amd")
GRAY = entity_color("startups")
LIGHT = entity_color("other")


def _widen(fig, **over):
    """Chart.save() hard-codes left/right margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _nl(s) -> str:
    return str(s).replace("\\n", "\n")


# --------------------------------------------------------------------------------------
# 1. Layer map: relationship x layer, shaded by evidence stage
# --------------------------------------------------------------------------------------
REL_COLS = ["partner", "compete", "complement", "absent"]
REL_TITLE = {"partner": "Partner\n(with NVIDIA)", "compete": "Compete\n(for NVIDIA's wallet)",
             "complement": "Complement\n(neutral supplier)", "absent": "Absent\n(no public effort)"}
STAGE_FILL = {1: SEQ_BLUE[0], 2: SEQ_BLUE[2], 3: SEQ_BLUE[5]}
STAGE_TAG = {0: "none", 1: "announced", 2: "signed", 3: "ships"}
ABSENT_FILL = "#ECEBE6"


@register
def layer_relationship_heatmap():
    df = load("x19_layer_map.csv", dtype={"layer_id": str})
    cm = load("competitor_matrix.csv")
    cm = cm[(cm["competitor"] == "Qualcomm") & (cm["dimension_type"] == "layer")].copy()
    cm["layer_id"] = cm["dimension"].str[:2]
    layers = df.drop_duplicates("layer_id")[["layer_id", "layer"]].values.tolist()
    prim = df[df["primary"] == "yes"].set_index("layer_id")["relationship"]
    counts = prim.value_counts()
    shipping_layers = sorted(df[df["stage"] == 3]["layer_id"].unique())
    title = (f"Qualcomm competes with NVIDIA in {counts.get('compete', 0)} of 12 layers, partners in "
             f"{counts.get('partner', 0)}, complements {counts.get('complement', 0)} and is absent from "
             f"{counts.get('absent', 0)}; it ships in {len(shipping_layers)}")
    alt = (f"Heatmap of Qualcomm's public datacenter efforts against NVIDIA's 12 stack layers, by relationship "
           f"(partner, compete, complement, absent) and evidence stage. Primary roles: compete in "
           f"{counts.get('compete', 0)} layers (accelerators, memory approach, scale-up, racks, inference software, "
           f"ecosystem), partner in 1 (CPU via NVLink Fusion), complement in 2 (Alphawave connectivity IP and "
           f"1.6T optics; Mojo, which also runs on NVIDIA GPUs) and absent from 3 (DPUs and NICs, domain "
           f"libraries, cloud capacity). Only {len(shipping_layers)} layers have a shipping product (Cloud AI 100, "
           f"LPDDR cards, Cloud AI SDK and Mojo, MAX and vLLM); AI200 racks, C1000 and AI300 are announced, signed "
           f"or in initial deployment. A fifth column repeats chapter 15's layer scores: {cm['score_0_5'].mean():.1f} "
           f"of 5 on average, behind in {(cm['verdict_vs_nvidia'] == 'behind').sum()} layers and different in "
           f"{(cm['verdict_vs_nvidia'] == 'different').sum()}.")
    c = Chart(
        id="19-layer-relationship-heatmap",
        title=title,
        subtitle="Qualcomm public efforts by NVIDIA stack layer; shade = evidence stage; bold outline = primary role; "
                 "last column = chapter 15 score (0-5)",
        alt=alt,
        data=["x19_layer_map.csv", "competitor_matrix.csv"],
        chapters=CH + ["15"],
        source="Qualcomm, NVIDIA and press announcements; scores are repo judgement",
        source_ids=sources_of(df) + [s for s in sources_of(cm) if s not in sources_of(df)],
        note="Public information only. Stage: 1 announced/roadmap, 2 signed/acquired/initial deployment, 3 shipping.",
    )
    fig, ax = c.figure(width=13.0, height=8.8)
    n = len(layers)
    ncol = len(REL_COLS) + 1
    for i, (lid, lname) in enumerate(layers):
        y = n - 1 - i
        for j, rel in enumerate(REL_COLS):
            sub = df[(df["layer_id"] == lid) & (df["relationship"] == rel)]
            if sub.empty:
                ax.add_patch(Rectangle((j, y), 1, 1, fc="#FFFFFF", ec=INK["grid"], lw=0.8))
                continue
            stage = int(sub["stage"].max())
            fill = ABSENT_FILL if rel == "absent" else STAGE_FILL.get(stage, ABSENT_FILL)
            is_prim = (sub["primary"] == "yes").any()
            ax.add_patch(Rectangle((j, y), 1, 1, fc=fill, ec=INK["title"] if is_prim else INK["grid"],
                                   lw=2.2 if is_prim else 0.8, zorder=2 if is_prim else 1))
            sep = " " if len(sub) > 1 else "\n"
            lines = [f"{_nl(r.cell_label)}" + ("" if rel == "absent" else f"{sep}({STAGE_TAG[int(r.stage)]})")
                     for r in sub.sort_values("stage", ascending=False).itertuples()]
            dark = (rel != "absent" and stage == 3)
            ax.text(j + 0.5, y + 0.5, "\n".join(lines), ha="center", va="center", fontsize=7.8,
                    color="#FFFFFF" if dark else INK["title"], zorder=3,
                    fontweight="bold" if is_prim else "normal")
        # chapter 15 score column
        row = cm[cm["layer_id"] == lid]
        j = len(REL_COLS)
        if not row.empty:
            verdict = row["verdict_vs_nvidia"].iloc[0]
            score = int(row["score_0_5"].iloc[0])
            ax.add_patch(Rectangle((j + 0.08, y), 0.84, 1, fc=VERDICT_COLORS.get(verdict, "#FFFFFF"),
                                   ec=INK["grid"], lw=0.8))
            ax.text(j + 0.5, y + 0.5, f"{score} / 5\n{verdict}", ha="center", va="center", fontsize=8,
                    color=INK["title"])
    ax.set_xlim(0, ncol)
    ax.set_ylim(0, n)
    ax.set_yticks([n - 1 - i + 0.5 for i in range(n)])
    ax.set_yticklabels([f"{lid} {lname}" for lid, lname in layers], fontsize=9)
    ax.set_xticks([j + 0.5 for j in range(ncol)])
    ax.set_xticklabels([REL_TITLE[r] for r in REL_COLS] + ["Capability vs\nNVIDIA (ch. 15)"], fontsize=9)
    ax.xaxis.tick_top()
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(fc=STAGE_FILL[1], ec=INK["grid"], label="announced / roadmap"),
               Patch(fc=STAGE_FILL[2], ec=INK["grid"], label="signed / acquired / initial deployment"),
               Patch(fc=STAGE_FILL[3], ec=INK["grid"], label="shipping"),
               Patch(fc=ABSENT_FILL, ec=INK["grid"], label="absent"),
               Patch(fc="#FFFFFF", ec=INK["title"], lw=2.2, label="primary relationship")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.45, -0.015), ncol=5, fontsize=8.2,
              frameon=False)
    _widen(fig, left=0.23, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.10)


# --------------------------------------------------------------------------------------
# 2. Where a challenger can win: attractiveness vs NVIDIA defensibility
# --------------------------------------------------------------------------------------
GROUP_STYLE = {
    "efficiency": ("o", QC, "Inference efficiency"),
    "deployment": ("s", QC, "Deployment constraint"),
    "workload": ("D", QC, "Specific workload"),
    "edge": ("^", QC, "Edge-to-cloud"),
    "reference": ("X", GRAY, "Reference (no Qualcomm product)"),
}
LABEL_OFFSET = {
    "MoE tokens per MW": (-8, -12, "right"),
    "LPDDR capacity per $": (9, 6, "left"),
    "Fast decode tier": (9, 4, "left"),
    "Low-power sites": (9, -6, "left"),
    "Agentic head-node CPU": (9, 4, "left"),
    "Recommendation": (-9, 6, "right"),
    "Small/medium models": (9, -8, "left"),
    "Sovereign AI": (9, 4, "left"),
    "Edge-to-cloud": (-9, -8, "right"),
    "Hyperscaler custom silicon": (-9, 10, "right"),
    "Frontier training": (9, -2, "left"),
}


@register
def challenger_win_matrix():
    df = load("x19_win_matrix.csv")
    open_ = df[(df["attractiveness_1_5"] >= 3.5) & (df["nvidia_defensibility_1_5"] < 3.0)]
    fortress = df[(df["attractiveness_1_5"] >= 3.5) & (df["nvidia_defensibility_1_5"] >= 4.0)]
    c = Chart(
        id="19-challenger-win-matrix",
        title="Repo view: custom silicon and agentic CPUs look most open to a challenger; MoE tokens per MW "
              "is NVIDIA's fortress",
        subtitle="Eleven inference and CPU segments scored 1-5 on attractiveness to a challenger and on NVIDIA's "
                 "defensibility (repo judgement, speculative)",
        alt=("Scatter of eleven segments by attractiveness to a challenger (x, 1-5) and NVIDIA's defensibility (y, "
             "1-5), all repo judgements. Most open (attractive, weakly defended): hyperscaler custom silicon (4.5, "
             "1.5) and agentic head-node CPUs (4.0, 2.5). NVIDIA's fortress: chat-speed MoE serving per megawatt "
             "(5.0, 5.0) and the fast-decode tier (3.5, 4.0); frontier training (2.5, 5.0) is shown for reference. "
             "Middle ground: LPDDR capacity-bound serving (3.5, 3.0) and sovereign programmes (3.5, 3.5). Niches "
             "with low defensibility but smaller, captive or unproven pools: small and medium dense models (3.25, "
             "2.0), power-capped sites (2.75, 2.5), recommendation (2.5, 2.5) and edge-to-cloud continuity (2.5, "
             "2.0)."),
        data=["x19_win_matrix.csv"],
        chapters=CH + ["14", "15"],
        source="repo analysis of layer pages and chapters 14-15",
        source_ids=sources_of(df),
        note=f"Speculative scores; {len(open_)} segments in the open quadrant, {len(fortress)} in the fortress.",
    )
    fig, ax = c.figure(width=11.0, height=7.4)
    ax.axvline(3.0, color=INK["base"], lw=1.2, zorder=1)
    ax.axhline(3.0, color=INK["base"], lw=1.2, zorder=1)
    corner = dict(fontsize=9.5, color=INK["muted"], fontweight="bold")
    ax.text(5.35, 5.38, "Fortress: attractive but\nheavily defended", ha="right", va="top", **corner)
    ax.text(0.65, 5.38, "Avoid: small and defended", ha="left", va="top", **corner)
    ax.text(0.65, 0.62, "Niche options", ha="left", va="bottom", **corner)
    ax.text(5.35, 0.62, "Openings: attractive and\nweakly defended", ha="right", va="bottom", **corner)
    for grp, (mk, col, lab) in GROUP_STYLE.items():
        sub = df[df["group"] == grp]
        ax.scatter(sub["attractiveness_1_5"], sub["nvidia_defensibility_1_5"], marker=mk, s=120, color=col,
                   edgecolor="#FFFFFF", linewidth=1.2, zorder=4, label=lab)
    for r in df.itertuples():
        dx, dy, ha = LABEL_OFFSET.get(r.short_label, (9, 0, "left"))
        ax.annotate(r.short_label, (r.attractiveness_1_5, r.nvidia_defensibility_1_5), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va="center", fontsize=9, color=INK["title"], zorder=5)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.grid(axis="both", color=INK["grid"], lw=0.6)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 0.08), fontsize=8.5, frameon=False)
    c.save(fig, ax, xlabel="Attractiveness to a challenger (pool size, growth, fit with public assets; 1-5)",
           ylabel="NVIDIA defensibility (1-5)", legend=False)


# --------------------------------------------------------------------------------------
# 3. Rack memory: accelerator-attached vs CPU-attached, and per kW
# --------------------------------------------------------------------------------------
@register
def rack_memory_capacity():
    df = load("x19_rack_memory.csv")
    df["cpu_attached_lpddr_tb"] = df["cpu_attached_lpddr_tb"].fillna(0.0)
    df["tb_per_kw"] = df["accelerator_memory_tb"] / df["rack_power_kw"]
    order = ["Qualcomm AI200 rack (MWC 2026 configuration)", "AMD Helios", "GB300 NVL72", "Vera Rubin NVL72"]
    df = df.set_index("system").loc[order].reset_index()
    short = {"Qualcomm AI200 rack (MWC 2026 configuration)": "Qualcomm AI200 rack\n(56 cards, reported)",
             "AMD Helios": "AMD Helios\n(72 MI455X)", "GB300 NVL72": "GB300 NVL72",
             "Vera Rubin NVL72": "Vera Rubin NVL72"}
    qc = df.iloc[0]
    vr = df[df["system"] == "Vera Rubin NVL72"].iloc[0]
    c = Chart(
        id="19-rack-memory-capacity",
        title=f"A reported AI200 rack holds ~{qc.accelerator_memory_tb:.0f} TB on its cards, 2x Rubin's HBM4, "
              f"but Vera Rubin adds {vr.cpu_attached_lpddr_tb:.0f} TB of LPDDR5X behind its CPUs",
        subtitle="Memory per rack in TB (accelerator-attached vs CPU-attached LPDDR5X) and accelerator memory per "
                 "kW of rack power",
        alt=(f"Two-panel bar chart. Left: memory per rack. A Qualcomm AI200 rack in a reported 56-card MWC 2026 "
             f"configuration holds about {qc.accelerator_memory_tb:.0f} TB of LPDDR on its accelerators; AMD Helios "
             f"31.1 TB of HBM4; GB300 NVL72 20.7 TB of HBM3E plus about 17 TB of CPU-attached LPDDR5X; Vera Rubin "
             f"NVL72 20.7 TB of HBM4 plus 54 TB of LPDDR5X on its Vera CPUs, about 75 TB in all. Right: "
             f"accelerator-attached memory per kW of rack power: AI200 about {qc.tb_per_kw:.2f} TB/kW at 160 kW, "
             f"GB300 0.16, Helios 0.13 and Vera Rubin 0.09. Capacity per watt favours the LPDDR design; bandwidth, "
             f"which Qualcomm has not disclosed for AI200, favours HBM (Vera Rubin 1,400 TB/s per rack)."),
        data=["x19_rack_memory.csv"],
        chapters=CH + ["03", "08"],
        source="Qualcomm, NVIDIA, AMD specifications and press reports",
        source_ids=sources_of(df),
        note="AI200 rack configuration from low-tier reports (single configuration); host DRAM of AI200 and Helios not counted.",
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=12.0, height=5.8, gridspec_kw={"width_ratios": [1.5, 1]})
    y = np.arange(len(df))[::-1]
    cols = [QC, AMD, NV, NV]
    a1.barh(y, df["accelerator_memory_tb"], color=cols, height=0.6, label="Accelerator-attached (HBM or LPDDR)")
    cpu_bars = a1.barh(y, df["cpu_attached_lpddr_tb"], left=df["accelerator_memory_tb"], color="#A9CC73",
                       height=0.6, label="CPU-attached LPDDR5X (hatched)")
    for p in cpu_bars.patches:
        p.set_hatch("///")
    for yi, r in zip(y, df.itertuples()):
        tot = r.accelerator_memory_tb + r.cpu_attached_lpddr_tb
        txt = f"{r.accelerator_memory_tb:.1f} TB {r.accelerator_memory_type}"
        if r.cpu_attached_lpddr_tb:
            txt += f" + {r.cpu_attached_lpddr_tb:.0f} TB LPDDR5X"
        a1.annotate(txt, (tot, yi), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.5,
                    color=INK["text"])
    a1.set_yticks(y)
    a1.set_yticklabels([short[s] for s in df["system"]], fontsize=9)
    a1.set_xlim(0, 125)
    a1.set_xlabel("Memory per rack (TB)")
    a1.grid(axis="x", color=INK["grid"], lw=0.6)
    a1.grid(axis="y", visible=False)
    a1.legend(loc="upper right", bbox_to_anchor=(1.0, 0.83), fontsize=8.2, frameon=False)
    a1.set_axisbelow(True)
    a2.set_axisbelow(True)
    a2.barh(y, df["tb_per_kw"], color=cols, height=0.6)
    for yi, r in zip(y, df.itertuples()):
        a2.annotate(f"{r.tb_per_kw:.2f} TB/kW ({r.rack_power_kw:.0f} kW)", (r.tb_per_kw, yi), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=8.5, color=INK["text"])
    a2.set_yticks(y)
    a2.set_yticklabels([])
    a2.set_xlim(0, 0.42)
    a2.set_xlabel("Accelerator memory per kW of rack power (TB/kW)")
    a2.grid(axis="x", color=INK["grid"], lw=0.6)
    a2.grid(axis="y", visible=False)
    for a in (a1, a2):
        a.tick_params(length=0)
    _widen(fig, left=0.15, right=0.98, wspace=0.08)
    c.save(fig, [a1, a2], legend=False, bottom=0.16)


# --------------------------------------------------------------------------------------
# 4. Edge base vs datacenter
# --------------------------------------------------------------------------------------
@register
def edge_vs_datacenter_revenue():
    df = load("x19_edge_base.csv")
    edge = df[df["panel"] == "edge"]
    dc = df[df["panel"] == "datacenter"]
    qc_edge = edge[edge["entity"] == "Qualcomm"]["revenue_usd_b"].sum()
    nv_edge = edge[edge["entity"] == "NVIDIA"]["revenue_usd_b"].sum()
    nv_dc = dc[dc["entity"] == "NVIDIA"]["revenue_usd_b"].sum()
    qc_dc = dc[dc["entity"] == "Qualcomm"]["revenue_usd_b"].sum()
    ratio = nv_dc / qc_dc
    c = Chart(
        id="19-edge-vs-datacenter-revenue",
        title=f"Qualcomm out-sells NVIDIA at the edge (${qc_edge:.1f}B vs ${nv_edge:.1f}B a quarter), but NVIDIA's "
              f"datacenter quarter is ~{ratio:.0f}x Qualcomm's goal",
        subtitle="Quarterly revenue, US$ B: Qualcomm QCT Q3 FY2026 vs NVIDIA Q2 FY2027 (quarters ending June-July 2026)",
        alt=(f"Two-panel horizontal bar chart of quarterly revenue. Edge: Qualcomm's QCT chip revenue for the quarter "
             f"to 2026-06-28 was about ${qc_edge:.1f}B (handsets $5.09B, IoT $1.83B, automotive $1.59B), against "
             f"NVIDIA's Edge Computing platform at ${nv_edge:.1f}B for the quarter to 2026-07-26 (former gaming, "
             f"professional visualization, automotive and OEM). Datacenter: NVIDIA's Data Center platform "
             f"${nv_dc:.1f}B in the same quarter versus ${qc_dc:.2f}B a quarter implied by Qualcomm's $5B FY2027 "
             f"data-center target (hatched), a ratio of about {ratio:.0f} to 1."),
        data=["x19_edge_base.csv"],
        chapters=CH + ["13"],
        source="Qualcomm and NVIDIA quarterly results",
        source_ids=sources_of(df),
        note="Hatched = company target divided by four, not reported revenue. Segments are not like-for-like.",
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=12.0, height=5.0, gridspec_kw={"width_ratios": [1, 1.25]})
    # edge panel: stacked Qualcomm vs NVIDIA
    shades = {"QCT Handsets": QC, "QCT IoT": "#6F7FD9", "QCT Automotive": "#A7B1EA"}
    left = 0.0
    for r in edge[edge["entity"] == "Qualcomm"].itertuples():
        a1.barh(1, r.revenue_usd_b, left=left, color=shades[r.segment], height=0.55, edgecolor="#FFFFFF")
        a1.text(left + r.revenue_usd_b / 2, 1, f"{r.segment.replace('QCT ', '').replace('Automotive', 'Auto')}\n${r.revenue_usd_b:.2f}B",
                ha="center", va="center", fontsize=8, color="#FFFFFF" if r.segment == "QCT Handsets" else INK["title"])
        left += r.revenue_usd_b
    a1.annotate(f"${qc_edge:.1f}B", (qc_edge, 1), xytext=(4, 0), textcoords="offset points", va="center",
                fontsize=9, fontweight="bold", color=QC)
    a1.barh(0, nv_edge, color=NV, height=0.55)
    a1.annotate(f"${nv_edge:.1f}B", (nv_edge, 0), xytext=(4, 0), textcoords="offset points", va="center",
                fontsize=9, fontweight="bold", color=NV)
    a1.set_yticks([1, 0])
    a1.set_yticklabels(["Qualcomm QCT\n(Q3 FY2026)", "NVIDIA Edge\nComputing (Q2 FY2027)"], fontsize=9)
    a1.set_xlim(0, 10.5)
    a1.set_xlabel("Edge revenue per quarter (US$ B)")
    a1.set_title("Edge and devices", fontsize=10, color=INK["text"], loc="left")
    # datacenter panel
    a2.barh(1, qc_dc, color=QC, height=0.55, hatch="///", alpha=0.75)
    a2.annotate(f"${qc_dc:.2f}B (FY2027 target / 4)", (qc_dc, 1), xytext=(4, 0), textcoords="offset points",
                va="center", fontsize=9, fontweight="bold", color=QC)
    a2.barh(0, nv_dc, color=NV, height=0.55)
    a2.annotate(f"${nv_dc:.1f}B", (nv_dc, 0), xytext=(-4, 0), textcoords="offset points", va="center",
                ha="right", fontsize=9, fontweight="bold", color="#FFFFFF")
    a2.set_yticks([1, 0])
    a2.set_yticklabels(["Qualcomm\nData Center", "NVIDIA\nData Center"], fontsize=9)
    a2.set_xlim(0, 95)
    a2.set_xlabel("Datacenter revenue per quarter (US$ B)")
    a2.set_title("Datacenter", fontsize=10, color=INK["text"], loc="left")
    for a in (a1, a2):
        a.grid(axis="x", color=INK["grid"], lw=0.6)
        a.grid(axis="y", visible=False)
        a.tick_params(length=0)
        a.set_axisbelow(True)
    _widen(fig, left=0.14, right=0.98, wspace=0.42)
    c.save(fig, [a1, a2], legend=False, bottom=0.2, top=0.80)


# --------------------------------------------------------------------------------------
# 5. Warrant "rebate" per purchase dollar: AMD-OpenAI vs Qualcomm-AWS
# --------------------------------------------------------------------------------------
@register
def warrant_rebate_curves():
    df = load("x19_warrant_terms.csv")
    amd = df[df["issuer"] == "AMD"].iloc[0]
    qc = df[df["issuer"] == "Qualcomm"].iloc[0]
    m = np.linspace(0.5, 4.0, 141)

    def pct(row, mult):
        price = mult * row.reference_price_usd
        intrinsic = np.maximum(price - row.strike_usd, 0.0) * row.warrant_shares_m * 1e6
        return intrinsic / (row.purchase_basis_usd_b * 1e9) * 100

    amd_1 = float(pct(amd, 1.0))
    qc_125 = float(pct(qc, 1.25))
    qc_2 = float(pct(qc, 2.0))
    amd_sep = 612.46 / amd.reference_price_usd
    c = Chart(
        id="19-warrant-rebate-curves",
        title=f"Per purchase dollar, AMD's penny warrant gave OpenAI ~{amd_1:.0f}% at signing; Qualcomm's AWS "
              f"warrant pays only if its stock rises",
        subtitle="Intrinsic value of the fully vested warrant as % of the purchases that vest it, vs issuer share "
                 "price as a multiple of the reference price",
        alt=(f"Line chart of warrant intrinsic value as a share of the purchases that vest it. AMD's warrant to "
             f"OpenAI (160M shares at a $0.01 strike, against a repo base case of ~$90B of AMD hardware for 6 GW) "
             f"is worth ~{amd_1:.0f}% of purchases at the pre-deal price of $164.67 and ~"
             f"{float(pct(amd, amd_sep)):.0f}% at the $612.46 close of 2026-09-21. Qualcomm's warrant to Amazon "
             f"(25M shares at a $161.26 strike, vesting on up to $60B of purchases through 2036) is worth 0% at the "
             f"strike, ~{qc_125:.1f}% if the stock is 25% higher and ~{qc_2:.1f}% if it doubles. The AMD structure "
             f"is a large equity rebate; the Qualcomm structure is an at-the-money option that pays only if "
             f"Qualcomm's shares appreciate."),
        data=["x19_warrant_terms.csv"],
        chapters=CH + ["13"],
        source="AMD and Qualcomm warrant terms as reported; CS4 spend scenario",
        source_ids=sources_of(df),
        note="Ignores time value, vesting hurdles and tax; AMD purchase basis is a repo scenario (speculative).",
    )
    fig, ax = c.figure(width=11.5, height=6.2)
    ax.plot(m, pct(amd, m), color=AMD, lw=2.2, label="AMD to OpenAI (160M shares, $0.01 strike, ~$90B est. purchases)")
    ax.plot(m, pct(qc, m), color=QC, lw=2.2, label="Qualcomm to AWS (25M shares, $161.26 strike, up to $60B purchases)")
    ax.scatter([1.0, amd_sep], [amd_1, float(pct(amd, amd_sep))], color=AMD, s=60, zorder=5)
    ax.annotate(f"At signing: ~{amd_1:.0f}%", (1.0, amd_1), xytext=(10, -14), textcoords="offset points",
                fontsize=9, color=AMD)
    ax.annotate(f"2026-09-21 close ($612): ~{float(pct(amd, amd_sep)):.0f}%", (amd_sep, float(pct(amd, amd_sep))),
                xytext=(-10, 10), textcoords="offset points", ha="right", fontsize=9, color=AMD)
    ax.scatter([1.0, 1.25, 2.0], [0.0, qc_125, qc_2], color=QC, s=60, zorder=5)
    ax.annotate(f"At strike: 0%   +25%: ~{qc_125:.1f}%", (1.25, qc_125), xytext=(10, 14), textcoords="offset points",
                fontsize=9, color=QC)
    ax.annotate(f"Doubles: ~{qc_2:.1f}%", (2.0, qc_2), xytext=(8, 12), textcoords="offset points", fontsize=9,
                color=QC)
    ax.set_xlim(0.5, 4.0)
    ax.set_ylim(0, 125)
    ax.grid(axis="y", color=INK["grid"], lw=0.6)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=8.5, frameon=False)
    c.save(fig, ax, xlabel="Issuer share price as a multiple of the reference price (AMD $164.67; Qualcomm $161.26 strike)",
           ylabel="Warrant value as % of purchases", legend=False)


# --------------------------------------------------------------------------------------
# 6. What datacenter capabilities have cost: price points by acquirer
# --------------------------------------------------------------------------------------
@register
def capability_price_points():
    df = load("x19_capability_price_points.csv", dtype={"layer_id": str}).sort_values("value_usd_b")
    qc_total = df[df["acquirer"] == "Qualcomm"]["value_usd_b"].sum()
    gaps = df[df["layer_id"].isin(["07", "08"])]
    lo, hi = gaps["value_usd_b"].min(), gaps["value_usd_b"].max()
    c = Chart(
        id="19-capability-price-points",
        title=f"Qualcomm's three priced datacenter buys total ${qc_total:.1f}B; the gaps it has not filled "
              f"(NIC, DPU, rack teams) traded at ${lo:.1f}-{hi:.1f}B elsewhere",
        subtitle="Announced or reported deal value, US$ B (log scale), by capability bought and stack layer, 2015-2026",
        alt=(f"Log-scale horizontal bar chart of datacenter capability deals. Qualcomm (indigo): NUVIA CPU cores "
             f"$1.4B (2021), Alphawave SerDes and connectivity IP ~$2.4B (2025) and Modular portable AI software "
             f"$3.9B (2026), ${qc_total:.1f}B in total; Ventana (RISC-V) was undisclosed. For comparison: NVIDIA's "
             f"Groq licence and team ~$20B, Mellanox $6.9B, Enfabrica >$0.9B and Run:ai ~$0.7B; SoftBank-Ampere "
             f"$6.5B; AMD's ZT Systems $4.9B (~$2B net), Pensando ~$1.9B and Silo AI $0.665B; Marvell-Celestial AI "
             f"$3.25B upfront; Intel-Habana ~$2B; Amazon-Annapurna ~$0.36B; Microsoft-Fungible ~$0.19B. "
             f"Capabilities Qualcomm has not publicly bought, such as NIC, DPU and rack-design teams, changed hands "
             f"for ${lo:.2f}-{hi:.1f}B (layers 07 and 08)."),
        data=["x19_capability_price_points.csv"],
        chapters=CH + ["13", "07", "08"],
        source="company announcements and press reports",
        source_ids=sources_of(df),
        note="Values are not like-for-like (licences, gross vs net, upfront vs earn-outs).",
    )
    fig, ax = c.figure(width=11.5, height=7.0)
    y = np.arange(len(df))
    cols = [entity_color(a) if a in ("Qualcomm", "NVIDIA", "AMD", "Marvell", "Intel", "Microsoft") else LIGHT
            for a in df["acquirer"]]
    bars = ax.barh(y, df["value_usd_b"], color=cols, height=0.62)
    for b, r in zip(bars, df.itertuples()):
        ax.annotate(f"${r.value_usd_b:g}B · L{r.layer_id} {r.capability}", (r.value_usd_b, b.get_y() + b.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.2, color=INK["text"])
    ax.set_yticks(y)
    ax.set_yticklabels([f"{d} ({yr})" for d, yr in zip(df["deal"], df["year"])], fontsize=8.6)
    for lab, a in zip(ax.get_yticklabels(), df["acquirer"]):
        if a == "Qualcomm":
            lab.set_color(QC)
            lab.set_fontweight("bold")
    ax.set_xscale("log")
    ax.set_xlim(0.1, 700)
    ax.grid(axis="x", color=INK["grid"], lw=0.6)
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    handles = [Patch(color=entity_color(a), label=a) for a in ("Qualcomm", "NVIDIA", "AMD", "Marvell", "Intel",
                                                               "Microsoft")]
    handles.append(Patch(color=LIGHT, label="Other (SoftBank, Amazon)"))
    ax.legend(handles=handles, loc="lower right", fontsize=8.2, frameon=False, ncol=2)
    _widen(fig, left=0.27, right=0.98)
    c.save(fig, ax, xlabel="Deal value (US$ B)", logx=True, legend=False)
