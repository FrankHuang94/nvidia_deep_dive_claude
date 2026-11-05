"""Software-ecosystem charts (chapters 09, 10, 11, CS2) built from data/software_ecosystem.csv.
Owner: Phase-1 agent A5."""
from __future__ import annotations

import re
from datetime import date

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, load, register,
                   sources_of)

VENDORS = [  # metric suffix, column label, entity for colour
    ("nvidia_cuda", "NVIDIA\nCUDA", "NVIDIA"),
    ("amd_rocm", "AMD\nROCm", "AMD"),
    ("intel_oneapi_gaudi", "Intel\noneAPI/Gaudi", "Intel"),
    ("google_tpu_xla", "Google\nTPU (XLA)", "Google"),
    ("aws_neuron", "AWS\nNeuron", "AWS"),
    ("huawei_cann", "Huawei\nCANN", "Huawei"),
    ("qualcomm_cloud_ai", "Qualcomm\nCloud AI", "Qualcomm"),
]
LEVEL_COLOR = {0: "#F0EFEC", 1: "#CDE2FB", 2: "#86B6EF", 3: "#256ABF"}
LEVEL_TEXT = {0: "0 · None", 1: "1 · Exp.", 2: "2 · Supported", 3: "3 · Native"}


def _yf(s: str) -> float:
    s = str(s)
    m = re.fullmatch(r"(\d{4})", s)
    if m:
        return int(m.group(1)) + 0.5
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m:
        return int(m.group(1)) + (int(m.group(2)) - 0.5) / 12
    y, mo, d = (int(x) for x in s.split("-"))
    return y + (date(y, mo, d) - date(y, 1, 1)).days / 365.25


def _fig_axes(width, height, rect):
    fig = plt.figure(figsize=(width, height))
    return fig, fig.add_axes(rect)


def _ts(metric: str, entity: str | None = None):
    df = load("software_ecosystem.csv", dtype={"value": str})
    d = df[(df.record_type == "time_series") & (df.metric == metric)].copy()
    if entity:
        d = d[d.entity == entity]
    d["x"] = d.date.map(_yf)
    return d.sort_values("x")


def _matrix():
    df = load("software_ecosystem.csv", dtype={"value": str})
    d = df[df.record_type == "support_matrix"].copy()
    d["value"] = d.value.astype(int)
    d["vendor"] = d.metric.str.replace("support_", "", regex=False)
    return d


# --------------------------------------------------------------------------------------
# 1. CUDA developers over time
# --------------------------------------------------------------------------------------
@register
def cuda_developers_over_time():
    d = _ts("cuda_registered_developers")
    d["v"] = d.value.astype(float) / 1e6
    v2020 = d[d.date == "2020"].v.iloc[0]
    peak = d.v.max()
    first_peak = d[d.v == peak].iloc[0]
    last = d.iloc[-1]
    c = Chart(
        id="09-cuda-developers-over-time",
        title=(f"CUDA developers tripled from {v2020:.0f}M (2020) to ~{peak:.0f}M ({first_peak.date[:4]}); "
               f"NVIDIA still cited {last.v:.0f}M in {last.date[:4]}"),
        subtitle="Registered CUDA / NVIDIA developer-program members as stated by NVIDIA, millions",
        alt=(f"Line chart of NVIDIA-stated CUDA developers: about 1M around 2018 (estimate), 2M in 2020, 3M in "
             f"March 2022, 4M in May 2023, 5M in June 2024, 5.9M in February 2025 and about 6M at GTC 2025 and "
             f"again at GTC 2026 — a plateau in the rounded headline figure."),
        data=["software_ecosystem.csv"], chapters=["09", "CS2", "01"],
        source="NVIDIA keynotes, press releases and earnings calls", source_ids=sources_of(d),
    )
    fig, ax = c.figure(width=10, height=5.6)
    real = d[d.confidence != "estimate"]
    est = d[d.confidence == "estimate"]
    ax.plot(d.x, d.v, color=NV, lw=2, zorder=2)
    ax.plot(real.x, real.v, "o", ms=8, color=NV, mec=NV_DARK, zorder=3)
    ax.plot(est.x, est.v, "o", ms=8, mfc="white", mec=NV, mew=2, zorder=3)
    labels = {"2020": "2M\n(2020)", "2022-03-22": "3M\nGTC 2022", "2023-05-29": "4M\nComputex 2023",
              "2024-06-02": "5M\nComputex 2024", "2025-03-18": "6M\nGTC 2025", "2026-03-16": "6M\nGTC 2026"}
    for _, r in d.iterrows():
        if r.date in labels:
            ax.annotate(labels[r.date], (r.x, r.v), xytext=(0, 9), textcoords="offset points", ha="center",
                        va="bottom", fontsize=8.3, color=INK["title"])
    ax.annotate("Est. ~1M (from NVIDIA's\n'13 years to 1M' remark)", (est.x.iloc[0], est.v.iloc[0]),
                xytext=(10, -4), textcoords="offset points",
                ha="left", va="top", fontsize=8.3, color=INK["text"])
    ax.set_xlim(2017.5, 2026.8)
    ax.set_ylim(0, 7.6)
    ax.set_xticks(range(2018, 2027))
    c.save(fig, ax, xlabel="Calendar year", ylabel="Developers (millions)", legend=False)


