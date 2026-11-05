"""Layer 12 (orchestration and cloud services) - CORE charts: the utilization economics of a GPU
($ per useful GPU-hour), where installed GPU-hours are lost, job-recovery losses as jobs grow,
rack fragmentation under random vs bin-packed placement, rental price per PFLOPS-hour by generation,
NVIDIA's multi-year cloud-service commitments (the DGX Cloud lease-back), neocloud power (active vs
contracted) and 2024 GPU purchases by buyer type.

Data: data/l12_utilization_scenarios.csv and data/l12_gpu_cloud_capacity.csv (owned by the layer-12
CORE author; documented in data/README.md) plus shared, read-only inputs: tco_model_inputs.csv,
system_specs.csv, gpu_rental_prices.csv, gpu_product_specs.csv, financials.csv,
l06_cluster_examples.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

CH = ["12"]
UTIL = "l12_utilization_scenarios.csv"
CAP = "l12_gpu_cloud_capacity.csv"
TCO = "tco_model_inputs.csv"
SYS = "system_specs.csv"
RENT = "gpu_rental_prices.csv"
SPECS = "gpu_product_specs.csv"
CLUST = "l06_cluster_examples.csv"
FIN = "financials.csv"
NEO = entity_color("startups")   # neoclouds have no palette entry: neutral gray (as in chart 14)


def _manual_axes(fig, rects):
    for a in list(fig.axes):
        fig.delaxes(a)
    return [fig.add_axes(r) for r in rects]


def _u(item: str, scenario: str = "all", rtype: str | None = None) -> pd.Series:
    d = load(UTIL)
    r = d[(d["item"] == item) & (d["scenario"] == scenario)]
    if rtype:
        r = r[r.record_type == rtype]
    return r.iloc[0]


def _tco(system: str, inp: str, basis: str | None = None) -> pd.Series:
    t = load(TCO)
    r = t[(t.system == system) & (t.input == inp)]
    if basis:
        r = r[r.basis.str.contains(basis, regex=False)]
    return r.iloc[0]


# --------------------------------------------------------------------------------------
# Shared cost model (also used for the numbers quoted on the pages)
# --------------------------------------------------------------------------------------
def cost_model() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cost per installed GPU-hour for three systems: (capex x (1 + cluster uplift)) / life / 8,760
    + max IT power per GPU x PUE x $/kWh. Returns (table, rows used)."""
    s = load(SYS).set_index("system")
    uplift = _u("cluster_uplift_pct")
    life6 = _u("useful_life_base_years")
    life5 = _u("useful_life_short_years")
    hours = _u("power_hours_basis")
    kwh = _tco("All", "electricity_price_us_industrial")
    pue_air = _tco("All", "pue_assumption_air_cooled")
    pue_liq = _tco("All", "pue_assumption_liquid_cooled")
    gb3_cap = _tco("GB300 NVL72", "capex_per_rack", "Morgan Stanley")
    vr_cap = _tco("Vera Rubin NVL72", "capex_per_rack", "Morgan Stanley (May")
    vr_name = [n for n in s.index if n.startswith("Vera Rubin NVL72")][0]
    rows = [
        ("DGX H200 (air)", s.loc["DGX H200"].est_price_usd_m, s.loc["DGX H200"].accelerators_per_system,
         s.loc["DGX H200"].power_kw, pue_air.value),
        ("GB300 NVL72", gb3_cap.value, 72, s.loc["GB300 NVL72"].power_kw, pue_liq.value),
        ("Vera Rubin NVL72", vr_cap.value, 72, s.loc[vr_name].power_kw, pue_liq.value),
    ]
    out = []
    for name, price_m, n, kw, pue in rows:
        capex_gpu = price_m * 1e6 / n * (1 + uplift.value / 100)
        power_hr = kw / n * pue * kwh.value
        for life in (life6.value, life5.value):
            out.append(dict(system=name, life=life, capex_gpu=capex_gpu, power_hr=power_hr,
                            dep_hr=capex_gpu / life / hours.value,
                            installed_hr=capex_gpu / life / hours.value + power_hr))
    used = pd.concat([s.loc[["DGX H200", "GB300 NVL72", vr_name]].reset_index(),
                      pd.DataFrame([uplift, life6, life5, hours, kwh, pue_air, pue_liq, gb3_cap, vr_cap])])
    return pd.DataFrame(out), used


