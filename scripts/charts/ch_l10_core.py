"""Layer 10 (Libraries, CUDA-X) - CORE charts: cumulative library launches by domain, NCCL all-reduce
models (ring vs in-network reduction, ring vs tree latency), NCCL release cadence, published library
speedups and the AWS Spark TPC-DS-derived cost/time benchmark.

Data: data/l10_library_timeline.csv, data/l10_library_speedups.csv, data/l10_spark_benchmark.csv,
data/l10_nccl_model.csv, data/l10_nccl_releases.csv (owned by the layer-10 CORE author; documented in
data/README.md) and data/interconnect_specs.csv (shared, read-only).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, Chart, load, register, sources_of

CH = ["10"]
TIMELINE = "l10_library_timeline.csv"
SPEEDUPS = "l10_library_speedups.csv"
SPARK = "l10_spark_benchmark.csv"
NCCL_MODEL = "l10_nccl_model.csv"
NCCL_REL = "l10_nccl_releases.csv"
IC = "interconnect_specs.csv"

GROUP_ORDER = [
    "Math and kernels",
    "Communication",
    "AI training and inference",
    "Data, optimization and search",
    "Simulation, science and quantum",
]
GROUP_COLORS = {
    "Math and kernels": "#104281",
    "Communication": "#3987E5",
    "AI training and inference": NV,
    "Data, optimization and search": "#86B6EF",
    "Simulation, science and quantum": "#C98500",
}


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


# --------------------------------------------------------------------------------------
# 1. Cumulative CUDA-X library launches by domain (sample of major libraries)
# --------------------------------------------------------------------------------------
@register
def l10_library_timeline():
    df = load(TIMELINE)
    libs = df[df.kind == "library"].copy()
    integ = df[df.kind == "integration"].copy()
    years = list(range(2007, 2027))
    n_lib = len(libs)
    pre2018 = int((libs.year < 2018).sum())
    since = libs[libs.year >= 2018]
    beyond_ai_new = int(since.domain_group.isin(["Data, optimization and search",
                                                  "Simulation, science and quantum"]).sum())
    c = Chart(
        id="10-cuda-x-library-timeline",
        title=(f"{len(since)} of {n_lib} major CUDA-X libraries arrived since 2018; "
               f"{beyond_ai_new} serve data, science or quantum"),
        subtitle=("Cumulative count of a dated sample of major NVIDIA libraries, by domain; "
                  "diamonds = zero-code-change framework integrations"),
        alt=(f"Stacked step chart of a sample of {n_lib} major CUDA-X libraries by first public release year. "
             f"{pre2018} appeared from 2007 to 2017 (cuBLAS, cuFFT, cuSPARSE, cuRAND, cuDNN, NCCL, TensorRT, CUTLASS "
             f"and others) and {len(since)} from 2018 to 2025, of which {beyond_ai_new} target data analytics, "
             "optimization, vector search, simulation, lithography, climate or quantum rather than AI models. "
             f"{len(integ)} zero-code-change integrations (Spark, pandas, Polars, scikit-learn, Faiss) arrived "
             "from 2020 to 2025. NVIDIA itself cites hundreds of libraries; this is a dated sample."),
        data=[TIMELINE],
        chapters=CH + ["09", "01"],
        source="changelogs, PyPI, CUDA archive, press",
        source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    ax.set_axisbelow(True)
    bottom = np.zeros(len(years))
    for g in GROUP_ORDER:
        sub = libs[libs.domain_group == g]
        cum = np.array([(sub.year <= y).sum() for y in years], dtype=float)
        ax.bar(years, cum, bottom=bottom, color=GROUP_COLORS[g], width=0.8, label=g,
               edgecolor="white", linewidth=0.6)
        bottom += cum
    total = bottom
    for y, t in zip(years, total):
        if y in (2010, 2015, 2017, 2020, 2023, 2025):
            ax.annotate(f"{int(t)}", (y, t), xytext=(0, 3), textcoords="offset points", ha="center",
                        fontsize=8.5, color=INK["text"])
    # integrations as diamonds just above the stack
    for _, r in integ.iterrows():
        y = int(r.year)
        h = total[years.index(y)]
        ax.plot([y], [h + 2.2], marker="D", color=NV_DARK, markersize=7, zorder=5)
    labels = {"cuDF plugin for Apache Spark": "Spark", "cudf.pandas": "pandas", "Polars GPU engine": "Polars",
              "cuml.accel": "sklearn", "Faiss cuVS backend": "Faiss"}
    offs = {}
    for _, r in integ.iterrows():
        y = int(r.year)
        k = offs.get(y, 0)
        offs[y] = k + 1
        h = total[years.index(y)]
        ax.annotate(labels.get(r.library, r.library), (y, h + 2.2), xytext=(0, 7 + 10 * k),
                    textcoords="offset points", ha="center", fontsize=8, color=NV_DARK)
    ax.axvline(2017.5, color=INK["base"], lw=1, ls="--")
    ax.text(2017.6, total.max() * 0.98, "RAPIDS era begins (2018)", fontsize=8.5, color=INK["muted"], va="top")
    ax.set_xticks(years[::2])
    ax.set_xlim(2006.3, 2026.7)
    ax.set_ylim(0, total.max() + 9)
    handles = [Patch(color=GROUP_COLORS[g], label=g) for g in GROUP_ORDER]
    handles.append(plt_line_handle())
    ax.legend(handles=handles, loc="upper left", fontsize=8.5)
    c.save(fig, ax, xlabel="Year of first public release", ylabel="Libraries in sample (cumulative)", legend=False)


def plt_line_handle():
    from matplotlib.lines import Line2D
    return Line2D([0], [0], marker="D", color="white", markerfacecolor=NV_DARK, markersize=7,
                  label="Framework integration (zero code change)")


# --------------------------------------------------------------------------------------
# 2. 70B gradient all-reduce: ring vs in-network reduction, by fabric
# --------------------------------------------------------------------------------------
def _per_dir_gbs(ic: pd.DataFrame, family: str, generation: str) -> float:
    row = ic[(ic.family == family) & (ic.generation == generation)].iloc[0]
    return float(row.per_device_bw_gbs_bidir) / 2.0


@register
def l10_nccl_allreduce_70b():
    m = load(NCCL_MODEL)
    ic = load(IC)
    sc = m[m.record_type == "scenario"]
    params = float(sc[sc["item"] == "model_params"].value.iloc[0]) * 1e9
    bpp = float(sc[sc["item"] == "bytes_per_param"].value.iloc[0])
    size_gb = params * bpp / 1e9
    ngpu = {r.fabric: int(r.value) for r in sc[sc["item"] == "n_gpus"].itertuples()}
    cases = [  # label, family, generation in interconnect_specs, key in l10_nccl_model, in-network name
        ("InfiniBand NDR 400G NIC (64 GPUs)", "InfiniBand", "NDR", "NDR", "SHARP"),
        ("InfiniBand XDR 800G NIC (64 GPUs)", "InfiniBand", "XDR", "XDR", "SHARP"),
        ("NVLink 4, HGX H100 (8 GPUs)", "NVLink", "NVLink 4 (HGX H100 NVL8)", "NVLink 4 (HGX H100 NVL8)", "NVLS"),
        ("NVLink 5, GB200 NVL72 (72 GPUs)", "NVLink", "NVLink 5 (GB200 NVL72)", "NVLink 5 (GB200 NVL72)", "NVLS"),
        ("NVLink 6, Vera Rubin NVL72 (72 GPUs)", "NVLink", "NVLink 6 (Vera Rubin NVL72)",
         "NVLink 6 (Vera Rubin NVL72)", "NVLS"),
    ]
    rows = []
    for lab, fam, gen, key, innet in cases:
        bw = _per_dir_gbs(ic, fam, gen)
        n = ngpu[key]
        ring = 2 * (n - 1) / n * size_gb / bw
        sharp = size_gb / bw
        rows.append(dict(label=lab, bw=bw, n=n, ring=ring, innet=sharp, kind=innet))
    d = pd.DataFrame(rows)
    nvl5 = d.iloc[3]
    xdr = d.iloc[1]
    ic_src = ic[ic.generation.isin([c[2] for c in cases])]
    c = Chart(
        id="10-nccl-allreduce-70b-ring-vs-innetwork",
        title=(f"In-switch reduction halves a 70B gradient all-reduce: {nvl5.ring:.2f} to {nvl5.innet:.2f} s "
               "on GB200 NVL72"),
        subtitle=(f"Ideal time to all-reduce {size_gb:.0f} GB of BF16 gradients: ring vs SHARP (InfiniBand) "
                  "or NVLS (NVLink)"),
        alt=(f"Grouped horizontal bar chart of the ideal time to all-reduce 140 GB of BF16 gradients. Ring vs "
             f"in-network reduction: 400G InfiniBand {d.iloc[0].ring:.1f} s vs {d.iloc[0].innet:.1f} s; 800G "
             f"InfiniBand {xdr.ring:.1f} s vs {xdr.innet:.1f} s; NVLink 4 on 8 H100s {d.iloc[2].ring:.2f} s vs "
             f"{d.iloc[2].innet:.2f} s; NVLink 5 on GB200 NVL72 {nvl5.ring:.2f} s vs {nvl5.innet:.2f} s; NVLink 6 "
             f"on Vera Rubin NVL72 {d.iloc[4].ring:.2f} s vs {d.iloc[4].innet:.2f} s. Switch-side adds cut the "
             "data each GPU sends from about 2x to 1x the gradient, so in-network reduction is up to ~2x faster."),
        data=[NCCL_MODEL, IC],
        chapters=CH + ["06", "05", "P4"],
        source="link specs + ring/SHARP formulas",
        source_ids=sources_of(sc) + [s for s in sources_of(ic_src) if s not in sources_of(sc)],
        note="Ideal times; real runs are slower",
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    y = np.arange(len(d))[::-1]
    h = 0.38
    b1 = ax.barh(y + h / 2, d.ring, height=h, color=GEN_PAST, label="Ring all-reduce (~2x gradient sent per GPU)")
    b2 = ax.barh(y - h / 2, d.innet, height=h, color=NV, label="In-network reduction: SHARP / NVLS (1x)")
    for bars, vals in ((b1, d.ring), (b2, d.innet)):
        for b, v in zip(bars, vals):
            ax.annotate(f"{v:.2f} s" if v < 1 else f"{v:.1f} s", (v, b.get_y() + b.get_height() / 2),
                        xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.5, color=INK["text"])
    ax.set_yticks(y)
    ax.set_yticklabels(d.label)
    ax.set_xscale("log")
    ax.set_xlim(0.05, 12)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8.5)
    _left_margin(fig, 0.30)
    c.save(fig, ax, xlabel="Seconds per all-reduce", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 3. Ring vs tree latency term as the job grows (NCCL default tuning constants)
# --------------------------------------------------------------------------------------
@register
def l10_nccl_latency_ring_vs_tree():
    m = load(NCCL_MODEL)
    k = m[m.record_type == "latency_constant"]

    def val(item, fabric, algo, proto):
        r = k[(k["item"] == item) & (k.fabric == fabric) & (k.algorithm == algo) & (k.protocol == proto)]
        return float(r.value.iloc[0])
    nodes = np.array([2 ** i for i in range(1, 15)], dtype=float)  # 2 .. 16,384
    ring_ll = val("base_latency", "any", "Ring", "LL") + 2 * (nodes - 1) * val("hw_latency_per_step", "Network", "Ring", "LL")
    ring_s = val("base_latency", "any", "Ring", "Simple") + 2 * (nodes - 1) * val("hw_latency_per_step", "Network", "Ring", "Simple")
    tree_ll = val("base_latency", "any", "Tree", "LL") + 2 * np.log2(nodes) * val("hw_latency_per_step", "Network", "Tree", "LL")
    tree_s = val("base_latency", "any", "Tree", "Simple") + 2 * np.log2(nodes) * val("hw_latency_per_step", "Network", "Tree", "Simple")
    nvls = val("hw_latency_per_step", "NVLink", "NVLS", "Simple")
    i2k = list(nodes).index(2048)
    c = Chart(
        id="10-nccl-latency-ring-vs-tree",
        title=(f"Ring latency grows with every node: ~{ring_ll[i2k] / 1000:.0f} ms at 2,048 nodes vs "
               f"~{tree_ll[i2k] / 1000:.2f} ms for a tree"),
        subtitle=("Latency term of one all-reduce across N nodes, from NCCL's default tuner constants "
                  "(no bandwidth term)"),
        alt=(f"Log-log line chart of the latency term of an all-reduce versus number of nodes, built from NCCL's "
             f"default tuner constants. A ring pays 2(N-1) network hops: about {ring_ll[i2k] / 1000:.0f} ms at "
             f"2,048 nodes with the low-latency LL protocol and {ring_s[i2k] / 1000:.0f} ms with the Simple protocol. "
             f"A tree pays 2 log2(N) hops: about {tree_ll[i2k]:.0f} microseconds (LL) and {tree_s[i2k]:.0f} "
             f"microseconds (Simple). Inside one NVLink domain, NVLink SHARP has a flat ~{nvls:.0f} microsecond term. "
             "This is why NCCL switches algorithms by message size and scale."),
        data=[NCCL_MODEL],
        chapters=CH + ["06", "P4"],
        source="NCCL source, default tuner constants",
        source_ids=sources_of(k),
        note="Simplified: one GPU per node",
    )
    fig, ax = c.figure(width=10.0, height=5.8)
    x = np.log2(nodes)
    ax.plot(x, ring_s, color=GEN_PAST, lw=2, ls="--", label="Ring, Simple protocol")
    ax.plot(x, ring_ll, color=NV_DARK, lw=2, marker="o", markersize=5, label="Ring, LL protocol")
    ax.plot(x, tree_s, color=SEQ_BLUE[3], lw=2, ls="--", label="Tree, Simple protocol")
    ax.plot(x, tree_ll, color=SEQ_BLUE[6], lw=2, marker="s", markersize=5, label="Tree, LL protocol")
    ax.axhline(nvls, color=INK["muted"], lw=1.2, ls=":")
    ax.text(14, nvls * 0.62, f"NVLink SHARP inside one NVLink domain: ~{nvls:.0f} µs, flat", fontsize=8.5,
            color=INK["muted"], ha="right")
    ax.annotate(f"~{ring_ll[i2k] / 1000:.0f} ms", (11, ring_ll[i2k]), xytext=(8, -12), textcoords="offset points",
                fontsize=9, color=NV_DARK, fontweight="bold")
    ax.annotate(f"~{tree_ll[i2k]:.0f} µs", (11, tree_ll[i2k]), xytext=(8, 8), textcoords="offset points",
                fontsize=9, color=SEQ_BLUE[6], fontweight="bold")
    ticks = [1, 3, 5, 7, 9, 11, 13]
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{2 ** t:,}" for t in ticks])
    ax.set_xlim(0.7, 14.3)
    ax.grid(axis="x", visible=False)
    ax.legend(loc="upper left", fontsize=8.5)
    c.save(fig, ax, xlabel="Nodes in the all-reduce (log scale)", ylabel="Latency term, µs", logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 4. NCCL release cadence (PyPI) with feature milestones
# --------------------------------------------------------------------------------------
@register
def l10_nccl_release_cadence():
    r = load(NCCL_REL)
    r["date"] = pd.to_datetime(r.first_pypi_upload)
    first, last = r.iloc[0], r.iloc[-1]
    months = (last.date.year - first.date.year) * 12 + (last.date.month - first.date.month)
    steps = int(last.minor - first.minor)
    c = Chart(
        id="10-nccl-release-cadence",
        title=(f"NCCL shipped {steps} minor versions in {months} months, from {first.version} "
               f"({first.date:%b %Y}) to {last.version} ({last.date:%b %Y})"),
        subtitle="NCCL minor version by first PyPI wheel upload (any CUDA variant), with selected feature milestones",
        alt=(f"Step chart of NCCL minor versions over time from PyPI release history: {first.version} in "
             f"{first.date:%B %Y} to {last.version} in {last.date:%B %Y}, {steps} minor versions in {months} "
             f"months or one every ~{months / steps:.1f} months. Milestones: NVLink SHARP buffer registration in "
             "2.19 (Oct 2023), PAT scaling algorithm in 2.23 (Sep 2024), symmetric-memory low-latency kernels in "
             "2.27 (Jun 2025) and the device API with GPU-initiated networking in 2.28 (Sep 2025)."),
        data=[NCCL_REL],
        chapters=CH + ["09", "06"],
        source="PyPI nvidia-nccl wheels; NCCL docs",
        source_ids=sources_of(r),
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    ax.step(r.date, r.minor, where="post", color=NV, lw=2.2)
    ax.plot(r.date, r.minor, "o", color=NV_DARK, markersize=5)
    feats = r[r.feature.notna() & (r.feature != "")]
    place = {"2.19": (-20, 40, "right"), "2.23": (25, -40, "left"), "2.27": (-25, 40, "right"),
             "2.28": (-12, 80, "right"), "2.32": (-30, 30, "right")}
    for _, fr in feats.iterrows():
        dx, dy, ha = place.get(str(fr.version), (10, 20, "left"))
        ax.annotate(f"{fr.version}: {fr.feature}", (fr.date, fr.minor), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8.5, color=INK["text"], ha=ha,
                    arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.8))
    ax.set_ylim(11, 35)
    ax.set_yticks(range(12, 35, 4))
    ax.set_yticklabels([f"2.{v}" for v in range(12, 35, 4)])
    c.save(fig, ax, xlabel="First PyPI upload", ylabel="NCCL version (2.x)", legend=False)


# --------------------------------------------------------------------------------------
# 5. Published GPU speedups by library domain (vendor vs independent evidence)
# --------------------------------------------------------------------------------------
@register
def l10_published_speedups():
    s = load(SPEEDUPS)
    s = s[s.metric == "runtime"].copy()
    vendor_types = {"vendor", "vendor-partner"}
    s["is_vendor"] = s.evidence_type.isin(vendor_types)
    s = s.sort_values("speedup_x")
    vmax = s[s.is_vendor].speedup_x.max()
    imax = s[~s.is_vendor].speedup_x.max()
    vmin = s.speedup_x.min()
    c = Chart(
        id="10-published-library-speedups",
        title=(f"Published GPU-library speedups run from {vmin:.2g}x to {vmax:.0f}x; "
               f"the top non-NVIDIA test is {imax:.0f}x"),
        subtitle="Runtime speedup vs the stated CPU (or older GPU) baseline, as published; each test uses its own data and hardware",
        alt=("Horizontal log-scale bar chart of published runtime speedups for CUDA-X libraries, colored by who ran the "
             "test. NVIDIA or NVIDIA-partner figures: cudf.pandas about 150x, cuLitho 45x, Polars GPU engine up to 13x, "
             "cuml.accel 5.8x median and 0.48x (slower) for a low-rank PCA. Third-party, customer or peer-reviewed "
             "figures: Parabricks germline calling up to 65x (BMC Bioinformatics) and 24x (Terra), an independent "
             "cudf.pandas re-test ~60x, FINRA Spark 14x, cuVS CAGRA index build 12.3x vs CPU HNSW (Meta), cuVS IVF "
             "4.7x vs older GPU code, and an AWS Spark TPC-DS-derived run at 1.06x vs native Spark and 0.63x vs Velox."),
        data=[SPEEDUPS],
        chapters=CH + ["15", "01"],
        source="vendor, customer and third-party tests",
        source_ids=sources_of(s),
        note="Not like-for-like",
    )
    fig, ax = c.figure(width=10.8, height=6.4)
    y = np.arange(len(s))
    colors = [GEN_PAST if v else SEQ_BLUE[5] for v in s.is_vendor]
    bars = ax.barh(y, s.speedup_x, color=colors, height=0.65)
    for b, v in zip(bars, s.speedup_x):
        ax.annotate(f"{v:g}x", (v, b.get_y() + b.get_height() / 2), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK["text"])
    ax.axvline(1.0, color=INK["title"], lw=1)
    ax.text(1.05, len(s) - 0.4, "1x = no gain", fontsize=8, color=INK["muted"])
    ax.set_yticks(y)
    ax.set_yticklabels(s.label, fontsize=8.8)
    ax.set_xscale("log")
    ax.set_xlim(0.3, 400)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=GEN_PAST, label="NVIDIA or NVIDIA-partner test"),
                       Patch(color=SEQ_BLUE[5], label="Third-party, customer or peer-reviewed test")],
              loc="lower right", fontsize=8.5)
    _left_margin(fig, 0.36)
    c.save(fig, ax, xlabel="Runtime speedup (x)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 6. Spark TPC-DS-derived benchmark on AWS: time vs cost (small multiples)
# --------------------------------------------------------------------------------------
@register
def l10_spark_time_vs_cost():
    sp = load(SPARK)
    nat = sp.iloc[0]
    gpu = sp.iloc[2]
    saving = 1 - gpu.total_job_cost_usd / nat.total_job_cost_usd
    c = Chart(
        id="10-spark-tpcds-time-vs-cost",
        title=(f"On a 1 TB Spark test, GPUs were barely faster ({gpu.speed_vs_native_x:.2f}x) "
               f"but cut job cost {saving:.0%}"),
        subtitle=("AWS data-on-eks, Jan 2026: TPC-DS-derived 1 TB, 104 queries x 3 runs on Amazon EKS; "
                  "runtime and job cost"),
        alt=(f"Two-panel bar chart from an AWS-run Spark benchmark (TPC-DS-derived, 1 TB). Runtime: native Spark on "
             f"8 c5d.12xlarge CPU nodes {nat.runtime_h} h, Gluten plus Velox vectorized CPU 1.0 h, NVIDIA's cuDF "
             f"plugin on 4 g6.2xlarge nodes with one L4 GPU each {gpu.runtime_h} h. Job cost: ${nat.total_job_cost_usd:.2f}, "
             f"$18.40 and ${gpu.total_job_cost_usd:.2f}. The GPU run was only 1.06x faster than native Spark and "
             "slower than Velox, but about 80% cheaper than native Spark and 66% cheaper than Velox."),
        data=[SPARK],
        chapters=CH + ["14", "15"],
        source="AWS Labs data-on-eks benchmark",
        source_ids=sources_of(sp),
        note="Not an official TPC-DS result",
    )
    fig, axes = c.figure_grid(1, 2, width=10.8, height=5.4)
    labels = ["Native Spark\n8 CPU nodes", "Gluten + Velox\n8 CPU nodes", "cuDF plugin\n4 L4 GPU nodes"]
    colors = ["#B5B5B5", "#7A7A7A", NV]
    for ax, col, ttl, fmt in ((axes[0], "runtime_h", "Runtime (hours)", "{:.1f} h"),
                              (axes[1], "total_job_cost_usd", "Job cost (US$, on-demand)", "${:.2f}")):
        ax.set_axisbelow(True)
        bars = ax.bar(labels, sp[col], color=colors, width=0.6)
        for b, v in zip(bars, sp[col]):
            ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=9, color=INK["text"])
        ax.set_title(ttl, fontsize=10.5, color=INK["text"], loc="left")
        ax.set_ylim(0, sp[col].max() * 1.2)
        ax.tick_params(axis="x", labelsize=8.8)
    axes[0].set_ylabel("Hours for 3 iterations")
    axes[1].set_ylabel("US$ per benchmark run")
    c.save(fig, list(axes), legend=False, top=0.80)
