# Visual QA (Phase 9, QA-C): charts, Mermaid and D2/Graphviz diagrams

**Reviewer:** independent QA pass (did not author the charts) · **Date:** 2026-11-05 ·
**Scope:** all 357 catalog charts (`assets/charts/`), 220 Mermaid blocks, 14 D2/Graphviz diagrams (`assets/diagrams/`).

## Method

| Step | Coverage | How |
|---|---|---|
| Automated layout scan | **357 / 357 charts** | A harness re-ran every `@register` builder with output redirected to a scratch folder and, just before each SVG was written, measured every drawn text box: text outside the figure (clipping), text-on-text overlaps, legend boxes covering plotted points or bars, 3D axes, two axes sharing one position (dual axis), log axes whose label lacks "log", and numeric axes with no label. Every flag was then looked at by eye. |
| Catalog checks | 357 / 357 | Title is a sentence (≥ 4 words; 355 carry a number, the two without are verdict heatmaps), subtitle present, `source` + `source_ids` present, as-of = 2026-11-05 on every chart. |
| Visual inspection | **~190 charts** (every chapter prefix: 00 8/8, 01 4/4, P1–P5 26/26, CS1–CS7 17/17, 16–19 25/25, 15 24/41, 02–14 5–8 each) | Rasterised with `rsvg-convert` (600–900 px, the width GitHub shows), tiled 6–9 per contact sheet and read; fixed charts were re-rendered and re-read. |
| Mermaid | 220 blocks validated (`mermaid_check.mjs`: OK); 16 of the most complex rendered to PNG with `mmdc` and read (4 sankey-beta, 2 block-beta, 4 gantt, 3 quadrantChart, 3 mindmap) | |
| D2 / Graphviz | **14 / 14** viewed at 780–900 px | |

Check codes used in the table: **T** takeaway title consistent with the plotted data · **S** subtitle with units ·
**X** axis labels with units · **F** footer with source ids and as-of date · **L** log scale labelled (axis text + `LOG SCALE` badge) ·
**P** entity palette (NVIDIA `#5F9E00`, AMD crimson, Google blue, …) · **E** estimates / roadmap visually distinct (hatch, hollow, dashed) ·
**O** no clipped or overlapping text, no legend over data · **D** no 3D, no dual axes.

## Results summary

- **Defects fixed: 27 charts in 23 table rows (8 Medium, 15 Low)**, plus `15-merchant-vs-custom-asic-share` (High), whose data was corrected concurrently by QA-A and which was re-verified here. All fixes are in the owning `scripts/charts/ch_*.py` module; no SVG was hand-edited; `run_all.py` (full) and `sync_alt.py` were re-run.
- **No 3D charts and no dual-axis charts** anywhere (harness: 0 shared-position axes; the twin-panel charts use separate panels).
- **Palette:** NVIDIA green, AMD crimson, Google blue, AWS amber, Microsoft teal, Meta violet, Broadcom pink, Huawei plum, Qualcomm indigo used consistently; one misuse fixed (Ethernet coloured as Broadcom).
- **Log scales:** every log axis carries the `LOG SCALE` badge; two axes lacked "(log …)" in the label and were fixed. One base-2 log axis printed "1.024k … 131.072k" ticks and was fixed.
- **Mermaid:** all 220 render. One systemic defect fixed: 13 gantt blocks used `axisFormat %Y` with no tick interval (Mermaid then draws a tick every ~3 months, so the axis reads "2025 2025 2026 2026 2026 …"), and two used `tickInterval 1year`, which Mermaid 11 silently ignores (its grammar accepts only millisecond…month). All 15 now use `tickInterval 12month` (one label per year); the 02 roadmap keeps its `6month` + `%b %Y`. One quadrant label collision fixed.
- **D2 / Graphviz:** all 14 legible at GitHub width; no fixes needed (minor notes below).
- **Near-duplicates:** 7 pairs worth consolidating, 3 of them involving charts no page embeds (list at the end).

## Defects found and fixed

