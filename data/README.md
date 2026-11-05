# Data dictionary

All charts are generated from these CSVs by `make charts`. Conventions (see `docs/AGENT_BRIEF.md`):
every row ends with `confidence` (`confirmed` | `reported` | `estimate` | `speculative`),
`source_id` (one or more `S…` ids separated by `;`, resolving in `sources/bibliography.md`) and
`notes`. Units live in column names (wide tables) or a `unit` column (long tables). Dates are
`YYYY-MM-DD`, `YYYY-MM` or `YYYY-Qn`. NVIDIA fiscal periods are written `FY2026`, `Q3FY2026`.
Compute figures are **dense** (no sparsity) unless a column says otherwise.

| File | Shape | What it holds |
|---|---|---|
| `gpu_product_specs.csv` | wide, one row per NVIDIA GPU product | specs by generation, Volta → Feynman |
| `competitor_accelerators.csv` | wide, one row per competitor accelerator | AMD Instinct, TPU, Trainium, Maia, MTIA, Gaudi, Ascend, startups, Qualcomm AI100/AI200/AI250 |
| `cpu_specs.csv` | wide, one row per CPU | Grace, Vera, EPYC, Xeon, Graviton, Axion, Cobalt, AmpereOne, Qualcomm (public) |
| `interconnect_specs.csv` | wide, one row per link generation | NVLink 1–6, NVLink-C2C, NV-HBI, NVSwitch, PCIe, UALink, Infinity Fabric, ICI, NeuronLink, IB, Ethernet |
| `networking_products.csv` | wide, one row per switch/NIC/DPU | Quantum, Spectrum, ConnectX, BlueField, photonics; Broadcom, Marvell, etc. |
| `system_specs.csv` | wide, one row per system | HGX, DGX, NVL racks, Helios, TPU pods, Trn UltraServers, CloudMatrix |
| `hbm_and_packaging.csv` | long | HBM generations, supplier shares, CoWoS capacity and allocation |
| `roadmap.csv` | wide, one row per roadmap item | all layers, NVIDIA + competitors, with confidence |
| `acquisitions_investments.csv` | wide, one row per deal | M&A, acquihires, licensing deals, equity investments |
| `competitor_matrix.csv` | long | competitor × dimension scores and verdicts (analyst judgement, sourced) |
| `mlperf_results.csv` | long | MLPerf Training / Inference results |
| `financials.csv` | long | NVIDIA by FY and quarter: revenue mix, margins, R&D, capex, commitments, concentration |
| `software_ecosystem.csv` | long | CUDA developers, downloads, library counts, framework support |
| `tco_model_inputs.csv` | long | inputs for `scripts/tco/` |

## Schemas

### gpu_product_specs.csv
`vendor,product,architecture,form_factor,announce_date,ship_date,process_node,dies_per_package,transistors_b,die_area_mm2_per_die,tdp_w,memory_type,memory_capacity_gb,memory_bandwidth_tbs,memory_stacks,fp64_tflops,fp32_tflops,tf32_tflops_dense,bf16_tflops_dense,fp8_tflops_dense,fp6_tflops_dense,fp4_tflops_dense,int8_tops_dense,scale_up_link,scale_up_bw_gbs_bidir,pcie_gen,status,confidence,source_id,notes`

`status`: `shipping` | `announced` | `roadmap` | `eol`. `form_factor`: `SXM` | `superchip` | `PCIe` | `rack-only`.

### competitor_accelerators.csv
`vendor,product,chip_type,year,status,availability,process_node,transistors_b,memory_type,memory_capacity_gb,memory_bandwidth_tbs,bf16_tflops_dense,fp8_tflops_dense,fp4_tflops_dense,int8_tops_dense,tdp_w,scale_up_tech,scale_up_bw_gbs_bidir,max_scale_up_domain,confidence,source_id,notes`

`chip_type`: `GPU` | `ASIC` | `wafer-scale` | `LPU` | `NPU`. `availability`: `merchant` | `cloud-only` | `internal`.

### cpu_specs.csv
`vendor,product,isa,core_design,cores,process_node,launch_date,status,memory_type,max_memory_gb,memory_bw_gbs,cpu_gpu_link,cpu_gpu_bw_gbs_bidir,tdp_w,role,confidence,source_id,notes`

### interconnect_specs.csv
`family,generation,year,scope,lane_rate_gbps,signaling,lanes_or_links_per_device,per_device_bw_gbs_bidir,max_domain_size,first_product,confidence,source_id,notes`

