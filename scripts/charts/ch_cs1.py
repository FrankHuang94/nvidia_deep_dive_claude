"""Case study CS1 (Mellanox: the best deal) charts: networking revenue before/after the deal and the
deal-payback scenarios.

Owner: CS1 case-study agent. Data: data/cs1_deal_economics.csv (documented in data/README.md) and the
shared data/financials.csv (networking revenue FY2024 onwards).
"""
from __future__ import annotations

import numpy as np

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

DEAL = "cs1_deal_economics.csv"
FIN = "financials.csv"


def _deal():
    return load(DEAL)


def _val(df, record_type, period, metric):
    r = df[(df.record_type == record_type) & (df.period == period) & (df.metric == metric)]
    return float(r.value.iloc[0])


def _networking_series():
    """FY2021 (estimate), FY2022-FY2023 (floor assumption), FY2024-FY2026 (financials.csv) and H1 FY2027."""
    d = _deal()
    fin = load(FIN)
    net = fin[fin.metric.eq("revenue_dc_networking")]
    fy = net[net.period_type.eq("FY")].set_index("period").value
    q = net[net.period_type.eq("Q")].set_index("period").value
    rows = [
        ("FY2021", _val(d, "nvidia_networking", "FY2021", "revenue"), "estimate"),
        ("FY2022", _val(d, "model_assumption", "FY2022", "networking_revenue_floor"), "floor"),
        ("FY2023", _val(d, "model_assumption", "FY2023", "networking_revenue_floor"), "floor"),
        ("FY2024", float(fy["FY2024"]), "estimate"),
        ("FY2025", float(fy["FY2025"]), "reported"),
        ("FY2026", float(fy["FY2026"]), "estimate"),
        ("H1 FY2027", float(q["Q1FY27"] + q["Q2FY27"]), "estimate"),
    ]
    used = net[net.period.isin(["FY2024", "FY2025", "FY2026", "Q1FY27", "Q2FY27"])]
    return rows, used


