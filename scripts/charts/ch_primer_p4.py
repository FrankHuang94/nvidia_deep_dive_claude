"""Primer P4 - parallelism explained: all-reduce time by fabric, communication volume by parallelism type,
pipeline bubble fraction, and the parallelism layouts of published frontier training runs.

Data: data/interconnect_specs.csv (shared; falls back to data/P4_fabric_bandwidth.csv), P4_comm_volume_example.csv,
P4_pipeline_bubble.csv, P4_parallelism_configs.csv (documented in data/README.md).
"""
import numpy as np
import pandas as pd
import matplotlib.patches as mpatches
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from style import Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, load, register, sources_of

GRAD_GB = 140.0      # 70B parameters x 2 bytes (BF16 gradients)
RING_N = 64          # GPUs in the ring
SCOPE_COLOR = {"scale-up": NV, "scale-out": SEQ_BLUE[5], "host-io": INK["muted"]}
SCOPE_LABEL = {"scale-up": "scale-up (NVLink, inside the rack)", "scale-out": "scale-out (one NIC per GPU)",
               "host-io": "host I/O (PCIe slot)"}


def _log_badge(fig):
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


def _plain_log_x(ax, fmt="{:g}"):
    ax.xaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 3.0)))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt.format(v)))
    ax.xaxis.set_minor_formatter(NullFormatter())


# (family, generation prefix in interconnect_specs.csv, label fabric, label generation, label product)
FABRIC_PICKS = [
    ("PCIe", "PCIe 5.0", "PCIe", "Gen5 x16", "host link"),
    ("InfiniBand", "NDR", "InfiniBand", "NDR 400 Gb/s", "ConnectX-7"),
    ("InfiniBand", "XDR", "InfiniBand", "XDR 800 Gb/s", "ConnectX-8"),
    ("Ethernet", "1.6TbE", "Ethernet", "1.6 Tb/s", "ConnectX-9"),
    ("NVLink", "NVLink 4 (HGX H100", "NVLink", "NVLink 4", "H100"),
    ("NVLink", "NVLink 5 (GB200", "NVLink", "NVLink 5", "B200"),
    ("NVLink", "NVLink 6 (Vera Rubin", "NVLink", "NVLink 6", "Rubin"),
]


def _fabrics():
    """Per-GPU link bandwidth from the shared interconnect_specs.csv; fall back to this primer's CSV."""
    try:
        ic = load("interconnect_specs.csv")
        rows = []
        for fam, gen, lf, lg, prod in FABRIC_PICKS:
            hit = ic[(ic.family == fam) & ic.generation.astype(str).str.startswith(gen) & ic.per_device_bw_gbs_bidir.notna()]
            if hit.empty:
                raise KeyError(gen)
            r = hit.iloc[0]
            rows.append(dict(fabric=lf, generation=lg, first_product=prod, year=int(r.year), scope=r.scope,
                             per_gpu_bw_gbs_unidir=r.per_device_bw_gbs_bidir / 2, per_gpu_bw_gbs_bidir=r.per_device_bw_gbs_bidir,
                             status="announced" if int(r.year) >= 2026 else "shipping", source_id=r.source_id))
        return pd.DataFrame(rows), "interconnect_specs.csv"
    except (KeyError, FileNotFoundError, AttributeError):
        return load("P4_fabric_bandwidth.csv"), "P4_fabric_bandwidth.csv"