`scope`: `die-to-die` | `chip-to-chip` | `scale-up` | `scale-out` | `host-io`.

### networking_products.csv
`vendor,product,category,generation,year,status,port_speed_gbps,ports,aggregate_tbps,serdes_gbps,process_node,optics,key_features,confidence,source_id,notes`

`category`: `infiniband-switch` | `ethernet-switch` | `nvlink-switch` | `supernic` | `nic` | `dpu` | `cpo-switch`.

### system_specs.csv
`vendor,system,category,year,status,accelerator,accelerators_per_system,cpus_per_system,scale_up_domain,total_hbm_tb,fp4_pflops_dense,fp8_pflops_dense,power_kw,cooling,weight_kg,est_price_usd_m,confidence,source_id,notes`

### hbm_and_packaging.csv (long)
`record_type,item,period,metric,value,unit,supplier,confidence,source_id,notes`

`record_type`: `hbm_generation` (per-stack specs) | `hbm_market_share` | `hbm_per_gpu` | `cowos_capacity` | `cowos_allocation` | `hbm_pricing` | `packaging_tech`.

### roadmap.csv
`layer,vendor,product,category,announced_date,window_start,window_end,status,key_specs,confidence,source_id,notes`

`layer`: `02`…`13`. `status`: `shipping` | `announced` | `roadmap` | `delayed` | `rumored` | `cancelled`.

### acquisitions_investments.csv
`announce_date,close_date,counterparty,deal_type,amount_usd_m,amount_basis,layer_strengthened,rationale,status,confidence,source_id,notes`

`deal_type`: `acquisition` | `acquihire-license` | `equity-investment` | `strategic-partnership-investment` | `failed-acquisition`. `amount_basis`: `disclosed` | `reported` | `estimate` | `up-to`.

### competitor_matrix.csv (long)
`competitor,dimension_type,dimension,score_0_5,verdict_vs_nvidia,rationale,confidence,source_id,notes`

`dimension_type`: `layer` (02–13) | `capability` (radar axes). `verdict_vs_nvidia`: `leads` | `parity` | `behind` | `different`. Scores are sourced analyst judgements (`confidence` usually `speculative`).

### mlperf_results.csv (long)
`round,round_date,benchmark,scenario,division,submitter,system,accelerator,accelerator_count,metric,value,unit,per_accelerator_value,confidence,source_id,notes`

### financials.csv (long)
`period,period_type,period_end,metric,value,unit,confidence,source_id,notes`

`period_type`: `FY` | `Q`. Metric names are snake_case (e.g. `revenue_total`, `revenue_data_center`, `revenue_dc_compute`, `revenue_dc_networking`, `gross_margin_gaap_pct`, `rd_expense`, `capex`, `purchase_obligations`, `customer_a_pct_revenue`).

### software_ecosystem.csv (long)
`record_type,date,entity,metric,value,unit,confidence,source_id,notes`

`record_type`: `time_series` | `support_matrix`.

### tco_model_inputs.csv (long)
`system,vendor,input,value,unit,basis,confidence,source_id,notes`

## Primer P3 — the four bottlenecks (`P3_*.csv`, charts in `scripts/charts/ch_primer_p3.py`)

### P3_roofline_inputs.csv (wide, one row per NVIDIA flagship GPU)
`vendor,product,architecture,year,status,bf16_tflops_dense,fp8_tflops_dense,fp4_tflops_dense,memory_bandwidth_tbs,memory_capacity_gb,scale_up_bw_gbs_bidir,tdp_w,confidence,source_id,notes`

Small, self-contained spec extract (V100 → Rubin) used for roofline ridge points and the memory-wall index. All compute is dense. V100's 16-bit value is FP16 (no BF16). Rubin uses the currently listed 19.2 TB/s HBM4 and 3.0 TB/s NVLink 6 (launched as 22 TB/s and 3.6 TB/s). `ch_primer_p3.py` now reads H100/B200/Rubin from the shared `gpu_product_specs.csv` and falls back to this file only if those rows are missing.

### P3_workload_intensity.csv (one row per operation)
`workload,phase,precision,batch_or_tokens,arithmetic_intensity_flops_per_byte,method,confidence,source_id,notes`

Arithmetic intensity computed by the repo for a 70B-class layer (hidden 8,192, BF16) with the GEMM formula 2MNK / (2·(MK+KN+MN)); attention and MoE rows use the formulas in `method`. All rows are `estimate`.

