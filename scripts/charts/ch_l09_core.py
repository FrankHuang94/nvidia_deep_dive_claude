"""Layer 09 (CUDA and system software) - CORE charts: attention-kernel efficiency by GPU generation,
the engineering effort to port one attention kernel, DeepSeek-V4-Pro day-0 readiness by platform,
AMD MI355X bring-up of DeepSeek-V4-Pro, and CUDA moat strength by customer segment.

Data (owned by the layer-09 CORE author, documented in data/README.md):
data/l09_kernel_efficiency.csv, data/l09_port_effort.csv, data/l09_dsv4_bringup.csv,
data/l09_moat_by_segment.csv.
"""
from __future__ import annotations

import matplotlib.patches as mpatches
import numpy as np

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

CH = ["09"]


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


# --------------------------------------------------------------------------------------
# 1. Attention-kernel efficiency by GPU generation
# --------------------------------------------------------------------------------------
@register
def l09_attention_kernel_efficiency():
    d = load("l09_kernel_efficiency.csv")
    d = d[~d.kernel.str.contains("FP8")].reset_index(drop=True)
    c = Chart(
        id="09-attention-kernel-efficiency",
        title="Attention kernels need a rewrite per GPU: FA2 hit 73% of A100 peak, 35% of H100's",
        subtitle="Share of dense 16-bit peak reached by FlashAttention kernels, by GPU (%); "
                 "FA3 restored 75% on H100 and FA4 reaches 71% on B200",
        alt=("Bar chart of attention-kernel utilization: FlashAttention-1 reached 25-40% of A100 peak (2022) and "
             "FlashAttention-2 50-73% of A100 peak (2023), but the same FA2 code reached only 35% of H100 peak until "
             "the Hopper-specific FlashAttention-3 hit 75% (740 TFLOPS FP16); FlashAttention-4, written in CuTe DSL "
             "for Blackwell, reaches 71% of B200 BF16 peak (1,613 TFLOPS) and up to 2.7x Triton."),
        data=["l09_kernel_efficiency.csv"], chapters=["09", "10", "02"],
        source="FlashAttention papers; GPU datasheets", source_ids=sources_of(d),
    )
    fig, ax = c.figure(10.5, 5.8)
    labels = [f"{r.kernel}\non {r.hardware} ({r.kernel_year})" for r in d.itertuples()]
    x = np.arange(len(d))
    hi = d.utilization_high_pct.values
    lo = d.utilization_low_pct.values
    colors = []
    for r in d.itertuples():
        if r.kernel_matches_gpu == "no":
            colors.append("#B5B5B5")
        elif r.architecture == "Ampere":
            colors.append(GEN_PAST)
        else:
            colors.append(NV)
    bars = ax.bar(x, hi, width=0.62, color=colors, edgecolor="white", zorder=3)
    for i, (l, h) in enumerate(zip(lo, hi)):
        if l != h:
            ax.plot([i, i], [l, h], color=INK["title"], lw=1.6, zorder=4)
            ax.plot([i - 0.08, i + 0.08], [l, l], color=INK["title"], lw=1.6, zorder=4)
            ax.text(i, h + 1.5, f"{l:.0f}-{h:.0f}%", ha="center", va="bottom", fontsize=9.5,
                    color=INK["title"], fontweight="bold")
        else:
            ax.text(i, h + 1.5, f"{h:.0f}%", ha="center", va="bottom", fontsize=9.5,
                    color=INK["title"], fontweight="bold")
    for i, r in enumerate(d.itertuples()):
        if r.achieved_tflops == r.achieved_tflops and r.achieved_tflops:  # not NaN
            ax.text(i, 6, f"{r.achieved_tflops:,.0f}\nTFLOPS", ha="center", va="bottom", fontsize=8,
                    color="#FFFFFF" if colors[i] == NV else INK["title"])
    ax.text(2, 20, "same FA2 code\non a new GPU", ha="center", va="center", fontsize=8.8, color=INK["title"])
    ax.text(-0.5, 96, "Grey = previous-generation kernel on a new GPU · whiskers = published range",
            ha="left", va="top", fontsize=8.6, color=INK["text"])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.6)
    ax.set_ylim(0, 100)
    ax.set_xlim(-0.6, len(d) - 0.4)
    c.save(fig, ax, ylabel="% of dense 16-bit peak FLOPS", legend=False, bottom=0.2)


