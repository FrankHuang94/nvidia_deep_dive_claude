"""NVIDIA capital deployment charts (Agent A4): M&A, acquihire/licensing deals and strategic equity
investments mapped to the stack layer they strengthen, dollars by year, and investments in customers.

Data: data/acquisitions_investments.csv, data/investments_in_customers.csv."""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import NullFormatter

from style import Chart, INK, NV, NV_DARK, SEQ_BLUE, load, register, sources_of

DEALS = "acquisitions_investments.csv"
IC = "investments_in_customers.csv"
LAYERS = {
    "02": "02 GPU silicon", "03": "03 Memory & supply chain", "04": "04 CPU", "05": "05 Scale-up (NVLink)",
    "06": "06 Scale-out networking", "07": "07 DPU & storage", "08": "08 Systems, AI factories, power",
    "09": "09 CUDA & system software", "10": "10 CUDA-X libraries", "11": "11 Inference & AI software",
    "12": "12 Orchestration & cloud", "13": "13 Ecosystem: labs, GTM",
}
MA_TYPES = ("acquisition", "acquihire-license", "failed-acquisition")
TYPE_STYLE = {
    "acquisition": dict(color=NV, label="Acquisition"),
    "acquihire-license": dict(color=NV_DARK, label="Acquihire + licence"),
    "failed-acquisition": dict(color=NV, label="Failed acquisition"),
    "equity-investment": dict(color=SEQ_BLUE[5], label="Equity investment"),
    "strategic-partnership-investment": dict(color=SEQ_BLUE[2], label="Strategic partnership / backstop"),
}


def _deals() -> pd.DataFrame:
    df = load(DEALS, dtype={"layer_strengthened": str})
    df["layer"] = df.layer_strengthened.str.zfill(2)
    parts = df.announce_date.astype(str).str.split("-", expand=True)
    y = parts[0].astype(float)
    m = parts[1].astype(float).fillna(6.5) if 1 in parts else 6.5
    d = parts[2].astype(float).fillna(15) if 2 in parts else 15
    df["t"] = y + (m - 1) / 12 + (d - 1) / 365
    df["year"] = y.astype(int)
    df["amt_b"] = pd.to_numeric(df.amount_usd_m, errors="coerce") / 1000
    return df


def _below(axes) -> None:
    for a in (axes if isinstance(axes, (list, tuple)) else [axes]):
        a.set_axisbelow(True)


