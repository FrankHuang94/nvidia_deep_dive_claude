"""Competitive-landscape charts (chapter 15; also 19). Owner: Phase-1 agent A6.

Data: data/competitor_matrix.csv (analyst scores 0-5 and verdicts vs NVIDIA, every row sourced).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import (Chart, INK, NV, VERDICT_COLORS, entity_color, load, register, sources_of)

DATA = "competitor_matrix.csv"
SHORT_LAYER = {"02": "Silicon", "03": "Memory &\nsupply", "04": "CPU", "05": "Scale-up", "06": "Scale-out",
               "07": "DPU /\nSuperNIC", "08": "Systems\n& racks", "09": "System\nsoftware", "10": "Libraries",
               "11": "Inference\nsoftware", "12": "Cloud &\norchestr.", "13": "Ecosystem\n& capital"}
ORDER = ["AMD", "Google TPU", "AWS Trainium", "Microsoft Maia", "Meta MTIA", "Broadcom", "Marvell", "Intel",
         "Huawei", "Qualcomm", "Cerebras", "Groq"]
LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}
VERDICT_LABEL = {"leads": "L = leads NVIDIA", "parity": "P = parity", "behind": "B = behind",
                 "different": "D = different approach"}
COLOR_KEY = {"AMD": "amd", "Google TPU": "google", "AWS Trainium": "aws", "Microsoft Maia": "microsoft",
             "Meta MTIA": "meta", "Broadcom": "broadcom", "Marvell": "marvell", "Intel": "intel", "Huawei": "huawei",
             "Qualcomm": "qualcomm", "Cerebras": "startups", "Groq": "startups"}


def _color(comp: str) -> str:
    return entity_color(COLOR_KEY.get(comp, comp))


def _margins(fig, **over):
    """Chart.save() hard-codes left/right margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


@register
def layer_competitor_heatmap():
    df = load(DATA)
    d = df[(df.dimension_type == "layer") & (df.competitor != "NVIDIA")].copy()
    layers = sorted(d.dimension.unique())
    ahead = d[d.verdict_vs_nvidia.isin(["leads", "parity"])].groupby("competitor").size().reindex(ORDER).fillna(0)
    best = ahead.idxmax()
    nbest = int(ahead.max())
    behind_share = (d.verdict_vs_nvidia == "behind").mean() * 100
    sw = d[d.dimension.str.startswith(("09", "10"))]
    sw_behind = int((sw.verdict_vs_nvidia == "behind").sum())
    c = Chart(
        id="15-layer-competitor-heatmap",
        title=f"No rival matches NVIDIA across the stack: the closest, {best}, is level or ahead in only {nbest} of 12 layers",
        subtitle="Repo verdict vs NVIDIA by stack layer (02-13) and competitor; letter = verdict, number = score 0-5 (analyst judgement, sourced)",
        alt=(f"Heatmap of 12 competitors against NVIDIA's 12 stack layers. {best} is at parity or ahead in {nbest} of 12 layers, "
             f"the most of any rival; {behind_share:.0f}% of all cells are 'behind', and {sw_behind} of {len(sw)} software and library "
             "cells are behind. Hyperscalers lead only in cloud services; Broadcom leads in Ethernet switching; Google's TPU leads on "
             "inference cost."),
        data=[DATA], chapters=["15", "19", "00"],
        source="repo analysis (competitor_matrix.csv)",
        source_ids=sources_of(d),
        note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=12.5, height=7.4)
    for i, comp in enumerate(ORDER):
        for j, lay in enumerate(layers):
            r = d[(d.competitor == comp) & (d.dimension == lay)]
            if r.empty:
                continue
            r = r.iloc[0]
            ax.add_patch(plt_rect(j, i, VERDICT_COLORS[r.verdict_vs_nvidia]))
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} {int(r.score_0_5)}", ha="center", va="center",
                    fontsize=9, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(layers))
    ax.set_ylim(len(ORDER), 0)
    ax.set_xticks(np.arange(len(layers)) + 0.5)
    ax.set_xticklabels([f"{lay[:2]}\n{SHORT_LAYER[lay[:2]]}" for lay in layers], fontsize=8.5)
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(len(ORDER)) + 0.5)
    ax.set_yticklabels(ORDER, fontsize=9.5)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.12, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.10)


def plt_rect(x, y, color):
    from matplotlib.patches import Rectangle
    return Rectangle((x + 0.03, y + 0.04), 0.94, 0.92, facecolor=color, edgecolor="#FFFFFF", linewidth=1.2)


