"""Layer 09 (CUDA and system software) strategy charts: day-0 software gap, payoff history, software M&A, monetization.

Owner: layer-09 STRATEGY agent. Data: data/l09_software_deals.csv, l09_dsv4_catchup.csv, l09_software_price_per_gpu.csv
(documented in data/README.md) and data/financials.csv (Data Center revenue, R&D).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from style import Chart, GEN_PAST, INK, NV, entity_color, load, register, sources_of

DEALS = "l09_software_deals.csv"
DSV4 = "l09_dsv4_catchup.csv"
PRICE = "l09_software_price_per_gpu.csv"
LAG = "l09_rocm_lag.csv"
FIN = "financials.csv"

ACQ_COLOR = {
    "NVIDIA": NV,
    "AMD": entity_color("AMD"),
    "Qualcomm": entity_color("Qualcomm"),
    "Red Hat (IBM)": entity_color("other"),
}


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _date(s: str) -> pd.Timestamp:
    s = str(s)
    if len(s) == 7:
        s += "-15"
    return pd.Timestamp(s)


# --------------------------------------------------------------------------------------
# 1. DeepSeek-V4 day-0 gap: ROCm software catch-up vs MI355X silicon parity
# --------------------------------------------------------------------------------------
@register
def mi355x_deepseek_v4_catchup():
    df = load(DSV4)
    tco = float(df[df.record_type.eq("tco")].value.iloc[0])
    fr = df[df.record_type.eq("frontier")].sort_values("days_since_first_light").copy()
    iso = df[df.record_type.eq("iso")].sort_values("days_since_first_light").copy()
    for d in (fr, iso):
        d["cost"] = tco / (d.value * 3600) * 1e6
    sp = df[df.record_type.eq("spec_ratio")]
    first, last = fr.iloc[0], fr.iloc[-1]
    ratio = first.cost / last.cost
    iso_ratio = iso.cost.iloc[0] / iso.cost.iloc[-1]
    c = Chart(
        id="09-mi355x-deepseek-v4-catchup",
        title=(f"Kernel work made MI355X's DeepSeek-V4 tokens {ratio:.0f}× cheaper in "
               f"{int(last.days_since_first_light)} days; the silicon was never the gap"),
        subtitle=(f"Left: MI355X DeepSeek-V4-Pro cost per M tokens (SGLang, 8k/1k) at ${tco:.2f}/GPU-hour TCO (Est.); "
                  "right: MI355X ÷ B200 specs"),
        alt=(f"Two panels. Left, log scale: converting SemiAnalysis throughput into cost at an estimated ${tco:.2f} per "
             f"GPU-hour, MI355X's DeepSeek-V4-Pro cost at peak throughput fell from about ${first.cost:.2f} per million "
             f"tokens on day 0 (FP8 only) to ${last.cost:.2f} after {int(last.days_since_first_light)} days and 31 kernel "
             f"PRs, about {ratio:.0f} times cheaper; at a usable 15 tokens/s per user it fell from ${iso.cost.iloc[0]:.2f} "
             f"(day 7) to ${iso.cost.iloc[-1]:.2f}, about {iso_ratio:.0f} times, while CUDA recipes worked on day 0. "
             "Right: on paper MI355X has 1.60x B200's HBM capacity, equal 8 TB/s bandwidth, 1.12x dense FP4 and FP8 and "
             "0.64x scale-up bandwidth, so the day-0 gap was software, not silicon."),
        data=[DSV4], chapters=["09", "15", "11"],
        source="SemiAnalysis InferenceX articles and TCO model", source_ids=sources_of(df),
        note="Est. cost = TCO ÷ throughput",
    )
    fig, (ax, ax2) = c.figure_grid(1, 2, width=12.2, height=5.9, gridspec_kw={"width_ratios": [1.55, 1]})
    amd = entity_color("AMD")
    ax.plot(fr.days_since_first_light, fr.cost, color=amd, marker="o", markersize=8, lw=2.2,
            label="At peak throughput (any interactivity)")
    ax.plot(iso.days_since_first_light, iso.cost, color=amd, marker="s", markersize=7, lw=1.8, ls="--",
            alpha=0.7, label="At 15 tok/s per user (usable)")
    for r in fr.itertuples():
        lab = f"${r.cost:.2f}" + (" (FP8)" if r.precision == "FP8" else "")
        dy = 9 if r.days_since_first_light not in (9,) else 9
        ax.annotate(lab, (r.days_since_first_light, r.cost), xytext=(0, -16 if r.days_since_first_light in (7, 15) else dy),
                    textcoords="offset points", ha="center", fontsize=9, color=INK["title"], fontweight="bold")
    for r in iso.itertuples():
        if r.days_since_first_light in (7, 26):
            ax.annotate(f"${r.cost:.2f}", (r.days_since_first_light, r.cost), xytext=(0, 9), textcoords="offset points",
                        ha="center", fontsize=8.6, color=amd)
    ax.text(0.98, 0.96, "CUDA (B200/B300, vLLM and SGLang):\nnative recipes worked on day 0",
            transform=ax.transAxes, ha="right", va="top", fontsize=9, color=NV, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", fc="#FFFFFF", ec=NV, lw=1))
    ax.set_yscale("log")
    ax.set_ylim(0.08, 20)
    ax.set_xlim(-2, 29)
    ax.set_xticks([0, 7, 9, 15, 26])
    ax.legend(loc="lower left", fontsize=8.6)
    ax.set_xlabel("Days since day-0 run (2026-04-25)")
    ax.set_ylabel("US$ per million tokens (log scale)")
    # right panel: spec ratios
    order = ["hbm_capacity", "hbm_bandwidth", "dense_fp4", "dense_fp8", "scale_up_bandwidth"]
    names = {"hbm_capacity": "HBM capacity", "hbm_bandwidth": "HBM bandwidth", "dense_fp4": "Dense FP4",
             "dense_fp8": "Dense FP8", "scale_up_bandwidth": "Scale-up bandwidth"}
    s = sp.set_index("metric").reindex(order)
    y = np.arange(len(order))[::-1]
    cols = [amd if v >= 1 else GEN_PAST for v in s.value]
    ax2.barh(y, s.value, color=[amd if v >= 1 else "#E8A0AD" for v in s.value], height=0.6)
    for yi, v, n in zip(y, s.value, s.notes):
        ax2.text(v + 0.03, yi, f"{v:.2f}×", va="center", fontsize=9.5, color=INK["title"], fontweight="bold")
    ax2.axvline(1.0, color=NV, lw=1.6, ls="--")
    ax2.text(1.0, len(order) - 0.35, "B200 = 1.0", color=NV, fontsize=8.6, ha="center", fontweight="bold")
    ax2.set_yticks(y, [names[m] for m in order])
    ax2.set_xlim(0, 2.0)
    ax2.set_xlabel("MI355X ÷ B200 (paper specs)")
    ax2.grid(axis="y", visible=False)
    ax2.grid(axis="x", color=INK["grid"], lw=0.6)
    _ = cols
    _margins(fig, wspace=0.42, left=0.07, right=0.97)
    c.save(fig, [ax, ax2], legend=False, logy=True, bottom=0.14)


# --------------------------------------------------------------------------------------
# 2. The decade before payoff: Data Center revenue vs total R&D
# --------------------------------------------------------------------------------------
@register
def dc_revenue_vs_rd():
    df = load(FIN)
    d = df[(df.period_type.eq("FY")) & df.metric.isin(["revenue_data_center", "rd_expense"])].copy()
    d["fy"] = d.period.str[2:].astype(int)
    d = d[d.fy.between(2016, 2026)]
    dc = d[d.metric.eq("revenue_data_center")].set_index("fy").value.sort_index()
    rd = d[d.metric.eq("rd_expense")].set_index("fy").value.sort_index()
    cross = int(next(fy for fy in dc.index if dc[fy] > rd[fy]))
    mult = dc[2026] / rd[2026]
    c = Chart(
        id="09-dc-revenue-vs-rd",
        title=f"Data Center revenue first topped NVIDIA's total R&D in FY{cross}, a decade after CUDA 1.0",
        subtitle=f"NVIDIA Data Center revenue vs total company R&D, US$ B per fiscal year, FY2016–FY2026 (FY2026: {mult:.0f}× R&D)",
        alt=(f"Log-scale line chart, FY2016 to FY2026. NVIDIA Data Center revenue was ${dc[2016]:.2f}B in FY2016 against "
             f"${rd[2016]:.2f}B of total R&D, crossed above R&D in FY{cross} (${dc[cross]:.2f}B vs ${rd[cross]:.2f}B), "
             f"reached ${dc[2024]:.1f}B in FY2024 and ${dc[2026]:.1f}B in FY2026, about {mult:.0f} times R&D of "
             f"${rd[2026]:.1f}B. CUDA 1.0 shipped in June 2007 (FY2008) and cuDNN in 2014, so the platform ran for about "
             "a decade before the data-center business paid for the company's research."),
        data=[FIN], chapters=["09", "16", "CS2"],
        source="NVIDIA 10-Ks (financials.csv)", source_ids=sources_of(d),
        note="Pre-FY2026 rows: QA pending",
    )
    fig, ax = c.figure(width=10.8, height=5.9)
    ax.plot(dc.index, dc.values, color=NV, marker="o", markersize=8, lw=2.4, label="Data Center revenue")
    ax.plot(rd.index, rd.values, color=INK["text"], marker="s", markersize=7, lw=2, label="Total R&D expense")
    ax.annotate(f"FY{cross}: ${dc[cross]:.1f}B vs ${rd[cross]:.1f}B", (cross, dc[cross]), xytext=(-150, 34),
                textcoords="offset points", fontsize=9, color=INK["title"],
                arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.8))
    for fy in (2016, 2024, 2026):
        ax.annotate(f"${dc[fy]:.1f}B" if dc[fy] >= 1 else f"${dc[fy]:.2f}B", (fy, dc[fy]), xytext=(0, 9),
                    textcoords="offset points", ha="center", fontsize=9, color=NV, fontweight="bold")
    ax.annotate(f"${rd[2026]:.1f}B", (2026, rd[2026]), xytext=(0, -16), textcoords="offset points", ha="center",
                fontsize=9, color=INK["text"])
    marks = [(2018, "Volta Tensor Cores\n(Dec 2017, FY2018)"), (2023, "ChatGPT launch\n(Nov 2022, FY2023)")]
    for fy, lab in marks:
        ax.axvline(fy, color=INK["base"], lw=1, ls=":")
        ax.text(fy + 0.08, 0.2, lab, fontsize=8.3, color=INK["muted"], va="bottom")
    ax.text(2016.05, 300, "Before FY2016: CUDA 1.0 (FY2008), AlexNet on two GTX 580s (2012),\n"
            "cuDNN (2014) — no separately reported data-center line", fontsize=8.5, color=INK["text"], va="top")
    ax.set_yscale("log")
    ax.set_ylim(0.15, 500)
    ax.set_xticks(range(2016, 2027), [f"FY{y}" for y in range(2016, 2027)], fontsize=8.8)
    ax.legend(loc="lower right")
    c.save(fig, ax, xlabel="NVIDIA fiscal year (ends late January)", ylabel="US$ B per year", logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 3. Software M&A timeline (swimlanes by acquirer)
# --------------------------------------------------------------------------------------
@register
def software_deals_timeline():
    df = load(DEALS)
    d = df[df.record_type.eq("deal")].copy()
    d["t"] = d.announce_date.map(_date)
    lanes = ["NVIDIA", "AMD", "Qualcomm", "Red Hat (IBM)"]
    since = d[d.t >= pd.Timestamp("2023-01-01")]
    chip_since = since[since.acquirer.isin(["NVIDIA", "AMD", "Qualcomm"])]
    chip_before = d[(d.t < pd.Timestamp("2023-01-01")) & d.acquirer.isin(["NVIDIA", "AMD", "Qualcomm"])]
    c = Chart(
        id="09-software-deals-timeline",
        title=(f"Chip vendors made {len(chip_since)} AI-software deals from 2023 to 2026, "
               f"against {len(chip_before)} tracked in 2008–2022"),
        subtitle="Compiler, model-optimization, orchestration and developer-tool acquisitions, one row per deal; dot area = disclosed or reported value",
        alt=(f"Dot timeline of AI-software acquisitions, one row per deal. NVIDIA: Ageia (2008), PGI (2013), Bright Computing (2022), then "
             "OmniML, Run:ai (~$700M), Deci (~$300M), Brev.dev, OctoAI (~$250M), Gretel, Lepton AI, CentML (~$400M) and "
             "SchedMD from 2023 to 2025. AMD: Nod.ai (2023), Silo AI ($665M, 2024), Brium, the Untether AI team and MK1 (2025). "
             "Qualcomm: Modular (~$3.9B, announced June 2026, closed July 2026). Red Hat: Neural Magic (2024). "
             f"{len(chip_since)} chip-vendor software deals since 2023 versus {len(chip_before)} in the prior 15 years tracked here."),
        data=[DEALS], chapters=["09", "13", "19"],
        source="company announcements and press reports", source_ids=sources_of(d),
        note="Excludes NVIDIA–Groq licence",
    )
    fig, ax = c.figure(width=11.5, height=7.4)
    d = d.sort_values("t").reset_index(drop=True)
    n = len(d)
    ax.axvspan(pd.Timestamp("2023-01-01"), pd.Timestamp("2027-03-31"), color="#F4F3EE", zorder=0)
    for i, r in enumerate(d.itertuples()):
        y = n - 1 - i
        col = ACQ_COLOR[r.acquirer]
        ax.plot([pd.Timestamp("2007-01-01"), r.t], [y, y], color=INK["grid"], lw=0.8, zorder=1)
        v = r.value_usd_m
        if pd.notna(v):
            ax.scatter(r.t, y, s=max(70, v * 0.32), color=col, alpha=0.9, edgecolor="#FFFFFF", lw=1.2, zorder=3)
            lab = f"${v/1000:.1f}B" if v >= 1000 else f"${v:,.0f}M"
            ax.annotate(lab, (r.t, y), xytext=(-12, 0), textcoords="offset points", ha="right", va="center",
                        fontsize=8.6, color=INK["title"], fontweight="bold")
        else:
            ax.scatter(r.t, y, s=60, facecolor="#FFFFFF", edgecolor=col, lw=2, zorder=3)
    ax.set_yticks(range(n), [f"{t} ({a.replace(' (IBM)', '')}, {str(dt)[:4]})" for t, a, dt in
                             zip(d.target[::-1], d.acquirer[::-1], d.announce_date[::-1])], fontsize=8.6)
    for lab, a in zip(ax.get_yticklabels(), d.acquirer[::-1]):
        lab.set_color(ACQ_COLOR.get(a, INK["text"]) if a != "Red Hat (IBM)" else INK["text"])
    ax.set_ylim(-0.8, n - 0.2)
    ax.set_xlim(pd.Timestamp("2007-01-01"), pd.Timestamp("2027-03-31"))
    ax.text(pd.Timestamp("2022-09-01"), n - 7.5, f"Shaded: 2023–2026,\n{len(chip_since)} chip-vendor deals →",
            fontsize=9.5, color=INK["title"], va="center", ha="right", fontweight="bold")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"], lw=0.5)
    handles = [Line2D([0], [0], marker="o", ls="", markersize=9, color=ACQ_COLOR[k], label=k)
               for k in ["NVIDIA", "AMD", "Qualcomm", "Red Hat (IBM)"]]
    handles.append(Line2D([0], [0], marker="o", ls="", markersize=9, markerfacecolor="#FFFFFF",
                          markeredgecolor=INK["text"], label="Value undisclosed"))
    ax.legend(handles=handles, loc="lower left", fontsize=8.8)
    _margins(fig, left=0.25, right=0.985)
    c.save(fig, ax, xlabel="Announcement date", legend=False)


# --------------------------------------------------------------------------------------
# 4. What software teams have cost
# --------------------------------------------------------------------------------------
@register
def software_deal_values():
    df = load(DEALS)
    d = df[df.value_usd_m.notna()].copy()
    d["year"] = d.announce_date.str[:4]
    deals = d[d.record_type.eq("deal")]
    ref = d[d.record_type.eq("reference")]
    mod = float(deals[deals.target.eq("Modular")].value_usd_m.iloc[0])
    runai = float(deals[deals.target.eq("Run:ai")].value_usd_m.iloc[0])
    val = float(ref[ref.category.eq("valuation reference")].value_usd_m.iloc[0])
    raised = float(ref[ref.category.eq("capital raised")].value_usd_m.iloc[0])
    c = Chart(
        id="09-software-deal-values",
        title=f"Qualcomm's ~${mod/1000:.1f}B for Modular: {mod/runai:.1f}× Run:ai, {mod/val:.1f}× Modular's 2025 valuation",
        subtitle="Disclosed or reported prices of AI-software acquisitions, US$ M; gray = Modular funding reference points",
        alt=(f"Horizontal bar chart of AI-software deal values: Qualcomm-Modular about ${mod:,.0f}M (2026), NVIDIA-Run:ai about "
             f"${runai:,.0f}M (2024), AMD-Silo AI $665M (2024), NVIDIA-CentML up to about $400M (2025), NVIDIA-Deci about "
             f"$300M (2024) and NVIDIA-OctoAI about $250M (2024). For reference, Modular was valued at ${val:,.0f}M in its "
             f"September 2025 Series C and had raised ${raised:,.0f}M in total, so Qualcomm paid about {mod/val:.1f} times "
             f"the last private valuation and about {mod/raised:.0f} times the capital invested."),
        data=[DEALS], chapters=["09", "19", "13"],
        source="company announcements and press reports", source_ids=sources_of(d),
    )
    rows = []
    for r in deals.itertuples():
        rows.append((f"{r.acquirer.replace(' (IBM)', '')} → {r.target} ({r.year})", r.value_usd_m, ACQ_COLOR[r.acquirer],
                     r.value_basis))
    for r in ref.itertuples():
        lab = ("Modular Series C valuation (Sep 2025)" if r.category == "valuation reference"
               else "Modular total capital raised (2022–25)")
        rows.append((lab, r.value_usd_m, entity_color("other"), "reference"))
    rows.sort(key=lambda x: x[1])
    fig, ax = c.figure(width=11, height=5.8)
    y = np.arange(len(rows))
    bars = ax.barh(y, [r[1] for r in rows], color=[r[2] for r in rows], height=0.62)
    for b, r in zip(bars, rows):
        if r[3] == "reported":
            b.set_hatch("//")
            b.set_edgecolor("#FFFFFF")
        lab = f"${r[1]/1000:.1f}B" if r[1] >= 1000 else f"${r[1]:,.0f}M"
        if r[3] == "reported":
            lab += " (reported)"
        ax.text(r[1] + 40, b.get_y() + b.get_height() / 2, lab, va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, [r[0] for r in rows], fontsize=9)
    ax.set_xlim(0, 4800)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"], lw=0.6)
    handles = [Line2D([0], [0], marker="s", ls="", markersize=10, color=ACQ_COLOR[k], label=k)
               for k in ["NVIDIA", "AMD", "Qualcomm"]]
    handles.append(Line2D([0], [0], marker="s", ls="", markersize=10, color=entity_color("other"), label="Reference"))
    ax.legend(handles=handles, loc="lower right", fontsize=9)
    _margins(fig, left=0.31, right=0.97)
    c.save(fig, ax, xlabel="US$ M (hatched = press-reported price)", legend=False)


# --------------------------------------------------------------------------------------
# 5. What NVIDIA charges for software per GPU-year vs the hardware it rides on
# --------------------------------------------------------------------------------------
@register
def software_price_per_gpu_year():
    df = load(PRICE)
    d = df.sort_values("value_usd_per_gpu_year")
    tco = float(df[df.item.str.startswith("B200 owner")].value_usd_per_gpu_year.iloc[0])
    lst = float(df[df.item.str.contains("1-year")].value_usd_per_gpu_year.iloc[0])
    huang = float(df[df.item.str.startswith("Huang")].value_usd_per_gpu_year.iloc[0])
    c = Chart(
        id="09-software-price-per-gpu-year",
        title=(f"NVIDIA AI Enterprise lists at ${lst:,.0f} per GPU-year, ~{lst/tco*100:.0f}% of a B200's "
               "yearly owner cost"),
        subtitle="US$ per GPU per year: NVIDIA software price points (green) vs B200 hardware cost references (gray, Est.)",
        alt=(f"Horizontal bar chart in US dollars per GPU per year. NVIDIA AI Enterprise: ${huang:,.0f} (Jensen Huang's "
             f"October 2026 figure), $3,600 (five-year subscription), ${lst:,.0f} (one-year list) and up to $8,760 in the "
             f"cloud at $1 per GPU-hour if billed every hour. For comparison a B200 costs an owner about ${tco:,.0f} a year "
             f"all-in (SemiAnalysis TCO estimate) and about $32,412 a year to rent, so list-price software adds roughly "
             f"{lst/tco*100:.0f}% and Huang's figure about {huang/tco*100:.0f}%."),
        data=[PRICE], chapters=["09", "12", "13"],
        source="NVIDIA licensing guide as reported; SemiAnalysis TCO", source_ids=sources_of(df),
        note="Hardware references hatched = estimates",
    )
    fig, ax = c.figure(width=11, height=5.4)
    y = np.arange(len(d))
    cols = [NV if g == "nvidia_software" else "#B5B5B5" for g in d.group]
    bars = ax.barh(y, d.value_usd_per_gpu_year, color=cols, height=0.6)
    for b, r in zip(bars, d.itertuples()):
        if r.group == "hardware_reference":
            b.set_hatch("//")
            b.set_edgecolor("#FFFFFF")
        ax.text(r.value_usd_per_gpu_year + 300, b.get_y() + b.get_height() / 2,
                f"${r.value_usd_per_gpu_year:,.0f}" + ("  (Est.)" if r.group == "hardware_reference" else ""),
                va="center", fontsize=9.2, color=INK["title"])
    ax.set_yticks(y, d.item, fontsize=9)
    ax.set_xlim(0, 37000)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"], lw=0.6)
    _margins(fig, left=0.36, right=0.97)
    c.save(fig, ax, xlabel="US$ per GPU per year", legend=False)


# --------------------------------------------------------------------------------------
# 6. How far ROCm trails CUDA, milestone by milestone
# --------------------------------------------------------------------------------------
@register
def rocm_lag_behind_cuda():
    df = load(LAG)
    d = df.copy()
    first, mid, last = d.iloc[0], d.iloc[1], d.iloc[2]
    c = Chart(
        id="09-rocm-lag-behind-cuda",
        title=(f"ROCm's lag behind CUDA fell from ~{first.lag_days/365:.0f} years to ~{mid.lag_days/30.4:.0f} months "
               f"to {last.lag_days} days"),
        subtitle="Days between a CUDA milestone and the matching ROCm milestone, three successive eras",
        alt=(f"Horizontal log-scale bar chart of how far AMD ROCm trailed NVIDIA CUDA: platform 1.0 came {first.lag_days:,} "
             f"days (about {first.lag_days/365:.1f} years) later (June 2007 vs April 2016); FP4 support came {mid.lag_days} "
             f"days (about {mid.lag_days/30.4:.0f} months) later (CUDA 12.8 in January 2025 vs ROCm 7.0 in September 2025); "
             f"usable serving of DeepSeek-V4-Pro came {last.lag_days} days after CUDA's day-0 recipes (April to May 2026). "
             "Each gap is roughly ten times shorter than the last, but a gap still recurs with every new model."),
        data=[LAG], chapters=["09", "15", "17"],
        source="CUDA/ROCm release histories; SemiAnalysis InferenceX", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10.5, height=4.6)
    y = np.arange(len(d))[::-1]
    amd = entity_color("AMD")
    bars = ax.barh(y, d.lag_days, color=[amd, amd, amd], alpha=0.9, height=0.55)
    for b, r in zip(bars, d.itertuples()):
        if r.lag_days >= 365:
            lab = f"{r.lag_days:,} days (~{r.lag_days/365:.1f} years)"
        elif r.lag_days >= 60:
            lab = f"{r.lag_days} days (~{r.lag_days/30.4:.0f} months)"
        else:
            lab = f"{r.lag_days} days"
        ax.text(r.lag_days * 1.12, b.get_y() + b.get_height() / 2, lab, va="center", fontsize=9.5,
                color=INK["title"], fontweight="bold")
    labels = [f"{r.capability}\n{r.cuda_milestone} ({str(r.cuda_date)[:7]}) → {r.rocm_milestone} ({str(r.rocm_date)[:7]})"
              for r in d.itertuples()]
    ax.set_yticks(y, labels, fontsize=8.6)
    ax.set_xscale("log")
    ax.set_xlim(10, 30000)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"], lw=0.6)
    _margins(fig, left=0.43, right=0.97)
    c.save(fig, ax, xlabel="Days ROCm trailed CUDA", logx=True, legend=False, bottom=0.17)
