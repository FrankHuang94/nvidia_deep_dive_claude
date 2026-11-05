"""Benchmark charts: MLPerf Inference/Training (primary MLCommons data) and InferenceX / NVIDIA-published
throughput-vs-interactivity and software-gain data (chapters 11, 14, 15). Owner: Phase-1 agent A6.

Data: data/mlperf_results.csv, data/inference_benchmarks.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from style import Chart, GEN_PAST, INK, NV, NV_DARK, axis_break, entity_color, load, register, sources_of

MLP = "mlperf_results.csv"
INF = "inference_benchmarks.csv"
AMD = entity_color("AMD")
AMD_LIGHT = "#E59AA8"
INTEL = entity_color("Intel")


def _margins(fig, **over):
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _ids(*frames):
    out = []
    for f in frames:
        for sid in sources_of(f):
            if sid not in out:
                out.append(sid)
    return out


def _plain_log(axis):
    def f(v, _pos):
        if v <= 0:
            return ""
        return f"{v:,.0f}" if v >= 1 else f"{v:g}"
    axis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    axis.set_major_formatter(FuncFormatter(f))
    axis.set_minor_formatter(NullFormatter())


def _date(s: str) -> pd.Timestamp:
    s = str(s)
    if len(s) == 7:
        s += "-15"
    return pd.Timestamp(s)


def _vendor_color(acc: str) -> str:
    a = str(acc)
    if a.startswith("NVIDIA"):
        return NV if any(k in a for k in ("GB300", "B300", "Vera", "GB200", "B200", "RTX PRO")) else GEN_PAST
    if a.startswith("AMD"):
        return AMD if any(k in a for k in ("MI355X", "MI350")) else AMD_LIGHT
    if a.startswith("Intel"):
        return INTEL
    if a.startswith("Google"):
        return entity_color("Google")
    return entity_color("other")


def _interp(front: pd.DataFrame, x0: float, ycol: str = "throughput_tok_s_per_gpu") -> float | None:
    """Log-linear interpolation of a Pareto frontier at interactivity x0 (no extrapolation)."""
    f = front.sort_values("interactivity_tok_s_per_user")
    xs, ys = f.interactivity_tok_s_per_user.values, f[ycol].values
    if len(xs) < 2 or x0 < xs.min() or x0 > xs.max():
        return None
    return float(np.exp(np.interp(x0, xs, np.log(ys))))


# --------------------------------------------------------------------------------------
# MLPerf
# --------------------------------------------------------------------------------------
@register
def mlperf_same_hardware_gains():
    df = load(MLP)
    d = df[df.notes.str.startswith("series=same-hardware") & (df.metric == "throughput")].copy()
    d["date"] = d.round_date.map(_date)
    series = [
        ("GB300 NVL72 · DeepSeek-R1 Server", "NVIDIA GB300", "DeepSeek-R1", "Server", NV_DARK, "o", "-"),
        ("GB200 NVL72 · DeepSeek-R1 Server", "NVIDIA GB200", "DeepSeek-R1", "Server", NV, "s", "-"),
        ("GB300 NVL72 · Llama 3.1 405B Server", "NVIDIA GB300", "Llama 3.1 405B", "Server", NV_DARK, "^", "--"),
        ("H200 · Llama 2 70B Offline", "NVIDIA H200", "Llama 2 70B (99.9% accuracy)", "Offline", GEN_PAST, "D", "-"),
        ("H100 · Llama 2 70B Offline", "NVIDIA H100", "Llama 2 70B (99.9% accuracy)", "Offline", GEN_PAST, "v", "--"),
    ]
    used, ends = [], {}
    for lab, acc, bench, scen, *_ in series:
        s = d[(d.accelerator == acc) & (d.benchmark == bench) & (d.scenario == scen)].sort_values("date")
        used.append(s)
        ends[lab] = (s.per_accelerator_value.iloc[-1] / s.per_accelerator_value.iloc[0], s.iloc[0], s.iloc[-1])
    g3 = ends[series[0][0]]
    h1 = ends[series[4][0]]
    c = Chart(
        id="11-mlperf-same-hardware-software-gains",
        title=f"Software alone lifted GB300 NVL72 DeepSeek-R1 MLPerf throughput {g3[0]:.1f}x in a year",
        subtitle="Per-GPU throughput of the same NVIDIA-submitted system across MLPerf Inference rounds, indexed to first round = 1.0",
        alt=(f"Line chart of MLPerf Inference per-GPU throughput for unchanged NVIDIA hardware across rounds. GB300 NVL72 on DeepSeek-R1 "
             f"Server rose from {g3[1].per_accelerator_value:,.0f} to {g3[2].per_accelerator_value:,.0f} tokens/s per GPU "
             f"({g3[0]:.1f}x, Sep 2025 to Sep 2026); GB200 NVL72 {ends[series[1][0]][0]:.1f}x; GB300 on Llama 3.1 405B "
             f"{ends[series[2][0]][0]:.1f}x; H100 on Llama 2 70B {h1[0]:.2f}x and H200 {ends[series[3][0]][0]:.2f}x over a year. "
             "Gains come from TensorRT-LLM, Dynamo and newer serving recipes, not new silicon."),
        data=[MLP], chapters=["11", "09", "15", "01"],
        source="MLCommons MLPerf Inference v4.0-v6.1 results", source_ids=_ids(*used),
    )
    fig, ax = c.figure(width=11, height=6.0)
    for (lab, acc, bench, scen, col, mk, ls), s in zip(series, used):
        idx = s.per_accelerator_value / s.per_accelerator_value.iloc[0]
        ax.plot(s.date, idx, color=col, marker=mk, ls=ls, lw=2, markersize=8, label=lab)
        ax.annotate(f"{idx.iloc[-1]:.2f}x" if idx.iloc[-1] < 2 else f"{idx.iloc[-1]:.1f}x", (s.date.iloc[-1], idx.iloc[-1]),
                    xytext=(8, 0), textcoords="offset points", va="center", fontsize=9.5, color=col, fontweight="bold")
    ax.axhline(1, color=INK["base"], lw=0.8)
    ax.set_ylim(0.8, 3.2)
    ax.set_xlim(pd.Timestamp("2024-02-01"), pd.Timestamp("2026-12-15"))
    ax.legend(loc="upper left", fontsize=9, frameon=False)
    c.save(fig, ax, xlabel="MLPerf round publication date", ylabel="Per-GPU throughput, first round = 1.0", legend=False)


def _per_acc_bars(round_name, bench, scen, chart_id, chapters, title_fn, sub, width=11, height=6.4):
    df = load(MLP)
    d = df[(df["round"] == round_name) & (df.benchmark == bench) & (df.scenario == scen) & (df.metric == "throughput")].copy()
    d = d.sort_values("per_accelerator_value").drop_duplicates("accelerator", keep="last")
    d = d.sort_values("per_accelerator_value")
    title, alt = title_fn(d)
    c = Chart(id=chart_id, title=title, subtitle=sub, alt=alt, data=[MLP], chapters=chapters,
              source=f"MLCommons MLPerf {round_name} results (closed division)", source_ids=_ids(d),
              note="Hatched = preview category")
    fig, ax = c.figure(width=width, height=height)
    y = np.arange(len(d))
    cols = [_vendor_color(a) for a in d.accelerator]
    bars = ax.barh(y, d.per_accelerator_value, color=cols, height=0.66)
    for b, (_, r) in zip(bars, d.iterrows()):
        if "category=preview" in r.notes:
            b.set_hatch("///")
        ax.text(r.per_accelerator_value + d.per_accelerator_value.max() * 0.01, b.get_y() + b.get_height() / 2,
                f"{r.per_accelerator_value:,.0f}  ({r.submitter}, {int(r.accelerator_count)} accel.)", va="center", fontsize=8.5,
                color=INK["text"])
    ax.set_yticks(y)
    ax.set_yticklabels(d.accelerator, fontsize=9)
    ax.set_xlim(0, d.per_accelerator_value.max() * 1.42)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    _margins(fig, left=0.2, right=0.97)
    handles = [Line2D([0], [0], color=NV, lw=8, label="NVIDIA Blackwell"), Line2D([0], [0], color=GEN_PAST, lw=8, label="NVIDIA earlier"),
               Line2D([0], [0], color=AMD, lw=8, label="AMD CDNA 4"), Line2D([0], [0], color=AMD_LIGHT, lw=8, label="AMD CDNA 3"),
               Line2D([0], [0], color=INTEL, lw=8, label="Intel")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.5, frameon=False)
    c.save(fig, ax, xlabel="Tokens/s per accelerator (best closed result in round)", legend=False)


@register
def mlperf_llm_inference_per_accelerator():
    def tf(d):
        g = d.set_index("accelerator").per_accelerator_value
        t = (f"On MLPerf Llama 2 70B, AMD's MI355X ({g['AMD MI355X']:,.0f} tok/s) matches B200 but trails GB300 by "
             f"{(1 - g['AMD MI355X'] / g['NVIDIA GB300']) * 100:.0f}%")
        alt = ("Horizontal bar chart of the best closed-division MLPerf Inference v6.0 Llama 2 70B Offline result per accelerator, "
               f"in tokens/s per accelerator: GB300 {g['NVIDIA GB300']:,.0f}, B300 {g['NVIDIA B300']:,.0f}, B200 {g['NVIDIA B200']:,.0f}, "
               f"MI355X {g['AMD MI355X']:,.0f}, GB200 {g['NVIDIA GB200']:,.0f}, MI350X {g['AMD MI350X']:,.0f}, MI325X {g['AMD MI325X']:,.0f}, "
               f"H200 NVL {g['NVIDIA H200 NVL']:,.0f}, MI300X {g['AMD MI300X']:,.0f}; Intel Arc Pro cards below 1,000.")
        return t, alt
    _per_acc_bars("Inference v6.0", "Llama 2 70B (99% accuracy)", "Offline", "15-mlperf-llm-inference-per-accelerator",
                  ["15", "02", "11"], tf, "MLPerf Inference v6.0 (Apr 2026), Llama 2 70B Offline, best closed result per accelerator, tokens/s per accelerator")


@register
def mlperf_gptoss_per_accelerator():
    def tf(d):
        g = d.set_index("accelerator").per_accelerator_value
        t = (f"MLPerf gpt-oss-120b: MI355X beats B300 per GPU ({g['AMD MI355X']:,.0f} vs {g['NVIDIA B300']:,.0f} tok/s); "
             f"GB300 leads")
        alt = ("Horizontal bar chart of the best closed MLPerf Inference v6.1 gpt-oss-120b Offline result per accelerator, tokens/s per "
               f"accelerator: GB300 {g['NVIDIA GB300']:,.0f}, GB200 {g['NVIDIA GB200']:,.0f}, MI355X {g['AMD MI355X']:,.0f}, "
               f"B300 {g['NVIDIA B300']:,.0f}, MI350X {g['AMD MI350X']:,.0f}, B200 {g['NVIDIA B200']:,.0f}, MI300X {g['AMD MI300X']:,.0f}, "
               "RTX PRO 6000 and Intel Arc Pro B70 far below. A small-active-parameter MoE favours AMD's memory bandwidth.")
        return t, alt
    _per_acc_bars("Inference v6.1", "gpt-oss-120b", "Offline", "15-mlperf-gpt-oss-per-accelerator", ["15", "11"], tf,
                  "MLPerf Inference v6.1 (Sep 2026), gpt-oss-120b Offline, best closed result per accelerator, tokens/s per accelerator")


@register
def mlperf_training_time_at_scale():
    df = load(MLP)
    d = df[(df.benchmark == "Llama 3.1 405B pre-training") & (df.metric == "time_to_train")].copy()
    groups = [("Training v5.0", "NVIDIA H100", "H100 · v5.0 (Jun 2025)", GEN_PAST, "s", "--"),
              ("Training v5.0", "NVIDIA GB200", "GB200 · v5.0 (Jun 2025)", NV, "o", "--"),
              ("Training v5.1", "NVIDIA GB200", "GB200 · v5.1 (Nov 2025)", NV, "o", "-"),
              ("Training v6.0", "NVIDIA GB200", "GB200 · v6.0 (Jun 2026)", NV, "*", ":"),
              ("Training v6.0", "NVIDIA GB300", "GB300 · v6.0 (Jun 2026)", NV_DARK, "^", "-")]
    first = d[(d["round"] == "Training v5.0") & (d.accelerator == "NVIDIA GB200")].sort_values("value").iloc[0]
    best = d.sort_values("value").iloc[0]
    h100 = d[(d.accelerator == "NVIDIA H100")].sort_values("value").iloc[0]
    c = Chart(
        id="15-mlperf-training-time-at-scale",
        title=(f"MLPerf Llama 3.1 405B training: {first.value:.0f} min on {int(first.accelerator_count):,} GB200s (2025) → "
               f"{best.value:.0f} min on {int(best.accelerator_count):,} (2026)"),
        subtitle="MLPerf Training time-to-train vs cluster size, Llama 3.1 405B, closed division (minutes; both axes log scale)",
        alt=(f"Log-log chart of MLPerf Training time-to-train against GPU count for Llama 3.1 405B. In v5.0 (June 2025) 2,496 GB200 GPUs "
             f"took {first.value:.1f} minutes and 8,192 H100s {h100.value:.1f}; in v5.1 5,120 GB200s took 10.0 minutes; in v6.0 "
             f"{int(best.accelerator_count):,} GB200s ({best.submitter}) took {best.value:.1f} minutes and 4,096 GB300s 9.8 minutes. "
             "No non-NVIDIA accelerator has submitted this benchmark."),
        data=[MLP], chapters=["15", "08", "06", "P1"],
        source="MLCommons MLPerf Training v5.0-v6.0 (repo-computed scores)", source_ids=_ids(d),
    )
    fig, ax = c.figure(width=11, height=6.2)
    for rnd, acc, lab, col, mk, ls in groups:
        s = d[(d["round"] == rnd) & (d.accelerator == acc)].sort_values("accelerator_count")
        s = s.groupby("accelerator_count", as_index=False).value.min()
        ax.plot(s.accelerator_count, s.value, color=col, marker=mk, ls=ls, lw=2, markersize=9 if mk != "*" else 14, label=lab)
    for _, r in d.sort_values("value").groupby(["round", "accelerator"]).head(1).iterrows():
        if r.accelerator_count >= 2048:
            off = (-52, -14) if r.accelerator == "NVIDIA GB300" else (6, 6)
            ax.annotate(f"{r.value:.1f} min", (r.accelerator_count, r.value), xytext=off, textcoords="offset points",
                        fontsize=8.5, color=INK["title"])
    ax.set_xscale("log")
    ax.set_yscale("log")
    _plain_log(ax.xaxis)
    _plain_log(ax.yaxis)
    ax.grid(axis="both", color=INK["grid"])
    ax.legend(loc="upper right", fontsize=9, frameon=False)
    c.save(fig, ax, xlabel="GPUs in the training cluster (log scale)", ylabel="Time to train, minutes (log scale)", logy=True,
           legend=False)


@register
def mlperf_participation_by_vendor():
    df = load(MLP)
    inf = df[df.metric == "performance_results_by_accelerator_vendor"].copy()
    trn = df[df.metric == "results_by_accelerator_vendor"].copy()
    org = df[df.metric == "submitting_organizations"]
    rounds_i = ["Inference v5.0", "Inference v5.1", "Inference v6.0", "Inference v6.1"]
    rounds_t = ["Training v4.1", "Training v5.0", "Training v5.1", "Training v6.0"]
    vend = [("NVIDIA", NV), ("AMD", AMD), ("Intel", INTEL), ("Google", entity_color("Google")), ("Mixed", "#7A7A7A"),
            ("CPU-only", entity_color("other"))]

    def share(frame, rnd, v):
        x = frame[frame["round"] == rnd]
        return x[x.accelerator == v].value.sum() / x.value.sum() * 100
    a0, a1 = share(inf, rounds_i[0], "AMD"), share(inf, rounds_i[-1], "AMD")
    n1 = share(inf, rounds_i[-1], "NVIDIA")
    c = Chart(
        id="15-mlperf-participation-by-vendor",
        title=f"AMD's share of closed MLPerf inference results rose from {a0:.0f}% to {a1:.0f}% in 18 months; NVIDIA still {n1:.0f}%",
        subtitle="Closed-division performance results by accelerator vendor per round (count); labels = submitting organisations",
        alt=(f"Two stacked bar panels. Inference rounds v5.0 to v6.1: AMD-based results rose from {a0:.0f}% to {a1:.0f}% of closed "
             f"performance results while NVIDIA-based results fell to {n1:.0f}%; Google submitted TPUs only in v5.0 and Intel added Arc "
             "Pro cards. Training rounds v4.1 to v6.0: NVIDIA accounts for 87-93% of results, AMD rose from 1 to 30 results and Google "
             "TPU results disappeared after v5.0."),
        data=[MLP], chapters=["15", "09"],
        source="MLCommons results repositories (repo count)", source_ids=_ids(inf, trn, org),
    )
    fig, (ax1, ax2) = c.figure_grid(1, 2, width=12, height=6.0)
    for ax, frame, rounds, ttl in [(ax1, inf, rounds_i, "Inference (closed, datacenter + edge)"),
                                   (ax2, trn, rounds_t, "Training (closed)")]:
        x = np.arange(len(rounds))
        bottom = np.zeros(len(rounds))
        for v, col in vend:
            vals = np.array([frame[(frame["round"] == r) & (frame.accelerator == v)].value.sum() for r in rounds])
            if vals.sum() == 0:
                continue
            ax.bar(x, vals, bottom=bottom, color=col, width=0.62, edgecolor="#FFFFFF", linewidth=0.6, label=v)
            for xi, val, b in zip(x, vals, bottom):
                if val >= 25:
                    ax.text(xi, b + val / 2, f"{int(val)}", ha="center", va="center", fontsize=8.5,
                            color="#FFFFFF" if v != "CPU-only" else INK["title"])
            bottom += vals
        for xi, r in zip(x, rounds):
            n = org[org["round"] == r].value
            if len(n):
                ax.text(xi, bottom[xi] + bottom.max() * 0.015, f"{int(n.iloc[0])} orgs", ha="center", va="bottom", fontsize=8.5,
                        color=INK["text"])
        ax.set_xticks(x)
        ax.set_xticklabels([r.split(" ")[1] for r in rounds])
        ax.set_title(ttl, fontsize=10.5, color=INK["title"], loc="left")
        ax.set_axisbelow(True)
        ax.set_ylim(0, bottom.max() * 1.1)
    ax1.set_ylabel("Closed-division results (count)")
    ax1.legend(loc="upper right", fontsize=8.5, frameon=False)
    _margins(fig, left=0.07, right=0.98, wspace=0.18)
    c.save(fig, [ax1, ax2], legend=False, top=0.82)


@register
def mlperf_training_single_node():
    df = load(MLP)
    d = df[(df.benchmark == "Llama 2 70B LoRA fine-tuning") & (df.metric == "time_to_train") & (df.accelerator_count == 8) &
           df["round"].isin(["Training v5.0", "Training v5.1", "Training v6.0"])].copy()
    accs = ["NVIDIA GB300", "NVIDIA B300", "NVIDIA B200", "NVIDIA GB200", "AMD MI355X", "AMD MI350X", "AMD MI325X", "NVIDIA H200",
            "AMD MI300X"]
    rounds = [("Training v5.0", "v5.0 (Jun 2025)", "o", "#FFFFFF"), ("Training v5.1", "v5.1 (Nov 2025)", "s", None),
              ("Training v6.0", "v6.0 (Jun 2026)", "D", None)]
    v6 = d[d["round"] == "Training v6.0"].set_index("accelerator").value
    c = Chart(
        id="15-mlperf-training-single-node",
        title=(f"MI355X fine-tunes Llama 2 70B on 8 GPUs in {v6['AMD MI355X']:.1f} min, {v6['AMD MI355X'] / v6['NVIDIA GB300']:.1f}x "
               f"GB300's {v6['NVIDIA GB300']:.1f} min and close to B200"),
        subtitle="MLPerf Training, Llama 2 70B LoRA, best 8-accelerator closed result per accelerator and round (minutes, lower is better)",
        alt=(f"Dot plot of 8-GPU MLPerf Training LoRA fine-tuning times. In v6.0: GB300 {v6['NVIDIA GB300']:.1f} min, B300 "
             f"{v6['NVIDIA B300']:.1f}, B200 {v6['NVIDIA B200']:.1f}, MI355X {v6['AMD MI355X']:.1f}, GB200 {v6['NVIDIA GB200']:.1f}, "
             f"MI350X {v6['AMD MI350X']:.1f}. AMD's MI325X needed about 21-22 minutes in 2025 and MI300X about 28-29, so AMD closed most "
             "of the single-node gap with CDNA 4 while NVIDIA's lead persists at rack scale."),
        data=[MLP], chapters=["15", "02"],
        source="MLCommons MLPerf Training v5.0-v6.0 (repo-computed scores)", source_ids=_ids(d),
    )
    fig, ax = c.figure(width=11, height=6.0)
    y = np.arange(len(accs))
    for rnd, lab, mk, face in rounds:
        xs, ys, cs = [], [], []
        for i, a in enumerate(accs):
            v = d[(d["round"] == rnd) & (d.accelerator == a)].value
            if len(v):
                xs.append(v.min()); ys.append(i); cs.append(_vendor_color(a))
        ax.scatter(xs, ys, marker=mk, s=80, facecolor=[face or col for col in cs] if face else cs, edgecolor=cs, linewidth=1.8,
                   zorder=3, label=lab)
    for i, a in enumerate(accs):
        v = d[d.accelerator == a].value
        ax.plot([v.min(), v.max()], [i, i], color=INK["grid"], lw=2, zorder=1)
        if a in v6.index:
            ax.annotate(f"{v6[a]:.1f}", (v6[a], i), xytext=(0, 9), textcoords="offset points", ha="center", fontsize=8.5,
                        color=INK["title"])
    ax.set_yticks(y)
    ax.set_yticklabels(accs)
    ax.invert_yaxis()
    ax.set_xlim(0, 32)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    leg = [Line2D([0], [0], marker=mk, ls="", markersize=8, markerfacecolor=face or INK["text"], markeredgecolor=INK["text"],
                  label=lab) for _, lab, mk, face in rounds]
    ax.legend(handles=leg, loc="center right", fontsize=9, frameon=False)
    _margins(fig, left=0.15, right=0.97)
    c.save(fig, ax, xlabel="Time to train, minutes (8 accelerators)", legend=False)


# --------------------------------------------------------------------------------------
# Inference throughput vs interactivity (InferenceX, NVIDIA-published)
# --------------------------------------------------------------------------------------
PARETO_SYS = [("GB300 NVL72", NV_DARK, "o", "-"), ("GB200 NVL72", NV, "s", "-"), ("B300", NV_DARK, "^", "--"),
              ("B200", NV, "v", "--"), ("H200", GEN_PAST, "D", "-"), ("H100", GEN_PAST, "P", ":"),
              ("MI355X", AMD, "o", "-"), ("MI300X", AMD_LIGHT, "s", "--")]


def _frontier():
    df = load(INF)
    return df[(df.benchmark_suite == "SemiAnalysis InferenceX (Pareto frontier, no speculative decoding)") &
              (df.model == "DeepSeek-R1-0528 (1k in/1k out)")].copy()


@register
def throughput_vs_interactivity_pareto():
    d = _frontier()
    x0 = 50.0
    at = {s: _interp(d[d.system == s], x0) for s, *_ in PARETO_SYS}
    g3, h2, m3 = at["GB300 NVL72"], at["H200"], at["MI355X"]
    c = Chart(
        id="11-throughput-vs-interactivity-pareto",
        title=(f"At {x0:.0f} tok/s/user, GB300 NVL72 delivers ~{g3 / h2:.0f}x H200 and ~{g3 / m3:.0f}x MI355X throughput per GPU"),
        subtitle="InferenceX Pareto frontiers, DeepSeek-R1-0528, 1k in/1k out, FP4 (FP8 on Hopper/CDNA 3), no speculative decoding",
        alt=(f"Log-scale Pareto chart of total tokens per second per GPU against tokens per second per user for eight systems on "
             f"DeepSeek-R1. Interpolated at {x0:.0f} tok/s/user: GB300 NVL72 about {g3:,.0f}, GB200 NVL72 about {at['GB200 NVL72']:,.0f}, "
             f"B300 about {at['B300']:,.0f}, B200 about {at['B200']:,.0f}, MI355X about {m3:,.0f}, H200 about {h2:,.0f} tokens/s per GPU. "
             "Rack-scale NVL72 systems dominate the low-to-mid interactivity range; all curves fall steeply as interactivity rises."),
        data=[INF], chapters=["11", "14", "15", "P2"],
        source="SemiAnalysis InferenceX public-API snapshot (Oct 2026)", source_ids=_ids(d),
        note="Snapshot subset; each point links to its run in the CSV",
    )
    fig, ax = c.figure(width=11, height=6.4)
    for sysname, col, mk, ls in PARETO_SYS:
        s = d[d.system == sysname].sort_values("interactivity_tok_s_per_user")
        s = s[s.interactivity_tok_s_per_user <= 200]
        if s.empty:
            continue
        prec = s.precision.iloc[0]
        ax.plot(s.interactivity_tok_s_per_user, s.throughput_tok_s_per_gpu, color=col, marker=mk, ls=ls, lw=2, markersize=7,
                label=f"{sysname} ({prec})")
    ax.axvline(x0, color=INK["muted"], lw=0.8, ls=":")
    ax.text(x0 + 1.5, 13000, f"{x0:.0f} tok/s/user", fontsize=8.5, color=INK["muted"])
    ax.set_yscale("log")
    _plain_log(ax.yaxis)
    ax.set_xlim(0, 200)
    ax.legend(loc="upper right", fontsize=8.8, frameon=False, ncol=2)
    c.save(fig, ax, xlabel="Interactivity: tokens/s per user (median)", ylabel="Throughput: total tokens/s per GPU (log scale)",
           logy=True, legend=False)


@register
def cost_per_million_tokens():
    d = _frontier()
    x0 = 50.0
    rows = []
    for sysname, col, *_ in PARETO_SYS:
        f = d[d.system == sysname]
        tput = _interp(f, x0)
        if tput is None:
            continue
        costh = float(f.notes.str.extract(r"TCO \$([\d.]+)/GPU-hr").iloc[0, 0])
        rows.append((sysname, f.vendor.iloc[0], costh * 1e6 / (tput * 3600), col, costh))
    r = pd.DataFrame(rows, columns=["system", "vendor", "cost", "color", "costh"]).sort_values("cost", ascending=False)
    q = load(INF)
    t = q[(q.benchmark_suite == "SemiAnalysis InferenceX article (TPU vs Blackwell)") & q.cost_usd_per_m_tokens.notna()]
    best = r.sort_values("cost").iloc[0]
    h200 = r[r.system == "H200"].cost.iloc[0]
    tpu = t[t.system.str.contains("TPU")].cost_usd_per_m_tokens.iloc[0]
    b200q = t[t.system == "B200"].cost_usd_per_m_tokens.iloc[0]
    c = Chart(
        id="14-cost-per-million-tokens-by-system",
        title=(f"{best.system} serves DeepSeek-R1 for ~${best.cost:.2f}/M tokens at {x0:.0f} tok/s/user, "
               f"{h200 / best.cost:.0f}x below H200 (Est.)"),
        subtitle="Est. US$ per million total tokens = owner TCO $/GPU-hr ÷ measured throughput (InferenceX); two workloads",
        alt=(f"Two bar panels of estimated cost per million total tokens. Left, DeepSeek-R1 at {x0:.0f} tokens/s per user: "
             + ", ".join(f"{a.system} ${a.cost:.2f}" for a in r.sort_values('cost').itertuples()) +
             f". Right, Qwen3.5 397B FP8 at 100 tokens/s per user: TPU7x Ironwood ${tpu:.3f}, B200 ${b200q:.3f}, B300 "
             f"${t[t.system == 'B300'].cost_usd_per_m_tokens.iloc[0]:.3f}, showing Google's TPU about "
             f"{(1 - tpu / b200q) * 100:.0f}% cheaper than B200 on that workload."),
        data=[INF], chapters=["14", "11", "15"],
        source="SemiAnalysis InferenceX (throughput; TCO $/GPU-hr); repo interpolation", source_ids=_ids(d, t),
        note="Est.: cost = TCO $/GPU-hr / throughput",
    )
    fig, (ax1, ax2) = c.figure_grid(1, 2, width=12, height=6.0, gridspec_kw=dict(width_ratios=[1.6, 1]))
    y = np.arange(len(r))
    bars = ax1.barh(y, r.cost, color=r.color, height=0.62)
    for b, a in zip(bars, r.itertuples()):
        ax1.text(a.cost * 1.1, b.get_y() + b.get_height() / 2, f"${a.cost:.2f}  (TCO ${a.costh:.2f}/GPU-hr)",
                 va="center", fontsize=8.5, color=INK["text"])
        b.set_hatch("//")
    ax1.set_yticks(y)
    ax1.set_yticklabels(r.system)
    ax1.set_xscale("log")
    ax1.set_xlim(0.05, r.cost.max() * 6)
    _plain_log(ax1.xaxis)
    ax1.set_title(f"DeepSeek-R1-0528, 1k/1k, at {x0:.0f} tok/s/user (no spec. decoding)", fontsize=10, loc="left", color=INK["title"])
    ax1.grid(axis="x", color=INK["grid"]); ax1.grid(axis="y", visible=False)
    t = t.sort_values("cost_usd_per_m_tokens", ascending=False)
    cols = [entity_color("Google") if "TPU" in s else NV for s in t.system]
    bb = ax2.barh(np.arange(len(t)), t.cost_usd_per_m_tokens, color=cols, height=0.55)
    for b, a in zip(bb, t.itertuples()):
        ax2.text(a.cost_usd_per_m_tokens + 0.004, b.get_y() + b.get_height() / 2, f"${a.cost_usd_per_m_tokens:.3f}", va="center",
                 fontsize=9, color=INK["text"])
        b.set_hatch("//")
    ax2.set_yticks(np.arange(len(t)))
    ax2.set_yticklabels(t.system)
    ax2.set_xlim(0, t.cost_usd_per_m_tokens.max() * 1.45)
    ax2.set_xlabel("US$ per million tokens (Est.)")
    ax2.set_title("Qwen3.5 397B FP8, 8k/1k, at 100 tok/s/user", fontsize=10, loc="left", color=INK["title"])
    ax2.grid(axis="x", color=INK["grid"]); ax2.grid(axis="y", visible=False)
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)
    _margins(fig, left=0.1, right=0.98, wspace=0.42)
    c.save(fig, [ax1, ax2], xlabel="US$ per million tokens (Est.)", logx=True, legend=False, top=0.8)


@register
def software_gains_same_gpu():
    q = load(INF)
    m = load(MLP)
    series = []

    def add(label, frame, col, mk, ls, ycol):
        f = frame.copy()
        f["date"] = f.date.map(_date) if "date" in f else f.round_date.map(_date)
        f = f.sort_values("date")
        f["idx"] = f[ycol] / f[ycol].iloc[0]
        series.append((label, f, col, mk, ls))
    lat = q[q.notes.str.contains("series=trtllm-blog-dsr1-latency", na=False)]
    add("B200 · DeepSeek-R1 min-latency, tok/s per user (TRT-LLM blog)", lat, NV_DARK, "o", "-", "interactivity_tok_s_per_user")
    thr = q[q.notes.str.contains("series=trtllm-blog-dsr1-throughput", na=False)]
    add("B200 · DeepSeek-R1 max throughput, tok/s per GPU (TRT-LLM blog)", thr, NV, "s", "-", "throughput_tok_s_per_gpu")
    ds = q[(q.benchmark_suite.str.startswith("NVIDIA TensorRT-LLM perf overview")) & (q.system == "B200") & q.model.str.startswith("DeepSeek")]
    add("B200 · DeepSeek-R1 1k/1k, tok/s per GPU (TRT-LLM perf overview)", ds, NV, "^", "--", "throughput_tok_s_per_gpu")
    ll = q[(q.benchmark_suite.str.startswith("NVIDIA TensorRT-LLM perf overview")) & (q.system == "B200") & q.model.str.startswith("Llama")]
    add("B200 · Llama 3.3 70B FP4, tok/s per GPU (TRT-LLM perf overview)", ll, GEN_PAST, "D", ":", "throughput_tok_s_per_gpu")
    gb = m[m.notes.str.startswith("series=same-hardware") & (m.accelerator == "NVIDIA GB300") & (m.benchmark == "DeepSeek-R1") &
           (m.scenario == "Server")].copy()
    gb["date"] = gb.round_date
    add("GB300 NVL72 · DeepSeek-R1 Server, tok/s per GPU (MLPerf)", gb, NV_DARK, "*", "--", "per_accelerator_value")
    l0 = series[0][1]
    t0 = series[1][1]
    llx = series[3][1]
    c = Chart(
        id="11-software-gains-same-gpu",
        title=(f"Same B200, new software: DeepSeek-R1 speed up {l0.idx.iloc[-1]:.1f}x in four months; dense Llama 70B flat"),
        subtitle="NVIDIA-published per-GPU performance on unchanged hardware across software releases, indexed to first point = 1.0",
        alt=(f"Line chart of NVIDIA-published performance on the same GPUs over time. B200 DeepSeek-R1 minimum-latency speed rose from "
             f"{l0.interactivity_tok_s_per_user.iloc[0]:.0f} to {l0.interactivity_tok_s_per_user.iloc[-1]:.0f} tokens/s per user "
             f"({l0.idx.iloc[-1]:.1f}x, Jan-May 2025); B200 DeepSeek-R1 max throughput from {t0.throughput_tok_s_per_gpu.iloc[0]:,.0f} "
             f"to {t0.throughput_tok_s_per_gpu.iloc[-1]:,.0f} tokens/s per GPU ({t0.idx.iloc[-1]:.1f}x); GB300 NVL72 MLPerf DeepSeek-R1 "
             f"Server {series[4][1].idx.iloc[-1]:.1f}x in a year; while B200 Llama 3.3 70B max throughput stayed within "
             f"{(llx.idx.max() - llx.idx.min()) * 100:.0f}% across four TensorRT-LLM releases. MoE models gain most from software."),
        data=[INF, MLP], chapters=["11", "09", "10", "01"],
        source="NVIDIA TensorRT-LLM docs and blogs; MLCommons", source_ids=_ids(lat, thr, ds, ll, gb),
    )
    fig, ax = c.figure(width=11, height=6.2)
    for lab, f, col, mk, ls in series:
        ax.plot(f.date, f.idx, color=col, marker=mk, ls=ls, lw=2, markersize=8 if mk != "*" else 13, label=lab)
        ax.annotate(f"{f.idx.iloc[-1]:.1f}x", (f.date.iloc[-1], f.idx.iloc[-1]), xytext=(7, 0), textcoords="offset points",
                    va="center", fontsize=9.5, color=col, fontweight="bold")
    ax.axhline(1, color=INK["base"], lw=0.8)
    ax.set_ylim(0, 6.2)
    ax.legend(loc="upper right", fontsize=8.6, frameon=False)
    c.save(fig, ax, xlabel="Software release / measurement date", ylabel="Performance, first point = 1.0", legend=False)


@register
def inferencex_same_hardware_history():
    q = load(INF)
    h = q[q.benchmark_suite == "SemiAnalysis InferenceX (history, same hardware and config)"].copy()
    h["series"] = h.notes.str.extract(r"series=([^:;]+)")
    h["date"] = h.date.map(_date)
    keep = [("b200-sglang-fp4-conc128-tp4", "B200 · SGLang FP4 (conc 128)", NV, "o", "-"),
            ("b200-trt-fp4-conc256-tp4", "B200 · TensorRT-LLM FP4 (conc 256)", NV, "s", "--"),
            ("h200-sglang-fp8-conc64-tp8", "H200 · SGLang FP8 (conc 64)", GEN_PAST, "D", "-"),
            ("mi355x-sglang-fp4-conc64-tp8", "MI355X · SGLang FP4 (conc 64)", AMD, "o", "-"),
            ("mi300x-sglang-fp8-conc64-tp8", "MI300X · SGLang FP8 (conc 64)", AMD_LIGHT, "s", "--")]
    out = {}
    for key, lab, *_ in keep:
        s = h[h.series == key].sort_values("date")
        out[key] = s
    g = {k: (v.throughput_tok_s_per_gpu.iloc[-1] / v.throughput_tok_s_per_gpu.iloc[0]) for k, v in out.items() if len(v)}
    c = Chart(
        id="11-inferencex-same-hardware-history",
        title=(f"Software alone: B200 DeepSeek-R1 throughput {(g['b200-sglang-fp4-conc128-tp4'] - 1) * 100:+.0f}% and MI355X "
               f"{(g['mi355x-sglang-fp4-conc64-tp8'] - 1) * 100:+.0f}% in six months"),
        subtitle="InferenceX, DeepSeek-R1-0528 1k/1k, same GPU, engine, concurrency and parallelism; total tokens/s per GPU, first run = 1.0",
        alt=("Line chart of InferenceX nightly runs with unchanged hardware and settings, Dec 2025 to Jun 2026. "
             + "; ".join(f"{lab} {(g[k] - 1) * 100:+.0f}%" for k, lab, *_ in keep if k in g) +
             ". Open-source engine updates (SGLang, TensorRT-LLM, ROCm/AITER) deliver double-digit gains on fixed silicon for both "
             "vendors, while older CDNA 3 parts saw regressions before recovering."),
        data=[INF], chapters=["11", "09", "15"],
        source="SemiAnalysis InferenceX public-API history snapshot", source_ids=_ids(h),
    )
    fig, ax = c.figure(width=11, height=6.0)
    for key, lab, col, mk, ls in keep:
        s = out[key]
        if s.empty:
            continue
        idx = s.throughput_tok_s_per_gpu / s.throughput_tok_s_per_gpu.iloc[0]
        ax.plot(s.date, idx, color=col, marker=mk, ls=ls, lw=2, markersize=7, label=lab)
        ax.annotate(f"{(idx.iloc[-1] - 1) * 100:+.0f}%", (s.date.iloc[-1], idx.iloc[-1]), xytext=(7, 0), textcoords="offset points",
                    va="center", fontsize=9, color=col, fontweight="bold")
    ax.axhline(1, color=INK["base"], lw=0.8)
    ax.set_ylim(0.7, 1.5)
    ax.set_xlim(pd.Timestamp("2025-12-01"), pd.Timestamp("2026-07-10"))
    axis_break(ax)  # QA 2026-11-05: index axis starts at 0.7, so mark the break (STYLE_GUIDE §6.7)
    ax.legend(loc="upper left", fontsize=8.8, frameon=False, ncol=2)
    c.save(fig, ax, xlabel="Nightly run date", ylabel="Throughput per GPU, first run = 1.0 (axis starts at 0.7)",
           legend=False)
