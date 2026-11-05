"""Scale-out networking, NIC/DPU and optics charts (layers 06 and 07), owned by agent A2.

Data: data/networking_products.csv, data/interconnect_specs.csv,
      data/network_topology_estimates.csv and data/optics_power_estimates.csv (all owned by A2).
Shared helpers (log axis with plain ticks, status legend, fixed axes) are imported from ch_interconnect,
which run_all.py imports first (alphabetical order).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

import style
from ch_interconnect import fixed_axes, log_axis, status_handles
from style import Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, hatch_future, load, register, sources_of

NP_FILE = "networking_products.csv"
IC_FILE = "interconnect_specs.csv"
TOPO_FILE = "network_topology_estimates.csv"
POWER_FILE = "optics_power_estimates.csv"
OTHER_DARK = "#7A7A7A"      # darker neutral for vendors outside the palette (e.g. Cisco) so marks stay legible


def _np() -> pd.DataFrame:
    return load(NP_FILE)


def _pick(df: pd.DataFrame, products: list[str]) -> pd.DataFrame:
    out = []
    for p in products:
        m = df[df["product"] == p]
        if m.empty:
            raise KeyError(p)
        out.append(m.iloc[0])
    return pd.DataFrame(out).reset_index(drop=True)


# ---------------------------------------------------------------------------------------------- 06-switch-aggregate-bandwidth
SWITCH_SERIES = [
    ("Broadcom Tomahawk", "Broadcom", "o", ["Tomahawk (BCM56960)", "Tomahawk 2", "Tomahawk 3", "Tomahawk 4", "Tomahawk 5", "Tomahawk 6"]),
    ("NVIDIA Spectrum (Ethernet)", "NVIDIA", "o", ["Spectrum (SN2700)", "Spectrum-2 (SN3700)", "Spectrum-3 (SN4700)", "Spectrum-4 (SN5600)",
                                                   "Spectrum-6 / Spectrum-X Photonics SN6810"]),
    ("NVIDIA Quantum (InfiniBand)", "NVIDIA", "s", ["Switch-IB (SB7700/SB7800)", "Quantum (QM8700)", "Quantum-2 (QM9700)", "Quantum-X800 (Q3400)"]),
    ("Cisco Silicon One", "Cisco", "D", ["Silicon One G100", "Silicon One G200", "Silicon One G300"]),
    ("Marvell Teralynx", "Marvell", "^", ["Teralynx 7", "Teralynx 10"]),
]


def _vendor_color(v: str) -> str:
    return OTHER_DARK if v == "Cisco" else entity_color(v)


@register
def switch_aggregate_bandwidth():
    df = _np()
    parts = {name: _pick(df, prods) for name, _, _, prods in SWITCH_SERIES}
    th = parts["Broadcom Tomahawk"]
    a, b = th.iloc[0], th.iloc[-1]
    mult = b.aggregate_tbps / a.aggregate_tbps
    dbl = (b.year - a.year) / math.log2(mult)
    sp6 = parts["NVIDIA Spectrum (Ethernet)"].iloc[-1]
    used = pd.concat(parts.values())
    c = Chart(
        id="06-switch-aggregate-bandwidth",
        title=(f"Switch ASIC bandwidth doubled every ~{dbl:.1f} years: {a.aggregate_tbps:.1f} Tb/s ({int(a.year)}) to "
               f"{b.aggregate_tbps:.1f} Tb/s ({int(b.year)}) at Broadcom"),
        subtitle=(f"Switching capacity per switch (ports × port speed, one direction), Tb/s. NVIDIA's Spectrum-6 reaches "
                  f"{sp6.aggregate_tbps:.1f} Tb/s in {int(sp6.year)}"),
        alt=(f"Log-scale line chart of switch capacity by year: Broadcom Tomahawk from {a.aggregate_tbps:.1f} Tb/s ({int(a.year)}) to "
             f"{b.aggregate_tbps:.1f} Tb/s (Tomahawk 6, {int(b.year)}), doubling about every {dbl:.1f} years; NVIDIA Spectrum Ethernet from "
             f"3.2 Tb/s (2015) to 51.2 Tb/s (Spectrum-4) and {sp6.aggregate_tbps:.1f} Tb/s (Spectrum-6, {int(sp6.year)}); NVIDIA Quantum InfiniBand "
             f"from 3.6 to 115.2 Tb/s (Quantum-X800 system); Cisco Silicon One and Marvell Teralynx track the same cadence."),
        data=[NP_FILE], chapters=["06", "16"],
        source="Broadcom, NVIDIA, Cisco, Marvell announcements", source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=12.2, height=6.4)
    for name, vendor, mk, _ in SWITCH_SERIES:
        d = parts[name]
        col = _vendor_color(vendor)
        firm = d[d.confidence != "speculative"]
        ax.plot(firm.year, firm.aggregate_tbps, color=col, marker=mk, ms=8, lw=2, label=name,
                ls="-" if "Quantum" not in name else (0, (4, 2)))
        spec = d[d.confidence == "speculative"]
        if not spec.empty:
            ax.plot([firm.year.iloc[-1], spec.year.iloc[0]], [firm.aggregate_tbps.iloc[-1], spec.aggregate_tbps.iloc[0]],
                    color=col, lw=1.4, ls=":")
            ax.plot(spec.year, spec.aggregate_tbps, ls="none", marker=mk, ms=9, mfc="white", mec=col, mew=2)
        fut = d[d.status == "announced"]
        if not fut.empty:
            ax.plot(fut.year, fut.aggregate_tbps, ls="none", marker=mk, ms=9, mfc="white", mec=col, mew=2)
    lab = {"Tomahawk 6": ("TH6 102.4", (-8, 6)), "Tomahawk (BCM56960)": ("TH1 3.2", (-6, 6)),
           "Spectrum-6 / Spectrum-X Photonics SN6810": ("Spectrum-6 102.4 (CPO)", (10, 6)),
           "Quantum-X800 (Q3400)": ("Quantum-X800 115.2\n(144-port system)", (-8, 8)),
           "Silicon One G300": ("Cisco G300 (unverified)", (10, -10)), "Teralynx 10": ("51.2 Tb/s class (2022-23):\nTH5, Spectrum-4, G200, Teralynx 10", (10, -26))}
    for _, r in used.iterrows():
        if r["product"] in lab:
            t, off = lab[r["product"]]
            col = INK["text"] if r["product"] == "Teralynx 10" else (_vendor_color(r.vendor) if r.vendor != "NVIDIA" else NV_DARK)
            ax.annotate(t, (r.year, r.aggregate_tbps), xytext=off, textcoords="offset points", fontsize=8,
                        ha="right" if off[0] < 0 else "left", color=col)
    ax.set_xlim(2013, 2028)
    ax.set_ylim(2, 300)
    log_axis(fig, ax)
    ax.legend(loc="upper left")
    ax.text(0.99, 0.02, "Hollow = announced or unverified; Quantum dashed = InfiniBand switch systems",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=8, color=INK["muted"])
    c.save(fig, ax, xlabel="Year of launch / first availability", ylabel="Tb/s per switch (log scale)", legend=False)


# ---------------------------------------------------------------------------------------------- 06-serdes-lane-rate-progression
@register
def serdes_lane_rate_progression():
    df = _np()
    sw = df[df.category.isin(["ethernet-switch", "infiniband-switch", "cpo-switch", "nvlink-switch"])
            & df.serdes_gbps.notna() & (df.vendor != "Google") & (df.confidence != "speculative")
            & ~df["product"].str.contains("Spectrum-X \\(|Spectrum-XGS|tray|Arista|7060|7800", regex=True)].copy()
    sw = sw.sort_values("year")
    years = np.arange(int(sw.year.min()), int(sw.year.max()) + 1)
    frontier = [sw[sw.year <= y].serdes_gbps.max() for y in years]
    first = {rate: int(sw[sw.serdes_gbps >= rate].year.min()) for rate in (25, 50, 100, 200)}
    yrs = first[200] - first[25]
    dbl = yrs / math.log2(200 / 25)
    ic = load(IC_FILE)
    nxt = ic[(ic.confidence == "speculative") & ic.family.isin(["InfiniBand", "Ethernet"])]
    c = Chart(
        id="06-serdes-lane-rate-progression",
        title=(f"Switch SerDes lane rates doubled about every {dbl:.1f} years: 25 Gb/s ({first[25]}) to 200 Gb/s ({first[200]})"),
        subtitle="Electrical lane (SerDes) rate per switch ASIC, Gb/s per lane per direction; line = fastest shipping lane rate to date",
        alt=(f"Scatter and step chart of switch SerDes lane rates by launch year: 25 Gb/s NRZ first in {first[25]}, 50 Gb/s PAM4 in "
             f"{first[50]}, 100 Gb/s PAM4 in {first[100]} and 200 Gb/s PAM4 in {first[200]} (NVIDIA Quantum-X800, then Broadcom Tomahawk 6), "
             f"a doubling roughly every {dbl:.1f} years; 400 Gb/s lanes for 3.2T Ethernet and 1.6T InfiniBand are not yet scheduled."),
        data=[NP_FILE, IC_FILE], chapters=["06", "P3"],
        source="Broadcom, NVIDIA, Cisco, Marvell; IBTA; IEEE", source_ids=sources_of(pd.concat([sw, nxt])),
    )
    fig, ax = c.figure(width=11.8, height=6.2)
    ax.step(years, frontier, where="post", color=INK["base"], lw=6, alpha=0.55, zorder=1, label="Fastest lane rate shipping")
    rng = np.random.default_rng(7)
    for vendor, grp in sw.groupby("vendor"):
        col = _vendor_color(vendor)
        for cat, mk in [("ethernet-switch", "o"), ("cpo-switch", "o"), ("infiniband-switch", "s"), ("nvlink-switch", "^")]:
            g = grp[grp.category == cat]
            if g.empty:
                continue
            jitter = rng.uniform(-0.12, 0.12, len(g))
            lbl = {"ethernet-switch": f"{vendor} Ethernet", "cpo-switch": None, "infiniband-switch": f"{vendor} InfiniBand",
                   "nvlink-switch": f"{vendor} NVLink switch"}[cat]
            ax.plot(g.year + jitter, g.serdes_gbps * np.exp(jitter * 0.3), ls="none", marker=mk, ms=8, color=col,
                    mec="white", mew=0.8, label=lbl, zorder=3)
    for rate, y in first.items():
        enc = "NRZ" if rate <= 25 else "PAM4"
        ax.annotate(f"{rate}G {enc}\nfirst {y}", (y, rate), xytext=(-10, 10), textcoords="offset points", ha="right",
                    fontsize=8.4, color=INK["text"])
    ax.annotate("Next: 400G lanes (3.2T Ethernet,\n1.6T IB GDR) - not yet scheduled", (2027.5, 400), ha="center", va="center",
                fontsize=8.4, color=INK["muted"], bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=INK["grid"], ls="--"))
    ax.set_xlim(2012.5, 2029.5)
    ax.set_xticks(range(2013, 2030, 2))
    ax.set_ylim(8, 900)
    log_axis(fig, ax)
    h, l = ax.get_legend_handles_labels()
    keep = [(hh, ll) for hh, ll in zip(h, l) if ll and not ll.startswith("_")]
    ax.legend([k[0] for k in keep], [k[1] for k in keep], loc="upper left", fontsize=8.4, ncol=2)
    c.save(fig, ax, xlabel="Year of launch / first availability", ylabel="SerDes lane rate, Gb/s (log scale)", legend=False)


# ---------------------------------------------------------------------------------------------- 07-nic-bandwidth-by-generation
CX = ["ConnectX-3", "ConnectX-4", "ConnectX-5", "ConnectX-6", "ConnectX-7", "ConnectX-8 SuperNIC", "ConnectX-9 SuperNIC"]
BF = ["BlueField", "BlueField-2", "BlueField-3 DPU", "BlueField-4"]
RIVALS = [("Thor Ultra", "Broadcom", "o", "Broadcom Thor Ultra NIC"), ("Pensando Pollara 400", "AMD", "o", "AMD Pensando Pollara 400 NIC"),
          ("Pensando Vulcano", "AMD", "D", "AMD Pensando Vulcano NIC"), ("Pensando Salina 400", "AMD", "s", "AMD Pensando Salina DPU"),
          ("IPU E2100 (Mount Evans)", "Intel", "s", "Intel IPU E2100")]


@register
def nic_bandwidth_by_generation():
    df = _np()
    cx, bf = _pick(df, CX), _pick(df, BF)
    rv = _pick(df, [r[0] for r in RIVALS])
    a, b = cx.iloc[0], cx.iloc[-1]
    mult = b.port_speed_gbps / a.port_speed_gbps
    dbl = (b.year - a.year) / math.log2(mult)
    c = Chart(
        id="07-nic-bandwidth-by-generation",
        title=(f"ConnectX bandwidth rose {mult:.0f}× from {a.port_speed_gbps:.0f} Gb/s ({int(a.year)}) to "
               f"{b.port_speed_gbps / 1000:.1f} Tb/s ({int(b.year)}), doubling about every {dbl:.0f} years"),
        subtitle="Maximum port bandwidth per NIC / DPU, Gb/s per direction, by launch year; rivals' AI NICs and DPUs shown as markers",
        alt=(f"Log-scale chart of NIC bandwidth by year: NVIDIA ConnectX from {a.port_speed_gbps:.0f} Gb/s (ConnectX-3, {int(a.year)}) through 100 "
             f"(ConnectX-4/5), 200 (ConnectX-6), 400 (ConnectX-7), 800 (ConnectX-8) to {b.port_speed_gbps:,.0f} Gb/s (ConnectX-9, {int(b.year)}); "
             f"BlueField DPUs from 100 to 800 Gb/s (BlueField-4); Broadcom Thor Ultra and AMD Vulcano reach 800 Gb/s in 2025-26, "
             f"Intel IPU E2100 200 Gb/s."),
        data=[NP_FILE], chapters=["07", "06"],
        source="NVIDIA/Mellanox, Broadcom, AMD, Intel", source_ids=sources_of(pd.concat([cx, bf, rv])),
    )
    fig, ax = c.figure(width=11.8, height=6.2)
    ax.plot(cx.year, cx.port_speed_gbps, color=NV, marker="o", ms=8, lw=2.4, label="NVIDIA ConnectX (NIC / SuperNIC)", zorder=4)
    for _, r in cx.iterrows():
        ax.annotate(r["product"].replace(" SuperNIC", "").replace("ConnectX-", "CX-"), (r.year, r.port_speed_gbps),
                    xytext=(-6, 7), textcoords="offset points", ha="right", fontsize=8.3, color=NV_DARK)
    bf_ok, bf_f = bf[bf.status != "announced"], bf[bf.status == "announced"]
    ax.plot(bf_ok.year, bf_ok.port_speed_gbps, color=GEN_PAST, marker="s", ms=8, lw=2, label="NVIDIA BlueField DPU", zorder=3)
    ax.plot([bf_ok.year.iloc[-1], bf_f.year.iloc[0]], [bf_ok.port_speed_gbps.iloc[-1], bf_f.port_speed_gbps.iloc[0]],
            color=GEN_PAST, lw=1.6, ls="--")
    ax.plot(bf_f.year, bf_f.port_speed_gbps, ls="none", marker="s", ms=9, mfc="white", mec=NV, mew=2, label="Announced")
    for _, r in bf.iterrows():
        ax.annotate(r["product"].replace(" DPU", "").replace("BlueField", "BF"), (r.year, r.port_speed_gbps), xytext=(6, -12),
                    textcoords="offset points", ha="left", fontsize=8.3, color=INK["text"])
    for prod, vendor, mk, name in RIVALS:
        r = rv[rv["product"] == prod].iloc[0]
        dx = {"Pensando Salina 400": 0.16, "Pensando Pollara 400": -0.16, "Pensando Vulcano": 0.18, "Thor Ultra": 0.0}.get(prod, 0)
        ax.plot(r.year + dx, r.port_speed_gbps, ls="none", marker=mk, ms=9, color=entity_color(vendor), mec="white", mew=0.8,
                zorder=5, label=f"{name} ({int(r.year)})")
    ax.set_xlim(2010, 2028)
    ax.set_ylim(30, 4000)
    log_axis(fig, ax)
    ax.legend(loc="upper left", fontsize=8.4)
    c.save(fig, ax, xlabel="Year of launch / first availability", ylabel="Gb/s per direction (log scale)", legend=False)


# ---------------------------------------------------------------------------------------------- 06-cpo-vs-pluggable-power
@register
def cpo_vs_pluggable_power():
    pw = load(POWER_FILE)
    topo = load(TOPO_FILE)
    order = ["Pluggable DSP (800G)", "Pluggable DSP (1.6T)", "Linear pluggable (LPO, 800G)",
             "CPO (NVIDIA Photonics, 1.6T port)", "CPO (Broadcom Bailly / TH6-Davisson, 800G-eq.)"]
    d = pw.set_index("technology").loc[order].reset_index()
    plug, cpo_nv = d.iloc[1], d.iloc[3]
    seg = topo[(topo.scenario == "800G per GPU, 3-tier") & topo.metric.isin(
        ["optics_nic_side", "optics_leaf_downlink", "optics_leaf_spine", "optics_spine_core"])]
    nic_mods = seg[seg.metric == "optics_nic_side"].value.sum()
    sw_mods = seg[seg.metric != "optics_nic_side"].value.sum()
    nic_w = d[d.technology == "Pluggable DSP (800G)"].watts_per_port.iloc[0]
    per_gpu_plug = nic_mods * nic_w + sw_mods * plug.watts_per_port
    per_gpu_cpo = nic_mods * nic_w + sw_mods * cpo_nv.watts_per_port
    mw_saved = (per_gpu_plug - per_gpu_cpo) * 100_000 / 1e6
    lo_cpo = d[d.technology.str.startswith("CPO")].pj_per_bit.min()
    hi_cpo = d[d.technology.str.startswith("CPO")].pj_per_bit.max()
    c = Chart(
        id="06-cpo-vs-pluggable-power",
        title=(f"Co-packaged optics cut optics power from ~{plug.pj_per_bit:.0f} to ~{lo_cpo:.0f}–{hi_cpo:.0f} pJ/bit: "
               f"~{per_gpu_plug:.0f} W → ~{per_gpu_cpo:.0f} W of optics per GPU"),
        subtitle="Left: optical I/O energy, pJ/bit (label: W per 800 Gb/s). Right: Est. optics watts per GPU, non-blocking 3-tier 800G fabric",
        alt=(f"Two-panel bar chart. Left: DSP pluggable optics about {plug.pj_per_bit:.0f} pJ/bit (~{plug.watts_per_800g:.0f} W per 800G; "
             f"NVIDIA cites ~30 W per 1.6T module), linear pluggables about {d.iloc[2].pj_per_bit:.0f} pJ/bit, co-packaged optics "
             f"{lo_cpo:.1f}-{hi_cpo:.1f} pJ/bit derived from NVIDIA's 3.5x and Broadcom's ~70% savings claims. Right: in a 3-tier 800G fat tree "
             f"optics draw about {per_gpu_plug:.0f} W per GPU with pluggables vs {per_gpu_cpo:.0f} W with CPO switches, roughly "
             f"{mw_saved:.1f} MW saved per 100,000 GPUs (estimate)."),
        data=[POWER_FILE, TOPO_FILE], chapters=["06", "08"],
        source="NVIDIA (GTC 2025 keynote, photonics release), Broadcom, LPO MSA; repo estimates",
        source_ids=sources_of(pd.concat([d, seg])),
    )
    fig, ax = fixed_axes(c, 12.5, 6.0, (0.255, 0.13, 0.43, 0.70))
    ax2 = fig.add_axes((0.775, 0.13, 0.195, 0.70))
    labels = ["DSP pluggable 800G (typical)", "DSP pluggable 1.6T (NVIDIA: ~30 W)", "Linear pluggable 800G (LPO)",
              "CPO: NVIDIA Photonics (3.5× claim)", "CPO: Broadcom (~70% claim)"]
    y = np.arange(len(d))[::-1]
    cols = [INK["text"], INK["text"], OTHER_DARK, NV, entity_color("Broadcom")]
    bars = ax.barh(y, d.pj_per_bit, color=cols, height=0.62)
    hatch_future(bars, d.confidence.eq("estimate").to_numpy())
    for b, (_, r) in zip(bars, d.iterrows()):
        ax.annotate(f"{r.pj_per_bit:.1f} pJ/bit · {r.watts_per_800g:.1f} W per 800G", (r.pj_per_bit, b.get_y() + b.get_height() / 2),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=8.4, color=INK["text"])
    ax.set_yticks(y, labels, fontsize=8.8)
    ax.set_xlim(0, 40)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("pJ per bit (optical I/O)")
    ax.legend(handles=status_handles("Vendor figure", "Est. / derived from vendor claim"), loc="lower right")
    b2 = ax2.bar([0, 1], [per_gpu_plug, per_gpu_cpo], color=[INK["text"], NV], width=0.6)
    hatch_future(b2, [True, True])
    for bb, v in zip(b2, [per_gpu_plug, per_gpu_cpo]):
        ax2.annotate(f"~{v:.0f} W", (bb.get_x() + bb.get_width() / 2, v), xytext=(0, 3), textcoords="offset points",
                     ha="center", fontsize=10, fontweight="bold", color=INK["title"])
    ax2.set_xticks([0, 1], ["All pluggable\n(1 × 800G + 2.5 × 1.6T)", "CPO switches\n(NIC module only)"], fontsize=8.6)
    ax2.set_ylim(0, per_gpu_plug * 1.25)
    ax2.set_ylabel("Optics W per GPU (Est.)")
    ax2.text(0.5, 0.93, f"≈ {mw_saved:.1f} MW less per 100k GPUs", transform=ax2.transAxes, ha="center", fontsize=9,
             color=NV_DARK, fontweight="bold")
    c.save(fig, [ax, ax2], legend=False)


# ---------------------------------------------------------------------------------------------- 06-optics-per-gpu
SEGMENTS = [("optics_nic_side", "NIC-side module", style.SEQ_BLUE[7]),
            ("optics_leaf_downlink", "Leaf, GPU-facing (twin-port)", style.SEQ_BLUE[5]),
            ("optics_leaf_spine", "Leaf ↔ spine, both ends", style.SEQ_BLUE[3]),
            ("optics_spine_core", "Spine ↔ core, both ends", style.SEQ_BLUE[1])]


@register
def optics_per_gpu():
    topo = load(TOPO_FILE)
    scen = ["400G per GPU, 2-tier", "400G per GPU, 3-tier", "800G per GPU, 2-tier", "800G per GPU, 3-tier"]
    t = topo[topo.scenario.isin(scen)]
    piv = t.pivot_table(index="scenario", columns="metric", values="value", aggfunc="first").reindex(scen).fillna(0)
    two, three = piv.loc["800G per GPU, 2-tier"], piv.loc["800G per GPU, 3-tier"]
    c = Chart(
        id="06-optics-per-gpu",
        title=(f"Est.: each GPU needs {two.optics_total_pluggable:.1f} pluggable optics (2 tiers) or "
               f"{three.optics_total_pluggable:.1f} (3 tiers); CPO switches cut that to {three.optics_total_cpo_switches:.0f}"),
        subtitle="Estimated optical modules per GPU, non-blocking rail-optimized fat tree (back-end fabric only), by NIC speed and tiers",
        alt=(f"Stacked bar chart (estimates): with all-optical links a GPU needs {two.optics_total_pluggable:.1f} pluggable modules in a "
             f"two-tier fat tree and {three.optics_total_pluggable:.1f} in three tiers (one NIC-side module, half a twin-port leaf module, "
             f"one module per upper tier), the same count at 400G and 800G; counted as optical port-ends it is {two.optical_port_ends:.0f} and "
             f"{three.optical_port_ends:.0f}, matching NVIDIA's '6 transceivers per GPU'; co-packaged-optics switches leave only the NIC-side "
             f"module, 1 per GPU."),
        data=[TOPO_FILE], chapters=["06", "08"],
        source="repo estimate (method in data/network_topology_estimates.csv); NVIDIA; SemiAnalysis", source_ids=sources_of(t),
    )
    fig, ax = c.figure(width=12.5, height=6.3)
    groups = np.arange(len(scen)) * 2.6
    w = 0.9
    for gi, s in zip(groups, scen):
        bottom = 0.0
        for m, lab, col in SEGMENTS:
            v = piv.loc[s, m]
            if v:
                ax.bar(gi, v, w, bottom=bottom, color=col, label=lab if gi == groups[0] or (m == "optics_spine_core" and "3-tier" in s and gi == groups[1]) else None,
                       edgecolor="white", lw=0.8)
                bottom += v
        ax.annotate(f"{bottom:.1f}", (gi, bottom), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10,
                    fontweight="bold", color=INK["title"])
        ax.annotate(f"{piv.loc[s, 'optical_port_ends']:.0f} optical\nport-ends", (gi, bottom), xytext=(0, 18),
                    textcoords="offset points", ha="center", fontsize=7.8, color=INK["muted"])
        cp = piv.loc[s, "optics_total_cpo_switches"]
        b = ax.bar(gi + w + 0.05, cp, w, color=style.SEQ_BLUE[7], edgecolor="white", lw=0.8)
        hatch_future(b, [True])
        ax.annotate(f"{cp:.0f}", (gi + w + 0.05, cp), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10,
                    fontweight="bold", color=INK["title"])
    ax.bar(0, 0, 0, color=style.SEQ_BLUE[7], hatch="///", edgecolor="white", label="With CPO switches (NIC module only)")
    mods = {"400G": "400G NIC module +\n800G (2×400G) switch modules", "800G": "800G NIC module +\n1.6T (2×800G) switch modules"}
    ax.set_xticks(groups + (w + 0.05) / 2, [f"{s[:4]} NIC · {s[-6:].replace('-tier', ' tiers')}\n{mods[s[:4]]}" for s in scen], fontsize=8.4)
    ax.set_ylim(0, 5.3)
    ax.set_ylabel("Optical modules per GPU (Est.)")
    h, l = ax.get_legend_handles_labels()
    ax.legend(h, l, loc="upper left", fontsize=8.6)
    ax.text(0.99, 0.985, "Assumes every link is optical (end-of-row leaves). Port-ends = 2 per link per tier,\n"
            "i.e. the module count if every module were single-port. Front-end/storage networks excluded.",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=INK["muted"])
    c.save(fig, ax, legend=False, bottom=0.18)


# ---------------------------------------------------------------------------------------------- 06-switches-for-100k-gpu-cluster
@register
def switches_for_100k_gpu_cluster():
    topo = load(TOPO_FILE)
    t = topo[topo.cluster_gpus == 100_000]
    scen = list(dict.fromkeys(t.scenario))
    piv = t.pivot_table(index="scenario", columns="metric", values="value", aggfunc="first").reindex(scen)
    three = piv[[("3-tier" in s) for s in scen]]
    twot = piv[[("2-tier" in s) for s in scen]].iloc[0]
    fewer_optics = 1 - twot.transceivers_total / three.transceivers_total.max()
    c = Chart(
        id="06-switches-for-100k-gpu-cluster",
        title=(f"Est.: 100k GPUs need ~{round(three.switches_total.min(), -2):,.0f}–{round(three.switches_total.max(), -2):,.0f} "
               f"switches in 3 tiers, or ~{round(twot.switches_total / 50) * 50:,.0f} in a 2-tier multi-plane fabric"),
        subtitle="Estimated back-end switches by tier for 100,000 GPUs (one NIC per GPU, 1:1 fat tree), with optical modules and worst-case hops",
        alt=(f"Stacked horizontal bar chart (estimates) of switches needed for 100,000 GPUs: 3-tier designs need "
             f"{three.switches_total.min():,.0f} to {three.switches_total.max():,.0f} switches and about {three.transceivers_total.max() / 1000:.0f}k "
             f"optical modules with 5 switch hops worst case; a 4-plane 2-tier design on 512-port 102.4T switches needs "
             f"{twot.switches_total:,.0f} switches, {twot.transceivers_total / 1000:.0f}k modules ({fewer_optics:.0%} fewer) and 3 hops."),
        data=[TOPO_FILE], chapters=["06", "08", "CS7"],
        source="repo estimate (method in data/network_topology_estimates.csv); Broadcom; NVIDIA; SemiAnalysis", source_ids=sources_of(t),
    )
    fig, ax = fixed_axes(c, 12.5, 6.2, (0.27, 0.13, 0.62, 0.70))
    y = np.arange(len(scen))[::-1]
    left = np.zeros(len(scen))
    for m, lab, col in [("switches_leaf", "Leaf", style.SEQ_BLUE[7]), ("switches_spine", "Spine", style.SEQ_BLUE[4]),
                        ("switches_core", "Core", style.SEQ_BLUE[1])]:
        vals = piv[m].to_numpy()
        ax.barh(y, vals, left=left, color=col, height=0.6, label=lab, edgecolor="white", lw=0.8)
        for yi, l0, v in zip(y, left, vals):
            if v > 250:
                ax.annotate(f"{v:,.0f}", (l0 + v / 2, yi), ha="center", va="center", fontsize=8.4,
                            color="white" if col != style.SEQ_BLUE[1] else INK["title"])
        left += vals
    for yi, (s, r) in zip(y, piv.iterrows()):
        ax.annotate(f"{r.switches_total:,.0f} switches\n{r.transceivers_total / 1000:,.0f}k optics · {int(r.switch_hops_max)} hops",
                    (r.switches_total, yi), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.6, color=INK["title"])
    names = [s.replace("100k GPUs: ", "").replace(", 3-tier", "\n3 tiers").replace(", 2-tier", "\n2 tiers per plane") for s in scen]
    ax.set_yticks(y, names, fontsize=8.8)
    ax.set_xlim(0, 5200)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", ncol=3)
    c.save(fig, ax, xlabel="Switches (Est.)", legend=False)


# ---------------------------------------------------------------------------------------------- 06-fat-tree-max-gpus-by-radix
@register
def fat_tree_max_gpus_by_radix():
    topo = load(TOPO_FILE)
    t = topo[topo.metric == "max_gpus_nonblocking"].copy()
    radii = sorted(t.switch_radix_ports.unique())
    two = t[t.tiers == 2].set_index("switch_radix_ports").value
    three = t[t.tiers == 3].set_index("switch_radix_ports").value
    names = t.drop_duplicates("switch_radix_ports").set_index("switch_radix_ports").switch_example
    c = Chart(
        id="06-fat-tree-max-gpus-by-radix",
        title=(f"Two network tiers reach {two[64]:,.0f} GPUs with 64-port switches but {two[512]:,.0f} with "
               f"512-port 102.4T switches"),
        subtitle="Maximum GPUs (one NIC port each) in a non-blocking fat tree: 2 tiers = R²/2, 3 tiers = R³/4, for switch radix R",
        alt=(f"Grouped log-scale bar chart: a two-tier non-blocking fat tree supports {two[40]:,.0f} GPUs with 40-port HDR switches, "
             f"{two[64]:,.0f} with 64-port Quantum-2, {two[128]:,.0f} with 128-port 51.2T, {two[144]:,.0f} with 144-port Quantum-X800 and "
             f"{two[512]:,.0f} with 512-port 102.4T switches; three tiers reach {three[64]:,.0f}, {three[128]:,.0f} and {three[144]:,.0f}; "
             f"a 100,000-GPU cluster therefore needs three tiers unless switches have 512-port radix (or multiple planes)."),
        data=[TOPO_FILE], chapters=["06", "P4"],
        source="repo calculation; NVIDIA and Broadcom switch specs", source_ids=sources_of(t),
    )
    fig, ax = fixed_axes(c, 12.5, 6.4, (0.10, 0.18, 0.87, 0.65))
    x = np.arange(len(radii))
    w = 0.38
    b2 = ax.bar(x - w / 2, [two[r] for r in radii], w, color=style.SEQ_BLUE[4], label="2-tier (leaf-spine)")
    b3 = ax.bar(x + w / 2, [three[r] for r in radii], w, color=style.SEQ_BLUE[7], label="3-tier (leaf-spine-core)")
    for bars in (b2, b3):
        for b in bars:
            v = b.get_height()
            ax.annotate(f"{v:,.0f}" if v < 1e6 else f"{v / 1e6:.0f}M", (b.get_x() + b.get_width() / 2, v), xytext=(0, 2),
                        textcoords="offset points", ha="center", fontsize=8.4, color=INK["text"])
    ax.axhline(100_000, color=NV, lw=1.6, ls="--")
    ax.annotate("100,000-GPU cluster", (x[0] - 0.45, 100_000), xytext=(0, 4), textcoords="offset points", ha="left",
                fontsize=8.8, color=NV_DARK, fontweight="bold")
    short = {40: "Quantum (HDR)\n40 × 200G", 64: "Quantum-2 (NDR)\n64 × 400G", 128: "51.2T switch\n128 × 400G",
             144: "Quantum-X800\n144 × 800G", 512: "102.4T switch\n512 × 200G"}
    ax.set_xticks(x, [f"R = {int(r)}\n{short.get(int(r), names[r])}" for r in radii], fontsize=8.6)
    ax.set_ylim(300, 3e8)
    log_axis(fig, ax)
    ax.legend(loc="upper left")
    c.save(fig, ax, ylabel="Max GPUs, non-blocking (log scale)", legend=False)
