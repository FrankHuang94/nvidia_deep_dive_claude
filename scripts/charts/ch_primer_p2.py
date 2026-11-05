"""Primer P2 (How AI inference works) charts. Data: data/P2_model_and_gpu_inputs.csv,
data/P2_token_demand.csv."""
import math

import numpy as np
import pandas as pd

from style import (Chart, INK, NV, NV_DARK, GEN_PAST, SEQ_BLUE, entity_color, load, register,
                   sources_of)

CH = ["P2", "11", "14", "03"]
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


# ---------------------------------------------------------------- helpers
def freeze_scale(ax) -> None:
    """Chart.save() re-applies set_[xy]scale('log') when logx/logy=True, which resets custom tick
    formatters; the axes are already log here, so make those calls no-ops for this axes."""
    ax.set_yscale = lambda *a, **k: None
    ax.set_xscale = lambda *a, **k: None


def log_ticks(ax, axis: str, fn) -> None:
    from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=10))
    a.set_major_formatter(FuncFormatter(lambda v, _p: fn(v)))
    a.set_minor_formatter(NullFormatter())


def compact(v: float) -> str:
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
        if v >= div:
            return f"{v / div:g}{suf}"
    return f"{v:g}"


def inputs():
    df = load("P2_model_and_gpu_inputs.csv")
    return df


def table(df, record_type):
    d = df[df.record_type == record_type]
    return d.pivot_table(index="item", columns="metric", values="value", aggfunc="first"), d


def kv_bytes_per_token(row, bytes_per_elem=2.0) -> float:
    """Bytes of KV cache per token for one sequence."""
    if not pd.isna(row.get("kv_cache_elements_per_layer", np.nan)):
        return row["layers"] * row["kv_cache_elements_per_layer"] * bytes_per_elem
    return 2 * row["layers"] * row["kv_heads"] * row["head_dim"] * bytes_per_elem


# ---------------------------------------------------------------- charts
@register
def kv_cache_vs_context_length():
    df = inputs()
    models, mraw = table(df, "model_config")
    gpus, graw = table(df, "gpu_spec")
    ctx = np.array([1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072])
    series = [
        ("Llama 3.1 70B without GQA (counterfactual)", INK["muted"], "--", "x", "70B, no GQA (counterfactual)"),
        ("Llama 3.1 405B", entity_color("meta"), "-", "s", "Llama 3.1 405B"),
        ("Llama 3.1 70B", entity_color("meta"), "-", "o", "Llama 3.1 70B"),
        ("Llama 3.1 8B", "#A79BEA", "-", "^", "Llama 3.1 8B"),
        ("DeepSeek-V3 (MLA)", entity_color("startups"), "-", "D", "DeepSeek-V3 (MLA)"),
    ]
    kv70 = kv_bytes_per_token(models.loc["Llama 3.1 70B"]) * 131072 / 1e9
    h100 = gpus.loc["H100 SXM", "memory_gb"]
    c = Chart(
        id="P2-kv-cache-vs-context-length",
        title=f"At 128k tokens, one Llama 3.1 70B chat needs ~{kv70:.0f} GB of KV cache",
        subtitle="KV-cache memory for one sequence vs context length, GB at BF16 (log-log); dotted lines = HBM per GPU (H100 = 80 GB)",
        alt=(f"Log-log line chart of KV-cache size per sequence versus context length at BF16. At 131,072 tokens: Llama 3.1 8B "
             f"about 17 GB, Llama 3.1 70B about {kv70:.0f} GB (more than half of an 80 GB H100), Llama 3.1 405B about 68 GB, "
             "the same 70B model without grouped-query attention about 344 GB (more than a 288 GB B300 or Rubin GPU), and "
             "DeepSeek-V3 with multi-head latent attention about 9 GB."),
        data=["P2_model_and_gpu_inputs.csv"], chapters=CH + ["P3"],
        source="Meta/DeepSeek configs; GQA, DeepSeek-V2 papers; NVIDIA",
        source_ids=sources_of(mraw) + sources_of(graw[graw.metric == "memory_gb"]),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    for item, col, ls, mk, lab in series:
        kv = kv_bytes_per_token(models.loc[item]) * ctx / 1e9
        ax.plot(ctx, kv, color=col, ls=ls, marker=mk, markersize=6, lw=2)
        ax.annotate(f"{lab}: {kv[-1]:,.0f} GB", (ctx[-1], kv[-1]), xytext=(8, 0), textcoords="offset points",
                    va="center", fontsize=8.8, color=col if col != "#A79BEA" else "#6250D6", fontweight="bold")
    for g, lab in (("H100 SXM", "H100: 80 GB HBM"), ("Rubin", "B300 / Rubin: 288 GB HBM")):
        v = gpus.loc[g, "memory_gb"]
        ax.axhline(v, color=NV_DARK, lw=1.1, ls=":")
        ax.text(1100, v * 1.08, lab, fontsize=8.5, color=NV_DARK, va="bottom")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    from matplotlib.ticker import FuncFormatter, NullFormatter
    ax.set_xticks([1024, 4096, 16384, 65536, 131072])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v / 1024:g}k"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    log_ticks(ax, "y", lambda v: f"{v:g}")
    ax.set_xlim(900, 131072 * 6)
    ax.set_ylim(0.05, 900)
    ax.grid(axis="x", color=INK["grid"])
    freeze_scale(ax)
    c.save(fig, ax, xlabel="Context length, tokens (log scale)", ylabel="KV cache per sequence, GB", logy=True,
           logx=True, legend=False)


