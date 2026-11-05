"""Chapter 15, part A (competitive landscape: index, AMD, Google TPU, AWS Trainium, Microsoft Maia, Meta MTIA).

Owner: chapter-15A agent. Data: data/x15a_accelerator_generations.csv and data/x15a_competitor_metrics.csv
(documented in data/README.md), plus the shared competitor_accelerators.csv, gpu_product_specs.csv,
competitor_matrix.csv and cs4_amd_openai.csv (read only).

Analysis conventions (repo estimates, source S15014):
- "NVIDIA same-year flagship" = the NVIDIA data-center GPU shipping in volume in that calendar year:
  2021 A100 80GB, 2022-2023 H100 SXM, 2024 H200 SXM, 2025 GB300 (per GPU), 2026 Rubin (VR200, per GPU).
- Gap ratio = challenger spec / NVIDIA same-year flagship spec, in percent (vendor peak figures, dense).
- Implied AMD commitment value = committed GW x hardware spend per GW (low/base/high from cs4_amd_openai.csv).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from style import INK, NV, Chart, entity_color, hatch_future, load, register, sources_of

GEN = "x15a_accelerator_generations.csv"
MET = "x15a_competitor_metrics.csv"
ACC = "competitor_accelerators.csv"
GPU = "gpu_product_specs.csv"
MAT = "competitor_matrix.csv"
CS4 = "cs4_amd_openai.csv"

AMD = entity_color("AMD")
GOOG = entity_color("Google")
AWS = entity_color("AWS")
MSFT = entity_color("Microsoft")
META = entity_color("Meta")

NV_FLAGSHIP = {2021: "A100 SXM 80GB", 2022: "H100 SXM", 2023: "H100 SXM", 2024: "H200 SXM",
               2025: "GB300 (per GPU)", 2026: "Rubin (VR200, per GPU)"}
NV_SHORT = {"A100 SXM 80GB": "A100", "H100 SXM": "H100", "H200 SXM": "H200", "GB300 (per GPU)": "GB300",
            "Rubin (VR200, per GPU)": "Rubin"}


def _margins(fig, **over):
    """Chart.save() hard-codes margins; widen them where labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _below(axes):
    """Draw gridlines under bars (default rc puts them above patches)."""
    for a in axes:
        a.set_axisbelow(True)


def _gpu():
    return load(GPU).set_index("product")


def _acc():
    return load(ACC)


def _chip(df, product):
    r = df[df["product"] == product]
    if r.empty:
        raise KeyError(product)
    return r.iloc[0]


def _all_chips():
    """Competitor chips from the shared CSV plus this chapter's newer rows, one frame."""
    a = _acc()[["vendor", "product", "year", "status", "memory_capacity_gb", "memory_bandwidth_tbs",
                "fp8_tflops_dense", "fp4_tflops_dense", "tdp_w", "max_scale_up_domain", "confidence", "source_id"]]
    g = load(GEN)[["vendor", "product", "year", "status", "memory_capacity_gb", "memory_bandwidth_tbs",
                   "fp8_tflops_dense", "fp4_tflops_dense", "tdp_w", "max_scale_up_domain", "confidence", "source_id"]]
    return pd.concat([a, g], ignore_index=True)


def _nv_sources(products):
    gpu = load(GPU)
    return sources_of(gpu[gpu["product"].isin(products)])


# ======================================================================================
# AMD
# ======================================================================================
@register
def amd_instinct_vs_nvidia():
    acc, gpu = _acc(), _gpu()
    pairs = [(2023, "Instinct MI300X", "H100 SXM"), (2024, "Instinct MI325X", "H200 SXM"),
             (2025, "Instinct MI355X", "GB300 (per GPU)"), (2026, "Instinct MI455X", "Rubin (VR200, per GPU)")]
    rows = []
    for yr, a, n in pairs:
        ar, nr = _chip(acc, a), gpu.loc[n]
        rows.append(dict(year=yr, amd=a.replace("Instinct ", ""), nv=NV_SHORT[n],
                         a_fp8=ar.fp8_tflops_dense / 1000, n_fp8=nr.fp8_tflops_dense / 1000,
                         a_gb=ar.memory_capacity_gb, n_gb=nr.memory_capacity_gb,
                         a_bw=ar.memory_bandwidth_tbs, n_bw=nr.memory_bandwidth_tbs, a_status=ar.status))
    d = pd.DataFrame(rows)
    last = d.iloc[-1]
    srcs = sources_of(acc[acc["product"].isin([p[1] for p in pairs])]) + _nv_sources([p[2] for p in pairs])
    c = Chart(
        id="15-amd-instinct-vs-nvidia-generations",
        title=(f"On paper every Instinct since MI300X matched or beat NVIDIA's same-year flagship: "
               f"{last.a_gb:.0f} vs {last.n_gb:.0f} GB in 2026"),
        subtitle=("Per GPU: dense FP8 PFLOPS, HBM capacity (GB) and HBM bandwidth (TB/s); AMD vs the NVIDIA flagship "
                  "shipping that year; MI455X announced, FP8 basis unstated"),
        alt=("Three grouped-bar panels comparing AMD Instinct GPUs with NVIDIA's same-year flagship. Dense FP8: MI300X 2.6 vs "
             "H100 2.0 PFLOPS (2023), MI325X 2.6 vs H200 2.0 (2024), MI355X 5.0 vs GB300 5.0 (2025), MI455X 20 vs Rubin 17.5 "
             "(2026, AMD basis unstated). HBM capacity: 192 vs 80 GB, 256 vs 141, 288 vs 288 and 432 vs 288. HBM bandwidth: "
             "5.3 vs 3.35 TB/s, 6.0 vs 4.8, 8.0 vs 8.0 and 19.6 vs 19.2 after NVIDIA's 2026 Rubin revision. AMD's gap to "
             "NVIDIA is therefore not on the spec sheet but in software, racks and revenue."),
        data=[ACC, GPU], chapters=["15", "02", "03"],
        source="AMD and NVIDIA specifications", source_ids=list(dict.fromkeys(srcs)),
        note="Hatched = announced, not yet shipping in volume",
    )
    fig, axs = c.figure_grid(1, 3, width=12.5, height=5.6)
    x = np.arange(len(d))
    w = 0.38
    panels = [("a_fp8", "n_fp8", "Dense FP8 (PFLOPS)", "{:.1f}"), ("a_gb", "n_gb", "HBM capacity (GB)", "{:.0f}"),
              ("a_bw", "n_bw", "HBM bandwidth (TB/s)", "{:.1f}")]
    for ax, (ak, nk, lab, fmt) in zip(axs, panels):
        ba = ax.bar(x - w / 2, d[ak], w, color=AMD, label="AMD Instinct")
        bn = ax.bar(x + w / 2, d[nk], w, color=NV, label="NVIDIA flagship")
        hatch_future(ba, d.a_status != "shipping")
        for bars, vals in ((ba, d[ak]), (bn, d[nk])):
            for b, v in zip(bars, vals):
                ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom",
                            fontsize=7.6, color=INK["text"], xytext=(0, 2), textcoords="offset points")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{r.year}\n{r.amd}\nvs {r.nv}" for r in d.itertuples()], fontsize=7.8)
        ax.set_title(lab, fontsize=10, color=INK["title"], loc="left")
        ax.set_ylim(0, max(d[ak].max(), d[nk].max()) * 1.18)
    axs[0].set_ylabel("Per GPU (units in panel title)")
    axs[0].legend(loc="upper left", fontsize=8.5)
    _below(axs)
    _margins(fig, left=0.06, right=0.98, wspace=0.22)
    c.save(fig, list(axs), legend=False, top=0.80, bottom=0.20)