### P3_power_demand.csv (long)
`scope,source_org,scenario,year,value_type,twh,share_of_electricity_pct,confidence,source_id,notes`

Datacenter electricity use and forecasts (IEA global; LBNL and EPRI United States). `value_type`: `estimate-of-actual` | `forecast`.

### P3_bottleneck_matrix.csv (long)
`workload,bottleneck,severity_1_3,label,rationale,confidence,source_id,notes`

Repo analysis (all `speculative`) of which bottleneck binds for each workload: 3 = Binding, 2 = Significant, 1 = Minor.

## Primer P4 — parallelism explained (`P4_*.csv`, charts in `scripts/charts/ch_primer_p4.py`)

### P4_fabric_bandwidth.csv (one row per link generation)
`fabric,generation,first_product,year,scope,per_gpu_bw_gbs_unidir,per_gpu_bw_gbs_bidir,status,confidence,source_id,notes`

Per-GPU link bandwidth (GB/s) for PCIe, InfiniBand and NVLink, used for all-reduce timing. `scope` as in `interconnect_specs.csv`. `ch_primer_p4.py` now reads the shared `interconnect_specs.csv` (adding the 1.6 Tb/s Rubin-generation NIC) and falls back to this file only if rows are missing.

### P4_comm_volume_example.csv (one row per parallelism type)
`parallelism,degree,fabric,gb_per_gpu_per_step,critical_path,formula,confidence,source_id,notes`

Repo estimate of GB sent per GPU per training step for a 70B dense model (80 layers, hidden 8,192, 4,096-token sequences, BF16) split TP8 × PP4 × DP64 on 2,048 GPUs with a 4M-token global batch. Formulas in `formula`.

### P4_pipeline_bubble.csv (generated grid)
`schedule,pipeline_stages,virtual_chunks,micro_batches,bubble_fraction_of_step,formula,confidence,source_id,notes`

Idle share of step time = (p−1)/(v·m+p−1) for p stages, m micro-batches and v interleaved chunks (v = 1 for plain 1F1B).

### P4_parallelism_configs.csv (one row per published training run)
`run,organization,year,model_params_b,accelerator,gpus,tp,cp,pp,dp,ep,sharding,seq_len,mfu_pct,confidence,source_id,notes`

Published parallelism degrees; `gpus` = tp × cp × pp × dp (expert parallelism `ep` overlaps the data-parallel GPUs). `mfu_pct` is model FLOPs utilization where the paper reports it.

## Primer P5 — chip economics (`P5_wafer_economics.csv`, charts in `scripts/charts/ch_primer_p5.py`)

### P5_wafer_economics.csv (long)
`record_type,item,period,metric,value,unit,confidence,source_id,notes`

Cited estimates behind the chip-economics primer. `record_type`: `wafer_price` (US$ per 300 mm
TSMC wafer by node; several estimates per node, the chart plots the median) · `wafer_asp` (TSMC
blended average) · `die` (die area, transistor counts) · `model_param` (reticle limits, wafer
diameter, illustrative defect densities, Epoch AI yield and HBM-price assumptions) · `bom`
(estimated H100/B200 unit build cost by component) · `price` (reported selling-price ranges) ·
`hbm_share` (HBM share of unit cost or of AI-chip component spend) · `tsmc_capex` (US$ B by
calendar year; 2026 = guidance midpoint) · `foundry_share` (share of top-10 foundry revenue) ·
`gpu_flops` (dense peak TFLOPS by precision, reused from primer P3 sources). Yield and
cost-per-good-die charts are computed from these parameters with the Poisson/Murphy model
documented in the chart module; TSMC publishes neither wafer prices nor absolute defect densities.

## Chapter 01 — the NVIDIA flywheel (`01_flywheel_ecosystem.csv`, charts in `scripts/charts/ch_flywheel.py`)

### 01_flywheel_ecosystem.csv (long)
`record_type,date,entity,metric,value,unit,confidence,source_id,notes`

NVIDIA's self-reported developer-ecosystem counts used to quantify the developer flywheel:
registered CUDA developers (millions), CUDA downloads, installed base of CUDA GPUs, accelerated
applications, SDKs/models and start-ups. All rows are `reported` company claims from keynotes,
blogs and earnings calls (sources registered by the Phase-1 software agent). Superseded by
`software_ecosystem.csv` where that file carries the same series. The chapter's other charts read
`financials.csv` and `acquisitions_investments.csv` directly.

## Systems, memory/packaging and TCO inputs (agent A3; sources S300–S399)

