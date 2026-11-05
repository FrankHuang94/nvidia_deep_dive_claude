"""Case study CS3 (Google TPU: the credible alternative) charts: TPU generations (per-chip compute and pod size)
and owner TCO per chip-hour vs NVIDIA and AMD.

Owner: CS3 case-study agent. Data: data/cs3_tpu_generations.csv and data/cs3_tpu_economics.csv (documented in
data/README.md) plus the shared data/competitor_accelerators.csv (TPU v4 to Ironwood).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from style import INK, NV, NV_DARK, Chart, entity_color, hatch_future, load, register, sources_of

GENS = "cs3_tpu_generations.csv"
ECON = "cs3_tpu_economics.csv"
COMP = "competitor_accelerators.csv"
GOOGLE = entity_color("google")


def _generations():
    g = load(GENS)
    comp = load(COMP)
    comp = comp[comp.vendor.eq("Google")].copy()
    rows = []
    for _, r in g.iterrows():
        rows.append(dict(gen=r.generation, year=int(r.announce_year), bf16=r.bf16_tflops_dense,
                         pod=r.max_pod_chips, status=r.status, src=r.source_id))
    for _, r in comp.iterrows():
        rows.append(dict(gen=r["product"], year=int(r.year), bf16=r.bf16_tflops_dense,
                         pod=r.max_scale_up_domain, status=r.status, src=r.source_id))
    df = pd.DataFrame(rows).sort_values(["year", "gen"]).reset_index(drop=True)
    return df, g, comp


@register
def cs3_tpu_generations():
    df, g, comp = _generations()
    flag = df[df.bf16.notna()]
    v2 = flag[flag.gen.eq("TPU v2")].iloc[0]
    v7 = flag[flag.gen.str.contains("Ironwood")].iloc[0]
    pods = df[df.pod.notna()]
    v7pod = pods[pods.gen.str.contains("Ironwood")].iloc[0].pod
    t8pod = pods[pods.gen.eq("TPU 8t")].iloc[0].pod
    c = Chart(
        id="CS3-tpu-generations",
        title=(f"TPU compute per chip rose ~{v7.bf16 / v2.bf16:.0f}× from v2 (2017) to Ironwood (2025); "
               f"pods grew {v7pod / v2.pod:.0f}× to {v7pod:,.0f} chips"),
        subtitle="Google TPU by generation: dense BF16 TFLOPS per chip (left, log scale) and max chips per pod (right)",
        alt=(f"Two-panel chart of Google TPU generations. Left, log scale: dense BF16 TFLOPS per chip rose from {v2.bf16:.0f} "
             f"(TPU v2, 2017) to 123 (v3, 2018), 275 (v4, 2021), 459 (v5p, 2023), 918 (v6e Trillium, 2024) and about "
             f"{v7.bf16:,.0f} (v7 Ironwood, 2025; BF16 reported as half its 4,614 FP8), about {v7.bf16 / v2.bf16:.0f} times in "
             f"eight years; the cost-optimised v5e has 197. Right: maximum chips per pod grew from {v2.pod:.0f} (v2) to 1,024 (v3), "
             f"4,096 (v4), 8,960 (v5p) and {v7pod:,.0f} (Ironwood), with {t8pod:,.0f} announced for TPU 8t in 2026; the v5e and "
             "Trillium efficiency parts stay at 256-chip pods. TPU v1 (2015) was an INT8 inference card with 92 TOPS and no pod."),
        data=[GENS, COMP], chapters=["CS3", "15", "05"],
        source="Google Cloud docs and blogs; ISCA papers",
        source_ids=sources_of(g) + sources_of(comp),
        note="Hatched = announced",
    )
    fig, (ax1, ax2) = c.figure_grid(1, 2, width=11.5, height=5.8)
    # left: BF16 per chip
    for _, r in flag.iterrows():
        eff = r.gen in ("TPU v5e",)
        ax1.scatter(r.year, r.bf16, s=70, color="#FFFFFF" if eff else GOOGLE, edgecolor=GOOGLE, linewidth=1.8, zorder=3)
        dy = -13 if eff else 7
        ax1.annotate(r.gen.replace("TPU ", "").replace(" (Trillium)", "\nTrillium").replace(" Ironwood", "\nIronwood"),
                     (r.year, r.bf16), xytext=(0, dy), textcoords="offset points", ha="center",
                     va="bottom" if dy > 0 else "top", fontsize=8.3, color=INK["text"])
    main = flag[~flag.gen.isin(["TPU v5e"])]
    ax1.plot(main.year, main.bf16, color=GOOGLE, lw=2, zorder=2)
    ax1.set_yscale("log")
    ax1.set_ylim(25, 6000)
    ax1.set_xlim(2016.3, 2026)
    ax1.set_ylabel("Dense BF16 TFLOPS per chip (log scale)")
    ax1.set_xlabel("Year announced")
    ax1.set_title("Compute per chip", fontsize=10.5, color=INK["text"], loc="left")
    # right: pod size bars
    p = pods.copy()
    p["label"] = p.gen.str.replace("TPU ", "", regex=False).str.replace(" (Trillium)", "", regex=False)
    p["label"] = p.label.str.replace("v7 Ironwood", "v7", regex=False)
    xs = np.arange(len(p))
    bars = ax2.bar(xs, p.pod, color=[GOOGLE if s != "announced" else "#86B6EF" for s in p.status], width=0.65,
                   edgecolor=GOOGLE)
    hatch_future(bars, (p.status == "announced").tolist())
    for xi, v in zip(xs, p.pod):
        ax2.annotate(f"{v:,.0f}", (xi, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                     fontsize=8.5, color=INK["title"])
    ax2.set_xticks(xs)
    ax2.set_xticklabels([f"{lab}\n{y}" for lab, y in zip(p.label, p.year)], fontsize=8.3)
    ax2.set_ylabel("Max chips per pod")
    ax2.set_ylim(0, p.pod.max() * 1.15)
    ax2.set_title("Pod size (scale-up domain)", fontsize=10.5, color=INK["text"], loc="left")
    c.save(fig, [ax1, ax2], legend=False, top=0.80, bottom=0.17)


@register
def cs3_owner_tco_per_chip_hour():
    e = load(ECON)
    o = e[e.metric.eq("owner_tco_per_chip_hour")].sort_values("value").reset_index(drop=True)
    tpu_int = o[o.system.str.contains("internal")].iloc[0].value
    tpu = o[o.system.eq("TPU7x Ironwood")].iloc[0].value
    gb300 = o[o.system.eq("GB300 NVL72")].iloc[0].value
    b200 = o[o.system.eq("B200")].iloc[0].value
    c = Chart(
        id="CS3-owner-tco-per-chip-hour",
        title=f"Est.: an owned Ironwood chip-hour costs ~${tpu:.2f}, about half a GB300's ${gb300:.2f}",
        subtitle="All-in owner cost per accelerator-hour (capex amortisation, power, hosting), US$, SemiAnalysis model, July 2026",
        alt=(f"Horizontal bar chart of estimated owner TCO per accelerator-hour: TPU7x Ironwood ${tpu_int:.2f} for Google itself "
             f"and ${tpu:.2f} for an external owner, H100 $1.17, H200 $1.22, AMD MI355X $1.50, B200 ${b200:.2f}, GB200 NVL72 "
             f"$1.86, B300 $2.26, GB300 NVL72 ${gb300:.2f} and Vera Rubin NVL72 $3.61. These are per chip, not per unit of work: "
             f"Ironwood's hour is {1 - tpu / b200:.0%} cheaper than a B200's, but on one SemiAnalysis workload its cost per "
             "token was only about 18% lower, because chips differ in throughput."),
        data=[ECON], chapters=["CS3", "14", "15"],
        source="SemiAnalysis InferenceX TCO registry",
        source_ids=sources_of(o),
        note="Est. · per chip, not per token",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    ys = np.arange(len(o))
    cols = [GOOGLE if v == "Google" else (entity_color("amd") if v == "AMD" else NV) for v in o.vendor]
    bars = ax.barh(ys, o.value, color=cols, height=0.62, edgecolor="#FFFFFF")
    for b in bars:
        b.set_hatch("//")
        b.set_alpha(0.9)
    for y, v in zip(ys, o.value):
        ax.annotate(f"${v:.2f}", (v, y), xytext=(4, 0), textcoords="offset points", va="center", fontsize=9.5,
                    color=INK["title"], fontweight="bold")
    ax.set_yticks(ys)
    ax.set_yticklabels(o.system, fontsize=9.3)
    ax.set_xlim(0, o.value.max() * 1.15)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.axvline(gb300, color=NV_DARK, lw=0.8, ls=":")
    _ = NV
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=GOOGLE, label="Google TPU"), Patch(color=NV, label="NVIDIA"),
                       Patch(color=entity_color("amd"), label="AMD")], loc="lower right", fontsize=9)

    def _adj(*a, **k):
        k.update(left=0.22)
        return orig(*a, **k)
    orig = fig.subplots_adjust
    fig.subplots_adjust = _adj
    c.save(fig, ax, xlabel="Owner TCO per accelerator-hour (US$)", legend=False)