@register
def amd_gigawatt_commitments():
    met, cs = load(MET), load(CS4)
    gw = met[met.metric == "amd_gw_commitment"].copy()
    total = gw.value.sum()
    per = cs[cs.record_type == "assumption"].set_index("metric").value
    lo, base, hi = per["amd_hardware_spend_per_gw_low"], per["amd_hardware_spend_per_gw_base"], per["amd_hardware_spend_per_gw_high"]
    run = met[met.metric == "dc_segment_revenue_annualized"].value.iloc[0]
    vals = [total * lo, total * base, total * hi]
    srcs = sources_of(gw) + sources_of(cs[cs.record_type == "assumption"]) + sources_of(met[met.metric == "dc_segment_revenue_annualized"]) + ["S15014"]
    c = Chart(
        id="15-amd-gigawatt-commitments",
        title=(f"Est.: AMD's {total:.0f} GW of commitments imply ~${vals[0]:.0f}–{vals[2]:.0f}B of hardware, "
               f"{vals[0] / run:.0f}–{vals[2] / run:.0f}× its ~${run:.0f}B DC run-rate"),
        subtitle=("Left: committed GW by customer (maximums). Right: implied hardware value at $10/15/20B per GW (repo "
                  "scenarios) vs AMD Data Center segment, Q3 2026 annualized (incl. EPYC)"),
        alt=(f"Two panels. Left: AMD's announced gigawatt commitments are OpenAI 6 GW (Oct 2025), Meta 6 GW (Feb 2026) and "
             f"Anthropic up to 2 GW (2026), {total:.0f} GW in total, all maximums tied to deployment. Right: at a repo scenario of "
             f"$10B, $15B or $20B of AMD hardware per GW, {total:.0f} GW implies about ${vals[0]:.0f}B, ${vals[1]:.0f}B or "
             f"${vals[2]:.0f}B of revenue over several years, compared with AMD's Data Center segment run-rate of about "
             f"${run:.0f}B a year (Q3 2026 annualized, including server CPUs): roughly {vals[0] / run:.0f} to "
             f"{vals[2] / run:.0f} years of today's business."),
        data=[MET, CS4], chapters=["15", "13", "CS4"],
        source="AMD and customer announcements; repo scenarios", source_ids=list(dict.fromkeys(srcs)),
        note="All values Est. or maximums; hatched = scenario",
    )
    fig, axs = c.figure_grid(1, 2, width=12, height=5.4, gridspec_kw=dict(width_ratios=[1, 1.35]))
    ax = axs[0]
    names = list(gw.entity)
    cols = [entity_color(n) if n == "Meta" else (INK["text"] if n == "OpenAI" else entity_color("other")) for n in names]
    cols = [META if n == "Meta" else ("#52514E" if n == "OpenAI" else "#898781") for n in names]
    bars = ax.barh(names[::-1], gw.value.values[::-1], color=cols[::-1])
    for b, v in zip(bars, gw.value.values[::-1]):
        ax.annotate(f"{v:.0f} GW", (v, b.get_y() + b.get_height() / 2), xytext=(4, 0), textcoords="offset points",
                    va="center", fontsize=9, color=INK["title"])
    ax.set_xlim(0, 7.5)
    ax.set_xlabel("Committed capacity (GW, maximum)")
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    ax.set_title("Who committed", fontsize=10, color=INK["title"], loc="left")
    ax2 = axs[1]
    labels = ["AMD DC run-rate\n(Q3 2026 ×4)", "14 GW @ $10B/GW", "14 GW @ $15B/GW", "14 GW @ $20B/GW"]
    v2 = [run] + vals
    b2 = ax2.bar(labels, v2, color=[AMD, AMD, AMD, AMD], width=0.6)
    hatch_future(b2, [False, True, True, True])
    for b, v in zip(b2, v2):
        ax2.annotate(f"${v:.0f}B", (b.get_x() + b.get_width() / 2, v), ha="center", va="bottom", fontsize=9,
                     color=INK["title"], xytext=(0, 2), textcoords="offset points")
    ax2.set_ylim(0, max(v2) * 1.15)
    ax2.tick_params(axis="x", labelsize=8.5)
    ax2.set_title("What it could be worth (multi-year)", fontsize=10, color=INK["title"], loc="left")
    ax2.set_ylabel("US$ B")
    _below([ax, ax2])
    _margins(fig, left=0.09, right=0.98, wspace=0.32)
    c.save(fig, [ax, ax2], legend=False, top=0.80, bottom=0.17)


