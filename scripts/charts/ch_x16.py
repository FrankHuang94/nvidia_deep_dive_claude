"""Chapter 16 (How NVIDIA built it): long-run revenue by era, era scorecard, years to revenue
milestones and the bet-to-payoff ledger. Data: data/x16_long_run_financials.csv (FY1999-FY2015),
data/cs2_cuda_trough.csv (FY2007-FY2015 margin and R&D), data/financials.csv (FY2016+),
data/x16_key_bets.csv. Owner: chapter 16 author."""
from __future__ import annotations

from datetime import date

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from style import Chart, GEN_PAST, INK, NV, NV_DARK, load, register, sources_of

FOUNDED = date(1993, 4, 5)
ERAS = [  # (label, first FY, last FY)
    ("1 · Survive and\nmake the GPU", 1999, 2006),
    ("2 · CUDA and the\nmobile detour", 2007, 2016),
    ("3 · Deep learning and\nthe data center", 2017, 2023),
    ("4 · AI factories", 2024, 2026),
]
ERA_SHADE = ["#F4F3EF", "#FFFFFF", "#F4F3EF", "#FFFFFF"]


def _fy(p: str) -> int:
    return int(str(p).replace("FY", ""))


def _series(metric: str) -> dict[int, float]:
    """FY -> value, merging the chapter's long-run file, the CS2 file and financials.csv
    (financials.csv wins where they overlap, then CS2, then the long-run file)."""
    out: dict[int, float] = {}
    for name in ("x16_long_run_financials.csv", "cs2_cuda_trough.csv", "financials.csv"):
        df = load(name)
        sub = df[(df.period_type == "FY") & (df.metric == metric)]
        for _, r in sub.iterrows():
            out[_fy(r.period)] = float(r.value)
    return dict(sorted(out.items()))


def _ids(*names, metrics=None) -> list[str]:
    ids: list[str] = []
    for n in names:
        df = load(n)
        if metrics and "metric" in df.columns:
            df = df[df.metric.isin(metrics)]
        for s in sources_of(df):
            if s not in ids:
                ids.append(s)
    return ids


# --------------------------------------------------------------------------------------
# 1. Revenue by era, log scale, with the bets annotated
# --------------------------------------------------------------------------------------
EVENTS = {  # FY -> label (calendar events mapped to NVIDIA's fiscal year)
    1999: "IPO (Jan 1999)",
    2000: "GeForce 256",
    2002: "Xbox ships · 3dfx assets",
    2008: "CUDA 1.0",
    2009: "margin trough",
    2013: "AlexNet",
    2015: "cuDNN",
    2017: "DGX-1",
    2018: "V100 tensor cores",
    2021: "Mellanox closes",
    2023: "Arm deal ends",
    2024: "ChatGPT boom · H100",
    2026: "Blackwell · $5T cap",
}


@register
def revenue_by_era_log():
    rev = _series("revenue_total")
    first, last = min(rev), max(rev)
    growth_share = (rev[last] - rev[2023]) / (rev[last] - rev[first])
    mult = rev[last] / rev[first]
    c = Chart(
        id="16-revenue-by-era-log",
        title=(f"Revenue rose ~{mult:,.0f}× since FY{first}, but {growth_share:.0%} of the dollar gain "
               f"came in the last three years"),
        subtitle="NVIDIA total revenue by fiscal year, US$ B (log scale), FY1999–FY2026, shaded by era; labels mark the key bets",
        alt=(f"Log-scale bar chart of NVIDIA annual revenue from FY{first} (${rev[first]*1000:.0f}M, the IPO year) to "
             f"FY{last} (${rev[last]:.0f}B), about {mult:,.0f} times higher, in four shaded eras: survive and make the GPU "
             f"(FY1999–FY2006, to ${rev[2006]:.1f}B), CUDA and the mobile detour (FY2007–FY2016, revenue stuck at "
             f"$3.3–5.0B), deep learning and the data center (FY2017–FY2023, to ${rev[2023]:.0f}B) and AI factories "
             f"(FY2024–FY2026). Labels mark the IPO, GeForce 256, Xbox, CUDA 1.0, AlexNet, cuDNN, DGX-1, tensor cores, "
             f"Mellanox, the Arm termination, ChatGPT and Blackwell; {growth_share:.0%} of all dollar growth came after FY2023."),
        data=["x16_long_run_financials.csv", "financials.csv"],
        chapters=["16", "00", "13"],
        source="NVIDIA 10-K/10-K405 filings and FY2026 results",
        source_ids=_ids("x16_long_run_financials.csv", metrics=["revenue_total"]) + ["S400", "S2", "S1"],
    )
    fig, ax = c.figure(11, 6.2)
    yrs = list(rev)
    for (label, a, b), shade in zip(ERAS, ERA_SHADE):
        ax.axvspan(a - 0.5, b + 0.5, color=shade, zorder=0)
        ax.text((a + b) / 2, 5200, label, ha="center", va="top", fontsize=8.6, color=INK["text"],
                fontweight="bold", linespacing=1.1)
    colors = [NV if y >= 2024 else GEN_PAST for y in yrs]
    ax.bar(yrs, [rev[y] for y in yrs], color=colors, edgecolor=NV_DARK, linewidth=0.5, width=0.75, zorder=2)
    ax.set_yscale("log")
    ax.set_ylim(0.1, 6500)
    for y, lab in EVENTS.items():
        if y in rev:
            ax.annotate(lab, (y, rev[y]), xytext=(0, 4), textcoords="offset points", rotation=90,
                        ha="center", va="bottom", fontsize=7.6, color=INK["title"])
    for y in (1999, 2002, 2016, 2023, 2026):
        v = rev[y]
        txt = f"${v*1000:.0f}M" if v < 1 else f"${v:,.1f}B" if v < 10 else f"${v:,.0f}B"
        ax.annotate(txt, (y, v), xytext=(0, -2), textcoords="offset points", ha="center", va="top",
                    fontsize=7.2, color="#FFFFFF" if y >= 2024 else NV_DARK, fontweight="bold")
    ax.set_xlim(1998.4, 2026.6)
    ax.set_xticks([1999, 2002, 2005, 2008, 2011, 2014, 2017, 2020, 2023, 2026])
    ax.set_xticklabels([f"FY{y}" for y in ax.get_xticks()])
    c.save(fig, ax, ylabel="Revenue, US$ B", logy=True, legend=False, top=0.86)