# --------------------------------------------------------------------------------------
# 1. Deals timeline by layer
# --------------------------------------------------------------------------------------
@register
def deals_timeline_by_layer():
    df = _deals()
    recent = df[df.year >= 2023]
    n_inv = int((~recent.deal_type.isin(MA_TYPES)).sum())
    c = Chart(
        id="13-deals-timeline-by-layer",
        title=f"Since 2023, {n_inv} of NVIDIA's {len(recent)} logged deals were stakes in customers and partners, not M&A",
        subtitle="Each deal by announcement date and the stack layer it strengthens; marker area ∝ US$ amount (small hollow = undisclosed)",
        alt=(f"Timeline scatter of {len(df)} NVIDIA acquisitions, acquihire-licence deals and strategic investments from "
             f"{df.year.min()} to {df.year.max()}, placed on the stack layer each strengthened. Early deals were GPU and mobile "
             f"silicon tuck-ins; Mellanox ($6.9B, 2019) built the networking layer; since 2023 {n_inv} of {len(recent)} deals "
             f"are equity stakes, led by OpenAI, Anthropic, Intel and CoreWeave, plus the ~$20B Groq licence."),
        data=[DEALS], chapters=["13", "16", "12"],
        source="NVIDIA filings and announcements; press reports", source_ids=sources_of(df),
        note="Pre-2019 axis compressed",
    )
    fig, (sp, axl, ax) = c.figure_grid(1, 3, width=11.5, height=6.8, gridspec_kw={"width_ratios": [0.62, 1, 3.2],
                                                                                    "wspace": 0.04})
    sp.axis("off")   # spacer: style.save() fixes left=0.08, long layer names need room
    order = sorted(LAYERS)
    ypos = {k: len(order) - 1 - i for i, k in enumerate(order)}
    rng = np.random.default_rng(7)
    df["yj"] = [ypos[k] + rng.uniform(-0.28, 0.28) for k in df.layer]
    for a, lo, hi in ((axl, 1999.5, 2014.5), (ax, 2018.8, 2028.6)):
        sub = df[(df.t >= lo) & (df.t <= hi)]
        for typ, st in TYPE_STYLE.items():
            s = sub[sub.deal_type == typ]
            known = s[s.amt_b.notna()]
            unk = s[s.amt_b.isna()]
            size = 18 + np.sqrt(known.amt_b * 1000) * 2.0
            marker = "X" if typ == "failed-acquisition" else ("D" if typ.startswith("strategic") else "o")
            upto = known.amount_basis == "up-to"
            a.scatter(known.t[~upto], known.yj[~upto], s=size[~upto], color=st["color"], alpha=0.85, marker=marker,
                      edgecolor="#FFFFFF", lw=0.6, zorder=3)
            a.scatter(known.t[upto], known.yj[upto], s=size[upto], facecolor="none", edgecolor=st["color"], lw=1.8,
                      marker=marker, zorder=3, linestyle="--")
            a.scatter(unk.t, unk.yj, s=26, facecolor="#FFFFFF", edgecolor=st["color"], lw=1.3, marker=marker, zorder=2)
        a.set_xlim(lo, hi)
        a.grid(axis="x", color=INK["grid"], lw=0.6)
    ax.spines["bottom"].set_bounds(2018.8, 2026.6)
    axl.set_xticks([2000, 2005, 2010])
    ax.set_xticks(range(2019, 2027))
    axl.set_yticks([ypos[k] for k in order])
    axl.set_yticklabels([LAYERS[k] for k in order], fontsize=9)
    axl.set_ylim(-0.7, len(order) - 0.3)
    ax.set_ylim(-0.7, len(order) - 0.3)
    ax.set_yticks([ypos[k] for k in order])
    ax.set_yticklabels([])
    axl.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    for a in (axl, ax):
        a.grid(axis="y", color=INK["grid"], lw=0.6)
    ax.tick_params(axis="y", length=0)
    # big deals: Mellanox/Arm labelled in place; the crowded 2025–26 cluster labelled in a right-hand margin column
    for name, txt, (dx, dy) in (("Mellanox Technologies", "Mellanox $6.9B", (-4, 14)),
                                ("Arm Ltd (from SoftBank)", "Arm $40B (blocked)", (10, 10))):
        r = df[df.counterparty == name].iloc[0]
        ax.annotate(txt, (r.t, r.yj), xytext=(dx, dy), textcoords="offset points", fontsize=8, color=INK["title"],
                    arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.6))
    margin = [("Intel", "Intel $5B", 0.0), ("Synopsys", "Synopsys $2B", 0.0), ("Groq", "Groq licence ~$20B", 0.0),
              ("CoreWeave capacity backstop", "CoreWeave backstop $6.3B", 0.25), ("CoreWeave (2026)", "CoreWeave $2B", -0.2),
              ("Anthropic", "Anthropic ≤$10B", 0.42), ("OpenAI (10 GW letter of intent)", "OpenAI LOI ≤$100B", 0.0),
              ("OpenAI (2026 round)", "OpenAI ~$30B (2026)", -0.42)]
    for name, txt, off in margin:
        r = df[df.counterparty == name]
        if r.empty:
            continue
        r = r.iloc[0]
        ax.annotate(txt, (r.t, r.yj), xytext=(2026.72, ypos[r.layer] + off), textcoords="data", fontsize=8,
                    color=INK["title"], va="center", arrowprops=dict(arrowstyle="-", color=INK["muted"], lw=0.6))
    for name, (dx, dy) in {"PortalPlayer": (2, 8), "Icera": (-30, -14), "3dfx Interactive (graphics assets)": (-4, -14)}.items():
        r = df[df.counterparty == name].iloc[0]
        axl.annotate(name.split(" (")[0], (r.t, r.yj), xytext=(dx, dy), textcoords="offset points", fontsize=7.5,
                     color=INK["title"])
    handles = [Line2D([], [], marker="o", ls="", color=NV, ms=8, label="Acquisition"),
               Line2D([], [], marker="o", ls="", color=NV_DARK, ms=8, label="Acquihire + licence"),
               Line2D([], [], marker="X", ls="", color=NV, ms=8, label="Failed acquisition"),
               Line2D([], [], marker="o", ls="", color=SEQ_BLUE[5], ms=8, label="Equity investment"),
               Line2D([], [], marker="D", ls="", color=SEQ_BLUE[2], ms=7, label="Partnership / backstop"),
               Line2D([], [], marker="o", ls="", mfc="none", mec=INK["text"], ms=8, label="Hollow = undisclosed or 'up to'")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.42, 1.0), fontsize=8, ncol=2, frameon=True,
              facecolor="#FFFFFF", edgecolor=INK["grid"])
    axl.set_xlabel("Announced (2000–2014)")
    ax.set_xlabel("Announced (2019–2026)")
    _below([axl, ax])
    c.save(fig, [axl, ax], legend=False, bottom=0.11)
    # interactive twin: hover for every deal
    import plotly.graph_objects as go
    pfig = go.Figure()
    for typ, st in TYPE_STYLE.items():
        s = df[df.deal_type == typ]
        if s.empty:
            continue
        amt = s.amt_b.fillna(0)
        hover = [f"<b>{r.counterparty}</b><br>{r.announce_date} · {st['label']}<br>"
                 f"{'US$ ' + format(r.amt_b, ',.2f') + 'B (' + r.amount_basis + ')' if r.amt_b == r.amt_b else 'amount undisclosed'}"
                 f"<br>Layer {LAYERS[r.layer]}<br>{r.rationale}<br><i>{r.confidence}; status {r.status}</i>"
                 for r in s.itertuples()]
        pfig.add_trace(go.Scatter(
            x=s.t, y=s.yj, mode="markers", name=st["label"], hovertext=hover, hoverinfo="text",
            marker=dict(size=8 + np.sqrt(amt * 1000) * 0.55, color=st["color"], opacity=0.85,
                        symbol="x" if typ == "failed-acquisition" else ("diamond" if typ.startswith("strategic") else "circle"),
                        line=dict(color="#FFFFFF", width=0.6))))
    pfig.update_yaxes(tickvals=[ypos[k] for k in order], ticktext=[LAYERS[k] for k in order], range=[-0.7, len(order) - 0.3])
    pfig.update_xaxes(title="Announcement date (fractional year)", range=[1999.5, 2026.8])
    c.save_plotly(pfig, height=640)