# ======================================================================================
# Google TPU
# ======================================================================================
@register
def tpu_memory_vs_nvidia():
    ch, gpu = _all_chips(), _gpu()
    gens = [("TPU v4", 2021), ("TPU v5p", 2023), ("TPU v6e (Trillium)", 2024), ("TPU v7 Ironwood", 2025),
            ("TPU 8t", 2026), ("TPU 8i", 2026)]
    rows = []
    for p, yr in gens:
        r = _chip(ch, p)
        n = gpu.loc[NV_FLAGSHIP[yr]]
        rows.append(dict(label=p.replace("TPU ", "").replace(" (Trillium)", "\nTrillium").replace("v7 ", "v7\n"),
                         year=yr, bw=r.memory_bandwidth_tbs, gb=r.memory_capacity_gb, status=r.status,
                         nbw=n.memory_bandwidth_tbs, ngb=n.memory_capacity_gb, nv=NV_SHORT[NV_FLAGSHIP[yr]]))
    d = pd.DataFrame(rows)
    i8 = d.iloc[-1]
    v4 = d.iloc[0]
    srcs = sources_of(ch[ch["product"].isin([g[0] for g in gens])]) + _nv_sources(set(NV_FLAGSHIP[g[1]] for g in gens))
    c = Chart(
        id="15-tpu-memory-vs-nvidia",
        title=(f"TPU 8i's {i8.bw:.1f} TB/s is ~{i8.bw / v4.bw:.0f}× TPU v4's, but only ~{i8.bw / i8.nbw * 100:.0f}% of "
               f"Rubin's {i8.nbw:.1f} TB/s"),
        subtitle=("HBM bandwidth (TB/s) and capacity (GB) per chip by TPU generation; green dots = NVIDIA flagship "
                  "shipping the same year; hatched = announced"),
        alt=(f"Two bar panels of Google TPU memory per chip with NVIDIA's same-year flagship as green dots. Bandwidth: v4 "
             f"1.2 TB/s (2021, A100 2.0), v5p 2.77 (2023, H100 3.35), Trillium 1.64 (2024, H200 4.8), Ironwood 7.37 (2025, "
             f"GB300 8.0, 92%), TPU 8t 6.5 and TPU 8i 8.6 (2026, Rubin 19.2). Capacity: 32, 95, 32, 192, 216 and 288 GB vs "
             f"80, 80, 141, 288 and 288 GB. Ironwood nearly closed the bandwidth gap in 2025; Rubin's HBM4 reopened it to "
             f"about 2.2 times, while TPU 8i matches Rubin's 288 GB."),
        data=[ACC, GEN, GPU], chapters=["15", "CS3", "03"],
        source="Google Cloud docs, press deep dives, NVIDIA specs", source_ids=list(dict.fromkeys(srcs)),
        note="TPU 8t/8i memory figures are press-reported",
    )
    fig, axs = c.figure_grid(1, 2, width=12, height=5.8)
    x = np.arange(len(d))
    for ax, k, nk, lab, fmt, unit in ((axs[0], "bw", "nbw", "HBM bandwidth per chip (TB/s)", "{:.1f}", "TB/s"),
                                      (axs[1], "gb", "ngb", "HBM capacity per chip (GB)", "{:.0f}", "GB")):
        b = ax.bar(x, d[k], 0.62, color=GOOG, label="Google TPU")
        hatch_future(b, d.status != "shipping")
        ax.scatter(x, d[nk], color=NV, s=70, zorder=4, marker="D", label="NVIDIA same-year flagship")
        for xi, r in zip(x, d.itertuples()):
            ax.annotate(f"{r.nv} {fmt.format(getattr(r, nk))}", (xi, getattr(r, nk)), ha="center", va="bottom",
                        fontsize=7.4, color=NV, xytext=(0, 7), textcoords="offset points")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{r.label}\n{r.year}\n{fmt.format(getattr(r, k))} {unit}" for r in d.itertuples()], fontsize=7.8)
        ax.set_title(lab, fontsize=10, color=INK["title"], loc="left")
        ax.set_ylim(0, max(d[k].max(), d[nk].max()) * 1.22)
    axs[0].set_ylabel("Per chip (units in panel title)")
    axs[0].legend(loc="upper left", fontsize=8.5)
    _below(axs)
    _margins(fig, left=0.07, right=0.98, wspace=0.18)
    c.save(fig, list(axs), legend=False, top=0.80, bottom=0.22)


