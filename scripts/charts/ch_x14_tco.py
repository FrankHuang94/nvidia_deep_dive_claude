"""Chapter 14 - training vs. inference economics: charts from the TCO model in scripts/tco/.

Each builder re-runs the (fast, deterministic) model in scripts/tco/tco_model.py, which reads
data/x14_tco_scenarios.csv, data/tco_model_inputs.csv, data/l08_power_per_gpu.csv,
data/cs3_tpu_economics.csv and data/inference_benchmarks.csv, and writes scripts/tco/outputs/*.csv.
All plotted values are estimates; "modelled" throughput (Vera Rubin, Helios, TPU, Trainium) is hatched.
"""
from __future__ import annotations

import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import GEN_PAST, INK, NV, NV_DARK, Chart, entity_color, load, register, sources_of

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tco"))
import tco_model as tm  # noqa: E402

CH = ["14"]
DATA_FILES = ["x14_tco_scenarios.csv", "tco_model_inputs.csv", "l08_power_per_gpu.csv", "cs3_tpu_economics.csv",
              "inference_benchmarks.csv"]
SHORT = {
    "H200 HGX": "H200 HGX", "B200 HGX": "B200 HGX", "GB300 NVL72": "GB300 NVL72",
    "Vera Rubin NVL72": "Vera Rubin NVL72", "MI355X platform": "MI355X (8-GPU)", "Helios (MI455X)": "Helios MI455X",
    "TPU v7 Ironwood (external)": "TPU v7 (external owner)", "TPU v7 Ironwood (Google internal)": "TPU v7 (Google itself)",
    "Trainium2 (Trn2 UltraServer)": "Trainium2", "Trainium3 (Trn3 UltraServer)": "Trainium3",
}
COMP_COLORS = {  # capex lines on the repo's sequential blue ramp, opex in neutrals; margin hatched
    "hardware": "#104281", "vendor_margin": "#3987E5", "network_storage": "#86B6EF", "cost_of_capital": "#CDE2FB",
    "facility": "#7A7A7A", "power": "#C98500", "ops": "#B5B5B5",
}
COMP_SHORT = {"hardware": "System\nat cost", "vendor_margin": "Vendor\nmargin", "network_storage": "Network\n& storage",
              "cost_of_capital": "Cost of\ncapital", "facility": "Facility", "power": "Power", "ops": "Ops"}
NOTE = "Est.: repo TCO model (scripts/tco); hatched = modelled throughput"


def _margins(fig, **over):
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


@lru_cache(maxsize=1)
def _run():
    return tm.run(write=True, verbose=False)


@lru_cache(maxsize=1)
def _model():
    return tm.Model()


def _scen():
    return load("x14_tco_scenarios.csv")


def _sids(*extra) -> list[str]:
    ids = sources_of(_scen())
    pri = ["S14000", "S621", "S622", "S332", "S625", "S626"]
    out = [s for s in pri if s in ids] + [s for s in ids if s not in pri]
    for e in extra:
        if e not in out:
            out.append(e)
    return out


def _color(system: str) -> str:
    if system.startswith(("H200", "B200")):
        return GEN_PAST
    if system.startswith(("GB300", "Vera")):
        return NV
    if system.startswith(("MI355", "Helios")):
        return entity_color("AMD")
    if system.startswith("TPU"):
        return entity_color("Google")
    return entity_color("AWS")


def _measured(system: str) -> bool:
    return system in ("H200 HGX", "B200 HGX", "GB300 NVL72", "MI355X platform")


def _fmt_usd(v: float) -> str:
    if v >= 1:
        return f"${v:.2f}"
    if v >= 0.1:
        return f"${v:.2f}"
    return f"${v:.3f}"


