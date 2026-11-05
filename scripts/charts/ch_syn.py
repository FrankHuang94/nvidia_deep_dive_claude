"""Synthesis (README, 00 executive summary, cheat sheet).

Charts built from:
- data/x00_layer_verdicts.csv   repo moat score, gap trend and value-capture score per layer (judgement, speculative)
- data/competitor_matrix.csv    chapter-15 rival-by-layer verdicts (counts of 'behind'/'different'/'parity'/'leads')
- data/x00_thesis_metrics.csv   one then-vs-now pair of numbers per thesis point (copied from layer/chapter data)
- data/financials.csv + data/x00_guidance.csv   quarterly GAAP gross margin and management's margin guidance

Every score in x00_layer_verdicts.csv is the repo's judgement; the charts say so in their footers.
"""
from __future__ import annotations

import textwrap

import numpy as np
import pandas as pd

from style import (DIVERGING, GEN_PAST, INK, NV, NV_DARK, VERDICT_COLORS, Chart, axis_break, entity_color, load,
                   register, sources_of)

CH = ["00"]
TREND_COLOR = {"widening": DIVERGING[0], "stable": "#9C9B96", "narrowing": DIVERGING[2]}
TREND_ARROW = {"widening": "↗", "stable": "→", "narrowing": "↘"}
SHORT = {
    "02": "02 GPU silicon", "03": "03 Memory & supply", "04": "04 CPU", "05": "05 Scale-up (NVLink)",
    "06": "06 Scale-out networking", "07": "07 DPU & SuperNIC", "08": "08 Systems & racks", "09": "09 CUDA",
    "10": "10 Libraries (CUDA-X)", "11": "11 Inference software", "12": "12 Orchestration & cloud",
    "13": "13 Ecosystem & capital",
}


def _verdicts() -> pd.DataFrame:
    d = load("x00_layer_verdicts.csv", dtype={"layer_id": str})
    d["layer_id"] = d.layer_id.str.zfill(2)
    return d


def _rival_counts() -> pd.DataFrame:
    m = load("competitor_matrix.csv")
    m = m[(m.dimension_type == "layer") & (m.competitor != "NVIDIA")].copy()
    m["layer_id"] = m.dimension.str[:2]
    out = m.pivot_table(index="layer_id", columns="verdict_vs_nvidia", values="competitor", aggfunc="count",
                        fill_value=0)
    for k in ("behind", "different", "parity", "leads"):
        if k not in out.columns:
            out[k] = 0
    out["n"] = out[["behind", "different", "parity", "leads"]].sum(axis=1)
    return out


def _inside_labels(ax, y, labels, xmin: float) -> None:
    """Draw category labels inside the axes (left of x=0), because Chart.save() fixes left=0.08 and long
    tick labels would be clipped; the left spine is hidden and a baseline drawn at x=0."""
    ax.set_yticks(y, [""] * len(y))
    for yi, lab in zip(y, labels):
        ax.text(-0.06 * (0 - xmin) / 2.4, yi, lab, ha="right", va="center", fontsize=9.5, color=INK["title"])
    ax.spines["left"].set_visible(False)
    ax.axvline(0, color=INK["base"], lw=1.0, zorder=2)


