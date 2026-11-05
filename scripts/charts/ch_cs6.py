"""Case study CS6 - China export controls: H20 and beyond.

Charts built from data/cs6_china_revenue.csv, data/cs6_china_parts.csv and data/cs6_scenarios.csv.

TPP (total processing performance, the US control metric) is computed in the CSV as
dense TFLOPS (or TOPS) x bit width of the operation, which equals 2 x MAC rate x bit width.
The scenario chart computes gross profit = revenue x (gross margin - revenue levy); a ban with the
capacity resold elsewhere keeps the base-case gross profit (supply-constrained case).
"""
from __future__ import annotations

import numpy as np

from style import INK, NV, GEN_PAST, entity_color, load, register, sources_of, Chart

CH = ["CS6", "13", "18"]


@register
def cs6_china_revenue_share():
    df = load("cs6_china_revenue.csv")
    fy = df[df.period_type == "FY"].copy()
    q = df[df.period_type == "Q"].copy()
    bill = fy[fy.basis == "billing"].sort_values("period_end")
    hq = fy[fy.basis == "headquarters"].sort_values("period_end")
    c = Chart(
        id="CS6-china-revenue-share",
        title="China fell from ~26% of NVIDIA revenue (FY2022) to ~9% (FY2026) and 6–8% in FY2027",
        subtitle="China incl. Hong Kong as % of total revenue; left: fiscal years (two reporting bases); "
                 "right: quarters, customer-HQ basis (hatched = secondary reading of the 10-Q)",
        alt=("Two-panel chart of China's share of NVIDIA revenue. Left, by fiscal year on the old billing "
             "basis: 23.9% FY2019, 25.0% FY2020, 23.3% FY2021, 26.4% FY2022, 21.4% FY2023, 16.9% FY2024, "
             "13.1% FY2025; on the new customer-headquarters basis: 20.2% FY2024, 19.2% FY2025 ($25.0B, the "
             "dollar peak) and 9.1% FY2026 ($19.7B). Right, by quarter on the headquarters basis: 21.9% in "
             "Q1 FY2026, 8.6% in Q2 FY2026 after the H20 licence requirement, 5.6% in Q1 FY2027 and 8.2% in "
             "Q2 FY2027 (all platforms, including gaming)."),
        data=["cs6_china_revenue.csv"],
        chapters=CH,
        source="NVIDIA 10-K and 10-Q geographic revenue notes",
        source_ids=sources_of(df),
    )
    fig, axes = c.figure_grid(1, 2, width=11.5, height=6.0, gridspec_kw={"width_ratios": [2.3, 1]})
    ax, axq = axes
    xs_all = ["FY2019", "FY2020", "FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]
    pos = {p: i for i, p in enumerate(xs_all)}
    ax.plot([pos[p] for p in bill.period], bill.china_share_pct, color=GEN_PAST, marker="o",
            label="Billing-location basis (old 10-Ks)")
    ax.plot([pos[p] for p in hq.period], hq.china_share_pct, color=NV, marker="s",
            label="Customer-HQ basis (FY2026 10-K recast)")
    for _, r in bill.iterrows():
        ax.annotate(f"{r.china_share_pct:.0f}%", (pos[r.period], r.china_share_pct), xytext=(0, -15),
                    textcoords="offset points", ha="center", fontsize=8.5, color=INK["text"])
    for _, r in hq.iterrows():
        last = r.period == "FY2026"
        ax.annotate(f"{r.china_share_pct:.0f}%\n${r.china_revenue_usd_b:.1f}B", (pos[r.period], r.china_share_pct),
                    xytext=(-12, -4) if last else (0, 8), textcoords="offset points",
                    ha="right" if last else "center", va="top" if last else "bottom", fontsize=8.5, color=NV,
                    fontweight="bold")
    events = [(3.6, "Oct 2022 rule"), (4.75, "Oct 2023 rule"), (6.35, "Apr 2025 H20 licence")]
    for x, lab in events:
        ax.axvline(x, color=INK["base"], lw=1, ls="--")
        ax.text(x + 0.05, 33.5, lab, fontsize=8.3, color=INK["text"], rotation=0, va="top")
    ax.set_xticks(range(len(xs_all)))
    ax.set_xticklabels(xs_all, fontsize=9)
    ax.set_ylim(0, 35)
    ax.set_ylabel("China share of NVIDIA revenue (%)")
    ax.legend(loc="lower left", fontsize=8.5)
    qq = q.sort_values("period_end")
    labels = ["Q1 FY26", "Q2 FY26", "Q1 FY27", "Q2 FY27"]
    bars = axq.bar(range(len(qq)), qq.china_share_pct, color=NV, width=0.62)
    for b, (_, r) in zip(bars, qq.iterrows()):
        if r.confidence != "confirmed":
            b.set_hatch("///")
            b.set_alpha(0.8)
        axq.annotate(f"{r.china_share_pct:.1f}%\n${r.china_revenue_usd_b:.2f}B",
                     (b.get_x() + b.get_width() / 2, b.get_height()), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8.3, color=INK["text"])
    axq.set_xticks(range(len(qq)))
    axq.set_xticklabels(labels, fontsize=8.8)
    axq.set_ylim(0, 35)
    axq.set_title("Quarterly (HQ basis)", fontsize=10, color=INK["text"], loc="left")
    axq.tick_params(length=0)
    c.save(fig, ax, xlabel="NVIDIA fiscal year (ends late January)", legend=False, top=0.82, bottom=0.14)


@register
def cs6_china_parts_tpp():
    df = load("cs6_china_parts.csv")
    d = df.iloc[::-1].reset_index(drop=True)
    c = Chart(
        id="CS6-china-parts-tpp",
        title="H20 was cut to ~2,400 TPP, half the 4,800 licence line and 1/7 of H200, but kept 4 TB/s HBM",
        subtitle="TPP (dense TFLOPS × bit width) per package; label = TPP · HBM bandwidth · China status; "
                 "hatched = reported/leaked",
        alt=("Horizontal bar chart of TPP, the US export-control metric, per accelerator with a dashed line at "
             "the 4,800 licence threshold. NVIDIA B200 36,000; H200 15,832; H800 15,832 (NVLink cut to 400 GB/s); "
             "H100 15,832; A800 4,992 (NVLink 400 GB/s); A100 4,992; H20 2,368 with 96 GB and 4.0 TB/s of HBM; "
             "Huawei Ascend 910C about 12,800 on paper (FP16) and Ascend 950PR about 8,000 (FP8). The H20 sits "
             "far below the line on compute while keeping more memory bandwidth than an H100."),
        data=["cs6_china_parts.csv"],
        chapters=["CS6", "02", "15"],
        source="NVIDIA datasheets, SemiAnalysis (H20 leak), Huawei, BIS",
        source_ids=sources_of(df),
    )
    fig, ax0 = c.figure(width=11, height=6.4)
    ax0.remove()
    ax = fig.add_axes([0.12, 0.12, 0.85, 0.71])  # fixed axes: room for product labels
    colors = []
    for _, r in d.iterrows():
        if r.vendor == "Huawei":
            colors.append(entity_color("Huawei"))
        elif r["product"] in ("H20", "H200"):
            colors.append(NV)
        else:
            colors.append(GEN_PAST)
    bars = ax.barh(range(len(d)), d.tpp, color=colors, height=0.62)
    for b, (_, r) in zip(bars, d.iterrows()):
        if r.confidence != "confirmed":
            b.set_hatch("///")
        ax.annotate(f"{r.tpp:,.0f}  ·  {r.memory_bw_tbs:g} TB/s  ·  {r.status_short}",
                    (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=8.5, color=INK["text"],
                    bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels([p.replace(" SXM", "").replace(" (HGX)", "") for p in d["product"]], fontsize=9)
    ax.axvline(4800, color="#C4314B", ls="--", lw=1.4)
    ax.text(4900, len(d) - 0.4, "TPP 4,800: licence line (2022 and 2023 rules)", color="#C4314B", fontsize=8.6,
            va="center")
    ax.set_xlim(0, 56000)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    c.save(fig, ax, xlabel="TPP (dense TFLOPS × bits)", legend=False, top=0.85, bottom=0.12)


@register
def cs6_levy_vs_ban():
    df = load("cs6_scenarios.csv").sort_values("order")
    gp = df.china_revenue_usd_b * (df.gross_margin_pct - df.levy_pct) / 100.0
    base = gp.iloc[0]
    c = Chart(
        id="CS6-levy-vs-ban-gross-profit",
        title="Est.: the 25% levy costs ~$4.4B/yr of gross profit on $17.5B of sales; a ban up to ~$13B",
        subtitle="Gross profit per year from a ~$17.5B China data-center market at 75% gross margin, by regime "
                 "($B; hatched = depends on resale)",
        alt=("Horizontal bar chart of repo estimates of NVIDIA's annual gross profit from a $17.5B China "
             "data-center market at a 75% gross margin: unrestricted sales $13.1B; an H20-style 15% revenue "
             "share $10.5B; the H200 deal with 25% of revenue to the US government $8.75B; a ban where the "
             "capacity is resold to other buyers about $13.1B (no short-run loss when supply is constrained); "
             "and a ban with idle capacity $0. The levy falls one-for-one on gross profit."),
        data=["cs6_scenarios.csv"],
        chapters=["CS6", "13", "18"],
        source="repo scenarios on NVIDIA filings and policy terms",
        source_ids=sources_of(df),
        kind="data",
    )
    fig, ax0 = c.figure(width=11, height=5.6)
    ax0.remove()
    ax = fig.add_axes([0.27, 0.13, 0.70, 0.70])  # fixed axes: room for scenario labels
    d = df.iloc[::-1].reset_index(drop=True)
    g = gp.iloc[::-1].reset_index(drop=True)
    colors = [NV if r.levy_pct == 0 and r.china_revenue_usd_b > 0 else (GEN_PAST if r.levy_pct > 0 else INK["base"])
              for _, r in d.iterrows()]
    bars = ax.barh(range(len(d)), g, color=colors, height=0.6)
    for b, (_, r), v in zip(bars, d.iterrows(), g):
        if r.capacity_resold == "yes":
            b.set_hatch("///")
        loss = base - v
        txt = f"${v:.2f}B" + (f"  (−${loss:.2f}B vs unrestricted)" if loss > 0.01 else "")
        ax.annotate(txt, (max(v, 0), b.get_y() + b.get_height() / 2), xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK["text"])
    ax.set_yticks(range(len(d)))
    ax.set_yticklabels(d.scenario, fontsize=9.2)
    ax.set_xlim(0, 20)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    c.save(fig, ax, xlabel="Gross profit per year ($B)", legend=False, top=0.84, bottom=0.13)