| Chart id | Checks | Issue | Fix (module) |
|---|---|---|---|
| `15-merchant-vs-custom-asic-share` | T O | Title read "~14% of revenue … but perhaps ~14% of units" (unit rows held the revenue values), and the 2026E revenue and unit labels printed on top of each other (100% overlap) | Data rows corrected by QA-A (27.8 / 69.7, S2517;S666); regenerated chart now separates the labels (70% / 28% units vs 86% / 14% revenue). Verified visually |
| `15-radar-amd` (and the other four single radars) | O | Takeaway title clipped at the right edge ("…Memory and Cost/TC") on the 8.6-in figure | Figure widened to 10.6 in (`ch_x15a._single_radar`) |
| `15-qualcomm-dc-revenue-targets` | O X | Two identical y labels "Qualcomm (target)", both clipped on the left ("ualcomm (target)") | Labels now "Qualcomm (FY2029 target)" / "(FY2027 target)"; left margin 0.11 → 0.19 (`ch_x15b`) |
| `13-investment-dollars-by-year` | O | 2026 deal labels ("OpenAI $30B / Hugging Face $13B") ran off the right edge; 2019 "Mellanox $6.9B" label collided with 2020 "3 deals, undisclosed" | x-limit extended when the last year carries side labels; side labels lifted to ≥16% of the y-range (`ch_deals`) |
| `16-revenue-by-era-log` | O | White-on-green value labels wider than the bars: "$216B" and "$27B" clipped / unreadable at bar edges | Labels moved onto a white backing box in dark NVIDIA ink (`ch_x16`) |
| `P2-kv-cache-vs-context-length` | L O | Base-2 log x-axis printed "1.024k, 4.096k, 16.384k, 65.536k, 131.072k" (style.py's global log formatter overrode the module's 1k/4k/16k/64k/128k labels) | Module formatter protected from the override (`ch_primer_p2`) |
| `02-transistor-count-by-generation` | O | X-axis label "GPU generation (year introduced)" overlapped the source footer (three-line tick labels) | Bottom margin 0.13 → 0.18 (`ch_gpu`) |
| `03-decode-ceiling-vs-batch-32k` | F O | Source footer ran off the right edge (as-of date cut) | Caveat "ignores compute and overhead limits" moved to the note line (`ch_l03_core`) |
| `P4-allreduce-time-by-fabric` | F O | Source footer ran off the right edge (as-of date cut) | Source text shortened to "link specs via interconnect_specs.csv; ring formula" (`ch_primer_p4`) |
| `00-rival-verdicts-by-layer` | X | Count axis had no label | X label "Number of rivals (of 12) per verdict" (`ch_syn`) |
| `05-deepep-nvlink-vs-rdma` | L | Right panel's log2 x-axis not labelled as log | Label "Expert-parallel width (GPUs, log2 scale)" (`ch_l05_core`) |
| `P3-rack-power-by-system` | L | Left panel log axis labelled just "kW" (badge present) | "kW (log scale)" (`ch_primer_p3`) |
| `05-torus-vs-switched-all-to-all` | O | Legend (centre-left) sat on top of the HGX B300 curve | Legend moved to the empty upper-right (`ch_l05_core`) |
| `14-tco-cost-vs-interactivity` | O | Left-panel legend covered the H200 curve | Legend moved to lower right (`ch_x14_tco`) |
| `11-inferencex-same-hardware-history` | X | Index axis starts at 0.7 with no break marker (STYLE_GUIDE §6.7) | `axis_break()` added; y label says "(axis starts at 0.7)" (`ch_mlperf`) |
| `12-nvidia-cloud-service-commitments` | O | Event leader lines struck through the "$2.2B" and "$11B" value labels | Leader lines stop above the labels (`shrinkB`) (`ch_l12_core`) |
| `P3-roofline-h100-b200-rubin` | O | "ridge ≈ 281 FLOPs/B" label struck through by the B200 roofline | White backing box on ridge labels (`ch_primer_p3`) |
| `17-roadmap-gantt-nvidia` | O | Labels on hatched roadmap bars (Rubin Ultra, LP35, Rosa, Kyber NVL144…) were hard to read through the white hatch | Light backing box behind labels on non-shipping bars (`ch_roadmap`) |
| `02-fp8-roadmap-by-vendor` | O | "Ironwood" label sat under the NVIDIA/AMD lines at 2025 | Label moved below its point (`ch_l02_strategy`) |
| `02-fp8-per-watt-vs-memory` | O | "Gaudi 3" and "H200" labels overlapped | Gaudi 3 label moved below its point (`ch_l02_strategy`) |
| `06-ib-vs-ethernet-ai-backend-share` | P | Multi-vendor Ethernet (incl. NVIDIA Spectrum-X) drawn in Broadcom pink, implying Broadcom owns the segment | Ethernet segment uses palette "Other" gray with dark labels (`ch_market`) |
| `P1-training-run-cost` | T | Title "bills span ~88×: $5.6M (DeepSeek-V3) to ~$0.5B" but the chart also plots Llama 3.1 8B at $2.9M, below the stated minimum | Title scoped to "Frontier final-run bills…" (`ch_primer_p1`) |
| `17-preannouncement-horizon` | T | Title "NVIDIA dates GPUs 26–40 months before they ship", but the chart's Blackwell Ultra bar is 14 months and Groq LP35 16 | Title scoped to "Rubin–Feynman GPUs" (`ch_x17`) |
| `18-hyperscaler-capex-trend` | T | Title "plan ~$505B of 2026 capex" used the Jan–Feb 2026 first guides while the repo's own tracker (`l12_hyperscaler_capex_guidance.csv`, S12518/S12519) shows ~$558B by Oct 2026; read as the current plan it is stale | Title/subtitle/alt now say "first guided ~$505B … since risen to ~$558B"; note line shows the latest midpoints computed from the tracker (`ch_financials`). Prose that still says "plan ~$505B" is logged Open for the page owners |