@register
def syn_moat_strength_by_layer():
    d = _verdicts()
    rc = _rival_counts()
    d = d.merge(rc[["behind", "n"]], left_on="layer_id", right_index=True, how="left")
    d = d.sort_values(["moat_score_1_5", "layer_id"], ascending=[True, False]).reset_index(drop=True)
    n_narrow = int((d.gap_trend == "narrowing").sum())
    top = d.iloc[-1]
    lows = d[d.moat_score_1_5 == d.moat_score_1_5.min()]
    c = Chart(
        id="00-moat-strength-by-layer",
        title=(f"NVIDIA's moat is deepest in libraries ({top.moat_score_1_5:.1f}/5) and shallowest in CPUs and cloud "
               f"({lows.moat_score_1_5.iloc[0]:.0f}/5); it is narrowing in {n_narrow} of 12 layers"),
        subtitle=("Repo moat score per stack layer, 1 = commoditised or behind, 5 = no rival close; colour = gap trend "
                  "over ~12 months; right column = rivals scored 'behind' NVIDIA (of 12, chapter-15 matrix)"),
        alt=("Horizontal bar chart of the repo's moat score for each of NVIDIA's twelve stack layers, coloured by gap "
             "trend. Libraries (CUDA-X) 4.5, stable; memory and supply 4.0, widening; scale-up NVLink 4.0, systems "
             "and racks 4.0 and ecosystem and capital 4.0, all narrowing; CUDA 3.5, narrowing; GPU silicon 3.0 and "
             "DPU/SuperNIC 3.0 narrowing; scale-out networking 3.0 and inference software 3.0 stable; CPU 2.0 and "
             "orchestration and cloud 2.0 stable. The gap is narrowing in 6 of 12 layers and widening only in "
             "supply. Rivals scored behind NVIDIA range from 4 of 12 (GPU silicon, cloud) to 11 of 12 (ecosystem)."),
        data=["x00_layer_verdicts.csv", "competitor_matrix.csv"],
        chapters=CH,
        source="repo synthesis (x00_layer_verdicts.csv) and ch. 15 matrix",
        source_ids=["S1500", "S15014"] + [f"S15{k:02d}" for k in range(2, 14)],
        note="Scores and trends are repo judgement (speculative)",
    )
    fig, ax = c.figure(width=11.2, height=6.6)
    y = np.arange(len(d))
    colors = [TREND_COLOR[t] for t in d.gap_trend]
    ax.barh(y, d.moat_score_1_5, color=colors, height=0.66, zorder=3)
    for yi, r in zip(y, d.itertuples()):
        ax.text(r.moat_score_1_5 + 0.06, yi, f"{r.moat_score_1_5:.1f}  {TREND_ARROW[r.gap_trend]} {r.gap_trend}",
                va="center", fontsize=9, color=INK["title"])
        ax.text(5.95, yi, f"{int(r.behind)} / {int(r.n)}", va="center", ha="center", fontsize=9, color=INK["text"])
    ax.text(5.95, len(d) - 0.35, "rivals\nbehind", ha="center", va="bottom", fontsize=8.5, color=INK["muted"])
    ax.set_xlim(-2.4, 6.4)
    _inside_labels(ax, y, [SHORT[k] for k in d.layer_id], -2.4)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.set_ylim(-0.6, len(d) - 0.1)
    ax.axvline(3, color=INK["base"], lw=0.8, ls=(0, (3, 3)), zorder=1)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    from matplotlib.patches import Patch
    handles = [Patch(color=TREND_COLOR[k], label=f"{TREND_ARROW[k]} gap {k}") for k in ("widening", "stable",
                                                                                           "narrowing")]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.62, 0.0), frameon=True, framealpha=0.95,
              edgecolor=INK["grid"])
    c.save(fig, ax, xlabel="Moat score (1–5, repo judgement)", legend=False, top=0.86)


