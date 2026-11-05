"""Roadmap charts (chapter 17 and layer roadmap pages) built from data/roadmap.csv and
data/gpu_architecture_cadence.csv. Owner: Phase-1 agent A5."""
from __future__ import annotations

import re
from datetime import date

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from matplotlib.lines import Line2D

from style import (Chart, GEN_PAST, INK, NV, NV_DARK, entity_color, load, register,
                   sources_of)

# --------------------------------------------------------------------------------------
# helpers (module-local)
# --------------------------------------------------------------------------------------
STATUS_STYLE = {
    "shipping": dict(fc=NV, ec=NV_DARK, hatch=None, label="Shipping"),
    "announced": dict(fc=GEN_PAST, ec=NV_DARK, hatch=None, label="Announced (not yet in volume)"),
    "roadmap": dict(fc=NV, ec=NV_DARK, hatch="///", label="Roadmap (future)"),
    "delayed": dict(fc="#F4C7C3", ec="#C4314B", hatch="xx", label="Delayed / reported slip"),
    "cancelled": dict(fc="#E1E0D9", ec="#898781", hatch=None, label="Cancelled"),
}
CONF_DOT = {"confirmed": "#3F8F3F", "reported": "#D9A400", "estimate": "#898781",
            "speculative": "#C4314B"}
CONF_TXT = {"confirmed": "Confirmed", "reported": "Reported", "estimate": "Estimate",
            "speculative": "Speculative"}


def _yf(d: date) -> float:
    """date -> fractional year."""
    start = date(d.year, 1, 1)
    return d.year + (d - start).days / 365.25


