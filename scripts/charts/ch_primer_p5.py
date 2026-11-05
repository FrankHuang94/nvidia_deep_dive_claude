"""Primer P5 - chip economics 101: wafer prices, yield model, cost build-up, HBM share, TSMC capex.

All inputs come from data/P5_wafer_economics.csv (cited estimates). The yield and cost-per-die
charts are *computed* from a documented model:

  gross dies per wafer   DPW = pi*(d/2)^2/S - pi*d/sqrt(2*S)      (d = wafer diameter mm, S = die mm2)
  Poisson yield          Y   = exp(-A*D0)                         (A = die area cm2, D0 = defects/cm2)
  Murphy yield           Y   = ((1 - exp(-A*D0)) / (A*D0))**2
  cost per good die      = wafer price / (DPW * Y)

The model ignores scribe lines, edge exclusion and die harvesting (selling partly defective dies
with units disabled), so it is a teaching approximation, not a foundry quote.
"""
from __future__ import annotations

import math

import numpy as np

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, hatch_future, label_bars, load,
                   register, sources_of)

CSV = "P5_wafer_economics.csv"
CH = ["P5", "02", "03"]


def _df():
    return load(CSV)


def dies_per_wafer(area_mm2: float, diameter_mm: float = 300.0) -> float:
    return math.pi * (diameter_mm / 2) ** 2 / area_mm2 - math.pi * diameter_mm / math.sqrt(2 * area_mm2)


def poisson_yield(area_mm2: float, d0_per_cm2: float) -> float:
    return math.exp(-area_mm2 / 100.0 * d0_per_cm2)


def murphy_yield(area_mm2: float, d0_per_cm2: float) -> float:
    ad = area_mm2 / 100.0 * d0_per_cm2
    return ((1 - math.exp(-ad)) / ad) ** 2 if ad > 0 else 1.0


def _param(df, item):
    r = df[(df.record_type == "model_param") & (df.item == item)]
    return float(r.value.iloc[0])


