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

## Layer 04 — CPU (Grace, Vera), CORE (`l04_*.csv`, charts in `scripts/charts/ch_l04_core.py`; sources S4000–S4499)

### l04_host_attach.csv (wide, one row per system)
`vendor,system,year,status,accelerator,accelerators_per_system,cpus_per_system,cpu,cores_per_cpu,threads_per_core,host_threads_per_system,host_memory_gb_per_system,hbm_gb_per_accelerator,host_link,host_link_gbs_bidir_per_accelerator,confidence,source_id,notes`

How the host CPU is attached to the accelerators in each system: CPU sockets, cores and hardware threads
(`host_threads_per_system` = sockets × cores × threads per core; for AWS rows it is the vCPU count from the
Neuron docs because AWS does not name the host CPU), CPU-attached memory per system (DDR or LPDDR5X; AWS GiB
treated as GB) and the CPU↔GPU link bandwidth **available to each accelerator**, both directions combined: a
PCIe x16 link per GPU, or an NVLink-C2C link divided by the GPUs that share it (GB200/GB300: 900 GB/s ÷ 2;
Vera Rubin: 1,800 GB/s ÷ 2 — repo arithmetic). DGX system-memory sizes were entered from the datasheets as
recalled and carry `[recall; re-verify]` in `notes`. Ratios that overlap `system_specs.csv` (sockets per system)
are read from that file by the charts where the system exists there.

### l04_scenarios.csv (long)
`record_type,item,metric,value,unit,confidence,source_id,notes`

