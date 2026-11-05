"""Primer P1 (How AI training works) charts. Data: data/P1_training_compute.csv,
data/P1_memory_per_parameter.csv, data/P2_model_and_gpu_inputs.csv (GPU spec rows)."""
import math

import numpy as np
import pandas as pd

from style import (Chart, INK, NV, NV_DARK, GEN_PAST, SEQ_BLUE, load, register, sources_of,
                   end_label)

CH = ["P1", "14", "02", "08"]
RENTAL_USD_PER_GPU_HOUR = 2.0   # DeepSeek-V3 report's assumed H800 rental price (S34007)
MFU = 0.40                      # Llama 3 405B measured 38-43% BF16 MFU (S34006)
RUN_DAYS = 90


def _year(s: str) -> float:
    s = str(s)
    y, m = (s.split("-") + ["6"])[:2]
    return int(y) + (int(m) - 0.5) / 12


def gpu_specs() -> pd.DataFrame:
    df = load("P2_model_and_gpu_inputs.csv")
    g = df[df.record_type == "gpu_spec"]
    wide = g.pivot_table(index="item", columns="metric", values="value", aggfunc="first")
    return wide, g


SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def pow10_ticks(ax, axis: str = "y") -> None:
    """Log-axis tick labels as 10²⁵ (mathtext is disabled repo-wide, so set them explicitly)."""
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

    def f(v, _pos):
        if v <= 0:
            return ""
        e = math.log10(v)
        if abs(e - round(e)) > 1e-6:
            return ""
        return "10" + str(int(round(e))).translate(SUP)
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=10))
    a.set_major_formatter(FuncFormatter(f))
    a.set_minor_formatter(NullFormatter())


def freeze_scale(ax) -> None:
    """style.Chart.save() re-applies set_[xy]scale('log') (which resets tick formatters) when
    logx/logy=True; the axes are already log here, so make those calls no-ops for this axes."""
    ax.set_yscale = lambda *a, **k: None
    ax.set_xscale = lambda *a, **k: None


def plain_log_ticks(ax, axis: str = "x", fmt: str = "{:,.0f}") -> None:
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=10))
    a.set_major_formatter(FuncFormatter(lambda v, _p: fmt.format(v) if v >= 1 else f"{v:g}"))
    a.set_minor_formatter(NullFormatter())


def row_labels(ax, labels, ys, dy: float = 0.28) -> None:
    """Category labels drawn above each horizontal bar, inside the plot area (no clipping)."""
    tr = ax.get_yaxis_transform()
    for lab, y in zip(labels, ys):
        ax.text(0.004, y + dy, lab, transform=tr, ha="left", va="bottom", fontsize=9.5,
                color=INK["title"], fontweight="bold")
    ax.set_yticks([])


def sig2(v: float) -> str:
    """Round to two significant figures for prose (12,353 -> 12,000)."""
    if v <= 0:
        return "0"
    d = int(math.floor(math.log10(v))) - 1
    return f"{round(v, -d):,.0f}"


def fmt_flop(x: float) -> str:
    e = int(math.floor(math.log10(x)))
    return f"{x / 10 ** e:.1f}e{e}"