# ======================================================================================
# AWS Trainium
# ======================================================================================
@register
def trainium_generations():
    acc = _acc()
    prods = ["Trainium (Trn1)", "Trainium2", "Trainium3", "Trainium4"]
    d = acc[acc["product"].isin(prods)].set_index("product").reindex(prods).reset_index()
    fp8 = d.fp8_tflops_dense.astype(float).values / 1000
    fp8[3] = fp8[2] * 3  # AWS claim: >=3x Trainium3 FP8 (repo Est.)
    bw = d.memory_bandwidth_tbs.values
    dom = d.max_scale_up_domain.values.astype(float)
    labels = ["Trn1\n2022", "Trn2\n2024", "Trn3\n2025", "Trn4 (Est.)\n2027?"]
    est = [False, False, False, True]
    c = Chart(
        id="15-trainium-generations",
        title=(f"Trainium FP8 per chip rose ~{fp8[2] / fp8[0]:.0f}× from Trn1 to Trn3; AWS claims Trainium4 "
               f"triples it and moves to NVLink Fusion"),
        subtitle=("Per chip: dense FP8 PFLOPS and HBM bandwidth (TB/s); scale-up domain = chips per UltraServer or instance; "
                  "Trainium4 = repo Est. from AWS multipliers"),
        alt=(f"Three bar panels of AWS Trainium generations. Dense FP8 per chip: Trn1 0.19 PFLOPS (2022), Trn2 1.3 (2024), "
             f"Trn3 2.52 (2025), about {fp8[2] / fp8[0]:.0f} times in three years, and an estimated ~{fp8[3]:.1f} for Trainium4 "
             f"from AWS's claim of at least 3 times Trn3. HBM bandwidth: 0.82, 2.9 and 4.9 TB/s, with Trainium4 estimated at "
             f"~19.6 TB/s from AWS's 4 times claim. Scale-up domain: 16 chips per Trn1 instance, 64 per Trn2 UltraServer and "
             f"144 per Trn3 UltraServer; Trainium4 is to adopt NVIDIA NVLink Fusion, so its domain is not yet defined."),
        data=[ACC], chapters=["15", "02", "05"],
        source="AWS Neuron docs and re:Invent 2025", source_ids=sources_of(d) + ["S90034"],
        note="Hatched = repo estimate from vendor multipliers",
    )
    fig, axs = c.figure_grid(1, 3, width=12.5, height=5.4)
    for ax, vals, lab, fmt in ((axs[0], fp8, "Dense FP8 per chip (PFLOPS)", "{:.2f}"),
                               (axs[1], bw, "HBM bandwidth per chip (TB/s)", "{:.1f}"),
                               (axs[2], dom, "Scale-up domain (chips)", "{:.0f}")):
        v = np.nan_to_num(vals.astype(float))
        b = ax.bar(labels, v, color=AWS, width=0.62)
        hatch_future(b, est)
        for bb, vv, raw in zip(b, v, vals):
            txt = "NVLink\nFusion" if (raw != raw) else fmt.format(vv)
            ax.annotate(txt, (bb.get_x() + bb.get_width() / 2, vv), ha="center", va="bottom", fontsize=8.2,
                        color=INK["text"], xytext=(0, 2), textcoords="offset points")
        ax.set_title(lab, fontsize=10, color=INK["title"], loc="left")
        ax.set_ylim(0, max(v) * 1.2)
        ax.tick_params(axis="x", labelsize=8.4)
    axs[0].set_ylabel("Per chip / per domain (units in panel title)")
    _below(axs)
    _margins(fig, left=0.07, right=0.98, wspace=0.25)
    c.save(fig, list(axs), legend=False, top=0.80, bottom=0.17)


# ======================================================================================
# Microsoft Maia
# ======================================================================================
@register
def maia_generations():
    ch, gpu = _all_chips(), _gpu()
    prods = ["Maia 100", "Maia 200", "Maia 300"]
    d = ch[ch["product"].isin(prods)].set_index("product").reindex(prods).reset_index()
    rub = gpu.loc["Rubin (VR200, per GPU)"]
    fp4 = d.fp4_tflops_dense.astype(float).values / 1000
    bw = d.memory_bandwidth_tbs.astype(float).values
    eff = d.fp4_tflops_dense.astype(float).values / d.tdp_w.astype(float).values
    r_eff = rub.fp4_tflops_dense / rub.tdp_w
    labels = ["Maia 100\n2024", "Maia 200\n2026", "Maia 300\n2027", "Rubin\n(ref.)"]
    srcs = sources_of(d) + _nv_sources(["Rubin (VR200, per GPU)"])
    c = Chart(
        id="15-maia-generations",
        title=(f"Maia 300 (2027) claims {bw[2]:.0f} TB/s, {bw[2] / bw[0]:.0f}× Maia 100, and ~{eff[2] / r_eff * 100:.0f}% "
               f"of Rubin's FP4 per watt on paper"),
        subtitle=("Per chip: dense FP4 PFLOPS, HBM bandwidth (TB/s) and FP4 TFLOPS per watt of chip power; NVIDIA Rubin "
                  "(2.3 kW, analyst-reported) as reference; hatched = announced"),
        alt=(f"Three bar panels of Microsoft Maia generations with NVIDIA Rubin as reference. Dense FP4: Maia 100 has no FP4, "
             f"Maia 200 at least 10 PFLOPS (2026), Maia 300 up to 13.8 (2027) vs Rubin 35. HBM bandwidth: 1.8, 7.0 and 18 TB/s "
             f"vs Rubin 19.2. FP4 per watt: Maia 200 about {eff[1]:.1f} TFLOPS/W at 750 W, Maia 300 about {eff[2]:.1f} at "
             f"950 W, Rubin about {r_eff:.1f} at a reported 2.3 kW. Maia trades peak compute for power efficiency in an "
             f"inference-only design; all Maia 300 figures are Microsoft claims."),
        data=[ACC, GEN, GPU], chapters=["15", "02"],
        source="Microsoft announcements, press, NVIDIA specs", source_ids=list(dict.fromkeys(srcs)),
        note="Hatched = announced; Rubin power analyst-reported",
    )
    fig, axs = c.figure_grid(1, 3, width=12.5, height=5.4)
    cols = [MSFT, MSFT, MSFT, NV]
    est = [False, False, True, False]
    sets = [(np.append(fp4, rub.fp4_tflops_dense / 1000), "Dense FP4 per chip (PFLOPS)", "{:.1f}"),
            (np.append(bw, rub.memory_bandwidth_tbs), "HBM bandwidth per chip (TB/s)", "{:.1f}"),
            (np.append(eff, r_eff), "FP4 TFLOPS per watt", "{:.1f}")]
    for ax, (vals, lab, fmt) in zip(axs, sets):
        v = np.nan_to_num(vals.astype(float))
        b = ax.bar(labels, v, color=cols, width=0.62)
        hatch_future(b, est)
        for bb, vv, raw in zip(b, v, vals):
            txt = "no FP4" if raw != raw else fmt.format(vv)
            ax.annotate(txt, (bb.get_x() + bb.get_width() / 2, vv), ha="center", va="bottom", fontsize=8.2,
                        color=INK["text"], xytext=(0, 2), textcoords="offset points")
        ax.set_title(lab, fontsize=10, color=INK["title"], loc="left")
        ax.set_ylim(0, max(v) * 1.2)
        ax.tick_params(axis="x", labelsize=8.4)
    axs[0].set_ylabel("Per chip (units in panel title)")
    _below(axs)
    _margins(fig, left=0.07, right=0.98, wspace=0.25)
    c.save(fig, list(axs), legend=False, top=0.80, bottom=0.17)


