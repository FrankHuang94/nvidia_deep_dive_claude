"""Primer P3 - the four bottlenecks: roofline, arithmetic intensity, rack power, power demand, bottleneck map.

Data: data/gpu_product_specs.csv (shared; falls back to data/P3_roofline_inputs.csv), system_specs.csv (shared),
P3_workload_intensity.csv, P3_power_demand.csv, P3_bottleneck_matrix.csv (documented in data/README.md).
The memory-wall index chart lives in the shared library as 03-compute-vs-memory-bandwidth-growth.
"""
import pandas as pd
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, load, register, sources_of)

CH = ["P3", "02", "03", "05", "11"]
GPU_STYLE = {  # past generation tint -> current -> announced (dashed)
    "H100 SXM": dict(color=GEN_PAST, ls="-", label="H100"),
    "B200 (HGX)": dict(color=NV, ls="-", label="B200"),
    "Rubin": dict(color=NV_DARK, ls="--", label="Rubin (2H 2026 ramp)"),
}


def _plain_log(ax, axis="both"):
    """Plain-number tick labels on log axes (mathtext is disabled repo-wide)."""
    fmt = FuncFormatter(lambda v, _: f"{v:,.0f}" if v >= 1 else f"{v:g}")
    targets = [ax.xaxis, ax.yaxis] if axis == "both" else [ax.xaxis if axis == "x" else ax.yaxis]
    for a in targets:
        a.set_major_locator(LogLocator(base=10))
        a.set_major_formatter(fmt)
        a.set_minor_formatter(NullFormatter())


def _log_badge(fig):
    """Same LOG SCALE badge style.Chart.save() stamps; used when we set log axes ourselves so that
    save() does not reset our plain-number tick formatters."""
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


ROOF_COLS = ["bf16_tflops_dense", "fp8_tflops_dense", "fp4_tflops_dense", "memory_bandwidth_tbs", "source_id"]
SHARED_MATCH = {"H100 SXM": "H100 SXM", "B200 (HGX)": "B200 (HGX)", "Rubin": "Rubin (VR200"}


def _roof_inputs():
    """H100 / B200 / Rubin dense specs: from the shared gpu_product_specs.csv when it has all three rows,
    else from this primer's own P3_roofline_inputs.csv. Returns (frame indexed by GPU_STYLE keys, file name)."""
    try:
        g = load("gpu_product_specs.csv")
        rows = {}
        for key, pat in SHARED_MATCH.items():
            hit = g[g["product"].astype(str).str.startswith(pat)]
            if hit.empty or hit.iloc[0][ROOF_COLS[:2] + ["memory_bandwidth_tbs"]].isna().any():
                raise KeyError(key)
            rows[key] = hit.iloc[0][ROOF_COLS]
        return pd.DataFrame(rows).T, "gpu_product_specs.csv"
    except (KeyError, FileNotFoundError, ValueError):
        df = load("P3_roofline_inputs.csv").set_index("product")
        return df.loc[[k for k in GPU_STYLE if k in df.index], ROOF_COLS], "P3_roofline_inputs.csv"


