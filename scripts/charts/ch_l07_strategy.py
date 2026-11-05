"""Layer 07 (DPU, SuperNIC, storage, security) strategy charts: competitor heatmap, deal values,
NIC speed-tier arrival by vendor, NIC/DPU roadmap by vendor, NIC+DPU content per rack, and
private-company valuations.

Owner: layer-07 STRATEGY agent. Data: data/l07_competitor_verdicts.csv, l07_dpu_nic_deals.csv,
l07_speed_tier_arrival.csv, l07_nic_dpu_roadmap.csv, l07_rack_nic_dpu_content.csv,
l07_private_companies.csv (documented in data/README.md).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

from style import GEN_PAST, INK, NV, VERDICT_COLORS, Chart, entity_color, load, register, sources_of

VERD = "l07_competitor_verdicts.csv"
DEALS = "l07_dpu_nic_deals.csv"
TIERS = "l07_speed_tier_arrival.csv"
ROAD = "l07_nic_dpu_roadmap.csv"
RACK = "l07_rack_nic_dpu_content.csv"
PRIV = "l07_private_companies.csv"

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
    if v == "Mellanox":
        return GEN_PAST
    if v == "Amazon":
        return entity_color("aws")
    if v in ("EZchip", "Xsight Labs"):
        return entity_color("other")
    return entity_color(v)


def _ym(s: str) -> float:
    t = pd.Timestamp(str(s))
    return t.year + (t.month - 1) / 12.0


# --------------------------------------------------------------------------------------
# 1. Competitor capability heatmap (layer-specific)
# --------------------------------------------------------------------------------------
@register
def nic_dpu_competitor_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    bw = df[df.dimension.eq("Bandwidth per device")]
    bw_behind = int(bw.verdict_vs_nvidia.eq("behind").sum())
    n_diff = int(df.verdict_vs_nvidia.eq("different").sum())
    n_lead = int(df.verdict_vs_nvidia.eq("leads").sum())
    c = Chart(
        id="07-nic-dpu-competitor-heatmap",
        title=f"{bw_behind} of {len(comps)} rivals trail ConnectX-9's 1.6 Tb/s; the deepest challenge is captive offload",
        subtitle=("Repo verdict for each rival's best NIC/DPU vs NVIDIA's nearest equivalent (SuperNIC vs NIC, DPU vs DPU), "
                  "six dimensions; cell = verdict letter + key fact"),
        alt=(f"Heatmap of {len(comps)} NIC and DPU challengers against NVIDIA on six dimensions. {bw_behind} rivals trail on "
             "bandwidth per device (AWS Nitro v6 400G per card, AMD Vulcano and Broadcom Thor Ultra 800G, Intel IPU 200G vs "
             "ConnectX-9 at 1.6 Tb/s); AMD Pensando and Broadcom reach parity on AI-transport features via Ultra Ethernet; "
             f"Broadcom leads on openness and AWS Nitro leads on deployed scale ({n_lead} 'leads' cells in total); Google, "
             f"Microsoft and AWS are mostly 'different approach' because their offload silicon is captive ({n_diff} such cells)."),
        data=[VERD], chapters=["07", "15"], source="repo analysis of vendor specs (l07_competitor_verdicts.csv)",
        source_ids=sources_of(df), note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=12.5, height=7.4)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            label = str(r.cell_label)
            if len(label) > 19:
                cut = label.rfind(" ", 0, 19)
                label = label[:cut] + "\n" + label[cut + 1:]
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {label}", ha="center", va="center",
                    fontsize=8.1, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" / ", " /\n").replace(" per ", "\nper ").replace("-transport ", "-transport\n")
                        for d in dims], fontsize=9)
    ax.xaxis.tick_top()
    prod = df.drop_duplicates("competitor").set_index("competitor").product_basis
    ax.set_yticks(np.arange(len(comps)) + 0.5)
    ax.set_yticklabels([f"{cmp}\n{prod[cmp]}" for cmp in comps], fontsize=8.4)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.19, right=0.985)
    c.save(fig, ax, legend=False, top=0.80, bottom=0.08)


# --------------------------------------------------------------------------------------
# 2. What DPU / NIC teams have cost
# --------------------------------------------------------------------------------------
@register
def dpu_nic_deal_values():
    d = load(DEALS).copy()
    d["year"] = d.close_date.astype(str).str[:4]
    d["label"] = d.apply(lambda r: f"{r.target} ← {r.acquirer} ({r.year})", axis=1)
    d = d.iloc[::-1].reset_index(drop=True)  # newest at top
    mel = d[d.target.str.startswith("Mellanox")].value_usd_m.item()
    pen = d[d.target.str.startswith("Pensando")].value_usd_m.item()
    others = d[~d.target.str.startswith("Mellanox") & d.value_usd_m.notna()]
    lo, hi = others.value_usd_m.min(), others.value_usd_m.max()
    c = Chart(
        id="07-dpu-nic-deal-values",
        title=(f"DPU and NIC teams sold for ${lo/1000:.2f}B–${hi/1000:.1f}B; NVIDIA paid ${mel/1000:.1f}B for all of "
               f"Mellanox ({mel/pen:.1f}× Pensando)"),
        subtitle="Disclosed or reported deal value, US$ millions (log scale), NIC/DPU-related acquisitions 2014–2025, by close year",
        alt=(f"Log-scale horizontal bar chart of NIC and DPU deals: NVIDIA's ${mel:,.0f}M Mellanox acquisition (closed 2020), AMD's "
             f"${pen:,.0f}M Pensando purchase (2022), NVIDIA's reported >$900M Enfabrica team-and-licence deal (2025), Mellanox's "
             "$811M EZchip purchase (2016), Amazon's reported ~$370M Annapurna Labs deal (2015) that became Nitro, Microsoft's "
             "reported ~$190M Fungible purchase (2023) and EZchip's up-to-$130M Tilera deal (2014); NVIDIA's Excelero storage "
             "software buy (2022) was undisclosed."),
        data=[DEALS], chapters=["07", "13"], source="company releases, filings and press", source_ids=sources_of(d),
        note="Hatched = reported / up-to, not disclosed",
    )
    fig, ax = c.figure(width=10.8, height=5.9)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = _vcolor(r.acquirer)
        if pd.isna(r.value_usd_m):
            ax.text(55, yi, "undisclosed", va="center", fontsize=8.8, color=INK["muted"], style="italic")
            continue
        bar = ax.barh(yi, r.value_usd_m, color=col, height=0.62, left=0)
        if r.value_basis in ("reported", "up-to"):
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_alpha(0.8)
        txt = f"${r.value_usd_m/1000:.1f}B" if r.value_usd_m >= 1000 else f"~${r.value_usd_m:,.0f}M"
        if r.value_basis == "up-to":
            txt = f"up to ${r.value_usd_m:,.0f}M"
        if r.target.startswith("Enfabrica"):
            txt = f">${r.value_usd_m:,.0f}M"
        ax.text(r.value_usd_m * 1.12, yi, txt, va="center", fontsize=9, color=INK["title"])
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label)
    ax.set_ylim(-0.7, len(d) - 0.4)
    ax.set_xscale("log")
    ax.set_xlim(50, 30000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=GEN_PAST, label="Mellanox (now NVIDIA)"),
               Patch(color=entity_color("AMD"), label="AMD"), Patch(color=entity_color("aws"), label="Amazon"),
               Patch(color=entity_color("microsoft"), label="Microsoft"), Patch(color=entity_color("other"), label="EZchip")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.6)
    _margins(fig, left=0.33, right=0.97)
    c.save(fig, ax, xlabel="Deal value, US$ millions (log scale)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 3. When each vendor reached each NIC speed tier (gap-closing chart)
# --------------------------------------------------------------------------------------
TIER_VENDORS = ["NVIDIA", "AMD", "Broadcom", "AWS", "Xsight Labs", "Intel"]
TIER_LABEL = {"NVIDIA": "NVIDIA (ConnectX)", "AMD": "AMD (Pensando)", "Broadcom": "Broadcom (Thor)",
              "AWS": "AWS (Nitro, captive)", "Xsight Labs": "Xsight Labs (DPU)", "Intel": "Intel (IPU)"}


@register
def nic_speed_tier_arrival():
    d = load(TIERS)
    nv = d[d.vendor.eq("NVIDIA")].set_index("speed_tier_gbps").year
    riv = d[~d.vendor.eq("NVIDIA")].copy()
    riv["lag"] = riv.apply(lambda r: r.year - nv.get(r.speed_tier_gbps, np.nan), axis=1)
    lag400 = riv[riv.speed_tier_gbps.eq(400)].lag.min()
    lag800 = riv[riv.speed_tier_gbps.eq(800)].lag.max()
    n1600 = int(riv.speed_tier_gbps.eq(1600).sum())
    c = Chart(
        id="07-nic-speed-tier-arrival",
        title=(f"Rivals needed ~{lag400:.0f} years to match ConnectX at 400G but ≤{lag800:.0f} at 800G; "
               f"{'none' if n1600 == 0 else n1600} has a 1.6T NIC"),
        subtitle="Year each vendor's fastest NIC/DPU per device reached 200G, 400G, 800G and 1.6T (first volume or sampling); hollow = sampling",
        alt=("Dot chart of the year each vendor first offered a NIC or DPU at each per-device speed tier. NVIDIA ConnectX: 400G "
             "in 2022 (ConnectX-7), 800G in 2025 (ConnectX-8) and 1.6T in 2026 (ConnectX-9). AMD Pensando reached 400G in 2025 "
             "(Pollara) and 800G in 2026 (Vulcano); Broadcom's Thor Ultra sampled at 800G in 2025; AWS's captive Nitro v6 card "
             "reached 400G in 2025; Xsight Labs' E1 DPU 800G in 2026; Intel's IPU E2100 sits at 200G (2022). No rival has "
             "announced a 1.6T NIC as of 2026-11."),
        data=[TIERS], chapters=["07", "15", "17"], source="vendor announcements and AWS documentation",
        source_ids=sources_of(d), note="Hollow = sampling, not volume",
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    tiers = [200, 400, 800, 1600]
    offs = {v: (i - (len(TIER_VENDORS) - 1) / 2) * 0.11 for i, v in enumerate(TIER_VENDORS)}
    mk = {"NVIDIA": "o", "AMD": "D", "Broadcom": "s", "AWS": "P", "Xsight Labs": "v", "Intel": "^"}
    for v in TIER_VENDORS:
        s = d[d.vendor.eq(v)]
        col = entity_color(v) if v != "Xsight Labs" else entity_color("startups")
        for r in s.itertuples():
            yi = tiers.index(r.speed_tier_gbps) + offs[v]
            samp = r.status == "sampling"
            ax.scatter(r.year, yi, s=140 if v == "NVIDIA" else 110, marker=mk[v], facecolor="white" if samp else col,
                       edgecolor=col, linewidth=2.2, zorder=5 if v == "NVIDIA" else 3)
            ax.annotate(r.product.replace("Pensando ", "").replace(" SuperNIC", "").replace(" (per card)", ""),
                        (r.year, yi), xytext=(9, 0), textcoords="offset points", va="center", fontsize=8.2,
                        color=INK["title"], fontweight="bold" if v == "NVIDIA" else "normal")
        ax.scatter([], [], s=90, marker=mk[v], color=col, label=TIER_LABEL[v])
    for t in (400, 800):
        y0 = tiers.index(t)
        lag = riv[riv.speed_tier_gbps.eq(t)].lag
        ax.annotate(f"rivals +{lag.min():.0f} to +{lag.max():.0f} yr", (nv[t], y0 - 0.38), fontsize=8.4,
                    color=INK["text"], style="italic", ha="left")
    ax.annotate("no rival 1.6T NIC announced", (2026.15, 3 - 0.36), fontsize=8.4, color=INK["text"], style="italic")
    ax.set_yticks(range(len(tiers)), ["200G", "400G", "800G", "1.6T"])
    ax.set_ylim(-0.6, 3.6)
    ax.set_xlim(2021.5, 2027.6)
    ax.set_xticks(range(2022, 2028))
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper left", fontsize=8.4, ncol=2)
    c.save(fig, ax, xlabel="Year of first volume (or sampling)", ylabel="Per-device NIC/DPU speed tier", legend=False)


# --------------------------------------------------------------------------------------
# 4. NIC / DPU roadmap by vendor, 2024–2028
# --------------------------------------------------------------------------------------
LANES = [("NVIDIA", "supernic", "NVIDIA SuperNIC"), ("NVIDIA", "dpu", "NVIDIA DPU"),
         ("AMD", None, "AMD Pensando"), ("Broadcom", None, "Broadcom"), ("AWS", None, "AWS Nitro"),
         ("Microsoft", None, "Microsoft"), ("Intel", None, "Intel IPU"), ("Xsight Labs", None, "Xsight Labs")]
SHORTP = {"BlueField-3 DPU": "BlueField-3", "ConnectX-8 SuperNIC": "CX-8", "ConnectX-9 SuperNIC": "CX-9",
          "BlueField-4 DPU": "BlueField-4", "ConnectX-10 SuperNIC": "CX-10", "BlueField-5 DPU": "BlueField-5",
          "Pollara 400 AI NIC": "Pollara", "Salina 400 DPU": "Salina", "Vulcano 800 AI NIC": "Vulcano",
          "Como / Monza (Helios 500)": "Como/Monza", "Palma / Levanzo (Helios 600)": "Palma/Levanzo",
          "Thor Ultra 800G NIC": "Thor Ultra", "Nitro v6": "Nitro v6", "Azure Boost DPU": "Azure Boost DPU",
          "IPU E2100": "E2100", "E1 DPU": "E1"}


@register
def nic_dpu_roadmap_by_vendor():
    d = load(ROAD)
    d["t"] = d.date.map(_ym)
    named_2028 = d[d.date.str.startswith("2028")].vendor.unique().tolist()
    c = Chart(
        id="07-nic-dpu-roadmap-by-vendor",
        title=(f"Only {' and '.join(named_2028)} name NIC/DPU parts for 2028; NVIDIA's 1.6T ConnectX-9 is a speed step "
               "ahead of 800G rivals"),
        subtitle="NIC, SuperNIC and DPU availability by vendor, 2024–2028; label = product · Gb/s per device; hollow = announced, sampling or roadmap",
        alt=("Timeline chart of NIC and DPU products 2024-2028 by vendor lane. NVIDIA: BlueField-3 (400G), ConnectX-8 (800G, "
             "2025), ConnectX-9 (1.6T, 2026), BlueField-4 (800G, 2026), ConnectX-10 and BlueField-5 (2028, no specs). AMD: "
             "Pollara and Salina (400G, 2025), Vulcano (800G, 2026), Como/Monza (2027) and Palma/Levanzo (2028), names only. "
             "Broadcom Thor Ultra (800G, sampling 2025), AWS Nitro v6 (400G per card), Microsoft Azure Boost DPU (2025), "
             "Intel IPU E2100 (200G) and Xsight Labs E1 (800G) have no disclosed successors."),
        data=[ROAD], chapters=["07", "17"], source="vendor announcements and press", source_ids=sources_of(d),
        note="Month positions approximate",
    )
    fig, ax = c.figure(width=11.5, height=6.2)
    for i, (vendor, cat, lab) in enumerate(LANES):
        s = d[d.vendor.eq(vendor)]
        if cat == "supernic":
            s = s[s.category.eq("supernic")]
        elif cat == "dpu":
            s = s[~s.category.eq("supernic")]
        col = entity_color(vendor) if vendor != "Xsight Labs" else entity_color("startups")
        ax.axhline(i, color=INK["grid"], lw=0.8, zorder=0)
        for k, r in enumerate(s.sort_values("t").itertuples()):
            future = r.status != "shipping"
            ax.scatter(r.t, i, s=150 if vendor == "NVIDIA" else 120, marker="o", facecolor="white" if future else col,
                       edgecolor=col, linewidth=2.2, zorder=4, hatch="////" if r.status == "roadmap" else None)
            bwl = f"{r.bandwidth_gbps/1000:.1f}T" if pd.notna(r.bandwidth_gbps) and r.bandwidth_gbps >= 1000 else (
                f"{r.bandwidth_gbps:.0f}G" if pd.notna(r.bandwidth_gbps) else "spec n/d")
            lab_txt = f"{SHORTP.get(r.product, r.product)} · {bwl}"
            dy = 12 if k % 2 == 0 else -13
            ax.annotate(lab_txt, (r.t, i), xytext=(0, dy), textcoords="offset points", ha="center", va="center",
                        fontsize=8.1, color=INK["title"], fontweight="bold" if vendor == "NVIDIA" else "normal")
    ax.axvline(_ym("2026-11"), color=INK["text"], lw=1, ls=":")
    ax.text(_ym("2026-11") + 0.04, len(LANES) - 0.45, "as of\n2026-11", fontsize=8, color=INK["text"], va="top")
    ax.set_yticks(range(len(LANES)), [lab for _, _, lab in LANES])
    ax.set_ylim(len(LANES) - 0.4, -0.7)
    ax.set_xlim(2023.7, 2029.0)
    ax.set_xticks(range(2024, 2029))
    ax.grid(False)
    ax.scatter([], [], s=110, color=INK["text"], label="shipping")
    ax.scatter([], [], s=110, facecolor="white", edgecolor=INK["text"], linewidth=2, label="announced / sampling")
    ax.scatter([], [], s=110, facecolor="white", edgecolor=INK["text"], linewidth=2, hatch="////", label="roadmap (no specs)")
    ax.legend(loc="lower left", fontsize=8.6, ncol=3)
    _margins(fig, left=0.14, right=0.98)
    c.save(fig, ax, xlabel="Availability (calendar year)", legend=False)


# --------------------------------------------------------------------------------------
# 5. Estimated SuperNIC + DPU content per NVL72 rack
# --------------------------------------------------------------------------------------
@register
def nic_dpu_content_per_rack():
    d = load(RACK).copy()
    d["lo"] = d.units_low * d.unit_price_low_usd / 1e3
    d["hi"] = d.units_high * d.unit_price_high_usd / 1e3
    d["mid"] = (d.lo + d.hi) / 2
    racks = list(dict.fromkeys(d.rack))
    tot = d.groupby("rack", sort=False).agg(lo=("lo", "sum"), hi=("hi", "sum"), mid=("mid", "sum"),
                                            price=("rack_price_usd_m", "first")).reindex(racks)
    tot["pct_lo"] = tot.lo / (tot.price * 1e3) * 100
    tot["pct_hi"] = tot.hi / (tot.price * 1e3) * 100
    vr = tot.loc["Vera Rubin NVL72"]
    c = Chart(
        id="07-nic-dpu-content-per-rack",
        title=(f"Est.: SuperNICs and DPUs add ~${tot.lo.min():.0f}K–${tot.hi.max():.0f}K per NVL72 rack, only "
               f"~{tot.pct_lo.min():.0f}–{tot.pct_hi.max():.0f}% of rack price"),
        subtitle=("Estimated NIC + DPU silicon per rack, US$ thousands (bar = midpoint, whisker = low–high case); "
                  "72 SuperNICs per rack (1 per GPU) and 18–36 DPUs"),
        alt=(f"Stacked bar chart of estimated SuperNIC and DPU content per NVL72 rack: GB200 about ${tot.lo.iloc[0]:.0f}K-"
             f"${tot.hi.iloc[0]:.0f}K ({tot.pct_lo.iloc[0]:.1f}-{tot.pct_hi.iloc[0]:.1f}% of a ~$3.0M rack), GB300 "
             f"${tot.lo.iloc[1]:.0f}K-${tot.hi.iloc[1]:.0f}K ({tot.pct_lo.iloc[1]:.1f}-{tot.pct_hi.iloc[1]:.1f}% of ~$3.99M) and "
             f"Vera Rubin ${vr.lo:.0f}K-${vr.hi:.0f}K ({vr.pct_lo:.1f}-{vr.pct_hi:.1f}% of ~$7.8M). Unit prices are repo "
             "assumptions anchored on BlueField-3 retail listings of $1.9K-$6.0K; NIC count is one per GPU."),
        data=[RACK], chapters=["07", "08", "14"], source="repo estimate; rack prices HSBC and Morgan Stanley; retail listings",
        source_ids=sources_of(d), note="Est. (repo, speculative): hatched",
    )
    fig, ax = c.figure(width=10.2, height=5.8)
    x = np.arange(len(racks))
    nic = d[d.component.str.contains("ConnectX")].set_index("rack").reindex(racks)
    dpu = d[d.component.str.contains("BlueField")].set_index("rack").reindex(racks)
    b1 = ax.bar(x, nic.mid.values, 0.55, color=NV, label="SuperNICs (ConnectX-7 → 8 → 9)")
    b2 = ax.bar(x, dpu.mid.values, 0.55, bottom=nic.mid.values, color=GEN_PAST, label="DPUs (BlueField-3 → 4)")
    for b in list(b1) + list(b2):
        b.set_hatch("//")
    ax.errorbar(x, tot.mid.values, yerr=[tot.mid - tot.lo, tot.hi - tot.mid], fmt="none", ecolor=INK["title"],
                capsize=6, lw=1.4)
    for xi, r in zip(x, tot.itertuples()):
        ax.annotate(f"${r.lo:.0f}K–${r.hi:.0f}K\n{r.pct_lo:.1f}–{r.pct_hi:.1f}% of ~${r.price:.2g}M rack",
                    (xi, r.hi), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8.8, color=INK["title"])
    ax.set_xticks(x, racks)
    ax.set_ylim(0, max(tot.hi) * 1.35)
    ax.legend(loc="upper left", fontsize=9)
    c.save(fig, ax, ylabel="US$ thousands per rack (Est.)", legend=False)


# --------------------------------------------------------------------------------------
# 6. Private-company marks and exit prices around the data path
# --------------------------------------------------------------------------------------
@register
def ai_storage_and_dpu_valuations():
    d = load(PRIV).copy()
    priv = d[d.status.eq("private")].sort_values("date").groupby("company").tail(1)
    exits = d[d.status.eq("acquired")]
    first_vast = d[(d.company == "VAST Data")].sort_values("date").iloc[0]
    v = priv.set_index("company").valuation_usd_m
    show = pd.concat([priv.sort_values("valuation_usd_m", ascending=False), exits.sort_values("valuation_usd_m", ascending=False)])
    c = Chart(
        id="07-ai-storage-and-dpu-valuations",
        title=(f"VAST Data's ${v['VAST Data']/1000:.0f}B mark is ~{v['VAST Data']/v['DDN']:.0f}× DDN's and "
               f"~{v['VAST Data']/v['WEKA']:.0f}× WEKA's; DPU startups exited for $0.2–1.9B"),
        subtitle="Last disclosed post-money valuation (private) or exit price (acquired), US$ millions (log scale); year of the mark in label",
        alt=(f"Log-scale horizontal bar chart: VAST Data valued at ${v['VAST Data']:,.0f}M (2026, up from "
             f"${first_vast.valuation_usd_m:,.0f}M in 2023), DDN ${v['DDN']:,.0f}M (2025), Xsight Labs ${v['Xsight Labs']:,.0f}M "
             f"(2026), WEKA ${v['WEKA']:,.0f}M (2024) and Hammerspace more than ${v['Hammerspace']:,.0f}M (2025); for comparison, "
             "DPU and NIC start-ups were bought for $1,900M (Pensando by AMD), >$900M (Enfabrica team by NVIDIA) and ~$190M "
             "(Fungible by Microsoft)."),
        data=[PRIV], chapters=["07", "13"], source="company releases and press", source_ids=sources_of(d),
        note="Marks are from different dates; hatched = exit price",
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    show = show.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(show))
    for yi, r in zip(y, show.itertuples()):
        exited = r.status == "acquired"
        col = entity_color("other") if not exited else INK["base"]
        if r.company in ("Xsight Labs", "Pensando Systems", "Enfabrica", "Fungible"):
            col = entity_color("startups") if not exited else "#B5B5B5"
        if r.company in ("VAST Data", "DDN", "WEKA", "Hammerspace"):
            col = "#256ABF"
        bar = ax.barh(yi, r.valuation_usd_m, color=col, height=0.62)
        if exited:
            bar.patches[0].set_hatch("///")
        pre = ">" if str(r.valuation_basis).startswith(("floor", "exit price (>")) else ("~" if "reported" in str(r.valuation_basis) else "")
        txt = f"{pre}${r.valuation_usd_m/1000:.1f}B" if r.valuation_usd_m >= 1000 else f"{pre}${r.valuation_usd_m:,.0f}M"
        ax.text(r.valuation_usd_m * 1.1, yi, txt, va="center", fontsize=9, color=INK["title"])
    vy = int(np.where(show.company.eq("VAST Data"))[0][0])
    ax.scatter([first_vast.valuation_usd_m], [vy], marker="|", s=300, color=INK["title"], zorder=4)
    ax.annotate(f"2023: ${first_vast.valuation_usd_m/1000:.1f}B", (first_vast.valuation_usd_m, vy), xytext=(0, 13),
                textcoords="offset points", ha="center", fontsize=8.2, color=INK["title"])
    labels = [f"{r.company} ({str(r.date)[:4]})" + (f"\n→ {r.lead_or_buyer}" if r.status == "acquired" else "")
              for r in show.itertuples()]
    ax.set_yticks(y, labels)
    ax.set_xscale("log")
    ax.set_xlim(100, 80000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color="#256ABF", label="AI storage / data platforms (private)"),
               Patch(color=entity_color("startups"), label="DPU / network silicon (private)"),
               Patch(facecolor="#B5B5B5", hatch="///", label="DPU / NIC exits (acquired)")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.6)
    _margins(fig, left=0.22, right=0.97)
    c.save(fig, ax, xlabel="US$ millions (log scale)", logx=True, legend=False)