@register
def allreduce_time_by_fabric():
    df, fname = _fabrics()
    vol = 2 * (RING_N - 1) / RING_N * GRAD_GB
    df["seconds"] = vol / df.per_gpu_bw_gbs_unidir
    df = df.sort_values("seconds", ascending=False).reset_index(drop=True)
    ib = df[df.generation.str.startswith("NDR")].iloc[0]
    nv5 = df[df.generation == "NVLink 5"].iloc[0]
    c = Chart(
        id="P4-allreduce-time-by-fabric",
        title=f"A 70B gradient sync takes ~{ib.seconds:.1f} s over 400G InfiniBand but ~{nv5.seconds:.1f} s over NVLink 5",
        subtitle=f"Ideal ring all-reduce of 140 GB of BF16 gradients across {RING_N} GPUs ({vol:.0f} GB sent per GPU), "
                 "by per-GPU link; seconds",
        alt=(f"Horizontal bar chart of ideal ring all-reduce time for 140 GB of BF16 gradients (a 70-billion-parameter model) "
             f"across 64 GPUs, about 276 GB sent per GPU: InfiniBand NDR 400 Gb/s about {ib.seconds:.1f} s, PCIe Gen5 x16 about "
             f"{df[df.fabric == 'PCIe'].seconds.iloc[0]:.1f} s, InfiniBand XDR 800 Gb/s about "
             f"{df[df.generation.str.startswith('XDR')].seconds.iloc[0]:.1f} s, NVLink 4 about "
             f"{df[df.generation == 'NVLink 4'].seconds.iloc[0]:.2f} s, NVLink 5 about {nv5.seconds:.2f} s and NVLink 6 about "
             f"{df[df.generation == 'NVLink 6'].seconds.iloc[0]:.2f} s, roughly 18 times faster on NVLink 5 than on 400G InfiniBand."
             + (f" A 1.6 Tb/s Rubin-generation NIC takes about {df[df.generation == '1.6 Tb/s'].seconds.iloc[0]:.1f} s."
                if (df.generation == "1.6 Tb/s").any() else "")),
        data=[fname], chapters=["P4", "05", "06"],
        source=("NVLink, InfiniBand, Ethernet and PCIe specs via " + fname + "; ring formula"),
        source_ids=list(dict.fromkeys([sid for sid in sources_of(df) if sid.startswith("S2") or sid.startswith("S3")]
                                      + ["S34011"])) if fname == "interconnect_specs.csv"
        else ["S34014", "S34015", "S34016", "S33004", "S34011"],
    )
    fig, ax0 = c.figure(width=10.5, height=5.6)
    ax0.remove()
    ax = fig.add_axes([0.31, 0.15, 0.65, 0.66])
    ax.set_axisbelow(True)
    y = np.arange(len(df))
    for i, r in df.iterrows():
        bar = ax.barh(i, r.seconds, color=SCOPE_COLOR[r.scope], height=0.62,
                      hatch="///" if r.status == "announced" else None)
        _ = bar
        ax.text(r.seconds * 1.06, i, f"{r.seconds:.2f} s" if r.seconds < 1 else f"{r.seconds:.1f} s",
                va="center", fontsize=9.2, color=INK["text"])
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.fabric} {r.generation.replace(' Gb/s', 'G').replace(' Tb/s', 'T')} "
                        f"({r.first_product}, {r.per_gpu_bw_gbs_unidir:,.0f} GB/s/dir)"
                        if r.fabric != "NVLink" else f"{r.generation} ({r.first_product}, {r.per_gpu_bw_gbs_unidir:,.0f} GB/s/dir)"
                        for _, r in df.iterrows()], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.1, 12)
    _plain_log_x(ax)
    ax.grid(True, axis="x")
    ax.grid(False, axis="y")
    handles = [mpatches.Patch(color=SCOPE_COLOR[k], label=SCOPE_LABEL[k]) for k in ["scale-up", "scale-out", "host-io"]]
    handles.append(mpatches.Patch(facecolor=NV, hatch="///", edgecolor="white", label="Rubin generation (2H 2026 ramp)"))
    ax.legend(handles=handles, loc="upper right", fontsize=8.6)
    _log_badge(fig)
    c.save(fig, ax, xlabel="Seconds per full gradient all-reduce (log scale)", legend=False)


