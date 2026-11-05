"""Layer 10 (Libraries, CUDA-X) strategy charts: library coverage heatmap and tally, AMD port lag,
CUTLASS architecture lead time, replication cost ladder, software deal values, NCCL vs RCCL versions.

Owner: layer-10 STRATEGY agent. Data: data/l10_library_coverage.csv, l10_port_versions.csv,
l10_cutlass_arch_support.csv, l10_replication_costs.csv, l10_software_deals.csv (documented in
data/README.md); also reads the shared gpu_architecture_cadence.csv.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.patches import Patch, Rectangle

from style import AS_OF, Chart, INK, NV, VERDICT_COLORS, entity_color, load, register, sources_of

COV = "l10_library_coverage.csv"
PORT = "l10_port_versions.csv"
CUT = "l10_cutlass_arch_support.csv"
REPL = "l10_replication_costs.csv"
DEALS = "l10_software_deals.csv"
CADENCE = "gpu_architecture_cadence.csv"

VENDORS = ["NVIDIA", "AMD", "Intel", "Google", "AWS", "Huawei"]
LETTER = {"leads": "L", "parity": "P", "behind": "B", "different": "D"}
VERDICT_LABEL = {"leads": "L = rival leads NVIDIA", "parity": "P = parity", "behind": "B = rival behind",
                 "different": "D = different approach"}
REF_FILL = "#E4EFD6"
AMD = entity_color("AMD")
DAYS_PER_MONTH = 30.44


def _margins(fig, **over):
    """Chart.save() hard-codes left/right margins; widen them where long labels need room."""
    orig = fig.subplots_adjust

    def adjusted(*args, **kw):
        kw.update(over)
        return orig(*args, **kw)
    fig.subplots_adjust = adjusted


def _d(value) -> pd.Timestamp:
    """Parse YYYY-MM-DD or YYYY-MM (plotted mid-month)."""
    s = str(value).strip()
    if len(s) == 7:
        s += "-15"
    return pd.Timestamp(s)


def _vcolor(name: str) -> str:
    n = str(name)
    if n.startswith("NVIDIA"):
        return NV
    if n.startswith("Repo"):
        return entity_color("startups")
    return entity_color(n)


# --------------------------------------------------------------------------------------
# 1. Coverage heatmap: 15 library domains x 6 vendors
# --------------------------------------------------------------------------------------
@register
def library_coverage_heatmap():
    df = load(COV)
    doms = df.sort_values("domain_order").drop_duplicates("domain").domain.tolist()
    riv = df[df.vendor.ne("NVIDIA")]
    n_lead = int(riv.verdict_vs_nvidia.eq("leads").sum())
    par = riv[riv.verdict_vs_nvidia.eq("parity")].groupby("vendor").size()
    amd_par = int(par.get("AMD", 0))
    intel_par = int(par.get("Intel", 0))
    g_diff = int(((riv.vendor == "Google") & riv.verdict_vs_nvidia.eq("different")).sum())
    aws_diff = int(((riv.vendor == "AWS") & riv.verdict_vs_nvidia.eq("different")).sum())
    hw_beh = int(((riv.vendor == "Huawei") & riv.verdict_vs_nvidia.eq("behind")).sum())
    lead_txt = "No rival leads NVIDIA in any" if n_lead == 0 else f"Rivals lead NVIDIA in only {n_lead} cells of"
    c = Chart(
        id="10-library-coverage-heatmap",
        title=f"{lead_txt} of {len(doms)} library domains; AMD matches it in {amd_par}",
        subtitle="First-party accelerated libraries by domain and vendor, Nov 2026; cell = repo verdict letter + library (NVIDIA = reference)",
        alt=(f"Heatmap of {len(doms)} library domains (rows) against NVIDIA, AMD, Intel, Google, AWS and Huawei (columns). "
             f"No rival leads NVIDIA in any domain. AMD reaches parity in {amd_par} (dense math with rocBLAS/hipBLASLt, "
             f"collectives with RCCL, FFT/sparse) and Intel in {intel_par} (oneMKL, oneDNN, FFT/sparse); Google takes a "
             f"different, compiler- or service-based route in {g_diff} domains and AWS in {aws_diff}; Huawei trails in "
             f"{hw_beh}. Only NVIDIA has first-party GPU libraries for optimization (cuOpt), computational lithography "
             "(cuLitho), genomics (Parabricks) and graph analytics (cuGraph)."),
        data=[COV], chapters=["10", "15"], source="vendor library documentation; repo verdicts",
        source_ids=sources_of(df), note="Verdicts are analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=13.5, height=9.8)
    for i, dom in enumerate(doms):
        for j, ven in enumerate(VENDORS):
            r = df[(df.domain == dom) & (df.vendor == ven)].iloc[0]
            if ven == "NVIDIA":
                fill, text, weight = REF_FILL, str(r.cell_label), "bold"
            else:
                fill = VERDICT_COLORS[r.verdict_vs_nvidia]
                text = f"{LETTER[r.verdict_vs_nvidia]} · {r.cell_label}"
                weight = "bold" if r.verdict_vs_nvidia in ("leads", "parity") else "normal"
            ax.add_patch(Rectangle((j + 0.03, i + 0.06), 0.94, 0.88, facecolor=fill, edgecolor="#FFFFFF", linewidth=1.2))
            ax.text(j + 0.5, i + 0.5, text, ha="center", va="center", fontsize=7.6, color=INK["title"], fontweight=weight)
    ax.set_xlim(0, len(VENDORS))
    ax.set_ylim(len(doms), 0)
    ax.set_xticks(np.arange(len(VENDORS)) + 0.5)
    ax.set_xticklabels(["NVIDIA (reference)"] + VENDORS[1:], fontsize=9.5, fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(np.arange(len(doms)) + 0.5)
    ax.set_yticklabels(doms, fontsize=9)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    handles = [Patch(facecolor=REF_FILL, edgecolor="#FFFFFF", label="NVIDIA library (reference)")]
    handles += [Patch(facecolor=VERDICT_COLORS[k], edgecolor="#FFFFFF", label=v) for k, v in VERDICT_LABEL.items()]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.005), ncol=5, fontsize=8.8, frameon=False)
    _margins(fig, left=0.185, right=0.99)
    c.save(fig, ax, legend=False, top=0.865, bottom=0.075)


# --------------------------------------------------------------------------------------
# 2. Coverage tally: verdict counts per rival
# --------------------------------------------------------------------------------------
@register
def library_coverage_tally():
    df = load(COV)
    riv = df[df.vendor.ne("NVIDIA")]
    n = riv.domain.nunique()
    order_v = ["leads", "parity", "different", "behind"]
    piv = riv.pivot_table(index="vendor", columns="verdict_vs_nvidia", values="domain", aggfunc="count", fill_value=0)
    for k in order_v:
        if k not in piv.columns:
            piv[k] = 0
    piv = piv[order_v].copy()
    piv["score"] = piv["leads"] * 2 + piv["parity"]
    piv = piv.sort_values(["score", "different"], ascending=[True, True])
    amd, intel = int(piv.loc["AMD", "parity"]), int(piv.loc["Intel", "parity"])
    leads = int(piv["leads"].sum())
    g_diff = int(piv.loc["Google", "different"])
    hw_beh = int(piv.loc["Huawei", "behind"])
    if amd == intel:
        head = f"AMD and Intel each match NVIDIA in only {amd} of {n} library domains"
    else:
        head = f"AMD and Intel match NVIDIA in only {amd} and {intel} of {n} library domains"
    c = Chart(
        id="10-library-coverage-tally",
        title=head + ("; none leads" if leads == 0 else f"; rivals lead in {leads}"),
        subtitle=f"Count of the {n} library domains by repo verdict versus NVIDIA, per rival (Nov 2026)",
        alt=(f"Stacked bar chart counting, for each rival, how many of {n} accelerated-library domains it leads, matches, "
             f"approaches differently or trails NVIDIA in. AMD: {amd} parity and {int(piv.loc['AMD', 'behind'])} behind. "
             f"Intel: {intel} parity, {int(piv.loc['Intel', 'different'])} different, {int(piv.loc['Intel', 'behind'])} behind. "
             f"Google: {g_diff} different (compiler or managed service) and {int(piv.loc['Google', 'behind'])} behind. "
             f"AWS: {int(piv.loc['AWS', 'different'])} different and {int(piv.loc['AWS', 'behind'])} behind. "
             f"Huawei: {hw_beh} behind. No rival leads in any domain."),
        data=[COV], chapters=["10", "15"], source="repo verdicts in l10_library_coverage.csv",
        source_ids=sources_of(riv), note="Analyst judgement (speculative)",
    )
    fig, ax = c.figure(width=10.5, height=5.2)
    y = np.arange(len(piv))
    left = np.zeros(len(piv))
    for k in order_v:
        vals = piv[k].values.astype(float)
        ax.barh(y, vals, left=left, color=VERDICT_COLORS[k], edgecolor="#FFFFFF", height=0.62,
                label=VERDICT_LABEL[k])
        for yi, (lf, v) in enumerate(zip(left, vals)):
            if v > 0:
                ax.text(lf + v / 2, yi, f"{int(v)} {LETTER[k]}", ha="center", va="center", fontsize=9,
                        color=INK["title"], fontweight="bold" if k in ("leads", "parity") else "normal")
        left = left + vals
    ax.set_yticks(y, piv.index)
    ax.set_xlim(0, n)
    ax.set_xticks(range(0, n + 1, 3))
    ax.set_axisbelow(True)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=4, fontsize=8.8, frameon=False)
    _margins(fig, left=0.11, right=0.97)
    c.save(fig, ax, xlabel=f"Number of library domains (of {n})", legend=False, bottom=0.27)


# --------------------------------------------------------------------------------------
# 3. Port lag: days from NVIDIA's release to AMD's compatible port shipping
# --------------------------------------------------------------------------------------
def _ports() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = load(PORT, dtype=str)
    df["t"] = df.release_date.map(_d)
    base = df[df.upstream_library.isna()].copy()
    up_map = {(r.library, r.version): r.t for r in base.itertuples()}
    ports = df[df.upstream_library.notna()].copy()
    ports["up_t"] = [up_map[(r.upstream_library, r.upstream_version)] for r in ports.itertuples()]
    ports["lag_d"] = (ports.t - ports.up_t).dt.days
    return df, ports


@register
def port_lag_amd_vs_nvidia():
    df, ports = _ports()
    first = ports.drop_duplicates(subset=["library", "version"], keep="first").sort_values("t")
    rccl = first[first.library.eq("RCCL")]
    hip = first[first.library.eq("hipDF")]
    worst = rccl.loc[rccl.lag_d.idxmax()]
    last = rccl.iloc[-1]
    hip_m = hip.lag_d.iloc[0] / DAYS_PER_MONTH
    c = Chart(
        id="10-port-lag-amd-vs-nvidia",
        title=(f"AMD's NCCL port now trails by ~{last.lag_d / DAYS_PER_MONTH:.0f} months, down from "
               f"~{worst.lag_d / DAYS_PER_MONTH:.0f}; hipDF trails cuDF ~{hip_m:.0f} months"),
        subtitle="Days from NVIDIA's release of a version to AMD shipping the matching port (RCCL in ROCm; hipDF in ROCm-DS)",
        alt=(f"Bar chart of how long AMD's ported libraries trail NVIDIA's originals. RCCL, AMD's port of NCCL, shipped "
             f"NCCL-compatible versions {', '.join(f'{int(v)}' for v in rccl.lag_d)} days after NVIDIA's matching NCCL "
             f"tag across ROCm releases from 5.4 (2022) to 7.1 (2025): the lag peaked at {int(worst.lag_d)} days with "
             f"{worst.release_vehicle} and fell to {int(last.lag_d)} days with {last.release_vehicle}. hipDF 2.0.0 "
             f"(ROCm-DS 25.10) aligned with cuDF 25.02 APIs, about {int(hip.lag_d.iloc[0])} days or {hip_m:.0f} months "
             "behind."),
        data=[PORT], chapters=["10", "15", "09"], source="NCCL tags, RCCL changelog, ROCm and RAPIDS release notes",
        source_ids=sources_of(pd.concat([first, df[df.upstream_library.isna()]])), note="Hatched = month-precision date",
    )
    fig, ax = c.figure(width=11.5, height=5.6)
    rows = pd.concat([rccl, hip])
    x = np.arange(len(rows), dtype=float)
    x[-1] += 0.6
    for xi, r in zip(x, rows.itertuples()):
        is_hip = r.library == "hipDF"
        bar = ax.bar(xi, r.lag_d, width=0.66, color=AMD, alpha=0.55 if is_hip else 0.9,
                     edgecolor=AMD, linewidth=1.2)
        if is_hip:
            bar.patches[0].set_hatch("///")
        ax.annotate(f"{int(r.lag_d)} d\n{r.lag_d / DAYS_PER_MONTH:.1f} mo", (xi, r.lag_d), xytext=(0, 3),
                    textcoords="offset points", ha="center", va="bottom", fontsize=8, color=INK["title"])
    ax.axvline(x[-1] - 0.8, color=INK["base"], lw=1, ls=":")
    labels = [f"{r.release_vehicle.replace(' (GA)', '')}\n{r.library} {r.version}" for r in rows.itertuples()]
    ax.set_xticks(x, labels, fontsize=7.8)
    ax.set_ylim(0, max(rows.lag_d.max() * 1.22, 100))
    ax.text(x[-1], ax.get_ylim()[1] * 0.96, "Dataframes", ha="center", va="top", fontsize=8.5, color=INK["muted"])
    ax.text(x[0] - 0.3, ax.get_ylim()[1] * 0.96, "Collectives (RCCL vs NCCL)", ha="left", va="top", fontsize=8.5,
            color=INK["muted"])
    _margins(fig, left=0.07, right=0.985)
    c.save(fig, ax, ylabel="Days behind NVIDIA's release", legend=False, bottom=0.17)


# --------------------------------------------------------------------------------------
# 4. CUTLASS lead time: days from first volume shipments to CUTLASS support
# --------------------------------------------------------------------------------------
@register
def cutlass_architecture_lead_time():
    cs = load(CUT, dtype={"cutlass_version": str})
    cad = load(CADENCE)
    avail = dict(zip(cad.architecture, cad.first_availability))
    cs["avail_t"] = cs.architecture.map(lambda a: _d(avail[a]))
    cs["t"] = cs.cutlass_date.map(_d)
    cs["days"] = (cs.t - cs.avail_t).dt.days
    first = cs[cs.milestone.eq("first support")].reset_index(drop=True)
    native = cs[cs.milestone.eq("native kernels")]
    mx = int(first.days.max())
    used_cad = cad[cad.architecture.isin(cs.architecture)]
    c = Chart(
        id="10-cutlass-architecture-lead-time",
        title=f"CUTLASS supported each new NVIDIA GPU within {mx} days of first volume shipments",
        subtitle="Days from first volume availability (month, plotted mid-month) to the CUTLASS release adding that architecture",
        alt=("Horizontal bar chart of how quickly NVIDIA's open-source CUTLASS kernel library supported each new data-center "
             "GPU after first volume shipments: " + "; ".join(
                 f"{r.architecture} {int(r.days)} days (CUTLASS {r.cutlass_version}, {r.cutlass_date})" for r in first.itertuples())
             + (f". Hopper's native TMA and WGMMA kernels built on CuTe followed in CUTLASS 3.0 after "
                f"{int(native.days.iloc[0])} days" if not native.empty else "")
             + ". Libraries arrive with the silicon because NVIDIA co-designs both."),
        data=[CUT, CADENCE], chapters=["10", "09", "17"], source="CUTLASS changelog; NVIDIA availability dates",
        source_ids=sources_of(cs) + [s for s in sources_of(used_cad) if s not in sources_of(cs)],
        note="Availability months are placeholders where NVIDIA gave a quarter",
    )
    fig, ax = c.figure(width=10.5, height=5.0)
    y = np.arange(len(first))[::-1]
    ax.barh(y, first.days, color=NV, height=0.56, label="First CUTLASS support")
    for yi, r in zip(y, first.itertuples()):
        ax.text(r.days + 1.5, yi, f"{int(r.days)} d", va="center", fontsize=9, color=INK["title"], fontweight="bold")
    for r in native.itertuples():
        yi = y[first.index[first.architecture.eq(r.architecture)][0]]
        ax.scatter(r.days, yi, marker="D", s=70, facecolor="white", edgecolor=NV, linewidth=2, zorder=4,
                   label="Native kernels (Hopper: CUTLASS 3.0, TMA + WGMMA)")
        ax.text(r.days + 2.5, yi, f"{int(r.days)} d", va="center", fontsize=9, color=INK["title"])
    ax.set_yticks(y, [f"{r.architecture} ({r.sm_target})\nCUTLASS {r.cutlass_version}, {r.cutlass_date}"
                      for r in first.itertuples()], fontsize=8.8)
    ax.set_xlim(0, max(110, cs.days.max() * 1.15))
    ax.set_axisbelow(True)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="lower right", fontsize=8.8)
    _margins(fig, left=0.24, right=0.97)
    c.save(fig, ax, xlabel="Days after first volume availability", legend=False)


# --------------------------------------------------------------------------------------
# 5. Replication cost ladder
# --------------------------------------------------------------------------------------
@register
def replication_cost_ladder():
    df = load(REPL).sort_values("value_usd_b").reset_index(drop=True)
    core = df[df["item"].str.contains("AI-core")].value_usd_b.item()
    full = df[df["item"].str.contains("15-domain")].value_usd_b.item()
    nv = df[df["item"].str.startswith("NVIDIA annual")].value_usd_b.item()
    months = core / nv * 12
    c = Chart(
        id="10-replication-cost-ladder",
        title=f"Est.: an AI-core library stack costs ~${core:.0f}B over 5 years, ~{months:.0f} months of NVIDIA's R&D",
        subtitle="US$ billions: software deals, R&D budgets and repo estimates of building CUDA-X-class libraries",
        alt=(f"Horizontal bar chart of software-replication cost reference points: AMD's Silo AI purchase $0.67B (2024), "
             f"NVIDIA's Run:ai about $0.7B (2024), AMD's R&D increase from 2022 to 2024 of about $1.45B a year, a repo "
             f"estimate of ${core:.0f}B for an AI-core library stack (1,500 engineers for five years at $0.4M each), "
             f"Qualcomm's announced $3.9B Modular deal, AMD's $6.5B total 2024 R&D, a repo estimate of ${full:.0f}B for "
             f"full 15-domain breadth over ten years, and NVIDIA's ${nv:.1f}B FY2026 R&D. Money is not the binding "
             "constraint; time and specialist talent are."),
        data=[REPL], chapters=["10", "13"], source="filings, deal reports and repo estimates", source_ids=sources_of(df),
        note="Hatched = repo estimate (speculative)",
    )
    fig, ax = c.figure(width=11, height=5.6)
    y = np.arange(len(df))
    for yi, r in zip(y, df.itertuples()):
        est = r.category == "estimate"
        col = _vcolor(r.entity)
        bar = ax.barh(yi, r.value_usd_b, color=col, height=0.6, alpha=0.75 if est else 0.92)
        if est:
            bar.patches[0].set_hatch("///")
        txt = f"${r.value_usd_b:.2f}B" if r.value_usd_b < 1 else f"${r.value_usd_b:.1f}B"
        ax.text(r.value_usd_b + 0.2, yi, txt, va="center", fontsize=9, color=INK["title"])
    labels = [str(it).replace(" (", "\n(").replace(" x ", " × ") for it in df["item"]]
    ax.set_yticks(y, labels, fontsize=8.6)
    ax.set_xlim(0, nv * 1.15)
    ax.set_axisbelow(True)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=AMD, label="AMD"),
               Patch(color=entity_color("qualcomm"), label="Qualcomm"),
               Patch(facecolor=entity_color("startups"), hatch="///", edgecolor="white", label="Repo estimate")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _margins(fig, left=0.27, right=0.97)
    c.save(fig, ax, xlabel="US$ billions", legend=False)


# --------------------------------------------------------------------------------------
# 6. Software and library deal values
# --------------------------------------------------------------------------------------
@register
def software_deal_values():
    df = load(DEALS)
    d = df.copy()
    d["year"] = d.announce_date.astype(str).str[:4]
    d["label"] = d.apply(lambda r: f"{r.target} ← {r.acquirer} ({r.year})", axis=1)
    d = d.sort_values(["value_usd_m", "announce_date"], na_position="first").reset_index(drop=True)
    q = d[d.acquirer.eq("Qualcomm")].value_usd_m.max()
    others = d[d.deal_type.eq("acquisition") & ~d.acquirer.eq("Qualcomm")]
    top = others.loc[others.value_usd_m.idxmax()]
    ratio = q / top.value_usd_m
    silo = d[d.target.eq("Silo AI")].value_usd_m.item()
    recent = d[d.deal_type.eq("acquisition") & (d.year.astype(int) >= 2022)]
    n_recent, n_priced = len(recent), int(recent.value_usd_m.notna().sum())
    c = Chart(
        id="10-software-deal-values",
        title=(f"{n_priced} of {n_recent} sampled software buys since 2022 have prices; Qualcomm's "
               f"${q / 1000:.1f}B tops them"),
        subtitle="Disclosed or reported value, US$ millions (log scale): a sample of library, AI-software and tools deals by chip vendors",
        alt=(f"Log-scale horizontal bar chart of a sample of library, AI-software and tools deals by chip vendors: {n_recent} "
             f"acquisitions since 2022, {n_priced} with public prices. Qualcomm's announced ${q:,.0f}M Modular acquisition (2026) is "
             f"~{ratio:.1f}x the largest earlier one, NVIDIA's ${top.value_usd_m:,.0f}M Run:ai (2024, reported); then $400M CentML, $300M Deci, "
             f"$250M OctoAI and $88M mental images; AMD's ${silo:,.0f}M Silo AI (2024); NVIDIA's $2,000M Synopsys equity "
             "stake (2025, not an acquisition). AMD's Mipsology, Nod.ai and Brium, Intel's Codeplay and NVIDIA's Ageia, "
             "PGI, Bright Computing and Excelero were undisclosed."),
        data=[DEALS], chapters=["10", "13", "19"], source="company releases and press", source_ids=sources_of(d),
        note="Hollow = equity stake; hatched = reported/announced",
    )
    fig, ax = c.figure(width=11, height=6.6)
    y = np.arange(len(d))
    for yi, r in zip(y, d.itertuples()):
        col = _vcolor(r.acquirer)
        if pd.isna(r.value_usd_m):
            ax.text(60, yi, "undisclosed", va="center", fontsize=8.6, color=INK["muted"], style="italic")
            continue
        equity = r.deal_type == "equity-investment"
        bar = ax.barh(yi, r.value_usd_m, color="white" if equity else col, edgecolor=col,
                      linewidth=2 if equity else 0, height=0.62)
        if r.value_basis in ("reported", "announced") and not equity:
            bar.patches[0].set_hatch("///")
            bar.patches[0].set_alpha(0.8)
        txt = f"${r.value_usd_m / 1000:.1f}B" if r.value_usd_m >= 1000 else f"~${r.value_usd_m:,.0f}M"
        if equity:
            txt += " (equity stake)"
        elif r.status == "announced":
            txt += " (announced)"
        ax.text(r.value_usd_m * 1.12, yi, txt, va="center", fontsize=8.8, color=INK["title"])
    ax.set_axisbelow(True)
    ax.set_yticks(y, d.label, fontsize=8.6)
    ax.set_ylim(-0.7, len(d) - 0.4)
    ax.set_xscale("log")
    ax.set_xlim(50, 30000)
    ax.grid(axis="x")
    ax.grid(axis="y", visible=False)
    handles = [Patch(color=NV, label="NVIDIA"), Patch(color=AMD, label="AMD"),
               Patch(color=entity_color("intel"), label="Intel"),
               Patch(color=entity_color("qualcomm"), label="Qualcomm")]
    ax.legend(handles=handles, loc="lower right", fontsize=8.8)
    _margins(fig, left=0.29, right=0.97)
    c.save(fig, ax, xlabel="Deal value, US$ millions", logx=True, legend=False)


# --------------------------------------------------------------------------------------
# 7. NCCL vs RCCL version progression
# --------------------------------------------------------------------------------------
@register
def nccl_rccl_version_progression():
    df = load(PORT, dtype=str)
    df["t"] = df.release_date.map(_d)
    nc = df[df.library.eq("NCCL")].copy()
    nc["minor"] = nc.version.str.split(".").str[1].astype(int)
    first = nc.groupby("minor", as_index=False).t.min().sort_values("t").reset_index(drop=True)
    rc = df[df.library.eq("RCCL")].copy()
    rc["minor"] = rc.upstream_version.str.split(".").str[1].astype(int)
    rc = rc.sort_values("t").reset_index(drop=True)
    gaps = [int(first[first.t <= r.t].minor.max() - r.minor) for r in rc.itertuples()]
    n_minors = int(first.minor.max() - first.minor.min())
    years = (first.t.max() - first.t.min()).days / 365.25
    asof = pd.Timestamp(AS_OF)
    c = Chart(
        id="10-nccl-rccl-version-progression",
        title=(f"NCCL advanced {n_minors} minor versions in ~{years:.0f} years; AMD's RCCL port shipped "
               f"{min(gaps)}–{max(gaps)} versions behind"),
        subtitle="NCCL 2.x minor version over time (first GitHub tag of each minor) vs the NCCL version each ROCm release's RCCL matches",
        alt=(f"Step chart of NCCL's minor version from 2.{first.minor.min()} (July 2022) to 2.{first.minor.max()} "
             f"(September 2026), with RCCL's NCCL-compatible version at each ROCm release from 5.4 to 7.2. RCCL trailed by "
             f"{min(gaps)} to {max(gaps)} minor versions; the gap was largest at ROCm 6.4 (2.22 vs 2.26) and narrowest at "
             "ROCm 7.0 and 7.1 (2.26 and 2.27, one behind). NCCL milestones: device API and copy-engine collectives (2.28, "
             "Oct 2025), TMA and elastic buffers (2.30, Apr 2026), initial Rubin support (2.32, Sep 2026)."),
        data=[PORT], chapters=["10", "06", "17"], source="NCCL GitHub tags and release notes; RCCL changelog; ROCm releases",
        source_ids=sources_of(df), note="Squares = ROCm release dates",
    )
    fig, ax = c.figure(width=11.5, height=6.0)
    ax.step(first.t, first.minor, where="post", color=NV, lw=2.4, label="NCCL (NVIDIA), first tag of each 2.x minor")
    ax.plot([first.t.iloc[-1], asof], [first.minor.iloc[-1]] * 2, color=NV, lw=2.4)
    ax.scatter(first.t, first.minor, color=NV, s=30, zorder=4)
    ax.step(rc.t, rc.minor, where="post", color=AMD, lw=2.0, label="RCCL (AMD) in ROCm: NCCL version it matches")
    ax.plot([rc.t.iloc[-1], asof], [rc.minor.iloc[-1]] * 2, color=AMD, lw=2.0, ls="--")
    ax.scatter(rc.t, rc.minor, color=AMD, marker="s", s=48, zorder=5)
    for r, g in zip(rc.itertuples(), gaps):
        ax.annotate(f"{r.release_vehicle.replace('ROCm ', '')}\n−{g}", (r.t, r.minor), xytext=(5, -5),
                    textcoords="offset points", ha="left", va="top", fontsize=7.2, color=AMD)
    notes = {28: "2.28: device API, copy-engine collectives", 30: "2.30: TMA kernels, elastic buffers",
             32: "2.32: initial Rubin support"}
    for m, txt in notes.items():
        row = first[first.minor.eq(m)]
        if row.empty:
            continue
        ax.annotate(txt, (row.t.iloc[0], m), xytext=(-8, 2), textcoords="offset points", ha="right", va="bottom",
                    fontsize=8.2, color=INK["title"])
    lo, hi = int(first.minor.min()), int(first.minor.max())
    ax.set_ylim(lo - 3, hi + 1.5)
    ticks = list(range(lo - 1, hi + 2, 2))
    ax.set_yticks(ticks, [f"2.{t}" for t in ticks])
    ax.set_xlim(pd.Timestamp("2022-05-01"), pd.Timestamp("2027-01-15"))
    ax.legend(loc="upper left", fontsize=8.8)
    _margins(fig, left=0.07, right=0.98)
    c.save(fig, ax, xlabel="Release date", ylabel="NCCL 2.x minor version", legend=False)
