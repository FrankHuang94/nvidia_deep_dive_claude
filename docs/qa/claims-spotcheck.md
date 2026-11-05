# Numerical claim spot-check (Phase 9, QA-A)

<sub>Independent QA · 2026-11-05 · reviewer did not write the content · companion to [`QA_LOG.md`](../../QA_LOG.md)</sub>

**Scope.** 89 numerical claims from 53 pages: at least 3 per layer folder (02–13), at least 2 per cross-cutting
chapter (14–19; two pages for chapter 15), at least 1 per case study (CS1–CS7) and per primer (P1–P5), and 8 from
README / 00 executive summary / cheat sheet. The sample favours Executive-Take headline numbers, worked
examples and chart titles. It mixes specs, financials, dates, deal terms, market shares and estimates.

**Method.** Pages could not be fetched in this environment. Each claim was checked against the cited source's
entry in `sources/registry/*.csv` (title, date, notes), the `data/*.csv` rows or `scripts/tco/outputs/*.csv`
behind the number, [`docs/research/2026-fact-sheet.md`](../research/2026-fact-sheet.md), other pages, and
arithmetic. Three WebSearch calls ran successfully (marked **WS**). Every check also confirmed that estimates
carry "Est." and that forward-looking claims carry 🟢/🟡/🔴.

Verdicts: ✅ matches · ⚠️ minor mismatch, rounding or missing caveat/label · ❌ wrong or unsupported ·
❓ cannot verify in this environment.

## Summary

| Area | Claims | ✅ | ⚠️ | ❌ | ❓ |
|---|---:|---:|---:|---:|---:|
| Synthesis (README, 00, cheat sheet) | 8 | 7 | 1 | 0 | 0 |
| Layers 02–13 | 46 | 40 | 4 | 1 | 1 |
| Cross-cutting 14–19 | 21 | 19 | 1 | 1 | 0 |
| Case studies CS1–CS7 | 8 | 7 | 1 | 0 | 0 |
| Primers P1–P5 | 6 | 4 | 2 | 0 | 0 |
| **Total** | **89** | **77** | **9** | **2** | **1** |

| Claim type (approx.) | Count |
|---|---:|
| Specs and performance | 27 |
| Financials and revenue | 24 |
| Estimates and repo models (TCO, BOM, per-MW) | 18 |
| Deal terms and valuations | 9 |
| Market shares | 6 |
| Dates and schedules | 5 |

**What was wrong.**

1. ❌ **Chart `15-merchant-vs-custom-asic-share`.** The title read "~14% of AI silicon revenue … but perhaps
   ~14% of units". The unit-share rows in `data/market_share.csv` held the revenue-share values (13.6 / 86.4).
   That contradicted the source notes (S666, S2517: TrendForce 27.8% ASIC / 69.7% GPU) and the pages' own prose.
   **Fixed:** the data rows now read 27.8 / 69.7, the chart is regenerated (its title now says "~28% of units")
   and the alt text is synced on the three pages that embed it. WS confirms TrendForce's January 2026 figures;
   TrendForce trimmed ASIC to ~27% in April 2026.
2. ❌ **Modular deal status was stale.** Layer 10 said "close expected H2 2026", but the deal closed on 2026-07-29
   (S9511, fact sheet). **Fixed** there and in four more places with the same stale wording.
3. ⚠️ **Seven smaller issues.**
   - The CoWoS multiple (~2.2×) used a different base from its cited source (~2×).
   - "Two nodes ago" should have been three (N7 → N2).
   - One headline share claim cited only sources from the year before.
   - Five confidence tags were missing.

   All fixed.
4. ❓ **MI455X HBM4 bandwidth (material).** The repo uses 19.6 TB/s, AMD's June 2025 figure (S144, flagged
   "re-verify in QA" in the registry). WS (2026-11-05) finds AMD's MI455X product page, Chips and Cheese and Tom's
   Hardware listing **23.3 TB/s** (12 × 36 GB HBM4 at ~7.6 GT/s). No registry or fact-sheet source carries 23.3, so
   nothing was changed. The item is logged **Open** in QA_LOG: about 19 pages and 10 CSVs would need updating, and
   the change would widen AMD's bandwidth lead over Rubin (19.2 TB/s) from ~2% to ~21%.