Inputs for two worked examples and one projection band. `data_loading`: NVIDIA's DGX-2 ResNet-50 case study
(synthetic-data ceiling, CPU-preprocessing and DALI throughput in images/s; host cores; list price).
`kv_offload`: the illustrative 32,768-token Llama 3.1 70B conversation with an FP8 KV cache (model shape comes
from `P2_model_and_gpu_inputs.csv`; link rates from `interconnect_specs.csv` and `l04_host_attach.csv`; recompute
uses H100 dense FP8 from `gpu_product_specs.csv` at P2's 50 % compute efficiency). KV bytes = 2 × layers ×
KV heads × head_dim × bytes × tokens; recompute FLOPs = 2 × params × tokens + 2 × layers × tokens² × heads ×
head_dim (causal attention). `ratio_projection`: reported 2026 CPU:GPU ratio projections for agentic AI servers
(Intel earnings call, TrendForce), drawn as a band.

## Layer 04 strategy — CPU competition, roadmap and value chain (`l04_*.csv`, charts in `scripts/charts/ch_l04_strategy.py`; sources S4500–S4547)

### l04_cpu_market_share.csv (long, one row per tracker data point)
`period,period_date,tracker,metric,scope,entity,value,unit,basis,confidence,source_id,notes`

Server CPU share as reported by Mercury Research, UBS, TrendForce and IDC (via press; trackers differ in scope, so
series are never mixed). `metric`: `unit_share` (share of all server CPU units), `revenue_share` (IDC share of
server *system* revenue, inflated by GPU racks), `x86_unit_share` / `x86_revenue_share` / `x86_normalized_share`
(AMD vs Intel only). `basis`: `actual` | `forecast`. `period_date` is a plotting mid-point.

### l04_cpu_verdicts.csv (long, competitor × dimension)
`competitor,product_basis,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes`

Repo verdicts (all `speculative`) for ten rival CPUs against NVIDIA Vera on five dimensions (cores per socket, memory
bandwidth, CPU-GPU link & coherence, software / ISA, merchant availability). `verdict_vs_nvidia` as in
`competitor_matrix.csv` (`leads` = rival ahead of NVIDIA). Feeds `04-cpu-competitor-heatmap`.

### l04_cpu_roadmap_specs.csv (one row per CPU generation)
`vendor,product,isa,core_type,year,status,max_cores,memory_bw_gbs,cpu_gpu_link,confidence,source_id,notes`

Max cores and peak memory bandwidth per socket by launch year, 2022–2028, for NVIDIA, AMD, Intel, AWS, Microsoft,
Google, Ampere, Arm, Huawei, Fujitsu and Qualcomm (public information only). Diamond Rapids values are derived from
Intel's "+50% cores, 2× Granite Rapids bandwidth" (`reported`); Qualcomm's 80-core figure is an unconfirmed press
report with a placeholder year (`speculative`). `status` as in `roadmap.csv`. Feeds the two roadmap charts.

### l04_cpu_deals.csv (one row per CPU-related deal)
`announce_date,close_date,acquirer,target,deal_type,value_usd_m,value_basis,what_was_bought,status,confidence,source_id,notes`

Server-CPU and CPU-adjacent transactions 2015–2025 (Annapurna, Arm, NUVIA, Ampere, Alphawave, Intel stake, Rivos,
Ventana). `value_usd_m` blank when undisclosed. Feeds `04-cpu-deal-values`.

### l04_cpu_value_chain.csv (long)
`record_type,item,component,metric,value,unit,confidence,source_id,notes`

`record_type = rack_bom`: estimated cost build-up of one Vera Rubin NVL72 rack (US$ M) from Morgan Stanley figures
(also in `tco_model_inputs.csv`), with a **repo split** of the memory line into HBM4 and LPDDR5X SOCAMM inferred
from Morgan Stanley's $7.8M vs $6.7M (CSP buys SOCAMM directly) scenarios; "Other" is the remainder to the total.
`record_type = royalty_rate`: analyst-estimated Arm royalty ranges as % of chip selling price (Armv8, Armv9, CSS);
Arm does not disclose rates. All rows `estimate`.

## Layer 02 CORE — GPU silicon mechanisms (`l02_*` core files, charts in `scripts/charts/ch_l02_core.py`; sources S2000–S2025)

### l02_gpu_microarchitecture.csv (one row per NVIDIA flagship GPU)
`product,architecture,year,sms,tensor_cores,tensor_cores_per_sm,dense_16bit_flops_per_clk_per_sm,register_file_kb_per_sm,l1_smem_kb_per_sm,l2_mb,tmem_kb_per_sm,new_tensor_formats,confidence,source_id,notes`

Enabled SMs and tensor cores per package (V100 → Rubin), per-SM 16-bit matrix FLOPs per clock where NVIDIA
publishes it (V100–H100), and on-chip memory sizes. Blank = not disclosed. Rubin rows come from NVIDIA's
July 2026 architecture blog as reported by the press (`reported`). Used by `02-sms-and-throughput-per-sm`
together with dense TFLOPS from `gpu_product_specs.csv`.

### l02_memory_hierarchy.csv (long: product × memory level)
`product,level,level_order,capacity_mb,bandwidth_tbs,basis,confidence,source_id,notes`

Capacity (MB; 1 GB = 1,000 MB) and aggregate bandwidth per GPU for registers, L1/shared memory, L2, HBM and
the NVLink domain (H100 SXM, B200, Rubin). `basis`: `spec` | `measured` (Chips and Cheese microbenchmarks) |
`derived` (repo arithmetic: register bandwidth = SMs × 1,536 B/clock, L1 = SMs × 128 B/clock, at the clock
implied by the dense BF16 peak; always `estimate`). NVLink-domain bandwidth is bidirectional per GPU.

### l02_compute_units.csv (one row per compute unit or chip)
`unit,category,scope,precision,flops_per_clock,basis,confidence,source_id,notes`

Peak dense 16-bit matrix FLOPs per clock for a CPU core (with/without Intel AMX), NVIDIA SMs (V100–H100), Google
TPU matrix units (128×128 and 256×256 systolic arrays) and whole chips. `category`: `CPU` | `GPU` | `ASIC`;
`scope`: `one core or SM or array` | `whole chip`. Whole-chip rows multiply unit counts (repo arithmetic).

### l02_number_formats.csv (one row per number format)
`format,total_bits,exponent_bits,mantissa_bits,block_size,scale_format,effective_bits_per_value,max_normal_value,first_nvidia_tensor_support,confidence,source_id,notes`

FP32 → NVFP4 with block-scaling overhead (`effective_bits_per_value`: MX formats add 8 bits per 32 values,
NVFP4 adds 8 bits per 16 values). Used by `02-decode-throughput-by-precision`, which also reads the Llama 3.1
70B configuration and serving-model efficiencies from `P2_model_and_gpu_inputs.csv` (batch 64 is a chart
constant). `02-multi-die-silicon-cost` reads wafer price, defect density and reticle limit from
`P5_wafer_economics.csv`.

## Layer 03 — memory, packaging and supply chain, strategy pages (`l03_*.csv` below; charts in `scripts/charts/ch_l03_strategy.py`; sources S3500–S3999)

### l03_rack_memory.csv (one row per rack-scale system and spec version)
`system,vendor,accelerator,accelerators,spec_version,status,hbm_capacity_tb,hbm_bandwidth_tbs,basis,confidence,source_id,notes` —
aggregate HBM per rack-scale unit. Vera Rubin NVL72 appears twice (`launch (CES 2026)` and `revised (Sep-Oct 2026)`). Rows
marked "repo calc" in `basis` multiply per-chip vendor figures by the accelerator count. CloudMatrix 384 spans 16 racks;
the Ironwood row is one 64-chip cube. Used by `03-rack-hbm-after-rubin-revision`.

### l03_memory_verdicts.csv (long: challenger x dimension)
`competitor,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes` — repo verdicts of each challenger's
position versus NVIDIA's 2026 flagship on six memory-system dimensions (`leads` | `parity` | `behind` | `different`, from the
challenger's point of view). `cell_label` is the short text printed in the heatmap. Used by `03-memory-supply-verdict-heatmap`.

### l03_hbm_share_2026.csv (long)
`period,supplier,share_pct,kind,confidence,source_id,notes` — HBM revenue share by supplier for 2026 quarters (Counterpoint),
extending the 2022–2025 rows in `hbm_and_packaging.csv`; `kind` = `actual` | `forecast` (Samsung Q4 2026, KB Securities).
Used by `03-hbm-share-shift-2025-2026`.

### l03_cowos_outlook.csv (one row per year end)
`year_end,low_k_wpm,mid_k_wpm,high_k_wpm,kind,confidence,source_id,notes` — TSMC CoWoS capacity in thousand wafers per month:
low / midpoint / high of press-reported analyst estimates; `kind` = `estimate` (capacity in place) | `projection` (reported
plans, 2027–2028). TSMC does not disclose these figures. Used by `03-cowos-capacity-outlook-2028`.

### l03_memory_roadmap.csv (one row per accelerator)
`vendor,product,year,status,capacity_gb,bandwidth_tbs,variant,confidence,source_id,notes` — memory per accelerator package,
2024–2028. `variant` = `base` | `launch-target` (Rubin's 22 TB/s CES figure) | `alt-report` (Rubin Ultra 768 GB report).
Trainium4 is a repo estimate from AWS multipliers. Used by `03-memory-roadmap-by-vendor`.

### l03_value_chain_margins.csv (one row per company or estimate)
`company,role,period,metric,margin_pct,confidence,source_id,notes` — latest margin by link of the AI-rack supply chain;
`metric` = `gross` | `operating`. Periods differ by company (see `period`); ODM rows are Morgan Stanley rack-level
estimates. Used by `03-value-chain-margins`.

## Layer 03 — memory, packaging and supply chain, core pages (`l03_memory_scenarios.csv`, `l03_cowos_geometry.csv`; charts in `scripts/charts/ch_l03_core.py`; sources S3000–S3499)

### l03_memory_scenarios.csv (one row per serving scenario)
`scenario,model,weight_bytes_per_param,kv_bytes_per_element,users,context_tokens,confidence,source_id,notes` — repo serving
scenarios (all `estimate`). Model shapes (layers, KV heads, head dim, MLA latent size) come from `P2_model_and_gpu_inputs.csv`;
KV cache per token = 2 × layers × KV heads × head dim × bytes (grouped-query attention) or latent size × layers × bytes (MLA).
Used by `03-hbm-needed-vs-per-gpu-hbm`; `03-decode-ceiling-vs-batch-32k` uses the same model shapes with a 32k context and
90% usable HBM.

### l03_cowos_geometry.csv (one row per NVIDIA package)
`product,package_tech,compute_dies,hbm_stacks,interposer_reticles_low,interposer_reticles_high,confidence,source_id,notes` —
repo assumptions of each package's interposer area as a multiple of the 858 mm² reticle (NVIDIA does not publish interposer
sizes), bounded by TSMC's CoWoS-S/-L limits in `hbm_and_packaging.csv`. `03-packages-per-cowos-wafer` counts how many
rectangles (aspect 1.25, 0.2 mm spacing) fit inside a 300-mm wafer with 3 mm edge exclusion, before yield loss.

## Layer 06 CORE — scale-out networking mechanisms (`l06_*` core files; charts in `scripts/charts/ch_l06_core.py`; sources S6000–S6031)

### l06_core_inputs.csv (long)
`record_type,item,metric,value,unit,confidence,source_id,notes` — inputs for the layer-06 CORE charts:
- `tail_latency_model`: illustrative parameters for `06-step-time-vs-tail-latency` (exposed-communication share of a step,
  slow-flow delay factor, slow-flow fractions, flows per collective, a $/GPU-hour value). Expected step time =
  (1−m) + m·[1 + (k−1)·(1−(1−p)^F)] for exposed-communication share m, delay factor k, slow-flow fraction p and F flows.
  All `estimate` (repo model).
- `cpo_scenario`: three counting bases (repo twin-port module count with NVIDIA's 3.5× and 2026 5× claims; Jensen Huang's
  "six 30 W transceivers per GPU" framing) as modules and watts per GPU plus the CPO power factor; the chart multiplies by
  100,000 GPUs. NIC-side modules stay pluggable.
- `network_cost_share`: published or derived estimates of the network's share of AI spend, each with its scope in `item`
  (whole data center vs cluster hardware vs vendor revenue mix vs optics only).
- `spectrum_x_claim`: NVIDIA's effective-throughput claims for Spectrum-X vs standard Ethernet (vendor claims, `reported`).

### l06_allreduce_traffic.csv (generated grid)
`algorithm,n_gpus,bytes_sent_per_gpu_x_message,formula,confidence,source_id,notes` — bytes each GPU sends per all-reduce
as a multiple of the message size: ring 2(N−1)/N vs SHARP in-network reduction 1 (bandwidth term only; latency ignored).

### l06_cluster_examples.csv (one row per disclosed cluster)
`cluster,operator,year,gpus,gpu_type,fabric,fabric_family,gbps_per_gpu,status,confidence,source_id,notes` — large AI
clusters with a disclosed back-end fabric. `fabric_family`: `infiniband` | `spectrum-x` | `ethernet-other` | `mixed`.
`status`: `operating` | `reported` (expansion reported, not verified) | `announced` (target). Rows with no disclosed GPU
count (e.g. Microsoft Fairwater) are kept for the text and skipped by the chart.

## Layer 07 STRATEGY — NIC/DPU competition, deals, roadmap and value chain (`l07_*` strategy files; charts in `scripts/charts/ch_l07_strategy.py`; sources S7500–S7536)

### l07_competitor_verdicts.csv (long, competitor × dimension)
`competitor,product_basis,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes` — repo verdict of
each rival's best NIC/DPU against NVIDIA's nearest equivalent (SuperNIC vs NIC, DPU vs DPU) on six dimensions (bandwidth
per device, programmability, AI-transport features, merchant availability, ecosystem/software, deployed scale).
`verdict_vs_nvidia`: `leads` | `parity` | `behind` | `different`. Judgement rows are `speculative`. Feeds
`07-nic-dpu-competitor-heatmap`.

### l07_dpu_nic_deals.csv (one row per deal)
`announce_date,close_date,acquirer,target,deal_type,value_usd_m,value_basis,what_it_became,status,confidence,source_id,notes`
— NIC/DPU-related acquisitions 2014–2025 (Tilera, Annapurna, EZchip, Mellanox, Excelero, Pensando, Fungible, Enfabrica).
`value_basis`: `disclosed` | `reported` | `up-to` | `undisclosed`. Feeds `07-dpu-nic-deal-values`.

### l07_speed_tier_arrival.csv (one row per vendor × speed tier)
`vendor,speed_tier_gbps,product,category,year,status,confidence,source_id,notes` — the year each vendor's fastest NIC/DPU
first reached a per-device speed tier (first volume, or sampling where `status` = `sampling`). Feeds
`07-nic-speed-tier-arrival`.

### l07_nic_dpu_roadmap.csv (one row per product)
`vendor,product,category,date,status,bandwidth_gbps,confidence,source_id,notes` — NIC/SuperNIC/DPU availability 2024–2028
by vendor; `date` is an approximate month of availability (parts already in market are pinned to 2024-01); blank
`bandwidth_gbps` = not disclosed. `status`: `shipping` | `announced` | `sampling` | `roadmap`. Feeds
`07-nic-dpu-roadmap-by-vendor`.

### l07_rack_nic_dpu_content.csv (one row per rack × component)
`rack,component,units_low,units_high,unit_price_low_usd,unit_price_high_usd,rack_price_usd_m,confidence,source_id,notes` —
repo estimate (all `estimate`) of SuperNIC and DPU dollars per NVL72 rack. SuperNIC count = one per GPU (vendor specs);
DPU count 18–36 (one or two per compute tray, assumption); unit prices are repo assumptions anchored on BlueField-3 retail
listings ($1.9K–$6.0K, S7531/S7532); rack prices are HSBC (GB200) and Morgan Stanley (GB300, Vera Rubin) estimates. Feeds
`07-nic-dpu-content-per-rack`.

### l07_private_companies.csv (one row per funding mark or exit)
`company,segment,date,event,raise_usd_m,valuation_usd_m,valuation_basis,lead_or_buyer,status,confidence,source_id,notes` —
last disclosed post-money valuations of private storage and data-path companies (VAST Data, DDN, WEKA, Hammerspace,
Xsight Labs) and exit prices of DPU/NIC start-ups (Pensando, Enfabrica, Fungible). `status`: `private` | `acquired`.
Feeds `07-ai-storage-and-dpu-valuations`.

## Layer 07 CORE — DPU, SuperNIC, storage and security mechanisms (`l07_*` core files; charts in `scripts/charts/ch_l07_core.py`; sources S7000–S7028)

### l07_bluefield_generations.csv (one row per BlueField generation)
`generation,product,year,status,arm_cores,core_type,dpu_memory_gb,network_gbps,host_pcie,claimed_cpu_core_equivalent,compute_vs_bluefield3,confidence,source_id,notes`
— Arm cores, on-board memory, maximum port speed (Gb/s per direction) and host PCIe for BlueField-1 to -4;
`claimed_cpu_core_equivalent` and `compute_vs_bluefield3` are NVIDIA claims. Feeds `07-bluefield-generations`.

### l07_infra_tax.csv (one row per estimate)
`estimate,basis,share_low_pct,share_high_pct,cores_freed,cores_total,confidence,source_id,notes` — published estimates of the
share of host CPU cores/cycles consumed by infrastructure software without offload (three of four are NVIDIA's). Feeds
`07-infrastructure-tax-estimates`.

### l07_offload_model.csv (one row per model input)
`input,value,unit,basis,confidence,source_id,notes` — inputs for the repo's estimate of the annual dollar value of DPU offload
per Vera Rubin compute tray (freed Vera cores at an estimated $5k per CPU over a 5-year life; best-case power saving;
1–3% GPU-time scenario at $4.99/GPU-hour). Formulas in `offload_values()`. Feeds `07-offload-value-per-tray`.

### l07_nic_per_gpu.csv (one row per system)
`system,vendor,year,status,accelerator,nic,nics_per_accelerator,nic_port_gbps,scale_out_gbps_per_accelerator,unit,accelerators_per_unit,host_cpu,host_cpus_per_unit,confidence,source_id,notes`
— scale-out NIC bandwidth per accelerator and the host CPUs per server/tray (names match `cpu_specs.csv`). Feeds
`07-gpudirect-host-memory-load` (host DRAM traffic needed to stage inbound NIC data = 2 × NIC GB/s, divided by the host
CPUs' peak memory bandwidth from `cpu_specs.csv`).

### l07_storage_paths.csv (one row per data path)
`system,path,bandwidth_gbs,basis,confidence,source_id,notes` — NVIDIA's DGX-2 measurements of storage-to-GPU bandwidth with
and without GPUDirect Storage (2019–20). Feeds `07-gds-bandwidth-dgx2`.

### l07_checkpoint_model.csv (long)
`record_type,item,value,unit,confidence,source_id,notes` — `model` (parameter counts), `bandwidth` (reference storage
bandwidths) and `cluster` (Llama 3 failure statistics). Checkpoint size = parameters × 14 bytes (BF16 weights + FP32 master
weights + Adam momentum + variance, from `P1_memory_per_parameter.csv`). Feeds `07-checkpoint-write-time`.

### l07_kv_tiers.csv (long)
`tier,label,value,unit,scope,confidence,source_id,notes` — one-way bandwidth of each KV-cache tier (G1 HBM, G2 CPU memory,
G3 local SSD, G3.5 BlueField-4 context storage, G4 shared storage) and the model inputs (`tier` = `model`) used to size a
128K-token Llama 3.1 70B FP8 KV cache and the recompute estimate. Feeds `07-kv-cache-reload-by-tier`.

### l07_cc_overhead.csv (one row per model × metric)
`study,gpu,model,metric,tee_off,tee_on,overhead_pct,confidence,source_id,notes` — H100 confidential-computing overhead from
Zhu et al. (arXiv 2409.03992). Feeds `07-confidential-computing-overhead`.

## Layer 06 — scale-out networking, strategy pages (`l06_*` strategy files; charts in `scripts/charts/ch_l06_strategy.py`; sources S6500–S6999)

### l06_competitor_verdicts.csv (long)
`competitor,product_basis,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes` — repo verdict
(`leads` | `parity` | `behind` | `different`) for eight scale-out rivals (Broadcom, Arista, Cisco, Marvell, white-box ODMs,
UEC ecosystem, Google, AWS) against NVIDIA InfiniBand + Spectrum-X on six dimensions (switch radix/bandwidth, congestion
control/tail latency, NIC co-design, openness, ecosystem/software, share). All rows `speculative` (analyst judgement on cited
facts). Feeds `06-scale-out-competitor-heatmap`.

### l06_switch_generations.csv (one row per switch ASIC)
`vendor,product,class_tbps,fabric,announce_date,ship_date,ship_basis,status,confidence,source_id,notes` — announcement and
first-shipment dates for 51.2T and 102.4T Ethernet switch generations (Broadcom, NVIDIA, Marvell, Cisco) and Quantum-X800.
`ship_date` is blank when not disclosed; Cisco G300 uses the H2 2026 midpoint (planned). Feeds `06-switch-generation-race`.

### l06_scale_out_per_accelerator.csv (one row per system)
`vendor,system,accelerator,year,nic,nics_per_accelerator,gbps_per_nic,scale_out_gbps_per_accelerator,status,confidence,source_id,notes`
— back-end NIC bandwidth per accelerator (Gb/s, one direction) for NVIDIA H100 → Feynman (roadmap), AMD Helios and AWS EFA
instances (instance bandwidth ÷ accelerators). Feeds `06-scale-out-bandwidth-per-accelerator`.

### l06_networking_vendor_revenue.csv (one row per vendor figure)
`entity,category,period,metric,value_usd_b,basis,confidence,source_id,notes` — latest annual revenue tied to AI networking:
NVIDIA networking (FY2026 and Q2 FY2027 × 4; includes NVLink switches), Broadcom AI semiconductors (includes custom XPUs),
Innolight and Eoptolink (CY2025), Arista's 2026 AI target and Credo (FY2026). Not like-for-like; see `notes`. Feeds
`06-networking-value-pool-by-vendor`.

### l06_networking_deals.csv (one row per deal)
`announce_date,close_date,acquirer,target,deal_type,value_usd_m,value_basis,what_was_bought,status,confidence,source_id,notes`
— networking, optics and interconnect deals 2019–2026 by NVIDIA and peers (`deal_type` as in `acquisitions_investments.csv`).
Feeds `06-networking-deal-values`. The `06-networking-attach-per-compute` chart reads `financials.csv` directly
(networking ÷ compute by quarter).

## Layer 05 strategy — scale-up competition, standards, value chain (`l05_*.csv`, charts in `scripts/charts/ch_l05_strategy.py`; sources S5500–S5528)

### l05_scale_up_verdicts.csv (long, competitor × dimension)
`competitor,product_basis,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes`

Repo verdicts of six scale-up rivals (AMD Helios, Google TPU ICI + OCS, AWS Trainium NeuronLink, Huawei UnifiedBus, UALink, Ethernet scale-up) against NVIDIA Vera Rubin NVL72 on five dimensions (bandwidth per accelerator, domain size, latency & semantics, openness, maturity / shipping). `verdict_vs_nvidia` is from the rival's side: `leads` | `parity` | `behind` | `different`. `cell_label` is the short fact printed in the heatmap.

### l05_standards_timeline.csv (one row per milestone)
`track,owner,model,milestone,milestone_type,date,status,confidence,source_id,notes`

Milestones for NVLink 5/6, NVLink Fusion, UALink, Ethernet scale-up (SUE/ESUN), Ultra Ethernet and PCIe 6.0/7.0. `milestone_type`: `formation` | `announce` | `spec` | `first_silicon` | `first_product`. `status`: `done` | `expected`; expected dates are mid-window placeholders for trade-press or analyst windows (see `notes`).

### l05_value_chain.csv (one row per company metric)
`company,role_in_scale_up,metric,period,period_end,value_usd_b,basis,confidence,source_id,notes`

Quarterly or annual revenue of companies that capture scale-up dollars (NVIDIA networking, Amphenol, Credo, Astera Labs, Marvell/XConn). `basis`: `disclosed` | `derived` (repo arithmetic on disclosed ratios) | `guidance midpoint` | `company target`. Scopes differ: NVIDIA networking includes InfiniBand, Ethernet and NICs; Amphenol's AI datacom line is derived from management's stated shares.

### l05_deals.csv (one row per deal)
`announce_date,close_date,buyer_or_lead,target,deal_type,value_usd_m,value_basis,scale_up_relevance,status,confidence,source_id,notes`

Interconnect-related acquisitions, strategic stakes, acquihires and start-up rounds, 2019–2026 (Mellanox, Intel and Marvell stakes, ZT Systems, Celestial AI, Alphawave, Enfabrica, XConn, Ayar Labs, Lightmatter, Upscale AI). `deal_type`: `acquisition` | `strategic-investment` | `acquihire-license` | `funding-round`. XConn's value is the cash portion only.

## Layer 09 strategy — CUDA competition, history and software M&A (`l09_*.csv`, charts in `scripts/charts/ch_l09_strategy.py`; sources S9500–S9538)

### l09_software_deals.csv (one row per AI-software deal or reference point)
`record_type,announce_date,close_date,acquirer,target,deal_type,category,value_usd_m,value_basis,what_was_bought,status,confidence,source_id,notes`

`record_type = deal`: compiler, model-optimisation, orchestration and developer-tool acquisitions by NVIDIA, AMD,
Qualcomm and (for comparison) Red Hat, 2008–2026. NVIDIA rows mirror `acquisitions_investments.csv` (several are
`[recall]`); NVIDIA–Groq (inference-silicon licence) and hardware/systems deals (ZT Systems, Enosemi) are excluded.
`value_usd_m` blank when undisclosed; `value_basis` = disclosed | reported | undisclosed. `record_type = reference`:
Modular's Series C valuation and total capital raised, used to benchmark Qualcomm's price. Feeds
`09-software-deals-timeline` and `09-software-deal-values`.

### l09_dsv4_catchup.csv (long)
`record_type,date,days_since_first_light,system,vendor,engine,precision,metric,value,unit,confidence,source_id,notes`

DeepSeek-V4-Pro (released 2026-04-24) day-0 software maturity from SemiAnalysis InferenceX: `frontier` = MI355X
peak tok/s per GPU by date on the AMD SGLang branch; `iso` = throughput at 15 tok/s per user; `spec_ratio` = MI355X ÷
B200 paper specs; `reference` = B200 vLLM tokens/s per provisioned MW on day 0 and day 42; `tco` = MI355X owner TCO per GPU-hour (SemiAnalysis, `estimate`) used to convert throughput into US$ per million tokens. Feeds `09-mi355x-deepseek-v4-catchup`.

### l09_software_price_per_gpu.csv (one row per price point)
`item,group,value_usd_per_gpu_year,basis,confidence,source_id,notes`

NVIDIA AI Enterprise price points (list prices as reported, CEO statement) converted to US$ per GPU per year, next to
B200 owner-TCO and rental references derived from SemiAnalysis $/GPU-hour × 8,760 h (`estimate`). Feeds
`09-software-price-per-gpu-year`.

## Layer 08 — systems, racks and AI factories, CORE pages (`l08_*` core files; charts in `scripts/charts/ch_l08_core.py`; sources S8000–S8025)

### l08_power_per_gpu.csv (one row per system)
`system,vendor,inferencex_key,all_in_kw_per_gpu,gpu_tdp_w,basis,confidence,source_id,notes` — SemiAnalysis's
"all-in utility provisioned power" per GPU (kW) from the InferenceX hardware registry (S622), the denominator InferenceX
uses for throughput per MW. It includes the GPU's share of host, network and facility overhead; the exact scope is not
public, so every row is `estimate`. `08-tokens-per-mw-by-system` divides the DeepSeek-R1 1k/1k Pareto frontier in
`inference_benchmarks.csv` (no speculative decoding), interpolated log-linearly at 50 tok/s/user, by this value.

### l08_liquid_cooling_share.csv (long: forecast vintage × year)
`forecast_vintage,release_date,year,share_pct,kind,scope,confidence,source_id,notes` — TrendForce liquid-cooling
penetration estimates by release (Sep 2024, Aug 2025, Nov 2025, Aug 2026). `kind` = `estimate` (year already past at
release) | `forecast`. Scopes differ slightly between releases (AI chips vs AI data centers); "over 20%" and
"approach 60%" are plotted at 20 and 60.

### l08_buildout_timelines.csv (one row per cited milestone)
`case,category,milestone,start,end,months,confidence,source_id,notes` — months for cited AI-factory build milestones
(`category = build`: xAI Colossus 1, Stargate Abilene) and grid-connection waits (`category = grid`: Dominion large-load
hookups, LBNL generator interconnection median). Build times are company-reported; the LBNL value is a floor ("over 4
years"). Used by `08-build-vs-grid-timelines`.

`08-facility-power-100k-gb300` and `08-capex-vs-power-per-gpu-hour` need no new file: they read rack power, prices and
GPU TDP from `system_specs.csv` / `gpu_product_specs.csv`, and PUE, electricity price, server life and the GB200
all-in/IT power ratio (145/120 kW, SemiAnalysis) from `tco_model_inputs.csv`. `08-gpu-heat-flux-by-generation` divides
`tdp_w` by `dies_per_package × die_area_mm2_per_die` in `gpu_product_specs.csv` (die areas for Blackwell and Rubin are
estimates).

### l09_rocm_lag.csv (one row per milestone pair)
`capability,cuda_milestone,cuda_date,rocm_milestone,rocm_date,lag_days,confidence,source_id,notes`

Days between a CUDA milestone and the matching ROCm milestone: platform 1.0 (month-level dates), FP4 toolkit support
and usable serving of DeepSeek-V4-Pro (from the day-0 run). Feeds `09-rocm-lag-behind-cuda`.

## Layer 08 — systems, racks and AI factories, STRATEGY pages (`l08_*` strategy files; charts in `scripts/charts/ch_l08_strategy.py`; sources S8500–S8530)

### l08_rack_verdicts.csv (long: rival × dimension)
`competitor,system_basis,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes` — repo verdict
(`leads` | `parity` | `behind` | `different`) of seven rival rack-scale systems against NVIDIA Vera Rubin NVL72 on seven
dimensions (compute, memory and power per rack, scale-up domain, liquid-cooling maturity, time to deploy, openness).
All rows are analyst judgement (`speculative`) built on the cited specs. Feeds `08-rack-system-verdict-heatmap`.

### l08_system_vendor_financials.csv (long)
`company,role,period,period_end,metric,value,unit,profit_basis,confidence,source_id,notes` — reported revenue, profit
and margins for NVIDIA, Dell (ISG and AI servers), Supermicro, HPE (Cloud and AI), Vertiv, Quanta, Foxconn and
Morgan Stanley's ODM-per-rack estimates. `profit_basis` = `gross` | `operating` | `adjusted operating`. Periods are
each company's fiscal periods (mid-2026 quarters are compared side by side). Rows with `estimate` are repo calculations
(e.g. gross profit = revenue × margin). Feeds `08-oem-ai-server-revenue-ramp`, `08-system-layer-margin-ladder` and
`08-ai-hardware-profit-pool`.

### l08_infra_deals.csv (one row per deal)
`announce_date,close_date,acquirer,target,category,value_usd_m,value_basis,status,rationale,confidence,source_id,notes`
— rack-adjacent M&A since 2024 (AMD–ZT, Sanmina–ZT manufacturing, Eaton–Boyd Thermal, Schneider–Motivair,
Vertiv–PurgeRite and Great Lakes, HPE–Juniper, AIP/GIP/MGX–Aligned). `value_basis` = `disclosed` | `reported` | `up-to`.
Feeds `08-infra-deal-values` and `08-zt-deal-net-cost` (the latter uses the Sanmina cash/premium/earn-out split in `notes`).

### l08_value_capture.csv (long: system × metric)
`system,era,metric,low,high,unit,confidence,source_id,method,notes` — repo estimates of NVIDIA's content as a share of
system price (`nvidia_content_share_pct`, low–high) and of integrator gross margin (`integrator_gross_margin_pct`) for
HGX H100/H200 servers, GB200, GB300 and Vera Rubin NVL72. `method` documents each calculation; inputs mix years and
analyst sources, so ranges are wide. Feeds `08-value-capture-by-generation`. `08-rack-spec-roadmap` reads
`system_specs.csv` only.

## Layer 11 CORE — inference and AI software (`l11_*` core files; charts in `scripts/charts/ch_l11_core.py`; sources S11000–S11035)

### l11_inference_share.csv (one row per management estimate)
`window,window_end,metric,value,unit,qualifier,confidence,source_id,notes` — NVIDIA management's quantified estimates of the
share of Data Center revenue that went to AI inference (`metric = inference_share_of_dc_revenue`, `unit = pct`).
`qualifier` keeps the wording (`approximately` 40% for the year to Q4 FY2024; `more than` 40% for the year to Q2 FY2025).
Every row is `estimate` (a CFO estimate, not a reported segment). No later percentage was found; later calls are
qualitative. `11-inference-share-of-dc-revenue` applies the shares to trailing-four-quarter Data Center revenue
summed from `financials.csv` and draws later years without a split (a dotted 40% line is a scale illustration only).

### l11_nemotron_models.csv (one row per open Nemotron model)
`model,family,release_date,date_basis,total_params_b,active_params_b,architecture,max_context_tokens,confidence,source_id,notes`
— total and active (per-token) parameters in billions for NVIDIA's flagship open models, from the Nemotron developer
repository and technical reports. `date_basis` says how the date is known; Nemotron 3.5 release months were not
verified (`release_date = 2026`). Used by `11-nemotron-total-vs-active-parameters`.

Two further CORE charts need no new file: `11-disaggregation-vs-aggregated-b200` reads the B200 Pareto-frontier rows of
`inference_benchmarks.csv` and splits them by serving mode (`disagg` in `notes`); `11-cost-per-m-tokens-software-releases`
divides a fixed SemiAnalysis owner TCO per GPU-hour (S622: GB300 $2.31, GB200 $1.86, B200 $1.73, H100 $1.17) by
same-hardware throughput series from `mlperf_results.csv` (Server scenario) and `inference_benchmarks.csv`.

## Layer 05 — Scale-up, CORE pages (`l05_*.csv`; charts in `scripts/charts/ch_l05_core.py`; sources S5000–S5499)

### l05_rack_fabric.csv (wide, one row per NVLink domain / system)
`system,year,status,nvlink_generation,gpus_in_domain,links_per_gpu,pairs_per_gpu,pair_gbps,bidirectional_pairs,per_gpu_bw_gbs_bidir,domain_bw_tbs_bidir,switch_chips,switch_trays,physical_medium,rack_copper_pairs,cables_reported,cable_miles_reported,confidence,source_id,notes`

NVLink fabric facts per system, DGX-1 (2016) → Kyber NVL144 (2027 roadmap). `pairs_per_gpu` = links × lanes × directions
(one differential pair per lane per direction; for NVLink 6/7 two bidirectional pairs per link, per SemiAnalysis) and
`pair_gbps` = Gb/s carried per pair, both directions combined — both are **repo calcs** because NVIDIA publishes link and
lane counts, not pair counts. `domain_bw_tbs_bidir` = GPUs × per-GPU NVLink (bidirectional). `rack_copper_pairs` covers
cable spines and (Kyber) midplane traces. Vera Rubin NVL72 has two rows: the CES 2026 design spec (3.6 TB/s per GPU) and
the revised production spec (3.0 TB/s). `cables_reported` / `cable_miles_reported` are NVIDIA's GTC 2024 keynote figures.

### l05_copper_vs_optics.csv (long)
`record_type,item,lane_gbps,metric,value_low,value_high,unit,confidence,source_id,notes`

`record_type`: `reach` (passive copper reach by lane rate, m; IEEE objectives and vendor listings), `cost` (US$ per 800G
DAC link and per 800G DSP optical module; single-vendor or rough market prices, ranges in `value_low`/`value_high`),
`claim` (NVIDIA GTC 2024 spine figures: cables, miles, kW of optics avoided) and `assumption` (modules an optical NVL72
spine would need). Optics power per technology is read from `optics_power_estimates.csv`.

### l05_moe_comm.csv (long)
`record_type,item,metric,value,unit,confidence,source_id,notes`

Inputs for the MoE all-to-all charts. `model_config` (DeepSeek-V3: hidden size, layers, experts, dispatch/combine bytes,
MLA cache width), `serving` (DeepSeek's published production EP degrees and throughput), `deepep_normal` and
`deepep_low_latency` (DeepEP README v1.2.1 measurements on H800 + 400G InfiniBand: bottleneck GB/s and µs per operation),
`system_link` (per-direction NVLink and NIC GB/s and NVLink domain size per system) and `scenario` (the repo model's
128 tokens per GPU and 64-way EP). The model is bandwidth-only: per layer, time = max(off-domain bytes ÷ NIC,
in-domain bytes ÷ NVLink), × 58 MoE layers.

### l05_nvlink_fusion_partners.csv (one row per partner)
`partner,role,category,announce_date,status,confidence,source_id,notes`

Publicly announced NVLink Fusion partners with announcement date and category (`Design services and IP`, `EDA tools`,
`Connectivity and optics`, `CPUs`, `Accelerators`). Ayar Labs and Lightmatter rest on a single low-authority report
(`reported`). Qualcomm rows use public information only.

## Layer 12 CORE — orchestration and utilization mechanisms (`l12_utilization_scenarios.csv`, `l12_gpu_cloud_capacity.csv`; charts in `scripts/charts/ch_l12_core.py`; sources S12000–S12022)

### l12_utilization_scenarios.csv (long)
`record_type,scenario,item,value,unit,basis,confidence,source_id,notes`

Inputs for the GPU utilization-economics charts. `record_type`: `utilization_level` (the 30/60/90 % illustration points, bracketed by Alibaba fleet and Llama 3 evidence) · `cost_input` (network/storage uplift on rack price, 6- and 5-year useful lives, power basis) · `funnel` (installed → allocated → productive → MFU chain for a `before_fix`/`after_fix` scheduler scenario) · `failure_model` (Llama 3's 419 unexpected interruptions in 54 days on 16,384 GPUs, plus assumed 3/15/60-minute recovery times) · `fragmentation_model` (18-rack NVL72 cluster filled with 8-GPU jobs). Rack prices, power, PUE and $/kWh are read from `tco_model_inputs.csv` and `system_specs.csv`, so the model stays consistent with chapter 14. Documented assumptions: cost per installed GPU-hour = rack price ÷ 72 × (1 + 26 % network/storage uplift) ÷ useful life ÷ 8,760 h + max IT power per GPU × PUE × $/kWh (power charged for all hours, an upper bound); facility capex, staff, software and financing are excluded, so every $/useful-hour figure is a floor. Recovery loss uses a renewal model: lost share = λT ÷ (1 + λT), with λ = per-GPU failure rate × GPUs in the job and T = recovery time. The funnel is a composite illustration (repo Est.), not one cluster's measurement.

### l12_gpu_cloud_capacity.csv (long)
`record_type,provider,provider_type,period,metric,value,unit,confidence,source_id,notes`

`record_type`: `gpu_purchases` (Omdia's estimate of Hopper GPUs bought in calendar 2024, via the FT) · `installed_gpus` (company-disclosed installed base) · `power` (active vs contracted data-center power in GW, company disclosures and guidance; secondary figures marked `estimate`, targets `speculative`). `provider_type`: `hyperscaler` · `neocloud` · `self-build platform` · `AI lab self-build` · `China platform`. Purchases (a flow) and installed GPUs (a stock) are different metrics and are drawn differently. The power rows back the page text; the layer-12 STRATEGY chart `12-neocloud-contracted-vs-active-power` plots neocloud power from its own file.

## Layer 09 CORE — CUDA and system software (`l09_*.csv` below; charts in `scripts/charts/ch_l09_core.py`; sources S9000–S9030)

### l09_kernel_efficiency.csv (one row per kernel × GPU)
`kernel,hardware,architecture,kernel_year,precision,achieved_tflops,peak_dense_tflops,utilization_low_pct,utilization_high_pct,kernel_matches_gpu,confidence,source_id,notes`

Share of dense peak FLOPS reached by FlashAttention 1–4 as published in the papers (ranges where the paper gives one). `kernel_matches_gpu = no` marks a previous-generation kernel run on a newer GPU (FA2 on H100). Peaks come from `gpu_product_specs.csv` sources. The FA3 FP8 row is repo arithmetic (Est.) and not plotted. Feeds `09-attention-kernel-efficiency`.

### l09_port_effort.csv (one row per porting phase)
`phase,order,low_engineer_months,high_engineer_months,evidence,confidence,source_id,notes`

Repo estimate (all rows `speculative`) of engineer-months to port one FlashAttention-class kernel to a new accelerator family, anchored on public bring-up evidence cited per row. The last row is a recurring yearly re-tune. Feeds `09-attention-kernel-port-effort`.

### l09_dsv4_bringup.csv (long)
`record_type,date,days_after_release,platform,vendor,engine,milestone,metric,value,unit,confidence,source_id,notes`

DeepSeek-V4-Pro (released 2026-04-24) bring-up by platform from SemiAnalysis InferenceX articles. `record_type = milestone`: `value` = days after release to the milestone (the day-43 AMD multi-node row is censored, i.e. not achieved by then; the MTP row's day is a placeholder for "week 4"). `record_type = throughput`: MI355X SGLang tokens/s per GPU at 15 tok/s/user (interpolated on each date's Pareto frontier; blank = unreachable) and peak, plus B200 vLLM tokens/s per provisioned MW. Feeds `09-dsv4-day0-readiness` and `09-dsv4-mi355x-bringup`.

### l09_moat_by_segment.csv (long: segment × workload)
`segment,segment_order,workload,workload_order,score_1_5,rationale,confidence,source_id,notes`

Repo scoring (all `speculative`) of switching cost off CUDA, 1 = can move within months, 5 = prohibitive, for seven customer segments × four workloads, each with a one-line rationale and sources. Feeds `09-moat-strength-by-segment`.

## Layer 10 CORE — Libraries, CUDA-X (`l10_*.csv` below; charts in `scripts/charts/ch_l10_core.py`; sources S10000–S10048)

### l10_library_timeline.csv (one row per library or framework integration)
`library,family,domain_group,kind,date,year,event,date_basis,confidence,source_id,notes`

A dated **sample** of 29 major CUDA-X libraries plus 5 zero-code-change framework integrations (`kind` = `library` | `integration`), not NVIDIA's full count (NVIDIA cites "hundreds"). `domain_group` is one of five chart groups (Math and kernels; Communication; AI training and inference; Data, optimization and search; Simulation, science and quantum). `date` is the first *verifiable* public release and `date_basis` says how it was dated: `changelog`, `pypi_first_upload` (earliest PyPI wheel; some libraries were announced earlier, noted in `notes`), `press_release`, `paper`, `toolkit_archive`, `repo`, `acquisition` or `recall` (from memory; notes carry `[recall]`).

### l10_library_speedups.csv (one row per published test)
`domain,library,label,workload,baseline,accelerated,metric,speedup_x,evidence_type,confidence,source_id,notes`

Published GPU-library speedups as reported (not re-run). `metric` = `runtime` (baseline time ÷ GPU time; values below 1 mean the GPU was slower) or `job_cost` (baseline cost ÷ GPU cost). `evidence_type` = `vendor` | `vendor-partner` | `customer` | `third-party` | `peer-company` | `peer-reviewed` | `independent`. Rows are not like-for-like: baselines, data sizes and hardware differ.

### l10_spark_benchmark.csv (one row per Spark engine)
`engine,instance_type,nodes,hardware_per_node,runtime_h,on_demand_usd_per_node_hr,total_job_cost_usd,speed_vs_native_x,confidence,source_id,notes`

AWS Labs data-on-eks benchmark (2026-01-12): TPC-DS-derived 1 TB, 104 queries × 3 iterations on Amazon EKS for native Spark, Gluten/Velox and NVIDIA's cuDF plugin for Spark. Not an official TPC-DS result.

### l10_nccl_model.csv (long)
`record_type,item,fabric,algorithm,protocol,value,unit,confidence,source_id,notes`

`record_type = latency_constant`: NCCL's default tuner constants in microseconds (`base_latency`, `hw_latency_per_step` by fabric NVLink | Network, algorithm and protocol) read from NCCL's source. `record_type = scenario`: inputs for the 70B gradient all-reduce example (parameters, bytes per parameter, GPUs per fabric scenario). Link bandwidths come from `interconnect_specs.csv` (per-direction = bidirectional ÷ 2). Ring time = 2(N−1)/N × size ÷ bandwidth; in-network (SHARP/NVLS) time = size ÷ bandwidth; ring latency = base + 2(N−1) × hop; tree latency = base + 2·log2(N) × hop (simplified, one GPU per node).

### l10_nccl_releases.csv (one row per NCCL minor version)
`version,minor,first_pypi_upload,package,feature,confidence,source_id,notes`

First PyPI upload of each NCCL 2.x minor version across the `nvidia-nccl-cu11/cu12/cu13` wheels, with selected feature milestones (2.23 and 2.27 features `reported`, from recalled NVIDIA blog posts).

## Layer 10 STRATEGY — library competition, history, roadmap and value chain (`l10_*` strategy files; charts in `scripts/charts/ch_l10_strategy.py`; sources S10500–S10570)

### l10_library_coverage.csv (long: domain × vendor)
`domain_order,domain,vendor,libraries,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes` — first-party
accelerated libraries in 15 domains for NVIDIA, AMD, Intel, Google, AWS and Huawei. NVIDIA rows are the reference
(`verdict_vs_nvidia = reference`, `confirmed`); rival rows carry a repo verdict (`leads` | `parity` | `behind` |
`different`, all `speculative`) cited to vendor documentation. "none found" means absent from the vendor's library index
or docs as of 2026-11-05. `different` = the vendor reaches the workload through a compiler (XLA, Neuron) or a managed
service rather than a library. Feeds `10-library-coverage-heatmap` and `10-library-coverage-tally`.

### l10_port_versions.csv (one row per release)
`library,vendor,version,release_date,release_vehicle,upstream_library,upstream_version,confidence,source_id,notes` —
NCCL GitHub tag dates (first tag of each 2.x minor plus the patches RCCL matched) and, for AMD's ports, the NVIDIA version
each port states compatibility with: RCCL per ROCm release (date = ROCm release date from `software_ecosystem.csv`) and
hipDF 2.0.0 in ROCm-DS 25.10 (aligned with cuDF 25.02; month precision, plotted mid-month). Lag = port date − upstream
date; when one RCCL version spans two ROCm releases only the first is used for lag. Feeds `10-port-lag-amd-vs-nvidia` and
`10-nccl-rccl-version-progression` (gap = latest NCCL minor released by the ROCm date − RCCL's matched minor).

### l10_cutlass_arch_support.csv (one row per architecture milestone)
`architecture,sm_target,milestone,cutlass_version,cutlass_date,what_landed,confidence,source_id,notes` — the CUTLASS
release that first supported each data-center GPU architecture (`first support`) and, for Hopper, the release with native
TMA/WGMMA kernels (`native kernels`), from the CUTLASS changelog. The chart subtracts `first_availability` (month, plotted
mid-month) from `gpu_architecture_cadence.csv`. Feeds `10-cutlass-architecture-lead-time`.

### l10_replication_costs.csv (one row per reference point)
`item,entity,category,year,value_usd_b,basis,confidence,source_id,notes` — US$ B reference points for replicating a
CUDA-X-class library stack: software acquisitions (`acquisition`), R&D budgets (`annual_rd`, `rd_delta`) and two repo
estimates (`estimate`, `speculative`) = years × engineers × $0.4M loaded cost per software engineer-year (assumption,
below NVIDIA's ~$0.6M of R&D spend per R&D employee in FY2026). Feeds `10-replication-cost-ladder`.

### l10_software_deals.csv (one row per deal)
`announce_date,acquirer,target,deal_type,what_was_bought,value_usd_m,value_basis,status,confidence,source_id,notes` —
library, AI-software and developer-tool deals by chip vendors (NVIDIA, AMD, Intel, Qualcomm) 2007–2026 plus NVIDIA's
Synopsys equity stake (`deal_type = equity-investment`). `value_basis`: `disclosed` | `reported` | `announced` |
`undisclosed` (blank value). NVIDIA rows mirror `acquisitions_investments.csv` (several `[recall]`); overlaps with
`l09_software_deals.csv` by design (different scope). Feeds `10-software-deal-values`.

## Layer 13 CORE — ecosystem, sovereign AI, enterprise channel and capital (`l13_sovereign_commitments.csv`, `l13_ecosystem_metrics.csv`, `l13_equity_holdings.csv`, `l13_ai_factory_model.csv`; charts in `scripts/charts/ch_l13_core.py`; sources S13000–S13043)

### l13_sovereign_commitments.csv (one row per country-level announcement)
`announce_date,country,region,counterparties,nvidia_role,gpus_committed,gpu_platform,power_mw,stated_value,timeline,status,headline_row,confidence,source_id,notes`

`gpus_committed` is the NVIDIA GPU count named in the announcement (blank when undisclosed); `power_mw` the stated site or
cluster power; `stated_value` free text in the announced currency. `headline_row = yes` marks the one row per country used by
`13-sovereign-gpu-commitments` (later expansions and superseded plans are `no`). Saudi Arabia's 600,000 is HUMAIN's
three-year plan across Saudi and US sites. (The layer-13 STRATEGY author's `l13_sovereign_deals.csv` tracks plans vs firm
orders and export-licence caps; the two files are complementary.)

### l13_ecosystem_metrics.csv (long)
`record_type,date,metric,value,unit,confidence,source_id,notes`

`record_type` ∈ `gtc` (`gtc_attendees_in_person`, `gtc_attendees_virtual`, `gtc_sessions`; 2024–26 are NVIDIA pre-event
figures), `inception` (`inception_members`; the 2025 row is a secondary, PitchBook-based `estimate`), `dli`
(`dli_training_target`, `dli_developers_trained_cumulative`), `nventures` (`nventures_deals`) and `corporate`
(`nvidia_venture_rounds`, PitchBook via press; counts conflict across outlets).

### l13_equity_holdings.csv (long)
`period,period_end,metric,value,unit,confidence,source_id,notes`

NVIDIA's equity securities in US$ B: `non_marketable_equity` (FY2025 and FY2026 from the FY2026 10-K roll-forward;
Q1/Q2 FY2027 from 10-Q readings), `marketable_equity`, `lockedup_public_equity`, `equity_purchases_half_year`,
`net_equity_gains_quarter`, `further_equity_commitments`. The ~$99B total is a press aggregation of three balance-sheet lines.

### l13_ai_factory_model.csv (scenario inputs)
`input,value,unit,basis,confidence,source_id,notes`

Scenario parameters for the 100,000-GPU national AI factory (`13-national-ai-factory-cost`): target GPU count and assumed
NVIDIA shares of non-GPU rack content and of scale-out networking plus storage (all `speculative`). Rack prices, BOM splits,
power, PUE, facility $/MW and electricity price are read from `tco_model_inputs.csv` (GB300 NVL72 rows; facility $/MW comes
from a Morgan Stanley model that was later retracted and is used only as an illustration).

## Case study CS4 — AMD, OpenAI and the second source (`cs4_amd_openai.csv`, charts in `scripts/charts/ch_cs4.py`; sources S24000–S24011)

### cs4_amd_openai.csv (long)
`record_type,period,entity,metric,value,unit,confidence,source_id,notes`

`record_type` ∈ `dc_revenue` (AMD Data Center segment, US$ B, 2026-Q1 to 2026-Q3; extends the 2023–2025 AMD rows in
`peer_financials.csv`, which the chart reads unchanged; 2026-Q3 is a repo calculation from the reported +97 % y/y),
`share_price` (AMD closes around the deal and the first close above $600), `warrant_term` (160M shares at $0.01, 6 GW, the
reported $600 final-tranche hurdle, pre-deal share count derived from market cap / price) and `assumption` (repo scenarios
for OpenAI's AMD hardware spend per GW: $10B / $15B / $20B, all `speculative`, anchored on the reported value of AMD's
identical 6 GW Meta deal). Used by `CS4-amd-vs-nvidia-dc-revenue` (with `financials.csv`, NVIDIA fiscal quarters mapped to
the calendar quarter they mostly cover) and `CS4-warrant-value-vs-hardware-spend`.

## Case study CS5 — the DeepSeek moment and the efficiency shock (`cs5_*.csv`, charts in `scripts/charts/ch_cs5.py`; sources S25000–S25012)

### cs5_cost_claims.csv (one row per cost figure)
`item,date,entity,category,value_usd_m,basis,confidence,source_id,notes`

DeepSeek's own training-cost claims (V3 final run, R1 reinforcement learning), SemiAnalysis's fleet estimates (GPU
investment, server capex) and NVIDIA's one-day market-value loss on 2025-01-27, all in US$ M. `category` ∈ `company claim` |
`analyst estimate` | `market reaction`. Used by `CS5-deepseek-cost-headline-vs-fleet`.

### cs5_elasticity_grid.csv (generated grid)
`price_drop_multiple,elasticity,quantity_multiple,spend_multiple,formula,confidence,source_id,notes`

Constant-elasticity demand: when the price per token falls by `price_drop_multiple` (3×, 10×, 30×), tokens demanded rise by
drop^ε and spend changes by drop^(ε−1). Spend rises only when ε > 1. All rows `estimate` (computed); ignores outward shifts
of the demand curve from new capabilities. Used by `CS5-spend-multiple-vs-elasticity`.

## Layer 11 STRATEGY — inference competition, deals, token prices and value pools (`l11_*` strategy files; charts in `scripts/charts/ch_l11_strategy.py`; sources S11500–S11541)

### l11_inference_verdicts.csv (long, challenger × dimension)
`competitor,product_basis,dimension,verdict_vs_nvidia,cell_label,rationale,confidence,source_id,notes` — repo verdict of eight
inference challengers (open-source serving, AMD, Google TPU, AWS, Microsoft Maia, Cerebras, Groq, Qualcomm — public information
only) against NVIDIA's GB300 / Vera Rubin NVL72 with Dynamo and TensorRT-LLM on five dimensions (tokens/s per user, throughput per
dollar, software maturity, model coverage, deployment flexibility). `verdict_vs_nvidia`: `leads` | `parity` | `behind` |
`different`. Judgement rows are `speculative` or carry the confidence of the underlying evidence. Feeds `11-inference-challenger-heatmap`.

### l11_inference_deals.csv (one row per deal)
`announce_date,close_date,acquirer,target,deal_type,value_usd_m,value_basis,what_it_brought,status,confidence,source_id,notes` —
inference software and silicon deals 2023–2026 by NVIDIA, AMD, Qualcomm, Intel and Red Hat. `value_basis`: `disclosed` |
`reported` | `up-to` | `undisclosed`; `status`: `closed` | `pending` | `not completed`. Feeds `11-inference-deal-values`.

### l11_token_prices.csv (one row per price point)
`date,model,provider,tier,input_usd_per_m,output_usd_per_m,blended_3to1_usd_per_m,basis,confidence,source_id,notes` — API list
prices per million tokens at launch or price cut (OpenAI flagship and small tiers) and the Stanford AI Index "capability floor"
(cheapest model at GPT-3.5-level quality). `blended_3to1` = (3 × input + output) / 4, Epoch AI's convention; AI Index rows give a
single price. Feeds `11-api-token-price-trend`.

### l11_private_companies.csv (one row per company)
`company,segment,date,event,raise_usd_m,valuation_usd_m,valuation_basis,status,confidence,source_id,notes` — last disclosed or
reported valuation of inference clouds, serving-engine companies and inference-silicon start-ups (public information only).
`segment`: `inference cloud` | `serving engine` | `inference silicon`; `valuation_basis` distinguishes closed rounds from talks,
offers, IPO pricing and acquisition prices; `status`: `private` | `public` | `acquired` | `licensed to NVIDIA`. Feeds
`11-inference-startup-valuations`.

### l11_token_value_pools.csv (one row per value-pool step)
`scenario,step,component,value_cents_per_usd,basis,confidence,source_id,notes` — repo estimate (all `estimate` except the reported
lab compute margin) of how $1.00 of closed-model API revenue served on rented GB300 NVL72 capacity splits between the model lab,
the cloud operator, electricity, facility/financing, other IT hardware, NVIDIA's cost of goods and NVIDIA's gross profit. Inputs:
OpenAI compute margin ~70% (The Information via S11537), GB300 rental $5.00 vs owner TCO $2.31 per GPU-hour (S622), power ~15% of
owner TCO, NVIDIA ~75% of IT hardware spend and a 75% gross margin (S3). Values sum to 100. Feeds `11-token-revenue-value-pools`.

`ch_l11_strategy.py` also builds `11-inference-memory-tradeoff` and `11-decode-bandwidth-by-vendor` directly from
`gpu_product_specs.csv` and `competitor_accelerators.csv`.

## Layer 13 STRATEGY — ecosystem and capital competition, deals and value chain (`l13_strat_*.csv`; charts in `scripts/charts/ch_l13_strategy.py`; sources S13500–S13536)

### l13_strat_peer_capital.csv (long)
`company,period,period_end,metric,value,unit,confidence,source_id,notes`

Deployable capital for NVIDIA, AMD, Broadcom and Qualcomm at each company's latest reported quarter end (US$ B):
cash and liquid securities (definitions differ by company and are named in `metric`), total debt, NVIDIA's listed and
private equity stakes and buyback authorization, and the latest quarterly free cash flow found. AMD and Qualcomm free
cash flow are aggregator figures (`estimate`). Most rows were read from filings via search snippets (sec.gov blocked).

### l13_strat_capital_per_gw.csv (one row per vendor-to-customer deal)
`deal,supplier,counterparty,announce_date,instrument,capital_usd_b,capital_basis,committed_gw,capital_per_gw_usd_b,status,confidence,source_id,notes`

Vendor capital offered per gigawatt of committed compute. AMD's OpenAI warrant is valued by the repo at two AMD share
prices (the reported $600 final-tranche hurdle and an illustrative $200); NVIDIA's 2026 OpenAI equity has no GW tie and
a blank `capital_per_gw_usd_b`.

### l13_strat_deals_2026_additions.csv
Same schema as `acquisitions_investments.csv`. 2026 deals missing from the shared file (xAI Series E, Lumentum,
Coherent, Marvell, the August 2026 financing platforms); `ch_l13_strategy.py` concatenates both files for the
deal-structure chart and maps each row to a structure (acquisition, licence + acquihire, stake in customer = layers
12/13, stake in supplier/partner = other layers, capacity or financing commitment).

### l13_strat_gw_pipeline.csv (one row per buyer × supplier programme)
`buyer,supplier,program,announce_date,deploy_window,gw,gw_basis,status,confidence,source_id,notes`

Announced compute programmes in gigawatts for OpenAI, Anthropic, HUMAIN and xAI by chip supplier. `gw` is the
announced ceiling or target, not deployed capacity; NVIDIA's OpenAI row is the September 2025 letter of intent
(restructured in 2026) and xAI's is a contested company claim.

### l13_strat_equity_portfolio.csv (long)
`period,period_end,metric,value,unit,confidence,source_id,notes`

Press readings of NVIDIA's 10-Q equity disclosures: non-marketable and marketable equity, equity purchases in the first
half of FY2026 and FY2027, net equity gains and further equity commitments. Used with `financials.csv`
(`shareholder_returns`) for the equity-vs-payouts chart.

## Layer 12 strategy — orchestration and cloud competition, roadmap and value chain (`l12_*.csv` below; charts in `scripts/charts/ch_l12_strategy.py`; sources S12500–S12536)

### l12_competitor_verdicts.csv (long, competitor × dimension)
`competitor,product_basis,dimension,verdict_vs_nvidia,cell_label,confidence,source_id,notes` — repo judgement of nine layer-12
rivals (AWS, Google Cloud, Microsoft Azure, CoreWeave, Nebius, Kubernetes + Kueue, Ray/Anyscale, SkyPilot, GPU marketplaces)
against NVIDIA's position (DGX Cloud/Lepton, Run:ai/KAI, Slurm, DSX OS, allocation and capital) on five dimensions: customer
ownership, owned capacity, accelerator control, scheduling & orchestration, hardware neutrality. All rows `speculative`; the
source ids are the evidence behind each cell. Feeds `12-cloud-competitor-heatmap`.

### l12_equity_holdings.csv (long)
`period,period_end,metric,value,unit,confidence,source_id,notes` — NVIDIA equity securities by balance-sheet line
(`marketable_equity`, `non_marketable_equity`, `locked_up_public_equity`) at Jan/Apr/Jul 2026, plus H1 equity purchases, H1 net
equity gains and outstanding equity commitments (US$ B). Q2 FY2027 lines are secondary readings of the 10-Q. The Apr 2026
non-marketable figure ($43.4B here) differs from the ~$42.3B in the S90070 registry note; flagged for QA. Feeds
`12-nvidia-customer-support-exposure` (with `financials.csv`).

### l12_neocloud_metrics.csv (long)
`company,period,metric,value_low,value_high,unit,confidence,source_id,notes` — CoreWeave and Nebius guidance and operating
metrics (revenue and capex guidance, revenue backlog by quarter, active/contracted power, debt, interest, ARR). Single values
repeat in `value_low` and `value_high`. The June 2025 CoreWeave backlog is derived from the reported +246% y/y growth
(`estimate`). Feeds `12-neocloud-capex-vs-revenue-2026` and `12-coreweave-backlog-growth`.

### l12_gpu_rental_index.csv (one row per observation)
`date,gpu,series,contract_type,usd_per_gpu_hour,confidence,source_id,notes` — H100 rental price observations by series
(SemiAnalysis 1-year contract index, Silicon Data index, spot prices as cited, 2023–24 anecdotal points shared with
`gpu_rental_prices.csv`). Contract types differ: compare within a series. Feeds `12-h100-rental-price-rebound`.

### l12_private_companies.csv (one row per company)
`company,category,what_they_do,last_round_date,last_round,amount_usd_b,valuation_usd_b,valuation_basis,nvidia_backed,confidence,source_id,notes`
— last public round of private AI-cloud and AI-infrastructure companies (public information only); Lambda's valuation is a
press-reported pre-IPO target. Feeds `12-neocloud-private-valuations`.

### l12_hyperscaler_capex_guidance.csv (one row per guidance issued)
`company,guidance_date,period,capex_low_usd_b,capex_high_usd_b,basis,confidence,source_id,notes` — calendar-2026 capex guidance
ranges by date issued for Alphabet, Amazon, Meta and Microsoft (calendar basis, incl. finance leases where the company does).
February 2026 rows repeat the `[recall]` rows of `peer_financials.csv`. Feeds `12-hyperscaler-capex-guidance-drift`.
