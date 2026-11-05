"""Layer 05 (Scale-up: NVLink, NVSwitch) - CORE charts: shard transfer time by link, NVLink domain bandwidth
by system, wire pairs per GPU, switch chips and copper pairs per domain, copper reach vs lane rate, copper vs
optics for the NVL72 spine, MoE all-to-all time by system, DeepEP measured NVLink vs RDMA, NVL72 vs NVL8 on the
same Blackwell silicon, switched vs torus all-to-all, and the NVLink Fusion partner timeline.

Data: data/interconnect_specs.csv, data/optics_power_estimates.csv, data/inference_benchmarks.csv (shared,
read-only) and data/l05_rack_fabric.csv, data/l05_copper_vs_optics.csv, data/l05_moe_comm.csv,
data/l05_nvlink_fusion_partners.csv (owned by the layer-05 CORE author; documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

IC = "interconnect_specs.csv"
FAB = "l05_rack_fabric.csv"
CVO = "l05_copper_vs_optics.csv"
MOE = "l05_moe_comm.csv"
FUS = "l05_nvlink_fusion_partners.csv"
OPT = "optics_power_estimates.csv"
INF = "inference_benchmarks.csv"
CH = ["05"]
GREY = "#B5B5B5"
DARKGREY = "#7A7A7A"


def _left_margin(fig, left: float, right: float | None = None) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        if right is not None:
            kw["right"] = right
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _ic_row(gen: str) -> pd.Series:
    d = load(IC)
    return d[d.generation == gen].iloc[0]


def _moe() -> pd.DataFrame:
    return load(MOE)


def _mval(df: pd.DataFrame, item: str, metric: str) -> float:
    r = df[(df["item"] == item) & (df["metric"] == metric)]
    return float(r["value"].iloc[0])


def _ms(v: float) -> str:
    return f"{v:,.1f} ms" if v < 20 else f"{v:,.0f} ms"


# --------------------------------------------------------------------------------------------------
# 1. Time to move a 10 GB tensor shard each way, by link
# --------------------------------------------------------------------------------------------------
@register
def l05_shard_transfer_time():
    links = [  # (interconnect_specs generation, label, kind)
        ("NVLink 6 (Vera Rubin NVL72)", "NVLink 6 · Vera Rubin (production spec)", "nvlink"),
        ("NVLink 5 (GB200 NVL72)", "NVLink 5 · Blackwell", "nvlink"),
        ("NVLink 4 (HGX H100 NVL8)", "NVLink 4 · Hopper", "nvlink_past"),
        ("1.6TbE (IEEE 802.3dj, 8x200G)", "1.6 Tb/s NIC port (ConnectX-9 class)", "nic"),
        ("PCIe 6.0", "PCIe 6.0 x16", "pcie"),
        ("XDR", "800 Gb/s NIC port (ConnectX-8 class)", "nic"),
        ("PCIe 5.0", "PCIe 5.0 x16", "pcie"),
        ("NDR", "400 Gb/s NIC port (ConnectX-7 class)", "nic"),
    ]
    rows = []
    for gen, lab, kind in links:
        r = _ic_row(gen)
        per_dir = float(r.per_device_bw_gbs_bidir) / 2
        rows.append(dict(label=lab, kind=kind, per_dir=per_dir, ms=10.0 / per_dir * 1000, source_id=r.source_id))
    d = pd.DataFrame(rows)
    nv5 = d.set_index("label").loc["NVLink 5 · Blackwell", "ms"]
    n800 = d.set_index("label").loc["800 Gb/s NIC port (ConnectX-8 class)", "ms"]
    nv6 = d.set_index("label").loc["NVLink 6 · Vera Rubin (production spec)", "ms"]
    c = Chart(
        id="05-shard-transfer-time",
        title=f"A 10 GB shard moves each way in ~{nv5:.0f} ms on NVLink 5 vs ~{n800:.0f} ms on an 800G NIC",
        subtitle="Milliseconds to send 10 GB each way at once (full duplex) at peak link rate; protocol overhead adds more",
        alt=(f"Horizontal log-scale bar chart of the time to move 10 GB each way per GPU: NVLink 6 on Vera Rubin about {nv6:.1f} ms "
             f"(1,500 GB/s per direction), NVLink 5 about {nv5:.0f} ms (900 GB/s), NVLink 4 about 22 ms (450 GB/s), a 1.6 Tb/s NIC "
             f"50 ms, PCIe 6.0 x16 about 78 ms, an 800 Gb/s NIC {n800:.0f} ms, PCIe 5.0 x16 about 156 ms and a 400 Gb/s NIC "
             f"200 ms: the scale-up link is roughly 9 to 15 times faster than the scale-out port beside it."),
        data=[IC], chapters=CH + ["06", "P4"], source="NVIDIA NVLink specs, PCI-SIG, IBTA, IEEE 802.3",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    color = {"nvlink": NV, "nvlink_past": GEN_PAST, "nic": DARKGREY, "pcie": GREY}
    y = np.arange(len(d))[::-1]
    ax.barh(y, d.ms, color=[color[k] for k in d.kind], height=0.62, zorder=2)
    for yi, (ms, pdir) in zip(y, zip(d.ms, d.per_dir)):
        ax.text(ms * 1.06, yi, f"{_ms(ms)}   ({pdir:,.0f} GB/s each way)", va="center", fontsize=8.8, color=INK["text"])
    ax.set_yticks(y, d.label)
    ax.set_xscale("log")
    ax.set_xlim(3, 2000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=NV, label="NVLink (scale-up)"), Patch(color=GEN_PAST, label="NVLink, previous generation"),
                       Patch(color=DARKGREY, label="NIC port (scale-out)"), Patch(color=GREY, label="PCIe x16 (host I/O)")],
              loc="upper right", fontsize=8.6)
    _left_margin(fig, 0.29)
    c.save(fig, ax, xlabel="Milliseconds to move 10 GB each way", logx=True, legend=False)


# --------------------------------------------------------------------------------------------------
# 2. NVLink domain aggregate bandwidth by system
# --------------------------------------------------------------------------------------------------
@register
def l05_domain_bandwidth_by_system():
    f = load(FAB)
    keep = ["DGX-1 (P100)", "DGX-1 (V100)", "DGX-2", "HGX A100 8-GPU", "HGX H100 8-GPU", "DGX GH200 (NVLink Switch System)",
            "HGX B200 8-GPU", "GB200 NVL72", "GB300 NVL72", "Vera Rubin NVL72 (production spec)", "Rubin Ultra Kyber NVL144"]
    d = f.set_index("system").loc[keep].reset_index()
    labels = {"DGX-1 (P100)": "DGX-1\nP100", "DGX-1 (V100)": "DGX-1\nV100", "DGX-2": "DGX-2", "HGX A100 8-GPU": "HGX\nA100",
              "HGX H100 8-GPU": "HGX\nH100", "DGX GH200 (NVLink Switch System)": "DGX\nGH200*", "HGX B200 8-GPU": "HGX\nB200",
              "GB200 NVL72": "GB200\nNVL72", "GB300 NVL72": "GB300\nNVL72", "Vera Rubin NVL72 (production spec)": "Vera Rubin\nNVL72",
              "Rubin Ultra Kyber NVL144": "Kyber\nNVL144"}
    design = float(f.set_index("system").loc["Vera Rubin NVL72 (CES 2026 design spec)", "domain_bw_tbs_bidir"])
    first = float(d.domain_bw_tbs_bidir.iloc[0])
    vr = float(d.set_index("system").loc["Vera Rubin NVL72 (production spec)", "domain_bw_tbs_bidir"])
    mult = vr / first
    c = Chart(
        id="05-nvlink-domain-bandwidth-by-system",
        title=f"NVLink domain bandwidth rose ~{round(mult, -1):.0f}× in a decade, to {vr:.0f} TB/s on Vera Rubin NVL72",
        subtitle="Aggregate NVLink bandwidth of one scale-up domain, TB/s bidirectional (GPUs × per-GPU NVLink); labels = GPUs",
        alt=(f"Log-scale bar chart of aggregate NVLink bandwidth per scale-up domain: DGX-1 P100 {first:.2f} TB/s (8 GPUs), DGX-1 V100 2.4, "
             f"DGX-2 4.8 (16), HGX A100 4.8, HGX H100 7.2, HGX B200 14.4, GB200 and GB300 NVL72 about 130 TB/s (72 GPUs), Vera Rubin "
             f"NVL72 {vr:.0f} TB/s on the revised production spec (launch spec {design:.0f}), and Kyber NVL144 about 518 TB/s on the "
             f"2027 roadmap (144 GPUs). DGX GH200 reached 230 TB/s across 256 GPUs but saw limited deployment."),
        data=[FAB], chapters=CH + ["08", "17"], source="NVIDIA specs; SemiAnalysis; repo calc", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    x = np.arange(len(d))
    colors, hatches = [], []
    for s, st in zip(d.system, d.status):
        if s.startswith("DGX GH200"):
            colors.append(GREY)
        elif s in ("GB200 NVL72", "GB300 NVL72", "Vera Rubin NVL72 (production spec)", "Rubin Ultra Kyber NVL144"):
            colors.append(NV)
        else:
            colors.append(GEN_PAST)
        hatches.append("///" if st == "roadmap" else None)
    bars = ax.bar(x, d.domain_bw_tbs_bidir, color=colors, width=0.66, zorder=2)
    for b, h in zip(bars.patches, hatches):
        if h:
            b.set_hatch(h)
            b.set_alpha(0.8)
    vi = list(d.system).index("Vera Rubin NVL72 (production spec)")
    ax.bar(x[vi], design, width=0.66, fill=False, edgecolor=NV_DARK, linestyle="--", linewidth=1.2, zorder=3)
    ax.annotate(f"launch spec {design:.0f}", (x[vi], design), xytext=(0, 3), textcoords="offset points", ha="center",
                fontsize=8, color=NV_DARK)
    for xi, (v, g) in enumerate(zip(d.domain_bw_tbs_bidir, d.gpus_in_domain)):
        txt = f"{v:,.1f}" if v < 10 else f"{v:,.0f}"
        yoff = 18 if xi == vi else 3
        ax.annotate(f"{txt}\n{int(g)} GPUs", (xi, v), xytext=(0, yoff), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.2, color=INK["text"])
    ax.set_xticks(x, [labels[s] for s in d.system], fontsize=8.6)
    ax.set_yscale("log")
    ax.set_ylim(0.5, 3000)
    ax.text(-0.4, 1500, "* DGX GH200: limited deployment\nhatched = roadmap · dashed = launch spec", fontsize=8.2,
            color=INK["muted"], va="center")
    c.save(fig, ax, ylabel="TB/s per NVLink domain", logy=True, legend=False, bottom=0.17)


# --------------------------------------------------------------------------------------------------
# 3. Wire pairs per GPU and rate per pair, by NVLink generation
# --------------------------------------------------------------------------------------------------
@register
def l05_pairs_per_gpu_and_rate():
    f = load(FAB)
    pick = [("DGX-1 (P100)", "NVLink 1\n2016"), ("DGX-1 (V100)", "NVLink 2\n2017"), ("HGX A100 8-GPU", "NVLink 3\n2020"),
            ("HGX H100 8-GPU", "NVLink 4\n2022"), ("GB200 NVL72", "NVLink 5\n2024"),
            ("Vera Rubin NVL72 (production spec)", "NVLink 6\n2026"), ("Rubin Ultra Kyber NVL144", "NVLink 7\n2027")]
    d = f.set_index("system").loc[[p[0] for p in pick]].reset_index()
    d["lab"] = [p[1] for p in pick]
    design = float(f.set_index("system").loc["Vera Rubin NVL72 (CES 2026 design spec)", "pair_gbps"])
    c = Chart(
        id="05-nvlink-pairs-per-gpu-and-rate",
        title="72 NVLink wire pairs per GPU since Hopper: bandwidth grew 3–4× via faster pairs",
        subtitle="Differential pairs per GPU (left; links × lanes × directions, repo calc) and Gb/s per pair (right); hatched = roadmap",
        alt=("Two-panel bar chart. Left: NVLink differential pairs per GPU were 64 (NVLink 1), 96 (NVLink 2 and 3) and then 72 for "
             "NVLink 4, 5, 6 and 7. Right: Gb/s per pair rose from 20 and 25 (NRZ) to 50, 100 (PAM4, Hopper), 200 (Blackwell) and "
             f"about 333 on Rubin's revised spec ({design:.0f} at launch, with each pair carrying traffic both ways), and 400 on "
             "Rubin Ultra (reported). Holding the pair count fixed is what lets the NVL72 copper spine keep its cable count."),
        data=[FAB], chapters=CH + ["17"], source="NVIDIA whitepapers and specs; SemiAnalysis; repo calc", source_ids=sources_of(d),
    )
    fig, axes = c.figure_grid(1, 2, width=11, height=5.4)
    x = np.arange(len(d))
    cols = [GEN_PAST] * 4 + [NV] * 3
    for ax, col, ylab in ((axes[0], "pairs_per_gpu", "Wire pairs per GPU"), (axes[1], "pair_gbps", "Gb/s per pair (both directions)")):
        bars = ax.bar(x, d[col], color=cols, width=0.64, zorder=2)
        for b, st in zip(bars.patches, d.status):
            if st == "roadmap":
                b.set_hatch("///")
                b.set_alpha(0.8)
        for xi, v in enumerate(d[col]):
            ax.annotate(f"{v:,.0f}", (xi, v), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.6,
                        color=INK["text"])
        ax.set_xticks(x, d.lab, fontsize=8.2)
        ax.set_ylabel(ylab)
    axes[1].bar(x[5], design, width=0.64, fill=False, edgecolor=NV_DARK, linestyle="--", linewidth=1.2, zorder=3)
    axes[1].annotate(f"launch {design:.0f}", (x[5], design), xytext=(-24, 3), textcoords="offset points", fontsize=7.8,
                     color=NV_DARK)
    axes[0].set_ylim(0, 115)
    axes[1].set_ylim(0, 460)
    axes[0].set_title("Wire pairs per GPU", fontsize=10.5, color=INK["title"], loc="left")
    axes[1].set_title("Speed per pair", fontsize=10.5, color=INK["title"], loc="left")
    fig.subplots_adjust(wspace=0.22)
    c.save(fig, list(axes), legend=False, top=0.80)


# --------------------------------------------------------------------------------------------------
# 4. Switch chips and copper pairs per NVLink domain
# --------------------------------------------------------------------------------------------------
@register
def l05_switch_chips_and_copper_pairs():
    f = load(FAB).set_index("system")
    sw = [("DGX-2", "DGX-2 (16 GPUs)"), ("HGX A100 8-GPU", "HGX A100 (8)"), ("HGX H100 8-GPU", "HGX H100 (8)"),
          ("HGX B200 8-GPU", "HGX B200 (8)"), ("GB200 NVL72", "GB200 NVL72 (72)"),
          ("Vera Rubin NVL72 (production spec)", "Vera Rubin NVL72 (72)"), ("Rubin Ultra Kyber NVL144", "Kyber NVL144 (144)")]
    ds = f.loc[[s for s, _ in sw]].reset_index()
    ds["lab"] = [lab for _, lab in sw]
    cp = [("GB200 NVL72", "GB200 / GB300\nNVL72 (2024–25)"), ("Vera Rubin NVL72 (production spec)", "Vera Rubin\nNVL72 (2026)"),
          ("Rubin Ultra Kyber NVL144", "Kyber NVL144\n(2027, roadmap)")]
    dc = f.loc[[s for s, _ in cp]].reset_index()
    dc["lab"] = [lab for _, lab in cp]
    gb = f.loc["GB200 NVL72"]
    c = Chart(
        id="05-switch-chips-and-copper-pairs",
        title="NVL72 doubled its switch chips (18 → 36) on the same ~5,184 copper pairs",
        subtitle="NVLink switch chips per domain (left) and NVLink copper pairs per rack, repo calc (right); hatched = roadmap",
        alt=("Two-panel bar chart. Left: NVSwitch chips per domain were 12 in DGX-2 (16 GPUs), 6 in HGX A100, 4 in HGX H100 and 2 in "
             "HGX B200 (8 GPUs each), then 18 in GB200 NVL72, 36 in Vera Rubin NVL72 and a reported 72 in Kyber NVL144 (Lockwood "
             "estimates 36). Right: GB200 and GB300 NVL72 carry about 5,184 copper pairs (NVIDIA quoted about 5,000 cables, 2 miles) "
             "for 130 TB/s; Vera Rubin NVL72 reuses the same count for 216 TB/s (260 at launch); Kyber NVL144 doubles to 10,368 pairs "
             "on a printed-circuit midplane for about 518 TB/s."),
        data=[FAB], chapters=CH + ["08"], source="NVIDIA; SemiAnalysis; KGI; Lockwood; repo calc",
        source_ids=sources_of(pd.concat([ds[["source_id"]], dc[["source_id"]]])),
    )
    fig, axes = c.figure_grid(1, 2, width=11.2, height=5.6, gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]
    y = np.arange(len(ds))[::-1]
    cols = [NV if g >= 72 else GEN_PAST for g in ds.gpus_in_domain]
    bars = ax.barh(y, ds.switch_chips, color=cols, height=0.62, zorder=2)
    for b, st in zip(bars.patches, ds.status):
        if st == "roadmap":
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yi, v, g in zip(y, ds.switch_chips, ds.gpus_in_domain):
        ax.text(v + 1, yi, f"{v:.0f}", va="center", fontsize=8.8, color=INK["text"])
    ax.text(ds.switch_chips.iloc[-1] + 9, y[-1], "(Lockwood: 36)", va="center", fontsize=8, color=INK["muted"])
    ax.set_yticks(y, ds.lab, fontsize=8.8)
    ax.set_xlim(0, 100)
    ax.set_xlabel("NVLink switch chips per domain")
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_title("Switch chips per domain", fontsize=10.5, color=INK["title"], loc="left")
    ax2 = axes[1]
    x = np.arange(len(dc))
    b2 = ax2.bar(x, dc.rack_copper_pairs, color=NV, width=0.6, zorder=2)
    for b, st in zip(b2.patches, dc.status):
        if st == "roadmap":
            b.set_hatch("///")
            b.set_alpha(0.8)
    for xi, (p, bw, med) in enumerate(zip(dc.rack_copper_pairs, dc.domain_bw_tbs_bidir, dc.physical_medium)):
        where = "cable spine" if med.startswith("copper cable") else "PCB midplane"
        ax2.annotate(f"{p:,.0f} pairs\n{bw:,.0f} TB/s\n{where}", (xi, p), xytext=(0, 3), textcoords="offset points",
                     ha="center", fontsize=8.2, color=INK["text"])
    ax2.axhline(float(gb.cables_reported), color=INK["muted"], linestyle=":", linewidth=1.2)
    ax2.legend(handles=[Line2D([], [], color=INK["muted"], linestyle=":", label="~5,000 cables quoted at GTC 2024")],
               loc="upper left", fontsize=8)
    ax2.set_xticks(x, dc.lab, fontsize=8.4)
    ax2.set_ylim(0, 14500)
    ax2.set_ylabel("NVLink copper pairs per rack (cable or PCB)")
    ax2.set_title("Copper pairs per rack", fontsize=10.5, color=INK["title"], loc="left")
    _left_margin(fig, 0.17)
    fig.subplots_adjust(wspace=0.32)
    c.save(fig, list(axes), legend=False, top=0.80, bottom=0.16)


# --------------------------------------------------------------------------------------------------
# 5. Passive copper reach vs lane rate
# --------------------------------------------------------------------------------------------------
@register
def l05_copper_reach_vs_lane_rate():
    cv = load(CVO)
    d = cv[cv.record_type == "reach"].sort_values("lane_gbps").reset_index(drop=True)
    miles = float(cv[(cv.record_type == "claim") & (cv.metric == "cable_length")].value_low.iloc[0])
    pairs = float(load(FAB).set_index("system").loc["GB200 NVL72", "rack_copper_pairs"])
    avg_m = miles * 1609.344 / pairs
    c = Chart(
        id="05-copper-reach-vs-lane-rate",
        title="Passive copper reach shrinks as lanes speed up: ~5 m at 25 Gb/s, ~1 m at 200 Gb/s",
        subtitle="Typical maximum length of a passive copper (twinax) link by per-lane signaling rate, metres; varies with wire gauge",
        alt=(f"Line chart of passive copper reach versus lane rate: about 5 m at 25 Gb/s per lane (NRZ), 3 m at 50 Gb/s, 2 m at "
             f"100 Gb/s (IEEE 802.3ck) and about 1 m at 200 Gb/s (IEEE 802.3dj objective), the lane rate NVLink 5 and 6 use. An "
             f"NVL72 spine averages about {avg_m:.1f} m per pair (2 miles over 5,184 pairs), which is why the rack, not the row, is "
             f"the natural copper boundary."),
        data=[CVO, FAB], chapters=CH + ["06", "08"], source="IEEE 802.3, SNIA, Keysight, vendor listings",
        source_ids=sources_of(d) + ["S5000"],
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    ax.plot(d.lane_gbps, d.value_low, color=DARKGREY, marker="o", markersize=8, zorder=3)
    ax.scatter([200], [float(d.value_low.iloc[-1])], s=140, color=NV, zorder=4)
    for lg, v, it in zip(d.lane_gbps, d.value_low, d["item"]):
        name = it.split("(")[-1].rstrip(")")
        ax.annotate(f"{v:g} m\n{name}", (lg, v), xytext=(10, 6), textcoords="offset points", fontsize=8.6, color=INK["text"])
    ax.axhline(avg_m, color=NV, linestyle="--", linewidth=1.2)
    ax.text(26, avg_m + 0.12, f"Average NVL72 spine pair ≈ {avg_m:.1f} m (2 miles ÷ {pairs:,.0f} pairs, repo calc)", fontsize=8.4,
            color=NV_DARK)
    ax.annotate("NVLink 5 / 6 lanes", (200, float(d.value_low.iloc[-1])), xytext=(-110, 40), textcoords="offset points",
                fontsize=8.6, color=NV_DARK, arrowprops=dict(arrowstyle="->", color=NV_DARK, lw=1))
    ax.set_xscale("log", base=2)
    ax.set_xticks([25, 50, 100, 200], ["25", "50", "100", "200"])
    ax.minorticks_off()
    ax.set_xlim(20, 320)
    ax.set_ylim(0, 6)
    c.save(fig, ax, xlabel="Lane rate, Gb/s per lane (log-2 spacing)", ylabel="Passive copper reach (m)", legend=False)


# --------------------------------------------------------------------------------------------------
# 6. Copper vs optics for the NVL72 spine: power and media cost
# --------------------------------------------------------------------------------------------------
@register
def l05_spine_copper_vs_optics():
    cv = load(CVO)
    op = load(OPT).set_index("technology")
    mods = float(cv[cv.record_type == "assumption"].value_low.iloc[0])
    links = mods / 2
    techs = [("Copper (passive) spine", "Copper (passive DAC / NVLink spine)"),
             ("Co-packaged optics", "CPO (NVIDIA Photonics, 1.6T port)"),
             ("Linear pluggable (LPO)", "Linear pluggable (LPO, 800G)"),
             ("DSP pluggable", "Pluggable DSP (800G)")]
    p = pd.DataFrame([dict(label=lab, kw=mods * float(op.loc[t, "watts_per_800g"]) / 1000, pj=float(op.loc[t, "pj_per_bit"]),
                           source_id=op.loc[t, "source_id"]) for lab, t in techs])
    claim = float(cv[(cv.record_type == "claim") & (cv.metric == "power")].value_low.iloc[0])
    cu = cv[cv["item"].str.startswith("800G passive copper")].iloc[0]
    ox = cv[cv["item"].str.startswith("800G DSP pluggable")].iloc[0]
    cost = pd.DataFrame([
        dict(label="Copper (DAC-equivalent)", lo=links * cu.value_low / 1e6, hi=links * cu.value_high / 1e6),
        dict(label="DSP optics (2 modules/link)", lo=mods * ox.value_low / 1e6, hi=mods * ox.value_high / 1e6),
    ])
    dsp_kw = float(p.kw.iloc[-1])
    c = Chart(
        id="05-nvl72-spine-copper-vs-optics",
        title=f"Est.: optics for an NVL72 spine would add ~{dsp_kw:.0f} kW and ~${((cost.lo + cost.hi) / 2).iloc[1]:.1f}M; copper adds ~0 W",
        subtitle=f"Optics power and media cost for 72 GPUs × 1.8 TB/s ({links:,.0f} 800G links, {mods:,.0f} modules); spine price not public",
        alt=(f"Two-panel chart. Left: power to drive an NVL72 spine of {links:,.0f} 800G links: passive copper about 0 kW beyond the "
             f"chips' SerDes, co-packaged optics about {p.kw.iloc[1]:.1f} kW, linear pluggables about {p.kw.iloc[2]:.0f} kW and DSP "
             f"pluggables about {dsp_kw:.0f} kW, matching NVIDIA's claim of {claim:.0f} kW saved. Right: media cost per rack about "
             f"${cost.lo.iloc[0]:.2f}-{cost.hi.iloc[0]:.2f}M for copper priced like 800G DACs versus ${cost.lo.iloc[1]:.2f}-"
             f"{cost.hi.iloc[1]:.2f}M for {mods:,.0f} DSP optical modules. All estimates."),
        data=[CVO, OPT], chapters=CH + ["06", "08"], source="NVIDIA (GTC 2024); vendor prices; repo calc",
        source_ids=sources_of(pd.concat([p[["source_id"]], cv[["source_id"]]])),
    )
    fig, axes = c.figure_grid(1, 2, width=11, height=5.2, gridspec_kw={"width_ratios": [1.25, 1]})
    ax = axes[0]
    y = np.arange(len(p))[::-1]
    cols = [NV, "#86B6EF", "#3987E5", "#104281"]
    ax.barh(y, p.kw, color=cols, height=0.6, zorder=2)
    for yi, (kw, pj) in zip(y, zip(p.kw, p.pj)):
        ax.text(kw + 0.4, yi, f"{kw:.1f} kW  ({pj:.1f} pJ/bit)", va="center", fontsize=8.6, color=INK["text"])
    ax.axvline(claim, color=INK["muted"], linestyle=":", linewidth=1.2)
    ax.text(claim - 0.3, y.max() + 0.45, f"NVIDIA: ~{claim:.0f} kW saved", fontsize=8, color=INK["muted"], ha="right")
    ax.set_yticks(y, p.label, fontsize=8.8)
    ax.set_xlim(0, 30)
    ax.set_ylim(-0.6, y.max() + 0.9)
    ax.set_xlabel("kW for the spine's optics")
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_title("Power", fontsize=10.5, color=INK["title"], loc="left")
    ax2 = axes[1]
    x = np.arange(len(cost))
    mid = (cost.lo + cost.hi) / 2
    ax2.bar(x, mid, color=[NV, "#104281"], width=0.55, zorder=2)
    ax2.errorbar(x, mid, yerr=[mid - cost.lo, cost.hi - mid], fmt="none", ecolor=INK["title"], capsize=6, lw=1.2, zorder=3)
    for xi, (lo, hi) in enumerate(zip(cost.lo, cost.hi)):
        ax2.annotate(f"${lo:.2f}–{hi:.2f}M", (xi, hi), xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8.6,
                     color=INK["text"])
    ax2.set_xticks(x, cost.label, fontsize=8.6)
    ax2.set_ylim(0, 1.0)
    ax2.set_ylabel("US$ millions per rack (Est.)")
    ax2.set_title("Media cost", fontsize=10.5, color=INK["title"], loc="left")
    _left_margin(fig, 0.19)
    fig.subplots_adjust(wspace=0.34)
    c.save(fig, list(axes), legend=False, top=0.80)


# --------------------------------------------------------------------------------------------------
# 7. MoE all-to-all time per decode step, by system (repo model) + DeepEP measured reference
# --------------------------------------------------------------------------------------------------
def _a2a_ms(nvlink: float, nic: float, dom: int, ep: int, tokens: int, hidden: int, topk: int, nbytes: float,
            layers: int) -> tuple[float, float]:
    """Bandwidth-only time (ms) for one decode step's MoE dispatch + combine on one GPU, and the off-domain share."""
    out_bytes = tokens * topk * hidden * nbytes  # dispatch (FP8) + combine (BF16) leaving this GPU per layer
    off = max(0, ep - dom) / ep
    inn = (min(ep, dom) - 1) / ep
    t = max(out_bytes * off / (nic * 1e9), out_bytes * inn / (nvlink * 1e9))
    return t * layers * 1e3, off


