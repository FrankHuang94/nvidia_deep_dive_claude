"""Case study CS5 (the DeepSeek moment and the efficiency shock): NVIDIA Data Center revenue before and after
the 2025-01-27 sell-off, DeepSeek's headline training cost vs its estimated fleet and NVIDIA's one-day loss,
and the demand elasticity needed for compute spend to rise when the price per token falls.

Owner: CS5 case-study agent. Data: data/cs5_cost_claims.csv, data/cs5_elasticity_grid.csv (documented in
data/README.md) plus the shared financials.csv (read only).
"""
from __future__ import annotations

import numpy as np

from style import GEN_PAST, INK, NV, Chart, entity_color, load, register, sources_of

FIN = "financials.csv"
COST = "cs5_cost_claims.csv"
GRID = "cs5_elasticity_grid.csv"


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


@register
def nvidia_dc_revenue_around_deepseek():
    fin = load(FIN)
    dc = fin[(fin.metric == "revenue_data_center") & (fin.period_type == "Q")].copy()
    dc = dc.sort_values("period_end")
    dc = dc[dc.period_end >= "2023-04-01"].reset_index(drop=True)
    shock = "2025-01-27"
    before = dc[dc.period_end < shock]
    after = dc[dc.period_end >= shock]
    pre_last = before.iloc[-1]
    post_last = after.iloc[-1]
    mult = post_last.value / pre_last.value
    n_after = len(after)
    c = Chart(
        id="CS5-nvidia-dc-revenue-around-deepseek",
        title=f"NVIDIA's Data Center revenue rose {mult:.1f}× in {n_after} quarters after the DeepSeek sell-off",
        subtitle="NVIDIA Data Center revenue per fiscal quarter, US$ B; dashed line = 2025-01-27, when NVIDIA fell ~17% in a day",
        alt=(f"Bar chart of NVIDIA Data Center revenue by fiscal quarter from {dc.period.iloc[0]} to {post_last.period}. "
             f"Before the DeepSeek sell-off of 2025-01-27 revenue had climbed from ${dc.value.iloc[0]:.1f}B to "
             f"${pre_last.value:.1f}B ({pre_last.period}); in the {n_after} quarters after it, revenue kept rising to "
             f"${post_last.value:.1f}B ({post_last.period}), {mult:.1f} times the pre-shock quarter. The efficiency shock "
             f"did not dent reported demand."),
        data=[FIN], chapters=["CS5", "00", "18"],
        source="NVIDIA quarterly results", source_ids=sources_of(dc),
    )
    fig, ax = c.figure(width=11, height=5.8)
    x = np.arange(len(dc))
    cols = [GEN_PAST if d < shock else NV for d in dc.period_end]
    ax.bar(x, dc.value, color=cols, width=0.68)
    xi = len(before) - 0.5
    ax.axvline(xi, color=INK["title"], lw=1.2, ls="--")
    ax.text(xi - 0.15, 82, "DeepSeek sell-off\n2025-01-27: −17%, ~$589B", ha="right", va="top", fontsize=9,
            color=INK["title"])
    ax.annotate(f"${pre_last.value:.1f}B", (len(before) - 1, pre_last.value), xytext=(0, 3), textcoords="offset points",
                ha="center", fontsize=8.8, color=INK["text"], fontweight="bold")
    ax.annotate(f"${post_last.value:.1f}B", (len(dc) - 1, post_last.value), xytext=(0, 3), textcoords="offset points",
                ha="center", fontsize=8.8, color=NV, fontweight="bold")
    ax.text(len(before) + 0.2, 95, f"After: ×{mult:.1f} in {n_after} quarters", fontsize=9.5, color=NV,
            fontweight="bold", va="top")
    ax.set_xticks(x, [p.replace("FY", "\nFY") for p in dc.period], fontsize=8.2)
    ax.set_ylim(0, 100)
    _margins(fig, left=0.07, right=0.98, top=0.83, bottom=0.16)
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter", ylabel="Data Center revenue (US$ B)", legend=False)


