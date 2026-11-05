"""CPU charts for layer 04 (Grace, Vera and competing server CPUs). Owner: Phase-1 agent A1.

Data: data/cpu_specs.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from style import Chart, INK, NV, entity_color, load, register, sources_of

CPU = "cpu_specs.csv"


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def cpus() -> pd.DataFrame:
    df = load(CPU)
    df["color"] = df["vendor"].map(lambda v: entity_color("nvidia") if str(v).startswith("NVIDIA")
                                   else entity_color(v))
    df["future"] = df["status"].isin(["announced", "roadmap"])
    return df


@register
def cpu_gpu_bandwidth_pcie_vs_c2c():
    df = cpus()
    items = [
        ("Xeon E5-2698 v4 (Broadwell-EP)", "PCIe Gen3 x16 · Xeon E5 v4 (DGX-1, 2016)"),
        ("EPYC 7742 (Rome)", "PCIe Gen4 x16 · EPYC Rome (DGX A100, 2020)"),
        ("Xeon Platinum 8480+ (Sapphire Rapids)", "PCIe Gen5 x16 · Xeon SPR (DGX H100, 2023)"),
        ("EPYC Venice (Zen 6)", "PCIe Gen6 x16 · EPYC Venice (2026)"),
        ("Grace", "NVLink-C2C · Grace (GH200/GB200/GB300)"),
        ("Vera", "NVLink-C2C · Vera (Vera Rubin, 2026)"),
    ]
    d = df.set_index("product").loc[[p for p, _ in items]].reset_index()
    d["label"] = [lab for _, lab in items]
    gen5 = d.loc[d["product"].str.contains("Sapphire"), "cpu_gpu_bw_gbs_bidir"].item()
    vera = d.loc[d["product"] == "Vera", "cpu_gpu_bw_gbs_bidir"].item()
    grace = d.loc[d["product"] == "Grace", "cpu_gpu_bw_gbs_bidir"].item()
    c = Chart(
        id="04-cpu-gpu-bandwidth-pcie-vs-c2c",
        title=f"Vera's NVLink-C2C moves {vera:,.0f} GB/s CPU↔GPU, {vera/gen5:.0f}× a PCIe Gen5 x16 link ({gen5:.0f} GB/s)",
        subtitle="CPU-to-GPU link bandwidth per GPU, GB/s, both directions combined: PCIe x16 generations vs NVLink-C2C",
        alt=(f"Horizontal bar chart of CPU-to-GPU bandwidth per GPU: PCIe Gen3 x16 about 32 GB/s (DGX-1), Gen4 64 GB/s "
             f"(DGX A100), Gen5 {gen5:.0f} GB/s (DGX H100) and Gen6 256 GB/s (2026 x86 CPUs such as EPYC Venice), versus "
             f"NVLink-C2C at {grace:.0f} GB/s on Grace and {vera:,.0f} GB/s on Vera - {vera/gen5:.0f} times a Gen5 x16 "
             f"link, which lets the GPU treat CPU LPDDR as a coherent second memory tier."),
        data=[CPU], chapters=["04", "05"], source="NVIDIA, AMD, Intel specs", source_ids=sources_of(d),
        note="Hatched = announced, not yet shipping",
    )
    fig, ax = c.figure(width=10, height=5.4)
    y = np.arange(len(d))
    bars = ax.barh(y, d.cpu_gpu_bw_gbs_bidir, color=d.color, height=0.6)
    for b, fut in zip(bars.patches, d.future):
        if fut:
            b.set_hatch("///")
            b.set_alpha(0.75)
    for yi, v in enumerate(d.cpu_gpu_bw_gbs_bidir):
        mult = v / gen5
        extra = f"  ({mult:.1f}× Gen5)" if v != gen5 else "  (baseline)"
        ax.text(v + 15, yi, f"{v:,.0f} GB/s{extra}", va="center", fontsize=8.8, color=INK["text"])
    ax.set_yticks(y, d.label)
    for tick, prod in zip(ax.get_yticklabels(), d["product"]):
        if prod in ("Grace", "Vera"):
            tick.set_fontweight("bold")
            tick.set_color(INK["title"])
    ax.set_xlim(0, vera * 1.3)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _left_margin(fig, 0.36)
    c.save(fig, ax, xlabel="CPU–GPU bandwidth per GPU (GB/s, bidirectional)", legend=False)


def _scatter_set(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna(subset=["cores", "memory_bw_gbs"]).copy()
    short = {
        "Grace": "Grace", "Vera": "Vera", "Xeon E5-2698 v4 (Broadwell-EP)": "Xeon E5 v4",
        "EPYC 7742 (Rome)": "EPYC Rome", "Xeon Platinum 8480+ (Sapphire Rapids)": "Xeon SPR",
        "EPYC 9654 (Genoa)": "EPYC Genoa", "EPYC 9965 (Turin Dense)": "EPYC Turin", "EPYC Venice (Zen 6)": "EPYC Venice",
        "Xeon 6980P (Granite Rapids-AP)": "Xeon 6 GNR", "Xeon 6+ (Clearwater Forest)": "Xeon 6+ CWF",
        "Graviton3": "Graviton3", "Graviton4": "Graviton4", "AmpereOne A192-32X": "AmpereOne",
    }
    d["short"] = d["product"].map(lambda p: short.get(p, p))
    d["bw_per_core"] = d.memory_bw_gbs / d.cores
    return d


@register
def cpu_cores_and_memory_bandwidth():
    df = cpus()
    d = _scatter_set(df)
    vera = d.set_index("short").loc["Vera"]
    x86 = d[d.isa.eq("x86-64") & ~d.future & d.launch_date.astype(str).str[:4].astype(int).ge(2022)]
    c = Chart(
        id="04-cpu-cores-and-memory-bandwidth",
        title=f"Vera's {vera.memory_bw_gbs/1000:.1f} TB/s memory bandwidth beats every shipping server CPU ({vera.cores:.0f} cores)",
        subtitle="Cores per socket (x) vs peak memory bandwidth per socket, GB/s (y); hollow = announced, not yet shipping",
        alt=(f"Scatter plot of server CPUs by core count and memory bandwidth: NVIDIA Vera has {vera.cores:.0f} cores and "
             f"{vera.memory_bw_gbs:,.0f} GB/s, Grace 72 cores and 512 GB/s; x86 parts span from Xeon Sapphire Rapids "
             f"(56 cores, 307 GB/s) to EPYC Turin (192 cores, 576 GB/s) and Xeon 6 Granite Rapids (128 cores, 845 GB/s "
             f"with MRDIMM); only AMD's announced EPYC Venice (256 cores, 1,600 GB/s) exceeds Vera's bandwidth, while "
             f"Arm cloud CPUs such as Graviton4 and AmpereOne sit at 333-538 GB/s."),
        data=[CPU], chapters=["04"], source="vendor specs", source_ids=sources_of(d),
        note="Hollow = announced",
    )
    fig, ax = c.figure(width=10, height=6.0)
    offsets = {"Vera": (10, 6), "Grace": (10, -4), "Xeon E5 v4": (8, 4), "EPYC Rome": (8, -8),
               "Xeon SPR": (-8, 10), "EPYC Genoa": (8, -10), "EPYC Turin": (8, 6), "EPYC Venice": (-10, 10),
               "Xeon 6 GNR": (8, 6), "Xeon 6+ CWF": (-10, 10), "Graviton3": (8, 4), "Graviton4": (8, -8),
               "AmpereOne": (8, -10)}
    order = d.assign(nv=d.vendor.str.startswith("NVIDIA")).sort_values("nv")
    for r in order.itertuples():
        nv = str(r.vendor).startswith("NVIDIA")
        ax.scatter(r.cores, r.memory_bw_gbs, s=110 if nv else 75, color="white" if r.future else r.color,
                   edgecolor=r.color, linewidth=2.2, zorder=3 if nv else 2)
        dx, dy = offsets.get(r.short, (8, 4))
        ax.annotate(r.short, (r.cores, r.memory_bw_gbs), xytext=(dx, dy), textcoords="offset points",
                    ha="right" if dx < 0 else "left", va="center", fontsize=8.8, color=INK["title"],
                    fontweight="bold" if nv else "normal")
    for vend, lab in (("NVIDIA", "NVIDIA"), ("AMD", "AMD"), ("Intel", "Intel"), ("AWS", "AWS"),
                      ("Ampere", "Ampere (other)")):
        ax.scatter([], [], s=60, color=entity_color(vend), label=lab)
    ax.legend(loc="upper left")
    ax.set_xlim(0, 310)
    ax.set_ylim(0, 1800)
    ax.grid(axis="both")
    c.save(fig, ax, xlabel="Cores per socket", ylabel="Peak memory bandwidth per socket (GB/s)", legend=False)


@register
def cpu_memory_bandwidth_per_core():
    df = cpus()
    d = _scatter_set(df)
    d = d[d.launch_date.astype(str).str[:4].astype(int).ge(2022)].sort_values("bw_per_core")
    vera = d.set_index("short").loc["Vera"]
    best_x86 = d[d.isa.eq("x86-64") & ~d.future].sort_values("bw_per_core").iloc[-1]
    c = Chart(
        id="04-cpu-memory-bandwidth-per-core",
        title=(f"Vera feeds each core {vera.bw_per_core:.1f} GB/s of memory bandwidth, {vera.bw_per_core/best_x86.bw_per_core:.1f}× "
               f"the best shipping x86"),
        subtitle="Peak memory bandwidth per core, GB/s (socket bandwidth ÷ cores); CPUs launched 2022 or later",
        alt=(f"Horizontal bar chart of memory bandwidth per core: NVIDIA Vera {vera.bw_per_core:.1f} GB/s per core and "
             f"Grace 7.1 lead; the best shipping x86 part, {best_x86['product']}, offers {best_x86.bw_per_core:.1f} GB/s per "
             f"core, and high-core-count parts such as EPYC Turin (3.0) and Xeon 6+ Clearwater Forest (2.7) fall below "
             f"3 GB/s - Vera is tuned to keep GPUs and agentic CPU work fed rather than to maximise core count."),
        data=[CPU], chapters=["04"], source="vendor specs; repo calc.", source_ids=sources_of(d),
        note="Hatched = announced",
    )
    fig, ax = c.figure(width=10, height=5.6)
    y = np.arange(len(d))
    bars = ax.barh(y, d.bw_per_core, color=d.color, height=0.62)
    for b, fut in zip(bars.patches, d.future):
        if fut:
            b.set_hatch("///")
            b.set_alpha(0.75)
    for yi, (v, cores, bw) in enumerate(zip(d.bw_per_core, d.cores, d.memory_bw_gbs)):
        ax.text(v + 0.15, yi, f"{v:.1f}  ({bw:,.0f} GB/s ÷ {cores:.0f} cores)", va="center", fontsize=8.6,
                color=INK["text"])
    ax.set_yticks(y, d["product"].str.replace(r" \(.*\)$", "", regex=True) + "  ·  " + d["vendor"])
    for tick, vend in zip(ax.get_yticklabels(), d.vendor):
        if str(vend).startswith("NVIDIA"):
            tick.set_fontweight("bold")
            tick.set_color(INK["title"])
    ax.set_xlim(0, d.bw_per_core.max() * 1.45)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _left_margin(fig, 0.27)
    c.save(fig, ax, xlabel="Memory bandwidth per core (GB/s)", legend=False)
