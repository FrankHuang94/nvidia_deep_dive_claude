"""Layer 06 (scale-out and scale-across networking) strategy charts: competitor heatmap, switch-generation race,
networking attach per compute dollar, scale-out bandwidth per accelerator, value pool by vendor, deal values.

Owner: layer-06 STRATEGY agent. Data: data/l06_competitor_verdicts.csv, l06_switch_generations.csv,
l06_scale_out_per_accelerator.csv, l06_networking_vendor_revenue.csv, l06_networking_deals.csv and the shared
financials.csv (all documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from style import Chart, INK, NV, VERDICT_COLORS, entity_color, load, register, sources_of

VERD = "l06_competitor_verdicts.csv"
GENS = "l06_switch_generations.csv"
SOUT = "l06_scale_out_per_accelerator.csv"
POOL = "l06_networking_vendor_revenue.csv"
DEALS = "l06_networking_deals.csv"
FIN = "financials.csv"

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
    if v in ("HPE", "Arista", "Innolight", "Eoptolink", "Credo", "Cisco"):
        return entity_color("other")
    return entity_color(v)


# --------------------------------------------------------------------------------------
# 1. Competitor capability heatmap (layer-specific)
# --------------------------------------------------------------------------------------
@register
def scale_out_competitor_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    radix_leads = df[df.dimension.eq("Switch radix / bandwidth") & df.verdict_vs_nvidia.eq("leads")].competitor.tolist()
    nic_leads = int(df[df.dimension.eq("NIC co-design")].verdict_vs_nvidia.eq("leads").sum())
    open_leads = int(df[df.dimension.eq("Openness / multi-vendor")].verdict_vs_nvidia.eq("leads").sum())
    c = Chart(
        id="06-scale-out-competitor-heatmap",
        title=(f"Only {radix_leads[0]} beats NVIDIA on switch bandwidth, {open_leads} of {len(comps)} rivals on openness; "
               f"{'none' if nic_leads == 0 else nic_leads} on NIC co-design"),
        subtitle="Repo verdict for each scale-out rival vs NVIDIA (InfiniBand + Spectrum-X) on six dimensions, as of 2026-11",
        alt=(f"Heatmap of {len(comps)} scale-out networking rivals against NVIDIA on six dimensions. Broadcom alone leads on "
             "switch radix and bandwidth (Tomahawk 6 at 102.4 Tb/s in 2025, about a year before Spectrum-6); "
             f"{open_leads} rivals lead on openness (merchant silicon, UEC, SONiC); none leads on NIC co-design, where "
             "Broadcom's 800G Thor Ultra trails ConnectX-9 at 1.6 Tb/s and AMD's UEC NICs reach parity only by using three "
             "per GPU; white-box ODMs led by Celestica lead on share of Ethernet AI back-end switch sales; Google and AWS "
             "run captive, different-approach fabrics."),
        data=[VERD], chapters=["06", "15"], source="repo analysis of vendor releases and Dell'Oro (l06_competitor_verdicts.csv)",
        source_ids=sources_of(df), note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=12.5, height=7.4)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {r.cell_label}", ha="center", va="center",
                    fontsize=8.4, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" / ", " /\n") for d in dims], fontsize=9)
    ax.xaxis.tick_top()
    prod = df.drop_duplicates("competitor").set_index("competitor").product_basis
    ax.set_yticks(np.arange(len(comps)) + 0.5)

    def _wrap(s: str, n: int = 30) -> str:
        if len(s) <= n:
            return s
        cut = s.rfind(" ", 0, n)
        return s[:cut] + "\n" + s[cut + 1:] if cut > 0 else s
    ax.set_yticklabels([f"{cmp}\n{_wrap(prod[cmp])}" for cmp in comps], fontsize=8.2)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.205, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.08)


# --------------------------------------------------------------------------------------
# 2. Switch-generation race: announce vs first shipment by vendor
# --------------------------------------------------------------------------------------
@register
def switch_generation_race():
    df = load(GENS)
    df["ann"] = pd.to_datetime(df.announce_date)
    df["ship"] = pd.to_datetime(df.ship_date)
    th6 = df[df["product"].eq("Tomahawk 6")].iloc[0]
    sp6 = df[df["product"].str.startswith("Spectrum-6")].iloc[0]
    gap = (sp6.ship - th6.ship).days / 30.44
    c = Chart(
        id="06-switch-generation-race",
        title=(f"Broadcom shipped 102.4 Tb/s ~{gap:.0f} months before NVIDIA's Spectrum-6 reached partners"),
        subtitle="Switch ASIC generations by vendor: announcement (hollow) to first shipments (filled); 51.2T and 102.4T classes",
        alt=(f"Dumbbell timeline of switch ASIC generations. 51.2 Tb/s: NVIDIA announced Spectrum-4 first (March 2022) but "
             "launched it as Spectrum-X in May 2023, while Broadcom shipped Tomahawk 5 in August 2022; Marvell Teralynx 10 "
             "(March 2023) and Cisco G200 (June 2023) followed. 102.4 Tb/s: NVIDIA announced Spectrum-6 photonics in March "
             f"2025, Broadcom shipped Tomahawk 6 in June 2025, and TrendForce reported limited Spectrum-6 shipments in July "
             f"2026, about {gap:.0f} months later; Cisco's G300 (announced February 2026) is planned for H2 2026. "
             "NVIDIA's 115.2 Tb/s Quantum-X800 InfiniBand switch was announced in March 2024 and shipped in 2025."),
        data=[GENS], chapters=["06", "15"], source="vendor releases and TrendForce", source_ids=sources_of(df),
        note="Hollow = announced; filled = shipping; dashed = planned",
    )
    order = [("51.2 Tb/s Ethernet", df[df.class_tbps.eq(51.2)]), ("102.4 Tb/s Ethernet", df[df.class_tbps.eq(102.4)]),
             ("InfiniBand", df[df.fabric.eq("InfiniBand")])]
    fig, ax = c.figure(width=11, height=6.2)
    y = 0
    yticks, ylabels = [], []
    for gname, g in order:
        ax.text(pd.Timestamp("2021-10-15"), y - 0.15, gname, fontsize=9.5, fontweight="bold", color=INK["title"], va="center")
        y += 0.75
        for r in g.sort_values("ann").itertuples():
            col = _vcolor(r.vendor) if r.vendor != "Cisco" else "#52514E"
            planned = r.status == "announced"
            if pd.notna(r.ship):
                ax.plot([r.ann, r.ship], [y, y], color=col, lw=2.2, ls="--" if planned else "-", zorder=2)
                ax.scatter([r.ship], [y], s=95, color="white" if planned else col, edgecolor=col, linewidth=2, zorder=3)
            ax.scatter([r.ann], [y], s=95, facecolor="white", edgecolor=col, linewidth=2, zorder=4)
            end = r.ship if pd.notna(r.ship) else r.ann
            lab = r.ship_basis if pd.notna(r.ship) else "ship date not disclosed"
            ax.annotate(lab, (end, y), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8.2,
                        color=INK["text"])
            yticks.append(y)
            ylabels.append(f"{r.vendor} {r.product}")
            y += 1
        y += 0.35
    ax.set_yticks(yticks, ylabels, fontsize=8.8)
    ax.set_ylim(y - 0.4, -0.7)
    ax.set_xlim(pd.Timestamp("2021-10-01"), pd.Timestamp("2028-06-30"))
    ax.axvline(pd.Timestamp("2026-11-05"), color=INK["base"], lw=1, ls=":")
    ax.text(pd.Timestamp("2026-11-20"), -0.45, "as of\n2026-11-05", fontsize=8, color=INK["muted"], va="top")
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=INK["text"], markersize=8,
                      label="announced"),
               Line2D([], [], marker="o", ls="", color=INK["text"], markersize=8, label="first shipments"),
               Patch(color=NV, label="NVIDIA"), Patch(color=entity_color("broadcom"), label="Broadcom"),
               Patch(color=entity_color("marvell"), label="Marvell"), Patch(color="#52514E", label="Cisco")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.6, ncol=2)
    _margins(fig, left=0.30, right=0.98)
    c.save(fig, ax, xlabel="Date", legend=False)


# --------------------------------------------------------------------------------------
# 3. Networking dollars per compute dollar (attach), by quarter
# --------------------------------------------------------------------------------------
@register
def networking_attach_per_compute():
    fin = load(FIN)
    q = fin[fin.period_type.eq("Q") & fin.metric.isin(["revenue_dc_networking", "revenue_dc_compute"])]
    w = q.pivot_table(index=["period", "period_end"], columns="metric", values="value", aggfunc="first").reset_index()
    w = w.dropna().sort_values("period_end")
    conf = q[q.metric.eq("revenue_dc_networking")].set_index("period").confidence
    comp_conf = q[q.metric.eq("revenue_dc_compute")].set_index("period").confidence
    w["attach"] = w.revenue_dc_networking / w.revenue_dc_compute
    w["est"] = w.period.map(lambda p: conf.get(p) == "estimate" or comp_conf.get(p) == "estimate")
    lo = w.loc[w.attach.idxmin()]
    last = w.iloc[-1]
    first = w.iloc[0]
    c = Chart(
        id="06-networking-attach-per-compute",
        title=(f"NVIDIA now sells ~${last.attach:.2f} of networking per $1 of compute, up from ${lo.attach:.2f} at the "
               f"Blackwell switchover"),
        subtitle="Data Center networking revenue ÷ Data Center compute revenue, by fiscal quarter (US$ per US$); hatched = estimate",
        alt=(f"Bar chart of NVIDIA networking revenue per dollar of compute revenue by quarter: about ${first.attach:.2f} in "
             f"{first.period} (estimate), falling to ${lo.attach:.2f} in {lo.period} as Blackwell compute ramped ahead of its "
             f"networking, then recovering to ${last.attach:.2f} in {last.period} (estimate: $17.5B networking vs $71.5B "
             "compute) as NVLink switch trays, Spectrum-X Ethernet and 800G InfiniBand shipped with GB200/GB300 racks. "
             "Networking includes NVLink scale-up switches, so this is not a pure scale-out attach rate."),
        data=[FIN], chapters=["06", "13"], source="NVIDIA CFO commentary and filings; repo calculation",
        source_ids=sources_of(fin[fin.period.isin(w.period) & fin.metric.isin(["revenue_dc_networking",
                                                                             "revenue_dc_compute"])]),
        note="Networking includes NVLink switches",
    )
    fig, ax = c.figure(width=11, height=5.8)
    x = np.arange(len(w))
    bars = ax.bar(x, w.attach, color=NV, width=0.68)
    for b, e, v in zip(bars, w.est, w.attach):
        if e:
            b.set_hatch("///")
            b.set_alpha(0.7)
        ax.annotate(f"{v:.2f}", (b.get_x() + b.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=8.3, color=INK["title"])
    ax.set_xticks(x, [p.replace("FY", "\nFY") for p in w.period], fontsize=8.5)
    ax.set_ylim(0, 0.34)
    spans = [("Hopper + InfiniBand\nbuild-outs", 0, 3), ("Blackwell compute\nramps first", 4, 8),
             ("NVLink racks + Spectrum-X\nscale out", 9, len(w) - 1)]
    for lab, a, b in spans:
        ax.annotate("", xy=(a - 0.35, 0.315), xytext=(b + 0.35, 0.315),
                    arrowprops=dict(arrowstyle="<->", color=INK["muted"], lw=1))
        ax.text((a + b) / 2, 0.322, lab, ha="center", va="bottom", fontsize=8.4, color=INK["text"])
    c.save(fig, ax, xlabel="NVIDIA fiscal quarter", ylabel="Networking $ per $ of compute", legend=False)


# --------------------------------------------------------------------------------------
# 4. Scale-out bandwidth per accelerator
# --------------------------------------------------------------------------------------
@register
def scale_out_bandwidth_per_accelerator():
    df = load(SOUT)
    helios = df[df.system.eq("Helios")].iloc[0]
    vr = df[df.system.eq("Vera Rubin NVL72")].iloc[0]
    c = Chart(
        id="06-scale-out-bandwidth-per-accelerator",
        title=(f"AMD's Helios gives each GPU {helios.scale_out_gbps_per_accelerator/1000:.1f} Tb/s of scale-out, "
               f"{helios.scale_out_gbps_per_accelerator/vr.scale_out_gbps_per_accelerator:.1f}× Vera Rubin's "
               f"{vr.scale_out_gbps_per_accelerator/1000:.1f} Tb/s"),
        subtitle="Scale-out (back-end NIC) bandwidth per accelerator, Gb/s per direction, by system and year; hatched = roadmap",
        alt=(f"Bar chart of scale-out NIC bandwidth per accelerator: NVIDIA HGX H100 400 Gb/s (2022), GB200 NVL72 400 (2024), "
             f"GB300 NVL72 800 (2025), Vera Rubin NVL72 1,600 (2026) and Feynman about 1,600 per ConnectX-10 port (2028, "
             f"reported); AMD Helios {helios.scale_out_gbps_per_accelerator:,.0f} Gb/s per MI455X through three 800G UEC "
             "NICs (2026); AWS Trn2 about 200 and P6-B200 400 Gb/s per chip over EFA. NVIDIA doubles per generation; AMD "
             "jumped ahead by buying more NICs per GPU."),
        data=[SOUT], chapters=["06", "07", "15"], source="vendor releases and docs", source_ids=sources_of(df),
        note="Hatched = roadmap (reported)",
    )
    d = df.sort_values(["vendor", "year"], key=lambda s: s.map({"NVIDIA": 0, "AMD": 1, "AWS": 2}) if s.name == "vendor" else s)
    fig, ax = c.figure(width=11, height=5.9)
    x = np.arange(len(d))
    cols = [_vcolor(v) for v in d.vendor]
    bars = ax.bar(x, d.scale_out_gbps_per_accelerator, color=cols, width=0.66)
    for b, r in zip(bars, d.itertuples()):
        if r.status == "roadmap":
            b.set_hatch("///")
            b.set_alpha(0.7)
        lab = f"{r.scale_out_gbps_per_accelerator:,.0f}"
        if pd.notna(r.nics_per_accelerator) and r.nics_per_accelerator > 1:
            lab += f"\n({r.nics_per_accelerator:.0f}×{r.gbps_per_nic:.0f}G)"
        ax.annotate(lab, (b.get_x() + b.get_width() / 2, r.scale_out_gbps_per_accelerator), xytext=(0, 3),
                    textcoords="offset points", ha="center", fontsize=8.6, color=INK["title"])
    ax.set_xticks(x, [f"{r.system}\n{r.nic}\n{r.year}" for r in d.itertuples()], fontsize=7.9)
    ax.set_ylim(0, 2900)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=entity_color("amd"), label="AMD (UEC)"),
               Patch(color=entity_color("aws"), label="AWS (EFA)")]
    ax.legend(handles=handles, loc="upper left", fontsize=9)
    _margins(fig, bottom=0.25)
    c.save(fig, ax, xlabel="System, NIC and year", ylabel="Gb/s per accelerator (one direction)", legend=False,
           bottom=0.25)


# --------------------------------------------------------------------------------------
# 5. Who captures networking dollars: latest annual revenue by vendor
# --------------------------------------------------------------------------------------
@register
def networking_value_pool_by_vendor():
    df = load(POOL)
    nv = df[df.metric.eq("networking_revenue")].iloc[0]
    inno = df[df.entity.eq("Innolight")].iloc[0]
    ari = df[df.entity.eq("Arista")].iloc[0]
    c = Chart(
        id="06-networking-value-pool-by-vendor",
        title=(f"NVIDIA's ~${nv.value_usd_b:.0f}B networking line is ~{nv.value_usd_b/inno.value_usd_b:.0f}× the largest "
               f"optics maker and ~{nv.value_usd_b/ari.value_usd_b:.0f}× Arista's 2026 AI target"),
        subtitle="Latest annual revenue tied to AI networking, US$ B (period in label); hatched = annualized or includes non-networking",
        alt=(f"Horizontal bar chart of AI-networking-related revenue: NVIDIA networking ${nv.value_usd_b}B in FY2026 and a "
             "~$70B annualized run-rate in Q2 FY2027 (both include NVLink switches); Broadcom AI semiconductors $20.2B in "
             f"FY2025, which mixes custom XPUs with AI Ethernet; optics makers Innolight ${inno.value_usd_b}B and Eoptolink "
             f"$3.5B in 2025; Arista's 2026 AI networking target of at least ${ari.value_usd_b}B; Credo $1.34B in fiscal "
             "2026. NVIDIA alone books more networking revenue than the merchant switch, optics and cable specialists shown "
             "combined, excluding Broadcom."),
        data=[POOL], chapters=["06", "13", "15"], source="company filings, LightCounting, press", source_ids=sources_of(df),
        note="Not like-for-like: see labels",
    )
    d = df.copy()
    d["label"] = d.apply(lambda r: f"{r.entity}: {r.category}\n({r.period})", axis=1)
    d = d.iloc[::-1].reset_index(drop=True)
    fig, ax = c.figure(width=11, height=6.2)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = _vcolor(r.entity)
        bar = ax.barh(yi, r.value_usd_b, color=col, height=0.62)
        if r.metric in ("networking_annualized_run_rate", "ai_semiconductor_revenue"):
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_alpha(0.65)
        note = ""
        if r.metric == "ai_semiconductor_revenue":
            note = "  incl. custom XPUs"
        elif r.metric == "ai_revenue_target":
            note = "  target (at least)"
        elif r.metric == "networking_annualized_run_rate":
            note = "  Q2 FY2027 × 4"
        ax.text(r.value_usd_b + 0.8, yi, f"${r.value_usd_b:,.1f}B{note}", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, d.label, fontsize=8.4)
    ax.set_xlim(0, 88)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.36, right=0.97)
    c.save(fig, ax, xlabel="US$ B per year", legend=False)


# --------------------------------------------------------------------------------------
# 6. Deal values in networking and optics
# --------------------------------------------------------------------------------------
@register
def networking_deal_values():
    df = load(DEALS)
    d = df.copy()
    d["year"] = d.announce_date.str[:4]
    d["label"] = d.apply(lambda r: f"{r.target} ← {r.acquirer} ({r.year})", axis=1)
    d = d.sort_values("value_usd_m", na_position="first").reset_index(drop=True)
    mel = d[d.target.eq("Mellanox")].value_usd_m.item()
    jun = d[d.target.eq("Juniper Networks")].value_usd_m.item()
    optics = d[d.acquirer.eq("NVIDIA") & d.target.str.contains("Lumentum|Coherent")].value_usd_m.sum()
    c = Chart(
        id="06-networking-deal-values",
        title=(f"Mellanox (${mel/1000:.1f}B) built NVIDIA's network franchise; its 2026 laser stakes add ${optics/1000:.0f}B"),
        subtitle="Disclosed or reported deal value, US$ millions (log scale), networking, optics and interconnect deals 2019–2026",
        alt=(f"Log-scale horizontal bar chart of networking deals: HPE-Juniper ${jun/1000:.0f}B (2024 announced), "
             f"NVIDIA-Mellanox ${mel/1000:.1f}B (2019), Marvell-Celestial AI ~$3.25B upfront (2025), Qualcomm-Alphawave "
             f"~$2.4B (2025), NVIDIA's $2B stakes in each of Lumentum, Coherent and Marvell (2026), AMD-Pensando $1.9B "
             "(2022) and NVIDIA's ~$0.9B Enfabrica acquihire (2025); NVIDIA-Cumulus (2020) and Marvell-Innovium (2021) "
             "terms are not in the repo's sources."),
        data=[DEALS], chapters=["06", "13", "19"], source="company releases and press", source_ids=sources_of(d),
        note="Hatched = reported; light = equity stake",
    )
    fig, ax = c.figure(width=11, height=6.2)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = _vcolor(r.acquirer)
        if pd.isna(r.value_usd_m):
            ax.text(120, yi, "terms not in repo sources", va="center", fontsize=8.6, color=INK["muted"], style="italic")
            continue
        stake = r.deal_type == "equity-investment"
        bar = ax.barh(yi, r.value_usd_m, color=col, height=0.62, alpha=0.5 if stake else 1.0)
        if r.value_basis == "reported":
            bar.patches[0].set_hatch("///")
        txt = f"${r.value_usd_m/1000:.1f}B" if r.value_usd_m >= 1000 else f"~${r.value_usd_m:,.0f}M"
        if stake:
            txt += " stake"
        ax.text(r.value_usd_m * 1.12, yi, txt, va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, d.label, fontsize=8.8)
    ax.set_ylim(-0.7, len(d) - 0.4)
    ax.set_xscale("log")
    ax.set_xlim(100, 60000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=entity_color("amd"), label="AMD"),
               Patch(color=entity_color("marvell"), label="Marvell"), Patch(color=entity_color("qualcomm"), label="Qualcomm"),
               Patch(color=entity_color("other"), label="HPE")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _margins(fig, left=0.30, right=0.97)
    c.save(fig, ax, xlabel="Deal value, US$ millions (log scale)", logx=True, legend=False)
