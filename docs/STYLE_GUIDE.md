# Style Guide

This guide makes 100+ pages and 250+ visuals read as **one system**. It covers voice, page
anatomy, citations, confidence tags, the color palette, chart rules, diagram rules and file
naming. Mechanics for contributors (source-ID ranges, link schemes, build commands) are in
[`AGENT_BRIEF.md`](AGENT_BRIEF.md).

---

## 1. Voice and audience

- **Reader:** a CFA-trained corporate development manager at Qualcomm (datacenter BU). Fluent in
  finance, M&A and strategy; technically literate but not a chip designer.
- **Register:** a senior sell-side or strategy analyst explaining to a sharp peer. Plain English,
  short sentences, no hype. Explain *mechanisms* ("HBM is fast because it sits millimetres from
  the GPU on a silicon interposer with a 2,048-bit-wide bus"), not just conclusions.
- **Balance:** every page gives real weight to NVIDIA's weaknesses, the strongest competitor
  argument and the bear case. Avoid unsourced superlatives ("best", "unmatched", "dominant")
  unless a number and a citation sit next to them.
- **Numbers:** always carry units (TB/s, GB, W, PFLOPS). Use `~` for approximations, "Est." for
  estimates (with the source of the estimate), and give the as-of date for anything that moves.
- **Terminology** (use consistently):

| Use | Not |
|---|---|
| GPU (the package a customer buys, e.g. "B200 GPU") and *die* (one piece of silicon) | "chip" for both |
| HBM3E, HBM4, HBM4E | HBM3e, HBM-4 |
| NVLink 5 / NVLink 6 (generation) | NVLink5, NVLinkv5 |
| NVL72 (rack with 72 GPU packages) | NVL-72 |
| GB200 NVL72, GB300 NVL72, Vera Rubin NVL144 | GB200-NVL72 |
| PFLOPS (rate), FLOPs (count of operations) | PFLOP/s, flops |
| dense FP4 / sparse FP4 — always state which | "FP4 PFLOPS" with no qualifier |
| scale-up (NVLink domain), scale-out (cluster network), scale-across (between datacenters) | intra-node / inter-node only |
| fiscal year as `FY2026` (NVIDIA's FY ends late January) | FY26, fiscal 26 |
| `$ B` written as `$46.7B`; `$ M` as `$700M` | 46.7 billion dollars |

> NVIDIA's fiscal year ends on the last Sunday of January. FY2026 ≈ calendar 2025. Always say
> "FY" for NVIDIA figures and "CY" when a calendar year could be confused.

---

## 2. Page anatomy (three reading depths)

Every content page follows this skeleton. Headings use these exact emoji so readers can scan.

```markdown
# <Page title>

<sub>Layer 02 · GPU silicon · ~15 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take
- 5–8 bullets, each a complete claim with a number and a citation [S2001]
- …

![<takeaway alt text>](/assets/charts/<chart>.svg)

## <Level 2 sections: How It Works …>
Plain-English mechanism, analogy, then a worked example with real numbers.

> [!TIP]
> **Worked example — why a 1T-parameter model doesn't fit on one GPU.** 1T params × 1 byte (FP8) = 1 TB …

<details>
<summary>🔧 Under the hood: <topic></summary>

Technical detail for the curious.

</details>

## 🎯 Corp Dev Lens
1. 3–6 questions/observations on value pools, defensibility, build/buy/partner angles.

## 📚 Sources
<!-- auto-generated -->
```

Rules:

- **Level 1 (Executive Take):** 5–8 bullets + one key visual. Readable in two minutes.
- **Level 2 (How It Works):** where the depth lives. Every Level-2 section has at least one
  **worked example with real numbers**, set in a `> [!TIP]` box titled "Worked example — …".
- **Level 3 (Under the Hood):** collapsible `<details><summary>🔧 Under the hood: …</summary>`.
  Leave a blank line after `<summary>` and before `</details>` so Markdown renders inside.
- **Callouts:** `> [!NOTE]` key insight · `> [!TIP]` worked example · `> [!IMPORTANT]` the one thing
  to remember · `> [!WARNING]` myth vs. reality, risk, or bear argument. Bull/bear pairs use
  `> [!NOTE]` titled **🐂 Bull view** and `> [!WARNING]` titled **🐻 Bear view**.
- **Glossary:** define each term on first use on a page and link it: `[HBM](glossary:hbm)`.
- **Every page ends** with `## 🎯 Corp Dev Lens` then `## 📚 Sources` (the Sources list is
  generated automatically from the citations on the page — do not hand-edit it).
- **Layer pages** answer the eight standard questions; label each answer with a small tag such as
  `**[Q4 · Source of advantage]**` so QA can find it.

---

## 3. Citations and confidence

- **Citation token:** `[S2031]` placed right after the claim. Multiple: `[S2031][S2044]`.
  The build turns tokens into links to [`sources/bibliography.md`](../sources/bibliography.md).
- **What needs a citation:** every number, date, spec, deal term, market share and roadmap item.
- **Estimates:** write "Est." and cite the estimator, e.g. `~$3.4M per rack (Est., SemiAnalysis) [S8012]`.
- **Confidence tags** on forward-looking or disputed claims — emoji first, then the claim:

| Tag | Meaning | Example |
|---|---|---|
| 🟢 Confirmed | Officially announced by the company | `🟢 Rubin Ultra NVL576 targeted for H2 2027 [S17003]` |
| 🟡 Reported | Credible press or analyst reporting | `🟡 TSMC CoWoS capacity ~X wafers/month by end-2026 [S3012]` |
| 🔴 Speculative | Inference, rumor, or this repo's own analysis | `🔴 Feynman likely adopts …` |

- **Quotes:** rare, under 15 words, in quotation marks, cited.

## 4. Comparison verdicts

Use these four emoji in comparison matrices, always with a short reason in the cell:

| Emoji | Meaning |
|---|---|
| 🟩 | Leads |
| 🟨 | Parity |
| 🟥 | Behind |
| 🟦 | Different approach (not directly comparable) |

---

## 5. Color palette (fixed; colorblind-checked)

Colors are **fixed per entity** and never re-assigned by rank. All marks sit on an explicit
**white (`#FFFFFF`) chart background**, so SVGs read the same in GitHub light and dark themes.

### Entity colors

| Entity | Hex | Notes |
|---|---|---|
| **NVIDIA** | `#5F9E00` | Deepened NVIDIA green (brand `#76B900` fails 3:1 contrast on white) |
| AMD | `#C4314B` | Crimson; tuned to separate from NVIDIA green for deuteranopes (ΔE 9.5) |
| Google (TPU) | `#2A78D6` | Blue |
| AWS (Trainium) | `#C98500` | Amber |
| Microsoft (Maia) | `#0F9FB0` | Teal |
| Meta (MTIA) | `#6250D6` | Violet |
| Broadcom | `#E0609A` | Pink |
| Huawei | `#9B3C9E` | Plum |
| Intel | `#4FA3E0` | Sky blue (sub-3:1 contrast → always direct-label) |
| Qualcomm | `#3C4FC4` | Indigo |
| Marvell | `#B0651A` | Copper |
| Startups (Cerebras, Groq, SambaNova, …) | `#7A7A7A` | Neutral gray |
| Other / industry / not attributed | `#B5B5B5` | Light gray |

**Validation (computed, not eyeballed):** the core eight in the order
NVIDIA → AMD → Google → AWS → Microsoft → Meta → Broadcom → Huawei pass all checks of the
data-viz palette validator on a white surface: lightness band, chroma floor, adjacent CVD
separation ≥ 8 ΔE (worst 9.5, NVIDIA↔AMD, deutan), normal-vision ≥ 15 ΔE (worst 16.3) and
≥ 3:1 contrast. The secondary three (Intel, Qualcomm, Marvell) pass all-pairs among themselves.

**Rules that follow from the palette:**

1. A chart shows **at most 8 colored entities**; fold the rest into "Other" (`#B5B5B5`) or use
   small multiples.
2. With **more than 4 entities**, add a secondary encoding: direct labels at line ends, distinct
   markers, or hatching. Intel and Google, or Qualcomm and Google, never rely on hue alone.
3. NVIDIA is always green and, where it is the subject, drawn last (on top) and labeled.

### Single-entity and value scales

- **NVIDIA generations** (Volta → Feynman) on one chart: single NVIDIA green; emphasize the
  current/next generation with full color and render past generations in a lighter tint
  (`#A9CC73`), future/roadmap bars with **diagonal hatching** and a 🟢/🟡/🔴 label.
- **Sequential (magnitude, heatmaps):** one hue, light→dark blue ramp
  `#CDE2FB → #86B6EF → #3987E5 → #256ABF → #104281`.
- **Diverging:** blue `#256ABF` ↔ gray `#F0EFEC` ↔ red `#C4314B`.
- **Capability heatmaps** (verdict scale): Behind `#F4C7C3` · Parity `#FBE6A2` · Leads `#B7E1A1` ·
  Different approach `#C6DAF7`, with the emoji printed in each cell so color is never alone.
- **Estimate vs. reported:** estimates are hatched (`//`) or drawn with a lighter alpha and
  labeled "Est.".

### Chart chrome

| Role | Value |
|---|---|
| Background | `#FFFFFF` |
| Title ink | `#0B0B0B`, bold, 15 pt, **states the takeaway** |
| Subtitle ink | `#52514E`, 11 pt (what is plotted, units, scope) |
| Axis labels / ticks | `#52514E`, 10 pt |
| Gridlines | `#E1E0D9`, solid hairline, y-axis only by default |
| Baseline | `#C3C2B7` |
| Footer (source + as-of) | `#898781`, 8.5 pt: `Source: data from <X> [S###]; chart by repo · As of YYYY-MM-DD` |
| Font | DejaVu Sans (rendered to paths in SVG for fidelity) |

---

## 6. Chart rules (enforced by `scripts/charts/style.py`)

1. **Title states the takeaway**, not the topic: "NVLink bandwidth per GPU grew 18× in 8 years
   while PCIe grew 4×", not "Bandwidth over time".
2. **Subtitle** names the metric, units and scope ("Bidirectional GB/s per GPU, 2016–2026").
3. **Axes labeled with units.** No unlabeled axes.
4. **Footer** always carries the source line and the **as-of date**.
5. **Log scale only when labeled:** the axis label ends in "(log scale)" and the helper stamps a
   `LOG SCALE` badge.
6. **No 3D, no dual axes**, no pie charts for close values. Use indexing (=100 at t0), small
   multiples or two charts instead of a second y-axis.
7. **No truncated axes** unless a visible break marker is drawn (`style.axis_break()`).
8. **Thin marks:** 2 px lines, ≥ 8 px markers, bars with small gaps; legend present for ≥ 2 series
   and direct labels on ≤ 4 series; no number on every point.
9. **Estimates and roadmap items** visibly distinct (hatching / lighter alpha) and labeled.
10. **Static + interactive:** each chart writes `assets/charts/<id>.svg` (GitHub) and, where useful,
    `assets/interactive/<id>.html` (Plotly, loads plotly.js from CDN).
11. **Alt text** is registered with the chart and reused verbatim in the Markdown embed; it states
    the takeaway and the key numbers (≥ 40 characters).
12. **Reproducible:** charts are generated only by `make charts` from `data/*.csv`; never hand-edit
    an SVG in `assets/charts/`.

## 7. Diagram rules

- **Mermaid** for anything GitHub can lay out well: flowcharts, sequences, timelines, gantts,
  quadrants, mindmaps, block-beta, sankey-beta, xychart-beta. Keep node labels short; put detail in
  the prose. Every Mermaid block is render-checked by `make validate`.
- **Mermaid colors:** do not hard-code a theme (GitHub switches light/dark). Where an entity color
  matters, use `classDef nvidia fill:#5F9E00,color:#ffffff,stroke:#3F6B00` (and the palette above
  for competitors); always keep white text on saturated fills.
- **D2 / Graphviz** for complex topologies (rack anatomy, multi-tier fabrics, software stacks).
  Sources in `diagrams/src/<id>.d2|.dot`, rendered SVG in `assets/diagrams/<id>.svg` by
  `make diagrams`. Rendered diagrams must have an explicit white background.
- **Anatomy diagrams** (GPU package, compute tray, NVL72-class rack, switch tray) are original
  drawings from public specifications; never trace or copy vendor imagery.
- **Tables** are visuals too: spec tables, comparison matrices with 🟩🟨🟥🟦 verdicts, "then vs. now".

## 8. File and ID naming

| Thing | Convention | Example |
|---|---|---|
| Chart id / file | `<chapter>-<slug>` in kebab case | `02-flops-by-precision-log.svg` |
| Diagram id / file | `<chapter>-<slug>` | `08-nvl72-rack-anatomy.svg` |
| Data file | `data/<snake_case>.csv`, first columns are keys, last columns `confidence,source_id,notes` | `data/gpu_product_specs.csv` |
| Source id | `S<number>`; ranges by chapter (see AGENT_BRIEF) | `S2031` |
| Glossary slug | lower kebab case | `hbm`, `kv-cache`, `nvlink-c2c` |

`confidence` in CSVs is one of `confirmed`, `reported`, `estimate`, `speculative`.
