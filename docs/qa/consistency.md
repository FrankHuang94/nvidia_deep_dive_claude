# QA: stale and inconsistent data

<sub>Phase 9 independent QA (QA-B) · checked 2026-11-05 · baseline: [`docs/research/2026-fact-sheet.md`](../research/2026-fact-sheet.md) (S9xxxx ids) and `sources/registry/*.csv`</sub>

This page lists the stale-data and cross-page consistency checks QA ran across every content page (README, 00, 01,
cheat sheet, primers, layers 02–13, chapters 14–19, case studies), what each check found and what was changed.
Every fix is also a row in [`QA_LOG.md`](../../QA_LOG.md). Verification basis: the fact sheet, the registry entry of
the cited source, the `data/*.csv` row carrying the number, and agreement across pages. No new sources were created.

## 1. Superseded numbers and stale status

| # | Check (search) | Found | Action | Basis |
|---|---|---|---|---|
| 1 | Rubin HBM4 "22 TB/s" presented as current | 2 hits, both already in revision context (launch vs revised 19.2 TB/s) | P5 tag corrected: the 19.2 TB/s figure was tagged "🟡 reported spec change, Nov 2026"; now "🟢 NVIDIA spec page, revised Sep–Oct 2026; cause unexplained" [S90006] | Fact sheet: spec page 🟢, cause 🔴 |
| 2 | NVLink 6 "3.6 TB/s" or rack "260 TB/s" / "1,580 TB/s" for Rubin without the revision | 0 — every remaining 3.6 TB/s is NVLink 7 (Rubin Ultra, reported) or AMD Helios; every 260 TB/s is Helios or "260 → 216" | none | `data/l02_rubin_spec_revisions.csv`, S90006–S90008 |
| 3 | Rubin CPX described as on the roadmap without the GTC 2026 caveat | 3 hits: P3 bottleneck table, P3 bull view, P2 Corp Dev Lens | Caveat added ("off the GTC 2026 roadmap; HBM4 revival reported, unconfirmed") [S115][S117] | Fact sheet 🟡/🔴; `data/roadmap.csv` |
| 4 | Qualcomm–Modular "expected to close" / "announced" / "agreed to acquire" as current status | 3 page hits missed by the earlier pass (CS2 Counter-arguments paragraph, CS4 Corp Dev Lens, layer 10 Corp Dev Lens) and 2 data rows (`l10_software_deals.csv`, `l10_replication_costs.csv`, both "expected to close H2 2026") | Reworded to "closed on 2026-07-29" with [S9511]; CSV status/notes updated; charts `10-software-deal-values` and `10-replication-cost-ladder` regenerated | S9511 (Qualcomm release), fact sheet |
| 5 | Hugging Face missing where NVIDIA's M&A is summarised | Layer 10 "M&A history" said NVIDIA's AI-software buys were all ≤ $0.7B and that it uses "partnerships rather than acquisitions"; chart `10-software-deal-values` titled "Qualcomm's $3.9B tops them"; layer 13 index mind-map listed "M&A and licences: Mellanox, Groq" | HF ($12.9B, pending, close targeted H1 2027) added to the prose, the Q8 answer, the mind-map and `data/l10_software_deals.csv`; the chart's title/alt logic now names the largest deal (HF) and keeps "~5.6× the largest earlier one" for Modular; alt text synced | S11500, S11025, S90084 |
| 6 | Broadcom FY2026 AI revenue "$45B" | Chart `15-custom-asic-revenue-trend` alt text hard-coded "~$45B (2026E scenario)" while its bar (from `data/market_share.csv`, Q1 guide + Q2 derived + Q3 reported + Q4 guide) shows ~$57B; `15/custom-asic-houses.md` said "the catalog chart below still shows it" | Alt and title made data-driven ("tracks ~$57B for FY2026"); 4 embeds synced (15 index, 15 custom-asic-houses, 18, CS3); prose updated, citing Broadcom's ~$58B [S2516][S15501] | `data/market_share.csv`, `data/x15_custom_silicon_scale.csv` |
| 7 | Qualcomm datacenter CPU described as undated | Layer 04 roadmap: Executive Take, Gantt bar (2027–28 placeholder), caption and table all said Qualcomm's Oryon server CPU had no public date (🔴) | Replaced with Dragonfly C1000, first deployments H2 2028, Meta first named customer [S90056][S90058] | Fact sheet (Investor Day 2026-06-24); `data/roadmap.csv` already correct |
| 8 | Google TPU "exists only inside Google's own buildings" | CS3 (stale against Oracle-hosted TPUs from 2027, cited on the same page) | Softened: "so far it runs only in Google's datacenters; TPUs hosted in Oracle Cloud from 2027 will be the first exception" [S552] | S552 |

## 2. Supply commitments: $95.2B vs $279B (orchestrator addendum)

The fact sheet (S90069, S90092) records that the Q2 FY2027 10-Q's **supply and capacity commitments of $279B** (from
**$119B** in Q1 FY2027) and the FY2026 10-K's **$95.2B "purchase obligations"** are different line items.

