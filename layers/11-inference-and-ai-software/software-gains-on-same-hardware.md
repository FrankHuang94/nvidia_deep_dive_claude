# Software gains on the same hardware

<sub>Layer 11 · Inference and AI software · ~8 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **Installed GPUs keep getting faster after purchase.** In MLPerf Inference an unchanged GB300 [NVL72](../../glossary.md#nvl72) went from 2,907 to 8,291 DeepSeek-R1 tokens/s per GPU between September 2025 and September 2026, 2.9×; GB200 NVL72 rose 2.4× [[S601]](../../sources/bibliography.md#s601)[[S603]](../../sources/bibliography.md#s603).
- **New architectures leave the most headroom.** NVIDIA's B200 numbers for DeepSeek-R1 rose 5.5× in minimum-latency speed and 2.3× in peak throughput within months [[S645]](../../sources/bibliography.md#s645)[[S646]](../../sources/bibliography.md#s646). Dense Llama 70B stayed within ~8% across four [TensorRT-LLM](../../glossary.md#tensorrt-llm) releases [[S641]](../../sources/bibliography.md#s641)[[S644]](../../sources/bibliography.md#s644).
- **Software gains are cost cuts.** At a fixed owner cost per [GPU-hour](../../glossary.md#gpu-hour), estimated cost per million tokens fell 65% on GB300 ($0.22 → $0.08) and 57% on B200 ($0.24 → $0.10) (Est.) [[S622]](../../sources/bibliography.md#s622)[[S603]](../../sources/bibliography.md#s603)[[S646]](../../sources/bibliography.md#s646).
- **On a 1,008-GPU GB300 fleet a 2.85× gain avoids ~$100M of capex**, the price of ~1,865 extra GPUs at the old software (Est.) [[S332]](../../sources/bibliography.md#s332)[[S11000]](../../sources/bibliography.md#s11000).
- **The gains are not NVIDIA-only.** In independent nightly runs B200 on [SGLang](../../glossary.md#sglang) improved 34% in six months and AMD's MI355X 29% [[S621]](../../sources/bibliography.md#s621). AMD reported up to 19× on Qwen3.5 in three months [[S632]](../../sources/bibliography.md#s632).
- **Headlines mix hardware and software.** [Dynamo](../../glossary.md#dynamo)'s "7× per GPU" compares GB200 NVL72 with Dynamo to B200 without [[S11001]](../../sources/bibliography.md#s11001); the bigger [NVLink](../../glossary.md#nvlink) domain alone accounts for ~3.5× (🔴 rough split) [[S621]](../../sources/bibliography.md#s621).

![Log-scale line chart of estimated cost per million tokens on unchanged NVIDIA hardware as software improved, holding each GPU's owner TCO fixed (SemiAnalysis: GB300 $2.31, GB200 $1.86, B200 $1.73, H100 $1.17 per GPU-hour). GB300 NVL72 · DeepSeek-R1 (MLPerf Server): $0.221 to $0.077 (65% lower, Sep 2025 to Sep 2026); GB200 NVL72 · DeepSeek-R1 (MLPerf Server): $0.222 to $0.094 (58% lower, Sep 2025 to Sep 2026); H100 · Llama 2 70B (MLPerf Server): $0.126 to $0.084 (34% lower, Mar 2024 to Apr 2025); B200 · DeepSeek-R1 max throughput (TensorRT-LLM blog): $0.240 to $0.104 (57% lower, Feb 2025 to May 2025); B200 · DeepSeek-R1, SGLang conc 128 (InferenceX): $0.269 to $0.201 (25% lower, Dec 2025 to May 2026). The hardware bill did not change; throughput per GPU did, so cost per token fell.](../../assets/charts/11-cost-per-m-tokens-software-releases.svg)

## Where the gains come from

**Analogy.** New silicon is a new highway. Software is the traffic management that arrives later: lane markings, ramp meters, express lanes. The road is unchanged, but cars per hour can double.

**Mechanism.** A GPU ships tuned for yesterday's models. Each new architecture needs new work: latent attention, mixture-of-experts routing, [FP4](../../glossary.md#fp4) recipes, multi-token prediction. NVIDIA's DeepSeek-R1 work on B200 combined custom attention and [MoE](../../glossary.md#mixture-of-experts) kernels, wider [expert parallelism](../../glossary.md#expert-parallelism), [CUDA graphs](../../glossary.md#cuda-graphs) and multi-token prediction [[S645]](../../sources/bibliography.md#s645)[[S646]](../../sources/bibliography.md#s646). Rack-scale gains then came from disaggregated serving through Dynamo, listed in NVIDIA's v6.0 MLPerf software stack [[S602]](../../sources/bibliography.md#s602).

![Line chart of MLPerf Inference per-GPU throughput for unchanged NVIDIA hardware across rounds. GB300 NVL72 on DeepSeek-R1 Server rose from 2,907 to 8,291 tokens/s per GPU (2.9x, Sep 2025 to Sep 2026); GB200 NVL72 2.4x; GB300 on Llama 3.1 405B 1.5x; H100 on Llama 2 70B 1.44x and H200 1.26x over a year. Gains come from TensorRT-LLM, Dynamo and newer serving recipes, not new silicon.](../../assets/charts/11-mlperf-same-hardware-software-gains.svg)

> [!TIP]
> **Worked example — why young models gain most.** Llama 70B-class models have run on [CUDA](../../glossary.md#cuda) since 2023; across four 2025 TensorRT-LLM releases, B200 throughput on Llama 3.3 70B stayed between ~6,434 and ~7,007 tokens/s per GPU [[S641]](../../sources/bibliography.md#s641)[[S642]](../../sources/bibliography.md#s642)[[S643]](../../sources/bibliography.md#s643)[[S644]](../../sources/bibliography.md#s644). DeepSeek-R1, a 671B mixture-of-experts reasoning model, gained 2.3× in throughput and 5.5× in minimum-latency speed on the same B200s in about four months [[S645]](../../sources/bibliography.md#s645)[[S646]](../../sources/bibliography.md#s646). **Business reading:** software gains recur with every new model family, and each family is a reason to stay on the platform that tunes it first.

![Line chart of NVIDIA-published performance on the same GPUs over time. B200 DeepSeek-R1 minimum-latency speed rose from 67 to 368 tokens/s per user (5.5x, Jan-May 2025); B200 DeepSeek-R1 max throughput from 2,000 to 4,600 tokens/s per GPU (2.3x); GB300 NVL72 MLPerf DeepSeek-R1 Server 2.9x in a year; while B200 Llama 3.3 70B max throughput stayed within 8% across four TensorRT-LLM releases. MoE models gain most from software.](../../assets/charts/11-software-gains-same-gpu.svg)

**[Q3 · Generational progress]** Two axes compound. **Hardware generations** moved the DeepSeek-R1 frontier at 50 tokens/s per user from ~308 tokens/s per GPU on H200 to ~6,261 on GB300 NVL72, ~20× [[S621]](../../sources/bibliography.md#s621). **Software generations** then added ~2.9× on the same GB300 within a year [[S603]](../../sources/bibliography.md#s603).

<details>
<summary>🔧 Under the hood: what MLPerf's "Server" scenario measures</summary>

MLPerf Inference's closed division fixes the model and an accuracy target, so submitters cannot trade quality for speed [[S600]](../../sources/bibliography.md#s600). *Offline* measures raw throughput with all queries available. *Server* sends queries at random times and enforces latency limits, including time to first token and time per output token. NVIDIA's v6.0 GB300 submission added Dynamo to the software list [[S602]](../../sources/bibliography.md#s602).

</details>

## What a 2–3× software gain is worth

> [!TIP]
> **Worked example — a 1,008-GPU GB300 fleet (14 NVL72 racks).**
>
> | | Sept 2025 software | Sept 2026 software |
> |---|---|---|
> | MLPerf DeepSeek-R1 Server, tokens/s per GPU | 2,907 | 8,291 |
> | Owner cost per GPU-hour (Est.) | $2.31 | $2.31 |
> | Fleet cost per year (× 8,760 h) | ~$20.4M | ~$20.4M |
> | Tokens per year at 70% utilization | ~65 trillion | ~185 trillion |
> | Cost per million tokens | ~$0.32 | ~$0.11 |
> | Gross profit at an illustrative $0.40 per million | ~$5.5M | ~$53M |
>
> Inputs [[S601]](../../sources/bibliography.md#s601)[[S603]](../../sources/bibliography.md#s603)[[S622]](../../sources/bibliography.md#s622); utilization and price are 🔴 illustrative; arithmetic [[S11000]](../../sources/bibliography.md#s11000). With the old software the same output would need ~2,870 GPUs, ~1,865 more. At ~$4.0M per rack (~$55K per GPU, Est., Morgan Stanley) [[S332]](../../sources/bibliography.md#s332) that is ~$100M of avoided capex. **Business reading:** software turns a marginal deployment into a strong one, and keeps NVIDIA's installed base from being replaced by cheaper chips.

Two forces cap the customer's windfall. Token prices fall as everyone's software improves, passing gains to end users. And many gains arrive through open engines (SGLang, [vLLM](../../glossary.md#vllm)) that rivals use too [[S621]](../../sources/bibliography.md#s621)[[S580]](../../sources/bibliography.md#s580)[[S582]](../../sources/bibliography.md#s582). NVIDIA's durable benefit is subtler: every lift raises the bar a competing chip must clear on cost per token.

> [!WARNING]
> **Myth vs. reality:** "Software gains are an NVIDIA moat on their own." AMD gets them too: MI355X on SGLang improved 29% in six months [[S621]](../../sources/bibliography.md#s621) and up to 19× on Qwen3.5 397B in three months [[S632]](../../sources/bibliography.md#s632). NVIDIA's edge is that its gains usually land first, on day 0 of a new model ([Layer 09](../09-cuda-and-system-software/index.md)).

![Line chart of InferenceX nightly runs with unchanged hardware and settings, Dec 2025 to Jun 2026. B200 · SGLang FP4 (conc 128) +34%; B200 · TensorRT-LLM FP4 (conc 256) +17%; H200 · SGLang FP8 (conc 64) +7%; MI355X · SGLang FP4 (conc 64) +29%; MI300X · SGLang FP8 (conc 64) +1%. Open-source engine updates (SGLang, TensorRT-LLM, ROCm/AITER) deliver double-digit gains on fixed silicon for both vendors, while older CDNA 3 parts saw regressions before recovering.](../../assets/charts/11-inferencex-same-hardware-history.svg)

## Reading vendor benchmarks

| Claim type | What to check | Example |
|---|---|---|
| "N× faster" | Same hardware as the baseline? | Dynamo "7×" is GB200 NVL72 with Dynamo vs B200 without [[S11001]](../../sources/bibliography.md#s11001) |
| Peak throughput | At what tokens/s per user? | GB300 ~6,261 at 50 but ~562 at 100 [[S621]](../../sources/bibliography.md#s621) |
| Per-GPU numbers | Counting prefill and decode pools? | Disaggregated B200 point used 44 GPUs [[S621]](../../sources/bibliography.md#s621) |
| Precision | FP4 or FP8, accuracy held? | MLPerf closed division fixes accuracy [[S600]](../../sources/bibliography.md#s600) |
| Tokens | Input plus output, or output only? | InferenceX counts both; NVIDIA blogs often output only [[S621]](../../sources/bibliography.md#s621)[[S646]](../../sources/bibliography.md#s646) |
| Cost per token | Owner or rental TCO? | $2.31 owner vs ~$5.00 rental per GB300-hour [[S622]](../../sources/bibliography.md#s622) |

> [!TIP]
> **Worked example — splitting a headline into hardware and software.** Dynamo's README cites 7× higher throughput per GPU on DeepSeek-R1, GB200 NVL72 with Dynamo vs B200 without [[S11001]](../../sources/bibliography.md#s11001). InferenceX shows a 72-GPU NVLink domain alone worth ~3.5× over 8-GPU B200 at ~49 tokens/s per user [[S621]](../../sources/bibliography.md#s621). That leaves ~2× for Dynamo, disaggregation and tuning (🔴 rough split; operating points differ). **Business reading:** ask every "N×" claim how much needs new hardware and how much a software update gives the installed fleet.

## 🎯 Corp Dev Lens

1. **Software lift is a retention tool.** A 2–3× lift on installed GPUs [[S603]](../../sources/bibliography.md#s603) postpones replacement. How does that change the payback a challenger must promise to displace an installed rack?
2. **Benchmarks are a battleground.** MLPerf, InferenceX and vendor blogs measure different things [[S600]](../../sources/bibliography.md#s600)[[S621]](../../sources/bibliography.md#s621)[[S646]](../../sources/bibliography.md#s646). Is there value in backing neutral benchmarking or tuning services?
3. **Day-0 tuning capacity is the scarce asset.** Gains concentrate in the months after a model launches [[S645]](../../sources/bibliography.md#s645)[[S646]](../../sources/bibliography.md#s646). Kernel teams that move fast on new architectures are the talent pool that matters.
4. **Depreciation logic shifts.** A 2–3× post-purchase lift supports the 5–6-year server lives most [hyperscalers](../../glossary.md#hyperscaler) now use [[S382]](../../sources/bibliography.md#s382)[[S383]](../../sources/bibliography.md#s383)[[S384]](../../sources/bibliography.md#s384). Amazon cut some back to 5 years in 2025 [[S385]](../../sources/bibliography.md#s385). Does the logic hold for Hopper fleets, which gained less [[S621]](../../sources/bibliography.md#s621)?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S382**](../../sources/bibliography.md#s382) Microsoft via SEC EDGAR, *Microsoft Corporation Form 10-K filings (FY2021, FY2023) - property and equipment useful lives*, 2023-07-27. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K&dateb=&owner=include&count=40)
- [**S383**](../../sources/bibliography.md#s383) Alphabet via SEC EDGAR, *Alphabet Inc. Form 10-K filings (FY2020, FY2022) - useful lives of servers and network equipment*, 2023-02-03. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K&dateb=&owner=include&count=40)
- [**S384**](../../sources/bibliography.md#s384) Meta via SEC EDGAR, *Meta Platforms Form 10-K filings (FY2022, FY2024) - useful lives of servers and network assets*, 2025-01-30. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K&dateb=&owner=include&count=40)
- [**S385**](../../sources/bibliography.md#s385) Amazon via SEC EDGAR, *Amazon.com Form 10-K filings (FY2019-FY2024) - useful lives of servers*, 2025-02-07. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K&dateb=&owner=include&count=40)
- [**S580**](../../sources/bibliography.md#s580) vLLM project (GitHub), *vLLM README and installation docs — supported hardware*, 2026-11. [Link](https://github.com/vllm-project/vllm/blob/main/docs/getting_started/installation/README.md)
- [**S582**](../../sources/bibliography.md#s582) SGLang project (GitHub: sgl-project/sglang), *SGLang README — supported hardware*, 2026-11. [Link](https://github.com/sgl-project/sglang/blob/main/README.md)
- [**S600**](../../sources/bibliography.md#s600) MLCommons, *MLPerf Inference v5.0 results (summary_results.json and per-submitter logs)*, 2025-04-02. [Link](https://github.com/mlcommons/inference_results_v5.0)
- [**S601**](../../sources/bibliography.md#s601) MLCommons, *MLPerf Inference v5.1 results (summary_results.json and per-submitter logs)*, 2025-09-09. [Link](https://github.com/mlcommons/inference_results_v5.1)
- [**S602**](../../sources/bibliography.md#s602) MLCommons, *MLPerf Inference v6.0 results (summary_results.json and per-submitter logs)*, 2026-04-01. [Link](https://github.com/mlcommons/inference_results_v6.0)
- [**S603**](../../sources/bibliography.md#s603) MLCommons, *MLPerf Inference v6.1 results (summary.csv and per-submitter logs)*, 2026-09. [Link](https://github.com/mlcommons/inference_results_v6.1)
- [**S621**](../../sources/bibliography.md#s621) SemiAnalysis (InferenceX-app repository), *InferenceX public API snapshot (benchmarks.json and benchmarks-history.json fixtures)*, 2026-10-17. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/tree/main/packages/app/cypress/fixtures/api)
- [**S622**](../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S632**](../../sources/bibliography.md#s632) SemiAnalysis, *AMD MI355X Qwen3.5 397B-A17B Inference: Up to 19x Throughput per GPU in 3 Months on SGLang FP8*, 2026-05-25. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/mi355x-qwen3-5-sglang-v0-5-12-up-to-17x.mdx)
- [**S641**](../../sources/bibliography.md#s641) NVIDIA, *TensorRT-LLM performance overview (release 0.19)*, 2025-05-16. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/df1943062933caad9c72c615d0fde9f3df591eb2/docs/source/performance/perf-overview.md)
- [**S642**](../../sources/bibliography.md#s642) NVIDIA, *TensorRT-LLM performance overview (release 0.21)*, 2025-07-30. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/18d19410831ecdec0d97c76401a1bf40b935c992/docs/source/performance/perf-overview.md)
- [**S643**](../../sources/bibliography.md#s643) NVIDIA, *TensorRT-LLM performance overview (release 1.0)*, 2025-09-21. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/c38d4cf6a66370f8fd58a517f398e12c7981fcf8/docs/source/legacy/performance/perf-overview.md)
- [**S644**](../../sources/bibliography.md#s644) NVIDIA, *TensorRT-LLM performance overview (release 1.1)*, 2025-12-09. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/1ffa2c893720ca2c3c6d245829b0c493485d21a6/docs/source/developer-guide/perf-overview.md)
- [**S645**](../../sources/bibliography.md#s645) NVIDIA TensorRT-LLM team, *Pushing Latency Boundaries: Optimizing DeepSeek-R1 Performance on NVIDIA B200 GPUs (TensorRT-LLM tech blog 1)*, 2025-05-16. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/blogs/tech_blog/blog01_Pushing_Latency_Boundaries_Optimizing_DeepSeek-R1_Performance_on_NVIDIA_B200_GPUs.md)
- [**S646**](../../sources/bibliography.md#s646) NVIDIA TensorRT-LLM team, *Optimizing DeepSeek R1 Throughput on NVIDIA Blackwell GPUs: A Deep Dive for Developers (TensorRT-LLM tech blog 3)*, 2025-05-30. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/blogs/tech_blog/blog03_Optimizing_DeepSeek_R1_Throughput_on_NVIDIA_Blackwell_GPUs.md)
- [**S11000**](../../sources/bibliography.md#s11000) nvidia_deep_dive_claude repository, *Repo analysis: layer 11 inference models (disaggregation comparison, cost per million tokens across software releases, implied inference revenue, tokens per MW and per-request economics)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/layers/11-inference-and-ai-software/index.md)
- [**S11001**](../../sources/bibliography.md#s11001) NVIDIA (GitHub), *NVIDIA Dynamo README (ai-dynamo/dynamo)*, 2026-11. [Link](https://github.com/ai-dynamo/dynamo/blob/main/README.md)
