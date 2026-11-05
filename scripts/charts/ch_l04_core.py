"""Layer 04 (CPU: Grace, Vera) - CORE charts: host-to-GPU ratios, host threads and memory per GPU,
host-link bandwidth by generation, KV-cache reload time and the DGX-2 data-loading bottleneck.

Data: data/system_specs.csv, data/cpu_specs.csv, data/interconnect_specs.csv, data/gpu_product_specs.csv,
data/P2_model_and_gpu_inputs.csv (shared, read-only) and data/l04_host_attach.csv, data/l04_scenarios.csv
(owned by the layer-04 CORE author; documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

ATTACH = "l04_host_attach.csv"
SCEN = "l04_scenarios.csv"
SYS = "system_specs.csv"
CH = ["04"]


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _attach() -> pd.DataFrame:
    return load(ATTACH)


def _scen(record_type: str) -> pd.DataFrame:
    s = load(SCEN)
    return s[s.record_type == record_type].copy()


def _scen_val(df: pd.DataFrame, metric: str) -> float:
    return float(df.loc[df.metric == metric, "value"].iloc[0])


def _hostcolor(row) -> str:
    """NVIDIA x86-hosted DGX = past-generation tint; NVIDIA Grace/Vera = full green; rivals = entity color."""
    if str(row.vendor).startswith("NVIDIA"):
        return NV if str(row.cpu) in ("Grace", "Vera") else GEN_PAST
    return entity_color(row.vendor)


# --------------------------------------------------------------------------------------
# 1. Host CPUs per 8 GPUs, by system
# --------------------------------------------------------------------------------------
@register
def l04_cpus_per_8_gpus_by_system():
    sysdf = load(SYS)
    want = [  # (system name in system_specs.csv, short label)
        ("DGX-1 (V100)", "DGX-1 V100 (2017)"),
        ("DGX-2", "DGX-2 (2018)"),
        ("DGX A100", "DGX A100 (2020)"),
        ("DGX H100", "DGX H100 (2022)"),
        ("DGX B200", "DGX B200 (2024)"),
        ("GB200 NVL72", "GB200 NVL72 (2024)"),
        ("GB300 NVL72", "GB300 NVL72 (2025)"),
        ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin NVL72 (2026)"),
        ("CloudMatrix 384", "Huawei CloudMatrix 384 (2025)"),
        ("Helios (72x MI455X)", "AMD Helios (2026)"),
    ]
    rows = []
    for name, lab in want:
        r = sysdf[sysdf.system == name].iloc[0]
        rows.append(dict(label=lab, vendor=r.vendor, status=r.status, acc=float(r.accelerators_per_system),
                         cpus=float(r.cpus_per_system), source_id=r.source_id,
                         cpu="Grace" if "GB" in name else ("Vera" if "Vera" in name else "x86")))
    gh = _attach().set_index("system").loc["GH200 Grace Hopper"]
    rows.insert(5, dict(label="GH200 Grace Hopper (2023)", vendor="NVIDIA", status=gh.status, acc=1.0, cpus=1.0,
                        source_id=gh.source_id, cpu="Grace"))
    d = pd.DataFrame(rows)
    d["per8"] = d.cpus / d.acc * 8
    d["color"] = [_hostcolor(r) for r in d.itertuples()]
    d["future"] = d.status.isin(["announced", "roadmap"])
    proj = _scen("ratio_projection")
    lo, hi = _scen_val(proj, "cpus_per_gpu_low") * 8, _scen_val(proj, "cpus_per_gpu_high") * 8
    h100 = d.set_index("label").loc["DGX H100 (2022)", "per8"]
    vr = d.set_index("label").loc["Vera Rubin NVL72 (2026)", "per8"]
    c = Chart(
        id="04-cpus-per-8-gpus-by-system",
        title=f"Grace and Vera racks pair {vr:.0f} CPUs with every 8 GPUs, double DGX H100's {h100:.0f}",
        subtitle=f"CPU sockets per 8 accelerators by system; hatched = announced; band = reported agentic-era projection ({lo:.0f}–{hi:.0f})",
        alt=(f"Horizontal bar chart of host CPU sockets per 8 GPUs: DGX-1, DGX A100, DGX H100 and DGX B200 have 2; DGX-2 has 1 "
             f"(2 CPUs for 16 GPUs); GH200 has 8 (one Grace per GPU); GB200, GB300 and Vera Rubin NVL72 have {vr:.0f} "
             f"(36 CPUs for 72 GPUs), as does Huawei CloudMatrix 384 (192 CPUs for 384 NPUs); AMD Helios has 2 (18 EPYC "
             f"Venice for 72 GPUs). A shaded band at {lo:.0f}-{hi:.0f} marks Intel's and TrendForce's 2026 view that agentic "
             f"AI pushes ratios toward 1:2 to 1:1."),
        data=[SYS, ATTACH, SCEN], chapters=CH, source="NVIDIA, AMD, Huawei system specs; Intel; TrendForce",
        source_ids=sources_of(pd.concat([d[["source_id"]], proj[["source_id"]]])),
    )
    fig, ax = c.figure(width=10, height=6.0)
    y = np.arange(len(d))[::-1]
    ax.axvspan(lo, hi, color="#F2EBD8", zorder=0)
    ax.text((lo + hi) / 2, y.max() + 0.75, "Agentic-era projection\n(Intel, TrendForce, 2026)", ha="center",
            va="bottom", fontsize=8.4, color=INK["text"])
    bars = ax.barh(y, d.per8, color=d.color, height=0.62, zorder=2)
    for b, fut in zip(bars.patches, d.future):
        if fut:
            b.set_hatch("///")
    for yi, (v, cpus, acc) in zip(y, zip(d.per8, d.cpus, d.acc)):
        ax.text(v + 0.12, yi, f"{v:g}  ({cpus:.0f} CPU : {acc:.0f} GPU)", va="center", fontsize=8.6, color=INK["text"],
                zorder=3)
    ax.set_yticks(y, d.label)
    for tick, cpu in zip(ax.get_yticklabels(), d.cpu):
        if cpu in ("Grace", "Vera"):
            tick.set_fontweight("bold")
            tick.set_color(INK["title"])
    ax.set_xlim(0, 12.5)
    ax.set_ylim(-0.6, y.max() + 1.9)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(color=GEN_PAST, label="NVIDIA, x86 host (PCIe)"), Patch(color=NV, label="NVIDIA, Grace/Vera host (NVLink-C2C)"),
                       Patch(color=entity_color("Huawei"), label="Huawei"), Patch(color=entity_color("AMD"), label="AMD")],
              loc="lower right", fontsize=8.4)
    _left_margin(fig, 0.27)
    c.save(fig, ax, xlabel="Host CPU sockets per 8 accelerators", legend=False, top=0.82)


# --------------------------------------------------------------------------------------
# 2. Host threads per accelerator (NVIDIA generations vs AWS Trainium)
# --------------------------------------------------------------------------------------
@register
def l04_host_threads_per_accelerator():
    a = _attach()
    order = ["DGX-1 (V100)", "DGX-2", "DGX A100", "DGX H100", "DGX B200", "GH200 Grace Hopper", "GB200 NVL72",
             "GB300 NVL72", "Vera Rubin NVL72", "Trn2 instance (trn2.48xlarge)", "Trn3 Gen2 UltraServer"]
    d = a.set_index("system").loc[order].reset_index()
    d["tpa"] = d.host_threads_per_system / d.accelerators_per_system
    d["cpa"] = d.cpus_per_system * d.cores_per_cpu / d.accelerators_per_system
    d["color"] = [_hostcolor(r) for r in d.itertuples()]
    d["future"] = d.status.isin(["announced", "roadmap"])
    labels = {"DGX-1 (V100)": "DGX-1 V100", "GH200 Grace Hopper": "GH200", "Trn2 instance (trn2.48xlarge)": "AWS Trn2",
              "Trn3 Gen2 UltraServer": "AWS Trn3 Gen2"}
    d["short"] = [labels.get(s, s) for s in d.system]
    s = d.set_index("system")
    vr, h100, trn3 = s.loc["Vera Rubin NVL72", "tpa"], s.loc["DGX H100", "tpa"], s.loc["Trn3 Gen2 UltraServer", "tpa"]
    c = Chart(
        id="04-host-threads-per-accelerator",
        title=f"Vera Rubin gives each GPU {vr:.0f} host threads, {vr/h100:.0f}× DGX H100; a Trainium3 gets {trn3:.0f}",
        subtitle="Host CPU hardware threads (vCPUs) per accelerator; labels add physical cores where known; hatched = announced",
        alt=(f"Bar chart of host CPU threads per accelerator: DGX-1 V100 10, DGX-2 6, DGX A100 32, DGX H100 {h100:.0f}, DGX B200 28, "
             f"GH200 72 (72 Grace cores, no SMT), GB200 and GB300 NVL72 36, Vera Rubin NVL72 {vr:.0f} (44 Olympus cores with "
             f"two threads each); AWS Trn2 instances have 12 host vCPUs per Trainium2 and Trn3 Gen2 UltraServers {trn3:.0f} "
             f"per Trainium3, so NVIDIA's rack designs carry several times more host compute per accelerator."),
        data=[ATTACH], chapters=CH, source="NVIDIA DGX datasheets; NVIDIA Grace/Vera; AWS Neuron docs",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(d))
    bars = ax.bar(x, d.tpa, color=d.color, width=0.66)
    for b, fut in zip(bars.patches, d.future):
        if fut:
            b.set_hatch("///")
    for xi, (t, cp) in enumerate(zip(d.tpa, d.cpa)):
        core = "" if pd.isna(cp) else f"\n{cp:.0f} cores"
        ax.text(xi, t + 1.5, f"{t:.0f}{core}", ha="center", va="bottom", fontsize=8.6, color=INK["title"])
    ax.set_xticks(x, d.short, rotation=30, ha="right")
    ax.set_ylim(0, d.tpa.max() * 1.28)
    ax.legend(handles=[Patch(color=GEN_PAST, label="NVIDIA, x86 host"), Patch(color=NV, label="NVIDIA, Grace/Vera host"),
                       Patch(color=entity_color("AWS"), label="AWS Trainium (host CPU undisclosed)")],
              loc="upper left", fontsize=8.6)
    c.save(fig, ax, ylabel="Host CPU threads per accelerator", legend=False, bottom=0.22)


# --------------------------------------------------------------------------------------
# 3. Host (CPU-attached) memory vs HBM per accelerator
# --------------------------------------------------------------------------------------
@register
def l04_host_memory_per_accelerator():
    a = _attach()
    order = ["DGX-1 (V100)", "DGX A100", "DGX H100", "DGX B200", "GH200 Grace Hopper", "GB200 NVL72", "GB300 NVL72",
             "Vera Rubin NVL72", "Trn2 instance (trn2.48xlarge)", "Trn3 Gen2 UltraServer"]
    d = a.set_index("system").loc[order].reset_index()
    d["host"] = d.host_memory_gb_per_system / d.accelerators_per_system
    d["future"] = d.status.isin(["announced", "roadmap"])
    labels = {"DGX-1 (V100)": "DGX-1 V100", "GH200 Grace Hopper": "GH200", "Trn2 instance (trn2.48xlarge)": "AWS Trn2",
              "Trn3 Gen2 UltraServer": "AWS Trn3 Gen2"}
    d["short"] = [labels.get(s, s) for s in d.system]
    s = d.set_index("system")
    vr, gb = s.loc["Vera Rubin NVL72", "host"], s.loc["GB200 NVL72", "host"]
    vr_hbm = s.loc["Vera Rubin NVL72", "hbm_gb_per_accelerator"]
    c = Chart(
        id="04-host-memory-per-accelerator",
        title=f"Vera Rubin attaches ~{vr:,.0f} GB of CPU memory per GPU, {vr/gb:.1f}× GB200, {vr/vr_hbm:.1f}× its HBM",
        subtitle="GB per accelerator: CPU-attached memory (DDR or LPDDR5X) vs on-package HBM; hatched = announced",
        alt=(f"Grouped bar chart of memory per accelerator. CPU-attached memory: DGX-1 V100 64 GB, DGX A100 128, DGX H100 and "
             f"DGX B200 256, GH200 480, GB200 and GB300 NVL72 {gb:.0f}, Vera Rubin NVL72 about {vr:,.0f} GB; HBM per GPU: 16, "
             f"40, 80, 180, 144, 186, 288 and {vr_hbm:.0f} GB. AWS Trn2 has 128 GB of host memory per Trainium2 (96 GB HBM) "
             f"and Trn3 192 GB (144 GB HBM). Grace and Vera memory is reachable by the GPU over coherent NVLink-C2C."),
        data=[ATTACH], chapters=CH, source="NVIDIA DGX/GB200/Vera Rubin specs; AWS Neuron docs",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(d))
    w = 0.38
    host_col = [entity_color("AWS") if v == "AWS" else (NV if cpu in ("Grace", "Vera") else GEN_PAST)
                for v, cpu in zip(d.vendor, d.cpu)]
    b1 = ax.bar(x - w / 2, d.host, w, color=host_col, label="CPU-attached memory")
    b2 = ax.bar(x + w / 2, d.hbm_gb_per_accelerator, w, color="#FFFFFF", edgecolor=INK["text"], linewidth=1.1,
                label="HBM on the accelerator")
    for b, fut in zip(b1.patches, d.future):
        if fut:
            b.set_hatch("///")
    for xi, (h, m) in enumerate(zip(d.host, d.hbm_gb_per_accelerator)):
        ax.text(xi - w / 2, h + 12, f"{h:,.0f}", ha="center", va="bottom", fontsize=8.2, color=INK["title"])
        ax.text(xi + w / 2, m + 12, f"{m:,.0f}", ha="center", va="bottom", fontsize=8.2, color=INK["text"])
    ax.set_xticks(x, d.short, rotation=30, ha="right")
    ax.set_ylim(0, d.host.max() * 1.18)
    ax.legend(handles=[Patch(color=GEN_PAST, label="CPU memory, x86 host (PCIe)"),
                       Patch(color=NV, label="CPU memory, Grace/Vera (coherent C2C)"),
                       Patch(color=entity_color("AWS"), label="Host memory, AWS Trainium"),
                       Patch(facecolor="#FFFFFF", edgecolor=INK["text"], label="HBM per accelerator")],
              loc="upper left", fontsize=8.6)
    c.save(fig, ax, ylabel="GB per accelerator", legend=False, bottom=0.22)


# --------------------------------------------------------------------------------------
# 4. Host-link bandwidth per GPU, by system generation
# --------------------------------------------------------------------------------------
@register
def l04_host_link_bandwidth_per_gpu():
    a = _attach()
    order = ["DGX-1 (V100)", "DGX A100", "DGX H100", "DGX B200", "GH200 Grace Hopper", "GB200 NVL72", "GB300 NVL72",
             "Vera Rubin NVL72", "Helios (72x MI455X)"]
    d = a.set_index("system").loc[order].reset_index()
    d["future"] = d.status.isin(["announced", "roadmap"])
    d["color"] = [_hostcolor(r) for r in d.itertuples()]
    labels = {"DGX-1 (V100)": "DGX-1 V100\n2017", "DGX A100": "DGX A100\n2020", "DGX H100": "DGX H100\n2022",
              "DGX B200": "DGX B200\n2024", "GH200 Grace Hopper": "GH200\n2023", "GB200 NVL72": "GB200 NVL72\n2024",
              "GB300 NVL72": "GB300 NVL72\n2025", "Vera Rubin NVL72": "Vera Rubin\nNVL72 2026",
              "Helios (72x MI455X)": "AMD Helios\n2026"}
    d["short"] = [labels[s] for s in d.system]
    link = {"PCIe Gen3 x16": "PCIe Gen3", "PCIe Gen4 x16": "PCIe Gen4", "PCIe Gen5 x16": "PCIe Gen5",
            "PCIe Gen6 x16 (assumed)": "PCIe Gen6?"}
    d["link_short"] = [link.get(h, "NVLink-C2C") for h in d.host_link]
    s = d.set_index("system")
    gh, gb, vr, h100 = (s.loc[k, "host_link_gbs_bidir_per_accelerator"] for k in
                        ("GH200 Grace Hopper", "GB200 NVL72", "Vera Rubin NVL72", "DGX H100"))
    c = Chart(
        id="04-host-link-bandwidth-per-gpu",
        title=f"Host link per GPU: {gh/h100:.0f}× jump with GH200, halved on GB200, restored on Vera Rubin",
        subtitle="CPU↔GPU bandwidth per GPU, GB/s, both directions; a shared C2C link is split across its GPUs; hatched = announced",
        alt=(f"Bar chart of CPU-to-GPU bandwidth per GPU: DGX-1 V100 32 GB/s (PCIe Gen3), DGX A100 64 (Gen4), DGX H100 and "
             f"DGX B200 {h100:.0f} (Gen5); GH200 {gh:.0f} GB/s over NVLink-C2C with one Grace per GPU; GB200 and GB300 NVL72 "
             f"about {gb:.0f} because two GPUs share one 900 GB/s Grace link; Vera Rubin NVL72 about {vr:.0f} (1.8 TB/s per "
             f"Vera shared by two GPUs); AMD Helios about 256 if its EPYC Venice host uses a PCIe Gen6 x16 link."),
        data=[ATTACH], chapters=["04", "05"], source="NVIDIA, AMD, PCI-SIG specs; heise; repo arithmetic",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(d))
    bars = ax.bar(x, d.host_link_gbs_bidir_per_accelerator, color=d.color, width=0.64)
    for b, fut in zip(bars.patches, d.future):
        if fut:
            b.set_hatch("///")
    for xi, (v, lk) in enumerate(zip(d.host_link_gbs_bidir_per_accelerator, d.link_short)):
        ax.text(xi, v + 14, f"{v:,.0f}\n{lk}", ha="center", va="bottom", fontsize=8.4, color=INK["title"])
    ax.set_xticks(x, d.short, fontsize=8.8)
    ax.set_ylim(0, 1150)
    ax.legend(handles=[Patch(color=GEN_PAST, label="NVIDIA, x86 host (PCIe)"), Patch(color=NV, label="NVIDIA, Grace/Vera (NVLink-C2C)"),
                       Patch(color=entity_color("AMD"), label="AMD (announced)")], loc="upper left", fontsize=8.6)
    c.save(fig, ax, ylabel="CPU↔GPU bandwidth per GPU (GB/s, bidirectional)", legend=False, bottom=0.17)


# --------------------------------------------------------------------------------------
# 5. KV-cache reload time over each host link vs recomputation
# --------------------------------------------------------------------------------------
@register
def l04_kv_cache_reload_time():
    p2 = load("P2_model_and_gpu_inputs.csv")
    m = p2[(p2.record_type == "model_config") & (p2["item"] == "Llama 3.1 70B")].set_index("metric")["value"].astype(float)
    eff = float(p2[(p2.record_type == "model_assumption") & (p2.metric == "compute_efficiency")]["value"].iloc[0])
    kv = _scen("kv_offload")
    tokens = _scen_val(kv, "context_tokens")
    bpe = _scen_val(kv, "kv_bytes_per_element")
    gpus = load("gpu_product_specs.csv")
    h100 = gpus[gpus["product"] == "H100 SXM"].iloc[0]
    h200 = gpus[gpus["product"] == "H200 SXM"].iloc[0]
    ic = load("interconnect_specs.csv")
    pcie = ic[ic.family == "PCIe"].set_index("generation")
    att = _attach().set_index("system")

    layers, kvh, hd, heads, params = m["layers"], m["kv_heads"], m["head_dim"], m["attention_heads"], m["params_b"] * 1e9
    kv_bytes = 2 * layers * kvh * hd * bpe * tokens                       # K and V for every layer
    flops = 2 * params * tokens + 2 * layers * tokens ** 2 * heads * hd   # dense matmuls + causal attention
    recompute_s = flops / (h100.fp8_tflops_dense * 1e12 * eff)
    paths = [
        ("Recompute the cache (prefill on one\nH100-class GPU, FP8, 50% efficiency)", None, "Est.", "#B5B5B5"),
        ("PCIe Gen4 x16 (x86 host)", pcie.loc["PCIe 4.0", "per_device_bw_gbs_bidir"] / 2, "pcie", GEN_PAST),
        ("PCIe Gen5 x16 (x86 host, e.g. DGX H100)", pcie.loc["PCIe 5.0", "per_device_bw_gbs_bidir"] / 2, "pcie", GEN_PAST),
        ("PCIe Gen6 x16 (2026 x86 hosts)", pcie.loc["PCIe 6.0", "per_device_bw_gbs_bidir"] / 2, "pcie", GEN_PAST),
        ("NVLink-C2C, GB200 (link shared by 2 GPUs)",
         att.loc["GB200 NVL72", "host_link_gbs_bidir_per_accelerator"] / 2, "c2c", NV),
        ("NVLink-C2C, GH200 / Vera Rubin (per GPU)",
         att.loc["GH200 Grace Hopper", "host_link_gbs_bidir_per_accelerator"] / 2, "c2c", NV),
        ("Reference: reading it from HBM3E (H200)", h200.memory_bandwidth_tbs * 1000, "hbm", "#FFFFFF"),
    ]
    rows = []
    for lab, gbs, kind, col in paths:
        ms = recompute_s * 1000 if gbs is None else kv_bytes / (gbs * 1e9) * 1000
        rows.append(dict(label=lab, ms=ms, gbs=gbs, kind=kind, color=col))
    d = pd.DataFrame(rows)
    gen5 = d.loc[2, "ms"]
    c2c = d.loc[5, "ms"]
    src = sources_of(pd.concat([p2[p2["item"].isin(["Llama 3.1 70B", "Serving model"])][["source_id"]], kv[["source_id"]],
                                pcie.reset_index()[["source_id"]], att.reset_index()[["source_id"]].iloc[[5, 6]],
                                gpus[gpus["product"].isin(["H100 SXM", "H200 SXM"])][["source_id"]]]))
    c = Chart(
        id="04-kv-cache-reload-time",
        title=f"KV-cache reload: {gen5:.0f} ms over PCIe Gen5, {c2c:.0f} ms over NVLink-C2C, ~{recompute_s:.0f} s to recompute",
        subtitle=f"Time to restore one 32k-token Llama 3.1 70B conversation ({kv_bytes/1e9:.1f} GB, FP8) to the GPU; peak one-way link rates",
        alt=(f"Log-scale horizontal bar chart. A 32,768-token Llama 3.1 70B conversation has a {kv_bytes/1e9:.1f} GB FP8 KV "
             f"cache. Recomputing it on one H100-class GPU at 50% of dense FP8 peak takes about {recompute_s:.1f} seconds "
             f"(estimate); copying it back from CPU memory takes about {d.loc[1,'ms']:.0f} ms over PCIe Gen4 x16, {gen5:.0f} ms "
             f"over Gen5, {d.loc[3,'ms']:.0f} ms over Gen6, {d.loc[4,'ms']:.0f} ms over GB200's shared NVLink-C2C and "
             f"{c2c:.0f} ms over a full GH200 or Vera Rubin per-GPU C2C share, versus about {d.loc[6,'ms']:.1f} ms to read it "
             f"from HBM3E."),
        data=["P2_model_and_gpu_inputs.csv", SCEN, "interconnect_specs.csv", ATTACH, "gpu_product_specs.csv"], chapters=["04", "11"],
        source="Meta Llama config; NVIDIA, PCI-SIG specs; repo arithmetic", source_ids=src,
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    y = np.arange(len(d))[::-1]
    bars = ax.barh(y, d.ms, color=d.color, height=0.6, edgecolor=[INK["text"] if k == "hbm" else "none" for k in d.kind])
    bars.patches[0].set_hatch("///")
    for yi, (v, g, k) in zip(y, zip(d.ms, d.gbs, d.kind)):
        txt = f"{v/1000:.1f} s" if v >= 1000 else (f"{v:.1f} ms" if v < 10 else f"{v:.0f} ms")
        if g is not None and not pd.isna(g):
            txt += f"   ({g:,.0f} GB/s)"
        ax.text(v * 1.12, yi, txt, va="center", fontsize=8.8, color=INK["title"])
    ax.set_yticks(y, d.label, fontsize=8.8)
    for tick, k in zip(ax.get_yticklabels(), d.kind):
        if k == "c2c":
            tick.set_fontweight("bold")
            tick.set_color(INK["title"])
    ax.set_xscale("log")
    ax.set_xlim(0.5, 60000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _left_margin(fig, 0.33)
    c.save(fig, ax, xlabel="Time to restore the KV cache (ms)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 6. DGX-2 data-loading bottleneck
# --------------------------------------------------------------------------------------
@register
def l04_dgx2_data_loading_bottleneck():
    dl = _scen("data_loading")
    ceil = _scen_val(dl, "synthetic_data_ceiling")
    cpu = _scen_val(dl, "cpu_preprocessing_pipeline")
    dali = _scen_val(dl, "dali_gpu_preprocessing")
    cores = _scen_val(dl, "host_cpu_cores")
    gpus = _scen_val(dl, "gpus")
    idle = 1 - cpu / ceil
    c = Chart(
        id="04-dgx2-data-loading-bottleneck",
        title=f"CPU-bound data loading left DGX-2's {gpus:.0f} GPUs {idle:.0%} idle; GPU decoding got {dali/ceil:.0%}",
        subtitle=f"ResNet-50 training throughput on one DGX-2 (16× V100, {cores:.0f} host CPU cores), images per second",
        alt=(f"Bar chart of ResNet-50 training throughput on a DGX-2: {ceil:,.0f} images per second when fed synthetic data "
             f"(the GPUs' ceiling), {cpu:,.0f} with the standard CPU preprocessing pipeline on {cores:.0f} host cores "
             f"({cpu/ceil:.0%} of the ceiling, so the GPUs sat idle {idle:.0%} of the time) and {dali:,.0f} with NVIDIA DALI "
             f"moving JPEG decoding and augmentation onto the GPUs ({dali/ceil:.0%})."),
        data=[SCEN], chapters=["04", "10"], source="NVIDIA DALI case study; DGX-2 datasheet", source_ids=sources_of(dl),
        note="Vendor measurement (NVIDIA)",
    )
    fig, ax = c.figure(width=10, height=5.4)
    labs = ["GPU ceiling\n(synthetic data, no loading)", f"CPU preprocessing\n({cores:.0f} host cores decode JPEGs)",
            "GPU preprocessing\n(DALI, decode on GPU)"]
    vals = [ceil, cpu, dali]
    cols = ["#FFFFFF", GEN_PAST, NV]
    bars = ax.bar(range(3), vals, color=cols, edgecolor=[INK["text"], "none", "none"], linewidth=1.2, width=0.58)
    bars.patches[0].set_hatch("..")
    for i, v in enumerate(vals):
        ax.text(i, v + 300, f"{v:,.0f}\n({v/ceil:.0%} of ceiling)", ha="center", va="bottom", fontsize=9.2,
                color=INK["title"])
    ax.annotate("", xy=(1.36, ceil), xytext=(1.36, cpu), arrowprops=dict(arrowstyle="<->", color=NV_DARK, lw=1.4))
    ax.plot([1.29, 1.42], [ceil, ceil], ls=":", color=NV_DARK, lw=1)
    ax.text(1.4, (ceil + cpu) / 2, f"{ceil - cpu:,.0f} img/s\nlost to a\nslow host", va="center", fontsize=8.6,
            color=NV_DARK)
    ax.set_xticks(range(3), labs)
    ax.set_ylim(0, ceil * 1.25)
    c.save(fig, ax, ylabel="Training throughput (images/s)", legend=False)


# --------------------------------------------------------------------------------------
# 7. Grace -> Vera generational gains (Q3)
# --------------------------------------------------------------------------------------
@register
def l04_grace_to_vera_gains():
    cpu = load("cpu_specs.csv").set_index("product")
    g, v = cpu.loc["Grace"], cpu.loc["Vera"]
    att = _attach().set_index("system")
    tg = att.loc["GH200 Grace Hopper", "threads_per_core"]
    tv = att.loc["Vera Rubin NVL72", "threads_per_core"]
    rows = [
        ("Cores", g.cores, v.cores, "{:.0f}"),
        ("Hardware threads", g.cores * tg, v.cores * tv, "{:.0f}"),
        ("Memory bandwidth (GB/s)", g.memory_bw_gbs, v.memory_bw_gbs, "{:,.0f}"),
        ("Bandwidth per core (GB/s)", g.memory_bw_gbs / g.cores, v.memory_bw_gbs / v.cores, "{:.1f}"),
        ("Max memory (GB)", g.max_memory_gb, v.max_memory_gb, "{:,.0f}"),
        ("NVLink-C2C to GPUs (GB/s)", g.cpu_gpu_bw_gbs_bidir, v.cpu_gpu_bw_gbs_bidir, "{:,.0f}"),
    ]
    d = pd.DataFrame(rows, columns=["metric", "grace", "vera", "fmt"])
    d["x"] = d.vera / d.grace
    d = d.sort_values("x").reset_index(drop=True)
    src = sources_of(pd.concat([cpu.loc[["Grace", "Vera"]].reset_index()[["source_id"]],
                                att.loc[["GH200 Grace Hopper", "Vera Rubin NVL72"]].reset_index()[["source_id"]]]))
    xs = dict(zip(d.metric, d.x))
    c = Chart(
        id="04-grace-to-vera-generational-gains",
        title=(f"Vera vs Grace: {xs['Max memory (GB)']:.1f}× memory, {xs['Memory bandwidth (GB/s)']:.1f}× bandwidth, "
               f"2× C2C, only {xs['Cores']:.2f}× cores"),
        subtitle="Vera (2026) ÷ Grace (2023) per CPU socket, × (1.0 = no change); labels show Grace → Vera values; Vera hatched (shipping H2 2026)",
        alt=(f"Horizontal bar chart of Vera-to-Grace ratios per CPU: cores 72 to 88 ({xs['Cores']:.2f} times), hardware threads "
             f"72 to 176 ({xs['Hardware threads']:.1f} times, via Spatial Multithreading), memory bandwidth 512 to 1,200 GB/s "
             f"({xs['Memory bandwidth (GB/s)']:.1f} times), bandwidth per core 7.1 to 13.6 GB/s "
             f"({xs['Bandwidth per core (GB/s)']:.1f} times), memory capacity 480 to 1,536 GB "
             f"({xs['Max memory (GB)']:.1f} times) and NVLink-C2C 900 to 1,800 GB/s (2 times): NVIDIA spent its new "
             f"transistors on feeding data rather than on core count."),
        data=["cpu_specs.csv", ATTACH], chapters=["04", "17"], source="NVIDIA Grace and Vera specifications", source_ids=src,
    )
    fig, ax = c.figure(width=10, height=5.0)
    y = np.arange(len(d))
    bars = ax.barh(y, d.x, color=NV, height=0.6)
    for b in bars.patches:
        b.set_hatch("///")
    ax.axvline(1, color=INK["text"], lw=1.2, ls="--")
    ax.text(1.02, len(d) - 0.45, "Grace = 1.0", fontsize=8.6, color=INK["text"], va="bottom")
    for yi, r in d.iterrows():
        lab = f"{r.x:.2f}×   ({r.fmt.format(r.grace)} → {r.fmt.format(r.vera)})"
        ax.text(r.x + 0.05, yi, lab, va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, d.metric)
    ax.set_xlim(0, 4.4)
    ax.set_ylim(-0.6, len(d) - 0.1)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _left_margin(fig, 0.25)
    c.save(fig, ax, xlabel="Vera ÷ Grace (×)", legend=False)
