"""Layer 08 (Systems, racks and AI factories) - CORE charts.

Mechanism and generation charts for the CORE pages of layer 08: tokens per MW by system, GPU package
power and heat flux, liquid-cooling penetration forecasts, the facility power stack for a 100k-GPU
GB300 build, capex vs electricity per GPU-hour, and build time vs grid-connection time.

Data: shared, read-only - data/inference_benchmarks.csv, data/system_specs.csv,
data/tco_model_inputs.csv, data/gpu_product_specs.csv; owned by the layer-08 CORE author -
data/l08_power_per_gpu.csv, data/l08_liquid_cooling_share.csv, data/l08_buildout_timelines.csv
(documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import (GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, Chart, entity_color, hatch_future, load,
                   register, sources_of)

BENCH = "inference_benchmarks.csv"
SYS = "system_specs.csv"
TCO = "tco_model_inputs.csv"
GPU = "gpu_product_specs.csv"
PWR = "l08_power_per_gpu.csv"
LIQ = "l08_liquid_cooling_share.csv"
BUILD = "l08_buildout_timelines.csv"


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _tco(system: str, inp: str, basis_contains: str | None = None) -> pd.Series:
    t = load(TCO)
    r = t[(t.system == system) & (t.input == inp)]
    if basis_contains:
        r = r[r.basis.astype(str).str.contains(basis_contains, regex=False)]
    return r.iloc[0]


# --------------------------------------------------------------------------------------
# 1. Tokens per second per MW at a fixed interactivity (InferenceX DeepSeek-R1 frontier)
# --------------------------------------------------------------------------------------
def _frontier(points):
    """Upper envelope of (interactivity, throughput) points: drop any point dominated by another."""
    pts = sorted(points)
    env = []
    for x, y in pts:
        if any((x2 >= x and y2 > y) or (x2 > x and y2 >= y) for x2, y2 in pts):
            continue
        env.append((x, y))
    return sorted(env)


def _interp_log(env, target):
    xs = [p[0] for p in env]
    ys = [np.log(p[1]) for p in env]
    if not env or target < xs[0] or target > xs[-1]:
        return np.nan
    return float(np.exp(np.interp(target, xs, ys)))


TARGET_TPS_USER = 50.0
WORKLOAD = "DeepSeek-R1-0528 (1k in/1k out)"
SYSTEMS_TPM = [  # (system in CSVs, label, vendor)
    ("H100", "H100\n(HGX, 2022)", "NVIDIA"),
    ("H200", "H200\n(HGX, 2024)", "NVIDIA"),
    ("B200", "B200\n(HGX, 2024)", "NVIDIA"),
    ("B300", "B300\n(HGX, 2025)", "NVIDIA"),
    ("GB200 NVL72", "GB200\nNVL72", "NVIDIA"),
    ("GB300 NVL72", "GB300\nNVL72", "NVIDIA"),
    ("MI300X", "MI300X\n(AMD)", "AMD"),
    ("MI355X", "MI355X\n(AMD)", "AMD"),
]


def _tokens_per_mw_table() -> pd.DataFrame:
    b = load(BENCH)
    f = b[b.benchmark_suite.str.contains("Pareto frontier, no speculative", regex=False) & (b.model == WORKLOAD)]
    p = load(PWR).set_index("system")
    rows = []
    for sys_name, label, vendor in SYSTEMS_TPM:
        g = f[f.system == sys_name]
        env = _frontier(list(zip(g.interactivity_tok_s_per_user, g.throughput_tok_s_per_gpu)))
        tps_gpu = _interp_log(env, TARGET_TPS_USER)
        kw = float(p.loc[sys_name, "all_in_kw_per_gpu"])
        rows.append(dict(system=sys_name, label=label, vendor=vendor, tps_gpu=tps_gpu, kw=kw,
                         tps_mw=tps_gpu / kw * 1000.0, sids=sources_of(g) + [p.loc[sys_name, "source_id"]]))
    return pd.DataFrame(rows)


@register
def l08_tokens_per_mw_by_system():
    d = _tokens_per_mw_table()
    h200 = d.set_index("system").loc["H200", "tps_mw"]
    gb300 = d.set_index("system").loc["GB300 NVL72", "tps_mw"]
    gb200 = d.set_index("system").loc["GB200 NVL72", "tps_mw"]
    h100 = d.set_index("system").loc["H100", "tps_mw"]
    mi355 = d.set_index("system").loc["MI355X", "tps_mw"]
    mult = gb300 / h200
    sids = []
    for s in d.sids:
        for x in s:
            if x not in sids:
                sids.append(x)
    c = Chart(
        id="08-tokens-per-mw-by-system",
        title=f"Per MW, GB300 NVL72 serves ~{mult:.0f}× H200's DeepSeek-R1 tokens at 50 tok/s per user",
        subtitle="Total tokens/s per MW of all-in power · DeepSeek-R1 1k in / 1k out, InferenceX frontier interpolated at 50 tok/s/user (repo calc)",
        alt=(f"Log-scale bar chart of DeepSeek-R1 tokens per second per megawatt of all-in power at 50 tokens/s per user "
             f"(InferenceX frontier divided by SemiAnalysis power per GPU): H100 about {h100/1e3:,.0f} thousand, H200 about "
             f"{h200/1e3:,.0f} thousand, B200 about {d.tps_mw[2]/1e6:.1f} million, B300 about {d.tps_mw[3]/1e6:.1f} million, "
             f"GB200 NVL72 about {gb200/1e6:.1f} million and GB300 NVL72 about {gb300/1e6:.1f} million, ~{mult:.0f} times H200; "
             f"AMD MI300X about {d.tps_mw[6]/1e3:,.0f} thousand and MI355X about {mi355/1e3:,.0f} thousand."),
        data=[BENCH, PWR], chapters=["08", "14", "11"],
        source="SemiAnalysis InferenceX frontier and hardware registry", source_ids=sids,
        note="Est.: frontier interpolation and power basis are repo choices",
    )
    fig, ax = c.figure(width=10.8, height=6.0)
    x = np.arange(len(d))
    cols = []
    for _, r in d.iterrows():
        if r.vendor == "AMD":
            cols.append(entity_color("AMD"))
        else:
            cols.append(NV if "NVL72" in r.system else GEN_PAST)
    bars = ax.bar(x, d.tps_mw, color=cols, width=0.66, zorder=2)
    for i, r in d.iterrows():
        v = r.tps_mw
        lab = f"{v/1e6:.2f}M" if v >= 1e6 else f"{v/1e3:,.0f}k"
        ax.annotate(lab, (i, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9.2, color=INK["title"], fontweight="bold")
        ink = INK["title"] if cols[i] == GEN_PAST else "#FFFFFF"
        ax.annotate(f"{r.tps_gpu:,.0f} tok/s\nper GPU\n÷ {r.kw:.2f} kW", (i, v), xytext=(0, -5),
                    textcoords="offset points", ha="center", va="top", fontsize=7.2, color=ink)
    ax.set_yscale("log")
    ax.set_ylim(1e4, 2e7)
    ax.set_xticks(x, d.label, fontsize=8.8)
    ax.axvline(5.5, color=INK["base"], lw=1, ls="--", zorder=1)
    handles = [Patch(facecolor=GEN_PAST, label="NVIDIA 8-GPU HGX servers"),
               Patch(facecolor=NV, label="NVIDIA NVL72 racks"),
               Patch(facecolor=entity_color("AMD"), label="AMD 8-GPU platforms (reference)")]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=8.8)
    c.save(fig, ax, ylabel="Tokens/s per MW", logy=True, legend=False, bottom=0.16)


# --------------------------------------------------------------------------------------
# 2. GPU package power and heat flux by generation (why air cooling ran out)
# --------------------------------------------------------------------------------------
HEAT_LINEAGE = [  # (product in gpu_product_specs.csv, label, cooling as deployed in NVIDIA's flagship system)
    ("P100 SXM2", "P100\n2016", "air"),
    ("V100 SXM2 32GB", "V100\n2018", "air"),
    ("A100 SXM 80GB", "A100\n2021", "air"),
    ("H100 SXM", "H100\n2022", "air"),
    ("B200 (HGX)", "B200\nHGX", "air"),
    ("B300 (HGX)", "B300\nHGX", "air"),
    ("GB200 (per GPU)", "GB200\nNVL72", "liquid"),
    ("GB300 (per GPU)", "GB300\nNVL72", "liquid"),
    ("Rubin (VR200, per GPU)", "Rubin\nVR NVL72", "liquid"),
]


@register
def l08_gpu_heat_flux_by_generation():
    g = load(GPU).set_index("product")
    d = g.loc[[p for p, _, _ in HEAT_LINEAGE]].reset_index()
    d["label"] = [lab for _, lab, _ in HEAT_LINEAGE]
    d["cooling"] = [c_ for _, _, c_ in HEAT_LINEAGE]
    d["silicon_cm2"] = d.dies_per_package * d.die_area_mm2_per_die / 100.0
    d["w_per_cm2"] = d.tdp_w / d.silicon_cm2
    first, last = d.iloc[0], d.iloc[-1]
    pmult = last.tdp_w / first.tdp_w
    fmult = last.w_per_cm2 / first.w_per_cm2
    c = Chart(
        id="08-gpu-heat-flux-by-generation",
        title=f"GPU package power rose ~{pmult:.0f}× since 2016 ({first.tdp_w:.0f} → {last.tdp_w:,.0f} W); heat per cm² ~{fmult:.0f}×",
        subtitle="Left: max power per GPU package, W · Right: W per cm² of compute silicon (TDP ÷ die area, Est.) · color = cooling in NVIDIA's flagship system",
        alt=(f"Two bar charts by NVIDIA GPU. Left: package power rises from {first.tdp_w:.0f} W (P100, 2016) through 700 W (H100), "
             f"1,000-1,100 W (B200, B300 in air-cooled HGX servers), 1,200 W (GB200) and 1,400 W (GB300) to about "
             f"{last.tdp_w:,.0f} W for Rubin at its maximum-performance setting, about {pmult:.0f} times. Right: watts per "
             f"square centimetre of compute die rise from about {first.w_per_cm2:.0f} to about {last.w_per_cm2:.0f} "
             f"(estimate), about {fmult:.0f} times. Every 1,200 W-plus superchip GPU ships only liquid-cooled."),
        data=[GPU], chapters=["08", "02"],
        source="NVIDIA datasheets, reported TDPs", source_ids=sources_of(d),
        note="Rubin: reported Max-P TDP; die areas Est.",
    )
    fig, axes = c.figure_grid(1, 2, width=11.5, height=6.0)
    x = np.arange(len(d))
    cols = [NV if c_ == "liquid" else GEN_PAST for c_ in d.cooling]
    for ax, col, fmt, ylab in ((axes[0], "tdp_w", "{:,.0f}", "Max power per GPU package (W)"),
                               (axes[1], "w_per_cm2", "{:,.0f}", "W per cm² of compute die (Est.)")):
        bars = ax.bar(x, d[col], color=cols, width=0.68, zorder=2)
        hatch_future(bars, [s != "shipping" and s != "eol" for s in d.status])
        for i, v in enumerate(d[col]):
            ax.annotate(fmt.format(v), (i, v), xytext=(0, 2), textcoords="offset points", ha="center",
                        va="bottom", fontsize=8.2, color=INK["title"], fontweight="bold")
        ax.set_xticks(x, d.label, fontsize=7.8)
        ax.set_ylabel(ylab)
        ax.set_ylim(0, d[col].max() * 1.16)
        ax.tick_params(length=0)
    axes[0].axhline(1100, color=INK["text"], lw=1, ls=":", zorder=1)
    axes[0].text(-0.4, 1190, "air-cooled ceiling so far: 1,100 W (B300 HGX)", fontsize=8.0, color=INK["text"], va="bottom")
    handles = [Patch(facecolor=GEN_PAST, label="Air-cooled flagship server"),
               Patch(facecolor=NV, label="Liquid-cooled only (superchip, NVL72)")]
    axes[1].legend(handles=handles, loc="upper left", frameon=False, fontsize=8.6)
    fig.subplots_adjust(wspace=0.25)
    c.save(fig, list(axes), legend=False, bottom=0.15)


# --------------------------------------------------------------------------------------
# 3. Liquid-cooling penetration: TrendForce forecasts by vintage
# --------------------------------------------------------------------------------------
@register
def l08_liquid_cooling_penetration():
    d = load(LIQ)
    vint = list(dict.fromkeys(d.forecast_vintage))  # oldest -> newest (file order)
    latest = d[d.forecast_vintage == vint[-1]]
    v26 = float(latest.loc[latest.year == 2026, "share_pct"].iloc[0])
    v27 = float(latest.loc[latest.year == 2027, "share_pct"].iloc[0])
    nov = d[(d.forecast_vintage == "TrendForce Nov 2025") & (d.year == 2026)].share_pct.iloc[0]
    c = Chart(
        id="08-liquid-cooling-penetration",
        title=f"TrendForce: liquid cooling on ~{v26:.0f}% of high-end AI chips in 2026, ~{v27:.0f}% in 2027",
        subtitle="Liquid-cooling penetration, % of AI accelerators / AI data-center deployments · one line per TrendForce forecast vintage",
        alt=(f"Line chart of TrendForce liquid-cooling penetration estimates by forecast vintage. September 2024 vintage: about 10% "
             f"in 2024 and over 20% in 2025. August 2025 vintage: 14% in 2024 and 33% in 2025. November 2025 vintage: {nov:.0f}% in "
             f"2026. August 2026 vintage: {v26:.0f}% in 2026 and about {v27:.0f}% in 2027, each forecast higher than the last."),
        data=[LIQ], chapters=["08"],
        source="TrendForce press releases 2024-2026", source_ids=sources_of(d),
        note="Scopes differ slightly by release",
    )
    fig, ax = c.figure(width=10.0, height=5.8)
    shades = [SEQ_BLUE[2], SEQ_BLUE[4], SEQ_BLUE[5], SEQ_BLUE[7]]
    markers = ["s", "^", "D", "o"]
    for i, v in enumerate(vint):
        s = d[d.forecast_vintage == v].sort_values("year")
        lw = 2.8 if i == len(vint) - 1 else 2.0
        ax.plot(s.year, s.share_pct, marker=markers[i % 4], color=shades[i % 4], lw=lw, ms=8, label=v, zorder=3)
        for _, r in s.iterrows():
            if i == len(vint) - 1 and r.year == 2025:
                continue  # same 33% point as the Aug 2025 vintage; label once
            txt = f">{r.share_pct:.0f}%" if (r.year == 2025 and r.share_pct == 20) else f"{r.share_pct:.0f}%"
            ax.annotate(txt, (r.year, r.share_pct), xytext=(8, -2 if i < 2 else 4),
                        textcoords="offset points", fontsize=8.6, color=shades[i % 4], fontweight="bold")
    ax.set_xticks([2024, 2025, 2026, 2027])
    ax.set_xlim(2023.7, 2027.5)
    ax.set_ylim(0, 75)
    ax.axvspan(2025.5, 2027.5, color="#F0EFEC", zorder=0)
    ax.text(2025.55, 72, "forecast years (as of Nov 2026)", fontsize=8.6, color=INK["text"], va="top")
    ax.legend(loc="upper left", frameon=False, fontsize=8.8, title="Forecast vintage", title_fontsize=8.8)
    c.save(fig, ax, xlabel="Calendar year", ylabel="Liquid-cooling penetration (%)", legend=False)


# --------------------------------------------------------------------------------------
# 4. Facility power for 100,000 GB300 GPUs (waterfall)
# --------------------------------------------------------------------------------------
N_GPUS = 100_000


def _facility_model() -> dict:
    s = load(SYS).set_index("system")
    g = load(GPU).set_index("product")
    gb300 = s.loc["GB300 NVL72"]
    gpus_per_rack = float(gb300.accelerators_per_system)
    rack_kw = float(gb300.power_kw)
    gpu_kw = float(g.loc["GB300 (per GPU)", "tdp_w"]) / 1000.0
    allin = float(_tco("GB200 NVL72", "rack_power_kw_all_in").value)
    gb200_rack = float(_tco("GB200 NVL72", "rack_power_kw").value)
    pue = float(_tco("All", "pue_assumption_liquid_cooled").value)
    pue_avg = float(_tco("All", "pue_industry_average").value)
    p_lo = float(_tco("All", "electricity_price_low").value)
    p_mid = float(_tco("All", "electricity_price_us_industrial").value)
    p_hi = float(_tco("All", "electricity_price_high").value)
    racks = N_GPUS / gpus_per_rack
    gpus_mw = N_GPUS * gpu_kw / 1000.0
    rack_mw = racks * rack_kw / 1000.0
    other_rack = rack_mw - gpus_mw
    net = rack_mw * (allin / gb200_rack - 1.0)
    it = rack_mw + net
    facility = it * pue
    overhead = facility - it
    sids = sources_of(s.loc[["GB300 NVL72", "GB200 NVL72"]].reset_index()) + sources_of(g.loc[["GB300 (per GPU)"]].reset_index())
    t = load(TCO)
    sel = t[((t.system == "GB200 NVL72") & t.input.isin(["rack_power_kw_all_in", "rack_power_kw"])) |
            ((t.system == "All") & t.input.isin(["pue_assumption_liquid_cooled", "pue_industry_average",
                                                  "electricity_price_low", "electricity_price_us_industrial",
                                                  "electricity_price_high"]))]
    for x in sources_of(sel):
        if x not in sids:
            sids.append(x)
    return dict(racks=racks, gpus_mw=gpus_mw, other_rack=other_rack, net=net, it=it, overhead=overhead,
                facility=facility, pue=pue, pue_avg=pue_avg, facility_avg=it * pue_avg, p_lo=p_lo, p_mid=p_mid,
                p_hi=p_hi, rack_kw=rack_kw, gpu_kw=gpu_kw, ratio=allin / gb200_rack, sids=sids)


@register
def l08_facility_power_100k_gb300():
    m = _facility_model()
    twh = m["facility"] * 8760 / 1e6
    cost = {k: twh * 1e9 * m[k] / 1e6 for k in ("p_lo", "p_mid", "p_hi")}  # $M per year at full load
    c = Chart(
        id="08-facility-power-100k-gb300",
        title=f"100,000 GB300 GPUs need ~{m['facility']:.0f} MW at the meter and ~${cost['p_mid']:.0f}M of power a year",
        subtitle=f"Power build-up, MW (repo calc) · {m['racks']:,.0f} NVL72 racks at ~{m['rack_kw']:.0f} kW · PUE {m['pue']:.2f} · cost at full load, ${m['p_mid']:.3f}/kWh",
        alt=(f"Waterfall chart: 100,000 GB300 GPUs at {m['gpu_kw']*1000:,.0f} W draw about {m['gpus_mw']:.0f} MW; the rest of "
             f"{m['racks']:,.0f} NVL72 racks (Grace CPUs, NVLink switch trays, NICs, pumps, conversion) adds about "
             f"{m['other_rack']:.0f} MW; scale-out networking, storage and management add about {m['net']:.0f} MW "
             f"(IT total {m['it']:.0f} MW); cooling and power-conversion overhead at PUE {m['pue']:.2f} adds about "
             f"{m['overhead']:.0f} MW, for about {m['facility']:.0f} MW at the meter ({m['facility_avg']:.0f} MW at the "
             f"industry-average PUE of {m['pue_avg']:.2f}). At full load that is {twh:.1f} TWh a year, about "
             f"${cost['p_lo']:.0f}M-${cost['p_hi']:.0f}M of electricity at 5-10 cents per kWh."),
        data=[SYS, GPU, TCO], chapters=["08", "14"],
        source="system_specs, gpu_product_specs, tco_model_inputs",
        source_ids=m["sids"], note="Est. (repo calc)",
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    steps = [(f"{N_GPUS:,} GPUs\n× {m['gpu_kw']:.1f} kW", m["gpus_mw"]),
             ("Rest of rack\n(CPUs, NVLink trays,\nNICs, pumps, PSU loss)", m["other_rack"]),
             ("Scale-out network,\nstorage, mgmt", m["net"]),
             (f"Cooling + power\nconversion (PUE {m['pue']:.2f})", m["overhead"])]
    base = 0.0
    x = np.arange(len(steps) + 1)
    cols = [NV, GEN_PAST, "#86B6EF", "#B5B5B5"]
    for i, (lab, v) in enumerate(steps):
        ax.bar(i, v, bottom=base, color=cols[i], width=0.62, zorder=2)
        ax.annotate(f"+{v:.0f} MW", (i, base + v), xytext=(0, 3), textcoords="offset points", ha="center",
                    va="bottom", fontsize=9.5, fontweight="bold", color=INK["title"])
        if i < len(steps) - 1:
            ax.plot([i + 0.31, i + 0.69], [base + v, base + v], color=INK["base"], lw=1, zorder=1)
        base += v
    ax.plot([len(steps) - 1 + 0.31, len(steps) - 0.31], [base, base], color=INK["base"], lw=1, zorder=1)
    ax.bar(len(steps), base, color=NV_DARK, width=0.62, zorder=2)
    ax.annotate(f"{base:.0f} MW", (len(steps), base), xytext=(0, 3), textcoords="offset points", ha="center",
                va="bottom", fontsize=10.5, fontweight="bold", color=INK["title"])
    ax.axhline(m["facility_avg"], color=INK["text"], lw=1.2, ls="--", zorder=1)
    ax.text(-0.35, m["facility_avg"] + 4, f"Same IT load at industry-average PUE {m['pue_avg']:.2f}: ~{m['facility_avg']:.0f} MW",
            fontsize=8.8, color=INK["text"], va="bottom")
    ax.text(-0.35, m["facility_avg"] * 0.80,
            f"Full-load energy: {twh:.1f} TWh a year\n≈ ${cost['p_lo']:.0f}M at 5¢/kWh · ${cost['p_mid']:.0f}M at {m['p_mid']*100:.1f}¢ · ${cost['p_hi']:.0f}M at 10¢",
            fontsize=9.2, color=INK["title"], ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.4", fc="#F7F7F4", ec=INK["base"]))
    ax.set_xticks(x, [s[0] for s in steps] + ["Grid connection\nneeded"], fontsize=8.6)
    ax.set_ylim(0, m["facility_avg"] * 1.12)
    c.save(fig, ax, ylabel="Power (MW)", legend=False, bottom=0.18)


# --------------------------------------------------------------------------------------
# 5. Capex vs electricity per GPU-hour by system generation
# --------------------------------------------------------------------------------------
CAPEX_LINEAGE = [  # (system in system_specs.csv, label, liquid?)
    ("DGX-1 (P100)", "DGX-1\nP100 · 2016", False),
    ("DGX-2", "DGX-2\n2018", False),
    ("DGX A100", "DGX A100\n2020", False),
    ("DGX H200", "DGX H200\n2024", False),
    ("DGX B200", "DGX B200\n2024", False),
    ("GB200 NVL72", "GB200\nNVL72 · 2024", True),
    ("GB300 NVL72", "GB300\nNVL72 · 2025", True),
    ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin\nNVL72 · 2026", True),
]


@register
def l08_capex_vs_power_per_gpu_hour():
    s = load(SYS).set_index("system")
    d = s.loc[[n for n, _, _ in CAPEX_LINEAGE]].reset_index()
    d["label"] = [lab for _, lab, _ in CAPEX_LINEAGE]
    d["liquid"] = [lq for _, _, lq in CAPEX_LINEAGE]
    life = float(_tco("All", "server_useful_life_years").value)  # first row = Microsoft, 6 years
    price = float(_tco("All", "electricity_price_us_industrial").value)
    pue_air = float(_tco("All", "pue_assumption_air_cooled").value)
    pue_liq = float(_tco("All", "pue_assumption_liquid_cooled").value)
    hours = life * 8760.0
    d["capex_hr"] = d.est_price_usd_m * 1e6 / d.accelerators_per_system / hours
    d["kw_gpu"] = d.power_kw / d.accelerators_per_system
    d["power_hr"] = d.kw_gpu * np.where(d.liquid, pue_liq, pue_air) * price
    d["share"] = d.power_hr / (d.capex_hr + d.power_hr)
    lo, hi = d.share.min() * 100, d.share.max() * 100
    vr = d.iloc[-1]
    t = load(TCO)
    sel = t[(t.system == "All") & t.input.isin(["server_useful_life_years", "electricity_price_us_industrial",
                                                "pue_assumption_air_cooled", "pue_assumption_liquid_cooled"])]
    sids = sources_of(d)
    for x_ in sources_of(sel):
        if x_ not in sids:
            sids.append(x_)
    c = Chart(
        id="08-capex-vs-power-per-gpu-hour",
        title=f"Electricity is only ~{lo:.0f}–{hi:.0f}% of hardware-plus-power cost per GPU-hour; capex dominates",
        subtitle=f"US$/GPU-hour: price ÷ GPUs ÷ {life:.0f} yrs, plus kW/GPU × PUE ({pue_air} air, {pue_liq} liquid) × ${price}/kWh · building and network excluded",
        alt=(f"Stacked bar chart of cost per GPU-hour by NVIDIA system. Hardware depreciation over {life:.0f} years rises from about "
             f"${d.capex_hr.iloc[0]:.2f} (DGX-1, 2016) to about ${d.capex_hr.iloc[5]:.2f} (GB200 NVL72), ${d.capex_hr.iloc[6]:.2f} "
             f"(GB300 NVL72) and ${vr.capex_hr:.2f} (Vera Rubin NVL72, estimated price); electricity adds about "
             f"${d.power_hr.iloc[0]:.2f} to ${vr.power_hr:.2f} per GPU-hour, only {lo:.0f}-{hi:.0f}% of the total, so "
             f"power limits how many GPUs fit rather than what each GPU-hour costs."),
        data=[SYS, TCO], chapters=["08", "14"],
        source="system_specs, tco_model_inputs", source_ids=sids,
        note="Prices 2024+ Est.; hatched = announced",
    )
    fig, ax = c.figure(width=10.8, height=6.0)
    x = np.arange(len(d))
    b1 = ax.bar(x, d.capex_hr, color=[NV if lq else GEN_PAST for lq in d.liquid], width=0.64, zorder=2,
                label="Hardware depreciation")
    b2 = ax.bar(x, d.power_hr, bottom=d.capex_hr, color="#F2B33D", width=0.64, zorder=2, label="Electricity")
    hatch_future(b1, [st in ("announced", "roadmap") for st in d.status])
    hatch_future(b2, [st in ("announced", "roadmap") for st in d.status])
    for i, r in d.iterrows():
        tot = r.capex_hr + r.power_hr
        ax.annotate(f"${tot:.2f}\npower {r.share*100:.0f}%", (i, tot), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.2, color=INK["title"])
    ax.set_xticks(x, d.label, fontsize=8.4)
    ax.set_ylim(0, (d.capex_hr + d.power_hr).max() * 1.2)
    handles = [Patch(facecolor=GEN_PAST, label="Hardware: air-cooled 8/16-GPU DGX"),
               Patch(facecolor=NV, label="Hardware: liquid-cooled NVL72 rack"),
               Patch(facecolor="#F2B33D", label="Electricity (incl. PUE)")]
    ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=8.8)
    c.save(fig, ax, ylabel="US$ per GPU-hour", legend=False, bottom=0.16)


# --------------------------------------------------------------------------------------
# 6. Build time vs grid-connection time
# --------------------------------------------------------------------------------------
@register
def l08_build_vs_grid_timelines():
    d = load(BUILD)
    d = d.iloc[::-1].reset_index(drop=True)  # first row on top
    labels = [f"{r.case}\n{r.milestone}" for _, r in d.iterrows()]
    build = d[d.category == "build"]
    grid = d[d.category == "grid"]
    c = Chart(
        id="08-build-vs-grid-timelines",
        title=f"Cited AI factories went up in {build.months.nlargest(3).min():.0f}–{build.months.max():.0f} months; new grid power can take {grid.months.min()/12:.0f}–{grid.months.max()/12:.0f} years",
        subtitle="Months for cited milestones · build = shell, power gear, racks to first compute · grid = utility hookup or new generation queue",
        alt=(f"Horizontal bar chart in months. Build milestones: xAI Colossus 1 first rack to training in 19 days (0.6 months) "
             f"and facility plus 100,000-GPU cluster in 122 days (4 months); Stargate Abilene first two buildings, 200+ MW, "
             f"about 15 months from construction start; the full 1.2 GW campus about 24 months (mid-2026 target, later "
             f"estimates Q4 2026). Grid milestones: median interconnection request to operation for new US generation over "
             f"48 months (LBNL), and up to 84 months for a large data-center hookup in Dominion's Northern Virginia territory."),
        data=[BUILD], chapters=["08", "12"],
        source="NVIDIA/xAI, Crusoe/DCD, Epoch AI, Bloomberg, LBNL", source_ids=sources_of(d),
        note="Build times company-reported",
    )
    fig, ax = c.figure(width=11.0, height=6.0)
    _left_margin(fig, 0.30)
    y = np.arange(len(d))
    cols = ["#256ABF" if cat == "build" else "#52514E" for cat in d.category]
    bars = ax.barh(y, d.months, color=cols, height=0.6, zorder=2)
    for i, r in d.iterrows():
        lab = f"{r.months:.1f} mo" if r.months < 2 else f"{r.months:.0f} mo"
        if r.category == "grid" and r.months == 48:
            lab = "> 48 mo (median)"
        if r.category == "grid" and r.months == 84:
            lab = "up to 84 mo"
        ax.annotate(lab, (r.months, i), xytext=(4, 0), textcoords="offset points", va="center", fontsize=9,
                    fontweight="bold", color=INK["title"])
    ax.set_yticks(y, labels, fontsize=8.4)
    ax.set_xlim(0, d.months.max() * 1.18)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    handles = [Patch(facecolor="#256ABF", label="Build the factory"), Patch(facecolor="#52514E", label="Get grid power")]
    ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=9)
    c.save(fig, ax, xlabel="Months", legend=False)