## Flags reviewed and accepted (no change)

| Chart id | Checks | Harness flag | Verdict |
|---|---|---|---|
| `00-gross-margin-path-and-guide`, `13-free-cash-flow-and-buybacks`, `18-nvidia-vs-peers-dc-revenue`, `CS1-payback-scenarios`, `P3-workload-arithmetic-intensity`, `03-packages-per-cowos-wafer`, `04-cpus-per-8-gpus-by-system` | O | Legend box overlaps a shaded band or short bars | Legend sits over a background band / empty headroom, not over data marks: OK |
| `00-nvidia-revenue-by-fiscal-year`, `00-quarterly-revenue-and-guidance`, `03-purchase-obligations-over-time`, `05-nvlink-generations`, `12-nvidia-customer-support-exposure`, `CS4-warrant-value-vs-hardware-spend` | O | Annotation box touches a value label | Labels touch but remain legible at 600 px: OK |
| `11-inference-memory-tradeoff`, `11-decode-bandwidth-by-vendor`, `12-cost-per-useful-gpu-hour`, `13-deals-timeline-by-layer`, `10-nccl-release-cadence` | O | Clustered direct labels | Labels are fanned out with leader lines and readable; `13-deals-timeline-by-layer`'s 2025–26 cluster is dense (5 labels) but legible. OK |
| `18-risk-heatmap` | O | Risk numbers inside circles overlap cell labels | By design (numbered markers); cell text is small (≈7 px at 600 px) but readable at full width. OK |
| `14-tco-cost-stack-waterfalls-by-system`, `16-era-scorecard`, `17-roadmap-by-layer-small-multiples`, `17-spec-progression-small-multiples`, `15-maia/-mtia/-trainium-generations`, `08-rack-spec-roadmap`, `02-rubin-spec-revision`, CS6/P3/P5 second panels | X | Numeric axis without its own label | Small multiples whose panel titles carry the unit (e.g. "HBM bandwidth per chip (TB/s)") and whose first panel or subtitle names it; year axes left unlabelled. Accepted under §6.3 |
| 11 other year-only x-axes (`06-ib-vs-ethernet…`, `09-cuda-vs-rocm-release-cadence`, `15-custom-asic-revenue-trend`, …) | X | Unlabelled numeric x-axis | Ticks are calendar years; accepted |

## Passed visual inspection with no issue