# ======================================================================================
# Meta MTIA
# ======================================================================================
@register
def mtia_generations():
    ch, gpu = _all_chips(), _gpu()
    acc = _acc()
    prods = ["MTIA v1", "MTIA v2", "MTIA 300", "MTIA 400", "MTIA 450", "MTIA 500"]
    d = ch[ch["product"].isin(prods)].set_index("product").reindex(prods).reset_index()
    # 8-bit compute: INT8 TOPS for v1/v2 (no FP8), FP8 TFLOPS from MTIA 300
    int8 = acc.set_index("product").int8_tops_dense
    eight = [int8["MTIA v1"], int8["MTIA v2"]] + list(d.fp8_tflops_dense.values[2:])
    eight = np.array(eight, dtype=float) / 1000
    bw = d.memory_bandwidth_tbs.astype(float).values
    rub = gpu.loc["Rubin (VR200, per GPU)"]
    years = [2023, 2024, 2026, 2026, 2027, 2027]
    labels = [f"{p.replace('MTIA ', '')}\n{y}" for p, y in zip(prods, years)]
    est = [s != "shipping" for s in d.status]
    srcs = sources_of(d) + _nv_sources(["Rubin (VR200, per GPU)"])
    c = Chart(
        id="15-mtia-generations",
        title=(f"Meta's MTIA went from {bw[1]:.1f} TB/s of LPDDR (2024) to {bw[-1]:.1f} TB/s of HBM planned for 2027, "
               f"~{bw[-1] / bw[1]:.0f}×"),
        subtitle=("Per chip: memory bandwidth (TB/s, log scale) and dense 8-bit compute (PFLOPS; INT8 TOPS for v1/v2, FP8 "
                  "from MTIA 300); dashed = NVIDIA Rubin; hatched = not yet shipping"),
        alt=(f"Two bar panels of Meta MTIA generations. Memory bandwidth per chip on a log scale: MTIA v1 0.18 TB/s and v2 0.20 "
             f"TB/s of LPDDR5 (2023-24), then HBM: MTIA 300 6.1 TB/s (in production 2026), MTIA 400 9.2, MTIA 450 18.4 and "
             f"MTIA 500 27.6 (2027), about {bw[-1] / bw[1]:.0f} times v2 and above Rubin's 19.2 TB/s on paper. Dense 8-bit "
             f"compute: 0.10 and 0.35 POPS INT8 for v1 and v2, then 1.2, 6, 7 and 10 PFLOPS FP8, against Rubin's 17.5. Meta "
             f"pivoted MTIA from small recommendation chips to HBM-class generative-AI inference parts on a six-month cadence."),
        data=[ACC, GEN, GPU], chapters=["15", "02", "03"],
        source="Meta announcements and press spec tables", source_ids=list(dict.fromkeys(srcs)),
        note="Hatched = announced/roadmap (Meta figures)",
    )
    fig, axs = c.figure_grid(1, 2, width=12, height=5.6)
    for ax, vals, ref, lab, fmt, log in ((axs[0], bw, rub.memory_bandwidth_tbs, "Memory bandwidth per chip (TB/s, log scale)", "{:.2g}", True),
                                         (axs[1], eight, rub.fp8_tflops_dense / 1000, "Dense 8-bit compute per chip (PFLOPS)", "{:.2g}", False)):
        b = ax.bar(labels, vals, color=META, width=0.62)
        hatch_future(b, est)
        if log:
            ax.set_yscale("log")
        ax.axhline(ref, color=NV, ls="--", lw=1.6)
        ax.annotate(f"NVIDIA Rubin {ref:g}", (-0.45, ref), xytext=(0, 4), textcoords="offset points",
                    ha="left", va="bottom", fontsize=8.4, color=NV, fontweight="bold")
        for bb, vv in zip(b, vals):
            txt = f"{vv:.2f}" if vv < 1 else f"{vv:.1f}"
            ax.annotate(txt, (bb.get_x() + bb.get_width() / 2, vv), ha="center", va="bottom", fontsize=8.2,
                        color=INK["text"], xytext=(0, 2), textcoords="offset points")
        ax.set_title(lab, fontsize=10, color=INK["title"], loc="left")
        ax.tick_params(axis="x", labelsize=8.4)
    axs[0].set_ylim(0.1, 60)
    axs[1].set_ylim(0, 20)
    _below(axs)
    _margins(fig, left=0.07, right=0.98, wspace=0.2)
    c.save(fig, list(axs), ylabel="TB/s (log scale)", logy=True, legend=False, top=0.80, bottom=0.17)


