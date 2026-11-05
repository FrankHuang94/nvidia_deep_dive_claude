"""Layer 03 (memory, packaging and supply chain) - CORE charts: decode ceiling vs batch at long context,
HBM needed for weights + KV cache vs per-GPU HBM, CoWoS packages per 300-mm wafer, and the memory-tier
bandwidth-vs-capacity map.

Data: data/P2_model_and_gpu_inputs.csv, data/gpu_product_specs.csv, data/competitor_accelerators.csv,
data/cpu_specs.csv, data/networking_products.csv, data/hbm_and_packaging.csv (shared, read-only) and
data/l03_memory_scenarios.csv, data/l03_cowos_geometry.csv (owned by the layer-03 CORE author;
documented in data/README.md). Every output is repo arithmetic (source S3000) on cited inputs.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import (GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, Chart, entity_color, load, register,
                   sources_of)

P2 = "P2_model_and_gpu_inputs.csv"
SCEN = "l03_memory_scenarios.csv"
GEO = "l03_cowos_geometry.csv"
HBM = "hbm_and_packaging.csv"
GPU = "gpu_product_specs.csv"
COMP = "competitor_accelerators.csv"
CPU = "cpu_specs.csv"
NET = "networking_products.csv"
CH = ["03"]
USABLE = 0.9          # fraction of HBM usable for weights + KV cache (same as Primer P2)


def _p2() -> pd.DataFrame:
    return load(P2)


def _cfg(p2: pd.DataFrame, model: str, metric: str) -> float:
    r = p2[(p2.record_type == "model_config") & (p2["item"] == model) & (p2.metric == metric)]
    return float(r.value.iloc[0])


def _gpu(p2: pd.DataFrame, gpu: str, metric: str) -> float:
    r = p2[(p2.record_type == "gpu_spec") & (p2["item"] == gpu) & (p2.metric == metric)]
    return float(r.value.iloc[0])


def _kv_bytes_per_token(p2: pd.DataFrame, model: str, kv_bytes: float) -> float:
    """KV-cache bytes per token: 2 (K and V) x layers x KV heads x head dim, or MLA's latent size x layers."""
    layers = _cfg(p2, model, "layers")
    mla = p2[(p2["item"] == model) & (p2.metric == "kv_cache_elements_per_layer")]
    if len(mla):
        return float(mla.value.iloc[0]) * layers * kv_bytes
    return 2 * layers * _cfg(p2, model, "kv_heads") * _cfg(p2, model, "head_dim") * kv_bytes


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