# --------------------------------------------------------------------------------------
# 1. GB300 cost-stack waterfall ($/M tokens)
# --------------------------------------------------------------------------------------
@register
def x14_gb300_cost_waterfall():
    out = _run()
    st = out["cost_stack"]
    g = st[st.system == "GB300 NVL72"].reset_index(drop=True)
    r = out["results"].set_index("system").loc["GB300 NVL72"]
    total = g.usd_per_m_tokens.sum()
    margin = g[g.component == "vendor_margin"].usd_per_m_tokens.iloc[0]
    capex_like = g[g.component.isin(["hardware", "vendor_margin", "network_storage", "cost_of_capital"])].usd_per_m_tokens.sum()
    power = g[g.component == "power"].usd_per_m_tokens.iloc[0]
    c = Chart(
        id="14-tco-gb300-cost-waterfall",
        title=(f"Est.: a GB300 NVL72 token costs ~${total:.2f}/M; NVIDIA's margin is ~{margin / total * 100:.0f}%, "
               f"electricity only ~{power / total * 100:.0f}%"),
        subtitle=("Owner cost per million total tokens, DeepSeek-R1 1k/1k at 50 tok/s/user, 70% utilization, 6-yr life, "
                  "8% cost of capital, $0.081/kWh, PUE 1.15"),
        alt=(f"Waterfall chart building GB300 NVL72's estimated cost of about ${total:.3f} per million tokens: rack hardware at "
             f"NVIDIA's and suppliers' cost ${g.usd_per_m_tokens[0]:.3f}, NVIDIA's gross margin in the price ${margin:.3f} "
             f"({margin / total * 100:.0f}%), scale-out network and storage ${g.usd_per_m_tokens[2]:.3f}, cost of capital "
             f"${g.usd_per_m_tokens[3]:.3f}, facility ${g.usd_per_m_tokens[4]:.3f}, electricity ${power:.3f} "
             f"({power / total * 100:.0f}%) and operations ${g.usd_per_m_tokens[6]:.3f}. Capital items are "
             f"{capex_like / total * 100:.0f}% of the total; the GPU-hour costs about ${r.usd_per_hour_installed:.2f} installed."),
        data=DATA_FILES, chapters=CH + ["08", "13"], source="repo TCO model on InferenceX throughput and analyst rack prices",
        source_ids=_sids(), note="Est.: repo TCO model (scripts/tco); hatched = vendor gross margin inside the price",
    )
    fig, ax = c.figure(width=10.8, height=6.0)
    cum = 0.0
    xs = np.arange(len(g) + 1)
    for i, row in g.iterrows():
        v = row.usd_per_m_tokens
        b = ax.bar(i, v, bottom=cum, color=COMP_COLORS[row.component], width=0.62, zorder=2,
                   edgecolor="white" if row.component != "cost_of_capital" else "#86B6EF", linewidth=0.8)
        if row.component == "vendor_margin":
            b.patches[0].set_hatch("///")
        ax.annotate(f"${v:.3f}\n{row.share * 100:.0f}%", (i, cum + v), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.6, color=INK["title"])
        if i < len(g) - 1:
            ax.plot([i + 0.31, i + 0.69], [cum + v, cum + v], color=INK["muted"], lw=0.9, zorder=1)
        cum += v
    ax.plot([len(g) - 1 + 0.31, len(g) - 0.31], [cum, cum], color=INK["muted"], lw=0.9, zorder=1)
    ax.bar(len(g), cum, color=NV, width=0.62, zorder=2)
    ax.annotate(f"${cum:.3f}/M\n(${r.usd_per_hour_installed:.2f}/GPU-hr)", (len(g), cum), xytext=(0, 3),
                textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold", color=NV_DARK)
    labels = [COMP_SHORT[k] for k in g.component] + ["Total"]
    ax.set_xticks(xs, labels, fontsize=8.8)
    ax.set_ylim(0, cum * 1.22)
    ax.axhspan(0, 0, color="none")
    ax.text(0.01, 0.96, "Capital (blue) vs operating (grey/amber) costs", transform=ax.transAxes, fontsize=8.6,
            color=INK["text"], va="top")
    c.save(fig, ax, ylabel="US$ per million tokens (Est.)", legend=False, bottom=0.16)


# --------------------------------------------------------------------------------------
# 2. Small-multiple waterfalls, one per system
# --------------------------------------------------------------------------------------
@register
def x14_cost_stack_waterfalls():
    out = _run()
    st = out["cost_stack"]
    res = out["results"].set_index("system")
    systems = ["GB300 NVL72", "Vera Rubin NVL72", "Helios (MI455X)", "MI355X platform", "TPU v7 Ironwood (external)",
               "Trainium3 (Trn3 UltraServer)", "Trainium2 (Trn2 UltraServer)", "H200 HGX"]
    tot = {s: res.loc[s, "usd_per_m_tokens"] for s in systems}
    msh = {s: res.loc[s, "vendor_margin_share_of_cost"] for s in systems}
    c = Chart(
        id="14-tco-cost-stack-waterfalls-by-system",
        title=(f"Est.: vendor margin is {min(msh.values()) * 100:.0f}–{max(msh.values()) * 100:.0f}% of each token's cost; "
               f"throughput, not margin, sets the {max(tot.values()) / min(tot.values()):.0f}× spread"),
        subtitle="Cost stack per million tokens by system (own y-scale per panel) · DeepSeek-R1 1k/1k, 50 tok/s/user, base case",
        alt=("Eight small waterfall charts of estimated cost per million tokens: " +
             "; ".join(f"{SHORT[s]} ${tot[s]:.3f} with vendor margin {msh[s] * 100:.0f}%" for s in systems) +
             ". Vendor gross margin is a minority of every stack; totals differ mainly because tokens per accelerator "
             "differ, and Vera Rubin, Helios, TPU and Trainium throughput is modelled rather than measured."),
        data=DATA_FILES, chapters=CH + ["15"], source="repo TCO model", source_ids=_sids(),
        note="Est.: repo TCO model (scripts/tco); hatched = vendor gross margin; Σ bar = total",
    )
    fig, axes = c.figure_grid(2, 4, width=12.5, height=7.2)
    for ax, s in zip(axes.flat, systems):
        g = st[st.system == s].reset_index(drop=True)
        cum = 0.0
        for i, row in g.iterrows():
            v = row.usd_per_m_tokens
            b = ax.bar(i, v, bottom=cum, color=COMP_COLORS[row.component], width=0.7, zorder=2,
                       edgecolor="white" if row.component != "cost_of_capital" else "#86B6EF", linewidth=0.6)
            if row.component == "vendor_margin":
                b.patches[0].set_hatch("///")
            cum += v
        ax.bar(len(g), cum, color=_color(s), width=0.7, zorder=2)
        ax.annotate(_fmt_usd(cum), (len(g), cum), xytext=(0, 2), textcoords="offset points", ha="center",
                    va="bottom", fontsize=8.6, fontweight="bold", color=INK["title"])
        ax.set_ylim(0, cum * 1.25)
        ax.set_xticks(range(len(g) + 1), ["S", "M", "N", "C", "F", "P", "O", "Σ"], fontsize=8)
        tag = "measured" if _measured(s) else "modelled"
        ax.set_title(f"{SHORT[s]} ({tag})", fontsize=9.2, loc="left", color=INK["title"])
        ax.text(0.03, 0.97, f"vendor margin {msh[s] * 100:.0f}%", transform=ax.transAxes, ha="left", va="top",
                fontsize=8, color=INK["text"])
        ax.tick_params(axis="y", labelsize=8)
    handles = [Patch(facecolor=COMP_COLORS[k], edgecolor="#86B6EF" if k == "cost_of_capital" else "white",
                     hatch="///" if k == "vendor_margin" else None,
                     label=f"{'SMNCFPO'[i]} = {lab}") for i, (k, lab) in enumerate(tm.COMPONENTS)]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.9), ncol=4, fontsize=8.2, frameon=False)
    _margins(fig, left=0.06, right=0.985, hspace=0.42, wspace=0.28, top=0.76)
    c.save(fig, list(axes.flat), legend=False, top=0.76, bottom=0.1)