# --------------------------------------------------------------------------------------
# 2. Framework support heatmap
# --------------------------------------------------------------------------------------
@register
def framework_support_heatmap():
    d = _matrix()
    frameworks = list(dict.fromkeys(d.entity))
    tot = d.groupby("vendor").value.sum()
    maxv = 3 * len(frameworks)
    c = Chart(
        id="09-framework-support-heatmap",
        title=(f"Only CUDA is native in all {len(frameworks)} major AI frameworks; ROCm "
               f"{tot['amd_rocm']}/{maxv}, Qualcomm {tot['qualcomm_cloud_ai']}/{maxv}"),
        subtitle=("Support level by framework and vendor stack, 2026-11-05: 0 none · 1 experimental · "
                  "2 supported · 3 native (breadth, not performance)"),
        alt=(f"Heatmap of {len(frameworks)} frameworks by 7 vendor stacks: NVIDIA CUDA is native (3) everywhere "
             f"({tot['nvidia_cuda']}/{maxv}); AMD ROCm {tot['amd_rocm']}, Intel {tot['intel_oneapi_gaudi']}, Huawei CANN "
             f"{tot['huawei_cann']}, Google TPU {tot['google_tpu_xla']}, AWS Neuron {tot['aws_neuron']} and Qualcomm Cloud "
             f"AI {tot['qualcomm_cloud_ai']}. TensorRT-LLM is NVIDIA-only; Ray and vLLM have the broadest hardware "
             f"coverage. Each cell is labelled with its level."),
        data=["software_ecosystem.csv"], chapters=["09", "15", "19"],
        source="Framework docs and READMEs (GitHub), vendor docs", source_ids=sources_of(d),
    )
    fig, ax = _fig_axes(11, 7.2, [0.13, 0.1, 0.85, 0.72])
    for i, fw in enumerate(frameworks):
        for j, (key, _, _) in enumerate(VENDORS):
            row = d[(d.entity == fw) & (d.vendor == key)].iloc[0]
            v = int(row.value)
            y = len(frameworks) - 1 - i
            ax.add_patch(mpatches.Rectangle((j, y), 0.96, 0.92, fc=LEVEL_COLOR[v], ec="white", lw=1))
            label = LEVEL_TEXT[v]
            if row.confidence == "speculative":
                label += " ?"
            ax.text(j + 0.48, y + 0.46, label, ha="center", va="center", fontsize=8,
                    color="#FFFFFF" if v == 3 else INK["title"])
    ax.set_xlim(0, len(VENDORS))
    ax.set_ylim(0, len(frameworks))
    ax.set_xticks([j + 0.48 for j in range(len(VENDORS))])
    ax.set_xticklabels([lab for _, lab, _ in VENDORS], fontsize=8.8)
    ax.xaxis.tick_top()
    ax.set_yticks([len(frameworks) - 1 - i + 0.46 for i in range(len(frameworks))])
    ax.set_yticklabels(frameworks, fontsize=9.2)
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    # totals row under the grid
    for j, (key, _, ent) in enumerate(VENDORS):
        ax.text(j + 0.48, -0.32, f"{tot[key]}/{maxv}", ha="center", va="center", fontsize=9,
                fontweight="bold", color=entity_color(ent), clip_on=False)
    ax.text(-0.08, -0.32, "Total", ha="right", va="center", fontsize=9, fontweight="bold",
            color=INK["title"], clip_on=False)
    ax.text(len(VENDORS), -0.62, "? = speculative (not verified in vendor docs this session)", ha="right",
            va="center", fontsize=7.6, color=INK["muted"], clip_on=False)
    c.save(fig, ax, legend=False)
    # interactive twin with the evidence for each cell on hover
    import plotly.graph_objects as go
    z, txt, hov = [], [], []
    for fw in frameworks:
        zr, tr, hr = [], [], []
        for key, lab, _ in VENDORS:
            row = d[(d.entity == fw) & (d.vendor == key)].iloc[0]
            zr.append(int(row.value))
            tr.append(LEVEL_TEXT[int(row.value)])
            hr.append(f"<b>{fw} × {lab.replace(chr(10), ' ')}</b><br>{row.notes}<br>"
                      f"Confidence: {row.confidence} · Sources: {row.source_id}")
        z.append(zr), txt.append(tr), hov.append(hr)
    scale = [[0, LEVEL_COLOR[0]], [0.33, LEVEL_COLOR[1]], [0.66, LEVEL_COLOR[2]], [1, LEVEL_COLOR[3]]]
    pfig = go.Figure(go.Heatmap(z=z, x=[lab.replace("\n", " ") for _, lab, _ in VENDORS], y=frameworks,
                                text=txt, texttemplate="%{text}", hovertext=hov, hoverinfo="text",
                                colorscale=scale, zmin=0, zmax=3, showscale=False, xgap=3, ygap=3))
    pfig.update_yaxes(autorange="reversed")
    pfig.update_xaxes(side="top")
    c.save_plotly(pfig, height=640)


