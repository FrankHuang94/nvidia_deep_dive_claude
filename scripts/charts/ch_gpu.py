"""NVIDIA GPU silicon charts (layer 02 GPU, 03 memory, 17 roadmap). Owner: Phase-1 agent A1.

Data: data/gpu_product_specs.csv (dense compute only; sparse vendor figures already halved).
"""
from __future__ import annotations

import numpy as np
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
import pandas as pd

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, end_label, hatch_future, label_bars, load, register,
                   sources_of)

GPU_CSV = "gpu_product_specs.csv"
RETICLE_MM2 = 858          # 26 mm x 33 mm EUV/193i reticle field [S35010]
RETICLE_SRC = "S35010"

# Short labels and the generation's introduction year (used only for x-axis labels).
SHORT = {
    "P100 SXM2": ("P100", 2016), "V100 SXM2 32GB": ("V100", 2017), "A100 SXM 80GB": ("A100", 2020),
    "H100 SXM": ("H100", 2022), "H200 SXM": ("H200", 2024), "GH200 Grace Hopper (per GPU)": ("GH200", 2024),
    "B200 (HGX)": ("B200", 2024), "GB200 (per GPU)": ("GB200", 2024), "B300 (HGX)": ("B300", 2025),
    "GB300 (per GPU)": ("GB300", 2025), "Rubin (VR200, per GPU)": ("Rubin", 2026),
    "Rubin Ultra (per GPU)": ("Rubin Ultra", 2027), "Feynman": ("Feynman", 2028),
}
FORMAT_GREENS = {  # ordinal ramp: wider format = lighter tint, narrower = darker (single NVIDIA hue)
    "FP64": "#B9D78C", "TF32": "#94C150", "BF16/FP16": "#5F9E00", "FP8": "#447300", "FP4": "#2A4A00",
}
FUTURE_NOTE = "Hatched/dashed = roadmap or Est."


def gpus() -> pd.DataFrame:
    df = load(GPU_CSV)
    df["short"] = df["product"].map(lambda p: SHORT.get(p, (p, None))[0])
    df["gen_year"] = df["product"].map(lambda p: SHORT.get(p, (p, None))[1])
    df["future"] = df["status"].isin(["roadmap", "announced"]) | (df["confidence"] == "estimate")
    return df


def pick(df: pd.DataFrame, shorts: list[str]) -> pd.DataFrame:
    out = df.set_index("short").loc[shorts].reset_index()
    return out


def xlabels(d: pd.DataFrame) -> list[str]:
    return [f"{s}\n{int(y)}" for s, y in zip(d["short"], d["gen_year"])]


def gen_colors(d: pd.DataFrame, current: set[str]) -> list[str]:
    return [NV if s in current else GEN_PAST for s in d["short"]]


def log_badge(fig) -> None:
    """Same LOG SCALE badge style.save() draws; used when the axis is set up here (logy=False in save)."""
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


def plain_log_axis(ax, axis: str = "y") -> None:
    """Log axis with plain-number tick labels (mathtext is disabled repo-wide)."""
    def f(v, _pos):
        if v <= 0:
            return ""
        return f"{v:,.0f}" if v >= 1 else f"{v:g}"
    target = ax.yaxis if axis == "y" else ax.xaxis
    target.set_major_locator(LogLocator(base=10))
    target.set_major_formatter(FuncFormatter(f))
    target.set_minor_formatter(NullFormatter())