# --------------------------------------------------------------------------------------
@register
def wafer_price_by_node():
    df = _df()
    d = df[df.record_type == "wafer_price"].copy()
    order = ["N7", "N5/N4", "N3", "N2", "A16"]
    hvm = {"N7": "2018", "N5/N4": "2020", "N3": "2022", "N2": "2025", "A16": "H2 2026"}
    med = d.groupby("item").value.median().reindex(order)
    lo = d.groupby("item").value.min().reindex(order)
    hi = d.groupby("item").value.max().reindex(order)
    ratio = med["N2"] / med["N7"]
    c = Chart(
        id="P5-wafer-price-by-node",
        title=f"A leading-edge wafer costs ~{ratio:.0f}× more at N2 (~${med['N2']/1e3:.0f}K) than at N7 (~${med['N7']/1e3:.1f}K)",
        subtitle="Est. price per 300 mm TSMC wafer, US$ (bar = median of published estimates; dots = individual estimates; hatched = rumor)",
        alt=(f"Bar chart of estimated TSMC wafer prices by node: N7 about ${round(med['N7'], -2):,.0f}, N5/N4 about "
             f"${round(med['N5/N4'], -2):,.0f}, N3 about ${med['N3']:,.0f}, N2 about ${med['N2']:,.0f} and a rumored "
             f"${med['A16']:,.0f} for A16, so a wafer costs roughly {ratio:.0f} times more at N2 than at N7."),
        data=[CSV], chapters=CH,
        source="CSET, Tom's Hardware, TechNode, Epoch AI, others", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.8)
    x = np.arange(len(order))
    colors = [SEQ_BLUE[2], SEQ_BLUE[3], SEQ_BLUE[4], SEQ_BLUE[6], SEQ_BLUE[7]]
    bars = ax.bar(x, med.values, color=colors, width=0.6, zorder=2)
    hatch_future(bars, [n == "A16" for n in order])
    for i, n in enumerate(order):
        pts = d[d.item == n].value.values
        ax.scatter([i] * len(pts), pts, s=34, color=INK["title"], zorder=3, marker="o",
                   facecolors="white", linewidths=1.3)
        if hi[n] > lo[n]:
            ax.plot([i, i], [lo[n], hi[n]], color=INK["text"], lw=1.2, zorder=3)
        ax.annotate(f"${med[n]/1e3:.1f}K" if med[n] < 10000 else f"${med[n]/1e3:.0f}K",
                    (i, max(hi[n], med[n])), xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold", color=INK["title"])
    ax.set_xticks(x)
    ax.set_xticklabels([f"{n}\n(volume {hvm[n]})" for n in order])
    ax.set_ylim(0, 52000)
    ax.yaxis.set_major_formatter(lambda v, _: f"${v/1e3:.0f}K")
    c.save(fig, ax, xlabel="TSMC process node (first volume production)", ylabel="US$ per 300 mm wafer", bottom=0.16)


# --------------------------------------------------------------------------------------
@register
def yield_vs_die_area():
    df = _df()
    p = df[df.record_type == "model_param"]
    d_lo, d_mid, d_hi = (_param(df, k) for k in ("defect_density_low", "defect_density_mid", "defect_density_high"))
    reticle = _param(df, "reticle_limit")
    reticle_hn = _param(df, "reticle_limit_high_na")
    h100 = float(df[(df.record_type == "die") & (df.metric == "die_area_mm2") & df.item.str.startswith("GH100")].value.iloc[0])
    y_h100 = poisson_yield(h100, d_mid)
    y_phone = poisson_yield(100, d_mid)
    c = Chart(
        id="P5-yield-vs-die-area",
        title=f"An {h100:.0f} mm² GPU die yields ~{y_h100:.0%} vs ~{y_phone:.0%} for a 100 mm² phone chip",
        subtitle=f"Modelled share of defect-free dies vs die area; central case D0 = {d_mid:.1f} defects/cm² (Poisson and Murphy models; no harvesting)",
        alt=(f"Line chart of modelled die yield versus die area: at {d_mid} defects per square centimetre yield falls "
             f"from about {y_phone:.0%} for a 100 mm2 die to about {y_h100:.0%} for an {h100:.0f} mm2 H100-class die; "
             f"at {d_hi} defects it is about {poisson_yield(h100, d_hi):.0%}; the reticle limit of {reticle:.0f} mm2 caps die size."),
        data=[CSV], chapters=CH,
        source="repo yield model; parameters from CSET, SemiEngineering, Epoch AI", source_ids=sources_of(p),
    )
    fig, ax = c.figure(width=10, height=5.9)
    a = np.linspace(20, 900, 300)
    for d0, col, lab in ((d_lo, SEQ_BLUE[3], f"D0 = {d_lo:.2f} (mature node)"),
                         (d_mid, SEQ_BLUE[5], f"D0 = {d_mid:.2f} (central case)"),
                         (d_hi, SEQ_BLUE[7], f"D0 = {d_hi:.2f} (early ramp)")):
        ax.plot(a, [poisson_yield(v, d0) * 100 for v in a], color=col, lw=2.2, label=f"Poisson, {lab}")
    ax.plot(a, [murphy_yield(v, d_mid) * 100 for v in a], color=SEQ_BLUE[5], lw=1.8, ls="--",
            label=f"Murphy, D0 = {d_mid:.2f}")
    ax.axvline(reticle, color=INK["title"], lw=1.4, ls="-")
    ax.text(reticle - 6, 97, f"Reticle limit\n{reticle:.0f} mm²", ha="right", va="top", fontsize=8.8, color=INK["title"])
    ax.axvline(reticle_hn, color=INK["muted"], lw=1.2, ls=":")
    ax.text(reticle_hn + 6, 97, f"High-NA EUV field\n{reticle_hn:.0f} mm²", ha="left", va="top", fontsize=8.8, color=INK["text"])
    ax.scatter([100], [y_phone * 100], s=70, color=INK["text"], zorder=4)
    ax.annotate(f"Phone SoC ~100 mm²\n~{y_phone:.0%} good", (100, y_phone * 100), xytext=(55, -130),
                textcoords="offset points", fontsize=8.8, color=INK["text"],
                arrowprops=dict(arrowstyle="-", color=INK["muted"]))
    ax.scatter([h100], [y_h100 * 100], s=80, color=NV, zorder=4, edgecolor=NV_DARK)
    ax.annotate(f"H100 die {h100:.0f} mm²\n~{y_h100:.0%} good", (h100, y_h100 * 100), xytext=(-120, -50),
                textcoords="offset points", fontsize=8.8, color=NV_DARK, fontweight="bold",
                arrowprops=dict(arrowstyle="-", color=NV_DARK))
    ax.set_xlim(0, 900)
    ax.set_ylim(0, 100)
    ax.legend(loc="lower left", fontsize=8.6)
    c.save(fig, ax, xlabel="Die area (mm²)", ylabel="Defect-free dies (% of dies on wafer)", legend=False)


# --------------------------------------------------------------------------------------
@register
def cost_per_good_die():
    df = _df()
    wafer = float(df[(df.record_type == "wafer_price") & (df.source_id == "S35020")].value.iloc[0])
    d0 = _param(df, "defect_density_mid")
    areas = [100, 200, 400, 600, 814]
    rows = []
    for s in areas:
        g = math.floor(dies_per_wafer(s))
        y = poisson_yield(s, d0)
        good = g * y
        rows.append((s, g, y, good, wafer / good))
    small, big = rows[0], rows[-1]
    ratio = big[4] / small[4]
    used = df[(df.source_id == "S35020") & (df.record_type == "wafer_price") | (df.item == "defect_density_mid")]
    c = Chart(
        id="P5-cost-per-good-die",
        title=f"An 8× bigger die costs ~{ratio:.0f}× more: ~${small[4]:,.0f} for 100 mm² vs ~${big[4]:,.0f} for 814 mm²",
        subtitle=f"Modelled silicon cost per defect-free die, ${wafer/1e3:.0f}K 4N-class wafer, {d0:.1f} defects/cm², US$ (excl. test, packaging, harvesting)",
        alt=(f"Bar chart of modelled cost per good die on a ${wafer:,.0f} wafer: about ${small[4]:,.0f} for a 100 mm2 die "
             f"({small[3]:.0f} good dies per wafer) rising to about ${big[4]:,.0f} for an 814 mm2 die ({big[3]:.0f} good dies), "
             f"roughly {ratio:.0f} times more for eight times the area."),
        data=[CSV], chapters=CH,
        source="repo model; wafer price assumption from Epoch AI", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(rows))
    cols = [SEQ_BLUE[2], SEQ_BLUE[3], SEQ_BLUE[4], SEQ_BLUE[5], NV]
    bars = ax.bar(x, [r[4] for r in rows], color=cols, width=0.6, zorder=2)
    for i, r in enumerate(rows):
        ax.annotate(f"${r[4]:,.0f}", (i, r[4]), xytext=(0, 4), textcoords="offset points", ha="center",
                    va="bottom", fontsize=10, fontweight="bold", color=INK["title"])
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r[0]} mm²" + (" (H100-class)" if r[0] == 814 else " (phone SoC)" if r[0] == 100 else "")
                        + f"\n{r[1]} gross → {r[3]:.0f} good dies\n${r[4]/r[0]:.2f} per mm²" for r in rows], fontsize=8.8)
    ax.set_ylim(0, big[4] * 1.15)
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}")
    c.save(fig, ax, xlabel="Die area (mm²), gross and good dies per 300 mm wafer, silicon cost per good mm²",
           ylabel="Silicon cost per good die (US$)", bottom=0.24)