# --------------------------------------------------------------------------------------
@register
def cost_per_useful_gpu_hour():
    m, used = cost_model()
    lv = load(UTIL)
    lv = lv[lv.record_type == "utilization_level"].value.astype(float).tolist()  # 30, 60, 90
    g6 = m[(m.system == "GB300 NVL72") & (m.life == 6)].iloc[0]
    g5 = m[(m.system == "GB300 NVL72") & (m.life == 5)].iloc[0]
    vr = m[(m.system == "Vera Rubin NVL72") & (m.life == 6)].iloc[0]
    h2 = m[(m.system == "DGX H200 (air)") & (m.life == 6)].iloc[0]
    lo, hi = lv[0] / 100, lv[-1] / 100
    c = Chart(
        id="12-cost-per-useful-gpu-hour",
        title=(f"Est.: at {lv[0]:.0f}% vs {lv[-1]:.0f}% utilization, a useful GB300 NVL72 GPU-hour costs "
               f"${g6.installed_hr / lo:.2f} vs ${g6.installed_hr / hi:.2f}"),
        subtitle=("US$ per useful GPU-hour = (capex +26% network/storage ÷ life + max power × PUE) ÷ utilization · "
                  "all Est.; excl. facility, staff, financing"),
        alt=(f"Line chart of estimated cost per useful GPU-hour against utilization. A GB300 NVL72 GPU costs about "
             f"${g6.installed_hr:.2f} per installed hour (capex ${g6.capex_gpu / 1e3:.0f}K incl. networking and storage, "
             f"6-year life, power ${g6.power_hr:.2f}/h), so ${g6.installed_hr / 0.3:.2f} per useful hour at 30% "
             f"utilization, ${g6.installed_hr / 0.6:.2f} at 60% and ${g6.installed_hr / 0.9:.2f} at 90%; with a 5-year "
             f"life ${g5.installed_hr / 0.3:.2f}, ${g5.installed_hr / 0.6:.2f} and ${g5.installed_hr / 0.9:.2f}. "
             f"Vera Rubin NVL72 (about ${vr.installed_hr:.2f} per installed hour) costs ${vr.installed_hr / 0.3:.2f}, "
             f"${vr.installed_hr / 0.6:.2f} and ${vr.installed_hr / 0.9:.2f}; DGX H200 about "
             f"${h2.installed_hr:.2f} per installed hour. Cost per useful hour scales with 1/utilization."),
        data=[UTIL, TCO, SYS], chapters=["12", "14"],
        source="MS, SemiAnalysis, resellers, EIA, 10-Ks (repo calc)",
        source_ids=sources_of(used) + ["S12015", "S34006"],
    )
    fig, ax = c.figure(width=11.5, height=6.2)
    u = np.linspace(0.2, 1.0, 81)
    series = [(h2, GEN_PAST, "-", "DGX H200 (6-yr life)"), (g5, NV, (0, (4, 3)), "GB300 NVL72 (5-yr life)"),
              (vr, NV_DARK, (0, (1.5, 2)), "Vera Rubin NVL72 (Est., 6-yr)"), (g6, NV, "-", "GB300 NVL72 (6-yr life)")]
    for r, col, ls, lab in series:
        ax.plot(u * 100, r.installed_hr / u, color=col, lw=2.4 if lab.startswith("GB300 NVL72 (6") else 2.0, ls=ls,
                zorder=3)
        ly = {"DGX H200 (6-yr life)": 0.55, "GB300 NVL72 (5-yr life)": 2.15, "GB300 NVL72 (6-yr life)": 1.35,
              "Vera Rubin NVL72 (Est., 6-yr)": 3.05}[lab]
        ax.annotate(f"{lab} · ${r.installed_hr:.2f}/h installed", (100, r.installed_hr), xytext=(102, ly),
                    textcoords="data", va="center", fontsize=8.6, annotation_clip=False,
                    color=INK["title"] if col != GEN_PAST else INK["text"], fontweight="bold" if col == NV else None,
                    arrowprops=dict(arrowstyle="-", color=INK["base"], lw=0.8))
    for pct in lv:
        x = pct / 100
        for r, dy in ((g6, -14), (vr, 10)):
            y = r.installed_hr / x
            ax.scatter([pct], [y], s=70, color=NV if r is g6 else NV_DARK, edgecolor="white", linewidth=1.2, zorder=5)
            ax.annotate(f"${y:.2f}", (pct, y), xytext=(8, dy), textcoords="offset points", fontsize=9.2,
                        color=INK["title"], fontweight="bold")
        ax.axvline(pct, color=INK["grid"], lw=1, zorder=1)
    ax.set_xlim(20, 100)
    ax.set_ylim(0, 16)
    ax.set_xticks([20, 30, 40, 50, 60, 70, 80, 90, 100], [f"{v}%" for v in [20, 30, 40, 50, 60, 70, 80, 90, 100]])
    _patch_right(fig, 0.7)
    c.save(fig, ax, xlabel="Utilization: share of installed GPU-hours doing useful work",
           ylabel="US$ per useful GPU-hour", legend=False)


def _patch_right(fig, right: float) -> None:
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw["right"] = right
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


