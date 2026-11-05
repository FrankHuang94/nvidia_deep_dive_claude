"""TCO model inputs (chapter 14) - agent A3.

Reads data/tco_model_inputs.csv, data/system_specs.csv, data/gpu_rental_prices.csv and
data/depreciation_useful_lives.csv. These charts show the *inputs*; the TCO model itself lives in
scripts/tco/.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, hatch_future, load, register,
                   sources_of)

TCO = "tco_model_inputs.csv"
SYS = "system_specs.csv"
RENT = "gpu_rental_prices.csv"
DEP = "depreciation_useful_lives.csv"


def manual_axes(fig, rects):
    for a in list(fig.axes):
        fig.delaxes(a)
    return [fig.add_axes(r) for r in rects]


def _row(t, system, inp, basis=None):
    r = t[(t.system == system) & (t.input == inp)]
    if basis:
        r = r[r.basis.str.contains(basis, regex=False)]
    return r.iloc[0]


# --------------------------------------------------------------------------------------
@register
def gpu_rental_price_trend():
    r = load(RENT)
    r["when"] = pd.to_datetime(r["date"] + "-15")
    h = r[r.gpu == "H100"]
    peak = h[h.provider_type == "neocloud"].usd_per_gpu_hour.max()
    low = h[h.provider_type == "marketplace"].usd_per_gpu_hour.min()
    aws = h[h.provider.str.startswith("AWS")].sort_values("when")
    aws_cut = 1 - aws.usd_per_gpu_hour.iloc[-1] / aws.usd_per_gpu_hour.iloc[0]
    c = Chart(
        id="14-gpu-rental-price-trend",
        title=(f"H100 rentals fell ~{(1 - low / peak) * 100:.0f}% from ~${peak:.0f}/GPU-hr (2023) to ~${low:.0f}–3 on neoclouds; "
               f"AWS list −{aws_cut * 100:.0f}%"),
        subtitle="On-demand list/observed prices, US$ per GPU-hour (instance ÷ GPUs) · marker = provider type · contract rates are lower",
        alt=(f"Scatter chart of GPU rental prices over time. H100: AWS p5 on-demand ${aws.usd_per_gpu_hour.iloc[0]:.2f} per GPU-hour at "
             f"launch in July 2023 and ${aws.usd_per_gpu_hour.iloc[-1]:.2f} after the June 2025 cut; neocloud H100 about ${peak:.0f} "
             f"in 2023, marketplaces under ${low:.0f} by late 2024, Lambda $2.99 and CoreWeave $6.16 list in 2025. Blackwell list "
             f"prices in 2025: B200 $4.99 (Lambda) to $8.60 (CoreWeave), GB200 $10.50 (CoreWeave)."),
        data=[RENT], chapters=["14", "12"],
        source="AWS, CoreWeave, Lambda, Latent Space",
        source_ids=sources_of(r),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    markers = {"hyperscaler": "s", "neocloud": "o", "marketplace": "^"}
    gcol = {"H100": GEN_PAST, "B200": NV, "GB200": NV_DARK}
    ax.plot(aws.when, aws.usd_per_gpu_hour, color=INK["muted"], lw=1.4, ls="--", zorder=1)
    trend = h[h.provider_type.isin(["neocloud", "marketplace"]) & ~h.provider.str.startswith("CoreWeave")].sort_values("when")
    ax.plot(trend.when, trend.usd_per_gpu_hour, color=GEN_PAST, lw=2, zorder=1)
    for _, row in r.iterrows():
        ax.scatter(row.when, row.usd_per_gpu_hour, marker=markers[row.provider_type], s=85, color=gcol[row.gpu],
                   edgecolor=INK["title"], linewidth=0.8, zorder=3)
        lab = f"{row.gpu} · {row.provider.split(' (')[0]} ${row.usd_per_gpu_hour:.2f}"
        dx, ha = (8, "left")
        if row.when >= pd.Timestamp("2025-05-01"):
            dx, ha = (-8, "right")
        dy = 0
        if row.gpu == "B200" and row.provider.startswith("Lambda"):
            dy = -8
        ax.annotate(lab, (row.when, row.usd_per_gpu_hour), xytext=(dx, dy), textcoords="offset points", ha=ha,
                    va="center", fontsize=8.2, color=INK["title"] if row.gpu == "H100" else NV_DARK)
    ax.set_ylim(0, 14)
    ax.set_xlim(pd.Timestamp("2023-04-01"), pd.Timestamp("2025-12-31"))
    handles = [Line2D([0], [0], marker=m, ls="", color="white", markeredgecolor=INK["title"], markerfacecolor=INK["grid"],
                      markersize=8, label=k.capitalize()) for k, m in markers.items()]
    handles += [Patch(facecolor=GEN_PAST, edgecolor=INK["title"], label="H100 (Hopper)"),
                Patch(facecolor=NV, edgecolor=INK["title"], label="B200"),
                Patch(facecolor=NV_DARK, edgecolor=INK["title"], label="GB200 NVL72")]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=8.6, ncol=2)
    c.save(fig, ax, ylabel="US$ per GPU-hour", legend=False)


# --------------------------------------------------------------------------------------
@register
def capex_per_accelerator_by_system():
    s = load(SYS)
    t = load(TCO)
    names = [("DGX-1 (P100)", "DGX-1 P100\n2016"), ("DGX-1 (V100)", "DGX-1 V100\n2017"), ("DGX-2", "DGX-2\n2018"),
             ("DGX A100", "DGX A100\n2020"), ("HGX H200 8-GPU server (Supermicro OEM)", "HGX H200\nOEM 2024"),
             ("DGX H200", "DGX H200\n2024"), ("DGX B200", "DGX B200\n2024"), ("GB200 NVL72", "GB200\nNVL72 2024"),
             ("GB300 NVL72", "GB300\nNVL72 2025"), ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin\nNVL72 2026")]
    d = s.set_index("system").loc[[n for n, _ in names]].reset_index()
    d["label"] = [lab for _, lab in names]
    d["per_gpu_k"] = d.est_price_usd_m * 1000 / d.accelerators_per_system
    # alternative rack estimates (dots)
    alt_map = {"GB200 NVL72": "GB200 NVL72", "GB300 NVL72": "GB300 NVL72",
               "Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)": "Vera Rubin NVL72"}
    alts = t[t.system.isin(alt_map.values()) & t.input.str.startswith("capex_per_rack")].copy()
    gb3 = d[d.system == "GB300 NVL72"].per_gpu_k.iloc[0]
    vr = d[d.label.str.startswith("Vera")].per_gpu_k.iloc[0]
    c = Chart(
        id="14-capex-per-accelerator-by-system",
        title=f"Est. capex per GPU roughly doubles from GB300 NVL72 (~${gb3:.0f}K) to Vera Rubin NVL72 (~${vr:.0f}K)",
        subtitle="System/rack price ÷ GPUs, US$ K (bar = central estimate; dots = other estimates; hatched = analyst Est.) · AMD/Google/AWS prices not public",
        alt=(f"Bar chart of capex per GPU: DGX-1 P100 about $16K (2016), DGX-1 V100 $19K, DGX-2 $25K, DGX A100 $25K, HGX H200 OEM about "
             f"$40K, DGX H200 about $58K, DGX B200 about $46K, GB200 NVL72 about $42K, GB300 NVL72 about ${gb3:.0f}K and Vera Rubin "
             f"NVL72 about ${vr:.0f}K per GPU, with alternative analyst estimates from about $39K to $126K shown as dots. "
             f"No public system prices exist for AMD, Google or AWS racks."),
        data=[SYS, TCO], chapters=["14", "08", "13"],
        source="resellers, HSBC, SemiAnalysis, Morgan Stanley, Bernstein",
        source_ids=sources_of(pd.concat([d, alts])),
    )
    fig, ax = c.figure(width=11, height=6.0)
    x = np.arange(len(d))
    cols = [GEN_PAST] * 7 + [NV] * 3
    b = ax.bar(x, d.per_gpu_k, color=cols, width=0.64, zorder=2)
    hatch_future(b, [i >= 7 for i in range(len(d))])
    for i, v in enumerate(d.per_gpu_k):
        ax.annotate(f"${v:.0f}K", (i, v), xytext=(-12 if i >= 7 else 0, 3), textcoords="offset points", ha="center",
                    va="bottom", fontsize=9, color=INK["title"], fontweight="bold")
    for sysname, short in alt_map.items():
        xi = d.index[d.system == sysname][0]
        vals = alts[alts.system == short].value.values * 1000 / 72
        ax.scatter([xi + 0.12] * len(vals), vals, s=26, color="white", edgecolor=INK["title"], linewidth=1.1, zorder=4)
        ax.plot([xi + 0.12, xi + 0.12], [vals.min(), vals.max()], color=INK["title"], lw=1, zorder=3)
    ax.set_xticks(x, d.label, fontsize=8.4)
    ax.set_ylim(0, 140)
    ax.legend(handles=[Patch(facecolor=GEN_PAST, label="8/16-GPU server (list/reseller price)"),
                       Patch(facecolor=NV, hatch="///", edgecolor="white", alpha=0.75, label="72-GPU rack (central analyst Est.)"),
                       Line2D([0], [0], marker="o", ls="-", color=INK["title"], markerfacecolor="white", markersize=6,
                              label="Range of other published rack estimates")],
              loc="upper left", frameon=False, fontsize=8.8)
    c.save(fig, ax, ylabel="US$ K per GPU", legend=False, bottom=0.15)


# --------------------------------------------------------------------------------------
@register
def depreciation_life_assumptions():
    dep = load(DEP)
    keep = {"Microsoft": "servers and network equipment", "Alphabet": "servers", "Amazon": None, "Meta": None,
            "CoreWeave": None}
    colors = {"Microsoft": entity_color("Microsoft"), "Alphabet": entity_color("Google"), "Amazon": entity_color("AWS"),
              "Meta": entity_color("Meta"), "CoreWeave": entity_color("startups")}
    marks = {"Microsoft": "s", "Alphabet": "o", "Amazon": "^", "Meta": "D", "CoreWeave": "v"}
    offs = {"Microsoft": 0.06, "Alphabet": -0.06, "Amazon": 0.0, "Meta": 0.0, "CoreWeave": 0.12}
    c = Chart(
        id="14-depreciation-life-assumptions",
        title="Hyperscalers stretched server lives to 5.5–6 years, but Amazon cut some back to 5 in 2025",
        subtitle="Useful life used to depreciate servers (and network gear where combined), years, by effective date of each 10-K change",
        alt=("Step chart of server useful lives: Microsoft 3 to 4 years (July 2020) and 6 years (July 2022); Alphabet 3 to 4 years "
             "(2021) and 6 years (2023); Amazon 3 to 4 (2020), 5 (2022), 6 (2024) and back to 5 years for part of its servers in "
             "2025; Meta 4 to 4.5 years (2022) and 5.5 years (2025); CoreWeave 6 years for GPU servers since 2023."),
        data=[DEP], chapters=["14", "18", "12"],
        source="10-K and S-1 filings via SEC EDGAR",
        source_ids=sources_of(dep),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    end = pd.Timestamp("2026-12-31")
    start = pd.Timestamp("2019-01-01")
    for co in ["Amazon", "Meta", "CoreWeave", "Alphabet", "Microsoft"]:
        dd = dep[dep.company == co]
        if keep[co]:
            dd = dd[dd.asset_class == keep[co]]
        dd = dd.sort_values("effective_date")
        st = pd.Timestamp("2021-01-01") if co == "CoreWeave" else start
        dts = [st] + list(pd.to_datetime(dd.effective_date)) + [end]
        vals = [dd.prior_life_years.iloc[0]] + list(dd.useful_life_years) + [dd.useful_life_years.iloc[-1]]
        vals = np.array(vals, dtype=float) + offs[co]
        ax.step(dts, vals, where="post", color=colors[co], lw=2.2, zorder=2)
        ax.scatter(pd.to_datetime(dd.effective_date), dd.useful_life_years + offs[co], marker=marks[co], s=60,
                   color=colors[co], edgecolor="white", zorder=3)
        ly = {"CoreWeave": 6.42, "Microsoft": 6.2, "Alphabet": 5.94}.get(co, vals[-1])
        ax.annotate(f"{co} {dd.useful_life_years.iloc[-1]:g}y", (end, vals[-1]), xytext=(pd.Timestamp("2027-01-20"), ly),
                    textcoords="data", va="center", fontsize=9, color=colors[co], fontweight="bold")
    ax.annotate("Amazon: 6 → 5 years for part of\nservers & networking (AI pace)", (pd.Timestamp("2025-01-01"), 5.0),
                xytext=(pd.Timestamp("2023-03-01"), 4.25), fontsize=8.6, color=INK["text"],
                arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.set_xlim(start, pd.Timestamp("2027-10-01"))
    ax.set_ylim(2.5, 6.7)
    ax.set_yticks([3, 4, 4.5, 5, 5.5, 6])
    c.save(fig, ax, ylabel="Useful life (years)", xlabel="Effective date", legend=False)


# --------------------------------------------------------------------------------------
@register
def rack_price_estimates_range():
    t = load(TCO)
    systems = ["GB200 NVL72", "GB300 NVL72", "Vera Rubin NVL72"]
    d = t[t.system.isin(systems) & t.input.str.startswith("capex_per_rack")].copy()
    rng = {s: (d[d.system == s].value.min(), d[d.system == s].value.max()) for s in systems}
    c = Chart(
        id="14-rack-price-estimates-range",
        title=(f"NVL72 rack price estimates: ~${rng['GB200 NVL72'][0]:.1f}–{rng['GB200 NVL72'][1]:.1f}M (GB200), "
               f"${rng['GB300 NVL72'][0]:.1f}–{rng['GB300 NVL72'][1]:.1f}M (GB300), ${rng['Vera Rubin NVL72'][0]:.0f}–"
               f"{rng['Vera Rubin NVL72'][1]:.1f}M (Vera Rubin)"),
        subtitle="Each published estimate of price per rack, US$ M · ◆ = analyst/BOM estimate, ○ = end of a quoted media range · all Est.",
        alt=(f"Dot plot of NVL72 rack price estimates. GB200 NVL72: ${rng['GB200 NVL72'][0]:.1f}M to ${rng['GB200 NVL72'][1]:.1f}M "
             f"including networking and storage (HSBC $3.0M, SemiAnalysis $3.1M). GB300 NVL72: Morgan Stanley $3.99M, Wolfe $4.3M, "
             f"Data Gravity $5.0M, media $6.0-6.5M. Vera Rubin NVL72: quotes from $5.0M, Morgan Stanley $7.8M ($6.7M if CSPs buy "
             f"memory directly), up to $8.8M reported and Bernstein $9.1M."),
        data=[TCO], chapters=["14", "08", "18"],
        source="HSBC, SemiAnalysis, Wolfe, Morgan Stanley, Bernstein, press",
        source_ids=sources_of(d),
    )
    fig, _ = c.figure(width=10.5, height=6.6)
    ax = manual_axes(fig, [[0.37, 0.12, 0.59, 0.72]])[0]
    rows, ylabels, y = [], [], 0
    gap_rows = []
    for s in systems[::-1]:
        dd = d[d.system == s].sort_values("value", ascending=False)
        for _, r in dd.iterrows():
            who = r.basis.split(", ", 1)[1] if ", " in r.basis else r.basis
            if r.input == "capex_per_rack_all_in":
                who = "SemiAnalysis, incl. network + storage"
            elif r.input.endswith("_low"):
                who = who + " (low)"
            elif r.input.endswith("_high"):
                who = who + " (high)"
            who = who.replace("ODM price to CSP, ", "").replace("per rack if CSP buys SOCAMM memory directly, ",
                                                                   "if CSP buys memory directly, ")
            ylabels.append(f"{s.replace(' NVL72', '')} · {who}")
            rows.append((y, r, s))
            y += 1
        gap_rows.append(y)
        y += 0.6
    for yi, r, s in rows:
        media = r.input.endswith(("_low", "_high"))
        col = GEN_PAST if s.startswith("GB200") else (NV if s.startswith("GB300") else NV_DARK)
        ax.plot([0, r.value], [yi, yi], color=INK["grid"], lw=1, zorder=1)
        ax.scatter(r.value, yi, marker="o" if media else "D", s=62, color="white" if media else col,
                   edgecolor=NV_DARK, linewidth=1.3, zorder=3)
        ax.annotate(f"${r.value:g}M", (r.value, yi), xytext=(7, 0), textcoords="offset points", va="center",
                    fontsize=8.6, color=INK["title"])
    ax.set_yticks([yi for yi, _, _ in rows], ylabels, fontsize=8.4)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(-0.8, y - 0.4)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="US$ M per rack", legend=False)


# --------------------------------------------------------------------------------------
@register
def capex_vs_power_cost_per_gpu_year():
    s = load(SYS)
    t = load(TCO)
    life = _row(t, "All", "server_useful_life_years", "since FY2023")  # Microsoft: 6 years
    price_kwh = _row(t, "All", "electricity_price_us_industrial")
    lo_kwh = _row(t, "All", "electricity_price_low")
    hi_kwh = _row(t, "All", "electricity_price_high")
    pue_air = _row(t, "All", "pue_assumption_air_cooled")
    pue_liq = _row(t, "All", "pue_assumption_liquid_cooled")
    names = [("DGX H200", "DGX H200 (air)", "air"), ("DGX B200", "DGX B200 (air)", "air"),
             ("GB200 NVL72", "GB200 NVL72", "liquid"), ("GB300 NVL72", "GB300 NVL72", "liquid"),
             ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin NVL72 (Est.)", "liquid")]
    d = s.set_index("system").loc[[n for n, _, _ in names]].reset_index()
    d["label"] = [lab for _, lab, _ in names]
    d["pue"] = [pue_air.value if k == "air" else pue_liq.value for _, _, k in names]
    d["capex_yr"] = d.est_price_usd_m * 1e6 / d.accelerators_per_system / life.value
    kw = d.power_kw / d.accelerators_per_system * d.pue
    d["power_yr"] = kw * 8760 * price_kwh.value
    d["power_lo"] = kw * 8760 * lo_kwh.value
    d["power_hi"] = kw * 8760 * hi_kwh.value
    d["share"] = d.power_yr / (d.power_yr + d.capex_yr)
    used = pd.concat([d, pd.DataFrame([life, price_kwh, lo_kwh, hi_kwh, pue_air, pue_liq])])
    c = Chart(
        id="14-capex-vs-power-cost-per-gpu-year",
        title=(f"Depreciation dominates: electricity is only ~{d.share.min() * 100:.0f}–{d.share.max() * 100:.0f}% "
               f"of a GPU's yearly cost at ${price_kwh.value:.3f}/kWh"),
        subtitle=(f"US$ K per GPU-year: capex ÷ {life.value:g}-yr life + max IT power × PUE ({pue_air.value:g} air / "
                  f"{pue_liq.value:g} liquid) × 8,760 h · whiskers = ${lo_kwh.value:.2f}–{hi_kwh.value:.2f}/kWh"),
        alt=("Stacked horizontal bars of yearly cost per GPU: straight-line depreciation of the system price over six years plus "
             f"electricity at full power. Electricity is about {d.share.min() * 100:.0f}-{d.share.max() * 100:.0f}% of the total: "
             f"DGX H200 about ${d.capex_yr.iloc[0] / 1e3:.1f}K capex plus ${d.power_yr.iloc[0] / 1e3:.1f}K power; GB300 NVL72 about "
             f"${d.capex_yr.iloc[3] / 1e3:.1f}K plus ${d.power_yr.iloc[3] / 1e3:.1f}K; Vera Rubin NVL72 about "
             f"${d.capex_yr.iloc[4] / 1e3:.1f}K plus ${d.power_yr.iloc[4] / 1e3:.1f}K (estimates)."),
        data=[SYS, TCO], chapters=["14", "08"],
        source="repo system data; EIA; Uptime; 10-Ks (repo calc)",
        source_ids=sources_of(used),
    )
    fig, _ = c.figure(width=10.5, height=5.8)
    ax = manual_axes(fig, [[0.2, 0.14, 0.76, 0.68]])[0]
    y = np.arange(len(d))[::-1]
    b1 = ax.barh(y, d.capex_yr / 1e3, color=[GEN_PAST, GEN_PAST, GEN_PAST, NV, NV], height=0.6, zorder=2,
                 label="Depreciation (capex ÷ life)")
    hatch_future(b1, [False, False, False, False, True])
    b2 = ax.barh(y, d.power_yr / 1e3, left=d.capex_yr / 1e3, color="#C98500", height=0.6, zorder=2,
                 label="Electricity at max power × PUE")
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.plot([(r.capex_yr + r.power_lo) / 1e3, (r.capex_yr + r.power_hi) / 1e3], [yi, yi], color=INK["title"], lw=1.2, zorder=3)
        ax.annotate(f"${(r.capex_yr + r.power_yr) / 1e3:.1f}K  (power {r.share * 100:.0f}%)",
                    ((r.capex_yr + r.power_hi) / 1e3, yi), xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=8.8, color=INK["title"])
    ax.set_yticks(y, d.label, fontsize=9.4)
    ax.set_xlim(0, (d.capex_yr + d.power_hi).max() / 1e3 * 1.35)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.text(0.99, 0.02, "Excludes facility capex, networking, staff and financing", transform=ax.transAxes, ha="right",
            va="bottom", fontsize=8.4, color=INK["muted"], style="italic")
    c.save(fig, ax, xlabel="US$ K per GPU per year", legend=False)
