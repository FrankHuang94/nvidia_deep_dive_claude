"""Competitive accelerator landscape charts (chapter 15, also 02/03). Owner: Phase-1 agent A1.

Data: data/competitor_accelerators.csv + NVIDIA rows from data/gpu_product_specs.csv. Dense figures only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

from style import Chart, INK, NV, entity_color, load, register, sources_of

COMP = "competitor_accelerators.csv"
GPU = "gpu_product_specs.csv"
FUTURE_NOTE = "Hatched = not yet shipping"


def _plain_log(ax, axis: str) -> None:
    def f(v, _pos):
        if v <= 0:
            return ""
        return f"{v:,.0f}" if v >= 1 else f"{v:g}"
    t = ax.yaxis if axis == "y" else ax.xaxis
    t.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    t.set_major_formatter(FuncFormatter(f))
    t.set_minor_formatter(NullFormatter())


def _log_badge(fig) -> None:
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))


def _left_margin(fig, left: float) -> None:
    """Chart.save() fixes left=0.08; widen it for long category labels on horizontal bars."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["left"] = left
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def combined() -> pd.DataFrame:
    """One frame with NVIDIA GPUs and competitor accelerators on common columns."""
    g = load(GPU)
    g = pd.DataFrame({
        "vendor": "NVIDIA", "product": g["product"], "status": g["status"], "confidence": g["confidence"],
        "memory_type": g["memory_type"], "mem_gb": g["memory_capacity_gb"], "bw_tbs": g["memory_bandwidth_tbs"],
        "fp8": g["fp8_tflops_dense"], "bf16": g["bf16_tflops_dense"], "fp4": g["fp4_tflops_dense"],
        "tdp_w": g["tdp_w"], "source_id": g["source_id"],
    })
    c = load(COMP)
    c = pd.DataFrame({
        "vendor": c["vendor"], "product": c["product"], "status": c["status"], "confidence": c["confidence"],
        "memory_type": c["memory_type"], "mem_gb": c["memory_capacity_gb"], "bw_tbs": c["memory_bandwidth_tbs"],
        "fp8": c["fp8_tflops_dense"], "bf16": c["bf16_tflops_dense"], "fp4": c["fp4_tflops_dense"],
        "tdp_w": c["tdp_w"], "source_id": c["source_id"],
    })
    df = pd.concat([g, c], ignore_index=True)
    df["future"] = df["status"].isin(["announced", "roadmap"]) | (df["confidence"] == "estimate")
    df["color"] = df["vendor"].map(entity_color)
    return df


def select(df: pd.DataFrame, items: list[tuple[str, str]]) -> pd.DataFrame:
    """items: (product, display label) in the order wanted."""
    rows = []
    for prod, label in items:
        m = df[df["product"] == prod]
        if m.empty:
            raise KeyError(prod)
        r = m.iloc[0].copy()
        r["label"] = label
        rows.append(r)
    return pd.DataFrame(rows).reset_index(drop=True)


# Current-generation flagship per vendor (latest shipping or announced for 2026).
FLAGSHIPS = [
    ("Rubin (VR200, per GPU)", "NVIDIA Rubin"),
    ("Instinct MI455X", "AMD MI455X"),
    ("TPU v7 Ironwood", "Google TPU v7 Ironwood"),
    ("Trainium3", "AWS Trainium3"),
    ("Maia 200", "Microsoft Maia 200"),
    ("Gaudi 3", "Intel Gaudi 3"),
    ("Ascend 950DT", "Huawei Ascend 950DT"),
]


def hbars(c: Chart, d: pd.DataFrame, col: str, xlabel: str, fmt: str, extra_label=None, width=10.0, height=5.8):
    d = d.sort_values(col, ascending=True).reset_index(drop=True)
    fig, ax = c.figure(width=width, height=height)
    y = np.arange(len(d))
    bars = ax.barh(y, d[col], color=d["color"], height=0.62)
    for b, fut in zip(bars.patches, d["future"]):
        if fut:
            b.set_hatch("///")
            b.set_alpha(0.75)
    xmax = d[col].max()
    for yi, (v, r) in enumerate(zip(d[col], d.itertuples())):
        txt = fmt.format(v)
        if extra_label:
            txt += f"  ·  {extra_label(r)}"
        if r.future:
            txt += "  (announced)" if r.status == "announced" else "  (roadmap)"
        ax.text(v + xmax * 0.01, yi, txt, va="center", ha="left", fontsize=8.6, color=INK["text"])
    ax.set_yticks(y, d["label"])
    for tick, colr, vend in zip(ax.get_yticklabels(), d["color"], d["vendor"]):
        if vend == "NVIDIA":
            tick.set_fontweight("bold")
            tick.set_color(INK["title"])
    ax.set_xlim(0, xmax * 1.42)
    _left_margin(fig, 0.25)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    return fig, ax


