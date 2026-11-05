# The utilization problem: why idle GPUs destroy ROI

<sub>Layer 12 · Orchestration and cloud services · ~9 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **A GPU's cost is almost all fixed.** Depreciation is ~81–88% of a modern GPU's yearly cost and electricity only ~12–19% at $0.081/kWh [[S389]](../../sources/bibliography.md#s389)[[S382]](../../sources/bibliography.md#s382), so an idle GPU costs nearly as much as a busy one.
- **Est. ~$1.50 per installed hour for a GB300 [NVL72](../../glossary.md#nvl72) GPU:** $3.99M per rack ÷ 72 [[S332]](../../sources/bibliography.md#s332), +26% for networking and storage [[S324]](../../sources/bibliography.md#s324), over six years [[S382]](../../sources/bibliography.md#s382)[[S386]](../../sources/bibliography.md#s386), plus ~$0.17/h of power [[S337]](../../sources/bibliography.md#s337)[[S389]](../../sources/bibliography.md#s389). That is **$5.00 per useful hour at 30% utilization, $2.50 at 60% and $1.67 at 90%**.
- **Each 10 points of utilization on 100,000 GB300 GPUs is worth ~$131M a year** of cost (Est., repo calc from the figures above).
- **Waste is structural, not careless.** In Alibaba's 155,410-GPU fleet, [fragmentation](../../glossary.md#gpu-fragmentation) was a primary reason idle GPUs could not be allocated; a scheduling change lifted the [allocation ratio](../../glossary.md#allocation-ratio) from 68% to 93%, and online inference ran at a median ~6% [SM utilization](../../glossary.md#sm-utilization) [[S12015]](../../sources/bibliography.md#s12015).
- **Even a frontier run leaks:** Meta's Llama 3 405B job saw 419 unexpected interruptions in 54 days on 16,384 GPUs, kept >90% [effective training time](../../glossary.md#effective-training-time) and ran at 38–41% [MFU](../../glossary.md#mfu) [[S34006]](../../sources/bibliography.md#s34006).
- **Shorter lives raise the stakes:** Amazon cut part of its server fleet back to five-year lives in 2025 [[S385]](../../sources/bibliography.md#s385), which lifts the hourly cost ~18%.
- **Someone always owns the idle hours.** [Take-or-pay](../../glossary.md#take-or-pay) contracts push them to tenants; NVIDIA's $6.3B CoreWeave backstop takes a slice onto NVIDIA's own books [[S90067]](../../sources/bibliography.md#s90067).

![Grouped bar chart of where installed GPU-hours go (composite estimate). Before a scheduler fix: 100 installed, 68 allocated (Alibaba's 68% allocation ratio), 61.2 productive after about 10% lost to failures, restarts and checkpoints (Llama 3 reported over 90% effective training time) and 24.5 worth of peak FLOPs at 40% MFU. After the fix: 93 allocated, 83.7 productive and 33.5 used, 1.37 times more useful work from the same hardware.](../../assets/charts/12-utilization-funnel.svg)

## Why a GPU is like an airline seat

An empty airline seat cannot be sold after take-off; an idle [GPU-hour](../../glossary.md#gpu-hour) cannot be sold after the hour passes. The owner has already paid for the aircraft. For a GPU, the "aircraft" is the purchase price written off over its useful life, and it is most of the [TCO](../../glossary.md#tco).

**[Q1 · Job & failure mode]** Layer 12's job is to turn installed racks into GPU-hours that do useful work and, for clouds, into GPU-hours someone pays for. When it is weak, nothing visibly breaks: GPUs sit allocated but idle, jobs queue behind fragments, large runs stall on failures, and the cost per useful token quietly doubles or triples.

![Bar chart of capex per GPU: DGX-1 P100 about $16K (2016), DGX-1 V100 $19K, DGX-2 $25K, DGX A100 $25K, HGX H200 OEM about $40K, DGX H200 about $58K, DGX B200 about $46K, GB200 NVL72 about $42K, GB300 NVL72 about $55K and Vera Rubin NVL72 about $108K per GPU, with alternative analyst estimates from about $39K to $126K shown as dots. No public system prices exist for AMD, Google or AWS racks.](../../assets/charts/14-capex-per-accelerator-by-system.svg)

> [!TIP]
> **Worked example — what an hour of a GB300 GPU costs.** Morgan Stanley puts a GB300 NVL72 rack at $3.99M [[S332]](../../sources/bibliography.md#s332) → $55.4K per GPU. SemiAnalysis's GB200 figures imply ~26% more for [scale-out](../../glossary.md#scale-out) networking and storage [[S324]](../../sources/bibliography.md#s324) → ~$69.8K. Over six years (Microsoft, Alphabet, CoreWeave policy) [[S382]](../../sources/bibliography.md#s382)[[S383]](../../sources/bibliography.md#s383)[[S386]](../../sources/bibliography.md#s386) that is $69.8K ÷ 6 ÷ 8,760 h = **$1.33/h**. Power: 132 kW ÷ 72 GPUs [[S337]](../../sources/bibliography.md#s337) × 1.15 [PUE](../../glossary.md#pue) × $0.081/kWh [[S389]](../../sources/bibliography.md#s389) = **$0.17/h**. Total ≈ **$1.50 per installed hour**. Divide by utilization: $5.00 at 30%, $2.50 at 60%, $1.67 at 90%. A Vera Rubin NVL72 GPU (~$7.8M per rack [[S330]](../../sources/bibliography.md#s330)) costs ~$2.89 per installed hour, so idleness hurts it twice as much in dollars. **Conclusion:** at 30% utilization a GB300 owner pays more per useful hour than the ~$2–3/h list price of a rented H100 on a [neocloud](../../glossary.md#neocloud) [[S393]](../../sources/bibliography.md#s393)[[S395]](../../sources/bibliography.md#s395).

![Line chart of estimated cost per useful GPU-hour against utilization. A GB300 NVL72 GPU costs about $1.50 per installed hour (capex $70K incl. networking and storage, 6-year life, power $0.17/h), so $5.00 per useful hour at 30% utilization, $2.50 at 60% and $1.67 at 90%; with a 5-year life $5.88, $2.94 and $1.96. Vera Rubin NVL72 (about $2.89 per installed hour) costs $9.65, $4.82 and $3.22; DGX H200 about $1.54 per installed hour. Cost per useful hour scales with 1/utilization.](../../assets/charts/12-cost-per-useful-gpu-hour.svg)

The useful life is the other lever. [Hyperscalers](../../glossary.md#hyperscaler) stretched server lives to six years in 2022–2023; Amazon reversed part of that in 2025, citing the pace of AI technology [[S385]](../../sources/bibliography.md#s385). Five years instead of six raises the GB300 hour from $1.50 to $1.76.

![Step chart of server useful lives: Microsoft 3 to 4 years (July 2020) and 6 years (July 2022); Alphabet 3 to 4 years (2021) and 6 years (2023); Amazon 3 to 4 (2020), 5 (2022), 6 (2024) and back to 5 years for part of its servers in 2025; Meta 4 to 4.5 years (2022) and 5.5 years (2025); CoreWeave 6 years for GPU servers since 2023.](../../assets/charts/14-depreciation-life-assumptions.svg)

<details>
<summary>🔧 Under the hood: the cost model and what it leaves out</summary>

Cost per useful hour = (capex per GPU × 1.26 ÷ life ÷ 8,760 + kW per GPU × PUE × $/kWh) ÷ utilization. Inputs come from `data/tco_model_inputs.csv` and `data/l12_utilization_scenarios.csv`. Power is charged at maximum for all hours, an upper bound. Facility capex, staff, software licences and financing are excluded, so every figure is a **floor**. A neocloud borrowing at high rates would add a large financing line. See [Training vs inference economics](../../cross-cutting/14-training-vs-inference-economics.md) for the full TCO model.

</details>

## Where the hours go: five sources of waste

Utilization leaks at several stages, and each stage needs a different fix.

| Source of waste | Mechanism | Evidence | What fixes it |
|---|---|---|---|
| Fragmentation | Free GPUs scattered in pieces too small for the next job | Primary cause of unallocatable idle GPUs at Alibaba; 68% → 93% allocation after a scheduler change [[S12015]](../../sources/bibliography.md#s12015) | [Bin-packing](../../glossary.md#bin-packing), [topology-aware scheduling](../../glossary.md#topology-aware-scheduling) |
| Failures and checkpoint restarts | One bad GPU stops a synchronous job; work since the last [checkpoint](../../glossary.md#checkpoint) is redone | 419 unexpected interruptions in 54 days, ~78% hardware-related [[S34006]](../../sources/bibliography.md#s34006)[[S31003]](../../sources/bibliography.md#s31003) | Health checks, fast automated recovery |
| Data stalls | GPUs wait for input data | DGX-2 ran at 56% of its ResNet-50 ceiling with CPU preprocessing [[S4017]](../../sources/bibliography.md#s4017) | GPU data loading, faster storage |
| Idle reservations | Teams hold GPUs "just in case"; notebooks hold a whole GPU | Small fractional jobs drove low utilization in a 6,742-GPU Alibaba cluster [[S12017]](../../sources/bibliography.md#s12017) | Quotas, [preemption](../../glossary.md#preemption), [fractional GPUs](../../glossary.md#fractional-gpu) |
| MFU vs allocation | A busy GPU still uses a fraction of peak FLOPs | 38–41% MFU on Llama 3 [[S34006]](../../sources/bibliography.md#s34006); ~6% median SM use for online inference [[S12015]](../../sources/bibliography.md#s12015) | Kernels, parallelism, batching (layers 10–11) |

> [!TIP]
> **Worked example — chaining the losses.** Start with 100 installed GPU-hours. Alibaba's pre-fix allocation of 68% leaves 68 allocated [[S12015]](../../sources/bibliography.md#s12015). Losing ~10% of allocated time to failures and restarts (Llama 3 kept >90%) [[S34006]](../../sources/bibliography.md#s34006) leaves 61.2 productive. At 40% MFU only **24.5 hours' worth of peak FLOPs** reach the model. With 93% allocation the chain ends at **33.5**, 1.37× more output from the same capex. **Conclusion:** the scheduler fix is worth as much as a 37% hardware discount (Est., composite illustration).

> [!WARNING]
> **Myth vs reality: "our GPUs show 100% utilization."** Simple tools report the share of time *any* kernel runs. A GPU can show 100% while most of its streaming multiprocessors idle. Allocation ratio, [SM utilization](../../glossary.md#sm-utilization) from [DCGM](../../glossary.md#dcgm) and MFU measure different things; always ask which one a claim uses.

**[Q2 · Metrics that matter]** Five numbers decide this layer: (1) **allocation ratio**, the share of installed GPUs assigned to jobs; (2) **effective training time** or [goodput](../../glossary.md#goodput), the share of allocated time that makes progress; (3) **MFU** or tokens per GPU-hour, the useful work per busy hour; (4) **[mean time to recovery](../../glossary.md#mttr)**, which sets how much a failure costs; (5) **$ per useful GPU-hour**, the number that folds the other four into ROI.

<details>
<summary>🔧 Under the hood: three meanings of "utilization"</summary>

- **Allocation ratio** (scheduler view): GPUs assigned ÷ GPUs installed. Easy to inflate by over-reserving.
- **SM activity / occupancy** (DCGM telemetry view): how much of each GPU's compute array is active. Exposes idle allocations.
- **MFU / goodput** (model view): FLOPs the model needed ÷ peak FLOPs available, net of restarts. The only one that maps to tokens or training progress.

</details>

## Who carries the idle risk

Every idle hour lands on someone. A hyperscaler running its own models carries it directly. A neocloud usually sells multi-year take-or-pay contracts, so the tenant pays whether or not it uses the hours. NVIDIA has agreed to buy up to $6.3B of CoreWeave's unsold capacity through April 2032 [[S90067]](../../sources/bibliography.md#s90067), absorbing part of the risk itself.

> [!TIP]
> **Worked example — what the backstop covers.** At the ~$2.35 one-year H100 contract rate of March 2026 [[S12516]](../../sources/bibliography.md#s12516), $6.3B buys ~2.7B GPU-hours. Spread over the ~6.5 years to April 2032, that is ~47,000 GPUs running full-time (Est.). CoreWeave ran >250,000 GPUs at end-2024 [[S12011]](../../sources/bibliography.md#s12011). **Conclusion:** the backstop is a floor under a slice of the fleet, not a guarantee of all of it.

> [!NOTE]
> **🐂 Bull view:** better schedulers, faster recovery and inference fleets that run 24/7 push utilization up, so each GPU earns more and the installed base stays valuable longer.

> [!WARNING]
> **🐻 Bear view:** if demand cools, utilization falls first at neoclouds with short contracts. Cost per useful hour then jumps (1/utilization), rental prices fall, and backstops become liabilities.

## 🎯 Corp Dev Lens

1. **Utilization is a cost-of-goods lever worth billions.** At ~$131M per 10 points per 100,000 GB300 GPUs (Est.), scheduling and recovery software has a quantifiable value that buyers can underwrite.
2. **Which metric does a target report?** Diligence on any GPU cloud or AI-infrastructure software company should ask for allocation, effective time and MFU separately.
3. **Depreciation policy is a hidden valuation input.** A one-year change in useful life moves hourly cost ~18%; compare tenants' and owners' assumptions [[S385]](../../sources/bibliography.md#s385)[[S386]](../../sources/bibliography.md#s386).
4. **Qualcomm question (public information only):** for inference racks such as AI200/AI250 [[S90028]](../../sources/bibliography.md#s90028), does a utilization story (fractional sharing, high duty cycle) matter more to buyers than peak TOPS?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S324**](../../sources/bibliography.md#s324) fal.ai, *NVIDIA GB200 price in 2026: what a GPU, a tray and an NVL72 rack cost*, 2026. [Link](https://fal.ai/learn/serverless/nvidia-gb200-price)
- [**S330**](../../sources/bibliography.md#s330) PC Gamer, *A single Nvidia Vera Rubin rack is estimated to cost $7,803,148 with over $2 million of that figure spent on memory alone*, 2026-05. [Link](https://pcgamer.com/hardware/a-single-nvidia-vera-rubin-rack-is-estimated-to-cost-usd7-803-148-with-over-usd2-million-of-that-figure-spent-on-memory-alone)
- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S337**](../../sources/bibliography.md#s337) Spheron, *NVIDIA GB300 (rental and specifications)*, 2026. [Link](https://spheron.network/gpu-rental/gb300/)
- [**S382**](../../sources/bibliography.md#s382) Microsoft via SEC EDGAR, *Microsoft Corporation Form 10-K filings (FY2021, FY2023) - property and equipment useful lives*, 2023-07-27. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K&dateb=&owner=include&count=40)
- [**S383**](../../sources/bibliography.md#s383) Alphabet via SEC EDGAR, *Alphabet Inc. Form 10-K filings (FY2020, FY2022) - useful lives of servers and network equipment*, 2023-02-03. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K&dateb=&owner=include&count=40)
- [**S385**](../../sources/bibliography.md#s385) Amazon via SEC EDGAR, *Amazon.com Form 10-K filings (FY2019-FY2024) - useful lives of servers*, 2025-02-07. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K&dateb=&owner=include&count=40)
- [**S386**](../../sources/bibliography.md#s386) CoreWeave via SEC EDGAR, *CoreWeave Form S-1 registration statement (2025) - technology equipment useful life*, 2025-03-03. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=coreweave&type=S-1&dateb=&owner=include&count=40)
- [**S389**](../../sources/bibliography.md#s389) U.S. Energy Information Administration, *EIA Electric Power Monthly, Table 5.6.A: average price of electricity to ultimate customers by end-use sector*, 2025. [Link](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a)
- [**S393**](../../sources/bibliography.md#s393) Latent Space (Eugene Cheah), *$2 H100s: how the GPU bubble burst*, 2024-10. [Link](https://www.latent.space/p/gpu-bubble)
- [**S395**](../../sources/bibliography.md#s395) Lambda, *Lambda GPU cloud pricing*, 2025. [Link](https://lambda.ai/pricing)
- [**S4017**](../../sources/bibliography.md#s4017) NVIDIA Technical Blog, *Case Study: ResNet50 with DALI*, 2019. [Link](https://developer.nvidia.com/blog/case-study-resnet50-dali/)
- [**S12011**](../../sources/bibliography.md#s12011) DatacenterDynamics, *CoreWeave files for IPO on Nasdaq stock market*, 2025-03. [Link](https://www.datacenterdynamics.com/en/news/coreweave-files-for-ipo-on-nasdaq-stock-market/)
- [**S12015**](../../sources/bibliography.md#s12015) USENIX OSDI '26 (Li et al. (Alibaba / HKUST)), *Heterogeneity at Hyperscale: Characterization and Scheduling of Large Production AI Clusters at Alibaba*, 2026-07. [Link](https://www.usenix.org/conference/osdi26/presentation/li-suyi)
- [**S12017**](../../sources/bibliography.md#s12017) USENIX NSDI '22 (Weng et al.), *MLaaS in the Wild: Workload Analysis and Scheduling in Large-Scale Heterogeneous GPU Clusters*, 2022-04. [Link](https://www.usenix.org/conference/nsdi22/presentation/weng)
- [**S12516**](../../sources/bibliography.md#s12516) SemiAnalysis, *The Great GPU Shortage - Rental Capacity - Launching our H100 1 Year Rental Price Index*, 2026-03. [Link](https://newsletter.semianalysis.com/p/the-great-gpu-shortage-rental-capacity)
- [**S31003**](../../sources/bibliography.md#s31003) Tom's Hardware, *Faulty Nvidia H100 GPUs and HBM3 memory caused half of the failures during Llama 3 training — one failure every three hours for Meta's 16,384 GPU training cluster*, 2024-07. [Link](https://www.tomshardware.com/tech-industry/artificial-intelligence/faulty-nvidia-h100-gpus-and-hbm3-memory-caused-half-of-the-failures-during-llama-3-training-one-failure-every-three-hours-for-metas-16384-gpu-training-cluster)
- [**S34006**](../../sources/bibliography.md#s34006) arXiv:2407.21783 (Llama Team (AI @ Meta)), *The Llama 3 Herd of Models*, 2024-07-31. [Link](https://arxiv.org/abs/2407.21783)
- [**S90028**](../../sources/bibliography.md#s90028) TechRepublic, *Qualcomm unveils AI chips to rival Nvidia, AMD*, 2025-10-27. [Link](https://techrepublic.com/article/news-qualcomm-unveils-ai-chips-to-rival-nvidia-amd)
- [**S90067**](../../sources/bibliography.md#s90067) DatacenterDynamics, *Nvidia to purchase unsold compute capacity from CoreWeave for $6.3bn*, 2025-09-16. [Link](https://www.datacenterdynamics.com/en/news/nvidia-to-purchase-unsold-compute-capacity-from-coreweave-for-63bn/)