@register
def roofline_h100_b200_rubin():
    df, fname = _roof_inputs()
    gpus = [g for g in GPU_STYLE if g in df.index]
    wl = load("P3_workload_intensity.csv")
    ridges = {g: df.loc[g, "bf16_tflops_dense"] / df.loc[g, "memory_bandwidth_tbs"] for g in gpus}
    b = df.loc["B200 (HGX)"]
    spec = "; ".join(f"{GPU_STYLE[g]['label'].split(' (')[0]}: {df.loc[g, 'bf16_tflops_dense']:,.0f} TFLOPS and "
                     f"{df.loc[g, 'memory_bandwidth_tbs']:g} TB/s, ridge point about {ridges[g]:.0f} FLOPs per byte"
                     for g in gpus)
    c = Chart(
        id="P3-roofline-h100-b200-rubin",
        title="Batch-1 decode sits ~200-300x left of the ridge point and uses under 1% of peak FLOPS",
        subtitle="Roofline: attainable dense BF16 TFLOPS per GPU vs arithmetic intensity (FLOPs per byte read from HBM), log-log",
        alt=(f"Log-log roofline chart in dense BF16. {spec}. "
             "Batch-1 decode (about 1 FLOP per byte) sits far left on the bandwidth slope; batch 64 (63) and batch 256 (241) "
             "move right; prefill (about 1,365) and training matrix multiplies (about 3,277) sit on the flat compute roof."),
        data=[fname, "P3_workload_intensity.csv"], chapters=CH,
        source="NVIDIA and Lenovo spec sheets; repo arithmetic", source_ids=["S33002", "S33003", "S33005", "S33007", "S33013"],
    )
    fig, ax = c.figure(width=10.5, height=6.4)
    x = np.logspace(-0.3, 4.0, 400)
    for g in gpus:
        st = GPU_STYLE[g]
        peak = df.loc[g, "bf16_tflops_dense"]
        bw = df.loc[g, "memory_bandwidth_tbs"]  # TB/s -> TFLOPS per (FLOP/byte)
        y = np.minimum(peak, bw * x)
        ax.plot(x, y, color=st["color"], ls=st["ls"], lw=2.4, label=f"{st['label']}: {peak:,.0f} TFLOPS, {bw:g} TB/s")
        r = ridges[g]
        ax.plot([r], [peak], "o", color=st["color"], ms=8, zorder=5)
    # ridge labels (stacked to avoid overlap)
    offs = {"H100 SXM": (12, -16), "B200 (HGX)": (12, -16), "Rubin": (-150, 8)}
    for g in gpus:
        r, peak = ridges[g], df.loc[g, "bf16_tflops_dense"]
        ax.annotate(f"ridge ≈ {r:,.0f} FLOPs/B", (r, peak), xytext=offs[g], textcoords="offset points",
                    fontsize=8.6, color=GPU_STYLE[g]["color"] if g != "H100 SXM" else INK["text"], fontweight="bold")
    # workload markers
    picks = ["Decode (batch 1)", "Decode (batch 64)", "Decode (batch 256)", "Prefill (2048-token prompt)",
             "Training GEMM (16K tokens per GPU)"]
    short = {"Decode (batch 1)": "decode\nbatch 1", "Decode (batch 64)": "decode\nbatch 64",
             "Decode (batch 256)": "decode\nbatch 256", "Prefill (2048-token prompt)": "prefill\n2K prompt",
             "Training GEMM (16K tokens per GPU)": "training\nGEMM"}
    for _, row in wl[wl.workload.isin(picks)].iterrows():
        ai = row.arithmetic_intensity_flops_per_byte
        ax.axvline(ai, color=INK["muted"], lw=1, ls=":", zorder=1)
        ax.text(ai, 1.15, short[row.workload], ha="center", va="bottom", fontsize=8.3, color=INK["text"],
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))
        ach = min(b.bf16_tflops_dense, b.memory_bandwidth_tbs * ai)
        ax.plot([ai], [ach], "s", color=NV, ms=6, zorder=6)
    ax.text(0.6, 260, "memory-bound zone\n(on the bandwidth slope)", fontsize=9.5, color=SEQ_BLUE[6], ha="left")
    ax.text(1500, 6200, "compute-bound (flat roof)", fontsize=9.5, color=NV_DARK, ha="center")
    ax.annotate("B200 at batch 1: 8 of 2,250 TFLOPS\n(≈0.4% of peak)", (1.0, b.memory_bandwidth_tbs * 1.0),
                xytext=(2.6, 1.7), fontsize=8.6, color=INK["text"],
                arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    ax.set_xlim(0.5, 10000)
    ax.set_ylim(1, 12000)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid(True, which="major", axis="both", color=INK["grid"])
    ax.legend(loc="upper left", fontsize=8.8)
    _plain_log(ax)
    _log_badge(fig)
    c.save(fig, ax, xlabel="Arithmetic intensity, FLOPs per byte (log scale)",
           ylabel="Attainable dense BF16 TFLOPS (log scale)", legend=False)


@register
def workload_arithmetic_intensity():
    wl = load("P3_workload_intensity.csv").sort_values("arithmetic_intensity_flops_per_byte")
    df, fname = _roof_inputs()
    bf16 = {g: df.loc[g, "bf16_tflops_dense"] / df.loc[g, "memory_bandwidth_tbs"] for g in GPU_STYLE}
    fp8 = {g: df.loc[g, "fp8_tflops_dense"] / df.loc[g, "memory_bandwidth_tbs"] for g in GPU_STYLE}
    lo, hi = (int(v + 0.5) for v in (min(bf16.values()), max(bf16.values())))
    lo8, hi8 = (int(v + 0.5) for v in (min(fp8.values()), max(fp8.values())))
    c = Chart(
        id="P3-workload-arithmetic-intensity",
        title="Decode runs up to ~300x below the ridge point; only prefill and training clear it",
        subtitle="Arithmetic intensity of common LLM operations (FLOPs per byte, BF16, 70B-class layer), vs GPU ridge points",
        alt=(f"Horizontal bar chart on a log scale of arithmetic intensity: batch-1 decode about 1 FLOP per byte, decode attention "
             f"and MoE expert matrix multiplies about 8, batch-64 decode 63, batch-256 decode 241, a 2,048-token prefill 1,365 and "
             f"a training matrix multiply 3,277. The BF16 ridge points of H100, B200 and Rubin fall between {lo:.0f} and {hi:.0f} "
             f"FLOPs per byte and the FP8 ridge points between {lo8:.0f} and {hi8:.0f}, so only prefill and training clear them."),
        data=["P3_workload_intensity.csv", fname], chapters=CH,
        source="Pope et al.; kipply; DeepSeek-V3 report; NVIDIA specs; repo arithmetic", source_ids=sources_of(wl),
    )
    fig, ax0 = c.figure(width=10.5, height=6.0)
    ax0.remove()
    ax = fig.add_axes([0.30, 0.14, 0.66, 0.69])
    y = np.arange(len(wl))
    ridge_hi = hi
    colors = [SEQ_BLUE[5] if v < lo else (SEQ_BLUE[2] if v <= hi else NV)
              for v in wl.arithmetic_intensity_flops_per_byte]
    ax.set_axisbelow(True)
    ax.barh(y, wl.arithmetic_intensity_flops_per_byte - 0.5, color=colors, height=0.6, left=0.5)
    for yi, v in zip(y, wl.arithmetic_intensity_flops_per_byte):
        ax.text(v * 1.12, yi, f"{v:,.0f}", va="center", fontsize=9, color=INK["text"])
    ax.set_yticks(y)
    ax.set_yticklabels(wl.workload, fontsize=9.2)
    ax.set_xscale("log")
    ax.set_xlim(0.5, 20000)
    ax.axvspan(lo, hi, color=NV, alpha=0.13, zorder=0)
    ax.axvspan(lo8, hi8, color=NV_DARK, alpha=0.08, zorder=0, hatch="//")
    ax.text((lo * hi) ** 0.5, len(wl) - 0.35, f"BF16 ridge\n{lo:.0f}-{hi:.0f}", ha="center", va="bottom",
            fontsize=8.5, color=NV_DARK, fontweight="bold")
    ax.text((lo8 * hi8) ** 0.5, len(wl) - 0.35, f"FP8 ridge\n{lo8:.0f}-{hi8:.0f}", ha="center", va="bottom",
            fontsize=8.5, color=NV_DARK)
    ax.set_ylim(-0.6, len(wl) + 0.6)
    ax.grid(True, axis="x", which="major")
    ax.grid(False, axis="y")
    handles = [mpatches.Patch(color=SEQ_BLUE[5], label="below every BF16 ridge: memory-bound"),
               mpatches.Patch(color=SEQ_BLUE[2], label="inside the ridge band: depends on the GPU"),
               mpatches.Patch(color=NV, label="above every BF16 ridge: compute-bound")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _ = ridge_hi
    _plain_log(ax, "x")
    _log_badge(fig)
    c.save(fig, ax, xlabel="Arithmetic intensity, FLOPs per byte of memory traffic (log scale)", legend=False)


@register
def rack_power_by_system():
    df = load("system_specs.csv")
    picks = [("DGX A100", "DGX A100"), ("DGX H100", "DGX H100"), ("DGX B200", "DGX B200"),
             ("GB200 NVL72", "GB200 NVL72"), ("GB300 NVL72", "GB300 NVL72"), ("Vera Rubin NVL72", "Vera Rubin NVL72"),
             ("Rubin Ultra NVL144 Kyber", "Rubin Ultra NVL144 Kyber")]
    rows = []
    for pat, label in picks:
        hit = df[(df.vendor == "NVIDIA") & df.system.astype(str).str.startswith(pat) & df.power_kw.notna()]
        if not hit.empty:
            r = hit.iloc[0]
            rows.append(dict(label=label, year=int(r.year), kw=float(r.power_kw), n=int(r.accelerators_per_system),
                             status=r.status, conf=r.confidence, src=r.source_id))
    d = pd.DataFrame(rows)
    d["kw_per_gpu"] = d.kw / d.n
    first_rack = d[d.n >= 72].iloc[0]
    last = d.iloc[-1]
    h100 = d[d.label == "DGX H100"].iloc[0]
    c = Chart(
        id="P3-rack-power-by-system",
        title=f"One NVIDIA scale-up domain draws ~{last.kw:,.0f} kW by {last.year}, vs {h100.kw:g} kW for an 8-GPU DGX H100",
        subtitle="kW per system (left) and per GPU package incl. CPUs and switches (right); hatched = not yet shipping",
        alt=(f"Two bar panels from the shared system specs data. Power per system: DGX A100 about 6.5 kW, DGX H100 {h100.kw:g} kW "
             f"and DGX B200 about 14.3 kW (8 GPUs each); GB200 NVL72 about {first_rack.kw:,.0f} kW, GB300 NVL72 about 132 kW, "
             f"Vera Rubin NVL72 about 230 kW (reported Max-P) and the Rubin Ultra Kyber rack about {last.kw:,.0f} kW "
             f"(144 packages, roadmap). Per GPU package, power rises from about 0.8 kW (DGX A100) and 1.3 kW (DGX H100) to "
             f"about 3.2 kW (Vera Rubin) and {last.kw_per_gpu:.1f} kW (Kyber)."),
        data=["system_specs.csv"], chapters=["P3", "08", "02"],
        source="NVIDIA datasheets, SemiAnalysis and press reports via system_specs.csv", source_ids=sources_of(
            df[df.system.isin([r for r in df.system if any(str(r).startswith(p) for p, _ in picks)])]),
    )
    fig, axes = c.figure_grid(1, 2, width=10.5, height=5.9, gridspec_kw={"width_ratios": [1.35, 1]})
    colors = [GEN_PAST if n == 8 else NV for n in d.n]
    future = [s_ in ("announced", "roadmap") for s_ in d.status]
    short = {"DGX A100": "DGX\nA100", "DGX H100": "DGX\nH100", "DGX B200": "DGX\nB200", "GB200 NVL72": "GB200\nNVL72",
             "GB300 NVL72": "GB300\nNVL72", "Vera Rubin NVL72": "VR\nNVL72", "Rubin Ultra NVL144 Kyber": "Kyber\nNVL144"}
    for ax, col, fmt, ttl in [(axes[0], "kw", "{:g}", "kW per system (log scale)"),
                              (axes[1], "kw_per_gpu", "{:.1f}", "kW per GPU package")]:
        bars = ax.bar(range(len(d)), d[col], color=colors, width=0.66)
        for bar, f in zip(bars, future):
            if f:
                bar.set_hatch("///")
                bar.set_alpha(0.8)
        for i, v in enumerate(d[col]):
            ax.text(i, v * (1.08 if col == "kw" else 1.0) + (0 if col == "kw" else 0.06), fmt.format(v),
                    ha="center", va="bottom", fontsize=8.6, color=INK["text"])
        ax.set_xticks(range(len(d)))
        ax.set_xticklabels([f"{short.get(lab, lab)}\n({y})" for lab, y in zip(d.label, d.year)], fontsize=8.2)
        ax.set_title(ttl, fontsize=10.5, color=INK["title"], loc="left")
        ax.set_axisbelow(True)
        ax.tick_params(length=0)
    axes[0].set_yscale("log")
    axes[0].set_ylim(3, 1500)
    axes[0].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    axes[0].yaxis.set_minor_formatter(NullFormatter())
    axes[1].set_ylim(0, max(d.kw_per_gpu) * 1.25)
    axes[0].set_ylabel("kW")
    handles = [mpatches.Patch(color=GEN_PAST, label="8-GPU server"), mpatches.Patch(color=NV, label="rack-scale NVLink domain"),
               mpatches.Patch(facecolor=NV, hatch="///", edgecolor="white", label="announced / roadmap")]
    axes[1].legend(handles=handles, loc="upper left", fontsize=8.4)
    _log_badge(fig)
    c.save(fig, list(axes), legend=False, top=0.80, bottom=0.17)


@register
def datacenter_power_demand_forecast():
    df = load("P3_power_demand.csv")
    c = Chart(
        id="P3-datacenter-power-demand-forecast",
        title="Datacenter electricity could double globally by 2030 and up to triple in the US by 2028",
        subtitle="Annual datacenter electricity use, TWh; solid = estimate of actual, hatched = forecast range (low to high)",
        alt=("Two bar panels. Global (IEA): about 415 TWh in 2024, about 1.5% of world electricity, rising to about 945 TWh "
             "by 2030 in the base case. United States: 76 TWh in 2018 and 176 TWh in 2023 (4.4% of US electricity, LBNL), "
             "with LBNL projecting 325 to 580 TWh by 2028 (6.7% to 12%) and EPRI 196 to 404 TWh by 2030 (4.6% to 9.1%)."),
        data=["P3_power_demand.csv"], chapters=["P3", "08", "18"],
        source="IEA Energy and AI (2025); LBNL (2024); EPRI (2024)", source_ids=sources_of(df),
    )
    fig, axes = c.figure_grid(1, 2, width=10.5, height=5.9, gridspec_kw={"width_ratios": [1, 2.1]})
    # global
    g = df[df.scope == "Global"].sort_values("year")
    ax = axes[0]
    for i, (_, r) in enumerate(g.iterrows()):
        fc = INK["muted"] if r.value_type != "forecast" else SEQ_BLUE[4]
        bar = ax.bar(i, r.twh, color=fc, width=0.6, hatch="///" if r.value_type == "forecast" else None)
        ax.text(i, r.twh + 15, f"{r.twh:,.0f} TWh\n({r.share_of_electricity_pct:g}%)", ha="center", va="bottom", fontsize=9)
        _ = bar
    ax.set_xticks(range(len(g)))
    ax.set_xticklabels([f"{y}\n{'IEA base' if t == 'forecast' else 'IEA est.'}" for y, t in zip(g.year, g.value_type)])
    ax.set_ylim(0, 1150)
    ax.set_title("Global (IEA)", fontsize=11, color=INK["title"], loc="left")
    ax.set_ylabel("TWh per year")
    # US
    u = df[df.scope == "United States"]
    ax = axes[1]
    pos = 0
    labels = []
    for (org, year), grp in u.groupby(["source_org", "year"], sort=False):
        grp = grp.sort_values("twh")
        if len(grp) == 1:
            r = grp.iloc[0]
            ax.bar(pos, r.twh, color=INK["muted"], width=0.6)
            ax.text(pos, r.twh + 12, f"{r.twh:,.0f}\n({r.share_of_electricity_pct:g}%)", ha="center", fontsize=9)
        else:
            lo_r, hi_r = grp.iloc[0], grp.iloc[-1]
            ax.bar(pos, hi_r.twh - lo_r.twh, bottom=lo_r.twh, color=SEQ_BLUE[4], width=0.6, hatch="///")
            ax.bar(pos, lo_r.twh, color=SEQ_BLUE[0], width=0.6)
            ax.text(pos, hi_r.twh + 12, f"{lo_r.twh:,.0f}-{hi_r.twh:,.0f}\n({lo_r.share_of_electricity_pct:g}-"
                    f"{hi_r.share_of_electricity_pct:g}%)", ha="center", fontsize=9)
        labels.append(f"{year}\n{org}{' range' if len(grp) > 1 else ' est.'}")
        pos += 1
    ax.set_xticks(range(pos))
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 690)
    ax.set_title("United States (LBNL, EPRI); % = share of national electricity", fontsize=11, color=INK["title"], loc="left")
    for a in axes:
        a.tick_params(length=0)
        a.set_axisbelow(True)
    c.save(fig, list(axes), top=0.80, bottom=0.15)


@register
def bottleneck_by_workload():
    df = load("P3_bottleneck_matrix.csv")
    rows = list(dict.fromkeys(df.workload))
    cols = list(dict.fromkeys(df.bottleneck))
    grid = df.pivot(index="workload", columns="bottleneck", values="severity_1_3").loc[rows, cols]
    labels = df.pivot(index="workload", columns="bottleneck", values="label").loc[rows, cols]
    c = Chart(
        id="P3-bottleneck-by-workload",
        title="Compute binds training and prefill; memory and interconnect bind decode and MoE",
        subtitle="Which bottleneck binds, by AI workload (repo analysis; Binding = sets the speed limit, Significant, Minor)",
        alt=("Heatmap of seven AI workloads against six bottlenecks. Dense pre-training: compute and power binding. "
             "MoE pre-training: scale-up and scale-out interconnect and power binding. Prefill: compute binding. "
             "Small-batch decode: memory bandwidth binding. Large-batch decode: memory capacity binding. Long-context reasoning: "
             "memory bandwidth, memory capacity and scale-up interconnect binding. MoE serving: memory bandwidth and scale-up binding."),
        data=["P3_bottleneck_matrix.csv"], chapters=["P3", "02", "03", "05", "06", "08", "11"],
        source="repo analysis drawing on Llama 3, DeepSeek-V3, Pope et al., IEA", source_ids=sources_of(df),
        kind="data",
    )
    fig, ax0 = c.figure(width=10.5, height=6.0)
    ax0.remove()
    ax = fig.add_axes([0.21, 0.08, 0.77, 0.66])
    cmap = {1: SEQ_BLUE[0], 2: SEQ_BLUE[2], 3: SEQ_BLUE[6]}
    for i, w in enumerate(rows):
        for j, b in enumerate(cols):
            v = int(grid.loc[w, b])
            ax.add_patch(mpatches.Rectangle((j, i), 0.96, 0.92, color=cmap[v]))
            ax.text(j + 0.48, i + 0.46, labels.loc[w, b], ha="center", va="center", fontsize=9.2,
                    color="white" if v == 3 else INK["title"], fontweight="bold" if v == 3 else "normal")
    ax.set_xlim(0, len(cols))
    ax.set_ylim(len(rows), 0)
    ax.set_xticks([j + 0.48 for j in range(len(cols))])
    ax.set_xticklabels([c_.replace(" interconnect", "\ninterconnect").replace(" network", "\nnetwork")
                        .replace("Memory ", "Memory\n") for c_ in cols], fontsize=9.3)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.46 for i in range(len(rows))])
    ax.set_yticklabels(rows, fontsize=9.3)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    c.save(fig, ax, legend=False, top=0.8)