# --------------------------------------------------------------------------------------
@register
def flops_by_precision_log():
    df = gpus()
    gens = ["V100", "A100", "H100", "GB200", "GB300", "Rubin", "Rubin Ultra"]
    d = pick(df, gens)
    cols = {"FP64": "fp64_tflops", "TF32": "tf32_tflops_dense", "BF16/FP16": "bf16_tflops_dense",
            "FP8": "fp8_tflops_dense", "FP4": "fp4_tflops_dense"}
    v100_16 = d.loc[d.short == "V100", "bf16_tflops_dense"].item()
    rubin = d.loc[d.short == "Rubin"].iloc[0]
    mult_total = rubin.fp4_tflops_dense / v100_16
    mult_16 = rubin.bf16_tflops_dense / v100_16
    c = Chart(
        id="02-flops-by-precision-log",
        title=(f"Rubin's {rubin.fp4_tflops_dense/1000:.0f} PFLOPS dense FP4 is {mult_total:.0f}× V100's 16-bit peak; "
               f"16-bit alone grew {mult_16:.0f}×"),
        subtitle="Dense peak PFLOPS per GPU package by number format, Volta → Rubin Ultra (no sparsity; log scale)",
        alt=(f"Log-scale line chart of dense peak compute per NVIDIA GPU by format from V100 (2017) to Rubin Ultra "
             f"(2027 roadmap). Rubin reaches {rubin.fp4_tflops_dense/1000:.0f} PFLOPS FP4 and "
             f"{rubin.fp8_tflops_dense/1000:.1f} PFLOPS FP8, {mult_total:.0f} times V100's {v100_16:.0f} TFLOPS FP16, "
             f"while 16-bit throughput grew only {mult_16:.0f} times and FP64 fell to about 1.4 TFLOPS on Blackwell "
             f"Ultra before recovering to 33 TFLOPS on Rubin."),
        data=[GPU_CSV], chapters=["02", "17"],
        source="NVIDIA specs", source_ids=sources_of(d), note=FUTURE_NOTE,
    )
    fig, ax = c.figure(width=10, height=6.0)
    x = np.arange(len(d))
    markers = {"FP64": "o", "TF32": "s", "BF16/FP16": "^", "FP8": "D", "FP4": "P"}
    future = d["future"].to_numpy()
    for name, col in cols.items():
        y = d[col].to_numpy(dtype=float) / 1000.0
        color = FORMAT_GREENS[name]
        ok = ~np.isnan(y)
        # solid segments between shipping points, dashed into roadmap points
        idx = np.where(ok)[0]
        for a, b in zip(idx[:-1], idx[1:]):
            ls = "--" if future[b] else "-"
            ax.plot([x[a], x[b]], [y[a], y[b]], color=color, lw=2, ls=ls, zorder=2)
        for i in idx:
            ax.plot(x[i], y[i], marker=markers[name], ms=8, color=color,
                    mfc="white" if future[i] else color, mew=2, zorder=3, ls="none")
        last = idx[-1]
        end_label(ax, x[last], y[last], name, color, dx=9)
    ax.plot([], [], color=INK["text"], ls="--", marker="P", mfc="white", label="Roadmap (Est. dense)")
    ax.set_xticks(x, xlabels(d))
    ax.set_xlim(-0.4, len(d) - 0.2)
    ax.set_ylim(0.0006, 200)
    ax.axvspan(len(d) - 1.5, len(d) - 0.2, color="#F3F2EE", zorder=0)
    ax.text(len(d) - 1, 120, "Roadmap", ha="center", va="center", fontsize=9, color=INK["muted"])
    ax.annotate(f"FP64 cut to\n{d.loc[d.short=='GB300','fp64_tflops'].item():.1f} TFLOPS",
                (x[4], d.loc[d.short == "GB300", "fp64_tflops"].item() / 1000), xytext=(-62, -6),
                textcoords="offset points", fontsize=8.5, color=INK["text"], ha="center")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_yscale("log")
    plain_log_axis(ax)
    log_badge(fig)
    c.save(fig, ax, xlabel="GPU generation (year introduced)", ylabel="Dense PFLOPS per GPU (log scale)")

    # Interactive twin
    try:
        import plotly.graph_objects as go
        pf = go.Figure()
        for name, col in cols.items():
            y = d[col] / 1000.0
            pf.add_trace(go.Scatter(x=d["short"], y=y, mode="lines+markers", name=name,
                                    line=dict(color=FORMAT_GREENS[name], width=2),
                                    hovertemplate="%{x}: %{y:.3f} PFLOPS dense " + name + "<extra></extra>"))
        pf.update_yaxes(type="log", title="Dense PFLOPS per GPU (log scale)")
        pf.update_xaxes(title="GPU generation")
        c.save_plotly(pf)
    except Exception:  # pragma: no cover - plotly optional
        pass


