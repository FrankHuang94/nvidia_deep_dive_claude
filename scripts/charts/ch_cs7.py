"""Case study CS7 - Gigawatt AI factories: xAI, Stargate and others.

Charts built from data/cs7_gigawatt_projects.csv, data/cs7_cost_per_gw.csv and
data/cs7_gw_build_inputs.csv.

Bottom-up model of a 1 GW Vera Rubin NVL72 site (all inputs in cs7_gw_build_inputs.csv):
  IT load            = site power at the meter / PUE
  all-in kW per rack = rack kW x (1 + non-rack IT overhead)          (network, storage, head nodes)
  racks              = IT load / all-in kW per rack;  GPUs = racks x 72
  rack capex         = racks x rack price
  network + storage  = rack capex x network_storage_to_rack_ratio
  facility           = facility capex per GW (power, cooling, electrical plant, shell, land)
  NVIDIA content     = rack capex x NVIDIA rack share + network/storage x NVIDIA network share
Break-even price per GPU-hour = (capital charge + power) / (GPUs x 8,760 h x utilisation), where
capital charge = IT capex x CRF(WACC, IT life) + facility x CRF(WACC, facility life) and
CRF(r, n) = r / (1 - (1 + r)^-n). Power = site MW x 8,760 h x price x (floor + (1 - floor) x util).
Excludes staff, software, maintenance, network transit, taxes and land rent.
"""
from __future__ import annotations

import numpy as np

from style import INK, NV, GEN_PAST, entity_color, load, register, sources_of, Chart

CH = ["CS7", "08", "13", "14"]


def _inputs() -> dict:
    df = load("cs7_gw_build_inputs.csv")
    return {r.input: float(r.value) for r in df.itertuples()}


def crf(rate: float, years: float) -> float:
    return rate / (1 - (1 + rate) ** -years)


def gw_model(case: str = "mid") -> dict:
    """Bottom-up 1 GW Vera Rubin site. case in {'low', 'mid', 'high'} (racks and shares)."""
    i = _inputs()
    it_mw = i["site_power_at_meter"] / i["pue"]
    kw = {"low": i["rack_kw_high"], "mid": (i["rack_kw_low"] + i["rack_kw_high"]) / 2,
          "high": i["rack_kw_low"]}[case]  # fewer, hotter racks = low capex case
    allin_kw = kw * (1 + i["non_rack_it_overhead"])
    racks = it_mw * 1000 / allin_kw
    gpus = racks * i["gpus_per_rack"]
    rack_capex = racks * i["rack_price"] / 1000  # $B
    net = rack_capex * i["network_storage_to_rack_ratio"]
    fac = {"low": i["facility_capex_low"], "high": i["facility_capex_high"],
           "mid": (i["facility_capex_low"] + i["facility_capex_high"]) / 2}[case]
    sh_r = {"low": i["nvidia_share_of_rack_low"], "high": i["nvidia_share_of_rack_high"],
            "mid": (i["nvidia_share_of_rack_low"] + i["nvidia_share_of_rack_high"]) / 2}[case] / 100
    sh_n = {"low": i["nvidia_share_network_storage_low"], "high": i["nvidia_share_network_storage_high"],
            "mid": (i["nvidia_share_network_storage_low"] + i["nvidia_share_network_storage_high"]) / 2}[case] / 100
    nv = rack_capex * sh_r + net * sh_n
    return dict(it_mw=it_mw, allin_kw=allin_kw, racks=racks, gpus=gpus, rack_capex=rack_capex, net=net,
                facility=fac, nvidia=nv, other_it=rack_capex + net - nv, total=rack_capex + net + fac)


