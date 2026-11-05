"""Chapter 17 (Roadmap 2025-2028): how far ahead each vendor dates its accelerators, and NVIDIA's
Data Center revenue through its roadmap reveals (the Osborne-effect test). Data:
data/x17_preannouncement_horizon.csv and data/financials.csv. Owner: chapter 17 author."""
from __future__ import annotations

from datetime import date

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from style import Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, load, register, sources_of


def _d(s: str) -> date:
    parts = [int(x) for x in str(s).split("-")]
    while len(parts) < 3:
        parts.append(15 if len(parts) == 2 else 7)
    return date(*parts)


# --------------------------------------------------------------------------------------
# 1. Pre-announcement horizon by vendor
# --------------------------------------------------------------------------------------
ORDER = ["NVIDIA", "Huawei", "AMD", "Qualcomm", "Meta", "AWS", "Microsoft", "Google"]


@register
def preannouncement_horizon():
    df = load("x17_preannouncement_horizon.csv")
    df["months"] = [(_d(b) - _d(a)).days / 30.44 for a, b in zip(df.first_dated_mention, df.availability_date)]
    df["vrank"] = df.vendor.map({v: i for i, v in enumerate(ORDER)})
    df = df.sort_values(["vrank", "months"], ascending=[True, False]).reset_index(drop=True)
    nv = df[(df.vendor == "NVIDIA") & df["product"].isin(["Rubin GPU", "Rubin Ultra", "Feynman"])]
    goog = df[df.vendor == "Google"]
    amd = df[df.vendor == "AMD"]
    c = Chart(
        id="17-preannouncement-horizon",
        # QA 2026-11-05: scoped to Rubin–Feynman (the plotted Blackwell Ultra bar is 14 months, outside "26–40")
        title=(f"NVIDIA dates Rubin–Feynman GPUs {nv.months.min():.0f}–{nv.months.max():.0f} months ahead; "
               f"Google dates TPUs ~{goog.months.mean():.0f} months ahead"),
        subtitle="Months from the first public, dated roadmap mention to (planned) volume availability, flagship accelerators announced 2024–2026",
        alt=(f"Horizontal bar chart of how far ahead vendors publicly date their accelerators. NVIDIA named Rubin and Rubin "
             f"Ultra at Computex 2024 and Feynman at GTC 2025, {nv.months.min():.0f} to {nv.months.max():.0f} months before "
             f"their planned volume availability; Huawei dated Ascend 970 about "
             f"{df[df['product'] == 'Ascend 970'].months.iloc[0]:.0f} months ahead; AMD dates Instinct parts "
             f"{amd.months.min():.0f}–{amd.months.max():.0f} months ahead on its annual cadence; AWS, Meta, Microsoft and "
             f"Qualcomm sit between about 0 and 25 months; Google announces each TPU only about {goog.months.mean():.0f} "
             f"months before general availability. Future availability dates are plans; year-only plans use mid-year."),
        data=["x17_preannouncement_horizon.csv"],
        chapters=["17", "15", "02"],
        source="vendor keynotes, press releases and trade press",
        source_ids=sources_of(df),
        note="Hatched = not yet shipping in volume (plan, or shipments unconfirmed); year-only plans placed at mid-year",
    )
    fig = plt.figure(figsize=(11, 7.4))
    ax = fig.add_axes([0.24, 0.12, 0.72, 0.72])
    ax.set_axisbelow(True)
    n = len(df)
    today = date(2026, 11, 5)
    for i, r in enumerate(df.itertuples()):
        y = n - 1 - i
        col = entity_color(r.vendor)
        future = r.status != "shipping" or _d(r.availability_date) > today
        bar = ax.barh(y, r.months, color=col, edgecolor=col, height=0.66, alpha=0.75 if future else 1.0)
        if future:
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_edgecolor("#FFFFFF")
        ax.annotate(f"{max(r.months, 0):.0f}", (max(r.months, 0), y), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=8.3, color=INK["title"])
    ax.set_yticks(range(n))
    ax.set_yticklabels([f"{v} · {p}" for v, p in zip(df.vendor, df["product"])][::-1], fontsize=8.4)
    for lab in ax.get_yticklabels():
        if lab.get_text().startswith("NVIDIA"):
            lab.set_fontweight("bold")
            lab.set_color(NV_DARK)
    ax.set_xlim(0, 46)
    ax.grid(axis="x", color=INK["grid"], linewidth=0.7)
    ax.grid(axis="y", visible=False)
    ax.axvline(12, color=INK["text"], lw=0.9, ls=":")
    ax.text(12.3, n - 0.3, "one annual cycle", fontsize=8, color=INK["text"], va="bottom")
    c.save(fig, ax, xlabel="Months from first dated public mention to volume availability", legend=False)