def when(s, end: bool = False) -> float | None:
    """Parse YYYY / YYYY-Qn / YYYY-MM / YYYY-MM-DD into a fractional year (start or end)."""
    if s is None or (isinstance(s, float) and s != s):
        return None
    s = str(s).strip()
    if not s:
        return None
    m = re.fullmatch(r"(\d{4})", s)
    if m:
        y = int(m.group(1))
        return y + (0.999 if end else 0.0)
    m = re.fullmatch(r"(\d{4})-Q([1-4])", s)
    if m:
        y, q = int(m.group(1)), int(m.group(2))
        return y + (q if end else q - 1) * 0.25 - (0.001 if end else 0)
    m = re.fullmatch(r"(\d{4})-(\d{2})", s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        return y + (mo if end else mo - 1) / 12 - (0.001 if end else 0)
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return _yf(date(int(m.group(1)), int(m.group(2)), int(m.group(3))))
    return None


def _fig_axes(width, height, rect):
    """Figure with a free-standing axes (not moved by Chart.save's subplots_adjust), so long y labels fit."""
    fig = plt.figure(figsize=(width, height))
    ax = fig.add_axes(rect)
    return fig, ax


def _style_bar(patch, status: str) -> None:
    st = STATUS_STYLE.get(status, STATUS_STYLE["announced"])
    patch.set_facecolor(st["fc"])
    patch.set_edgecolor(st["ec"])
    patch.set_linewidth(0.8)
    if st["hatch"]:
        patch.set_hatch(st["hatch"])
        if hasattr(patch, "set_hatchcolor"):
            patch.set_hatchcolor("#FFFFFF" if status == "roadmap" else st["ec"])
        if status == "roadmap":
            patch.set_alpha(0.8)


def _year_axis(ax, x0=2024, x1=2029):
    ax.set_xlim(x0, x1)
    ax.set_xticks(range(x0, x1 + 1))
    ax.grid(axis="x", color=INK["grid"], linewidth=0.7)
    ax.grid(axis="y", visible=False)
    ax.axvline(when("2026-11-05"), color=INK["text"], lw=1.0, ls="--", zorder=1)


def _find(df, vendor, product_prefix):
    sub = df[(df.vendor == vendor) & (df["product"].str.startswith(product_prefix))]
    if sub.empty:
        raise KeyError(f"{vendor} / {product_prefix} not in roadmap.csv")
    return sub.iloc[0]


SHIFT_RE = re.compile(r"(SLIP|PULL-IN) from (\d{4}(?:-Q[1-4]|-\d{2})?) to (\d{4}(?:-Q[1-4]|-\d{2})?)")


# --------------------------------------------------------------------------------------
# 1. NVIDIA gantt
# --------------------------------------------------------------------------------------
GANTT_ROWS = [  # (row label, sequential generations?, [(product prefix, short label)])
    ("GPU", True, [("Blackwell B200", "B200"), ("Blackwell Ultra", "B300"), ("Rubin GPU", "Rubin"),
                   ("Rubin Ultra", "Rubin Ultra"), ("Feynman GPU", "Feynman")]),
    ("Decode LPU", True, [("Groq 3 LPU", "Groq 3 LPU"), ("Groq LP35", "LP35"), ("LP40 LPU", "LP40")]),
    ("Prefill GPU", True, [("Rubin CPX", "Rubin CPX")]),
    ("CPU", True, [("Vera CPU", "Vera"), ("Rosa CPU", "Rosa")]),
    ("Scale-up (NVLink)", True, [("NVLink 5", "NVLink 5"), ("NVLink 6", "NVLink 6"), ("NVLink 7", "NVLink 7"),
                                 ("Feynman-era NVLink", "Cu + CPO")]),
    ("SuperNIC / DPU", True, [("ConnectX-8", "CX-8"), ("ConnectX-9", "CX-9 + BF-4"),
                              ("ConnectX-10", "CX-10 + BF-5")]),
    ("Ethernet switches", True, [("Spectrum-6", "Spectrum-6"), ("Next-gen Spectrum", "Next gen")]),
    ("Co-packaged optics", False, [("Quantum-X Photonics", "Quantum-X Photonics (IB)"),
                                   ("Spectrum-X Photonics", "Spectrum-X Photonics")]),
    ("NVL rack", True, [("GB200 NVL72", "GB200 NVL72"), ("GB300 NVL72", "GB300 NVL72"),
                        ("Vera Rubin NVL72", "VR NVL72"), ("Kyber NVL144", "Kyber NVL144"),
                        ("Feynman Kyber", "Feynman NVL1152")]),
    ("Inference racks", False, [("Groq 3 LPX", "Groq 3 LPX"), ("Vera Rubin NVL144 CPX", "VR CPX rack")]),
    ("Power", True, [("800 V DC", "800 V DC")]),
]
SOFTWARE_EVENTS = [("Dynamo (open-source", "Dynamo"), ("Spectrum-XGS", "Spectrum-XGS"),
                   ("CUDA 13.0", "CUDA 13"), ("Dynamo 1.0", "Dynamo 1.0")]


def _bar_extent(rec, starts, j, seq, x_end):
    x0 = starts[j]
    nxt = [s for s in starts[j + 1:] if s is not None and s > x0] if seq else []
    if nxt:
        return x0, min(nxt)
    if rec.status == "delayed" or rec.status == "cancelled":
        return x0, max(when(rec.window_end, end=True) or x0 + 0.5, x0 + 0.5)
    return x0, x_end


@register
def roadmap_gantt_nvidia():
    df = load("roadmap.csv")
    nv = df[df.vendor == "NVIDIA"].copy()
    used, rows, sw = [], [], []
    for label, seq, items in GANTT_ROWS:
        recs = []
        for prefix, short in items:
            rec = _find(nv, "NVIDIA", prefix)
            used.append(rec.name)
            recs.append((rec, short))
        rows.append((label, seq, recs))
    for prefix, short in SOFTWARE_EVENTS:
        rec = _find(nv, "NVIDIA", prefix)
        used.append(rec.name)
        sw.append((rec, short))
    d = nv.loc[used]
    n_future = int((d.status.isin(["roadmap", "announced"])).sum())
    n_delay = int((d.status == "delayed").sum())
    c = Chart(
        id="17-roadmap-gantt-nvidia",
        title=(f"NVIDIA's roadmap refreshes every layer about yearly to 2028; {n_delay} items carry "
               f"reported slips"),
        subtitle=("NVIDIA availability windows by product line, 2024–2028 (bar runs to the next generation; "
                  "dot = confidence)"),
        alt=(f"Gantt chart of NVIDIA data-center products 2024–2028 across {len(rows) + 1} product lines: GPUs "
             f"move from Blackwell (2024) to Blackwell Ultra (2025), Rubin (shipping since Aug 2026), Rubin "
             f"Ultra (2H 2027) and Feynman (2028), with matching NVLink, NIC, CPU and rack generations. "
             f"{n_future} items are announced or roadmap; {n_delay} (Rubin CPX, its CPX rack and the Kyber "
             f"NVL144 rack) carry reported slips shown against their original windows."),
        data=["roadmap.csv"], chapters=["17", "02", "08"],
        source="NVIDIA keynotes, filings and trade press", source_ids=sources_of(d),
        note="Dotted red box = originally announced window",
    )
    fig, ax = _fig_axes(11.5, 7.6, [0.135, 0.15, 0.845, 0.70])
    x_end = 2029.0
    nrow = len(rows) + 1
    for i, (label, seq, recs) in enumerate(rows):
        y = nrow - 1 - i
        starts = [when(r.window_start) for r, _ in recs]
        spans = [_bar_extent(r, starts, j, seq, x_end) for j, (r, _) in enumerate(recs)]
        lanes = [0] * len(spans)
        for k in range(len(spans)):
            for m in range(k):
                if spans[k][0] < spans[m][1] - 1e-6 and spans[m][0] < spans[k][1] - 1e-6:
                    lanes[m], lanes[k] = 1, -1
        for (rec, short), (x0, x1), lane in zip(recs, spans, lanes):
            h = 0.62 if lane == 0 else 0.3
            yc = y + 0.16 * lane
            bar = ax.barh(yc, x1 - x0, left=x0, height=h, zorder=3)[0]
            _style_bar(bar, rec.status)
            txt_col = "#FFFFFF" if rec.status == "shipping" else INK["title"]
            fs = 7.5 if lane == 0 else 6.6
            ax.text(x0 + 0.05, yc, short, va="center", ha="left", fontsize=fs, color=txt_col, zorder=5,
                    clip_on=True)
            ax.plot(x0, yc + h / 2, "o", ms=4.6, color=CONF_DOT.get(rec.confidence, "#898781"),
                    mec="white", mew=0.7, zorder=6, clip_on=False)
            mt = SHIFT_RE.search(str(rec.notes))
            if mt:
                o0, o1 = when(mt.group(2)), when(mt.group(2), end=True)
                ax.add_patch(mpatches.Rectangle((o0, yc - h / 2), max(o1 - o0, 0.25), h, fill=False,
                                                ls=":", lw=1.3, ec="#C4314B", zorder=4))
                ax.annotate("", xy=(x0, yc), xytext=(o0 + max(o1 - o0, 0.25), yc),
                            arrowprops=dict(arrowstyle="->", color="#C4314B", lw=1.0), zorder=6)
    for k, (rec, short) in enumerate(sw):
        x = when(rec.window_start)
        ax.plot(x, 0, marker="D", ms=7, color=NV, mec=NV_DARK, zorder=5)
        ax.text(x, 0.28 if k % 2 == 0 else -0.5, short, ha="center", va="bottom", fontsize=7.2,
                color=INK["title"])
    labels = [r for r, _, _ in rows] + ["Software & features"]
    ax.set_yticks(range(nrow))
    ax.set_yticklabels(list(reversed(labels)), fontsize=8.8)
    ax.set_ylim(-0.75, nrow - 0.35)
    _year_axis(ax)
    ax.text(when("2026-11-05") + 0.03, nrow - 0.5, "today", fontsize=7.5, color=INK["text"])
    handles = [mpatches.Patch(facecolor=v["fc"], edgecolor=v["ec"], hatch=v["hatch"], label=v["label"])
               for k, v in STATUS_STYLE.items() if k != "cancelled"]
    handles += [Line2D([], [], marker="o", ls="", color=CONF_DOT[k], label=CONF_TXT[k])
                for k in ("confirmed", "reported")]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.45, -0.06), ncol=6, fontsize=7.8,
              frameon=False, handlelength=1.6, columnspacing=1.1)
    c.save(fig, ax, legend=False)
    _gantt_plotly(c, rows, x_end)