@register
def l05_moe_all_to_all_time():
    m = _moe()
    H = _mval(m, "DeepSeek-V3", "hidden_size")
    L = int(_mval(m, "DeepSeek-V3", "moe_layers"))
    K = int(_mval(m, "DeepSeek-V3", "activated_experts"))
    nb = _mval(m, "DeepSeek-V3", "dispatch_bytes_per_value") + _mval(m, "DeepSeek-V3", "combine_bytes_per_value")
    T = int(_mval(m, "repo all-to-all model", "tokens_per_gpu_per_step"))
    EP = int(_mval(m, "repo all-to-all model", "ep_degree"))
    systems = ["HGX H200 (8-GPU NVLink + 400G NIC)", "HGX B300 (8-GPU NVLink + 800G NIC)",
               "HGX Rubin NVL8 (8-GPU NVLink + 1.6T NIC)", "GB300 NVL72", "Vera Rubin NVL72"]
    rows = []
    for s in systems:
        ms, off = _a2a_ms(_mval(m, s, "nvlink_gbs_per_dir"), _mval(m, s, "nic_gbs_per_dir"), int(_mval(m, s, "domain_gpus")),
                          EP, T, H, K, nb, L)
        rows.append(dict(label=s, ms=ms, off=off, kind="nv72" if "NVL72" in s else "nvl8"))
    ll = m[(m.record_type == "deepep_low_latency") & (m["item"] == f"EP{EP}")]
    meas = float(ll.value.sum()) / 1000 * L
    rows.insert(0, dict(label=f"Measured: DeepEP on H800 + 400G IB (EP{EP})", ms=meas, off=np.nan, kind="measured"))
    d = pd.DataFrame(rows)
    h200 = d.set_index("label").loc["HGX H200 (8-GPU NVLink + 400G NIC)", "ms"]
    gb3 = d.set_index("label").loc["GB300 NVL72", "ms"]
    vr = d.set_index("label").loc["Vera Rubin NVL72", "ms"]
    used = m[m.record_type.isin(["model_config", "system_link", "scenario"]) | (m.record_type == "deepep_low_latency")]
    c = Chart(
        id="05-moe-all-to-all-time-by-system",
        title=f"Est.: a decode step's MoE all-to-all: ~{h200:.0f} ms on HGX H200, ~{gb3:.1f} ms on GB300 NVL72",
        subtitle=f"DeepSeek-V3-class model, {T} tokens per GPU, {EP}-way expert parallelism, {L} MoE layers; ms per step",
        alt=(f"Horizontal log-scale bar chart of estimated MoE dispatch-plus-combine time per decode step: HGX H200 about {h200:.0f} ms "
             f"(87.5% of expert traffic leaves the 8-GPU NVLink domain over a 400G NIC), HGX B300 about 11 ms, HGX Rubin NVL8 about "
             f"5.6 ms, GB300 NVL72 about {gb3:.1f} ms and Vera Rubin NVL72 about {vr:.1f} ms, where all 64 expert GPUs sit in one NVLink "
             f"domain. DeepEP's measured kernels on H800 with 400G InfiniBand take about {meas:.0f} ms, close to the model. A decode step "
             f"at DeepSeek's ~20 tokens/s per user lasts ~50 ms."),
        data=[MOE], chapters=CH + ["11", "P4"], source="DeepSeek-V3 config and DeepEP (GitHub); NVIDIA specs; repo model",
        source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=11, height=5.3)
    color = {"measured": DARKGREY, "nvl8": GEN_PAST, "nv72": NV}
    y = np.arange(len(d))[::-1]
    ax.barh(y, d.ms, color=[color[k] for k in d.kind], height=0.6, zorder=2)
    for yi, (ms, off, k) in zip(y, zip(d.ms, d.off, d.kind)):
        extra = "" if k == "measured" else f"   ({off:.1%} of expert traffic on the NIC)".replace(".0%", "%")
        ax.text(ms * 1.07, yi, f"{_ms(ms)}{extra}", va="center", fontsize=8.7, color=INK["text"])
    ax.set_yticks(y, d.label, fontsize=9)
    ax.set_xscale("log")
    ax.set_xlim(0.5, 400)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=GEN_PAST, label="8-GPU NVLink domain + NIC"), Patch(color=NV, label="72-GPU NVLink domain"),
                       Patch(color=DARKGREY, label="Measured (DeepEP)")], loc="lower right", fontsize=8.6)
    _left_margin(fig, 0.33)
    c.save(fig, ax, xlabel="ms of all-to-all per decode step (bandwidth-only model, no overlap)", logx=True, legend=False)


