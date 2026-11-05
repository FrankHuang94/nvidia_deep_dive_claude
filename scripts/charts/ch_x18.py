"""Chapter 18 - Vulnerabilities and bear case.

Charts built from:
- data/x18_risks.csv               likelihood x impact scores for the ten risks (repo judgement, speculative)
- data/x18_customer_concentration.csv + data/financials.csv   direct customers >= 10% of revenue
- data/x18_financing_comparison.csv  NVIDIA customer-support ties vs Lucent's 1999-2000 vendor financing
- data/x18_pjm_capacity_prices.csv  PJM capacity auction clearing prices (power-constraint signal)
- data/x18_valuation_scenarios.csv  FY2028 earnings multiples under four revenue/margin paths

Valuation arithmetic (repo, speculative): net income = FY2028 revenue x net margin; P/E = market cap / net income;
implied perpetual growth = cost of equity (9%) - 1/(P/E), i.e. the growth a full-payout Gordon model needs to
justify the price from that earnings base.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from style import INK, NV, NV_DARK, GEN_PAST, SEQ_BLUE, entity_color, load, register, sources_of, Chart

CH = ["18"]


def _score_color(score: float) -> str:
    """Single-hue sequential ramp for likelihood x impact (1..25)."""
    bins = [(3, "#F2F7FE"), (6, SEQ_BLUE[0]), (9, SEQ_BLUE[1]), (12, SEQ_BLUE[2]), (16, SEQ_BLUE[4]),
            (25, SEQ_BLUE[6])]
    for top, col in bins:
        if score <= top:
            return col
    return SEQ_BLUE[-1]


@register
def x18_risk_heatmap():
    df = load("x18_risks.csv")
    c = Chart(
        id="18-risk-heatmap",
        title="Repo view: custom ASICs (16) and the capex cycle (15) are NVIDIA's biggest risks; Taiwan is the tail",
        subtitle="Ten risks scored 1–5 for likelihood within their horizon and impact on FY2028–FY2030 gross profit; "
                 "score = likelihood × impact (repo judgement; rationale and evidence in data/x18_risks.csv)",
        alt=("Risk heatmap with likelihood on the x-axis and impact on the y-axis, each scored 1 to 5, plus a ranked "
             "bar panel. Scores (likelihood x impact): hyperscaler custom ASICs 16 (4x4), circular financing and the "
             "capex cycle 15 (3x5), customer concentration 12 (3x4), inference commoditization 12 (4x3), software "
             "abstraction eroding CUDA 9 (3x3), power constraints 8 (4x2), China and export controls 8 (4x2), "
             "antitrust 6 (3x2), open interconnect standards 6 (3x2) and TSMC/Taiwan concentration 5 (1x5), a "
             "low-probability, extreme-impact tail. All scores are the repo's judgement."),
        data=["x18_risks.csv"],
        chapters=CH,
        source="repo scoring of cited evidence (see data/x18_risks.csv)",
        source_ids=["S18027", "S90069", "S2516", "S407", "S90072", "S379"],
        note="Scores are repo judgement (speculative), not forecasts",
    )
    fig, axes = c.figure_grid(1, 2, width=12.6, height=6.6, gridspec_kw={"width_ratios": [1.25, 1]})
    ax, axb = axes
    # background grid of cells coloured by score
    for li in range(1, 6):
        for im in range(1, 6):
            s = li * im
            ax.add_patch(plt_rect(li - 0.5, im - 0.5, _score_color(s)))
            ax.text(li + 0.42, im - 0.42, f"{s}", ha="right", va="bottom", fontsize=7.5, color=INK["muted"])
    # offsets for risks sharing a cell
    offsets = {"R4": (-0.22, 0.12), "R5": (0.2, -0.16), "R6": (-0.22, 0.12), "R9": (0.2, -0.16)}
    label_pos = {
        "R1": (0.0, 0.33, "Concentration"), "R2": (0.0, 0.33, "Custom ASICs"),
        "R3": (0.0, 0.42, "Inference\npricing"), "R4": (0.0, 0.3, "Power"), "R5": (0.0, -0.3, "China"),
        "R6": (0.0, 0.3, "Antitrust"), "R7": (0.0, 0.33, "Capex cycle"), "R8": (0.0, -0.36, "TSMC/Taiwan"),
        "R9": (0.0, -0.4, "Open\ninterconnect"), "R10": (0.0, -0.36, "CUDA erosion"),
    }
    for _, r in df.iterrows():
        dx, dy = offsets.get(r.risk_id, (0.0, 0.0))
        x, y = r.likelihood + dx, r.impact + dy
        ax.scatter([x], [y], s=430, color=INK["title"], zorder=5, edgecolor="white", linewidth=1.2)
        ax.text(x, y, r.risk_id.replace("R", ""), ha="center", va="center", fontsize=8.6, color="white",
                fontweight="bold", zorder=6)
        lx, ly, lab = label_pos[r.risk_id]
        ax.text(x + lx, y + ly, lab, ha="center", va="center", fontsize=7.9, color=INK["title"], zorder=6,
                linespacing=0.95,
                bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.85))
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xticklabels(["1\nrare", "2", "3", "4", "5\nlikely"], fontsize=9)
    ax.set_yticklabels(["1 minor", "2", "3", "4", "5 severe"], fontsize=9)
    ax.set_xlabel("Likelihood within horizon (1 = <10%, 5 = >70%)")
    ax.set_aspect("equal")
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    # ranked bars
    d = df.sort_values(["score", "impact"], ascending=[True, True]).reset_index(drop=True)
    bars = axb.barh(range(len(d)), d.score, color=[_score_color(s) for s in d.score], edgecolor=SEQ_BLUE[5],
                    linewidth=0.8, height=0.66)
    for b, (_, r) in zip(bars, d.iterrows()):
        axb.text(b.get_width() + 0.3, b.get_y() + b.get_height() / 2,
                 f"{int(r.score)}  ({int(r.likelihood)}×{int(r.impact)}) · {r.horizon}", va="center", fontsize=8.4,
                 color=INK["text"])
    axb.set_yticks(range(len(d)))
    axb.set_yticklabels([f"{rid.replace('R', '')}. {lab}" for rid, lab in zip(d.risk_id, d.short_label)],
                        fontsize=9)
    axb.set_xlim(0, 25)
    axb.set_xlabel("Score = likelihood × impact (max 25)")
    axb.grid(axis="x", color=INK["grid"])
    axb.grid(axis="y", visible=False)
    axb.tick_params(length=0)
    for sp in ("top", "right"):
        axb.spines[sp].set_visible(False)
    c.save(fig, ax, ylabel="Impact on FY2028–FY2030 gross profit", legend=False, top=0.83, bottom=0.14)
    # rebalance spacing between panels after chrome is applied is not possible post-save; set before save
    return None


def plt_rect(x, y, color):
    import matplotlib.patches as mpatches
    return mpatches.Rectangle((x, y), 1, 1, facecolor=color, edgecolor="white", linewidth=1.5, zorder=0)


@register
def x18_direct_customer_concentration():
    fin = load("financials.csv")
    cols = ["customer_a_pct_revenue", "customer_b_pct_revenue", "customer_c_pct_revenue", "customer_d_pct_revenue"]
    hist = fin[fin.metric.isin(cols) & fin.period.isin(["FY2024", "FY2025", "Q1FY26", "Q2FY26", "Q3FY26"])].copy()
    hist["rank"] = hist.metric.map({m: i for i, m in enumerate(cols)})
    new = load("x18_customer_concentration.csv")
    new["rank"] = new.groupby("period").cumcount()
    new = new.rename(columns={"pct_revenue": "value"})
    periods = ["FY2024", "FY2025", "Q1FY26", "Q2FY26", "Q3FY26", "H1FY27", "Q2FY27"]
    labels = ["FY2024\n(year)", "FY2025\n(year)", "Q1 FY26", "Q2 FY26", "Q3 FY26", "H1 FY27\n(half)", "Q2 FY27"]
    allrows = pd.concat([hist[["period", "rank", "value", "confidence", "source_id"]],
                         new[["period", "rank", "value", "confidence", "source_id"]]])
    c = Chart(
        id="18-direct-customer-concentration",
        title="Direct-buyer concentration peaked at 61% (Q3 FY2026); in Q2 FY2027 one buyer was 16%",
        subtitle="Direct customers (mostly OEMs/ODMs building for hyperscalers) at ≥10% of NVIDIA revenue, % of revenue "
                 "per period; hatched = quarterly rows pending re-verification against the 10-Q",
        alt=("Stacked bar chart of NVIDIA direct customers above 10% of revenue: FY2024 one customer at 13%; FY2025 three "
             "customers at 12%, 11% and 11% (34%); Q1 FY2026 16% and 14% (30%); Q2 FY2026 23% and 16% (39%); Q3 FY2026 "
             "four customers at 22%, 15%, 13% and 11% (61%); first half of FY2027 three customers at 16%, 15% and 13% "
             "(44%); Q2 FY2027 a single customer at 16%. Indirect buyers such as hyperscalers are larger than these "
             "direct ODM figures suggest."),
        data=["financials.csv", "x18_customer_concentration.csv"],
        chapters=["18", "13"],
        source="NVIDIA 10-K and 10-Q customer-concentration notes",
        source_ids=sources_of(allrows),
    )
    fig, ax = c.figure(width=11.4, height=6.0)
    ramp = [SEQ_BLUE[6], SEQ_BLUE[4], SEQ_BLUE[2], SEQ_BLUE[0]]
    for i, p in enumerate(periods):
        sub = allrows[allrows.period == p].sort_values("rank")
        bottom = 0.0
        for _, r in sub.iterrows():
            b = ax.bar(i, r.value, bottom=bottom, color=ramp[int(r["rank"])], width=0.62, edgecolor="white",
                       linewidth=0.8)
            if r.confidence != "confirmed":
                b[0].set_hatch("///")
                b[0].set_edgecolor("white")
            ax.text(i, bottom + r.value / 2, f"{r.value:.0f}%", ha="center", va="center", fontsize=8.3,
                    color="white" if int(r["rank"]) < 2 else INK["title"])
            bottom += r.value
        n = len(sub)
        ax.text(i, bottom + 1.2, f"{bottom:.0f}%\n({n} buyer{'s' if n > 1 else ''})", ha="center", va="bottom",
                fontsize=8.6, color=INK["title"], fontweight="bold")
    ax.set_xticks(range(len(periods)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 75)
    ax.axvline(4.5, color=INK["base"], lw=1, ls="--")
    ax.text(4.55, 72, "FY2027 disclosures", fontsize=8.4, color=INK["text"], va="top")
    c.save(fig, ax, xlabel="NVIDIA fiscal period (customer letters are re-assigned every period)",
           ylabel="% of NVIDIA revenue", legend=False, top=0.84, bottom=0.16)


@register
def x18_financing_vs_lucent():
    df = load("x18_financing_comparison.csv")
    c = Chart(
        id="18-financing-vs-lucent",
        title="H1 FY2027 equity buying was 24% of NVIDIA revenue, Lucent's ratio at the 2000 peak",
        subtitle="Financing extended to (or stakes held in) customers as % of revenue; Lucent 1999–2000 vs NVIDIA "
                 "measures at July 2026 (LTM = last four quarters, $303B)",
        alt=("Horizontal bar chart of customer financing as a share of revenue. Lucent's vendor-financing commitments in "
             "1999-2000 were $8.1B, 24% of $33.6B revenue. NVIDIA's purchases of equity securities in H1 FY2027 were "
             "$42.4B, 24% of $177.8B half-year revenue; its equity stakes of about $99B equal 33% of $303B "
             "last-four-quarter revenue; and all customer-support ties (stakes, further equity commitments, AI-cloud "
             "capacity and cloud service agreements, about $189B) equal 62%. NVIDIA funds these from operating cash "
             "flow, while Lucent lent to thinly capitalised carriers."),
        data=["x18_financing_comparison.csv"],
        chapters=["18", "13", "12"],
        source="Tunguz (Lucent), NVIDIA 10-Q readings, repo calculation",
        source_ids=sources_of(df),
    )
    d = df.iloc[::-1].reset_index(drop=True)
    labels = {
        "Vendor-financing commitments to customers": "Lucent: vendor financing,\n1999–2000 ($8.1B / $33.6B)",
        "Purchases of equity securities (H1 FY2027)": "NVIDIA: equity purchases,\nH1 FY2027 ($42.4B / $177.8B)",
        "Equity stakes held (Jul 2026)": "NVIDIA: equity stakes held,\nJul 2026 ($99B / $303B LTM)",
    }
    fig, ax0 = c.figure(width=11, height=5.6)
    ax0.remove()
    ax = fig.add_axes([0.27, 0.15, 0.68, 0.66])
    cols = []
    for _, r in d.iterrows():
        cols.append(INK["muted"] if r.entity == "Lucent" else NV)
    bars = ax.barh(range(len(d)), d.ratio_pct, color=cols, height=0.6)
    names = []
    for b, (_, r) in zip(bars, d.iterrows()):
        if r.measure.startswith("All customer-support"):
            names.append("NVIDIA: all customer-support\nties, Jul 2026 ($189B / $303B LTM)")
            b.set_alpha(0.55)
            b.set_hatch("///")
        else:
            names.append(labels.get(r.measure, r.measure))
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2, f"{r.ratio_pct:.0f}%", va="center",
                fontsize=10, color=INK["title"], fontweight="bold")
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(names, fontsize=9)
    ax.axvline(24.1, color=INK["muted"], lw=1, ls="--")
    ax.text(24.6, len(d) - 0.45, "Lucent peak ratio", fontsize=8.4, color=INK["text"], va="center")
    ax.set_xlim(0, 75)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    c.note = "Hatched = mixes assets and future commitments (upper bound)"
    c.save(fig, ax, xlabel="% of revenue (period basis shown in label)", legend=False, top=0.84, bottom=0.14)


@register
def x18_pjm_capacity_price():
    df = load("x18_pjm_capacity_prices.csv")
    c = Chart(
        id="18-pjm-capacity-price",
        title="PJM's grid-capacity price rose ~11.5× in three auctions as data centers drove demand",
        subtitle="PJM base residual auction clearing price, $ per MW-day of capacity, by delivery year; "
                 "hatched = PJM's estimate without the negotiated price cap",
        alt=("Bar chart of PJM capacity auction clearing prices per megawatt-day: $28.92 for 2024/25, $269.92 for "
             "2025/26, $329.17 for 2026/27 and $333.44 for 2027/28, both later auctions at a negotiated cap, about 11.5 "
             "times in three auctions. PJM estimates the 2027/28 price would have been about $530 without the cap; "
             "roughly 5,100 MW of the forecast load increase is tied to data centers and the region fell about "
             "6,600 MW short of its reliability target."),
        data=["x18_pjm_capacity_prices.csv"],
        chapters=["18", "08"],
        source="PJM, Utility Dive, Citizens Utility Board, Maryland OPC",
        source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=10, height=5.6)
    xs = range(len(df))
    cols = [SEQ_BLUE[2], SEQ_BLUE[4], SEQ_BLUE[5], SEQ_BLUE[6], SEQ_BLUE[1]]
    bars = ax.bar(xs, df.clearing_price_usd_per_mw_day, color=cols, width=0.6)
    for b, (_, r) in zip(bars, df.iterrows()):
        if r.confidence == "estimate":
            b.set_hatch("///")
            b.set_edgecolor(SEQ_BLUE[5])
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 8, f"${r.clearing_price_usd_per_mw_day:,.2f}"
                if r.confidence != "estimate" else f"~${r.clearing_price_usd_per_mw_day:,.0f}", ha="center",
                va="bottom", fontsize=9.5, color=INK["title"], fontweight="bold")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(["2024/25", "2025/26", "2026/27\n(at cap)", "2027/28\n(at cap)", "2027/28\nwithout cap (Est.)"],
                       fontsize=9)
    ax.set_ylim(0, 620)
    c.save(fig, ax, xlabel="Capacity delivery year (June–May)", ylabel="$ per MW-day", legend=False, top=0.84,
           bottom=0.16)


@register
def x18_implied_pe_scenarios():
    df = load("x18_valuation_scenarios.csv")
    sc = df[df.kind == "scenario"].sort_values("order")
    ref = df[df.kind == "reference"].iloc[0]
    c = Chart(
        id="18-implied-pe-scenarios",
        title="At ~$5.5T NVIDIA trades near 14× guided FY2028 earnings; only a stall or a 2001-style reset makes it look expensive",
        subtitle="Market cap ÷ FY2028 net income under four revenue and margin paths (repo arithmetic, speculative; label = "
                 "revenue · gross margin · net income · growth the price implies after FY2028)",
        alt=("Bar chart of NVIDIA's price-to-earnings multiple on FY2028 net income at a market value of about $5.5 "
             "trillion. Guide delivered (+70% revenue to about $697B, 72.5% gross margin, about $390B net income): 14.1 "
             "times. Pre-guide consensus (+45%, $594B, $333B): 16.5 times. Growth stalls (flat at $410B, 65% gross "
             "margin, $197B): 27.9 times. A 2001-style reset (revenue down 40% to $246B, 55% gross margin, $81B): 67.8 "
             "times. The S&P 500 traded near 21 times forward earnings in April 2026. At the guided path the price "
             "implies only about 2% annual growth after FY2028."),
        data=["x18_valuation_scenarios.csv"],
        chapters=["18"],
        source="NVIDIA results and guidance, market reports, repo scenarios",
        source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=11, height=6.0)
    xs = np.arange(len(sc))
    cols = [NV, GEN_PAST, SEQ_BLUE[3], INK["muted"]]
    bars = ax.bar(xs, sc.pe, color=cols, width=0.6)
    for b in bars:
        b.set_hatch("///")
        b.set_edgecolor("white")
    for b, (_, r) in zip(bars, sc.iterrows()):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, f"{r.pe:.1f}×", ha="center", va="bottom",
                fontsize=11, color=INK["title"], fontweight="bold")
        ax.text(b.get_x() + b.get_width() / 2, -6.5,
                f"${r.fy2028_revenue_usd_b:.0f}B · {r.gross_margin_pct:.1f}% GM\nNI ${r.net_income_usd_b:.0f}B · "
                f"implied g {r.implied_perpetual_growth_pct:.1f}%", ha="center", va="top", fontsize=8.2,
                color=INK["text"])
    ax.axhline(ref.pe, color=INK["muted"], lw=1.2, ls="--")
    ax.text(-0.42, ref.pe + 0.8, f"S&P 500 forward P/E ~{ref.pe:.0f}× (Apr 2026)", ha="left", va="bottom",
            fontsize=8.6, color=INK["text"])
    ax.set_xticks(xs)
    ax.set_xticklabels(sc.scenario, fontsize=9.2)
    ax.tick_params(axis="x", pad=40)
    ax.set_ylim(0, 80)
    c.note = "All bars hatched: scenarios, not forecasts"
    c.save(fig, ax, ylabel="Market cap ÷ FY2028 net income (×)", legend=False, top=0.84, bottom=0.25)