@register
def transistor_count_by_generation():
    df = gpus()
    d = pick(df, ["P100", "V100", "A100", "H100", "B200", "Rubin"])
    first, last = d.iloc[0], d.iloc[-1]
    mult = last.transistors_b / first.transistors_b
    c = Chart(
        id="02-transistor-count-by-generation",
        title=(f"Transistors per GPU rose {mult:.0f}× from P100 to Rubin ({first.transistors_b:.1f}B → "
               f"{last.transistors_b:.0f}B), now on two dies"),
        subtitle="Transistors per GPU package, billions; dies per package labeled (flagship datacenter GPU per generation)",
        alt=(f"Bar chart of transistors per NVIDIA datacenter GPU: P100 {first.transistors_b:.1f}B (2016), V100 21.1B, "
             f"A100 54.2B, H100 80B, B200 208B on two dies and Rubin {last.transistors_b:.0f}B on two dies, a "
             f"{mult:.0f}-fold rise; since Blackwell the growth comes from adding a second reticle-sized die."),
        data=[GPU_CSV], chapters=["02"], source="NVIDIA whitepapers",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(d))
    bars = ax.bar(x, d.transistors_b, color=gen_colors(d, {"Rubin"}), width=0.62)
    label_bars(ax, bars, fmt="{:,.1f}B")
    ax.set_xticks(x, [f"{lab}\n{int(n)} die" + ("s" if n > 1 else "")
                      for lab, n in zip(xlabels(d), d.dies_per_package)])
    ax.set_ylim(0, d.transistors_b.max() * 1.15)
    c.save(fig, ax, xlabel="GPU generation (year introduced)", ylabel="Transistors per package (billions)")


@register
def tdp_by_generation():
    df = gpus()
    order = ["P100", "V100", "A100", "H100", "H200", "B200", "GB200", "B300", "GB300", "Rubin"]
    d = pick(df, order)
    v100 = d.loc[d.short == "V100", "tdp_w"].item()
    rubin = d.loc[d.short == "Rubin", "tdp_w"].item()
    c = Chart(
        id="02-tdp-by-generation",
        title=f"Power per GPU rose ~{rubin/v100:.1f}× from V100 ({v100:.0f} W) to Rubin (~{rubin:,.0f} W, Max-P)",
        subtitle="Maximum power per GPU package, watts (superchip rows exclude the CPU share; Rubin is press-reported)",
        alt=(f"Bar chart of NVIDIA GPU package power: P100 and V100 at {v100:.0f} W, A100 400 W, H100 and H200 700 W, "
             f"B200 1,000 W, GB200 1,200 W, B300 1,100 W, GB300 1,400 W and Rubin about {rubin:,.0f} W in its "
             f"reported Max-P profile (1,800 W Max-Q), roughly {rubin/v100:.1f} times V100."),
        data=[GPU_CSV], chapters=["02", "03", "17"], source="NVIDIA specs; SemiAnalysis",
        source_ids=sources_of(d), note="Hatched = press-reported",
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(d))
    bars = ax.bar(x, d.tdp_w, color=gen_colors(d, {"Rubin", "GB300"}), width=0.62)
    hatch_future(bars, (d.short == "Rubin").tolist())
    label_bars(ax, bars, fmt="{:,.0f} W")
    ri = int(np.where(d.short == "Rubin")[0][0])
    ax.hlines(1800, ri - 0.31, ri + 0.31, color=INK["title"], lw=1.6, ls=":")
    ax.annotate("Max-Q ~1,800 W", (ri - 0.31, 1800), xytext=(-62, 0), textcoords="offset points", va="center",
                ha="center", fontsize=8.5, color=INK["text"], arrowprops=dict(arrowstyle="-", color=INK["muted"]))
    ax.set_xticks(x, xlabels(d))
    ax.set_ylim(0, rubin * 1.15)
    c.save(fig, ax, xlabel="GPU (year introduced)", ylabel="Power per GPU package (W)")


