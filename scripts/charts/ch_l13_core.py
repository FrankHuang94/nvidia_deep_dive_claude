"""Layer 13 (ecosystem, go-to-market and capital) - CORE charts: announced sovereign GPU commitments,
the cost build-up of a 100k-GPU national AI factory, GTC attendance, NVIDIA Inception membership,
NVIDIA's equity holdings and the Data Center revenue split by customer type.

Data: data/l13_*.csv (owned by the layer-13 CORE author; documented in data/README.md) plus
data/tco_model_inputs.csv and data/financials.csv (shared, read-only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, load, register, sources_of

CH = ["13"]
SOV = "l13_sovereign_commitments.csv"
ECO = "l13_ecosystem_metrics.csv"
EQ = "l13_equity_holdings.csv"
FAC = "l13_ai_factory_model.csv"
TCO = "tco_model_inputs.csv"
FIN = "financials.csv"
BLUE = "#3987E5"
LBLUE = "#86B6EF"
GRAY = "#B5B5B5"


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _clean(ax) -> None:
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# --------------------------------------------------------------------------------------
# Shared model: a 100k-GPU national AI factory on GB300 NVL72 (all figures Est.)
# --------------------------------------------------------------------------------------
def factory_model() -> dict:
    t = load(TCO)
    g = t[t.system == "GB300 NVL72"]

    def tv(system: str, inp: str, basis_has: str | None = None) -> float:
        rows = t[(t.system == system) & (t.input == inp)]
        if basis_has:
            rows = rows[rows.basis.str.contains(basis_has, regex=False)]
        return float(rows.value.iloc[0])

    rack_price = tv("GB300 NVL72", "capex_per_rack", "Morgan Stanley")
    gpu_bom = tv("GB300 NVL72", "bom_gpu")
    mem_bom = tv("GB300 NVL72", "bom_memory")
    net_share = tv("GB200 NVL72", "networking_storage_share_of_capex") / 100
    rack_kw = tv("GB200 NVL72", "rack_power_kw_all_in")
    pue = tv("All", "pue_assumption_liquid_cooled")
    fac_per_mw = tv("All", "facility_capex_per_mw")
    price_kwh = tv("All", "electricity_price_us_industrial")
    f = load(FAC)
    fv = {r.input: r.value for r in f.itertuples()}
    gpus = float(fv["target_gpus"])
    racks = int(np.ceil(gpus / tv("GB300 NVL72", "accelerators_per_rack")))
    out = dict(racks=racks, gpus=gpus, rack_price=rack_price)
    out["gpu"] = gpu_bom * racks / 1000
    out["memory"] = mem_bom * racks / 1000
    out["rest"] = (rack_price - gpu_bom - mem_bom) * racks / 1000
    all_in = rack_price / (1 - net_share)
    out["network"] = (all_in - rack_price) * racks / 1000
    out["it_mw"] = racks * rack_kw / 1000
    out["facility_mw"] = out["it_mw"] * pue
    out["facility"] = out["facility_mw"] * fac_per_mw / 1000
    out["total"] = out["gpu"] + out["memory"] + out["rest"] + out["network"] + out["facility"]
    out["power_usd_m_yr"] = out["facility_mw"] * 1000 * 8760 * price_kwh / 1e6
    lo = (out["gpu"] + out["memory"] + out["rest"] * float(fv["nvidia_share_rest_of_rack_low"]) / 100
          + out["network"] * float(fv["nvidia_share_network_storage_low"]) / 100)
    hi = (out["gpu"] + out["memory"] + out["rest"] * float(fv["nvidia_share_rest_of_rack_high"]) / 100
          + out["network"] * float(fv["nvidia_share_network_storage_high"]) / 100)
    out["nv_low"], out["nv_high"] = lo, hi
    out["sources"] = sources_of(g) + ["S324", "S340", "S357", "S387", "S388", "S389"] + sources_of(f)
    return out


# --------------------------------------------------------------------------------------
# 1. Announced sovereign GPU commitments by country
# --------------------------------------------------------------------------------------
@register
def l13_sovereign_gpu_commitments():
    d = load(SOV)
    h = d[d.headline_row == "yes"].copy()
    h["gpus"] = pd.to_numeric(h.gpus_committed, errors="coerce")
    named = h.dropna(subset=["gpus"]).sort_values("gpus")
    undisclosed = h[h.gpus.isna()]
    total = named.gpus.sum()
    top2 = named.nlargest(2, "gpus").gpus.sum()
    c = Chart(
        id="13-sovereign-gpu-commitments",
        title=(f"Sovereign deals name ~{total / 1e6:.2f}M NVIDIA GPUs; HUMAIN and Korea are "
               f"{top2 / total:.0%} of them"),
        subtitle="GPUs named in country-level AI-factory announcements, May 2024 - Feb 2026; hatched = press-reported, solid = company-confirmed",
        alt=("Horizontal bar chart of NVIDIA GPUs named in sovereign AI announcements: Saudi Arabia's HUMAIN up to "
             "600,000 over three years (across Saudi Arabia and the US, Nov 2025), South Korea 260,000 (Oct 2025: "
             "government 50,000, Samsung, SK and Hyundai 50,000 each, Naver 60,000), United Kingdom 120,000 by end-2026, "
             "India's Yotta 20,736 B300, France's Mistral Compute 18,000 Grace Blackwell and Germany's Deutsche Telekom "
             "10,000. About 1.03M GPUs in total, 84% of them in the Saudi and Korean deals. Stargate UAE (1 GW) and "
             "Japan's subsidised clouds (>$740M) disclosed no GPU count."),
        data=[SOV], chapters=CH + ["01", "18", "19"],
        source="NVIDIA and partner announcements and press", source_ids=sources_of(h),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    rows = list(undisclosed.itertuples()) + list(named.itertuples())
    labels, vals, hatch = [], [], []
    for r in rows:
        country = str(r.country).replace(" (+ US)", "\n(+ US sites)")
        labels.append(f"{country}\n{str(r.announce_date)[:7]}")
        vals.append(0 if pd.isna(r.gpus) else r.gpus)
        hatch.append(r.confidence != "confirmed")
    y = np.arange(len(rows))
    bars = ax.barh(y, vals, color=NV, edgecolor=NV_DARK, linewidth=0.6, height=0.62)
    for b, hh in zip(bars.patches, hatch):
        if hh:
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yi, r, v in zip(y, rows, vals):
        if v == 0:
            txt = "1 GW cluster; GPU count not disclosed" if "Emirates" in r.country else \
                  ">$740M state support; GPU count not disclosed"
            ax.text(8000, yi, txt, va="center", fontsize=9, color=INK["text"], style="italic")
        else:
            who = str(r.counterparties).split(";")[0].split(",")[0].split("(")[0].strip()
            if who.startswith("Deutsche"):
                who = "Deutsche Telekom"
            if who.startswith("Government"):
                who = "Government + Samsung, SK, Hyundai, Naver"
            if who.startswith("HUMAIN"):
                who = "HUMAIN, over 3 years"
            ax.text(v + 8000, yi, f"{v:,.0f}  ·  {who}",
                    va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, labels, fontsize=9)
    ax.set_xlim(0, 900000)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(lambda v, _p: f"{v / 1000:,.0f}k")
    ax.grid(axis="x", color=INK["grid"], lw=0.6)
    ax.grid(axis="y", visible=False)
    _clean(ax)
    _left_margin(fig, 0.2)
    c.save(fig, ax, xlabel="NVIDIA GPUs named in the announcement")


# --------------------------------------------------------------------------------------
# 2. What a 100k-GPU national AI factory costs (waterfall build-up, Est.)
# --------------------------------------------------------------------------------------
@register
def l13_national_ai_factory_cost():
    m = factory_model()
    c = Chart(
        id="13-national-ai-factory-cost",
        title=(f"Est.: a 100k-GPU national AI factory costs ~${m['total']:.1f}B; NVIDIA invoices "
               f"~{m['nv_low'] / m['total'] * 100:.0f}-{m['nv_high'] / m['total'] * 100:.0f}%"),
        subtitle=(f"US$ B for {m['racks']:,} GB300 NVL72 racks, scale-out network, storage and a "
                  f"~{m['facility_mw']:.0f} MW liquid-cooled facility; all values estimates"),
        alt=(f"Waterfall chart estimating the up-front cost of a 100,000-GPU national AI factory built from "
             f"{m['racks']:,} GB300 NVL72 racks at about $3.99M each: NVIDIA GPUs about ${m['gpu']:.1f}B, HBM and LPDDR "
             f"memory about ${m['memory']:.1f}B, the rest of the rack (Grace CPUs, NVLink switch trays, boards, power, "
             f"cooling, ODM margin) about ${m['rest']:.1f}B, scale-out networking and storage about ${m['network']:.1f}B "
             f"and the facility shell and power plant for ~{m['facility_mw']:.0f} MW about ${m['facility']:.1f}B, "
             f"totalling about ${m['total']:.1f}B. NVIDIA would invoice an estimated ${m['nv_low']:.1f}-"
             f"{m['nv_high']:.1f}B; electricity adds ~${m['power_usd_m_yr']:.0f}M a year."),
        data=[TCO, FAC], chapters=CH + ["08", "14"],
        source="analyst rack estimates, Uptime, EIA; repo model", source_ids=m["sources"],
    )
    steps = [
        ("NVIDIA GPUs\n(B300, ex-memory)", m["gpu"], NV, "NVIDIA"),
        ("HBM3E + LPDDR5X\nmemory", m["memory"], GEN_PAST, "in NVIDIA's price;\nSK hynix, Samsung, Micron"),
        ("Rest of rack", m["rest"], LBLUE, "Grace, NVLink switches\n+ ODM/OEM, power, cooling"),
        ("Scale-out network\n+ storage", m["network"], BLUE, "NVIDIA switches/NICs\n+ storage, optics"),
        ("Facility, power\nand cooling plant", m["facility"], GRAY, "developer, utility,\nVertiv/Schneider class"),
    ]
    fig, ax = c.figure(width=11.0, height=6.2)
    base = 0.0
    for i, (lab, v, col, who) in enumerate(steps):
        ax.bar(i, v, bottom=base, color=col, edgecolor=INK["text"], linewidth=0.6, width=0.62, hatch="//")
        ax.text(i, base + v + 0.12, f"${v:.2f}B", ha="center", va="bottom", fontsize=10, fontweight="bold",
                color=INK["title"])
        wy = base + v / 2 if v > 1.0 else base / 2
        ax.text(i, wy, who, ha="center", va="center", fontsize=7.6, color=INK["title"],
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.85))
        if i < len(steps) - 1:
            ax.plot([i + 0.31, i + 0.69], [base + v, base + v], color=INK["base"], lw=1, ls="--")
        base += v
    n = len(steps)
    ax.bar(n, m["total"], color="#52514E", width=0.62, edgecolor=INK["title"], linewidth=0.6, hatch="//", alpha=0.85)
    ax.text(n, m["total"] + 0.12, f"${m['total']:.1f}B", ha="center", va="bottom", fontsize=11, fontweight="bold")
    # NVIDIA bracket
    ax.annotate("", xy=(n + 0.45, m["nv_low"]), xytext=(n + 0.45, 0),
                arrowprops=dict(arrowstyle="-", color=NV_DARK, lw=3))
    ax.text(n + 0.52, m["nv_low"] / 2, f"NVIDIA\n~${m['nv_low']:.1f}-{m['nv_high']:.1f}B", va="center",
            fontsize=9, color=NV_DARK, fontweight="bold")
    ax.set_xticks(range(n + 1), [s[0] for s in steps] + ["Total\nup-front"], fontsize=9)
    ax.set_xlim(-0.6, n + 1.25)
    ax.set_ylim(0, m["total"] * 1.12)
    ax.set_axisbelow(True)
    ax.text(-0.5, m["total"] * 1.06, "All bars Est.; facility $/MW from a Morgan Stanley model it later retracted (illustrative)",
            fontsize=8.2, color=INK["muted"], style="italic")
    ax.grid(axis="y", color=INK["grid"], lw=0.6)
    ax.grid(axis="x", visible=False)
    _clean(ax)
    c.save(fig, ax, ylabel="Cumulative cost, US$ B (Est.)", bottom=0.16)


# --------------------------------------------------------------------------------------
# 3. GTC attendance
# --------------------------------------------------------------------------------------
@register
def l13_gtc_attendance():
    d = load(ECO)
    g = d[d.metric == "gtc_attendees_in_person"].copy()
    g["year"] = g.date.astype(str).str[:4]
    first, last = g.iloc[0], g.iloc[-1]
    virt = d[(d.metric == "gtc_attendees_virtual")].value.max()
    c = Chart(
        id="13-gtc-attendance",
        title=(f"GTC grew ~{last.value / first.value:.0f}× from ~{first.value:,.0f} attendees (2009) to "
               f">{last.value / 1000:.0f}k expected in 2026"),
        subtitle="In-person attendees at the spring GTC in San Jose; 2024-26 are NVIDIA pre-event figures (no final counts published)",
        alt=("Bar chart of in-person attendance at NVIDIA's spring GTC: about 1,500 at the first GTC in 2009, more than "
             "16,000 projected for 2024, about 25,000 estimated by NVIDIA for 2025 with about 300,000 online, and more "
             "than 30,000 from over 190 countries expected for 2026, when the agenda listed 500+ sessions. Attendance "
             "grew about 20-fold, making GTC a launch platform for partners as well as NVIDIA."),
        data=[ECO], chapters=CH + ["01", "09"],
        source="NVIDIA announcements, press previews", source_ids=sources_of(d[d.record_type == "gtc"]),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(g))
    cols = [NV if y == g.year.iloc[-1] else GEN_PAST for y in g.year]
    ax.bar(x, g.value, color=cols, edgecolor=NV_DARK, linewidth=0.6, width=0.6)
    for xi, v, y in zip(x, g.value, g.year):
        lab = f">{v:,.0f}" if y in ("2024", "2026") else f"~{v:,.0f}"
        ax.text(xi, v + 500, lab, ha="center", va="bottom", fontsize=10, color=INK["title"], fontweight="bold")
    for xi, y in zip(x, g.year):
        if y in ("2024", "2025"):
            ax.text(xi, 6000, f"+ ~{virt / 1000:.0f}k\nonline", ha="center", fontsize=9, color=INK["title"],
                    fontweight="bold")
    ax.set_xticks(x, [f"GTC {y}" for y in g.year])
    ax.set_ylim(0, 34000)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(lambda v, _p: f"{v / 1000:,.0f}k")
    ax.grid(axis="y", color=INK["grid"], lw=0.6)
    ax.grid(axis="x", visible=False)
    _clean(ax)
    c.save(fig, ax, ylabel="In-person attendees")


# --------------------------------------------------------------------------------------
# 4. NVIDIA Inception membership
# --------------------------------------------------------------------------------------
@register
def l13_inception_members():
    d = load(ECO)
    i = d[d.metric == "inception_members"].copy()

    def dec(s: str) -> float:
        s = str(s)
        return int(s[:4]) + ((int(s[5:7]) - 0.5) / 12 if len(s) >= 7 else 0.5)
    i["x"] = i.date.map(dec)
    off = i[i.confidence != "estimate"]
    est = i[i.confidence == "estimate"]
    first, last_off, last = off.iloc[0], off.iloc[-1], i.iloc[-1]
    c = Chart(
        id="13-inception-members",
        title=(f"Inception grew {last_off.value / first.value:.0f}× to ~{last_off.value / 1000:.0f}k start-ups by "
               f"2022; secondary data say >{last.value / 1000:.0f}k by 2025"),
        subtitle="Member companies of NVIDIA's free start-up program (launched 2016); dashed = secondary estimate, not an NVIDIA figure",
        alt=("Line chart of NVIDIA Inception membership: 2,000 start-ups in 2017 (under 18 months after the 2016 launch), "
             "7,000 in December 2020 (+25% in a year), 8,500 in August 2021 from 90 countries with more than $60B raised, "
             "9,000 in late 2021 (about two-thirds of the world's AI start-ups by PitchBook's count) and about 10,000 in "
             "March 2022. A dashed segment shows a secondary, PitchBook-based estimate of more than 22,000 active members "
             "in 2025; NVIDIA has not published an official recent count."),
        data=[ECO], chapters=CH + ["01"],
        source="NVIDIA blogs and releases; press", source_ids=sources_of(i),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    ax.plot(off.x, off.value, color=NV, lw=2.2, marker="o", ms=8, zorder=3)
    ax.plot([last_off.x, est.x.iloc[0]], [last_off.value, est.value.iloc[0]], color=NV, lw=2, ls="--", zorder=2)
    ax.plot(est.x, est.value, ls="none", marker="o", ms=9, mfc="white", mec=NV_DARK, mew=2, zorder=3)
    for xv, v, dt, conf in zip(i.x, i.value, i.date, i.confidence):
        dy = -700 if v in (8500, 9000) else 500
        dx = {9000: 0.45, 10000: -0.15}.get(v, 0) - (0.25 if conf == "estimate" else 0)
        lab = f"{v:,.0f}\n({dt})" if conf != "estimate" else f">{v:,.0f} (2025, Est.)"
        ax.text(xv + dx, v + dy, lab, ha="center",
                va="bottom" if dy > 0 else "top", fontsize=8.6, color=INK["title"])
    ax.axvline(2016.4, color=INK["base"], lw=1, ls="--")
    ax.text(2016.5, 21000, "Program\nlaunched 2016", fontsize=8.5, color=INK["text"], va="top")
    ax.set_xlim(2016, 2026.2)
    ax.set_ylim(0, 25500)
    ax.yaxis.set_major_formatter(lambda v, _p: f"{v / 1000:,.0f}k")
    ax.grid(axis="y", color=INK["grid"], lw=0.6)
    _clean(ax)
    c.save(fig, ax, xlabel="Year", ylabel="Inception member start-ups")


# --------------------------------------------------------------------------------------
# 5. NVIDIA equity holdings
# --------------------------------------------------------------------------------------
@register
def l13_equity_holdings_growth():
    d = load(EQ)
    nm = d[d.metric == "non_marketable_equity"].reset_index(drop=True)
    last = d[d.period == "Q2FY27"].set_index("metric").value
    total = last["non_marketable_equity"] + last["marketable_equity"] + last["lockedup_public_equity"]
    buys = d[d.metric == "equity_purchases_half_year"].set_index("period").value
    c = Chart(
        id="13-equity-holdings-growth",
        title=(f"NVIDIA's private stakes grew {nm.value.iloc[-1] / nm.value.iloc[0]:.0f}× in 18 months to "
               f"${nm.value.iloc[-1]:.0f}B; all stakes ~${total:.0f}B"),
        subtitle="Carrying value of equity securities, US$ B, Jan 2025 - Jul 2026; hatched = secondary reading of the 10-Q",
        alt=(f"Bar chart of NVIDIA's non-marketable (private) equity securities: ${nm.value.iloc[0]:.1f}B at end-January "
             f"2025, ${nm.value.iloc[1]:.1f}B at end-January 2026, ${nm.value.iloc[2]:.1f}B in April 2026 and "
             f"${nm.value.iloc[3]:.1f}B in July 2026, about 15 times in 18 months. A final stacked bar adds "
             f"${last['marketable_equity']:.1f}B of marketable equity and ${last['lockedup_public_equity']:.1f}B of "
             f"locked-up public equity for about ${total:.0f}B in July 2026. Equity purchases were "
             f"${buys['H1FY27']:.1f}B in H1 FY2027 versus ${buys['H1FY26']:.1f}B a year earlier; much of the rest is "
             "mark-to-market gains."),
        data=[EQ], chapters=CH + ["12", "18"],
        source="NVIDIA 10-K/10-Q and secondary readings", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    labels = ["Jan 2025\n(FY2025 end)", "Jan 2026\n(FY2026 end)", "Apr 2026\n(Q1 FY2027)", "Jul 2026\n(Q2 FY2027)"]
    x = np.arange(len(nm))
    bars = ax.bar(x, nm.value, color=NV, edgecolor=NV_DARK, linewidth=0.6, width=0.6, label="Non-marketable (private) equity")
    for b, conf in zip(bars.patches, nm.confidence):
        if conf != "confirmed":
            b.set_hatch("///")
    for xi, v in zip(x, nm.value):
        ax.text(xi, v + 1.2, f"${v:.1f}B", ha="center", va="bottom", fontsize=10, fontweight="bold")
    xt = len(nm) + 0.3
    b0 = last["non_marketable_equity"]
    ax.bar(xt, b0, color=NV, edgecolor=NV_DARK, width=0.6, hatch="///")
    ax.bar(xt, last["marketable_equity"], bottom=b0, color=BLUE, edgecolor=INK["text"], width=0.6, hatch="///",
           label="Marketable equity (public stakes)")
    ax.bar(xt, last["lockedup_public_equity"], bottom=b0 + last["marketable_equity"], color=LBLUE,
           edgecolor=INK["text"], width=0.6, hatch="///", label="Locked-up public equity")
    ax.text(xt, total + 1.2, f"~${total:.0f}B", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.text(xt + 0.34, b0 + last["marketable_equity"] / 2, f"${last['marketable_equity']:.1f}B", va="center", fontsize=9)
    ax.set_xticks(list(x) + [xt], labels + ["Jul 2026\nall equity stakes"], fontsize=9)
    ax.set_ylim(0, total * 1.15)
    ax.set_axisbelow(True)
    ax.set_xlim(-0.6, xt + 0.9)
    ax.grid(axis="y", color=INK["grid"], lw=0.6)
    ax.grid(axis="x", visible=False)
    _clean(ax)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    c.save(fig, ax, ylabel="Carrying value, US$ B", legend=False)


# --------------------------------------------------------------------------------------
# 6. Data Center revenue by customer type (new FY2027 disclosure)
# --------------------------------------------------------------------------------------
@register
def l13_dc_revenue_by_customer_type():
    f = load(FIN)
    rows = f[f.metric.isin(["revenue_dc_hyperscale", "revenue_dc_acie"]) & f.period.isin(["Q1FY27", "Q2FY27"])]
    p = rows.pivot(index="period", columns="metric", values="value").loc[["Q1FY27", "Q2FY27"]]
    share = p.revenue_dc_acie / (p.revenue_dc_acie + p.revenue_dc_hyperscale)
    c = Chart(
        id="13-dc-revenue-by-customer-type",
        title=(f"Non-hyperscale buyers took ~${p.revenue_dc_acie.iloc[-1]:.0f}B, {share.iloc[-1]:.0%} of "
               f"Q2 FY2027 Data Center revenue"),
        subtitle="NVIDIA Data Center revenue by customer type, US$ B per quarter (new split from Q1 FY2027; rounded, per CFO commentary)",
        alt=(f"Stacked bar chart of NVIDIA Data Center revenue by customer type: Q1 FY2027 hyperscale about "
             f"${p.revenue_dc_hyperscale.iloc[0]:.0f}B and AI clouds, industrial and enterprise (ACIE) about "
             f"${p.revenue_dc_acie.iloc[0]:.0f}B ({share.iloc[0]:.0%}); Q2 FY2027 hyperscale about "
             f"${p.revenue_dc_hyperscale.iloc[1]:.1f}B and ACIE about ${p.revenue_dc_acie.iloc[1]:.1f}B "
             f"({share.iloc[1]:.0%}). Non-hyperscale buyers reached through partners and neoclouds are nearly half of "
             "Data Center demand."),
        data=[FIN], chapters=CH + ["12", "18"],
        source="NVIDIA Q1/Q2 FY2027 results and CFO commentary", source_ids=sources_of(rows),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(p))
    b1 = ax.bar(x, p.revenue_dc_hyperscale, color=GEN_PAST, edgecolor=NV_DARK, width=0.55, label="Hyperscale")
    b2 = ax.bar(x, p.revenue_dc_acie, bottom=p.revenue_dc_hyperscale, color=NV, edgecolor=NV_DARK, width=0.55,
                label="AI clouds, industrial and enterprise (ACIE)")
    for xi, h, a, s in zip(x, p.revenue_dc_hyperscale, p.revenue_dc_acie, share):
        ax.text(xi, h / 2, f"${h:.1f}B", ha="center", va="center", fontsize=10, color=INK["title"])
        ax.text(xi, h + a / 2, f"${a:.1f}B\n({s:.0%})", ha="center", va="center", fontsize=10, color="white",
                fontweight="bold")
        ax.text(xi, h + a + 1.5, f"${h + a:.0f}B", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_xticks(x, ["Q1 FY2027\n(Feb-Apr 2026)", "Q2 FY2027\n(May-Jul 2026)"])
    ax.set_ylim(0, 105)
    ax.set_axisbelow(True)
    ax.set_xlim(-0.7, 1.7)
    ax.grid(axis="y", color=INK["grid"], lw=0.6)
    ax.grid(axis="x", visible=False)
    _clean(ax)
    ax.legend(handles=[Patch(color=NV, label="AI clouds, industrial and enterprise (ACIE)"),
                       Patch(color=GEN_PAST, label="Hyperscale")], loc="upper left", frameon=False, fontsize=9)
    c.save(fig, ax, ylabel="Revenue per quarter, US$ B", legend=False)