# --------------------------------------------------------------------------------------
# 3. $/accelerator-hour stack with SemiAnalysis cross-check
# --------------------------------------------------------------------------------------
@register
def x14_cost_per_accelerator_hour():
    out = _run()
    st = out["cost_stack"]
    res = out["results"].set_index("system")
    order = res.sort_values("usd_per_hour_installed").index.tolist()
    gb = res.loc["GB300 NVL72"]
    vr = res.loc["Vera Rubin NVL72"]
    tpu = res.loc["TPU v7 Ironwood (external)"]
    c = Chart(
        id="14-tco-cost-per-accelerator-hour",
        title=(f"Est.: an installed GB300 GPU-hour costs ~${gb.usd_per_hour_installed:.2f}, Vera Rubin ~${vr.usd_per_hour_installed:.2f}, "
               f"a TPU v7 ~${tpu.usd_per_hour_installed:.2f}"),
        subtitle="Owner cost per installed accelerator-hour by component, US$ · ◆ = SemiAnalysis owner TCO (cross-check) · base case",
        alt=("Stacked horizontal bars of estimated owner cost per installed accelerator-hour: " +
             ", ".join(f"{SHORT[s]} ${res.loc[s, 'usd_per_hour_installed']:.2f}" for s in order) +
             f". SemiAnalysis's owner TCO figures are close for GB300 NVL72 (${gb.sa_owner_tco_usd_per_hour:.2f}) and lower for "
             f"H200 (${res.loc['H200 HGX', 'sa_owner_tco_usd_per_hour']:.2f}) and MI355X "
             f"(${res.loc['MI355X platform', 'sa_owner_tco_usd_per_hour']:.2f}). Capital charges are most of every bar; "
             "TPU capex is calibrated to SemiAnalysis's TPU-to-GB300 ratio and Trainium capex is a repo estimate."),
        data=DATA_FILES, chapters=CH + ["12", "08"], source="repo TCO model; SemiAnalysis owner TCO", source_ids=_sids(),
        note="Est.: repo TCO model (scripts/tco); hatched = vendor gross margin inside the price",
    )
    fig, ax = c.figure(width=11, height=6.4)
    y = np.arange(len(order))
    left = np.zeros(len(order))
    for key, lab in tm.COMPONENTS:
        vals = np.array([st[(st.system == s) & (st.component == key)].usd_per_accelerator_hour.iloc[0] for s in order])
        b = ax.barh(y, vals, left=left, color=COMP_COLORS[key], height=0.62, zorder=2, label=lab,
                    edgecolor="white" if key != "cost_of_capital" else "#86B6EF", linewidth=0.6)
        if key == "vendor_margin":
            for p in b.patches:
                p.set_hatch("///")
        left += vals
    for yi, s in zip(y, order):
        sa = res.loc[s, "sa_owner_tco_usd_per_hour"]
        if sa == sa:
            ax.scatter(sa, yi, marker="D", s=46, color="white", edgecolor=INK["title"], linewidth=1.2, zorder=4)
        tag = "" if not res.loc[s, "capex_calibrated"] else "  (capex calibrated)"
        if s.startswith("Trainium") or s.startswith("MI355") or s.startswith("Helios"):
            tag = "  (capex = repo Est.)" if not s.startswith("Helios") else "  (capex = Futurum Est.)"
        ax.annotate(f"${res.loc[s, 'usd_per_hour_installed']:.2f}{tag}", (left[yi], yi), xytext=(5, 0),
                    textcoords="offset points", va="center", fontsize=8.6, color=INK["title"])
    ax.set_yticks(y, [SHORT[s] for s in order], fontsize=9)
    ax.set_xlim(0, left.max() * 1.42)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Line2D([0], [0], marker="D", ls="", color="white", markeredgecolor=INK["title"], markersize=7,
                          label="SemiAnalysis owner TCO"))
    ax.legend(handles=handles, loc="lower right", fontsize=8.2, frameon=False, ncol=2)
    _margins(fig, left=0.17, right=0.98)
    c.save(fig, ax, xlabel="US$ per installed accelerator-hour (Est.)", legend=False)