### system_specs.csv — conventions
`category`: `server-8gpu` | `server-16gpu` | `rack` (one scale-up rack or rack-like unit) | `multi-rack`
(several racks forming one product, e.g. CloudMatrix 384, DGX SuperPOD) | `pod` (pod-scale scale-up
domain, e.g. TPU superpod, Atlas SuperPoD) | `wafer-scale`. `status`: `shipping` | `announced` |
`roadmap` | `eol`. `accelerators_per_system` counts GPU/accelerator **packages** (Vera Rubin NVL72 = 72,
Rubin Ultra Kyber = 144 packages / 576 dies). `fp4_pflops_dense` / `fp8_pflops_dense` are dense peak
(vendor sparse figures halved; Rubin's NVFP4 *inference* figure relies on adaptive compression rather
than 2:4 sparsity and is shown as published). Systems without FP8 (pre-Hopper, Ascend 910C) leave
`fp8_pflops_dense` blank; CloudMatrix 384 BF16 is in `tco_model_inputs.csv`. `power_kw` is IT power of
the unit (rack/system), not facility power. `est_price_usd_m` is always an analyst/reseller estimate
or list price; see `notes` for whose. A row's `confidence` describes its specification columns; price
and power caveats are in `notes`. Notes ending "QA: recheck" were filled from prior knowledge because
the session's web search budget ran out — verify before publication.

### hbm_and_packaging.csv — additions
Extra `record_type` **`hbm_market_size`** (HBM TAM, US$ B). Metric names used: `hbm_generation` →
`pin_speed` (Gb/s), `interface_width` (bits), `stack_bandwidth` (GB/s), `channels`,
`max_stack_capacity` / `jedec_max_stack_capacity` (GB), `max_stack_height` (dies); `hbm_per_gpu` →
`stacks`, `capacity` (GB), `bandwidth` (TB/s); `hbm_market_share` → `share` (pct; `supplier` = SK hynix /
Samsung / Micron); `cowos_capacity` → `capacity` (k wafers/month, year-end run-rate) and
`growth_multiple`; `cowos_allocation` → `wafers` (k wafers/year) and `share` (pct); `packaging_tech`
and `hbm_pricing` use self-describing metric names. CoWoS figures are press-reported analyst
estimates (TSMC does not disclose wafer capacity) and are always plotted hatched.

### tco_model_inputs.csv — conventions
`input` names are snake_case and repeat across systems (`capex_per_rack`, `capex_per_rack_low/high`,
`bom_gpu`, `bom_memory`, `bom_cooling`, `odm_gross_margin_pct`, `rack_power_kw`,
`accelerators_per_rack`, `revenue_per_gpu_hour`, …). Several `capex_per_rack` rows per system are
alternative estimates — `basis` names the estimator and date. `system = All` rows are industry-wide
inputs (PUE, $/kWh, facility capex per MW, hyperscaler server useful lives). Rows from Morgan
Stanley's Aug 2025 "100 MW AI inference factory" model are `speculative` because MS retracted it.

### gpu_rental_prices.csv (one row per observed price point)
`date,gpu,provider,provider_type,pricing_model,usd_per_gpu_hour,confidence,source_id,notes`

`provider_type`: `hyperscaler` | `neocloud` | `marketplace`. `pricing_model`: `on-demand list`,
`on-demand`, `on-demand / spot`, `reserved`. Prices are per GPU-hour (instance price ÷ GPUs).

### depreciation_useful_lives.csv (one row per accounting change)
`company,effective_date,asset_class,useful_life_years,prior_life_years,confidence,source_id,notes`

Useful-life changes for servers/network equipment disclosed in 10-K/S-1 filings; charts draw the
policy as a step function from each `effective_date`.

## Roadmap and software ecosystem (Agent A5; charts in `scripts/charts/ch_roadmap.py` and `ch_software.py`)

### roadmap.csv conventions
- `window_start` / `window_end`: the announced availability window (`YYYY-MM-DD`, `YYYY-MM`, `YYYY-Qn` or `YYYY`;
  "H2 2027" is written `2027-Q3`…`2027-Q4`). For `delayed` rows `window_start` is the **current** (reported) window.
- `notes` tag schedule changes in a parseable form used by `17-roadmap-slips-and-pull-ins`:
  `SLIP from <old> to <new>` and `PULL-IN from <old> to <new>`; spec reductions are tagged `SPEC CUT:`.
- Renamed systems keep the current name with the old one in brackets (e.g. *Vera Rubin NVL72 (formerly
  'Vera Rubin NVL144')*: NVIDIA moved from counting dies to counting GPU packages at CES 2026).
