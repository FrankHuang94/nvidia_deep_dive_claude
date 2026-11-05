"""Layer 13 (ecosystem, go-to-market and capital) strategy charts: deployable capital vs peers,
vendor capital per gigawatt of committed compute, NVIDIA deal-structure mix over time, frontier
buyers' gigawatt pipelines by supplier, and equity purchases vs shareholder returns.

Owner: layer-13 STRATEGY agent. Data: data/l13_strat_peer_capital.csv, l13_strat_capital_per_gw.csv,
l13_strat_deals_2026_additions.csv, l13_strat_gw_pipeline.csv, l13_strat_equity_portfolio.csv
(documented in data/README.md) plus the shared acquisitions_investments.csv and financials.csv (read only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, Chart, entity_color, load, register, sources_of

PEER = "l13_strat_peer_capital.csv"
PERGW = "l13_strat_capital_per_gw.csv"
DEALS = "acquisitions_investments.csv"
DEALS_ADD = "l13_strat_deals_2026_additions.csv"
GWP = "l13_strat_gw_pipeline.csv"
FIN = "financials.csv"
EQ = "l13_strat_equity_portfolio.csv"

ORDER = ["NVIDIA", "Broadcom", "AMD", "Qualcomm"]


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


# --------------------------------------------------------------------------------------
# 1. Deployable capital: NVIDIA vs AMD vs Broadcom vs Qualcomm
# --------------------------------------------------------------------------------------
@register
def deployable_capital_vs_peers():
    df = load(PEER)

    def val(co, metric):
        r = df[(df.company == co) & (df.metric == metric)]
        return float(r.value.iloc[0]) if len(r) else np.nan

    cash_metric = {"NVIDIA": "cash_and_debt_securities", "AMD": "cash_and_short_term_investments",
                   "Broadcom": "cash_and_equivalents", "Qualcomm": "cash_and_marketable_securities"}
    cash = {c: val(c, m) for c, m in cash_metric.items()}
    nv_eq = val("NVIDIA", "marketable_equity_securities")
    fcf = {c: val(c, "free_cash_flow_quarter") for c in ORDER}
    fcf_est = {c: (df[(df.company == c) & (df.metric == "free_cash_flow_quarter")].confidence.iloc[0] == "estimate")
               for c in ORDER}
    debt = {c: val(c, "total_debt") for c in ["AMD", "Qualcomm"]}
    others = cash["AMD"] + cash["Broadcom"] + cash["Qualcomm"]
    others_fcf = fcf["AMD"] + fcf["Broadcom"] + fcf["Qualcomm"]

    c = Chart(
        id="13-deployable-capital-vs-peers",
        title=(f"NVIDIA's ~${cash['NVIDIA']:.0f}B cash pile beats AMD, Broadcom and Qualcomm combined "
               f"(~${others:.0f}B)"),
        subtitle=("Left: cash and liquid securities at latest quarter end (US$ B). Right: free cash flow in the latest "
                  "quarter found (US$ B). Hatched = aggregator estimate"),
        alt=(f"Two-panel bar chart. Left: cash and liquid securities at the latest quarter end: NVIDIA "
             f"${cash['NVIDIA']:.1f}B of cash and debt securities (July 2026) plus ${nv_eq:.1f}B of listed equity stakes, "
             f"Broadcom ${cash['Broadcom']:.1f}B (August 2026), AMD ${cash['AMD']:.1f}B (September 2026, debt "
             f"${debt['AMD']:.1f}B) and Qualcomm ${cash['Qualcomm']:.1f}B (September 2026, debt ${debt['Qualcomm']:.1f}B), "
             f"so the three peers together hold about ${others:.0f}B. Right: latest quarterly free cash flow: NVIDIA "
             f"${fcf['NVIDIA']:.1f}B (Q1 FY2027), Broadcom ${fcf['Broadcom']:.1f}B, AMD about ${fcf['AMD']:.1f}B and "
             f"Qualcomm about ${fcf['Qualcomm']:.1f}B (aggregator estimates)."),
        data=[PEER], chapters=["13", "15", "19"],
        source="company filings and releases",
        source_ids=sources_of(df), note="Periods differ by up to a quarter",
    )
    fig, axes = c.figure_grid(1, 2, width=11.5, height=5.6)
    ax1, ax2 = axes
    y = np.arange(len(ORDER))[::-1]
    for yi, co in zip(y, ORDER):
        col = NV if co == "NVIDIA" else entity_color(co)
        ax1.barh(yi, cash[co], color=col, height=0.6)
        if co != "NVIDIA":
            ax1.annotate(f"${cash[co]:.1f}B", (cash[co], yi), xytext=(4, 0), textcoords="offset points",
                         va="center", fontsize=9, color=INK["text"])
        else:
            ax1.text(cash[co] / 2, yi, f"${cash[co]:.1f}B cash + debt sec.", ha="center", va="center",
                     fontsize=8.6, color="white", fontweight="bold")
        if co == "NVIDIA":
            ax1.barh(yi, nv_eq, left=cash[co], color=GEN_PAST, height=0.6, hatch="..", edgecolor="white")
            ax1.annotate(f"+ ${nv_eq:.1f}B listed\nequity stakes", (cash[co] + nv_eq, yi), xytext=(4, 0),
                         textcoords="offset points", va="center", fontsize=8.5, color=INK["muted"])
    ax1.set_yticks(y, ORDER)
    ax1.set_xlim(0, 135)
    ax1.set_xlabel("Cash and liquid securities (US$ B)")
    ax1.set_title("Balance-sheet liquidity", fontsize=10.5, color=INK["text"], loc="left")
    ax1.grid(axis="x", color=INK["grid"])
    ax1.grid(axis="y", visible=False)

    for yi, co in zip(y, ORDER):
        col = NV if co == "NVIDIA" else entity_color(co)
        b = ax2.barh(yi, fcf[co], color=col, height=0.6)
        if fcf_est[co]:
            for p in b.patches:
                p.set_hatch("///")
                p.set_alpha(0.75)
                p.set_edgecolor("white")
        lab = f"~${fcf[co]:.1f}B (Est.)" if fcf_est[co] else f"${fcf[co]:.1f}B"
        ax2.annotate(lab, (fcf[co], yi), xytext=(4, 0), textcoords="offset points", va="center",
                     fontsize=9, color=INK["text"])
    ax2.set_yticks(y, ORDER)
    ax2.set_xlim(0, 62)
    ax2.set_xlabel("Free cash flow, latest quarter (US$ B)")
    ax2.set_title(f"One quarter of NVIDIA FCF vs ~${others_fcf:.0f}B for the three peers",
                  fontsize=10.5, color=INK["text"], loc="left")
    ax2.grid(axis="x", color=INK["grid"])
    ax2.grid(axis="y", visible=False)
    _margins(fig, left=0.09, right=0.97, wspace=0.32, top=0.80, bottom=0.17)
    c.save(fig, list(axes), legend=False)


# --------------------------------------------------------------------------------------
# 2. Vendor capital per GW of committed compute
# --------------------------------------------------------------------------------------
@register
def capital_per_gigawatt():
    df = load(PERGW)
    d = df.dropna(subset=["capital_per_gw_usd_b"]).copy()
    d = d.sort_values("capital_per_gw_usd_b")
    amd_hi = float(d[d.deal.str.contains(r"\$600")].capital_per_gw_usd_b.iloc[0])
    amd_lo = float(d[d.deal.str.contains("illustrative")].capital_per_gw_usd_b.iloc[0])
    nv_anth = float(d[(d.supplier == "NVIDIA") & (d.counterparty == "Anthropic")].capital_per_gw_usd_b.iloc[0])
    c = Chart(
        id="13-capital-per-gigawatt",
        title=(f"AMD's warrant may give OpenAI ~${amd_hi:.0f}B/GW (at $600/share) vs NVIDIA's "
               f"~${nv_anth:.0f}B/GW pledges"),
        subtitle="Vendor capital offered per gigawatt of committed compute, US$ B per GW (equity, or warrant value at a given AMD share price)",
        alt=(f"Horizontal bar chart of vendor capital per gigawatt of compute a customer commits to: AMD's warrant for "
             f"160 million shares is worth about ${amd_hi:.0f}B per GW to OpenAI if AMD reaches the reported $600 "
             f"share-price hurdle, or ~${amd_lo:.1f}B per GW at an illustrative $200; NVIDIA's pledges were about "
             f"${nv_anth:.0f}B per GW for Anthropic (up to $10B, 1 GW) and for OpenAI's superseded letter of intent "
             f"($100B, 10 GW); AMD's up-to-$5B Anthropic stake ~$2.5B per GW (2 GW); NVIDIA's xAI stake ~$2B per GW, "
             f"Poolside ~$0.5B and CoreWeave ~$0.47B; Broadcom's "
             f"10 GW OpenAI programme carries no disclosed vendor capital. NVIDIA's 2026 $30B OpenAI equity has no GW tie."),
        data=[PERGW], chapters=["13", "12", "15", "CS4"],
        source="company announcements, press; repo arithmetic",
        source_ids=sources_of(df), note="Hatched = repo calculation",
    )
    fig, ax = c.figure(width=11, height=5.8)
    y = np.arange(len(d))
    for yi, (_, r) in zip(y, d.iterrows()):
        col = entity_color(r.supplier) if r.supplier != "NVIDIA" else NV
        if r.status == "superseded":
            col = GEN_PAST
        bar = ax.barh(yi, max(r.capital_per_gw_usd_b, 0.0), color=col, height=0.62)
        if r.confidence in ("estimate", "speculative"):
            for p in bar.patches:
                p.set_hatch("///")
                p.set_alpha(0.8)
                p.set_edgecolor("white")
        lab = f"${r.capital_per_gw_usd_b:.1f}B/GW" if r.capital_per_gw_usd_b > 0 else "$0 (no vendor capital disclosed)"
        if r.capital_per_gw_usd_b > 0:
            lab += f"  (${r.capital_usd_b:,.0f}B / {r.committed_gw:.0f} GW)" if r.capital_usd_b >= 1 else \
                f"  (${r.capital_usd_b:.2f}B / {r.committed_gw:.0f} GW)"
        ax.annotate(lab, (max(r.capital_per_gw_usd_b, 0), yi), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.8, color=INK["text"])
    ax.set_yticks(y, list(d.deal))
    ax.set_xlim(0, 24)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=NV, label="NVIDIA equity"), Patch(color=GEN_PAST, label="NVIDIA (superseded LOI)"),
                       Patch(color=entity_color("AMD"), label="AMD equity"),
                       Patch(facecolor=entity_color("AMD"), hatch="///", edgecolor="white", label="AMD warrant (value depends on share price)"),
                       Patch(color=entity_color("Broadcom"), label="Broadcom")],
              loc="lower right", fontsize=8.5, frameon=False)
    _margins(fig, left=0.31, right=0.97, top=0.84, bottom=0.14)
    c.save(fig, ax, xlabel="Vendor capital per GW of committed compute (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 3. Deal-structure mix over time
# --------------------------------------------------------------------------------------
STRUCT_ORDER = ["Acquisition (incl. failed Arm)", "Licence + acquihire", "Stake in customer (lab, neocloud, app)",
                "Stake in supplier / ecosystem partner", "Capacity or financing commitment"]
STRUCT_COLOR = {
    "Acquisition (incl. failed Arm)": NV,
    "Licence + acquihire": "#3F6B00",
    "Stake in customer (lab, neocloud, app)": "#2A78D6",
    "Stake in supplier / ecosystem partner": "#86B6EF",
    "Capacity or financing commitment": "#C98500",
}


def _structure(r) -> str:
    t = r.deal_type
    if t in ("acquisition", "failed-acquisition"):
        return STRUCT_ORDER[0]
    if t == "acquihire-license":
        return STRUCT_ORDER[1]
    if t == "strategic-partnership-investment":
        return STRUCT_ORDER[4]
    lay = str(r.layer_strengthened).zfill(2)
    return STRUCT_ORDER[2] if lay in ("12", "13") else STRUCT_ORDER[3]


@register
def deal_structure_mix():
    base = load(DEALS, dtype={"layer_strengthened": str})
    add = load(DEALS_ADD, dtype={"layer_strengthened": str})
    df = pd.concat([base, add], ignore_index=True)
    df["year"] = df.announce_date.astype(str).str[:4].astype(int)
    df["structure"] = df.apply(_structure, axis=1)
    d = df[df.year >= 2019]
    piv = d.pivot_table(index="year", columns="structure", values="counterparty", aggfunc="count", fill_value=0)
    piv = piv.reindex(columns=STRUCT_ORDER, fill_value=0).reindex(range(2019, 2027), fill_value=0)
    early = piv.loc[2019:2022].sum()
    late = piv.loc[2023:2026].sum()
    acq_early = early[STRUCT_ORDER[0]] / early.sum() * 100
    acq_late = late[STRUCT_ORDER[0]] / late.sum() * 100
    stakes_late = int(late[STRUCT_ORDER[2]] + late[STRUCT_ORDER[3]])
    c = Chart(
        id="13-deal-structure-mix",
        title=(f"Since 2023 only {acq_late:.0f}% of NVIDIA's {int(late.sum())} logged deals were acquisitions; "
               f"{stakes_late} were stakes"),
        subtitle=("NVIDIA deals per year by structure (count, announce year), 2019–2026 YTD; pre-2023 venture stakes "
                  "are under-recorded"),
        alt=(f"Stacked bar chart of NVIDIA deals by year and structure, 2019 to 2026. In 2019-2022 acquisitions "
             f"(Mellanox, Cumulus, Bright, the failed Arm bid) were {acq_early:.0f}% of {int(early.sum())} deals. In "
             f"2023-2026 there were {int(late.sum())} deals and acquisitions fell to {acq_late:.0f}%: {int(late[STRUCT_ORDER[2]])} "
             f"stakes in customers such as OpenAI, Anthropic, xAI, CoreWeave and Mistral, {int(late[STRUCT_ORDER[3]])} "
             f"stakes in suppliers and partners such as Intel, Nokia, Synopsys, Marvell, Lumentum and Coherent, "
             f"{int(late[STRUCT_ORDER[1]])} licence-plus-acquihire deals (Enfabrica, Groq) and "
             f"{int(late[STRUCT_ORDER[4]])} capacity or financing commitments including the CoreWeave backstop and the "
             f"2026 financing platforms."),
        data=[DEALS, DEALS_ADD], chapters=["13", "12", "19"],
        source="repo deal files",
        source_ids=sources_of(d), note="Counts, not dollars",
    )
    fig, ax = c.figure(width=11, height=5.8)
    x = np.arange(len(piv.index))
    bottom = np.zeros(len(x))
    for s in STRUCT_ORDER:
        vals = piv[s].values
        ax.bar(x, vals, bottom=bottom, color=STRUCT_COLOR[s], width=0.7, label=s, edgecolor="white", linewidth=0.6)
        bottom += vals
    for xi, tot in zip(x, bottom):
        ax.annotate(f"{int(tot)}", (xi, tot), xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=9, color=INK["text"])
    ax.set_xticks(x, [str(i) if i < 2026 else "2026 YTD" for i in piv.index])
    ax.set_ylim(0, bottom.max() * 1.18)
    ax.legend(loc="upper left", fontsize=8.8, frameon=False)
    c.save(fig, ax, xlabel="Announce year", ylabel="Deals (count)", legend=False)


# --------------------------------------------------------------------------------------
# 4. Frontier buyers' announced gigawatts by supplier
# --------------------------------------------------------------------------------------
SUPPLIER_COLOR = {"NVIDIA": NV, "Broadcom": entity_color("Broadcom"), "AMD": entity_color("AMD"),
                  "Google (TPU)": entity_color("Google"), "Qualcomm": entity_color("Qualcomm")}


@register
def gw_pipeline_by_supplier():
    df = load(GWP)
    buyers = ["OpenAI", "Anthropic", "HUMAIN", "xAI"]
    sups = ["NVIDIA", "Broadcom", "AMD", "Google (TPU)", "Qualcomm"]
    tot = df.groupby("buyer").gw.sum()
    nv = df[df.supplier == "NVIDIA"].groupby("buyer").gw.sum()
    oai_tot, oai_nv = tot["OpenAI"], nv["OpenAI"]
    all_tot, all_nv = df.gw.sum(), df[df.supplier == "NVIDIA"].gw.sum()
    c = Chart(
        id="13-gw-pipeline-by-supplier",
        title=(f"NVIDIA holds {oai_nv:.0f} of OpenAI's {oai_tot:.0f} announced GW and ~{all_nv / all_tot:.0%} of "
               f"four big buyers' total"),
        subtitle="Announced compute programmes by buyer and chip supplier, gigawatts (2025–2026 announcements; deployments 2026–2030)",
        alt=(f"Stacked horizontal bar chart of announced compute programmes in gigawatts. OpenAI {oai_tot:.0f} GW: "
             f"NVIDIA 10 (September 2025 letter of intent, since restructured), Broadcom custom accelerators 10 and AMD 6. "
             f"Anthropic {tot['Anthropic']:g} GW: AMD Helios up to 2 (with an up-to-$5B AMD investment), NVIDIA up to 1 and "
             f"Google TPUs over 1 GW in 2026 (a further multi-GW TPU expansion from 2027 is unquantified). HUMAIN: NVIDIA "
             f"up to 0.5 GW, AMD 0.5 GW and Qualcomm 0.2 GW. xAI: about 1 GW on NVIDIA "
             f"(company claim, contested). NVIDIA's share across these programmes is about {all_nv / all_tot:.0%}."),
        data=[GWP], chapters=["13", "15", "17", "CS4"],
        source="company announcements and press",
        source_ids=sources_of(df), note="Hatched = restructured LOI or contested",
    )
    fig, ax = c.figure(width=11, height=5.4)
    y = np.arange(len(buyers))[::-1]
    for yi, b in zip(y, buyers):
        left = 0.0
        for s_ in sups:
            r = df[(df.buyer == b) & (df.supplier == s_)]
            if r.empty:
                continue
            g = float(r.gw.iloc[0])
            bar = ax.barh(yi, g, left=left, color=SUPPLIER_COLOR[s_], height=0.6, edgecolor="white", linewidth=0.8)
            if r.status.iloc[0] == "superseded" or "contested" in str(r.gw_basis.iloc[0]):
                for p in bar.patches:
                    p.set_hatch("///")
                    p.set_alpha(0.8)
            if g >= 3:
                ax.text(left + g / 2, yi, f"{s_.split(' ')[0]} {g:g}", ha="center", va="center", fontsize=8.6,
                        color="white", fontweight="bold")
            left += g
        ax.annotate(f"{tot[b]:g} GW", (left, yi), xytext=(5, 0), textcoords="offset points", va="center",
                    fontsize=9.5, color=INK["title"], fontweight="bold")
    ax.set_yticks(y, buyers)
    ax.set_xlim(0, 30)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=SUPPLIER_COLOR[s_], label=s_) for s_ in sups], loc="lower right",
              fontsize=8.8, frameon=False)
    c.save(fig, ax, xlabel="Announced compute (GW)", legend=False)


# --------------------------------------------------------------------------------------
# 5. Equity purchases vs shareholder returns
# --------------------------------------------------------------------------------------
@register
def equity_vs_shareholder_returns():
    eq = load(EQ)
    fin = load(FIN)

    def ev(period, metric):
        return float(eq[(eq.period == period) & (eq.metric == metric)].value.iloc[0])

    def ret(qs):
        r = fin[(fin.metric == "shareholder_returns") & (fin.period.isin(qs))]
        return float(r.value.sum()), r

    r26, rows26 = ret(["Q1FY26", "Q2FY26"])
    r27, rows27 = ret(["Q1FY27", "Q2FY27"])
    p26, p27 = ev("H1FY2026", "equity_purchases"), ev("H1FY2027", "equity_purchases")
    gains = ev("H1FY2027", "net_equity_gains")
    more = ev("Q2FY2027", "further_equity_commitments")
    c = Chart(
        id="13-equity-vs-shareholder-returns",
        title=(f"Equity buying hit {p27 / r27:.0%} of NVIDIA's shareholder payouts in H1 FY2027: "
               f"${p27:.1f}B vs ${r27:.1f}B"),
        subtitle="Cash spent on purchases of equity securities vs buybacks + dividends, first half of each fiscal year (US$ B)",
        alt=(f"Grouped bar chart comparing NVIDIA's first-half cash uses. H1 FY2026: buybacks and dividends ${r26:.1f}B, "
             f"equity purchases ${p26:.1f}B ({p26 / r26:.0%}). H1 FY2027: buybacks and dividends ${r27:.1f}B, equity "
             f"purchases ${p27:.1f}B ({p27 / r27:.0%}), led by the ~$30B OpenAI stake. Net gains on equity securities in "
             f"H1 FY2027 were ${gains:.1f}B, largely unrealised, and further equity commitments were about ${more:.0f}B."),
        data=[EQ, FIN], chapters=["13", "12", "18"],
        source="NVIDIA filings, press readings",
        source_ids=sources_of(eq) + [s for s in sources_of(pd.concat([rows26, rows27])) if s not in sources_of(eq)],
        note="Gains are mark-to-market, not cash",
    )
    fig, ax = c.figure(width=11, height=5.6)
    x = np.arange(2)
    w = 0.36
    b1 = ax.bar(x - w / 2, [r26, r27], width=w, color=GEN_PAST, label="Buybacks + dividends")
    b2 = ax.bar(x + w / 2, [p26, p27], width=w, color=NV, label="Purchases of equity securities")
    for bars in (b1, b2):
        for b in bars.patches:
            h = b.get_height()
            ax.annotate(f"${h:.1f}B", (b.get_x() + b.get_width() / 2, h), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=9.5, color=INK["text"])
    ax.text(0.99, 0.97, f"H1 FY2027 also: +${gains:.1f}B net equity gains (paper)\n"
            f"and ~${more:.0f}B of further equity commitments", transform=ax.transAxes, ha="right", va="top",
            fontsize=9, color=INK["muted"])
    ax.set_xticks(x, ["H1 FY2026\n(Feb–Jul 2025)", "H1 FY2027\n(Feb–Jul 2026)"])
    ax.set_ylim(0, 58)
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    c.save(fig, ax, ylabel="US$ B", legend=False)
