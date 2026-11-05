# Contributor brief (for every human or AI contributor)

Read this, then [`MASTER_PROMPT.md`](MASTER_PROMPT.md) (the spec) and [`STYLE_GUIDE.md`](STYLE_GUIDE.md)
(voice, page anatomy, palette, chart rules). State lives in [`../PROGRESS.md`](../PROGRESS.md).

## 0. Ground rules

1. **Live research.** Today is the "as-of" date in `scripts/charts/style.py` (`AS_OF`). Verify
   every product, number, date and deal with web search / page fetches. Your training memory is a
   *hint* about what to search for, never a source. NVIDIA's numbers move every quarter.
2. **Primary sources first:** NVIDIA 10-K/10-Q/8-K (sec.gov), earnings call transcripts, investor
   presentations, GTC/Computex/Hot Chips material, NVIDIA technical blogs/docs/datasheets,
   competitor filings and launch posts, MLCommons results. Then credible analysts (SemiAnalysis,
   The Next Platform, ServeTheHome, Chips and Cheese, Fabricated Knowledge, Stratechery, TrendForce,
   sell-side quoted in Reuters/Bloomberg/WSJ/FT/CNBC).
3. **Public information only.** No confidential Qualcomm information; never invent any. Qualcomm
   content uses only public announcements and filings, framed as questions/options.
4. **Balance.** Give real weight to NVIDIA's weaknesses and the strongest competitor/bear arguments.
5. **Copyright.** Never download or embed third-party images, charts, die shots or press photos.
   Recreate from data. Quotes under 15 words, rare, cited.
6. **Do not run git** (no commit/push/branch). The orchestrator commits. Only write the files you own.
7. **Stay in your lane.** Touch only the files/ID ranges assigned to you. Never edit another
   chapter's pages, another agent's registry file, or shared files (style.py, Makefile, validators).
   If you need a shared change, say so in your final report.

## 1. Citations — the source registry