# --------------------------------------------------------------------------------------
# 2. Deal dollars by year
# --------------------------------------------------------------------------------------
@register
def investment_dollars_by_year():
    df = _deals()
    use = df[~df.status.isin(["terminated", "superseded"]) & df.amt_b.notna() & (df.year >= 2019)]
    years = list(range(2019, int(df.year.max()) + 1))
    tot = use.groupby("year").amt_b.sum().reindex(years, fill_value=0)
    pre = use[use.year < 2025].amt_b.sum() + df[(df.year < 2019) & df.amt_b.notna() & ~df.status.isin(["terminated"])].amt_b.sum()
    y25 = tot.get(2025, 0)
    c = Chart(
        id="13-investment-dollars-by-year",
        title=f"NVIDIA's deal commitments jumped to ~${y25:.0f}B in 2025, {y25 / pre:.0f}× all its deals before 2025",
        subtitle="Disclosed or press-reported deal value by announcement year, US$ B; excludes blocked Arm and superseded OpenAI LOI",
        alt=(f"Stacked bar chart of NVIDIA deal dollars by year 2019–{years[-1]}: Mellanox ($6.9B) dominates 2019, small "
             f"software tuck-ins follow, then ~${y25:.0f}B in 2025 (Groq licence ~$20B, Anthropic up to $10B, CoreWeave "
             f"$6.3B backstop, Intel $5B, Synopsys $2B, xAI up to $2B, Nokia $1B) and ~${tot.get(2026, 0):.0f}B in 2026 "
             f"(OpenAI ~$30B, CoreWeave $2B); all pre-2025 deals total about ${pre:.0f}B."),
        data=[DEALS], chapters=["13", "18", "12"],
        source="NVIDIA filings and announcements; press reports", source_ids=sources_of(use),
        note="Arm ($40B, 2020) blocked",
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    x = np.arange(len(years))
    bottom = np.zeros(len(years))
    for typ in ["acquisition", "acquihire-license", "equity-investment", "strategic-partnership-investment"]:
        st = TYPE_STYLE[typ]
        for upto in (False, True):
            s = use[(use.deal_type == typ) & ((use.amount_basis == "up-to") == upto)]
            v = s.groupby("year").amt_b.sum().reindex(years, fill_value=0).values
            if v.sum() == 0:
                continue
            ax.bar(x, v, bottom=bottom, color=st["color"], width=0.62, hatch="///" if upto else None,
                   alpha=0.7 if upto else 1.0, edgecolor="#FFFFFF", lw=0.6)
            bottom += v
    n_deals = df[df.year >= 2019].groupby("year").size().reindex(years, fill_value=0)
    for i, (yr, t) in enumerate(tot.items()):
        if t > 0.05:
            txt = f"${t:.1f}B" if t < 10 else f"${t:.0f}B"
        elif n_deals[yr]:
            txt = f"{n_deals[yr]} deal{'s' if n_deals[yr] > 1 else ''},\nundisclosed"
        else:
            continue
        ax.annotate(txt, (i, t), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8.5 if t <= 0.05 else 9,
                    color=INK["title"] if t > 0.05 else INK["muted"], fontweight="bold" if t > 0.05 else "normal")
    big = use[use.amt_b >= 5].sort_values("amt_b", ascending=False)
    lab = {}
    for _, r in big.iterrows():
        nm = {"CoreWeave capacity backstop": "CoreWeave backstop", "Mellanox Technologies": "Mellanox"}.get(
            r.counterparty, r.counterparty.split(" (")[0])
        amt = f"{r.amt_b:.1f}" if r.amt_b < 10 else f"{r.amt_b:.0f}"
        lab.setdefault(r.year, []).append(f"{nm} {'≤' if r.amount_basis == 'up-to' else ''}${amt}B")
    for yr, items in lab.items():
        i = years.index(yr)
        left = yr == 2025
        # QA 2026-11-05: lift labels on short bars clear of the next bar's "n deals, undisclosed" note
        y_lab = max(tot[yr] * 0.55, tot.max() * 0.16)
        ax.annotate("\n".join(items), (i - 0.36 if left else i + 0.36, y_lab), fontsize=8.5,
                    color=INK["text"], va="center", ha="right" if left else "left")
    ax.set_xticks(x)
    ax.set_xticklabels([str(y) for y in years])
    # QA 2026-11-05: room on the right for the last year's right-hand labels (they were clipped)
    ax.set_xlim(-0.6, len(years) + (1.0 if years[-1] in lab else -0.1))
    ax.set_ylim(0, tot.max() * 1.15)
    handles = [Patch(color=TYPE_STYLE[k]["color"], label=TYPE_STYLE[k]["label"]) for k in
               ["acquisition", "acquihire-license", "equity-investment", "strategic-partnership-investment"]]
    handles.append(Patch(facecolor="#FFFFFF", edgecolor=INK["text"], hatch="///", label="'Up to' amount"))
    ax.legend(handles=handles, loc="upper left")
    _below(ax)
    c.save(fig, ax, xlabel="Announcement year", ylabel="Deal value (US$ B)", legend=False)


# --------------------------------------------------------------------------------------
# 3. Investments in customers (circular-financing debate)
# --------------------------------------------------------------------------------------
@register
def investments_in_customers_bubble():
    df = load(IC)
    df["superseded"] = df.commitment_description.str.contains("LOI")
    df["per_gw"] = df.nvidia_investment_usd_b / df.customer_compute_commitment_gw
    live = df[~df.superseded]
    gw = live.groupby("counterparty").customer_compute_commitment_gw.max().sum()
    usd = live.nvidia_investment_usd_b.sum()
    c = Chart(
        id="12-investments-in-customers-bubble",
        title=f"NVIDIA pledged up to ~${usd:.0f}B to five customers planning ~{gw:.0f} GW of compute",
        subtitle="x: NVIDIA equity committed (US$ B, log); y: customer's announced compute plan (GW); bubble area ∝ NVIDIA US$ B per GW",
        alt=(f"Bubble chart of NVIDIA investments in customers: OpenAI (about $30B in 2026, after an up-to-$100B letter of "
             f"intent tied to 10 GW), Anthropic (up to $10B, up to 1 GW), CoreWeave ($2.35B equity, >5 GW plan), xAI (up to "
             f"$2B, ~1 GW) and Poolside (up to $1B, 2 GW). In total about ${usd:.0f}B against ~{gw:.0f} GW, the core of the "
             f"circular-financing debate."),
        data=[IC], chapters=["12", "13", "18", "CS4", "CS7"],
        source="company releases; press", source_ids=sources_of(df),
        note="Hollow = reported; dashed = superseded",
    )
    fig, ax = c.figure(width=10.5, height=6.0)
    for _, r in df.iterrows():
        size = 120 + 900 * np.sqrt(r.per_gw / df.per_gw.max())
        conf = r.confidence == "confirmed"
        if r.superseded:
            ax.scatter(r.nvidia_investment_usd_b, r.customer_compute_commitment_gw, s=size, facecolor="none",
                       edgecolor=INK["muted"], lw=1.5, linestyle="--", zorder=2)
        else:
            ax.scatter(r.nvidia_investment_usd_b, r.customer_compute_commitment_gw, s=size,
                       facecolor=NV if conf else "#FFFFFF", edgecolor=NV_DARK, lw=1.8, alpha=0.85, zorder=3)
        pre = "≤" if r.investment_basis == "up-to" else ("~" if r.investment_basis == "reported" else "")
        tag = " (LOI, superseded)" if r.superseded else (" (2026 round)" if r.counterparty == "OpenAI" else "")
        txt = f"{r.counterparty}{tag}\n{pre}${r.nvidia_investment_usd_b:g}B → {r.customer_compute_commitment_gw:g} GW · ${r.per_gw:.1f}B/GW"
        dx, dy = {"Anthropic": (18, 12), "CoreWeave": (16, 4), "xAI": (16, -16), "Poolside": (12, 20)}.get(r.counterparty, (16, 0))
        if r.counterparty == "OpenAI":
            dx, dy = (-14, -36) if r.superseded else (-16, 30)
        ax.annotate(txt, (r.nvidia_investment_usd_b, r.customer_compute_commitment_gw), xytext=(dx, dy),
                    textcoords="offset points", fontsize=8.5, color=INK["title"], ha="left" if dx > 0 else "right",
                    va="center")
    ax.set_xscale("log")
    ax.set_xlim(0.5, 400)
    ax.set_ylim(0, 12.5)
    ax.set_xticks([1, 3, 10, 30, 100])
    ax.set_xticklabels(["$1B", "$3B", "$10B", "$30B", "$100B"])
    ax.text(0.01, 0.97, "Bear case: equity returns as GPU orders ('circular financing').\n"
                        "Bull case: stakes are small vs. orders and lock in multi-year demand.",
            transform=ax.transAxes, ha="left", va="top", fontsize=8.5, color=INK["text"], style="italic")
    _below(ax)
    # log x drawn here (style.save(logx=True) would reset the $-formatted ticks); badge replicated from style.py
    fig.text(0.988, 0.925, "LOG SCALE", ha="right", va="top", fontsize=8.5, fontweight="bold", color="#FFFFFF",
             bbox=dict(boxstyle="round,pad=0.3", fc=INK["text"], ec="none"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    c.save(fig, ax, xlabel="NVIDIA investment (US$ B, log scale)", ylabel="Customer compute commitment (GW)",
           legend=False)


# --------------------------------------------------------------------------------------
# 4. Deal count by layer
# --------------------------------------------------------------------------------------
@register
def deals_count_by_layer():
    df = _deals()
    order = sorted(LAYERS)
    ma = df[df.deal_type.isin(MA_TYPES)].groupby("layer").size().reindex(order, fill_value=0)
    inv = df[~df.deal_type.isin(MA_TYPES)].groupby("layer").size().reindex(order, fill_value=0)
    tot = ma + inv
    top = tot.idxmax()
    top_ma = ma.idxmax()
    c = Chart(
        id="13-deals-count-by-layer",
        title=(f"Layer {top} draws {tot[top]} of {len(df)} deals, nearly all stakes; M&A concentrates in layer "
               f"{top_ma} ({ma[top_ma]})"),
        subtitle=f"Number of logged NVIDIA deals ({len(df)}) by the stack layer each strengthens, split by M&A vs investment",
        alt=(f"Horizontal stacked bar chart of {len(df)} NVIDIA deals by layer: layer {top} (labs and ecosystem) has "
             f"{tot[top]} deals, almost all equity stakes; layer 12 (orchestration and cloud) has {tot['12']} mixing "
             f"tuck-ins like Run:ai with neocloud stakes; layer 11 (inference software) has {tot['11']}, mostly "
             f"acquisitions; silicon, CPU and networking layers have few but large deals (Mellanox, Arm, Intel)."),
        data=[DEALS], chapters=["13", "19"],
        source="NVIDIA filings and announcements; press reports", source_ids=sources_of(df),
    )
    fig, (sp, ax) = c.figure_grid(1, 2, width=10, height=6.0, gridspec_kw={"width_ratios": [0.2, 1], "wspace": 0.02})
    sp.axis("off")   # spacer for long layer names (style.save() fixes left=0.08)
    y = np.arange(len(order))[::-1]
    ax.barh(y, ma.values, color=NV, height=0.62, label="Acquisitions, acquihires (incl. failed)")
    ax.barh(y, inv.values, left=ma.values, color=SEQ_BLUE[5], height=0.62, label="Equity / partnership investments")
    for yy, t in zip(y, tot.values):
        if t:
            ax.annotate(str(t), (t, yy), xytext=(4, 0), textcoords="offset points", va="center", fontsize=9,
                        color=INK["title"], fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([LAYERS[k] for k in order])
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, tot.max() * 1.12)
    ax.legend(loc="upper right")
    _below(ax)
    c.save(fig, ax, xlabel="Number of deals", legend=False)