@register
def cs7_site_scale():
    df = load("cs7_gigawatt_projects.csv")
    d = df.iloc[::-1].reset_index(drop=True)
    c = Chart(
        id="CS7-site-scale-mw",
        title="AI sites grew from ~150 MW (2024) to 0.35–0.74 GW in use in 2026; plans reach 1–5 GW",
        subtitle="Site power (MW): solid = best public evidence of power in use (hatched = repo Est.); light = "
                 "announced plan; ◆ = claim; gray = silicon undisclosed",
        alt=("Horizontal bar chart of AI site power. xAI Colossus 1 about 150 MW (repo estimate for 100,000 H100s "
             "in 2024, ~300 MW planned at 200,000 GPUs); Stargate Abilene 200+ MW live in Sept 2025 of a 1.2 GW "
             "campus; Microsoft Fairwater Wisconsin about 737 MW of IT power (Epoch estimate, 2026); xAI Colossus 2 "
             "about 350 MW of cooling seen by satellite in Jan 2026 against a 1 GW claim and a ~2 GW plan; Meta "
             "Prometheus 1 GW planned with its first phase complete in Oct 2026; Meta Hyperion up to 5 GW; "
             "Stargate UAE 1 GW (first 200 MW in 2026); HUMAIN's NVIDIA build up to 500 MW."),
        data=["cs7_gigawatt_projects.csv"],
        chapters=["CS7", "08", "13"],
        source="company releases, Epoch AI, satellite analysis, repo estimates",
        source_ids=sources_of(df),
    )
    fig, ax0 = c.figure(width=11, height=6.2)
    ax0.remove()
    ax = fig.add_axes([0.22, 0.12, 0.75, 0.71])
    y = np.arange(len(d))
    plan = d.mw_planned.fillna(0)
    op = d.mw_operating.fillna(0)
    colors = [NV if "NVIDIA" in str(sil) else INK["muted"] for sil in d.silicon]  # NVIDIA silicon vs undisclosed
    ax.barh(y, plan, color=colors, alpha=0.28, height=0.62, label="Announced plan")
    bars = ax.barh(y, op, color=colors, height=0.62, label="Power in use (best evidence)")
    for b, (_, r) in zip(bars, d.iterrows()):
        if r.confidence == "estimate":
            b.set_hatch("///")
        txt = []
        if r.mw_operating > 0:
            txt.append(f"{r.mw_operating:,.0f} MW now")
        elif r.mw_operating == 0:
            txt.append("not yet in use")
        else:
            txt.append("in use, MW undisclosed")
        if r.mw_planned and r.mw_planned != r.mw_operating:
            txt.append(f"{r.mw_planned:,.0f} MW plan")
        ax.annotate("  ·  ".join(txt), (max(r.mw_planned if r.mw_planned == r.mw_planned else 0, r.mw_operating
                                        if r.mw_operating == r.mw_operating else 0), b.get_y() + b.get_height() / 2),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.5, color=INK["text"])
        if r.mw_claimed == r.mw_claimed and r.mw_claimed:
            ax.plot([r.mw_claimed], [b.get_y() + b.get_height() / 2], marker="D", color=INK["title"], ms=8)
            ax.annotate("claim", (r.mw_claimed, b.get_y() + b.get_height() / 2), xytext=(0, 9),
                        textcoords="offset points", ha="center", fontsize=8, color=INK["title"])
    ax.axvline(1000, color=INK["base"], ls="--", lw=1)
    ax.text(1010, len(d) - 0.45, "1 GW", fontsize=8.5, color=INK["text"])
    ax.set_yticks(y)
    ax.set_yticklabels([f"{p} ({str(r)[:4]})" for p, r in zip(d.project, d.first_power)], fontsize=9)
    ax.set_xlim(0, 7600)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    ax.legend(loc="lower right", fontsize=8.5)
    c.save(fig, ax, xlabel="Site power (MW)", legend=False, top=0.85, bottom=0.12)


