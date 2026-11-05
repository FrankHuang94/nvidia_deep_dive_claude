"""Layer 05 (scale-up: NVLink, NVSwitch) strategy charts: competitor verdicts, domain vs bandwidth,
open-standard timelines, roadmap progression, supplier revenue and deal values.

Owner: layer-05 STRATEGY agent. Data: data/l05_scale_up_verdicts.csv, l05_standards_timeline.csv,
l05_value_chain.csv, l05_deals.csv (documented in data/README.md) and the shared interconnect_specs.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

from style import (Chart, GEN_PAST, INK, NV, VERDICT_COLORS, entity_color, hatch_future, load, register,
                   sources_of)

VERD = "l05_scale_up_verdicts.csv"
STD = "l05_standards_timeline.csv"
VALUE = "l05_value_chain.csv"
DEALS = "l05_deals.csv"
IC = "interconnect_specs.csv"

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


def _ic_row(df: pd.DataFrame, generation: str) -> pd.Series:
    r = df[df.generation.eq(generation)]
    if r.empty:
        raise KeyError(generation)
    return r.iloc[0]


# --------------------------------------------------------------------------------------
# 1. Competitor capability heatmap (scale-up specific)
# --------------------------------------------------------------------------------------
@register
def scale_up_competitor_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    n = len(comps)
    lead = {d: int(df[df.dimension.eq(d)].verdict_vs_nvidia.eq("leads").sum()) for d in dims}
    c = Chart(
        id="05-scale-up-competitor-heatmap",
        title=(f"Rivals out-scale NVLink on domain size ({lead['Domain size']} of {n}) and openness "
               f"({lead['Openness']} of {n}); only AMD beats it on per-GPU bandwidth"),
        subtitle="Repo verdict for each scale-up rival vs NVIDIA Vera Rubin NVL72 (NVLink 6) on five dimensions; cell = verdict letter + key fact",
        alt=(f"Heatmap of six scale-up rivals against NVIDIA's Vera Rubin NVL72 on five dimensions. On domain size "
             f"{lead['Domain size']} of {n} lead (Google TPU pods 9,216-9,600 chips, Huawei 384 to 8,192, AWS 144, UALink spec "
             "1,024, Ethernet 512) while AMD Helios ties at 72. On bandwidth per accelerator only AMD Helios leads (3.6 vs "
             "3.0 TB/s); Google, AWS and Huawei trail. UALink, Ethernet scale-up and AMD lead on openness. On maturity "
             "UALink, Huawei's Atlas 950 and Helios trail, while Google's optical-switched pods have run since 2021."),
        data=[VERD], chapters=["05", "15"], source="repo analysis of vendor specs (l05_scale_up_verdicts.csv)",
        source_ids=sources_of(df), note="Analyst judgement; see rationale column",
    )
    fig, ax = c.figure(width=12.5, height=6.4)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            label = str(r.cell_label)
            if len(label) > 24:
                cut = label.rfind(" ", 0, 24)
                label = label[:cut] + "\n" + label[cut + 1:]
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {label}", ha="center", va="center",
                    fontsize=8.4, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(n, 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" & ", " &\n").replace(" / ", " /\n").replace(" per ", "\nper ") for d in dims],
                       fontsize=9.5)
    ax.xaxis.tick_top()
    prod = df.drop_duplicates("competitor").set_index("competitor").product_basis
    ax.set_yticks(np.arange(n) + 0.5)
    ylabels = []
    for cmp in comps:
        p = str(prod[cmp])
        if len(p) > 30:
            cut = p.rfind(" ", 0, 30)
            p = p[:cut] + "\n" + p[cut + 1:]
        ylabels.append(f"{cmp}\n{p}")
    ax.set_yticklabels(ylabels, fontsize=8.4)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.205, right=0.985)
    c.save(fig, ax, legend=False, top=0.79, bottom=0.08)


# --------------------------------------------------------------------------------------
# 2. Domain size vs per-accelerator bandwidth (topology as marker)
# --------------------------------------------------------------------------------------
POINTS = [
    # (label, generation key in interconnect_specs.csv, vendor, topology, status)
    ("GB200 NVL72", "NVLink 5 (GB200 NVL72)", "NVIDIA", "switched", "past"),
    ("Vera Rubin NVL72", "NVLink 6 (Vera Rubin NVL72)", "NVIDIA", "switched", "now"),
    ("Kyber NVL144 (2027)", "NVLink 7 (Rubin Ultra Kyber NVL144)", "NVIDIA", "switched", "roadmap"),
    ("MI355X 8-GPU", "Infinity Fabric / xGMI (MI355X)", "AMD", "mesh", "now"),
    ("Helios", "UALoE (Helios, MI455X)", "AMD", "switched", "now"),
    ("Ironwood pod", "ICI (TPU7x Ironwood)", "Google", "torus", "now"),
    ("TPU 8t pod", "ICI (TPU 8t)", "Google", "torus", "roadmap"),
    ("Trn2 UltraServer", "NeuronLink-v3 (Trn2 UltraServer)", "AWS", "torus", "now"),
    ("Trn3 UltraServer", "NeuronLink-v4 + NeuronSwitch-v1 (Trn3 UltraServer)", "AWS", "switched", "now"),
    ("CloudMatrix 384", "UnifiedBus (CloudMatrix 384, Ascend 910C)", "Huawei", "switched", "now"),
    ("Atlas 950 SuperPoD", "UnifiedBus 2.0 (Atlas 950 SuperPoD, Ascend 950)", "Huawei", "switched", "roadmap"),
    ("Gaudi 3 node", "Gaudi 3 integrated 200GbE RoCE", "Intel", "mesh", "now"),
]
MARKERS = {"switched": "o", "torus": "s", "mesh": "^"}
TOPO_LABEL = {"switched": "Switched all-to-all (1 switch hop)", "torus": "Torus / multi-hop (neighbour links)",
              "mesh": "Direct mesh, no switch (8 devices)"}


@register
def scale_up_domain_vs_bandwidth():
    ic = load(IC)
    rows = []
    for lab, gen, vendor, topo, status in POINTS:
        r = _ic_row(ic, gen)
        rows.append(dict(label=lab, vendor=vendor, topo=topo, status=status,
                         domain=float(r.max_domain_size), bw=float(r.per_device_bw_gbs_bidir) / 1000,
                         source_id=r.source_id))
    d = pd.DataFrame(rows)
    vr = d[d.label.eq("Vera Rubin NVL72")].iloc[0]
    tpu = d[d.label.eq("Ironwood pod")].iloc[0]
    c = Chart(
        id="05-scale-up-domain-vs-bandwidth",
        title=(f"No one leads on both axes: TPU pods are {tpu.domain / vr.domain:.0f}× larger, "
               f"but NVIDIA and AMD give each GPU {vr.bw:.1f}–3.6 TB/s"),
        subtitle="Scale-up domain size (accelerators, log scale) vs scale-up bandwidth per accelerator (TB/s, bidirectional); marker = topology",
        alt=(f"Scatter plot of scale-up domains. Switched all-to-all designs sit at 72-384 accelerators: NVIDIA GB200 NVL72 "
             f"(1.8 TB/s), Vera Rubin NVL72 ({vr.bw:.1f} TB/s), AMD Helios (3.6 TB/s), AWS Trn3 (144 chips, 2.0 TB/s), Huawei "
             f"CloudMatrix 384 (0.78 TB/s) and the roadmap Kyber NVL144 (3.6 TB/s). Torus designs reach 9,216 chips (Google "
             f"Ironwood, {tpu.bw:.1f} TB/s) and 9,600 (TPU 8t, 2.4 TB/s), and Huawei's Atlas 950 targets 8,192 at 2.0 TB/s. "
             "Eight-device meshes (MI355X, Gaudi 3) sit at 1.1-1.2 TB/s."),
        data=[IC], chapters=["05", "15"], source="vendor specs compiled in interconnect_specs.csv",
        source_ids=sources_of(d), note="Hollow = announced / roadmap",
    )
    fig, ax = c.figure(width=11, height=6.4)
    order = ["Intel", "Huawei", "AWS", "Google", "AMD", "NVIDIA"]
    offsets = {
        "GB200 NVL72": (8, -12), "Vera Rubin NVL72": (-10, -16), "Kyber NVL144 (2027)": (8, 6),
        "MI355X 8-GPU": (8, -12), "Helios": (-8, 9), "Ironwood pod": (-12, -15), "TPU 8t pod": (-12, 9),
        "Trn2 UltraServer": (8, -4), "Trn3 UltraServer": (8, -12), "CloudMatrix 384": (8, -4),
        "Atlas 950 SuperPoD": (-14, 9), "Gaudi 3 node": (8, 4),
    }
    for vendor in order:
        sub = d[d.vendor.eq(vendor)]
        for r in sub.itertuples():
            col = NV if vendor == "NVIDIA" else entity_color(vendor)
            if vendor == "NVIDIA" and r.status == "past":
                col = GEN_PAST
            hollow = r.status == "roadmap"
            ax.scatter([r.domain], [r.bw], s=150 if vendor == "NVIDIA" else 120, marker=MARKERS[r.topo],
                       facecolor="white" if hollow else col, edgecolor=NV if (vendor == "NVIDIA") else col,
                       linewidth=2.2, zorder=4 if vendor == "NVIDIA" else 3)
            dx, dy = offsets.get(r.label, (8, 4))
            ha = "right" if dx < 0 else "left"
            ax.annotate(f"{r.label} · {vendor}", (r.domain, r.bw), xytext=(dx, dy), textcoords="offset points",
                        fontsize=8.6, ha=ha, va="center", color=INK["title"] if vendor == "NVIDIA" else INK["text"],
                        fontweight="bold" if vendor == "NVIDIA" else "normal")
    ax.set_xscale("log")
    ax.set_xlim(4, 30000)
    ax.set_ylim(0, 4.2)
    ax.axvline(72, color=INK["base"], lw=1, ls=":")
    ax.text(72 * 1.05, 4.05, "72 = one NVL72 rack", fontsize=8.3, color=INK["muted"], va="top")
    handles = [Line2D([0], [0], marker=MARKERS[k], color="none", markerfacecolor=INK["text"], markeredgecolor=INK["text"],
                      markersize=9, label=v) for k, v in TOPO_LABEL.items()]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8, title="Topology", title_fontsize=9)
    c.save(fig, ax, xlabel="Scale-up domain size (accelerators)", logx=True,
           ylabel="Scale-up bandwidth per accelerator (TB/s)", legend=False)


# --------------------------------------------------------------------------------------
# 3. Open standards: formation -> spec -> silicon -> product
# --------------------------------------------------------------------------------------
@register
def open_standards_time_to_silicon():
    df = load(STD)
    df["t"] = pd.to_datetime(df.date)
    tracks = list(dict.fromkeys(df.track))
    ual = df[df.track.eq("UALink")]
    ual_start = ual[ual.milestone_type.eq("formation")].t.min()
    ual_prod = ual[ual.milestone_type.eq("first_product")].t.max()
    yrs = (ual_prod - ual_start).days / 365.25
    nv5 = df[df.track.eq("NVLink 5 / NVL72")]
    nv6 = df[df.track.eq("NVLink 6 / Vera Rubin")]
    m5 = (nv5[nv5.milestone_type.eq("first_product")].t.max() - nv5[nv5.milestone_type.eq("announce")].t.min()).days / 30.44
    m6 = (nv6[nv6.milestone_type.eq("first_product")].t.max() - nv6[nv6.milestone_type.eq("announce")].t.min()).days / 30.44
    c = Chart(
        id="05-open-standards-time-to-silicon",
        title=(f"UALink needs ~{yrs:.0f} years from founding to products; NVIDIA ships NVLink "
               f"{m5:.0f}–{m6:.0f} months after announcing it"),
        subtitle="Milestones per scale-up and related interconnect track, 2022–2027; hollow markers = expected (trade-press or analyst window)",
        alt=(f"Timeline chart. NVIDIA's GB200 NVL72 went from announcement (March 2024) to first volume shipments in about "
             f"{m5:.0f} months and NVLink 6 Vera Rubin from roadmap (March 2025) to production shipments (August 2026) in about "
             f"{m6:.0f} months. UALink's promoter group formed in May 2024, published spec 1.0 in April 2025 and 2.0 in April "
             f"2026, with silicon expected in labs in H2 2026 and products in 2027, about {yrs:.0f} years after founding. "
             "Broadcom shipped Tomahawk Ultra in July 2025 before the SUE and ESUN specs (2025-26); NVLink Fusion's first "
             "third-party accelerator (Trainium4) is estimated for 2027; PCIe 6.0 took about three years from spec to GPU platforms."),
        data=[STD], chapters=["05", "06"], source="consortium releases, vendor announcements and trade press (l05_standards_timeline.csv)",
        source_ids=sources_of(df), note="Expected dates are mid-window placeholders",
    )
    fig, ax = c.figure(width=12, height=6.6)
    style = {
        "formation": ("o", "#7A7A7A", "Group formed / workstream"),
        "announce": ("o", NV, "Announced (NVIDIA)"),
        "spec": ("D", "#256ABF", "Specification published"),
        "first_silicon": ("s", "#C98500", "First silicon"),
        "first_product": ("s", INK["title"], "First product / shipments"),
    }
    for i, tr in enumerate(tracks):
        sub = df[df.track.eq(tr)].sort_values("t")
        is_nv = sub.owner.iloc[0].startswith("NVIDIA")
        col_line = NV if is_nv else INK["base"]
        done = sub[sub.status.eq("done")]
        ax.plot(sub.t, [i] * len(sub), color=col_line, lw=3 if is_nv else 2.2, zorder=1, alpha=0.9)
        exp = sub[sub.status.eq("expected")]
        if not exp.empty and not done.empty:
            ax.plot([done.t.max(), exp.t.max()], [i, i], color="#FFFFFF", lw=3.2, zorder=1.5)
            ax.plot([done.t.max(), exp.t.max()], [i, i], color=col_line, lw=2.2, ls=(0, (2, 2)), zorder=2)
        for r in sub.itertuples():
            mk, col, _ = style[r.milestone_type]
            if r.milestone_type == "announce":
                col = NV
            hollow = r.status == "expected"
            ax.scatter([r.t], [i], marker=mk, s=95, facecolor="white" if hollow else col, edgecolor=col,
                       linewidth=2, zorder=3)
        # duration label
        span = (sub.t.max() - sub.t.min()).days / 30.44
        ax.annotate(f"{span:.0f} mo", (sub.t.max(), i), xytext=(9, 0), textcoords="offset points", va="center",
                    fontsize=8.6, color=NV if is_nv else INK["text"], fontweight="bold" if is_nv else "normal")
    ax.set_yticks(range(len(tracks)))
    ax.set_yticklabels(tracks, fontsize=9.2)
    ax.set_ylim(len(tracks) - 0.5, -0.6)
    ax.set_xlim(pd.Timestamp("2021-10-01"), pd.Timestamp("2028-01-31"))
    ax.axvline(pd.Timestamp("2026-11-05"), color=INK["muted"], lw=1, ls=":")
    ax.text(pd.Timestamp("2026-11-20"), -0.45, "as of 2026-11-05", fontsize=8, color=INK["muted"], va="center")
    ax.grid(axis="x", color=INK["grid"], lw=0.8)
    ax.grid(axis="y", visible=False)
    handles = [Line2D([0], [0], marker=v[0], color="none", markerfacecolor=v[1], markeredgecolor=v[1], markersize=8,
                      label=v[2]) for v in style.values()]
    handles.append(Line2D([0], [0], marker="s", color="none", markerfacecolor="white", markeredgecolor=INK["title"],
                          markersize=8, label="Expected (hollow)"))
    ax.legend(handles=handles, loc="lower left", fontsize=8.5, ncol=3, frameon=True)
    _margins(fig, left=0.205, right=0.975)
    c.save(fig, ax, xlabel="Date", legend=False)


# --------------------------------------------------------------------------------------
# 4. Roadmap progression: per-accelerator bandwidth and domain size by year and vendor
# --------------------------------------------------------------------------------------
SERIES = {
    "NVIDIA": [("NVLink 1", 2016, "8"), ("NVLink 2", 2017, None), ("NVLink 3", 2020, None),
               ("NVLink 4 (HGX H100 NVL8)", 2022, None), ("NVLink 5 (GB200 NVL72)", 2024, None),
               ("NVLink 6 (Vera Rubin NVL72)", 2026, None), ("NVLink 7 (Rubin Ultra Kyber NVL144)", 2027, None)],
    "AMD": [("Infinity Fabric / xGMI (MI300X)", 2023, None), ("Infinity Fabric / xGMI (MI355X)", 2025, None),
            ("UALoE (Helios, MI455X)", 2026, None)],
    "Google": [("ICI (TPU v4)", 2021, None), ("ICI (TPU v5p)", 2023, None), ("ICI (TPU7x Ironwood)", 2025, None),
               ("ICI (TPU 8t)", 2026, None)],
    "AWS": [("NeuronLink-v3 (Trn2 UltraServer)", 2024, None),
            ("NeuronLink-v4 + NeuronSwitch-v1 (Trn3 UltraServer)", 2025, None)],
    "Huawei": [("UnifiedBus (CloudMatrix 384, Ascend 910C)", 2025, None),
               ("UnifiedBus 2.0 (Atlas 950 SuperPoD, Ascend 950)", 2026, None),
               ("UnifiedBus (Atlas 960 SuperPoD, Ascend 960)", 2027, None)],
}
ROADMAP_GENS = {"NVLink 7 (Rubin Ultra Kyber NVL144)", "ICI (TPU 8t)", "UnifiedBus 2.0 (Atlas 950 SuperPoD, Ascend 950)",
                "UnifiedBus (Atlas 960 SuperPoD, Ascend 960)"}
# NVIDIA domain steps (productized domains), incl. limited DGX GH200 and roadmap NVL1152
NV_DOMAIN = [("NVLink 1", 2016), ("NVLink 2 + NVSwitch (DGX-2)", 2018), ("NVLink 3", 2020),
             ("NVLink 4 (NVLink Switch System, DGX GH200)", 2023), ("NVLink 5 (GB200 NVL72)", 2024),
             ("NVLink 6 (Vera Rubin NVL72)", 2026), ("NVLink 7 (Rubin Ultra Kyber NVL144)", 2027),
             ("NVLink 8 CPO (Feynman Kyber NVL1152)", 2028)]


@register
def scale_up_roadmap_progression():
    ic = load(IC)
    used = []
    c_rows = {}
    for vendor, items in SERIES.items():
        pts = []
        for gen, year, _ in items:
            r = _ic_row(ic, gen)
            used.append(r)
            bw = r.per_device_bw_gbs_bidir
            pts.append(dict(gen=gen, year=year, bw=float(bw) / 1000 if pd.notna(bw) else np.nan,
                            dom=float(r.max_domain_size) if pd.notna(r.max_domain_size) else np.nan,
                            road=gen in ROADMAP_GENS))
        c_rows[vendor] = pd.DataFrame(pts)
    nvd = []
    for gen, year in NV_DOMAIN:
        r = _ic_row(ic, gen)
        used.append(r)
        nvd.append(dict(gen=gen, year=year, dom=float(r.max_domain_size), road=year >= 2027,
                        limited="GH200" in gen))
    nvd = pd.DataFrame(nvd)
    src = pd.DataFrame(used)
    c = Chart(
        id="05-scale-up-roadmap-progression",
        title="Rivals caught NVLink's per-GPU bandwidth by 2026 (AMD 3.6, Google 2.4 TB/s); domain sizes diverge from 72 to 9,600",
        subtitle="Left: scale-up bandwidth per accelerator (TB/s, bidirectional). Right: largest scale-up domain (accelerators, log scale). Hollow = roadmap",
        alt=("Two-panel line chart by vendor and year. Bandwidth per accelerator: NVIDIA NVLink 0.16 TB/s (2016), 0.6 (2020), "
             "0.9 (2022), 1.8 (2024), 3.0 (Vera Rubin, 2026, cut from 3.6) and a reported 3.6 for Rubin Ultra (2027); AMD 0.9 "
             "(MI300X, 2023), 1.1 (MI355X, 2025) then 3.6 with Helios (2026); Google 0.6 (TPU v4), 1.2 (v5p, Ironwood) and 2.4 "
             "(TPU 8t, 2026); AWS 1.0 (Trn2) and 2.0 (Trn3); Huawei 0.78 (CloudMatrix 384) and 2.0 (Atlas 950). Domain size: "
             "NVIDIA 8 to 16 GPUs until 2022, 256 in the limited DGX GH200, 72 with NVL72 (2024), 144 with Kyber (2027) and a "
             "speculative 1,152 (2028); Google 4,096 to 9,600; Huawei 384 to 8,192 and 15,488 (2027); AWS 64 to 144; AMD 8 to 72."),
        data=[IC], chapters=["05", "17"], source="vendor specs compiled in interconnect_specs.csv",
        source_ids=sources_of(src), note="Hollow / dashed = roadmap or announced",
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=13, height=6.3)
    draw_order = ["Huawei", "AWS", "Google", "AMD", "NVIDIA"]
    for vendor in draw_order:
        d = c_rows[vendor]
        col = NV if vendor == "NVIDIA" else entity_color(vendor)
        b = d.dropna(subset=["bw"])
        act = b[~b.road]
        a1.plot(act.year, act.bw, color=col, lw=2.6 if vendor == "NVIDIA" else 2, marker="o", markersize=7,
                zorder=4 if vendor == "NVIDIA" else 3)
        rd = b[b.road]
        if not rd.empty:
            seg = pd.concat([act.tail(1), rd])
            a1.plot(seg.year, seg.bw, color=col, lw=2, ls="--", zorder=2)
            a1.scatter(rd.year, rd.bw, s=60, facecolor="white", edgecolor=col, linewidth=2, zorder=5)
        last = b.iloc[-1]
        dy = {"NVIDIA": -0.22, "AMD": 0.16, "Google": -0.05, "AWS": -0.12, "Huawei": 0.08}[vendor]
        a1.annotate(f"{vendor} {last.bw:.1f}", (last.year, last.bw), xytext=(6, dy * 40), textcoords="offset points",
                    fontsize=8.8, color=col, fontweight="bold", va="center")
        # domain panel (non-NVIDIA)
        if vendor != "NVIDIA":
            dd = d.dropna(subset=["dom"])
            act = dd[~dd.road]
            a2.plot(act.year, act.dom, color=col, lw=2, marker="o", markersize=7, zorder=3)
            rd = dd[dd.road]
            if not rd.empty:
                seg = pd.concat([act.tail(1), rd])
                a2.plot(seg.year, seg.dom, color=col, lw=2, ls="--", zorder=2)
                a2.scatter(rd.year, rd.dom, s=60, facecolor="white", edgecolor=col, linewidth=2, zorder=5)
            last = dd.iloc[-1]
            a2.annotate(f"{vendor} {last.dom:,.0f}", (last.year, last.dom), xytext=(6, 0), textcoords="offset points",
                        fontsize=8.8, color=col, fontweight="bold", va="center")
    # rubin launch spec marker
    a1.scatter([2026], [3.6], s=55, marker="x", color=NV, zorder=5)
    a1.annotate("Rubin launch spec 3.6\n(cut to 3.0, Sep–Oct 2026)", (2026, 3.6), xytext=(-8, 16), textcoords="offset points",
                fontsize=8, color=INK["text"], ha="right")
    # NVIDIA domain steps
    act = nvd[~nvd.road & ~nvd.limited]
    a2.step(act.year, act.dom, where="post", color=NV, lw=2.6, zorder=4)
    a2.scatter(act.year, act.dom, color=NV, s=45, zorder=5)
    lim = nvd[nvd.limited]
    a2.scatter(lim.year, lim.dom, s=70, marker="D", facecolor="white", edgecolor=NV, linewidth=2, zorder=5)
    a2.annotate("DGX GH200 256\n(limited)", (lim.year.iloc[0], lim.dom.iloc[0]), xytext=(-6, 12), textcoords="offset points",
                fontsize=8, color=INK["text"], ha="right")
    rd = nvd[nvd.road]
    seg = pd.concat([act.tail(1), rd])
    a2.plot(seg.year, seg.dom, color=NV, lw=2, ls="--", zorder=3)
    a2.scatter(rd.year, rd.dom, s=60, facecolor="white", edgecolor=NV, linewidth=2, zorder=5)
    a2.annotate("NVIDIA 72 → 144 (Kyber)\n→ 1,152 (Feynman, 🔴)", (2028, 1152), xytext=(-8, 0), textcoords="offset points",
                fontsize=8.6, color=NV, fontweight="bold", ha="right", va="center")
    a1.set_xlim(2015.5, 2028.6)
    a2.set_xlim(2015.5, 2029.3)
    a1.set_ylim(0, 4.0)
    a2.set_yscale("log")
    a2.set_ylim(5, 40000)
    a1.set_xlabel("Year (first product)")
    a2.set_xlabel("Year (first product)")
    a1.set_ylabel("Scale-up bandwidth per accelerator (TB/s)")
    a2.set_ylabel("Largest scale-up domain (accelerators, log scale)")
    a1.set_title("Bandwidth per accelerator", fontsize=11, color=INK["title"], loc="left")
    a2.set_title("Domain size", fontsize=11, color=INK["title"], loc="left")
    fig.text(0.988, 0.925, "RIGHT: LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))
    _margins(fig, left=0.06, right=0.985, wspace=0.22)
    c.save(fig, [a1, a2], legend=False, top=0.82)


# --------------------------------------------------------------------------------------
# 5. Who books the scale-up dollars: latest quarterly revenue by supplier
# --------------------------------------------------------------------------------------
@register
def scale_up_supplier_revenue():
    df = load(VALUE)
    pick = [
        ("NVIDIA", "networking_revenue_quarter", "Q2FY27", "NVIDIA networking\n(NVLink switches, IB, Ethernet, NICs)"),
        ("Amphenol", "ai_datacom_sales_quarter", "Q3 2026", "Amphenol AI-related\nIT datacom (cables, connectors)"),
        ("Credo", "revenue_quarter", "Q1FY27", "Credo total revenue\n(mostly AECs)"),
        ("Astera Labs", "revenue_quarter", "Q2 2026", "Astera Labs total revenue\n(retimers, fabric switches)"),
    ]
    rows = []
    for comp, metric, per, lab in pick:
        r = df[df.company.eq(comp) & df.metric.eq(metric) & df.period.eq(per)].iloc[0]
        rows.append(dict(label=f"{lab}\n{per}", company=comp, value=r.value_usd_b, conf=r.confidence,
                         source_id=r.source_id))
    d = pd.DataFrame(rows)
    nv = d.value.iloc[0]
    others = d.value.iloc[1:].sum()
    nv_hist = df[df.company.eq("NVIDIA")]
    c = Chart(
        id="05-scale-up-supplier-revenue",
        title=(f"NVIDIA's networking line books ~${nv:.1f}B a quarter, ~{nv / others:.0f}× the AI-connectivity sales "
               "of Amphenol, Credo and Astera combined"),
        subtitle="Latest reported quarterly revenue (US$ B); hatched = repo-derived estimate; scopes differ (see labels)",
        alt=(f"Horizontal bar chart of quarterly revenue: NVIDIA networking about ${nv:.1f}B in Q2 FY2027 (estimate from the "
             f"CFO's +18% q/q on $14.8B; growth in Q4 FY2026 was driven primarily by NVLink scale-up switches), Amphenol "
             f"AI-related IT datacom about ${d.value.iloc[1]:.1f}B in Q3 2026 (derived: 48% of $10.2B sales, three-quarters "
             f"AI), Credo ${d.value.iloc[2]:.2f}B (quarter to August 2026) and Astera Labs ${d.value.iloc[3]:.2f}B (Q2 2026, "
             f"guiding ~$0.55B for Q3). Together the three suppliers book about ${others:.1f}B, roughly a quarter of NVIDIA's networking."),
        data=[VALUE], chapters=["05", "06", "13"], source="company filings and earnings coverage (l05_value_chain.csv)",
        source_ids=sources_of(pd.concat([d, nv_hist])), note="Hatched = estimate",
    )
    fig, ax = c.figure(width=11, height=5.6)
    y = np.arange(len(d))[::-1]
    cols = [NV if cmp == "NVIDIA" else ("#B5B5B5" if cmp == "Amphenol" else "#7A7A7A") for cmp in d.company]
    bars = ax.barh(y, d.value, color=cols, height=0.62)
    hatch_future(bars, [cf == "estimate" for cf in d.conf])
    for b, v, cf in zip(bars, d.value, d.conf):
        ax.annotate(f"${v:.2f}B" if v < 1 else f"${v:.1f}B" + (" (Est.)" if cf == "estimate" else ""),
                    (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=9.5, color=INK["title"])
    ax.set_yticks(y, d.label, fontsize=9)
    ax.set_xlim(0, nv * 1.22)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"])
    _margins(fig, left=0.27, right=0.97)
    c.save(fig, ax, xlabel="Quarterly revenue (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 6. Deal values in scale-up interconnect
# --------------------------------------------------------------------------------------
TYPE_LABEL = {"acquisition": "Acquisition", "strategic-investment": "Strategic equity stake",
              "acquihire-license": "Acquihire + licence", "funding-round": "Start-up funding round"}
TYPE_HATCH = {"acquisition": "", "strategic-investment": "//", "acquihire-license": "..", "funding-round": "xx"}


@register
def scale_up_deal_values():
    df = load(DEALS).sort_values("value_usd_m")
    df["year"] = df.announce_date.astype(str).str[:4]

    def buyer_color(b: str) -> str:
        b = str(b)
        if b.startswith("NVIDIA"):
            return NV
        if b.startswith(("AMD", "Marvell", "Qualcomm")):
            return entity_color(b.split()[0])
        return "#7A7A7A"
    df["color"] = df.buyer_or_lead.map(buyer_color)
    mell = df[df.target.eq("Mellanox")].iloc[0]
    cel = df[df.target.eq("Celestial AI")].iloc[0]
    alpha = df[df.target.eq("Alphawave Semi")].iloc[0]
    c = Chart(
        id="05-scale-up-deal-values",
        title=(f"Mellanox (${mell.value_usd_m / 1000:.1f}B) is still the largest scale-up deal; 2025–26 money went to "
               f"optics (Celestial AI ${cel.value_usd_m / 1000:.2f}B) and SerDes (Alphawave ${alpha.value_usd_m / 1000:.1f}B)"),
        subtitle="Disclosed or reported deal value (US$ M) for interconnect-related acquisitions, stakes and rounds, 2019–2026; colour = buyer",
        alt=("Horizontal bar chart of interconnect-related deals: NVIDIA-Mellanox $6.9B (2019), NVIDIA's $5B Intel stake for NVLink "
             "x86 CPUs (2025), AMD-ZT Systems $4.9B (2024, rack design team), Marvell-Celestial AI $3.25B upfront (closed 2026), "
             "Qualcomm-Alphawave Semi $2.4B (2025), NVIDIA's $2B Marvell stake for NVLink Fusion (2026), NVIDIA-Enfabrica "
             "acquihire over $0.9B (2025), Ayar Labs $500M Series E (2026), Lightmatter $400M (2024), Upscale AI $200M "
             "Series A (2026), Marvell-XConn about $325M cash plus stock (2026) and Ayar Labs $155M (2024)."),
        data=[DEALS], chapters=["05", "13"], source="company releases and press (l05_deals.csv)",
        source_ids=sources_of(df), note="Hatch = deal type",
    )
    fig, ax = c.figure(width=11.5, height=6.6)
    y = np.arange(len(df))
    bars = ax.barh(y, df.value_usd_m, color=df.color, height=0.66, edgecolor="#FFFFFF")
    for b, t in zip(bars, df.deal_type):
        if TYPE_HATCH[t]:
            b.set_hatch(TYPE_HATCH[t])
            b.set_edgecolor("#FFFFFF")
    for b, r in zip(bars, df.itertuples()):
        v = r.value_usd_m
        txt = f"${v / 1000:.2f}B" if v >= 1000 else f"${v:,.0f}M"
        if r.value_basis.startswith("cash portion"):
            txt += " cash + stock"
        ax.annotate(txt, (b.get_width(), b.get_y() + b.get_height() / 2), xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK["title"])
    labels = [f"{r.target} ← {r.buyer_or_lead.replace(' (lead)', '')} ({r.year})" if r.deal_type != "funding-round"
              else f"{r.target} ({r.year})" for r in df.itertuples()]
    ax.set_yticks(y, labels, fontsize=8.8)
    ax.set_xlim(0, df.value_usd_m.max() * 1.18)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=INK["grid"])
    ent = [("NVIDIA", NV), ("AMD", entity_color("AMD")), ("Marvell", entity_color("Marvell")),
           ("Qualcomm", entity_color("Qualcomm")), ("Investors / start-up round", "#7A7A7A")]
    h1 = [Patch(facecolor=cl, label=nm) for nm, cl in ent]
    h2 = [Patch(facecolor="#FFFFFF", edgecolor=INK["text"], hatch=TYPE_HATCH[k], label=v) for k, v in TYPE_LABEL.items()]
    ax.legend(handles=h1 + h2, loc="lower right", fontsize=8.4, ncol=2, frameon=True)
    _margins(fig, left=0.30, right=0.97)
    c.save(fig, ax, xlabel="Deal value (US$ M)", legend=False)