def _gantt_plotly(c, rows, x_end):
    """Interactive twin: same bars, hover shows specs, confidence and notes."""
    import plotly.graph_objects as go
    fig = go.Figure()
    seen = set()
    for label, seq, recs in rows:
        starts = [when(r.window_start) for r, _ in recs]
        for j, (rec, short) in enumerate(recs):
            x0, x1 = _bar_extent(rec, starts, j, seq, x_end)
            st = STATUS_STYLE.get(rec.status, STATUS_STYLE["announced"])
            hover = (f"<b>{rec['product']}</b><br>Status: {rec.status} · Confidence: {rec.confidence}<br>"
                     f"Window: {rec.window_start} – {rec.window_end}<br>{rec.key_specs}<br>"
                     f"<i>{str(rec.notes)[:300]}</i><br>Sources: {rec.source_id}")
            fig.add_trace(go.Bar(
                y=[label], x=[x1 - x0], base=[x0], orientation="h", name=st["label"],
                legendgroup=rec.status, showlegend=rec.status not in seen,
                marker=dict(color=st["fc"], line=dict(color=st["ec"], width=1),
                            pattern=dict(shape="/" if rec.status == "roadmap" else
                                         ("x" if rec.status == "delayed" else ""))),
                text=short, textposition="inside", insidetextanchor="start",
                hovertext=hover, hoverinfo="text"))
            seen.add(rec.status)
    fig.update_layout(barmode="overlay", xaxis=dict(range=[2024, 2029], dtick=1, title="Year"),
                      yaxis=dict(autorange="reversed"), legend=dict(orientation="h", y=-0.15))
    fig.add_vline(x=when("2026-11-05"), line_dash="dash", line_color=INK["text"])
    c.save_plotly(fig, height=640)