@register
def cs7_cost_per_gw():
    df = load("cs7_cost_per_gw.csv")
    m = gw_model("mid")
    lo, hi = gw_model("low"), gw_model("high")
    comps = ["nvidia_or_gpu", "other_it", "facility", "unallocated"]
    names = {"nvidia_or_gpu": "NVIDIA / GPU content", "other_it": "Other IT (memory, ODM, network, storage)",
             "facility": "Facility (power, cooling, shell, land)", "unallocated": "Not split by the source"}
    cols = {"nvidia_or_gpu": NV, "other_it": "#86B6EF", "facility": "#256ABF", "unallocated": INK["base"]}
    order = ["NVIDIA CEO (Aug 2025)", "Repo bottom-up: Vera Rubin (Est.)", "Bernstein (2026 note)",
             "Barclays (Sep 2025)", "Bernstein (Oct 2025)", "Bloomberg: Abilene (2025)"]
    piv = df.pivot_table(index="estimate", columns="component", values="value_usd_b", aggfunc="sum").reindex(
        columns=comps).fillna(0)
    piv.loc["Repo bottom-up: Vera Rubin (Est.)"] = [m["nvidia"], m["other_it"], m["facility"], 0]
    piv = piv.reindex(order[::-1])
    rng = df.dropna(subset=["low_usd_b"]).groupby("estimate")[["low_usd_b", "high_usd_b"]].first()
    rng.loc["Repo bottom-up: Vera Rubin (Est.)"] = [lo["total"], hi["total"]]
    c = Chart(
        id="CS7-cost-per-gw-estimates",
        title=f"A gigawatt of AI capacity costs ~$30–60B; the repo's Vera Rubin build-up lands at ~${m['total']:.0f}B",
        subtitle="Capex per GW by estimator and component ($B); whiskers = stated range; NVIDIA CEO split = "
                 "NVIDIA content vs the rest",
        alt=(f"Stacked horizontal bar chart of capital cost per gigawatt of AI data center. NVIDIA's CEO (Aug 2025): "
             f"$50-60B with about $35B of NVIDIA content. Repo bottom-up for Vera Rubin NVL72 (estimate): about "
             f"${m['total']:.0f}B (range ${lo['total']:.0f}-{hi['total']:.0f}B), of which NVIDIA about "
             f"${m['nvidia']:.0f}B, other IT about ${m['other_it']:.0f}B and facility about ${m['facility']:.0f}B. "
             "Bernstein's 2026 note: up to $39.5B for Vera Rubin. Barclays: $32.5-42B. Bernstein (Oct 2025): "
             "about $35B, 39% GPUs, 13% networking and about one-third electrical and mechanical. Bloomberg on "
             "Abilene: about $30B including $17B of chips."),
        data=["cs7_cost_per_gw.csv", "cs7_gw_build_inputs.csv"],
        chapters=["CS7", "08", "14", "13"],
        source="NVIDIA, Bernstein, Barclays, Bloomberg, Morgan Stanley BOM; repo model",
        source_ids=sources_of(df) + [s for s in sources_of(load("cs7_gw_build_inputs.csv"))
                                      if s not in sources_of(df)],
    )
    fig, ax0 = c.figure(width=11, height=6.0)
    ax0.remove()
    ax = fig.add_axes([0.24, 0.25, 0.73, 0.58])
    y = np.arange(len(piv))
    left = np.zeros(len(piv))
    for comp in comps:
        vals = piv[comp].values
        bars = ax.barh(y, vals, left=left, color=cols[comp], height=0.6, label=names[comp])
        for b, v, est in zip(bars, vals, piv.index):
            if v >= 4:
                ax.annotate(f"{v:.0f}", (b.get_x() + v / 2, b.get_y() + b.get_height() / 2), ha="center",
                            va="center", fontsize=8.5, color="white" if comp != "unallocated" else INK["title"])
        left += vals
    for yi, est in zip(y, piv.index):
        tot = piv.loc[est].sum()
        if est in rng.index:
            l_, h_ = rng.loc[est]
            if est == "NVIDIA CEO (Aug 2025)":
                l_, h_ = 50, 60
            ax.plot([l_, h_], [yi, yi], color=INK["title"], lw=1.4)
            ax.plot([l_, l_], [yi - 0.12, yi + 0.12], color=INK["title"], lw=1.4)
            ax.plot([h_, h_], [yi - 0.12, yi + 0.12], color=INK["title"], lw=1.4)
            ax.annotate(f"${tot:.1f}B", (max(tot, h_), yi), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=8.8, color=INK["title"], fontweight="bold")
        else:
            ax.annotate(f"${tot:.1f}B", (tot, yi), xytext=(6, 0), textcoords="offset points", va="center",
                        fontsize=8.8, color=INK["title"], fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels(piv.index, fontsize=9)
    ax.set_xlim(0, 72)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    ax.legend(loc="upper center", bbox_to_anchor=(0.42, -0.17), ncol=2, fontsize=8.5)
    c.save(fig, ax, xlabel="Capex per GW ($B)", legend=False, top=0.85, bottom=0.2)


@register
def cs7_breakeven_utilisation():
    i = _inputs()
    m = gw_model("mid")
    util = np.linspace(0.4, 1.0, 61)
    it_capex = m["rack_capex"] + m["net"]

    def be(u, wacc):
        cap = it_capex * crf(wacc, i["it_life_years"]) + m["facility"] * crf(wacc, i["facility_life_years"])
        power = i["site_power_at_meter"] * 8760 * 1000 * i["electricity_price"] / 1e9 * (
            i["power_draw_floor"] + (1 - i["power_draw_floor"]) * u)
        return (cap + power) * 1e9 / (m["gpus"] * 8760 * u)

    w_lo, w_hi = i["wacc_low"] / 100, i["wacc_high"] / 100
    lo_line = [be(u, w_lo) for u in util]
    hi_line = [be(u, w_hi) for u in util]
    b89_lo, b89_hi = be(0.89, w_lo), be(0.89, w_hi)
    b60_hi = be(0.60, w_hi)
    c = Chart(
        id="CS7-breakeven-vs-utilization",
        title=f"Est.: a 1 GW Vera Rubin site breaks even at ~${b89_lo:.1f}–{b89_hi:.1f}/GPU-hr at 89% use",
        subtitle=f"Break-even $/GPU-hour vs utilisation: capital charge + power only (excl. staff, software, "
                 f"taxes); ~{m['gpus'] / 1000:,.0f}k GPUs, ~${it_capex + m['facility']:.0f}B capex",
        alt=(f"Line chart of the estimated break-even price per GPU-hour for a 1 GW Vera Rubin NVL72 site with about "
             f"{m['gpus'] / 1000:,.0f} thousand GPUs and about ${it_capex + m['facility']:.0f}B of capex, counting "
             f"only the capital charge (6-year IT life, 20-year facility life) and power at $0.081/kWh. At 8% cost "
             f"of capital the break-even falls from about ${be(0.4, w_lo):.1f} at 40% utilisation to "
             f"${be(1.0, w_lo):.1f} at 100%; at 12% from ${be(0.4, w_hi):.1f} to ${be(1.0, w_hi):.1f}. At 89% "
             f"utilisation (Meta-style 11% hot spares) it is ${b89_lo:.1f}-{b89_hi:.1f}. Utilisation moves the "
             "answer far more than the cost of capital."),
        data=["cs7_gw_build_inputs.csv"],
        chapters=["CS7", "14", "08", "12"],
        source="repo model on Morgan Stanley BOM, EIA power price, hyperscaler useful lives",
        source_ids=sources_of(load("cs7_gw_build_inputs.csv")),
    )
    fig, ax = c.figure(width=11, height=5.8)
    ax.fill_between(util * 100, lo_line, hi_line, color=NV, alpha=0.15)
    ax.plot(util * 100, lo_line, color=NV, label=f"Cost of capital {i['wacc_low']:.0f}%")
    ax.plot(util * 100, hi_line, color="#3F6B00", ls="--", label=f"Cost of capital {i['wacc_high']:.0f}%")
    for u, lab in [(0.89, "89%: 8 of 72 GPUs held as spares"), (0.6, "60%")]:
        ax.axvline(u * 100, color=INK["base"], lw=1, ls=":")
        ax.text(u * 100 - 0.6, max(hi_line) * 0.97, lab, fontsize=8.5, color=INK["text"], va="top", ha="right")
    ax.annotate(f"${b89_lo:.2f}–{b89_hi:.2f}", (89, b89_hi), xytext=(8, 14), textcoords="offset points",
                fontsize=9, color=INK["title"], fontweight="bold")
    ax.annotate(f"${b60_hi:.2f}", (60, b60_hi), xytext=(8, 6), textcoords="offset points", fontsize=9,
                color=INK["title"], fontweight="bold")
    ax.set_xlim(40, 100)
    ax.set_ylim(0, max(hi_line) * 1.05)
    ax.legend(loc="lower left")
    c.save(fig, ax, xlabel="Average utilisation of installed GPUs (%)", ylabel="Break-even $ per GPU-hour",
           legend=False, top=0.84, bottom=0.13)
