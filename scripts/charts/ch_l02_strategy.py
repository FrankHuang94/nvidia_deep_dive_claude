"""Layer 02 (GPU silicon) STRATEGY charts: competition, history, roadmap, value chain.

Data: gpu_product_specs.csv, competitor_accelerators.csv, market_share.csv, financials.csv and the
layer's own files l02_replication_costs.csv, l02_chip_startups.csv, l02_rubin_spec_revisions.csv,
l02_custom_silicon_revenue.csv (documented in data/README.md, "Layer 02 strategy").
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import (Chart, GEN_PAST, INK, NV, entity_color, load, register, sources_of)


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
# 1. Competition: FP8 compute per watt vs memory per chip
# ------------------------------------------------------------------------------------------
NV_PICK = {"H100 SXM": "H100", "H200 SXM": "H200", "B200 (HGX)": "B200", "B300 (HGX)": "B300",
           "GB300 (per GPU)": "GB300", "Rubin (VR200, per GPU)": "Rubin"}
COMP_PICK = {"Instinct MI300X": "MI300X", "Instinct MI325X": "MI325X", "Instinct MI350X": "MI350X",
             "Instinct MI355X": "MI355X", "Gaudi 2": "Gaudi 2", "Gaudi 3": "Gaudi 3", "Maia 200": "Maia 200",
             "Blackhole p150": "Blackhole"}
RUBIN_MAXQ_W = 1800  # reported Max-Q power profile (SemiAnalysis/Kuo), see gpu_product_specs notes


@register
def fp8_per_watt_vs_memory():
    g = load("gpu_product_specs.csv")
    k = load("competitor_accelerators.csv")
    gs = g[g["product"].isin(NV_PICK)].copy()
    gs["label"] = gs["product"].map(NV_PICK)
    gs["entity"] = "NVIDIA"
    ks = k[k["product"].isin(COMP_PICK)].copy()
    ks["label"] = ks["product"].map(COMP_PICK)
    ks["entity"] = ks["vendor"]
    cols = ["label", "entity", "memory_capacity_gb", "memory_bandwidth_tbs", "fp8_tflops_dense", "tdp_w"]
    d = pd.concat([gs[cols], ks[cols]], ignore_index=True).dropna(subset=["fp8_tflops_dense", "tdp_w"])
    d["eff"] = d.fp8_tflops_dense / d.tdp_w
    rubin = d[d.label == "Rubin"].iloc[0]
    maia = d[d.label == "Maia 200"].iloc[0]
    best_amd = d[d.entity == "AMD"].sort_values("eff").iloc[-1]
    rubin_q = rubin.fp8_tflops_dense / RUBIN_MAXQ_W
    c = Chart(
        id="02-fp8-per-watt-vs-memory",
        title=f"Rubin leads FP8 per watt (~{rubin.eff:.1f} TFLOPS/W); Maia 200 is next at ~{maia.eff:.1f}",
        subtitle="Dense FP8 TFLOPS per watt of chip/module power vs memory per chip; bubble area = memory bandwidth (TB/s)",
        alt=(f"Scatter chart of dense FP8 TFLOPS per watt against memory per chip. NVIDIA Rubin reaches about {rubin.eff:.1f} "
             f"TFLOPS/W at a reported 2.3 kW (about {rubin_q:.1f} at 1.8 kW) with 288 GB; Microsoft Maia 200 about {maia.eff:.1f} "
             f"with 216 GB; AMD's best, {best_amd.label}, about {best_amd.eff:.1f} with {best_amd.memory_capacity_gb:.0f} GB; "
             "B200 4.5, GB300 3.6, MI355X 3.6, H100 2.8 and Gaudi 3 2.0. Google TPU, AWS Trainium, AMD MI455X and Huawei "
             "Ascend 950 are not plotted because no chip power is published."),
        data=["gpu_product_specs.csv", "competitor_accelerators.csv"], chapters=["02", "15"],
        source="vendor specifications (power partly reported)",
        source_ids=_ids(gs, ks),
    )
    fig, ax = c.figure(width=10.5, height=6.2)
    # Rubin range Max-Q..Max-P
    ax.plot([rubin.memory_capacity_gb] * 2, [rubin.eff, rubin_q], color=NV, lw=2, alpha=0.5, zorder=2)
    ax.annotate(f"Rubin at 1.8 kW Max-Q (reported): {rubin_q:.1f}", (rubin.memory_capacity_gb, rubin_q),
                xytext=(-8, 0), textcoords="offset points", va="center", ha="right", fontsize=8.5, color=INK["text"])
    offsets = {"H100": (-8, -14), "H200": (8, -12), "B200": (-10, 8), "B300": (8, 6), "GB300": (10, -12),
               "Rubin": (12, -4), "MI300X": (-6, 12), "MI325X": (8, -10), "MI350X": (8, 8), "MI355X": (10, 9),
               "Gaudi 2": (8, -8), "Gaudi 3": (8, 6), "Maia 200": (10, 6), "Blackhole": (8, 6)}
    order = sorted(d.itertuples(), key=lambda r: (r.entity == "NVIDIA", r.label == "Rubin"))
    for r in order:
        col = NV if r.entity == "NVIDIA" else entity_color(r.entity)
        if r.entity == "NVIDIA" and r.label not in ("Rubin",):
            col = GEN_PAST if r.label in ("H100", "H200") else NV
        size = 40 + 32 * float(r.memory_bandwidth_tbs)
        ax.scatter(r.memory_capacity_gb, r.eff, s=size, color=col, alpha=0.85, edgecolor="white", lw=1.2,
                   zorder=4 if r.entity == "NVIDIA" else 3)
        dx, dy = offsets.get(r.label, (8, 6))
        ax.annotate(r.label, (r.memory_capacity_gb, r.eff), xytext=(dx, dy), textcoords="offset points",
                    fontsize=9, color=INK["title"] if r.entity == "NVIDIA" else col,
                    fontweight="bold" if r.label in ("Rubin", "Maia 200") else "normal",
                    ha="left" if dx >= 0 else "right", va="center")
    ax.set_xlim(0, 340)
    ax.set_ylim(0, 10.8)
    ax.text(0.01, 0.97, "Not plotted (no chip power published): Google Ironwood / TPU 8t, AWS Trainium3,\n"
            "AMD MI455X, Huawei Ascend 950. Power = vendor TDP or reported module power,\n"
            "so cross-vendor comparisons are approximate.",
            transform=ax.transAxes, va="top", fontsize=8.5, color=INK["muted"])
    handles = [Line2D([], [], marker="o", ls="", color=entity_color(e), markersize=9, label=e)
               for e in ["NVIDIA", "AMD", "Intel", "Microsoft", "Tenstorrent"]]
    ax.legend(handles=handles, loc="lower right", ncol=5, fontsize=8.5)
    c.save(fig, ax, xlabel="Memory per chip (GB)", ylabel="Dense FP8 TFLOPS per watt", legend=False)


# ------------------------------------------------------------------------------------------
# 2. Competition / value chain: Broadcom AI revenue as % of NVIDIA data-center revenue
# ------------------------------------------------------------------------------------------
def _cal_q(ts: str) -> str:
    t = pd.Timestamp(ts)
    return f"{t.year}-Q{(t.month - 1) // 3 + 1}"


@register
def broadcom_vs_nvidia_dc():
    ms = load("market_share.csv")
    b1 = ms[(ms.segment == "custom_asic_partner_revenue") & (ms.entity == "Broadcom")][
        ["year", "value", "confidence", "source_id", "notes"]].rename(columns={"year": "q"})
    cs = load("l02_custom_silicon_revenue.csv")
    b2 = cs[(cs.company == "Broadcom") & (cs.basis != "guidance")][
        ["calendar_quarter", "value", "confidence", "source_id", "basis"]].rename(columns={"calendar_quarter": "q"})
    b2 = b2.rename(columns={"basis": "notes"})
    b = pd.concat([b1, b2], ignore_index=True).drop_duplicates("q", keep="last")
    f = load("financials.csv")
    nv = f[(f.metric == "revenue_data_center") & (f.period_type == "Q")].copy()
    nv["q"] = nv.period_end.map(_cal_q)
    m = b.merge(nv[["q", "value", "period", "source_id"]], on="q", suffixes=("_b", "_nv"))
    m = m.sort_values("q")
    m["ratio"] = 100 * m.value_b / m.value_nv
    m["est"] = m.notes.astype(str).str.contains("derived|Guidance|guidance", regex=True)
    first, last = m.iloc[0], m.iloc[-1]
    c = Chart(
        id="02-broadcom-ai-vs-nvidia-dc",
        title=(f"Broadcom's AI revenue rose from ~{m.ratio.iloc[:8].mean():.0f}% to ~{last.ratio:.0f}% of NVIDIA's "
               "data-center revenue in 2026"),
        subtitle="Broadcom AI semiconductor revenue ÷ NVIDIA Data Center revenue, same calendar quarter of quarter-end, %",
        alt=(f"Bar chart: Broadcom's quarterly AI semiconductor revenue held at about 11-14% of NVIDIA's data-center revenue "
             f"from {first.q} to 2026-Q1, then rose to {m.ratio.iloc[-2]:.0f}% in 2026-Q2 (derived) and {last.ratio:.0f}% in "
             f"2026-Q3, when Broadcom booked ${last.value_b:.1f}B against NVIDIA's ${last.value_nv:.1f}B. Broadcom guides "
             "$21.7B for its next quarter."),
        data=["market_share.csv", "l02_custom_silicon_revenue.csv", "financials.csv"], chapters=["02", "15", "18"],
        source="Broadcom and NVIDIA filings; repo calculation",
        source_ids=_ids(b1, b2) + ["S403", "S405"],
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(m))
    bars = ax.bar(x, m.ratio, color=entity_color("Broadcom"), width=0.68)
    for p, e in zip(bars.patches, m.est):
        if e:
            p.set_hatch("///")
            p.set_alpha(0.7)
    for xi, r in zip(x, m.itertuples()):
        ax.annotate(f"{r.ratio:.1f}%", (xi, r.ratio), xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=8.5, color=INK["text"])
    ax.set_xticks(x, [f"{r.q}\n${r.value_b:.1f}B\n/ ${r.value_nv:.0f}B" for r in m.itertuples()], rotation=0,
                  fontsize=8.2)
    ax.set_ylim(0, 22)
    ax.text(0.01, 0.97, "Hatched = Broadcom quarter based on guidance (2026-Q1) or derived from reported growth (2026-Q2).\n"
            "Broadcom AI revenue includes AI Ethernet switching; NVIDIA Data Center includes networking.\n"
            "Tick labels: Broadcom AI revenue / NVIDIA Data Center revenue in the quarter.",
            transform=ax.transAxes, va="top", fontsize=8.3, color=INK["muted"])
    c.save(fig, ax, xlabel="Calendar quarter in which each company's fiscal quarter ended",
           ylabel="Broadcom AI ÷ NVIDIA DC revenue (%)", legend=False, bottom=0.2)


# ------------------------------------------------------------------------------------------
# 3. History: what it costs to play (log scale)
# ------------------------------------------------------------------------------------------
CAT_COLOR = {"design_cost": "#B5B5B5", "startup_capital": "#7A7A7A", "acquisition": None,
             "program_cost": None, "annual_rd": None}


@register
def chip_program_cost_ladder():
    d = load("l02_replication_costs.csv").sort_values("value_usd_b")
    d2 = d[d.item.str.contains("2 nm")].iloc[0]
    bw = d[d.item.str.contains("Blackwell")].iloc[0]
    rd = d[d.item.str.contains("NVIDIA total R&D")].iloc[0]
    c = Chart(
        id="02-chip-program-cost-ladder",
        title=(f"A leading-edge chip design costs ~${d2.value_usd_b:.1f}B; NVIDIA spent ~${bw.value_usd_b:.0f}B on "
               "Blackwell alone"),
        subtitle="US$ billions, log scale: single-chip design estimates, start-up capital, acquisitions and annual R&D budgets",
        alt=(f"Horizontal log-scale bar chart: IBS-based estimates put the design cost of one large chip at about $0.48B (5 nm), "
             f"$0.59B (3 nm) and $0.72B (2 nm); MatX raised $0.5B and Tenstorrent $0.69B; Intel paid $2B for Habana; Cerebras' "
             f"IPO raised $5.55B; AMD's 2024 R&D was $6.5B and Intel's $16.5B; NVIDIA put ~$10B into Blackwell, spent "
             f"${rd.value_usd_b:.1f}B on R&D in FY2026 and paid ~$20B for Groq's technology and team."),
        data=["l02_replication_costs.csv"], chapters=["02", "13", "19"],
        source="IBS via Silicon Analysts and Tom's Hardware; company filings; press reports",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.8, height=6.4)
    _margins(fig, left=0.33, right=0.95)
    y = np.arange(len(d))
    colors = []
    for r in d.itertuples():
        base = CAT_COLOR.get(r.category)
        colors.append(base if base else entity_color(r.entity))
    bars = ax.barh(y, d.value_usd_b, color=colors, height=0.66)
    for p, r in zip(bars.patches, d.itertuples()):
        if r.confidence in ("estimate",) or r.basis == "estimate":
            p.set_hatch("///")
        ax.annotate(f"${r.value_usd_b:,.2f}B" if r.value_usd_b < 1 else f"${r.value_usd_b:,.1f}B",
                    (r.value_usd_b, p.get_y() + p.get_height() / 2), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK["text"])
    labels = [r.item if r.category == "design_cost" or str(r.year) in r.item else f"{r.item} ({r.year})"
              for r in d.itertuples()]
    ax.text(0.99, 0.03, "Light grey hatched = IBS design-cost estimate per chip (excludes IP reuse; may run high)\n"
            "Dark grey = start-up capital raised · colored = company spend · green hatched = CEO estimate",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.2, color=INK["muted"])
    ax.set_yticks(y, labels, fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 60)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="US$ billions (log scale)", legend=False, logx=True)


# ------------------------------------------------------------------------------------------
# 4. Roadmap: flagship dense FP8 per chip by vendor and year
# ------------------------------------------------------------------------------------------
ROADMAP_POINTS = [
    # (vendor, file, product, year, label, status) status: shipping | announced | estimate
    ("NVIDIA", "g", "H100 SXM", 2022, "H100", "shipping"),
    ("NVIDIA", "g", "B200 (HGX)", 2024, "B200", "shipping"),
    ("NVIDIA", "g", "GB300 (per GPU)", 2025, "GB300", "shipping"),
    ("NVIDIA", "g", "Rubin (VR200, per GPU)", 2026, "Rubin", "shipping"),
    ("NVIDIA", "g", "Rubin Ultra (per GPU)", 2027, "Rubin Ultra (Est.)", "estimate"),
    ("AMD", "k", "Instinct MI300X", 2023, "MI300X", "shipping"),
    ("AMD", "k", "Instinct MI355X", 2025, "MI355X", "shipping"),
    ("AMD", "k", "Instinct MI455X", 2026, "MI455X", "shipping"),
    ("Google", "k", "TPU v7 Ironwood", 2025, "Ironwood", "shipping"),
    ("AWS", "k", "Trainium2", 2024, "Trn2", "shipping"),
    ("AWS", "k", "Trainium3", 2025, "Trn3", "shipping"),
    ("Microsoft", "k", "Maia 200", 2026, "Maia 200", "shipping"),
    ("Intel", "k", "Gaudi 3", 2024, "Gaudi 3", "shipping"),
    ("Huawei", "k", "Ascend 950DT", 2026, "Ascend 950", "shipping"),
    ("Huawei", "k", "Ascend 960", 2027, "960", "announced"),
    ("Huawei", "k", "Ascend 970", 2028, "970", "announced"),
]
LABEL_OFF = {"Trn2": (0, -11), "Gaudi 3": (0, -11), "Ascend 950": (0, -11), "960": (0, -11),
             "Ironwood": (-8, -4), "MI355X": (8, -9), "GB300": (0, 10), "Rubin": (9, -6), "MI455X": (-9, 4),
             "MI300X": (0, 10), "H100": (0, 10), "B200": (0, 10)}
TRN4_FP8_MULT = 3.0  # AWS/press: Trainium4 >= 3x Trainium3 FP8 (S557); repo estimate


@register
def fp8_roadmap_by_vendor():
    g = load("gpu_product_specs.csv").set_index("product")
    k = load("competitor_accelerators.csv").set_index("product")
    rows = []
    used_g, used_k = [], []
    for vendor, f, prod, yr, lab, st in ROADMAP_POINTS:
        src = g if f == "g" else k
        val = float(src.loc[prod, "fp8_tflops_dense"]) / 1000
        (used_g if f == "g" else used_k).append(prod)
        rows.append(dict(vendor=vendor, year=yr, label=lab, status=st, pf=val))
    trn3 = float(k.loc["Trainium3", "fp8_tflops_dense"]) / 1000
    rows.append(dict(vendor="AWS", year=2027, label="Trn4 (Est. ≥3×)", status="estimate", pf=trn3 * TRN4_FP8_MULT))
    d = pd.DataFrame(rows)
    rub = d[d.label == "Rubin"].pf.iloc[0]
    mi455 = d[d.label == "MI455X"].pf.iloc[0]
    maia = d[d.label == "Maia 200"].pf.iloc[0]
    asc = d[d.label == "Ascend 950"].pf.iloc[0]
    gsub = load("gpu_product_specs.csv")
    ksub = load("competitor_accelerators.csv")
    c = Chart(
        id="02-fp8-roadmap-by-vendor",
        title=(f"Rubin and MI455X reach {rub:.1f}–{mi455:.0f} PFLOPS FP8 in 2026: {rub / maia:.1f}× Maia 200, "
               f"{rub / asc:.0f}× Ascend 950"),
        subtitle="Flagship dense FP8 PFLOPS per chip by year of volume availability (log scale); hollow = announced/roadmap, dashed = estimate",
        alt=(f"Log-scale line chart of flagship FP8 compute per chip by year: NVIDIA rises from 2.0 PFLOPS (H100, 2022) to "
             f"{rub:.1f} (Rubin, 2026) and an estimated ~35 for Rubin Ultra (2027); AMD from 2.6 (MI300X, 2023) to {mi455:.0f} "
             f"(MI455X, 2026, basis not stated); Google Ironwood 4.6 (2025); AWS Trainium2 1.3, Trainium3 2.5 and an estimated "
             f"~{trn3 * TRN4_FP8_MULT:.1f} for Trainium4; Microsoft Maia 200 {maia:.0f}; Intel Gaudi 3 1.8; Huawei Ascend 950 "
             f"{asc:.0f}, 960 2 and 970 4 PFLOPS by 2028."),
        data=["gpu_product_specs.csv", "competitor_accelerators.csv"], chapters=["02", "15", "17"],
        source="vendor specs and roadmaps; repo Est. for Rubin Ultra, Trn4",
        source_ids=_ids(gsub[gsub["product"].isin(used_g)], ksub[ksub["product"].isin(used_k)]) + ["S557"],
    )
    fig, ax = c.figure(width=10.5, height=6.2)
    order = ["Huawei", "Intel", "AWS", "Google", "Microsoft", "AMD", "NVIDIA"]
    for v in order:
        s = d[d.vendor == v].sort_values("year")
        col = entity_color(v)
        real = s[s.status == "shipping"]
        solid = s[s.status != "estimate"]
        ax.plot(solid.year, solid.pf, color=col, lw=2, alpha=0.9, zorder=3 if v != "NVIDIA" else 5)
        est = s[s.status == "estimate"]
        if len(est):
            prev = s[s.status != "estimate"].iloc[-1]
            ax.plot([prev.year, est.year.iloc[0]], [prev.pf, est.pf.iloc[0]], color="white", lw=2.6, zorder=4)
            ax.plot([prev.year, est.year.iloc[0]], [prev.pf, est.pf.iloc[0]], color=col, lw=2, ls="--", zorder=4)
        ax.scatter(real.year, real.pf, s=60, color=col, zorder=6, edgecolor="white")
        fut = s[s.status != "shipping"]
        ax.scatter(fut.year, fut.pf, s=60, facecolor="white", edgecolor=col, lw=2, zorder=6)
        for r in s.itertuples():
            dx, dy = LABEL_OFF.get(r.label, (0, 9))
            ax.annotate(r.label, (r.year, r.pf), xytext=(dx, dy), textcoords="offset points",
                        ha="center" if dx == 0 else ("left" if dx > 0 else "right"), va="center",
                        fontsize=8.3, color=col if v != "NVIDIA" else INK["title"],
                        fontweight="bold" if r.label in ("Rubin", "MI455X") else "normal")
    ax.set_yscale("log")
    ax.set_ylim(0.6, 60)
    ax.set_xlim(2021.6, 2028.5)
    ax.set_xticks(range(2022, 2029))
    ax.set_yticks([1, 2, 5, 10, 20, 50], ["1", "2", "5", "10", "20", "50"])
    handles = [Line2D([], [], color=entity_color(v), lw=2, marker="o", label=v) for v in reversed(order)]
    ax.legend(handles=handles, loc="upper left", ncol=4, fontsize=8.5)
    ax.text(0.01, 0.86, "Google TPU 8t (2026) publishes FP4 only (12.6 PFLOPS) and is omitted.\n"
            "MI455X: AMD did not state dense vs sparse.\nHollow = roadmap; dashed = repo estimate.",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.2, color=INK["muted"])
    c.save(fig, ax, xlabel="Year of volume availability", ylabel="Dense FP8 PFLOPS per chip", logy=True, legend=False)


# ------------------------------------------------------------------------------------------
# 5. Roadmap: Rubin 2026 spec revision vs AMD MI455X
# ------------------------------------------------------------------------------------------
@register
def rubin_spec_revision():
    d = load("l02_rubin_spec_revisions.csv")
    metrics = [("hbm_bandwidth_per_gpu", "HBM bandwidth per GPU (TB/s)"),
               ("scale_up_bandwidth_per_gpu", "Scale-up bandwidth per GPU (TB/s)"),
               ("hbm_capacity_per_gpu", "HBM capacity per GPU (GB)"),
               ("fp8_dense_per_gpu", "FP8 compute per GPU (PFLOPS)")]

    def val(prod, met, ver):
        s = d[(d["product"] == prod) & (d.metric == met) & (d.spec_version == ver)]
        return float(s.value.iloc[0])
    hb_l, hb_r = val("NVIDIA Rubin", metrics[0][0], "launch"), val("NVIDIA Rubin", metrics[0][0], "revised")
    nl_l, nl_r = val("NVIDIA Rubin", metrics[1][0], "launch"), val("NVIDIA Rubin", metrics[1][0], "revised")
    c = Chart(
        id="02-rubin-spec-revision",
        title=(f"Rubin's 2026 revision cut HBM bandwidth {100 * (1 - hb_r / hb_l):.0f}% and NVLink "
               f"{100 * (1 - nl_r / nl_l):.0f}%; MI455X now leads on paper"),
        subtitle="Per-GPU specs: Rubin at CES 2026 launch (hatched, superseded) vs revised pages (Sep–Oct 2026) vs AMD MI455X",
        alt=(f"Four-panel bar chart. HBM bandwidth per GPU: Rubin launch {hb_l:.0f} TB/s, revised {hb_r:.1f}, MI455X 19.6. "
             f"Scale-up bandwidth: Rubin launch {nl_l:.1f} TB/s, revised {nl_r:.1f}, MI455X 3.6. HBM capacity: Rubin 288 GB "
             "unchanged, MI455X 432 GB. Dense FP8: Rubin 17.5 PFLOPS unchanged, MI455X 20 PFLOPS (AMD did not state dense "
             "or sparse). NVIDIA says the revised figures reflect quality volume production."),
        data=["l02_rubin_spec_revisions.csv"], chapters=["02", "03", "05", "17"],
        source="NVIDIA product pages and statements; AMD; press coverage of the revision",
        source_ids=sources_of(d),
    )
    fig, axes = c.figure_grid(1, 4, width=11.5, height=5.6)
    series = [("NVIDIA Rubin", "launch", "Rubin\nlaunch"), ("NVIDIA Rubin", "revised", "Rubin\nrevised"),
              ("AMD MI455X", "launch", "MI455X")]
    for ax, (met, lab) in zip(axes, metrics):
        vals = [val(p, met, v) for p, v, _ in series]
        cols = [GEN_PAST, NV, entity_color("AMD")]
        bars = ax.bar(range(3), vals, color=cols, width=0.7)
        bars.patches[0].set_hatch("///")
        for b, v in zip(bars.patches, vals):
            ax.annotate(f"{v:g}", (b.get_x() + b.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=9, color=INK["text"])
        ax.set_xticks(range(3), [s[2] for s in series], fontsize=8.5)
        ax.set_title(lab, fontsize=9.5, color=INK["title"], pad=8)
        ax.set_ylim(0, max(vals) * 1.22)
        ax.tick_params(length=0)
        ax.set_axisbelow(True)
    _margins(fig, left=0.05, right=0.98, wspace=0.35)
    c.save(fig, axes, legend=False, top=0.80)


# ------------------------------------------------------------------------------------------
# 6. Value chain: AI-chip start-up valuations and exits
# ------------------------------------------------------------------------------------------
STATUS_COLOR = {"public": "#3C3C3C", "licensed to NVIDIA": NV, "acquired": entity_color("Marvell"),
                "private": "#7A7A7A"}


@register
def chip_startup_valuations():
    d = load("l02_chip_startups.csv").sort_values("value_usd_b")
    top = d.iloc[-1]
    c = Chart(
        id="02-chip-startup-valuations",
        title=f"AI-chip start-up values span ~$1.6B–${top.value_usd_b:.0f}B; Groq's ~$20B exit went to NVIDIA",
        subtitle="Latest disclosed valuation or deal value, US$ billions (basis varies: see labels)",
        alt=("Horizontal bar chart of AI-chip start-up values: Cerebras about $40B at its May 2026 IPO (reports up to ~$56B fully "
             "diluted); Groq ~$20B NVIDIA licence and team deal (Dec 2025); Etched $10.3B (Series C, Jul 2026, reported); "
             "Lightmatter $4.4B (Oct 2024); Celestial AI $3.25B upfront from Marvell (Feb 2026); Tenstorrent ~$2.7B post-money "
             "(Dec 2024); d-Matrix $2.0B (Nov 2025); SambaNova ~$1.6B in stalled Intel talks versus $5B in 2021."),
        data=["l02_chip_startups.csv"], chapters=["02", "13", "19"],
        source="company announcements, IPO and press reports",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.8, height=5.9)
    _margins(fig, left=0.2, right=0.97)
    y = np.arange(len(d))
    cols = [STATUS_COLOR.get(s, "#7A7A7A") for s in d.status]
    bars = ax.barh(y, d.value_usd_b, color=cols, height=0.64)
    for p, r in zip(bars.patches, d.itertuples()):
        ax.annotate(f"${r.value_usd_b:g}B · {r.latest_event} ({str(r.event_date)[:7]})",
                    (r.value_usd_b, p.get_y() + p.get_height() / 2), xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK["text"])
    ax.set_yticks(y, [f"{r.company}\n{r.architecture}" for r in d.itertuples()], fontsize=8.6)
    ax.set_xlim(0, 56)
    ax.set_axisbelow(True)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.text(0.99, 0.30, "Not like-for-like: IPO pricing (low end of reports),\nround valuations, deal values and a reported offer",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.2, color=INK["muted"])
    handles = [Patch(color=v, label=k) for k, v in STATUS_COLOR.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=8.5)
    c.save(fig, ax, xlabel="US$ billions", legend=False)