@register
def communication_volume_by_parallelism():
    df = load("P4_comm_volume_example.csv").sort_values("gb_per_gpu_per_step").reset_index(drop=True)
    tp = df[df.parallelism.str.startswith("Tensor")].gb_per_gpu_per_step.iloc[0]
    dp = df[df.parallelism.str.startswith("Data (DP")].gb_per_gpu_per_step.iloc[0]
    pp = df[df.parallelism.str.startswith("Pipeline")].gb_per_gpu_per_step.iloc[0]
    c = Chart(
        id="P4-communication-volume-by-parallelism",
        title=f"TP moves ~{tp / dp:.0f}x more data per GPU per step than DP, which is why it stays on NVLink",
        subtitle="Est. GB sent per GPU per training step: 70B dense model, TP8 x PP4 x DP64 on 2,048 GPUs, 4M-token batch, BF16",
        alt=(f"Horizontal bar chart of estimated data sent per GPU per training step for a 70-billion-parameter model split "
             f"8-way tensor, 4-way pipeline and 64-way data parallel: tensor parallelism about {tp:.0f} GB, data-parallel gradient "
             f"all-reduce about {dp:.1f} GB, fully sharded data parallelism about "
             f"{df[df.parallelism.str.startswith('Fully')].gb_per_gpu_per_step.iloc[0]:.1f} GB and pipeline sends about {pp:.1f} GB; "
             f"for contrast, plain data parallelism with a full model copy per GPU would send about 276 GB."),
        data=["P4_comm_volume_example.csv"], chapters=["P4", "05", "06"],
        source="Megatron-LM, ZeRO and ring all-reduce formulas; repo arithmetic", source_ids=sources_of(df),
    )
    fig, ax0 = c.figure(width=10.5, height=5.4)
    ax0.remove()
    ax = fig.add_axes([0.30, 0.15, 0.66, 0.66])
    ax.set_axisbelow(True)
    for i, r in df.iterrows():
        contrast = r.parallelism.startswith("Data, full")
        ax.barh(i, r.gb_per_gpu_per_step, height=0.6, color=SCOPE_COLOR[r.fabric],
                hatch="///" if contrast else None, alpha=0.55 if contrast else 1.0)
        tag = "on the critical path" if r.critical_path == "yes" else "overlaps with backward pass"
        ax.text(r.gb_per_gpu_per_step + 3, i, f"{r.gb_per_gpu_per_step:,.1f} GB · {tag}", va="center", fontsize=9,
                color=INK["text"])
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df.parallelism, fontsize=9.2)
    ax.set_xlim(0, 470)
    ax.grid(True, axis="x")
    ax.grid(False, axis="y")
    handles = [mpatches.Patch(color=NV, label="travels over NVLink (scale-up)"),
               mpatches.Patch(color=SEQ_BLUE[5], label="travels over InfiniBand/Ethernet (scale-out)"),
               mpatches.Patch(facecolor=SEQ_BLUE[5], alpha=0.55, hatch="///", edgecolor="white",
                              label="contrast case: no model sharding")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.6)
    c.save(fig, ax, xlabel="GB sent per GPU per training step (Est.)", legend=False)


@register
def pipeline_bubble_fraction():
    df = load("P4_pipeline_bubble.csv")
    p16 = df[(df.schedule == "1F1B") & (df.pipeline_stages == 16)].set_index("micro_batches")
    c = Chart(
        id="P4-pipeline-bubble-fraction",
        title=f"A 16-stage pipeline idles ~{p16.loc[16, 'bubble_fraction_of_step']:.0%} of the time with 16 micro-batches "
              f"and ~{p16.loc[128, 'bubble_fraction_of_step']:.0%} with 128",
        subtitle="Pipeline bubble: share of step time each GPU sits idle vs micro-batches per step, (p-1)/(v*m+p-1)",
        alt=("Line chart of pipeline bubble fraction against micro-batches per step (log scale). With 4 stages the idle share "
             "falls from 75% at 1 micro-batch to about 9% at 32; with 8 stages it is about 30% at 16 micro-batches; with 16 "
             "stages it is about 48% at 16 micro-batches and about 10% at 128; an interleaved schedule with 4 virtual chunks "
             "cuts the 16-stage bubble at 16 micro-batches to about 19%."),
        data=["P4_pipeline_bubble.csv"], chapters=["P4", "05", "06"],
        source="GPipe and Megatron-LM pipeline-bubble formulas", source_ids=sources_of(df),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    styles = {(4, 1): (GEN_PAST, "-", "o"), (8, 1): (NV, "-", "s"), (16, 1): (NV_DARK, "-", "D"),
              (16, 4): (SEQ_BLUE[5], "--", "D")}
    for (p, v), (col, ls, mk) in styles.items():
        d = df[(df.pipeline_stages == p) & (df.virtual_chunks == v)].sort_values("micro_batches")
        lab = f"{p} stages, 1F1B" if v == 1 else f"{p} stages, interleaved (v={v})"
        ax.plot(d.micro_batches, d.bubble_fraction_of_step * 100, color=col, ls=ls, marker=mk, ms=7, lw=2.2, label=lab)
    ax.axhline(10, color=INK["muted"], lw=1, ls=":")
    ax.text(1.05, 11.5, "10% idle", fontsize=8.6, color=INK["muted"])
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 128])
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(0.85, 160)
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.0f}%"))
    _log_badge(fig)
    c.save(fig, ax, xlabel="Micro-batches per training step, m (log scale)", ylabel="Share of step time idle (bubble)",
           legend=False)