# --------------------------------------------------------------------------------------
@register
def utilization_funnel():
    d = load(UTIL)
    f = d[d.record_type == "funnel"]
    stages = ["installed", "allocated", "effective_time", "mfu"]
    labels = ["Installed\nGPU-hours", "Allocated to a job\n(scheduler)", "Productive\n(after failures/restarts)",
              "Peak FLOPs actually used\n(× MFU)"]

    def chain(sc):
        v = f[f.scenario == sc].set_index("item").value.astype(float)
        a = v["allocated"]
        p = a * v["effective_time"] / 100
        return [100.0, a, p, p * v["mfu"] / 100]
    before, after = chain("before_fix"), chain("after_fix")
    c = Chart(
        id="12-utilization-funnel",
        title=(f"Est.: of 100 GPU-hours bought, only ~{before[-1]:.0f}–{after[-1]:.0f} hours' worth of peak FLOPs reach "
               f"the model"),
        subtitle=(f"% of installed GPU-hours left after each loss · allocation: Alibaba fleet before/after a scheduler fix "
                  f"(+{(after[-1] / before[-1] - 1) * 100:.0f}% output) · failures, MFU: Llama 3"),
        alt=(f"Grouped bar chart of where installed GPU-hours go (composite estimate). Before a scheduler fix: 100 installed, "
             f"{before[1]:.0f} allocated (Alibaba's 68% allocation ratio), {before[2]:.1f} productive after about 10% lost to "
             f"failures, restarts and checkpoints (Llama 3 reported over 90% effective training time) and {before[3]:.1f} "
             f"worth of peak FLOPs at 40% MFU. After the fix: 93 allocated, {after[2]:.1f} productive and {after[3]:.1f} "
             f"used, {after[-1] / before[-1]:.2f} times more useful work from the same hardware."),
        data=[UTIL], chapters=["12", "14"],
        source="Alibaba OSDI '26 trace paper; Meta Llama 3 paper (repo composite)",
        source_ids=sources_of(f),
        note="Composite illustration (Est.)",
    )
    fig, ax = c.figure(width=11, height=6.0)
    x = np.arange(len(stages))
    w = 0.36
    b1 = ax.bar(x - w / 2 - 0.01, before, w, color=GEN_PAST, label="Before: 68% of GPUs allocatable (fragmented)", zorder=2)
    b2 = ax.bar(x + w / 2 + 0.01, after, w, color=NV, label="After: 93% allocated (fragmentation-aware scheduler)",
                zorder=2)
    for bars in (b1, b2):
        for b in bars:
            ax.annotate(f"{b.get_height():.1f}" if b.get_height() < 100 else "100", (b.get_x() + b.get_width() / 2,
                        b.get_height()), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9.2,
                        color=INK["title"], fontweight="bold")
    ax.set_xticks(x, labels, fontsize=9.2)
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    c.save(fig, ax, ylabel="% of installed GPU-hours", legend=False, bottom=0.17)


# --------------------------------------------------------------------------------------
@register
def recovery_loss_vs_job_size():
    d = load(UTIL)
    fm = d[d.record_type == "failure_model"].set_index("item")
    g = float(fm.loc["gpus_in_job"].value)
    days = float(fm.loc["snapshot_days"].value)
    n_int = float(fm.loc["unexpected_interruptions"].value)
    rate = n_int / (days * 24 * g)  # interruptions per GPU-hour
    recs = [(float(fm.loc[k].value), k) for k in ("recovery_minutes_fast", "recovery_minutes_mid", "recovery_minutes_slow")]
    cl = load(CLUST)
    cl = cl[cl.gpus.notna()]

    def lost(n, minutes):
        lt = rate * n * minutes / 60
        return lt / (1 + lt) * 100
    l100_15, l100_3 = lost(100_000, recs[1][0]), lost(100_000, recs[0][0])
    mtbf100 = 60 / (rate * 100_000)
    c = Chart(
        id="12-recovery-loss-vs-job-size",
        title=(f"Est.: a 100k-GPU job fails every ~{mtbf100:.0f} min, so 15-min recoveries waste ~{l100_15:.0f}% of its time"),
        subtitle=(f"% of time lost to recovery vs job size · Llama 3 rate: {n_int:.0f} failures in {days:.0f} days on "
                  f"{g:,.0f} GPUs · lost = λT/(1+λT)"),
        alt=(f"Line chart, log-scale x-axis. Using Llama 3's {n_int:.0f} unexpected interruptions in {days:.0f} days on "
             f"{g:,.0f} GPUs (one every ~{60 / (rate * g) / 60:.1f} hours), the time a single job loses to recovery grows with "
             f"its size. At 16,384 GPUs: {lost(g, 3):.1f}% with 3-minute recovery, {lost(g, 15):.1f}% with 15 minutes and "
             f"{lost(g, 60):.0f}% with 60 minutes. At 100,000 GPUs (one failure every ~{mtbf100:.0f} minutes): "
             f"{l100_3:.0f}%, {l100_15:.0f}% and {lost(100_000, 60):.0f}%. At 800,000 GPUs even 3-minute recovery loses "
             f"{lost(800_000, 3):.0f}%. Fast automated recovery and fault-tolerant training are what make giant jobs viable."),
        data=[UTIL, CLUST], chapters=["12", "06"],
        source="Llama 3 paper; layer-06 cluster data (repo model)",
        source_ids=sources_of(d[d.record_type == "failure_model"]) + sources_of(cl),
    )
    fig, ax = c.figure(width=11, height=6.2)
    n = np.logspace(3, 6, 200)
    cols = {"recovery_minutes_fast": NV, "recovery_minutes_mid": NV_DARK, "recovery_minutes_slow": INK["text"]}
    styles = {"recovery_minutes_fast": "-", "recovery_minutes_mid": (0, (4, 3)), "recovery_minutes_slow": (0, (1.5, 2))}
    for minutes, key in recs:
        ax.plot(n, lost(n, minutes), color=cols[key], ls=styles[key], lw=2.2, zorder=3)
        xl = {"recovery_minutes_slow": 2.5e4, "recovery_minutes_mid": 6.0e4, "recovery_minutes_fast": 3.0e5}[key]
        ax.annotate(f"{minutes:.0f}-min recovery", (xl, lost(xl, minutes)), xytext=(-6, 8), textcoords="offset points",
                    ha="right", fontsize=9.2, color=INK["title"], fontweight="bold")
    marks = [(g, "Llama 3 job\n16,384", "left")]
    for _, r in cl.iterrows():
        if r.gpus >= 50_000:
            nm = "OCI Zettascale10\n800k (target)" if r.gpus >= 500_000 else (
                "Colossus\n100k" if r.gpus < 150_000 else "Colossus\n200k")
            marks.append((float(r.gpus), nm, "right" if r.gpus >= 500_000 or r.gpus < 150_000 else "left"))
    seen = set()
    for x, lab, ha in marks:
        if x in seen:
            continue
        seen.add(x)
        ax.axvline(x, color=INK["base"], lw=1, ls="-", zorder=1)
        ax.annotate(lab, (x, 98), xytext=(3 if ha == "left" else -3, 0), textcoords="offset points", fontsize=8.2,
                    va="top", ha=ha, color=INK["text"])
        ax.scatter([x], [lost(x, 15)], s=48, color=NV_DARK, edgecolor="white", zorder=4)
    ax.set_xscale("log")
    ax.set_xlim(1e3, 1e6)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100], ["0%", "20%", "40%", "60%", "80%", "100%"])
    c.save(fig, ax, xlabel="GPUs in one synchronous job", ylabel="% of time lost to failure recovery", logx=True,
           legend=False)