@register
def frontier_training_compute_log():
    df = load("P1_training_compute.csv")
    d = df[df.flop_basis != "scenario"].copy()
    d["yr"] = d.release_date.map(_year)
    d = d.sort_values("yr")
    first = d[d.model == "GPT-3"].iloc[0]
    top = d.loc[d.training_flop.idxmax()]
    mult = top.training_flop / first.training_flop
    yrs = top.yr - first.yr
    # fit on the running frontier (max-so-far)
    d["runmax"] = d.training_flop.cummax()
    fr = d[d.training_flop >= d.runmax * 0.999]
    slope, icpt = np.polyfit(fr.yr, np.log10(fr.training_flop), 1)
    per_year = 10 ** slope
    c = Chart(
        id="P1-frontier-training-compute-log",
        title=f"Frontier training compute rose ~{round(mult, -2):,.0f}× in five years, roughly 4–5× per year",
        subtitle="Training compute of notable language models, FLOPs (log scale); hollow = Epoch AI estimate (often ±10× or more)",
        alt=(f"Log-scale scatter of training compute for notable AI models from GPT-3 (3.1e23 FLOPs, 2020) to "
             f"Grok 4 (about 5e26 FLOPs, Epoch AI estimate, 2025): roughly {round(mult, -2):,.0f} times more in five years, "
             f"a fitted frontier trend of about {per_year:.1f} times per year, consistent with Epoch AI's 4-5x per year. "
             "Llama 3.1 405B used 3.8e25 FLOPs; GPT-5 (about 5e25) used less than GPT-4.5 (about 3.8e26)."),
        data=["P1_training_compute.csv"], chapters=CH,
        source="Epoch AI; Meta, DeepSeek, OpenAI, DeepMind papers",
        source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    xs = np.linspace(first.yr - 0.2, 2027.1, 50)
    ax.plot(xs, 10 ** (icpt + slope * xs), ls="--", lw=1.4, color=INK["muted"], zorder=1)
    ax.annotate(f"Frontier fit ≈ {per_year:.1f}× / year\n(Epoch AI: 4–5× / year)", (2021.0, 10 ** (icpt + slope * 2021.0)),
                xytext=(2020.15, 2.5e25), fontsize=9, color=INK["text"],
                arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    for _, r in d.iterrows():
        est = r.flop_basis == "epoch_estimate"
        col = SEQ_BLUE[6] if r.flop_basis == "reported" else SEQ_BLUE[4]
        ax.scatter(r.yr, r.training_flop, s=70, zorder=3,
                   facecolor="white" if est else col, edgecolor=col, linewidth=2)
    offsets = {"GPT-3": (6, -12), "Chinchilla": (6, -4), "GPT-4": (-10, 9), "Gemini 1.0 Ultra": (-30, 10),
               "Llama 3.1 405B": (8, 3), "Llama 3.1 70B": (6, -3), "Llama 3.1 8B": (6, -3),
               "DeepSeek-V3": (7, -3), "Grok 3": (-48, 6), "GPT-4.5": (-8, 10), "Claude Opus 4": (6, -11),
               "Grok 4": (6, 4), "GPT-5": (6, -4)}
    for _, r in d.iterrows():
        dx, dy = offsets.get(r.model, (6, 0))
        ax.annotate(r.model, (r.yr, r.training_flop), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.5, color=INK["title"], va="center")
    sc = df[df.flop_basis == "scenario"].iloc[0]
    ax.scatter(_year(sc.release_date), sc.training_flop, s=80, marker="D", facecolor="white",
               edgecolor=INK["muted"], linewidth=1.6, hatch="///", zorder=3)
    ax.annotate("1e27 run (repo scenario)", (_year(sc.release_date), sc.training_flop), xytext=(-80, -16),
                textcoords="offset points", fontsize=8.5, color=INK["muted"], style="italic")
    ax.set_xlim(2019.9, 2027.4)
    ax.set_ylim(1e23, 5e27)
    ax.scatter([], [], s=60, facecolor=SEQ_BLUE[6], edgecolor=SEQ_BLUE[6], label="Reported by developer")
    ax.scatter([], [], s=60, facecolor=SEQ_BLUE[4], edgecolor=SEQ_BLUE[4], label="Derived: 6 × params × tokens")
    ax.scatter([], [], s=60, facecolor="white", edgecolor=SEQ_BLUE[4], linewidth=2, label="Epoch AI estimate")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_yscale("log")
    pow10_ticks(ax, "y")
    freeze_scale(ax)
    c.save(fig, ax, xlabel="Release date", ylabel="Training compute, FLOPs", logy=True, legend=False)


@register
def memory_per_parameter_training():
    df = load("P1_memory_per_parameter.csv")
    order = ["Inference FP4", "Inference FP8", "Inference BF16", "Training (mixed precision + Adam)"]
    comp_cols = {"weights": SEQ_BLUE[6], "gradients": SEQ_BLUE[4], "master weights": SEQ_BLUE[2],
                 "Adam momentum": "#C98500", "Adam variance": "#E3B04B"}
    tot = df.groupby("regime").bytes_per_param.sum()
    train = tot[order[-1]]
    ratio = train / tot["Inference BF16"]
    c = Chart(
        id="P1-memory-per-parameter-training",
        title=f"Training needs ~{train:.0f} bytes per parameter, {ratio:.0f}× BF16 inference, before activations",
        subtitle="Memory per model parameter by regime and component, bytes (mixed-precision training with the Adam optimizer)",
        alt=(f"Stacked horizontal bars of bytes per parameter: FP4 inference about 0.56, FP8 inference 1, BF16 inference 2, "
             f"and mixed-precision training with Adam {train:.0f} (2 weights + 2 gradients + 4 FP32 master weights + "
             f"4 momentum + 4 variance), {ratio:.0f} times BF16 inference. A 405B model therefore carries about 6.5 TB "
             "of training state, about 81 H100s' worth of memory, before activations."),
        data=["P1_memory_per_parameter.csv"], chapters=["P1", "P4", "03"],
        source="ZeRO paper (Microsoft) and NVIDIA NVFP4 documentation", source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    y = np.arange(len(order))
    for i, reg in enumerate(order):
        left = 0.0
        rows = df[df.regime == reg]
        for _, r in rows.iterrows():
            col = comp_cols.get(r.component, SEQ_BLUE[6])
            ax.barh(i, r.bytes_per_param, left=left, color=col, height=0.5, edgecolor="white", linewidth=1)
            if r.bytes_per_param >= 2 and reg.startswith("Training"):
                ax.text(left + r.bytes_per_param / 2, i, f"{r.component}\n{r.bytes_per_param:g} B", ha="center",
                        va="center", fontsize=8.2, color="white" if r.component in ("weights", "gradients") else INK["title"])
            left += r.bytes_per_param
        # regime label above each bar (keeps long labels inside the plot area)
        ax.text(0, i - 0.3, reg, ha="left", va="bottom", fontsize=9.5, color=INK["title"], fontweight="bold")
        if reg.startswith("Training"):
            ax.barh(i, 3.0, left=left, color="#E1E0D9", edgecolor=INK["muted"], hatch="///", height=0.5, linewidth=1)
            ax.text(left + 1.5, i, "activations\n(vary)", ha="center", va="center", fontsize=8, color=INK["title"],
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
            ax.text(left + 3.2, i, f"{left:g} B\n+ activations", va="center", fontsize=10, fontweight="bold",
                    color=INK["title"])
        else:
            ax.text(left + 0.2, i, f"{left:g} B" if left >= 1 else f"{left:.2f} B", va="center", fontsize=10,
                    fontweight="bold", color=INK["title"])
    ax.set_yticks([])
    ax.set_ylim(len(order) - 0.55, -0.85)
    ax.set_xlim(0, 22.5)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="Bytes per parameter", legend=False, bottom=0.15)


@register
def gpus_needed_by_model_size():
    df = load("P1_training_compute.csv")
    wide, graw = gpu_specs()
    picks = ["GPT-4", "Llama 3.1 405B", "Grok 4", "Hypothetical 1e27 FLOP run"]
    runs = df.set_index("model").loc[picks]
    gpus = ["H100 SXM", "B200", "Rubin"]
    secs = RUN_DAYS * 86400
    need = {g: [runs.training_flop[m] / (wide.loc[g, "bf16_tflops_dense"] * 1e12 * MFU * secs) for m in picks]
            for g in gpus}
    g4h, g4r = need["H100 SXM"][2], need["Rubin"][2]
    c = Chart(
        id="P1-gpus-needed-by-model-size",
        title=f"A Grok 4-scale run in 90 days needs ~{g4h / 1000:,.0f}k H100s, or ~{g4r / 1000:,.0f}k Rubin GPUs",
        subtitle=f"GPUs needed to finish each training budget in {RUN_DAYS} days at {MFU:.0%} BF16 utilization (log scale); hatched = scenario",
        alt=(f"Grouped log-scale bars of GPUs needed to finish a training run in {RUN_DAYS} days at {MFU:.0%} BF16 model FLOPs "
             f"utilization: a GPT-4-class run (2.1e25 FLOPs, Est.) needs about {sig2(need['H100 SXM'][0])} H100s; Llama 3.1 405B "
             f"(3.8e25) about {sig2(need['H100 SXM'][1])} H100s or {sig2(need['B200'][1])} B200s; Grok 4 (5e26, Est.) about "
             f"{sig2(g4h)} H100s, {sig2(need['B200'][2])} B200s or {sig2(g4r)} Rubin GPUs; a 1e27 scenario about "
             f"{sig2(need['H100 SXM'][3])} H100s or {sig2(need['Rubin'][3])} Rubin GPUs."),
        data=["P1_training_compute.csv", "P2_model_and_gpu_inputs.csv"], chapters=CH + ["P4"],
        source="Epoch AI, Meta; NVIDIA spec pages",
        source_ids=sources_of(runs.reset_index()) + sources_of(graw[graw.metric == "bf16_tflops_dense"]),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(picks))
    w = 0.26
    cols = {"H100 SXM": GEN_PAST, "B200": NV, "Rubin": NV_DARK}
    for k, g in enumerate(gpus):
        bars = ax.bar(x + (k - 1) * w, need[g], width=w, color=cols[g], label=f"{g} ({wide.loc[g, 'bf16_tflops_dense'] / 1000:g} PFLOPS BF16)")
        bars.patches[-1].set_hatch("///")
        for b, v in zip(bars, need[g]):
            ax.annotate(f"{v / 1000:,.0f}k" if v >= 1000 else f"{v:,.0f}", (b.get_x() + b.get_width() / 2, v),
                        ha="center", va="bottom", fontsize=8, color=INK["text"], xytext=(0, 2), textcoords="offset points")
    labels = [f"GPT-4-class\n{fmt_flop(runs.training_flop[picks[0]])} (Est.)",
              f"Llama 3.1 405B\n{fmt_flop(runs.training_flop[picks[1]])}",
              f"Grok 4-class\n{fmt_flop(runs.training_flop[picks[2]])} (Est.)",
              f"Next frontier\n{fmt_flop(runs.training_flop[picks[3]])} (scenario)"]
    ax.set_xticks(x, labels)
    ax.set_ylim(500, 1.5e6)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_yscale("log")
    from matplotlib.ticker import FuncFormatter
    plain_log_ticks(ax, "y")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v / 1e6:g}M" if v >= 1e6 else f"{v / 1e3:g}k"))
    freeze_scale(ax)
    c.save(fig, ax, ylabel="GPUs for 90 days", logy=True, legend=False)


@register
def tokens_per_parameter_overtraining():
    df = load("P1_training_compute.csv")
    d = df.dropna(subset=["training_tokens_t", "active_params_b"]).copy()
    d["tpp"] = d.training_tokens_t * 1e12 / (d.active_params_b * 1e9)
    d = d.sort_values("tpp")
    chin = 20.0
    top = d.iloc[-1]
    c = Chart(
        id="P1-tokens-per-parameter-overtraining",
        title=f"{top.model} saw ~{top.tpp:,.0f} training tokens per parameter, {top.tpp / chin:.0f}× the Chinchilla ratio",
        subtitle="Training tokens per (active) parameter, log scale; Chinchilla's compute-optimal rule of thumb is ~20",
        alt=(f"Log-scale horizontal bars of training tokens per active parameter: GPT-3 about 1.7, Chinchilla 20, "
             f"Llama 3.1 405B about 39, Llama 3.1 70B about 214, DeepSeek-V3 about 400 per active parameter and "
             f"Llama 3.1 8B about {top.tpp:,.0f}, {top.tpp / chin:.0f} times the compute-optimal ratio, because smaller "
             "over-trained models are cheaper to serve."),
        data=["P1_training_compute.csv"], chapters=["P1", "14"],
        source="OpenAI, DeepMind, Meta and DeepSeek papers and model cards", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    cols = [SEQ_BLUE[3] if m != "Chinchilla" else INK["muted"] for m in d.model]
    labels = [m + (" (per active param)" if m == "DeepSeek-V3" else "") for m in d.model]
    ys = np.arange(len(d))
    bars = ax.barh(ys, d.tpp, color=cols, height=0.5)
    row_labels(ax, labels, ys)
    ax.set_ylim(-0.6, len(d) - 0.2)
    for b, v in zip(bars, d.tpp):
        ax.text(v * 1.08, b.get_y() + b.get_height() / 2, f"{v:,.0f}" if v >= 10 else f"{v:.1f}", va="center",
                fontsize=9, color=INK["title"])
    ax.axvline(chin, color=INK["title"], lw=1.2, ls="--")
    ax.text(chin * 1.05, -0.55, "Chinchilla-optimal ≈ 20", fontsize=8.5, color=INK["title"], va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(1, 6000)
    plain_log_ticks(ax, "x")
    freeze_scale(ax)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="Training tokens per parameter (log scale)", logx=True, legend=False)


@register
def training_run_cost():
    df = load("P1_training_compute.csv")
    d = df.dropna(subset=["gpu_hours_m"]).copy()
    d["cost_m"] = d.gpu_hours_m * RENTAL_USD_PER_GPU_HOUR
    d = d.sort_values("cost_m")
    lo, hi = d.iloc[0], d.iloc[-1]
    ds = d[d.model == "DeepSeek-V3"].iloc[0]
    c = Chart(
        id="P1-training-run-cost",
        title=f"Final-run compute bills span ~{hi.cost_m / ds.cost_m:.0f}×: ${ds.cost_m:.1f}M (DeepSeek-V3) to ~${hi.cost_m / 1000:.1f}B (Grok 4, Est.)",
        subtitle=f"GPU-hours × ${RENTAL_USD_PER_GPU_HOUR:.0f}/GPU-hour (DeepSeek's rental assumption), US$ M (log scale); hatched = estimate",
        alt=(f"Log-scale horizontal bars of rental-equivalent compute cost at $2 per GPU-hour: Llama 3.1 8B about "
             f"${d[d.model == 'Llama 3.1 8B'].cost_m.iloc[0]:.1f}M (1.46M GPU-hours), DeepSeek-V3 ${ds.cost_m:.1f}M "
             f"(2.788M H800 hours), Llama 3.1 70B ${d[d.model == 'Llama 3.1 70B'].cost_m.iloc[0]:.0f}M, Llama 3.1 405B "
             f"about ${d[d.model == 'Llama 3.1 405B'].cost_m.iloc[0]:.0f}M (30.84M H100 hours) and Grok 4 about "
             f"${hi.cost_m:.0f}M (Epoch AI estimate of 246M H100-hours)."),
        data=["P1_training_compute.csv"], chapters=["P1", "14", "13"],
        source="Meta model card, DeepSeek-V3 report, Epoch AI", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.2)
    cols = [GEN_PAST if r.confidence == "speculative" else SEQ_BLUE[5] for _, r in d.iterrows()]
    ys = np.arange(len(d))
    bars = ax.barh(ys, d.cost_m, color=cols, height=0.5)
    row_labels(ax, [m + (" (Est.)" if cf == "speculative" else "") for m, cf in zip(d.model, d.confidence)], ys)
    ax.set_ylim(-0.45, len(d) - 0.2)
    for b, (_, r) in zip(bars, d.iterrows()):
        if r.confidence == "speculative":
            b.set_hatch("///")
        lab = f"${r.cost_m:,.1f}M" if r.cost_m < 100 else f"${r.cost_m:,.0f}M"
        ax.text(r.cost_m * 1.1, b.get_y() + b.get_height() / 2,
                f"{lab}  ({r.gpu_hours_m:,.{0 if r.gpu_hours_m >= 100 else 2}f}M GPU-h, {r.hardware.replace('NVIDIA ', '')})", va="center",
                fontsize=8.8, color=INK["title"])
    ax.set_xscale("log")
    ax.set_xlim(1, 30000)
    plain_log_ticks(ax, "x", "${:,.0f}M")
    freeze_scale(ax)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="Compute cost, US$ millions (log scale)", logx=True, legend=False)
