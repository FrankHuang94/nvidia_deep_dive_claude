# The inference shift

<sub>Layer 11 · Inference and AI software · ~8 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **Tokens per task, not users, drive demand.** A reasoning answer generates ~21× a chat reply's tokens; a 30-turn coding agent handles ~1,100× the total (Est.) [[S32025]](../../sources/bibliography.md#s32025). Google's monthly tokens grew ~134× in 18 months [[S32018]](../../sources/bibliography.md#s32018)[[S32020]](../../sources/bibliography.md#s32020).
- **Inference is sold on a latency curve.** On DeepSeek-R1, GB300 NVL72 serves ~6,261 tokens/s per GPU at 50 tokens/s per user but ~562 at 100 [[S621]](../../sources/bibliography.md#s621). Faster tiers cost ~11× more per token (Est.) [[S622]](../../sources/bibliography.md#s622).
- **Power is the binding budget.** At 50 tokens/s per user, GB300 NVL72 yields ~3.0M tokens/s per MW of all-in power vs ~225k for H200, ~13× [[S621]](../../sources/bibliography.md#s621)[[S622]](../../sources/bibliography.md#s622). 🟡 NVIDIA claims Vera Rubin plus Groq LPX raises tokens per watt 35× [[S113]](../../sources/bibliography.md#s113)[[S90003]](../../sources/bibliography.md#s90003).
- **NVIDIA's last number: inference was >40% of Data Center revenue** for the year to Q2 FY2025, implying ≥$33B [[S11011]](../../sources/bibliography.md#s11011)[[S441]](../../sources/bibliography.md#s441). 🔴 At that share the latest year's $277.7B would hold ~$111B, but no split has been disclosed since [[S405]](../../sources/bibliography.md#s405).
- **Management now talks qualitatively.** It cites an "inflection in inference demand" and $1T of Blackwell plus Rubin demand through 2027 [[S409]](../../sources/bibliography.md#s409)[[S90001]](../../sources/bibliography.md#s90001).
- **The bear point: inference is easier to contest than training.** Requests are independent and cost per token is easy to benchmark. Google's TPU served Qwen3.5 397B for ~$0.18 per million tokens vs ~$0.22 on B200 [[S625]](../../sources/bibliography.md#s625).

![Log-scale chart of disclosed AI token volumes: Google rose from 9.7 trillion tokens per month (April 2024) to 480 trillion (April 2025), about 980 trillion (mid-2025) and over 1.3 quadrillion (October 2025), about 134 times in 18 months. Microsoft processed over 100 trillion tokens in Jan-Mar 2025 (5 times a year earlier) with 50 trillion in March alone; OpenAI's API ran about 6 billion tokens per minute in October 2025, roughly 259 trillion per month.](../../assets/charts/P2-token-demand-growth.svg)

## Why reasoning and agents multiply token demand

**Analogy.** A chatbot is a vending machine: one question, one answer. A [reasoning model](../../glossary.md#reasoning-model) is a consultant who drafts pages of notes before replying. An [agent](../../glossary.md#agentic-ai) is a project team that rereads the whole file before every step.

**Mechanism.** Reasoning models write hidden "thinking" tokens, billed as output and costing full [decode](../../glossary.md#decode) time [[S32024]](../../sources/bibliography.md#s32024). Agents loop: plan, call a tool, read the result, reread the growing context. Each reread is [prefill](../../glossary.md#prefill); each new thought is decode ([Primer P2](../../primers/P2-how-ai-inference-works.md)). NVIDIA's CEO said in 2025 that reasoning and agents need easily 100× the computation expected a year earlier (🟡 vendor claim) [[S33020]](../../sources/bibliography.md#s33020).

![Illustrative log-scale bars of tokens per task: a chat reply reads about 600 tokens and generates 400; a reasoning answer generates about 8,400 (mostly hidden thinking), 21 times more; a 30-turn agentic coding task re-reads about 1.05 million context tokens and generates about 45 thousand, roughly 1,095 times the chat total.](../../assets/charts/P2-reasoning-token-multiplier.svg)

> [!TIP]
> **Worked example — what one agentic coding task costs to serve.** The repo's illustrative task reads ~1.05M context tokens and generates ~45k (Est.) [[S32025]](../../sources/bibliography.md#s32025).
>
> | | GB300 NVL72 | H200 |
> |---|---|---|
> | Tokens/s per GPU at 50 tokens/s per user | ~6,261 | ~308 |
> | Owner cost per GPU-hour (Est.) | $2.31 | $1.22 |
> | $ per million tokens = cost ÷ (tokens/s × 3,600) × 10⁶ | ~$0.10 | ~$1.10 |
> | Cost of ~1.1M tokens | ~$0.11 | ~$1.20 |
>
> Inputs [[S621]](../../sources/bibliography.md#s621)[[S622]](../../sources/bibliography.md#s622); arithmetic [[S11000]](../../sources/bibliography.md#s11000). 🔴 Upper bound: cached prefixes make rereads cheaper than decode. The decode alone takes ~15 minutes at 50 tokens/s per user, 5 at 150. **Business reading:** agents reward cheap tokens and fast tokens at once, which favors the newest racks.

## Latency vs throughput: the frontier

**Mechanism.** A GPU serves many users at once by [batching](../../glossary.md#batching) them. Bigger batches raise tokens per GPU but slow each user, because every decode step waits for the whole batch. Plot each configuration as tokens/s per user ([interactivity](../../glossary.md#interactivity)) against tokens/s per GPU; the upper envelope is the [Pareto frontier](../../glossary.md#pareto-frontier).

![Log-scale Pareto chart of total tokens per second per GPU against tokens per second per user for eight systems on DeepSeek-R1. Interpolated at 50 tok/s/user: GB300 NVL72 about 6,261, GB200 NVL72 about 4,625, B300 about 2,982, B200 about 1,387, MI355X about 738, H200 about 308 tokens/s per GPU. Rack-scale NVL72 systems dominate the low-to-mid interactivity range; all curves fall steeply as interactivity rises.](../../assets/charts/11-throughput-vs-interactivity-pareto.svg)

> [!TIP]
> **Worked example — why a fast tier must cost ~11× more.** GB300 NVL72 delivers ~6,261 tokens/s per GPU at 50 tokens/s per user and ~562 at 100 (interpolated) [[S621]](../../sources/bibliography.md#s621). At a fixed $2.31 per GPU-hour [[S622]](../../sources/bibliography.md#s622), cost per million tokens rises from ~$0.10 to ~$1.14 (Est.) [[S11000]](../../sources/bibliography.md#s11000). **Business reading:** doubling reading speed for premium users needs ~11× the price per token to earn the same per GPU-hour.

**[Q1 · Job & failure mode]** This layer converts GPU-hours into tokens at each latency tier. When it is weak, the same silicon yields fewer tokens: MLPerf throughput on an unchanged GB300 NVL72 differed 2.9× between September 2025 and September 2026 software [[S601]](../../sources/bibliography.md#s601)[[S603]](../../sources/bibliography.md#s603).

**[Q2 · Metrics that matter]**

| Metric | Why it matters | Example value |
|---|---|---|
| Tokens/s per GPU at a stated tokens/s per user | Revenue capacity of a GPU at a product tier | GB300 NVL72 ~6,261 at 50 [[S621]](../../sources/bibliography.md#s621) |
| Tokens/s per MW (all-in power) | Revenue capacity of a power-limited site | GB300 NVL72 ~3.0M; H200 ~225k [[S621]](../../sources/bibliography.md#s621)[[S622]](../../sources/bibliography.md#s622) |
| $ per million tokens at a stated interactivity | Unit cost vs API price | GB300 ~$0.10 at 50, ~$1.14 at 100 (Est.) [[S622]](../../sources/bibliography.md#s622) |
| [Time to first token](../../glossary.md#ttft) and [goodput](../../glossary.md#goodput) | Share of traffic meeting latency targets | Dynamo's Planner autoscales to TTFT and inter-token targets [[S11001]](../../sources/bibliography.md#s11001) |
| Tokens per task | Converts users into compute demand | ~21× to ~1,100× a chat reply (Est.) [[S32025]](../../sources/bibliography.md#s32025) |

> [!WARNING]
> **Myth vs. reality:** "Inference is a commodity, so the cheapest chip per FLOP wins." Decode is bound by memory bandwidth, KV capacity and the interconnect, not FLOPs [[S32027]](../../sources/bibliography.md#s32027). At 50 tokens/s per user the NVL72 racks lead MI355X ~8× per GPU [[S621]](../../sources/bibliography.md#s621). Yet on another model at 100 tokens/s per user, Google's TPU was ~18% cheaper than B200 [[S625]](../../sources/bibliography.md#s625). The answer depends on model and tier.

<details>
<summary>🔧 Under the hood: how the InferenceX frontier is measured</summary>

SemiAnalysis's InferenceX runs each system nightly across engines, parallelism settings and concurrency, keeping the best points as the frontier [[S620]](../../sources/bibliography.md#s620)[[S621]](../../sources/bibliography.md#s621). Throughput counts input plus output tokens per GPU; interactivity is the median tokens/s per user. Cost per million tokens divides SemiAnalysis's owner TCO per GPU-hour by throughput [[S622]](../../sources/bibliography.md#s622): an estimate, not a price.

</details>

## Tokens per second per megawatt: the AI-factory metric

A site has a fixed grid connection, so the scarce input is power. NVIDIA therefore sells an [AI factory](../../glossary.md#ai-factory) by its [tokens per second per megawatt](../../glossary.md#tokens-per-megawatt).

![Log-scale bar chart of DeepSeek-R1 tokens per second per megawatt of all-in power at 50 tokens/s per user (InferenceX frontier divided by SemiAnalysis power per GPU): H100 about 29 thousand, H200 about 225 thousand, B200 about 0.8 million, B300 about 1.6 million, GB200 NVL72 about 2.5 million and GB300 NVL72 about 3.0 million, ~13 times H200; AMD MI300X about 117 thousand and MI355X about 353 thousand.](../../assets/charts/08-tokens-per-mw-by-system.svg)

> [!TIP]
> **Worked example — what a 100 MW site produces.** GB300 NVL72 draws ~2.12 kW per GPU all-in, so ~6,261 tokens/s per GPU becomes ~2.95M tokens/s per MW [[S621]](../../sources/bibliography.md#s621)[[S622]](../../sources/bibliography.md#s622). A 100 MW site at full load makes ~295M tokens/s, ~765 trillion in a 30-day month: ~59% of Google's October 2025 monthly volume [[S32020]](../../sources/bibliography.md#s32020). Filled with H200s it makes ~58 trillion. 🔴 Full utilization on one workload assumed. **Business reading:** when power is fixed, a newer rack is a capacity expansion, not just a cost cut.


## How much of NVIDIA's revenue is inference?

![Bar chart of trailing-twelve-month NVIDIA Data Center revenue. To Q4 FY2024 $47.5B, of which about 40% (~$19B) was inference by management's estimate; to Q2 FY2025 $81.8B with more than 40% (at least ~$33B) inference. Later bars, FY2025 $115.2B, FY2026 $193.7B and the year to Q2 FY2027 $277.7B, have no disclosed split; a dotted marker shows what 40% would be ($111B for the latest year) purely for scale. Management now calls inference the main growth driver without giving a percentage.](../../assets/charts/11-inference-share-of-dc-revenue.svg)

> [!TIP]
> **Worked example — implied inference revenue.** The CFO estimated ~40% of the year to Q4 FY2024 (~$47.5B) was inference, about $19B [[S9516]](../../sources/bibliography.md#s9516)[[S439]](../../sources/bibliography.md#s439). For the year to Q2 FY2025 she said "more than 40%" of ~$81.8B, so at least ~$33B [[S11011]](../../sources/bibliography.md#s11011)[[S441]](../../sources/bibliography.md#s441). Data Center revenue then reached $277.7B for the year to Q2 FY2027 [[S405]](../../sources/bibliography.md#s405)[[S403]](../../sources/bibliography.md#s403)[[S402]](../../sources/bibliography.md#s402). 🔴 Had the share merely held, inference would be ~$111B. **Business reading:** the direction is clear; the size is a model, not a disclosure.

The split is soft. The same GPUs train and serve, and reinforcement-learning post-training generates huge numbers of rollout tokens: inference work booked as training (🔴 repo analysis).

> [!NOTE]
> **🐂 Bull view.** Tokens per task compound with reasoning and agents [[S32025]](../../sources/bibliography.md#s32025). Interactivity tiers reward the newest racks, and software keeps raising the installed base's output [[S603]](../../sources/bibliography.md#s603). NVIDIA leads the recurring market on tokens per MW [[S621]](../../sources/bibliography.md#s621)[[S622]](../../sources/bibliography.md#s622).

> [!WARNING]
> **🐻 Bear view.** Inference splits into small, independent jobs that do not need NVIDIA's training fabric. Cost per token is easy to benchmark and multi-source, which TPUs and custom ASICs exploit [[S625]](../../sources/bibliography.md#s625). Sparse models, FP4 and caching may cut hardware per token faster than demand grows.

## 🎯 Corp Dev Lens

1. **Price follows the latency tier.** Cost per token rises ~11× between 50 and 100 tokens/s per user on the same rack (Est.) [[S622]](../../sources/bibliography.md#s622). Which customers pay for fast tiers, and where can a cheaper accelerator win at relaxed latency?
2. **Tokens per MW is the procurement metric.** A challenger needs independent, workload-matched numbers on this axis. How would Qualcomm's AI200 and AI250 [[S173]](../../sources/bibliography.md#s173) show up on it?
3. **The inference share is undisclosed.** Any training-vs-inference revenue split rests on 2024 data [[S11011]](../../sources/bibliography.md#s11011). What would update it: hyperscaler commentary, benchmark volumes, token disclosures?
4. **Agents change the product.** Long-lived contexts favor capacity, KV offload and fast networks. Which memory, storage and NIC suppliers gain regardless of the accelerator?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S113**](../../sources/bibliography.md#s113) Tom's Hardware, *How Nvidia's $20 billion Groq 3 LPU deal reshapes the Nvidia Vera Rubin Platform*, 2026-03. [Link](https://www.tomshardware.com/tech-industry/semiconductors/nvidias-20-billion-groq-deal-produces-its-first-chip)
- [**S173**](../../sources/bibliography.md#s173) Qualcomm, *Qualcomm Unveils AI200 and AI250 - Redefining Rack-Scale Data Center Inference*, 2025-10-27. [Link](https://www.qualcomm.com/news/releases/2025/10/qualcomm-unveils-ai200-and-ai250-redefining-rack-scale-data-cent)
- [**S402**](../../sources/bibliography.md#s402) NVIDIA Corporation via SEC EDGAR (Colette Kress), *CFO Commentary on Fourth Quarter and Fiscal 2026 Results (Form 8-K exhibit 99.2)*, 2026-02-25. [Link](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000019/q4fy26cfocommentary.htm)
- [**S403**](../../sources/bibliography.md#s403) NVIDIA Corporation via SEC EDGAR, *NVIDIA Announces Financial Results for First Quarter Fiscal 2027 (Form 8-K exhibit 99.1)*, 2026-05-20. [Link](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000051/q1fy27pr.htm)
- [**S405**](../../sources/bibliography.md#s405) NVIDIA Corporation via SEC EDGAR, *NVIDIA Announces Financial Results for Second Quarter Fiscal 2027 (Form 8-K exhibit 99.1)*, 2026-08-26. [Link](https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000073/q2fy27pr.htm)
- [**S409**](../../sources/bibliography.md#s409) NVIDIA Corporation, *NVIDIA Corp. (NVDA) Q1 Fiscal 2027 earnings call transcript (20 May 2026)*, 2026-05-20. [Link](https://s201.q4cdn.com/141608511/files/doc_financials/2027/q1/NVDA-Q1-2027-Earnings-Call-20-May-2026-5_00-PM-ET.pdf)
- [**S439**](../../sources/bibliography.md#s439) NVIDIA Corporation, *NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2024 (press release with CFO commentary)*, 2024-02-21. [Link](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2024)
- [**S441**](../../sources/bibliography.md#s441) NVIDIA Corporation, *NVIDIA Announces Financial Results for Second Quarter Fiscal 2025 (press release with CFO commentary)*, 2024-08-28. [Link](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2025)
- [**S601**](../../sources/bibliography.md#s601) MLCommons, *MLPerf Inference v5.1 results (summary_results.json and per-submitter logs)*, 2025-09-09. [Link](https://github.com/mlcommons/inference_results_v5.1)
- [**S603**](../../sources/bibliography.md#s603) MLCommons, *MLPerf Inference v6.1 results (summary.csv and per-submitter logs)*, 2026-09. [Link](https://github.com/mlcommons/inference_results_v6.1)
- [**S620**](../../sources/bibliography.md#s620) SemiAnalysis, *SemiAnalysis InferenceX (formerly InferenceMAX) open-source benchmark repository*, 2026-11. [Link](https://github.com/SemiAnalysisAI/InferenceX)
- [**S621**](../../sources/bibliography.md#s621) SemiAnalysis (InferenceX-app repository), *InferenceX public API snapshot (benchmarks.json and benchmarks-history.json fixtures)*, 2026-10-17. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/tree/main/packages/app/cypress/fixtures/api)
- [**S622**](../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S625**](../../sources/bibliography.md#s625) SemiAnalysis, *TPU Inference Externalization Full Steam Ahead*, 2026-09-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/tpu-inferencex-full-steam.mdx)
- [**S9516**](../../sources/bibliography.md#s9516) MarketBeat, *NVIDIA Q4 FY2024 earnings call transcript*, 2024-02-21. [Link](https://www.marketbeat.com/earnings/reports/2024-2-21-nvidia-co-stock)
- [**S11000**](../../sources/bibliography.md#s11000) nvidia_deep_dive_claude repository, *Repo analysis: layer 11 inference models (disaggregation comparison, cost per million tokens across software releases, implied inference revenue, tokens per MW and per-request economics)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/layers/11-inference-and-ai-software/index.md)
- [**S11001**](../../sources/bibliography.md#s11001) NVIDIA (GitHub), *NVIDIA Dynamo README (ai-dynamo/dynamo)*, 2026-11. [Link](https://github.com/ai-dynamo/dynamo/blob/main/README.md)
- [**S11011**](../../sources/bibliography.md#s11011) MarketBeat, *NVIDIA Q2 Fiscal 2025 earnings call transcript (28 August 2024)*, 2024-08-28. [Link](https://www.marketbeat.com/earnings/transcripts/110080/)
- [**S32018**](../../sources/bibliography.md#s32018) Google (The Keyword) (Sundar Pichai), *Google I/O 2025 keynote remarks (Sundar Pichai)*, 2025-05-20. [Link](https://blog.google/technology/ai/io-2025-keynote/)
- [**S32020**](../../sources/bibliography.md#s32020) Alphabet / Google (The Keyword) (Sundar Pichai), *Alphabet CEO remarks on token volume (October 2025)*, 2025-10. [Link](https://blog.google/inside-google/message-ceo/alphabet-earnings-q3-2025/)
- [**S32024**](../../sources/bibliography.md#s32024) OpenAI, *Reasoning models guide (OpenAI API documentation)*, 2025. [Link](https://platform.openai.com/docs/guides/reasoning)
- [**S32025**](../../sources/bibliography.md#s32025) nvidia_deep_dive_claude repository, *Repo analysis: inference token-budget scenarios and roofline serving model (Primer P2)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/primers/P2-how-ai-inference-works.md)
- [**S32027**](../../sources/bibliography.md#s32027) NVIDIA Technical Blog, *Mastering LLM Techniques: Inference Optimization*, 2023-11. [Link](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/)
- [**S33020**](../../sources/bibliography.md#s33020) NVIDIA (Jensen Huang), *NVIDIA GTC 2025 keynote (Jensen Huang)*, 2025-03-18. [Link](https://www.nvidia.com/gtc/keynote/)
- [**S90001**](../../sources/bibliography.md#s90001) The Star (Reuters), *Nvidia bets on AI inference as chip revenue opportunity hits $1 trillion (Reuters)*, 2026-03-17. [Link](https://www.thestar.com.my/tech/tech-news/2026/03/17/nvidia-bets-on-ai-inference-as-chip-revenue-opportunity-hits-1-trillion)
- [**S90003**](../../sources/bibliography.md#s90003) eWeek, *Everything Nvidia Just Announced at GTC 2026: 7 Chips, 5 Racks, 1 Giant Bet on Agentic AI*, 2026-03-17. [Link](https://www.eweek.com/news/nvidia-gtc-2026-ai-inference-vera-rubin-neuron/)