# --------------------------------------------------------------------------------------
@register
def gpu_cost_build_up_waterfall():
    df = _df()
    b = df[(df.record_type == "bom") & (df.item == "B200")].set_index("metric")
    pr = df[(df.record_type == "price") & (df.item == "B200")].set_index("metric")
    price = (pr.loc["selling_price_low", "value"] + pr.loc["selling_price_high", "value"]) / 2
    steps = [("Logic dies\n(2× 4NP)", b.loc["logic_dies", "value"]),
             ("HBM3E\n192 GB", b.loc["hbm", "value"]),
             ("CoWoS-L\npackaging", b.loc["advanced_packaging", "value"]),
             ("Packaging\nyield loss", b.loc["packaging_yield_loss", "value"]),
             ("Substrate,\ntest, other", b.loc["substrate_test_other", "value"])]
    total = b.loc["total_manufacturing_cost", "value"]
    gp = price - total
    gm = gp / price
    used = df[((df.record_type == "bom") | (df.record_type == "price")) & (df.item == "B200")]
    c = Chart(
        id="P5-gpu-cost-build-up-waterfall",
        title=f"Est. ~${total/1e3:.1f}K to build a B200 vs a ~$30–40K price; HBM is the biggest cost",
        subtitle="Est. unit manufacturing cost and implied gross profit per B200 GPU package, US$ (price = midpoint of CEO's range; hatched = Est.)",
        alt=(f"Waterfall chart of an estimated B200 cost build-up: logic dies about ${steps[0][1]:,.0f}, HBM3E about "
             f"${steps[1][1]:,.0f}, CoWoS-L packaging about ${steps[2][1]:,.0f}, packaging yield loss about "
             f"${steps[3][1]:,.0f} and other about ${steps[4][1]:,.0f}, totalling about ${total:,.0f}, against a "
             f"selling price of about ${price:,.0f}, implying a chip-level gross margin near {gm:.0%}."),
        data=[CSV], chapters=CH + ["14"],
        source="Epoch AI, Silicon Analysts, CNBC via Tom's Hardware", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    labels, bottoms, heights, colors = [], [], [], []
    run = 0.0
    comp_cols = [SEQ_BLUE[5], "#C98500", SEQ_BLUE[3], "#C4314B", "#B5B5B5"]
    for (lab, v), col in zip(steps, comp_cols):
        labels.append(lab)
        bottoms.append(run)
        heights.append(v)
        colors.append(col)
        run += v
    labels += ["= Build cost", "Gross profit\n(implied)", "= Price\n(~midpoint)"]
    bottoms += [0, total, 0]
    heights += [total, gp, price]
    colors += [INK["text"], GEN_PAST, NV]
    x = np.arange(len(labels))
    bars = ax.bar(x, heights, bottom=bottoms, color=colors, width=0.62, zorder=2, edgecolor="white")
    for patch in bars.patches[:5]:
        patch.set_hatch("//")
    for i in range(len(labels)):
        top = bottoms[i] + heights[i]
        txt = f"${heights[i]:,.0f}"
        if i == 6:
            txt = f"${heights[i]:,.0f}\n(~{gm:.0%} of price)"
        ax.annotate(txt, (i, top), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9, fontweight="bold", color=INK["title"])
    for i in range(4):
        ax.plot([i + 0.31, i + 0.69], [bottoms[i] + heights[i]] * 2, color=INK["muted"], lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.8)
    ax.set_ylim(0, price * 1.18)
    ax.yaxis.set_major_formatter(lambda v, _: f"${v/1e3:.0f}K")
    ax.text(2.0, total + 7000, f"HBM ≈ {steps[1][1]/total:.0%} of build cost;\nlogic dies ≈ {steps[0][1]/total:.0%}",
            ha="center", fontsize=9, color=INK["text"])
    c.save(fig, ax, ylabel="US$ per GPU package")


# --------------------------------------------------------------------------------------
@register
def hbm_cost_share():
    df = _df()
    d = df[df.record_type == "hbm_share"]
    chips = d[d.metric == "hbm_pct_of_unit_cost"]
    fleet = d[d.metric == "hbm_pct_of_component_spend"]
    c = Chart(
        id="P5-hbm-cost-share",
        title=f"HBM rose from ~{chips.value.iloc[0]:.0f}% of an A100's build cost to ~{chips.value.iloc[-1]:.0f}% of a B200's",
        subtitle="Estimated HBM share of unit manufacturing cost (left) and of all AI-accelerator component spend (right), %",
        alt=(f"Two bar panels: HBM share of unit cost rose from about {chips.value.iloc[0]:.0f}% for the A100 to about "
             f"{chips.value.iloc[1]:.0f}% for the H100 and about {chips.value.iloc[2]:.0f}% for the B200; across all AI "
             f"accelerators memory's share of component spend rose from {fleet.value.iloc[0]:.0f}% in Q1 2024 to "
             f"{fleet.value.iloc[1]:.0f}% in Q4 2025."),
        data=[CSV], chapters=CH,
        source="Silicon Analysts, Epoch AI", source_ids=sources_of(d),
        note="All values are estimates",
    )
    fig, axes = c.figure_grid(1, 2, width=10.5, height=5.6, gridspec_kw={"width_ratios": [3, 2]})
    ax1, ax2 = axes
    b1 = ax1.bar(chips["item"], chips.value, color=[GEN_PAST, GEN_PAST, NV], width=0.6, zorder=2)
    label_bars(ax1, b1, fmt="{:.0f}%", fontsize=10)
    ax1.set_ylim(0, 80)
    ax1.set_title("Per GPU (NVIDIA)", fontsize=10.5, color=INK["text"], loc="left")
    ax1.set_ylabel("HBM share of cost (%)")
    b2 = ax2.bar(fleet.period, fleet.value, color=[SEQ_BLUE[3], SEQ_BLUE[6]], width=0.55, zorder=2)
    label_bars(ax2, b2, fmt="{:.0f}%", fontsize=10)
    ax2.set_ylim(0, 80)
    ax2.set_title("All AI accelerators (Epoch)", fontsize=10.5, color=INK["text"], loc="left")
    for a in (ax1, ax2):
        for p in a.patches:
            p.set_hatch("//")
    fig.subplots_adjust(wspace=0.25)
    c.save(fig, axes, xlabel="Product / period", ylabel="HBM share of cost (%)", legend=False)


# --------------------------------------------------------------------------------------
@register
def tsmc_capex():
    df = _df()
    d = df[df.record_type == "tsmc_capex"].copy()
    d["year"] = d.period.astype(int)
    d = d.sort_values("year")
    first, last = d.iloc[0], d.iloc[-1]
    mult = last.value / first.value
    c = Chart(
        id="P5-tsmc-capex",
        title=f"TSMC's capex rose ~{mult:.1f}× from ${first.value:.1f}B (2019) to a guided ~${last.value:.0f}B (2026)",
        subtitle="TSMC capital expenditure by calendar year, US$ billions (2026 hatched = midpoint of $52–56B guidance, whisker = range)",
        alt=(f"Bar chart of TSMC capital expenditure: ${first.value:.1f}B in 2019, a then-record $36.3B in 2022, "
             f"$40.9B in 2025 and guidance of $52-56B for 2026 (midpoint ${last.value:.0f}B), about {mult:.1f} times 2019; "
             f"one report says 2026 guidance was raised to $60-64B."),
        data=[CSV], chapters=CH + ["18"],
        source="TSMC via AP, TrendForce, SemiWiki, TickerLeague", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    cols = [SEQ_BLUE[4]] * (len(d) - 1) + [SEQ_BLUE[6]]
    bars = ax.bar(d.year.astype(str), d.value, color=cols, width=0.62, zorder=2)
    hatch_future(bars, [y == 2026 for y in d.year])
    label_bars(ax, bars[:-1], fmt="${:,.1f}B")
    ax.text(len(d) - 1 - 0.06, 57, "$52–56B guide", ha="right", va="bottom", fontsize=8.5, color=INK["text"])
    i26 = len(d) - 1
    ax.plot([i26, i26], [52, 56], color=INK["title"], lw=1.5, zorder=3)
    ax.scatter([i26], [62], marker="D", s=40, color="#C98500", zorder=4)
    ax.annotate("Reported raise\nto $60–64B", (i26, 62), xytext=(-120, 12), textcoords="offset points",
                fontsize=8.6, color=INK["text"], arrowprops=dict(arrowstyle="-", color=INK["muted"]))
    ax.set_ylim(0, 72)
    c.save(fig, ax, xlabel="Calendar year", ylabel="Capital expenditure (US$ B)")


# --------------------------------------------------------------------------------------
@register
def cost_per_flop_trend():
    import matplotlib.ticker as mticker
    df = _df()
    pr = df[df.record_type == "system_price"].set_index("item")
    fl = df[df.record_type == "system_flops"]
    order = list(pr.index)
    fmt = {"DGX-1 (8x V100)": "FP16", "DGX A100 (8x A100)": "BF16", "HGX H200 (8x H200)": "FP8",
           "DGX B200 (8x B200)": "FP4", "GB200 NVL72": "FP4", "GB300 NVL72": "FP4", "Vera Rubin NVL72": "NVFP4"}
    rows = []
    for sys_ in order:
        price_k = float(pr.loc[sys_, "value"]) * 1000.0
        yr = str(pr.loc[sys_, "period"])
        bf = fl[(fl["item"] == sys_) & (fl.metric == "bf16_pflops_dense")].value
        lp = fl[(fl["item"] == sys_) & (fl.metric == "lowp_pflops_dense")].value
        rows.append((sys_, yr, price_k / float(bf.iloc[0]) if len(bf) else None,
                     price_k / float(lp.iloc[0]), pr.loc[sys_, "confidence"]))
    first, last = rows[0], rows[-1]
    drop = first[3] / last[3]
    best_bf = min(r[2] for r in rows if r[2])
    used = df[df.record_type.isin(["system_price", "system_flops"])]
    c = Chart(
        id="P5-cost-per-flop-trend",
        title=f"PFLOPS got ~{drop:.0f}× cheaper since 2017 at low precision, but BF16 stalled after GB200",
        subtitle="System price ÷ dense peak PFLOPS, US$ K per PFLOPS (log scale); low precision = each system's smallest float format",
        alt=(f"Log-scale chart of system price per dense PFLOPS: about ${first[3]:,.0f}K for a DGX-1 with V100 (FP16, 2017) "
             f"falling to about ${last[3]:,.1f}K for a Vera Rubin NVL72 at NVFP4 (2026), roughly {drop:.0f} times lower; "
             f"at BF16 the best value is about ${best_bf:,.0f}K for GB200 NVL72 while Vera Rubin NVL72 is about "
             f"${last[2]:,.0f}K because its gains and its memory cost are concentrated elsewhere."),
        data=[CSV], chapters=CH + ["14", "08"],
        source="NVIDIA, HSBC, Morgan Stanley, resellers via repo registry", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    x = np.arange(len(rows))
    bfx = [i for i, r in enumerate(rows) if r[2]]
    ax.plot(bfx, [rows[i][2] for i in bfx], color=SEQ_BLUE[3], lw=2.2, marker="o", ms=8,
            label="BF16 / FP16 (dense)")
    ax.plot(x, [r[3] for r in rows], color=NV, lw=2.4, marker="s", ms=8, label="Lowest float format (dense)")
    for i, r in enumerate(rows):
        hollow = r[4] == "estimate"
        ax.annotate(f"${r[3]:,.1f}K\n{fmt.get(r[0], '')}" if r[3] < 10 else f"${r[3]:,.0f}K\n{fmt.get(r[0], '')}",
                    (i, r[3]), xytext=(0, -26), textcoords="offset points", ha="center", va="top",
                    fontsize=8.6, color=NV_DARK, fontweight="bold")
        if r[2] and r[2] != r[3]:
            ax.annotate(f"${r[2]:,.0f}K", (i, r[2]), xytext=(0, 8), textcoords="offset points", ha="center",
                        va="bottom", fontsize=8.6, color=SEQ_BLUE[6])
        if hollow:
            ax.scatter([i], [r[3]], marker="s", s=64, facecolors="white", edgecolors=NV_DARK, zorder=5, linewidths=1.4)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r[0]}\n({r[1]})" for r in rows], fontsize=8.4)
    ax.set_yscale("log")
    ax.set_ylim(1.2, 400)
    ax.yaxis.set_major_locator(mticker.FixedLocator([2, 5, 10, 20, 50, 100, 200]))
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:g}K"))
    ax.legend(loc="upper right", fontsize=9)
    ax.text(-0.3, 1.45, "Hollow markers = estimated rack/system price; HGX H200 = 2026 listing price", ha="left",
            fontsize=8.4, color=INK["muted"])
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))
    c.save(fig, ax, xlabel="System (year of first shipment)", ylabel="US$ K per dense PFLOPS (log scale)",
           legend=False, bottom=0.17)