| Chart id | Checks | Issue | Fix |
|---|---|---|---|
| `00-annual-revenue-by-segment` | T S X F L P E O D | none | — |
| `00-moat-strength-by-layer` | T S X F L P E O D | none | — |
| `00-moat-vs-value-capture` | T S X F L P E O D | none | — |
| `00-thesis-in-five-numbers` | T S X F L P E O D | none | — |
| `01-capital-deployment` | T S X F L P E O D | none | — |
| `01-cuda-developers` | T S X F L P E O D | none | — |
| `01-loop-engines` | T S X F L P E O D | none | — |
| `01-revenue-mix-stacked-area` | T S X F L P E O D | none | — |
| `02-broadcom-ai-vs-nvidia-dc` | T S X F L P E O D | none | — |
| `02-die-area-vs-reticle-limit` | T S X F L P E O D | none | — |
| `02-flops-by-precision-log` | T S X F L P E O D | none | — |
| `02-tdp-by-generation` | T S X F L P E O D | none | — |
| `03-cowos-capacity-and-nvidia-share` | T S X F L P E O D | none | — |
| `03-hbm-bandwidth-per-gpu` | T S X F L P E O D | none | — |
| `03-hbm-market-share-by-supplier` | T S X F L P E O D | none | — |
| `03-memory-supply-verdict-heatmap` | T S X F L P E O D | none | — |
| `03-packages-per-cowos-wafer` | T S X F L P E O D | none | — |
| `03-supply-chain-value-sankey` | T S X F L P E O D | none | — |
| `04-amd-x86-server-share-units-vs-revenue` | T S X F L P E O D | none | — |
| `04-arm-server-cpu-share-trackers` | T S X F L P E O D | none | — |
| `04-cpu-competitor-heatmap` | T S X F L P E O D | none | — |
| `04-cpu-gpu-bandwidth-pcie-vs-c2c` | T S X F L P E O D | none | — |
| `04-cpus-per-8-gpus-by-system` | T S X F L P E O D | none | — |
| `04-server-cpu-core-count-roadmap` | T S X F L P E O D | none | — |
| `05-nvlink-fusion-partner-timeline` | T S X F L P E O D | none | — |
| `05-scale-up-bandwidth-per-accelerator-by-vendor` | T S X F L P E O D | none | — |
| `05-scale-up-domain-vs-bandwidth` | T S X F L P E O D | none | — |
| `06-cpo-vs-pluggable-power` | T S X F L P E O D | none | — |
| `06-networking-revenue-and-share` | T S X F L P E O D | none | — |
| `06-networking-value-pool-by-vendor` | T S X F L P E O D | none | — |
| `06-serdes-lane-rate-progression` | T S X F L P E O D | none | — |
| `06-switch-generation-race` | T S X F L P E O D | none | — |
| `07-bluefield-generations` | T S X F L P E O D | none | — |
| `07-checkpoint-write-time` | T S X F L P E O D | none | — |
| `07-infrastructure-tax-estimates` | T S X F L P E O D | none | — |
| `07-nic-dpu-competitor-heatmap` | T S X F L P E O D | none | — |
| `07-nic-dpu-roadmap-by-vendor` | T S X F L P E O D | none | — |
| `08-ai-hardware-profit-pool` | T S X F L P E O D | none | — |
| `08-kw-per-rack-by-generation` | T S X F L P E O D | none | — |
| `08-liquid-cooling-penetration` | T S X F L P E O D | none | — |
| `08-rack-bom-waterfall` | T S X F L P E O D | none | — |
| `08-tokens-per-mw-by-system` | T S X F L P E O D | none | — |
| `09-cuda-developers-over-time` | T S X F L P E O D | none | — |
| `09-cuda-vs-rocm-release-cadence` | T S X F L P E O D | none | — |
| `09-dc-revenue-vs-rd` | T S X F L P E O D | none | — |
| `09-framework-support-heatmap` | T S X F L P E O D | none | — |
| `09-rocm-lag-behind-cuda` | T S X F L P E O D | none | — |
| `09-software-deals-timeline` | T S X F L P E O D | none | — |
| `10-cuda-x-library-timeline` | T S X F L P E O D | none | — |
| `10-library-coverage-heatmap` | T S X F L P E O D | none | — |
| `10-port-lag-amd-vs-nvidia` | T S X F L P E O D | none | — |
| `10-published-library-speedups` | T S X F L P E O D | none | — |
| `11-api-token-price-trend` | T S X F L P E O D | none | — |
| `11-disaggregation-vs-aggregated-b200` | T S X F L P E O D | none | — |
| `11-inference-engine-release-velocity` | T S X F L P E O D | none | — |
| `11-throughput-vs-interactivity-pareto` | T S X F L P E O D | none | — |
| `11-token-revenue-value-pools` | T S X F L P E O D | none | — |
| `12-fragmentation-whole-racks` | T S X F L P E O D | none | — |
| `12-h100-rental-price-rebound` | T S X F L P E O D | none | — |
| `12-neocloud-power-active-vs-contracted` | T S X F L P E O D | none | — |
| `12-utilization-funnel` | T S X F L P E O D | none | — |
| `13-customer-concentration-over-time` | T S X F L P E O D | none | — |
| `13-gross-margin-trend` | T S X F L P E O D | none | — |
| `13-inception-members` | T S X F L P E O D | none | — |
| `13-sovereign-gpu-commitments` | T S X F L P E O D | none | — |
| `14-cost-per-million-tokens-by-system` | T S X F L P E O D | none | — |
| `14-gpu-rental-price-trend` | T S X F L P E O D | none | — |
| `14-tco-gb300-tornado` | T S X F L P E O D | none | — |
| `14-tco-training-run-cost` | T S X F L P E O D | none | — |
| `15-accelerator-landscape-bubble` | T S X F L P E O D | none | — |
| `15-ai-accelerator-market-share` | T S X F L P E O D | none | — |
| `15-amd-instinct-vs-nvidia-generations` | T S X F L P E O D | none | — |
| `15-broadcom-ai-revenue-guidance` | T S X F L P E O D | none | — |
| `15-challenger-gap-to-nvidia` | T S X F L P E O D | none | — |
| `15-china-ai-chip-vendor-revenue` | T S X F L P E O D | none | — |
| `15-competitor-radar-small-multiples` | T S X F L P E O D | none | — |
| `15-competitor-radar-small-multiples-2` | T S X F L P E O D | none | — |
| `15-custom-asic-revenue-trend` | T S X F L P E O D | none | — |
| `15-hyperscaler-capex-vs-silicon-2026` | T S X F L P E O D | none | — |
| `15-latest-quarter-dc-revenue` | T S X F L P E O D | none | — |
| `15-layer-competitor-heatmap` | T S X F L P E O D | none | — |
| `15-memory-bandwidth-by-accelerator` | T S X F L P E O D | none | — |
| `15-mlperf-participation-by-vendor` | T S X F L P E O D | none | — |
| `15-mlperf-training-time-at-scale` | T S X F L P E O D | none | — |
| `15-qualcomm-dc-roadmap-timeline` | T S X F L P E O D | none | — |
| `15-tpu-memory-vs-nvidia` | T S X F L P E O D | none | — |
| `16-bet-lag-to-payoff` | T S X F L P E O D | none | — |
| `16-years-to-revenue-milestones` | T S X F L P E O D | none | — |
| `17-competitor-roadmap-alignment` | T S X F L P E O D | none | — |
| `17-dc-revenue-through-transitions` | T S X F L P E O D | none | — |
| `17-nvidia-release-cadence` | T S X F L P E O D | none | — |
| `17-roadmap-slips-and-pull-ins` | T S X F L P E O D | none | — |
| `17-spec-progression-small-multiples` | T S X F L P E O D | none | — |
| `18-direct-customer-concentration` | T S X F L P E O D | none | — |
| `18-financing-vs-lucent` | T S X F L P E O D | none | — |
| `18-implied-pe-scenarios` | T S X F L P E O D | none | — |
| `18-pjm-capacity-price` | T S X F L P E O D | none | — |
| `19-capability-price-points` | T S X F L P E O D | none | — |
| `19-challenger-win-matrix` | T S X F L P E O D | none | — |
| `19-edge-vs-datacenter-revenue` | T S X F L P E O D | none | — |
| `19-layer-relationship-heatmap` | T S X F L P E O D | none | — |
| `19-rack-memory-capacity` | T S X F L P E O D | none | — |
| `19-warrant-rebate-curves` | T S X F L P E O D | none | — |
| `CS1-networking-before-after` | T S X F L P E O D | none | — |
| `CS2-dc-revenue-per-cuda-developer` | T S X F L P E O D | none | — |
| `CS2-margin-and-rd-through-cuda-years` | T S X F L P E O D | none | — |
| `CS3-owner-tco-per-chip-hour` | T S X F L P E O D | none | — |
| `CS3-tpu-generations` | T S X F L P E O D | none | — |
| `CS4-amd-vs-nvidia-dc-revenue` | T S X F L P E O D | none | — |
| `CS5-deepseek-cost-headline-vs-fleet` | T S X F L P E O D | none | — |
| `CS5-nvidia-dc-revenue-around-deepseek` | T S X F L P E O D | none | — |
| `CS5-spend-multiple-vs-elasticity` | T S X F L P E O D | none | — |
| `CS6-china-parts-tpp` | T S X F L P E O D | none | — |
| `CS6-china-revenue-share` | T S X F L P E O D | none | — |
| `CS6-levy-vs-ban-gross-profit` | T S X F L P E O D | none | — |
| `CS7-breakeven-vs-utilization` | T S X F L P E O D | none | — |
| `CS7-cost-per-gw-estimates` | T S X F L P E O D | none | — |
| `CS7-site-scale-mw` | T S X F L P E O D | none | — |
| `P1-frontier-training-compute-log` | T S X F L P E O D | none | — |
| `P1-gpus-needed-by-model-size` | T S X F L P E O D | none | — |
| `P1-memory-per-parameter-training` | T S X F L P E O D | none | — |
| `P1-tokens-per-parameter-overtraining` | T S X F L P E O D | none | — |
| `P2-decode-tokens-per-second-bound-by-bandwidth` | T S X F L P E O D | none | — |
| `P2-reasoning-token-multiplier` | T S X F L P E O D | none | — |
| `P2-throughput-interactivity-frontier-modeled` | T S X F L P E O D | none | — |
| `P2-token-demand-growth` | T S X F L P E O D | none | — |
| `P3-bottleneck-by-workload` | T S X F L P E O D | none | — |
| `P3-datacenter-power-demand-forecast` | T S X F L P E O D | none | — |
| `P4-communication-volume-by-parallelism` | T S X F L P E O D | none | — |
| `P4-parallelism-dimensions-frontier-runs` | T S X F L P E O D | none | — |
| `P4-pipeline-bubble-fraction` | T S X F L P E O D | none | — |
| `P5-cost-per-flop-trend` | T S X F L P E O D | none | — |
| `P5-cost-per-good-die` | T S X F L P E O D | none | — |
| `P5-gpu-cost-build-up-waterfall` | T S X F L P E O D | none | — |
| `P5-hbm-cost-share` | T S X F L P E O D | none | — |
| `P5-tsmc-capex` | T S X F L P E O D | none | — |
| `P5-wafer-price-by-node` | T S X F L P E O D | none | — |
| `P5-yield-vs-die-area` | T S X F L P E O D | none | — |