# --------------------------------------------------------------------------------------
# 2. Era scorecard: growth, gross margin, R&D intensity
# --------------------------------------------------------------------------------------
@register
def era_scorecard():
    rev = _series("revenue_total")
    gm = _series("gross_margin_gaap_pct")
    rd = _series("rd_expense")
    cagr, gm_avg, rd_avg, gm_n = [], [], [], []
    for i, (_, a, b) in enumerate(ERAS):
        base = a if i == 0 else ERAS[i - 1][2]
        n = b - base
        cagr.append(((rev[b] / rev[base]) ** (1 / n) - 1) * 100)
        g = [gm[y] for y in range(a, b + 1) if y in gm]
        gm_avg.append(sum(g) / len(g))
        gm_n.append(len(g))
        r = [rd[y] / rev[y] * 100 for y in range(a, b + 1) if y in rd and y in rev]
        rd_avg.append(sum(r) / len(r) if r else None)
    c = Chart(
        id="16-era-scorecard",
        title=(f"Each era raised the margin floor: average gross margin went "
               f"{gm_avg[0]:.0f}% → {gm_avg[1]:.0f}% → {gm_avg[2]:.0f}% → {gm_avg[3]:.0f}%"),
        subtitle="NVIDIA by era: revenue CAGR (from the prior era's last year), average GAAP gross margin and average R&D as % of revenue",
        alt=(f"Three-panel bar chart of NVIDIA's four eras. Revenue growth per year: {cagr[0]:.0f}% (FY1999–FY2006), "
             f"{cagr[1]:.0f}% (FY2006–FY2016), {cagr[2]:.0f}% (FY2016–FY2023) and {cagr[3]:.0f}% (FY2023–FY2026). "
             f"Average GAAP gross margin: {gm_avg[0]:.0f}% (FY2001–FY2003 only), {gm_avg[1]:.0f}%, {gm_avg[2]:.0f}% and "
             f"{gm_avg[3]:.0f}%. Average R&D intensity: not in repo data for era 1, {rd_avg[1]:.0f}% in the CUDA era, "
             f"{rd_avg[2]:.0f}% in the deep-learning era and {rd_avg[3]:.0f}% in the AI-factory era: the CUDA era was the "
             f"slow-growth, high-R&D investment phase that the later eras harvested."),
        data=["x16_long_run_financials.csv", "cs2_cuda_trough.csv", "financials.csv"],
        chapters=["16", "13"],
        source="NVIDIA 10-K filings; repo era arithmetic",
        source_ids=["S16015", "S16006", "S16008", "S22000", "S22001", "S22003", "S22004", "S400", "S2", "S1", "S401", "S16016"],
    )
    fig, axes = c.figure_grid(1, 3, 11, 5.6)
    names = ["Era 1\nFY99–06", "Era 2\nFY07–16", "Era 3\nFY17–23", "Era 4\nFY24–26"]
    cols = [GEN_PAST, GEN_PAST, GEN_PAST, NV]
    panels = [("Revenue CAGR, % per year", cagr, "{:.0f}%"),
              ("Avg GAAP gross margin, %", gm_avg, "{:.0f}%"),
              ("Avg R&D, % of revenue", rd_avg, "{:.0f}%")]
    for ax, (lab, vals, fmt) in zip(axes, panels):
        ax.set_axisbelow(True)
        xs = list(range(4))
        hv = [v if v is not None else 0 for v in vals]
        bars = ax.bar(xs, hv, color=cols, edgecolor=NV_DARK, linewidth=0.6, width=0.65)
        for x, v, b in zip(xs, vals, bars):
            if v is None:
                ax.text(x, 1, "n/a\n(not in\nrepo data)", ha="center", va="bottom", fontsize=7.8, color=INK["muted"])
                b.set_visible(False)
            else:
                ax.annotate(fmt.format(v), (x, v), xytext=(0, 2), textcoords="offset points", ha="center",
                            va="bottom", fontsize=9, color=INK["title"], fontweight="bold")
        ax.set_xticks(xs)
        ax.set_xticklabels(names, fontsize=8.5)
        ax.set_title(lab, fontsize=10, color=INK["text"], loc="left")
        ax.set_ylim(0, max(hv) * 1.2)
    axes[1].annotate("FY2001–03\nonly", (0, gm_avg[0]), xytext=(0, 16), textcoords="offset points",
                     ha="center", va="bottom", fontsize=7.4, color=INK["muted"])
    c.save(fig, list(axes), ylabel="Percent", legend=False, top=0.78)


