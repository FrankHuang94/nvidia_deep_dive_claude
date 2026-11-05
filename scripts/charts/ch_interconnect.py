"""Scale-up interconnect charts (layer 05) and link-speed charts (layer 06), owned by agent A2.

Data: data/interconnect_specs.csv and data/networking_products.csv (both owned by A2).
Helpers below (log axes with plain tick labels, status legend, fixed-position axes for long
horizontal-bar labels) live here because style.py is shared and must not be edited.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, hatch_future, load, register,
                   sources_of)

IC_FILE = "interconnect_specs.csv"
NP_FILE = "networking_products.csv"
NEUTRAL = INK["text"]          # industry-standard (vendor-neutral) series, e.g. PCIe / Ethernet


# ---------------------------------------------------------------------------------------------- helpers
def log_axis(fig, ax, axis: str = "y") -> None:
    """Log scale with plain-number ticks (mathtext is disabled repo-wide) + the LOG SCALE badge.
    Use instead of Chart.save(logy=True), whose set_yscale() call would reset the formatter."""
    (ax.set_yscale if axis == "y" else ax.set_xscale)("log")
    a = ax.yaxis if axis == "y" else ax.xaxis
    a.set_major_locator(LogLocator(base=10, numticks=12))
    a.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}" if v >= 1 else f"{v:g}"))
    a.set_minor_formatter(NullFormatter())
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


def status_handles(shipping_label: str = "Shipping", future_label: str = "Announced / roadmap") -> list:
    return [Patch(facecolor="#8C8C8C", label=shipping_label),
            Patch(facecolor="#8C8C8C", hatch="///", edgecolor="#FFFFFF", alpha=0.75, label=future_label)]


def fixed_axes(c: Chart, width: float, height: float, rect: tuple[float, float, float, float]):
    """Figure with an axes at a fixed position (not moved by Chart.save's subplots_adjust)."""
    fig, ax0 = c.figure(width=width, height=height)
    ax0.remove()
    ax = fig.add_axes(rect)
    return fig, ax


def _ic() -> pd.DataFrame:
    return load(IC_FILE)


def _row(df: pd.DataFrame, generation: str) -> pd.Series:
    m = df[df.generation == generation]
    if m.empty:
        raise KeyError(generation)
    return m.iloc[0]


def _tb(v_gbs: float) -> str:
    """GB/s -> 'x.x' / 'x.xx' TB/s label without spurious trailing zeros."""
    s = f"{v_gbs / 1000:.2f}".rstrip("0")
    return s + "0" if s.endswith(".") else s


def _fmt_gbs(v: float) -> str:
    return f"{v / 1000:.1f} TB/s" if v >= 1000 else f"{v:,.0f} GB/s"


# ---------------------------------------------------------------------------------------------- 05-nvlink-vs-pcie-bandwidth
NVLINK_MAIN = ["NVLink 1", "NVLink 2", "NVLink 3", "NVLink 4 (HGX H100 NVL8)", "NVLink 5 (GB200 NVL72)",
               "NVLink 6 (Vera Rubin NVL72)", "NVLink 7 (Rubin Ultra Kyber NVL144)"]
NVLINK_SHORT = {"NVLink 1": ("NVLink 1", "P100"), "NVLink 2": ("NVLink 2", "V100"), "NVLink 3": ("NVLink 3", "A100"),
                "NVLink 4 (HGX H100 NVL8)": ("NVLink 4", "H100"), "NVLink 5 (GB200 NVL72)": ("NVLink 5", "B200"),
                "NVLink 6 (Vera Rubin NVL72)": ("NVLink 6", "Rubin"),
                "NVLink 7 (Rubin Ultra Kyber NVL144)": ("NVLink 7", "Rubin Ultra")}


@register
def nvlink_vs_pcie_bandwidth():
    df = _ic()
    nv = pd.DataFrame([_row(df, g) for g in NVLINK_MAIN])
    pc = df[df.family == "PCIe"].sort_values("year")
    nv1, nv6 = _row(df, "NVLink 1"), _row(df, "NVLink 6 (Vera Rubin NVL72)")
    g3, g6, g7 = _row(df, "PCIe 3.0"), _row(df, "PCIe 6.0"), _row(df, "PCIe 7.0")
    nv_mult = nv6.per_device_bw_gbs_bidir / nv1.per_device_bw_gbs_bidir
    pc_mult = g6.per_device_bw_gbs_bidir / g3.per_device_bw_gbs_bidir
    used = pd.concat([nv, pc])
    c = Chart(
        id="05-nvlink-vs-pcie-bandwidth",
        title=(f"NVLink per-GPU bandwidth grew ~{nv_mult:.0f}× from {int(nv1.year)} to {int(nv6.year)}; "
               f"the PCIe x16 link GPUs use grew {pc_mult:.0f}×"),
        subtitle="Bidirectional GB/s per GPU (NVLink, by GPU launch year) vs one PCIe x16 slot (by specification year)",
        alt=(f"Log-scale line chart: NVLink bandwidth per GPU rose from {nv1.per_device_bw_gbs_bidir:.0f} GB/s (P100, {int(nv1.year)}) "
             f"to {nv6.per_device_bw_gbs_bidir:,.0f} GB/s (Rubin, {int(nv6.year)}), about {nv_mult:.0f} times, while PCIe x16 rose from "
             f"{g3.per_device_bw_gbs_bidir:.0f} GB/s (Gen3) to {g6.per_device_bw_gbs_bidir:.0f} GB/s (Gen6, used by 2025-26 GPUs), "
             f"{pc_mult:.0f} times; PCIe 7.0 ({g7.per_device_bw_gbs_bidir:.0f} GB/s) is ratified but not yet in GPUs."),
        data=[IC_FILE], chapters=["05", "04", "P3"],
        source="NVIDIA whitepapers and NVLink page; PCI-SIG", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=12, height=6.2)
    shipped, road = nv[nv.year <= 2026], nv[nv.year > 2026]
    ax.plot(shipped.year, shipped.per_device_bw_gbs_bidir, color=NV, marker="o", ms=8, lw=2.4, label="NVLink per GPU", zorder=4)
    ax.plot([shipped.year.iloc[-1], road.year.iloc[0]], [shipped.per_device_bw_gbs_bidir.iloc[-1], road.per_device_bw_gbs_bidir.iloc[0]],
            color=NV, lw=2, ls="--", zorder=3)
    ax.plot(road.year, road.per_device_bw_gbs_bidir, ls="none", marker="o", ms=9, mfc="white", mec=NV, mew=2, zorder=4,
            label="NVLink roadmap (reported)")
    for _, r in nv.iterrows():
        gen, gpu = NVLINK_SHORT[r.generation]
        if gen == "NVLink 7":
            ax.annotate(f"{gen} · {gpu}\n{_fmt_gbs(r.per_device_bw_gbs_bidir)} (2027)", (r.year, r.per_device_bw_gbs_bidir),
                        xytext=(8, 4), textcoords="offset points", ha="left", va="bottom", fontsize=8.5, color=NV_DARK)
        else:
            ax.annotate(f"{gen} · {gpu}\n{_fmt_gbs(r.per_device_bw_gbs_bidir)}", (r.year, r.per_device_bw_gbs_bidir),
                        xytext=(-6, 8), textcoords="offset points", ha="right", va="bottom", fontsize=8.5, color=NV_DARK)
    pc_ok, pc_f = pc[pc.year <= 2025], pc[pc.year > 2025]
    ax.plot(pc_ok.year, pc_ok.per_device_bw_gbs_bidir, color=NEUTRAL, marker="s", ms=7, lw=2, label="PCIe x16 (spec year)", zorder=3)
    ax.plot([pc_ok.year.iloc[-1], pc_f.year.iloc[0]], [pc_ok.per_device_bw_gbs_bidir.iloc[-1], pc_f.per_device_bw_gbs_bidir.iloc[0]],
            color=NEUTRAL, lw=1.6, ls="--")
    ax.plot(pc_f.year, pc_f.per_device_bw_gbs_bidir, ls="none", marker="s", ms=8, mfc="white", mec=NEUTRAL, mew=2,
            label="PCIe 8.0 (2028 target)")
    for _, r in pc.iterrows():
        ax.annotate(f"{r.generation.replace('PCIe ', 'Gen ')}\n{r.per_device_bw_gbs_bidir:,.0f}", (r.year, r.per_device_bw_gbs_bidir),
                    xytext=(0, -10), textcoords="offset points", ha="center", va="top", fontsize=8.2, color=NEUTRAL)
    ax.text(0.99, 0.03, f"NVLink 6: {nv6.per_device_bw_gbs_bidir:,.0f} GB/s is the production spec (Sept 2026);\n"
            "3,600 GB/s was announced at CES 2026. PCIe 7.0 is ratified but not yet in GPUs.",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8.2, color=INK["muted"])
    ax.set_xlim(2009, 2030)
    ax.set_ylim(10, 20000)
    ax.set_xticks(range(2010, 2031, 2))
    log_axis(fig, ax)
    ax.legend(loc="upper left")
    c.save(fig, ax, xlabel="Year (NVLink: first GPU; PCIe: specification release)",
           ylabel="Bidirectional bandwidth, GB/s (log scale)", legend=False)


# ---------------------------------------------------------------------------------------------- 05-nvlink-generations
@register
def nvlink_generations():
    df = _ic()
    nv = pd.DataFrame([_row(df, g) for g in NVLINK_MAIN]).reset_index(drop=True)
    labels = [f"{NVLINK_SHORT[g][0]}\n{NVLINK_SHORT[g][1]}\n{int(y)}" for g, y in zip(nv.generation, nv.year)]
    first, cur = nv.iloc[0], nv[nv.generation.str.startswith("NVLink 6")].iloc[0]
    mult = cur.per_device_bw_gbs_bidir / first.per_device_bw_gbs_bidir
    gens = int(cur.generation.split()[1]) - int(first.generation.split()[1])
    c = Chart(
        id="05-nvlink-generations",
        title=(f"NVLink per-GPU bandwidth rose {mult:.0f}× in {gens} generations, from {first.per_device_bw_gbs_bidir:.0f} GB/s "
               f"(P100) to {cur.per_device_bw_gbs_bidir:,.0f} GB/s (Rubin)"),
        subtitle="Left: bidirectional GB/s per GPU. Right: NVLink links per GPU × bidirectional GB/s per link",
        alt=(f"Two-panel bar chart of NVLink generations 1 to 7: per-GPU bandwidth {', '.join(f'{v:,.0f}' for v in nv.per_device_bw_gbs_bidir)} GB/s; "
             f"links per GPU 4, 6, 12, 18, 18 and 36 (NVLink 6 doubles links, with Rubin's production spec cut from 3.6 to 3.0 TB/s); "
             f"NVLink 7 (Rubin Ultra, 2027) is a reported 3.6 TB/s roadmap figure."),
        data=[IC_FILE], chapters=["05", "02"],
        source="NVIDIA whitepapers, NVLink page; SemiAnalysis", source_ids=sources_of(nv),
    )
    fig, axes = c.figure_grid(1, 2, width=12, height=6.2, gridspec_kw={"width_ratios": [1.25, 1]})
    ax, ax2 = axes
    x = np.arange(len(nv))
    is_road = (nv.year > 2026).to_numpy()
    colors = [NV if (g.startswith("NVLink 6") or r) else GEN_PAST for g, r in zip(nv.generation, is_road)]
    bars = ax.bar(x, nv.per_device_bw_gbs_bidir, color=colors, width=0.66)
    hatch_future(bars, is_road)
    for b, v in zip(bars, nv.per_device_bw_gbs_bidir):
        ax.annotate(f"{v:,.0f}", (b.get_x() + b.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=8.8, color=INK["text"])
    ax.set_xticks(x, labels, fontsize=8.3)
    ax.set_ylim(0, nv.per_device_bw_gbs_bidir.max() * 1.18)
    ax.set_ylabel("GB/s per GPU (bidirectional)")
    ax.annotate("cut from 3,600\n(Sept 2026)", (x[5], cur.per_device_bw_gbs_bidir), xytext=(-92, 26), textcoords="offset points",
                fontsize=8, color=INK["muted"], arrowprops=dict(arrowstyle="->", color=INK["muted"], lw=0.8))
    ax.legend(handles=status_handles("Shipping", "Roadmap (reported)"), loc="upper left")
    lk = nv[nv.lanes_or_links_per_device.notna()]
    x2 = np.arange(len(lk))
    bars2 = ax2.bar(x2, lk.lanes_or_links_per_device, width=0.62,
                    color=[NV if g.startswith("NVLink 6") else GEN_PAST for g in lk.generation])
    for b, (_, r) in zip(bars2, lk.iterrows()):
        per_link = r.per_device_bw_gbs_bidir / r.lanes_or_links_per_device
        ax2.annotate(f"{int(r.lanes_or_links_per_device)} ×\n{per_link:.0f} GB/s", (b.get_x() + b.get_width() / 2, b.get_height()),
                     xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.2, color=INK["text"])
    ax2.set_xticks(x2, [labels[i] for i in lk.index], fontsize=8.3)
    ax2.set_ylim(0, lk.lanes_or_links_per_device.max() * 1.3)
    ax2.set_ylabel("NVLink links per GPU")
    ax2.text(0.02, 0.97, "NVLink 7 link count not published", transform=ax2.transAxes, ha="left", va="top",
             fontsize=8, color=INK["muted"])
    fig.subplots_adjust(wspace=0.22)
    c.save(fig, [ax, ax2], legend=False, bottom=0.17)


# ---------------------------------------------------------------------------------------------- 05-scale-up-domain-size-by-vendor
# (generation row, label, vendor, status)  status: shipping | announced | roadmap | spec
DOMAINS = [
    ("NVLink 4 (HGX H100 NVL8)", "NVIDIA HGX H100 (NVL8)", "NVIDIA", "shipping"),
    ("NVLink 4 (NVLink Switch System, DGX GH200)", "NVIDIA DGX GH200 (2023, limited)", "NVIDIA", "shipping"),
    ("NVLink 5 (GB200 NVL72)", "NVIDIA GB200 / GB300 NVL72", "NVIDIA", "shipping"),
    ("NVLink 6 (Vera Rubin NVL72)", "NVIDIA Vera Rubin NVL72 (2026)", "NVIDIA", "shipping"),
    ("NVLink 7 (Rubin Ultra Kyber NVL144)", "NVIDIA Rubin Ultra Kyber NVL144 (2027)", "NVIDIA", "roadmap"),
    ("NVLink 7 (Rubin Ultra NVL576, 8 racks)", "NVIDIA Rubin Ultra NVL576 (2027)", "NVIDIA", "roadmap"),
    ("NVLink 8 CPO (Feynman Kyber NVL1152)", "NVIDIA Feynman NVL1152 (2028)", "NVIDIA", "roadmap"),
    ("Infinity Fabric / xGMI (MI355X)", "AMD MI355X platform (mesh)", "AMD", "shipping"),
    ("UALoE (Helios, MI455X)", "AMD Helios MI455X (2026)", "AMD", "shipping"),
    ("NeuronLink-v3 (Trn2 UltraServer)", "AWS Trn2 UltraServer (torus)", "AWS", "shipping"),
    ("NeuronLink-v4 + NeuronSwitch-v1 (Trn3 UltraServer)", "AWS Trn3 UltraServer", "AWS", "shipping"),
    ("UnifiedBus (CloudMatrix 384, Ascend 910C)", "Huawei CloudMatrix 384", "Huawei", "shipping"),
    ("UnifiedBus 2.0 (Atlas 950 SuperPoD, Ascend 950)", "Huawei Atlas 950 SuperPoD (Q4 2026)", "Huawei", "announced"),
    ("UnifiedBus (Atlas 960 SuperPoD, Ascend 960)", "Huawei Atlas 960 SuperPoD (Q4 2027)", "Huawei", "roadmap"),
    ("ICI (TPU 8i, Boardfly)", "Google TPU 8i pod (2026)", "Google", "announced"),
    ("ICI (TPU v5p)", "Google TPU v5p pod (torus)", "Google", "shipping"),
    ("ICI (TPU7x Ironwood)", "Google Ironwood superpod (torus)", "Google", "shipping"),
    ("ICI (TPU 8t)", "Google TPU 8t superpod (2026, torus)", "Google", "announced"),
    ("UALink 200G 1.0", "UALink 1.0 specification maximum", "industry", "spec"),
]


@register
def scale_up_domain_size_by_vendor():
    df = _ic()
    rows = []
    for gen, label, vendor, status in DOMAINS:
        r = _row(df, gen)
        rows.append(dict(label=label, vendor=vendor, status=status, n=r.max_domain_size, source_id=r.source_id))
    d = pd.DataFrame(rows)
    ship = d[d.status == "shipping"]
    nv_now = int(ship[(ship.vendor == "NVIDIA") & ship.label.str.contains("NVL72")]["n"].max())
    aws = int(ship[ship.vendor == "AWS"]["n"].max())
    hw = int(ship[ship.vendor == "Huawei"]["n"].max())
    gg = int(ship[ship.vendor == "Google"]["n"].max())
    c = Chart(
        id="05-scale-up-domain-size-by-vendor",
        title=f"NVIDIA's {nv_now}-GPU NVLink domain trails AWS ({aws}), Huawei ({hw}) and Google TPU pods ({gg:,}) in size",
        subtitle="Accelerators per scale-up domain, shipping vs announced. Topologies differ (box): bigger is not automatically better",
        alt=(f"Horizontal log-scale bar chart of scale-up domain sizes: NVIDIA NVL72 {nv_now} GPUs today, Kyber NVL144 and NVL576 in 2027 "
             f"and NVL1152 in 2028 (roadmap); AMD Helios 72; AWS Trn3 UltraServer {aws}; Huawei CloudMatrix {hw} and Atlas 950 8,192 "
             f"(Q4 2026); Google Ironwood {gg:,} and TPU 8t 9,600 chips, though TPU pods are multi-hop tori rather than switched all-to-all; "
             f"UALink 1.0 allows 1,024."),
        data=[IC_FILE], chapters=["05", "15", "CS3"],
        source="NVIDIA, AMD, AWS, Google, Huawei, UALink; analysts", source_ids=sources_of(d),
    )
    fig, ax = fixed_axes(c, 12.5, 7.8, (0.255, 0.115, 0.715, 0.72))
    y = np.arange(len(d))[::-1]
    bars = ax.barh(y, d["n"], color=[entity_color(v) for v in d.vendor], height=0.68)
    hatch_future(bars, d.status.isin(["announced", "roadmap", "spec"]))
    for b, v in zip(bars, d["n"]):
        ax.annotate(f"{int(v):,}", (v, b.get_y() + b.get_height() / 2), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.6, color=INK["text"])
    ax.set_yticks(y, d.label, fontsize=8.8)
    for t, v in zip(ax.get_yticklabels(), d.vendor):
        t.set_color(INK["title"] if v == "NVIDIA" else INK["text"])
    ax.set_xlim(4, 300000)
    log_axis(fig, ax, "x")
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.text(0.99, 0.985,
            "Not like-for-like:\n• NVLink, NeuronSwitch (Trn3), UB and UALink: switched,\n  single-hop all-to-all fabrics\n"
            "• TPU pods and Trn2: tori (multi-hop; per-chip links feed\n  neighbours; TPU tori re-wired by optical switches)\n"
            "• AMD MI355X: 8-GPU direct mesh, no switch",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=INK["text"], multialignment="left",
            bbox=dict(boxstyle="round,pad=0.4", fc="#F7F7F4", ec=INK["grid"]))
    ax.legend(handles=status_handles("Shipping", "Announced / roadmap / spec"), loc="lower right")
    c.save(fig, ax, xlabel="Accelerators in one scale-up domain (log scale)", legend=False)


# ---------------------------------------------------------------------------------------------- 05-scale-up-bandwidth-per-accelerator-by-vendor
BW_ROWS = [
    ("NVLink 5 (GB200 NVL72)", "NVIDIA B200 / B300 (NVLink 5)", "NVIDIA", "shipping"),
    ("NVLink 6 (Vera Rubin NVL72)", "NVIDIA Rubin (NVLink 6, 2026)", "NVIDIA", "shipping"),
    ("NVLink 7 (Rubin Ultra Kyber NVL144)", "NVIDIA Rubin Ultra (NVLink 7, 2027)", "NVIDIA", "roadmap"),
    ("Infinity Fabric / xGMI (MI355X)", "AMD MI355X (Infinity Fabric)", "AMD", "shipping"),
    ("UALoE (Helios, MI455X)", "AMD MI455X (Helios UALoE, 2026)", "AMD", "shipping"),
    ("ICI (TPU7x Ironwood)", "Google Ironwood (ICI)", "Google", "shipping"),
    ("ICI (TPU 8t)", "Google TPU 8t (ICI, 2026)", "Google", "announced"),
    ("NeuronLink-v3 (Trn2 UltraServer)", "AWS Trainium2 (NeuronLink-v3)", "AWS", "shipping"),
    ("NeuronLink-v4 + NeuronSwitch-v1 (Trn3 UltraServer)", "AWS Trainium3 (NeuronLink-v4)", "AWS", "shipping"),
    ("UnifiedBus (CloudMatrix 384, Ascend 910C)", "Huawei Ascend 910C (UB)", "Huawei", "shipping"),
    ("UnifiedBus 2.0 (Atlas 950 SuperPoD, Ascend 950)", "Huawei Ascend 950 (UB 2.0, Q4 2026)", "Huawei", "announced"),
    ("Gaudi 3 integrated 200GbE RoCE", "Intel Gaudi 3 (24 × 200GbE RoCE)", "Intel", "shipping"),
]


@register
def scale_up_bandwidth_per_accelerator_by_vendor():
    df = _ic()
    d = pd.DataFrame([dict(label=lab, vendor=v, status=s, bw=_row(df, g).per_device_bw_gbs_bidir,
                           source_id=_row(df, g).source_id) for g, lab, v, s in BW_ROWS])
    nv = d[d.label.str.contains("NVLink 6")].bw.iloc[0]
    amd = d[d.label.str.contains("MI455X")].bw.iloc[0]
    others = d[d.label.str.contains("TPU 8t|Trainium3|Ascend 950")]
    lo, hi = others.bw.min() / 1000, others.bw.max() / 1000
    c = Chart(
        id="05-scale-up-bandwidth-per-accelerator-by-vendor",
        title=(f"AMD's Helios ({amd / 1000:.1f} TB/s per GPU) now out-specs NVIDIA Rubin's production NVLink 6 "
               f"({nv / 1000:.1f} TB/s)"),
        subtitle=(f"Scale-up bandwidth per accelerator, bidirectional TB/s. Google, AWS and Huawei next-gen parts: "
                  f"{lo:.1f}–{hi:.1f} TB/s"),
        alt=(f"Horizontal bar chart of scale-up bandwidth per accelerator: NVIDIA Blackwell 1.8 TB/s, Rubin {nv / 1000:.1f} TB/s "
             f"(cut from 3.6 TB/s) and Rubin Ultra 3.6 TB/s (roadmap); AMD MI355X 1.1 TB/s and MI455X {amd / 1000:.1f} TB/s; "
             f"Google Ironwood 1.2 and TPU 8t 2.4 TB/s; AWS Trainium2 1.0 and Trainium3 2.0 TB/s; Huawei Ascend 910C 0.8 and "
             f"Ascend 950 2.0 TB/s; Intel Gaudi 3 1.2 TB/s."),
        data=[IC_FILE], chapters=["05", "15"],
        source="NVIDIA, AMD, Google, AWS, Huawei, Intel; SemiAnalysis", source_ids=sources_of(d),
    )
    fig, ax = fixed_axes(c, 12.5, 6.9, (0.245, 0.12, 0.725, 0.71))
    y = np.arange(len(d))[::-1]
    bars = ax.barh(y, d.bw / 1000, color=[entity_color(v) for v in d.vendor], height=0.66)
    hatch_future(bars, d.status.isin(["announced", "roadmap"]))
    for b, v in zip(bars, d.bw):
        ax.annotate(_tb(v), (v / 1000, b.get_y() + b.get_height() / 2), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=8.8, color=INK["text"])
    ax.set_yticks(y, d.label, fontsize=8.8)
    for t, v in zip(ax.get_yticklabels(), d.vendor):
        t.set_color(INK["title"] if v == "NVIDIA" else INK["text"])
    ax.set_xlim(0, 4.6)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    rub = y[d.label.str.contains("NVLink 6").to_numpy().argmax()]
    ax.plot([3.6, 3.6], [rub - 0.36, rub + 0.36], color=NV_DARK, lw=1.4, ls=":")
    ax.annotate("3.6 as announced (Jan 2026)", (3.6, rub), xytext=(6, 0), textcoords="offset points", fontsize=7.8,
                color=INK["muted"], va="center")
    ax.text(0.99, 0.02, "Helios per-GPU figure derived from AMD's 260 TB/s for 72 GPUs.\n"
            "TPU ICI links feed torus neighbours, not a switch;\nGaudi 3 counts all 24 Ethernet ports.",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=INK["muted"])
    ax.legend(handles=status_handles(), loc="center right", bbox_to_anchor=(1.0, 0.42))
    c.save(fig, ax, xlabel="TB/s per accelerator (bidirectional)", legend=False)


# ---------------------------------------------------------------------------------------------- 05-nvswitch-generations
@register
def nvswitch_generations():
    df = _ic()
    d = df[df.family == "NVSwitch"].sort_values("year").reset_index(drop=True)
    g1, n5, n6 = d.iloc[0], _row(df, "NVLink 5 Switch"), _row(df, "NVLink 6 Switch")
    mult = n5.per_device_bw_gbs_bidir / g1.per_device_bw_gbs_bidir
    c = Chart(
        id="05-nvswitch-generations",
        title=(f"NVSwitch bandwidth grew {mult:.0f}× by {int(n5.year)}, then held at {n6.per_device_bw_gbs_bidir / 1000:.1f} TB/s "
               f"in {int(n6.year)}: half the ports, twice the speed"),
        subtitle="Bidirectional TB/s per NVSwitch / NVLink Switch chip, labeled with NVLink ports per chip and largest NVLink domain",
        alt=(f"Bar chart of NVSwitch generations: gen 1 (2018) {g1.per_device_bw_gbs_bidir / 1000:.1f} TB/s with 18 ports, gen 2 1.8 TB/s "
             f"with 36 ports, gen 3 3.2 TB/s with 64 ports, NVLink 5 Switch 7.2 TB/s with 72 ports, NVLink 6 Switch 7.2 TB/s with 36 "
             f"double-speed ports, NVLink 7 Switch (2027, reported) 7.2 TB/s; domains grew from 16 GPUs to 72 and 144."),
        data=[IC_FILE], chapters=["05"],
        source="NVIDIA Hot Chips and technical blogs; SemiAnalysis", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=12, height=6)
    x = np.arange(len(d))
    road = (d.year > 2026).to_numpy()
    cols = [NV if (g.startswith("NVLink 6") or r) else GEN_PAST for g, r in zip(d.generation, road)]
    bars = ax.bar(x, d.per_device_bw_gbs_bidir / 1000, color=cols, width=0.62)
    hatch_future(bars, road)
    for b, (_, r) in zip(bars, d.iterrows()):
        ports = "ports n/a" if pd.isna(r.lanes_or_links_per_device) else f"{int(r.lanes_or_links_per_device)} ports"
        ax.annotate(f"{r.per_device_bw_gbs_bidir / 1000:.1f} TB/s\n{ports}\ndomain {int(r.max_domain_size):,}",
                    (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=8.4, color=INK["text"])
    ax.set_xticks(x, [f"{g}\n{int(y)}" for g, y in zip(d.generation, d.year)], fontsize=8.8)
    ax.set_ylim(0, 9.8)
    ax.text(0.99, 0.985, "Vera Rubin NVL72's production spec (216 TB/s over 36 chips)\nimplies ~6.0 TB/s per NVLink 6 Switch in use",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=INK["muted"])
    ax.legend(handles=status_handles("Shipping", "Roadmap (reported)"), loc="upper left")
    c.save(fig, ax, ylabel="TB/s per switch chip (bidirectional)", legend=False)


# ---------------------------------------------------------------------------------------------- 06-switch-port-speed-by-generation
@register
def switch_port_speed_by_generation():
    df = _ic()
    ib = df[df.family == "InfiniBand"].sort_values("year").copy()
    eth = df[df.family == "Ethernet"].sort_values("year").copy()
    eth = eth[~eth.generation.str.contains("802.3bm|802.3ck")]  # same port speed as an earlier row
    for d in (ib, eth):
        d["gbps"] = d.per_device_bw_gbs_bidir * 4  # GB/s bidirectional -> Gb/s per direction
    ibk, ek = ib[ib.confidence != "speculative"], eth[eth.confidence != "speculative"]
    ib_a, ib_b, e_a, e_b = ibk.iloc[0], ibk.iloc[-1], ek.iloc[0], ek.iloc[-1]
    m_ib, m_e = ib_b.gbps / ib_a.gbps, e_b.gbps / e_a.gbps
    c = Chart(
        id="06-switch-port-speed-by-generation",
        title=(f"Port speeds rose {m_ib:.0f}× on InfiniBand ({int(ib_a.year)}–{int(ib_b.year)}) and "
               f"{m_e:.0f}× on Ethernet ({int(e_a.year)}–{int(e_b.year)})"),
        subtitle=(f"Gb/s per direction per port: InfiniBand 4x (now {ib_b.gbps:.0f} Gb/s XDR) and IEEE Ethernet "
                  f"(now {e_b.gbps / 1000:.1f} Tb/s), by first product / standard year"),
        alt=(f"Log-scale step chart: InfiniBand 4x port speed climbed from {ib_a.gbps:.0f} Gb/s (SDR, {int(ib_a.year)}) through 56 (FDR), 100 (EDR), "
             f"200 (HDR), 400 (NDR) to {ib_b.gbps:.0f} Gb/s (XDR, {int(ib_b.year)}); Ethernet from 10 GbE ({int(e_a.year)}) to 100, 400, 800 GbE and "
             f"1.6 TbE ({int(e_b.year)}); next steps (1.6 Tb/s IB GDR, 3.2 TbE) are speculative."),
        data=[IC_FILE], chapters=["06", "16"],
        source="IBTA, NVIDIA docs, IEEE 802.3, Ethernet Alliance", source_ids=sources_of(pd.concat([ib, eth])),
    )
    fig, ax = c.figure(width=12, height=6.2)
    for d, col, mk, lab, below in [(ib, NV, "o", "InfiniBand (4x port)", False), (eth, NEUTRAL, "s", "Ethernet (IEEE port speed)", True)]:
        ok, sp = d[d.confidence != "speculative"], d[d.confidence == "speculative"]
        ax.step(ok.year, ok.gbps, where="post", color=col, lw=2, alpha=0.9)
        ax.plot(ok.year, ok.gbps, ls="none", marker=mk, ms=8, color=col, label=lab)
        if not sp.empty:
            ax.plot([ok.year.iloc[-1], sp.year.iloc[0]], [ok.gbps.iloc[-1], sp.gbps.iloc[0]], color=col, lw=1.4, ls="--")
            ax.plot(sp.year, sp.gbps, ls="none", marker=mk, ms=9, mfc="white", mec=col, mew=2,
                    label=f"{lab.split(' (')[0]} roadmap (speculative)")
        for _, r in d.iterrows():
            name = r.generation.split(" (")[0]
            if not below:
                ax.annotate(f"{name} {r.gbps:,.0f}G", (r.year, r.gbps), xytext=(0, 9), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8.2, color=col)
            elif r.year < 2005:
                ax.annotate(name.replace("GbE", "GbE "), (r.year, r.gbps), xytext=(0, -12), textcoords="offset points",
                            ha="center", va="top", fontsize=8.2, color=col)
            else:
                ax.annotate(name.replace("GbE", " GbE").replace("TbE", " TbE"), (r.year, r.gbps), xytext=(-7, 0),
                            textcoords="offset points", ha="right", va="center", fontsize=8.2, color=col)
    ax.set_xlim(1999.5, 2030)
    ax.set_ylim(4, 8000)
    log_axis(fig, ax)
    ax.legend(loc="upper left")
    c.save(fig, ax, xlabel="Year", ylabel="Port speed, Gb/s per direction (log scale)", legend=False)


# ---------------------------------------------------------------------------------------------- 05-scale-up-vs-scale-out-per-gpu
# GPU generation -> (NVLink row, NIC paired one-per-GPU in NVIDIA reference designs)
PAIRS = [("V100 (2017)", "NVLink 2", "ConnectX-5"),
         ("A100 (2020)", "NVLink 3", "ConnectX-6"),
         ("H100 (2022)", "NVLink 4 (HGX H100 NVL8)", "ConnectX-7"),
         ("GB200 (2024)", "NVLink 5 (GB200 NVL72)", "ConnectX-7"),
         ("GB300 (2025)", "NVLink 5 (GB200 NVL72)", "ConnectX-8 SuperNIC"),
         ("Vera Rubin (2026)", "NVLink 6 (Vera Rubin NVL72)", "ConnectX-9 SuperNIC")]


@register
def scale_up_vs_scale_out_per_gpu():
    ic = _ic()
    npd = load(NP_FILE)
    rows = []
    for gpu, nvl, nic in PAIRS:
        a = _row(ic, nvl)
        b = npd[npd["product"] == nic].iloc[0]
        rows.append(dict(gpu=gpu, nvlink=a.per_device_bw_gbs_bidir, nic=b.port_speed_gbps / 8 * 2,  # Gb/s/dir -> GB/s bidir
                         nic_name=nic.replace(" SuperNIC", ""), source_id=f"{a.source_id};{b.source_id}"))
    d = pd.DataFrame(rows)
    d["ratio"] = d.nvlink / d.nic
    last = d.iloc[-1]
    c = Chart(
        id="05-scale-up-vs-scale-out-per-gpu",
        title=(f"NVLink gives each GPU {d.ratio.min():.1f}–{d.ratio.max():.0f}× its scale-out NIC bandwidth: "
               f"{last.nvlink:,.0f} vs {last.nic:,.0f} GB/s on Vera Rubin"),
        subtitle="Bidirectional GB/s per GPU: NVLink scale-up vs the one-per-GPU ConnectX NIC of NVIDIA reference designs",
        alt=(f"Grouped log-scale bar chart comparing per-GPU NVLink and NIC bandwidth: V100 {d.nvlink[0]:.0f} vs {d.nic[0]:.0f} GB/s, "
             f"H100 900 vs 100, GB200 1,800 vs 100 (18x), GB300 1,800 vs 200, Vera Rubin {last.nvlink:,.0f} vs {last.nic:,.0f} GB/s "
             f"({last.ratio:.1f}x): the scale-up domain always has roughly an order of magnitude more bandwidth than scale-out."),
        data=[IC_FILE, NP_FILE], chapters=["05", "06", "P4"],
        source="NVIDIA product pages and whitepapers", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=11.5, height=6)
    x = np.arange(len(d))
    w = 0.38
    b1 = ax.bar(x - w / 2, d.nvlink, w, color=NV, label="NVLink per GPU (scale-up)")
    b2 = ax.bar(x + w / 2, d.nic, w, color=GEN_PAST, label="ConnectX NIC per GPU (scale-out)")
    for b, v in zip(b1, d.nvlink):
        ax.annotate(f"{v:,.0f}", (b.get_x() + b.get_width() / 2, v), xytext=(0, 2), textcoords="offset points",
                    ha="center", fontsize=8.4, color=INK["text"])
    for b, (_, r) in zip(b2, d.iterrows()):
        ax.annotate(f"{r.nic:,.0f}\n{r.nic_name}", (b.get_x() + b.get_width() / 2, r.nic), xytext=(0, 2), textcoords="offset points",
                    ha="center", fontsize=7.8, color=INK["text"])
    for i, r in d.iterrows():
        ax.annotate(f"{r.ratio:.1f}×" if r.ratio < 10 else f"{r.ratio:.0f}×", (i, 25000), ha="center", va="center",
                    fontsize=10.5, fontweight="bold", color=NV_DARK)
    ax.text(-0.55, 25000, "NVLink ÷ NIC:", fontsize=8.5, color=INK["muted"], va="center", ha="right")
    ax.set_xticks(x, d.gpu)
    ax.set_xlim(-1.35, len(d) - 0.5)
    ax.set_ylim(10, 60000)
    log_axis(fig, ax)
    ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.88))
    c.save(fig, ax, ylabel="GB/s per GPU, bidirectional (log scale)", legend=False)
