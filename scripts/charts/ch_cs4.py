"""Case study CS4 (AMD, OpenAI and the second source): AMD vs NVIDIA data-center revenue by quarter,
and the value of AMD's OpenAI warrant against OpenAI's (assumed) AMD hardware bill.

Owner: CS4 case-study agent. Data: data/cs4_amd_openai.csv (documented in data/README.md) plus the shared
peer_financials.csv and financials.csv (read only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from style import INK, NV, Chart, entity_color, load, register, sources_of

CS4 = "cs4_amd_openai.csv"
PEER = "peer_financials.csv"
FIN = "financials.csv"
AMD = entity_color("AMD")


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _nv_calendar_quarter(period_end: str) -> str:
    """NVIDIA fiscal quarters end late Apr/Jul/Oct/Jan; map to the calendar quarter they mostly cover."""
    d = pd.Timestamp(period_end)
    m = d.month
    if m in (4, 5):
        return f"{d.year}-Q1"
    if m in (7, 8):
        return f"{d.year}-Q2"
    if m in (10, 11):
        return f"{d.year}-Q3"
    return f"{d.year - 1}-Q4"  # January end -> previous calendar Q4


def _dc_frame():
    peer = load(PEER)
    amd = peer[(peer.company == "AMD") & (peer.metric == "revenue_data_center") & (peer.period_type == "Q")]
    amd = amd[["period", "value", "confidence", "source_id"]].rename(columns={"value": "amd"})
    cs = load(CS4)
    add = cs[cs.record_type == "dc_revenue"][["period", "value", "confidence", "source_id"]].rename(columns={"value": "amd"})
    amd = pd.concat([amd, add], ignore_index=True).drop_duplicates("period", keep="last")
    fin = load(FIN)
    nv = fin[(fin.metric == "revenue_data_center") & (fin.period_type == "Q")].copy()
    nv["cq"] = nv.period_end.map(_nv_calendar_quarter)
    nv = nv[["cq", "value", "source_id"]].rename(columns={"cq": "period", "value": "nv", "source_id": "nv_src"})
    df = amd.merge(nv, on="period", how="left").sort_values("period").reset_index(drop=True)
    df = df[df.period >= "2023-Q1"].reset_index(drop=True)
    return df, peer, cs, fin


@register
def amd_vs_nvidia_dc_revenue():
    df, peer, cs, fin = _dc_frame()
    first, last = df.iloc[0], df.iloc[-1]
    both = df.dropna(subset=["nv"])
    lastb = both.iloc[-1]
    ratio = both.nv / both.amd
    growth_amd = last.amd / first.amd
    srcs = sorted(set(sources_of(peer[(peer.company == "AMD") & (peer.metric == "revenue_data_center")]))
                  | set(sources_of(cs[cs.record_type == "dc_revenue"]))
                  | set(sources_of(fin[(fin.metric == "revenue_data_center") & (fin.period >= "Q1FY24")])))
    c = Chart(
        id="CS4-amd-vs-nvidia-dc-revenue",
        title=(f"AMD's data-center revenue rose ~{growth_amd:.1f}× since 2023, but NVIDIA's lead widened "
               f"from {ratio.iloc[0]:.1f}× to {ratio.iloc[-1]:.0f}×"),
        subtitle=("Quarterly data-center revenue (US$ B) and NVIDIA ÷ AMD; AMD's segment includes EPYC CPUs; "
                  "calendar quarters"),
        alt=(f"Two-panel chart, calendar 2023-Q1 to {last.period}. Left: AMD's Data Center segment revenue rose from "
             f"${first.amd:.1f}B to ${last.amd:.1f}B a quarter ({last.period} is a repo estimate from AMD's +97% y/y), about "
             f"{growth_amd:.1f} times, while NVIDIA's Data Center revenue rose from ${first.nv:.1f}B to ${lastb.nv:.1f}B "
             f"({lastb.period}). Right: NVIDIA's data-center revenue was {ratio.iloc[0]:.1f} times AMD's in 2023-Q1, "
             f"{ratio.iloc[len(ratio)//2]:.1f} times in {both.period.iloc[len(ratio)//2]} and {ratio.iloc[-1]:.1f} times in "
             f"{lastb.period}: the second source has not yet narrowed the revenue gap. AMD's figure includes EPYC "
             f"server CPUs, so its GPU-only gap is larger."),
        data=[PEER, CS4, FIN], chapters=["CS4", "15", "18"],
        source="AMD and NVIDIA quarterly results", source_ids=srcs,
        note="Hatched = repo estimate",
    )
    fig, axes = c.figure_grid(1, 2, width=11.5, height=5.8, gridspec_kw={"width_ratios": [1.55, 1]})
    ax1, ax2 = axes
    x = np.arange(len(df))
    w = 0.4
    est = (df.confidence == "estimate").values
    b_nv = ax1.bar(x - w / 2, df.nv.fillna(0), width=w, color=NV, label="NVIDIA Data Center")
    b_amd = ax1.bar(x + w / 2, df.amd, width=w, color=AMD, label="AMD Data Center segment")
    for p, e in zip(b_amd.patches, est):
        if e:
            p.set_hatch("///")
            p.set_alpha(0.75)
            p.set_edgecolor("white")
    ax1.annotate(f"${lastb.nv:.1f}B", (both.index[-1] - w / 2, lastb.nv), xytext=(0, 3),
                 textcoords="offset points", ha="center", fontsize=8.6, color=NV, fontweight="bold")
    ax1.annotate(f"${last.amd:.1f}B\n(Est.)" if est[-1] else f"${last.amd:.1f}B", (x[-1] + w / 2, last.amd),
                 xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.4, color=AMD, fontweight="bold")
    ax1.set_xticks(x, [p.replace("-", "\n") for p in df.period], fontsize=8)
    ax1.set_ylabel("Data-center revenue per quarter (US$ B)")
    ax1.set_ylim(0, 100)
    ax1.legend(loc="upper left")
    ax1.set_title("Both grew; NVIDIA grew faster", fontsize=10.5, color=INK["text"], loc="left")

    xb = np.array([df.index[df.period == p][0] for p in both.period])
    ax2.plot(xb, ratio.values, color=INK["text"], lw=2, marker="o", ms=5)
    for i in (0, len(ratio) // 2, len(ratio) - 1):
        ax2.annotate(f"{ratio.iloc[i]:.1f}×", (xb[i], ratio.iloc[i]), xytext=(0, 7), textcoords="offset points",
                     ha="center", fontsize=9, color=INK["title"], fontweight="bold")
    ax2.set_xticks(xb[::2], [p.replace("-", "\n") for p in both.period.iloc[::2]], fontsize=8)
    ax2.set_ylim(0, 16)
    ax2.set_ylabel("NVIDIA ÷ AMD data-center revenue (×)")
    ax2.set_title("The revenue gap widened", fontsize=10.5, color=INK["text"], loc="left")
    _margins(fig, left=0.07, right=0.98, wspace=0.25, top=0.80, bottom=0.17)
    c.save(fig, list(axes), legend=False)


@register
def warrant_value_vs_hardware_spend():
    cs = load(CS4)

    def g(metric, period=None):
        r = cs[cs.metric == metric]
        if period:
            r = r[r.period == period]
        return float(r.value.iloc[0])

    shares_m = g("warrant_shares")
    gw = g("committed_capacity")
    hurdle = g("final_tranche_share_price_hurdle")
    lo, base, hi = (g(f"amd_hardware_spend_per_gw_{k}") for k in ("low", "base", "high"))
    px = cs[cs.record_type == "share_price"].sort_values("period")
    prices = np.linspace(0, 800, 161)
    value = shares_m * prices / 1000.0  # US$ B
    spend_lo, spend_base, spend_hi = lo * gw, base * gw, hi * gw
    v_pre = shares_m * px.value.iloc[0] / 1000
    v_hurdle = shares_m * hurdle / 1000
    be_base = spend_base * 1000 / shares_m  # share price at which warrant = base hardware bill
    c = Chart(
        id="CS4-warrant-value-vs-hardware-spend",
        title=(f"At the ${hurdle:.0f} hurdle, AMD's warrant (~${v_hurdle:.0f}B) ≈ OpenAI's 6 GW AMD "
               f"hardware bill (Est. ~${spend_base:.0f}B)"),
        subtitle=(f"Value of 160M AMD shares at $0.01 if fully vested (US$ B) vs share price; band = assumed "
                  f"6 GW spend at ${lo:.0f}–{hi:.0f}B/GW"),
        alt=(f"Line chart: the warrant for {shares_m:.0f} million AMD shares at a $0.01 strike is worth about "
             f"${v_pre:.0f}B at the pre-deal price of ${px.value.iloc[0]:.2f} (2025-10-03), ${shares_m*px.value.iloc[1]/1000:.0f}B "
             f"after the first day's ~24% jump, ${v_hurdle:.0f}B at the reported ${hurdle:.0f} final-tranche hurdle and "
             f"${shares_m*px.value.iloc[-1]/1000:.0f}B at the ${px.value.iloc[-1]:.2f} close of 2026-09-21. A shaded band shows "
             f"a repo assumption of OpenAI's AMD hardware spend for {gw:.0f} GW: ${spend_lo:.0f}B to ${spend_hi:.0f}B "
             f"(base ${spend_base:.0f}B). Above roughly ${be_base:.0f} a share the fully vested warrant would be worth as "
             f"much as the base-case hardware bill; vesting also needs all {gw:.0f} GW deployed."),
        data=[CS4], chapters=["CS4", "13"],
        source="AMD/OpenAI terms and AMD share prices",
        source_ids=sources_of(cs[cs.record_type != "dc_revenue"]),
        note="Band = repo scenario",
    )
    fig, ax = c.figure(width=11, height=6.0)
    ax.axhspan(spend_lo, spend_hi, color=AMD, alpha=0.10, lw=0)
    ax.axhline(spend_base, color=AMD, lw=1.2, ls="--")
    ax.text(15, spend_base + 2, f"Base-case AMD hardware bill, 6 GW (~${spend_base:.0f}B)", color=AMD, fontsize=9,
            va="bottom")
    ax.text(15, spend_hi - 2, f"${spend_hi:.0f}B (high)", color=AMD, fontsize=8.5, va="top", alpha=0.9)
    ax.text(15, spend_lo + 2, f"${spend_lo:.0f}B (low)", color=AMD, fontsize=8.5, va="bottom", alpha=0.9)
    ax.plot(prices, value, color=INK["title"], lw=2.2)
    pts = [(px.value.iloc[0], "Pre-deal close\n$164.67 (Oct 2025)", (-10, 34)),
           (px.value.iloc[1], "Day-one close\n~$204 (Est.)", (14, -40)),
           (hurdle, f"${hurdle:.0f} final-tranche\nhurdle (reported)", (-118, 12)),
           (px.value.iloc[-1], "Close $612\n(Sep 21, 2026)", (14, -34))]
    for p, lab, off in pts:
        v = shares_m * p / 1000
        ax.plot([p], [v], "o", ms=8, color=AMD if p != hurdle else INK["title"], zorder=5)
        ax.annotate(f"{lab}\n→ ${v:.0f}B", (p, v), xytext=off, textcoords="offset points", fontsize=8.6,
                    color=INK["text"], arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.8))
    ax.axvline(be_base, color=INK["muted"], lw=0.8, ls=":")
    ax.text(be_base + 6, 4, f"break-even ~${be_base:.0f}", fontsize=8.5, color=INK["muted"])
    ax.set_xlim(0, 800)
    ax.set_ylim(0, 135)
    _margins(fig, left=0.08, right=0.97, top=0.82, bottom=0.14)
    c.save(fig, ax, xlabel="AMD share price (US$)", ylabel="Warrant value if fully vested (US$ B)", legend=False)