# --------------------------------------------------------------------------------------
# 1. Before / after: Mellanox revenue vs NVIDIA networking revenue
# --------------------------------------------------------------------------------------
@register
def cs1_networking_before_after():
    d = _deal()
    rows, used = _networking_series()
    m18 = _val(d, "mellanox_actual", "CY2018", "revenue")
    m19 = _val(d, "mellanox_actual", "CY2019", "revenue")
    fy26 = [v for p, v, _ in rows if p == "FY2026"][0]
    h1 = [v for p, v, _ in rows if p == "H1 FY2027"][0]
    mult = fy26 / m19
    c = Chart(
        id="CS1-networking-before-after",
        title=f"Networking revenue rose ~{mult:.0f}× from Mellanox's ${m19:.2f}B (2019) to ~${fy26:.1f}B in FY2026",
        subtitle="Annual revenue, US$ B: Mellanox as a standalone company (CY2018–19) vs NVIDIA's networking line after the deal",
        alt=(f"Bar chart of networking revenue. Mellanox alone earned ${m18:.2f}B in 2018 and ${m19:.2f}B in 2019. "
             f"After the April 2020 close NVIDIA's networking line was about $1.67B in FY2021 (estimate: ~10% of revenue for "
             f"~9 months), was not disclosed for FY2022-FY2023, then reached about $8.6B in FY2024 (estimate), $13.0B in FY2025 "
             f"and about ${fy26:.1f}B in FY2026, roughly {mult:.0f} times Mellanox's 2019 revenue; the first half of FY2027 alone "
             f"brought about ${h1:.1f}B. The line now also includes NVLink switches, which Mellanox never sold."),
        data=[DEAL, FIN], chapters=["CS1", "06", "13"],
        source="Mellanox 10-K; NVIDIA filings",
        source_ids=sources_of(d[d.record_type.isin(["mellanox_actual", "nvidia_networking"])]) + sources_of(used),
        note="Hatched = Est.",
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    labels = ["Mellanox\nCY2018", "Mellanox\nCY2019"] + [p.replace(" FY", "\nFY") for p, _, _ in rows]
    vals = [m18, m19] + [v if kind != "floor" else np.nan for _, v, kind in rows]
    kinds = ["mellanox", "mellanox"] + [k for _, _, k in rows]
    x = np.arange(len(labels))
    for xi, v, k in zip(x, vals, kinds):
        if np.isnan(v):
            ax.text(xi, 1.2, "not\ndisclosed", ha="center", va="bottom", fontsize=8.5, color=INK["muted"], style="italic")
            continue
        color = entity_color("other") if k == "mellanox" else NV
        b = ax.bar(xi, v, width=0.68, color=color, edgecolor=NV_DARK if k != "mellanox" else "#8C8C8C", linewidth=0.8)
        if k == "estimate":
            b.patches[0].set_hatch("///")
            b.patches[0].set_alpha(0.8)
        ax.annotate(f"${v:.1f}B" if v >= 2 else f"${v:.2f}B", (xi, v), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=9, color=INK["title"], fontweight="bold")
    ax.axvline(1.5, color=INK["base"], lw=1.2, ls="--")
    ax.text(1.55, max(vals[i] for i in range(len(vals)) if not np.isnan(vals[i])) * 0.92,
            "Deal closes\n27 Apr 2020", fontsize=9, color=INK["text"], va="top")
    ax.text(8.0, h1 * 0.55, "6 months\nonly", ha="center", fontsize=8.5, color="#FFFFFF", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, max(v for v in vals if not np.isnan(v)) * 1.15)
    c.save(fig, ax, ylabel="Revenue (US$ B)", legend=False, bottom=0.16)


# --------------------------------------------------------------------------------------
# 2. Payback: cumulative networking gross profit credited to the deal vs the price
# --------------------------------------------------------------------------------------
def _scenarios():
    d = _deal()
    rows, used = _networking_series()
    gm_lo = _val(d, "model_assumption", "all", "gross_margin_low_pct") / 100
    gm_hi = _val(d, "model_assumption", "all", "gross_margin_high_pct") / 100
    h_lo = _val(d, "model_assumption", "all", "heritage_share_low_pct") / 100
    h_mid = _val(d, "model_assumption", "all", "heritage_share_mid_pct") / 100
    h_hi = _val(d, "model_assumption", "all", "heritage_share_high_pct") / 100
    coc = _val(d, "model_assumption", "all", "cost_of_capital_pct") / 100
    price = _val(d, "deal_term", "2019-03-11", "price_equity")
    # years since close (2020-04-27) at each period end
    t = np.array([0.76, 1.76, 2.76, 3.75, 4.75, 5.75, 6.25])
    rev = np.array([v for _, v, _ in rows])
    scen = {
        f"Bull: {h_hi:.0%} of networking × {gm_hi:.0%} margin": np.cumsum(rev * h_hi * gm_hi),
        f"Base: {h_mid:.0%} × {gm_lo:.0%}": np.cumsum(rev * h_mid * gm_lo),
        f"Bear: {h_lo:.0%} × {gm_lo:.0%}": np.cumsum(rev * h_lo * gm_lo),
    }
    hurdle = price * (1 + coc) ** t
    return d, rows, used, t, scen, price, hurdle, coc


def _first_cross(cum, line, labels):
    for lab, a, b in zip(labels, cum, line):
        if a >= b:
            return lab
    return "not yet"


@register
def cs1_payback_scenarios():
    d, rows, used, t, scen, price, hurdle, coc = _scenarios()
    labels = [p for p, _, _ in rows]
    names = list(scen)
    bear = scen[names[2]]
    bull = scen[names[0]]
    bear_cross = _first_cross(bear, np.full_like(bear, price), labels)
    bear_hurdle = _first_cross(bear, hurdle, labels)
    c = Chart(
        id="CS1-payback-scenarios",
        title=(f"At half of networking and a 65% margin, Mellanox's ${price:.1f}B was repaid by {bear_cross}"),
        subtitle="Cumulative networking gross profit credited to the deal, US$ B, by fiscal year-end, three scenarios (repo model)",
        alt=(f"Line chart of cumulative networking gross profit attributed to the Mellanox deal from FY2021 to the first half of "
             f"FY2027 under three repo scenarios, against the ${price:.1f}B price and the price compounded at {coc:.0%} a year. "
             f"Bull (100% of networking at 75% gross margin) passes the price in {_first_cross(bull, np.full_like(bull, price), labels)} "
             f"and reaches about ${bull[-1]:.0f}B; base (70% at 65%) reaches about ${scen[names[1]][-1]:.0f}B; bear (50% at 65%) "
             f"passes the price in {bear_cross}, clears the compounded hurdle in {bear_hurdle} and reaches about ${bear[-1]:.0f}B, "
             f"{bear[-1] / price:.1f} times the price. FY2022-FY2023 networking revenue is not disclosed and is set to a "
             "conservative floor of $2.2B a year; gross profit is not cash flow, since networking R&D and SG&A are excluded."),
        data=[DEAL, FIN], chapters=["CS1", "06", "13"],
        source="NVIDIA and Mellanox filings; repo model",
        source_ids=sources_of(d) + sources_of(used),
        note="Repo model (speculative)",
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    x = np.arange(len(labels))
    styles = [(NV, "-", "o"), (NV_DARK, "--", "s"), (GEN_PAST, "-", "D")]
    for (name, cum), (col, ls, mk) in zip(scen.items(), styles):
        ax.plot(x, cum, color=col, ls=ls, marker=mk, lw=2.2, ms=7, label=name, zorder=3)
        ax.annotate(f"${cum[-1]:.0f}B", (x[-1], cum[-1]), xytext=(6, 0), textcoords="offset points",
                    va="center", fontsize=9, color=col, fontweight="bold")
    ax.axhline(price, color=entity_color("amd"), lw=1.8, ls="-", zorder=2)
    ax.text(0.0, price + 1.0, f"Price paid: ${price:.1f}B", color=entity_color("amd"), fontsize=9, fontweight="bold")
    ax.plot(x, hurdle, color=INK["text"], lw=1.4, ls=":", label=f"Price compounded at {coc:.0%}/yr", zorder=2)
    ax.axvspan(0.6, 2.4, color="#F0EFEC", zorder=0)
    ax.text(1.5, bull[-1] * 0.55, "FY2022–23:\nfloor\nassumption", ha="center", fontsize=8.5, color=INK["text"], style="italic")
    ax.set_xticks(x)
    ax.set_xticklabels([lab.replace(" FY", "\nFY") for lab in labels])
    ax.set_xlim(-0.3, len(labels) - 0.4)
    ax.set_ylim(0, bull[-1] * 1.12)
    ax.legend(loc="upper left", fontsize=8.8)
    c.save(fig, ax, ylabel="Cumulative gross profit (US$ B)", legend=False)