# --------------------------------------------------------------------------------------------------
# 8. DeepEP measured: NVLink vs RDMA bandwidth, and latency vs EP width
# --------------------------------------------------------------------------------------------------
@register
def l05_deepep_nvlink_vs_rdma():
    m = _moe()
    nb = m[m.record_type == "deepep_normal"].copy()
    piv = nb.pivot_table(index="item", columns="metric", values="value", sort=False).reset_index()
    piv["lab"] = [i.replace(" intranode", "\n").replace(" internode", "\n").replace("(", "").replace(")", "") for i in piv["item"]]
    ll = m[m.record_type == "deepep_low_latency"].copy()
    ll["ep"] = ll["item"].str.replace("EP", "").astype(int)
    lp = ll.pivot_table(index="ep", columns="metric", values="value").reset_index().sort_values("ep")
    nvl = float(piv.dispatch_bw.iloc[0])
    rd = piv.dispatch_bw.iloc[1:]
    c = Chart(
        id="05-deepep-nvlink-vs-rdma",
        title=f"MoE all-to-all measured at {nvl:.0f} GB/s over NVLink vs {rd.min():.0f}–{rd.max():.0f} GB/s over InfiniBand",
        subtitle="DeepEP on H800 (NVLink capped ~160 GB/s) + 400G InfiniBand: bandwidth (left), latency for 128 tokens (right)",
        alt=(f"Two-panel chart of DeepSeek's DeepEP measurements. Left: expert-parallel dispatch bandwidth {nvl:.0f} GB/s at EP8 inside "
             f"one NVLink node versus 43, 58 and 51 GB/s at EP16, EP32 and EP64 across InfiniBand (combine similar). Right: "
             f"low-latency kernels for a 128-token decode batch take 77 microseconds to dispatch and 114 to combine at EP8, rising to "
             f"about 194 and 360 microseconds at EP256. H800 is an export variant with NVLink cut to about 160 GB/s, so the gap on "
             f"H100 or Blackwell is wider."),
        data=[MOE], chapters=CH + ["06", "11"], source="DeepSeek DeepEP README v1.2.1 (GitHub)",
        source_ids=sources_of(m[m.record_type.isin(["deepep_normal", "deepep_low_latency"])]),
    )
    fig, axes = c.figure_grid(1, 2, width=11, height=5.2)
    ax = axes[0]
    x = np.arange(len(piv))
    w = 0.36
    cols = [NV] + [DARKGREY] * (len(piv) - 1)
    ax.bar(x - w / 2, piv.dispatch_bw, w, color=cols, zorder=2, label="Dispatch (FP8)")
    ax.bar(x + w / 2, piv.combine_bw, w, color=cols, alpha=0.55, zorder=2, label="Combine (BF16)")
    for xi, (a, b) in enumerate(zip(piv.dispatch_bw, piv.combine_bw)):
        ax.annotate(f"{a:.0f}", (xi - w / 2, a), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=8.4)
        ax.annotate(f"{b:.0f}", (xi + w / 2, b), xytext=(0, 2), textcoords="offset points", ha="center", fontsize=8.4)
    ax.set_xticks(x, piv.lab, fontsize=8.6)
    ax.set_ylabel("GB/s (bottleneck link)")
    ax.set_ylim(0, 190)
    ax.legend(handles=[Patch(color=GREY, label="Dispatch (solid) / combine (light)"), Patch(color=NV, label="NVLink"),
                       Patch(color=DARKGREY, label="RDMA (InfiniBand)")], loc="upper right", fontsize=8.2)
    ax.set_title("Throughput kernels (4,096 tokens)", fontsize=10.5, color=INK["title"], loc="left")
    ax2 = axes[1]
    ax2.plot(lp.ep, lp.dispatch_latency, color=DARKGREY, marker="o", label="Dispatch")
    ax2.plot(lp.ep, lp.combine_latency, color="#104281", marker="s", label="Combine")
    for e, v in zip(lp.ep, lp.combine_latency):
        ax2.annotate(f"{v:.0f}", (e, v), xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8)
    for e, v in zip(lp.ep, lp.dispatch_latency):
        ax2.annotate(f"{v:.0f}", (e, v), xytext=(0, -13), textcoords="offset points", ha="center", fontsize=8)
    ax2.set_xscale("log", base=2)
    ax2.set_xticks(list(lp.ep), [str(e) for e in lp.ep])
    ax2.minorticks_off()
    ax2.set_ylim(0, 420)
    ax2.set_xlabel("Expert-parallel width (GPUs, log2 scale)")  # QA 2026-11-05: log axis must say so
    ax2.set_ylabel("Microseconds per operation")
    ax2.legend(loc="lower right", fontsize=8.6)
    ax2.set_title("Low-latency kernels (128 tokens)", fontsize=10.5, color=INK["title"], loc="left")
    fig.subplots_adjust(wspace=0.28)
    c.save(fig, list(axes), legend=False, top=0.80, bottom=0.15)