# ======================================================================================
# Cross-vendor: gap to NVIDIA's same-year flagship
# ======================================================================================
GAP_SERIES = {
    "AMD": [(2023, "Instinct MI300X"), (2024, "Instinct MI325X"), (2025, "Instinct MI355X"), (2026, "Instinct MI455X")],
    "Google TPU": [(2021, "TPU v4"), (2023, "TPU v5p"), (2025, "TPU v7 Ironwood"), (2026, "TPU 8i")],
    "AWS Trainium": [(2022, "Trainium (Trn1)"), (2024, "Trainium2"), (2025, "Trainium3")],
    "Microsoft Maia": [(2024, "Maia 100"), (2026, "Maia 200")],
    "Meta MTIA": [(2024, "MTIA v2"), (2026, "MTIA 300")],
}


@register
def challenger_gap_to_nvidia():
    ch, gpu = _all_chips(), _gpu()
    recs = []
    for vend, pts in GAP_SERIES.items():
        for yr, p in pts:
            r = _chip(ch, p)
            n = gpu.loc[NV_FLAGSHIP[yr]]
            bw = r.memory_bandwidth_tbs / n.memory_bandwidth_tbs * 100
            fp8 = (r.fp8_tflops_dense / n.fp8_tflops_dense * 100) if (r.fp8_tflops_dense == r.fp8_tflops_dense and
                                                                       n.fp8_tflops_dense == n.fp8_tflops_dense) else np.nan
            recs.append(dict(vendor=vend, year=yr, product=p, bw=bw, fp8=fp8, status=r.status))
    d = pd.DataFrame(recs)
    hs = d[(d.year == 2026) & (d.vendor != "AMD")]
    amd26 = d[(d.vendor == "AMD") & (d.year == 2026)].iloc[0]
    iw = d[d["product"] == "TPU v7 Ironwood"].iloc[0]
    used = [p for pts in GAP_SERIES.values() for _, p in pts]
    srcs = sources_of(ch[ch["product"].isin(used)]) + _nv_sources(set(NV_FLAGSHIP.values())) + ["S15014"]
    c = Chart(
        id="15-challenger-gap-to-nvidia",
        title=(f"Rubin reset the gap: 2026 hyperscaler chips have {hs.bw.min():.0f}–{hs.bw.max():.0f}% of its "
               f"bandwidth; only AMD keeps pace"),
        subtitle=("Challenger chip as % of the NVIDIA flagship shipping the same year (100% = parity); left: HBM/DRAM "
                  "bandwidth per chip; right: dense FP8 per chip; vendor peak figures"),
        alt=(f"Two line panels of challenger chips as a percentage of NVIDIA's same-year flagship. Memory bandwidth: AMD at "
             f"158% (MI300X vs H100, 2023), 125%, 100% and {amd26.bw:.0f}% (MI455X vs Rubin, 2026); Google TPU rose from 59% "
             f"(v4, 2021) to {iw.bw:.0f}% (Ironwood vs GB300, 2025) before falling to about 45% (TPU 8i vs Rubin, 2026); AWS "
             f"Trainium 24%, 60% and 61% (2022-2025); Microsoft Maia 38% (2024) and 36% (2026); Meta MTIA 4% (v2, 2024) and "
             f"32% (MTIA 300, 2026). Dense FP8: AMD 101-132%; Ironwood 92%; Trainium 10%, 66% and 50%; Maia 200 29%; MTIA "
             f"300 7%. Rubin's HBM4 jump re-opened a gap that custom chips had almost closed in 2025."),
        data=[ACC, GEN, GPU], chapters=["15", "02", "03", "17"],
        source="vendor specifications; repo ratios", source_ids=list(dict.fromkeys(srcs)),
        note="Repo calculation; hollow markers = announced, not yet shipping",
    )
    fig, axs = c.figure_grid(1, 2, width=12.5, height=6.0)
    markers = {"AMD": "o", "Google TPU": "s", "AWS Trainium": "^", "Microsoft Maia": "D", "Meta MTIA": "v"}
    for ax, k, lab in ((axs[0], "bw", "Memory bandwidth per chip (% of NVIDIA)"), (axs[1], "fp8", "Dense FP8 per chip (% of NVIDIA)")):
        ax.axhline(100, color=NV, lw=1.6, ls="--")
        ax.annotate("NVIDIA same-year flagship = 100%", (2020.9, 100), xytext=(0, 4), textcoords="offset points",
                    fontsize=8.2, color=NV, fontweight="bold")
        for vend, g in d.groupby("vendor", sort=False):
            g = g.dropna(subset=[k])
            if g.empty:
                continue
            col = entity_color(vend)
            ax.plot(g.year, g[k], color=col, lw=2, marker=markers[vend], ms=7, label=vend)
            for _, r in g.iterrows():
                if r.status != "shipping":
                    ax.scatter([r.year], [r[k]], s=70, facecolor="#FFFFFF", edgecolor=col, zorder=4, marker=markers[vend], lw=1.6)
            last = g.iloc[-1]
            dy = {"Meta MTIA": -5, "Microsoft Maia": 4}.get(vend, 0) if k == "bw" else 0
            ax.annotate(vend.split()[0] if vend != "Google TPU" else "TPU", (last.year, last[k]), xytext=(6, dy),
                        textcoords="offset points", va="center", fontsize=8.4, color=col, fontweight="bold")
        ax.set_xlim(2020.7, 2026.8)
        ax.set_xticks(range(2021, 2027))
        ax.set_ylim(0, 175)
        ax.set_title(lab, fontsize=10, color=INK["title"], loc="left")
        ax.set_xlabel("Year the chip shipped or is announced to ship")
    axs[0].set_ylabel("% of NVIDIA's same-year flagship")
    axs[1].legend(loc="upper right", fontsize=8.2, ncol=1)
    _margins(fig, left=0.07, right=0.97, wspace=0.18)
    c.save(fig, list(axs), legend=False, top=0.80, bottom=0.15)