# --------------------------------------------------------------------------------------
# 4. $/M tokens by system with P10-P90 ranges
# --------------------------------------------------------------------------------------
@register
def x14_cost_per_million_tokens_ranges():
    res = _run()["results"].sort_values("usd_per_m_tokens", ascending=False).reset_index(drop=True)
    r = res.set_index("system")
    gb = r.loc["GB300 NVL72"]
    c = Chart(
        id="14-tco-cost-per-million-tokens-ranges",
        title=(f"Est.: at 50 tok/s/user a GB300 token costs ~${gb.usd_per_m_tokens:.2f}/M, "
               f"{r.loc['TPU v7 Ironwood (external)', 'usd_per_m_tokens'] / gb.usd_per_m_tokens:.1f}× below TPU v7, "
               f"{r.loc['MI355X platform', 'usd_per_m_tokens'] / gb.usd_per_m_tokens:.0f}× below MI355X"),
        subtitle="Owner cost per million total tokens, US$ (log scale) · bar = base case, whisker = Monte Carlo P10–P90 · hatched = modelled throughput",
        alt=("Log-scale horizontal bar chart of estimated owner cost per million DeepSeek-R1 tokens at 50 tokens/s per user, "
             "base case with P10 to P90 range: " +
             "; ".join(f"{SHORT[s]} ${r.loc[s, 'usd_per_m_tokens']:.3f} ({_fmt_usd(r.loc[s, 'usd_per_m_tokens_p10'])}–"
                       f"{_fmt_usd(r.loc[s, 'usd_per_m_tokens_p90'])}){'' if _measured(s) else ' modelled'}"
                       for s in res.system[::-1]) +
             ". Rack-scale NVIDIA systems lead at this operating point; at 100 tokens/s per user the TPU and Trainium3 "
             "estimates draw level with GB300."),
        data=DATA_FILES, chapters=CH + ["11", "15"], source="repo TCO model on InferenceX throughput", source_ids=_sids(), note=NOTE,
    )
    fig, ax = c.figure(width=11, height=6.4)
    y = np.arange(len(res))
    cols = [_color(s) for s in res.system]
    bars = ax.barh(y, res.usd_per_m_tokens, color=cols, height=0.6, zorder=2)
    for b, s in zip(bars, res.system):
        if not _measured(s):
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yi, row in res.iterrows():
        ax.plot([row.usd_per_m_tokens_p10, row.usd_per_m_tokens_p90], [yi, yi], color=INK["title"], lw=1.3, zorder=3)
        for v in (row.usd_per_m_tokens_p10, row.usd_per_m_tokens_p90):
            ax.plot([v, v], [yi - 0.14, yi + 0.14], color=INK["title"], lw=1.3, zorder=3)
        ax.annotate(f"{_fmt_usd(row.usd_per_m_tokens)}  ({_fmt_usd(row.usd_per_m_tokens_p10)}–{_fmt_usd(row.usd_per_m_tokens_p90)})",
                    (row.usd_per_m_tokens_p90, yi), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.6,
                    color=INK["title"])
    ax.axvline(gb.usd_per_m_tokens, color=NV_DARK, lw=0.9, ls=":", zorder=1)
    ax.set_xscale("log")
    ax.set_xlim(0.04, 12)
    ax.set_yticks(y, [SHORT[s] + ("" if _measured(s) else " ·m") for s in res.system], fontsize=9)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    handles = [Patch(facecolor=NV, label="NVIDIA rack-scale"), Patch(facecolor=GEN_PAST, label="NVIDIA 8-GPU HGX"),
               Patch(facecolor=entity_color("AMD"), label="AMD"), Patch(facecolor=entity_color("Google"), label="Google TPU"),
               Patch(facecolor=entity_color("AWS"), label="AWS Trainium"),
               Patch(facecolor="#B5B5B5", hatch="///", edgecolor="white", label="·m = modelled throughput")]
    ax.legend(handles=handles, loc="upper right", fontsize=8.4, frameon=False)
    _margins(fig, left=0.19, right=0.98)
    c.save(fig, ax, xlabel="US$ per million tokens (Est.)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 5. tokens per MW by system with ranges
# --------------------------------------------------------------------------------------
@register
def x14_tokens_per_mw_ranges():
    res = _run()["results"].sort_values("tokens_per_s_per_mw").reset_index(drop=True)
    r = res.set_index("system")
    gb = r.loc["GB300 NVL72", "tokens_per_s_per_mw"]
    c = Chart(
        id="14-tco-tokens-per-mw-ranges",
        title=(f"Est.: per MW, GB300 NVL72 serves ~{gb / 1e6:.1f}M tokens/s, ~{gb / r.loc['TPU v7 Ironwood (external)', 'tokens_per_s_per_mw']:.0f}× a TPU v7 "
               f"and ~{gb / r.loc['MI355X platform', 'tokens_per_s_per_mw']:.0f}× an MI355X"),
        subtitle="Total tokens/s per MW of facility power (IT all-in × PUE 1.15), DeepSeek-R1 1k/1k at 50 tok/s/user · whisker = P10–P90 · hatched = modelled",
        alt=("Log-scale horizontal bar chart of estimated tokens per second per megawatt at the utility meter: " +
             "; ".join(f"{SHORT[s]} {r.loc[s, 'tokens_per_s_per_mw'] / 1e6:.2f} million"
                       f"{'' if _measured(s) else ' (modelled)'}" for s in res.system[::-1]) +
             ". These are lower than chart 08-tokens-per-mw-by-system because this model counts PUE; rankings match."),
        data=DATA_FILES, chapters=CH + ["08", "11"], source="repo TCO model on InferenceX throughput and SemiAnalysis power",
        source_ids=_sids(), note=NOTE,
    )
    fig, ax = c.figure(width=11, height=6.3)
    y = np.arange(len(res))
    bars = ax.barh(y, res.tokens_per_s_per_mw / 1e6, color=[_color(s) for s in res.system], height=0.6, zorder=2)
    for b, s in zip(bars, res.system):
        if not _measured(s):
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yi, row in res.iterrows():
        lo, hi = row.tokens_per_s_per_mw_p10 / 1e6, row.tokens_per_s_per_mw_p90 / 1e6
        ax.plot([lo, hi], [yi, yi], color=INK["title"], lw=1.3, zorder=3)
        for v in (lo, hi):
            ax.plot([v, v], [yi - 0.14, yi + 0.14], color=INK["title"], lw=1.3, zorder=3)
        ax.annotate(f"{row.tokens_per_s_per_mw / 1e6:.2f}M  ({row.facility_kw_per_accelerator:.2f} kW/accel.)", (hi, yi),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=8.6, color=INK["title"])
    ax.set_xscale("log")
    ax.set_xlim(0.1, 30)
    ax.set_yticks(y, [SHORT[s] + ("" if _measured(s) else " ·m") for s in res.system], fontsize=9)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)
    _margins(fig, left=0.19, right=0.98)
    c.save(fig, ax, xlabel="Million tokens/s per MW at the meter (Est.)", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 6-7. Tornado charts
# --------------------------------------------------------------------------------------
def _fmt_in(v: float) -> str:
    if abs(v) >= 100:
        return f"{v:,.0f}"
    if abs(v) >= 10:
        return f"{v:.0f}"
    if abs(v) >= 1:
        return f"{v:.2f}".rstrip("0").rstrip(".")
    return f"{v:.3f}".rstrip("0").rstrip(".")


def _tornado(ax, t: pd.DataFrame, base: float, fmt) -> None:
    t = t.sort_values("swing").reset_index(drop=True)
    for i, row in t.iterrows():
        lo, hi = row.result_at_low, row.result_at_high
        for v, inp in ((lo, row.low_input), (hi, row.high_input)):
            col = "#256ABF" if v < base else "#C4314B"
            ax.barh(i, v - base, left=base, color=col, height=0.62, zorder=2)
            ha = "left" if v >= base else "right"
            dx = 4 if v >= base else -4
            ax.annotate(f"{_fmt_in(inp)} → {fmt(v)}", (v, i), xytext=(dx, 0), textcoords="offset points", ha=ha,
                        va="center", fontsize=8.1, color=INK["title"])
    ax.axvline(base, color=INK["title"], lw=1.1, zorder=3)
    ax.set_yticks(range(len(t)), t.label, fontsize=8.9)
    ax.grid(axis="x", color=INK["grid"], lw=0.7)
    ax.grid(axis="y", visible=False)


@register
def x14_gb300_tornado():
    t = _run()["tornado"]
    t = t[t.case.str.startswith("GB300")]
    base = t.base_result.iloc[0]
    top = t.sort_values("swing", ascending=False).iloc[0]
    elec = t[t.parameter == "electricity_usd_per_kwh"].iloc[0]
    c = Chart(
        id="14-tco-gb300-tornado",
        title=(f"Est.: utilization moves GB300's ${base:.2f}/M token cost from ${top.result_at_high:.2f} to ${top.result_at_low:.2f}; "
               f"power price barely matters"),
        subtitle="One-at-a-time sensitivity of GB300 NVL72 US$ per million tokens · label = input value → result · blue = cheaper, red = dearer",
        alt=("Tornado chart of GB300 NVL72's estimated cost per million tokens around a base of "
             f"${base:.3f}: " + "; ".join(f"{row.label} {_fmt_in(row.low_input)} to {_fmt_in(row.high_input)} gives "
                                          f"${row.result_at_low:.3f} to ${row.result_at_high:.3f}"
                                          for row in t.sort_values('swing', ascending=False).itertuples()) +
             f". Electricity from ${elec.low_input:.2f} to ${elec.high_input:.2f} per kWh moves the result by under a cent per million."),
        data=DATA_FILES, chapters=CH + ["12"], source="repo TCO model", source_ids=_sids(), note="Est.: repo TCO model (scripts/tco)",
    )
    fig, ax = c.figure(width=11, height=6.4)
    _tornado(ax, t, base, lambda v: f"${v:.3f}")
    lo = t[["result_at_low", "result_at_high"]].min().min()
    hi = t[["result_at_low", "result_at_high"]].max().max()
    ax.set_xlim(lo - (base - lo) * 0.9, hi + (hi - base) * 0.45)
    ax.text(base, len(t) - 0.3, f"base ${base:.3f}/M", ha="center", va="bottom", fontsize=8.6, color=INK["title"],
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"), zorder=5)
    _margins(fig, left=0.27, right=0.98)
    c.save(fig, ax, xlabel="GB300 NVL72 US$ per million tokens (Est.)", legend=False)


@register
def x14_gb300_vs_tpu_ratio_tornado():
    t = _run()["tornado"]
    t = t[t.case.str.startswith("TPU")]
    base = t.base_result.iloc[0]
    op = _run()["operating_points"]
    o100 = op[op.interactivity_tok_s_per_user == 100].set_index("system")
    r100 = o100.loc["TPU v7 Ironwood (external)", "usd_per_m_tokens"] / o100.loc["GB300 NVL72", "usd_per_m_tokens"]
    fin = t[t.parameter.str.startswith("All:")]
    c = Chart(
        id="14-tco-gb300-vs-tpu-ratio-tornado",
        title=(f"Est.: throughput assumptions, not finance, decide GB300 vs TPU; base TPU cost {base:.1f}× GB300's, "
               f"~{r100:.1f}× at 100 tok/s/user"),
        subtitle="One-at-a-time sensitivity of (TPU v7 external $/M tokens) ÷ (GB300 NVL72 $/M tokens) at 50 tok/s/user · >1 = GB300 cheaper",
        alt=(f"Tornado chart of the ratio of TPU v7 to GB300 NVL72 estimated cost per token, base {base:.2f}: " +
             "; ".join(f"{row.label} gives {row.result_at_low:.2f} to {row.result_at_high:.2f}"
                       for row in t.sort_values('swing', ascending=False).itertuples()) +
             f". Financial inputs (cost of capital, life, power price, utilization, facility) move the ratio by less than "
             f"{fin.swing.max():.2f}; at 100 tokens/s per user the ratio is about {r100:.2f}, close to parity."),
        data=DATA_FILES, chapters=CH + ["15", "CS3"], source="repo TCO model; SemiAnalysis TPU vs Blackwell", source_ids=_sids(),
        note="Est.: TPU throughput is modelled from SemiAnalysis's TPU-vs-B200 result",
    )
    fig, ax = c.figure(width=11, height=6.4)
    _tornado(ax, t, base, lambda v: f"{v:.2f}×")
    ax.axvline(1.0, color=entity_color("Google"), lw=1.4, ls="--", zorder=1)
    ax.text(1.02, 0.2, "parity (1.0×)", color=entity_color("Google"), fontsize=8.6, va="bottom")
    ax.set_xlim(0.5, 5.6)
    ax.text(base, len(t) - 0.3, f"base {base:.2f}×", ha="center", va="bottom", fontsize=8.6, color=INK["title"],
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"), zorder=5)
    _margins(fig, left=0.27, right=0.98)
    c.save(fig, ax, xlabel="TPU v7 cost per token ÷ GB300 cost per token (Est.)", legend=False)


# --------------------------------------------------------------------------------------
# 8. $/M tokens vs interactivity (measured systems; TPU modelled), without and with MTP
# --------------------------------------------------------------------------------------
@register
def x14_cost_vs_interactivity():
    m = _model()
    base = m.inp.base_point()
    xs = np.arange(30, 181, 2.5)
    lines = [("GB300 NVL72", NV_DARK, "-"), ("B200 HGX", NV, "--"), ("H200 HGX", GEN_PAST, "-"),
             ("MI355X platform", entity_color("AMD"), "-"), ("TPU v7 Ironwood (external)", entity_color("Google"), ":")]
    curves = {}
    for s, *_ in lines:
        nos, mtp = [], []
        for x in xs:
            pt = tm._copy(base)
            pt["g"]["ref_interactivity_tok_s_per_user"] = float(x)
            r = m.evaluate(s, pt)
            nos.append(r["usd_per_m_tokens"])
            if m.is_measured(s):
                tps = m.measured_tps(s, float(x), tm.SUITE_MTP)
                mtp.append(r["total"] / (tps * 3600 * 8760 * 0.7) * 1e6 if tps == tps else np.nan)
            else:
                mtp.append(np.nan)
        curves[s] = (np.array(nos), np.array(mtp))
    i50, i100 = list(xs).index(50.0), list(xs).index(100.0)
    g50, g100 = curves["GB300 NVL72"][0][i50], curves["GB300 NVL72"][0][i100]
    t100 = curves["TPU v7 Ironwood (external)"][0][i100]
    b50m = curves["B200 HGX"][1][i50]
    gm100 = curves["GB300 NVL72"][1][i100]
    c = Chart(
        id="14-tco-cost-vs-interactivity",
        title=(f"Est.: GB300's cost per token rises {g100 / g50:.0f}× from 50 to 100 tok/s/user; speculative decoding "
               f"cuts it back to ~${gm100:.2f}/M"),
        subtitle="Owner cost per million tokens vs interactivity, DeepSeek-R1 1k/1k, base TCO assumptions (log scale) · left: no speculative decoding, right: with MTP",
        alt=(f"Two-panel log-scale line chart of estimated cost per million tokens against tokens per second per user. Without "
             f"speculative decoding GB300 NVL72 costs about ${g50:.2f} at 50 and ${g100:.2f} at 100 tokens/s per user, where the "
             f"modelled TPU v7 is about ${t100:.2f}, near parity; H200 and MI355X sit above both. With MTP speculative decoding "
             f"measured costs fall several-fold: B200 about ${b50m:.2f} at 50 and GB300 about ${gm100:.2f} at 100 tokens/s per user. "
             "The operating point and the software configuration move cost per token as much as the hardware choice."),
        data=DATA_FILES, chapters=CH + ["11", "P2"], source="repo TCO model on InferenceX frontiers", source_ids=_sids(),
        note="Est.: TPU line modelled (no MTP data); frontiers interpolated, not extrapolated",
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=12, height=6.0, sharey=True)
    for s, col, ls in lines:
        nos, mtp = curves[s]
        a1.plot(xs, nos, color=col, ls=ls, lw=2.1, label=SHORT[s] + ("" if _measured(s) else " (modelled)"))
        if not np.all(np.isnan(mtp)):
            a2.plot(xs, mtp, color=col, ls=ls, lw=2.1, label=SHORT[s])
    for a, ttl in ((a1, "No speculative decoding (reference)"), (a2, "With MTP speculative decoding (measured systems)")):
        a.set_yscale("log")
        a.set_xlim(30, 180)
        a.set_ylim(0.03, 30)
        a.axvline(50, color=INK["muted"], lw=0.8, ls=":")
        a.axvline(100, color=INK["muted"], lw=0.8, ls=":")
        a.set_title(ttl, fontsize=9.6, loc="left", color=INK["title"])
        a.set_xlabel("Tokens/s per user (interactivity)")
    a1.legend(loc="upper left", fontsize=8.4, frameon=False)
    a2.legend(loc="upper left", fontsize=8.4, frameon=False)
    _margins(fig, left=0.08, right=0.98, wspace=0.08)
    c.save(fig, [a1, a2], ylabel="US$ per million tokens (Est., log scale)", logy=True, legend=False)


# --------------------------------------------------------------------------------------
# 9. Free-chip test at 50 and 100 tok/s/user
# --------------------------------------------------------------------------------------
@register
def x14_free_chip_test():
    op = _run()["operating_points"]
    rivals = ["MI355X platform", "Trainium2 (Trn2 UltraServer)", "Trainium3 (Trn3 UltraServer)",
              "TPU v7 Ironwood (external)", "TPU v7 Ironwood (Google internal)", "Helios (MI455X)"]
    d50 = op[op.interactivity_tok_s_per_user == 50].set_index("system")
    d100 = op[op.interactivity_tok_s_per_user == 100].set_index("system")
    g50, g100 = d50.loc["GB300 NVL72", "usd_per_m_tokens"], d100.loc["GB300 NVL72", "usd_per_m_tokens"]
    free_beat_50 = [s for s in rivals if d50.loc[s, "usd_per_m_tokens_if_system_free"] < g50]
    free_beat_100 = [s for s in rivals if d100.loc[s, "usd_per_m_tokens_if_system_free"] < g100]
    free_lose_100 = [s for s in rivals if s not in free_beat_100]
    c = Chart(
        id="14-tco-free-chip-test",
        title=(f"Est.: at 50 tok/s/user even a free MI355X, TPU or Trainium makes costlier tokens than a paid-for GB300; "
               f"at 100 the test mostly fails"),
        subtitle="US$ per million tokens: rival at its estimated price (bar) vs with its accelerator system free (◆; network, facility, power, ops still paid) · line = GB300 at full price",
        alt=(f"Two-panel horizontal bar chart. At 50 tokens/s per user GB300 NVL72 costs about ${g50:.3f} per million tokens at "
             "full price, while rivals' costs with their accelerator systems given away are: " +
             ", ".join(f"{SHORT[s]} ${d50.loc[s, 'usd_per_m_tokens_if_system_free']:.3f}" for s in rivals) +
             f"; only {', '.join(SHORT[s] for s in free_beat_50) or 'none'} beat GB300 when free. At 100 tokens/s per user GB300 costs "
             f"about ${g100:.2f} and every free version undercuts it except "
             f"{', '.join(SHORT[s] for s in free_lose_100) or 'none'} (TPU v7 external free "
             f"${d100.loc['TPU v7 Ironwood (external)', 'usd_per_m_tokens_if_system_free']:.2f}). "
             "The 'free is not cheap enough' argument holds only where NVIDIA's rack-scale throughput lead is large."),
        data=DATA_FILES, chapters=CH + ["15", "18"], source="repo TCO model", source_ids=_sids("S14006"), note=NOTE,
    )
    fig, axes = c.figure_grid(1, 2, width=12.4, height=6.0)
    for ax, d, gref, ttl in ((axes[0], d50, g50, "50 tok/s/user"), (axes[1], d100, g100, "100 tok/s/user")):
        y = np.arange(len(rivals))
        paid = [d.loc[s, "usd_per_m_tokens"] for s in rivals]
        free = [d.loc[s, "usd_per_m_tokens_if_system_free"] for s in rivals]
        bars = ax.barh(y, paid, color=[_color(s) for s in rivals], height=0.58, zorder=2, alpha=0.85)
        for b, s in zip(bars, rivals):
            if not _measured(s):
                b.set_hatch("///")
        ax.scatter(free, y, marker="D", s=52, color="white", edgecolor=INK["title"], linewidth=1.3, zorder=4)
        for yi, (pv, fv) in enumerate(zip(paid, free)):
            ax.annotate(f"{_fmt_usd(pv)} · free {_fmt_usd(fv)}", (max(pv, fv), yi), xytext=(6, 0), textcoords="offset points",
                        va="center", fontsize=8.2, color=INK["title"])
        ax.axvline(gref, color=NV_DARK, lw=1.8, zorder=3)
        ax.text(gref, len(rivals) - 0.45, f" GB300 paid {_fmt_usd(gref)}", color=NV_DARK, fontsize=8.6, va="bottom",
                fontweight="bold")
        ax.set_xscale("log")
        ax.set_xlim(min(free + [gref]) * 0.5, max(paid) * 8)
        ax.set_yticks(y, [SHORT[s] for s in rivals], fontsize=8.8)
        ax.set_title(ttl, fontsize=10, loc="left", color=INK["title"])
        ax.grid(axis="x", color=INK["grid"], lw=0.7)
        ax.grid(axis="y", visible=False)
        ax.set_xlabel("US$ per million tokens (Est., log scale)")
    axes[1].set_yticklabels([])
    _margins(fig, left=0.15, right=0.985, wspace=0.06)
    c.save(fig, list(axes), legend=False)


# --------------------------------------------------------------------------------------
# 10. Depreciation life vs owner cost per useful hour, with rental prices
# --------------------------------------------------------------------------------------
@register
def x14_depreciation_life_sensitivity():
    grid = _run()["sensitivity_grid"]
    tco = load("cs3_tpu_economics.csv")
    rent = tco[tco.metric == "rental_per_chip_hour"].set_index("system").value
    pick = [("GB300 NVL72", NV, "GB300 NVL72"), ("B200 HGX", GEN_PAST, "B200"), ("MI355X platform", entity_color("AMD"), "MI355X")]
    g = grid[(grid.utilisation_pct == 70) & (grid.electricity_usd_per_kwh == 0.081)]
    def val(s, life, w):
        return g[(g.system == s) & (g.it_life_years == life) & (g.wacc_pct == w)].usd_per_hour_useful.iloc[0]
    gb6, gb4, gb3 = val("GB300 NVL72", 6, 8), val("GB300 NVL72", 4, 8), val("GB300 NVL72", 3, 8)
    c = Chart(
        id="14-tco-depreciation-life-sensitivity",
        title=(f"Est.: cutting GB300's life from 6 to 4 years lifts a useful GPU-hour from ${gb6:.2f} to ${gb4:.2f}, "
               f"close to its ${rent['GB300 NVL72']:.2f} rental price"),
        subtitle="Owner cost per useful accelerator-hour (70% utilization) vs useful life · solid = 8% cost of capital, dashed = 0% · dotted = July 2026 rental price",
        alt=(f"Line chart of estimated owner cost per useful hour against depreciation life from 3 to 7 years. GB300 NVL72 at 8% cost "
             f"of capital: about ${gb3:.2f} at 3 years, ${gb4:.2f} at 4 and ${gb6:.2f} at 6, against a SemiAnalysis July 2026 rental "
             f"price of ${rent['GB300 NVL72']:.2f}; B200 about ${val('B200 HGX', 6, 8):.2f} at 6 years vs ${rent['B200']:.2f} rental; "
             f"MI355X about ${val('MI355X platform', 6, 8):.2f} vs ${rent['MI355X']:.2f}. Shorter lives squeeze a renter's margin; "
             "without a cost of capital each line drops by roughly 10-20%."),
        data=DATA_FILES, chapters=CH + ["12", "18"], source="repo TCO model; SemiAnalysis rental survey", source_ids=_sids(),
        note="Est.: repo TCO model; rental = SemiAnalysis July 2026 survey (S622)",
    )
    fig, ax = c.figure(width=10.8, height=6.0)
    lives = [3, 4, 5, 6, 7]
    rent_key = {"GB300 NVL72": "GB300 NVL72", "B200 HGX": "B200", "MI355X platform": "MI355X"}
    for s, col, lab in pick:
        ax.plot(lives, [val(s, L, 8) for L in lives], color=col, lw=2.2, marker="o", label=f"{lab} (8% capital)")
        ax.plot(lives, [val(s, L, 0) for L in lives], color=col, lw=1.4, ls="--")
        rv = rent[rent_key[s]]
        ax.axhline(rv, color=col, lw=1.2, ls=":")
        ax.text(7.12, rv + 0.04, f"{lab} rental ${rv:.2f}", color=col, fontsize=8.6, va="bottom",
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none"))
    ax.axvline(6, color=INK["muted"], lw=0.8, ls=":")
    ax.text(6.04, 0.25, "6 yrs: Microsoft,\nAlphabet, CoreWeave", fontsize=8, color=INK["muted"], va="bottom")
    ax.axvline(5, color=INK["muted"], lw=0.8, ls=":")
    ax.text(5.04, 0.25, "5 yrs: Amazon\n(part, 2025)", fontsize=8, color=INK["muted"], va="bottom")
    ax.set_xlim(2.8, 8.2)
    ax.set_xticks(lives)
    ax.set_ylim(0, max(val("GB300 NVL72", 3, 8), rent.max()) * 1.18)
    ax.legend(loc="upper right", fontsize=8.6, frameon=False)
    c.save(fig, ax, xlabel="Useful (depreciation) life, years", ylabel="US$ per useful accelerator-hour (Est.)", legend=False)


# --------------------------------------------------------------------------------------
# 11. Training-run cost and time
# --------------------------------------------------------------------------------------
@register
def x14_training_run_cost():
    tr = _run()["training_run"].set_index("system")
    order = ["Vera Rubin NVL72", "Helios (MI455X)", "TPU v7 Ironwood (Google internal)", "TPU v7 Ironwood (external)",
             "MI355X platform", "B200 HGX", "GB300 NVL72", "Trainium3 (Trn3 UltraServer)", "Trainium2 (Trn2 UltraServer)", "H200 HGX"]
    order = sorted(order, key=lambda s: tr.loc[s, "train_cost_usd_m"])
    gb = tr.loc["GB300 NVL72"]
    vr = tr.loc["Vera Rubin NVL72"]
    tpu = tr.loc["TPU v7 Ironwood (external)"]
    c = Chart(
        id="14-tco-training-run-cost",
        title=(f"Est.: a 10²⁷-FLOP run costs ~${gb.train_cost_usd_m / 1e3:.2f}B on GB300 vs ~${tpu.train_cost_usd_m / 1e3:.2f}B on TPU v7, "
               f"but Rubin finishes in ~{vr.train_days_on_cluster:.0f} days"),
        subtitle="Hypothetical 1e27-FLOP training run: owner cost (US$ M, whisker = P10–P90) and calendar days on 100,000 accelerators · FP8, base MFU, 90% goodput",
        alt=("Two-panel bar chart for a hypothetical 10 to the 27 FLOP training run. Estimated owner compute cost: " +
             ", ".join(f"{SHORT[s]} ${tr.loc[s, 'train_cost_usd_m']:.0f}M" for s in order) +
             ". Days on 100,000 accelerators: " +
             ", ".join(f"{SHORT[s]} {tr.loc[s, 'train_days_on_cluster']:.0f}" for s in order) +
             ". Per FLOP NVIDIA is not the cheapest; its training case rests on time to train and delivered utilization."),
        data=DATA_FILES, chapters=CH + ["P1", "15"], source="repo TCO model; Epoch AI scenario", source_ids=_sids("S31007", "S34006"),
        note="Est.: equal-MFU assumptions favour less mature platforms; MI455X FP8 may be a sparse figure",
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=12.4, height=6.4, gridspec_kw=dict(width_ratios=[1.35, 1]))
    y = np.arange(len(order))
    cost = [tr.loc[s, "train_cost_usd_m"] for s in order]
    bars = a1.barh(y, cost, color=[_color(s) for s in order], height=0.6, zorder=2)
    for b, s in zip(bars, order):
        if not _measured(s):
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yi, s in enumerate(order):
        lo, hi = tr.loc[s, "train_cost_usd_m_p10"], tr.loc[s, "train_cost_usd_m_p90"]
        a1.plot([lo, hi], [yi, yi], color=INK["title"], lw=1.2, zorder=3)
        a1.annotate(f"${tr.loc[s, 'train_cost_usd_m']:.0f}M", (hi, yi), xytext=(5, 0), textcoords="offset points",
                    va="center", fontsize=8.6, color=INK["title"])
    a1.set_yticks(y, [SHORT[s] for s in order], fontsize=8.8)
    a1.set_xlim(0, max(tr.loc[s, "train_cost_usd_m_p90"] for s in order) * 1.18)
    a1.set_xlabel("Owner compute cost, US$ M (Est.)")
    a1.set_title("Cost of the run", fontsize=10, loc="left", color=INK["title"])
    days = [tr.loc[s, "train_days_on_cluster"] for s in order]
    b2 = a2.barh(y, days, color=[_color(s) for s in order], height=0.6, zorder=2)
    for b, s in zip(b2, order):
        if not _measured(s):
            b.set_hatch("///")
            b.set_alpha(0.8)
    for yi, s in enumerate(order):
        a2.annotate(f"{tr.loc[s, 'train_days_on_cluster']:.0f} d · {tr.loc[s, 'train_cluster_mw']:.0f} MW", (days[yi], yi),
                    xytext=(5, 0), textcoords="offset points", va="center", fontsize=8.4, color=INK["title"])
    a2.set_yticks(y, [""] * len(order))
    a2.set_xlim(0, max(days) * 1.45)
    a2.set_xlabel("Days on 100,000 accelerators (site MW at the meter)")
    a2.set_title("Time to train", fontsize=10, loc="left", color=INK["title"])
    for a in (a1, a2):
        a.grid(axis="x", color=INK["grid"], lw=0.7)
        a.grid(axis="y", visible=False)
    _margins(fig, left=0.17, right=0.985, wspace=0.05)
    c.save(fig, [a1, a2], legend=False)