## Mermaid diagrams

| Diagram (file:line) | Type | Checks | Issue | Fix |
|---|---|---|---|---|
| 13 gantt blocks: `17-roadmap-2025-2028.md` (×2), `18-vulnerabilities-and-bear-case.md`, `layers/03,04,05,06,07,09,10,11,12,13/roadmap.md` | gantt | axis | `axisFormat %Y` without a tick interval: Mermaid places a tick about every 3 months, so the axis reads "2024 2024 2024 2024 2025 2025 …" | Added `tickInterval 12month` (one tick per year); verified by rendering the 11 and 17 roadmaps |
| `cross-cutting/15-competitive-landscape/amd.md`, `layers/08-systems-racks-ai-factories/roadmap.md` | gantt | axis | `tickInterval 1year` is not valid in Mermaid 11 (accepted units: millisecond…month) and is silently ignored, so these had the same repeated-year axis | Changed to `tickInterval 12month` |
| `cross-cutting/15-competitive-landscape/index.md:60` | quadrantChart | O | NVIDIA [0.97, 0.97] and Google TPU [0.93, 0.93] labels overlapped and "NVIDIA" ran past the plot edge | NVIDIA nudged to [0.95, 0.97] (the caption already says the two are nudged apart) |
| `cross-cutting/16-how-nvidia-built-it-timeline.md:302` | quadrantChart | O | "Hugging Face pending" [0.36, 0.5] sits on the quadrant-3 title, and "Tensor cores" [0.96, 0.86] is clipped at the right edge | **Not changed** (page prose owned by ch. 16; positions encode a judgement). Suggest y 0.5 → 0.46 and x 0.96 → 0.92 |
| `layers/02-gpu-silicon/competition.md:92`, `case-studies/CS7…:134`, `layers/02…/value-chain-and-corp-dev.md:31`, `00-executive-summary.md:178`, `layers/12…/value-chain-and-corp-dev.md:20` | quadrantChart, sankey-beta | O T | none: labels legible, flows sum correctly (e.g. CS7 1 GW = 8.8 + 2.4 + 12 + 22.4 = 45.6; 00 Q2 FY27 96.2 = 89 + 7.2) | — |
| `primers/P4-parallelism-explained.md:120, :187` | block-beta | O | none | — |
| `layers/04, 07, 08 …/index.md:47–48` | mindmap | O | none: colour-coded branches legible at 1,100 px | — |
| `layers/02-gpu-silicon/roadmap.md:26`, `layers/11…/roadmap.md:14`, `17-roadmap…:23, :77` | gantt | O E | Confidence emoji are in each bar label; "Kyber rack reported slip" uses `crit` (red) as intended; long labels spill outside short bars (Mermaid default) but stay readable | — |

