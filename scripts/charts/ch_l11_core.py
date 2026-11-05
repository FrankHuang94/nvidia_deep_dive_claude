"""Layer 11 (inference and AI software) - CORE charts: what disaggregated serving buys on the same GPUs,
what software releases do to cost per million tokens on unchanged hardware, how much of NVIDIA's Data Center
revenue management has said is inference, and how NVIDIA's Nemotron models went sparse.

Data: data/l11_inference_share.csv and data/l11_nemotron_models.csv (owned by the layer-11 CORE author;
documented in data/README.md) plus shared, read-only data/inference_benchmarks.csv, data/mlperf_results.csv
and data/financials.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

CH = ["11"]
INF = "inference_benchmarks.csv"
MLP = "mlperf_results.csv"
FIN = "financials.csv"
SHARE = "l11_inference_share.csv"
NEMO = "l11_nemotron_models.csv"
GRAY = "#898781"
LIGHT = "#B5B5B5"
AMD = entity_color("AMD")


def _ids(*frames) -> list[str]:
    out: list[str] = []
    for f in frames:
        for sid in sources_of(f):
            if sid not in out:
                out.append(sid)
    return out


def _margins(fig, **over) -> None:
    """Chart.save() fixes the subplot margins; override selected ones for this figure."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _date(s: str) -> pd.Timestamp:
    s = str(s)
    if len(s) == 7:
        s += "-15"
    return pd.Timestamp(s)


def _tco(notes: pd.Series) -> float:
    """InferenceX owner TCO ($/GPU-hr) quoted in the row notes."""
    return float(notes.str.extract(r"TCO \$([\d.]+)/GPU-hr").dropna().iloc[0, 0])


# --------------------------------------------------------------------------------------
# 1. Disaggregated vs aggregated serving on the same B200s (InferenceX frontier points)
# --------------------------------------------------------------------------------------
def disagg_points() -> pd.DataFrame:
    d = load(INF)
    f = d[(d.benchmark_suite == "SemiAnalysis InferenceX (Pareto frontier, no speculative decoding)") &
          (d.system == "B200")].copy()
    f["mode"] = np.where(f.notes.str.contains("; disagg;"), "disaggregated", "aggregated")
    f["engine"] = f.notes.str.extract(r"interactivity = median tok/s/user; ([^;]+);")[0].str.strip()
    return f