# --------------------------------------------------------------------------------------------------
# 9. Same Blackwell silicon, different NVLink domain: B200 (8) vs GB200 NVL72 on DeepSeek-R1
# --------------------------------------------------------------------------------------------------
def _frontier(df: pd.DataFrame, system: str) -> pd.DataFrame:
    g = df[df.system == system].sort_values("interactivity_tok_s_per_user")
    return g


def _interp(g: pd.DataFrame, q: float) -> float:
    x = g.interactivity_tok_s_per_user.to_numpy()
    y = g.throughput_tok_s_per_gpu.to_numpy()
    if q < x.min() or q > x.max():
        return float("nan")
    return float(np.exp(np.interp(q, x, np.log(y))))


@register
def l05_nvl72_vs_nvl8_frontier():
    inf = load(INF)
    model = "DeepSeek-R1-0528 (1k in/1k out)"
    f = inf[inf.benchmark_suite.str.contains("Pareto frontier, no spec") & (inf.model == model)]
    b2 = _frontier(f, "B200")
    g2 = _frontier(f, "GB200 NVL72")
    h2 = _frontier(f, "H200")
    h2 = h2[h2.throughput_tok_s_per_gpu > 10]  # drop one degenerate tail point (2.7 tok/s/GPU)
    q1 = float(b2.interactivity_tok_s_per_user.iloc[0])
    r1 = _interp(g2, q1) / float(b2.throughput_tok_s_per_gpu.iloc[0])
    q2 = 90.0
    r2 = _interp(g2, q2) / _interp(b2, q2)
    c = Chart(
        id="05-nvl72-vs-nvl8-deepseek-frontier",
        title=f"9× bigger NVLink domain, same GPU: ~{r1:.1f}× throughput at {q1:.0f} tok/s/user, ~{r2:.1f}× at {q2:.0f}",
        subtitle="DeepSeek-R1 1k/1k, best published configs (SemiAnalysis InferenceX): tokens/s per GPU vs per user",
        alt=(f"Log-scale line chart of throughput per GPU against interactivity for DeepSeek-R1. GB200 NVL72 (72-GPU NVLink domain, FP4) "
             f"reaches about 6,700-7,100 tokens/s per GPU at 21-45 tokens/s per user and about {r1:.1f} times B200's 8-GPU servers at "
             f"~{q1:.0f} tokens/s per user, but the curves cross near {q2:.0f} tokens/s per user (ratio {r2:.2f}) and B200 is ahead at "
             f"higher interactivity. H200 (FP8) sits far below both. Frontier points come from different dates and software versions."),
        data=[INF], chapters=CH + ["11"], source="SemiAnalysis InferenceX public-API snapshot", source_ids=sources_of(pd.concat([b2, g2, h2])),
    )
    fig, ax = c.figure(width=11, height=5.6)
    ax.plot(h2.interactivity_tok_s_per_user, h2.throughput_tok_s_per_gpu, color=GREY, marker="o", markersize=6,
            label="H200 · 8-GPU NVLink 4 · FP8")
    ax.plot(b2.interactivity_tok_s_per_user, b2.throughput_tok_s_per_gpu, color=GEN_PAST, marker="s", markersize=7,
            label="B200 · 8-GPU NVLink 5 · FP4")
    ax.plot(g2.interactivity_tok_s_per_user, g2.throughput_tok_s_per_gpu, color=NV, marker="o", markersize=7,
            label="GB200 NVL72 · 72-GPU NVLink 5 · FP4")
    ax.axvline(q1, color=INK["muted"], linestyle=":", linewidth=1)
    ax.annotate(f"~{r1:.1f}× at {q1:.0f} tok/s/user", (q1, _interp(g2, q1)), xytext=(10, 18), textcoords="offset points",
                fontsize=8.8, color=NV_DARK, arrowprops=dict(arrowstyle="->", color=NV_DARK, lw=1))
    ax.annotate(f"curves cross near {q2:.0f}", (q2, _interp(b2, q2)), xytext=(18, 26), textcoords="offset points", fontsize=8.6,
                color=INK["text"], arrowprops=dict(arrowstyle="->", color=INK["text"], lw=1))
    ax.set_yscale("log")
    ax.set_xlim(10, 180)
    ax.set_ylim(1, 20000)
    ax.legend(loc="lower left", fontsize=8.8)
    ax.text(178, 1.4, "Each point = best config at its date;\nsoftware maturity differs by date", ha="right", fontsize=8.2,
            color=INK["muted"])
    c.save(fig, ax, xlabel="Interactivity, tokens/s per user", ylabel="Throughput, tokens/s per GPU", logy=True, legend=False)