@register
def perf_per_watt_by_generation():
    df = gpus()
    order = ["V100", "A100", "H100", "H200", "B200", "GB200", "B300", "GB300", "Rubin"]
    d = pick(df, order).copy()

    def best(r):
        for col, lab in (("fp4_tflops_dense", "FP4"), ("fp8_tflops_dense", "FP8"), ("bf16_tflops_dense", "BF16")):
            if pd.notna(r[col]):
                lab = "FP16" if (lab == "BF16" and r["short"] == "V100") else lab
                return r[col], lab
        return np.nan, ""

    d[["best_tf", "best_fmt"]] = d.apply(lambda r: pd.Series(best(r)), axis=1)
    d["eff"] = d.best_tf / d.tdp_w
    d["eff_fp8"] = d.fp8_tflops_dense / d.tdp_w
    v, h, r = (d.set_index("short").loc[k] for k in ("V100", "H100", "Rubin"))
    m_best = r.eff / v.eff
    m_fp8 = r.eff_fp8 / h.eff_fp8
    c = Chart(
        id="02-perf-per-watt-by-generation",
        title=f"Compute/W rose {m_best:.0f}× V100→Rubin, but just {m_fp8:.1f}× over H100 at like-for-like FP8",
        subtitle="Dense TFLOPS per watt of package power: bars = best low-precision format (labeled); diamonds = FP8",
        alt=(f"Bar chart of dense TFLOPS per watt for NVIDIA GPUs. Using each generation's best low-precision format, "
             f"efficiency rose from {v.eff:.2f} TFLOPS/W on V100 (FP16) to {h.eff:.1f} on H100 (FP8) and {r.eff:.1f} on "
             f"Rubin (FP4 at ~2,300 W), {m_best:.0f} times overall; at the same FP8 format Rubin delivers "
             f"{r.eff_fp8:.1f} TFLOPS/W, {m_fp8:.1f} times H100, so most of the gain comes from smaller number formats."),
        data=[GPU_CSV], chapters=["02", "14"], source="NVIDIA specs; repo calc.",
        source_ids=sources_of(d), note="Hatched = reported power",
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(d))
    bars = ax.bar(x, d.eff, color=gen_colors(d, {"Rubin", "GB300", "B300"}), width=0.62, label="Best format")
    hatch_future(bars, (d.short == "Rubin").tolist())
    for xi, (e, f) in enumerate(zip(d.eff, d.best_fmt)):
        ax.annotate(f"{e:.1f}\n{f}", (xi, e), xytext=(0, 12 if f == "FP8" else 3), textcoords="offset points", ha="center",
                    va="bottom", fontsize=8.3, color=INK["text"])
    ax.plot(x, d.eff_fp8, ls="none", marker="D", ms=8, color=INK["title"], mfc="white", mew=1.8,
            label="FP8 like-for-like", zorder=4)
    ax.set_xticks(x, xlabels(d))
    ax.set_ylim(0, d.eff.max() * 1.25)
    ax.legend(loc="upper left")
    c.save(fig, ax, xlabel="GPU (year introduced)", ylabel="Dense TFLOPS per watt", legend=False)