- Sources live in **`sources/registry/<your-file>.csv`** with the header
  `id,title,publisher,author,date,url,accessed,type,notes`
  - `id`: `S<number>` inside **your assigned range** (below). Never reuse an id.
  - `date`: publication date `YYYY-MM-DD` (or `YYYY-MM` / `YYYY` if that is all that is known).
  - `accessed`: the date you accessed it (`YYYY-MM-DD`, use today's date).
  - `type`: filing · transcript · keynote · press-release · blog · docs · whitepaper · paper ·
    analyst · news · dataset.
  - Quote fields containing commas (standard CSV quoting).
- **Reuse before you add:** `grep -i "<url or title words>" sources/registry/*.csv` — if a source
  already exists (any range), cite its existing id instead of creating a duplicate.
- In prose, cite with bare tokens right after the claim: `… 288 GB of HBM3E [S120].` Multiple:
  `[S120][S133]`. Do **not** hand-write links; `make build` converts tokens into links to
  `sources/bibliography.md` and regenerates each page's `## 📚 Sources` list.
- Estimates: "Est." + the estimator's citation. Forward-looking/disputed claims: 🟢/🟡/🔴 tag.

### Source-id ranges

| Range | Owner |
|---|---|
| S1–S99 | Orchestrator (seed/core) |
| S100–S699 | Phase 1 data agents (100-blocks, assigned per agent) |
| S1000–S1999 | Synthesis: README, 00, 01 flywheel, cheat sheet |
| S`NN`000–S`NN`999 | Chapter NN, for NN = 02…19 (e.g. layer 06 → S6000–S6999; ch. 15 → S15000–S15999) |
| S2`n`000–S2`n`999 | Case study CS`n` (e.g. CS3 → S23000–S23999) |
| S3`n`000–S3`n`999 | Primer P`n` (e.g. P2 → S32000–S32999) |
| S90000+ | QA and refresh |

## 2. Data files (`data/*.csv`)

- Schemas are documented in [`../data/README.md`](../data/README.md). Keep column names exactly.
- Every row has `confidence` (`confirmed` | `reported` | `estimate` | `speculative`) and
  `source_id` (one or more ids separated by `;`). Units go in the column name or a `unit` column.
- No comment lines in CSVs. Dates as `YYYY-MM-DD`, `YYYY-MM`, or `YYYY-Qn`.
- You may add a **new** CSV for your chapter (`data/<chapter>_<topic>.csv`, same conventions,
  documented in a short section appended to `data/README.md` — append only, under your own
  heading). Do not restructure existing CSVs you do not own; you may append rows to a shared CSV
  only if your assignment says so.

## 3. Charts (`scripts/charts/`)

- One module per chart family: `scripts/charts/ch_<topic>.py`. Each chart is a function decorated
  with `@register` that builds a `style.Chart(...)` and calls `c.save(...)` (matplotlib SVG) and,
  where useful, `c.save_plotly(...)` (interactive HTML; `static=True` for Sankey/treemap SVG).
- Required on every chart: **takeaway title** (a sentence with the number that matters), subtitle
  (metric, units, scope), axis labels with units, `source` text + `source_ids`, **alt text**
  (≥ 40 chars, states the takeaway and key numbers), `chapters` list (e.g. `["02","17"]`).
- Chart id = file name: `<chapter>-<slug>` (e.g. `06-networking-revenue-share`).
- Follow the palette: `entity_color("AMD")`, `NV`, `GEN_PAST`, `hatch_future()`; estimates and
  roadmap bars hatched and labeled; log scales labeled (`logy=True` adds the badge).
- Build one module quickly: `python3 scripts/charts/run_all.py <module-or-function-substring>`.
  Full rebuild: `make charts`. **Look at your SVGs** (they are images; open/inspect them) to catch
  overlapping labels.
- The catalog `assets/charts/CATALOG.md` lists every chart with its title, chapters and alt text —
  check it before making a duplicate.

## 4. Diagrams

- Mermaid inline in Markdown (validated by `make validate`). Keep labels short; quote labels that
  contain punctuation: `A["NVLink 5 · 1.8 TB/s"]`. Avoid `%%{init}%%` theme overrides.
- Complex topologies: D2 (`diagrams/src/<chapter>-<slug>.d2`) or Graphviz (`.dot`), rendered by
  `make diagrams` into `assets/diagrams/<id>.svg`. Embed with alt text.
- Validate Mermaid in your files: `node scripts/validate/mermaid_check.mjs <file.md> [...]`.

## 5. Pages

- Follow the page skeleton in STYLE_GUIDE §2 exactly (⚡ The Executive Take → Level-2 sections with
  `> [!TIP]` worked examples → `<details>` 🔧 Under the hood → `## 🎯 Corp Dev Lens` →
  `## 📚 Sources` as the **last** heading, left empty — it is generated).
- **Links:** you may write root-relative links (`/assets/charts/02-x.svg`,
  `/layers/05-scale-up-nvlink-nvswitch/index.md`) and glossary links (`[HBM](glossary:hbm)`);
  `make build` rewrites them into proper relative paths.
- **Embeds:** `![<alt text from CATALOG.md>](/assets/charts/<id>.svg)`; optionally add
  `<sub>[Interactive version](/assets/interactive/<id>.html)</sub>` under it.
- **Glossary:** add every new term you define to `docs/glossary/<your-chapter>.csv`
  (`term,slug,definition,see_also`). Definitions: 1–2 plain-English sentences. Check
  `docs/glossary/*.csv` first and reuse existing slugs.
- **Layer pages:** answer the eight standard questions explicitly, each marked with a bold tag such
  as `**[Q2 · Metrics that matter]**` (Q1 Job & failure mode · Q2 Metrics that matter ·
  Q3 Generational progress · Q4 Source of advantage · Q5 Strongest challenger · Q6 Replication
  cost · Q7 Roadmap & what changes the picture · Q8 Value pools & M&A angles).
- Visual quotas: layer folder ≥ 12 (≥ 40 % data charts from `data/*.csv`), primer ≥ 5,
  cross-cutting ≥ 8, case study ≥ 4. Words: layer folder 6,000–10,000.

## 6. Commands

```bash
make charts      # regenerate all charts from data/*.csv (+ catalog)
make diagrams    # render diagrams/src/* to assets/diagrams/*.svg
make build       # bibliography + glossary + link/citation normalisation + PROGRESS stats
make validate    # citations, links, alt text + quotas, Mermaid render (must pass before any push)
python3 scripts/validate/check_visuals.py --unit 06   # stats for one unit
```

## 7. Your final report (to the orchestrator)

Keep it under ~250 words: files written; words and visuals per page; charts added (ids); source-id
range used (first–last); new glossary terms count; facts you could not verify or that conflict
between sources; anything needing a shared-file change; open gaps.