@register
def accelerator_landscape_bubble():
    df = combined()
    items = [("H100 SXM", "H100"), ("GB300 (per GPU)", "GB300"), ("Rubin (VR200, per GPU)", "Rubin"),
             ("Instinct MI300X", "MI300X"), ("Instinct MI355X", "MI355X"), ("Instinct MI455X", "MI455X"),
             ("TPU v7 Ironwood", "TPU v7 Ironwood"), ("Trainium2", "Trainium2"), ("Trainium3", "Trainium3"),
             ("Maia 200", "Maia 200"), ("Gaudi 3", "Gaudi 3"), ("Ascend 950DT", "Ascend 950DT"),
             ("Ascend 960", "Ascend 960"), ("Blackhole p150", "Tenstorrent Blackhole")]
    d = select(df, items)
    d["fp8_pf"] = d["fp8"] / 1000
    rub = d.set_index("label").loc["Rubin"]
    mi = d.set_index("label").loc["MI455X"]
    asic = d[d.vendor.isin(["Google", "AWS", "Microsoft"]) & ~d.future & (d.label != "Trainium2")]
    lo, hi = asic.fp8_pf.min(), asic.fp8_pf.max()
    c = Chart(
        id="15-accelerator-landscape-bubble",
        title=f"Rubin and MI455X claim {rub.fp8_pf:.1f}–{mi.fp8_pf:.0f} PFLOPS FP8; shipping custom ASICs sit at {lo:.1f}–{hi:.0f}",
        subtitle="Dense FP8 PFLOPS (x) vs memory bandwidth TB/s (y) per accelerator; bubble area = memory GB (log–log)",
        alt=(f"Log-log bubble chart of AI accelerators: NVIDIA Rubin ({rub.fp8_pf:.1f} PFLOPS dense FP8, "
             f"{rub.bw_tbs:.1f} TB/s, 288 GB) and AMD's announced MI455X ({mi.fp8_pf:.0f} PFLOPS, {mi.bw_tbs:.1f} TB/s, "
             f"432 GB) sit far up and to the right; shipping custom ASICs - Google Ironwood, AWS Trainium3 and "
             f"Microsoft Maia 200 - cluster at {lo:.1f}-{hi:.0f} PFLOPS and 4.9-7.4 TB/s, level with GB300 and "
             f"MI355X; Huawei's Ascend 950DT and Intel Gaudi 3 trail."),
        data=[COMP, GPU], chapters=["15", "02", "03"], source="vendor specs",
        source_ids=sources_of(d), note=FUTURE_NOTE,
    )
    fig, ax = c.figure(width=10, height=6.4)
    offsets = {  # label placement (points) to avoid collisions in the 4.5-5 PFLOPS cluster
        "H100": (12, -11, "left"), "GB300": (-14, 14, "right"), "Rubin": (-22, -2, "right"),
        "MI300X": (14, 6, "left"), "MI355X": (14, -10, "left"), "MI455X": (22, 0, "left"),
        "TPU v7 Ironwood": (-16, 4, "right"), "Trainium2": (12, -8, "left"), "Trainium3": (12, -8, "left"),
        "Maia 200": (14, -16, "left"), "Gaudi 3": (-14, 7, "right"), "Ascend 950DT": (-14, 8, "right"),
        "Ascend 960": (14, 6, "left"), "Tenstorrent Blackhole": (12, 4, "left"),
    }
    order = d.assign(nv=d.vendor.eq("NVIDIA")).sort_values("nv")  # NVIDIA drawn last (on top)
    for r in order.itertuples():
        size = r.mem_gb * 2.4
        kw = dict(s=size, color=r.color, alpha=0.55 if r.future else 0.8, edgecolor="white", linewidth=1.5,
                  zorder=3 if r.vendor == "NVIDIA" else 2)
        sc = ax.scatter(r.fp8_pf, r.bw_tbs, **kw)
        if r.future:
            sc.set_hatch("///")
        dx, dy, ha = offsets.get(r.label, (10, 0, "left"))
        ax.annotate(r.label + (" *" if r.future else ""), (r.fp8_pf, r.bw_tbs), xytext=(dx, dy),
                    textcoords="offset points", ha=ha, va="center", fontsize=8.6,
                    color=INK["title"], fontweight="bold" if r.vendor == "NVIDIA" else "normal")
    # vendor legend (one handle per colored vendor)
    for vend in ["NVIDIA", "AMD", "Google", "AWS", "Microsoft", "Intel", "Huawei", "Startups"]:
        ax.scatter([], [], s=60, color=entity_color(vend), label=vend if vend != "Startups" else "Startup (gray)")
    ax.legend(loc="upper left", ncol=2, fontsize=8.4, title="Vendor  (* = not yet shipping)", title_fontsize=8.4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.45, 40)
    ax.set_ylim(0.35, 40)
    _plain_log(ax, "x")
    _plain_log(ax, "y")
    ax.grid(axis="both")
    _log_badge(fig)
    c.save(fig, ax, xlabel="Dense FP8 PFLOPS per accelerator (log scale)",
           ylabel="Memory bandwidth, TB/s (log scale)", legend=False)

    try:
        import plotly.graph_objects as go
        pf = go.Figure()
        for vend, g in d.groupby("vendor", sort=False):
            pf.add_trace(go.Scatter(
                x=g.fp8_pf, y=g.bw_tbs, mode="markers+text", name=vend, text=g.label, textposition="top center",
                marker=dict(size=np.sqrt(g.mem_gb) * 2.2, color=entity_color(vend), opacity=0.75,
                            line=dict(color="white", width=1)),
                customdata=np.stack([g.mem_gb, g.status], axis=-1),
                hovertemplate="%{text}<br>FP8 %{x:.2f} PFLOPS dense<br>%{y:.2f} TB/s<br>%{customdata[0]:.0f} GB"
                              "<br>%{customdata[1]}<extra></extra>"))
        pf.update_xaxes(type="log", title="Dense FP8 PFLOPS (log scale)")
        pf.update_yaxes(type="log", title="Memory bandwidth TB/s (log scale)")
        c.save_plotly(pf, height=620)
    except Exception:  # pragma: no cover
        pass