def _radar(comps: list[str], chart_id: str, title_fn, chapters):
    df = load(DATA)
    d = df[df.dimension_type == "capability"].copy()
    axes_names = list(d[d.competitor == "NVIDIA"].dimension)
    nv = d[d.competitor == "NVIDIA"].set_index("dimension").score_0_5.reindex(axes_names).values
    sub = d[d.competitor.isin(comps + ["NVIDIA"])]
    means = {cmp: sub[sub.competitor == cmp].score_0_5.mean() for cmp in comps}
    leads = {cmp: list(sub[(sub.competitor == cmp) & (sub.verdict_vs_nvidia == "leads")].dimension) for cmp in comps}
    title, alt = title_fn(means, leads, nv.mean())
    c = Chart(
        id=chart_id, title=title,
        subtitle="Capability scores 0-5 on nine axes; competitor (filled) vs NVIDIA reference (dashed green); analyst judgement, sourced",
        alt=alt, data=[DATA], chapters=chapters,
        source="repo analysis (competitor_matrix.csv)",
        source_ids=sources_of(sub), note="Analyst judgement (speculative)",
    )
    n = len(axes_names)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    ang_c = ang + ang[:1]
    fig, axs = c.figure_grid(2, 3, width=12.5, height=8.6, subplot_kw=dict(projection="polar"))
    short = {"Peak compute": "Compute", "Memory capacity & bandwidth": "Memory", "Scale-up fabric": "Scale-up",
             "Scale-out networking": "Scale-out", "Software ecosystem": "Software", "Rack-scale systems": "Racks",
             "Supply access (CoWoS/HBM)": "Supply", "Cost/TCO": "Cost/TCO", "Merchant availability": "Merchant"}
    for ax, comp in zip(np.ravel(axs), comps):
        vals = sub[sub.competitor == comp].set_index("dimension").score_0_5.reindex(axes_names).values.tolist()
        col = _color(comp)
        ax.plot(ang_c, list(nv) + [nv[0]], color=NV, lw=1.6, ls="--")
        ax.fill(ang_c, vals + vals[:1], color=col, alpha=0.28)
        ax.plot(ang_c, vals + vals[:1], color=col, lw=2)
        ax.scatter(ang, vals, color=col, s=14, zorder=3)
        ax.set_ylim(0, 5)
        ax.set_yticks([1, 2, 3, 4, 5])
        ax.set_yticklabels(["", "", "", "", ""])
        ax.set_xticks(ang)
        ax.set_xticklabels([short[a] for a in axes_names], fontsize=7.6, color=INK["text"])
        ax.tick_params(axis="x", pad=1)
        ax.grid(color=INK["grid"], lw=0.7)
        ax.spines["polar"].set_color(INK["base"])
        ax.set_title(f"{comp}  (avg {means[comp]:.1f} vs NVIDIA {nv.mean():.1f})", fontsize=10, color=col
                     if comp not in ("Intel",) else INK["title"], fontweight="bold", pad=14)
    fig.subplots_adjust(wspace=0.45, hspace=0.55)
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([0], [0], color=NV, ls="--", lw=1.6, label="NVIDIA reference"),
                        Patch(facecolor="#B5B5B5", alpha=0.5, label="Competitor (entity color)")],
               loc="lower right", bbox_to_anchor=(0.985, 0.045), ncol=2, fontsize=8.5, frameon=False)
    _margins(fig, left=0.05, right=0.97, wspace=0.45, hspace=0.6)
    c.save(fig, list(np.ravel(axs)), legend=False, top=0.82, bottom=0.10)


@register
def competitor_radar_1():
    comps = ["AMD", "Google TPU", "AWS Trainium", "Microsoft Maia", "Meta MTIA", "Intel"]

    def tf(means, leads, nvm):
        best = max(means, key=means.get)
        t = (f"{best} is the strongest all-round challenger, averaging {means[best]:.1f} of 5 vs NVIDIA's {nvm:.1f}")
        alt = ("Six radar charts comparing AMD, Google TPU, AWS Trainium, Microsoft Maia, Meta MTIA and Intel with NVIDIA on nine "
               "capability axes. Average scores: " + "; ".join(f"{k} {v:.1f}" for k, v in means.items()) +
               f" versus NVIDIA {nvm:.1f}. AMD leads on memory capacity; Google TPU leads on scale-up domain size and cost; "
               "every rival trails on software ecosystem and rack-scale systems.")
        return t, alt
    _radar(comps, "15-competitor-radar-small-multiples", tf, ["15", "19"])