# --------------------------------------------------------------------------------------
# 2. Small multiples by layer group
# --------------------------------------------------------------------------------------
GROUPS = [
    ("Silicon (GPU / ASIC / LPU)", ["02"]),
    ("Memory & packaging", ["03"]),
    ("CPU", ["04"]),
    ("Scale-up interconnect", ["05"]),
    ("Scale-out, NIC & DPU", ["06", "07"]),
    ("Systems & racks", ["08"]),
    ("Software & cloud", ["09", "10", "11", "12"]),
]
STATUS_MARK = {"shipping": ("o", True), "announced": ("D", True), "roadmap": ("o", False),
               "delayed": ("X", True), "cancelled": ("x", True)}
VENDOR_KEY = {
    "NVIDIA": "NVIDIA", "NVIDIA / Intel": "NVIDIA", "AWS / NVIDIA": "AWS", "AMD": "AMD", "Google": "Google",
    "Google Cloud": "Google", "Oracle / Google": "Google", "Google / Red Hat / community": "Google",
    "AWS": "AWS", "Microsoft": "Microsoft", "Meta": "Meta", "Huawei": "Huawei", "Intel": "Intel",
    "Qualcomm": "Qualcomm", "Broadcom": "Broadcom", "OpenAI / Broadcom": "Broadcom",
    "UALink Consortium": "Standards", "OCP (ESUN workstream)": "Standards",
    "Ultra Ethernet Consortium": "Standards",
}