# --------------------------------------------------------------------------------------
# 3. Years to revenue milestones
# --------------------------------------------------------------------------------------
@register
def years_to_milestones():
    rev = _series("revenue_total")
    ends = {}
    for name in ("x16_long_run_financials.csv", "financials.csv"):
        df = load(name)
        sub = df[(df.period_type == "FY") & (df.metric == "revenue_total")]
        for _, r in sub.iterrows():
            ends[_fy(r.period)] = date.fromisoformat(str(r.period_end))
    marks = []
    for thr, lab in ((1, "$1B"), (10, "$10B"), (100, "$100B"), (200, "$200B")):
        fy = min(y for y, v in rev.items() if v >= thr)
        yrs = (ends[fy] - FOUNDED).days / 365.25
        marks.append((lab, fy, yrs))
    gaps = [marks[0][2]] + [marks[i][2] - marks[i - 1][2] for i in range(1, len(marks))]
    c = Chart(
        id="16-years-to-revenue-milestones",
        title=(f"NVIDIA took {gaps[0]:.0f} years to reach $1B of revenue, {gaps[1]:.0f} more to reach $10B, "
               f"then {gaps[2]:.0f} to pass $100B"),
        subtitle="Years from founding (April 1993) to the end of the first fiscal year above each annual-revenue threshold",
        alt=(f"Horizontal bar chart of the time between revenue milestones. From founding in April 1993 NVIDIA needed "
             f"{gaps[0]:.1f} years to its first $1B fiscal year (FY{marks[0][1]}), {gaps[1]:.1f} more years to pass $10B "
             f"(FY{marks[1][1]}), {gaps[2]:.1f} years to pass $100B (FY{marks[2][1]}) and {gaps[3]:.1f} year to pass "
             f"$200B (FY{marks[3][1]}). The long middle stretch covers the CUDA and mobile years."),
        data=["x16_long_run_financials.csv", "financials.csv"],
        chapters=["16"],
        source="NVIDIA 10-K filings and FY2026 results; repo arithmetic",
        source_ids=["S16006", "S400", "S2", "S1", "S16002", "S16003"],
    )
    fig = plt.figure(figsize=(10, 4.6))
    ax = fig.add_axes([0.17, 0.17, 0.79, 0.64])
    ax.set_axisbelow(True)
    labels = ["Founding → $1B", "$1B → $10B", "$10B → $100B", "$100B → $200B"]
    cols = [GEN_PAST, GEN_PAST, NV, NV]
    ys = list(range(len(gaps)))[::-1]
    ax.barh(ys, gaps, color=cols, edgecolor=NV_DARK, linewidth=0.6, height=0.6)
    for y, g, (lab, fy, yrs) in zip(ys, gaps, marks):
        ax.annotate(f"{g:.1f} year{'' if round(g, 1) == 1 else 's'} · first hit in FY{fy} (year {yrs:.0f})", (g, y),
                    xytext=(5, 0), textcoords="offset points", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(ys)
    ax.set_yticklabels(labels)
    ax.set_xlim(0, 30)
    ax.grid(axis="x", color=INK["grid"], linewidth=0.7)
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel="Years", legend=False)