@register
def syn_moat_vs_value_capture():
    d = _verdicts()
    c = Chart(
        id="00-moat-vs-value-capture",
        title=("The GPU (moat 3.0) is NVIDIA's profit engine; its deepest moats, libraries (4.5) and supply (4.0), "
               "earn little directly"),
        subtitle=("Repo moat score (x) vs how much of the layer's spend NVIDIA books directly as gross profit (y), "
                  "both 1–5; colour = gap trend over ~12 months"),
        alt=("Scatter chart placing NVIDIA's twelve stack layers by moat score (x, 1 to 5) and direct value capture "
             "(y, 1 to 5). Top: GPU silicon (moat 3.0, capture 5) is the profit engine; scale-up NVLink and systems "
             "(4.0, 4) and scale-out networking (3.0, 4) also earn well. Bottom right: libraries (4.5, 2), CUDA "
             "(3.5, 2) and memory and supply (4.0, 1) are deep moats that earn little directly and protect the GPU "
             "margin. Bottom left: CPU (2.0, 2) and orchestration and cloud (2.0, 1) are thin on both. Ecosystem and "
             "capital sits at 4.0, 3. All scores are repo judgement."),
        data=["x00_layer_verdicts.csv"],
        chapters=CH,
        source="repo synthesis (data/x00_layer_verdicts.csv)",
        source_ids=["S1500"] + [f"S15{k:02d}" for k in range(2, 14)],
        note="Scores are repo judgement (speculative)",
    )
    fig, ax = c.figure(width=10.6, height=6.6)
    ax.axvline(3.25, color=INK["base"], lw=0.9, zorder=1)
    ax.axhline(3.25, color=INK["base"], lw=0.9, zorder=1)
    quad = [(4.97, 5.42, "Moat and money", "right"), (1.03, 5.42, "Money, thinner moat", "left"),
            (4.97, 0.62, "Moat that protects the margin,\nearns little itself", "right"),
            (1.03, 0.62, "Thin on both", "left")]
    for qx, qy, txt, ha in quad:
        ax.text(qx, qy, txt, ha=ha, va="center", fontsize=9, color=INK["muted"], style="italic")
    offs = {"02": (8, 4), "03": (8, -2), "04": (8, 4), "05": (8, 9), "06": (8, 4), "07": (8, 4), "08": (8, -11),
            "09": (8, 4), "10": (-8, 13), "11": (-8, -13), "12": (8, 4), "13": (8, 4)}
    has = {"10": "right", "11": "right"}
    jit = {"05": -0.05, "08": 0.05}  # 05 and 08 share (4.0, 4): nudge apart so both dots show
    for r in d.itertuples():
        ax.scatter(r.moat_score_1_5 + jit.get(r.layer_id, 0.0), r.value_capture_1_5, s=150, color=TREND_COLOR[r.gap_trend], zorder=4,
                   edgecolor="#FFFFFF", linewidth=1.2)
        dx, dy = offs.get(r.layer_id, (8, 4))
        ax.annotate(SHORT[r.layer_id], (r.moat_score_1_5, r.value_capture_1_5), xytext=(dx, dy),
                    textcoords="offset points", fontsize=9, color=INK["title"], va="center",
                    ha=has.get(r.layer_id, "left"))
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=TREND_COLOR[k], markersize=10,
                      label=f"{TREND_ARROW[k]} gap {k}") for k in ("widening", "stable", "narrowing")]
    ax.legend(handles=handles, loc="center left", bbox_to_anchor=(0.0, 0.33), frameon=True, framealpha=0.95,
              edgecolor=INK["grid"])
    ax.set_xlim(0.8, 5.2)
    ax.set_ylim(0.3, 5.7)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.grid(axis="both", color=INK["grid"], lw=0.6)
    c.save(fig, ax, xlabel="Moat score (1–5, repo judgement)",
           ylabel="NVIDIA direct value capture (1–5)", legend=False, top=0.86)


