# Page templates

Copy the skeleton for your page type. Headings marked *(fixed)* must appear verbatim so readers and
validators can find them. Everything in `<…>` is yours to fill. See [`STYLE_GUIDE.md`](STYLE_GUIDE.md)
for voice and visuals and [`AGENT_BRIEF.md`](AGENT_BRIEF.md) for citations, links and charts.

---

## A. Layer `index.md`

````markdown
# Layer NN — <Layer name>

<sub>Layer NN of 12 · <one-line scope> · ~<N> min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take            ← (fixed)
- <5–8 bullets: each a complete claim with a number and a citation [S…]>
- <one bullet must state NVIDIA's biggest weakness / the strongest challenger argument in this layer>

![<alt from CATALOG.md>](/assets/charts/<key-chart>.svg)

## Where this layer sits in the stack
```mermaid
flowchart TB
  … highlight this layer with classDef nvidia fill:#5F9E00,color:#ffffff,stroke:#3F6B00 …
```

## Layer map
```mermaid
mindmap
  root((<Layer>))
    …
```

## The eight questions at a glance
| # | Question | Short answer | Where answered |
|---|---|---|---|
| Q1 | What job does this layer do, and what breaks if it is weak? | … | [link](<page>.md#…) |
| … Q2–Q8 … |

## Pages in this layer
| Page | What you will learn |
|---|---|
| [<sub-page>](<sub-page>.md) | … |
| [Competition](competition.md) | … |
| [History and how NVIDIA built it](history-and-how-built.md) | … |
| [Roadmap](roadmap.md) | … |
| [Value chain and corp dev angles](value-chain-and-corp-dev.md) | … |

## 🎯 Corp Dev Lens                 ← (fixed)
1. <3–6 numbered questions/observations: value pools, defensibility, build/buy/partner>

## 📚 Sources                       ← (fixed, leave empty; generated)
````

## B. Layer sub-page (subtopic)

````markdown
# <Subtopic title>

<sub>Layer NN · <Layer name> · ~<N> min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take
- <5–8 bullets with numbers + citations>

![<alt>](/assets/charts/<chart>.svg)

## <Level-2 section 1: the mechanism, in plain English>
<analogy → mechanism → why it matters commercially>

> [!TIP]
> **Worked example — <what>.** <real numbers, step by step, ending in a business-relevant conclusion>

**[Q2 · Metrics that matter]** <explicit answer where relevant>

<details>
<summary>🔧 Under the hood: <topic></summary>

<deeper technical detail>

</details>

## <Level-2 section 2 …>

> [!WARNING]
> **Myth vs. reality:** <a common misconception and the correction>

## 🎯 Corp Dev Lens
1. …

## 📚 Sources
````

## C. Layer `competition.md`

Required elements: comparison matrix with 🟩🟨🟥🟦 verdicts and reasons; capability heatmap
(chart `15-layer-competitor-heatmap` or a layer-specific one); one subsection per serious challenger
(what they have, their best argument, how much the gap has closed, with numbers); a `> [!NOTE]` 🐂 Bull
view and `> [!WARNING]` 🐻 Bear view pair; **[Q5 · Strongest challenger]** answered explicitly;
a quadrantChart where positioning helps.

## D. Layer `history-and-how-built.md`

Required: a Mermaid `timeline`; "key decisions and deals" table (date · decision · why it mattered ·
source); **[Q4 · Source of advantage]** and **[Q6 · Replication cost]** answered with an estimate of
time, dollars and talent and the reasoning; a "Counterfactuals — what if NVIDIA hadn't…" section
(2–4 counterfactuals, tagged 🔴 as analysis).

## E. Layer `roadmap.md`

Required: a Mermaid `gantt` (NVIDIA + key competitors, 2024–2028) with 🟢/🟡/🔴 in task names or a
legend table; spec-progression chart(s) from the CSVs; a roadmap table (item · window · status ·
confidence · source); "what would change the picture" bullets; **[Q7 · Roadmap & what changes the picture]**.

## F. Layer `value-chain-and-corp-dev.md`

Required: who captures the dollars (BOM share / margin structure table or chart, e.g. Sankey or
waterfall); suppliers and partners; private companies worth knowing (name · what they do · stage /
last public funding · why it matters — public information only); M&A history in the layer;
**[Q8 · Value pools & M&A angles]**; the Corp Dev Lens (questions, not recommendations).

## G. Primer page

Same as B, plus: start from zero ("you know spreadsheets and finance, not chips"); at least two
worked examples; a "Key numbers to remember" table; a "How this connects to the layers" section
linking forward to the relevant layer pages. ≥ 5 visuals.

## H. Cross-cutting chapter

Same as B, ≥ 8 visuals, with the chapter-specific requirements from the master prompt.

## I. Case study

````markdown
# CSn · <Title>

<sub>Case study · ~<N> min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take
## 1. Context
## 2. The decision
## 3. The outcome (with numbers)
## 4. Why it worked (or didn't)
## 5. Lessons for corp dev
## 🎯 Corp Dev Lens
## 📚 Sources
````

≥ 4 visuals (a timeline, a deal-economics chart or table, a before/after chart, a decision diagram).
