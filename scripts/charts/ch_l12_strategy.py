"""Layer 12 (orchestration and cloud services) strategy charts: competitor heatmap, NVIDIA equity holdings and
cloud-capacity commitments (circular-financing evidence), neocloud economics and power, H100 rental index, private
neocloud valuations and hyperscaler capex guidance drift.

Owner: layer-12 STRATEGY agent. Data: data/l12_competitor_verdicts.csv, l12_equity_holdings.csv,
l12_neocloud_metrics.csv, l12_gpu_rental_index.csv, l12_private_companies.csv, l12_hyperscaler_capex_guidance.csv
(documented in data/README.md) plus financials.csv (cloud commitments) and gpu_rental_prices.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

from style import Chart, INK, NV, NV_DARK, SEQ_BLUE, VERDICT_COLORS, entity_color, load, register, sources_of

VERD = "l12_competitor_verdicts.csv"
EQ = "l12_equity_holdings.csv"
NEO = "l12_neocloud_metrics.csv"
RENT = "l12_gpu_rental_index.csv"
PRIV = "l12_private_companies.csv"
CAPEX = "l12_hyperscaler_capex_guidance.csv"
FIN = "financials.csv"

LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}
VERDICT_LABEL = {"leads": "L = rival leads NVIDIA", "parity": "P = parity", "behind": "B = rival behind",
                 "different": "D = different approach"}
COREWEAVE = "#256ABF"   # neoclouds are not palette entities: use the sequential blue ramp, direct-labelled
NEBIUS = "#86B6EF"


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


# --------------------------------------------------------------------------------------
# 1. Competitor capability heatmap (layer-specific)
# --------------------------------------------------------------------------------------
@register
def cloud_competitor_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    cust = int(df[df.dimension.eq("Customer ownership")].verdict_vs_nvidia.eq("leads").sum())
    accel_lead = int(df[df.dimension.eq("Accelerator control")].verdict_vs_nvidia.eq("leads").sum())
    neutral = int(df[df.dimension.eq("Hardware neutrality")].verdict_vs_nvidia.eq("leads").sum())
    c = Chart(
        id="12-cloud-competitor-heatmap",
        title=(f"{cust} of {len(comps)} rivals own the cloud customer NVIDIA rarely bills; "
               f"{'none' if accel_lead == 0 else accel_lead} out-control its accelerators"),
        subtitle="Repo verdict for each rival vs NVIDIA's layer-12 position (DGX Cloud/Lepton, Run:ai/KAI, Slurm, DSX OS, allocation, capital)",
        alt=(f"Heatmap of {len(comps)} orchestration and cloud rivals against NVIDIA on five dimensions. AWS, Google Cloud, "
             f"Microsoft Azure, CoreWeave and Nebius lead on customer ownership and owned capacity (CoreWeave $104B backlog, "
             f"1.5 GW active); none leads on accelerator control, where AWS Trainium and Google TPU are at parity and NVIDIA-only "
             f"neoclouds are behind; schedulers are mostly at parity; {neutral} open-source tools and marketplaces lead on "
             "hardware and cloud neutrality."),
        data=[VERD], chapters=["12", "15"], source="repo analysis of company disclosures",
        source_ids=sources_of(df)[:5], note="Repo judgement",
    )
    fig, ax = c.figure(width=12.5, height=7.2)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            label = str(r.cell_label)
            if len(label) > 26:
                cut = label.rfind(" ", 0, 26)
                cut = cut if cut > 0 else 26
                label = label[:cut] + "\n" + label[cut + 1:]
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {label}", ha="center", va="center",
                    fontsize=8.0, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" & ", " &\n") for d in dims], fontsize=9.2)
    ax.xaxis.tick_top()
    prod = df.drop_duplicates("competitor").set_index("competitor").product_basis
    ax.set_yticks(np.arange(len(comps)) + 0.5)
    ax.set_yticklabels([f"{cmp}\n{prod[cmp]}" for cmp in comps], fontsize=8.4)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.215, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.08)


# --------------------------------------------------------------------------------------
# 2. NVIDIA balance-sheet exposure to its customers' build-out (circular-financing evidence)
# --------------------------------------------------------------------------------------
@register
def nvidia_customer_support_exposure():
    eq = load(EQ)
    fin = load(FIN)
    q2 = eq[eq.period.eq("Q2FY27")].set_index("metric").value
    commit = q2["equity_commitments_outstanding"]
    cloud = fin[(fin.period == "Q2FY27") & (fin.metric == "cloud_service_commitments")].value.item()
    aicl = fin[(fin.period == "Q2FY27") & (fin.metric == "ai_cloud_capacity_agreements")].value.item()
    rev = fin[(fin.period == "FY2026") & (fin.metric == "revenue_total")].value.item()
    held = q2["marketable_equity"] + q2["non_marketable_equity"] + q2["locked_up_public_equity"]
    total = held + commit + cloud + aicl
    used = pd.concat([eq[eq.period.eq("Q2FY27")],
                      fin[((fin.period == "Q2FY27") & fin.metric.isin(["cloud_service_commitments",
                                                                       "ai_cloud_capacity_agreements"]))
                          | ((fin.period == "FY2026") & (fin.metric == "revenue_total"))]])
    c = Chart(
        id="12-nvidia-customer-support-exposure",
        title=(f"NVIDIA's stakes, pledges and capacity buy-backs add up to ~${total:.0f}B vs ${rev:.0f}B FY2026 revenue"),
        subtitle="US$ B at Jul 26, 2026 (Q2 FY2027): equity held plus multi-year commitments (a stock plus future obligations, not one year's cash)",
        alt=(f"Horizontal stacked bar chart of NVIDIA's balance-sheet ties to the AI build-out at July 2026: equity securities "
             f"held ${held:.0f}B (marketable ${q2['marketable_equity']:.1f}B, non-marketable ${q2['non_marketable_equity']:.1f}B, "
             f"locked-up ${q2['locked_up_public_equity']:.0f}B), further equity commitments ${commit:.0f}B, AI-cloud capacity "
             f"agreements ${aicl:.0f}B (buying capacity partners cannot resell, including the $6.3B CoreWeave backstop) and "
             f"multi-year cloud service agreements ${cloud:.0f}B, about ${total:.0f}B in all versus FY2026 revenue of "
             f"${rev:.0f}B. The $500B financing platforms with six asset managers are third-party capital and not included."),
        data=[EQ, FIN], chapters=["12", "13", "18"], source="NVIDIA filings; secondary readings",
        source_ids=sources_of(used)[:5], note="Equity per secondary reading",
    )
    fig, ax = c.figure(width=11, height=5.6)
    rows = [
        ("Equity securities held", [(q2["non_marketable_equity"], NV_DARK, "private stakes"),
                                    (q2["marketable_equity"], NV, "public stakes"),
                                    (q2["locked_up_public_equity"], "#A9CC73", "locked-up")]),
        ("Further equity commitments", [(commit, NV, None)]),
        ("AI-cloud capacity agreements\n(buy capacity partners can't resell)", [(aicl, NV, None)]),
        ("Multi-year cloud service\nagreements (rent-back)", [(cloud, NV, None)]),
    ]
    y = np.arange(len(rows))[::-1]
    for yi, (lab, segs) in zip(y, rows):
        left = 0
        for v, col, seg in segs:
            hatch = "///" if lab.startswith(("Further", "AI-cloud", "Multi")) else None
            ax.barh(yi, v, 0.58, left=left, color=col if not hatch else "#CFE3B0", edgecolor=NV_DARK if hatch else col,
                    hatch=hatch, linewidth=1.2 if hatch else 0)
            if seg and v > 8:
                ax.text(left + v / 2, yi, f"{seg}\n${v:.1f}B", ha="center", va="center", fontsize=8.4,
                        color="#FFFFFF", fontweight="bold")
            left += v
        ax.text(left + 1.5, yi, f"${left:.0f}B", va="center", fontsize=10, color=INK["title"], fontweight="bold")
    ax.annotate("incl. $6.3B CoreWeave backstop\n(through Apr 2032)", (6.3, y[2]), xytext=(60, y[2] + 0.42),
                fontsize=8.4, color=INK["text"], va="center", arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.axvline(rev, color=INK["muted"], ls="--", lw=1.2)
    ax.text(rev - 2, y[0] + 0.45, f"FY2026 revenue ${rev:.0f}B", ha="right", fontsize=9, color=INK["text"])
    ax.text(rev - 2, y[-1] - 0.5, f"Sum ≈ ${total:.0f}B", ha="right", fontsize=10, color=INK["title"],
            fontweight="bold")
    ax.set_yticks(y, [r[0] for r in rows], fontsize=9)
    ax.set_xlim(0, 240)
    ax.set_ylim(-0.8, len(rows) - 0.3)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    _margins(fig, left=0.25, right=0.97)
    c.save(fig, ax, xlabel="US$ B (hatched = commitments not yet paid)", legend=False)


# --------------------------------------------------------------------------------------
# 4. Neocloud 2026 capex vs revenue guidance
# --------------------------------------------------------------------------------------
def _rng(df, comp, metric):
    r = df[(df.company == comp) & (df.metric == metric)].iloc[0]
    return float(r.value_low), float(r.value_high)


@register
def neocloud_capex_vs_revenue_2026():
    df = load(NEO)
    rows = []
    for comp in ["CoreWeave", "Nebius"]:
        rl, rh = _rng(df, comp, "revenue_guidance")
        cl, ch = _rng(df, comp, "capex_guidance")
        rows.append((comp, rl, rh, cl, ch))
    ratios = {r[0]: ((r[3] + r[4]) / 2) / ((r[1] + r[2]) / 2) for r in rows}
    bl = _rng(df, "CoreWeave", "revenue_backlog")[0]
    c = Chart(
        id="12-neocloud-capex-vs-revenue-2026",
        title=(f"Neoclouds plan ${ratios['CoreWeave']:.1f} (CoreWeave) to ${ratios['Nebius']:.1f} (Nebius) of 2026 capex "
               "per $1 of 2026 revenue"),
        subtitle="Company guidance for calendar 2026, US$ B (bar = midpoint, whisker = range); CoreWeave backlog shown for scale",
        alt=(f"Grouped bar chart of 2026 guidance: CoreWeave revenue ${rows[0][1]}–{rows[0][2]}B versus capex "
             f"${rows[0][3]:.0f}–{rows[0][4]:.0f}B (about {ratios['CoreWeave']:.1f} dollars of capex per dollar of revenue) with a "
             f"${bl}B revenue backlog; Nebius revenue ${rows[1][1]}–{rows[1][2]}B versus capex ${rows[1][3]:.0f}–{rows[1][4]:.0f}B "
             f"(about {ratios['Nebius']:.1f} to 1). The gap is funded by debt, customer prepayments and equity, which is why "
             "financing terms drive neocloud economics."),
        data=[NEO], chapters=["12", "14", "18"], source="CoreWeave and Nebius Q2 2026 results",
        source_ids=sources_of(df[df.metric.isin(["revenue_guidance", "capex_guidance", "revenue_backlog"])]),
        note="Guidance as of Aug 2026",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(rows))
    w = 0.34
    for i, (comp, rl, rh, cl, ch) in enumerate(rows):
        col = COREWEAVE if comp == "CoreWeave" else NEBIUS
        rm, cm = (rl + rh) / 2, (cl + ch) / 2
        ax.bar(i - w / 2, rm, w, color=col, alpha=0.5, edgecolor=col, linewidth=1.5,
               label="2026 revenue guidance" if i == 0 else None)
        ax.errorbar(i - w / 2, rm, yerr=[[rm - rl], [rh - rm]], color=INK["title"], capsize=4, lw=1.2)
        ax.bar(i + w / 2, cm, w, color=col, label="2026 capex guidance" if i == 0 else None)
        ax.errorbar(i + w / 2, cm, yerr=[[cm - cl], [ch - cm]], color=INK["title"], capsize=4, lw=1.2)
        ax.text(i - w / 2, rh + 1.0, f"${rl:g}–{rh:g}B", ha="center", va="bottom", fontsize=9, color=INK["title"])
        ax.text(i + w / 2, ch + 1.0, f"${cl:g}–{ch:g}B", ha="center", va="bottom", fontsize=9, color=INK["title"])
        ax.text(i, ch + 6.5, f"capex ÷ revenue ≈ {ratios[comp]:.1f}×", ha="center", fontsize=10, color=INK["title"],
                fontweight="bold")
    ax.set_axisbelow(True)
    ax.set_xticks(x, [r[0] for r in rows])
    ax.set_xlim(-0.8, 1.6)
    ax.set_ylim(0, 55)
    ax.legend(loc="upper right")
    c.save(fig, ax, ylabel="Calendar 2026 guidance (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 5. CoreWeave revenue backlog growth
# --------------------------------------------------------------------------------------
@register
def coreweave_backlog_growth():
    df = load(NEO)
    b = df[(df.company == "CoreWeave") & (df.metric == "revenue_backlog")].copy()
    b["t"] = pd.to_datetime(b.period)
    b = b.sort_values("t")
    rl, rh = _rng(df, "CoreWeave", "revenue_guidance")
    first, last = b.iloc[0].value_low, b.iloc[-1].value_low
    c = Chart(
        id="12-coreweave-backlog-growth",
        title=(f"CoreWeave's contracted backlog rose {last / first:.1f}× in a year to ${last:.0f}B, "
               f"~{last / ((rl + rh) / 2):.0f}× its 2026 revenue guide"),
        subtitle="Revenue backlog (remaining contracted revenue) at quarter end, US$ B; hatched = derived from reported growth rate",
        alt=(f"Bar chart of CoreWeave's revenue backlog: about ${first:.1f}B at June 2025 (derived from the reported 246% growth), "
             f"$55.6B at September 2025, $66.8B at December 2025 and ${last}B at June 2026, with more than $25B of new "
             f"commitments signed after quarter end; the June 2026 backlog equals about {last / ((rl + rh) / 2):.0f} years of "
             f"its 2026 revenue guidance of ${rl}-{rh}B. Customers include OpenAI, Meta and Microsoft."),
        data=[NEO], chapters=["12", "17", "18"], source="CoreWeave results as reported",
        source_ids=sources_of(b), note="Backlog = signed contracts, not cash",
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    x = np.arange(len(b))
    bars = ax.bar(x, b.value_low, 0.6, color=COREWEAVE)
    for p, conf in zip(bars.patches, b.confidence):
        if conf == "estimate":
            p.set_hatch("///")
            p.set_alpha(0.7)
    for xi, v in zip(x, b.value_low):
        inside = xi == x[-1]
        ax.text(xi, v - 7 if inside else v + 2, f"${v:.1f}B", ha="center", va="bottom", fontsize=10,
                color="#FFFFFF" if inside else INK["title"], fontweight="bold")
    ax.bar(x[-1], 25, 0.6, bottom=last + 0.5, color="#CDE2FB", edgecolor=COREWEAVE, hatch="..", linewidth=1.2)
    ax.text(x[-1] + 0.36, last + 12.5, ">$25B more signed\nafter quarter end", fontsize=8.6, color=INK["text"], va="center")
    ax.axhline((rl + rh) / 2, color=INK["muted"], ls="--", lw=1.2)
    ax.text(x[-1] + 0.34, (rl + rh) / 2 + 3, f"2026 revenue\nguide ~${(rl + rh) / 2:.1f}B", fontsize=8.6,
            color=INK["text"], ha="left")
    ax.set_axisbelow(True)
    ax.set_xticks(x, [t.strftime("%b %Y") for t in b.t])
    ax.set_xlim(-0.6, len(b) - 0.1)
    ax.set_ylim(0, 145)
    c.save(fig, ax, ylabel="Revenue backlog (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 6. H100 rental price rebound
# --------------------------------------------------------------------------------------
@register
def h100_rental_price_rebound():
    df = load(RENT)
    df["t"] = pd.to_datetime(df.date.astype(str).str.slice(0, 10), format="mixed")
    low = df[df.series.str.contains("1-year") & (df.date == "2025-10")].usd_per_gpu_hour.item()
    hi = df[df.series.str.contains("1-year") & (df.date == "2026-03")].usd_per_gpu_hour.item()
    c = Chart(
        id="12-h100-rental-price-rebound",
        title=(f"H100 rentals rose {(hi / low - 1) * 100:.0f}% from a ${low:.2f}/hr low (Oct 2025) "
               f"to ${hi:.2f} by Mar 2026"),
        subtitle="H100 rental price observations by series, US$ per GPU-hour (different contract types: compare within a series)",
        alt=(f"Line and scatter chart of H100 rental prices: about $8 per GPU-hour on neoclouds in September 2023 and $6.62 spot in "
             f"late 2023, about $2 on marketplaces by October 2024, then SemiAnalysis's one-year contract index at a ${low:.2f} low "
             f"in October 2025 rising to ${hi:.2f} in March 2026 (+{(hi / low - 1) * 100:.0f}%), Silicon Data's index rising from "
             "$2.00 to $2.20 between December 2025 and January 2026, and a cited spot price of $2.83 in February 2026. Old GPUs "
             "re-priced upward as inference demand outran supply."),
        data=[RENT], chapters=["12", "14", "18"], source="SemiAnalysis, Silicon Data, Latent Space as cited",
        source_ids=sources_of(df), note="Mixed contract types; 2023–24 points are anecdotal",
    )
    fig, ax = c.figure(width=11.5, height=5.8)
    styles = {
        "Neocloud market (typical)": ("#B5B5B5", "o", "2023 neocloud on-demand (anecdotal)"),
        "SemiAnalysis spot (as cited)": ("#86B6EF", "s", "Spot, SemiAnalysis as cited by a marketplace blog"),
        "GPU marketplaces (low end)": ("#7A7A7A", "o", "Marketplace low end (anecdotal)"),
        "SemiAnalysis 1-year contract index": (NV, "D", "SemiAnalysis H100 1-year contract index"),
        "Silicon Data H100 index": ("#256ABF", "^", "Silicon Data H100 rental index"),
    }
    for s, (col, mk, lab) in styles.items():
        d = df[df.series == s].sort_values("t")
        ls = "-" if len(d) > 1 else "none"
        ax.plot(d.t, d.usd_per_gpu_hour, color=col, marker=mk, markersize=8, lw=2, ls=ls, label=lab)
        for r in d.itertuples():
            dy = 10 if s != "Silicon Data H100 index" else -16
            ax.annotate(f"${r.usd_per_gpu_hour:.2f}", (r.t, r.usd_per_gpu_hour), xytext=(0, dy), textcoords="offset points",
                        ha="center", fontsize=8.6, color=INK["title"])
    ax.axvspan(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-03-31"), color="#E1E0D9", alpha=0.45, lw=0)
    ax.text(pd.Timestamp("2025-12-15"), 4.6, "Rebound:\ninference demand\n> supply", ha="center", fontsize=8.8,
            color=INK["text"])
    ax.set_ylim(0, 9)
    ax.set_xlim(pd.Timestamp("2023-06-01"), pd.Timestamp("2026-06-30"))
    ax.legend(loc="upper center", fontsize=8.4)
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    c.save(fig, ax, xlabel="Date", ylabel="US$ per H100 GPU-hour", legend=False)


# --------------------------------------------------------------------------------------
# 7. Private neocloud / AI-infrastructure valuations
# --------------------------------------------------------------------------------------
@register
def neocloud_private_valuations():
    df = load(PRIV).sort_values("valuation_usd_b")
    tot = df.valuation_usd_b.sum()
    nv = int(df.nvidia_backed.eq("yes").sum())
    c = Chart(
        id="12-neocloud-private-valuations",
        title=(f"Six private AI-cloud companies carry ~${tot:.0f}B of last-round value; NVIDIA backs {nv} of them"),
        subtitle="Latest reported valuation, US$ B, with round and date; hatched = target or reported, not company-confirmed",
        alt=("Horizontal bar chart of private AI-infrastructure valuations: Crusoe $30.9B (Series F, Sep 2026), VAST Data $30B "
             "(Series F, Apr 2026), Nscale $14.6B (Series C, Mar 2026, plus $3.36B pre-IPO convertibles), Lambda about $14.5B "
             "(pre-IPO target, Oct 2026), Fluidstack $7B (Apr 2026, Google-backstopped leases) and Together AI $3.3B (2025). "
             f"NVIDIA is an investor in {nv} of the six; several are preparing IPOs."),
        data=[PRIV], chapters=["12", "13"], source="company and press reports", source_ids=sources_of(df)[:5],
        note="Green = NVIDIA investor",
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    y = np.arange(len(df))
    for yi, r in zip(y, df.itertuples()):
        col = NV if r.nvidia_backed == "yes" else INK["base"]
        target = "target" in str(r.valuation_basis) or r.company in ("Lambda",)
        b = ax.barh(yi, r.valuation_usd_b, 0.6, color=col)
        if target:
            b.patches[0].set_hatch("///")
            b.patches[0].set_alpha(0.75)
        when = pd.Timestamp(str(r.last_round_date)[:7]).strftime("%b %Y")
        ax.text(r.valuation_usd_b + 0.4, yi, f"${r.valuation_usd_b:g}B · {r.last_round} · {when}", va="center",
                fontsize=9, color=INK["title"])
    ax.set_yticks(y, [f"{r.company}\n{r.category}" for r in df.itertuples()], fontsize=8.6)
    ax.set_xlim(0, 48)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    _margins(fig, left=0.25, right=0.97)
    c.save(fig, ax, xlabel="Latest reported valuation (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 8. Hyperscaler 2026 capex guidance drift
# --------------------------------------------------------------------------------------
@register
def hyperscaler_capex_guidance_drift():
    df = load(CAPEX)
    df["mid"] = (df.capex_low_usd_b + df.capex_high_usd_b) / 2
    df["t"] = pd.to_datetime(df.guidance_date.astype(str).str.slice(0, 7))
    comps = ["Alphabet", "Amazon", "Meta", "Microsoft"]
    first = df.sort_values("t").groupby("company").first().mid
    last = df.sort_values("t").groupby("company").last().mid
    big3_first = first[["Alphabet", "Amazon", "Meta"]].sum()
    big3_last = last[["Alphabet", "Amazon", "Meta"]].sum()
    big4_last = last[comps].sum()
    c = Chart(
        id="12-hyperscaler-capex-guidance-drift",
        title=(f"Big-3 2026 capex guides rose from ~${big3_first:.0f}B to ~${big3_last:.0f}B; "
               f"~${big4_last:.0f}B incl. Microsoft"),
        subtitle="Calendar-2026 capital-expenditure guidance midpoints by date issued, US$ B (whiskers = guided range)",
        alt=(f"Line chart of 2026 capex guidance midpoints: Alphabet rose from $180B (Feb 2026) to $185B (Apr) and $200B (Jul); "
             f"Amazon from about $200B to about $220B; Meta from $125B (Jan) to about $137.5B (Jul); Microsoft's calendar-2026 "
             f"figure was about $175B in July and about $170B in October. Combined, the big three rose from about "
             f"${big3_first:.0f}B to ${big3_last:.0f}B and the big four total about ${big4_last:.0f}B; other tallies on "
             "different bases reach $803-828B."),
        data=[CAPEX], chapters=["12", "18", "08"], source="company guidance as reported", source_ids=sources_of(df),
        note="Bases differ (leases)",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    for comp in comps:
        d = df[df.company == comp].sort_values("t")
        col = entity_color(comp)
        ax.plot(d.t, d.mid, color=col, marker="o", markersize=8, lw=2)
        ax.vlines(d.t, d.capex_low_usd_b, d.capex_high_usd_b, color=col, lw=1.2, alpha=0.7)
        last_r = d.iloc[-1]
        ax.annotate(f"{comp} ${last_r.mid:.0f}B", (last_r.t, last_r.mid), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=9.5, color=col, fontweight="bold")
    ax.set_xlim(pd.Timestamp("2025-12-15"), pd.Timestamp("2026-12-31"))
    ax.set_ylim(100, 240)
    ax.set_yticks([100, 125, 150, 175, 200, 225])
    from style import axis_break
    import matplotlib.dates as mdates
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    axis_break(ax)
    c.save(fig, ax, xlabel="Date guidance issued", ylabel="CY2026 capex guidance midpoint (US$ B; axis starts at 100)",
           legend=False)