@register
def syn_rival_verdicts_by_layer():
    rc = _rival_counts().sort_index(ascending=False)
    tot = rc[["behind", "different", "parity", "leads"]].sum()
    cells = int(tot.sum())
    m = load("competitor_matrix.csv")
    m = m[(m.dimension_type == "layer") & (m.competitor != "NVIDIA")]
    c = Chart(
        id="00-rival-verdicts-by-layer",
        title=(f"{int(tot.behind)} of {cells} rival-by-layer cells score 'behind' NVIDIA; rivals lead in only "
               f"{int(tot.leads)}, three of them in cloud services"),
        subtitle=("Chapter-15 verdicts for 12 rivals (AMD, Google TPU, AWS, Microsoft, Meta, Broadcom, Marvell, Intel, "
                  "Huawei, Qualcomm, Cerebras, Groq) in each NVIDIA stack layer; count of rivals per verdict"),
        alt=(f"Stacked horizontal bar chart counting, for each of NVIDIA's twelve stack layers, how many of 12 rivals "
             f"score behind, different approach, parity or leads in the chapter-15 matrix. {int(tot.behind)} of "
             f"{cells} cells are behind, {int(tot.different)} different, {int(tot.parity)} parity and "
             f"{int(tot.leads)} leads. Libraries (10 behind) and ecosystem and capital (11 behind) are the most "
             "one-sided layers; GPU silicon (4 behind, 2 parity) and orchestration and cloud (4 behind, 3 leads) "
             "are the most contested. Rivals lead in CPUs (AMD), scale-out switching (Broadcom), inference cost "
             "(Google TPU, Cerebras) and cloud services (Google, AWS, Microsoft)."),
        data=["competitor_matrix.csv"],
        chapters=CH + ["15"],
        source="ch. 15 competitor matrix (competitor_matrix.csv)",
        source_ids=["S15014"] + sources_of(m)[:20],
    )
    fig, ax = c.figure(width=11.0, height=6.4)
    y = np.arange(len(rc))
    left = np.zeros(len(rc))
    labels = {"behind": "Behind NVIDIA", "different": "Different approach", "parity": "Parity",
              "leads": "Leads NVIDIA"}
    for k in ("behind", "different", "parity", "leads"):
        vals = rc[k].values
        ax.barh(y, vals, left=left, color=VERDICT_COLORS[k], edgecolor="#FFFFFF", height=0.7, label=labels[k],
                zorder=3)
        for yi, lv, v in zip(y, left, vals):
            if v > 0:
                ax.text(lv + v / 2, yi, f"{int(v)}", ha="center", va="center", fontsize=9, color=INK["title"])
        left += vals
    ax.set_xlim(-4.6, 12)
    _inside_labels(ax, y, [SHORT[k] for k in rc.index], -4.6)
    ax.set_xticks(range(0, 13, 2))
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, frameon=False)
    # QA 2026-11-05: the count axis had no label (STYLE_GUIDE §6.3)
    c.save(fig, ax, xlabel="Number of rivals (of 12) per verdict", legend=False, top=0.86, bottom=0.22)