# --------------------------------------------------------------------------------------
# 3. Support breadth by vendor (bar)
# --------------------------------------------------------------------------------------
@register
def framework_support_by_vendor():
    d = _matrix()
    n = d.entity.nunique()
    tot = d.groupby("vendor").value.sum()
    native = d[d.value == 3].groupby("vendor").size()
    order = [k for k, _, _ in VENDORS]
    vals = [int(tot.get(k, 0)) for k in order]
    nat = [int(native.get(k, 0)) for k in order]
    c = Chart(
        id="09-framework-support-by-vendor",
        title=(f"CUDA scores {vals[0]}/{3 * n} on framework support; ROCm {vals[1]}, Huawei {vals[5]}, "
               f"Qualcomm {vals[6]}"),
        subtitle=(f"Sum of 0–3 support scores across {n} AI frameworks (max {3 * n}); TPU and Neuron lean on "
                  "their own stacks (JAX, NxD)"),
        alt=(f"Horizontal bar chart of summed support scores across {n} frameworks: NVIDIA CUDA {vals[0]} of "
             f"{3 * n} (native in {nat[0]}), AMD ROCm {vals[1]} (native in {nat[1]}), Intel {vals[2]}, Huawei "
             f"CANN {vals[5]}, Google TPU {vals[3]} (native in JAX and TensorFlow), AWS Neuron {vals[4]} and "
             f"Qualcomm Cloud AI {vals[6]}."),
        data=["software_ecosystem.csv"], chapters=["09", "15", "19"],
        source="Framework docs and READMEs (GitHub), vendor docs", source_ids=sources_of(d),
    )
    fig, ax = _fig_axes(10, 5.4, [0.16, 0.13, 0.80, 0.70])
    ax.set_axisbelow(True)
    idx = sorted(range(len(order)), key=lambda i: -vals[i])
    labels = [VENDORS[i][1].replace("\n", " ") for i in idx]
    vals, nat = [vals[i] for i in idx], [nat[i] for i in idx]
    ys = list(range(len(order)))[::-1]
    bars = ax.barh(ys, vals, color=[entity_color(VENDORS[i][2]) for i in idx], height=0.62)
    for b, v, k in zip(bars, vals, nat):
        ax.text(b.get_width() + 0.4, b.get_y() + b.get_height() / 2, f"{v}  ({k} native)", va="center",
                fontsize=9, color=INK["title"])
    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlim(0, 3 * n + 6)
    ax.axvline(3 * n, color=INK["muted"], ls=":", lw=1)
    ax.grid(axis="x", color=INK["grid"])
    ax.grid(axis="y", visible=False)
    c.save(fig, ax, xlabel=f"Support score (max {3 * n})", legend=False)


