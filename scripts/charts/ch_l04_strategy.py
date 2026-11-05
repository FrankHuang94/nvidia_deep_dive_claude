"""Layer 04 (CPU: Grace, Vera) strategy charts: market share, competitor heatmap, deals, roadmap, value chain.

Owner: layer-04 STRATEGY agent. Data: data/l04_cpu_market_share.csv, l04_cpu_verdicts.csv, l04_cpu_deals.csv,
l04_cpu_roadmap_specs.csv, l04_cpu_value_chain.csv (all documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from style import Chart, INK, NV, VERDICT_COLORS, entity_color, load, register, sources_of

SHARE = "l04_cpu_market_share.csv"
VERD = "l04_cpu_verdicts.csv"
DEALS = "l04_cpu_deals.csv"
ROAD = "l04_cpu_roadmap_specs.csv"
VALUE = "l04_cpu_value_chain.csv"

LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}
VERDICT_LABEL = {"leads": "L = rival leads NVIDIA", "parity": "P = parity", "behind": "B = rival behind",
                 "different": "D = different approach"}


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _vcolor(vendor: str) -> str:
    v = str(vendor)
    if v.startswith("NVIDIA"):
        return NV
    if v in ("SoftBank Group", "Ampere", "Arm", "Fujitsu"):
        return entity_color("other")
    if v == "Amazon":
        return entity_color("aws")
    return entity_color(v)


def _qdate(s: str) -> pd.Timestamp:
    return pd.Timestamp(s)


# --------------------------------------------------------------------------------------
# 1. Arm share of server CPUs: units vs revenue, by tracker
# --------------------------------------------------------------------------------------
@register
def arm_server_cpu_share_trackers():
    df = load(SHARE)
    arm = df[df.entity.eq("Arm") & df.metric.eq("unit_share")].copy()
    rev = df[df.metric.eq("revenue_share")].iloc[0]
    arm["t"] = arm.period_date.map(_qdate)
    m_last = arm[arm.tracker.eq("Mercury Research")].sort_values("t").iloc[-1]
    u_last = arm[arm.tracker.eq("UBS") & arm.basis.eq("actual")].sort_values("t").iloc[-1]
    c = Chart(
        id="04-arm-server-cpu-share-trackers",
        title=(f"Arm holds {m_last.value:.0f}–{u_last.value:.0f}% of server CPU units but ~{rev.value:.0f}% of server revenue"),
        subtitle="Arm share of server CPU shipments (%) by tracker, 2025–2030; dashed/hollow = forecast; diamond = share of server system revenue",
        alt=(f"Line chart of Arm's share of server CPU units: Mercury Research 12.5% (Q4 2025) and {m_last.value}% (Q1 2026); "
             f"UBS 11.5% (Q1 2025) and {u_last.value}% (Q1 2026) with a 40-45% forecast for 2030; TrendForce about 10% in 2025, "
             f"over 20% forecast for 2026 and about 30% for 2027. IDC puts non-x86 (mostly Arm) at {rev.value}% of Q1 2026 server "
             "revenue, inflated by NVIDIA Grace-based GPU racks where the CPU is a small part of the cost."),
        data=[SHARE], chapters=["04", "15"],
        source="Mercury Research, UBS, TrendForce, IDC as reported", source_ids=sources_of(df[df.entity.isin(["Arm", "Non-x86 (mostly Arm)"])]),
        note="Forecasts dashed",
    )
    fig, ax = c.figure(width=10.5, height=5.9)
    styles = {"Mercury Research": ("#256ABF", "o"), "UBS": ("#104281", "s"), "TrendForce": ("#86B6EF", "^")}
    for tr, (col, mk) in styles.items():
        d = arm[arm.tracker.eq(tr)].sort_values("t")
        act = d[d.basis.eq("actual")]
        fc = d[d.basis.eq("forecast")]
        ax.plot(act.t, act.value, color=col, marker=mk, markersize=8, lw=2, label=f"{tr} (units)")
        if not fc.empty:
            seg = pd.concat([act.tail(1), fc])
            ax.plot(seg.t, seg.value, color=col, lw=2, ls="--")
            ax.scatter(fc.t, fc.value, s=70, marker=mk, facecolor="white", edgecolor=col, linewidth=2, zorder=3)
        for r in d.itertuples():
            lab = f"{r.value:g}%"
            dy = -13 if (tr == "Mercury Research") else 9
            if tr == "TrendForce" and r.period == "2025":
                dy = -13
            ax.annotate(lab, (r.t, r.value), xytext=(0, dy), textcoords="offset points", ha="center",
                        fontsize=8.5, color=col if tr != "TrendForce" else "#256ABF")
    ax.scatter([_qdate(rev.period_date)], [rev.value], s=150, marker="D", color=INK["text"], zorder=4,
               label="IDC: non-x86 share of server revenue")
    ax.annotate(f"IDC Q1 2026: {rev.value}% of server revenue\n(non-x86, >95% Arm; GPU racks dominate)",
                (_qdate(rev.period_date), rev.value), xytext=(14, -4), textcoords="offset points", fontsize=8.8,
                color=INK["title"], va="center")
    ax.set_ylim(0, 60)
    ax.set_xlim(pd.Timestamp("2024-10-01"), pd.Timestamp("2030-12-31"))
    ax.legend(loc="upper left", ncol=2, fontsize=8.8)
    c.save(fig, ax, xlabel="Period (quarter or calendar year)", ylabel="Arm share (%)", legend=False)


# --------------------------------------------------------------------------------------
# 2. AMD share of x86 server CPUs: units vs revenue
# --------------------------------------------------------------------------------------
@register
def amd_x86_server_share_units_vs_revenue():
    df = load(SHARE)
    d = df[df.entity.eq("AMD") & df.metric.str.startswith("x86")].copy()
    quarters = ["2025-Q1", "2026-Q1", "2026-Q2"]
    units = d[d.metric.eq("x86_unit_share")].set_index("period").value.reindex(quarters)
    revn = d[d.metric.isin(["x86_revenue_share", "x86_normalized_share"])].set_index("period").value.reindex(quarters)
    c = Chart(
        id="04-amd-x86-server-share-units-vs-revenue",
        title=(f"AMD rose to {units.iloc[-1]:.1f}% of x86 server CPU units by Q2 2026, ~{revn.max():.0f}% by value"),
        subtitle="AMD share of x86 server CPUs (%), Mercury Research as reported; light bar = revenue or like-for-like value share",
        alt=(f"Grouped bar chart of AMD's share of x86 server CPUs per Mercury Research: units {units.iloc[0]}% in Q1 2025, "
             f"{units.iloc[1]}% in Q1 2026 and {units.iloc[2]}% in Q2 2026; by revenue {revn.iloc[1]}% in Q1 2026 and on a "
             f"normalised EPYC-versus-Xeon basis {revn.iloc[2]}% in Q2 2026 - x86 incumbency is now a two-vendor fight, "
             "with Intel still ahead on units."),
        data=[SHARE], chapters=["04", "15"], source="Mercury Research via press", source_ids=sources_of(d),
        note="Excludes Arm",
    )
    fig, ax = c.figure(width=10, height=5.4)
    x = np.arange(len(quarters))
    w = 0.36
    amd = entity_color("AMD")
    b1 = ax.bar(x - w / 2, units.values, w, color=amd, label="Unit share")
    b2 = ax.bar(x + w / 2, revn.fillna(0).values, w, color=amd, alpha=0.45, label="Revenue / like-for-like share")
    for b, v in zip(list(b1) + list(b2), list(units.values) + list(revn.values)):
        if pd.notna(v) and v > 0:
            ax.annotate(f"{v:.1f}%", (b.get_x() + b.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=9, color=INK["title"])
    ax.annotate("no revenue figure", (x[0] + w / 2, 1.5), ha="center", fontsize=8, color=INK["muted"], rotation=90,
                va="bottom")
    ax.axhline(50, color=INK["base"], lw=1, ls=":")
    ax.text(2.55, 50.8, "50%", fontsize=8.5, color=INK["muted"], ha="right")
    ax.set_xticks(x, ["Q1 2025", "Q1 2026", "Q2 2026\n(revenue bar = EPYC vs Xeon\nlike-for-like)"])
    ax.set_ylim(0, 60)
    ax.legend(loc="upper left")
    c.save(fig, ax, ylabel="AMD share of x86 server CPUs (%)", legend=False, bottom=0.17)


# --------------------------------------------------------------------------------------
# 3. Competitor capability heatmap (layer-specific)
# --------------------------------------------------------------------------------------
@register
def cpu_competitor_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    link = df[df.dimension.eq("CPU-GPU link & coherence")]
    n_link_lead = int(link.verdict_vs_nvidia.isin(["leads"]).sum())
    cores_lead = int(df[df.dimension.eq("Cores per socket")].verdict_vs_nvidia.eq("leads").sum())
    c = Chart(
        id="04-cpu-competitor-heatmap",
        title=(f"{cores_lead} of {len(comps)} rival CPUs out-core Vera, but none beats its coherent 1.8 TB/s GPU link"),
        subtitle="Repo verdict for each rival CPU vs NVIDIA Vera (Grace where noted) on five dimensions; cell = verdict letter + key number",
        alt=(f"Heatmap of {len(comps)} rival server CPUs against NVIDIA Vera on five dimensions. {cores_lead} rivals lead on cores "
             "per socket (EPYC Venice 256, Graviton5 192, Kunpeng 950 192), AMD alone leads on memory bandwidth (1.6 vs 1.2 TB/s), "
             f"{'none' if n_link_lead == 0 else n_link_lead} leads on CPU-GPU link and coherence (PCIe Gen5/Gen6 at 128-256 GB/s vs NVLink-C2C 1.8 TB/s), x86 vendors "
             "lead on software compatibility, and hyperscaler CPUs are a different approach because they are not sold."),
        data=[VERD], chapters=["04", "15"], source="repo analysis of vendor specs (l04_cpu_verdicts.csv)",
        source_ids=sources_of(df), note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=12, height=7.0)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {r.cell_label}", ha="center", va="center",
                    fontsize=8.6, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" & ", " &\n").replace(" / ", " /\n") for d in dims], fontsize=9)
    ax.xaxis.tick_top()
    prod = df.drop_duplicates("competitor").set_index("competitor").product_basis
    ax.set_yticks(np.arange(len(comps)) + 0.5)
    ax.set_yticklabels([f"{cmp}\n{prod[cmp]}" for cmp in comps], fontsize=8.6)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.17, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.08)


# --------------------------------------------------------------------------------------
# 4. What server-CPU teams and assets have cost
# --------------------------------------------------------------------------------------
@register
def cpu_deal_values():
    df = load(DEALS)
    d = df.copy()
    d["year"] = d.announce_date.str[:4]
    d["label"] = d.apply(lambda r: f"{r.target} ← {r.acquirer} ({r.year})", axis=1)
    d = d.sort_values("value_usd_m", na_position="first")
    arm = d[d.target.str.startswith("Arm")].value_usd_m.item()
    nxt = d[~d.target.str.startswith("Arm")].value_usd_m.max()
    nuvia = d[d.target.eq("NUVIA")].value_usd_m.item()
    ampere = d[d.target.eq("Ampere Computing")].value_usd_m.item()
    c = Chart(
        id="04-cpu-deal-values",
        title=(f"CPU teams sold for ${nuvia/1000:.1f}B–${ampere/1000:.1f}B; NVIDIA's failed Arm bid was ${arm/1000:.0f}B "
               f"({arm/nxt:.0f}× more)"),
        subtitle="Disclosed or reported deal value, US$ millions (log scale), server-CPU and CPU-adjacent transactions 2015–2025",
        alt=(f"Log-scale horizontal bar chart of CPU-related deals: NVIDIA's terminated ${arm:,.0f}M bid for Arm (2020), SoftBank's "
             f"${ampere:,.0f}M purchase of Ampere (2025), NVIDIA's $5,000M Intel stake (2025), Qualcomm's $2,400M Alphawave and "
             f"${nuvia:,.0f}M NUVIA deals, and Amazon's reported ~$370M Annapurna Labs purchase (2015) that seeded Graviton; Meta-Rivos "
             "and Qualcomm-Ventana (2025) were undisclosed."),
        data=[DEALS], chapters=["04", "13"], source="company releases and press", source_ids=sources_of(d),
        note="Hollow = terminated; hatched = reported",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = _vcolor(r.acquirer)
        if pd.isna(r.value_usd_m):
            ax.text(120, yi, "undisclosed", va="center", fontsize=8.8, color=INK["muted"], style="italic")
            continue
        failed = r.status == "terminated"
        bar = ax.barh(yi, r.value_usd_m, color="white" if failed else col, edgecolor=col, linewidth=2 if failed else 0,
                      height=0.62, left=0)
        if r.value_basis == "reported":
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_alpha(0.75)
        txt = f"${r.value_usd_m/1000:.1f}B" if r.value_usd_m >= 1000 else f"~${r.value_usd_m:,.0f}M"
        if failed:
            txt += " (terminated)"
        ax.text(r.value_usd_m * 1.12, yi, txt, va="center", fontsize=9, color=INK["title"])
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label)
    ax.set_ylim(-0.7, len(d) - 0.4)
    ax.set_xscale("log")
    ax.set_xlim(100, 200000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=entity_color("qualcomm"), label="Qualcomm"),
               Patch(color=entity_color("aws"), label="Amazon"), Patch(color=entity_color("other"), label="SoftBank"),
               Patch(color=entity_color("meta"), label="Meta")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _margins(fig, left=0.33, right=0.97)
    c.save(fig, ax, xlabel="Deal value, US$ millions (log scale)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 5–6. Roadmap spec progression: cores and memory bandwidth per socket
# --------------------------------------------------------------------------------------
LINE_GROUPS = [  # (vendor, filter on product, series label)
    ("NVIDIA", None, "NVIDIA Grace → Vera"),
    ("AMD", None, "AMD EPYC"),
    ("Intel", "P", "Intel Xeon P-core"),
    ("AWS", None, "AWS Graviton"),
    ("Microsoft", None, "Microsoft Cobalt"),
    ("Huawei", None, "Huawei Kunpeng"),
]


SHORT = {"EPYC 9004 Genoa": "Genoa", "EPYC 9005 Turin": "Turin", "EPYC Venice": "Venice",
         "Xeon 4th Gen Sapphire Rapids": "Xeon SPR", "Xeon 6 Granite Rapids-AP": "Xeon 6 GNR",
         "Xeon 6+ Clearwater Forest": "Xeon 6+ CWF (E-core)", "Xeon 7 Diamond Rapids": "Diamond Rapids (rep.)",
         "AmpereOne A192-32X": "AmpereOne", "Arm AGI CPU": "Arm AGI", "Axion (C4A)": "Axion",
         "Datacenter CPU (Oryon-based)": "Qualcomm (rep.)"}
JITTER = {"Arm AGI CPU": -0.14, "Axion (C4A)": 0.0}


def _short(product: str) -> str:
    return SHORT.get(product, product)


def _road() -> pd.DataFrame:
    d = load(ROAD)
    d["future"] = d.status.isin(["announced", "roadmap", "rumored"])
    d["pcore"] = ~d.core_type.str.contains("E-core", na=False)
    return d


def _progression(metric: str, chart_id: str, title: str, subtitle: str, alt: str, ylabel: str, ylim: float,
                 label_fmt, offsets: dict):
    d = _road()
    d = d[d[metric].notna()]
    c = Chart(id=chart_id, title=title, subtitle=subtitle, alt=alt, data=[ROAD], chapters=["04", "17"],
              source="vendor announcements and press", source_ids=sources_of(d),
              note="Hollow / dashed = not yet shipping")
    fig, ax = c.figure(width=10.5, height=6.0)
    used = set()
    for vendor, filt, lab in LINE_GROUPS:
        s = d[d.vendor.eq(vendor)]
        if filt == "P":
            s = s[s.pcore]
        s = s.sort_values("year")
        if s.empty:
            continue
        col = _vcolor(vendor)
        used.update(s.index)
        lw = 2.6 if vendor == "NVIDIA" else 2.0
        for a, b in zip(s.iloc[:-1].itertuples(), s.iloc[1:].itertuples()):
            ax.plot([a.year, b.year], [getattr(a, metric), getattr(b, metric)], color=col, lw=lw,
                    ls="--" if b.future else "-", zorder=4 if vendor == "NVIDIA" else 2)
        for r in s.itertuples():
            ax.scatter(r.year, getattr(r, metric), s=90 if vendor == "NVIDIA" else 70,
                       facecolor="white" if r.future else col, edgecolor=col, linewidth=2,
                       zorder=5 if vendor == "NVIDIA" else 3)
        ax.plot([], [], color=col, marker="o", lw=2, label=lab)
    rest = d[~d.index.isin(used)]
    for r in rest.itertuples():
        col = _vcolor(r.vendor) if r.vendor in ("Intel",) else entity_color("other")
        ax.scatter(r.year + JITTER.get(r.product, 0), getattr(r, metric), s=70, marker="D", facecolor="white" if r.future else col,
                   edgecolor=col, linewidth=2, zorder=3)
    if not rest.empty:
        ax.scatter([], [], marker="D", color=entity_color("other"), label="Other (Ampere, Arm, Fujitsu, Google)")
    for r in d.itertuples():
        dx, dy = offsets.get(r.product, (7, 0))
        ax.annotate(label_fmt(r), (r.year + JITTER.get(r.product, 0), getattr(r, metric)), xytext=(dx, dy), textcoords="offset points",
                    fontsize=8.2, color=INK["title"], va="center", ha="left" if dx >= 0 else "right",
                    fontweight="bold" if r.vendor == "NVIDIA" else "normal")
    ax.set_xlim(2021.6, 2028.9)
    ax.set_ylim(0, ylim)
    ax.set_xticks(range(2022, 2029))
    ax.legend(loc="upper left", fontsize=8.6, ncol=2)
    c.save(fig, ax, xlabel="Launch / availability year", ylabel=ylabel, legend=False)


@register
def server_cpu_core_count_roadmap():
    d = _road()
    vera = d[d["product"].eq("Vera")].max_cores.item()
    venice = d[d["product"].eq("EPYC Venice")].max_cores.item()
    g5 = d[d["product"].eq("Graviton5")].max_cores.item()
    cwf = d[d["product"].str.contains("Clearwater")].max_cores.item()
    short = lambda r: f"{_short(r.product)} {r.max_cores:.0f}"  # noqa: E731
    offsets = {"Grace": (-8, 9), "Vera": (7, -10), "EPYC 9005 Turin": (-7, 9), "EPYC Venice": (7, 4),
               "Graviton5": (-7, -10), "Kunpeng 950": (7, 9), "Kunpeng 960": (-7, 9), "AmpereOne A192-32X": (-7, 9),
               "Xeon 6 Granite Rapids-AP": (7, -9), "Cobalt 100": (-7, 9), "Cobalt 200": (7, -6),
               "Arm AGI CPU": (-7, 8), "MONAKA": (7, -7), "Axion (C4A)": (7, -8), "Graviton4": (7, -8),
               "Graviton3": (7, -8), "EPYC 9004 Genoa": (7, 9), "Xeon 4th Gen Sapphire Rapids": (7, -9),
               "Xeon 7 Diamond Rapids": (7, 9), "Xeon 6+ Clearwater Forest": (7, 0),
               "Datacenter CPU (Oryon-based)": (7, -6)}
    _progression(
        "max_cores", "04-server-cpu-core-count-roadmap",
        title=(f"Rivals ship 2–3× Vera's {vera:.0f} cores: EPYC Venice {venice:.0f}, Graviton5 {g5:.0f}, "
               f"Xeon 6+ {cwf:.0f} E-cores"),
        subtitle="Maximum cores per socket by launch year, 2022–2028 (Qualcomm's 80-core part is an unconfirmed report)",
        alt=(f"Line chart of maximum cores per server CPU socket by year: NVIDIA Grace 72 (2023) and Vera {vera:.0f} (2026); AMD EPYC "
             f"96, 192 and {venice:.0f} (Venice, 2026); Intel Xeon P-core 60, 128 and a reported 192 (Diamond Rapids, 2027) plus "
             f"{cwf:.0f} E-cores (Clearwater Forest, 2026); AWS Graviton 64, 96 and {g5:.0f}; Huawei Kunpeng 192 (2026) and 256 "
             "(2028); Ampere 192, Arm AGI CPU 136, Fujitsu MONAKA 144. NVIDIA does not compete on core count."),
        ylabel="Max cores per socket", ylim=320, label_fmt=short, offsets=offsets)


@register
def server_cpu_memory_bandwidth_roadmap():
    d = _road()
    grace = d[d["product"].eq("Grace")].memory_bw_gbs.item()
    vera = d[d["product"].eq("Vera")].memory_bw_gbs.item()
    venice = d[d["product"].eq("EPYC Venice")].memory_bw_gbs.item()
    dmr = d[d["product"].str.contains("Diamond")].memory_bw_gbs.item()
    short = lambda r: f"{_short(r.product)} {r.memory_bw_gbs:,.0f}"  # noqa: E731
    offsets = {"Grace": (-8, 10), "Vera": (7, -12), "EPYC Venice": (-8, 8), "Xeon 7 Diamond Rapids": (-8, 10),
               "EPYC 9005 Turin": (7, -10), "EPYC 9004 Genoa": (7, 9), "Graviton4": (7, 9), "Graviton3": (7, -10),
               "Xeon 4th Gen Sapphire Rapids": (7, -10), "Xeon 6 Granite Rapids-AP": (-8, 8),
               "Xeon 6+ Clearwater Forest": (7, -9), "AmpereOne A192-32X": (7, 8)}
    _progression(
        "memory_bw_gbs", "04-server-cpu-memory-bandwidth-roadmap",
        title=(f"Vera's {vera/1000:.1f} TB/s ({vera/grace:.1f}× Grace) is matched by x86 within a year: Venice {venice/1000:.1f} TB/s"),
        subtitle="Peak memory bandwidth per socket, GB/s, by launch year (vendor claims; Diamond Rapids = Intel's '2x Granite Rapids', reported)",
        alt=(f"Line chart of peak memory bandwidth per CPU socket: NVIDIA Grace {grace:.0f} GB/s (2023) to Vera {vera:,.0f} GB/s (2026); "
             f"AMD EPYC 461, 576 and {venice:,.0f} GB/s (Venice, 2026, AMD claim); Intel Xeon 307, 845 and about {dmr:,.0f} GB/s "
             "reported for Diamond Rapids (2027); AWS Graviton 307 and 538 GB/s; AmpereOne 333 GB/s. NVIDIA's LPDDR5X lead "
             "over x86 is a 2025-26 window rather than a permanent gap."),
        ylabel="Peak memory bandwidth per socket (GB/s)", ylim=1900, label_fmt=short, offsets=offsets)


# --------------------------------------------------------------------------------------
# 7. Where the CPU dollars sit in a Vera Rubin NVL72 rack
# --------------------------------------------------------------------------------------
@register
def vera_rubin_rack_cpu_share():
    df = load(VALUE)
    d = df[df.record_type.eq("rack_bom")].copy()
    total = d[d.component.eq("Total")].value.item()
    d = d[~d.component.eq("Total")].sort_values("value")
    cpu = d[d.component.str.startswith("Vera CPUs")].value.item()
    soc = d[d.component.str.startswith("LPDDR5X")].value.item()
    gpu = d[d.component.str.startswith("Rubin")].value.item()
    c = Chart(
        id="04-vera-rubin-rack-cpu-share",
        title=(f"Est.: Vera CPUs are ~{cpu/total*100:.0f}% of a ${total:.1f}M Vera Rubin rack; with LPDDR5X, ~{(cpu+soc)/total*100:.0f}%"),
        subtitle="Estimated cost build-up of one Vera Rubin NVL72 rack (ODM price to cloud), US$ M; Morgan Stanley plus a repo split of memory",
        alt=(f"Horizontal bar chart of an estimated ${total:.2f}M Vera Rubin NVL72 rack: 72 Rubin GPUs ${gpu:.2f}M, other content "
             f"(NVSwitch trays, NICs, PCB, power, chassis) about $1.46M, LPDDR5X SOCAMM memory for the Vera CPUs about ${soc:.2f}M "
             f"(implied), HBM4 about $0.90M, 36 Vera CPUs ${cpu:.2f}M (about $5k each, {cpu/gpu*100:.1f} cents per GPU dollar), "
             "ODM margin $0.15M and cooling $0.06M."),
        data=[VALUE], chapters=["04", "08"], source="Morgan Stanley via press; repo split", source_ids=sources_of(d),
        note="All Est.; hatched = repo inference",
    )
    fig, ax = c.figure(width=10.5, height=5.4)
    y = np.arange(len(d))
    cols = []
    for comp in d.component:
        if comp.startswith(("Rubin", "Vera")):
            cols.append(NV)
        elif comp.startswith(("HBM", "LPDDR")):
            cols.append("#3987E5")
        else:
            cols.append(entity_color("other"))
    ax.set_axisbelow(True)
    bars = ax.barh(y, d.value, color=cols, height=0.62, alpha=0.85)
    for b, comp in zip(bars.patches, d.component):
        if "implied" in comp:
            b.set_hatch("///")
    for yi, v in zip(y, d.value):
        ax.text(v + 0.04, yi, f"${v:.2f}M ({v/total*100:.1f}%)", va="center", fontsize=9, color=INK["title"])
    labels = [cmp.replace(" (implied)", "*").replace("Other (NVSwitch trays, NICs, DPUs, PCB, power, chassis)",
                                                       "Other: NVSwitch, NICs, PCB, power")
              for cmp in d.component]
    ax.set_yticks(y, labels)
    for tick, comp in zip(ax.get_yticklabels(), d.component):
        if comp.startswith(("Vera", "LPDDR5X")):
            tick.set_fontweight("bold")
    ax.set_xlim(0, gpu * 1.32)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA silicon"), Patch(color="#3987E5", label="Memory"),
               Patch(color=entity_color("other"), label="Other"),
               Patch(facecolor="#3987E5", hatch="///", edgecolor="white", label="* implied by repo")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _margins(fig, left=0.29, right=0.97)
    c.save(fig, ax, xlabel="US$ millions per rack (Est.)", legend=False)


# --------------------------------------------------------------------------------------
# 8. Arm's royalty ladder
# --------------------------------------------------------------------------------------
@register
def arm_royalty_rate_ladder():
    df = load(VALUE)
    d = df[df.record_type.eq("royalty_rate")].copy()
    piv = d.pivot_table(index="item", columns="metric", values="value", aggfunc="first")
    order = ["Armv8 cores", "Armv9 cores", "Compute Subsystem (CSS)"]
    piv = piv.reindex(order)
    asp = 5000  # ~Vera-class CPU cost per Morgan Stanley ($0.18M / 36), see l04_cpu_value_chain.csv
    c = Chart(
        id="04-arm-royalty-rate-ladder",
        title=(f"Est.: Arm's royalty climbs from ~{piv.iloc[0].low_pct_of_chip_asp:.0f}–{piv.iloc[0].high_pct_of_chip_asp:.0f}% "
               f"of chip price (v8) to ~{piv.iloc[2].low_pct_of_chip_asp:.0f}–{piv.iloc[2].high_pct_of_chip_asp:.0f}% (CSS)"),
        subtitle="Analyst-estimated Arm royalty as % of chip selling price by licensing tier; labels = US$ per chip on a ~$5,000 server CPU",
        alt=(f"Range bar chart of estimated Arm royalty rates as a share of chip price: Armv8 about 1-3%, Armv9 about 2-5% and "
             f"Compute Subsystems about 8-10% or more, per TIKR and Kavout analyses. On a ~${asp:,} server CPU that is roughly "
             "$50-150, $100-250 and $400-500 per chip - tiny next to a GPU rack, but a rising tax on every Arm server CPU."),
        data=[VALUE], chapters=["04", "13"], source="TIKR and Kavout analyst estimates", source_ids=sources_of(d),
        note="Est.; Arm does not disclose rates",
    )
    fig, ax = c.figure(width=10, height=4.8)
    y = np.arange(len(piv))
    shades = ["#86B6EF", "#3987E5", "#104281"]
    for yi, (name, r), col in zip(y, piv.iterrows(), shades):
        lo, hi = r.low_pct_of_chip_asp, r.high_pct_of_chip_asp
        ax.barh(yi, hi - lo, left=lo, color=col, height=0.5, hatch="//", edgecolor="white", alpha=0.85)
        ax.text(hi + 0.25, yi, f"{lo:g}–{hi:g}%  →  ${asp*lo/100:,.0f}–{asp*hi/100:,.0f} per chip", va="center",
                fontsize=9.2, color=INK["title"])
    ax.set_yticks(y, ["Armv8 cores (e.g. Graviton2)", "Armv9 cores (e.g. Grace, Graviton4)",
                      "Compute Subsystem (e.g. Cobalt)"])
    ax.set_axisbelow(True)
    ax.set_xlim(0, 14)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.30, right=0.97)
    c.save(fig, ax, xlabel="Royalty as % of chip selling price (Est.)", legend=False)
