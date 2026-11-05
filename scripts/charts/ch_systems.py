"""Systems, racks and AI factories (chapter 08) - agent A3.

All charts read data/system_specs.csv (one row per system) and, for the rack BOM waterfall,
data/tco_model_inputs.csv. Compute is dense peak (vendor sparse figures halved in the CSV).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, hatch_future, load, register,
                   sources_of)

SYS = "system_specs.csv"
TCO = "tco_model_inputs.csv"

# NVIDIA flagship lineage, oldest -> newest (system name in CSV -> short axis label)
LINEAGE = [
    ("DGX-1 (P100)", "DGX-1\nP100 · 2016"),
    ("DGX-2", "DGX-2\nV100 · 2018"),
    ("DGX A100", "DGX A100\n2020"),
    ("DGX H100", "DGX H100\n2022"),
    ("DGX B200", "DGX B200\n2024"),
    ("GB200 NVL72", "GB200\nNVL72 · 2024"),
    ("GB300 NVL72", "GB300\nNVL72 · 2025"),
    ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin\nNVL72 · 2026"),
    ("Rubin Ultra NVL144 Kyber (GTC 2025 name: NVL576)", "Rubin Ultra\nKyber · 2027"),
]
FUTURE = {"announced", "roadmap"}


def log_ticks(ax, ticks, labels, axis="y"):
    """style.Chart.save() calls set_yscale('log'), which resets tick formatters (and mathtext is off,
    so default log labels render as raw '$10^{1}$'). Patch the axis so our fixed ticks survive."""
    from matplotlib.ticker import FixedFormatter, FixedLocator, NullFormatter

    setter = ax.set_yscale if axis == "y" else ax.set_xscale
    ax_obj = ax.yaxis if axis == "y" else ax.xaxis

    def patched(*a, **k):
        setter(*a, **k)
        ax_obj.set_major_locator(FixedLocator(ticks))
        ax_obj.set_major_formatter(FixedFormatter(labels))
        ax_obj.set_minor_formatter(NullFormatter())

    patched("log")
    if axis == "y":
        ax.set_yscale = patched
    else:
        ax.set_xscale = patched


def manual_axes(fig, rects):
    """Replace subplot axes with fixed-position axes (save() re-applies subplots_adjust, which would
    otherwise clip long horizontal-bar labels)."""
    for a in list(fig.axes):
        fig.delaxes(a)
    return [fig.add_axes(r) for r in rects]


def _sys() -> pd.DataFrame:
    return load(SYS)


def _pick(df: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    d = df.set_index("system").loc[names].reset_index()
    return d


def _lineage(df: pd.DataFrame) -> pd.DataFrame:
    d = _pick(df, [n for n, _ in LINEAGE])
    d["label"] = [lab for _, lab in LINEAGE]
    return d


def _nv_colors(d: pd.DataFrame) -> list[str]:
    """Past NVIDIA generations in the light tint; shipping current racks and roadmap in full green."""
    cols = []
    for _, r in d.iterrows():
        current = r["status"] in FUTURE or r["system"] in ("GB300 NVL72",)
        cols.append(NV if current else GEN_PAST)
    return cols


def _future_legend(ax, loc="upper left", extra=None):
    handles = [Patch(facecolor=GEN_PAST, label="Past generation"),
               Patch(facecolor=NV, label="Current generation"),
               Patch(facecolor=NV, hatch="///", edgecolor="white", alpha=0.75, label="Announced / roadmap (vendor-stated)")]
    if extra:
        handles += extra
    ax.legend(handles=handles, loc=loc, frameon=False, fontsize=8.8)


# --------------------------------------------------------------------------------------
@register
def kw_per_rack_by_generation():
    df = _sys()
    d = _lineage(df)
    first, last = d.iloc[0], d.iloc[-1]
    mult = round(last.power_kw / first.power_kw, -1)
    vr = d.iloc[7]
    c = Chart(
        id="08-kw-per-rack-by-generation",
        title=f"Power per NVIDIA system rose ~{mult:.0f}× in a decade: {first.power_kw:.1f} kW (DGX-1) to ~{last.power_kw:.0f} kW (Kyber)",
        subtitle="Maximum IT power per system or rack, kW · 8/16-GPU DGX servers 2016–2024, NVLink racks from 2024 · hatched = announced/roadmap",
        alt=(f"Bar chart of maximum power per NVIDIA system: DGX-1 {first.power_kw:.1f} kW (2016), DGX-2 10 kW, DGX A100 6.5 kW, "
             f"DGX H100 10.2 kW, DGX B200 14.3 kW, then rack-scale GB200 NVL72 ~120 kW, GB300 NVL72 ~132 kW, Vera Rubin NVL72 "
             f"~190-{vr.power_kw:.0f} kW and the Rubin Ultra Kyber rack ~{last.power_kw:.0f} kW, about {mult:.0f} times the DGX-1."),
        data=[SYS], chapters=["08", "17", "14"],
        source="NVIDIA, AnandTech, TweakTown, eeNews, Hashrate Index, DCD",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    x = np.arange(len(d))
    bars = ax.bar(x, d.power_kw, color=_nv_colors(d), width=0.66, zorder=2)
    hatch_future(bars, [s in FUTURE for s in d.status])
    for i, r in d.iterrows():
        lab = f"{r.power_kw:g}"
        if i == 7:
            lab = f"~190–{r.power_kw:.0f}"
        elif r.power_kw >= 100:
            lab = f"~{r.power_kw:.0f}"
        ax.annotate(lab, (i, r.power_kw), xytext=(0, 3), textcoords="offset points", ha="center",
                    va="bottom", fontsize=9, color=INK["title"], fontweight="bold")
    ax.axvline(4.5, color=INK["base"], lw=1, ls="--", zorder=1)
    ax.text(4.4, 560, "8–16 GPU servers\n(air-cooled)", ha="right", va="top", fontsize=9, color=INK["text"])
    ax.text(4.6, 560, "72–144 GPU racks\n(liquid-cooled)", ha="left", va="top", fontsize=9, color=INK["text"])
    ax.set_xticks(x, d.label, fontsize=8.6)
    ax.set_ylim(0, last.power_kw * 1.12)
    _future_legend(ax, loc="upper left")
    ax.get_legend().set_bbox_to_anchor((0.0, 0.80))
    c.save(fig, ax, ylabel="Max IT power per system (kW)", legend=False, bottom=0.16)


# --------------------------------------------------------------------------------------
@register
def accelerators_per_mw():
    df = _sys()
    d = _lineage(df)
    d["gpus_per_mw"] = d.accelerators_per_system / d.power_kw * 1000
    d["fp8_pf_per_mw"] = d.fp8_pflops_dense / d.power_kw * 1000
    g0, g1 = d.gpus_per_mw.iloc[0], d.gpus_per_mw.iloc[-1]
    f = d.dropna(subset=["fp8_pf_per_mw"])
    f0, f1 = f.fp8_pf_per_mw.iloc[0], f.fp8_pf_per_mw.iloc[-1]
    c = Chart(
        id="08-accelerators-per-mw",
        title=f"1 MW now hosts ~{g0 / g1:.0f}× fewer NVIDIA GPUs than in 2016, yet up to ~{f1 / f0:.0f}× Hopper's FP8 per MW",
        subtitle="Per MW of system IT power (excludes cooling/PUE): GPU packages (left) and dense FP8 PFLOPS (right) · hatched = announced/roadmap",
        alt=(f"Two bar charts by NVIDIA system generation. Left: GPUs per MW of IT power fall from about {g0:,.0f} for DGX-1 "
             f"to about {d.gpus_per_mw.iloc[5]:,.0f} for GB200 NVL72 and {g1:,.0f} for the Rubin Ultra Kyber rack. Right: dense FP8 "
             f"PFLOPS per MW rise from about {f0:,.0f} for DGX H100 to about {f.fp8_pf_per_mw.iloc[-2]:,.0f} for Vera Rubin NVL72 "
             f"and {f1:,.0f} for Kyber, roughly {f1 / f0:.0f} times Hopper."),
        data=[SYS], chapters=["08", "14", "17"],
        source="NVIDIA, press power estimates (repo calc)",
        source_ids=sources_of(d),
    )
    fig, axes = c.figure_grid(1, 2, width=11.5, height=6.0)
    x = np.arange(len(d))
    short = ["DGX-1\n2016", "DGX-2\n2018", "DGX\nA100", "DGX\nH100", "DGX\nB200", "GB200\nNVL72",
             "GB300\nNVL72", "Vera\nRubin\nNVL72", "Rubin\nUltra\nKyber"]
    labels = short
    ax = axes[0]
    b = ax.bar(x, d.gpus_per_mw, color=_nv_colors(d), width=0.68, zorder=2)
    hatch_future(b, [s in FUTURE for s in d.status])
    for i, v in enumerate(d.gpus_per_mw):
        ax.annotate(f"{v:,.0f}", (i, v), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.2, color=INK["title"])
    ax.set_xticks(x, labels, fontsize=7.8)
    ax.set_title("GPU packages per MW", fontsize=10.5, color=INK["title"], loc="left")
    ax.set_ylabel("GPUs per MW of IT power")
    ax.set_ylim(0, d.gpus_per_mw.max() * 1.14)
    ax2 = axes[1]
    fx = np.arange(len(f))
    b2 = ax2.bar(fx, f.fp8_pf_per_mw, color=_nv_colors(f), width=0.62, zorder=2)
    hatch_future(b2, [s in FUTURE for s in f.status])
    for i, v in enumerate(f.fp8_pf_per_mw):
        ax2.annotate(f"{v:,.0f}", (i, v), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                     fontsize=8.2, color=INK["title"])
    ax2.set_xticks(fx, short[3:], fontsize=7.8)
    ax2.set_title("Dense FP8 PFLOPS per MW (Hopper onward)", fontsize=10.5, color=INK["title"], loc="left")
    ax2.set_ylabel("Dense FP8 PFLOPS per MW")
    ax2.set_ylim(0, f.fp8_pf_per_mw.max() * 1.14)
    ax2.tick_params(length=0)
    c.save(fig, list(axes), legend=False, bottom=0.17)


# --------------------------------------------------------------------------------------
RACKS = [
    ("GB200 NVL72", "GB200 NVL72", "NVIDIA"),
    ("GB300 NVL72", "GB300 NVL72", "NVIDIA"),
    ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin NVL72 (2026)", "NVIDIA"),
    ("Rubin Ultra NVL144 Kyber (GTC 2025 name: NVL576)", "Rubin Ultra Kyber (2027)", "NVIDIA"),
    ("Helios (72x MI455X)", "AMD Helios (2026)", "AMD"),
    ("TPU7x Ironwood rack (64-chip cube)", "TPU Ironwood 64-chip cube", "Google"),
    ("Trn2 UltraServer", "Trn2 UltraServer (64)", "AWS"),
    ("Trn3 UltraServer Gen2 (144 chips)", "Trn3 UltraServer (144)", "AWS"),
    ("CloudMatrix 384", "Huawei CloudMatrix 384 (BF16)", "Huawei"),
]


def _rack_table() -> pd.DataFrame:
    df = _sys()
    tco = load(TCO)
    d = _pick(df, [n for n, _, _ in RACKS])
    d["label"] = [lab for _, lab, _ in RACKS]
    d["entity"] = [e for _, _, e in RACKS]
    cm_bf16 = tco[(tco.system == "CloudMatrix 384") & (tco.input == "bf16_pflops_dense")].value.iloc[0]
    d.loc[d.system == "CloudMatrix 384", "fp8_pflops_dense"] = cm_bf16
    return d, tco[(tco.system == "CloudMatrix 384") & (tco.input == "bf16_pflops_dense")]


@register
def system_memory_and_compute_by_rack():
    d, cm = _rack_table()
    vr = d[d.label.str.startswith("Vera Rubin")].iloc[0]
    hel = d[d.entity == "AMD"].iloc[0]
    c = Chart(
        id="08-system-memory-and-compute-by-rack",
        title=(f"AMD Helios claims ~{hel.total_hbm_tb / vr.total_hbm_tb:.1f}× Vera Rubin NVL72's HBM ({hel.total_hbm_tb:.0f} vs "
               f"{vr.total_hbm_tb:.0f} TB) and ~{hel.fp8_pflops_dense / vr.fp8_pflops_dense:.1f}× its dense FP8"),
        subtitle="Per scale-up rack or rack-like unit: total HBM (TB, left) and dense FP8 PFLOPS (right) · hatched = announced/roadmap or repo estimate",
        alt=(f"Two horizontal bar charts comparing rack-scale systems. HBM: GB200 NVL72 13.8 TB, GB300 NVL72 20.7 TB, Vera Rubin "
             f"NVL72 {vr.total_hbm_tb:.1f} TB, AMD Helios {hel.total_hbm_tb:.1f} TB, Rubin Ultra Kyber ~144 TB, Trn3 UltraServer 20.7 TB, "
             f"Huawei CloudMatrix 384 49.2 TB. Dense FP8: GB200/GB300 360 PF, Vera Rubin {vr.fp8_pflops_dense:,.0f} PF, Helios "
             f"{hel.fp8_pflops_dense:,.0f} PF, Kyber 5,000 PF, Trn3 362 PF, Ironwood 64-chip cube 295 PF, CloudMatrix 300 PF BF16."),
        data=[SYS, TCO], chapters=["08", "15", "05", "03"],
        source="NVIDIA, AMD, Google, AWS, SemiAnalysis",
        source_ids=sources_of(pd.concat([d, cm])),
    )
    fig, _ = c.figure_grid(1, 2, width=11.5, height=6.4)
    axes = manual_axes(fig, [[0.225, 0.13, 0.355, 0.66], [0.615, 0.13, 0.355, 0.66]])
    y = np.arange(len(d))[::-1]
    cols = [entity_color(e) for e in d.entity]
    est = [(s in FUTURE) or (conf == "estimate") or lab.startswith("Huawei") for s, conf, lab in
           zip(d.status, d.confidence, d.label)]
    for ax, col, ttl, fmt in [(axes[0], "total_hbm_tb", "Total HBM per unit (TB)", "{:,.1f}"),
                              (axes[1], "fp8_pflops_dense", "Dense FP8 PFLOPS per unit", "{:,.0f}")]:
        b = ax.barh(y, d[col], color=cols, height=0.66, zorder=2)
        hatch_future(b, est)
        for yi, v in zip(y, d[col]):
            ax.annotate(fmt.format(v), (v, yi), xytext=(3, 0), textcoords="offset points", va="center",
                        fontsize=8.6, color=INK["title"])
        ax.set_title(ttl, fontsize=10.5, color=INK["title"], loc="left")
        ax.set_xlim(0, d[col].max() * 1.16)
        ax.grid(axis="x", color=INK["grid"], lw=0.7)
        ax.grid(axis="y", visible=False)
        ax.tick_params(length=0)
    axes[0].set_yticks(y, d.label, fontsize=9)
    axes[1].set_yticks(y, [""] * len(y))
    axes[0].set_xlabel("TB of HBM")
    axes[1].set_xlabel("PFLOPS (dense FP8; CloudMatrix = BF16, no FP8)")
    axes[1].text(0.98, 0.02, "Ironwood cube = 64 of a 9,216-chip pod (repo calc)", transform=axes[1].transAxes,
                 ha="right", va="bottom", fontsize=8, color=INK["muted"])
    c.save(fig, list(axes), legend=False, bottom=0.14)
    # interactive twin
    try:
        import plotly.graph_objects as go
        pf = go.Figure()
        for _, r in d.iterrows():
            pf.add_trace(go.Scatter(x=[r.total_hbm_tb], y=[r.fp8_pflops_dense], mode="markers+text", text=[r.label],
                                    textposition="top center", marker=dict(size=14, color=entity_color(r.entity)),
                                    name=r.label, hovertemplate="%{text}<br>HBM %{x} TB<br>FP8 %{y} PF<extra></extra>"))
        pf.update_layout(showlegend=False, xaxis_title="Total HBM (TB, log)", yaxis_title="Dense FP8 PFLOPS (log)")
        pf.update_xaxes(type="log")
        pf.update_yaxes(type="log")
        c.save_plotly(pf)
    except Exception as exc:  # pragma: no cover
        print("plotly twin skipped:", exc)


# --------------------------------------------------------------------------------------
@register
def compute_per_kw_by_rack():
    df = _sys()
    tco = load(TCO)
    names = [("DGX H100", "DGX H100 (8 GPU)", "NVIDIA"), ("DGX B200", "DGX B200 (8 GPU)", "NVIDIA"),
             ("GB200 NVL72", "GB200 NVL72", "NVIDIA"), ("GB300 NVL72", "GB300 NVL72", "NVIDIA"),
             ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin NVL72", "NVIDIA"),
             ("Rubin Ultra NVL144 Kyber (GTC 2025 name: NVL576)", "Rubin Ultra Kyber", "NVIDIA"),
             ("Instinct MI355X Platform (8-GPU UBB 2.0)", "AMD MI355X (8 GPU)", "AMD"),
             ("Helios (72x MI455X)", "AMD Helios", "AMD"),
             ("CloudMatrix 384", "Huawei CloudMatrix 384 (BF16)", "Huawei")]
    d = _pick(df, [n for n, _, _ in names])
    d["label"] = [lab for _, lab, _ in names]
    d["entity"] = [e for _, _, e in names]
    cm = tco[(tco.system == "CloudMatrix 384") & (tco.input == "bf16_pflops_dense")]
    d.loc[d.system == "CloudMatrix 384", "fp8_pflops_dense"] = cm.value.iloc[0]
    d["pf_per_kw"] = d.fp8_pflops_dense / d.power_kw
    d = d.sort_values("pf_per_kw").reset_index(drop=True)
    vr = d[d.label == "Vera Rubin NVL72"].iloc[0]
    cmr = d[d.entity == "Huawei"].iloc[0]
    gb = d[d.label == "GB200 NVL72"].iloc[0]
    c = Chart(
        id="08-compute-per-kw-by-rack",
        title=f"Vera Rubin NVL72 targets ~{vr.pf_per_kw:.1f} FP8 PFLOPS/kW, ~{vr.pf_per_kw / cmr.pf_per_kw:.0f}× Huawei's CloudMatrix 384",
        subtitle="Peak dense FP8 PFLOPS ÷ max IT power · peak specs, not delivered throughput · hatched = roadmap or estimated power",
        alt=(f"Horizontal bar chart of dense FP8 PFLOPS per kW: Huawei CloudMatrix 384 about {cmr.pf_per_kw:.2f} (BF16), DGX H100 "
             f"about 1.5, DGX B200 about 2.5, GB300 NVL72 about 2.7, GB200 NVL72 about {gb.pf_per_kw:.1f}, AMD MI355X platform about 3.7, "
             f"Vera Rubin NVL72 about {vr.pf_per_kw:.1f}, AMD Helios about 6.0 on estimated power and Rubin Ultra Kyber about 8.3."),
        data=[SYS, TCO], chapters=["08", "14", "15"],
        source="NVIDIA, AMD, SemiAnalysis, press (repo calc)",
        source_ids=sources_of(pd.concat([d, cm])),
    )
    fig, _ = c.figure(width=10, height=6.0)
    ax = manual_axes(fig, [[0.25, 0.13, 0.71, 0.70]])[0]
    y = np.arange(len(d))
    cols = [entity_color(e) for e in d.entity]
    b = ax.barh(y, d.pf_per_kw, color=cols, height=0.64, zorder=2)
    est_power = {"GB300 NVL72", "Instinct MI355X Platform (8-GPU UBB 2.0)", "Helios (72x MI455X)", "CloudMatrix 384"}
    est = [(s in FUTURE) or (n in est_power) for s, n in zip(d.status, d.system)]
    hatch_future(b, est)
    for yi, v in zip(y, d.pf_per_kw):
        ax.annotate(f"{v:.2f}" if v < 1 else f"{v:.1f}", (v, yi), xytext=(3, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, d.label, fontsize=9.2)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, d.pf_per_kw.max() * 1.12)
    c.save(fig, ax, xlabel="Dense FP8 PFLOPS per kW", legend=False)


# --------------------------------------------------------------------------------------
@register
def system_price_by_generation():
    df = _sys()
    names = [("DGX-1 (P100)", "DGX-1 P100\n2016"), ("DGX-1 (V100)", "DGX-1 V100\n2017"), ("DGX-2", "DGX-2\n2018"),
             ("DGX A100", "DGX A100\n2020"), ("DGX H200", "DGX H200\n2024"), ("DGX B200", "DGX B200\n2024"),
             ("GB200 NVL72", "GB200 NVL72\n2024"), ("GB300 NVL72", "GB300 NVL72\n2025"),
             ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin\nNVL72 2026")]
    d = _pick(df, [n for n, _ in names])
    d["label"] = [lab for _, lab in names]
    first, last = d.iloc[0], d.iloc[-1]
    mult = last.est_price_usd_m / first.est_price_usd_m
    c = Chart(
        id="08-system-price-by-generation",
        title=f"NVIDIA system prices rose ~{mult:.0f}×: ${first.est_price_usd_m * 1000:.0f}K DGX-1 (2016) to ~${last.est_price_usd_m:.1f}M Vera Rubin rack",
        subtitle="List or estimated price per system/rack, US$ M (log scale) · servers = list/reseller price; NVL racks = analyst Est. (hatched)",
        alt=(f"Log-scale bar chart of NVIDIA system prices: DGX-1 ${first.est_price_usd_m * 1000:.0f}K (2016), DGX-1 V100 $149K, DGX-2 $399K, "
             f"DGX A100 $199K, DGX H200 about $467K, DGX B200 about $370K, then rack-scale GB200 NVL72 about $3.0M, GB300 NVL72 about $4.0M "
             f"and Vera Rubin NVL72 about ${last.est_price_usd_m:.1f}M (estimates), roughly {mult:.0f} times the first DGX-1."),
        data=[SYS], chapters=["08", "14", "13"],
        source="AnandTech, TweakTown, resellers, HSBC, Morgan Stanley",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    x = np.arange(len(d))
    cols = [GEN_PAST] * 6 + [NV] * 3
    b = ax.bar(x, d.est_price_usd_m, color=cols, width=0.64, zorder=2)
    hatch_future(b, [i >= 6 for i in range(len(d))])
    for i, v in enumerate(d.est_price_usd_m):
        lab = f"${v * 1000:.0f}K" if v < 1 else f"~${v:.1f}M"
        ax.annotate(lab, (i, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9,
                    color=INK["title"], fontweight="bold")
    ax.set_xticks(x, d.label, fontsize=8.6)
    ax.set_ylim(0.08, 20)
    log_ticks(ax, [0.1, 0.3, 1, 3, 10], ["$0.1M", "$0.3M", "$1M", "$3M", "$10M"])
    ax.legend(handles=[Patch(facecolor=GEN_PAST, label="8/16-GPU server (list or reseller price)"),
                       Patch(facecolor=NV, hatch="///", edgecolor="white", alpha=0.75, label="72-GPU rack (analyst Est.)")],
              loc="upper left", frameon=False, fontsize=9)
    c.save(fig, ax, ylabel="Price per system (US$ M)", logy=True, legend=False, bottom=0.15)


# --------------------------------------------------------------------------------------
def _tco(t: pd.DataFrame, system: str, inp: str, basis_contains: str | None = None) -> pd.Series:
    r = t[(t.system == system) & (t.input == inp)]
    if basis_contains:
        r = r[r.basis.str.contains(basis_contains, regex=False)]
    return r.iloc[0]


@register
def rack_bom_waterfall():
    t = load(TCO)
    S = "GB300 NVL72"
    price = _tco(t, S, "capex_per_rack", "Morgan Stanley")
    gpu = _tco(t, S, "bom_gpu")
    mem = _tco(t, S, "bom_memory")
    cool = _tco(t, S, "bom_cooling")
    odm_pct = _tco(t, S, "odm_gross_margin_pct")
    n_gpu = _tco(t, S, "accelerators_per_rack")
    # GPU die + packaging cost to NVIDIA, Epoch AI B200 basis (excl. HBM, which MS counts under memory)
    logic = _tco(t, "HGX B200", "bom_logic_dies")
    cowos = _tco(t, "HGX B200", "bom_cowos_l")
    other_chip = _tco(t, "HGX B200", "bom_other")
    gpu_cost = n_gpu.value * (logic.value + cowos.value + other_chip.value) / 1e6
    nv_gp = gpu.value - gpu_cost
    odm = price.value * odm_pct.value / 100
    other = price.value - gpu.value - mem.value - cool.value - odm
    used = pd.DataFrame([price, gpu, mem, cool, odm_pct, n_gpu, logic, cowos, other_chip])
    steps = [
        ("GPU dies, CoWoS-L\n& test (NVIDIA cost, Est.)", gpu_cost, GEN_PAST, True),
        ("NVIDIA gross profit\non 72 GPUs (Est.)", nv_gp, NV, True),
        ("HBM3E +\nLPDDR5X\nmemory", mem.value, "#3987E5", False),
        ("Other: Grace CPUs,\nNVLink switch trays,\nNICs, PCB, power,\nchassis (residual)", other, "#B5B5B5", False),
        ("Liquid\ncooling", cool.value, "#0F9FB0", False),
        (f"ODM gross\nmargin ({odm_pct.value:.1f}%)", odm, "#7A7A7A", False),
    ]
    share = nv_gp / price.value
    c = Chart(
        id="08-rack-bom-waterfall",
        title=f"Est. ~{share * 100:.0f}% of a ~${price.value:.1f}M GB300 NVL72 rack is NVIDIA's gross profit on the 72 GPUs alone",
        subtitle="Estimated build-up of the ODM-to-hyperscaler rack price, US$ M · Morgan Stanley BOM (May 2026) + Epoch AI B200 unit-cost basis",
        alt=(f"Waterfall chart of an estimated ${price.value:.2f}M GB300 NVL72 rack: GPU dies, CoWoS-L packaging and test about "
             f"${gpu_cost:.2f}M, NVIDIA gross profit on the GPUs about ${nv_gp:.2f}M ({share * 100:.0f}%), HBM3E and LPDDR5X memory "
             f"${mem.value:.2f}M, other rack content (Grace CPUs, NVLink switch trays, NICs, PCB, power, chassis) about ${other:.2f}M, "
             f"liquid cooling ${cool.value * 1000:.0f}K and ODM gross margin about ${odm * 1000:.0f}K."),
        data=[TCO], chapters=["08", "03", "14", "13"],
        source="Morgan Stanley via press; Epoch AI; repo calc",
        source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=11, height=6.3)
    cum = 0.0
    xs = np.arange(len(steps) + 1)
    for i, (lab, v, col, hatched) in enumerate(steps):
        b = ax.bar(i, v, bottom=cum, color=col, width=0.62, zorder=2,
                   hatch="///" if hatched else None, edgecolor="white" if hatched else None)
        ax.annotate(f"${v:.2f}M" if v >= 0.1 else f"${v * 1000:.0f}K", (i, cum + v), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=9.2, color=INK["title"],
                    fontweight="bold")
        if i < len(steps):
            ax.plot([i + 0.31, i + 0.69], [cum + v, cum + v], color=INK["muted"], lw=0.9, zorder=1)
        cum += v
    ax.bar(len(steps), price.value, color=INK["text"], width=0.62, zorder=2)
    ax.annotate(f"${price.value:.2f}M", (len(steps), price.value), xytext=(0, 3), textcoords="offset points",
                ha="center", va="bottom", fontsize=9.6, color=INK["title"], fontweight="bold")
    ax.set_xticks(xs, [s[0] for s in steps] + ["Rack price\nto hyperscaler"], fontsize=8.3)
    ax.set_ylim(0, price.value * 1.12)
    ax.text(2.55, price.value * 0.42,
            "All values Est.; hatched = repo split of Morgan Stanley's GPU line.\n"
            f"Morgan Stanley's GPU line (${gpu.value:.2f}M ≈ ${gpu.value / n_gpu.value * 1e3:.0f}K/GPU) excludes HBM;\n"
            f"cost split uses Epoch AI's B200 logic + CoWoS-L + test ≈ ${(logic.value + cowos.value + other_chip.value) / 1e3:.1f}K/GPU.",
            fontsize=8.4, color=INK["text"], va="top")
    c.save(fig, ax, ylabel="US$ M per rack", legend=False, bottom=0.2)