@register
def die_area_vs_reticle_limit():
    df = gpus()
    d = pick(df, ["P100", "V100", "A100", "H100", "B200", "Rubin", "Rubin Ultra"]).copy()
    d["total"] = d.die_area_mm2_per_die * d.dies_per_package
    est = d.short.isin(["B200", "Rubin", "Rubin Ultra"]).tolist()
    pct = d.loc[d.short == "V100", "die_area_mm2_per_die"].item() / RETICLE_MM2
    ids = [RETICLE_SRC] + sources_of(d)
    c = Chart(
        id="02-die-area-vs-reticle-limit",
        title=(f"Dies hit ~{pct*100:.0f}% of the {RETICLE_MM2} mm² reticle by Volta; NVIDIA now scales "
               "by adding dies"),
        subtitle="Area per compute die, mm², vs the ~858 mm² lithography reticle limit; dies per package and total silicon labeled",
        alt=(f"Bar chart of die area per NVIDIA GPU compute die against the {RETICLE_MM2} mm2 reticle limit: P100 610 mm2, "
             f"V100 815, A100 826 and H100 814 mm2 sit at about {pct*100:.0f} percent of the limit; Blackwell and Rubin "
             f"use two reticle-sized dies (about 1,600 mm2 of compute silicon, estimated) and Rubin Ultra four "
             f"(about 3,200 mm2), so scaling now comes from packaging more dies rather than larger ones."),
        data=[GPU_CSV], chapters=["02", "03"], source="NVIDIA; SemiEngineering",
        source_ids=ids, note="Hatched = Est. area / roadmap",
    )
    fig, ax = c.figure(width=10, height=5.8)
    x = np.arange(len(d))
    colors = [GEN_PAST] * 4 + [NV, NV, NV]
    bars = ax.bar(x, d.die_area_mm2_per_die, color=colors, width=0.62)
    hatch_future(bars, est)
    ax.axhline(RETICLE_MM2, color=INK["title"], lw=1.4, ls="--")
    ax.text(-0.45, RETICLE_MM2 + 18, f"Reticle limit ~{RETICLE_MM2} mm² (26 × 33 mm)", fontsize=9,
            color=INK["title"], va="bottom")
    for xi, (a, n, t, e) in enumerate(zip(d.die_area_mm2_per_die, d.dies_per_package, d.total, est)):
        lab = f"{a:,.0f}" + (" (Est.)" if e else "")
        ax.text(xi, a / 2, lab, ha="center", va="center", fontsize=8.5, color=INK["title"], fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none") if e else None)
        ax.text(xi, 935, f"×{int(n)} die" + ("s" if n > 1 else "") + (f"\n≈{t:,.0f} mm²" if n > 1 else ""),
                ha="center", va="bottom", fontsize=8.5, color=NV_DARK if n > 1 else INK["text"],
                fontweight="bold" if n > 1 else "normal")
    ax.set_xticks(x, xlabels(d))
    ax.set_ylim(0, 1130)
    c.save(fig, ax, xlabel="GPU generation (year introduced)", ylabel="Area per compute die (mm²)")


@register
def fp64_vs_low_precision():
    df = gpus()
    d = pick(df, ["P100", "V100", "A100", "H100", "B200", "GB200", "B300", "GB300", "Rubin"])
    h = d.loc[d.short == "H100", "fp64_tflops"].item()
    gb3 = d.loc[d.short == "GB300", "fp64_tflops"].item()
    rub = d.loc[d.short == "Rubin", "fp64_tflops"].item()
    c = Chart(
        id="02-fp64-per-gpu-by-generation",
        title=f"FP64 peaked at {h:.0f} TFLOPS per GPU on Hopper; Blackwell Ultra cut it to ~{gb3:.1f} TFLOPS",
        subtitle="Peak FP64 TFLOPS per GPU (Tensor Core where available); Rubin native rate shown, emulated DGEMM excluded",
        alt=(f"Bar chart of FP64 throughput per NVIDIA GPU: P100 5.3, V100 7.8, A100 19.5 and H100 {h:.0f} TFLOPS, then "
             f"B200 37, GB200 40, B300 1.25 and GB300 {gb3:.2f} TFLOPS, recovering to {rub:.0f} TFLOPS native on Rubin "
             f"(NVIDIA quotes 200 TFLOPS via emulation); NVIDIA is trading double precision for AI formats."),
        data=[GPU_CSV], chapters=["02", "18"], source="NVIDIA specs", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(d))
    bars = ax.bar(x, d.fp64_tflops, color=gen_colors(d, {"GB300", "B300", "Rubin"}), width=0.62)
    label_bars(ax, bars, fmt="{:,.1f}")
    ax.annotate("Blackwell Ultra:\nFP64 ~1 TFLOPS", (6.5, 3), xytext=(6.5, 30), ha="center", fontsize=8.5,
                color=INK["text"], arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.set_xticks(x, xlabels(d))
    ax.set_ylim(0, h * 1.18)
    c.save(fig, ax, xlabel="GPU (year introduced)", ylabel="FP64 TFLOPS per GPU")


@register
def hbm_bandwidth_per_gpu():
    df = gpus()
    d = pick(df, ["P100", "V100", "A100", "H100", "H200", "B200", "B300", "Rubin", "Rubin Ultra"])
    first = d.iloc[0]
    rub = d.loc[d.short == "Rubin"].iloc[0]
    mult = rub.memory_bandwidth_tbs / first.memory_bandwidth_tbs
    c = Chart(
        id="03-hbm-bandwidth-per-gpu",
        title=(f"HBM bandwidth per GPU rose {mult:.0f}× from P100 to Rubin "
               f"({first.memory_bandwidth_tbs:.2f} → {rub.memory_bandwidth_tbs:.1f} TB/s)"),
        subtitle="Peak memory bandwidth per GPU package, TB/s; Rubin shown at the revised production figure",
        alt=(f"Bar chart of HBM bandwidth per NVIDIA GPU: P100 {first.memory_bandwidth_tbs:.2f} TB/s, V100 0.9, "
             f"A100 2.0, H100 3.35, H200 4.8, B200 and B300 8, Rubin {rub.memory_bandwidth_tbs:.1f} TB/s (cut from a "
             f"22 TB/s launch target in late 2026) and Rubin Ultra about 32 TB/s on the 2027 roadmap; "
             f"a {mult:.0f}-fold rise from P100 to Rubin."),
        data=[GPU_CSV], chapters=["03", "02", "17"], source="NVIDIA specs; press",
        source_ids=sources_of(d), note=FUTURE_NOTE,
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(d))
    bars = ax.bar(x, d.memory_bandwidth_tbs, color=gen_colors(d, {"Rubin", "Rubin Ultra", "B300"}), width=0.62)
    hatch_future(bars, d.future.tolist())
    label_bars(ax, bars, fmt="{:,.1f}")
    ri = int(np.where(d.short == "Rubin")[0][0])
    ax.plot(ri, 22, marker="_", ms=26, mew=2, color=INK["title"])
    ax.annotate("Launch target 22 TB/s\n(revised 2026)", (ri, 22), xytext=(-95, 6), textcoords="offset points",
                fontsize=8.5, color=INK["text"], va="center", arrowprops=dict(arrowstyle="-", color=INK["muted"]))
    ax.set_xticks(x, xlabels(d))
    ax.set_ylim(0, d.memory_bandwidth_tbs.max() * 1.15)
    c.save(fig, ax, xlabel="GPU (year introduced)", ylabel="Memory bandwidth per GPU (TB/s)")


@register
def hbm_capacity_per_gpu():
    df = gpus()
    d = pick(df, ["P100", "V100", "A100", "H100", "H200", "B200", "GB200", "B300", "Rubin", "Rubin Ultra"])
    first = d.iloc[0]
    rub = d.loc[d.short == "Rubin"].iloc[0]
    ru = d.loc[d.short == "Rubin Ultra"].iloc[0]
    mult = rub.memory_capacity_gb / first.memory_capacity_gb
    c = Chart(
        id="03-hbm-capacity-per-gpu",
        title=(f"HBM per GPU grew {mult:.0f}× from P100 to Rubin ({first.memory_capacity_gb:.0f} → "
               f"{rub.memory_capacity_gb:.0f} GB); Rubin Ultra targets {ru.memory_capacity_gb/1024:.0f} TB"),
        subtitle="HBM capacity per GPU package, GB (usable capacity as specified; roadmap hatched)",
        alt=(f"Bar chart of HBM capacity per NVIDIA GPU: P100 {first.memory_capacity_gb:.0f} GB, V100 32, A100 and H100 80, "
             f"H200 141, B200 180, GB200 186, B300 and Rubin {rub.memory_capacity_gb:.0f} GB, and Rubin Ultra "
             f"{ru.memory_capacity_gb:,.0f} GB as announced for 2027 (2026 reports suggest 768 GB); "
             f"{mult:.0f} times more from P100 to Rubin."),
        data=[GPU_CSV], chapters=["03", "02", "17"], source="NVIDIA specs and roadmap",
        source_ids=sources_of(d), note=FUTURE_NOTE,
    )
    fig, ax = c.figure(width=10, height=5.6)
    x = np.arange(len(d))
    bars = ax.bar(x, d.memory_capacity_gb, color=gen_colors(d, {"Rubin", "Rubin Ultra", "B300"}), width=0.62)
    hatch_future(bars, d.future.tolist())
    label_bars(ax, bars, fmt="{:,.0f}")
    rui = int(np.where(d.short == "Rubin Ultra")[0][0])
    ax.plot(rui, 768, marker="_", ms=26, mew=2, color=INK["title"])
    ax.annotate("768 GB if cut\n(2026 reports)", (rui, 768), xytext=(-88, -4), textcoords="offset points",
                fontsize=8.5, color=INK["text"], va="center", arrowprops=dict(arrowstyle="-", color=INK["muted"]))
    ax.set_xticks(x, xlabels(d))
    ax.set_ylim(0, d.memory_capacity_gb.max() * 1.12)
    c.save(fig, ax, xlabel="GPU (year introduced)", ylabel="HBM capacity per GPU (GB)")


@register
def compute_vs_memory_bandwidth_growth():
    df = gpus()
    d = pick(df, ["V100", "A100", "H100", "H200", "B200", "GB300", "Rubin", "Rubin Ultra"]).copy()
    d["best"] = d[["fp4_tflops_dense", "fp8_tflops_dense", "bf16_tflops_dense"]].max(axis=1)
    base = d.iloc[0]
    d["i_best"] = d.best / base.best
    d["i_16"] = d.bf16_tflops_dense / base.bf16_tflops_dense
    d["i_bw"] = d.memory_bandwidth_tbs / base.memory_bandwidth_tbs
    r = d.loc[d.short == "Rubin"].iloc[0]
    c = Chart(
        id="03-compute-vs-memory-bandwidth-growth",
        title=(f"Since V100, compute grew {r.i_best:.0f}× but HBM bandwidth only {r.i_bw:.0f}×: "
               "the memory wall"),
        subtitle="Per-GPU growth indexed to V100 = 1: dense peak FLOPS (best format, and 16-bit) vs HBM bandwidth (log scale)",
        alt=(f"Log-scale index chart with V100 = 1: by Rubin, dense compute in the best supported format is {r.i_best:.0f} "
             f"times V100 and 16-bit compute {r.i_16:.0f} times, while HBM bandwidth is only {r.i_bw:.0f} times "
             f"higher, so each byte of memory bandwidth must feed far more math - the memory wall that makes "
             f"LLM decode bandwidth-bound."),
        data=[GPU_CSV], chapters=["03", "02", "P3"], source="NVIDIA specs; repo index",
        source_ids=sources_of(d), note="Dashed = roadmap (Est.)",
    )
    fig, ax = c.figure(width=10, height=5.8)
    x = np.arange(len(d))
    fut = d.future.to_numpy()
    series = [("i_best", "Compute, best format (FP16→FP8→FP4)", NV),
              ("i_16", "Compute, 16-bit only", GEN_PAST),
              ("i_bw", "HBM bandwidth", "#256ABF")]
    for col, lab, colr in series:
        y = d[col].to_numpy(dtype=float)
        ok = np.where(~np.isnan(y))[0]
        for a, b in zip(ok[:-1], ok[1:]):
            ax.plot([x[a], x[b]], [y[a], y[b]], color=colr, lw=2.2, ls="--" if fut[b] else "-")
        ax.plot(x[ok], y[ok], ls="none", marker="o", ms=7, color=colr, label=lab)
        ax.plot(x[ok][fut[ok]], y[ok][fut[ok]], ls="none", marker="o", ms=7, mfc="white", mec=colr, mew=2)
        last = ok[-1]
        end_label(ax, x[last], y[last], f"{y[last]:.0f}×", colr, dx=8)
    ax.set_xticks(x, xlabels(d))
    ax.set_xlim(-0.3, len(d) - 0.4)
    ax.set_ylim(0.8, 1000)
    ax.legend(loc="upper left")
    ax.set_yscale("log")
    plain_log_axis(ax)
    log_badge(fig)
    c.save(fig, ax, xlabel="GPU (year introduced)", ylabel="Index, V100 = 1 (log scale)", legend=False)


@register
def spec_progression_small_multiples():
    df = gpus()
    order = ["H100", "H200", "B200", "GB300", "Rubin", "Rubin Ultra", "Feynman"]
    d = pick(df, order).copy()
    d["lowp"] = d.fp4_tflops_dense.fillna(d.fp8_tflops_dense) / 1000
    d["lowp_fmt"] = np.where(d.fp4_tflops_dense.notna(), "FP4", np.where(d.fp8_tflops_dense.notna(), "FP8", ""))
    h, r = d.set_index("short").loc["H100"], d.set_index("short").loc["Rubin"]
    m = dict(c=r.lowp / h.lowp, bw=r.memory_bandwidth_tbs / h.memory_bandwidth_tbs,
             cap=r.memory_capacity_gb / h.memory_capacity_gb, pw=r.tdp_w / h.tdp_w)
    c = Chart(
        id="17-spec-progression-small-multiples",
        title=(f"H100 → Rubin: low-precision compute {m['c']:.0f}×, HBM bandwidth {m['bw']:.1f}×, "
               f"capacity {m['cap']:.1f}×, power {m['pw']:.1f}×"),
        subtitle="Per-GPU specs by generation, 2022–2028: dense FP8 (Hopper) or FP4 (Blackwell+) PFLOPS, HBM TB/s, HBM GB, W",
        alt=(f"Four small-multiple bar charts of NVIDIA GPU specs from H100 (2022) to Feynman (2028). From H100 to Rubin, "
             f"dense low-precision compute rose {m['c']:.0f} times (2.0 PFLOPS FP8 to 35 PFLOPS FP4), HBM bandwidth "
             f"{m['bw']:.1f} times (3.35 to 19.2 TB/s), capacity {m['cap']:.1f} times (80 to 288 GB) and power "
             f"{m['pw']:.1f} times (700 to about 2,300 W). Rubin Ultra (2027) is hatched; Feynman figures are not "
             f"yet disclosed."),
        data=[GPU_CSV], chapters=["17", "02", "03"], source="NVIDIA specs and roadmap",
        source_ids=sources_of(d), note="Hatched = roadmap; n/d = not disclosed",
    )
    fig, axes = c.figure_grid(2, 2, width=11, height=7.2)
    panels = [("lowp", "Dense low-precision PFLOPS", "{:,.1f}"),
              ("memory_bandwidth_tbs", "HBM bandwidth (TB/s)", "{:,.1f}"),
              ("memory_capacity_gb", "HBM capacity (GB)", "{:,.0f}"),
              ("tdp_w", "Power per GPU (W)", "{:,.0f}")]
    x = np.arange(len(d))
    for ax, (col, lab, fmt) in zip(axes.flat, panels):
        vals = d[col].astype(float)
        bars = ax.bar(x, vals.fillna(0), color=gen_colors(d, {"Rubin", "Rubin Ultra", "Feynman"}), width=0.66)
        hatch_future(bars, d.future.tolist())
        for xi, v in enumerate(vals):
            if np.isnan(v):
                ax.text(xi, 0, "n/d", ha="center", va="bottom", fontsize=8, color=INK["muted"])
            else:
                ax.annotate(fmt.format(v), (xi, v), xytext=(0, 2), textcoords="offset points", ha="center",
                            va="bottom", fontsize=8, color=INK["text"])
        if col == "lowp":
            for xi, (f, v) in enumerate(zip(d.lowp_fmt, vals)):
                if f and v > 5:
                    ax.text(xi, 0.6, f, ha="center", va="bottom", fontsize=7.5, color="white", fontweight="bold")
        if col == "tdp_w":
            ax.text(4, 60, "rep.", ha="center", va="bottom", fontsize=7.5, color="white")
        ax.set_title(lab, fontsize=10.5, color=INK["title"], loc="left", fontweight="bold")
        ax.set_xticks(x, [f"{s.replace(' ', chr(10))}\n{int(y)}" for s, y in zip(d.short, d.gen_year)], fontsize=8.3)
        ax.set_ylim(0, np.nanmax(vals) * 1.2)
    fig.subplots_adjust(hspace=0.62, wspace=0.18)
    c.save(fig, axes, top=0.83, bottom=0.13)
