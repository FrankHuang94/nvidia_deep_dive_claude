"""Layer 02 (GPU silicon) CORE charts: mechanism charts for SMs, memory hierarchy, number formats,
multi-die economics and GPU vs CPU vs ASIC. Owner: Layer 02 CORE agent.

Data: data/l02_gpu_microarchitecture.csv, data/l02_memory_hierarchy.csv, data/l02_compute_units.csv,
data/l02_number_formats.csv (new, this layer) plus the shared data/gpu_product_specs.csv,
data/P2_model_and_gpu_inputs.csv (Llama 3.1 70B config + serving-model efficiencies) and
data/P5_wafer_economics.csv (wafer price, defect density, reticle limit). All compute is dense.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, entity_color, load, register, sources_of)

CH = ["02"]
UARCH = "l02_gpu_microarchitecture.csv"
MEMH = "l02_memory_hierarchy.csv"
UNITS = "l02_compute_units.csv"
FORMATS = "l02_number_formats.csv"
GPU = "gpu_product_specs.csv"
P2 = "P2_model_and_gpu_inputs.csv"
P5 = "P5_wafer_economics.csv"
REPO_MODEL = "S2021"
FORMAT_GREENS = {"TF32": "#94C150", "16-bit": "#5F9E00", "FP8": "#447300", "FP6": "#365C00", "FP4": "#2A4A00"}


def _log_badge(fig) -> None:
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


def _plain_log(axis) -> None:
    def f(v, _pos):
        if v <= 0:
            return ""
        if v >= 1:
            return f"{v:,.0f}"
        return f"{v:g}"
    axis.set_major_locator(LogLocator(base=10))
    axis.set_major_formatter(FuncFormatter(f))
    axis.set_minor_formatter(NullFormatter())


def _ids(*dfs) -> list[str]:
    out: list[str] = []
    for d in dfs:
        for s in sources_of(d):
            if s not in out:
                out.append(s)
    return out


def _gpu_row(df: pd.DataFrame, product: str) -> pd.Series:
    return df.loc[df["product"] == product].iloc[0]


# --------------------------------------------------------------------------------------
@register
def flops_per_clock_cpu_gpu_asic():
    df = load(UNITS)
    h100 = df.loc[df.unit.str.startswith("NVIDIA H100 SXM")].flops_per_clock.item()
    core = df.loc[df.unit == "Intel Xeon core (AVX-512 only)"].flops_per_clock.item()
    xeon = df.loc[df.unit.str.startswith("Intel Xeon 6980P")].flops_per_clock.item()
    sm = df.loc[df.unit.str.startswith("NVIDIA H100 SM")].flops_per_clock.item()
    mxu = df.loc[df.unit.str.startswith("Google Ironwood MXU")].flops_per_clock.item()
    c = Chart(
        id="02-flops-per-clock-cpu-gpu-asic",
        title=f"One H100 does ~{h100/1000:,.0f}K 16-bit FLOPs per clock, ~{h100/xeon:.0f}× a 128-core AMX Xeon",
        subtitle="Peak dense matrix FLOPs per clock cycle (BF16/FP16) by compute unit and by whole chip; vendor figures and repo arithmetic",
        alt=(f"Log-scale horizontal bar chart of peak 16-bit matrix FLOPs per clock. One CPU core without AMX does {core:.0f}, "
             f"with AMX 1,024; an NVIDIA V100 SM 1,024, A100 SM 2,048 and H100 SM {sm:,.0f}; a Google TPU v4 128x128 "
             f"systolic array 32,768 and an Ironwood 256x256 array {mxu:,.0f}. Whole chips: a 128-core Xeon with AMX "
             f"about {xeon:,.0f}, a TPU v4 chip 262,144 and an H100 {h100:,.0f}, about {h100/xeon:.0f} times the Xeon. "
             f"GPUs win by replicating many mid-sized matrix engines, ASICs by building a few very large ones."),
        data=[UNITS], chapters=CH + ["15"],
        source="NVIDIA, Intel, Google papers", source_ids=sources_of(df), note="Hatched = Est.",
    )
    fig, ax = c.figure(width=10.5, height=6.4)
    df = df.copy()
    df["grp"] = np.where(df.scope == "whole chip", 1, 0)
    df = df.sort_values(["grp", "flops_per_clock"], ascending=[True, True]).reset_index(drop=True)
    ys, y = [], 0.0
    prev = None
    for g in df.grp:
        if prev is not None and g != prev:
            y += 0.9
        ys.append(y)
        y += 1
        prev = g
    colors = {"CPU": entity_color("Intel"), "GPU": NV, "ASIC": entity_color("Google")}
    bars = ax.barh(ys, df.flops_per_clock, color=[colors[k] for k in df.category], height=0.46, zorder=2)
    for b, conf in zip(bars, df.confidence):
        if conf == "estimate":
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yy, v in zip(ys, df.flops_per_clock):
        ax.annotate(f"{v:,.0f}", (v, yy), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.8,
                    color=INK["title"])
    for yy, name in zip(ys, df.unit):
        ax.text(34, yy + 0.27, name, ha="left", va="bottom", fontsize=8.6, color=INK["title"])
    ax.set_yticks([])
    ax.set_ylim(-0.6, ys[-1] + 0.9)
    ax.set_xscale("log")
    ax.set_xlim(30, 6e6)
    _plain_log(ax.xaxis)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    split = (ys[int((df.grp == 0).sum()) - 1] + ys[int((df.grp == 0).sum())]) / 2
    ax.axhline(split, color=INK["base"], lw=1, ls="--")
    ax.text(5.5e6, split - 0.45, "one core / SM / matrix array", ha="right", va="center", fontsize=8.5,
            color=INK["muted"], style="italic")
    ax.text(5.5e6, split + 0.35, "whole chip", ha="right", va="center", fontsize=8.5, color=INK["muted"],
            style="italic")
    handles = [Patch(color=colors[k], label=k) for k in ("CPU", "GPU", "ASIC")]
    ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(1.0, 0.12), fontsize=9)
    _log_badge(fig)
    c.save(fig, ax, xlabel="Peak dense 16-bit matrix FLOPs per clock cycle (log scale)", legend=False,
           bottom=0.12, top=0.86)


# --------------------------------------------------------------------------------------
@register
def memory_hierarchy_capacity_vs_bandwidth():
    df = load(MEMH)
    h = df[df["product"] == "H100 SXM"].set_index("level")
    reg_bw, hbm_bw = h.loc["Registers", "bandwidth_tbs"], h.loc["HBM3", "bandwidth_tbs"]
    reg_cap, hbm_cap = h.loc["Registers", "capacity_mb"], h.loc["HBM3", "capacity_mb"]
    b = df[df["product"] == "B200"].set_index("level")
    c = Chart(
        id="02-memory-hierarchy-capacity-vs-bandwidth",
        title=f"H100 registers are ~{reg_bw/hbm_bw:.0f}× faster than its HBM but hold ~{round(hbm_cap/reg_cap, -2):,.0f}× less data",
        subtitle="Total capacity vs aggregate bandwidth per GPU at each memory level, H100 SXM, B200 and Rubin (both axes log scale)",
        alt=(f"Log-log chart of capacity against bandwidth for each GPU memory level. H100: registers about {reg_cap:.0f} MB "
             f"at an estimated {reg_bw:.0f} TB/s, L1/shared memory {h.loc['L1 / shared memory','capacity_mb']:.0f} MB at "
             f"about {h.loc['L1 / shared memory','bandwidth_tbs']:.0f} TB/s, L2 50 MB at over 5.5 TB/s, HBM3 80 GB at "
             f"3.35 TB/s and the 8-GPU NVLink domain 640 GB at 0.9 TB/s per GPU. B200: L2 126 MB at about 21 TB/s, HBM3E "
             f"180 GB at 8 TB/s and the NVL72 domain 13.4 TB at 1.8 TB/s. Rubin: HBM4 288 GB at 19.2 TB/s and the NVL72 "
             f"domain 20.7 TB at 3.0 TB/s. Each step outward gives roughly 100 to 1,000 times more capacity for less bandwidth."),
        data=[MEMH], chapters=CH + ["03", "P3"],
        source="NVIDIA, Chips and Cheese, repo Est.", source_ids=sources_of(df), note="Hollow = Est.",
    )
    fig, ax = c.figure(width=10.5, height=6.2)
    styles = {"H100 SXM": ("#8DB85A", "o"), "B200": (NV, "s"), "Rubin": (NV_DARK, "D")}
    for prod, (col, mk) in styles.items():
        d = df[df["product"] == prod].sort_values("level_order")
        ax.plot(d.capacity_mb, d.bandwidth_tbs, color=col, lw=2, zorder=2, label=prod)
        for _, r in d.iterrows():
            est = r.confidence == "estimate"
            ax.plot(r.capacity_mb, r.bandwidth_tbs, marker=mk, ms=9, color=col, mfc="white" if est else col,
                    mew=2, zorder=3, ls="none")
    # level labels (placed near the H100 / B200 points)
    lab = [("Registers", "H100 SXM", (-10, -3)), ("L1 / shared memory", "H100 SXM", (-10, -3)),
           ("L2 cache", "H100 SXM", (8, -10)), ("HBM3", "H100 SXM", (-10, -16)),
           ("NVLink domain (HGX 8-GPU)", "H100 SXM", (-30, -16)), ("L2 cache", "B200", (8, 4)),
           ("HBM3E", "B200", (8, 6)), ("NVLink domain (NVL72)", "B200", (-40, 10)),
           ("HBM4", "Rubin", (8, 6)), ("NVLink domain (NVL72)", "Rubin", (8, 6))]
    names = {"Registers": "registers", "L1 / shared memory": "L1 / shared mem", "L2 cache": "L2",
             "HBM3": "HBM3", "HBM3E": "HBM3E", "HBM4": "HBM4", "NVLink domain (HGX 8-GPU)": "NVLink domain (8 GPUs)",
             "NVLink domain (NVL72)": "NVL72 domain"}
    for level, prod, off in lab:
        r = df[(df["product"] == prod) & (df.level == level)].iloc[0]
        left = level in ("Registers", "L1 / shared memory")
        ax.annotate(names[level], (r.capacity_mb, r.bandwidth_tbs), xytext=off, textcoords="offset points",
                    fontsize=8.6, color=INK["text"], ha="right" if left else "left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 1e8)
    ax.set_ylim(0.3, 1500)
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(FuncFormatter(
        lambda v, _p: {1: "1 MB", 10: "10 MB", 100: "100 MB", 1e3: "1 GB", 1e4: "10 GB", 1e5: "100 GB", 1e6: "1 TB",
                       1e7: "10 TB", 1e8: "100 TB"}.get(v, "")))
    ax.xaxis.set_minor_formatter(NullFormatter())
    _plain_log(ax.yaxis)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.legend(loc="upper right", fontsize=9)
    ax.text(1.3, 0.42, f"B200 L2: {b.loc['L2 cache','capacity_mb']:.0f} MB at ~{b.loc['L2 cache','bandwidth_tbs']:.0f} TB/s "
            "(measured); Rubin on-chip sizes not disclosed", fontsize=8.4, color=INK["muted"])
    _log_badge(fig)
    c.save(fig, ax, xlabel="Total capacity per GPU (log scale)", ylabel="Aggregate bandwidth, TB/s (log scale)",
           legend=False)


# --------------------------------------------------------------------------------------
@register
def sms_and_throughput_per_sm():
    ua = load(UARCH)
    g = load(GPU)
    pairs = [("V100", "V100 SXM2 32GB", "V100 SXM2 32GB"), ("A100", "A100 SXM 80GB", "A100 SXM 80GB"),
             ("H100", "H100 SXM", "H100 SXM"), ("B200", "B200", "B200 (HGX)"),
             ("B300/GB300", "GB300 (Blackwell Ultra)", "GB300 (per GPU)"), ("Rubin", "Rubin (VR200)", "Rubin (VR200, per GPU)")]
    rows = []
    for short, up, gp in pairs:
        u = ua.loc[ua["product"] == up].iloc[0]
        s = _gpu_row(g, gp)
        sms = float(u.sms)
        rows.append(dict(short=short, year=int(u.year), sms=sms,
                         b16=s.bf16_tflops_dense / sms,
                         fp8=(s.fp8_tflops_dense / sms) if pd.notna(s.fp8_tflops_dense) else np.nan,
                         fp4=(s.fp4_tflops_dense / sms) if pd.notna(s.fp4_tflops_dense) else np.nan))
    d = pd.DataFrame(rows)
    h, r = d.set_index("short").loc["H100"], d.set_index("short").loc["Rubin"]
    used_g = g[g["product"].isin([p[2] for p in pairs])]
    c = Chart(
        id="02-sms-and-throughput-per-sm",
        title=f"Since H100, 16-bit FLOPS per SM rose {r.b16/h.b16:.1f}× but low-precision FLOPS per SM {r.fp4/h.fp8:.0f}×",
        subtitle="Left: streaming multiprocessors (SMs) per GPU package. Right: dense peak TFLOPS per SM by format (log scale)",
        alt=(f"Two-panel chart. SMs per GPU: V100 80, A100 108, H100 132, B200 148, Blackwell Ultra 160 and Rubin 224. "
             f"Dense TFLOPS per SM: 16-bit rose from {d.b16.iloc[0]:.1f} on V100 to {h.b16:.1f} on H100, then only to "
             f"{r.b16:.1f} on Rubin; FP8 per SM went from {h.fp8:.0f} on H100 to {r.fp8:.0f} on Rubin and FP4 per SM "
             f"from {d.set_index('short').loc['B200','fp4']:.0f} on B200 to {r.fp4:.0f} on Rubin, so most new tensor-core "
             f"silicon serves narrow formats."),
        data=[UARCH, GPU], chapters=CH + ["17"],
        source="NVIDIA whitepapers and blogs, Chips and Cheese; repo arithmetic",
        source_ids=_ids(ua, used_g),
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=11.5, height=5.8, gridspec_kw=dict(width_ratios=[1, 1.6]))
    x = np.arange(len(d))
    cols = [NV if s == "Rubin" else GEN_PAST for s in d.short]
    bars = a1.bar(x, d.sms, color=cols, width=0.65, zorder=2)
    for b_, v in zip(bars, d.sms):
        a1.annotate(f"{v:.0f}", (b_.get_x() + b_.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=9, color=INK["title"])
    a1.set_xticks(x, [f"{s}\n{y}" for s, y in zip(d.short, d.year)], fontsize=8.6)
    a1.set_ylabel("SMs per GPU package")
    a1.set_ylim(0, 250)
    a1.set_title("SMs per GPU", fontsize=10.5, color=INK["text"], loc="left")
    w = 0.26
    for k, (col, lab) in enumerate([("b16", "16-bit (FP16/BF16)"), ("fp8", "FP8"), ("fp4", "FP4")]):
        color = FORMAT_GREENS["16-bit" if col == "b16" else lab]
        vals = d[col].to_numpy(dtype=float)
        a2.bar(x + (k - 1) * w, np.nan_to_num(vals, nan=0), width=w, color=color, label=lab, zorder=2)
        for i, v in enumerate(vals):
            if not np.isnan(v) and (col != "fp8" or d.short.iloc[i] in ("H100", "Rubin")):
                a2.annotate(f"{v:.1f}" if v < 10 else f"{v:.0f}", (x[i] + (k - 1) * w, v), xytext=(0, 2),
                            textcoords="offset points", ha="center", fontsize=7.8, color=INK["title"])
    a2.set_yscale("log")
    a2.set_ylim(0.8, 400)
    _plain_log(a2.yaxis)
    a2.set_xticks(x, [f"{s}\n{y}" for s, y in zip(d.short, d.year)], fontsize=8.6)
    a2.set_ylabel("Dense TFLOPS per SM (log scale)")
    a2.set_title("Dense TFLOPS per SM", fontsize=10.5, color=INK["text"], loc="left")
    a2.legend(loc="upper left", fontsize=8.5)
    a2.text(0.5, 40, "no FP8/FP4\nbefore Hopper", fontsize=8, color=INK["muted"], ha="center")
    _log_badge(fig)
    fig.subplots_adjust(wspace=0.28)
    c.save(fig, [a1, a2], legend=False, bottom=0.16)
    fig.subplots_adjust(wspace=0.28)


# --------------------------------------------------------------------------------------
@register
def throughput_multiple_vs_bf16():
    g = load(GPU)
    gens = [("A100", "A100 SXM 80GB"), ("H100", "H100 SXM"), ("B200", "B200 (HGX)"),
            ("GB300", "GB300 (per GPU)"), ("Rubin", "Rubin (VR200, per GPU)")]
    fmts = [("TF32", "tf32_tflops_dense"), ("FP8", "fp8_tflops_dense"), ("FP6", "fp6_tflops_dense"),
            ("FP4", "fp4_tflops_dense")]
    rows = []
    for short, prod in gens:
        s = _gpu_row(g, prod)
        rows.append({"short": short, **{f: (s[col] / s.bf16_tflops_dense if pd.notna(s[col]) else np.nan)
                                         for f, col in fmts}})
    d = pd.DataFrame(rows).set_index("short")
    used = g[g["product"].isin([p for _, p in gens])]
    c = Chart(
        id="02-throughput-multiple-vs-bf16",
        title=(f"Rubin runs FP4 {d.loc['Rubin','FP4']:.2f}× and FP8 {d.loc['Rubin','FP8']:.1f}× faster than BF16; "
               f"on H100 FP8 was {d.loc['H100','FP8']:.0f}×"),
        subtitle="Dense peak throughput in each format divided by the same GPU's dense BF16 throughput (BF16 = 1.0)",
        alt=(f"Grouped bar chart of throughput relative to BF16. TF32 runs at 0.5x on A100, H100, B200 and GB300. FP8 is 2x "
             f"BF16 on H100, B200 and GB300 but {d.loc['Rubin','FP8']:.1f}x on Rubin. FP6 matches FP8. FP4 is 4x on B200, "
             f"6x on Blackwell Ultra (GB300) and {d.loc['Rubin','FP4']:.2f}x on Rubin. A100 has no FP8 or FP4. Each new "
             f"generation spends more tensor-core silicon on narrow formats than on BF16."),
        data=[GPU], chapters=CH + ["11", "14"],
        source="NVIDIA datasheets (dense = sparse figures halved)", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(d))
    w = 0.2
    for k, (f, _) in enumerate(fmts):
        vals = d[f].to_numpy(dtype=float)
        pos = x + (k - 1.5) * w
        ax.bar(pos, np.nan_to_num(vals, nan=0), width=w, color=FORMAT_GREENS[f], label=f, zorder=2)
        for p, v in zip(pos, vals):
            if np.isnan(v):
                ax.text(p, 0.12, "n/a", ha="center", va="bottom", fontsize=7.5, color=INK["muted"], rotation=90)
            else:
                lab = f"{v:.2f}".rstrip("0").rstrip(".")
                if len(lab) > 3 and v < 5:
                    lab = f"{v:.1f}"
                ax.annotate(f"{lab}×", (p, v), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=8,
                            color=INK["title"])
    ax.axhline(1.0, color=INK["text"], lw=1.2, ls="--", zorder=3)
    ax.text(-0.45, 1.12, "BF16 = 1.0", fontsize=8.5, color=INK["text"], ha="left")
    ax.set_xticks(x, d.index)
    ax.set_ylim(0, 10)
    ax.legend(loc="upper left", ncol=4, fontsize=9)
    c.save(fig, ax, xlabel="GPU", ylabel="Throughput relative to BF16 (×)", legend=False)


# --------------------------------------------------------------------------------------
def _llama70b():
    p2 = load(P2)
    cfg = p2[(p2.record_type == "model_config") & (p2["item"] == "Llama 3.1 70B")].set_index("metric").value
    asm = p2[(p2.record_type == "model_assumption")].set_index("metric").value
    used = p2[((p2.record_type == "model_config") & (p2["item"] == "Llama 3.1 70B")) |
              (p2.metric.isin(["avg_context_tokens", "bandwidth_efficiency", "compute_efficiency", "memory_headroom"]))]
    return cfg, asm, used


@register
def decode_throughput_by_precision():
    cfg, asm, used_p2 = _llama70b()
    fm = load(FORMATS).set_index("format")
    g = load(GPU)
    batch = 64
    params = float(cfg["params_b"]) * 1e9
    layers, kvh, hd, heads = (float(cfg[k]) for k in ("layers", "kv_heads", "head_dim", "attention_heads"))
    ctx = float(asm["avg_context_tokens"])
    bw_eff, fl_eff, head = (float(asm[k]) for k in ("bandwidth_efficiency", "compute_efficiency", "memory_headroom"))
    kv_elems_per_token = 2 * layers * kvh * hd
    attn_flops_per_token = 4 * layers * ctx * heads * hd
    precisions = [("BF16", float(fm.loc["BF16", "effective_bits_per_value"]), 2.0, "bf16_tflops_dense"),
                  ("FP8", float(fm.loc["FP8 E4M3", "effective_bits_per_value"]), 1.0, "fp8_tflops_dense"),
                  ("NVFP4", float(fm.loc["NVFP4 (E2M1)", "effective_bits_per_value"]), 1.0, "fp4_tflops_dense")]
    gpus = [("H100", "H100 SXM"), ("B200", "B200 (HGX)"), ("Rubin", "Rubin (VR200, per GPU)")]
    res = {}
    for short, prod in gpus:
        s = _gpu_row(g, prod)
        for name, bits, kvb, col in precisions:
            peak = s[col]
            if pd.isna(peak):
                res[(short, name)] = (np.nan, np.nan)
                continue
            w_bytes = params * bits / 8
            kv_bytes = batch * ctx * kv_elems_per_token * kvb
            step_bytes = w_bytes + kv_bytes
            flops = batch * (2 * params + attn_flops_per_token)
            mem_tps = batch * s.memory_bandwidth_tbs * 1e12 * bw_eff / step_bytes
            cmp_tps = batch * peak * 1e12 * fl_eff / flops
            n_gpus = math.ceil(step_bytes / (s.memory_capacity_gb * 1e9 * head))
            res[(short, name)] = (min(mem_tps, cmp_tps), n_gpus)
    b_bf, b_fp4 = res[("B200", "BF16")][0], res[("B200", "NVFP4")][0]
    h_bf, r_fp4 = res[("H100", "BF16")][0], res[("Rubin", "NVFP4")][0]
    used_g = g[g["product"].isin([p for _, p in gpus])]
    used_f = load(FORMATS)
    used_f = used_f[used_f.format.isin(["BF16", "FP8 E4M3", "NVFP4 (E2M1)"])]
    c = Chart(
        id="02-decode-throughput-by-precision",
        title=f"Est.: NVFP4 lets a B200 serve ~{b_fp4/b_bf:.1f}× its BF16 tokens/s on a 70B model",
        subtitle=(f"Modelled decode tokens/s per GPU: Llama 3.1 70B, {batch} streams × {ctx:,.0f}-token context, "
                  f"{bw_eff:.0%} of peak HBM bandwidth"),
        alt=(f"Grouped bar chart of modelled decode throughput per GPU for Llama 3.1 70B with 64 concurrent users. "
             f"H100: about {res[('H100','BF16')][0]:,.0f} tokens/s at BF16 and {res[('H100','FP8')][0]:,.0f} at FP8 (no FP4). "
             f"B200: {b_bf:,.0f} at BF16, {res[('B200','FP8')][0]:,.0f} at FP8 and {b_fp4:,.0f} at NVFP4. Rubin: "
             f"{res[('Rubin','BF16')][0]:,.0f}, {res[('Rubin','FP8')][0]:,.0f} and {r_fp4:,.0f}. Every case is limited by "
             f"memory bandwidth, so fewer bytes per weight translate almost directly into more tokens per GPU and per "
             f"dollar; Rubin at NVFP4 serves about {r_fp4/h_bf:.0f} times H100 at BF16. Estimates from a roofline model."),
        data=[P2, GPU, FORMATS], chapters=CH + ["11", "14", "P2"],
        source="repo roofline model", source_ids=[REPO_MODEL] + _ids(used_p2, used_g, used_f), note="Est.",
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    x = np.arange(len(gpus))
    w = 0.26
    cols = {"BF16": FORMAT_GREENS["16-bit"], "FP8": FORMAT_GREENS["FP8"], "NVFP4": FORMAT_GREENS["FP4"]}
    for k, (name, *_rest) in enumerate(precisions):
        vals = [res[(s, name)][0] for s, _ in gpus]
        pos = x + (k - 1) * w
        bars = ax.bar(pos, np.nan_to_num(vals, nan=0), width=w, color=cols[name], label=name, zorder=2)
        for b_ in bars:
            b_.set_hatch("//")
        for p, v, (s, _) in zip(pos, vals, gpus):
            if np.isnan(v):
                ax.text(p, 300, "no FP4\non Hopper", ha="center", va="bottom", fontsize=7.6, color=INK["muted"])
                continue
            ax.annotate(f"{v:,.0f}", (p, v), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=8.4,
                        color=INK["title"])
            ax.text(p, 120, f"×{res[(s, name)][1]}", ha="center", va="bottom", fontsize=8, color="#FFFFFF",
                    fontweight="bold")
    ax.set_xticks(x, [s for s, _ in gpus])
    ax.set_ylim(0, max(v for v, _ in res.values() if not np.isnan(v)) * 1.15)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:,.0f}"))
    ax.legend(loc="upper left", fontsize=9)
    c.save(fig, ax, xlabel="GPU (×n inside bars = GPUs needed to hold weights + KV cache; FP8 KV cache for FP8/NVFP4)",
           ylabel="Decode tokens/s per GPU (Est.)", legend=False)


# --------------------------------------------------------------------------------------
@register
def multi_die_silicon_cost():
    p5 = load(P5)
    wafer = float(p5[(p5.record_type == "wafer_price") & (p5.source_id == "S35020")].value.iloc[0])
    d0 = float(p5[(p5.record_type == "model_param") & (p5["item"] == "defect_density_mid")].value.iloc[0])
    reticle = float(p5[(p5.record_type == "model_param") & (p5["item"] == "reticle_limit")].value.iloc[0])
    used = p5[((p5.record_type == "wafer_price") & (p5.source_id == "S35020")) |
              (p5["item"].isin(["defect_density_mid", "reticle_limit"]))]
    total = 1600.0

    def dpw(a):
        return math.pi * 150 ** 2 / a - math.pi * 300 / math.sqrt(2 * a)

    rows = []
    for n in (1, 2, 4, 8, 16):
        a = total / n
        gross = math.floor(dpw(a))
        y = math.exp(-a / 100 * d0)
        per_die = wafer / (gross * y)
        rows.append(dict(n=n, area=a, gross=gross, y=y, cost=n * per_die))
    d = pd.DataFrame(rows)
    c1, c2, c8 = d.cost.iloc[0], d.cost.iloc[1], d.cost.iloc[3]
    c = Chart(
        id="02-multi-die-silicon-cost",
        title=f"Est.: two dies instead of one cut silicon cost per GPU ~{1 - c2/c1:.0%}; eight chiplets ~{1 - c8/c1:.0%}",
        subtitle=(f"Good logic silicon for one GPU (1,600 mm²), ${wafer/1e3:.0f}K wafer, {d0:.1f} defects/cm², Poisson "
                  f"yield; excludes D2D area, packaging, assembly yield"),
        alt=(f"Bar chart of modelled silicon cost for 1,600 mm2 of GPU logic split into 1, 2, 4, 8 or 16 dies on a "
             f"${wafer:,.0f} wafer at {d0} defects per cm2. One 1,600 mm2 die (impossible: the reticle limit is {reticle:.0f} mm2) "
             f"would yield {d.y.iloc[0]:.0%} and cost about ${c1:,.0f}; two 800 mm2 dies like Blackwell or Rubin yield "
             f"{d.y.iloc[1]:.0%} each and cost about ${c2:,.0f}; four 400 mm2 dies about ${d.cost.iloc[2]:,.0f}; eight "
             f"200 mm2 chiplets about ${c8:,.0f}; sixteen 100 mm2 about ${d.cost.iloc[4]:,.0f}. Savings flatten while "
             f"packaging cost, die-to-die power and assembly risk rise with every extra die."),
        data=[P5], chapters=CH + ["03", "P5"],
        source="repo yield model, Epoch AI", source_ids=[REPO_MODEL] + sources_of(used), note="Est.",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(d))
    cols = [INK["base"], NV, SEQ_BLUE[3], SEQ_BLUE[5], SEQ_BLUE[2]]
    bars = ax.bar(x, d.cost, color=cols, width=0.62, zorder=2)
    bars[0].set_hatch("///")
    for i, r in d.iterrows():
        ax.annotate(f"${r.cost:,.0f}", (i, r.cost), xytext=(0, 3), textcoords="offset points", ha="center",
                    fontsize=10, fontweight="bold", color=INK["title"])
    labels = [f"{int(r.n)} × {r.area:,.0f} mm²\nyield {r.y:.0%} each" for _, r in d.iterrows()]
    labels[0] += "\n(over reticle:\nnot buildable)"
    labels[1] += "\nBlackwell / Rubin"
    labels[3] += "\nchiplet style\n(AMD MI300/MI355-like)"
    ax.set_xticks(x, labels, fontsize=8.6)
    ax.set_ylim(0, c1 * 1.15)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"${v:,.0f}"))
    c.save(fig, ax, xlabel="How 1,600 mm² of logic is split (dies × area per die)",
           ylabel="Silicon cost of good dies per GPU (US$, Est.)", bottom=0.27)