All 220 Mermaid blocks pass `node scripts/validate/mermaid_check.mjs` after the edits. Note: the validator cannot catch silently ignored directives such as `tickInterval 1year`.

## D2 / Graphviz diagrams (`assets/diagrams/`, 14 of 14 viewed)

| Diagram | Checks | Notes |
|---|---|---|
| `00-moat-layer-cake`, `00-stack-layer-cake` | O P | Legible; tall (1,900 px) but each layer is readable at GitHub width. Verdict colours (green / amber / red) match the verdict palette |
| `01-flywheel` | O | Legible; edge labels ("units sold", "funds R&D + supply") are the smallest text (~9 px at 900 px) but readable |
| `02-gpu-package-anatomy`, `03-hbm-stack-cross-section` | O | Legible; long and text-dense (best viewed full width) |
| `04-host-attach-pcie-vs-superchip`, `07-dpu-offload`, `08-compute-tray-anatomy`, `08-nvl72-rack-anatomy`, `09-cuda-software-stack`, `05-nvl72-vs-tpu-pod-topology` | O P | Legible; NVIDIA parts in NVIDIA green, Google in Google blue |
| `05-nvlink-switch-tray-anatomy` | O | Legible; the "manages" edge label sits on the switch-board border (cosmetic) |
| `05-nvl72-all-to-all-topology`, `06-rail-optimized-fat-tree` (Graphviz, ~1,230–1,365 pt wide) | O | Legible but scaled to roughly half size at GitHub's content width, so body text renders ~8–9 px. In `05-nvl72-all-to-all-topology` the header's bold run and normal run touch under rsvg ("chips(72 ports…"; the source has a space; font-metric difference). Optional: raise `fontsize` in the .dot sources |