@register
def parallelism_dimensions_frontier_runs():
    df = load("P4_parallelism_configs.csv").sort_values(["year", "gpus"]).reset_index(drop=True)
    dims = [("tp", "Tensor (TP)", NV), ("cp", "Context (CP)", SEQ_BLUE[1]), ("pp", "Pipeline (PP)", SEQ_BLUE[3]),
            ("dp", "Data (DP)", SEQ_BLUE[6])]
    c = Chart(
        id="P4-parallelism-dimensions-frontier-runs",
        title="Frontier GPU runs keep tensor parallelism at 8 or less: one NVLink server",
        subtitle="Published parallelism degrees; bar length = log2(GPUs), each segment = log2(degree); GPUs = TP x CP x PP x DP",
        alt=("Stacked horizontal bars showing how published training runs factor their GPU counts: Megatron 1T on 3,072 A100s "
             "(TP 8, PP 64, DP 6); MT-NLG 530B on 4,480 A100s (TP 8, PP 35, DP 16); BLOOM 176B on 384 A100s (TP 4, PP 12, DP 8); "
             "PaLM 540B on 6,144 TPU v4 chips (12-way model, 512-way data); Nemotron-4 340B on 6,144 H100s (TP 8, PP 12, DP 64); "
             "Llama 3 405B on 16,384 H100s (TP 8, PP 16, DP 128, and TP 8, CP 16, PP 16, DP 8 for long context); DeepSeek-V3 on "
             "2,048 H800s (no TP, PP 16, DP 128 with 64-way expert parallelism)."),
        data=["P4_parallelism_configs.csv"], chapters=["P4", "05", "06", "08"],
        source="published training papers", source_ids=sources_of(df),
    )
    fig, ax0 = c.figure(width=10.8, height=6.4)
    ax0.remove()
    ax = fig.add_axes([0.27, 0.15, 0.70, 0.66])
    ax.set_axisbelow(True)
    for i, r in df.iterrows():
        left = 0.0
        for key, lab, col in dims:
            deg = r[key]
            if deg <= 1:
                continue
            w = np.log2(deg)
            ax.barh(i, w, left=left, color=col, height=0.62, edgecolor="white", linewidth=1.2)
            txt = f"{key.upper()} {deg:g}"
            ax.text(left + w / 2, i, txt, ha="center", va="center", fontsize=8.4,
                    color="white" if key in ("tp", "dp") else INK["title"])
            left += w
        extra = f"  {int(r.gpus):,} {r.accelerator}" + (" (ICI torus, not NVLink)" if "TPU" in r.accelerator else "")
        if r.ep > 1:
            extra += f" · EP {int(r.ep)} overlaps DP"
        ax.text(left + 0.15, i, extra, va="center", fontsize=8.6, color=INK["text"])
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([f"{r.run} ({r.year})" for _, r in df.iterrows()], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 19.5)
    ticks = list(range(0, 15, 2))
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{2 ** t:,}" for t in ticks])
    ax.set_ylim(len(df) + 0.25, -0.6)
    ax.axvline(3, color=NV_DARK, lw=1.2, ls=":")
    ax.text(3.08, len(df) - 0.42, "TP = 8 = one NVLink server", fontsize=8.4, color=NV_DARK, va="top")
    ax.grid(True, axis="x")
    ax.grid(False, axis="y")
    handles = [mpatches.Patch(color=col, label=lab) for _, lab, col in dims]
    ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(0.0, 1.0), fontsize=8.6, ncol=4)
    _log_badge(fig)
    c.save(fig, ax, xlabel="GPUs (log2 scale; segments multiply)", legend=False)
