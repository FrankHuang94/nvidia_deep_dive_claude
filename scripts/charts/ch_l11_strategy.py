"""Layer 11 (inference and AI software) strategy charts: challenger heatmap, inference-silicon memory trade-off,
bandwidth progression by vendor, inference deal values, API token prices, private-company valuations and the
value pools behind $1 of API revenue.

Owner: layer-11 STRATEGY agent. Data: data/l11_inference_verdicts.csv, l11_inference_deals.csv, l11_token_prices.csv,
l11_private_companies.csv, l11_token_value_pools.csv (documented in data/README.md) plus the shared
gpu_product_specs.csv and competitor_accelerators.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from style import (Chart, GEN_PAST, INK, NV, SEQ_BLUE, VERDICT_COLORS, end_label, entity_color, load, register,
                   sources_of)

VERD = "l11_inference_verdicts.csv"
DEALS = "l11_inference_deals.csv"
PRICES = "l11_token_prices.csv"
PRIV = "l11_private_companies.csv"
POOLS = "l11_token_value_pools.csv"
GPU = "gpu_product_specs.csv"
COMP = "competitor_accelerators.csv"

LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}
VERDICT_LABEL = {"leads": "L = rival leads NVIDIA", "parity": "P = parity", "behind": "B = rival behind",
                 "different": "D = different approach"}
STARTUP = entity_color("startups")


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _vcolor(name: str) -> str:
    n = str(name)
    if n.startswith("NVIDIA"):
        return NV
    if n.startswith("Red Hat"):
        return entity_color("other")
    return entity_color(n)


def _wrap(label: str, width: int = 20) -> str:
    if len(label) <= width:
        return label
    cut = label.rfind(" ", 0, width)
    if cut <= 0:
        return label
    return label[:cut] + "\n" + label[cut + 1:]


# --------------------------------------------------------------------------------------
# 1. Challenger heatmap: eight challengers x five inference dimensions
# --------------------------------------------------------------------------------------
@register
def inference_challenger_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    hw = df[~df.competitor.eq("Open-source serving")]
    n_hw = hw.competitor.nunique()
    tpu_cost = df[(df.competitor == "Google TPU") & (df.dimension == "Throughput per dollar")].iloc[0]
    sw_behind = int(hw[hw.dimension.eq("Software maturity")].verdict_vs_nvidia.eq("behind").sum())
    c = Chart(
        id="11-inference-challenger-heatmap",
        title=(f"{sw_behind} of {n_hw} hardware challengers trail NVIDIA on serving software; "
               "TPU leads on cost, SRAM chips on speed"),
        subtitle=("Repo verdict vs NVIDIA (GB300 / Vera Rubin NVL72 with Dynamo and TensorRT-LLM) on five inference "
                  "dimensions; cell = verdict letter + key fact"),
        alt=(f"Heatmap of eight inference challengers on five dimensions. Open-source serving (vLLM, SGLang, llm-d) is at "
             "parity on speed, cost and maturity and leads on model coverage and hardware breadth (seven hardware "
             f"families). Google TPU leads on throughput per dollar ({tpu_cost.cell_label}); Cerebras and Groq lead on "
             "tokens per second per user thanks to on-chip SRAM but trail on cost; AMD is at parity on cost and model "
             f"coverage but behind on interactivity and software; {sw_behind} of {n_hw} hardware challengers are behind "
             "on software maturity; AWS, Microsoft and Qualcomm lack public benchmarks and are mostly 'different "
             "approach' or 'behind'."),
        data=[VERD], chapters=["11", "15"], source="repo analysis of benchmarks and vendor data (l11_inference_verdicts.csv)",
        source_ids=sources_of(df), note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=12.8, height=7.6)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {_wrap(str(r.cell_label), 21)}", ha="center",
                    va="center", fontsize=8.1, color=INK["title"],
                    fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" per ", "\nper ").replace(" maturity", "\nmaturity").replace(" coverage", "\ncoverage")
                        .replace(" flexibility", "\nflexibility") for d in dims], fontsize=9.2)
    ax.xaxis.tick_top()
    prod = df.drop_duplicates("competitor").set_index("competitor").product_basis
    ax.set_yticks(np.arange(len(comps)) + 0.5)
    ax.set_yticklabels([f"{cmp}\n{prod[cmp]}" for cmp in comps], fontsize=8.4)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.2, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.08)


# --------------------------------------------------------------------------------------
# 2. Inference silicon: memory capacity vs bandwidth (SRAM vs HBM vs LPDDR)
# --------------------------------------------------------------------------------------
NV_PICK = {"H100 SXM": "H100", "H200 SXM": "H200", "B200 (HGX)": "B200", "B300 (HGX)": "B300",
           "Rubin (VR200, per GPU)": "Rubin", "Rubin Ultra (per GPU)": "Rubin Ultra (Est.)",
           "Groq 3 LPU (LP30)": "Groq 3 LPU (LP30)"}
COMP_PICK = {"Instinct MI355X": "MI355X", "Instinct MI455X": "MI455X", "TPU v7 Ironwood": "Ironwood",
             "Trainium3": "Trainium3", "Inferentia2": "Inferentia2", "Maia 200": "Maia 200",
             "WSE-3 (CS-3)": "Cerebras WSE-3", "LPU v1 (GroqChip)": "Groq LPU v1", "Corsair": "d-Matrix Corsair (SRAM tier)",
             "Blackhole p150": "Tenstorrent Blackhole", "Cloud AI 100 Ultra": "Qualcomm AI 100 Ultra",
             "AI200": "Qualcomm AI200"}


def _silicon_frame() -> pd.DataFrame:
    g = load(GPU)
    g = g[g["product"].isin(NV_PICK)].copy()
    g["label"] = g["product"].map(NV_PICK)
    g["vendor"] = "NVIDIA"
    g["future"] = g.status.isin(["roadmap", "announced"]) | g.confidence.eq("estimate")
    k = load(COMP)
    k = k[k["product"].isin(COMP_PICK)].copy()
    k["label"] = k["product"].map(COMP_PICK)
    k["future"] = k.status.isin(["roadmap", "announced"]) & ~k["product"].eq("Instinct MI455X")
    cols = ["vendor", "label", "memory_capacity_gb", "memory_bandwidth_tbs", "future", "source_id"]
    return pd.concat([g[cols], k[cols]], ignore_index=True)


@register
def inference_memory_tradeoff():
    d = _silicon_frame()
    d["sweeps"] = d.memory_bandwidth_tbs * 1000 / d.memory_capacity_gb
    lp = d[d.label.eq("Groq 3 LPU (LP30)")].iloc[0]
    rb = d[d.label.eq("Rubin")].iloc[0]
    qc = d[d.label.eq("Qualcomm AI200")].iloc[0]
    au = d[d.label.eq("Qualcomm AI 100 Ultra")].iloc[0]
    mx = d[d.label.eq("MI455X")].iloc[0]  # QA 2026-11-05: 23.3 TB/s (S90093), was hard-coded 19.6
    c = Chart(
        id="11-inference-memory-tradeoff",
        title=(f"An LPU re-reads its {lp.memory_capacity_gb:g} GB of SRAM ~{lp.sweeps:,.0f}×/s; "
               f"Rubin re-reads {rb.memory_capacity_gb:.0f} GB of HBM4 ~{rb.sweeps:.0f}×/s"),
        subtitle=("Memory capacity (GB) vs bandwidth (TB/s) per chip or card; diagonals = full memory reads per second, "
                  "the decode-step ceiling"),
        alt=(f"Log-log scatter of inference chips by memory capacity and bandwidth. SRAM designs sit top-left: NVIDIA's "
             f"Groq 3 LPU holds {lp.memory_capacity_gb:g} GB at {lp.memory_bandwidth_tbs:.0f} TB/s (~{lp.sweeps:,.0f} full "
             "reads per second), Groq LPU v1 0.23 GB at 80 TB/s, d-Matrix Corsair 2 GB at 150 TB/s and Cerebras WSE-3 "
             "44 GB at 21,000 TB/s. HBM GPUs and cloud ASICs cluster in the middle at 80-432 GB and 3-23 TB/s (25-70 reads "
             f"per second): Rubin {rb.memory_capacity_gb:.0f} GB at {rb.memory_bandwidth_tbs:g} TB/s, MI455X 432 GB at "
             f"{mx.memory_bandwidth_tbs:g} TB/s, Ironwood 192 GB at 7.4 TB/s, Maia 200 216 GB at 7 TB/s. LPDDR cards sit bottom-right: Qualcomm "
             f"AI 100 Ultra {au.memory_capacity_gb:.0f} GB at {au.memory_bandwidth_tbs:g} TB/s (~{au.sweeps:.0f} reads per "
             f"second) and the AI200 with {qc.memory_capacity_gb:.0f} GB per card (bandwidth not disclosed)."),
        data=[GPU, COMP], chapters=["11", "15", "03", "02"], source="vendor specifications",
        source_ids=sources_of(d), note="Hollow = roadmap / Est.",
    )
    fig, ax = c.figure(width=11.0, height=6.9)
    xs = np.logspace(-1, 3.5, 50)
    label_x = {10: 1500, 100: 1500, 1e3: 20, 1e4: 3, 1e5: 8, 1e6: 1.5}
    for s_, xl in label_x.items():
        ax.plot(xs, s_ * xs / 1000, color=INK["grid"], lw=1.0, zorder=1)
        ax.text(xl, s_ * xl / 1000 * 1.12, f"{s_:,.0f}×/s", fontsize=7.8, color=INK["muted"], rotation=22,
                ha="center", va="bottom")
    local = {"H100": (-14, -14), "B200": (-30, 8), "Rubin": (-38, 6), "MI455X": (8, 0), "Rubin Ultra (Est.)": (6, 6),
             "Groq 3 LPU (LP30)": (8, 6), "Cerebras WSE-3": (8, -4), "Groq LPU v1": (8, -10),
             "d-Matrix Corsair (SRAM tier)": (8, -2), "Tenstorrent Blackhole": (-118, -10), "Inferentia2": (8, -4),
             "Qualcomm AI 100 Ultra": (8, 8)}
    leader = {"H200": (45, 8.0, "right"), "Trainium3": (45, 4.3, "right"), "B300 (= MI355X)": (650, 4.6, "left"),
              "Ironwood": (650, 2.9, "left"), "Maia 200": (650, 1.85, "left")}
    for r in d.itertuples():
        if pd.isna(r.memory_bandwidth_tbs):
            continue
        col = NV if r.vendor == "NVIDIA" else (STARTUP if entity_color(r.vendor) == entity_color("other")
                                               else entity_color(r.vendor))
        mk = "D" if "LPU" in r.label or "LP30" in r.label else "o"
        size = 150 if r.label == "MI355X" else 80
        ax.scatter(r.memory_capacity_gb, r.memory_bandwidth_tbs, s=size, marker=mk, zorder=4 if r.label != "B300" else 5,
                   facecolor="#FFFFFF" if r.future else col, edgecolor=col, linewidth=2)
        bold = "bold" if r.vendor == "NVIDIA" else "normal"
        ink = INK["title"] if r.vendor == "NVIDIA" else INK["text"]
        name = "B300 (= MI355X)" if r.label == "B300" else r.label
        if r.label == "MI355X":
            continue
        if name in leader:
            tx, ty, ha = leader[name]
            ax.annotate(name, (r.memory_capacity_gb, r.memory_bandwidth_tbs), xytext=(tx, ty), textcoords="data",
                        fontsize=8.2, color=ink, fontweight=bold, ha=ha, va="center",
                        arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.7, shrinkA=2, shrinkB=4))
            continue
        dx, dy = local.get(r.label, (8, 2))
        ax.annotate(r.label, (r.memory_capacity_gb, r.memory_bandwidth_tbs), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8.2, color=ink, fontweight=bold)
    # Qualcomm AI200: capacity known, bandwidth not disclosed -> marker on the floor of the chart
    qcol = entity_color("qualcomm")
    ax.scatter(qc.memory_capacity_gb, 0.3, s=90, marker="^", facecolor="#FFFFFF", edgecolor=qcol, linewidth=2, zorder=4,
               clip_on=False)
    ax.annotate("Qualcomm AI200: 768 GB/card, bandwidth n/a", (qc.memory_capacity_gb, 0.3), xytext=(-10, 1),
                textcoords="offset points", fontsize=8.2, color=INK["text"], ha="right", va="center")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.12, 3000)
    ax.set_ylim(0.25, 60000)
    ax.grid(axis="both", color=INK["grid"], lw=0.5)
    handles = [Line2D([], [], marker="o", ls="", color=NV, markersize=8, label="NVIDIA"),
               Line2D([], [], marker="o", ls="", color=entity_color("AMD"), markersize=8, label="AMD"),
               Line2D([], [], marker="o", ls="", color=entity_color("google"), markersize=8, label="Google"),
               Line2D([], [], marker="o", ls="", color=entity_color("aws"), markersize=8, label="AWS"),
               Line2D([], [], marker="o", ls="", color=entity_color("microsoft"), markersize=8, label="Microsoft"),
               Line2D([], [], marker="o", ls="", color=qcol, markersize=8, label="Qualcomm"),
               Line2D([], [], marker="o", ls="", color=STARTUP, markersize=8, label="Start-ups"),
               Line2D([], [], marker="D", ls="", color=INK["text"], markersize=7, label="LPU (SRAM)")]
    ax.legend(handles=handles, loc="upper left", fontsize=8.4, ncol=2)
    c.save(fig, ax, xlabel="Memory capacity per chip or card, GB", ylabel="Memory bandwidth, TB/s", logx=True,
           logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 3. HBM bandwidth per chip by vendor and year (spec progression)
# --------------------------------------------------------------------------------------
SERIES = {
    "NVIDIA": ["A100 SXM 80GB", "H100 SXM", "B200 (HGX)", "B300 (HGX)", "Rubin (VR200, per GPU)", "Rubin Ultra (per GPU)"],
    "AMD": ["Instinct MI250X", "Instinct MI300X", "Instinct MI325X", "Instinct MI355X", "Instinct MI455X"],
    "Google": ["TPU v4", "TPU v5p", "TPU v7 Ironwood"],
    "AWS": ["Trainium (Trn1)", "Trainium2", "Trainium3", "Trainium4"],
    "Microsoft": ["Maia 100", "Maia 200"],
    "Huawei": ["Ascend 910B", "Ascend 910C", "Ascend 950DT", "Ascend 960", "Ascend 970"],
    "Qualcomm": ["Cloud AI 100 Ultra"],
}
SHORT = {"A100 SXM 80GB": "A100", "H100 SXM": "H100", "B200 (HGX)": "B200", "B300 (HGX)": "B300",
         "Rubin (VR200, per GPU)": "Rubin", "Rubin Ultra (per GPU)": "Rubin Ultra", "Instinct MI455X": "MI455X",
         "TPU v7 Ironwood": "Ironwood", "Trainium4": "Trn4", "Maia 200": "Maia 200", "Ascend 970": "Ascend 970",
         "Cloud AI 100 Ultra": "AI 100 Ultra"}


def _bw_frame() -> pd.DataFrame:
    g = load(GPU)
    g["year"] = pd.to_numeric(g.ship_date.astype(str).str[:4], errors="coerce")
    g["vendor"] = "NVIDIA"
    g["future"] = g.status.isin(["roadmap"]) | g.confidence.eq("estimate")
    k = load(COMP)
    k["future"] = k.status.isin(["roadmap"]) | k.confidence.eq("estimate")
    rows = []
    for vendor, prods in SERIES.items():
        src = g if vendor == "NVIDIA" else k
        for p in prods:
            r = src[src["product"].eq(p)].iloc[0]
            rows.append(dict(vendor=vendor, product=p, year=int(r.year), bw=float(r.memory_bandwidth_tbs),
                             future=bool(r.future), source_id=r.source_id))
    return pd.DataFrame(rows)


@register
def decode_bandwidth_by_vendor():
    d = _bw_frame()
    rub = d[d["product"].eq("Rubin (VR200, per GPU)")].bw.item()
    mi = d[d["product"].eq("Instinct MI455X")].bw.item()
    asic = d[d.vendor.isin(["Google", "Microsoft"]) & ~d.future].bw.max()
    c = Chart(
        id="11-decode-bandwidth-by-vendor",
        # QA 2026-11-05: MI455X corrected 19.6 -> 23.3 TB/s (S90093); it now leads Rubin rather than matching it
        title=(f"MI455X leads Rubin on memory bandwidth ({mi:g} vs {rub:g} TB/s); cloud ASICs trail Rubin "
               f"~{rub / asic:.1f}×"),
        subtitle="Peak memory (HBM or LPDDR) bandwidth per accelerator, TB/s (log scale), by first shipment year, 2021–2028",
        alt=(f"Log-scale line chart of memory bandwidth per accelerator by vendor. NVIDIA rises from A100 (2.0 TB/s, 2021) "
             f"and H100 (3.35) to B200/B300 (8.0) and Rubin ({rub:g} TB/s after the 2026 spec revision), with Rubin Ultra "
             f"estimated at 32 TB/s in 2027. AMD tracks or leads at each step: MI300X 5.3, MI355X 8.0, MI455X {mi:g}. "
             f"Google Ironwood (7.37) and Microsoft Maia 200 (7.0) sit ~{rub / asic:.1f}x below Rubin; AWS Trainium3 is 4.9 "
             "with Trainium4 estimated near 19.6 in 2027; Huawei's Ascend roadmap reaches 14.4 TB/s in 2028; Qualcomm's "
             "LPDDR-based AI 100 Ultra is 0.55 TB/s."),
        data=[GPU, COMP], chapters=["11", "15", "03"], source="vendor specifications and roadmaps",
        source_ids=sources_of(d), note="Hollow / dashed = roadmap or Est.",
    )
    fig, ax = c.figure(width=11.0, height=6.4)
    order = ["Qualcomm", "Huawei", "Microsoft", "AWS", "Google", "AMD", "NVIDIA"]
    for vendor in order:
        s = d[d.vendor.eq(vendor)].sort_values("year")
        col = NV if vendor == "NVIDIA" else entity_color(vendor)
        act = s[~s.future]
        ax.plot(act.year, act.bw, color=col, lw=2.4 if vendor == "NVIDIA" else 2, marker="o", markersize=7,
                zorder=5 if vendor == "NVIDIA" else 3)
        if s.future.any() and len(act):
            fut = pd.concat([act.tail(1), s[s.future]])
            ax.plot(fut.year, fut.bw, color=col, lw=1.8, ls="--", zorder=2)
            ax.scatter(s[s.future].year, s[s.future].bw, s=56, facecolor="#FFFFFF", edgecolor=col, linewidth=2, zorder=4)
        last = s.iloc[-1]
        lab = f"{vendor} · {SHORT.get(last['product'], last['product'])} ({last.bw:g})"
        if vendor in ("Google", "Microsoft"):
            ty = 5.0 if vendor == "Google" else 3.4
            ax.annotate(lab, (last.year, last.bw), xytext=(2027.15, ty), textcoords="data", fontsize=8.6, color=col,
                        fontweight="bold", va="center",
                        arrowprops=dict(arrowstyle="-", color=col, lw=0.8, shrinkA=2, shrinkB=5))
            continue
        dx, dy, ha = {"AMD": (-8, 9, "right"), "NVIDIA": (6, 2, "left"), "AWS": (6, -9, "left"),
                      "Huawei": (6, 0, "left"), "Qualcomm": (6, 0, "left")}[vendor]
        ax.annotate(lab, (last.year, last.bw), xytext=(dx, dy), textcoords="offset points", fontsize=8.6, color=col,
                    fontweight="bold", va="center", ha=ha)
    ax.set_yscale("log")
    ax.set_ylim(0.4, 50)
    ax.set_xlim(2020.6, 2029.6)
    ax.set_xticks(range(2021, 2029))
    c.save(fig, ax, xlabel="First shipment year (roadmap years per vendor)", ylabel="Memory bandwidth per chip, TB/s",
           logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 4. Inference-related deal values
# --------------------------------------------------------------------------------------
@register
def inference_deal_values():
    d = load(DEALS).copy()
    d["year"] = d.announce_date.astype(str).str[:4]
    d["label"] = d.apply(lambda r: f"{r.target} ← {r.acquirer} ({r.year})", axis=1)
    d = d.sort_values("announce_date").iloc[::-1].reset_index(drop=True)  # oldest at top (y=0 is the bottom row)
    groq = d[d.target.str.startswith("Groq")].value_usd_m.item()
    hf = d[d.target.eq("Hugging Face")].value_usd_m.item()
    mod = d[d.target.eq("Modular")].value_usd_m.item()
    silo = d[d.target.eq("Silo AI")].value_usd_m.item()
    n_und = int(d.value_usd_m.isna().sum())
    c = Chart(
        id="11-inference-deal-values",
        title=(f"NVIDIA's ~${groq / 1000:.0f}B Groq and ${hf / 1000:.1f}B Hugging Face deals dwarf "
               f"Qualcomm–Modular (${mod / 1000:.1f}B)"),
        subtitle="Disclosed or reported deal value, US$ millions (log scale), inference software and silicon deals 2023–2026",
        alt=(f"Log-scale horizontal bar chart of inference-related deals. NVIDIA: Groq licence and team (~${groq:,.0f}M "
             f"reported, Dec 2025), Hugging Face (${hf:,.0f}M announced Sep 2026, pending, close expected H1 2027), "
             "Run:ai (~$700M, 2024), CentML (up to ~$400M incl. earn-outs, 2025), Deci (~$300M, 2024), "
             f"OctoAI (~$250M, 2024). Qualcomm: Modular (${mod:,.0f}M, 2026). AMD: Silo AI (${silo:,.0f}M, 2024) plus "
             "undisclosed Nod.ai, Brium, the Untether AI team and MK1. Intel's ~$1.6B SambaNova talks did not complete; "
             f"Red Hat's Neural Magic purchase was undisclosed ({n_und} deals in total without a price)."),
        data=[DEALS], chapters=["11", "13", "09"], source="releases and press", source_ids=sources_of(d),
        note="Hatched = reported / pending",
    )
    fig, ax = c.figure(width=10.8, height=6.6)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = _vcolor(r.acquirer)
        if pd.isna(r.value_usd_m):
            ax.text(55, yi, "undisclosed", va="center", fontsize=8.8, color=INK["muted"], style="italic")
            continue
        bar = ax.barh(yi, r.value_usd_m, color=col, height=0.62)
        if r.value_basis in ("reported", "up-to") or r.status not in ("closed",):
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_alpha(0.8)
        v = r.value_usd_m
        txt = f"${v / 1000:.1f}B" if v >= 1000 else f"${v:,.0f}M"
        if r.value_basis == "reported":
            txt = "~" + txt
        if r.value_basis == "up-to":
            txt = "up to " + txt
        if r.status == "pending":
            txt += " (pending)"
        elif r.status != "closed":
            txt += " (talks)"
        ax.text(v * 1.12, yi, txt, va="center", fontsize=9, color=INK["title"])
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label)
    ax.set_ylim(-0.7, len(d) - 0.4)
    ax.set_xscale("log")
    ax.set_xlim(50, 90000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=entity_color("AMD"), label="AMD"),
               Patch(color=entity_color("qualcomm"), label="Qualcomm"), Patch(color=entity_color("intel"), label="Intel"),
               Patch(color=entity_color("other"), label="Red Hat (IBM)")]
    ax.legend(handles=handles, loc="upper right", fontsize=8.6)
    _margins(fig, left=0.33, right=0.97)
    c.save(fig, ax, xlabel="Deal value, US$ millions (log scale)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 5. API token prices over time: flagship vs small vs capability floor
# --------------------------------------------------------------------------------------
@register
def api_token_price_trend():
    p = load(PRICES).copy()
    p["t"] = pd.to_datetime(p.date.astype(str).str.slice(0, 7) + "-15")
    p.loc[p.date.astype(str).str.len() == 10, "t"] = pd.to_datetime(p.date[p.date.astype(str).str.len() == 10])
    floor = p[p.tier.eq("capability floor")].sort_values("t")
    flag = p[p.tier.eq("flagship")].sort_values("t")
    small = p[p.tier.eq("small")].sort_values("t")
    f_ratio = floor.blended_3to1_usd_per_m.iloc[0] / floor.blended_3to1_usd_per_m.iloc[-1]
    g4 = flag[flag.model.str.startswith("GPT-4 (8K)")].blended_3to1_usd_per_m.item()
    g5 = flag[flag.model.eq("GPT-5")].blended_3to1_usd_per_m.item()
    g55 = flag[flag.model.eq("GPT-5.5")].blended_3to1_usd_per_m.item()
    c = Chart(
        id="11-api-token-price-trend",
        title=(f"GPT-3.5-level tokens fell ~{f_ratio:.0f}× in 2 years, but OpenAI's flagship rose "
               f"{g55 / g5:.1f}× in 2026"),
        subtitle=("API list price, US$ per million tokens, blended 3:1 input:output; OpenAI tiers vs the cheapest "
                  "GPT-3.5-level model"),
        alt=(f"Log-scale chart of API prices per million tokens. The cheapest model at GPT-3.5-level quality fell from $20 "
             f"(Nov 2022) to $0.07 (Oct 2024), ~{f_ratio:.0f}x. OpenAI's flagship fell from GPT-4 at ${g4:.2f} blended "
             f"(Mar 2023) through GPT-4 Turbo ($15), GPT-4o ($7.50, then $4.38) to GPT-5 at ${g5:.2f} (Aug 2025), "
             f"~{g4 / g5:.0f}x cheaper, then GPT-5.5 launched at ${g55:.2f} (Apr 2026, reported), {g55 / g5:.1f}x GPT-5. "
             "OpenAI's small tier fell from gpt-3.5-turbo at $2.00 (2023) to GPT-4o mini ($0.26) and GPT-5 nano ($0.14)."),
        data=[PRICES], chapters=["11", "14", "P2"], source="OpenAI posts, AI Index 2025, press",
        source_ids=sources_of(p), note="Blended = (3 × in + out) / 4",
    )
    fig, ax = c.figure(width=11.0, height=6.2)
    blue, light = SEQ_BLUE[6], SEQ_BLUE[3]
    ax.plot(flag.t, flag.blended_3to1_usd_per_m, color=blue, marker="o", markersize=8, lw=2.2, drawstyle="steps-post",
            label="OpenAI flagship (list)")
    ax.plot(small.t, small.blended_3to1_usd_per_m, color=light, marker="s", markersize=8, lw=2, drawstyle="steps-post",
            label="OpenAI small tier (list)")
    ax.plot(floor.t, floor.blended_3to1_usd_per_m, color=INK["text"], marker="^", markersize=9, lw=1.8, ls="--",
            label="Cheapest at GPT-3.5-level quality (AI Index)")
    rep = flag[flag.confidence.eq("reported")]
    ax.scatter(rep.t, rep.blended_3to1_usd_per_m, s=90, facecolor="#FFFFFF", edgecolor=blue, linewidth=2, zorder=5)
    off = {"GPT-4 (8K)": (6, 6), "GPT-4 Turbo": (6, 6), "GPT-4o": (6, 6), "GPT-4o (2024-08-06)": (6, -12),
           "GPT-5": (6, -12), "GPT-5.5": (-60, 8), "gpt-3.5-turbo": (6, 6), "gpt-3.5-turbo-0125": (6, 6),
           "GPT-4o mini": (6, 6), "GPT-5 nano": (6, -12)}
    for r in pd.concat([flag, small]).itertuples():
        name = r.model.replace(" (2024-08-06)", " (Aug)").replace("-0125", " (Jan 24)")
        dx, dy = off.get(r.model, (6, 6))
        ax.annotate(f"{name} ${r.blended_3to1_usd_per_m:,.2f}", (r.t, r.blended_3to1_usd_per_m), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8.2, color=INK["title"])
    for r, xy in zip(floor.itertuples(), [(-26, -4), (9, -3)]):
        ax.annotate(f"${r.blended_3to1_usd_per_m:g}", (r.t, r.blended_3to1_usd_per_m), xytext=xy,
                    textcoords="offset points", fontsize=8.2, color=INK["text"])
    ax.set_yscale("log")
    ax.set_ylim(0.04, 80)
    ax.set_xlim(pd.Timestamp("2022-09-01"), pd.Timestamp("2026-10-31"))
    ax.legend(loc="lower left", fontsize=8.8)
    c.save(fig, ax, xlabel="Price effective date", ylabel="US$ per million tokens, blended", logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 6. Valuations of inference start-ups (serving software/clouds vs silicon)
# --------------------------------------------------------------------------------------
@register
def inference_startup_valuations():
    v = load(PRIV).copy()
    seg_order = ["inference cloud", "serving engine", "inference silicon"]
    names = {"inference cloud": "Inference clouds", "serving engine": "Serving engines and software",
             "inference silicon": "Inference silicon"}
    fw = v[v.company.eq("Fireworks AI")].valuation_usd_m.item()
    tg = v[v.company.eq("Together AI")].valuation_usd_m.item()
    et = v[v.company.eq("Etched")].valuation_usd_m.item()
    cb = v[v.company.eq("Cerebras")].valuation_usd_m.item()
    c = Chart(
        id="11-inference-startup-valuations",
        title=(f"Inference clouds price like chip start-ups: Fireworks ~${fw / 1000:.0f}B vs Etched ${et / 1000:.1f}B"),
        subtitle="Last disclosed or reported valuation, US$ millions (log scale); Cerebras at IPO pricing; acquisitions at deal price",
        alt=(f"Log-scale horizontal bar chart of inference start-up valuations. Inference clouds: Fireworks AI ~${fw:,.0f}M "
             f"(talks, May 2026), Together AI ${tg:,.0f}M (Jul 2026), Baseten $5,000M (Jan 2026), Modal ~$2,500M (talks). "
             "Serving software: Hugging Face $12,930M (NVIDIA acquisition announced Sep 2026, pending), Modular $3,900M "
             "(acquired by Qualcomm, 2026), Inferact (vLLM) $800M and RadixArk (SGLang) $400M seed valuations. "
             f"Silicon: Cerebras ~${cb:,.0f}M at its May 2026 IPO, Etched ${et:,.0f}M, Groq "
             "$6,900M before its ~$20B NVIDIA licence, Positron $5,000M, Tenstorrent ~$2,700M, d-Matrix $2,000M, "
             "SambaNova ~$1,600M (Intel offer talks); MatX and FuriosaAI valuations undisclosed."),
        data=[PRIV], chapters=["11", "13", "15"], source="company announcements and press",
        source_ids=sources_of(v), note="Hatched = talks / offer",
    )
    fig, ax = c.figure(width=10.8, height=7.6)
    ypos, labels, ticks = [], [], []
    y = 0.0
    headers = []
    for seg in seg_order:
        g = v[v.segment.eq(seg)].sort_values("valuation_usd_m", ascending=False, na_position="last")
        headers.append((y, names[seg]))
        y += 1.0
        for r in g.itertuples():
            ypos.append((y, r))
            y += 1.0
        y += 0.3
    for yi, r in ypos:
        col = STARTUP
        if r.status == "acquired":
            col = NV if "NVIDIA" in str(r.event) else entity_color("qualcomm")
        ticks.append(yi)
        labels.append(f"{r.company} · {pd.Timestamp(str(r.date)[:7] + '-01'):%b %Y}")
        if pd.isna(r.valuation_usd_m):
            raise_txt = f"raised ${r.raise_usd_m:,.0f}M; valuation undisclosed" if not pd.isna(r.raise_usd_m) else "undisclosed"
            ax.text(110, yi, raise_txt, va="center", fontsize=8.6, color=INK["muted"], style="italic")
            continue
        bar = ax.barh(yi, r.valuation_usd_m, color=col, height=0.62)
        if "talks" in str(r.valuation_basis) or "offer" in str(r.valuation_basis):
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_alpha(0.8)
        txt = f"${r.valuation_usd_m / 1000:.1f}B" if r.valuation_usd_m >= 1000 else f"${r.valuation_usd_m:,.0f}M"
        extra = {"Groq": "  → then ~$20B NVIDIA licence", "Cerebras": "  (IPO)",
                 "Modular": "  (acquired by Qualcomm)", "Hugging Face": "  (NVIDIA deal, pending)"}.get(r.company, "")
        ax.text(r.valuation_usd_m * 1.12, yi, txt + extra, va="center", fontsize=8.8, color=INK["title"])
    for yh, name in headers:
        ax.text(105, yh, name, va="center", ha="left", fontsize=9.5, color=INK["title"], fontweight="bold")
        if yh > 0:
            ax.axhline(yh - 0.65, color=INK["base"], lw=0.8)
    ax.set_yticks(ticks, labels, fontsize=8.8)
    ax.set_ylim(y - 0.6, -0.7)
    ax.set_xscale("log")
    ax.set_xlim(100, 300000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.22, right=0.97)
    c.save(fig, ax, xlabel="Valuation, US$ millions (log scale)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 7. Value pools behind $1 of API revenue (waterfall, estimate)
# --------------------------------------------------------------------------------------
@register
def token_revenue_value_pools():
    p = load(POOLS).sort_values("step")
    lab = p[p.component.str.startswith("Model lab")].value_cents_per_usd.item()
    cloud = p[p.component.str.startswith("Cloud")].value_cents_per_usd.item()
    nvgp = p[p.component.eq("NVIDIA gross profit")].value_cents_per_usd.item()
    c = Chart(
        id="11-token-revenue-value-pools",
        title=(f"Est.: of $1 of API revenue the lab keeps ~{lab:.0f}¢, the cloud ~{cloud:.0f}¢, NVIDIA ~{nvgp:.0f}¢ "
               "of gross profit"),
        subtitle="Split of $1.00 of closed-model API revenue served on rented GB300 NVL72 capacity, US cents (repo estimate)",
        alt=(f"Waterfall chart splitting $1.00 of API revenue: the model lab's compute margin leaves ~{lab:.0f} cents of gross "
             f"profit (reported ~70% for OpenAI, Oct 2025); the remaining 30 cents of compute splits into the cloud operator's "
             f"gross margin (~{cloud:.0f} cents, from rental $5.00 vs owner TCO $2.31 per GB300 GPU-hour), electricity "
             "(~2 cents), facility, operations and financing (~3 cents), other IT hardware (~2 cents), NVIDIA's cost of "
             f"goods (~2 cents) and NVIDIA's gross profit (~{nvgp:.0f} cents). The lab's share must still fund training "
             "compute and R&D, much of which also flows to NVIDIA."),
        data=[POOLS], chapters=["11", "14", "13"], source="repo estimate on reported margins and TCO",
        source_ids=sources_of(p), note="Hatched = Est.",
    )
    fig, ax = c.figure(width=11.0, height=6.2)
    colors = [SEQ_BLUE[7], SEQ_BLUE[5], SEQ_BLUE[3], SEQ_BLUE[1], "#B5B5B5", GEN_PAST, NV]
    ax.bar(0, 100, color=INK["text"], width=0.62)
    ax.text(0, 101.5, "$1.00", ha="center", fontsize=9.5, color=INK["title"], fontweight="bold")
    top = 100.0
    for i, (r, col) in enumerate(zip(p.itertuples(), colors), start=1):
        bottom = top - r.value_cents_per_usd
        b = ax.bar(i, r.value_cents_per_usd, bottom=bottom, color=col, width=0.62, edgecolor="#FFFFFF")
        if r.confidence == "estimate":
            b.patches[0].set_hatch("///")
        ax.plot([i - 0.69, i - 0.31], [top, top], color=INK["base"], lw=1)
        ax.text(i, top + 1.5, f"{r.value_cents_per_usd:.1f}¢", ha="center", fontsize=9.2, color=INK["title"],
                fontweight="bold" if "NVIDIA gross" in r.component else "normal")
        top = bottom
    names = ["API revenue", "Model lab\ngross profit", "Cloud operator\ngross margin", "Electricity",
             "Facility, ops,\nfinancing", "Other IT\nhardware", "NVIDIA COGS\n(TSMC, HBM)", "NVIDIA\ngross profit"]
    ax.set_xticks(range(len(names)), names, fontsize=8.8)
    ax.set_axisbelow(True)
    ax.set_ylim(0, 112)
    ax.set_xlim(-0.6, len(names) - 0.4)
    c.save(fig, ax, ylabel="US cents per $1.00 of API revenue", legend=False, bottom=0.17)