@register
def syn_gross_margin_path_and_guide():
    f = load("financials.csv")
    g = f[(f.metric == "gross_margin_gaap_pct") & (f.period_type == "Q")].sort_values("period_end")
    g = g[g.period.str.match(r"Q\dFY(2[5-7])")]
    gd = load("x00_guidance.csv")
    q3 = gd[(gd.period == "Q3FY27") & (gd.metric == "gross_margin_gaap_pct")].iloc[0]
    q4 = gd[(gd.period == "Q4FY27") & (gd.metric == "gross_margin_pct")].iloc[0]
    fy = gd[(gd.period == "FY2028") & (gd.metric == "gross_margin_pct")].iloc[0]
    actual = list(g.period)
    labels = actual + ["Q3FY27", "Q4FY27", "Q1FY28", "Q2FY28", "Q3FY28", "Q4FY28"]
    x = np.arange(len(labels))
    xa = x[: len(actual)]
    c = Chart(
        id="00-gross-margin-path-and-guide",
        title=(f"Gross margin is guided from {g.value.iloc[-1]:.0f}% to a {q4.low:.0f}–{q4.high:.0f}% trough in "
               f"Q4 FY2027, then {fy.low:.0f}–{fy.high:.0f}% in FY2028"),
        subtitle=("NVIDIA GAAP gross margin by fiscal quarter, % of revenue (Q1 FY2025–Q2 FY2027), with management's "
                  "guidance range for Q3 FY2027 and outlook for Q4 FY2027 and FY2028"),
        alt=("Line chart of NVIDIA's quarterly GAAP gross margin from Q1 FY2025 (78.4%) through the H20-charge "
             "quarter Q1 FY2026 (60.5%) back to 75.0% in Q2 FY2027, followed by management guidance: 74% plus or "
             "minus 0.5 points for Q3 FY2027, a 71-72% trough in Q4 FY2027 because memory costs run above plan, and "
             "72-73% for FY2028 as price increases take effect. A dashed reference line at 65% marks chapter 18's "
             "most probable bear outcome, a drift toward the mid-60s."),
        data=["financials.csv", "x00_guidance.csv"],
        chapters=CH + ["18"],
        source="NVIDIA 8-Ks; Q2 FY2027 call as reported",
        source_ids=sources_of(g) + ["S90085", "S18000", "S18027"],
        note="Hatched = guidance/outlook; axis starts at 55% (break marked)",
    )
    fig, ax = c.figure(width=11.0, height=6.0)
    ax.plot(xa, g.value.values, color=NV, lw=2.2, marker="o", ms=6, zorder=4, label="Reported GAAP gross margin")
    for xi, v, p in zip(xa, g.value.values, actual):
        if p in ("Q1FY25", "Q1FY26", "Q2FY27"):
            ax.annotate(f"{v:.1f}%", (xi, v), xytext=(0, 9 if p != "Q1FY26" else -15), textcoords="offset points",
                        ha="center", fontsize=9, color=NV_DARK, fontweight="bold")
    ax.annotate("Q1 FY2026: $4.5B H20\nexport-licence charge", (xa[actual.index("Q1FY26")], 60.5),
                xytext=(xa[actual.index("Q1FY26")] + 0.6, 57.2), fontsize=8.5, color=INK["text"])
    i3, i4 = len(actual), len(actual) + 1
    # Q3 guide: range bar + midpoint; Q4: range bar; FY2028: band over four quarters
    for xi, lo, hi in ((i3, q3.low, q3.high), (i4, q4.low, q4.high)):
        ax.bar(xi, hi - lo, bottom=lo, width=0.5, color=NV, alpha=0.55, hatch="///", edgecolor="#FFFFFF", zorder=3)
    ax.plot([xa[-1], i3, i4], [g.value.iloc[-1], (q3.low + q3.high) / 2, (q4.low + q4.high) / 2], color=NV, lw=1.6,
            ls=(0, (4, 3)), zorder=3, label="Guidance / outlook (midpoint)")
    ax.fill_between([i4 + 0.6, x[-1] + 0.4], fy.low, fy.high, color=NV, alpha=0.35, hatch="///", edgecolor="#FFFFFF",
                    lw=0, zorder=2)
    ax.text(i3, q3.high + 0.6, "Q3 guide\n74% ± 0.5", ha="center", va="bottom", fontsize=8.5, color=NV_DARK)
    ax.text(i4, q4.low - 0.6, "Q4 trough\n71–72%", ha="center", va="top", fontsize=8.5, color=NV_DARK)
    ax.text((i4 + 0.6 + x[-1] + 0.4) / 2, fy.high + 0.6, "FY2028 outlook 72–73%", ha="center", va="bottom",
            fontsize=8.5, color=NV_DARK)
    ax.axhline(65, color=entity_color("AMD"), lw=1.2, ls=(0, (5, 4)), zorder=2)
    ax.text(5.3, 65.5, "Ch. 18 most probable bear outcome: drift toward the mid-60s (repo view)", fontsize=8.5,
            color=entity_color("AMD"), va="bottom")
    ax.axvspan(len(actual) - 0.5, x[-1] + 0.5, color="#F4F3EE", zorder=0)
    ax.set_xticks(x, [f"{p[:2]}\n{p[2:].replace('FY', 'FY20')}" for p in labels], fontsize=8.6)
    ax.set_ylim(55, 81)
    ax.set_xlim(-0.6, x[-1] + 0.6)
    axis_break(ax)
    ax.legend(loc="upper right", frameon=True, framealpha=0.95, edgecolor=INK["grid"])
    c.save(fig, ax, ylabel="Gross margin (% of revenue)", legend=False, top=0.86, bottom=0.17)