@register
def l11_disaggregation_vs_aggregated():
    f = disagg_points()
    long = f[f.model.str.startswith("DeepSeek-R1-0528 (8k")]
    dis = long[long["mode"] == "disaggregated"].sort_values("interactivity_tok_s_per_user").iloc[0]
    agg = long[long["mode"] == "aggregated"].sort_values("interactivity_tok_s_per_user").iloc[0]
    ratio = dis.throughput_tok_s_per_gpu / agg.throughput_tok_s_per_gpu
    short = f[f.model.str.startswith("DeepSeek-R1-0528 (1k")]
    c = Chart(
        id="11-disaggregation-vs-aggregated-b200",
        title=(f"Splitting prefill from decode lifted B200 throughput ~{ratio:.1f}× per GPU with 8k-token prompts"),
        subtitle=("InferenceX frontier points on B200, DeepSeek-R1-0528, FP4, no speculative decoding, by serving mode"),
        alt=(f"Two-panel log-scale scatter of B200 frontier points by serving mode. Left, 8k-token input and 1k output: "
             f"the disaggregated Dynamo plus TensorRT-LLM setup (prefill and decode on separate GPUs, "
             f"{dis.accelerators:.0f} GPUs in total) delivers about {dis.throughput_tok_s_per_gpu:,.0f} tokens/s per GPU at "
             f"{dis.interactivity_tok_s_per_user:.0f} tokens/s per user, versus about {agg.throughput_tok_s_per_gpu:,.0f} for "
             f"the best aggregated 8-GPU TensorRT-LLM setup at {agg.interactivity_tok_s_per_user:.0f}, about {ratio:.1f} times. "
             "Right, 1k input and 1k output: aggregated setups hold the frontier at low interactivity and disaggregation "
             "appears only above about 100 tokens/s per user, so the gain depends on prompt length."),
        data=[INF], chapters=["11", "05", "P2"],
        source="SemiAnalysis InferenceX public-API snapshot (Oct 2026)", source_ids=_ids(f),
        note="Points = best config per mode; label = engine, GPUs",
    )
    fig, axes = c.figure_grid(1, 2, width=12, height=6.2, sharey=True)
    styles = {"disaggregated": (NV_DARK, "o", "Disaggregated (prefill and decode pools; Dynamo)"),
              "aggregated": (GEN_PAST, "s", "Aggregated (prefill and decode on the same GPUs)")}
    panels = [(axes[0], long, "8k in / 1k out: long prompts"), (axes[1], short, "1k in / 1k out: short prompts")]
    for ax, frame, ttl in panels:
        for mode, (col, mk, lab) in styles.items():
            s = frame[frame["mode"] == mode].sort_values("interactivity_tok_s_per_user")
            ax.scatter(s.interactivity_tok_s_per_user, s.throughput_tok_s_per_gpu, color=col, marker=mk, s=70,
                       edgecolor=NV_DARK, linewidth=0.8, zorder=3, label=lab)
            for r in s.itertuples():
                eng = r.engine.replace("dynamo-", "Dynamo+").replace("trt", "TRT-LLM").replace("sglang", "SGLang")
                ax.annotate(f"{eng}, {r.accelerators:.0f} GPUs", (r.interactivity_tok_s_per_user, r.throughput_tok_s_per_gpu),
                            xytext=(6, 4), textcoords="offset points", fontsize=7.6, color=INK["text"])
        ax.set_yscale("log")
        ax.set_xlim(0, 215)
        ax.set_ylim(25, 40000)
        ax.set_title(ttl, fontsize=10.5, loc="left", color=INK["title"])
        ax.grid(axis="y", color=INK["grid"])
        ax.set_axisbelow(True)
        ax.set_xlabel("Interactivity: tokens/s per user (median)")
    a0 = axes[0]
    a0.annotate("", xy=(dis.interactivity_tok_s_per_user, dis.throughput_tok_s_per_gpu),
                xytext=(agg.interactivity_tok_s_per_user, agg.throughput_tok_s_per_gpu),
                arrowprops=dict(arrowstyle="->", color=NV_DARK, lw=1.4))
    a0.text(agg.interactivity_tok_s_per_user + 6, (dis.throughput_tok_s_per_gpu * agg.throughput_tok_s_per_gpu) ** 0.5,
            f"~{ratio:.1f}×", fontsize=11, fontweight="bold", color=NV_DARK)
    handles = [Line2D([], [], marker=m, ls="", color=col, markeredgecolor=NV_DARK, markersize=8, label=lab)
               for col, m, lab in styles.values()]
    axes[1].legend(handles=handles, loc="upper right", fontsize=8.6, frameon=False)
    _margins(fig, wspace=0.08, left=0.08, right=0.98)
    c.save(fig, list(axes), ylabel="Throughput: total tokens/s per GPU (log scale)", logy=True, legend=False, top=0.82)


# --------------------------------------------------------------------------------------
# 2. Cost per million tokens across software releases on unchanged hardware
# --------------------------------------------------------------------------------------
def software_cost_series() -> tuple[pd.DataFrame, list[str]]:
    """Est. $/M tokens = owner TCO $/GPU-hr x 1e6 / (tokens/s per GPU x 3,600), TCO held fixed per GPU."""
    m = load(MLP)
    d = load(INF)
    tco = {"GB300": 2.31, "GB200": 1.86, "B200": 1.73, "H100": 1.17}  # S622 (InferenceX registry, Jul 2026)
    rows = []
    sh = m[m.notes.astype(str).str.startswith("series=same-hardware") & (m.scenario == "Server")]
    for acc, bench, label in [("NVIDIA GB300", "DeepSeek-R1", "GB300 NVL72 · DeepSeek-R1 (MLPerf Server)"),
                              ("NVIDIA GB200", "DeepSeek-R1", "GB200 NVL72 · DeepSeek-R1 (MLPerf Server)"),
                              ("NVIDIA H100", "Llama 2 70B (99.9% accuracy)", "H100 · Llama 2 70B (MLPerf Server)")]:
        s = sh[(sh.accelerator == acc) & (sh.benchmark == bench)].sort_values("round_date")
        for r in s.itertuples():
            rows.append((label, _date(r.round_date), r.round, r.per_accelerator_value, tco[acc.split()[-1]], r.source_id))
    blog = d[d.benchmark_suite == "NVIDIA TensorRT-LLM tech blog (DeepSeek-R1 on Blackwell)"].sort_values("date")
    for r in blog.itertuples():
        rows.append(("B200 · DeepSeek-R1 max throughput (TensorRT-LLM blog)", _date(r.date), "TRT-LLM",
                     r.throughput_tok_s_per_gpu, tco["B200"], r.source_id))
    hist = d[(d.benchmark_suite == "SemiAnalysis InferenceX (history, same hardware and config)") &
             d.notes.str.contains("series=b200-sglang-fp4-conc128")].sort_values("date")
    for r in hist.itertuples():
        rows.append(("B200 · DeepSeek-R1, SGLang conc 128 (InferenceX)", _date(r.date), "nightly",
                     r.throughput_tok_s_per_gpu, tco["B200"], r.source_id))
    out = pd.DataFrame(rows, columns=["series", "date", "release", "tps", "tco", "source_id"])
    out["usd_per_m"] = out.tco * 1e6 / (out.tps * 3600)
    ids = _ids(out) + ["S622"]
    return out, list(dict.fromkeys(ids))