- `confidence` describes the row as a whole: `confirmed` = on an official roadmap/announcement (timing
  as officially stated); `reported` = timing or status rests on press/analyst reporting (e.g. Kyber slip).

### software_ecosystem.csv (long)
- `record_type = time_series`: `metric` ∈ `cuda_registered_developers`, `cuda_downloads_cumulative`,
  `cuda_downloads_in_year`, `cuda_downloads_per_month`, `cuda_accelerated_applications`,
  `cuda_x_sdks_and_models`, `cuda_gpus_installed_base`, `startups_using_platform`, `cuda_release` and
  `rocm_release` (`value` = version number as text, `unit = version`; notes start with `major` or `minor`),
  `pypi_stable_releases` / `pypi_prereleases` (count of PyPI versions first uploaded in that calendar year;
  dev/nightly builds excluded; 2026 = year to date). `date` may be a bare year when the source gives no month.
- `record_type = support_matrix` (as of 2026-11-05): `entity` = framework/runtime, `metric` =
  `support_<vendor stack>` with stacks `nvidia_cuda`, `amd_rocm`, `intel_oneapi_gaudi`, `google_tpu_xla`,
  `aws_neuron`, `huawei_cann`, `qualcomm_cloud_ai`; `value` 0–3 (`unit = level_0_3`):
  **3** native/first-class (upstream in-tree backend with official binaries and CI, or the vendor's own
  framework), **2** supported (upstream backend or vendor-maintained plugin/fork that is documented and
  released), **1** experimental/community/limited (labelled experimental/beta/preview, contributor-only
  validation, stale, or an indirect path such as ONNX export), **0** none. `notes` start with the text label
  and the evidence. The matrix measures breadth across common open-source frameworks, not performance.

### gpu_architecture_cadence.csv (one row per NVIDIA data-center GPU architecture)
`vendor,architecture,flagship_product,announce_event,announce_date,first_availability,availability_basis,status,confidence,source_id,notes`

`first_availability` is the first volume-availability month (mid-quarter placeholder where only a quarter or
half is known; planned dates for `roadmap` rows). Used for `17-nvidia-release-cadence`.

### P1_training_compute.csv (Primer P1; one row per model or scenario)
`model,developer,release_date,params_b,active_params_b,training_tokens_t,training_flop,flop_basis,hardware,gpu_count,gpu_hours_m,confidence,source_id,notes`

`flop_basis`: `reported` (developer figure) | `derived_6nd` (6 × active params × tokens, repo arithmetic) |
`epoch_estimate` (Epoch AI database / data insights; Epoch's own bands are ~3× confident, ~10× likely,
~31× speculative) | `scenario` (repo what-if, never plotted as data). `params_b` / `active_params_b` in
billions (differ for MoE models), `training_tokens_t` in trillions, `gpu_hours_m` in millions of GPU-hours.
Used by charts `P1-frontier-training-compute-log`, `P1-gpus-needed-by-model-size`,
`P1-tokens-per-parameter-overtraining`, `P1-training-run-cost`.

### P1_memory_per_parameter.csv (Primer P1)
`regime,component,bytes_per_param,precision,confidence,source_id,notes` — bytes of GPU memory per model
parameter by regime (FP4/FP8/BF16 inference; mixed-precision training with Adam, ZeRO accounting).
Activations are excluded (they depend on batch and sequence length).

### P2_model_and_gpu_inputs.csv (Primer P2; long)
`record_type,item,metric,value,unit,confidence,source_id,notes`

`record_type`: `model_config` (layers, attention/KV heads, head_dim, params; MLA models use
`kv_cache_elements_per_layer`) | `gpu_spec` (memory_gb, memory_bw_tbs, bf16/fp8/fp4 dense TFLOPS; values
mirror `gpu_product_specs.csv`, reconcile on refresh) | `model_assumption` (inputs of the repo's
roofline serving model: efficiencies, overhead, context, headroom; all `estimate`) | `scenario`
(illustrative tokens per task; all `estimate`). Used by all `P2-*` charts and by `P1-gpus-needed-by-model-size`.

### P2_token_demand.csv (Primer P2; one row per disclosed figure)
`date,entity,metric,value,unit,monthly_tokens_t,basis,confidence,source_id,notes` — publicly disclosed
token volumes (Google, Microsoft, OpenAI API). `value`/`unit` keep the figure as disclosed;
`monthly_tokens_t` normalises it to trillions of tokens per month (quarter ÷ 3; per-minute × 60 × 24 × 30).
`basis`: `reported` | `derived` (normalised or implied from a stated growth rate; drawn hollow).