**Labels.** Every sampled estimate was labelled "Est." (or 🔴 for repo models). Five forward-looking or reported
claims had no tag and now do. One tag was stale (🟡 "close expected"); the deal had closed.

## Results

Basis abbreviations: **reg** = registry notes of the cited id · **data** = named CSV row(s) · **FS** = 2026 fact
sheet · **calc** = arithmetic re-done here · **WS** = WebSearch 2026-11-05.

### Synthesis

| # | File:line | Claim | Cited | Basis | Verdict | Fix |
|---|---|---|---|---|---|---|
| S-1 | README.md:13 | 1 GW AI factory: NVIDIA content ~$35B of a $50–60B budget | S398 | reg S398; data `cs7_cost_per_gw.csv` | ✅ | — |
| S-2 | README.md:25–26 | NVIDIA ~87% of AI DC silicon revenue in 2025; pool grew ~4.2× (Est.) | S416 S660 S663 | data `market_share.csv` (86.6%; $52.6B → $223.6B = 4.25×) | ⚠️ number right, but cites only FY2024-basis sources; the 2025 inputs are S1 (NVIDIA FY2026) and S661 (Broadcom FY2025) | Added [S1][S661] here, in 00:9 and in 15/index:7 |
| S-3 | README.md:30 | Q2 FY2027 $96.2B (+106%), 75.0% GM, Q3 guide $108B, GM trough 71–72% Q4 FY2027 | S405 S3 S90085 | reg; FS | ✅ | — |
| S-4 | 00-executive-summary.md:9–10 | Data Center 90% of FY2026 revenue of $215.9B | S1 S402 | data `market_share.csv` 193.7 / 215.9 = 89.7% | ✅ | — |
| S-5 | 00-executive-summary.md:19–20 | B200 costs ~$6,400 to build vs $30–40K price (Est.) | S35020 S35026 | reg; data `P5_wafer_economics.csv` BOM rows | ✅ | — |
| S-6 | 00-executive-summary.md:27 | $42.4B equity bought in H1 FY2027, ~24% of revenue | S90072 S18007 | reg; calc 42.4 / (81.6 + 96.2) = 23.8% | ✅ | — |
| S-7 | CHEATSHEET.md:31 | Networking ~$17.5B in Q2 FY2027 (Est.), ~20% of Data Center | S408 | FS (+18% q/q on $14.8B); WS (+138% y/y on ~$7.3B ≈ $17.4B); 17.5 / 89.0 = 19.7% | ✅ | — |
| S-8 | CHEATSHEET.md:27 | Rubin 35 PFLOPS dense FP4; 288 GB HBM4 at 19.2 TB/s | S33005 S90006 | data `gpu_product_specs.csv` Rubin row; FS revision | ✅ (35 PF is NVIDIA's NVFP4 "training" figure, treated as dense; documented in the data notes) | — |

### Layers 02–13

| # | File:line | Claim | Cited | Basis | Verdict | Fix |
|---|---|---|---|---|---|---|
| L02-1 | layers/02-gpu-silicon/index.md:8 | Rubin 35 PFLOPS dense NVFP4 ≈ 280× V100's 125 TFLOPS; 16-bit gain ~32× | S33005 S33010 S100 | data `gpu_product_specs.csv`; calc 35,000/125, 4,000/125 | ✅ | — |
| L02-2 | layers/02-gpu-silicon/index.md:10 | HBM BW ~5.7× H100 → Rubin (3.35 → 19.2 TB/s) vs compute ~18× | S33002 S33007 | reg S33002; calc 19.2/3.35; 35,000/1,979 | ✅ | — |
| L02-3 | layers/02-gpu-silicon/index.md:11 | Rubin HBM4 22 → 19.2, NVLink 6 3.6 → 3.0 TB/s 🟢; production shipments early Aug 2026 | S90006 S500 S90009 | reg; FS | ✅ | — |
| L02-4 | layers/02-gpu-silicon/competition.md:88 | Per MW: ~435 Rubin ≈ 7.6 EF FP8; ~714 MI355X ≈ 3.6 EF; ~1,333 Maia 200 ≈ 6.7 EF | S106 S143 S158 | reg (2.3 kW Max-P is analyst-reported; 1,400 W; 750 W); data `competitor_accelerators.csv` | ✅ | — |
| L02-5 | layers/02-gpu-silicon/value-chain-and-corp-dev.md:126 | Groq ~$20B ≈ 2.9× its $6.9B mark ≈ 3 weeks of Q2 FY2027 DC revenue | S90019 S405 | reg; calc 89.0/13 = $6.85B/week | ⚠️ price undisclosed and only reported (FS 🟡), but untagged | Added "(🟡 reported)" |
| L02-6 | layers/02-gpu-silicon/roadmap.md:105 | 70B FP8 decode ceiling 314 → 274 tok/s (~13%); MI455X ≈ 280 | — | calc | ✅ | — |
| L03-1 | layers/03-memory-packaging-supply-chain/index.md:7 | Since V100: compute ~280×, HBM BW ~21×; 70B FP8 stream ~48 tok/s on H100, ~274 on Rubin | S33010 S33005 S33007 S33002 | calc 0.9 → 19.2; 3.35/70; 19.2/70 | ✅ | — |
| L03-2 | layers/03-memory-packaging-supply-chain/index.md:8 | Memory ~9% → ~26% of NVL72 rack cost, GB300 → Vera Rubin (Est.) | S330 S332 | reg S330 ($2.0M of $7.80M = 25.6%), S331 ($0.374M of ~$3.99M = 9.4%) | ✅ | — |
| L03-3 | layers/03-memory-packaging-supply-chain/index.md:10 | 🟡 CoWoS ~15k → ~115k wafers/month end-2023 → end-2026 (Est.); NVIDIA ~60% of 2026 wafers | S379 | data `hbm_and_packaging.csv` (15 / 115); reg S379 (~595k wafers, ~60%); FS (105–130k) | ✅ (`l03_cowos_outlook.csv` uses a 120k midpoint; both are inside the range) | — |
| L03-4 | layers/03-memory-packaging-supply-chain/supply-chain-as-a-weapon.md:20 | $279B ≈ 11.6 quarters (~2.9 years) of COGS; mid-2022 $9.2B ≈ 1.4× revenue | S405 S407 S420 S433 | reg S407; calc 96.2 × 0.25 = $24B | ✅ | — |
| L03-5 | layers/03-memory-packaging-supply-chain/roadmap.md:72 | CoWoS "~2.2× from ~120k (end-2026) to ~260k (2028)" | S3002 | reg S3002 says ~130k → ~260k (≈2×); 120k is the repo midpoint | ⚠️ multiple and base do not match the cited source | Now "roughly double, from ~120–130k"; "twice the wafers" |
| L03-6 | layers/03-memory-packaging-supply-chain/index.md:12 | MI455X 432 GB at 19.6 TB/s vs Rubin 288 GB at 19.2 | S144 S33007 | reg S144 ("re-verify in QA"); FS (Helios 31 TB ✓); **WS: AMD MI455X page, Chips and Cheese and Tom's Hardware list 23.3 TB/s** | ❓ 432 GB ✓; 19.6 TB/s not confirmed and likely superseded | Not changed (no in-repo source for 23.3). Logged Open in QA_LOG (High) |
| L04-1 | layers/04-cpu-grace-vera/index.md:7 | DGX-2 delivered 56% of its ResNet-50 throughput when CPUs prepared the data | S4017 | reg; calc 12,586 / 22,656 = 55.6% | ✅ | — |
| L04-2 | layers/04-cpu-grace-vera/index.md:8 | 900 GB/s NVLink-C2C ≈ 7× PCIe Gen5 x16 | S129 S222 | calc 900 / 128 | ✅ | — |
| L04-3 | layers/04-cpu-grace-vera/index.md:10 | Vera: 88 cores / 176 threads, up to 1.5 TB LPDDR5X at ~1.2 TB/s; 256-CPU rack | S4000 S4002 | reg; data `cpu_specs.csv` | ✅ | — |
| L04-4 | layers/04-cpu-grace-vera/index.md:12 | Host ~2% of rack: ~$180k of an estimated $7.8M | S331 | reg S331 (Vera CPUs ~$180k); calc 2.3% | ✅ | — |
| L04-5 | layers/04-cpu-grace-vera/index.md:11 | CPU:GPU ratios moving toward 1:2–1:1 (Intel, TrendForce forecast) | S4012 S4013 | reg | ⚠️ forward-looking forecast, no tag | Added 🟡 |
| L05-1 | layers/05-scale-up-nvlink-nvswitch/index.md:7 | NVLink 5 900 GB/s each way ≈ 9× an 800G NIC | S200 S264 | calc 900 / 100 | ✅ | — |
| L05-2 | layers/05-scale-up-nvlink-nvswitch/index.md:8 | NVL72: 18 switch chips, ~5,000 cables, 130 TB/s; Vera Rubin 216 TB/s after cut from 260 | S262 S5000 S200 S201 | reg S5000; FS (3.0 TB/s × 72); calc 72 × 1.8 / 3.0 / 3.6 | ✅ | — |
| L05-3 | layers/05-scale-up-nvlink-nvswitch/index.md:10 | Copper avoids ~19 kW and ~$0.7M of optics per rack (Est.) | S5000 S5016 | data `l05_copper_vs_optics.csv` (1,296 modules × $500–600 = $0.65–0.78M; NVIDIA ~20 kW) | ✅ (deep-dive page gives the net saving, ~$0.5M; consistent) | — |
| L06-1 | layers/06-scale-out-scale-across-networking/index.md:8 | Networking $14.8B Q1 FY2027 (record), ~$17.5B Q2 (Est.), ~20% of DC | S90014 S408 | FS; WS | ✅ | — |
| L06-2 | layers/06-scale-out-scale-across-networking/index.md:9 | Switch capacity 25.6 → 115.2 Tb/s (Quantum-2 → Quantum-X800); NIC 400G → 1.6T | S266 S264 S33004 | calc 64 × 400G; 144 × 800G | ✅ | — |
| L06-3 | layers/06-scale-out-scale-across-networking/index.md:11 | 100k-GPU fabric ~3,500 switches, ~350,000 modules (Est.); networking ~17–21% of capex | S294 S6026 S324 | data `network_topology_estimates.csv` (3,473 switches; 350,000 modules); reg S6026 (17–19%) | ✅ | — |
| L07-1 | layers/07-dpu-supernic-storage-security/index.md:7 | SuperNIC per GPU 400 / 800 / 1,600 Gb/s (GB200 / GB300 / Vera Rubin) | S266 S264 S33004 | reg; data `l07_nic_per_gpu.csv` | ✅ | — |
| L07-2 | layers/07-dpu-supernic-storage-security/index.md:10 | 128K-token context reloads in ~0.2 s vs ~4.7 s to recompute (Est.) | S7000 | data `l07_kv_tiers.csv`; calc 21.5 GB ÷ 100 GB/s; ≈4.1e16 FLOPs ÷ (50% × 17.5 PF) | ✅ | — |
| L07-3 | layers/07-dpu-supernic-storage-security/storage-for-ai.md:25 | Checkpoint stalls 10.2% / 3.2% / 1.2%; cluster $429M/yr; 1 TB/s storage worth ~$30M/yr (Est.) | S34004 S34006 S395 S7000 | calc (Young interval 18.4 / 5.8 min; 16,384 × 8,760 × $2.99) | ✅ | — |
| L07-4 | layers/07-dpu-supernic-storage-security/index.md:13 | Helios: 2.4 Tb/s of Pensando NICs per GPU, 1.5× Vera Rubin | S228 S7500 | reg S228; calc 2.4 / 1.6 | ✅ | — |
| L08-1 | layers/08-systems-racks-ai-factories/index.md:7 | $129K DGX-1 → ~$4.0M GB300 NVL72 → ~$7.8M Vera Rubin NVL72 (Est., Morgan Stanley) | S310 S332 S330 | reg | ✅ | — |
| L08-2 | layers/08-systems-racks-ai-factories/index.md:9 | Power per system ~190×: 3.2 kW → ~600 kW Kyber (🟢); VR ~190–230 kW (🟡) | S310 S337 S303 S305 | calc 600 / 3.2 = 188; tags present | ✅ | — |
| L08-3 | layers/08-systems-racks-ai-factories/index.md:10 | GB300 NVL72 ~13× H200 tokens per MW at 50 tok/s/user (Est.) | S621 S622 | data `x00_thesis_metrics.csv` (6,261 vs 308) ÷ `l08_power_per_gpu.csv` (2.12 vs 1.37 kW) = 13.1× | ✅ | — |
| L09-1 | layers/09-cuda-and-system-software/index.md:9 | MI355X: FP4 on day 8, 50 tok/s/user on day 27, still ~5× behind B200 | S633 S631 | data `l09_dsv4_bringup.csv` | ✅ | — |
| L09-2 | layers/09-cuda-and-system-software/index.md:10 | FA2 73% (A100) → 35% (H100); FA3 75%; FA4 71% on B200 | S9002 S9003 S9004 | reg | ✅ | — |
| L09-3 | layers/09-cuda-and-system-software/index.md:11 | Qualcomm closed the ~$3.9B Modular purchase on 2026-07-29 | S90057 S9511 | reg S9511; FS (one low-tier source: $3.1B) | ✅ | — |
| L10-1 | layers/10-libraries-cuda-x/index.md:8 | Rubin dense FP4 = 8.75× its BF16 rate | S100 | calc 35,000 / 4,000 | ✅ | — |
| L10-2 | layers/10-libraries-cuda-x/index.md:9 | In-switch reduction: 70B all-reduce on GB200 NVL72 0.31 → 0.16 s; NCCL 19 minor versions in 50 months | S34011 S200 S10038 | calc 2 × 71/72 × 140 GB ÷ 900 GB/s; data `l10_nccl_releases.csv` (2.13 Jul 2022 → 2.32 Sep 2026) | ✅ | — |
| L10-3 | layers/10-libraries-cuda-x/index.md:13 | Spark on GPU 1.06× faster, ~80% cheaper; "Qualcomm's agreed $3.9B purchase of Modular (🟡 close expected H2 2026)" | S10020 S90057 | reg S10020 ($6.27 vs $31.28 ✓); reg S9511 + FS: closed 2026-07-29 | ❌ deal status stale | Now "~$3.9B purchase of Modular, closed on 2026-07-29" [S9511]. Same fix in layers/10/roadmap.md:89, layers/12/value-chain-and-corp-dev.md:131 and :136, CS2:12 |
| L11-1 | layers/11-inference-and-ai-software/index.md:7 | Inference >40% of DC revenue for the year to Q2 FY2025 → at least ~$33B | S11011 S441 | reg; data `financials.csv` (DC Q3 FY24–Q2 FY25 = $81.7B × 40% = $32.7B) | ✅ | — |
| L11-2 | layers/11-inference-and-ai-software/index.md:8 | Google's monthly tokens up ~134× in 18 months | S32018 S32020 | data `P2_token_demand.csv` (9.7T Apr 2024 → 1,300T Oct 2025) | ✅ | — |
| L11-3 | layers/11-inference-and-ai-software/index.md:10 | MLPerf DeepSeek-R1 on unchanged GB300 NVL72 +2.9× in a year; cost per M tokens −65% | S601 S603 S622 | data `mlperf_results.csv` (Server 2,907 → 8,291 tok/s/GPU = 2.85×) | ✅ | — |
| L12-1 | layers/12-orchestration-and-cloud-services/index.md:7 | GB300 GPU ~$1.50 per installed hour; $5.00 per useful hour at 30%, $1.67 at 90% (Est.) | S332 S324 | calc $70K ÷ (6 × 8,760) + $0.17 | ✅ | — |
| L12-2 | layers/12-orchestration-and-cloud-services/index.md:8 | Alibaba 155,410 GPUs, allocation 68% → 93%; Llama 3 had 419 unexpected interruptions in 54 days, 38–41% MFU | S12015 S34006 | reg; Llama 3 paper (466 total, 419 unexpected) | ✅ | — |
| L12-3 | layers/12-orchestration-and-cloud-services/index.md:10 | $29B cloud-service plus $36B AI-cloud capacity agreements (Jul 2026) | S407 | reg S407 | ✅ | — |
| L12-4 | layers/12-orchestration-and-cloud-services/index.md:11 | Hyperscale ~55% of Q2 FY2027 Data Center revenue | S90011 S90013 | FS; calc 48.7 / 89.0 | ✅ | — |
| L13-1 | layers/13-ecosystem-gtm-and-capital/index.md:9 | Sovereign >~$30B FY2026 ≈ 14% of revenue; ~1.03M GPUs named (HUMAIN 600k, Korea 260k) | S90071 S1 S13003 S13000 | data `l13_sovereign_commitments.csv` (headline rows sum 1,028,736) | ✅ | — |
| L13-2 | layers/13-ecosystem-gtm-and-capital/index.md:11 | Private stakes $3.4B → $51.2B; all stakes ~$99B; "led by ~$30B in OpenAI" | S13043 S90072 S90073 S90015 | reg; FS (OpenAI ~$30B reported 🟡, close not confirmed) | ⚠️ OpenAI stake stated as fact, untagged | Added "(🟡 reported)" |
| L13-3 | layers/13-ecosystem-gtm-and-capital/index.md:8 | GTC ~1,500 attendees (2009) → >30,000 expected (2026) | S13024 S13533 | reg | ✅ | — |

### Cross-cutting 14–19

| # | File:line | Claim | Cited | Basis | Verdict | Fix |
|---|---|---|---|---|---|---|
| 14-1 | cross-cutting/14-training-vs-inference-economics.md:8 | GB300 ~$2.46 per installed hour (Est.) vs SemiAnalysis $2.31 | S332 S14000 S622 | `scripts/tco/outputs/x14_tco_results.csv` (2.4595); reg S622 | ✅ | — |
| 14-2 | cross-cutting/14-training-vs-inference-economics.md:9 | ~$0.16 per M tokens (Est.); ~3.4× below TPU v7, ~6× below MI355X | S14000 S621 | TCO results (0.156 / 0.532 / 0.978) | ✅ | — |
| 14-3 | cross-cutting/14-training-vs-inference-economics.md:12 | 10²⁷-FLOP run ~$515M on GB300 vs ~$293M on TPU v7 (Est.); Vera Rubin ~26 days (🔴) | S14000 S31007 | `x14_tco_training_run.csv` (514.6 / 292.6 / 26.2) | ✅ | — |
| 15-1 | cross-cutting/15-competitive-landscape/index.md:12 | ~$194B FY2026 DC ≈ 12× AMD DC segment, ≈ 10× Broadcom AI; Broadcom $16.7B, +221% | S1 S450 S451 S2516 | data `market_share.csv` (193.7 / 16.7 = 11.6; / 20.2 = 9.6); reg S2516 | ✅ | — |
| 15-2 | cross-cutting/15-competitive-landscape/index.md:9 | MLPerf Llama 2 70B: MI355X 12,935 vs B200 12,994 tok/s per GPU | S602 | data `mlperf_results.csv` v6.0 Offline | ✅ | — |
| 15-3 | cross-cutting/15-competitive-landscape/amd.md:10 | NVIDIA DC revenue 3.3× AMD's (early 2023) → ~13× (mid-2026) | S450 S405 | reg S543 (AMD Q2 2026 DC $6.7B); calc 89.0 / 6.7 = 13.3 | ✅ | — |
| 15-4 | chart `15-merchant-vs-custom-asic-share` (embedded at 15/index.md:32, 15/custom-asic-houses.md:199, 18:150) | Title "Custom ASICs … ~14% of revenue by 2026E, but perhaps ~14% of units" | S666 (data) | data `market_share.csv` unit rows (13.6 / 86.4) vs reg S666/S2517 (27.8 / 69.7) and page prose; WS (TrendForce Jan 2026: 27.8% / 69.7%; ~27% in Apr 2026 update) | ❌ unit share was the revenue share copied in | Data rows corrected to 27.8 / 69.7 (S2517;S666); chart regenerated ("~28% of units"); alt text synced |
| 16-1 | cross-cutting/16-how-nvidia-built-it-timeline.md:8 | Revenue $158M (FY1999) → $215.9B (FY2026) ≈ 1,365×; 88% of the growth came in FY2024–26 | S16015 S1 S16016 | data `x16_long_run_financials.csv`; calc (215.9 − 27.0) / (215.9 − 0.16) = 87.6% | ✅ | — |
| 16-2 | cross-cutting/16-how-nvidia-built-it-timeline.md:9 | GM 45.6% (FY2008) → 34.3% (FY2009) | S22000 | reg | ✅ | — |
| 16-3 | cross-cutting/16-how-nvidia-built-it-timeline.md:10 | Arm $40B bid terminated in 2022, ~$1.36B charge; Icera $367M | S465 S466 S16009 | reg (Reuters gives $352.2M for Icera) | ✅ | — |
| 17-1 | cross-cutting/17-roadmap-2025-2028.md:11 | Data Center revenue rose for 14 straight quarters | S405 S17006 | data `financials.csv` (up every quarter, Q1 FY24 → Q2 FY27) | ✅ | — |
| 17-2 | cross-cutting/17-roadmap-2025-2028.md:14 | Q3 FY2027 results on 2026-11-17; GTC DC keynote 2026-12-01; GTC 2027 March 14–18 | S17005 S90047 S17000 | reg; FS | ✅ | — |
| 17-3 | cross-cutting/17-roadmap-2025-2028.md:10 | Groq 3 LPX (256 LPUs) in full production from August 2026 | S506 S108 S109 | reg S506 (2026-08-24) | ✅ | — |
| 18-1 | cross-cutting/18-vulnerabilities-and-bear-case.md:8 | Commitments $279B = 2.9× quarterly revenue vs ~1.4× before the FY2023 bust | S407 | calc 279 / 96.2; 9.2 / 6.7 | ✅ | — |
| 18-2 | cross-cutting/18-vulnerabilities-and-bear-case.md:9 | $42.4B of equity (~24% of H1 revenue); $50.3B operating cash flow in Q1 FY2027 | S90072 S403 | data `financials.csv` (OCF 50.3, confirmed) | ✅ | — |
| 18-3 | cross-cutting/18-vulnerabilities-and-bear-case.md:11 | China ~26% (FY2022) → 5.6–8.2% (FY2027 quarters); SAMR fine ~$0.2–2.5B | S2 S90070 S90069 S9505 S401 | data `cs6_china_revenue.csv` (FY2025 $25.0B, FY2026 $19.7B, HQ basis) | ✅ | — |
| 19-1 | cross-cutting/19-implications-for-qualcomm.md:15 | Qualcomm's $15B-by-FY2029 goal ≈ 8% of NVIDIA's FY2026 DC revenue | S90059 S1 | FS; calc 15 / 193.7 | ✅ | — |
| 19-2 | cross-cutting/19-implications-for-qualcomm.md:20–21 | NUVIA $1.4B + Alphawave ~$2.4B + Modular $3.9B ≈ $7.7B | S4538 S4514 S90057 | reg | ✅ | — |
| 19-3 | cross-cutting/19-implications-for-qualcomm.md:32–33 | QCT ~$8.5B vs NVIDIA Edge $7.2B; $89.0B DC quarter ≈ 71× Qualcomm's FY2027 run-rate goal | S19002 S405 S15512 | reg ($8,504M; $5B FY2027 target); calc 89 / 1.25 | ✅ | — |
| 19-4 | cross-cutting/19-implications-for-qualcomm.md:27 | GB300 ~2.6M tok/s per MW vs ≤0.7M for shipping rivals (Est.) | S14000 | TCO results (2.57M; TPU v7 0.69–0.73M; MI355X 0.31M) | ✅ (Helios, modelled at 2.45M, is excluded as not yet in volume) | — |
| 19-5 | cross-cutting/19-implications-for-qualcomm.md:21–22 | "Meta is the first Dragonfly C1000 customer from H2 2028" | S90058 | FS (Investor Day, 🟢 announced) | ⚠️ forward-looking, no tag | Added 🟢 |

### Case studies

| # | File:line | Claim | Cited | Basis | Verdict | Fix |
|---|---|---|---|---|---|---|
| CS1 | case-studies/CS1-mellanox-the-best-deal.md:10 | Networking ~$31.4B (FY2026) ≈ 24× Mellanox's 2019 revenue; closed 413 days after announcement | S402 S21008 S21000 | reg S21000 ($1,330.6M); calc 31.4 / 1.33; 2019-03-11 → 2020-04-27 | ✅ | — |
| CS2-a | case-studies/CS2-cuda-the-15-year-bet.md:11 | ~$32K of DC revenue per developer, ~10× FY2021 (🔴 indicator) | S22009 | data `software_ecosystem.csv`; calc 193.7B / 6M; 6.7B / 2M | ✅ | — |
| CS2-b | case-studies/CS2-cuda-the-15-year-bet.md:12 | "Qualcomm agreed in June 2026 to acquire Modular for $3.9B" | S90057 | reg S9511; FS | ⚠️ omits that the deal closed 2026-07-29 | Added "and closed the deal on 2026-07-29" [S9511] |
| CS3 | case-studies/CS3-google-tpu-the-credible-alternative.md:9 | Ironwood 4,614 TFLOPS FP8, 192 GB; 9,216-chip pod = 42.5 EF | S151 S650 | calc 4.614 × 9,216 | ✅ | — |
| CS4 | case-studies/CS4-amd-openai-and-the-second-source.md:9–10 | AMD +23.7% (~$63B on $267B); warrant ~$26B (~9.9% of shares); ~$96B at the $600 hurdle | S24002 S24001 S24005 | calc 160M × $164.67; × $600 | ✅ | — |
| CS5 | case-studies/CS5-deepseek-moment-and-efficiency-shock.md:7 | DeepSeek-V3: 2.788M H800 GPU-hours ≈ $5.6M at $2/h | S34007 | calc | ✅ | — |
| CS6 | case-studies/CS6-china-export-controls-h20-and-beyond.md:10 | $4.5B H20 charge in Q1 FY2026; GAAP gross margin 60.5% | S90081 S90082 S444 | FS; data `financials.csv` (Q1FY26 GAAP GM 60.5) | ✅ | — |
| CS7 | case-studies/CS7-gigawatt-ai-factories-xai-stargate-etc.md:9 | Bottom-up Vera Rubin GW ~$46B (Est.), ~$22B NVIDIA content | repo model | data `cs7_gw_build_inputs.csv`; calc 870 MW ÷ 254 kW = 3,425 racks × $7.8M + 26% + $12B facility = $45.6B | ✅ | — |

### Primers

| # | File:line | Claim | Cited | Basis | Verdict | Fix |
|---|---|---|---|---|---|---|
| P1 | primers/P1-how-ai-training-works.md:12–13 | 6 × 405B × 15.6T ≈ 3.8 × 10²⁵ FLOPs; 30.84M H100-hours ≈ $62M at $2 (Est.) | S34006 S31002 S34007 | calc | ✅ | — |
| P2 | primers/P2-how-ai-inference-works.md:15 | ~43 GB KV cache for one 128k-token Llama 3.1 70B conversation | S32006 S32010 | calc 2 × 80 × 8 × 128 × 2 B × 131,072 = 42.9 GB | ✅ | — |
| P3-a | primers/P3-the-four-bottlenecks.md:8 | Ridge points 295 / 281 / 208 FLOPs per byte (H100 / B200 / Rubin) | S33002 S33003 S33005 S33007 | calc | ✅ | — |
| P3-b | primers/P3-the-four-bottlenecks.md:12 | "~600 kW Kyber racks reported for 2027" | S35019 | FS (Kyber ~600 kW, reported) | ⚠️ reported figure, no tag | Added 🟡 |
| P4 | primers/P4-parallelism-explained.md:10 | Ring all-reduce of 140 GB sends ~276 GB per GPU: ~5.5 s at 400 Gb/s vs ~0.31 s on NVLink 5 | S34011 S34015 S34014 | calc | ✅ | — |
| P5 | primers/P5-chip-economics-101.md:13–18 | Wafer ~3× "two nodes ago" ($9.4K N7 → $30K N2); 814 mm² die ~44% yield vs ~90%; ~21× cost per good die | S35001 S35003 S35020 S35008 | data `P5_wafer_economics.csv`; calc (Poisson e^−0.814; 63.5 vs 640 gross dies → 20.6×) | ⚠️ N7 → N2 is three node steps, not two | Now "three nodes ago (N7 → N2)" |

## Files changed by this pass

- `data/market_share.csv`: the two `share_of_ai_server_shipments` rows. The chart
  `assets/charts/15-merchant-vs-custom-asic-share.svg` was regenerated, and the catalog and alt text synced.
- Pages, all re-normalized:
  - README.md, 00-executive-summary.md
  - layers/02/value-chain-and-corp-dev.md, layers/03/roadmap.md, layers/04/index.md
  - layers/10/index.md, layers/10/roadmap.md, layers/12/value-chain-and-corp-dev.md, layers/13/index.md
  - cross-cutting/15-competitive-landscape/index.md, cross-cutting/15-competitive-landscape/custom-asic-houses.md
  - cross-cutting/18-vulnerabilities-and-bear-case.md, cross-cutting/19-implications-for-qualcomm.md
  - case-studies/CS2, primers/P3, primers/P5