@register
def syn_thesis_in_five_numbers():
    t = load("x00_thesis_metrics.csv").sort_values("thesis_no")
    c = Chart(
        id="00-thesis-in-five-numbers",
        title=("The thesis in five numbers: 20× rack throughput, 2.3× from software alone, $279B of supply, "
               "15× more stakes, and rivals still gaining"),
        subtitle="One then-vs-now pair per thesis point; each panel has its own units and scale",
        alt=("Five small bar-chart panels, one per thesis point. 1: DeepSeek-R1 tokens per second per GPU at 50 "
             "tokens/s per user rise from about 308 on H200 to about 6,261 on a GB300 NVL72 rack, about 20 times. "
             "2: software alone lifted a B200 from about 2,000 to 4,600 tokens/s per GPU between February and May "
             "2025, 2.3 times. 3: supply and capacity commitments rose from $119B to $279B in one quarter. 4: NVIDIA's "
             "private equity stakes rose from $3.4B (January 2025) to $51.2B (July 2026), about 15 times. 5: "
             "Broadcom's AI revenue rose from about 12% of NVIDIA's data-center revenue (2024-25 average) to about "
             "19% in calendar Q3 2026."),
        data=["x00_thesis_metrics.csv"],
        chapters=CH,
        source="layer and chapter data (x00_thesis_metrics.csv)",
        source_ids=sources_of(t),
    )
    fig, axes = c.figure_grid(1, 5, width=13.2, height=6.0)
    fmt = {1: "{:,.0f}", 2: "{:,.0f}", 3: "${:,.0f}B", 4: "${:,.1f}B", 5: "{:.1f}%"}
    for ax, r in zip(axes, t.itertuples()):
        after_col = entity_color("Broadcom") if r.thesis_no == 5 else NV
        before_col = "#D9D8D2" if r.thesis_no == 5 else GEN_PAST
        bars = ax.bar([0, 1], [r.before_value, r.after_value], color=[before_col, after_col], width=0.62, zorder=3)
        if r.confidence == "estimate":
            for p in bars.patches:
                p.set_hatch("///")
        top = max(r.before_value, r.after_value)
        for b, v in zip(bars.patches, [r.before_value, r.after_value]):
            ax.text(b.get_x() + b.get_width() / 2, v + top * 0.02, fmt[r.thesis_no].format(v), ha="center",
                    va="bottom", fontsize=9, color=INK["title"], fontweight="bold")
        mult = (f"+{r.after_value - r.before_value:.1f} pts" if r.thesis_no == 5
                else f"{r.after_value / r.before_value:.1f}×")
        ax.text(0.5, top * 1.17, mult, ha="center", va="bottom", fontsize=12, fontweight="bold",
                color=NV_DARK if r.thesis_no != 5 else entity_color("Broadcom"))
        ax.set_ylim(0, top * 1.38)
        ax.set_xticks([0, 1], ["\n".join(textwrap.wrap(str(r.before_label), 12)),
                               "\n".join(textwrap.wrap(str(r.after_label), 12))], fontsize=8.4)
        ax.set_title("\n".join(textwrap.wrap(f"{r.thesis_no}. {r.thesis}", 22)), fontsize=9.6, color=INK["title"],
                     fontweight="bold", loc="left", pad=8)
        ax.set_ylabel("\n".join(textwrap.wrap(f"{r.metric} ({r.unit})", 34)), fontsize=8.2)
        ax.tick_params(axis="y", labelsize=8)
    fig.subplots_adjust(wspace=0.62)
    c.save(fig, list(axes), legend=False, top=0.74, bottom=0.2)