## Financials, peers and capital deployment (Phase 1, agent A4; sources S400–S484)

### financials.csv — metric catalogue
Long format as above. Money is `USD_B` (US$ billions, 3 decimals where filed in millions); ratios are `pct`.
Annual rows `FY2016`–`FY2026`; quarterly rows `Q1FY23`–`Q2FY27` (plus `Q2FY22`–`Q4FY22` for purchase obligations
and the Q1 FY23 outlook). Metrics:

- Revenue: `revenue_total`, `revenue_data_center`, `revenue_dc_compute`, `revenue_dc_networking` (split disclosed from
  Q1 FY25; FY24 quarters back-calculated from stated y/y growth = `estimate`), `revenue_gaming`,
  `revenue_pro_visualization`, `revenue_automotive`, `revenue_oem_other`. **From Q1 FY27 NVIDIA reports only Data
  Center (`revenue_dc_hyperscale`, `revenue_dc_acie` = AI clouds, industrial, enterprise) and `revenue_edge_computing`
  (= former gaming + ProViz + auto + OEM)**, so gaming/ProViz/auto rows stop at Q4 FY26.
- Margins and costs: `gross_margin_gaap_pct`, `gross_margin_nongaap_pct` (from Q1 FY27 non-GAAP no longer excludes
  stock-based compensation), `gross_margin_nongaap_ex_h20_pct`, `h20_charge`, `inventory_provision`, `rd_expense`,
  `sga_expense`, `operating_expenses_total`, `operating_income`, `net_income`.
- Cash and returns: `operating_cash_flow`, `capex` (purchases of PP&E and intangibles), `free_cash_flow` (= OCF − capex,
  `estimate`, except Q1 FY27 as reported), `share_repurchases`, `dividends_paid`, `shareholder_returns`.
- Supply chain: `inventory`, `purchase_obligations` (inventory purchase + long-term supply and capacity obligations; from
  Q3 FY26 "manufacturing, supply and capacity commitments"), `prepaid_supply_agreements`, `cloud_service_commitments`,
  `ai_cloud_capacity_agreements`, `total_future_commitments`.
- Customers and outlook: `customer_a_pct_revenue` … `customer_d_pct_revenue` (direct customers ≥10% of revenue; letters
  are re-assigned every period), `indirect_customer_a_pct_revenue`, `guidance_next_q_revenue` (midpoint issued **with**
  that period's results, for the following quarter).

**`[recall]` tag in `notes`:** during this pass sec.gov, nvidianews and q4cdn could not be fetched and the shared web
search budget ran out, so rows tagged `[recall]` were transcribed from the cited filing from memory and cross-checked
arithmetically (segments sum to totals; quarters sum to filed annual totals) but not re-read online. Rows noting
"checked via web search 2026-11-05" were verified this session. QA should re-verify `[recall]` rows first.

### peer_financials.csv (long)
`company,period,period_type,period_end,metric,value,unit,confidence,source_id,notes`

Same conventions as `financials.csv` with a leading `company` column. Calendar-year periods are `CY2024`; company fiscal
years keep the company's own label (`FY2025`) with the true `period_end`. Metrics: `revenue_data_center` (AMD,
Marvell), `revenue_ai_semiconductor` (Broadcom), `revenue_dcai` (Intel; scope changed in 2024 and 2025 — not
like-for-like), `hpc_share_of_revenue_pct` (TSMC), `rd_expense`, `capex` (Alphabet, Amazon, Meta, Microsoft, Oracle;
2025–2026 outlook rows are `reported`).

### acquisitions_investments.csv — conventions
Schema above. `status`: `closed` | `announced` | `active` (ongoing commitment) | `terminated` | `superseded` |
`closed (wound down 2015)`. `amount_usd_m` is blank (not 0) when undisclosed. `layer_strengthened` uses the two-digit
layer number (`02`–`13`); AI labs and other demand-side stakes map to `13`, neoclouds to `12`, power/data-centre
developers to `08`.

### investments_in_customers.csv
`counterparty,date,nvidia_investment_usd_b,investment_basis,customer_compute_commitment_gw,customer_commitment_usd_b,commitment_description,confidence,source_id,notes`