| Page | Claim before QA | Now |
|---|---|---|
| `01-the-nvidia-flywheel.md` (supply pre-commitments paragraph) | Series $4.79B → $95.2B → $119B → $279B with no caveat | Same series plus: the 10-K and 10-Q figures are different line items, the long series is indicative, the like-for-like step is $119B → $279B in one quarter [S90092] |
| `01-the-nvidia-flywheel.md` (flywheel metrics table) | "~58×" from Q2 FY2022 to Q2 FY2027 | "~58× (line definitions differ across years [S90092])" |
| `01-the-nvidia-flywheel.md` (bear case) | Burry's $95B "before they nearly tripled" | "before the broader 10-Q commitments line reached $279B (a different line item [S90092])" |
| `layers/03-…/supply-chain-as-a-weapon.md` (Executive Take) | "$95.2B at the end of FY2026 … now ~2.9× quarterly revenue" | Adds that the 10-K line is not strictly comparable with the 10-Q series ($119B → $279B) [S90092] |
| `layers/03-…/supply-chain-as-a-weapon.md` (body) | "Commitments nearly tripled from $95B in six months" | Bears' near-tripling reading attributed to S431; like-for-like step $119B → $279B [S90092][S404] |
| `layers/03-…/history-and-how-built.md` | "$4.9B in January 2023 to $279B in July 2026" | Adds: the disclosed line was broadened in 2026, so the multiple is indicative [S90092] |
| `cross-cutting/18-vulnerabilities-and-bear-case.md` | Burry's $95B; "six months later … nearly three times that" | 10-K $95B vs the broader 10-Q $279B; like-for-like $119B → $279B [S90092] |

Pages that already said "$279B, up from $119B a quarter earlier" (00, README, 03 index, 17, 18 Executive Take, cheat
sheet) were left unchanged.

**Open for QA-C / orchestrator (charts not changed by QA-B):**

- `03-purchase-obligations-over-time` (embedded in 01, 03 supply-chain-as-a-weapon, 17, 18): subtitle reads
  "purchase/supply commitments vs inventory" and the series runs $4.8B (Q2 FY2022) → $279B (Q2 FY2027) with no note
  that the disclosed line changed definition in 2026. Suggest a chart `note=` such as "10-K purchase obligations
  through FY2026; 10-Q supply and capacity commitments from Q1 FY2027 — not strictly comparable (S90092)".
- `03-commitments-vs-cowos-and-revenue` (03 history-and-how-built): "commitments grew 17× since end-2023" spans the
  same definition change; same note suggested.

## 3. Headline figures across pages

Searched every content page for each headline figure and for competing values of the same metric.

| Figure (fact-sheet value) | Occurrences found | Competing values | Result |
|---|---:|---|---|
| FY2026 revenue $215.9B (S1, S90091) | 21 × "$215.9B", 10 × "$216B" | none ("$210B"/"$200B" hits are other metrics) | ✅ consistent (rounding only) |
| FY2025 revenue $130.5B (S90090) | 2 | none | ✅ |
| FY2026 Data Center $193.7B (S90091) | 4 × "$193.7B", 2 × "~$194B" | none | ✅ |
| Q2 FY2027 revenue $96.2B (S3, S405) | 45 | none ("$96B"/"$95B"/"$98B" hits are AMD-warrant, Dell backlog and DRAM figures) | ✅ |
| Q2 FY2027 Data Center ~$89.0B | 14 | none | ✅ |
| Q2 FY2027 GAAP gross margin 75.0 % | 12 | none (other margins are historical quarters or other companies) | ✅ |
| Q3 FY2027 guide $108B ± 2 %, GM 74 % ± 50 bp | 14 | none ("$104.2B" = CoreWeave backlog) | ✅ |
| FY2028 outlook ~70 % growth, supply-constrained; GM 71–72 % trough Q4 FY2027, 72–73 % FY2028 | 7 + 7 | none | ✅ |
| One direct customer = 16 % of Q2 FY2027 revenue (S90069) | 8 | "~19 %" is NVIDIA's share of TSMC revenue (different metric) | ✅ |
| Supply commitments $279B (from $119B) | 40+ | see section 2 | fixed |

## 4. Other items noted

- **Fact sheet wording (orchestrator file, not edited):** the Qualcomm Investor Day row still says the Modular deal is
  "expected to close H2 2026", while the later row records the 2026-07-29 close. Low; suggest aligning the earlier row.
- **Terminology:** `lint_editorial.py` reported **0** terminology warnings in prose (FY26, HBM3e, NVLink5, NVL-72 and
  so on); no edits needed.
- **Superlatives:** the linter's 4 "unsourced superlative" warnings are all the verb *dominates* in a technical or
  chart-description sense (memory traffic, bandwidth, a chart bar), not claims about a company, so they were left.
  An extended scan for *only / no rival / fastest / best / most powerful* found 3 company claims to fix (row 8 above;
  layer 06 Bull view now cites ConnectX-9 [S33004]; layer 07's "no rival has publicly matched them" now carries a 🔴
  repo-judgement tag).