# --------------------------------------------------------------------------------------
# 2. Data Center revenue through the roadmap reveals (Osborne test)
# --------------------------------------------------------------------------------------
EVENTS = [  # (date, short label, source id)
    ("2024-03-18", "GTC 2024: Blackwell revealed", "S396"),
    ("2024-06-02", "Computex 2024: one-year rhythm,\nRubin and Rubin Ultra named", "S17003"),
    ("2025-03-18", "GTC 2025: Rubin Ultra and Feynman\ndated; 'chief revenue destroyer'", "S17001"),
    ("2026-01-05", "CES 2026: Rubin in\nfull production", "S33004"),
    ("2026-03-16", "GTC 2026: Kyber,\nFeynman, Groq LPX", "S109"),
    ("2026-08-01", "Rubin production\nshipments begin", "S500"),
]


@register
def dc_revenue_through_transitions():
    fin = load("financials.csv")
    q = fin[(fin.period_type == "Q") & (fin.metric == "revenue_data_center")].copy()
    q["end"] = q.period_end.map(date.fromisoformat)
    q = q.sort_values("end").reset_index(drop=True)
    q["growth"] = q.value.astype(float).pct_change() * 100
    shown = q[q.end >= date(2023, 4, 1)].reset_index(drop=True)
    streak = 0
    for g in shown.growth[::-1]:
        if g > 0:
            streak += 1
        else:
            break
    low = shown.loc[shown.growth.idxmin()]
    c = Chart(
        id="17-dc-revenue-through-transitions",
        title=(f"Data Center revenue grew {streak} quarters in a row through six roadmap reveals: "
               f"no Osborne dip so far"),
        subtitle="NVIDIA Data Center revenue by fiscal quarter, US$ B, with q/q growth; lines mark roadmap announcements and the Rubin ramp",
        alt=(f"Bar chart of NVIDIA quarterly Data Center revenue from {shown.period.iloc[0]} "
             f"(${float(shown.value.iloc[0]):.1f}B) to {shown.period.iloc[-1]} (${float(shown.value.iloc[-1]):.1f}B). "
             f"Revenue rose quarter on quarter {streak} times in a row while NVIDIA revealed Blackwell (GTC 2024), moved to a "
             f"one-year rhythm and named Rubin (Computex 2024), dated Rubin Ultra and Feynman (GTC 2025), put Rubin in full "
             f"production (CES 2026), showed Kyber and Feynman details (GTC 2026) and began Rubin shipments (August 2026). "
             f"The weakest quarter, {low.period} at +{low.growth:.0f}%, coincided with the H20 export ban rather than a "
             f"buyer pause; customers did not stop buying the current generation to wait for the announced one."),
        data=["financials.csv"],
        chapters=["17", "18", "13"],
        source="NVIDIA quarterly results; roadmap dates from keynotes",
        source_ids=sources_of(shown) + [e[2] for e in EVENTS],
    )
    fig, ax = c.figure(11, 6.0)
    ax.set_axisbelow(True)
    xs = list(range(len(shown)))
    cols = [NV if p.endswith("FY27") else GEN_PAST for p in shown.period]
    ax.bar(xs, shown.value.astype(float), color=cols, edgecolor=NV_DARK, linewidth=0.5, width=0.7, zorder=3)
    for x, v, g in zip(xs, shown.value.astype(float), shown.growth):
        ax.annotate(f"{v:.0f}", (x, v), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.2, color=INK["title"], fontweight="bold")
        ax.annotate(f"+{g:.0f}%", (x, 0), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=7.4, color="#FFFFFF" if v > 8 else INK["text"], zorder=4)
    # map event dates to x positions (quarter i spans (end[i-1], end[i]])
    ends = list(shown.end)
    starts = [q.end[q.index[q.end == ends[0]][0] - 1]] + ends[:-1]

    def xpos(d: date) -> float:
        for i, (a, b) in enumerate(zip(starts, ends)):
            if a < d <= b:
                return i - 0.5 + (d - a).days / (b - a).days
        return len(ends) - 0.5 + (d - ends[-1]).days / 91

    ymax = float(shown.value.max()) * 1.55
    heights = [0.62, 0.80, 0.96, 0.62, 0.80, 0.96]
    for (ds, lab, _), h in zip(EVENTS, heights):
        x = xpos(date.fromisoformat(ds))
        ax.axvline(x, color=INK["text"], lw=0.9, ls="--", zorder=1)
        ax.text(x - 0.08, ymax * h, lab, ha="right", va="top", fontsize=7.6, color=INK["title"], linespacing=1.1)
    ax.set_ylim(0, ymax)
    ax.set_xlim(-0.6, len(xs) - 0.4)
    ax.set_xticks(xs)
    ax.set_xticklabels([p.replace("FY", "\nFY") for p in shown.period], fontsize=8.2)
    c.save(fig, ax, ylabel="Data Center revenue, US$ B", legend=False)