CUDA_HEADLINE = {"1.0": "first release (G80)", "2.0": "double precision", "3.0": "Fermi; C++ in kernels",
                 "4.0": "unified virtual addressing", "5.0": "dynamic parallelism", "6.0": "Unified Memory",
                 "7.0": "C++11; runtime compile", "8.0": "Pascal; NVLink; FP16", "9.0": "Volta Tensor Cores",
                 "10.0": "Turing; CUDA Graphs", "11.0": "Ampere: TF32, MIG", "12.0": "Hopper / Ada",
                 "13.0": "Blackwell era; unified Arm"}

# --------------------------------------------------------------------------------------
# 4. CUDA major-release timeline
# --------------------------------------------------------------------------------------
@register
def cuda_release_timeline():
    d = _ts("cuda_release")
    major = d[d.notes.str.startswith("major")].copy()
    minor13 = d[d.value.str.startswith("13.") & d.notes.str.startswith("minor")]
    first, last = major.iloc[0], major.iloc[-1]
    years = int(last.date[:4]) - int(first.date[:4])
    c = Chart(
        id="09-cuda-release-timeline",
        title=f"CUDA shipped {len(major)} major versions in {years} years; 13.x minors now land quarterly",
        subtitle=("CUDA Toolkit major versions with headline additions, and 13.x minor releases "
                  "(pre-2019 months per NVIDIA's toolkit archive)"),
        alt=(f"Timeline of CUDA major versions from 1.0 (June 2007) to 13.0 (August 2025): {len(major)} majors, "
             f"each tied to a GPU architecture or programming-model addition such as double precision (2.0), "
             f"unified memory (6.0), Tensor Cores (9.0), CUDA Graphs (10.0), TF32/MIG (11.0) and Hopper (12.0); "
             f"{len(minor13)} 13.x minor releases followed by November 2026, including CUDA Tile in 13.1."),
        data=["software_ecosystem.csv"], chapters=["09", "CS2", "16"],
        source="NVIDIA CUDA Toolkit archive, release notes and PyPI", source_ids=sources_of(major) + [
            s for s in sources_of(minor13) if s not in sources_of(major)],
    )
    fig, ax = c.figure(width=11.5, height=5.8)
    ax.axhline(0, color=INK["base"], lw=1.2, zorder=1)
    for k, (_, r) in enumerate(major.iterrows()):
        what = CUDA_HEADLINE.get(r.value, "")
        up = k % 2 == 0
        h = (0.55 + 0.32 * ((k // 2) % 3)) * (1 if up else -1)
        col = NV if int(r.date[:4]) >= 2022 else GEN_PAST
        ax.plot([r.x, r.x], [0, h], color=col, lw=1.2, zorder=2)
        ax.plot(r.x, 0, "o", ms=9, color=col, mec=NV_DARK, zorder=3)
        ax.text(r.x, h + (0.04 if up else -0.04), f"CUDA {r.value}\n{what}", ha="center",
                va="bottom" if up else "top", fontsize=7.4, color=INK["title"], wrap=False)
    for _, r in minor13.iterrows():
        ax.plot(r.x, 0, "|", ms=12, mew=1.6, color=NV_DARK, zorder=3)
    ax.text(2026.95, -0.2, "13.1–13.5\nminors", fontsize=7.4, color=NV_DARK, ha="right", va="top")
    ax.set_ylim(-1.75, 1.85)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlim(2006.3, 2027.3)
    ax.set_xticks(range(2007, 2027, 2))
    ax.grid(False)
    c.save(fig, ax, xlabel="Release date", legend=False)


# --------------------------------------------------------------------------------------
# 5. CUDA vs ROCm release cadence
# --------------------------------------------------------------------------------------
@register
def cuda_vs_rocm_release_cadence():
    cu = _ts("cuda_release")
    ro = _ts("rocm_release")
    years = [2023, 2024, 2025, 2026]
    cu_n = [int((cu.date.str[:4] == str(y)).sum()) for y in years]
    ro_n = [int((ro.date.str[:4] == str(y)).sum()) for y in years]
    head = int(ro.iloc[0].date[:4]) - int(cu.iloc[0].date[:4])
    c = Chart(
        id="09-cuda-vs-rocm-release-cadence",
        title=(f"ROCm started {head} years after CUDA but now ships feature releases at the same pace: "
               f"{min(ro_n)}–{max(ro_n)} a year"),
        subtitle="Left: major versions on a timeline. Right: feature releases (x.y, excl. patches) per calendar year, 2023–2026 YTD",
        alt=(f"Two panels. Left: CUDA majors from 1.0 (2007) to 13.0 (2025) and ROCm majors from 1.0 (2016) to 10.0 "
             f"(2026), a {head}-year head start for CUDA. Right: feature releases per year 2023–2026 — CUDA "
             f"{', '.join(map(str, cu_n))} and ROCm {', '.join(map(str, ro_n))} — roughly equal cadence."),
        data=["software_ecosystem.csv"], chapters=["09", "15"],
        source="NVIDIA CUDA archive and PyPI; AMD ROCm release history", source_ids=sources_of(cu) + [
            s for s in sources_of(ro) if s not in sources_of(cu)],
        note="2026 = to Nov 5",
    )
    fig, (a1, a2) = c.figure_grid(1, 2, width=11.5, height=5.4, gridspec_kw={"width_ratios": [1.6, 1]})
    for y, d, ent, lab in [(1, cu, "NVIDIA", "CUDA"), (0, ro, "AMD", "ROCm")]:
        mj = d[d.notes.str.startswith("major")]
        col = entity_color(ent)
        a1.plot(mj.x, [y] * len(mj), color=col, lw=1.5, alpha=0.5)
        a1.plot(mj.x, [y] * len(mj), "o", ms=8, color=col)
        for k, (_, r) in enumerate(mj.iterrows()):
            a1.text(r.x, y + (0.13 if k % 2 == 0 else -0.13), r.value, ha="center",
                    va="bottom" if k % 2 == 0 else "top", fontsize=7.6, color=INK["title"])
    a1.set_yticks([1, 0])
    a1.set_yticklabels(["CUDA", "ROCm"], fontsize=10)
    for lab, ent in zip(a1.get_yticklabels(), ["NVIDIA", "AMD"]):
        lab.set_color(entity_color(ent))
        lab.set_fontweight("bold")
    a1.set_ylim(-0.6, 1.6)
    a1.set_xlim(2006, 2027.5)
    a1.set_xticks(range(2007, 2028, 4))
    a1.grid(axis="x", color=INK["grid"])
    a1.grid(axis="y", visible=False)
    a1.set_title("Major versions", fontsize=10, loc="left", color=INK["title"], fontweight="bold")
    w = 0.38
    xs = range(len(years))
    b1 = a2.bar([x - w / 2 for x in xs], cu_n, width=w, color=NV, label="CUDA")
    b2 = a2.bar([x + w / 2 for x in xs], ro_n, width=w, color=entity_color("AMD"), label="ROCm")
    for bars in (b1, b2):
        for b in bars:
            a2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.05, f"{int(b.get_height())}",
                    ha="center", va="bottom", fontsize=9)
    b1[-1].set_hatch("//")
    b2[-1].set_hatch("//")
    a2.set_xticks(list(xs))
    a2.set_xticklabels([str(y) if y < 2026 else "2026\nYTD" for y in years])
    a2.set_ylim(0, max(cu_n + ro_n) + 1.2)
    a2.set_ylabel("Feature releases per year")
    a2.legend(loc="upper left", fontsize=9)
    a2.set_title("Release tempo", fontsize=10, loc="left", color=INK["title"], fontweight="bold")
    fig.subplots_adjust(wspace=0.25)
    c.save(fig, [a1, a2], legend=False)


# --------------------------------------------------------------------------------------
# 6. Inference-engine release velocity (PyPI)
# --------------------------------------------------------------------------------------
ENGINES = [("vLLM", "#7A7A7A"), ("SGLang", "#B5B5B5"), ("TensorRT-LLM", NV), ("NVIDIA Dynamo", NV_DARK)]


@register
def inference_engine_release_velocity():
    st = _ts("pypi_stable_releases")
    pr = _ts("pypi_prereleases")
    years = ["2023", "2024", "2025", "2026"]

    def val(df, e, y):
        r = df[(df.entity == e) & (df.date == y)]
        return int(r.value.iloc[0]) if len(r) else None
    v25 = val(st, "vLLM", "2025")
    c = Chart(
        id="11-inference-engine-release-velocity",
        title=f"vLLM ships a stable release every ~{365 // v25} days; TensorRT-LLM mostly ships RCs",
        subtitle=("Versions first uploaded to PyPI per calendar year (solid = stable, hatched = rc/alpha/beta; "
                  "nightlies excluded; 2026 to Nov 5)"),
        alt=(f"Grouped bars of PyPI releases per year: vLLM {val(st, 'vLLM', '2023')}, {val(st, 'vLLM', '2024')}, "
             f"{v25} and {val(st, 'vLLM', '2026')} (2026 YTD) stable releases; SGLang {val(st, 'SGLang', '2024')} in "
             f"2024 and {val(st, 'SGLang', '2025')} in 2025; TensorRT-LLM {val(st, 'TensorRT-LLM', '2025')} stable plus "
             f"{val(pr, 'TensorRT-LLM', '2025')} release candidates in 2025; NVIDIA Dynamo "
             f"{val(st, 'NVIDIA Dynamo', '2025')} in 2025 and {val(st, 'NVIDIA Dynamo', '2026')} in 2026 YTD."),
        data=["software_ecosystem.csv"], chapters=["11", "09"],
        source="PyPI JSON API (vllm, sglang, tensorrt-llm, ai-dynamo)", source_ids=sources_of(st),
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    ax.set_axisbelow(True)
    w = 0.2
    for k, (e, col) in enumerate(ENGINES):
        for i, y in enumerate(years):
            s = val(st, e, y)
            p = val(pr, e, y)
            if s is None:
                continue
            x = i + (k - 1.5) * w
            ax.bar(x, s, width=w * 0.92, color=col, edgecolor=col)
            if p:
                b = ax.bar(x, p, bottom=s, width=w * 0.92, color="white", edgecolor=col, hatch="///", lw=1)[0]
                if hasattr(b, "set_hatchcolor"):
                    b.set_hatchcolor(col)
            ax.text(x, s + (p or 0) + 0.8, f"{s + (p or 0)}", ha="center", va="bottom", fontsize=7.4,
                    color=INK["title"])
    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([y if y != "2026" else "2026 YTD" for y in years])
    handles = [mpatches.Patch(color=col, label=e) for e, col in ENGINES]
    handles.append(mpatches.Patch(facecolor="white", edgecolor=INK["text"], hatch="///",
                                  label="pre-releases (rc/alpha/beta)"))
    ax.legend(handles=handles, loc="upper left", fontsize=8.6, ncol=3)
    ax.set_ylim(0, 85)
    c.save(fig, ax, ylabel="PyPI releases per year", legend=False)