One row per NVIDIA equity commitment to a company that has also announced a large compute plan (input for the
circular-financing bubble chart `12-investments-in-customers-bubble`). `investment_basis` as `amount_basis` above;
a commitment described as an LOI that was later replaced is treated as superseded by the chart.

## Competition, market share and benchmarks (agent A6; sources S600–S699, charts in `scripts/charts/ch_competition.py`, `ch_mlperf.py`, `ch_market.py`)

### competitor_matrix.csv — conventions
13 entities (NVIDIA reference rows plus AMD, Google TPU, AWS Trainium, Microsoft Maia, Meta MTIA,
Broadcom, Marvell, Intel, Huawei, Qualcomm (public information only), Cerebras, Groq). `dimension`
for `dimension_type = layer` is the layer number plus a short name (`02 Accelerator silicon` …
`13 Ecosystem, GTM & capital`); for `capability` it is one of nine radar axes (Peak compute, Memory
capacity & bandwidth, Scale-up fabric, Scale-out networking, Software ecosystem, Rack-scale systems,
Supply access (CoWoS/HBM), Cost/TCO, Merchant availability). Scores 0–5 are the repo's judgement
(`confidence = speculative` on every row); `notes` record the confidence of the underlying evidence.
NVIDIA rows are the reference (`verdict_vs_nvidia = parity`).

### mlperf_results.csv — conventions
Built from the MLCommons results repositories (primary data, fetched via git): Inference v4.0–v6.1
and Training v4.1–v6.0. `metric`: `throughput` (inference, `unit` tokens/s, samples/s or queries/s;
`per_accelerator_value` = value / accelerator_count), `time_to_train` (minutes; computed by the repo
from the result logs with MLPerf scoring — olympic average × `scaling.json` factor — and checked
against published headline numbers, e.g. 27.3 min on 2,496 GB200 for Llama 3.1 405B in v5.0),
`submitting_organizations`, `performance_results_by_accelerator_vendor` (inference, closed, power
results excluded) and `results_by_accelerator_vendor` (training). `notes` start with
`series=same-hardware…` (same NVIDIA-submitted system across rounds) or `selection=…` (how the row
was picked) and always state `category=available|preview`. Accelerator names are normalised
(`NVIDIA GB300`, `AMD MI355X`, …). v6.0 training results that are byte-identical copies of v5.1
results were dropped.

### market_share.csv (long)
`year,segment,entity,metric,value,unit,confidence,source_id,notes`

`year`: calendar year (`2026E` = estimate) or quarter (`2025-Q4`; Broadcom fiscal quarters mapped
to the calendar quarter in which they end). `segment`: `ai_datacenter_vendor_revenue` (US$ B, NVIDIA
fiscal year used as proxy for the prior calendar year), `custom_asic_partner_revenue` (Broadcom
quarterly AI revenue), `ai_accelerator_revenue_share` and `merchant_vs_custom` (pct; repo
calculation = vendor AI data-center revenue / sum across vendors, custom ASICs valued at
design-partner revenue, China domestic excluded), `datacenter_gpu_shipments` /
`custom_asic_shipments` / `*_commitments` (units or GW), `ai_backend_network_switch_share`
(InfiniBand vs Ethernet, pct). Third-party estimates that could not be re-verified in this session
are `speculative` and say "as recalled" in `notes` — verify before publication.

### inference_benchmarks.csv (long)
`benchmark_suite,date,model,system,vendor,accelerators,precision,interactivity_tok_s_per_user,throughput_tok_s_per_gpu,cost_usd_per_m_tokens,confidence,source_id,notes`

Throughput-vs-interactivity points. `benchmark_suite` values: `SemiAnalysis InferenceX (Pareto
frontier, no speculative decoding|with MTP speculative decoding)` (frontier points per system and
precision from the InferenceX public-API snapshot; throughput = total input+output tokens/s per GPU,
interactivity = median tok/s/user), `SemiAnalysis InferenceX (history, same hardware and config)`
(fixed concurrency and parallelism over time; `notes` carry `series=`), `NVIDIA TensorRT-LLM perf
overview (max-throughput, trtllm-bench)` (output tokens/s per GPU at maximum load by release; no
interactivity), `NVIDIA TensorRT-LLM tech blog …` and `SemiAnalysis InferenceX article …` (single
published data points). `cost_usd_per_m_tokens` = InferenceX owner TCO ($/GPU-hr, S622) × 10⁶ /
(tokens/s × 3,600), i.e. per million total tokens unless `notes` say output tokens; it is an
estimate even when the throughput is measured. `accelerators` = GPUs in the serving instance
(aggregated: tensor-parallel size; disaggregated: prefill + decode GPUs).