# --------------------------------------------------------------------------------------------------
# 10. Switched vs torus: uniform all-to-all bandwidth per chip vs number of chips (repo model)
# --------------------------------------------------------------------------------------------------
def _switched(n: np.ndarray, nvl: float, nic: float, dom: int) -> np.ndarray:
    out = []
    for N in n:
        if N <= dom:
            out.append(nvl)
            continue
        f_out = (N - dom) / (N - 1)
        f_in = (dom - 1) / (N - 1)
        out.append(min(nvl, nic / f_out, nvl / f_in))
    return np.array(out)


def _torus(n: np.ndarray, bidir_per_chip: float, links: int) -> np.ndarray:
    b = bidir_per_chip / links / 2  # GB/s per link per direction
    k = n ** (1 / 3)
    return np.minimum(8 * b / k, links * b)


@register
def l05_torus_vs_switched():
    ic = load(IC).set_index("generation")
    nv5 = ic.loc["NVLink 5 (GB200 NVL72)"]
    nv6 = ic.loc["NVLink 6 (Vera Rubin NVL72)"]
    iw = ic.loc["ICI (TPU7x Ironwood)"]
    t8 = ic.loc["ICI (TPU 8t)"]
    e800 = ic.loc["800GbE (IEEE 802.3df, 8x100G)"]
    e16 = ic.loc["1.6TbE (IEEE 802.3dj, 8x200G)"]
    n = np.unique(np.round(np.logspace(np.log10(8), np.log10(9216), 120)).astype(int))
    nt = n[n >= 64]
    s_gb = _switched(n, nv5.per_device_bw_gbs_bidir / 2, e800.per_device_bw_gbs_bidir / 2, 72)
    s_hgx = _switched(n, nv5.per_device_bw_gbs_bidir / 2, e800.per_device_bw_gbs_bidir / 2, 8)
    s_vr = _switched(n, nv6.per_device_bw_gbs_bidir / 2, e16.per_device_bw_gbs_bidir / 2, 72)
    t_iw = _torus(nt, float(iw.per_device_bw_gbs_bidir), int(iw.lanes_or_links_per_device))
    t_8t = _torus(nt, float(t8.per_device_bw_gbs_bidir), 6)
    iw64 = float(_torus(np.array([64]), float(iw.per_device_bw_gbs_bidir), 6)[0])
    iwmax = float(_torus(np.array([9216]), float(iw.per_device_bw_gbs_bidir), 6)[0])
    gbmax = float(_switched(np.array([9216]), 900, 100, 72)[0])
    ids = sources_of(pd.DataFrame({"source_id": [nv5.source_id, nv6.source_id, iw.source_id, t8.source_id, e800.source_id,
                                                 e16.source_id]}))
    c = Chart(
        id="05-torus-vs-switched-all-to-all",
        title=f"Est.: all-to-all bandwidth per chip is 900 GB/s in NVL72, ~{iw64:.0f} in a 64-chip TPU cube",
        subtitle="Uniform all-to-all GB/s per chip per direction vs chips exchanging; bandwidth-only repo model",
        alt=(f"Log-log line chart of modeled all-to-all bandwidth per chip. A switched GB300-class NVL72 gives 900 GB/s per direction "
             f"to every GPU up to 72 GPUs, then falls to the 800G NIC's ~100 GB/s ({gbmax:.0f} GB/s at 9,216 GPUs); an 8-GPU HGX node "
             f"drops to ~100 GB/s beyond 8 GPUs; Vera Rubin NVL72 starts at 1,500 and settles near 200 with 1.6T NICs. A TPU Ironwood "
             f"3D torus (1.2 TB/s over six links) delivers about {iw64:.0f} GB/s in a 64-chip cube, falling with the cube root of chip "
             f"count to about {iwmax:.0f} at 9,216; TPU 8t doubles that. Torus links carry multi-hop traffic, which switched fabrics avoid."),
        data=[IC], chapters=CH + ["15", "06"], source="NVIDIA, Google Cloud, IEEE specs; repo model", source_ids=ids,
    )
    fig, ax = c.figure(width=11, height=5.7)
    ax.plot(n, s_vr, color=NV, linestyle="--", label="Vera Rubin NVL72 + 1.6T NIC (switched)")
    ax.plot(n, s_gb, color=NV, label="GB300 NVL72 + 800G NIC (switched)")
    ax.plot(n, s_hgx, color=GEN_PAST, label="HGX B300 8-GPU + 800G NIC (switched)")
    ax.plot(nt, t_8t, color=entity_color("Google"), linestyle="--", label="TPU 8t 3D torus (2.4 TB/s ICI)")
    ax.plot(nt, t_iw, color=entity_color("Google"), label="TPU Ironwood 3D torus (1.2 TB/s ICI)")
    for xv, lab in ((72, "72"), (9216, "9,216")):
        ax.axvline(xv, color=INK["grid"], linewidth=1, zorder=0)
        ax.text(xv, 2600, lab, ha="center", fontsize=8, color=INK["muted"])
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(7, 12000)
    ax.set_ylim(20, 3000)
    # QA 2026-11-05: legend moved off the HGX curve into the empty upper-right region
    ax.legend(loc="upper right", bbox_to_anchor=(0.88, 0.93), fontsize=8.4)
    ax.text(11500, 23, "Torus: 8b/k per chip (b = link GB/s each way, k = chips^(1/3)); ignores OCS twisting\n"
            "and expert placement. Switched: non-blocking NIC fat tree beyond the NVLink domain.", ha="right",
            fontsize=7.8, color=INK["muted"])
    c.save(fig, ax, xlabel="Chips in the all-to-all exchange", ylabel="All-to-all GB/s per chip per direction", logy=True, logx=True,
           legend=False)


