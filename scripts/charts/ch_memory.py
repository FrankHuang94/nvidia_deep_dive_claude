"""Memory, packaging and supply chain (chapter 03) - agent A3.

Reads data/hbm_and_packaging.csv (long), data/tco_model_inputs.csv and data/system_specs.csv.
CoWoS figures are press-reported analyst estimates and are always hatched.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, SEQ_BLUE, entity_color, hatch_future, load,
                   register, sources_of)

HBM = "hbm_and_packaging.csv"
TCO = "tco_model_inputs.csv"
SYS = "system_specs.csv"
SUPPLIER_COLORS = {"SK hynix": "#104281", "Samsung": "#3987E5", "Micron": "#9EC5F4"}


def _h() -> pd.DataFrame:
    return load(HBM)


def _val(df, **kw) -> pd.Series:
    d = df
    for k, v in kw.items():
        d = d[d[k] == v]
    if d.empty:
        raise KeyError(kw)
    return d.iloc[0]


# --------------------------------------------------------------------------------------
@register
def hbm_stack_bandwidth_by_generation():
    h = _h()
    g = h[h.record_type == "hbm_generation"]
    gens = [("HBM", "HBM\n2013", "JEDEC"), ("HBM2", "HBM2\n2016", "JEDEC"), ("HBM2E", "HBM2E\n2020", "SK hynix"),
            ("HBM3", "HBM3\n2022", "JEDEC"), ("HBM3E 12-high", "HBM3E\n2024", "Samsung"),
            ("HBM4", "HBM4\nJEDEC 2025", "JEDEC"), ("HBM4", "HBM4 SK hynix\n2025 (>10 Gb/s)", "SK hynix")]
    rows, pins, widths = [], [], []
    for item, _, sup in gens:
        rows.append(_val(g, item=item, metric="stack_bandwidth", supplier=sup))
        p = g[(g.item == item) & (g.metric == "pin_speed") & (g.supplier == sup)]
        pins.append(p.value.iloc[0] if len(p) else np.nan)
        base = item.split(" ")[0]
        w = g[(g.item.str.split(" ").str[0] == base) & (g.metric == "interface_width")]
        widths.append(w.value.iloc[0] if len(w) else np.nan)
    d = pd.DataFrame(rows).reset_index(drop=True)
    d["label"] = [f"{lab}\n{p:g} Gb/s × {w:,.0f}" for (_, lab, _), p, w in zip(gens, pins, widths)]
    # as-shipped per-stack bandwidth in NVIDIA GPUs (bandwidth / stacks)
    pg = h[h.record_type == "hbm_per_gpu"]
    ship = [("NVIDIA P100", 1, "P100"), ("NVIDIA V100", 1, "V100"), ("NVIDIA A100 80GB", 2, "A100 80GB"),
            ("NVIDIA H100 SXM", 3, "H100"), ("NVIDIA H200", 4, "H200"), ("NVIDIA B200", 4, "B200/B300"),
            ("NVIDIA Rubin", 5, "Rubin")]
    pts = []
    for gpu, xi, lab in ship:
        bw = _val(pg, item=gpu, metric="bandwidth")
        st = _val(pg, item=gpu, metric="stacks")
        pts.append((xi, bw.value * 1000 / st.value, lab, bw, st))
    used = pd.concat([d, pd.DataFrame([p[3] for p in pts]), pd.DataFrame([p[4] for p in pts])])
    first, jedec4 = d.iloc[0], d.iloc[5]
    mult = jedec4.value / first.value
    rubin = pts[-1][1]
    c = Chart(
        id="03-hbm-stack-bandwidth-by-generation",
        title=f"Per-stack HBM bandwidth rose {mult:.0f}× from HBM ({first.value:.0f} GB/s) to JEDEC HBM4 ({jedec4.value:,.0f} GB/s)",
        subtitle="Peak GB/s per HBM stack (bars; axis label = pin speed × interface bits) · ◆ = as run in NVIDIA GPUs (GPU GB/s ÷ stacks)",
        alt=(f"Bar chart of peak bandwidth per HBM stack: HBM {first.value:.0f} GB/s (2013), HBM2 256, HBM2E 460, HBM3 819, HBM3E "
             f"about 1,280, JEDEC HBM4 {jedec4.value:,.0f} and SK hynix HBM4 at over 10 Gb/s about 2,560 GB/s, a {mult:.0f}-fold rise. "
             f"Diamonds show NVIDIA's as-shipped rates per stack, from about 183 GB/s on P100 to about {rubin:,.0f} GB/s on Rubin; "
             f"HBM4 doubled the interface from 1,024 to 2,048 bits."),
        data=[HBM], chapters=["03", "02", "17"],
        source="JEDEC, Micron, Samsung, SK hynix, NVIDIA",
        source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    x = np.arange(len(d))
    cols = [SEQ_BLUE[i] for i in (1, 2, 3, 4, 5, 6, 7)]
    b = ax.bar(x, d.value, color=cols, width=0.62, zorder=2)
    hatch_future(b, [conf == "estimate" for conf in d.confidence])
    for i, (v, p, w) in enumerate(zip(d.value, pins, widths)):
        ax.annotate(f"{v:,.0f}", (i, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9.2, color=INK["title"], fontweight="bold")
    for xi, v, lab, _, _ in pts:
        off = {"P100": -0.16, "V100": 0.16, "H200": -0.16, "B200/B300": 0.16}.get(lab, 0)
        left = lab in ("P100", "H200")
        ax.scatter(xi + off, v, marker="D", s=46, color=NV, edgecolor="white", linewidth=0.8, zorder=4)
        ax.annotate(lab, (xi + off, v), xytext=(-7 if left else 7, 0), textcoords="offset points", va="center",
                    ha="right" if left else "left", fontsize=8, color=NV_DARK, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85), zorder=5)
    ax.set_xticks(x, d.label, fontsize=8.4)
    ax.set_ylim(0, d.value.max() * 1.13)
    ax.legend(handles=[Patch(facecolor=SEQ_BLUE[5], label="Peak per stack (spec / fastest vendor bin)"),
                       Patch(facecolor=SEQ_BLUE[7], hatch="///", edgecolor="white", label="Repo calc from vendor pin speed"),
                       plt_marker()], loc="upper left", frameon=False, fontsize=8.8)
    c.save(fig, ax, ylabel="GB/s per stack", legend=False, bottom=0.15)


def plt_marker():
    from matplotlib.lines import Line2D
    return Line2D([0], [0], marker="D", color="white", markerfacecolor=NV, markersize=7,
                  label="As run in an NVIDIA GPU")


# --------------------------------------------------------------------------------------
@register
def hbm_stack_capacity_by_generation():
    h = _h()
    g = h[h.record_type == "hbm_generation"]
    gens = [("HBM", "HBM\n2013"), ("HBM2", "HBM2\n2016"), ("HBM2E", "HBM2E\n2020"), ("HBM3", "HBM3\n2022"),
            ("HBM3E 12-high", "HBM3E\n12-high 2024"), ("HBM3E 16-high", "HBM3E\n16-high 2025"),
            ("HBM4 (Rubin implementation)", "HBM4\nin Rubin 2026"), ("HBM4E", "HBM4E\nRubin Ultra 2027")]
    rows, heights = [], []
    for item, _ in gens:
        r = g[(g.item == item) & (g.metric == "max_stack_capacity")].iloc[0]
        rows.append(r)
        hh = g[(g.item == item) & (g.metric == "max_stack_height")]
        heights.append(hh.value.iloc[0] if len(hh) else np.nan)
    d = pd.DataFrame(rows).reset_index(drop=True)
    d["label"] = [f"{lab}\n{hh:.0f}-high" for (_, lab), hh in zip(gens, heights)]
    jed = g[g.metric == "jedec_max_stack_capacity"]
    first = d.iloc[0]
    ship_max = d[d.item == "HBM3E 12-high"].value.iloc[0]
    e = d[d.item == "HBM4E"].iloc[0]
    c = Chart(
        id="03-hbm-stack-capacity-by-generation",
        title=f"HBM stack capacity rose {ship_max / first.value:.0f}× in a decade, from {first.value:.0f} GB to {ship_max:.0f} GB; HBM4E targets {e.value:.0f} GB",
        subtitle="Largest stack per generation, GB (axis label = DRAM dies per stack) · hollow ○ = JEDEC maximum · hatched = sampling or roadmap",
        alt=(f"Bar chart of maximum HBM capacity per stack: HBM {first.value:.0f} GB (4-high), HBM2 8 GB, HBM2E 16 GB, HBM3 24 GB, "
             f"12-high HBM3E {ship_max:.0f} GB, 16-high HBM3E 48 GB (sampling), HBM4 as used in Rubin 36 GB and HBM4E planned for "
             f"Rubin Ultra about {e.value:.0f} GB per stack (1 TB in 16 stacks); JEDEC's HBM3 and HBM4 standards allow up to 64 GB."),
        data=[HBM], chapters=["03", "02"],
        source="JEDEC, SK hynix, Samsung, NVIDIA roadmap",
        source_ids=sources_of(pd.concat([d, jed])),
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    x = np.arange(len(d))
    cols = [SEQ_BLUE[i] for i in (1, 2, 3, 4, 5, 5, 6, 7)]
    b = ax.bar(x, d.value, color=cols, width=0.62, zorder=2)
    hatch_future(b, [it in ("HBM3E 16-high", "HBM4E") for it in d.item])
    for i, (v, hh) in enumerate(zip(d.value, heights)):
        ax.annotate(f"{v:.0f} GB", (i, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9.2, color=INK["title"], fontweight="bold")
    for _, r in jed.iterrows():
        xi = 3 if r["item"] == "HBM3" else 6
        ax.scatter(xi, r.value, s=70, facecolors="white", edgecolors=INK["text"], linewidths=1.4, zorder=4)
        ax.annotate(f"JEDEC max {r.value:.0f} GB", (xi, r.value), xytext=(-8, 0), textcoords="offset points",
                    va="center", ha="right", fontsize=8, color=INK["text"])
    ax.set_xticks(x, d.label, fontsize=8.4)
    ax.set_ylim(0, 72)
    c.save(fig, ax, ylabel="GB per stack", legend=False, bottom=0.15)


# --------------------------------------------------------------------------------------
@register
def hbm_market_share_by_supplier():
    h = _h()
    m = h[(h.record_type == "hbm_market_share") & (h.supplier.notna()) & (h.supplier != "")]
    periods = ["2022", "2023", "2025-Q1", "2025-Q2", "2025-Q3"]
    labels = ["2022", "2023 (Est.)", "Q1 2025", "Q2 2025", "Q3 2025"]
    sups = ["SK hynix", "Samsung", "Micron"]
    q3 = m[m.period == "2025-Q3"].set_index("supplier").value
    lo = m[m.supplier == "SK hynix"].value.min()
    hi = m[m.supplier == "SK hynix"].value.max()
    c = Chart(
        id="03-hbm-market-share-by-supplier",
        title=f"SK hynix held {lo:.0f}–{hi:.0f}% of HBM revenue in 2022–25; Samsung, Micron ~{q3['Micron']:.0f}–{q3['Samsung']:.0f}% each",
        subtitle="Share of HBM revenue by supplier, % (TrendForce for 2022–2023; Counterpoint for 2025 quarters) · hatched = estimate",
        alt=(f"Stacked 100% bar chart of HBM revenue share: 2022 SK hynix 50%, Samsung 40%, Micron 10%; 2023 estimate 53/38/9; "
             f"Q1 2025 SK hynix about 70%; Q2 2025 SK hynix 62%, Micron 21%, Samsung 17%; Q3 2025 SK hynix {q3['SK hynix']:.0f}%, "
             f"Samsung {q3['Samsung']:.0f}%, Micron {q3['Micron']:.0f}%."),
        data=[HBM], chapters=["03", "18"],
        source="TrendForce, Counterpoint Research",
        source_ids=sources_of(m),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(len(periods))
    bottom = np.zeros(len(periods))
    for s in sups:
        vals = []
        for p in periods:
            r = m[(m.period == p) & (m.supplier == s)]
            vals.append(r.value.iloc[0] if len(r) else np.nan)
        vals = np.array(vals, dtype=float)
        v0 = np.nan_to_num(vals)
        b = ax.bar(x, v0, bottom=bottom, color=SUPPLIER_COLORS[s], width=0.6, label=s, zorder=2,
                   edgecolor="white", linewidth=0.8)
        hatch_future(b, [p == "2023" for p in periods])
        for xi, v, bt in zip(x, vals, bottom):
            if v == v and v > 0:
                ax.text(xi, bt + v / 2, f"{s}\n{v:.0f}%" if v >= 14 else f"{v:.0f}%", ha="center", va="center",
                        fontsize=8.6, color="white" if s != "Micron" else INK["title"], fontweight="bold")
        bottom += v0
    # Q1 2025: only SK hynix split published
    q1 = periods.index("2025-Q1")
    rest = 100 - bottom[q1]
    ax.bar(q1, rest, bottom=bottom[q1], color=INK["grid"], width=0.6, zorder=2, edgecolor="white")
    ax.text(q1, bottom[q1] + rest / 2, "Samsung +\nMicron\n(split n/a)", ha="center", va="center", fontsize=8,
            color=INK["text"])
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    c.save(fig, ax, ylabel="Share of HBM revenue", legend=False)


# --------------------------------------------------------------------------------------
@register
def cowos_capacity_and_nvidia_share():
    h = _h()
    cap = h[(h.record_type == "cowos_capacity") & (h.metric == "capacity")].sort_values("period")
    al = h[(h.record_type == "cowos_allocation") & (h.metric == "wafers")]
    nv_share = _val(h, record_type="cowos_allocation", metric="share")
    total = al[al.item.str.endswith("total")].value.iloc[0]
    custs = al[~al.item.str.endswith("total")].copy()
    custs["cust"] = custs.item.str.split(": ").str[1]
    other = total - custs.value.sum()
    mult = cap.value.iloc[-1] / cap.value.iloc[0]
    c = Chart(
        id="03-cowos-capacity-and-nvidia-share",
        title=f"Est.: TSMC CoWoS capacity grew ~{mult:.0f}× from 2023 to 2026, and NVIDIA booked ~{nv_share.value:.0f}% of 2026 wafers",
        subtitle="Left: year-end CoWoS run-rate, k wafers/month (midpoint of press-reported ranges) · Right: 2026 CoWoS bookings by customer, k wafers",
        alt=(f"Two-panel chart of estimates. Left: TSMC CoWoS capacity about {cap.value.iloc[0]:.0f}k wafers per month at end-2023, "
             f"{cap.value.iloc[1]:.0f}k in 2024, {cap.value.iloc[2]:.0f}k in 2025 and about {cap.value.iloc[3]:.0f}k in 2026, roughly "
             f"{mult:.0f} times higher. Right: of about {total:,.0f}k wafers of 2026 CoWoS demand, NVIDIA about 595k "
             f"({nv_share.value:.0f}%), Broadcom 150k, AMD 105k and others about {other:.0f}k."),
        data=[HBM], chapters=["03", "13", "18"],
        source="TrendForce, Morgan Stanley via trade press, TSMC",
        source_ids=sources_of(pd.concat([cap, al])),
        note="All values Est. (TSMC does not disclose CoWoS wafers)",
    )
    fig, axes = c.figure_grid(1, 2, width=11.5, height=6.0, gridspec_kw=dict(width_ratios=[1.15, 1]))
    ax = axes[0]
    x = np.arange(len(cap))
    b = ax.bar(x, cap.value, color=[SEQ_BLUE[3], SEQ_BLUE[4], SEQ_BLUE[5], SEQ_BLUE[7]], width=0.6, zorder=2)
    hatch_future(b, [True] * len(cap))
    rng = cap.notes.str.extract(r"\(([\d\-]+k) wafers")[0].tolist()
    for i, (v, r) in enumerate(zip(cap.value, rng)):
        ax.annotate(f"~{v:.0f}k\n({r})", (i, v), xytext=(0, 3), textcoords="offset points", ha="center",
                    va="bottom", fontsize=8.8, color=INK["title"])
    ax.set_xticks(x, [f"End-{p}" for p in cap.period])
    ax.set_ylim(0, cap.value.max() * 1.25)
    ax.set_ylabel("k wafers per month (Est.)")
    ax.set_title("TSMC CoWoS capacity", fontsize=10.5, color=INK["title"], loc="left")
    ax2 = axes[1]
    parts = [("NVIDIA", float(custs[custs.cust == "NVIDIA"].value.iloc[0]), NV),
             ("Broadcom", float(custs[custs.cust == "Broadcom"].value.iloc[0]), entity_color("Broadcom")),
             ("AMD", float(custs[custs.cust == "AMD"].value.iloc[0]), entity_color("AMD")),
             ("Others", float(other), entity_color("other"))]
    left = 0.0
    for name, v, col in parts:
        bb = ax2.barh([0], [v], left=left, color=col, height=0.5, zorder=2, edgecolor="white")
        hatch_future(bb, [True])
        big = v >= 200
        ax2.text(left + v / 2, 0, f"{name}\n{v:.0f}k\n{v / total * 100:.0f}%" if big else f"{v:.0f}k\n{v / total * 100:.0f}%",
                 ha="center", va="center", fontsize=9 if big else 8.2,
                 color="white" if name != "Others" else INK["title"], fontweight="bold")
        if not big:
            ax2.text(left + v / 2, 0.29, name, ha="center", va="bottom", fontsize=8.6, color=INK["title"],
                     fontweight="bold")
        left += v
    ax2.set_xlim(0, total)
    ax2.set_ylim(-0.6, 0.6)
    ax2.set_yticks([])
    ax2.set_xlabel("k wafers booked for 2026 (Est.)")
    ax2.set_title(f"2026 CoWoS bookings (~{total / 1000:.1f}M wafers)", fontsize=10.5, color=INK["title"], loc="left")
    ax2.grid(axis="y", visible=False)
    ax2.grid(axis="x", color=INK["grid"], lw=0.7)
    ax2.tick_params(length=0)
    c.save(fig, list(axes), legend=False)


# --------------------------------------------------------------------------------------
def _tco_row(t, system, inp, basis=None):
    r = t[(t.system == system) & (t.input == inp)]
    if basis:
        r = r[r.basis.str.contains(basis, regex=False)]
    return r.iloc[0]


@register
def supply_chain_value_sankey():
    import plotly.graph_objects as go
    t = load(TCO)
    h = _h()
    s = load(SYS)
    S = "GB300 NVL72"
    price = _tco_row(t, S, "capex_per_rack", "Morgan Stanley")
    gpu = _tco_row(t, S, "bom_gpu")
    mem = _tco_row(t, S, "bom_memory")
    cool = _tco_row(t, S, "bom_cooling")
    odm_pct = _tco_row(t, S, "odm_gross_margin_pct")
    ngpu = _tco_row(t, S, "accelerators_per_rack")
    logic = _tco_row(t, "HGX B200", "bom_logic_dies")
    cowos = _tco_row(t, "HGX B200", "bom_cowos_l")
    oth = _tco_row(t, "HGX B200", "bom_other")
    sa_rack = _tco_row(t, "GB200 NVL72", "capex_per_rack", "SemiAnalysis")
    sa_all = _tco_row(t, "GB200 NVL72", "capex_per_rack_all_in")
    hbm_px = _val(h, record_type="hbm_pricing", item="HBM3E contract price")
    hbm_tb = s[s.system == S].iloc[0]
    n = ngpu.value
    v_logic = n * logic.value / 1e6
    v_cowos = n * cowos.value / 1e6
    v_oth = n * oth.value / 1e6
    v_nv = gpu.value - v_logic - v_cowos - v_oth
    v_hbm = hbm_tb.total_hbm_tb * 1000 * hbm_px.value / 1e6
    v_lp = mem.value - v_hbm
    v_odm = price.value * odm_pct.value / 100
    v_other = price.value - gpu.value - mem.value - cool.value - v_odm
    v_net = sa_all.value - sa_rack.value
    total = price.value + v_net
    used = pd.concat([pd.DataFrame([price, gpu, mem, cool, odm_pct, ngpu, logic, cowos, oth, sa_rack, sa_all]),
                      pd.DataFrame([hbm_px]), s[s.system == S]])
    c = Chart(
        id="03-supply-chain-value-sankey",
        title=f"Est.: of ~${total:.1f}M spent on a GB300 NVL72 rack + network, NVIDIA keeps ~${v_nv:.1f}M as GPU gross profit",
        subtitle=(f"Where the dollars go, US$ M · rack price ${price.value:.2f}M (Morgan Stanley, May 2026) + ~${v_net:.1f}M scale-out "
                  "network/storage (SemiAnalysis GB200 basis) · GPU cost on Epoch AI B200 basis"),
        alt=(f"Sankey diagram of estimated value flows for a GB300 NVL72 rack plus its share of network: of about ${total:.1f}M, "
             f"NVIDIA GPU gross profit about ${v_nv:.2f}M, TSMC logic wafers about ${v_logic:.2f}M and CoWoS-L packaging about "
             f"${v_cowos:.2f}M, HBM makers about ${v_hbm:.2f}M, LPDDR5X about ${v_lp:.2f}M, other rack content about "
             f"${v_other:.2f}M, liquid cooling ${cool.value:.2f}M, ODM margin about ${v_odm:.2f}M and scale-out networking "
             f"and storage about ${v_net:.1f}M."),
        data=[TCO, HBM, SYS], chapters=["03", "08", "13", "14"],
        source="Morgan Stanley, SemiAnalysis, Epoch AI (repo calc)",
        source_ids=sources_of(used),
    )
    nodes = [
        f"Hyperscaler spend<br>${total:.2f}M",                                   # 0
        f"GB300 NVL72 rack<br>(ODM price) ${price.value:.2f}M",                  # 1
        f"Scale-out network<br>& storage ${v_net:.2f}M",                         # 2
        f"72 B300 GPU modules<br>${gpu.value:.2f}M",                             # 3
        f"Memory ${mem.value:.2f}M",                                             # 4
        f"Other rack content ${v_other:.2f}M<br>(Grace, NVLink switches, NICs,<br>PCB, power, chassis)",  # 5
        f"Liquid cooling ${cool.value:.2f}M",                                    # 6
        f"ODM gross margin ${v_odm:.2f}M<br>(Foxconn, Quanta, Wistron…)",        # 7
        f"NVIDIA gross profit<br>on GPUs ${v_nv:.2f}M",                          # 8
        f"TSMC logic wafers ${v_logic:.2f}M",                                    # 9
        f"TSMC CoWoS-L ${v_cowos:.2f}M",                                         # 10
        f"Substrate, test, other ${v_oth:.2f}M",                                 # 11
        f"HBM makers ${v_hbm:.2f}M<br>(SK hynix, Samsung, Micron)",              # 12
        f"LPDDR5X DRAM ${v_lp:.2f}M",                                            # 13
        f"Switches, NICs, optics<br>${v_net:.2f}M",                              # 14
    ]
    colors = ["#52514E", "#898781", "#B0651A", "#A9CC73", "#3987E5", "#B5B5B5", "#0F9FB0", "#7A7A7A",
              NV, "#256ABF", "#5598E7", "#9EC5F4", "#104281", "#86B6EF", "#B0651A"]
    links = [(0, 1, price.value), (0, 2, v_net), (1, 3, gpu.value), (1, 4, mem.value), (1, 5, v_other),
             (1, 6, cool.value), (1, 7, v_odm), (3, 8, v_nv), (3, 9, v_logic), (3, 10, v_cowos), (3, 11, v_oth),
             (4, 12, v_hbm), (4, 13, v_lp), (2, 14, v_net)]
    link_col = []
    for a, b_, _ in links:
        col = colors[b_]
        rgb = tuple(int(col[i:i + 2], 16) for i in (1, 3, 5))
        link_col.append(f"rgba({rgb[0]},{rgb[1]},{rgb[2]},0.35)")
    xs = [0.001, 0.30, 0.30, 0.60, 0.60, 0.60, 0.60, 0.60, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999, 0.999]
    ys = [0.42, 0.36, 0.93, 0.40, 0.66, 0.08, 0.74, 0.80, 0.27, 0.53, 0.585, 0.635, 0.70, 0.775, 0.93]
    pf = go.Figure(go.Sankey(
        arrangement="fixed",
        node=dict(label=nodes, color=colors, pad=14, thickness=16, line=dict(color="white", width=0.5), x=xs, y=ys),
        link=dict(source=[a for a, _, _ in links], target=[b_ for _, b_, _ in links],
                  value=[max(v, 0.004) for _, _, v in links], color=link_col,
                  hovertemplate="%{source.label} → %{target.label}<br>$%{value:.2f}M<extra></extra>"),
        textfont=dict(size=11, color=INK["title"]),
    ))
    pf.add_annotation(text="All values Est. · NVIDIA also earns margin inside 'Other rack content' (Grace, NVLink switches, NICs) "
                           "and much of the network spend; those splits are not public.",
                      xref="paper", yref="paper", x=0, y=-0.07, showarrow=False, xanchor="left",
                      font=dict(size=10, color=INK["muted"]))
    c.save_plotly(pf, static=True, height=620, width=1100)


# --------------------------------------------------------------------------------------
@register
def memory_share_of_rack_bom():
    t = load(TCO)
    rows = []
    for sysname, lab in [("GB300 NVL72", "GB300 NVL72\n(2025)"), ("Vera Rubin NVL72", "Vera Rubin NVL72\n(2026)")]:
        price = _tco_row(t, sysname, "capex_per_rack", "Morgan Stanley")
        mem = _tco_row(t, sysname, "bom_memory")
        gpu = _tco_row(t, sysname, "bom_gpu")
        rows.append(dict(label=lab, price=price.value, mem=mem.value, gpu=gpu.value, rows=[price, mem, gpu]))
    used = pd.DataFrame([r for x in rows for r in x["rows"]])
    a, b_ = rows
    sa, sb = a["mem"] / a["price"] * 100, b_["mem"] / b_["price"] * 100
    c = Chart(
        id="03-memory-share-of-rack-bom",
        title=f"Est.: memory rises from ~{sa:.0f}% to ~{sb:.0f}% of an NVL72 rack's cost (GB300 → Vera Rubin)",
        subtitle="Morgan Stanley rack BOM (ODM price to hyperscaler, May 2026), US$ M · memory = HBM + CPU-attached LPDDR5X",
        alt=(f"Stacked bar chart of estimated NVL72 rack cost: GB300 NVL72 ${a['price']:.2f}M with GPUs ${a['gpu']:.2f}M and memory "
             f"${a['mem']:.2f}M ({sa:.0f}%); Vera Rubin NVL72 ${b_['price']:.2f}M with GPUs ${b_['gpu']:.2f}M and memory "
             f"${b_['mem']:.2f}M ({sb:.0f}%), a {b_['mem'] / a['mem']:.1f}-fold rise in memory dollars per rack."),
        data=[TCO], chapters=["03", "08", "14"],
        source="Morgan Stanley via PC Gamer, Wccftech, iTiger",
        source_ids=sources_of(used),
    )
    fig, ax = c.figure(width=10.5, height=5.8)
    x = np.arange(2)
    gpu_v = np.array([a["gpu"], b_["gpu"]])
    mem_v = np.array([a["mem"], b_["mem"]])
    oth_v = np.array([a["price"], b_["price"]]) - gpu_v - mem_v
    b1 = ax.bar(x, gpu_v, color=NV, width=0.5, label="GPUs (excl. memory)", zorder=2)
    b2 = ax.bar(x, mem_v, bottom=gpu_v, color="#3987E5", width=0.5, label="Memory (HBM + LPDDR5X)", zorder=2)
    b3 = ax.bar(x, oth_v, bottom=gpu_v + mem_v, color="#B5B5B5", width=0.5, label="Everything else", zorder=2)
    for bars in (b1, b2, b3):
        hatch_future(bars, [False, True])
    for i in range(2):
        ax.text(i, gpu_v[i] / 2, f"${gpu_v[i]:.2f}M", ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        mlab = f"${mem_v[i]:.2f}M ({mem_v[i] / (gpu_v[i] + mem_v[i] + oth_v[i]) * 100:.0f}%)"
        if mem_v[i] < 0.8:
            ax.annotate("Memory " + mlab, (i + 0.25, gpu_v[i] + mem_v[i] / 2), xytext=(8, 0), textcoords="offset points",
                        va="center", fontsize=9.2, color="#256ABF", fontweight="bold")
        else:
            ax.text(i, gpu_v[i] + mem_v[i] / 2, mlab.replace(" (", "\n("), ha="center", va="center", color="white",
                    fontsize=9.5, fontweight="bold")
        ax.text(i, gpu_v[i] + mem_v[i] + oth_v[i] / 2, f"${oth_v[i]:.2f}M", ha="center", va="center",
                color=INK["title"], fontsize=9.2)
        tot = gpu_v[i] + mem_v[i] + oth_v[i]
        ax.annotate(f"${tot:.2f}M", (i, tot), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color=INK["title"])
    ax.set_xticks(x, [a["label"], b_["label"]])
    ax.set_xlim(-0.7, 1.7)
    ax.set_ylim(0, b_["price"] * 1.12)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    c.save(fig, ax, ylabel="US$ M per rack (Est.)", legend=False)


# --------------------------------------------------------------------------------------
@register
def hbm_stacks_per_package():
    h = _h()
    pg = h[(h.record_type == "hbm_per_gpu") & (h.metric == "stacks")].copy()
    order = ["NVIDIA P100", "NVIDIA V100", "NVIDIA A100 40GB", "NVIDIA H100 SXM", "NVIDIA H200", "NVIDIA B200",
             "NVIDIA B300", "NVIDIA Rubin", "NVIDIA Rubin Ultra", "AMD MI300X", "AMD MI355X", "AMD MI455X"]
    d = pg.set_index("item").loc[order].reset_index()
    cap = h[(h.record_type == "hbm_per_gpu") & (h.metric == "capacity")].set_index("item").value
    d["cap"] = [cap[i] for i in d["item"]]
    d["label"] = [f"{i.split(' ', 1)[1]}\n{int(p)}" for i, p in zip(d["item"], d.period)]
    pk = h[h.record_type == "packaging_tech"]
    c = Chart(
        id="03-hbm-stacks-per-package",
        title="HBM stacks per NVIDIA GPU package grew 4×, from 4 (P100) to 16 (Rubin Ultra, roadmap)",
        subtitle="HBM stacks per accelerator package (label = GB per package) · CoWoS-S silicon interposer → CoWoS-L bridges · hatched = roadmap",
        alt=("Bar chart of HBM stacks per package: NVIDIA P100 4, V100 4, A100 5, H100 5, H200 6, B200 8, B300 8, Rubin 8 and "
             "Rubin Ultra 16 (roadmap, 1 TB); AMD MI300X 8, MI355X 8 and MI455X 12 (432 GB). NVIDIA moved from CoWoS-S silicon "
             "interposers to CoWoS-L bridges with the two-die B200; TSMC targets about 5.5x reticle interposers in 2026 and 9.5x in 2027."),
        data=[HBM], chapters=["03", "02"],
        source="NVIDIA, AMD, TSMC",
        source_ids=sources_of(pd.concat([d, pk])),
    )
    fig, ax = c.figure(width=11, height=5.8)
    x = np.array(list(range(9)) + [9.8, 10.8, 11.8])
    cols = [GEN_PAST] * 7 + [NV, NV] + [entity_color("AMD")] * 3
    b = ax.bar(x, d.value, color=cols, width=0.66, zorder=2)
    hatch_future(b, [i in ("NVIDIA Rubin Ultra", "AMD MI455X") for i in d["item"]])
    for xi, v, cp in zip(x, d.value, d.cap):
        ax.annotate(f"{v:.0f}", (xi, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                    fontsize=9.5, color=INK["title"], fontweight="bold")
        ax.text(xi, 0.25, f"{cp:,.0f} GB", ha="center", va="bottom", fontsize=7.4, color=INK["title"], rotation=90)
    ax.set_xticks(x, d.label, fontsize=8)
    ax.axvspan(-0.45, 4.45, color="#F0EFEC", zorder=0)
    ax.text(2.0, 15.2, "CoWoS-S (silicon interposer)", ha="center", fontsize=8.6, color=INK["text"])
    ax.text(4.6, 15.2, "CoWoS-L (bridges) from B200 →", ha="left", fontsize=8.6, color=INK["text"])
    ax.set_ylim(0, 17.5)
    ax.legend(handles=[Patch(facecolor=GEN_PAST, label="NVIDIA (past)"), Patch(facecolor=NV, label="NVIDIA Rubin family"),
                       Patch(facecolor=entity_color("AMD"), label="AMD Instinct")], loc="upper right",
              frameon=False, fontsize=8.8)
    c.save(fig, ax, ylabel="HBM stacks per package", legend=False, bottom=0.15)