# --------------------------------------------------------------------------------------
def fragmentation_values() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Whole free NVL72 racks vs cluster allocation, for random (spread) placement of small jobs
    (exact hypergeometric expectation) and for bin-packing. Returns (grid, rows used)."""
    from math import comb
    d = load(UTIL)
    fr = d[d.record_type == "fragmentation_model"].set_index("item")
    racks = int(fr.loc["racks"].value)
    gpr = int(fr.loc["gpus_per_rack"].value)
    job = int(fr.loc["small_job_gpus"].value)
    spr = gpr // job                      # small-job slots per rack
    slots = racks * spr
    out = []
    for k in range(slots + 1):
        x = k / slots
        p_free = comb(slots - spr, k) / comb(slots, k) if k <= slots - spr else 0.0
        out.append(dict(alloc=x * 100, random=racks * p_free, packed=racks - int(np.ceil(k / spr - 1e-9)),
                        free_gpus=(1 - x) * racks * gpr))
    return pd.DataFrame(out), d[d.record_type == "fragmentation_model"]


@register
def fragmentation_whole_racks():
    g, used = fragmentation_values()
    racks = int(used.set_index("item").loc["racks"].value)
    at30 = g.iloc[(g.alloc - 30).abs().argmin()]
    at10 = g.iloc[(g.alloc - 10).abs().argmin()]
    c = Chart(
        id="12-fragmentation-whole-racks",
        title=(f"Est.: at 30% allocation, scattered 8-GPU jobs leave <1 whole NVL72 rack of {racks}; packed, "
               f"{at30.packed:.0f}"),
        subtitle=(f"Expected NVL72 racks with all 72 GPUs free vs share of an {racks}-rack cluster allocated to 8-GPU jobs "
                  f"(repo model)"),
        alt=(f"Line chart of a {racks}-rack, {racks * 72:,}-GPU NVL72 cluster filled with 8-GPU jobs. If the scheduler scatters "
             f"jobs randomly, whole free racks vanish fast: about {at10.random:.1f} remain at {at10.alloc:.0f}% allocation and "
             f"about {at30.random:.1f} at {at30.alloc:.0f}%, even though ~{at30.free_gpus:,.0f} GPUs are idle. A bin-packing, "
             f"topology-aware scheduler that fills racks one at a time keeps {at10.packed:.0f} and {at30.packed:.0f} racks whole. "
             f"Fragmentation, not a shortage of GPUs, is what blocks large jobs."),
        data=[UTIL], chapters=["12", "05"],
        source="repo model (hypergeometric placement); NVL72 rack size from NVIDIA",
        source_ids=sources_of(used),
        note="Illustrative model (Est.)",
    )
    fig, ax = c.figure(width=11.5, height=6.0)
    ax.step(g.alloc, g.packed, where="post", color=NV, lw=2.4, zorder=3)
    ax.plot(g.alloc, g.random, color=INK["text"], lw=2.2, ls=(0, (4, 3)), zorder=3)
    ax.annotate("Bin-packed / topology-aware:\nfill one rack before opening the next", (50.5, 8.6),
                xytext=(58, 12.5), fontsize=9.2, color=NV_DARK, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=NV_DARK))
    ax.annotate("Random spread: whole racks vanish\nwhile most GPUs are still idle", (15, g.iloc[(g.alloc - 15).abs().argmin()].random),
                xytext=(22, 7.5), fontsize=9.2, color=INK["title"], fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=INK["text"]))
    for row in (at10, at30):
        ax.scatter([row.alloc, row.alloc], [row.random, row.packed], s=60, color=[INK["text"], NV], edgecolor="white",
                   zorder=4)
        ax.annotate(f"{row.random:.1f}", (row.alloc, row.random), xytext=(6, 6), textcoords="offset points",
                    fontsize=9, color=INK["title"])
        ax.annotate(f"{row.packed:.0f}", (row.alloc, row.packed), xytext=(6, 4), textcoords="offset points",
                    fontsize=9, color=INK["title"], fontweight="bold")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, racks + 1)
    ax.set_yticks([0, 3, 6, 9, 12, 15, 18])
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100], [f"{v}%" for v in range(0, 101, 10)])
    c.save(fig, ax, xlabel="Share of cluster GPUs allocated to 8-GPU jobs", ylabel=f"Whole free NVL72 racks (of {racks})",
           legend=False)


# --------------------------------------------------------------------------------------
@register
def rental_cost_per_pflops_hour():
    r = load(RENT)
    s = load(SPECS).set_index("product")
    spec = {"H100": s.loc["H100 SXM"], "B200": s.loc["B200 (HGX)"], "GB200": s.loc["GB200 (per GPU)"]}
    pick = [("CoreWeave", "H100"), ("CoreWeave", "B200"), ("CoreWeave", "GB200"), ("Lambda", "H100"), ("Lambda", "B200")]
    rows = []
    for prov, gpu in pick:
        rr = r[(r.gpu == gpu) & r.provider.str.startswith(prov)].sort_values("date").iloc[-1]
        sp = spec[gpu]
        fp8 = sp.fp8_tflops_dense / 1000
        best = (sp.fp4_tflops_dense if pd.notna(sp.fp4_tflops_dense) else sp.fp8_tflops_dense) / 1000
        rows.append(dict(prov=prov, gpu=gpu, date=rr.date, price=rr.usd_per_gpu_hour, fp8=rr.usd_per_gpu_hour / fp8,
                         best=rr.usd_per_gpu_hour / best, best_fmt="FP4" if pd.notna(sp.fp4_tflops_dense) else "FP8",
                         source_id=f"{rr.source_id};{sp.source_id}"))
    d = pd.DataFrame(rows)
    cw = d[d.prov == "CoreWeave"].set_index("gpu")
    lb = d[d.prov == "Lambda"].set_index("gpu")
    fp8_lo, fp8_hi = sorted([lb.loc["H100"].fp8 / lb.loc["B200"].fp8, cw.loc["H100"].fp8 / cw.loc["B200"].fp8])
    b_lo, b_hi = sorted([lb.loc["H100"].best / lb.loc["B200"].best, cw.loc["H100"].best / cw.loc["B200"].best])
    c = Chart(
        id="12-rental-cost-per-pflops-hour",
        title=(f"List prices: a Blackwell PFLOPS-hour costs {fp8_lo:.1f}–{fp8_hi:.1f}× less than H100 at FP8, "
               f"{b_lo:.1f}–{b_hi:.1f}× less at FP4"),
        subtitle="On-demand list price ÷ dense peak PFLOPS per GPU, US$ per PFLOPS-hour · H100 has no FP4, so its best format is FP8",
        alt=(f"Grouped horizontal bar chart of rental price per dense PFLOPS-hour, 2025 list prices. CoreWeave: H100 "
             f"${cw.loc['H100'].price:.2f}/GPU-hr = ${cw.loc['H100'].fp8:.2f} per FP8 PFLOPS-hour; B200 "
             f"${cw.loc['B200'].price:.2f} = ${cw.loc['B200'].fp8:.2f} at FP8 and ${cw.loc['B200'].best:.2f} at FP4; GB200 "
             f"${cw.loc['GB200'].price:.2f} = ${cw.loc['GB200'].fp8:.2f} at FP8 and ${cw.loc['GB200'].best:.2f} at FP4. "
             f"Lambda: H100 ${lb.loc['H100'].price:.2f} = ${lb.loc['H100'].fp8:.2f}; B200 ${lb.loc['B200'].price:.2f} = "
             f"${lb.loc['B200'].fp8:.2f} at FP8 and ${lb.loc['B200'].best:.2f} at FP4. Blackwell is {fp8_lo:.1f}-{fp8_hi:.1f} "
             f"times cheaper per FLOP at the same precision and {b_lo:.1f}-{b_hi:.1f} times cheaper using FP4."),
        data=[RENT, SPECS], chapters=["12", "14"],
        source="CoreWeave, Lambda list prices; NVIDIA",
        source_ids=sources_of(d),
    )
    fig, _ = c.figure(width=11.5, height=6.0)
    ax = _manual_axes(fig, [[0.2, 0.13, 0.62, 0.69]])[0]
    y = np.arange(len(d))[::-1] * 1.0
    h = 0.36
    ax.barh(y + h / 2, d.fp8, h, color=GEN_PAST, label="At FP8 (same precision)", zorder=2)
    fp4 = d.best_fmt == "FP4"
    ax.barh(y[fp4.values] - h / 2, d.best[fp4], h, color=NV, zorder=2)
    for yi, (_, row) in zip(y, d.iterrows()):
        ax.annotate(f"${row.fp8:.2f}", (row.fp8, yi + h / 2), xytext=(4, 0), textcoords="offset points", va="center",
                    fontsize=8.8, color=INK["title"])
        if row.best_fmt == "FP4":
            ax.annotate(f"${row.best:.2f} at FP4", (row.best, yi - h / 2), xytext=(4, 0), textcoords="offset points",
                        va="center", fontsize=8.8, color=INK["title"], fontweight="bold")
        else:
            ax.annotate("no FP4 support", (0.02, yi - h / 2), va="center", fontsize=8.4, color=INK["muted"],
                        style="italic")
    ax.set_yticks(y, [f"{p} · {g}\n${pr:.2f}/GPU-hr ({dt})" for p, g, pr, dt in zip(d.prov, d.gpu, d.price, d.date)],
                  fontsize=8.8)
    ax.set_xlim(0, 3.9)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(facecolor=GEN_PAST, label="At FP8 (same precision)"),
                       Patch(facecolor=NV, label="At lowest precision (FP4 for Blackwell)")],
              loc="lower right", frameon=False, fontsize=8.8)
    c.save(fig, ax, xlabel="US$ per dense PFLOPS-hour", legend=False)


# --------------------------------------------------------------------------------------
@register
def gpu_purchases_2024():
    d = load(CAP)
    g = d[d.record_type.isin(["gpu_purchases", "installed_gpus"])].copy()
    g = g.sort_values("value")
    hyp = g[g.provider_type == "hyperscaler"].value.sum()
    tracked = g[g.record_type == "gpu_purchases"].value.sum()
    cwv = g[g.record_type == "installed_gpus"].value.iloc[0]
    c = Chart(
        id="12-gpu-purchases-by-buyer-2024",
        title=(f"Est.: three hyperscalers bought ~{hyp / 1e3:.0f}K of ~{tracked / 1e6:.2f}M tracked Hopper GPUs in 2024 "
               f"({hyp / tracked * 100:.0f}%)"),
        subtitle="Hopper GPUs bought in 2024 by buyer, thousands (Omdia Est.) · CoreWeave bar = installed base, all generations",
        alt=(f"Horizontal bar chart of estimated 2024 Hopper GPU purchases (Omdia): Microsoft 485,000; ByteDance and Tencent "
             f"about 230,000 each (mostly China-specific H20/H800); Meta 224,000; xAI/Tesla about 200,000; Amazon 196,000; "
             f"Google 169,000. The three hyperscalers total about {hyp / 1e3:.0f}K, {hyp / tracked * 100:.0f}% of the "
             f"{tracked / 1e6:.2f} million tracked. For comparison, CoreWeave reported more than {cwv / 1e3:.0f}K GPUs of all "
             f"generations installed at the end of 2024."),
        data=[CAP], chapters=["12", "13"],
        source="Omdia via Financial Times / DCD; CoreWeave S-1",
        source_ids=sources_of(g),
        note="Purchases are Omdia estimates (Est.)",
    )
    fig, _ = c.figure(width=11, height=6.0)
    ax = _manual_axes(fig, [[0.2, 0.13, 0.66, 0.69]])[0]
    col = {"Microsoft": entity_color("Microsoft"), "Amazon": entity_color("AWS"), "Google": entity_color("Google"),
           "Meta": entity_color("Meta"), "xAI / Tesla": entity_color("startups"), "ByteDance": entity_color("other"),
           "Tencent": entity_color("other"), "CoreWeave": "white"}
    y = np.arange(len(g))
    for yi, (_, r) in zip(y, g.iterrows()):
        if r.record_type == "installed_gpus":
            ax.barh(yi, r.value / 1e3, 0.62, color="#C9C8C2", edgecolor=NEO, hatch="///", lw=1.2, zorder=2)
        else:
            ax.barh(yi, r.value / 1e3, 0.62, color=col[r.provider], zorder=2)
        ax.annotate(f"{r.value / 1e3:.0f}K" + ("+" if r.record_type == "installed_gpus" else ""), (r.value / 1e3, yi),
                    xytext=(5, 0), textcoords="offset points", va="center", fontsize=9.2, fontweight="bold",
                    color=INK["title"])
    ax.set_yticks(y, [f"{p}  ·  {t}" for p, t in zip(g.provider, g.provider_type)], fontsize=9.2)
    ax.set_xlim(0, 560)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(handles=[Patch(facecolor=entity_color("Microsoft"), label="Hyperscaler (entity colour)"),
                       Patch(facecolor=entity_color("other"), label="China platform"),
                       Patch(facecolor="#C9C8C2", edgecolor=NEO, hatch="///", label="Neocloud installed base (different metric)")],
              loc="lower right", frameon=False, fontsize=8.6)
    c.save(fig, ax, xlabel="Thousands of GPUs", legend=False)


# --------------------------------------------------------------------------------------
@register
def nvidia_cloud_service_commitments():
    f = load(FIN)
    d = f[f.metric == "cloud_service_commitments"].copy()
    d["end"] = pd.to_datetime(d.period_end)
    d = d.sort_values("end").drop_duplicates("period_end")
    first, last = d.iloc[0], d.iloc[-1]
    peak = d.value.max()
    c = Chart(
        id="12-nvidia-cloud-service-commitments",
        title=(f"NVIDIA's cloud-service commitments rose ~{last.value / first.value:.0f}× to ${last.value:.0f}B: "
               f"it is now a big GPU-cloud tenant"),
        subtitle="Multi-year cloud service agreements disclosed in 10-K/10-Q filings, US$ B at period end (capacity NVIDIA rents from clouds)",
        alt=(f"Bar chart of NVIDIA's disclosed multi-year cloud service agreements: ${first.value:.2f}B at the end of FY2023 "
             f"(January 2023, just before DGX Cloud launched), $10.6B at Q1 FY2026 (April 2025), $27.0B at FY2026 year-end "
             f"(January 2026), ${peak:.0f}B at Q1 FY2027 and ${last.value:.0f}B at Q2 FY2027 (July 2026). The commitments pay "
             f"for capacity NVIDIA leases from cloud partners for DGX Cloud and, increasingly, its own research; they are "
             f"separate from the $36B of AI-cloud capacity agreements disclosed in July 2026."),
        data=[FIN], chapters=["12", "13"],
        source="NVIDIA 10-K and 10-Q filings",
        source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=11, height=5.8)
    lab = {"FY2023": "FY2023 end\n(Jan 2023)", "Q1FY26": "Q1 FY2026\n(Apr 2025)", "FY2026": "FY2026 end\n(Jan 2026)",
           "Q4FY26": "FY2026 end\n(Jan 2026)", "Q1FY27": "Q1 FY2027\n(Apr 2026)", "Q2FY27": "Q2 FY2027\n(Jul 2026)"}
    x = np.arange(len(d))
    cols = [GEN_PAST] * (len(d) - 1) + [NV]
    ax.bar(x, d.value, color=cols, width=0.6, zorder=2)
    for xi, v in zip(x, d.value):
        ax.annotate(f"${v:.1f}B" if v < 10 else f"${v:.0f}B", (xi, v), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=9.6, fontweight="bold", color=INK["title"])
    ax.set_xticks(x, [lab.get(p, p) for p in d.period], fontsize=9.2)
    events = [(0, "Mar 2023: DGX Cloud launches\non OCI, then Azure and GCP"), (1, "May 2025: DGX Cloud\nLepton marketplace"),
              (2, "Sep 2025: DGX Cloud\nrefocused on internal R&D")]
    for xi, txt in events:
        ax.annotate(txt, (xi, d.value.iloc[xi]), xytext=(0, 46 if xi else 58), textcoords="offset points",
                    ha="center", fontsize=8.4, color=INK["text"],
                    # QA 2026-11-05: stop the leader line above the value label instead of striking through it
                    arrowprops=dict(arrowstyle="-", color=INK["base"], shrinkB=17))
    ax.set_ylim(0, 38)
    c.save(fig, ax, ylabel="US$ B of commitments", legend=False, bottom=0.15)


# --------------------------------------------------------------------------------------
@register
def neocloud_power():
    d = load(CAP)
    p = d[d.record_type == "power"].copy()
    cw = p[p.provider == "CoreWeave"].copy()
    cw["when"] = pd.to_datetime(cw.period + "-15")
    act = cw[cw.metric == "active_power"].sort_values("when")
    con = cw[cw.metric == "contracted_power"].sort_values("when")
    tgt = cw[cw.metric == "active_power_target"]
    a0, a1 = act.iloc[0], act.iloc[-1]
    months = (a1.when.year - a0.when.year) * 12 + a1.when.month - a0.when.month
    clast = con.iloc[-1]
    c = Chart(
        id="12-neocloud-power-active-vs-contracted",
        title=(f"CoreWeave's live power grew ~{a1.value / a0.value:.0f}× to {a1.value:.1f} GW in {months} months; "
               f"contracts run ~{clast.value / a1.value:.0f}× ahead"),
        subtitle="Data-center power, GW · active = energized and billing; contracted = signed future capacity · hatched = target or secondary estimate",
        alt=(f"Two panels. Left, CoreWeave: active power {a0.value:.2f} GW at end-2024, {act.value.iloc[1]:.2f} GW at end-2025 and "
             f"{a1.value:.1f} GW in mid-2026, with about {tgt.value.iloc[0]:.2f} GW targeted for end-2026; contracted power "
             f"rose from {con.value.iloc[0]:.1f} GW to {con.value.iloc[1]:.1f} GW and {clast.value:.1f} GW by August 2026. "
             f"Right, contracted vs active: CoreWeave {clast.value:.1f} vs {a1.value:.1f} GW; Nebius targets about 5 GW "
             f"contracted by end-2026; Crusoe about 4.9 GW contracted and 0.2 GW energized at Abilene (secondary estimate)."),
        data=[CAP], chapters=["12", "08"],
        source="CoreWeave filings and results; DCD; MarkTechPost (secondary)",
        source_ids=sources_of(p),
    )
    fig, _ = c.figure(width=11, height=6.0)
    ax1, ax2 = _manual_axes(fig, [[0.07, 0.14, 0.5, 0.68], [0.68, 0.14, 0.29, 0.68]])
    ax1.plot(act.when, act.value, color=NEO, lw=2.4, marker="o", ms=8, zorder=3, label="Active (live)")
    ax1.plot(con.when, con.value, color=NEO, lw=2, ls=(0, (4, 3)), marker="s", ms=7, mfc="white", zorder=3,
             label="Contracted")
    tw = pd.to_datetime(tgt.period + "-15").iloc[0]
    ax1.plot([a1.when, tw], [a1.value, tgt.value.iloc[0]], color=NEO, lw=1.6, ls=":", zorder=2)
    ax1.scatter([tw], tgt.value, marker="o", s=64, facecolor="white", edgecolor=NEO, zorder=4)
    ax1.annotate(f"YE2026 target\n{tgt.value.iloc[0]:.2f} GW", (tw, tgt.value.iloc[0]), xytext=(0, -30),
                 textcoords="offset points", ha="center", fontsize=8.4, color=INK["text"])
    for _, r in act.iterrows():
        ax1.annotate(f"{r.value:.2f} GW" if r.value < 1 else f"{r.value:.1f} GW", (r.when, r.value), xytext=(0, 9),
                     textcoords="offset points", ha="center", fontsize=8.8, fontweight="bold", color=INK["title"])
    for _, r in con.iterrows():
        ax1.annotate(f"{r.value:.1f}", (r.when, r.value), xytext=(0, 8), textcoords="offset points", ha="center",
                     fontsize=8.8, color=INK["title"])
    ax1.set_ylim(0, 5)
    ax1.set_xlim(pd.Timestamp("2024-09-01"), pd.Timestamp("2027-02-28"))
    ticks = pd.to_datetime(["2025-01-01", "2025-07-01", "2026-01-01", "2026-07-01", "2027-01-01"])
    ax1.set_xticks(ticks, [t.strftime("%b %Y") for t in ticks])
    ax1.set_ylabel("GW")
    ax1.set_title("CoreWeave: active vs contracted", fontsize=10.5, color=INK["title"], loc="left")
    ax1.legend(loc="upper left", frameon=False, fontsize=9)
    ax1.tick_params(length=0)
    bars = [("CoreWeave", clast.value, a1.value, False, False),
            ("Nebius", p[(p.provider == "Nebius")].value.iloc[0], np.nan, True, False),
            ("Crusoe", p[(p.provider == "Crusoe") & (p.metric == "contracted_power")].value.iloc[0],
             p[(p.provider == "Crusoe") & (p.metric == "active_power")].value.iloc[0], True, True)]
    x = np.arange(len(bars))
    for xi, (name, cval, aval, c_est, a_est) in zip(x, bars):
        bc = ax2.bar(xi - 0.19, cval, 0.36, color="#C9C8C2", edgecolor=NEO, lw=1, zorder=2)
        if c_est:
            bc[0].set_hatch("///")
        ax2.annotate(f"{cval:.1f}", (xi - 0.19, cval), xytext=(0, 3), textcoords="offset points", ha="center",
                     fontsize=8.8, color=INK["title"])
        if not np.isnan(aval):
            ba = ax2.bar(xi + 0.19, aval, 0.36, color=NEO, zorder=2)
            if a_est:
                ba[0].set_hatch("///")
            ax2.annotate(f"{aval:.1f}", (xi + 0.19, aval), xytext=(0, 3), textcoords="offset points", ha="center",
                         fontsize=8.8, fontweight="bold", color=INK["title"])
        else:
            ax2.annotate("n/d", (xi + 0.19, 0.08), ha="center", fontsize=8.2, color=INK["muted"])
    ax2.set_xticks(x, ["CoreWeave\n(Aug 2026)", "Nebius\n(YE26 target)", "Crusoe\n(secondary)"], fontsize=8.8)
    ax2.set_ylim(0, 6)
    ax2.set_title("Contracted (light) vs active (dark), GW", fontsize=10.5, color=INK["title"], loc="left")
    ax2.tick_params(length=0)
    ax2.spines[["top", "right"]].set_visible(False)
    c.save(fig, ax1, legend=False)