# --------------------------------------------------------------------------------------
# 4. Bet ledger: time from bet to payoff (or exit)
# --------------------------------------------------------------------------------------
OUT_STYLE = {
    "won": dict(fc=NV, ec=NV_DARK, hatch=None, label="Paid off"),
    "mixed": dict(fc="#FBE6A2", ec="#9A7A00", hatch=None, label="Mixed (revenue at lower margin)"),
    "lost": dict(fc="#C3C2B7", ec="#52514E", hatch=None, label="Failed or abandoned"),
    "pending": dict(fc=GEN_PAST, ec=NV_DARK, hatch="///", label="Pending (2025–26 bets)"),
}


def _yf(s: str) -> float:
    y, m = str(s).split("-")[:2]
    return int(y) + (int(m) - 1) / 12


@register
def bet_lag_to_payoff():
    df = load("x16_key_bets.csv")
    df["s"] = df.start_date.map(_yf)
    df["e"] = df.payoff_date.map(_yf)
    df["lag"] = df.e - df.s
    won = df[df.outcome == "won"]
    lost = df[df.outcome == "lost"]
    c = Chart(
        id="16-bet-lag-to-payoff",
        title=(f"NVIDIA's winning bets took {won.lag.min():.0f}–{won.lag.max():.0f} years to pay off; "
               f"it cut its failed bets within {lost.lag.max():.0f}"),
        subtitle="Years from each key bet to its payoff milestone (or to the exit), 1995–2027; milestones defined in data/x16_key_bets.csv",
        alt=("Gantt-style bar chart of twelve NVIDIA bets. Paid off: GeForce 256 to the first $1B year in "
             f"{won[won.bet.str.startswith('GeForce')].lag.iloc[0]:.1f} years, CUDA to Data Center revenue exceeding R&D in "
             f"{won[won.bet.str.startswith('CUDA')].lag.iloc[0]:.1f} years, DGX-1 to the NVL72 rack in "
             f"{won[won.bet.str.startswith('DGX')].lag.iloc[0]:.1f}, tensor cores to the Hopper surge in "
             f"{won[won.bet.str.startswith('Tensor')].lag.iloc[0]:.1f}, Mellanox to payback in "
             f"{won[won.bet.str.startswith('Mellanox')].lag.iloc[0]:.1f} and Grace to GB200 in "
             f"{won[won.bet.str.startswith('Grace')].lag.iloc[0]:.1f}. Failed: NV1's quadratic surfaces (about 2 years to "
             f"the RIVA 128 pivot), Tegra phones and Icera modems (4 years) and the $40B Arm bid (1.4 years). Mixed: Xbox. "
             f"Pending: the ~$20B Groq licence and the $12.9B Hugging Face purchase."),
        data=["x16_key_bets.csv"],
        chapters=["16", "13", "CS2"],
        source="NVIDIA filings and press releases, trade press, repo case studies",
        source_ids=sources_of(df),
    )
    fig = plt.figure(figsize=(11, 6.4))
    ax = fig.add_axes([0.30, 0.15, 0.66, 0.68])
    ax.set_axisbelow(True)
    n = len(df)
    for i, r in enumerate(df.itertuples()):
        y = n - 1 - i
        st = OUT_STYLE[r.outcome]
        bar = ax.barh(y, r.e - r.s, left=r.s, height=0.6, color=st["fc"], edgecolor=st["ec"], linewidth=0.8)
        if st["hatch"]:
            bar.patches[0].set_hatch(st["hatch"])
        txt = f"{r.lag:.1f} yrs"
        if isinstance(r.cost_usd_b, float) and r.cost_usd_b == r.cost_usd_b and r.outcome != "mixed":
            txt += f" · ${r.cost_usd_b:g}B" + (" (Est.)" if r.confidence == "estimate" and "CUDA" in r.bet else "")
        ax.annotate(txt, (r.e, y), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.3,
                    color=INK["title"])
    ax.set_yticks(range(n))
    ax.set_yticklabels(list(df.bet)[::-1], fontsize=8.6)
    ax.set_xlim(1994, 2031)
    ax.set_xticks(range(1995, 2031, 5))
    ax.grid(axis="x", color=INK["grid"], linewidth=0.7)
    ax.grid(axis="y", visible=False)
    ax.axvline(2026 + 10 / 12, color=INK["text"], lw=1.0, ls="--")
    ax.text(2026 + 10 / 12, -0.75, " today", fontsize=8, color=INK["text"], va="center")
    handles = [mpatches.Patch(facecolor=s["fc"], edgecolor=s["ec"], hatch=s["hatch"], label=s["label"])
               for s in OUT_STYLE.values()]
    ax.legend(handles=handles, loc="upper right", fontsize=8.2, frameon=True, facecolor="#FFFFFF", edgecolor=INK["grid"])
    ax.set_xlabel("Calendar year (bar = bet → payoff milestone or exit; label = years, price where disclosed)")
    c.save(fig, ax, legend=False)