@register
def roadmap_by_layer_small_multiples():
    df = load("roadmap.csv")
    df = df[df.layer.astype(str).str.zfill(2) != "13"].copy()
    df["layer"] = df.layer.astype(str).str.zfill(2)
    df["vkey"] = df.vendor.map(VENDOR_KEY).fillna("Other")
    df["x"] = df.window_start.map(when)
    df = df[df.x.notna()]
    per_group = {g: df[df.layer.isin(ls)] for g, ls in GROUPS}
    nv_future = df[(df.vkey == "NVIDIA") & (df.x >= 2027)]
    comp_future = df[(df.vkey != "NVIDIA") & (df.x >= 2027)]
    hw = [g for g, ls in GROUPS if not set(ls) & {"09", "10", "11", "12"}]
    hw_groups = sum(1 for g in hw if ((per_group[g].vkey == "NVIDIA") & (per_group[g].x >= 2027)).any())
    chip_share = 100 * comp_future.layer.isin(["02", "08"]).mean()
    c = Chart(
        id="17-roadmap-by-layer-small-multiples",
        title=(f"NVIDIA has 2027–28 items in all {hw_groups} hardware layers; {chip_share:.0f}% of rivals' "
               f"are chips or racks"),
        subtitle="Roadmap items by layer group and vendor, plotted at the start of the availability window, 2024–2028",
        alt=(f"Seven small-multiple timelines (silicon, memory, CPU, scale-up, scale-out/NIC, systems, software) "
             f"show NVIDIA with {len(nv_future)} items dated 2027 or later spread across all {hw_groups} hardware "
             f"layers, while AMD, Google, AWS, Microsoft, Meta, Huawei, Intel, Qualcomm, Broadcom and the "
             f"standards bodies have {len(comp_future)} such items, {chip_share:.0f}% of them accelerators or racks. "
             f"Software and cloud items are mostly near-term (dated 2025–2026)."),
        data=["roadmap.csv"], chapters=["17"],
        source="Company announcements and trade press", source_ids=sources_of(df),
    )
    fig, axes = c.figure_grid(4, 2, width=12, height=11.5)
    flat = list(axes.ravel())
    order = ["NVIDIA", "AMD", "Google", "AWS", "Microsoft", "Meta", "Huawei", "Intel", "Qualcomm",
             "Broadcom", "Standards"]
    for ax, (g, _) in zip(flat, GROUPS):
        sub = per_group[g]
        vendors = [v for v in order if v in set(sub.vkey)]
        ypos = {v: len(vendors) - 1 - i for i, v in enumerate(vendors)}
        seen: dict = {}
        for _, r in sub.sort_values("x").iterrows():
            mk, filled = STATUS_MARK.get(r.status, ("o", True))
            col = entity_color(r.vkey) if r.vkey not in ("Standards", "Other") else "#7A7A7A"
            key = (r.vkey, round(r.x * 8))
            k = seen.get(key, 0)
            seen[key] = k + 1
            y = ypos[r.vkey] + [0, 0.22, -0.22, 0.11, -0.11][k % 5]
            ax.plot(r.x, y, marker=mk, ms=8 if mk != "X" else 9, ls="",
                    mfc=col if filled else "white", mec=col, mew=1.6, zorder=4)
        ax.set_yticks(range(len(vendors)))
        ax.set_yticklabels(list(reversed(vendors)), fontsize=8.5)
        ax.set_ylim(-0.7, len(vendors) - 0.3)
        _year_axis(ax)
        ax.set_title(f"{g}  ·  {len(sub)} items", fontsize=10, color=INK["title"], loc="left",
                     fontweight="bold")
        ax.tick_params(axis="x", labelsize=8.5)
    # legend panel
    lax = flat[-1]
    lax.axis("off")
    h = [Line2D([], [], marker="o", ls="", mfc=NV, mec=NV, ms=8, label="Shipping"),
         Line2D([], [], marker="D", ls="", mfc=NV, mec=NV, ms=7, label="Announced"),
         Line2D([], [], marker="o", ls="", mfc="white", mec=NV, mew=1.6, ms=8, label="Roadmap"),
         Line2D([], [], marker="X", ls="", mfc=NV, mec=NV, ms=9, label="Delayed (reported)"),
         Line2D([], [], marker="x", ls="", mfc=NV, mec=NV, ms=8, label="Cancelled"),
         Line2D([], [], color=INK["text"], ls="--", label="Today (2026-11-05)")]
    lax.legend(handles=h, loc="center left", fontsize=9.5, frameon=False, title="Marker = status; colour = vendor",
               title_fontsize=9.5)
    fig.subplots_adjust(hspace=0.55, wspace=0.18)
    c.save(fig, flat, legend=False, top=0.89, bottom=0.06)


# --------------------------------------------------------------------------------------
# 3. NVIDIA release cadence
# --------------------------------------------------------------------------------------
@register
def nvidia_release_cadence():
    df = load("gpu_architecture_cadence.csv")
    df = df[df.vendor == "NVIDIA"].copy()
    df["x"] = df.first_availability.map(when)
    df = df.sort_values("x").reset_index(drop=True)
    gaps = []
    for i in range(1, len(df)):
        prev, cur = df.iloc[i - 1], df.iloc[i]
        months = round((cur.x - prev.x) * 12)
        gaps.append(dict(label=f"{prev.architecture} →\n{cur.architecture}", months=months,
                         future=cur.status == "roadmap", cur=cur.architecture))
    early = [g["months"] for g in gaps[:3]]
    recent = [g["months"] for g in gaps if g["cur"] in ("Blackwell Ultra", "Rubin")]
    e_avg, r_avg = sum(early) / len(early), sum(recent) / len(recent)
    c = Chart(
        id="17-nvidia-release-cadence",
        title=(f"NVIDIA's GPU cadence sped up from ~{int(e_avg + 0.5)} months per generation to "
               f"~{int(r_avg + 0.5)} (annual)"),
        subtitle="Months between first volume availability of successive NVIDIA data-center GPU architectures, Volta → Feynman",
        alt=(f"Bar chart of months between NVIDIA GPU generations: Volta→Ampere, Ampere→Hopper and "
             f"Hopper→Blackwell averaged about {int(e_avg + 0.5)} months; Blackwell→Blackwell Ultra and Blackwell "
             f"Ultra→Rubin averaged about {int(r_avg + 0.5)} months; planned Rubin Ultra (2H 2027) and Feynman (2028) "
             f"keep a ~12-month cadence, though the Kyber rack is reported to slip to 2028."),
        data=["gpu_architecture_cadence.csv"], chapters=["17", "02", "16"],
        source="NVIDIA keynotes and launch coverage", source_ids=sources_of(df),
        note="Hatched = planned (roadmap)",
    )
    fig, ax = c.figure(width=10.5, height=5.6)
    xs = range(len(gaps))
    colors = [GEN_PAST if not g["future"] and g["cur"] not in ("Rubin",) else NV for g in gaps]
    bars = ax.bar(xs, [g["months"] for g in gaps], color=colors, width=0.62, edgecolor=NV_DARK, linewidth=0.6)
    for b, g in zip(bars, gaps):
        if g["future"]:
            b.set_hatch("///")
            b.set_alpha(0.75)
            b.set_facecolor(NV)
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.6, f"{g['months']} mo", ha="center",
                va="bottom", fontsize=9, color=INK["title"])
    ax.set_xticks(list(xs))
    ax.set_xticklabels([g["label"] for g in gaps], fontsize=8.6)
    ax.axhline(12, color=INK["muted"], ls=":", lw=1)
    ax.text(-0.45, 12.6, "12 months", fontsize=8, color=INK["muted"], ha="left")
    ax.set_ylim(0, max(g["months"] for g in gaps) * 1.18)
    c.save(fig, ax, ylabel="Months since previous generation", legend=False)