### network_topology_estimates.csv (long; agent A2, connectivity)
`scenario,cluster_gpus,gbps_per_gpu,switch_example,switch_radix_ports,port_gbps,planes,tiers,metric,value,unit,confidence,source_id,notes`

Repo calculations (`confidence` = `estimate`) for non-blocking (1:1) rail-optimized fat trees,
back-end compute fabric only (front-end, storage and out-of-band networks excluded; one NIC port per
GPU per plane). Three record groups, told apart by `scenario`/`metric`:
- `fat-tree capacity, radix R` · `max_gpus_nonblocking`: 2 tiers = R²/2, 3 tiers = R³/4.
- `400G|800G per GPU, 2-tier|3-tier` · `optics_nic_side`, `optics_leaf_downlink`, `optics_leaf_spine`,
  `optics_spine_core`, `optics_total_pluggable` (modules per GPU, all links optical, twin-port
  2×400G / 2×800G modules on switches), `optical_port_ends` (2 per link per tier = module count if
  every module were single-port) and `optics_total_cpo_switches` (switch-side pluggables removed).
- `100k GPUs: …` · `switches_leaf|spine|core|total`, `transceivers_total`, `switch_hops_max`:
  leaf = N/(R/2), spine = N/(R/2) (3 tiers) or N/R (2 tiers), core = N/R, per plane, rounded up.
Rail optimization changes which leaf a NIC lands on, not the counts.

### optics_power_estimates.csv (wide; agent A2, connectivity)
`technology,example,port_gbps,year,watts_per_port,watts_per_800g,pj_per_bit,basis,confidence,source_id,notes`

Optical-I/O power per port: DSP pluggables, linear pluggables (LPO), co-packaged optics (CPO) and a
copper reference. `pj_per_bit` = W ÷ (Gb/s) × 1000. Vendor CPO claims (NVIDIA "3.5×", Broadcom
"~70% lower") are converted to watts against the stated pluggable baseline and marked `estimate`;
`basis` says which.

## Layer 02 — GPU silicon, strategy pages (`l02_*.csv`; charts in `scripts/charts/ch_l02_strategy.py`; sources S2500–S2999)

### l02_replication_costs.csv (one row per cost reference point)
`item,entity,category,year,value_usd_b,basis,confidence,source_id,notes` — what it costs to play in AI silicon, in US$ B:
single-chip design (NRE) estimates by node (`design_cost`, IBS series via Silicon Analysts / Tom's Hardware, flagged as
possibly high), start-up capital raised (`startup_capital`), acquisitions and licence deals (`acquisition`), program
spend (`program_cost`, e.g. NVIDIA's CEO estimate for Blackwell) and annual company R&D (`annual_rd`, reused from
`peer_financials.csv` / `financials.csv`). Used by `02-chip-program-cost-ladder`.

### l02_chip_startups.csv (one row per company)
`company,architecture,latest_event,event_date,amount_usd_b,value_usd_b,value_basis,status,confidence,source_id,notes` —
latest disclosed valuation, IPO value or deal value of AI-chip start-ups (public information only). `value_basis` says
what the number is (IPO pricing, round valuation, upfront deal value, reported offer); values are not like-for-like.
`status`: `public` | `private` | `acquired` | `licensed to NVIDIA`. Used by `02-chip-startup-valuations`.

### l02_rubin_spec_revisions.csv (long)
`product,metric,spec_version,value,unit,date,confidence,source_id,notes` — Rubin per-GPU, NVL72-rack and HGX NVL8
specifications at the CES 2026 launch (`launch`) and on the revised product pages of Sep–Oct 2026 (`revised`), with
AMD MI455X reference values (`launch` = AMD's published figures). Used by `02-rubin-spec-revision`.

### l02_custom_silicon_revenue.csv (long)
`calendar_quarter,company,fiscal_period,metric,value,unit,basis,confidence,source_id,notes` — recent custom-silicon
revenue points that extend `market_share.csv`: Broadcom AI semiconductor revenue for fiscal Q2–Q4 2026 (`basis`:
`reported` | `derived` (repo arithmetic from reported growth) | `guidance`) and MediaTek's reported 2026 AI-ASIC revenue
target. `calendar_quarter` = calendar quarter in which the fiscal quarter ends (same convention as `market_share.csv`).
Used with `market_share.csv` and `financials.csv` by `02-broadcom-ai-vs-nvidia-dc`.