# --------------------------------------------------------------------------------------------------
# 11. NVLink Fusion partner timeline
# --------------------------------------------------------------------------------------------------
@register
def l05_fusion_partner_timeline():
    d = load(FUS)
    d["date"] = pd.to_datetime(d.announce_date)
    cats = ["Design services and IP", "EDA tools", "Connectivity and optics", "CPUs", "Accelerators"]
    d["y"] = [len(cats) - 1 - cats.index(cv) for cv in d.category]
    launch = int((d.announce_date == "2025-05-19").sum())
    d["grp"] = d.announce_date.str[:7] + "|" + d.category
    d["k"] = d.groupby("grp").cumcount()
    d["n"] = d.groupby("grp")["partner"].transform("count")
    d["yp"] = d.y + 0.2 * ((d.n - 1) / 2 - d.k)
    c = Chart(
        id="05-nvlink-fusion-partner-timeline",
        title=f"NVLink Fusion: {launch} launch partners, {len(d)} by June 2026, one hyperscale XPU",
        subtitle="Publicly announced NVLink Fusion partners by category and announcement date (filled = company-confirmed, hollow = reported)",
        alt=(f"Timeline dot chart of NVLink Fusion partners. At launch on 19 May 2025: MediaTek, Marvell and Alchip (design services), "
             f"Synopsys and Cadence (EDA), Astera Labs (connectivity), Qualcomm and Fujitsu (CPUs). Later: Intel x86 CPUs (Sept 2025), "
             f"Arm Neoverse (Nov 2025), AWS Trainium4 (Dec 2025, the only hyperscaler accelerator) and, as reported but not confirmed, "
             f"Ayar Labs and Lightmatter for optics (June 2026). AMD, Broadcom and Google are absent."),
        data=[FUS], chapters=CH + ["13", "04"], source="NVIDIA; partner and press reports", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    for r in d.itertuples():
        col = entity_color(r.partner.split(" ")[0])
        if col == entity_color("other"):
            col = DARKGREY
        hollow = r.confidence != "confirmed"
        ax.scatter(r.date, r.yp, s=110, facecolors="white" if hollow else col, edgecolors=col, linewidths=1.8, zorder=3)
        ax.annotate(r.partner, (r.date, r.yp), xytext=(9, 0), textcoords="offset points", fontsize=8.4,
                    color=INK["title"], va="center")
    ax.set_yticks(range(len(cats)), cats[::-1], fontsize=9)
    ax.set_ylim(-0.7, len(cats) - 0.2)
    ax.set_xlim(pd.Timestamp("2025-04-01"), pd.Timestamp("2026-10-01"))
    ax.axvline(pd.Timestamp("2025-05-19"), color=INK["grid"], linewidth=1, zorder=0)
    ax.grid(axis="x")
    ax.legend(handles=[Line2D([], [], marker="o", color="w", markerfacecolor=DARKGREY, markeredgecolor=DARKGREY, markersize=9,
                              label="Company-confirmed"),
                       Line2D([], [], marker="o", color="w", markerfacecolor="white", markeredgecolor=DARKGREY, markersize=9,
                              label="Reported only")], loc="lower right", fontsize=8.6)
    _left_margin(fig, 0.2)
    c.save(fig, ax, xlabel="Announcement date", legend=False)
