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