@register
def decode_tokens_per_second_bound_by_bandwidth():
    df = inputs()
    models, mraw = table(df, "model_config")
    gpus, graw = table(df, "gpu_spec")
    params = models.loc["Llama 3.1 70B", "params_b"] * 1e9
    order = ["H100 SXM", "H200 SXM", "B200", "B300", "Rubin"]
    precs = [("BF16", 2.0, SEQ_BLUE[2]), ("FP8", 1.0, SEQ_BLUE[4]), ("FP4", 0.5625, SEQ_BLUE[6])]
    rate = {p: [gpus.loc[g, "memory_bw_tbs"] * 1e12 / (params * b) for g in order] for p, b, _ in precs}
    h_fp8, r_fp8 = rate["FP8"][0], rate["FP8"][-1]
    c = Chart(
        id="P2-decode-tokens-per-second-bound-by-bandwidth",
        title=f"One Llama 3.1 70B stream at FP8 decodes at most ~{h_fp8:.0f} tokens/s on H100, ~{r_fp8:.0f} on Rubin",
        subtitle="Upper bound on single-stream decode = HBM bandwidth ÷ weight bytes read per token, tokens/s per GPU (batch 1, KV reads ignored)",
        alt=(f"Grouped bar chart of the bandwidth ceiling on decode speed for one Llama 3.1 70B stream per GPU: at FP8 weights "
             f"about {rate['FP8'][0]:.0f} tokens/s on H100 (3.35 TB/s), {rate['FP8'][1]:.0f} on H200 (4.8 TB/s), "
             f"{rate['FP8'][2]:.0f} on B200 and B300 (8 TB/s) and {r_fp8:.0f} on Rubin (19.2 TB/s); BF16 halves these and FP4 "
             "roughly doubles them. Hatched bars mark cases where the weights alone exceed 90% of the GPU's memory."),
        data=["P2_model_and_gpu_inputs.csv"], chapters=CH + ["P3", "02"],
        source="NVIDIA specs; Meta Llama 3.1 config; repo calculation",
        source_ids=sources_of(graw[graw.metric.isin(["memory_bw_tbs", "memory_gb"])]) + ["S32006", "S33013"],
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(order))
    w = 0.26
    for k, (p, b, col) in enumerate(precs):
        bars = ax.bar(x + (k - 1) * w, rate[p], width=w, color=col, label=f"Weights in {p} ({params * b / 1e9:.0f} GB)")
        for bar, g, v in zip(bars, order, rate[p]):
            too_big = params * b / 1e9 > 0.9 * gpus.loc[g, "memory_gb"]
            if too_big:
                bar.set_hatch("///")
                bar.set_alpha(0.55)
            ax.annotate(f"{v:.0f}", (bar.get_x() + bar.get_width() / 2, v), ha="center", va="bottom", fontsize=8,
                        color=INK["text"], xytext=(0, 2), textcoords="offset points")
    labels = [f"{g.replace(' SXM', '')}\n{gpus.loc[g, 'memory_bw_tbs']:g} TB/s · {gpus.loc[g, 'memory_gb']:.0f} GB" for g in order]
    ax.set_xticks(x, labels)
    ax.set_ylim(0, max(rate["FP4"]) * 1.15)
    ax.legend(loc="upper left", fontsize=8.8, title="Hatched = weights alone > 90% of one GPU's HBM", title_fontsize=8.5)
    c.save(fig, ax, ylabel="Max tokens/s for one stream", legend=False)


