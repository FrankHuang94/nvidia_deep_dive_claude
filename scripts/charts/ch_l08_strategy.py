"""Layer 08 (systems, racks and AI factories) strategy charts: rack competitors, OEM economics, deals, roadmap.

Owner: layer-08 STRATEGY agent. Data: data/l08_rack_verdicts.csv, l08_system_vendor_financials.csv,
l08_infra_deals.csv, l08_value_capture.csv (documented in data/README.md) and the shared system_specs.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

from style import Chart, GEN_PAST, INK, NV, VERDICT_COLORS, entity_color, load, register, sources_of

VERD = "l08_rack_verdicts.csv"
FIN = "l08_system_vendor_financials.csv"
DEALS = "l08_infra_deals.csv"
VALUE = "l08_value_capture.csv"
SYS = "system_specs.csv"

LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}
VERDICT_LABEL = {"leads": "L = rival leads NVIDIA", "parity": "P = parity", "behind": "B = rival behind",
                 "different": "D = different approach / not disclosed"}
ROLE_COLORS = {"NVIDIA": NV, "power and cooling": "#256ABF", "OEM": "#52514E", "ODM": "#9A9890"}


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _fin(company: str, period: str, metric: str) -> pd.Series:
    df = load(FIN)
    r = df[df.company.eq(company) & df.period.eq(period) & df.metric.eq(metric)]
    if r.empty:
        raise KeyError((company, period, metric))
    return r.iloc[0]


# --------------------------------------------------------------------------------------
# 1. Rack-scale competitor verdict heatmap
# --------------------------------------------------------------------------------------
@register
def rack_system_verdict_heatmap():
    df = load(VERD)
    comps = list(dict.fromkeys(df.competitor))
    dims = list(dict.fromkeys(df.dimension))
    leads = df[df.verdict_vs_nvidia.eq("leads")]
    n_lead_rivals = leads.competitor.nunique()
    amd_leads = int(leads.competitor.eq("AMD").sum())
    scale_leads = int(df[df.dimension.eq("Scale-up domain")].verdict_vs_nvidia.eq("leads").sum())
    c = Chart(
        id="08-rack-system-verdict-heatmap",
        title=(f"AMD's Helios leads Vera Rubin NVL72 on {amd_leads} of 7 rack metrics on paper; "
               f"{scale_leads} rivals have bigger scale-up domains"),
        subtitle="Repo verdict for each rival rack-scale system vs NVIDIA Vera Rubin NVL72 (2026 basis); cell = verdict letter + key number",
        alt=(f"Heatmap of 7 rival AI systems against NVIDIA Vera Rubin NVL72 on 7 dimensions. AMD Helios leads on compute "
             "(1.4 vs 1.26 EF FP8), memory (31.1 vs 20.7 TB HBM4) and openness (OCP double-wide rack), is at parity on power "
             "and domain size, and is behind on liquid-cooling maturity and time to deploy (ships end-Q3 2026). Google, AWS and "
             "Huawei lead on scale-up domain size (9,216, 144 and 384-8,192 chips vs 72). Google leads on liquid-cooling maturity. "
             f"Qualcomm's AI200 rack leads only on power (160 kW) and openness. {n_lead_rivals} of 7 rivals lead on at least one metric."),
        data=[VERD], chapters=["08", "15"], source="repo analysis of vendor specs (l08_rack_verdicts.csv)",
        source_ids=sources_of(df), note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=13, height=6.9)
    for i, comp in enumerate(comps):
        for j, dim in enumerate(dims):
            r = df[(df.competitor == comp) & (df.dimension == dim)].iloc[0]
            ax.add_patch(Rectangle((j + 0.03, i + 0.05), 0.94, 0.9, facecolor=VERDICT_COLORS[r.verdict_vs_nvidia],
                                   edgecolor="#FFFFFF", linewidth=1.2))
            lab = str(r.cell_label)
            if len(lab) > 18 and ";" in lab:
                lab = lab.replace("; ", ";\n")
            elif len(lab) > 19:
                parts = lab.split(" ")
                mid = len(parts) // 2
                lab = " ".join(parts[:mid]) + "\n" + " ".join(parts[mid:])
            ax.text(j + 0.5, i + 0.5, f"{LETTER[r.verdict_vs_nvidia]} · {lab}", ha="center", va="center",
                    fontsize=7.9, color=INK["title"], fontweight="bold" if r.verdict_vs_nvidia == "leads" else "normal")
    ax.set_xlim(0, len(dims))
    ax.set_ylim(len(comps), 0)
    ax.set_xticks(np.arange(len(dims)) + 0.5)
    ax.set_xticklabels([d.replace(" per rack", "\nper rack").replace(" / ", " /\n").replace(" maturity", "\nmaturity")
                        .replace(" to deploy", "\nto deploy").replace(" domain", "\ndomain") for d in dims], fontsize=9)
    ax.xaxis.tick_top()
    basis = df.drop_duplicates("competitor").set_index("competitor").system_basis
    ax.set_yticks(np.arange(len(comps)) + 0.5)
    ax.set_yticklabels([f"{cmp}\n{basis[cmp]}" for cmp in comps], fontsize=8.6)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=4, fontsize=9, frameon=False)
    _margins(fig, left=0.17, right=0.985)
    c.save(fig, ax, legend=False, top=0.79, bottom=0.08)


# --------------------------------------------------------------------------------------
# 2. OEM AI-server revenue ramp (Dell, Supermicro)
# --------------------------------------------------------------------------------------
@register
def oem_ai_server_revenue_ramp():
    df = load(FIN)
    dell = df[df.company.eq("Dell (AI servers)") & df.metric.eq("ai_server_revenue") & df.period.str.startswith("FY")]
    smci = df[df.company.eq("Supermicro") & df.metric.eq("revenue") & df.period.str.startswith("FY")]
    d26 = dell[dell.period.eq("FY2026")].value.item()
    d27 = dell[dell.period.eq("FY2027E")].value.item()
    s26 = smci[smci.period.eq("FY2026")].value.item()
    s27 = smci[smci.period.eq("FY2027E")].value.item()
    q2 = _fin("Dell (AI servers)", "Q2FY2027", "ai_server_revenue").value
    c = Chart(
        id="08-oem-ai-server-revenue-ramp",
        title=(f"Dell guides AI servers to ${d27:.0f}B in FY2027 ({d27/d26:.1f}×); Supermicro to $65–72B "
               f"({s27/s26:.2f}×)"),
        subtitle="US$ billions by fiscal year; Dell = AI-optimized server revenue; Supermicro = total net sales; hatched = guidance",
        alt=(f"Bar chart: Dell AI-server revenue ${d26}B in FY2026 (to Jan 2026) and ${d27:.0f}B guided for FY2027, with "
             f"${q2}B in Q2 FY2027 alone and a $95B AI backlog; Supermicro net sales $22.0B (FY2025), ${s26}B (FY2026, to "
             f"June 2026) and $65-72B guided for FY2027. OEM AI revenue is growing 2-3x a year, but on mid-single-digit "
             "AI-server operating margins at Dell."),
        data=[FIN], chapters=["08", "13"], source="Dell and Supermicro results as reported",
        source_ids=sources_of(pd.concat([dell, smci])), note="Hatched = company guidance",
    )
    fig, ax = c.figure(width=11, height=5.6)
    groups = [("Dell AI servers", dell, "#52514E"), ("Supermicro net sales", smci, "#9A9890")]
    x0 = 0
    ticks, ticklabels = [], []
    for name, d, col in groups:
        d = d.sort_values("period_end")
        for k, r in enumerate(d.itertuples()):
            xi = x0 + k
            guide = r.period.endswith("E")
            b = ax.bar(xi, r.value, 0.7, color=col, edgecolor="white", alpha=0.55 if guide else 1.0,
                       hatch="///" if guide else None)
            lab = f"${r.value:.0f}B" if r.value >= 10 else f"${r.value:.1f}B"
            if name.startswith("Super") and guide:
                lab = "$65–72B"
                ax.errorbar(xi, r.value, yerr=[[r.value - 65], [72 - r.value]], color=INK["title"], capsize=5, lw=1.2)
            ax.annotate(lab, (xi, r.value), xytext=(0, 4 if not (name.startswith("Super") and guide) else 12),
                        textcoords="offset points", ha="center", fontsize=9.5, color=INK["title"], fontweight="bold")
            ticks.append(xi)
            ticklabels.append(r.period.replace("E", "\nguide"))
        ax.text(x0 + (len(d) - 1) / 2, -11, name, ha="center", fontsize=10, color=INK["title"], fontweight="bold")
        x0 += len(d) + 0.8
    ax.set_xticks(ticks, ticklabels)
    ax.set_ylim(0, 85)
    ax.text(2.1, 52, f"Dell Q2 FY2027\nalone: ${q2}B;\nAI backlog $95B", ha="center", fontsize=8.8,
            color=INK["text"], style="italic")
    c.save(fig, ax, ylabel="US$ billions", legend=False, bottom=0.2)


# --------------------------------------------------------------------------------------
# 3. ZT Systems: AMD's net cost for a rack-design team
# --------------------------------------------------------------------------------------
@register
def zt_deal_net_cost():
    d = load(DEALS)
    amd = d[d.acquirer.eq("AMD")].value_usd_m.item() / 1000
    steps = [("AMD pays for ZT Systems\n(Aug 2024 / Mar 2025)", amd, "total"),
             ("Sanmina cash\nfor factories", -2.25, "delta"),
             ("Premium\n(cash + equity)", -0.30, "delta"),
             ("Net before\nearn-out", None, "sub"),
             ("Earn-out\n(up to)", -0.45, "delta_contingent"),
             ("Net if earn-out\nis paid", None, "sub")]
    net1 = amd - 2.25 - 0.30
    net2 = net1 - 0.45
    c = Chart(
        id="08-zt-deal-net-cost",
        title=f"AMD's net cost for ZT's rack-design teams: ~${net2:.1f}–{net1:.2f}B after selling the factories",
        subtitle="US$ billions; AMD's $4.9B ZT Systems purchase less Sanmina's payment for the ZT manufacturing business (closed 2025-10-27)",
        alt=(f"Waterfall chart: AMD paid ${amd:.1f}B for ZT Systems (announced August 2024, closed March 2025), then sold ZT's "
             "manufacturing business to Sanmina for $2.25B cash plus a $0.30B premium and up to $0.45B of earn-out. AMD's net cost "
             f"for the design and customer-enablement teams is about ${net1:.2f}B, or ${net2:.1f}B if the earn-out is paid - "
             "the market price of a proven rack-scale design organisation."),
        data=[DEALS], chapters=["08", "13", "15"], source="AMD, Sanmina and Evertiq", source_ids=sources_of(d[d.target.str.contains("ZT")]),
        note="Hatched = contingent",
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    level = 0.0
    for i, (lab, val, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, val, 0.62, color=entity_color("AMD"))
            level = val
            ax.annotate(f"${val:.1f}B", (i, val), xytext=(0, 4), textcoords="offset points", ha="center", fontsize=10,
                        fontweight="bold", color=INK["title"])
        elif kind.startswith("delta"):
            cont = kind == "delta_contingent"
            ax.bar(i, -val, 0.62, bottom=level + val, color="#9A9890", alpha=0.6 if cont else 1.0,
                   hatch="///" if cont else None, edgecolor="white")
            ax.annotate(f"−${-val:.2f}B", (i, level), xytext=(0, 4), textcoords="offset points", ha="center",
                        fontsize=9.5, color=INK["title"])
            ax.plot([i - 0.31 - 0.38, i - 0.31], [level, level], color=INK["base"], lw=1)
            level += val
        else:
            ax.bar(i, level, 0.62, color=entity_color("AMD"), alpha=0.55)
            ax.annotate(f"${level:.2f}B", (i, level), xytext=(0, 4), textcoords="offset points", ha="center",
                        fontsize=10, fontweight="bold", color=INK["title"])
    ax.set_axisbelow(True)
    ax.set_xticks(range(len(steps)), [s[0] for s in steps], fontsize=8.8)
    ax.set_ylim(0, 5.6)
    ax.text(5.4, 5.1, "AMD kept ZT's design and customer-\nenablement teams; Sanmina builds\nHelios-class racks for AMD",
            ha="right", va="top", fontsize=8.8, color=INK["text"], style="italic")
    c.save(fig, ax, ylabel="US$ billions", legend=False, bottom=0.19)


# --------------------------------------------------------------------------------------
# 4. Rack spec roadmap: kW, dense FP8 PFLOPS and HBM TB per rack
# --------------------------------------------------------------------------------------
RACKS = [  # (system name in system_specs.csv, short label, vendor, kind)
    ("GB200 NVL72", "GB200\nNVL72\n2024", "NVIDIA", "past"),
    ("GB300 NVL72", "GB300\nNVL72\n2025", "NVIDIA", "past"),
    ("Vera Rubin NVL72 (GTC 2025 name: Vera Rubin NVL144)", "Vera Rubin\nNVL72\n2026", "NVIDIA", "current"),
    ("Rubin Ultra NVL144 Kyber (GTC 2025 name: NVL576)", "Kyber\nNVL144\n2027-28", "NVIDIA", "roadmap"),
    ("Helios (72x MI455X)", "AMD\nHelios\n2026", "AMD", "current"),
    ("Trn3 UltraServer Gen2 (144 chips)", "AWS Trn3\n144-chip\n2025", "AWS", "current"),
    ("TPU7x Ironwood rack (64-chip cube)", "Google\nIronwood\nrack 2025", "Google", "current"),
]


@register
def rack_spec_roadmap():
    s = load(SYS).set_index("system")
    rows = []
    for name, lab, vendor, kind in RACKS:
        r = s.loc[name]
        rows.append(dict(name=name, label=lab, vendor=vendor, kind=kind, kw=r.power_kw, fp8=r.fp8_pflops_dense,
                         hbm=r.total_hbm_tb, sid=r.source_id))
    d = pd.DataFrame(rows)
    g2 = d.iloc[0]
    ky = d.iloc[3]
    c = Chart(
        id="08-rack-spec-roadmap",
        title=(f"GB200 → Kyber: ~{ky.kw/g2.kw:.0f}× rack power ({g2.kw:.0f} → ~{ky.kw:.0f} kW) buys ~{ky.fp8/g2.fp8:.0f}× "
               f"dense FP8 and ~{ky.hbm/g2.hbm:.0f}× HBM per rack"),
        subtitle="Per rack or rack-equivalent: maximum power (kW), dense FP8 PFLOPS and HBM capacity (TB); hatched = roadmap or estimate",
        alt=(f"Three bar panels comparing rack-scale systems. Power: GB200 NVL72 {g2.kw:.0f} kW, GB300 132 kW, Vera Rubin NVL72 "
             f"about 190-230 kW, AMD Helios about 225-245 kW (estimate), Kyber about {ky.kw:.0f} kW (roadmap); AWS and Google do not "
             f"publish rack power. Dense FP8: GB200 and GB300 360 PF, Vera Rubin 1,260 PF, Helios 1,400 PF, Kyber {ky.fp8:,.0f} PF, "
             f"Trn3 144-chip 362 PF, Ironwood 64-chip rack 295 PF. HBM: 13.8, 20.7, 20.7, 31.1 (Helios), about {ky.hbm:.0f} TB "
             "(Kyber, as announced), 20.7 (Trn3) and 12.3 TB (Ironwood rack)."),
        data=[SYS], chapters=["08", "17", "15"], source="vendor specs and estimates in system_specs.csv",
        source_ids=sources_of(pd.DataFrame({"source_id": d.sid})), note="Kyber = GTC 2025/2026 targets; slip to 2028 reported",
    )
    fig, axes = c.figure_grid(1, 3, width=13.5, height=6.0)
    panels = [("kw", "Max power per rack (kW)", "{:,.0f}"), ("fp8", "Dense FP8 PFLOPS per rack", "{:,.0f}"),
              ("hbm", "HBM per rack (TB)", "{:,.1f}")]
    for ax, (col, ttl, fmt) in zip(axes, panels):
        x = np.arange(len(d))
        for xi, r in zip(x, d.itertuples()):
            v = getattr(r, col)
            if r.vendor == "NVIDIA":
                color = GEN_PAST if r.kind == "past" else NV
            else:
                color = entity_color(r.vendor)
            if pd.isna(v):
                ax.text(xi, d[col].max() * 0.015, "n/d", ha="center", va="bottom", fontsize=8.3, color=INK["muted"])
                continue
            b = ax.bar(xi, v, 0.7, color=color)
            est = r.kind == "roadmap" or (r.vendor == "AMD" and col == "kw")
            if est:
                b.patches[0].set_hatch("///")
                b.patches[0].set_alpha(0.8)
            ax.annotate(f"{v:,.0f}" if v >= 100 else fmt.format(v), (xi, v), xytext=(0, 3), textcoords="offset points",
                        ha="center", fontsize=8.3,
                        color=INK["title"], fontweight="bold" if r.vendor == "NVIDIA" else "normal")
        ax.set_xticks(x, d.label, fontsize=7.6)
        ax.set_title(ttl, fontsize=10.5, color=INK["title"], loc="left")
        ax.set_ylim(0, d[col].max() * 1.15)
        ax.tick_params(length=0)
        ax.set_axisbelow(True)
    axes[1].text(0.02, 0.9, "Kyber: 15 EF FP4 / 5 EF FP8\n(GTC 2025 figures)", transform=axes[1].transAxes,
                 fontsize=8.3, color=INK["text"], style="italic")
    axes[2].text(0.02, 0.62, "Kyber: 144 × 1 TB HBM4E\nas announced; 768 GB per\nGPU reported (~110 TB)",
                 transform=axes[2].transAxes, fontsize=8.3, color=INK["text"], style="italic")
    _margins(fig, left=0.05, right=0.99, wspace=0.18)
    c.save(fig, list(axes), ylabel="Value per rack (units in panel title)", legend=False, top=0.82, bottom=0.17)


# --------------------------------------------------------------------------------------
# 5. Margin ladder across the system value chain
# --------------------------------------------------------------------------------------
LADDER = [  # (company, period, metric, label)
    ("NVIDIA", "Q2FY2027", "gross_margin_pct", "NVIDIA gross (Q2 FY2027)"),
    ("NVIDIA", "FY2026", "operating_margin_pct", "NVIDIA operating (FY2026)"),
    ("Vertiv", "Q3 2026", "operating_margin_pct", "Vertiv adj. operating (Q3 2026)"),
    ("Supermicro", "Q4FY2026", "gross_margin_pct", "Supermicro gross (Q4 FY2026)"),
    ("HPE (Cloud and AI)", "Q3FY2026", "operating_margin_pct", "HPE Cloud & AI operating (Q3 FY2026)"),
    ("Dell (ISG)", "Q2FY2027", "operating_margin_pct", "Dell ISG operating (Q2 FY2027)"),
    ("Supermicro", "FY2026", "gross_margin_pct", "Supermicro gross (FY2026)"),
    ("Quanta", "Q4 2025", "gross_margin_pct", "Quanta gross (Q4 2025)"),
    ("Foxconn (Hon Hai)", "Q2 2025", "gross_margin_pct", "Foxconn gross (Q2 2025)"),
    ("Dell (AI servers)", "FY2026", "operating_margin_pct", "Dell AI servers operating (target, Est.)"),
    ("Quanta (GB AI servers)", "Q4 2025", "gross_margin_pct", "Quanta GB rack servers gross (KGI Est.)"),
    ("Quanta", "Q4 2025", "operating_margin_pct", "Quanta operating (Q4 2025)"),
    ("ODM on a GB300 NVL72 rack", "2026", "gross_margin_pct", "ODM on a GB300 NVL72 rack (MS Est.)"),
    ("ODM on a Vera Rubin NVL72 rack", "2026", "gross_margin_pct", "ODM on a Vera Rubin rack (MS Est.)"),
]


@register
def system_layer_margin_ladder():
    df = load(FIN)
    rows = []
    for comp, per, met, lab in LADDER:
        r = df[df.company.eq(comp) & df.period.eq(per) & df.metric.eq(met)].iloc[0]
        role = "NVIDIA" if comp == "NVIDIA" else r.role
        rows.append(dict(label=lab, value=r.value, role=role, basis=str(r.profit_basis), conf=r.confidence,
                         source_id=r.source_id))
    d = pd.DataFrame(rows).iloc[::-1].reset_index(drop=True)
    nv = d[d.label.str.startswith("NVIDIA gross")].value.item()
    c = Chart(
        id="08-system-layer-margin-ladder",
        title=f"NVIDIA keeps a {nv:.0f}% gross margin; the ODMs that assemble its racks keep ~2–5%",
        subtitle="Gross or operating margin (%), latest reported period per company; solid = gross, hatched = operating; light = estimate",
        alt=("Horizontal bar chart of margins across the AI system value chain: NVIDIA gross margin 75.0% (Q2 FY2027) and "
             "operating margin 60.4% (FY2026); Vertiv adjusted operating margin 25.2% (Q3 2026); Supermicro gross margin 17.5% in "
             "Q4 FY2026 but 10.8% for FY2026; HPE Cloud and AI operating margin 17.0%; Dell ISG operating margin 15.0%; Quanta and "
             "Foxconn gross margins 6.3%; Dell's AI-server operating margin target in the mid single digits (~5%); Quanta GB rack "
             "servers ~5% gross (KGI); ODM gross margin on a GB300 NVL72 rack 2.7% and on a Vera Rubin rack 1.9% (Morgan Stanley)."),
        data=[FIN], chapters=["08", "13", "03"], source="company results; KGI, MS estimates",
        source_ids=sources_of(d), note="Mixed periods and bases",
    )
    fig, ax = c.figure(width=11, height=6.6)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = ROLE_COLORS.get(r.role, "#9A9890")
        op = "operating" in r.basis
        b = ax.barh(yi, r.value, 0.66, color=col, alpha=0.5 if r.conf == "estimate" else 1.0)
        if op:
            b.patches[0].set_hatch("///")
            b.patches[0].set_edgecolor("white")
        ax.text(r.value + 0.8, yi, f"{r.value:.1f}%", va="center", fontsize=9, color=INK["title"],
                fontweight="bold" if r.role == "NVIDIA" else "normal")
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label, fontsize=9)
    ax.set_xlim(0, 85)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=ROLE_COLORS["NVIDIA"], label="NVIDIA"),
               Patch(color=ROLE_COLORS["power and cooling"], label="Power & cooling"),
               Patch(color=ROLE_COLORS["OEM"], label="OEM (Dell, HPE, Supermicro)"),
               Patch(color=ROLE_COLORS["ODM"], label="ODM / EMS"),
               Patch(facecolor="#C3C2B7", hatch="///", edgecolor="white", label="Operating margin")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _margins(fig, left=0.30, right=0.97)
    c.save(fig, ax, xlabel="Margin (%)", legend=False)


# --------------------------------------------------------------------------------------
# 6. Profit pool: one quarter of revenue and profit (mid-2026)
# --------------------------------------------------------------------------------------
@register
def ai_hardware_profit_pool():
    pool = [  # (label, company, period, revenue metric, profit metric, profit label)
        ("NVIDIA (Q2 FY2027, May–Jul 2026)", "NVIDIA", "Q2FY2027", "revenue", "gross_profit", "gross"),
        ("Dell ISG (Q2 FY2027, May–Jul 2026)", "Dell (ISG)", "Q2FY2027", "segment_revenue", "operating_profit", "operating"),
        ("Supermicro (Q4 FY2026, Apr–Jun 2026)", "Supermicro", "Q4FY2026", "revenue", "gross_profit", "gross"),
        ("HPE Cloud & AI (Q3 FY2026, May–Jul 2026)", "HPE (Cloud and AI)", "Q3FY2026", "segment_revenue", "operating_profit", "operating"),
        ("Vertiv (Q3 2026, Jul–Sep 2026)", "Vertiv", "Q3 2026", "revenue", "operating_profit", "adj. operating"),
    ]
    rows = []
    for lab, comp, per, rm, pm, pl in pool:
        rev = _fin(comp, per, rm)
        pro = _fin(comp, per, pm)
        rows.append(dict(label=lab, rev=rev.value, profit=pro.value, plab=pl, source_id=f"{rev.source_id};{pro.source_id}"))
    d = pd.DataFrame(rows)
    nv_op = _fin("NVIDIA", "Q2FY2027", "operating_profit").value
    others = d.iloc[1:].profit.sum()
    nv_gp = d.iloc[0].profit
    c = Chart(
        id="08-ai-hardware-profit-pool",
        title=(f"Mid-2026: NVIDIA's quarterly profit was {nv_op/others:.0f}–{nv_gp/others:.0f}× that of four system "
               "vendors combined"),
        subtitle="One fiscal quarter ending Jun–Sep 2026, US$ billions: revenue (light) and profit (dark; gross or operating as labelled)",
        alt=(f"Horizontal paired bars for one quarter in mid-2026. NVIDIA revenue $96.2B with about ${nv_gp:.1f}B gross profit "
             f"(about ${nv_op:.0f}B operating profit, repo estimate); Dell ISG revenue $31.8B and $4.8B operating profit; Supermicro "
             "revenue $11.1B and about $1.9B gross profit; HPE Cloud and AI revenue $9.0B and $1.5B operating profit; Vertiv revenue "
             f"$4.3B and $1.1B adjusted operating profit. The four system and infrastructure vendors together earned about ${others:.1f}B."),
        data=[FIN], chapters=["08", "13", "18"], source="company results; repo calc",
        source_ids=sources_of(d), note="Profit bases differ (see labels)",
    )
    fig, ax = c.figure(width=11, height=5.6)
    y = np.arange(len(d))[::-1]
    for yi, r in zip(y, d.itertuples()):
        col = NV if r.label.startswith("NVIDIA") else ("#256ABF" if r.label.startswith("Vertiv") else "#52514E")
        ax.barh(yi + 0.18, r.rev, 0.36, color=col, alpha=0.35)
        ax.barh(yi - 0.18, r.profit, 0.36, color=col)
        ax.text(r.rev + 0.8, yi + 0.18, f"${r.rev:.1f}B revenue", va="center", fontsize=8.6, color=INK["text"])
        ax.text(r.profit + 0.8, yi - 0.18, f"${r.profit:.1f}B {r.plab} profit", va="center", fontsize=8.8,
                color=INK["title"], fontweight="bold")
    ax.plot([nv_op, nv_op], [y[0] - 0.38, y[0] + 0.02], color="white", lw=2)
    ax.text(nv_op, y[0] - 0.40, f"≈${nv_op:.0f}B operating (Est.)", fontsize=8.2, color=INK["text"], ha="center",
            va="top", style="italic")
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label, fontsize=9)
    ax.set_xlim(0, 125)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.30, right=0.97)
    c.save(fig, ax, xlabel="US$ billions in the quarter", legend=False)


# --------------------------------------------------------------------------------------
# 7. Value capture by generation: NVIDIA content share vs integrator margin
# --------------------------------------------------------------------------------------
@register
def value_capture_by_generation():
    df = load(VALUE)
    share = df[df.metric.eq("nvidia_content_share_pct")].reset_index(drop=True)
    marg = df[df.metric.eq("integrator_gross_margin_pct")].set_index("system").reindex(share.system).reset_index()
    h = share.iloc[0]
    nvl = share[share.system.str.startswith("GB")]
    c = Chart(
        id="08-value-capture-by-generation",
        title=(f"Est.: NVIDIA's share of system value rose from ~{h.low:.0f}–{h.high:.0f}% (HGX) to "
               f"~{nvl.low.min():.0f}–{nvl.high.max():.0f}% (NVL72)"),
        subtitle="Left: estimated NVIDIA content as % of system price (range). Right: integrator gross margin (%). Repo estimates from analyst BOMs",
        alt=("Two-panel chart. Left: estimated share of system price paid for NVIDIA content - about 50-75% for an HGX H100/H200 "
             "8-GPU server, 72-84% for GB200 NVL72, 71-83% for GB300 NVL72 and 62-72% for Vera Rubin NVL72, where memory price "
             "inflation shifts value to HBM and LPDDR makers. Right: integrator gross margin falls from 11.1% (Supermicro, server "
             "era) to about 5% (Quanta GB racks, KGI), 2.7% (GB300 rack ODM) and 1.9% (Vera Rubin rack ODM, Morgan Stanley)."),
        data=[VALUE], chapters=["08", "13", "03"], source="analyst BOMs; repo calc",
        source_ids=sources_of(df), note="Estimates",
    )
    fig, (ax1, ax2) = c.figure_grid(1, 2, width=12, height=5.8, gridspec_kw={"width_ratios": [1.6, 1]})
    x = np.arange(len(share))
    labels = [f"{s}\n({e})".replace(" 8-GPU server", "\n8-GPU server") for s, e in zip(share.system, share.era)]
    for xi, r in zip(x, share.itertuples()):
        col = GEN_PAST if xi < 2 else NV
        ax1.bar(xi, r.high - r.low, 0.55, bottom=r.low, color=col, hatch="//", edgecolor="white", alpha=0.9)
        ax1.annotate(f"{r.low:.0f}–{r.high:.0f}%", (xi, r.high), xytext=(0, 4), textcoords="offset points", ha="center",
                     fontsize=9.5, fontweight="bold", color=INK["title"])
    ax1.set_xticks(x, labels, fontsize=8.2)
    ax1.set_ylim(0, 100)
    ax1.set_ylabel("NVIDIA content, % of system price (Est.)")
    ax1.set_title("NVIDIA content share", fontsize=10.5, loc="left", color=INK["title"])
    ax1.annotate("memory makers take\nshare on Rubin", (3, 62), xytext=(2.2, 30), fontsize=8.5, color=INK["text"],
                 arrowprops=dict(arrowstyle="->", color=INK["muted"]))
    for xi, r in zip(x, marg.itertuples()):
        col = "#52514E" if xi == 0 else "#9A9890"
        b = ax2.bar(xi, r.low, 0.55, color=col, alpha=1.0 if r.confidence == "reported" else 0.6)
        ax2.annotate(f"{r.low:.1f}%", (xi, r.low), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9.5,
                     color=INK["title"], fontweight="bold")
    ax2.set_xticks(x, ["Supermicro\n(server OEM)", "Quanta\nGB racks", "ODM\nGB300", "ODM\nVera Rubin"], fontsize=8.2)
    ax2.set_ylim(0, 14)
    ax2.set_title("Integrator gross margin", fontsize=10.5, loc="left", color=INK["title"])
    ax2.set_ylabel("Gross margin (%)")
    for a in (ax1, ax2):
        a.tick_params(length=0)
        a.set_axisbelow(True)
    _margins(fig, left=0.07, right=0.98, wspace=0.25)
    c.save(fig, [ax1, ax2], legend=False, bottom=0.2, top=0.82)


# --------------------------------------------------------------------------------------
# 8. Rack-adjacent M&A since 2024
# --------------------------------------------------------------------------------------
CAT_COLORS = {"datacenter developer": "#104281", "systems vendor buys networking": "#52514E",
              "rack-scale design team": entity_color("AMD"), "rack manufacturing": "#E3A0AC",
              "liquid cooling": "#3987E5", "liquid-cooling services": "#86B6EF", "racks and enclosures": "#9EC5F4"}


@register
def infra_deal_values():
    d = load(DEALS).copy()
    short = {"AIP, GIP and MGX consortium": "AIP/GIP/MGX", "ZT Systems manufacturing (from AMD)": "ZT factories",
             "Schneider Electric": "Schneider"}
    d["label"] = d.apply(lambda r: f"{short.get(r.target, r.target)} ← {short.get(r.acquirer, r.acquirer)} "
                                   f"({str(r.announce_date)[:4]})", axis=1)
    d = d.sort_values("value_usd_m").reset_index(drop=True)
    pc = d[d.category.isin(["liquid cooling", "liquid-cooling services", "racks and enclosures"])].value_usd_m.sum() / 1000
    top = d.iloc[-1]
    c = Chart(
        id="08-infra-deal-values",
        title=(f"Cooling and rack-hardware deals total ~${pc:.1f}B since 2024; Aligned (${top.value_usd_m/1000:.0f}B) "
               "is the largest"),
        subtitle="Disclosed or reported deal value, US$ millions (log scale); AI-system, cooling, rack and datacenter deals announced 2024–2025",
        alt=("Log-scale horizontal bar chart of rack-adjacent deals: AIP/GIP/MGX's $40B purchase of Aligned Data Centers (closed "
             "July 2026), HPE's $14B Juniper deal, Eaton's $9.5B Boyd Thermal (closed March 2026), AMD's $4.9B ZT Systems and "
             "Sanmina's up-to-$3.0B purchase of ZT's factories, Vertiv's ~$1.0B PurgeRite (plus earn-out) and $200M Great Lakes, "
             f"and Schneider's $850M for 75% of Motivair. Cooling and rack-hardware deals sum to about ${pc:.1f}B."),
        data=[DEALS], chapters=["08", "13"], source="company releases and press", source_ids=sources_of(d),
        note="Hatched = up-to or reported value",
    )
    fig, ax = c.figure(width=11, height=5.8)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = CAT_COLORS.get(r.category, "#B5B5B5")
        b = ax.barh(yi, r.value_usd_m, 0.62, color=col)
        if r.value_basis in ("up-to", "reported"):
            b.patches[0].set_hatch("///")
            b.patches[0].set_edgecolor("white")
        txt = f"${r.value_usd_m/1000:.1f}B" if r.value_usd_m >= 1000 else f"${r.value_usd_m:,.0f}M"
        if r.value_basis == "up-to":
            txt = "up to " + txt
        ax.text(r.value_usd_m * 1.1, yi, txt, va="center", fontsize=9, color=INK["title"])
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label, fontsize=8.8)
    ax.set_xscale("log")
    ax.set_xlim(100, 150000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    seen = list(dict.fromkeys(d.category[::-1]))
    handles = [Patch(color=CAT_COLORS.get(k, "#B5B5B5"), label=k) for k in seen]
    ax.legend(handles=handles, loc="lower right", fontsize=8.3)
    _margins(fig, left=0.29, right=0.97)
    c.save(fig, ax, xlabel="Deal value, US$ millions (log scale)", logx=True, legend=False)