@register
def memory_capacity_by_accelerator():
    df = combined()
    items = FLAGSHIPS + [("AI200", "Qualcomm AI200"), ("SN40L", "SambaNova SN40L"), ("WSE-3 (CS-3)", "Cerebras WSE-3")]
    d = select(df, items)
    rub = d.set_index("label").loc["NVIDIA Rubin"]
    qc = d.set_index("label").loc["Qualcomm AI200"]
    mi = d.set_index("label").loc["AMD MI455X"]
    c = Chart(
        id="15-memory-capacity-by-accelerator",
        title=(f"Qualcomm AI200 ({qc.mem_gb:.0f} GB LPDDR) and MI455X ({mi.mem_gb:.0f} GB) out-pack Rubin's "
               f"{rub.mem_gb:.0f} GB"),
        subtitle="Memory capacity per accelerator package or card, GB; current-generation flagship per vendor, memory type labeled",
        alt=(f"Horizontal bar chart of memory per accelerator: Qualcomm AI200 {qc.mem_gb:.0f} GB of LPDDR per card "
             f"(announced for 2026), AMD MI455X {mi.mem_gb:.0f} GB HBM4 (announced), NVIDIA Rubin {rub.mem_gb:.0f} GB "
             f"HBM4, Microsoft Maia 200 216 GB, Google Ironwood 192 GB, AWS Trainium3 and Huawei Ascend 950DT 144 GB, "
             f"Intel Gaudi 3 128 GB, SambaNova SN40L 64 GB HBM and Cerebras WSE-3 44 GB of on-wafer SRAM; "
             f"capacity leadership has passed to AMD and to LPDDR-based designs, which trade bandwidth for size."),
        data=[COMP, GPU], chapters=["15", "03"], source="vendor specs", source_ids=sources_of(d), note=FUTURE_NOTE,
    )
    fig, ax = hbars(c, d, "mem_gb", "GB", "{:,.0f} GB", extra_label=lambda r: r.memory_type)
    c.save(fig, ax, xlabel="Memory per accelerator (GB)", legend=False)