# --------------------------------------------------------------------------------------
# 1. Decode ceiling vs batch size at 32k context: bandwidth sets speed, capacity sets batch
# --------------------------------------------------------------------------------------
@register
def l03_decode_ceiling_vs_batch():
    p2 = _p2()
    model = "Llama 3.1 70B"
    ctx = 32768
    w_gb = _cfg(p2, model, "params_b") * 1.0                      # FP8 weights: 1 byte per parameter
    kv_seq_gb = _kv_bytes_per_token(p2, model, 1.0) * ctx / 1e9     # FP8 KV cache per sequence
    gpus = [("H200 SXM", "H200 · 141 GB · 4.8 TB/s", GEN_PAST, "o"),
            ("B200", "B200 (HGX) · 180 GB · 8 TB/s", GEN_PAST, "s"),
            ("B300", "B300 · 288 GB · 8 TB/s", "#7FB23A", "D"),
            ("Rubin", "Rubin · 288 GB · 19.2 TB/s", NV, "^")]
    rows = []
    for g, lab, col, mk in gpus:
        cap = _gpu(p2, g, "memory_gb")
        bw = _gpu(p2, g, "memory_bw_tbs")
        bmax = int(math.floor((cap * USABLE - w_gb) / kv_seq_gb))
        rows.append(dict(gpu=g, label=lab, color=col, marker=mk, cap=cap, bw=bw, bmax=bmax))
    d = pd.DataFrame(rows)

    def tps(bw, b):
        return b * bw * 1000 / (w_gb + b * kv_seq_gb)

    r = d[d.gpu == "Rubin"].iloc[0]
    rub_peak = tps(r.bw, r.bmax)
    kv_share = r.bmax * kv_seq_gb / (w_gb + r.bmax * kv_seq_gb)
    asym = r.bw * 1000 / kv_seq_gb
    used = p2[(p2["item"].isin([model] + list(d.gpu)))]
    c = Chart(
        id="03-decode-ceiling-vs-batch-32k",
        title=f"HBM capacity caps the batch: a 70B FP8 model at 32k context fills 288 GB at {r.bmax} users",
        subtitle=("Decode ceiling from memory bandwidth, tokens/s per GPU (all users) · Llama 3.1 70B, FP8 weights and KV cache, "
                  "32k context"),
        alt=(f"Line chart of the memory-bandwidth ceiling on decode throughput per GPU versus batch size for Llama 3.1 70B at FP8 "
             f"with 32k-token contexts (about {kv_seq_gb:.1f} GB of KV cache per user). H200 runs out of memory at "
             f"{int(d.bmax[0])} users (~{tps(d.bw[0], d.bmax[0]):,.0f} tokens/s), B200 at {int(d.bmax[1])} "
             f"(~{tps(d.bw[1], d.bmax[1]):,.0f}), B300 at {int(d.bmax[2])} (~{tps(d.bw[2], d.bmax[2]):,.0f}) and Rubin at "
             f"{r.bmax} (~{rub_peak:,.0f} tokens/s). Rubin's 2.4x bandwidth lifts speed but not the batch, and at its limit "
             f"KV-cache reads are ~{kv_share * 100:.0f}% of bytes moved per step."),
        data=[P2], chapters=["03", "11", "P2"],
        source="repo model (Est.) on Primer P2 inputs",
        source_ids=["S3000", "S32006", "S32002", "S33003", "S32004", "S33007"],
        note="Est.: ignores compute and overhead limits",  # moved out of the footer, which was clipped (QA 2026-11-05)
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    for _, g in d.iterrows():
        bs = np.unique(np.round(np.logspace(0, math.log10(g.bmax), 60)).astype(int))
        ax.plot(bs, [tps(g.bw, b) for b in bs], color=g.color, lw=2.2, zorder=3)
        ax.scatter([g.bmax], [tps(g.bw, g.bmax)], marker="X", s=95, color=g.color, edgecolor="white",
                   linewidth=0.8, zorder=4)
        ax.annotate(f"{g.label}\nHBM full at {g.bmax} users · {tps(g.bw, g.bmax):,.0f} tok/s",
                    (g.bmax, tps(g.bw, g.bmax)), xytext=(8, -14 if g.gpu == "B200" else -2),
                    textcoords="offset points", va="center",
                    fontsize=8.6, color=NV_DARK if g.gpu in ("Rubin", "B300") else INK["text"],
                    fontweight="bold" if g.gpu == "Rubin" else "normal")
    ax.axhline(asym, color=NV, lw=1.0, ls=(0, (4, 3)), zorder=2)
    ax.annotate(f"Rubin asymptote with unlimited HBM: {asym:,.0f} tok/s (KV-cache reads dominate)",
                (1.05, asym), xytext=(0, 4), textcoords="offset points", fontsize=8.4, color=NV_DARK)
    ax.set_xscale("log")
    ax.set_xlim(0.9, 160)
    ax.set_ylim(0, asym * 1.12)
    ax.set_xticks([1, 2, 5, 10, 20, 50, 100])
    ax.set_xticklabels(["1", "2", "5", "10", "20", "50", "100"])
    ax.legend(handles=[Line2D([0], [0], marker="X", color="white", markerfacecolor=INK["text"], markersize=9,
                              label="Weights + KV cache reach 90% of HBM")], loc="upper left",
              bbox_to_anchor=(0.0, 0.9), frameon=False)
    c.save(fig, ax, xlabel="Concurrent users (batch size)", ylabel="Decode ceiling, tokens/s per GPU",
           logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 2. HBM needed for weights + KV cache vs per-GPU HBM
# --------------------------------------------------------------------------------------
@register
def l03_hbm_needed_vs_per_gpu():
    p2 = _p2()
    sc = load(SCEN)
    rows = []
    for _, s in sc.iterrows():
        w = _cfg(p2, s.model, "params_b") * s.weight_bytes_per_param
        kv = _kv_bytes_per_token(p2, s.model, s.kv_bytes_per_element) * s.users * s.context_tokens / 1e9
        rows.append(dict(label=s.scenario.replace(": ", ":\n", 1), weights=w, kv=kv, total=w + kv))
    d = pd.DataFrame(rows)
    gpus = [("H100 SXM", "H100 80 GB"), ("H200 SXM", "H200 141 GB"), ("B300", "B300/Rubin 288 GB")]
    caps = {lab: _gpu(p2, g, "memory_gb") for g, lab in gpus}
    caps["B200 192 GB"] = 192.0  # raw HBM3E on B200 (hbm_and_packaging.csv); HGX exposes 180 GB
    h100, rubin = caps["H100 80 GB"], caps["B300/Rubin 288 GB"]
    d["n_h100"] = np.ceil(d.total / (h100 * USABLE)).astype(int)
    d["n_rubin"] = np.ceil(d.total / (rubin * USABLE)).astype(int)
    used = pd.concat([sc, p2[p2["item"].isin(list(sc.model) + [g for g, _ in gpus])]])
    c = Chart(
        id="03-hbm-needed-vs-per-gpu-hbm",
        title=(f"Serving four model scenarios needs {d.total.min():,.0f}–{d.total.max():,.0f} GB of HBM: "
               f"{d.n_rubin.min()}–{d.n_rubin.max()} Rubin GPUs or {d.n_h100.min()}–{d.n_h100.max()} H100s"),
        subtitle=("HBM needed for FP8 weights + FP8 KV cache, GB (stacked) vs memory per GPU (dashed lines) · "
                  "GPU counts assume 90% of HBM is usable"),
        alt=("Horizontal stacked bar chart of HBM needed to serve four repo scenarios at FP8: Llama 3.1 70B with 32 users at "
             f"32k context {d.total[0]:,.0f} GB (70 GB weights, {d.kv[0]:,.0f} GB KV cache); the same model with 16 users at "
             f"128k {d.total[1]:,.0f} GB; Llama 3.1 405B with 16 users at 32k {d.total[2]:,.0f} GB; DeepSeek-V3 671B with "
             f"64 users at 32k {d.total[3]:,.0f} GB, where compressed attention keeps the KV cache to {d.kv[3]:,.0f} GB. "
             f"Against 80, 141, 192 and 288 GB per GPU that is {d.n_rubin.min()} to {d.n_rubin.max()} Rubin GPUs or "
             f"{d.n_h100.min()} to {d.n_h100.max()} H100s."),
        data=[SCEN, P2], chapters=["03", "P2", "11"],
        source="model configs in Primer P2; repo scenarios",
        source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    y = np.arange(len(d))[::-1]
    ax.barh(y, d.weights, color=SEQ_BLUE[6], height=0.56, label="Weights (FP8)", zorder=2)
    ax.barh(y, d.kv, left=d.weights, color=SEQ_BLUE[2], height=0.56, label="KV cache (FP8)", zorder=2)
    for yi, (_, r) in zip(y, d.iterrows()):
        ax.annotate(f"{r.total:,.0f} GB → {r.n_rubin} Rubin · {r.n_h100} H100",
                    (r.total, yi), xytext=(6, 0), textcoords="offset points", va="center", fontsize=9,
                    color=INK["title"], fontweight="bold")
    styles = {"H100 80 GB": (GEN_PAST, 80), "H200 141 GB": (GEN_PAST, 141), "B200 192 GB": (GEN_PAST, 192),
              "B300/Rubin 288 GB": (NV, 288)}
    for lab, (col, v) in styles.items():
        ax.axvline(v, color=col, lw=1.6, ls=(0, (5, 3)), zorder=1)
        ax.annotate(lab, (v, len(d) + 0.6), rotation=90, xytext=(-3, 0), textcoords="offset points", ha="right",
                    va="top", fontsize=8.2, color=NV_DARK if col == NV else INK["text"])
    ax.set_ylim(-0.55, len(d) + 0.62)
    ax.set_yticks(y, d.label, fontsize=9)
    ax.set_xlim(0, d.total.max() * 1.42)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper right", frameon=False)
    _left_margin(fig, 0.27)
    c.save(fig, ax, xlabel="GB of HBM", legend=False)


# --------------------------------------------------------------------------------------
# 3. CoWoS packages per 300-mm wafer vs interposer size
# --------------------------------------------------------------------------------------
WAFER_R = 150.0 - 3.0   # mm; 3 mm edge exclusion
SPACING = 0.2           # mm between interposers


def _rects_in_wafer(area_mm2: float, aspect: float = 1.25, steps: int = 16) -> int:
    """Max count of w x h rectangles fully inside the usable wafer circle over a grid of offsets."""
    h = math.sqrt(area_mm2 / aspect)
    w = area_mm2 / h
    W, H = w + SPACING, h + SPACING
    best = 0
    nx, ny = int(2 * WAFER_R / W) + 3, int(2 * WAFER_R / H) + 3
    r2 = WAFER_R * WAFER_R
    for i in range(steps):
        for j in range(steps):
            ox, oy = -W * i / steps, -H * j / steps
            n = 0
            for a in range(-nx, nx):
                x0 = ox + a * W
                xs = (x0, x0 + w)
                for b in range(-ny, ny):
                    y0 = oy + b * H
                    if all(x * x + y * y <= r2 for x in xs for y in (y0, y0 + h)):
                        n += 1
            best = max(best, n)
    return best


@register
def l03_packages_per_cowos_wafer():
    h = load(HBM)
    pk = h[h.record_type == "packaging_tech"]
    reticle = float(pk[pk["item"] == "Lithography reticle limit"].value.iloc[0])
    lim_s = pk[(pk["item"] == "CoWoS-S") & (pk.metric == "max_interposer_area_reticles")].iloc[0]
    lim_l = pk[(pk["item"] == "CoWoS-L") & (pk.metric == "max_interposer_area_reticles")].sort_values("period")
    geo = load(GEO)
    mults = np.round(np.arange(1.0, 10.01, 0.25), 2)
    curve = [_rects_in_wafer(m * reticle) for m in mults]
    prods = []
    for _, g in geo.iterrows():
        lo = _rects_in_wafer(g.interposer_reticles_high * reticle)
        hi = _rects_in_wafer(g.interposer_reticles_low * reticle)
        prods.append(dict(product=g["product"], lo=lo, hi=hi, m_lo=g.interposer_reticles_low,
                          m_hi=g.interposer_reticles_high, conf=g.confidence))
    p = pd.DataFrame(prods)
    at2, at95 = _rects_in_wafer(2.0 * reticle), _rects_in_wafer(9.5 * reticle)
    used = pd.concat([pk, geo])
    c = Chart(
        id="03-packages-per-cowos-wafer",
        title=f"A 300-mm CoWoS wafer fits ~{at2} interposers at 2× reticle but only ~{at95} at 9.5×",
        subtitle="Gross interposers per wafer (before yield) vs interposer size · shaded bands = repo estimate of NVIDIA packages",
        alt=(f"Step chart of how many rectangular interposers fit on a 300-mm CoWoS wafer as package size grows: about {at2} at "
             f"twice the 858 square-millimetre reticle, {_rects_in_wafer(3.3 * reticle)} at CoWoS-S's 3.3x limit, "
             f"{_rects_in_wafer(5.5 * reticle)} at the 5.5x CoWoS-L size targeted for 2026 and about {at95} at the 9.5x size "
             f"targeted for 2027. Repo estimates place H100 at {p.lo[0]}-{p.hi[0]} per wafer, B200/B300 at {p.lo[1]}-{p.hi[1]}, "
             f"Rubin at {p.lo[2]}-{p.hi[2]} and a four-die Rubin Ultra at {p.lo[3]}-{p.hi[3]}, so the same wafer count "
             "yields ever fewer GPU packages."),
        data=[HBM, GEO], chapters=["03", "02", "17"],
        source="repo geometry model (Est., before yield) on TSMC reticle multiples",
        source_ids=["S380", "S3000", "S358", "S360", "S35041", "S509"],
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    ax.step(mults, curve, where="mid", color=INK["text"], lw=1.8, zorder=3, label="Gross interposers per wafer")
    for xv, lab in [(float(lim_s.value), f"CoWoS-S max ~{float(lim_s.value):g}×")] + \
            [(float(r.value), f"CoWoS-L target ~{float(r.value):g}× ({r.period})") for _, r in lim_l.iterrows()]:
        ax.axvline(xv, color=INK["base"], lw=1.2, ls=(0, (4, 3)), zorder=1)
        ax.annotate(lab, (xv, 60), rotation=90, xytext=(-3, 0), textcoords="offset points", ha="right", va="top",
                    fontsize=8.2, color=INK["text"])
    cols = [GEN_PAST, "#7FB23A", NV, NV]
    for i, (_, r) in enumerate(p.iterrows()):
        ax.axvspan(r.m_lo, r.m_hi, facecolor=cols[i], alpha=0.28 if r.conf != "speculative" else 0.16, zorder=0,
                   hatch="///" if r.conf == "speculative" else None, edgecolor="white")
        ymid = (r.lo + r.hi) / 2
        dx, dy = [(-6, 52), (4, 36), (34, 34), (0, 30)][i]
        ax.annotate(f"{r['product']}\n~{r.lo}–{r.hi} per wafer", ((r.m_lo + r.m_hi) / 2, ymid),
                    xytext=(dx, dy), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.6, fontweight="bold", color=NV_DARK,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9),
                    arrowprops=dict(arrowstyle="-", color=NV_DARK, lw=0.8))
    ax.set_xlim(1, 10)
    ax.set_ylim(0, 66)
    ax.set_xticks(range(1, 11))
    ax.set_xticklabels([f"{v}×" for v in range(1, 11)])
    ax.legend(handles=[Line2D([0], [0], color=INK["text"], lw=1.8, label="Gross interposers per 300-mm wafer"),
                       Patch(facecolor=NV, alpha=0.28, label="Estimated NVIDIA package size (range)"),
                       Patch(facecolor=NV, alpha=0.16, hatch="///", edgecolor="white", label="Roadmap package (speculative)")],
              loc="upper left", bbox_to_anchor=(0.5, 0.99), frameon=False)
    c.save(fig, ax, xlabel="Interposer area, multiples of the 858 mm² reticle", ylabel="Interposers per wafer",
           legend=False)


# --------------------------------------------------------------------------------------
# 4. Memory tiers: bandwidth vs capacity per device
# --------------------------------------------------------------------------------------
@register
def l03_memory_tiers():
    gpu = load(GPU)
    comp = load(COMP)
    cpu = load(CPU)
    net = load(NET)

    def g(prod):
        r = gpu[gpu["product"] == prod].iloc[0]
        return r, float(r.memory_capacity_gb), float(r.memory_bandwidth_tbs)

    def a(prod):
        r = comp[comp["product"] == prod].iloc[0]
        return r, float(r.memory_capacity_gb), float(r.memory_bandwidth_tbs)

    pts = []  # (label, cap GB, bw TB/s, entity, tech, row)
    for prod, lab in [("Rubin (VR200, per GPU)", "Rubin HBM4"), ("B300 (HGX)", "B300 HBM3E"), ("H100 SXM", "H100 HBM3")]:
        r, cap, bw = g(prod)
        pts.append((lab, cap, bw, "NVIDIA", "HBM", r))
    r, cap, bw = g("Groq 3 LPU (LP30)")
    pts.append(("Groq 3 LPU SRAM (NVIDIA)", cap, bw, "NVIDIA", "SRAM", r))
    for prod, lab in [("Vera", "Vera CPU LPDDR5X"), ("Grace", "Grace CPU LPDDR5X")]:
        rc = cpu[cpu["product"] == prod].iloc[0]
        pts.append((lab, float(rc.max_memory_gb), float(rc.memory_bw_gbs) / 1000, "NVIDIA", "LPDDR", rc))
    r, cap, bw = a("Instinct MI455X")
    pts.append(("AMD MI455X HBM4", cap, bw, "AMD", "HBM", r))
    r, cap, bw = a("WSE-3 (CS-3)")
    pts.append(("Cerebras WSE-3 SRAM", cap, bw, "Cerebras", "SRAM", r))
    r, cap, bw = a("Corsair")
    pts.append(("d-Matrix Corsair SRAM", cap, bw, "d-Matrix", "SRAM", r))
    r, cap, bw = a("Cloud AI 100 Ultra")
    pts.append(("Qualcomm AI 100 Ultra LPDDR4x", cap, bw, "Qualcomm", "LPDDR", r))
    r, cap, bw = a("Blackhole p150")
    pts.append(("Tenstorrent Blackhole GDDR6", cap, bw, "Tenstorrent", "GDDR", r))
    no_bw = []
    ai200 = comp[comp["product"] == "AI200"].iloc[0]
    no_bw.append(("Qualcomm AI200 LPDDR", float(ai200.memory_capacity_gb), "Qualcomm", ai200))
    cpx = gpu[gpu["product"] == "Rubin CPX"].iloc[0]
    no_bw.append(("Rubin CPX GDDR7 (as announced)", float(cpx.memory_capacity_gb), "NVIDIA", cpx))
    bf4 = net[net["product"] == "BlueField-4"].iloc[0]
    bf4_tbs = float(bf4.port_speed_gbps) / 8 / 1000
    used = pd.DataFrame([p[5] for p in pts] + [n[3] for n in no_bw] + [bf4])
    rub = pts[0]
    groq = pts[3]
    vera = pts[4]
    c = Chart(
        id="03-memory-tiers-bandwidth-vs-capacity",
        title=(f"HBM4 is {rub[2] / vera[2]:.0f}× faster than LPDDR5X but holds 1/{vera[1] / rub[1]:.0f} as much; "
               f"SRAM is ~{groq[2] / rub[2]:.0f}× faster again"),
        subtitle="Memory bandwidth vs capacity per chip · marker = memory type, color = vendor · grey strip = bandwidth not disclosed",
        alt=(f"Log-log scatter of memory capacity versus bandwidth per chip. SRAM designs sit top-left: NVIDIA's Groq 3 LPU "
             f"{groq[1]:g} GB at about {groq[2]:,.0f} TB/s, d-Matrix Corsair 2 GB at 150 TB/s and Cerebras WSE-3 44 GB at "
             f"21,000 TB/s. HBM sits in the middle: H100 80 GB at 3.35 TB/s, B300 288 GB at 8 TB/s, Rubin {rub[1]:,.0f} GB at "
             f"{rub[2]:g} TB/s and AMD MI455X 432 GB at 19.6 TB/s. LPDDR sits bottom-right: Grace 480 GB at 0.5 TB/s, Vera "
             f"{vera[1]:,.0f} GB at {vera[2]:g} TB/s and Qualcomm AI 100 Ultra 128 GB at 0.55 TB/s; Qualcomm AI200 (768 GB) and "
             f"Rubin CPX (128 GB GDDR7) have no disclosed bandwidth. A BlueField-4 link to NVMe context storage moves "
             f"~{bf4_tbs:g} TB/s."),
        data=[GPU, COMP, CPU, NET], chapters=["03", "15", "04"],
        source="NVIDIA, AMD, Cerebras, d-Matrix, Qualcomm, Tenstorrent specs",
        source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=6.3)
    markers = {"SRAM": "D", "HBM": "o", "LPDDR": "s", "GDDR": "^"}
    ecol = {"NVIDIA": NV, "AMD": entity_color("AMD"), "Qualcomm": entity_color("Qualcomm"),
            "Cerebras": entity_color("startups"), "d-Matrix": entity_color("startups"),
            "Tenstorrent": entity_color("startups")}
    offs = {"Rubin HBM4": (-8, 8, "right"), "B300 HBM3E": (8, -2, "left"), "H100 HBM3": (8, -2, "left"),
            "AMD MI455X HBM4": (8, -8, "left"), "Groq 3 LPU SRAM (NVIDIA)": (8, 6, "left"),
            "d-Matrix Corsair SRAM": (8, -8, "left"), "Cerebras WSE-3 SRAM": (8, 0, "left"),
            "Vera CPU LPDDR5X": (-8, 9, "right"), "Grace CPU LPDDR5X": (8, -6, "left"),
            "Qualcomm AI 100 Ultra LPDDR4x": (-8, -10, "right"), "Tenstorrent Blackhole GDDR6": (-8, 8, "right")}
    for lab, cap, bw, ent, tech, _ in pts:
        col = ecol[ent]
        ax.scatter(cap, bw, s=95, marker=markers[tech], color=col, edgecolor="white", linewidth=0.9,
                   zorder=4 if ent == "NVIDIA" else 3)
        dx, dy, ha = offs.get(lab, (8, 0, "left"))
        ax.annotate(lab, (cap, bw), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=8.4,
                    color=NV_DARK if ent == "NVIDIA" else (col if ent in ("AMD", "Qualcomm") else INK["text"]),
                    fontweight="bold" if ent == "NVIDIA" else "normal")
    ystrip = 0.03
    for lab, cap, ent, _ in no_bw:
        col = ecol[ent]
        ax.scatter(cap, ystrip, s=80, marker="|", color=col, linewidths=2.5, zorder=4)
        right = ent == "NVIDIA"
        ax.annotate(lab, (cap, ystrip), xytext=(-6 if right else 6, 7), textcoords="offset points",
                    ha="right" if right else "left", va="bottom", fontsize=8.2, color=NV_DARK if right else col)
    ax.axhline(bf4_tbs, color=INK["base"], lw=1.2, ls=(0, (4, 3)), zorder=1)
    ax.annotate(f"BlueField-4 link to NVMe context storage: {bf4.port_speed_gbps:,.0f} Gb/s ≈ {bf4_tbs:g} TB/s",
                (0.25, bf4_tbs), xytext=(0, 4), textcoords="offset points", fontsize=8.2, color=INK["text"])
    ax.axhspan(0.018, 0.05, color="#F0EFEC", zorder=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.2, 4000)
    ax.set_ylim(0.018, 60000)
    handles = [Line2D([0], [0], marker=m, color="white", markerfacecolor=INK["text"], markersize=8, label=t)
               for t, m in markers.items()]
    handles += [Patch(facecolor=NV, label="NVIDIA"), Patch(facecolor=entity_color("AMD"), label="AMD"),
                Patch(facecolor=entity_color("Qualcomm"), label="Qualcomm"),
                Patch(facecolor=entity_color("startups"), label="Start-ups")]
    ax.legend(handles=handles, loc="upper right", frameon=False, ncol=2, fontsize=8.4)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    c.save(fig, ax, xlabel="Memory capacity per chip, GB", ylabel="Memory bandwidth per chip, TB/s",
           logx=True, logy=True, legend=False)
