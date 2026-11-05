"""Layer 07 (DPU, SuperNIC, storage, security) - CORE charts: BlueField generations, the host-CPU
'infrastructure tax', the dollar value of DPU offload per compute tray, scale-out bandwidth per GPU,
GPUDirect Storage paths, checkpoint write time, KV-cache reload time by tier and confidential-computing
overhead.

Data: data/l07_*.csv (owned by the layer-07 CORE author; documented in data/README.md) plus
data/P1_memory_per_parameter.csv (shared, read-only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

CH = ["07"]
BF = "l07_bluefield_generations.csv"
TAX = "l07_infra_tax.csv"
OFF = "l07_offload_model.csv"
NIC = "l07_nic_per_gpu.csv"
GDS = "l07_storage_paths.csv"
CKPT = "l07_checkpoint_model.csv"
KV = "l07_kv_tiers.csv"
CC = "l07_cc_overhead.csv"
P1 = "P1_memory_per_parameter.csv"
GRAY = "#898781"


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _offload_inputs() -> tuple[dict, pd.DataFrame]:
    d = load(OFF)
    return dict(zip(d.input, d.value.astype(float))), d


def offload_values() -> dict:
    """Annual $ per Vera Rubin compute tray (Est.) - shared with the page text."""
    v, _ = _offload_inputs()
    cores = v["vera_cores_per_cpu"] * v["vera_cpus_per_tray"]
    per_core = v["vera_price"] / v["vera_cores_per_cpu"]
    out = {"cores": cores, "per_core": per_core}
    for k in ("low", "high"):
        freed = cores * v[f"infra_share_{k}"] / 100
        out[f"freed_{k}"] = freed
        out[f"hw_{k}"] = freed * per_core / v["server_life"]
        out[f"gpu_{k}"] = v["gpus_per_tray"] * v["gpu_rental_price"] * 8760 * v[f"gpu_time_gain_{k}"] / 100
    out["power"] = v["dpu_power_saving_max"] / 1000 * 8760 * v["electricity_price"] * v["pue"]
    out["gpu_year"] = v["gpus_per_tray"] * v["gpu_rental_price"] * 8760
    return out


def checkpoint_bytes_per_param() -> float:
    """Weights + FP32 master + Adam momentum + Adam variance (gradients are not saved)."""
    p = load(P1)
    keep = p[(p.regime == "Training (mixed precision + Adam)") & (p.component != "gradients")]
    return float(keep.bytes_per_param.sum())


def kv_reload() -> pd.DataFrame:
    k = load(KV)
    tiers = k[k.tier != "model"].copy()
    m = k[k.tier == "model"].set_index("label").value.astype(float)
    per_tok, ctx = m["Llama 3.1 70B KV cache per token (FP8)"], m["Context length"]
    fp8, params = m["Rubin dense FP8"] * 1e12, m["Llama 3.1 70B parameters"] * 1e9
    size_gb = per_tok * ctx / 1e9
    tiers["seconds"] = size_gb / tiers.value.astype(float)
    # recompute (prefill) Est.: 2 x params x tokens (matmuls) + 2 x layers x tokens^2 x hidden (causal attention)
    flops = 2 * params * ctx + 2 * 80 * ctx ** 2 * 8192
    rec = flops / (0.5 * fp8)
    recompute = pd.DataFrame([dict(tier="recompute", label="Recompute the prefill (Est.)", value=np.nan,
                                   scope="Rubin at 50% of dense FP8 peak", confidence="estimate",
                                   source_id="S7000;S100", seconds=rec)])
    out = pd.concat([tiers, recompute], ignore_index=True)
    out.attrs.update(size_gb=size_gb, flops=flops)
    return out


# --------------------------------------------------------------------------------------
# 1. BlueField generations: cores, bandwidth, cores per 100 Gb/s
# --------------------------------------------------------------------------------------
@register
def l07_bluefield_generations():
    d = load(BF)
    d["cores_per_100g"] = d.arm_cores / (d.network_gbps / 100)
    bf3, bf4 = d.set_index("generation").loc["BlueField-3"], d.set_index("generation").loc["BlueField-4"]
    c = Chart(
        id="07-bluefield-generations",
        title=(f"BlueField-4 carries {bf4.arm_cores:.0f} Arm cores, {bf4.arm_cores / bf3.arm_cores:.0f}× BlueField-3, "
               f"for {bf4.network_gbps / bf3.network_gbps:.0f}× the bandwidth ({bf4.network_gbps:.0f} Gb/s)"),
        subtitle="Arm cores, network Gb/s per direction and cores per 100 Gb/s, BlueField-1 to -4; hatched = 2026 launch; * = NVIDIA claim",
        alt=("Three-panel bar chart of NVIDIA BlueField DPUs. Arm cores: BlueField-1 16 (Cortex-A72, 2018), BlueField-2 8 "
             "(A72, 2020), BlueField-3 16 (A78, 2022), BlueField-4 64 (Neoverse V2, Grace-class, 2026). Network bandwidth: "
             "100, 200, 400 and 800 Gb/s. Cores per 100 Gb/s: 16, 4, 4 and 8, so BlueField-4 doubles compute per bit, "
             "signalling that it runs services such as storage and KV-cache management, not just packet offload. NVIDIA "
             "claims BlueField-2 replaced ~30 CPU cores, BlueField-3 up to 300 and BlueField-4 has 6x BlueField-3's compute."),
        data=[BF], chapters=CH, source="NVIDIA/Mellanox BlueField announcements and datasheets",
        source_ids=sources_of(d),
    )
    fig, axes = c.figure_grid(1, 3, width=12.0, height=5.6)
    x = np.arange(len(d))
    labels = [g.replace("BlueField-", "BF-") + f"\n({y})" for g, y in zip(d.generation, d.year)]
    cols = [NV if s == "announced" else GEN_PAST for s in d.status]
    panels = [("arm_cores", "Arm cores per DPU", "{:.0f}"), ("network_gbps", "Network, Gb/s per direction", "{:,.0f}"),
              ("cores_per_100g", "Arm cores per 100 Gb/s", "{:.0f}")]
    for ax, (col, lab, fmt) in zip(axes, panels):
        bars = ax.bar(x, d[col], color=cols, width=0.62, edgecolor=NV_DARK, linewidth=0.6)
        for b, s in zip(bars.patches, d.status):
            if s == "announced":
                b.set_hatch("///")
        for xi, v in zip(x, d[col]):
            ax.text(xi, v * 1.02 + d[col].max() * 0.01, fmt.format(v), ha="center", va="bottom", fontsize=9.5,
                    color=INK["title"], fontweight="bold")
        ax.set_xticks(x, labels, fontsize=8.8)
        ax.set_ylim(0, d[col].max() * 1.32)
        ax.set_title(lab, fontsize=10.5, color=INK["text"], loc="left")
    # vendor claims under the first panel
    claims = {"BlueField-2": "~30 core-\nequiv.*", "BlueField-3": "≤300 core-\nequiv.*", "BlueField-4": "6× BF-3\ncompute*"}
    for xi, g in zip(x, d.generation):
        if g in claims:
            axes[0].text(xi, d.arm_cores.max() * 1.17, claims[g], ha="center", va="center", fontsize=7.6,
                         color=INK["muted"], style="italic")
    core_short = [ct.replace("Arm ", "").replace(" (Grace-class)", "") for ct in d.core_type]
    axes[0].set_xticks(x, [f"{lab}\n{cs}" for lab, cs in zip(labels, core_short)], fontsize=8.4)
    axes[1].set_ylabel("Gb/s per direction")
    axes[2].set_ylabel("Arm cores per 100 Gb/s")
    c.save(fig, list(axes), ylabel="Arm cores", legend=False, top=0.80, bottom=0.18)


# --------------------------------------------------------------------------------------
# 2. Infrastructure tax: share of host CPU consumed without offload
# --------------------------------------------------------------------------------------
@register
def l07_infrastructure_tax_estimates():
    d = load(TAX)
    lo = d.share_low_pct.fillna(0)
    hi = d.share_high_pct
    c = Chart(
        id="07-infrastructure-tax-estimates",
        title="Estimates put the host CPU's 'infrastructure tax' at ~19–33% of its cores",
        subtitle="Share of host CPU cores or cycles spent on networking, storage, security and management software (no DPU offload)",
        alt=("Horizontal range chart of estimates of the host-CPU infrastructure tax: NVIDIA's BlueField-2 Redis test freed 12 of "
             "64 cores (18.75%); NVIDIA's cluster power model frees 26 of 80 cores per server (32.5%); NVIDIA's DPU white paper "
             "says up to 30% of cycles; academic work on the 'datacenter tax' cites 25-30% of data-center CPU cycles. "
             "Three of the four estimates come from NVIDIA, which sells DPUs."),
        data=[TAX], chapters=CH, source="NVIDIA DPU power white paper; The Next Platform; arXiv 2511.06558",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.4, height=4.6)
    y = np.arange(len(d))[::-1]
    for yi, (l, h, est, cf, ct) in zip(y, zip(lo, hi, d.estimate, d.cores_freed, d.cores_total)):
        vendor = est.startswith("NVIDIA")
        col = NV if vendor else entity_color("other")
        if l > 0 and l != h:
            ax.barh(yi, h - l, left=l, color=col, height=0.5, zorder=2)
            ax.text(h + 0.6, yi, f"{l:.0f}–{h:.0f}%", va="center", fontsize=9.5, color=INK["title"])
        elif l == 0:
            ax.barh(yi, h, color=col, alpha=0.35, height=0.5, zorder=2, hatch="///", edgecolor=col, linewidth=1.2)
            ax.text(h + 0.6, yi, f"up to {h:.0f}%", va="center", fontsize=9.5, color=INK["title"])
        else:
            ax.barh(yi, h, color=col, height=0.5, zorder=2)
            ax.text(h + 0.6, yi, f"{h:.1f}%  ({cf:.0f} of {ct:.0f} cores)", va="center", fontsize=9.5, color=INK["title"])
    ax.set_yticks(y, d.estimate)
    ax.set_xlim(0, 62)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=NV, label="NVIDIA (DPU vendor) test or claim"),
                       Patch(color=entity_color("other"), label="Independent / academic")], loc="lower right", fontsize=8.6)
    _left_margin(fig, 0.30)
    c.save(fig, ax, xlabel="Share of host CPU cores or cycles, %", legend=False, top=0.80, bottom=0.17)


# --------------------------------------------------------------------------------------
# 3. Dollar value of DPU offload per Vera Rubin compute tray
# --------------------------------------------------------------------------------------
@register
def l07_offload_value_per_tray():
    v, raw = _offload_inputs()
    o = offload_values()
    rows = [
        ("Freed host CPU cores\n(hardware value, annualized)", o["hw_low"], o["hw_high"], GEN_PAST,
         f"{o['freed_low']:.0f}–{o['freed_high']:.0f} of {o['cores']:.0f} Vera cores × ${o['per_core']:.0f}/core ÷ {v['server_life']:.0f} yrs"),
        ("Power saved by offload\n(best case)", 0, o["power"], "#B5B5B5",
         f"≤{v['dpu_power_saving_max']:.0f} W × ${v['electricity_price']:.3f}/kWh × PUE {v['pue']:.2f}"),
        ("GPU time recovered\n(1–3% scenario)", o["gpu_low"], o["gpu_high"], NV,
         f"{v['gpus_per_tray']:.0f} GPUs × ${v['gpu_rental_price']:.2f}/GPU-hr × 8,760 h × 1–3%"),
    ]
    c = Chart(
        id="07-offload-value-per-tray",
        title=(f"Est.: 1–3% more GPU time is worth ${o['gpu_low'] / 1e3:.1f}–{o['gpu_high'] / 1e3:.1f}K per tray a year; "
               f"freed CPU cores ~${o['hw_low'] / 1e3:.1f}–{o['hw_high'] / 1e3:.1f}K"),
        subtitle="US$ per compute tray (4 Rubin GPUs, 2 Vera CPUs) per year, by source of DPU value; repo estimate from cited inputs",
        alt=(f"Range bar chart (estimates) of the annual value of DPU offload per Vera Rubin compute tray: freed host cores, "
             f"{o['freed_low']:.0f}-{o['freed_high']:.0f} of {o['cores']:.0f} Vera cores valued at about ${o['per_core']:.0f} per core "
             f"over {v['server_life']:.0f} years, are worth about ${o['hw_low']:,.0f}-{o['hw_high']:,.0f} a year; best-case power "
             f"savings of 247 W are worth about ${o['power']:,.0f}; recovering 1-3% of GPU time on four GPUs rented at "
             f"${v['gpu_rental_price']:.2f} per hour is worth about ${o['gpu_low']:,.0f}-{o['gpu_high']:,.0f}. In AI servers the "
             f"DPU's value lies in GPU utilization and tenant isolation, not in CPU cycles."),
        data=[OFF], chapters=CH, source="Morgan Stanley via press (Vera price), NVIDIA, EIA, Lambda; repo model",
        source_ids=sources_of(raw),
    )
    fig, ax = c.figure(width=11.2, height=4.9)
    y = np.arange(len(rows))[::-1]
    for yi, (lab, lo, hi, col, how) in zip(y, rows):
        b = ax.barh(yi, hi - lo, left=lo, color=col, height=0.52, zorder=2, edgecolor=NV_DARK if col == NV else col)
        b.patches[0].set_hatch("//")
        txt = f"${lo:,.0f}–{hi:,.0f}" if lo > 0 else f"≤${hi:,.0f}"
        ax.text(hi + 90, yi + 0.08, txt, va="bottom", fontsize=10, color=INK["title"], fontweight="bold")
        ax.text(hi + 90, yi - 0.06, how, va="top", fontsize=8.2, color=INK["text"])
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, o["gpu_high"] * 2.05)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _left_margin(fig, 0.25)
    c.save(fig, ax, xlabel="US$ per compute tray per year (Est.)", legend=False, top=0.80, bottom=0.17)


# --------------------------------------------------------------------------------------
# 4. Without GPUDirect: host-memory bandwidth needed to stage NIC traffic
# --------------------------------------------------------------------------------------
def bounce_load() -> pd.DataFrame:
    """Share of host DRAM bandwidth that staging inbound NIC traffic would consume (write + read = 2x)."""
    d = load(NIC)
    d = d[d.host_cpu.notna()].copy()
    cpu = load("cpu_specs.csv").set_index("product")
    d["nic_gbs_unit"] = d.scale_out_gbps_per_accelerator * d.accelerators_per_unit / 8
    d["host_bw_gbs"] = [cpu.loc[c, "memory_bw_gbs"] * n for c, n in zip(d.host_cpu, d.host_cpus_per_unit)]
    d["bounce_gbs"] = 2 * d.nic_gbs_unit
    d["share"] = d.bounce_gbs / d.host_bw_gbs * 100
    d.attrs["cpu_sources"] = sources_of(cpu.loc[d.host_cpu.unique()].reset_index())
    return d.sort_values("year").reset_index(drop=True)


@register
def l07_gpudirect_host_memory_load():
    d = bounce_load()
    lo, hi = d.share.min(), d.share.max()
    h100 = d.set_index("system").loc["DGX H100"]
    c = Chart(
        id="07-gpudirect-host-memory-load",
        title=f"Without GPUDirect, staging NIC data in CPU memory would use {lo:.0f}–{hi:.0f}% of its bandwidth",
        subtitle="Inbound NIC data staged in host DRAM (written, then read = 2×) as % of host CPUs' peak memory bandwidth; one direction",
        alt=("Bar chart (repo arithmetic): if inbound network data had to be staged in CPU memory before reaching the GPUs, each byte "
             "would cross host DRAM twice. That would need 100 GB/s of a DGX-1's 154 GB/s (65%), 400 of a DGX A100's 410 GB/s (98%), "
             "800 of a DGX H100's 614 GB/s (130%), 400 of a GB200 tray's 1,024 GB/s (39%), 800 of a GB300 tray's 1,024 (78%), "
             "1,600 of a Vera Rubin tray's 2,400 (67%) and, for a whole AMD Helios rack, 43,200 of its 18 EPYC Venice CPUs' 28,800 GB/s (150%). "
             "GPUDirect RDMA removes this traffic by letting the NIC write straight into GPU memory."),
        data=[NIC, "cpu_specs.csv"], chapters=CH + ["04", "06"], source="NVIDIA, AMD system specs; CPU datasheets; repo arithmetic",
        source_ids=sources_of(d) + [s for s in d.attrs["cpu_sources"] if s not in sources_of(d)] + ["S7000"],
    )
    fig, ax = c.figure(width=11.2, height=5.6)
    x = np.arange(len(d))
    cols = [entity_color(v) if v != "NVIDIA" else (NV if y >= 2024 else GEN_PAST) for v, y in zip(d.vendor, d.year)]
    ax.bar(x, d.share, color=cols, width=0.62, zorder=2)
    ax.axhline(100, color=entity_color("AMD"), lw=1.3, ls="--", zorder=3)
    ax.text(3.5, 103, "100% = all of the host's memory bandwidth", ha="center", va="bottom", fontsize=8.6,
            color=entity_color("AMD"))
    for xi, r in zip(x, d.itertuples()):
        ax.text(xi, r.share + 3, f"{r.share:.0f}%", ha="center", va="bottom", fontsize=10, color=INK["title"], fontweight="bold")
        ax.text(xi, r.share / 2, f"{r.bounce_gbs:,.0f}\nof\n{r.host_bw_gbs:,.0f}\nGB/s", ha="center", va="center", fontsize=7.8,
                color="#FFFFFF" if (r.share > 45 and not (r.vendor == "NVIDIA" and r.year < 2024)) else INK["title"])
    short = {"Xeon E5-2698 v4 (Broadwell-EP)": "Xeon E5", "EPYC 7742 (Rome)": "EPYC Rome", "Grace": "Grace", "Vera": "Vera",
             "Xeon Platinum 8480+ (Sapphire Rapids)": "Xeon SPR", "EPYC Venice (Zen 6)": "EPYC Venice"}
    labels = [f"{r.system.replace(' (V100)', '').replace(' (MI455X)', '')}\n{r.accelerators_per_unit:.0f} GPU : "
              f"{r.host_cpus_per_unit:.0f} {short[r.host_cpu]}" for r in d.itertuples()]
    ax.set_xticks(x, labels, fontsize=8.4)
    ax.set_ylim(0, max(170, d.share.max() * 1.18))
    ax.legend(handles=[Patch(color=GEN_PAST, label="NVIDIA, x86 host"), Patch(color=NV, label="NVIDIA, Grace/Vera host"),
                       Patch(color=entity_color("AMD"), label="AMD Helios")], loc="upper left", fontsize=8.6)
    c.save(fig, ax, ylabel="% of host peak memory bandwidth", legend=False, top=0.80, bottom=0.2)


# --------------------------------------------------------------------------------------
# 5. GPUDirect Storage paths on a DGX-2
# --------------------------------------------------------------------------------------
@register
def l07_gds_bandwidth_dgx2():
    d = load(GDS)
    base = d.iloc[0]
    c = Chart(
        id="07-gds-bandwidth-dgx2",
        title=(f"Bypassing the CPU lifted a DGX-2's storage-to-GPU ceiling from ~{base.bandwidth_gbs:.0f} GB/s "
               f"to {d.bandwidth_gbs.iloc[2]:.0f}–{d.bandwidth_gbs.max():.0f} GB/s"),
        subtitle="GB/s into the 16 V100 GPUs of one DGX-2, by data path; NVIDIA measurements (2019–20); hatched = theoretical sum",
        alt=("Horizontal bar chart of storage-to-GPU bandwidth in an NVIDIA DGX-2: the classic path through a CPU bounce buffer in "
             "system memory tops out at about 50 GB/s; with GPUDirect Storage, local NVMe drives deliver 53+ GB/s, remote storage "
             "via the NICs 100 GB/s or more, RAID cards in eight PCIe slots 112 GB/s, and all sources together a theoretical "
             "~215 GB/s, about 4x the bounce-buffer path. NVIDIA also reported ~3x better CPU utilization. Vendor figures."),
        data=[GDS], chapters=CH, source="NVIDIA Technical Blog; Blocks and Files", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.4, height=4.6)
    y = np.arange(len(d))[::-1]
    cols = [GRAY] + [NV] * (len(d) - 1)
    bars = ax.barh(y, d.bandwidth_gbs, color=cols, height=0.56, zorder=2)
    bars.patches[-1].set_hatch("///")
    bars.patches[-1].set_alpha(0.75)
    for yi, v in zip(y, d.bandwidth_gbs):
        ax.text(v + 3, yi, f"{v:.0f} GB/s  ({v / base.bandwidth_gbs:.1f}×)", va="center", fontsize=9.3, color=INK["title"])
    ax.set_yticks(y, d.path)
    ax.set_xlim(0, d.bandwidth_gbs.max() * 1.42)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=GRAY, label="Without GPUDirect Storage"), Patch(color=NV, label="With GPUDirect Storage")],
              loc="upper right", fontsize=8.6)
    _left_margin(fig, 0.33)
    c.save(fig, ax, xlabel="GB/s into GPU memory (one DGX-2)", legend=False, top=0.80, bottom=0.17)


# --------------------------------------------------------------------------------------
# 6. Checkpoint write time vs storage bandwidth
# --------------------------------------------------------------------------------------
@register
def l07_checkpoint_write_time():
    k = load(CKPT)
    bpp = checkpoint_bytes_per_param()
    models = k[k.record_type == "model"]
    refs = k[k.record_type == "bandwidth"]
    ll = float(models.set_index("item").loc["Llama 3.1 405B", "value"]) * 1e9 * bpp / 1e12  # TB
    r = refs.set_index("item").value.astype(float)
    t100, t7k = ll * 1000 / r.iloc[0], ll * 1000 / r.iloc[2]
    c = Chart(
        id="07-checkpoint-write-time",
        title=f"A 405B model's {ll:.1f} TB checkpoint takes ~{t100:.0f} s at 100 GB/s, {t7k:.1f} s at Meta's 7 TB/s",
        subtitle=f"Seconds to write one full training checkpoint ({bpp:.0f} bytes/parameter) vs aggregate storage bandwidth",
        alt=(f"Log-log line chart of checkpoint write time against storage bandwidth for four model sizes at {bpp:.0f} bytes per "
             f"parameter: Llama 3.1 70B (~0.98 TB), Llama 3.1 405B (~{ll:.1f} TB), DeepSeek-V3 671B (~9.4 TB) and a 1-trillion-parameter "
             f"model (14 TB). At 100 GB/s, the line rate of one BlueField-4 port, the 405B checkpoint takes about {t100:.0f} seconds; "
             f"at 1 TB/s about {t100 / 10:.1f} s; at the ~7 TB/s peak of Meta's Llama 3 storage cluster about {t7k:.1f} s."),
        data=[CKPT, P1], chapters=CH + ["P1"], source="Meta (Llama 3), DeepSeek, ZeRO paper; repo arithmetic",
        source_ids=sources_of(k) + ["S34004"],
    )
    fig, ax = c.figure(width=10.4, height=5.8)
    bw = np.logspace(1, np.log10(20000), 200)
    shades = {"Llama 3.1 70B": GEN_PAST, "Llama 3.1 405B": NV, "DeepSeek-V3": entity_color("other"),
              "1T-parameter model (illustrative)": INK["text"]}
    for _, m in models.iterrows():
        tb = float(m.value) * 1e9 * bpp / 1e12
        ls = "--" if "illustrative" in m["item"] else "-"
        ax.plot(bw, tb * 1000 / bw, color=shades[m["item"]], lw=2.6 if "405B" in m["item"] else 2, ls=ls, zorder=3,
                label=f"{m['item']} · {tb:.1f} TB")
    for name, val in r.items():
        ax.axvline(val, color=INK["base"], lw=1, ls=":", zorder=1)
        short = {"One BlueField-4 link (800 Gb/s)": "1 BlueField-4 port\n100 GB/s",
                 "1 TB/s storage system (round reference)": "1 TB/s",
                 "Meta Llama 3 Tectonic storage peak": "Meta Llama 3\nstorage peak 7 TB/s"}[name]
        ax.text(val * 1.06, 3000, short, fontsize=8.2, color=INK["text"], va="top")
        t = ll * 1000 / val
        ax.plot(val, t, "o", color=NV, ms=8, zorder=4, mec="white")
        ax.annotate(f"{t:.1f} s" if t < 10 else f"{t:.0f} s", (val, t), xytext=(7, -2), textcoords="offset points",
                    fontsize=9, color=NV_DARK, fontweight="bold")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(10, 20000)
    ax.set_ylim(0.03, 4000)
    ax.grid(axis="x", which="major")
    h, lab = ax.get_legend_handles_labels()
    ax.legend(h[::-1], lab[::-1], loc="lower left", fontsize=8.6, title="Checkpoint size (weights + FP32 master + Adam)",
              title_fontsize=8.6)
    c.save(fig, ax, xlabel="Aggregate storage write bandwidth, GB/s (log scale)", ylabel="Seconds per checkpoint",
           logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 7. KV-cache reload time by memory/storage tier
# --------------------------------------------------------------------------------------
@register
def l07_kv_cache_reload_by_tier():
    d = kv_reload()
    size = d.attrs["size_gb"]
    s = d.set_index("tier").seconds
    order = ["G1", "G2", "G3.5", "G3", "recompute", "G4"]
    d = d.set_index("tier").loc[order].reset_index()

    def fmt(t):
        return f"{t * 1000:.1f} ms" if t < 0.1 else (f"{t * 1000:.0f} ms" if t < 1 else f"{t:.1f} s")
    c = Chart(
        id="07-kv-cache-reload-by-tier",
        title=(f"128K-token 70B context: {fmt(s['G1'])} from HBM, {s['G3.5']:.1f} s from BlueField-4 flash, "
               f"{s['recompute']:.1f} s to recompute"),
        subtitle=f"Time to move a {size:.1f} GB FP8 KV cache (Llama 3.1 70B, 131,072 tokens) into a Rubin GPU, by tier",
        alt=(f"Log-scale horizontal bar chart of the time to restore a {size:.1f} GB KV cache (Llama 3.1 70B, 128K tokens, FP8): "
             f"G1 HBM4 at 19.2 TB/s about {fmt(s['G1'])}; G2 Vera LPDDR5X over NVLink-C2C at ~450 GB/s about {fmt(s['G2'])}; "
             f"G3.5 BlueField-4 context-memory storage over an 800 Gb/s link about {fmt(s['G3.5'])}; G3 one local PCIe Gen5 x4 SSD "
             f"about {fmt(s['G3'])}; recomputing the prefill on a Rubin GPU at 50% of dense FP8 peak about {s['recompute']:.1f} s "
             f"(estimate); and a per-GPU share of Meta's 7 TB/s Llama 3 storage cluster about {s['G4']:.0f} s. The G3.5 tier is "
             f"~{s['recompute'] / s['G3.5']:.0f}x faster than recomputing."),
        data=[KV], chapters=CH + ["11", "03"], source="NVIDIA (Rubin, Vera, BlueField-4), Meta (Llama 3), PCI-SIG; repo arithmetic",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=11.6, height=5.4)
    y = np.arange(len(d))[::-1]
    cols = [NV if t in ("G1", "G2", "G3.5") else (GRAY if t == "recompute" else GEN_PAST) for t in d.tier]
    bars = ax.barh(y, d.seconds, color=cols, height=0.6, zorder=2)
    for b, t in zip(bars.patches, d.tier):
        if t == "recompute":
            b.set_hatch("///")
    for yi, (t, sec) in zip(y, zip(d.tier, d.seconds)):
        ax.text(sec * 1.25, yi, fmt(sec), va="center", fontsize=9.5, color=INK["title"], fontweight="bold")
    short = {"G3.5": "BlueField-4 context storage (800G link)", "G4": "Shared storage, per-GPU share (Llama 3)",
             "G2": "Vera LPDDR5X via NVLink-C2C"}
    ax.set_yticks(y, [f"{t} · {short.get(t, lab)}" if t != "recompute" else "Recompute the prefill (Est., 50% of FP8 peak)"
                      for t, lab in zip(d.tier, d.label)])
    ax.set_xscale("log")
    ax.set_xlim(5e-4, 600)
    ax.grid(axis="x", which="major")
    ax.grid(axis="y", visible=False)
    _left_margin(fig, 0.34)
    c.save(fig, ax, xlabel="Seconds to restore the context", logx=True, legend=False, top=0.82)


# --------------------------------------------------------------------------------------
# 8. Confidential-computing overhead on H100
# --------------------------------------------------------------------------------------
@register
def l07_confidential_computing_overhead():
    d = load(CC)
    d["label"] = [f"{m}\n{'throughput' if 'throughput' in met else 'time to first token'}" for m, met in zip(d.model, d.metric)]
    d["ov"] = d.overhead_pct.clip(lower=0)
    t8 = d[(d.model == "Llama-3.1-8B") & d.metric.str.startswith("throughput")].overhead_pct.iloc[0]
    t70 = d[d.model == "Llama-3.1-70B"].overhead_pct.iloc[0]
    ttft = d[d.metric.str.startswith("time")].overhead_pct.iloc[0]
    c = Chart(
        id="07-confidential-computing-overhead",
        title=f"Confidential mode cost an H100 {t8:.2f}% of throughput on an 8B model, ~0% on 70B",
        subtitle="Performance overhead of running an LLM inside an H100 TEE vs normal mode, %; one published benchmark (2024)",
        alt=(f"Bar chart of H100 confidential-computing overhead from a 2024 benchmark: throughput overhead {t8:.2f}% for "
             f"Llama-3.1-8B, 4.58% for Phi-3-14B and {t70:.2f}% (about zero) for Llama-3.1-70B; time-to-first-token overhead "
             f"{ttft:.0f}% for Llama-3.1-8B. The cost comes mainly from encrypting CPU-GPU transfers, so it shrinks as the model, "
             f"and the compute per byte moved, grows."),
        data=[CC], chapters=CH, source="Zhu et al., arXiv 2409.03992", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.0, height=5.2)
    x = np.arange(len(d))
    cols = [NV if "throughput" in m else GEN_PAST for m in d.metric]
    ax.bar(x, d.ov, color=cols, width=0.58, zorder=2, edgecolor=NV_DARK, linewidth=0.6)
    for xi, (v, raw) in enumerate(zip(d.ov, d.overhead_pct)):
        lab = f"{raw:.2f}%"
        if raw < 0:
            lab += "\n(≈0, noise)"
        ax.text(xi, v + 0.4, lab, ha="center", va="bottom", fontsize=9.8, color=INK["title"], fontweight="bold")
    ax.set_xticks(x, d.label, fontsize=9)
    ax.set_ylim(0, d.ov.max() * 1.3)
    ax.legend(handles=[Patch(color=NV, label="Throughput (tokens/s) overhead"), Patch(color=GEN_PAST, label="Latency (TTFT) overhead")],
              loc="upper right", fontsize=8.8)
    c.save(fig, ax, ylabel="Overhead vs non-confidential mode, %", legend=False, top=0.82, bottom=0.17)