# --------------------------------------------------------------------------------------
# 4. Competitor flagship alignment
# --------------------------------------------------------------------------------------
FLAGSHIPS = {
    "NVIDIA": ["Blackwell B200", "Blackwell Ultra", "Rubin GPU", "Rubin Ultra", "Feynman GPU"],
    "AMD": ["Instinct MI325X", "Instinct MI350X", "Instinct MI455X", "Instinct MI500", "Instinct MI600"],
    "Google": ["TPU v6e", "TPU v7", "TPU 8t"],
    "AWS": ["Trainium2", "Trainium3", "Trainium4"],
}
SHORT = {"Blackwell B200": "B200", "Blackwell Ultra": "B300", "Rubin GPU": "Rubin", "Rubin Ultra": "Rubin Ultra",
         "Feynman GPU": "Feynman", "Instinct MI325X": "MI325X", "Instinct MI350X": "MI355X",
         "Instinct MI455X": "MI455X", "Instinct MI500": "MI500", "Instinct MI600": "MI600",
         "TPU v6e": "Trillium", "TPU v7": "Ironwood", "TPU 8t": "TPU 8t/8i", "Trainium2": "Trn2",
         "Trainium3": "Trn3", "Trainium4": "Trn4 (est.)"}


def _short(product):
    for k, v in SHORT.items():
        if product.startswith(k):
            return v
    return product


def _quarter(x):
    return int(x), int((x - int(x)) * 4) + 1


