"""Layer 06 (scale-out and scale-across networking) - CORE charts: why tail latency matters, SHARP's
traffic halving, NVIDIA's Spectrum-X effective-bandwidth claim, CPO power savings for a 100k-GPU cluster,
network share of cluster capex and the fabrics of disclosed large AI clusters.

Data: data/l06_core_inputs.csv, data/l06_allreduce_traffic.csv, data/l06_cluster_examples.csv
(owned by the layer-06 CORE author; documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, NullFormatter

from style import INK, NV, NV_DARK, SEQ_BLUE, Chart, hatch_future, load, register, sources_of

INPUTS = "l06_core_inputs.csv"
ALLRED = "l06_allreduce_traffic.csv"
CLUSTERS = "l06_cluster_examples.csv"
CH = ["06"]
GRAY = "#7A7A7A"
LIGHT = "#B5B5B5"


def _inputs(record_type: str) -> pd.DataFrame:
    d = load(INPUTS)
    return d[d.record_type == record_type].copy()


def _val(d: pd.DataFrame, metric: str, item: str | None = None) -> float:
    m = d[d.metric == metric]
    if item is not None:
        m = m[m["item"] == item]
    return float(m.value.iloc[0])


def _fixed(c: Chart, width: float, height: float, rect):
    fig, ax0 = c.figure(width=width, height=height)
    ax0.remove()
    return fig, fig.add_axes(rect)


def _log_x(fig, ax) -> None:
    ax.set_xscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


# --------------------------------------------------------------------------------------
# 1. Step-time inflation vs tail latency
# --------------------------------------------------------------------------------------
@register
def l06_step_time_vs_tail_latency():
    d = _inputs("tail_latency_model")
    m = _val(d, "exposed_comm_share")
    k = _val(d, "slow_flow_delay_factor")
    f_ex = _val(d, "flows_per_collective_example")
    ps = [("slow_flow_fraction_low", "0.01% of flows slow"), ("slow_flow_fraction_mid", "0.1% of flows slow"),
          ("slow_flow_fraction_high", "1% of flows slow")]
    flows = np.logspace(0, 5, 200)

    def step(p, f):
        hit = 1 - (1 - p) ** f
        return 100 * ((1 - m) + m * (1 + (k - 1) * hit))

    at = {key: step(_val(d, key), f_ex) for key, _ in ps}
    ceiling = 100 * ((1 - m) + m * k)
    c = Chart(
        id="06-step-time-vs-tail-latency",
        title=(f"Est.: if 1% of network flows run {k:.0f}× slow, a {f_ex:,.0f}-flow training step takes "
               f"{at['slow_flow_fraction_high'] / 100:.1f}× as long"),
        subtitle=(f"Step time index (100 = no slow flows) vs flows per collective; {m:.0%} of step is exposed comms; "
                  f"slow flow = {k:.0f}× longer"),
        alt=(f"Line chart from a simple repo model: a synchronous training step waits for its slowest network flow. With "
             f"{m:.0%} of step time in exposed communication and slow flows taking {k:.0f} times longer, a step with "
             f"{f_ex:,.0f} flows takes {at['slow_flow_fraction_low']:.0f} (index) if 0.01% of flows are slow, "
             f"{at['slow_flow_fraction_mid']:.0f} if 0.1% are slow and {at['slow_flow_fraction_high']:.0f} if 1% are slow, "
             f"versus 100 with none; the ceiling is {ceiling:.0f}. Bigger collectives hit the ceiling at lower slow-flow rates."),
        data=[INPUTS], chapters=CH + ["P4"], source="repo model; straggler evidence from ByteDance/NYU (OSDI '25)",
        source_ids=sources_of(d), note="Illustrative model (Est.)",
    )
    fig, ax = _fixed(c, 10.5, 6.0, (0.085, 0.13, 0.86, 0.70))
    cols = [SEQ_BLUE[2], SEQ_BLUE[5], NV_DARK]
    for (key, lab), col in zip(ps, cols):
        p = _val(d, key)
        y = step(p, flows)
        ax.plot(flows, y, color=col, lw=2.2, label=f"{lab}: index {at[key]:.0f} at {f_ex:,.0f} flows")
    ax.axhline(ceiling, color=INK["muted"], lw=1, ls="--")
    ax.text(1.2, ceiling + 6, f"Ceiling {ceiling:.0f}: every step waits for a {k:.0f}× slow flow", fontsize=8.6,
            color=INK["muted"])
    ax.axvline(f_ex, color=INK["base"], lw=1, ls=":")
    for key, col in zip([p[0] for p in ps], cols):
        ax.plot([f_ex], [at[key]], "o", color=col, ms=7, zorder=5)
    ax.text(f_ex * 1.08, 88, f"{f_ex:,.0f} flows", fontsize=8.6, color=INK["text"])
    ax.set_ylim(0, ceiling + 30)
    ax.set_xlim(1, 1e5)
    ax.legend(loc="lower right", fontsize=9)
    _log_x(fig, ax)
    c.save(fig, ax, xlabel="Concurrent flows the collective must wait for (log scale)",
           ylabel="Expected step time (index, 100 = no slow flows)", legend=False)


# --------------------------------------------------------------------------------------
# 2. All-reduce traffic per GPU: ring vs SHARP
# --------------------------------------------------------------------------------------
@register
def l06_allreduce_traffic_sharp():
    d = load(ALLRED)
    ring = d[d.algorithm.str.startswith("Ring")].sort_values("n_gpus")
    sharp = d[d.algorithm.str.contains("SHARP")].sort_values("n_gpus")
    r8 = float(ring.loc[ring.n_gpus == 8, "bytes_sent_per_gpu_x_message"].iloc[0])
    rbig = float(ring.bytes_sent_per_gpu_x_message.iloc[-1])
    c = Chart(
        id="06-allreduce-traffic-sharp",
        title=f"SHARP halves the data each GPU sends per all-reduce: 1× the message vs ~{rbig:.0f}× for a ring",
        subtitle="Bytes each GPU sends per all-reduce ÷ message size, by number of GPUs (bandwidth term only)",
        alt=(f"Line chart: with ring all-reduce each GPU sends 2(N-1)/N times the message, {r8:.2f} times at 8 GPUs and "
             f"approaching {rbig:.1f} times at tens of thousands of GPUs; with SHARP in-network reduction each GPU sends its "
             f"data once (1.0 times) because the switches do the additions, so bandwidth-bound all-reduces can run up to "
             f"about twice as fast. NVIDIA reported about 2x all-reduce bandwidth on HDR InfiniBand."),
        data=[ALLRED], chapters=CH + ["P4", "10"], source="Patarasuk & Yuan (ring all-reduce); NCCL docs; NVIDIA SHARP docs",
        source_ids=sources_of(d),
    )
    fig, ax = _fixed(c, 10.5, 5.8, (0.085, 0.14, 0.68, 0.69))
    ax.plot(ring.n_gpus, ring.bytes_sent_per_gpu_x_message, "-o", color=INK["text"], lw=2.2, ms=6)
    ax.plot(sharp.n_gpus, sharp.bytes_sent_per_gpu_x_message, "-s", color=NV, lw=2.4, ms=6)
    xe = float(ring.n_gpus.iloc[-1])
    ax.annotate("Ring all-reduce\n(GPUs add, then share)\n2(N−1)/N × message", (xe, rbig), xytext=(8, 0),
                textcoords="offset points", va="center", fontsize=9, color=INK["text"], fontweight="bold",
                annotation_clip=False)
    ax.annotate("SHARP in-network\n(switches add)\n1 × message", (xe, 1.0), xytext=(8, 0), textcoords="offset points",
                va="center", fontsize=9, color=NV_DARK, fontweight="bold", annotation_clip=False)
    ax.fill_between(ring.n_gpus, sharp.bytes_sent_per_gpu_x_message.values, ring.bytes_sent_per_gpu_x_message.values,
                    color=NV, alpha=0.10, lw=0)
    ax.text(300, 1.42, "Traffic SHARP removes\n(~half at scale)", ha="center", fontsize=9, color=NV_DARK)
    ax.set_ylim(0, 2.3)
    ax.set_xlim(1.6, 9e4)
    _log_x(fig, ax)
    c.save(fig, ax, xlabel="GPUs in the all-reduce (log scale)", ylabel="Bytes sent per GPU ÷ message size", legend=False)


# --------------------------------------------------------------------------------------
# 3. Spectrum-X effective bandwidth claim
# --------------------------------------------------------------------------------------
@register
def l06_spectrum_x_effective_bandwidth():
    d = _inputs("spectrum_x_claim")
    std = _val(d, "effective_throughput_pct", "Standard Ethernet at 100k-GPU scale (NVIDIA claim)")
    sx = _val(d, "effective_throughput_pct", "Spectrum-X on xAI Colossus (NVIDIA claim)")
    port = _val(d, "port_gbps")
    mult = _val(d, "performance_multiplier")
    vals = [port, port * sx / 100, port * std / 100]
    labels = ["Line rate (BlueField-3 SuperNIC)", f"Spectrum-X on Colossus: {sx:.0f}% (NVIDIA claim)",
              f"Standard Ethernet at scale: {std:.0f}% (NVIDIA claim)"]
    c = Chart(
        id="06-spectrum-x-effective-bandwidth",
        title=f"NVIDIA claims Spectrum-X keeps {sx:.0f}% of link bandwidth vs {std:.0f}% for standard Ethernet",
        subtitle=f"Effective Gb/s per GPU, {port:.0f} Gb/s port, 100k-GPU scale (xAI Colossus); hatched = vendor claim, untested",
        alt=(f"Horizontal bar chart: each Colossus GPU has a {port:.0f} Gb/s SuperNIC port; NVIDIA says Spectrum-X sustains "
             f"{sx:.0f}% of it (~{vals[1]:.0f} Gb/s) while standard Ethernet with hash-based load balancing manages ~{std:.0f}% "
             f"(~{vals[2]:.0f} Gb/s) at that scale because of flow collisions. The ratio {sx:.0f}/{std:.0f} = {sx/std:.2f} matches "
             f"NVIDIA's '{mult:.1f}x AI networking performance' claim. Both figures are vendor claims."),
        data=[INPUTS], chapters=CH, source="NVIDIA (xAI Colossus release; Spectrum-X product page)",
        source_ids=sources_of(d),
    )
    fig, ax = _fixed(c, 10.5, 4.8, (0.34, 0.17, 0.58, 0.62))
    y = np.arange(3)[::-1]
    bars = ax.barh(y, vals, color=[LIGHT, NV, GRAY], height=0.58)
    hatch_future(bars, [False, True, True])
    for yi, v in zip(y, vals):
        ax.text(v + 5, yi, f"{v:.0f} Gb/s", va="center", fontsize=10, fontweight="bold", color=INK["title"])
    ax.set_yticks(y, labels, fontsize=9.4)
    ax.set_xlim(0, port * 1.45)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.annotate("", xy=(vals[1], 0.5), xytext=(vals[2], 0.5),
                arrowprops=dict(arrowstyle="->", color=NV_DARK, lw=1.6))
    ax.text(vals[1] + 6, 0.5, f"{sx:.0f} ÷ {std:.0f} = {sx/std:.2f}× ≈ the '{mult:.1f}×' claim", ha="left", va="center",
            fontsize=9, color=NV_DARK, fontweight="bold")
    c.save(fig, ax, xlabel="Effective bandwidth per GPU (Gb/s)", legend=False)


# --------------------------------------------------------------------------------------
# 4. CPO power for a 100k-GPU cluster, three counting bases
# --------------------------------------------------------------------------------------
@register
def l06_cpo_power_100k_gpus():
    d = _inputs("cpo_scenario")
    n = _val(d, "gpus", "100k-GPU cluster")
    bases = [b for b in d["item"].unique() if b != "100k-GPU cluster"]
    rows = []
    for b in bases:
        s = d[d["item"] == b]
        nic_m, nic_w = _val(s, "nic_modules_per_gpu"), _val(s, "nic_module_w")
        sw_m, sw_w, fac = _val(s, "switch_modules_per_gpu"), _val(s, "switch_module_w"), _val(s, "cpo_power_factor")
        plug = n * (nic_m * nic_w + sw_m * sw_w) / 1e6
        cpo = n * (nic_m * nic_w + sw_m * sw_w / fac) / 1e6
        rows.append(dict(basis=b, plug=plug, cpo=cpo, saved=plug - cpo))
    r = pd.DataFrame(rows)
    lo, hi = r.saved.min(), r.saved.max()
    c = Chart(
        id="06-cpo-power-100k-gpus",
        title=f"Est.: co-packaged optics save ~{lo:.0f}–{hi:.0f} MW of optics power in a 100k-GPU cluster",
        subtitle="Optics power (MW, IT load before cooling overhead) for 100,000 GPUs in a 3-tier fabric: all-pluggable vs CPO switches",
        alt=(f"Grouped bar chart (estimates). Counting twin-port modules (1 NIC module at 15 W plus 2.5 switch-side 1.6T "
             f"modules at 30 W per GPU) optics draw {r.plug[0]:.1f} MW for 100,000 GPUs; CPO switches cut that to "
             f"{r.cpo[0]:.1f} MW with NVIDIA's 3.5x claim or {r.cpo[1]:.1f} MW with its 2026 5x claim. Using Jensen Huang's "
             f"keynote framing of six 30 W transceivers per GPU, optics draw {r.plug[2]:.0f} MW and CPO {r.cpo[2]:.1f} MW. "
             f"Savings range {lo:.1f} to {hi:.1f} MW before cooling overhead."),
        data=[INPUTS], chapters=CH + ["08"], source="NVIDIA claims; repo counts",
        source_ids=sources_of(d), note="All values Est.",
    )
    fig, ax = _fixed(c, 10.5, 5.6, (0.33, 0.14, 0.60, 0.68))
    y = np.arange(len(r))[::-1] * 1.0
    h = 0.36
    b1 = ax.barh(y + h / 2, r.plug, height=h, color=GRAY, label="All pluggable transceivers")
    b2 = ax.barh(y - h / 2, r.cpo, height=h, color=NV, label="CPO switches (NIC side stays pluggable)")
    hatch_future(b1, [True] * len(r))
    hatch_future(b2, [True] * len(r))
    for yi, (p, cp, s) in zip(y, zip(r.plug, r.cpo, r.saved)):
        ax.text(p + 0.2, yi + h / 2, f"{p:.1f} MW", va="center", fontsize=9, color=INK["text"])
        ax.text(cp + 0.2, yi - h / 2, f"{cp:.1f} MW  (saves {s:.1f} MW)", va="center", fontsize=9, color=NV_DARK,
                fontweight="bold")
    ax.set_yticks(y, list(r.basis), fontsize=9.2)
    ax.set_xlim(0, r.plug.max() * 1.3)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper right", fontsize=8.8)
    c.save(fig, ax, xlabel="Optics power for 100,000 GPUs (MW)", legend=False)


# --------------------------------------------------------------------------------------
# 5. Network share of cluster capex: the estimates side by side
# --------------------------------------------------------------------------------------
@register
def l06_network_share_of_cluster_capex():
    d = _inputs("network_cost_share").sort_values("value")
    scope = []
    for it in d["item"]:
        if it.startswith("Reuters"):
            scope.append(("Whole AI data center (incl. building, power)", LIGHT))
        elif it.startswith("NVIDIA"):
            scope.append(("NVIDIA revenue mix (proxy)", NV))
        elif it.startswith("Huang"):
            scope.append(("Optics only", SEQ_BLUE[2]))
        else:
            scope.append(("Cluster hardware estimate", SEQ_BLUE[5]))
    d["scope"], d["color"] = [s for s, _ in scope], [c for _, c in scope]
    cl = d[d.scope == "Cluster hardware estimate"].value
    c = Chart(
        id="06-network-share-of-cluster-capex",
        title=f"Networking is ~{int(cl.min() + 0.5)}–{int(cl.max() + 0.5)}% of AI cluster hardware capex by most estimates (13% of a whole site)",
        subtitle="Network share of spend, %, by estimate and scope; hatched = analyst or repo estimate",
        alt=("Horizontal bar chart of estimates of the network's share of AI spending: switches alone about 3% and all "
             "networking about 13% of a whole 1 GW data center's spend (Reuters); optics alone about 11% of a GB300 NVL72's "
             "per-GPU price using Jensen Huang's six $1,000 transceivers per GPU; about 17% (576 GPUs) and 19% (24,576 GPUs) "
             "of cluster capex in one bottom-up blog estimate; NVIDIA networking at about 20% of its Data Center revenue in "
             "Q2 FY2027; and about 20.5% networking plus storage in SemiAnalysis's all-in GB200 NVL72 cost."),
        data=[INPUTS], chapters=CH + ["08", "14"], source="Reuters, SemiAnalysis via fal.ai, AMCompute, NVIDIA, Morgan Stanley; repo calc",
        source_ids=sources_of(d),
    )
    fig, ax = _fixed(c, 11.0, 6.0, (0.44, 0.13, 0.50, 0.70))
    y = np.arange(len(d))
    bars = ax.barh(y, d.value, color=d.color, height=0.6)
    hatch_future(bars, d.confidence.eq("estimate").to_numpy())
    for yi, v in zip(y, d.value):
        ax.text(v + 0.4, yi, f"{v:.1f}%" if v % 1 else f"{v:.0f}%", va="center", fontsize=9.5, fontweight="bold",
                color=INK["title"])
    ax.set_yticks(y, d["item"], fontsize=8.8)
    ax.set_xlim(0, 25)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    seen = []
    handles = []
    for s, col in zip(d.scope, d.color):
        if s not in seen:
            seen.append(s)
            handles.append(Patch(color=col, label=s))
    ax.legend(handles=handles, loc="lower right", fontsize=8.4)
    c.save(fig, ax, xlabel="Network share of spend (%)", legend=False)


# --------------------------------------------------------------------------------------
# 6. Disclosed AI clusters by size and fabric
# --------------------------------------------------------------------------------------
@register
def l06_ai_cluster_fabrics():
    d = load(CLUSTERS)
    d = d[d.gpus.notna()].copy().sort_values(["year", "gpus"])
    fam = {"infiniband": ("NVIDIA InfiniBand", NV), "spectrum-x": ("NVIDIA Spectrum-X Ethernet", NV_DARK),
           "ethernet-other": ("Other Ethernet / RoCE", GRAY)}
    d["label"] = [fam[f][0] for f in d.fabric_family]
    d["color"] = [fam[f][1] for f in d.fabric_family]
    eagle = d[d.cluster.str.startswith("Azure Eagle")].iloc[0]
    oci = d[d.cluster.str.startswith("OCI")].iloc[0]
    c = Chart(
        id="06-ai-cluster-fabrics",
        title=f"Disclosed AI fabrics grew from {eagle.gpus/1000:.0f}k GPUs on InfiniBand (2023) to 100k+ on Ethernet (2024)",
        subtitle=f"GPUs in one back-end fabric, by fabric; hatched = reported or announced (Oracle targets {oci.gpus/1000:,.0f}k)",
        alt=("Horizontal log-scale bar chart of disclosed AI clusters: Microsoft Azure Eagle 14,400 H100 on InfiniBand NDR "
             "(2023 TOP500 run); Meta's two 24,576-GPU H100 clusters, one InfiniBand and one RoCE Ethernet (2024); xAI "
             "Colossus 100,000 H100 on NVIDIA Spectrum-X Ethernet (2024) with a reported expansion to 200,000; Oracle's "
             "Zettascale10 RoCE multiplanar design targeting up to 800,000 GPUs (announced for 2026). The largest fabrics "
             "since 2024 are Ethernet."),
        data=[CLUSTERS], chapters=CH + ["08"], source="Microsoft, Meta, NVIDIA/xAI, Oracle announcements",
        source_ids=sources_of(d),
    )
    fig, ax = _fixed(c, 11.0, 5.8, (0.34, 0.14, 0.58, 0.69))
    y = np.arange(len(d))[::-1]
    bars = ax.barh(y, d.gpus, color=d.color, height=0.6)
    hatch_future(bars, d.status.isin(["reported", "announced"]).to_numpy())
    for yi, (g, gbps) in zip(y, zip(d.gpus, d.gbps_per_gpu)):
        extra = f" · {gbps:.0f} Gb/s per GPU" if gbps == gbps else ""
        ax.text(g * 1.08, yi, f"{g:,.0f}{extra}", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, [f"{cl} ({yr})" for cl, yr in zip(d.cluster, d.year)], fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(5_000, 6_000_000)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=col, label=lab) for lab, col in fam.values()]
    handles.append(Patch(facecolor="#8C8C8C", hatch="///", edgecolor="#FFFFFF", alpha=0.75,
                         label="Reported / announced"))
    ax.legend(handles=handles, loc="upper right", fontsize=8.4)
    c.save(fig, ax, xlabel="GPUs in one back-end fabric (log scale)", legend=False)


_ = Line2D  # imported for optional legend handles