## Near-duplicate charts

| Pair | Same data / message | Embeds | Recommendation |
|---|---|---|---|
| `01-cuda-developers` vs `09-cuda-developers-over-time` | Same metric (registered CUDA developers, 2M → 6M), near-identical titles, but from two different CSVs (`01_flywheel_ecosystem.csv`, `software_ecosystem.csv`), so they can drift | 2 / 3 pages | Keep `09-…` (canonical `software_ecosystem.csv`); repoint the two `01-cuda-developers` embeds to it and retire `01-cuda-developers` |
| `14-capex-vs-power-cost-per-gpu-year` vs `08-capex-vs-power-per-gpu-hour` | Same inputs (`system_specs.csv`, `tco_model_inputs.csv`) and message ("power is only ~12–19% of cost"); per-year vs per-hour units | **0** / 1 | Keep `08-…`; drop the unembedded `14-…` builder |
| `15-fp8-compute-by-accelerator` vs `15-accelerator-landscape-bubble` and `02-fp8-roadmap-by-vendor` | Same FP8 figures and message ("MI455X 20 vs Rubin 17.5; ASICs ≤ 5") | **0** / 2 / 2 | Drop the unembedded `15-fp8-compute-by-accelerator`, or embed it in place of the bubble on pages that need a plain ranking |
| `00-nvidia-revenue-by-fiscal-year` vs `00-annual-revenue-by-segment` | Same series (`financials.csv`, FY2016–FY2026 total revenue, $5.0B → $216B) | **0** / 5 | Keep `00-annual-revenue-by-segment`; drop the unembedded total-only chart |
| `13-customer-concentration-over-time` vs `18-direct-customer-concentration` | Same `financials.csv` rows and message (peak 61% in Q3 FY26); the ch. 13 chart stops at Q3 FY26, three quarters stale, while ch. 18's extends to Q2 FY2027 | 3 / 1 | Keep `18-…` as canonical; repoint the three `13-…` embeds (or extend `13-…` to Q2 FY2027) |
| `11-decode-bandwidth-by-vendor` vs `15-memory-bandwidth-by-accelerator` | Same bandwidth figures and takeaway (MI455X > Rubin; ASICs ~2.6× lower) | 1 / 1 | Keep both: different forms (trend vs ranking) on different chapters. Keep the numbers in sync (both now read MI455X 23.3 TB/s) |
| `05-nvlink-generations` vs `05-nvlink-vs-pcie-bandwidth` | Same `interconnect_specs.csv` series and "19×" headline | 2 / 1 | Keep both (the second adds the PCIe contrast); consider dropping one from the ch. 05 page that shows both |
| `15-radar-*` (5 singles) vs `15-competitor-radar-small-multiples` | Same `competitor_matrix.csv` scores | 1 each / 2 | Intentional: singles are used on the per-competitor pages. Keep |
| `10-library-coverage-heatmap` vs `10-library-coverage-tally` | Tally is the column sum of the heatmap | 1 / 1 | Keep (detail vs summary) |