def _frontier(g, w_bytes, peak_tflops, params, kv_tok, a):
    n = a["gpus_per_node"]
    bw = g["memory_bw_tbs"] * 1e12 * n * a["bandwidth_efficiency"]
    flops = peak_tflops * 1e12 * n * a["compute_efficiency"]
    cap = g["memory_gb"] * 1e9 * n * a["memory_headroom"]
    kv_seq = kv_tok * a["avg_context_tokens"]
    bmax = int((cap - w_bytes) // kv_seq)
    bs = np.unique(np.clip(np.round(np.geomspace(1, max(bmax, 1), 60)).astype(int), 1, None))
    mem_t = (w_bytes + bs * kv_seq) / bw
    cmp_t = 2 * params * bs / flops
    step = np.maximum(mem_t, cmp_t) + a["step_overhead_ms"] / 1000
    return bs, 1 / step, bs / step / n


@register
def throughput_interactivity_frontier_modeled():
    df = inputs()
    models, mraw = table(df, "model_config")
    gpus, graw = table(df, "gpu_spec")
    araw = df[df.record_type == "model_assumption"]
    a = dict(zip(araw.metric, araw.value))
    m = models.loc["Llama 3.1 70B"]
    params = m["params_b"] * 1e9
    kv_tok = 2 * m["layers"] * m["kv_heads"] * m["head_dim"] * a["kv_bytes_per_element"]
    cfg = [  # label, gpu, weight bytes/param, peak column, color, linestyle
        ("8× H100 · FP8", "H100 SXM", 1.0, "fp8_tflops_dense", GEN_PAST, "-"),
        ("8× H200 · FP8", "H200 SXM", 1.0, "fp8_tflops_dense", "#86B34A", "-"),
        ("8× B200 · FP8", "B200", 1.0, "fp8_tflops_dense", NV, "-"),
        ("8× B200 · FP4", "B200", 0.5625, "fp4_tflops_dense", NV, "--"),
        ("8× Rubin · FP8", "Rubin", 1.0, "fp8_tflops_dense", NV_DARK, "-"),
    ]
    target = 100.0  # tokens/s per user
    res = {}
    for lab, g, wb, col_peak, color, ls in cfg:
        bs, tpu, tpg = _frontier(gpus.loc[g], params * wb, gpus.loc[g, col_peak], params, kv_tok, a)
        res[lab] = (bs, tpu, tpg, color, ls)

    def at_target(lab, tgt=target):
        _, tpu, tpg, *_ = res[lab]
        ok = tpu >= tgt
        return tpg[ok].max() if ok.any() else float("nan")
    h = at_target("8× H100 · FP8")
    b8 = at_target("8× B200 · FP8")
    r8 = at_target("8× Rubin · FP8")
    c = Chart(
        id="P2-throughput-interactivity-frontier-modeled",
        title=f"At {target:.0f} tokens/s per user, B200 serves ~{b8 / h:.0f}× and Rubin ~{r8 / h:.0f}× H100's tokens per GPU (Est.)",
        subtitle="Est. roofline model: Llama 3.1 70B on one 8-GPU node, FP8 KV cache, 4k-token average context; each point = a batch size",
        alt=(f"Modeled Pareto curves of throughput per GPU versus speed per user for Llama 3.1 70B on 8-GPU nodes: bigger batches "
             f"raise tokens per GPU but slow each user. At {target:.0f} tokens/s per user the model gives about {h:,.0f} tokens/s "
             f"per GPU for H100 at FP8, {at_target('8× H200 · FP8'):,.0f} for H200, {b8:,.0f} for B200 at FP8, "
             f"{at_target('8× B200 · FP4'):,.0f} for B200 at FP4 and {r8:,.0f} for Rubin at FP8; at 50 tokens/s per user the "
             f"B200 lead over H100 shrinks to about {at_target('8× B200 · FP8', 50) / at_target('8× H100 · FP8', 50):.1f} times. "
             "Estimates from a simple roofline model, not benchmarks."),
        data=["P2_model_and_gpu_inputs.csv"], chapters=CH + ["P3", "02", "08"],
        source="repo roofline model; NVIDIA specs; Llama 3.1 config",
        source_ids=["S32025", "S33013"] + sources_of(graw) + ["S32006"],
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    offs = {"8× B200 · FP4": (4, 8), "8× B200 · FP8": (60, -26), "8× Rubin · FP8": (6, 2),
            "8× H200 · FP8": (4, 4), "8× H100 · FP8": (4, 4)}
    for lab, (bs, tpu, tpg, color, ls) in res.items():
        ax.plot(tpu, tpg, color=color, ls=ls, lw=2.2)
        i = int(np.argmax(tpg))
        ax.annotate(lab, (tpu[i], tpg[i]), xytext=offs.get(lab, (6, 2)), textcoords="offset points", fontsize=9,
                    color=color, fontweight="bold", va="bottom")
    ax.axvline(target, color=INK["muted"], lw=1, ls=":")
    ax.text(target * 1.03, 7600, f"{target:.0f} tokens/s per user", fontsize=8.5, color=INK["muted"], rotation=90,
            va="bottom")
    ax.set_xscale("log")
    ax.set_xlim(20, 400)
    from matplotlib.ticker import FuncFormatter, FixedLocator, NullFormatter
    ax.xaxis.set_major_locator(FixedLocator([20, 50, 100, 200, 400]))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_ylim(0, None)
    ax.annotate("bigger batch → more tokens per GPU\nbut fewer tokens/s for each user", xy=(21, ax.get_ylim()[1] * 0.80),
                fontsize=8.5, color=INK["text"])
    freeze_scale(ax)
    c.save(fig, ax, xlabel="Interactivity: tokens/s per user (log scale)", ylabel="Throughput: tokens/s per GPU",
           logx=True, legend=False)


@register
def token_demand_growth():
    df = load("P2_token_demand.csv")
    g = df[df.entity == "Google"].sort_values("date")
    first, last = g.iloc[0], g.iloc[-1]
    mult = last.monthly_tokens_t / first.monthly_tokens_t

    def yr(s):
        y, mth = str(s).split("-")
        return int(y) + (int(mth) - 0.5) / 12
    months = round((yr(last.date) - yr(first.date)) * 12)
    c = Chart(
        id="P2-token-demand-growth",
        title=f"Google's monthly tokens rose ~{mult:.0f}× in {months} months, to over 1.3 quadrillion",
        subtitle="Tokens processed per month, trillions (log scale), as disclosed by companies; hollow = derived from a stated rate",
        alt=(f"Log-scale chart of disclosed AI token volumes: Google rose from 9.7 trillion tokens per month (April 2024) to "
             f"480 trillion (April 2025), about 980 trillion (mid-2025) and over 1.3 quadrillion (October 2025), about "
             f"{mult:.0f} times in {months} months. Microsoft processed over 100 trillion tokens in Jan-Mar 2025 (5 times a year "
             "earlier) with 50 trillion in March alone; OpenAI's API ran about 6 billion tokens per minute in October 2025, "
             "roughly 259 trillion per month."),
        data=["P2_token_demand.csv"], chapters=CH + ["00", "13"],
        source="Alphabet, Microsoft and OpenAI executive remarks", source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    styles = {"Google": (entity_color("google"), "o"), "Microsoft": (entity_color("microsoft"), "s"),
              "OpenAI API": (INK["text"], "D")}
    for ent, d in df.groupby("entity", sort=False):
        d = d.sort_values("date")
        col, mk = styles.get(ent, (INK["muted"], "o"))
        xs = d.date.map(yr)
        if ent == "Google":
            ax.plot(xs, d.monthly_tokens_t, color=col, lw=2)
        for x_, v, basis in zip(xs, d.monthly_tokens_t, d.basis):
            ax.scatter(x_, v, s=70, marker=mk, facecolor="white" if basis == "derived" else col, edgecolor=col,
                       linewidth=2, zorder=3)
        for x_, v, metric in zip(xs, d.monthly_tokens_t, d.metric):
            lab = f"{v / 1000:.1f} quadrillion" if v >= 1000 else f"{v:,.0f}T" if v >= 10 else f"{v:.1f}T"
            if metric == "quarterly_tokens_processed":
                lab += " (qtr avg)"
            dy = 10 if ent != "Microsoft" else -14
            ax.annotate(lab, (x_, v), xytext=(0, dy), textcoords="offset points", ha="center", fontsize=8.3, color=col)
        ax.scatter([], [], s=60, marker=mk, color=col, label=ent)
    ax.set_yscale("log")
    log_ticks(ax, "y", lambda v: f"{v:,.0f}")
    ax.set_ylim(2, 5000)
    ax.set_xlim(2023.9, 2026.1)
    ax.set_xticks([2024, 2024.5, 2025, 2025.5, 2026], ["Jan 2024", "Jul 2024", "Jan 2025", "Jul 2025", "Jan 2026"])
    ax.legend(loc="upper left", fontsize=9)
    freeze_scale(ax)
    c.save(fig, ax, xlabel="Date of the disclosed figure", ylabel="Tokens per month, trillions", logy=True, legend=False)


@register
def reasoning_token_multiplier():
    df = inputs()
    sc = df[df.record_type == "scenario"]
    t = sc.pivot_table(index="item", columns="metric", values="value", aggfunc="first")
    order = ["Chat reply", "Reasoning answer", "Agentic coding task"]
    t = t.loc[order]
    t["generated"] = t.reasoning_tokens + t.output_tokens
    t["total"] = t.generated + t.input_tokens
    base = t.loc["Chat reply"]
    c = Chart(
        id="P2-reasoning-token-multiplier",
        title=(f"Reasoning multiplies generated tokens ~{t.loc['Reasoning answer', 'generated'] / base.generated:.0f}×; "
               f"an agentic task uses ~{round(t.loc['Agentic coding task', 'total'] / base.total, -2):,.0f}× in total (Est.)"),
        subtitle="Illustrative tokens per task (Est.), log scale: context read (prefill) vs tokens generated (decode, incl. hidden reasoning)",
        alt=(f"Illustrative log-scale bars of tokens per task: a chat reply reads about {base.input_tokens:,.0f} tokens and generates "
             f"{base.generated:,.0f}; a reasoning answer generates about {t.loc['Reasoning answer', 'generated']:,.0f} (mostly hidden "
             f"thinking), {t.loc['Reasoning answer', 'generated'] / base.generated:.0f} times more; a 30-turn agentic coding task re-reads "
             f"about {t.loc['Agentic coding task', 'input_tokens'] / 1e6:.2f} million context tokens and generates about "
             f"{t.loc['Agentic coding task', 'generated'] / 1e3:,.0f} thousand, roughly "
             f"{t.loc['Agentic coding task', 'total'] / base.total:,.0f} times the chat total."),
        data=["P2_model_and_gpu_inputs.csv"], chapters=CH + ["01"],
        source="repo scenarios; OpenAI reasoning guide", source_ids=sources_of(sc),
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    y = np.arange(len(order))
    h = 0.34
    b1 = ax.barh(y - h / 2, t.input_tokens, height=h, color=SEQ_BLUE[3], label="Context read (prefill / input tokens)")
    b2 = ax.barh(y + h / 2, t.generated, height=h, color="#C98500", label="Generated (decode: reasoning + answer)")
    for bars, vals in ((b1, t.input_tokens), (b2, t.generated)):
        for b, v in zip(bars, vals):
            b.set_hatch("//")
            ax.text(v * 1.12, b.get_y() + b.get_height() / 2, compact(v), va="center", fontsize=9, color=INK["title"])
    tr = ax.get_yaxis_transform()
    for i, item in enumerate(order):
        mult = t.loc[item, "total"] / base.total
        ax.text(0.004, i - 0.42, f"{item} — total {compact(t.loc[item, 'total'])} tokens ({mult:,.0f}× chat)",
                transform=tr, fontsize=9.5, fontweight="bold", color=INK["title"], va="bottom")
    ax.set_yticks([])
    ax.set_ylim(len(order) - 0.45, -0.75)
    ax.set_xscale("log")
    log_ticks(ax, "x", compact)
    ax.set_xlim(100, 2e7)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8.8)
    freeze_scale(ax)
    c.save(fig, ax, xlabel="Tokens per task (log scale)", logx=True, legend=False)