@register
def deepseek_cost_headline_vs_fleet():
    df = load(COST)
    df = df.sort_values("value_usd_m").reset_index(drop=True)
    v3 = float(df[df.item.str.startswith("V3")].value_usd_m.iloc[0])
    capex = float(df[df.item.str.startswith("Server capex")].value_usd_m.iloc[0])
    loss = float(df[df.category == "market reaction"].value_usd_m.iloc[0])
    share = v3 / capex * 100
    c = Chart(
        id="CS5-deepseek-cost-headline-vs-fleet",
        title=(f"DeepSeek's ${v3:.1f}M run was ~1/{capex/v3:.0f} of a ~${capex/1000:.1f}B fleet; "
               f"NVIDIA lost ${loss/1000:.0f}B in a day"),
        subtitle="US$ M (log scale): DeepSeek's own cost claims, SemiAnalysis fleet estimates, NVIDIA's 2025-01-27 market-value loss",
        alt=(f"Log-scale horizontal bar chart: DeepSeek's R1 reinforcement-learning run cost about $0.29M (Nature, 512 H800s "
             f"for ~80 hours) and the V3 final pre-training run ${v3:.2f}M (2.788M H800 GPU-hours at $2), both company claims; "
             f"SemiAnalysis estimated more than $500M of GPU investment and about ${capex/1000:.1f}B of server capex for a "
             f"~50,000-GPU Hopper fleet, so the headline was about {share:.2f}% of the fleet; NVIDIA lost about "
             f"${loss/1000:.0f}B of market value on 2025-01-27, roughly 100,000 times the headline training cost."),
        data=[COST], chapters=["CS5", "P1"],
        source="DeepSeek, SemiAnalysis, Bloomberg", source_ids=sources_of(df),
        note="Hatched = estimate",
    )
    fig, ax = c.figure(width=11.5, height=5.6)
    y = np.arange(len(df))
    colors = []
    for cat in df.category:
        if cat == "market reaction":
            colors.append(NV)
        elif cat == "analyst estimate":
            colors.append(entity_color("other"))
        else:
            colors.append(INK["text"])
    bars = ax.barh(y, df.value_usd_m, color=colors, height=0.6)
    for b, cat in zip(bars.patches, df.category):
        if cat == "analyst estimate":
            b.set_hatch("///")
            b.set_edgecolor("white")
    labels = {
        "R1 reinforcement-learning run": "R1 RL run (DeepSeek, Nature)",
        "V3 final pre-training run": "V3 final run (DeepSeek)",
        "GPU investment (fleet)": "GPU investment (Est., >)",
        "Server capex (fleet)": "Server capex, ~50k GPUs (Est.)",
        "NVIDIA one-day market-value loss": "NVIDIA market value lost, 1 day",
    }
    ax.set_yticks(y, [labels.get(i, i) for i in df.item])
    ax.set_xscale("log")
    for yi, v in zip(y, df.value_usd_m):
        txt = f"${v:,.2f}M" if v < 10 else (f"${v:,.0f}M" if v < 1000 else f"${v/1000:,.1f}B")
        ax.annotate(txt, (v, yi), xytext=(4, 0), textcoords="offset points", va="center", fontsize=9,
                    color=INK["title"])
    ax.set_xlim(0.1, 3e6)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.24, right=0.97, top=0.83, bottom=0.15)
    c.save(fig, ax, xlabel="US$ M", logx=True, legend=False)


@register
def spend_multiple_vs_elasticity():
    g = load(GRID)
    ten = g[g.price_drop_multiple == 10]
    e_double = 1 + np.log10(2)
    s15 = float(ten[np.isclose(ten.elasticity, 1.5)].spend_multiple.iloc[0])
    s05 = float(ten[np.isclose(ten.elasticity, 0.5)].spend_multiple.iloc[0])
    c = Chart(
        id="CS5-spend-multiple-vs-elasticity",
        title=f"10× cheaper tokens raise compute spend only if demand elasticity exceeds 1 (ε 1.5 → {s15:.1f}×)",
        subtitle="Spend after the price drop ÷ spend before, by price elasticity of token demand (constant-elasticity model, log scale)",
        alt=(f"Log-scale line chart of the spend multiple against demand elasticity for price drops of 3, 10 and 30 times. "
             f"All three lines cross 1.0 at an elasticity of 1: below it, cheaper tokens shrink total spend; above it, spend grows. "
             f"For a 10 times price drop, elasticity 0.5 leaves spend at {s05:.2f} times the old level, elasticity 1.5 lifts it "
             f"to {s15:.1f} times and elasticity 2 to 10 times; spend doubles at an elasticity of about {e_double:.2f}. "
             f"Bigger price drops amplify both outcomes."),
        data=[GRID], chapters=["CS5", "14"],
        source="repo model (Jevons-paradox arithmetic)", source_ids=sources_of(g),
        note="Model, not a forecast",
    )
    fig, ax = c.figure(width=11, height=5.8)
    styles = {3: ("#86B6EF", "--"), 10: (INK["title"], "-"), 30: ("#256ABF", ":")}
    for drop, (col, ls) in styles.items():
        d = g[g.price_drop_multiple == drop]
        ax.plot(d.elasticity, d.spend_multiple, color=col, lw=2.2 if drop == 10 else 1.8, ls=ls)
        yend = float(d.spend_multiple.iloc[-1])
        ax.annotate(f"price ÷{drop}", (2.0, yend), xytext=(5, 0), textcoords="offset points", va="center",
                    fontsize=9, color=col, fontweight="bold")
    ax.axhline(1, color=INK["base"], lw=1.2)
    ax.axvline(1, color=INK["muted"], lw=0.9, ls=":")
    ax.text(1.02, 0.05, "ε = 1: spend flat", fontsize=8.8, color=INK["muted"])
    ax.axvspan(0, 1, color="#F4C7C3", alpha=0.25, lw=0)
    ax.axvspan(1, 2, color="#B7E1A1", alpha=0.22, lw=0)
    ax.text(0.05, 12, "Efficiency shrinks spend\n(the Jan 2025 market fear)", fontsize=9, color=INK["text"], va="top")
    ax.text(1.42, 0.08, "Jevons: efficiency\ngrows spend", fontsize=9, color=INK["text"], va="bottom")
    for e, lab in ((0.5, f"{s05:.2f}×"), (1.5, f"{s15:.1f}×"), (e_double, "2×")):
        v = 10 ** (e - 1)
        ax.plot([e], [v], "o", ms=7, color=NV, zorder=5)
        ax.annotate(lab, (e, v), xytext=(7, -13), textcoords="offset points", ha="left", fontsize=9,
                    color=NV, fontweight="bold")
    ax.set_xlim(0, 2.25)
    ax.set_ylim(0.03, 40)
    _margins(fig, left=0.08, right=0.95, top=0.83, bottom=0.14)
    c.save(fig, ax, xlabel="Price elasticity of token demand (ε)", ylabel="Spend multiple (×)", logy=True, legend=False)