# ======================================================================================
# Hyperscaler wallet: capex vs NVIDIA vs custom silicon (2026)
# ======================================================================================
@register
def hyperscaler_capex_vs_silicon():
    met = load(MET)
    cap = met[met.metric == "capex_guidance_mid"]
    cap_total = cap.value.sum()
    nv = met[met.metric == "dc_hyperscale_revenue_annualized"].value.iloc[0]
    avgo = met[met.metric == "ai_semiconductor_revenue_annualized"].value.iloc[0]
    aws = met[met.metric == "custom_silicon_run_rate"].value.iloc[0]
    amd = met[met.metric == "dc_segment_revenue_annualized"].value.iloc[0]
    used = met[met.metric.isin(["capex_guidance_mid", "dc_hyperscale_revenue_annualized",
                                "ai_semiconductor_revenue_annualized", "custom_silicon_run_rate",
                                "dc_segment_revenue_annualized"])]
    c = Chart(
        id="15-hyperscaler-capex-vs-silicon-2026",
        title=(f"Est.: NVIDIA's ~${nv:.0f}B hyperscale run-rate equals ~{nv / cap_total * 100:.0f}% of the "
               f"Big-4's ~${cap_total:.0f}B 2026 capex"),
        subtitle=("US$ B per year, 2026: Big-4 capex guidance (midpoints) vs annualized supplier run-rates; scopes differ "
                  "(see notes): an order-of-magnitude view of who captures the hyperscaler AI dollar"),
        alt=(f"Horizontal bar chart. The four largest hyperscalers guide about ${cap_total:.0f}B of 2026 capex (Amazon ~$220B, "
             f"Alphabet ~$200B, Microsoft ~$170B, Meta ~$138B, midpoints). Against that, NVIDIA's hyperscale Data Center revenue "
             f"annualizes to about ${nv:.0f}B (first half of FY2027 times two), roughly {nv / cap_total * 100:.0f}% of the capex; "
             f"Broadcom's AI semiconductor revenue annualizes to about ${avgo:.0f}B (Q3 FY2026 times four, including networking "
             f"and non-hyperscaler customers); Amazon's own custom-silicon business passed a ${aws:.0f}B run rate; AMD's whole "
             f"Data Center segment annualizes to about ${amd:.0f}B. Most capex goes to buildings, power, networking and memory, "
             f"not accelerators."),
        data=[MET], chapters=["15", "12", "18"],
        source="company guidance and filings; repo annualization", source_ids=sources_of(used) + ["S15014"],
        note="Est.: run-rates annualized by repo; scopes not identical",
    )
    fig, ax = c.figure(width=11.5, height=5.6)
    labels = ["Big-4 capex 2026 (guidance midpoints)", "NVIDIA hyperscale DC revenue (H1 FY27 ×2)",
              "Broadcom AI semis (Q3 FY26 ×4)", "AMD Data Center segment (Q3 2026 ×4)", "Amazon custom silicon run-rate"]
    y = np.arange(len(labels))[::-1]
    # stacked capex bar
    left = 0
    order = ["Amazon", "Alphabet", "Microsoft", "Meta"]
    for comp in order:
        v = cap[cap.entity == comp].value.iloc[0]
        col = entity_color("AWS" if comp == "Amazon" else ("Google" if comp == "Alphabet" else comp))
        ax.barh(y[0], v, left=left, color=col, height=0.6, edgecolor="#FFFFFF")
        ax.annotate(f"{comp}\n${v:.0f}B", (left + v / 2, y[0]), ha="center", va="center", fontsize=8, color="#FFFFFF",
                    fontweight="bold")
        left += v
    ax.annotate(f"${cap_total:.0f}B", (cap_total, y[0]), xytext=(4, 0), textcoords="offset points", va="center",
                fontsize=9.5, color=INK["title"], fontweight="bold")
    others = [(nv, NV), (avgo, entity_color("Broadcom")), (amd, AMD), (aws, AWS)]
    for yi, (v, col) in zip(y[1:], others):
        b = ax.barh(yi, v, color=col, height=0.6)
        hatch_future(b, [True])
        ax.annotate(f"${v:.0f}B  ({v / cap_total * 100:.0f}% of Big-4 capex)", (v, yi), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlim(0, cap_total * 1.12)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    _below([ax])
    _margins(fig, left=0.30, right=0.97)
    c.save(fig, ax, xlabel="US$ B per year", legend=False, top=0.82, bottom=0.15)


# ======================================================================================
# Per-competitor radars (competitor_matrix.csv capability axes)
# ======================================================================================
SHORT = {"Peak compute": "Compute", "Memory capacity & bandwidth": "Memory", "Scale-up fabric": "Scale-up",
         "Scale-out networking": "Scale-out", "Software ecosystem": "Software", "Rack-scale systems": "Racks",
         "Supply access (CoWoS/HBM)": "Supply", "Cost/TCO": "Cost/TCO", "Merchant availability": "Merchant"}


def _single_radar(comp: str, chart_id: str, color: str, story: str):
    df = load(MAT)
    d = df[df.dimension_type == "capability"]
    names = list(d[d.competitor == "NVIDIA"].dimension)
    nv = d[d.competitor == "NVIDIA"].set_index("dimension").score_0_5.reindex(names).values.astype(float)
    sub = d[d.competitor == comp].set_index("dimension").reindex(names)
    vals = sub.score_0_5.values.astype(float)
    mean = vals.mean()
    leads = [SHORT[n] for n in names if sub.loc[n, "verdict_vs_nvidia"] == "leads"]
    ahead = [SHORT[n] for n, v, r in zip(names, vals, nv) if v > r]
    behind = [SHORT[n] for n, v, r in zip(names, vals, nv) if v < r - 1.5]
    if ahead:
        title = f"{comp} averages {mean:.1f} of 5 vs NVIDIA's {nv.mean():.1f}, ahead only on {' and '.join(ahead)}"
    else:
        title = f"{comp} averages {mean:.1f} of 5 vs NVIDIA's {nv.mean():.1f} and is ahead on no axis"
    pairs = "; ".join(f"{SHORT[n]} {v:.0f} vs {r:.0f}" for n, v, r in zip(names, vals, nv))
    alt = (f"Radar chart of {comp} against NVIDIA on nine capability axes scored 0-5 (repo analyst judgement): {pairs}. "
           f"Average {mean:.1f} vs {nv.mean():.1f}. " + story)
    srcs = sources_of(df[(df.dimension_type == "capability") & (df.competitor.isin([comp, "NVIDIA"]))])
    c = Chart(
        id=chart_id, title=title,
        subtitle=f"Capability scores 0-5; {comp} (filled) vs NVIDIA reference (dashed green); analyst judgement with sourced rationale",
        alt=alt, data=[MAT], chapters=["15"], source="repo analysis (competitor_matrix.csv)", source_ids=srcs,
        note="Analyst judgement (speculative)",
    )
    n = len(names)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angc = ang + ang[:1]
    fig, ax = c.figure(width=8.6, height=7.2, subplot_kw=dict(projection="polar"))
    ax.plot(angc, list(nv) + [nv[0]], color=NV, lw=1.8, ls="--", label="NVIDIA")
    ax.fill(angc, list(vals) + [vals[0]], color=color, alpha=0.28)
    ax.plot(angc, list(vals) + [vals[0]], color=color, lw=2.2, label=comp)
    ax.scatter(ang, vals, color=color, s=30, zorder=3)
    for a, v in zip(ang, vals):
        ax.annotate(f"{v:.0f}", (a, v), xytext=(0, 7), textcoords="offset points", ha="center", fontsize=9,
                    color=color if comp != "Intel" else INK["title"], fontweight="bold")
    ax.set_ylim(0, 5.4)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1", "2", "3", "4", "5"], fontsize=7, color=INK["muted"])
    ax.set_xticks(ang)
    ax.set_xticklabels([SHORT[a] for a in names], fontsize=9.5, color=INK["text"])
    ax.tick_params(axis="x", pad=6)
    ax.grid(color=INK["grid"], lw=0.7)
    ax.spines["polar"].set_color(INK["base"])
    fig.legend(handles=[Line2D([0], [0], color=NV, ls="--", lw=1.8, label="NVIDIA reference"),
                        Patch(facecolor=color, alpha=0.5, label=comp)],
               loc="lower right", bbox_to_anchor=(0.98, 0.05), ncol=1, fontsize=9, frameon=False)
    _margins(fig, left=0.10, right=0.84)
    c.save(fig, [ax], legend=False, top=0.80, bottom=0.10)


@register
def radar_amd():
    _single_radar("AMD", "15-radar-amd", AMD,
                  "AMD leads only on memory and sits close on compute, cost and merchant availability; its weakest axes are "
                  "scale-up fabric and rack-scale systems (2 each) until Helios ramps.")


@register
def radar_google_tpu():
    _single_radar("Google TPU", "15-radar-google-tpu", GOOG,
                  "Google's TPU leads on scale-up domain size and cost, but scores 2 on merchant availability and 3 on the "
                  "software ecosystem outside Google.")


@register
def radar_aws_trainium():
    _single_radar("AWS Trainium", "15-radar-aws-trainium", AWS,
                  "Trainium is built for cost inside AWS: strong on cost and racks, weak on software (2) and merchant "
                  "availability (1, AWS-only).")


@register
def radar_microsoft_maia():
    _single_radar("Microsoft Maia", "15-radar-microsoft-maia", MSFT,
                  "Maia is an internal inference program: mid-range on silicon, weak on software and supply, and zero on "
                  "merchant availability.")


@register
def radar_meta_mtia():
    _single_radar("Meta MTIA", "15-radar-meta-mtia", META,
                  "MTIA is a different approach: strong on PyTorch software and Meta's in-house Ethernet, weak on scale-up "
                  "and supply, and zero on merchant availability.")