@register
def l11_cost_per_m_tokens_software():
    s, ids = software_cost_series()
    g = s[s.series.str.startswith("GB300")].sort_values("date")
    cut = 1 - g.usd_per_m.iloc[-1] / g.usd_per_m.iloc[0]
    summary = []
    for name, grp in s.groupby("series", sort=False):
        grp = grp.sort_values("date")
        summary.append((name, grp.usd_per_m.iloc[0], grp.usd_per_m.iloc[-1], 1 - grp.usd_per_m.iloc[-1] / grp.usd_per_m.iloc[0],
                        grp.date.iloc[0], grp.date.iloc[-1]))
    c = Chart(
        id="11-cost-per-m-tokens-software-releases",
        title=(f"Software alone cut GB300 NVL72's estimated cost per million tokens {cut:.0%} in a year"),
        subtitle=("Est. US$/M tokens = fixed owner TCO ÷ measured tokens/s per GPU on unchanged hardware; compare slopes, not levels"),
        alt=("Log-scale line chart of estimated cost per million tokens on unchanged NVIDIA hardware as software improved, "
             "holding each GPU's owner TCO fixed (SemiAnalysis: GB300 $2.31, GB200 $1.86, B200 $1.73, H100 $1.17 per GPU-hour). "
             + "; ".join(f"{n}: ${a:.3f} to ${b:.3f} ({x:.0%} lower, {d0:%b %Y} to {d1:%b %Y})" for n, a, b, x, d0, d1 in summary)
             + ". The hardware bill did not change; throughput per GPU did, so cost per token fell."),
        data=[MLP, INF], chapters=["11", "14", "09"],
        source="MLPerf Inference; TensorRT-LLM blog; InferenceX + TCO; repo math",
        source_ids=ids,
    )
    fig, ax = c.figure(width=11, height=6.4)
    style = {"GB300": (NV_DARK, "o", "-"), "GB200": (NV, "s", "-"), "B200 · DeepSeek-R1 max": (NV, "^", "--"),
             "B200 · DeepSeek-R1, SGLang": (GEN_PAST, "v", ":"), "H100": (GRAY, "D", "-")}
    for name, grp in s.groupby("series", sort=False):
        grp = grp.sort_values("date")
        col, mk, ls = next(v for k, v in style.items() if name.startswith(k))
        ax.plot(grp.date, grp.usd_per_m, color=col, marker=mk, ls=ls, lw=2, markersize=7, label=name)
        last = grp.iloc[-1]
        x = 1 - last.usd_per_m / grp.usd_per_m.iloc[0]
        ax.annotate(f"−{x:.0%}", (last.date, last.usd_per_m), xytext=(7, -2), textcoords="offset points",
                    fontsize=9, fontweight="bold", color=col if col != GEN_PAST else NV_DARK, va="center")
    ax.set_yscale("log")
    ax.set_ylim(0.05, 0.4)
    ax.set_yticks([0.05, 0.075, 0.1, 0.15, 0.2, 0.3, 0.4])
    ax.set_xlim(pd.Timestamp("2024-02-01"), pd.Timestamp("2026-12-31"))
    ax.grid(axis="y", color=INK["grid"])
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=8.4, frameon=False)
    c.save(fig, ax, xlabel="Software release / benchmark round date", ylabel="Est. US$ per million tokens (log scale)",
           logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 3. Inference share of Data Center revenue: the last quantified management estimates
# --------------------------------------------------------------------------------------
def dc_ttm() -> pd.DataFrame:
    f = load(FIN)
    q = f[(f.metric == "revenue_data_center") & (f.period_type == "Q")].copy()
    q["end"] = pd.to_datetime(q.period_end)
    q = q.sort_values("end").drop_duplicates("period")
    q["ttm"] = q.value.rolling(4).sum()
    return q


@register
def l11_inference_share_of_dc_revenue():
    q = dc_ttm()
    sh = load(SHARE)
    ttm = q.set_index("period").ttm
    bars = [("TTM to Q4 FY2024\n(= FY2024)", "Q4FY24", True), ("TTM to Q2 FY2025", "Q2FY25", True),
            ("FY2025", "Q4FY25", False), ("FY2026", "Q4FY26", False), ("TTM to Q2 FY2027", "Q2FY27", False)]
    rows = []
    for label, per, disclosed in bars:
        total = float(ttm[per])
        share = None
        if disclosed:
            r = sh[sh.window.str.startswith("TTM to " + per)].iloc[0]
            share = float(r.value)
        rows.append((label, per, total, share))
    r = pd.DataFrame(rows, columns=["label", "period", "total", "share"])
    inf2 = r.iloc[1].total * r.iloc[1].share / 100
    inf1 = r.iloc[0].total * r.iloc[0].share / 100
    last = r.iloc[-1].total
    fin = load(FIN)
    fin_ids = sources_of(fin[(fin.metric == "revenue_data_center") & fin.period.isin(
        ["Q1FY24", "Q2FY24", "Q3FY24", "Q4FY24", "Q1FY25", "Q2FY25", "Q3FY25", "Q4FY25", "Q1FY26", "Q2FY26", "Q3FY26",
         "Q4FY26", "Q1FY27", "Q2FY27"])])
    c = Chart(
        id="11-inference-share-of-dc-revenue",
        title=(f"NVIDIA last sized inference at >40% of Data Center revenue in mid-2024: ≥${inf2:.0f}B a year"),
        subtitle=("Trailing-four-quarter Data Center revenue, US$ B; hatched = inference at management's estimate; "
                  "dotted = 40% for scale only"),
        alt=(f"Bar chart of trailing-twelve-month NVIDIA Data Center revenue. To Q4 FY2024 ${r.iloc[0].total:.1f}B, of which "
             f"about 40% (~${inf1:.0f}B) was inference by management's estimate; to Q2 FY2025 ${r.iloc[1].total:.1f}B with "
             f"more than 40% (at least ~${inf2:.0f}B) inference. Later bars, FY2025 ${r.iloc[2].total:.1f}B, FY2026 "
             f"${r.iloc[3].total:.1f}B and the year to Q2 FY2027 ${last:.1f}B, have no disclosed split; a dotted marker shows "
             f"what 40% would be (${last * 0.4:.0f}B for the latest year) purely for scale. Management now calls inference "
             "the main growth driver without giving a percentage."),
        data=[SHARE, FIN], chapters=["11", "14", "13"],
        source="NVIDIA earnings calls and results; repo math",
        source_ids=list(dict.fromkeys(_ids(sh) + fin_ids)),
    )
    fig, ax = c.figure(width=11, height=6.2)
    x = np.arange(len(r))
    for i, row in r.iterrows():
        if row.share is not None and not pd.isna(row.share):
            infv = row.total * row.share / 100
            ax.bar(i, row.total, width=0.62, color="#DDE9C8", edgecolor=NV_DARK, linewidth=0.6)
            ax.bar(i, infv, width=0.62, color=NV, edgecolor=NV_DARK, linewidth=0.6, hatch="//", alpha=0.85)
            pre = "~" if i == 0 else "≥"
            ax.text(i, infv / 2, f"inference {pre}${infv:.0f}B", ha="center", va="center", fontsize=8.4, color=NV_DARK,
                    fontweight="bold", bbox=dict(boxstyle="round,pad=0.25", fc="#FFFFFF", ec=NV_DARK, lw=0.6))
            ax.text(i, infv + (row.total - infv) / 2, "training\nand other", ha="center", va="center", fontsize=8.2,
                    color=INK["text"])
        else:
            ax.bar(i, row.total, width=0.62, color=LIGHT, edgecolor=GRAY, linewidth=0.6)
            ax.plot([i - 0.31, i + 0.31], [row.total * 0.4] * 2, ls=":", color=INK["text"], lw=1.6)
            ax.text(i + 0.33, row.total * 0.4, f"40% = ${row.total * 0.4:.0f}B", fontsize=7.8, color=INK["text"], va="center")
            ax.text(i, row.total * 0.70, "split not\ndisclosed", ha="center", va="center", fontsize=8.4, color=INK["text"])
        ax.text(i, row.total + 4, f"${row.total:.1f}B", ha="center", va="bottom", fontsize=9.2, color=INK["title"],
                fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(r.label, fontsize=9)
    ax.set_ylim(0, r.total.max() * 1.14)
    ax.set_xlim(-0.55, len(r) - 0.2)
    ax.grid(axis="y", color=INK["grid"])
    ax.set_axisbelow(True)
    handles = [Patch(facecolor=NV, edgecolor=NV_DARK, hatch="//", label="Inference (management estimate)"),
               Patch(facecolor="#DDE9C8", edgecolor=NV_DARK, label="Training and other (remainder)"),
               Patch(facecolor=LIGHT, edgecolor=GRAY, label="No split disclosed"),
               Line2D([], [], ls=":", color=INK["text"], label="40% for scale only (illustration)")]
    ax.legend(handles=handles, loc="upper left", fontsize=8.6, frameon=False)
    c.save(fig, ax, ylabel="Data Center revenue, trailing four quarters (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 4. Nemotron: total vs active parameters
# --------------------------------------------------------------------------------------
@register
def l11_nemotron_total_vs_active():
    d = load(NEMO)
    d["pct"] = d.active_params_b / d.total_params_b * 100
    sparse = d[d.family != "Nemotron-4"]
    ultra = d[d.model.str.contains("Ultra")].iloc[0]
    c = Chart(
        id="11-nemotron-total-vs-active-parameters",
        title=(f"Nemotron went sparse: new models use ~{sparse.pct.mean():.0f}% of their weights per token, vs 100% in 2024"),
        subtitle="NVIDIA's open Nemotron models: total vs active parameters per token, billions (log scale), in release order",
        alt=("Log-scale paired horizontal bars of total and active parameters for NVIDIA's open Nemotron models: Nemotron-4 340B "
             "(June 2024, dense) 340B total and 340B active; "
             + "; ".join(f"{r.model} ({r.release_date}) {r.total_params_b:g}B total, {r.active_params_b:g}B active ({r.pct:.0f}%)"
                         for r in sparse.itertuples())
             + ". The Nemotron 3 generation uses hybrid Mamba-Transformer mixture-of-experts designs that activate about a tenth "
               "of the weights per token, cutting the memory bandwidth and compute each generated token needs."),
        data=[NEMO], chapters=["11"],
        source="NVIDIA Nemotron repository and reports; press for dates", source_ids=_ids(d),
    )
    fig, ax = c.figure(width=11, height=5.8)
    y = np.arange(len(d))[::-1]
    h = 0.36
    ax.barh(y + h / 2, d.total_params_b, height=h, color="#DDE9C8", edgecolor=NV_DARK, linewidth=0.6, label="Total parameters")
    ax.barh(y - h / 2, d.active_params_b, height=h, color=NV, edgecolor=NV_DARK, linewidth=0.6, label="Active per token")
    for yi, r in zip(y, d.itertuples()):
        ax.text(r.total_params_b * 1.06, yi + h / 2, f"{r.total_params_b:g}B", va="center", fontsize=8.6, color=INK["text"])
        ax.text(r.active_params_b * 1.06, yi - h / 2, f"{r.active_params_b:g}B ({r.pct:.0f}%)", va="center", fontsize=8.6,
                color=NV_DARK, fontweight="bold")
    ax.set_yticks(y)
    def short(a: str) -> str:
        a = a.split(" with")[0].replace("Transformer ", "").replace("Attention ", "").replace("hybrid ", "hybrid ")
        return a.replace("vision-language", "VLM").replace("Mamba-", "Mamba ")
    ax.set_yticklabels([f"{m}\n{dt} · {short(arch)}" for m, dt, arch in zip(d.model, d.release_date, d.architecture)],
                       fontsize=8.4)
    ax.set_xscale("log")
    ax.set_xlim(1, 2000)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.set_axisbelow(True)
    ax.legend(loc="lower right", fontsize=8.8, frameon=False)
    _margins(fig, left=0.29, right=0.97)
    c.save(fig, ax, xlabel="Parameters, billions (log scale)", logx=True, legend=False)