@register
def competitor_radar_2():
    comps = ["Broadcom", "Marvell", "Huawei", "Qualcomm", "Cerebras", "Groq"]

    def tf(means, leads, nvm):
        t = (f"ASIC partners, China and start-ups attack one or two axes each; none averages above {max(means.values()):.1f} of 5")
        alt = ("Six radar charts comparing Broadcom, Marvell, Huawei, Qualcomm, Cerebras and Groq with NVIDIA on nine capability "
               "axes. Average scores: " + "; ".join(f"{k} {v:.1f}" for k, v in means.items()) +
               f" versus NVIDIA {nvm:.1f}. Broadcom leads in scale-out Ethernet switching, Huawei matches on scale-up domain size "
               "but is supply-constrained, and Qualcomm, Cerebras and Groq avoid HBM supply limits with different memory designs.")
        return t, alt
    _radar(comps, "15-competitor-radar-small-multiples-2", tf, ["15", "19"])


@register
def breadth_vs_depth():
    df = load(DATA)
    d = df[(df.dimension_type == "layer")].copy()
    g = d.groupby("competitor").agg(breadth=("score_0_5", lambda s: int((s >= 3).sum())),
                                    depth=("score_0_5", "mean")).reset_index()
    nvr = g[g.competitor == "NVIDIA"].iloc[0]
    rivals = g[g.competitor != "NVIDIA"].sort_values("breadth", ascending=False)
    top = rivals.iloc[0]
    c = Chart(
        id="15-competitor-breadth-vs-depth",
        title=(f"NVIDIA scores 3+ in {nvr.breadth} of 12 layers; the broadest rival, {top.competitor}, in {top.breadth}, "
               "and most rivals compete in only a few"),
        subtitle="Breadth = layers (02-13) scored 3 or more of 5; depth = average layer score; repo analyst judgement",
        alt=(f"Scatter of stack breadth against average depth. NVIDIA scores 3 or more in {nvr.breadth} of 12 layers with an average "
             f"of {nvr.depth:.1f}; {top.competitor} is the broadest rival at {top.breadth} layers (average {top.depth:.1f}). "
             "Custom-ASIC partners and start-ups cluster at low breadth, showing they compete on one or two layers."),
        data=[DATA], chapters=["15", "19"],
        source="repo analysis (competitor_matrix.csv)", source_ids=sources_of(d),
        note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=10, height=6.2)
    offsets = {"Marvell": (6, -10), "Groq": (6, -10), "Qualcomm": (6, 6), "Cerebras": (6, 6), "Microsoft Maia": (6, -11),
               "AWS Trainium": (6, 6), "Meta MTIA": (6, -10), "Intel": (6, 6), "Broadcom": (6, 6), "Huawei": (6, -11),
               "Google TPU": (6, 6), "AMD": (6, -11)}
    for _, r in g.iterrows():
        col = NV if r.competitor == "NVIDIA" else _color(r.competitor)
        ax.scatter(r.breadth, r.depth, s=140 if r.competitor == "NVIDIA" else 90, color=col, edgecolor="#FFFFFF", zorder=3)
        dx, dy = offsets.get(r.competitor, (6, 6))
        ax.annotate(r.competitor, (r.breadth, r.depth), xytext=(dx, dy), textcoords="offset points", fontsize=9,
                    color=col if r.competitor not in ("Intel",) else INK["title"],
                    fontweight="bold" if r.competitor in ("NVIDIA",) else "normal")
    ax.axvline(6, color=INK["base"], lw=0.8, ls=":")
    ax.axhline(2.5, color=INK["base"], lw=0.8, ls=":")
    ax.text(11.9, 0.55, "Broad but shallow", ha="right", fontsize=8.5, color=INK["muted"])
    ax.text(11.9, 4.75, "Full-stack", ha="right", fontsize=8.5, color=INK["muted"])
    ax.text(0.1, 4.75, "Point solutions (deep, narrow)", ha="left", fontsize=8.5, color=INK["muted"])
    ax.text(0.1, 0.55, "Niche", ha="left", fontsize=8.5, color=INK["muted"])
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 5)
    ax.grid(axis="both", color=INK["grid"])
    c.save(fig, ax, xlabel="Breadth: layers scored ≥ 3 of 5 (count of 12)", ylabel="Depth: average layer score (0-5)", legend=False)