@register
def competitor_roadmap_alignment():
    df = load("roadmap.csv")
    picked = {}
    for v, prods in FLAGSHIPS.items():
        picked[v] = [_find(df, v, p) for p in prods]
    allrows = df.loc[[r.name for rs in picked.values() for r in rs]]
    same_q = 0
    for a, b in zip(picked["NVIDIA"][:3], picked["AMD"][:3]):
        if _quarter(when(a.window_start)) == _quarter(when(b.window_start)):
            same_q += 1
    c = Chart(
        id="17-competitor-roadmap-alignment",
        title=f"NVIDIA and AMD launched flagships in the same quarter {same_q} years running",
        subtitle="Start of availability window for each vendor's flagship AI accelerator; both publish annual roadmaps to 2028",
        alt=(f"Timeline of flagship accelerators: NVIDIA B200 (Q4 2024), B300 (Q3 2025), Rubin (Q3 2026), Rubin "
             f"Ultra (2H 2027), Feynman (2028); AMD MI325X, MI355X and MI455X landed in the same quarters "
             f"({same_q} of 3 years) with MI500 (2027) and MI600 (2028) planned; Google Trillium, Ironwood and "
             f"TPU 8t/8i arrive each December–Q4; AWS Trn2 and Trn3 each December with Trn4 estimated for 2027."),
        data=["roadmap.csv"], chapters=["17", "15"],
        source="Company announcements", source_ids=sources_of(allrows),
        note="Hollow = roadmap · pale = not yet GA",
    )
    fig, ax = _fig_axes(11, 5.4, [0.09, 0.13, 0.88, 0.70])
    vendors = list(FLAGSHIPS)
    for i, v in enumerate(vendors):
        y = len(vendors) - 1 - i
        col = entity_color(v)
        xs = [when(r.window_start) for r in picked[v]]
        ax.plot(xs, [y] * len(xs), color=col, lw=1.6, alpha=0.5, zorder=2)
        for k, (r, x) in enumerate(zip(picked[v], xs)):
            future = r.status in ("roadmap",)
            face = "white" if future else (to_rgba(col, 0.35) if r.status == "announced" else col)
            ax.plot(x, y, "o", ms=11, mfc=face, mec=col, mew=2, zorder=4)
            off = 0.22 if k % 2 == 0 else -0.36
            ax.text(x, y + off, _short(r["product"]),
                    ha="center", va="bottom", fontsize=8.4, color=INK["title"], fontweight="bold" if v == "NVIDIA" else None)
    ax.set_yticks(range(len(vendors)))
    ax.set_yticklabels(list(reversed(vendors)), fontsize=10)
    ax.set_ylim(-0.7, len(vendors) - 0.3)
    _year_axis(ax, 2024, 2029)
    for lab in ax.get_yticklabels():
        lab.set_color(entity_color(lab.get_text()))
        lab.set_fontweight("bold")
    c.save(fig, ax, legend=False)


# --------------------------------------------------------------------------------------
# 5. Slips and pull-ins
# --------------------------------------------------------------------------------------
@register
def roadmap_slips_and_pull_ins():
    df = load("roadmap.csv")
    rows = []
    for _, r in df.iterrows():
        m = SHIFT_RE.search(str(r.notes))
        if not m:
            continue
        kind, old, new = m.group(1), when(m.group(2)), when(m.group(3))
        rows.append(dict(rec=r, kind=kind, old=old, new=new, months=round((new - old) * 12)))
    rows.sort(key=lambda d: d["months"])
    sub = df.loc[[d["rec"].name for d in rows]]
    biggest = max(rows, key=lambda d: d["months"])
    pulls = [d for d in rows if d["kind"] == "PULL-IN"]
    slips = [d for d in rows if d["kind"] == "SLIP"]
    nv_slips = [d for d in slips if d["rec"].vendor == "NVIDIA"]
    pull_txt = (f"; Huawei pulled Ascend 960 in by {abs(pulls[0]['months'])} months" if pulls else "")
    c = Chart(
        id="17-roadmap-slips-and-pull-ins",
        title=(f"{len(nv_slips)} NVIDIA roadmap items slipped, led by Kyber's reported "
               f"{biggest['months']}-month delay"),
        subtitle="Originally announced (hollow) vs current official or reported (filled) start of availability window",
        alt=("Dumbbell chart of schedule changes (Huawei's is a pull-in): " + ", ".join(
            "{} {:+d} months".format(d["rec"]["product"].split(" (")[0], d["months"]) for d in rows) + ". "
             "The Kyber NVL144 slip is SemiAnalysis-reported and disputed by NVIDIA; the Rubin CPX return is an analyst claim."),
        data=["roadmap.csv"], chapters=["17", "18"],
        source="Company statements, SemiAnalysis, TrendForce, trade press", source_ids=sources_of(sub),
    )
    fig, ax = _fig_axes(11, 5.2, [0.33, 0.13, 0.64, 0.70])
    for i, d in enumerate(rows):
        r = d["rec"]
        col = entity_color(r.vendor)
        ax.annotate("", xy=(d["new"], i), xytext=(d["old"], i),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=2, shrinkA=6, shrinkB=6), zorder=3)
        ax.plot(d["old"], i, "o", ms=10, mfc="white", mec=col, mew=2, zorder=4)
        ax.plot(d["new"], i, "o", ms=10, mfc=col, mec=col, zorder=4)
        ax.text(max(d["old"], d["new"]) + 0.08, i, f"{d['months']:+d} mo", va="center", fontsize=9,
                color=INK["title"], fontweight="bold")
    labels = ["{}: {} ({})".format(d["rec"].vendor, d["rec"]["product"].split(" (")[0], d["rec"].confidence)
              for d in rows]
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    _year_axis(ax, 2025, 2029)
    c.save(fig, ax, legend=False)