No chart was deleted (none of the duplicates is removable without page edits, or they are unembedded and harmless).

## Open items

- **Prose still says hyperscalers "plan ~$505B" for 2026** (`01-the-nvidia-flywheel.md:448, :525`, `layers/13-ecosystem-gtm-and-capital/history-and-how-built.md:76`, `cross-cutting/18-vulnerabilities-and-bear-case.md:256`). The figure is the Jan–Feb 2026 first guide; the repo's own tracker shows ~$558B by Oct 2026 (S12518, S12519). The chart now shows both; page owners should say "first guided" or update the figure.
- **`16-how-nvidia-built-it-timeline.md:302` quadrant**: two labels collide or clip (see Mermaid table); suggested coordinates given.
- **Systemic `style.py` suggestions** (not edited; shared file): (1) `Chart.save()` replaces every log-axis tick formatter with `PLAIN_LOG`, which silently overrides module formatters (the cause of the P2 tick bug; P1/P2 work around it with `freeze_scale`). Suggest applying `PLAIN_LOG` only when the axis still has matplotlib's default `LogFormatterSciNotation`. (2) The footer is a single unwrapped line; long `source` strings run off the right edge (two cases fixed here). Suggest truncating `source` to fit the width or wrapping it onto the note line. (3) Rule §6.5 is enforced only when `ylabel=` is passed to `save()`; axes labelled with `set_ylabel()` bypass it. Suggest checking `get_ylabel()` in `save()`.