# --------------------------------------------------------------------------------------
# 2. Engineering effort to port one attention kernel (estimate)
# --------------------------------------------------------------------------------------
@register
def l09_attention_kernel_port_effort():
    d = load("l09_port_effort.csv").sort_values("order")
    lo_tot, hi_tot = d.low_engineer_months.sum(), d.high_engineer_months.sum()
    c = Chart(
        id="09-attention-kernel-port-effort",
        title=(f"Est.: porting one attention kernel to a new chip takes ~{lo_tot / 12:.1f}-"
               f"{hi_tot / 12:.1f} engineer-years"),
        subtitle="Engineer-months per phase (low-high) for experienced kernel engineers; hatched = speculative "
                 "repo estimate; dark = tuning work",
        alt=(f"Horizontal range chart of estimated engineer-months to port one FlashAttention-class kernel to a new "
             f"accelerator: functional forward port 1-3, backward pass and numerics 2-6, performance tuning to about "
             f"70% of peak 6-18, feature variants 6-18, framework integration and packaging 3-9, plus 3-12 per year "
             f"to re-tune for each new chip generation - {lo_tot}-{hi_tot} engineer-months in total, about "
             f"{lo_tot / 12:.1f}-{hi_tot / 12:.1f} engineer-years (speculative repo estimate)."),
        data=["l09_port_effort.csv"], chapters=["09", "15", "19"],
        source="repo estimate; FlashAttention, InferenceX evidence",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(10.5, 5.6)
    y = np.arange(len(d))[::-1]
    for yi, r in zip(y, d.itertuples()):
        tuning = r.order in (3, 4)
        col = NV if tuning else GEN_PAST
        b = ax.barh(yi, r.high_engineer_months - r.low_engineer_months, left=r.low_engineer_months,
                    height=0.55, color=col, edgecolor=NV_DARK, lw=0.8, zorder=3)
        for p in b.patches:
            p.set_hatch("///")
        ax.text(r.high_engineer_months + 0.4, yi, f"{r.low_engineer_months:.0f}-{r.high_engineer_months:.0f}",
                va="center", fontsize=9.5, color=INK["title"], fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(list(d.phase), fontsize=9.2)
    ax.set_xlim(0, 22)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#E1E0D9", lw=0.6)
    ax.text(21.8, len(d) - 0.55, f"Total: {lo_tot}-{hi_tot} engineer-months\n(~{lo_tot / 12:.1f}-{hi_tot / 12:.1f} years)",
            ha="right", va="top", fontsize=10, fontweight="bold", color=NV_DARK)
    ax.set_ylim(-0.6, len(d) - 0.4)
    _left_margin(fig, 0.33)
    c.save(fig, ax, xlabel="Engineer-months (low-high range)", legend=False, bottom=0.15)


# --------------------------------------------------------------------------------------
# 3. DeepSeek-V4-Pro day-0 readiness by platform
# --------------------------------------------------------------------------------------
@register
def l09_dsv4_day0_readiness():
    d = load("l09_dsv4_bringup.csv")
    m = d[d.record_type == "milestone"].copy()
    lanes = [("NVIDIA", "NVIDIA (CUDA)"), ("Huawei", "Huawei Ascend (CANN)"), ("AMD", "AMD MI355X (ROCm)")]
    c = Chart(
        id="09-dsv4-day0-readiness",
        title="DeepSeek-V4-Pro ran on CUDA on day 0; ROCm needed 8 days for FP4, 27 for 50 tok/s/user",
        subtitle="Days after the 2026-04-24 release to each serving milestone "
                 "(open-source engines on InferenceX; Huawei per its own docs)",
        alt=("Timeline dot chart of DeepSeek-V4-Pro (released 2026-04-24) bring-up: on NVIDIA CUDA, vLLM and SGLang "
             "supported it natively on day 0, GB200 NVL72 disaggregated serving and MTP ran by day 3, and a "
             "TensorRT-LLM output-corruption bug was found on day 9; Huawei documented day-0 Ascend support; on AMD "
             "MI355X, first light on day 1 was FP8-only at 1-2 tok/s/user, FP4 worked on day 8, 50 tok/s/user on "
             "day 27, MTP around day 28, and multi-node serving still did not work at day 43."),
        data=["l09_dsv4_bringup.csv"], chapters=["09", "11", "15"],
        source="SemiAnalysis InferenceX articles", source_ids=sources_of(m),
        note="Arrow = not achieved by day 43",
    )
    fig, ax = c.figure(11, 5.8)
    ypos = {"NVIDIA": 2, "Huawei": 1, "AMD": 0}
    # (short label, vertical offset) keyed by a substring of the milestone text
    style_map = [
        ("Native support at public release", "vLLM + SGLang native", 0.22),
        ("Multi-node disaggregated", "GB200 NVL72 disaggregated serving", -0.22),
        ("First MTP", "MTP speculative decoding (SGLang)", 0.44),
        ("Hidden-size bug", "TensorRT-LLM corruption bug found", -0.44),
        ("Day-0 inference support", "day-0 support (Huawei documentation)", 0.22),
        ("First light", "FP8-only first light, 1-2 tok/s/user", 0.22),
        ("Native FP4", "native FP4 path working", -0.22),
        ("50 tok/s/user", "first point at 50 tok/s/user", 0.22),
        ("MTP working", "MTP working (~week 4)", -0.22),
        ("still not working", "no multi-node serving yet", 0.44),
    ]
    for r in m.itertuples():
        yv = ypos[r.vendor]
        col = entity_color(r.vendor)
        x = float(r.value)
        label, dy = next((lab, off) for key, lab, off in style_map if key in r.milestone)
        if "still not" in r.milestone:
            ax.annotate("", xy=(48, yv), xytext=(43.6, yv), arrowprops=dict(arrowstyle="->", color=col, lw=2))
        ax.scatter([x], [yv], s=90, color=col, edgecolor="white", lw=1.2, zorder=4)
        ax.plot([x, x], [yv, yv + dy * 0.8], color=col, lw=0.8, alpha=0.6, zorder=2)
        ax.annotate(f"Day {int(x)}: {label}", (x, yv + dy), xytext=(3, 0), textcoords="offset points",
                    fontsize=8.4, color=INK["title"], va="center", ha="left")
    for v, lab in lanes:
        ax.axhline(ypos[v], color=entity_color(v), lw=1, alpha=0.35, zorder=1)
    ax.set_yticks([ypos[v] for v, _ in lanes])
    ax.set_yticklabels([lab for _, lab in lanes], fontsize=9.6)
    for t, (v, _) in zip(ax.get_yticklabels(), lanes):
        t.set_color(entity_color(v))
        t.set_fontweight("bold")
    ax.set_xlim(-1, 62)
    ax.set_ylim(-0.7, 2.7)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#E1E0D9", lw=0.6)
    _left_margin(fig, 0.19)
    c.save(fig, ax, xlabel="Days after DeepSeek-V4-Pro release (2026-04-24)", legend=False)


# --------------------------------------------------------------------------------------
# 4. MI355X DeepSeek-V4-Pro bring-up (throughput at fixed interactivity)
# --------------------------------------------------------------------------------------
@register
def l09_dsv4_mi355x_bringup():
    d = load("l09_dsv4_bringup.csv")
    t = d[(d.record_type == "throughput") & (d.metric == "tok_s_per_gpu_at_15_tok_s_user")].copy()
    t = t.sort_values("days_after_release")
    first = t.value.dropna().iloc[0]
    last = t.value.dropna().iloc[-1]
    c = Chart(
        id="09-dsv4-mi355x-bringup",
        title=f"31 AMD pull requests lifted MI355X DeepSeek-V4-Pro throughput {last / first:.0f}x in 19 days",
        subtitle="AMD MI355X, SGLang, 8K in / 1K out, throughput per GPU at 15 tok/s per user (tok/s/GPU), "
                 "by date of InferenceX run",
        alt=(f"Bar chart of AMD MI355X DeepSeek-V4-Pro throughput at 15 tokens/s per user: unreachable on day 1 "
             f"(FP8 first light never exceeded 2.5 tok/s/user), then 104 tok/s/GPU on day 8 after FP4 was enabled, "
             f"194 on day 10, 775 on day 16 and 1,272 on day 27 after 31 optimization PRs - about {last / first:.0f}x "
             f"in 19 days, yet NVIDIA B200 on CUDA SGLang was still about 5x higher in the 15-30 tok/s/user band."),
        data=["l09_dsv4_bringup.csv"], chapters=["09", "11", "15"],
        source="SemiAnalysis InferenceX (MI355X DeepSeek-V4-Pro on SGLang)", source_ids=sources_of(t),
    )
    fig, ax = c.figure(10, 5.6)
    x = np.arange(len(t))
    vals = t.value.fillna(0).values
    bars = ax.bar(x, vals, width=0.6, color=entity_color("AMD"), edgecolor="white", zorder=3)
    for i, (r, v) in enumerate(zip(t.itertuples(), vals)):
        if v == 0:
            ax.text(i, 40, "unreachable\n(FP8 only,\n<2.5 tok/s/user)", ha="center", va="bottom", fontsize=8.5,
                    color=INK["text"])
        else:
            ax.text(i, v + 25, f"{v:,.0f}", ha="center", va="bottom", fontsize=10, fontweight="bold",
                    color=INK["title"])
    ax.set_xticks(x)
    short = {1: "FP8 first light", 8: "FP4 enabled,\nTileLang attention", 10: "fused\ncompress-decode",
             16: "AITER mHC,\nTriton SWA", 27: "SGLang 0.5.12,\nFlyDSL MoE"}
    ax.set_xticklabels([f"{r.date[5:]} (day {int(r.days_after_release)})\n{short.get(int(r.days_after_release), '')}"
                        for r in t.itertuples()], fontsize=8.4)
    ax.set_ylim(0, 1550)
    ax.text(1.5, 1420, "NVIDIA B200 on CUDA (SGLang) was still ~5x higher\nin the 15-30 tok/s/user band (SemiAnalysis)",
            ha="center", va="top", fontsize=9, color=NV_DARK, fontweight="bold")
    c.save(fig, ax, ylabel="tok/s per GPU at 15 tok/s/user", legend=False, bottom=0.2)


# --------------------------------------------------------------------------------------
# 5. CUDA moat strength by customer segment (heatmap)
# --------------------------------------------------------------------------------------
RAMP = {1: "#F0EFEC", 2: "#CDE2FB", 3: "#86B6EF", 4: "#3987E5", 5: "#104281"}


@register
def l09_moat_strength_by_segment():
    d = load("l09_moat_by_segment.csv")
    segs = list(d.sort_values("segment_order").segment.unique())
    works = list(d.sort_values("workload_order").workload.unique())
    avg = d.groupby("segment").score_1_5.mean()
    wavg = d.groupby("workload").score_1_5.mean()
    lo_seg, hi_seg = avg.idxmin(), avg.idxmax()
    c = Chart(
        id="09-moat-strength-by-segment",
        title=(f"Est.: CUDA lock-in is strongest in academia ({avg.max():.2f}/5), weakest for Chinese labs "
               f"({avg.min():.1f})"),
        subtitle="Repo scoring of switching cost off CUDA, 1 (can move within months) to 5 (prohibitive), "
                 "by customer segment and workload - speculative",
        alt=(f"Heatmap scoring CUDA lock-in from 1 to 5 for seven customer segments across four workloads. Averages: "
             f"academia {avg['Academia and research']:.2f}, enterprises {avg['Enterprises (self-hosted)']:.2f}, "
             f"sovereign AI {avg['Sovereign AI programs']:.2f}, startups and neoclouds "
             f"{avg['AI startups and neoclouds']:.2f}, hyperscalers {avg['Hyperscalers (own workloads)']:.2f}, "
             f"frontier labs {avg['Frontier labs']:.2f}, Chinese labs {avg['Chinese labs (export-constrained)']:.2f}. "
             f"Inference on popular models is the weakest column (average {wavg['Inference: popular models']:.1f}) "
             f"versus about {wavg['Frontier pre-training']:.1f} for pre-training and new architectures."),
        data=["l09_moat_by_segment.csv"], chapters=["09", "18", "19"],
        source="repo judgement; lab and benchmark disclosures", source_ids=sources_of(d),
    )
    fig = __import__("matplotlib.pyplot", fromlist=["figure"]).figure(figsize=(11, 6.6))
    ax = fig.add_axes([0.25, 0.1, 0.72, 0.68])
    cols = works + ["Average"]
    for i, s in enumerate(segs):
        yv = len(segs) - 1 - i
        for j, w in enumerate(cols):
            if w == "Average":
                v = avg[s]
                fc = RAMP[int(round(v))]
                txt = f"{v:.2f}"
            else:
                v = int(d[(d.segment == s) & (d.workload == w)].score_1_5.iloc[0])
                fc = RAMP[v]
                txt = str(v)
            x0 = j + (0.15 if w == "Average" else 0)
            ax.add_patch(mpatches.Rectangle((x0, yv), 0.96, 0.92, fc=fc, ec="white", lw=1))
            dark = (v >= 3.5)
            ax.text(x0 + 0.48, yv + 0.46, txt, ha="center", va="center", fontsize=11 if w != "Average" else 10.5,
                    fontweight="bold", color="#FFFFFF" if dark else INK["title"])
    ax.set_xlim(0, len(cols) + 0.15)
    ax.set_ylim(0, len(segs))
    ax.set_xticks([j + (0.15 if w == "Average" else 0) + 0.48 for j, w in enumerate(cols)])
    ax.set_xticklabels([w.replace(": ", ":\n").replace(" and ", " and\n") for w in cols], fontsize=8.8)
    ax.xaxis.tick_top()
    ax.set_yticks([len(segs) - 1 - i + 0.46 for i in range(len(segs))])
    ax.set_yticklabels(segs, fontsize=9.4)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    for j, w in enumerate(works):
        ax.text(j + 0.48, -0.3, f"avg {wavg[w]:.1f}", ha="center", va="center", fontsize=9, color=INK["text"],
                fontweight="bold", clip_on=False)
    c.save(fig, ax, legend=False)
    # interactive twin with the rationale on hover
    import plotly.graph_objects as go
    z, hov = [], []
    for s in segs:
        zr, hr = [], []
        for w in works:
            r = d[(d.segment == s) & (d.workload == w)].iloc[0]
            zr.append(int(r.score_1_5))
            hr.append(f"<b>{s} · {w}</b><br>Score {int(r.score_1_5)}/5<br>{r.rationale}<br>Sources: {r.source_id}")
        z.append(zr)
        hov.append(hr)
    scale = [[0, RAMP[1]], [0.25, RAMP[2]], [0.5, RAMP[3]], [0.75, RAMP[4]], [1, RAMP[5]]]
    pfig = go.Figure(go.Heatmap(z=z, x=works, y=segs, text=z, texttemplate="%{text}", hovertext=hov,
                                hoverinfo="text", colorscale=scale, zmin=1, zmax=5, xgap=3, ygap=3,
                                colorbar=dict(title="Lock-in")))
    pfig.update_yaxes(autorange="reversed")
    pfig.update_xaxes(side="top")
    c.save_plotly(pfig, height=620)