@register
def fp8_compute_by_accelerator():
    df = combined()
    items = FLAGSHIPS + [("Blackhole p150", "Tenstorrent Blackhole")]
    d = select(df, items)
    d["fp8_pf"] = d["fp8"] / 1000
    rub = d.set_index("label").loc["NVIDIA Rubin"]
    mi = d.set_index("label").loc["AMD MI455X"]
    asic_hi = d[d.vendor.isin(["Google", "AWS", "Microsoft"])].fp8_pf.max()
    c = Chart(
        id="15-fp8-compute-by-accelerator",
        title=(f"On paper MI455X ({mi.fp8_pf:.0f}) edges Rubin ({rub.fp8_pf:.1f} PFLOPS FP8); "
               f"custom ASICs top out at ~{asic_hi:.0f}"),
        subtitle="Dense FP8 PFLOPS per accelerator (no sparsity); current-generation flagship per vendor",
        alt=(f"Horizontal bar chart of dense FP8 compute: AMD MI455X {mi.fp8_pf:.0f} PFLOPS (announced for H2 2026) and "
             f"NVIDIA Rubin {rub.fp8_pf:.1f} PFLOPS lead; Microsoft Maia 200 about 5, Google Ironwood 4.6, AWS "
             f"Trainium3 2.5, Intel Gaudi 3 1.8, Huawei Ascend 950DT 1.0 and Tenstorrent Blackhole about 0.7 PFLOPS. "
             f"Hyperscaler ASICs deliver roughly a quarter of a Rubin per chip and compete on cost per token instead."),
        data=[COMP, GPU], chapters=["15", "02"], source="vendor specs (dense)", source_ids=sources_of(d),
        note=FUTURE_NOTE,
    )
    fig, ax = hbars(c, d, "fp8_pf", "PFLOPS", "{:,.1f}")
    c.save(fig, ax, xlabel="Dense FP8 PFLOPS per accelerator", legend=False)


@register
def memory_bandwidth_by_accelerator():
    df = combined()
    items = FLAGSHIPS + [("Cloud AI 100 Ultra", "Qualcomm Cloud AI 100 Ultra"),
                         ("Blackhole p150", "Tenstorrent Blackhole")]
    d = select(df, items)
    rub = d.set_index("label").loc["NVIDIA Rubin"]
    mi = d.set_index("label").loc["AMD MI455X"]
    asic = d[d.vendor.isin(["Google", "AWS", "Microsoft"])].sort_values("bw_tbs").iloc[-1]
    c = Chart(
        id="15-memory-bandwidth-by-accelerator",
        # QA 2026-11-05: MI455X corrected 19.6 -> 23.3 TB/s (S90093), so the two no longer "reach ~19 TB/s" together
        title=(f"MI455X leads at {mi.bw_tbs:.1f} TB/s per chip (~{mi.bw_tbs / rub.bw_tbs:.1f}× Rubin); Rubin is "
               f"{rub.bw_tbs/asic.bw_tbs:.1f}× the best custom ASIC"),
        subtitle="Peak memory bandwidth per accelerator, TB/s; current-generation flagship per vendor (Rubin at revised 19.2 TB/s)",
        alt=(f"Horizontal bar chart of memory bandwidth: AMD MI455X {mi.bw_tbs:.1f} TB/s (announced) and NVIDIA Rubin "
             f"{rub.bw_tbs:.1f} TB/s lead; Google Ironwood {asic.bw_tbs:.2f} TB/s is the best custom ASIC, about "
             f"{rub.bw_tbs/asic.bw_tbs:.1f} times lower, followed by Microsoft Maia 200 7.0, AWS Trainium3 4.9, Huawei "
             f"Ascend 950DT 4.0 and Intel Gaudi 3 3.7 TB/s; LPDDR and GDDR designs such as Qualcomm Cloud AI 100 "
             f"Ultra and Tenstorrent Blackhole sit near 0.5 TB/s."),
        data=[COMP, GPU], chapters=["15", "03"], source="vendor specs", source_ids=sources_of(d), note=FUTURE_NOTE,
    )
    fig, ax = hbars(c, d, "bw_tbs", "TB/s", "{:,.1f} TB/s", extra_label=lambda r: r.memory_type)
    c.save(fig, ax, xlabel="Memory bandwidth per accelerator (TB/s)", legend=False)
