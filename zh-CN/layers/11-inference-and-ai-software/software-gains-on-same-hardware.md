# 同一硬件上的软件增益

> [!NOTE]
> 本页为英文原文的简体中文参考译文，仅供参考；如有出入，以[英文原文](../../../layers/11-inference-and-ai-software/software-gains-on-same-hardware.md "English original")为准。

<sub>第 11 层 · 推理与 AI 软件 · 约 8 分钟阅读 · 最近核实：2026-11-05</sub>

## ⚡ 要点速览

- **已部署的 GPU 在购买后还会持续变快。** 在 MLPerf Inference 中，硬件不变的 GB300 [NVL72](../../glossary.md#nvl72) 在 2025 年 9 月至 2026 年 9 月间，DeepSeek-R1 每 GPU 吞吐量从 2,907 提升到 8,291 tokens/s，增长 2.9×；GB200 NVL72 提升 2.4× [[S601]](../../../sources/bibliography.md#s601)[[S603]](../../../sources/bibliography.md#s603)。
- **新架构的提升空间最大。** 英伟达（NVIDIA）公布的 B200 运行 DeepSeek-R1 数据，在数月之内最低延迟速度提升 5.5×，峰值吞吐量提升 2.3× [[S645]](../../../sources/bibliography.md#s645)[[S646]](../../../sources/bibliography.md#s646)。稠密模型 Llama 70B 在四个 [TensorRT-LLM](../../glossary.md#tensorrt-llm) 版本中的变化幅度则保持在 ~8% 以内 [[S641]](../../../sources/bibliography.md#s641)[[S644]](../../../sources/bibliography.md#s644)。
- **软件增益就是成本削减。** 在每 [GPU 小时](../../glossary.md#gpu-hour)所有者成本固定的前提下，估计每百万 token 成本在 GB300 上下降 65%（$0.22 → $0.08），在 B200 上下降 57%（$0.24 → $0.10）（估计）[[S622]](../../../sources/bibliography.md#s622)[[S603]](../../../sources/bibliography.md#s603)[[S646]](../../../sources/bibliography.md#s646)。
- **对一个 1,008 块 GPU 的 GB300 机群而言，2.85× 的增益可避免 ~$100M 的资本开支**，相当于在旧软件下需额外购置的 ~1,865 块 GPU 的价格（估计）[[S332]](../../../sources/bibliography.md#s332)[[S11000]](../../../sources/bibliography.md#s11000)。
- **这些增益并非英伟达独享。** 在独立的每晚测试中，B200 在 [SGLang](../../glossary.md#sglang) 上六个月内提升 34%，AMD 的 MI355X 提升 29% [[S621]](../../../sources/bibliography.md#s621)。AMD 报告其在 Qwen3.5 上三个月内最高提升 19× [[S632]](../../../sources/bibliography.md#s632)。
- **宣传数字往往混合了硬件与软件。** [Dynamo](../../glossary.md#dynamo) 的“每 GPU 7×”是拿使用 Dynamo 的 GB200 NVL72 与未使用 Dynamo 的 B200 相比 [[S11001]](../../../sources/bibliography.md#s11001)；仅更大的 [NVLink](../../glossary.md#nvlink) 域一项就贡献了 ~3.5×（🔴 粗略拆分）[[S621]](../../../sources/bibliography.md#s621)。

![对数坐标折线图：在硬件不变、每块 GPU 的所有者 TCO 固定的前提下（SemiAnalysis：GB300 $2.31、GB200 $1.86、B200 $1.73、H100 $1.17 每 GPU 小时），随着软件改进，英伟达硬件的估计每百万 token 成本变化。GB300 NVL72 · DeepSeek-R1（MLPerf Server）：$0.221 降至 $0.077（下降 65%，2025 年 9 月至 2026 年 9 月）；GB200 NVL72 · DeepSeek-R1（MLPerf Server）：$0.222 降至 $0.094（下降 58%，2025 年 9 月至 2026 年 9 月）；H100 · Llama 2 70B（MLPerf Server）：$0.126 降至 $0.084（下降 34%，2024 年 3 月至 2025 年 4 月）；B200 · DeepSeek-R1 最大吞吐量（TensorRT-LLM 博客）：$0.240 降至 $0.104（下降 57%，2025 年 2 月至 2025 年 5 月）；B200 · DeepSeek-R1，SGLang 并发 128（InferenceX）：$0.269 降至 $0.201（下降 25%，2025 年 12 月至 2026 年 5 月）。硬件账单没变，变的是每 GPU 吞吐量，因此每 token 成本下降。](../../../assets/charts/11-cost-per-m-tokens-software-releases.svg)

## 增益从何而来

**类比。** 新芯片好比一条新修的高速公路。软件则是随后到来的交通管理：车道标线、匝道信号灯、快速车道。道路本身没变，但每小时通过的车辆可以翻倍。

**机制。** GPU 出厂时是针对上一代模型调优的。每种新架构都需要新的工作：潜在注意力（latent attention）、混合专家路由、[FP4](../../glossary.md#fp4) 配方、多 token 预测。英伟达在 B200 上针对 DeepSeek-R1 的优化，综合运用了定制注意力与 [MoE](../../glossary.md#mixture-of-experts) 内核、更大范围的[专家并行](../../glossary.md#expert-parallelism)、[CUDA graphs](../../glossary.md#cuda-graphs) 以及多 token 预测 [[S645]](../../../sources/bibliography.md#s645)[[S646]](../../../sources/bibliography.md#s646)。随后，机架级的增益来自通过 Dynamo 实现的分离式服务，它被列入英伟达 v6.0 MLPerf 提交的软件栈中 [[S602]](../../../sources/bibliography.md#s602)。

![折线图：硬件不变的英伟达系统在历轮 MLPerf Inference 中的每 GPU 吞吐量。GB300 NVL72 运行 DeepSeek-R1 Server 从每 GPU 2,907 提升到 8,291 tokens/s（2.9 倍，2025 年 9 月至 2026 年 9 月）；GB200 NVL72 提升 2.4 倍；GB300 运行 Llama 3.1 405B 提升 1.5 倍；一年内 H100 运行 Llama 2 70B 提升 1.44 倍，H200 提升 1.26 倍。增益来自 TensorRT-LLM、Dynamo 和更新的服务配方，而非新芯片。](../../../assets/charts/11-mlperf-same-hardware-software-gains.svg)

> [!TIP]
> **算例 —— 为什么新模型的增益最大。** Llama 70B 级模型自 2023 年起就在 [CUDA](../../glossary.md#cuda) 上运行；在 2025 年的四个 TensorRT-LLM 版本中，B200 运行 Llama 3.3 70B 的吞吐量始终在每 GPU ~6,434 到 ~7,007 tokens/s 之间 [[S641]](../../../sources/bibliography.md#s641)[[S642]](../../../sources/bibliography.md#s642)[[S643]](../../../sources/bibliography.md#s643)[[S644]](../../../sources/bibliography.md#s644)。DeepSeek-R1 是一个 671B 参数的混合专家推理模型，在同样的 B200 上，大约四个月内吞吐量提升 2.3×，最低延迟速度提升 5.5× [[S645]](../../../sources/bibliography.md#s645)[[S646]](../../../sources/bibliography.md#s646)。**商业解读：**每出现一个新的模型家族，软件增益就会再来一次；而每个新家族都是客户继续留在率先完成调优的平台上的理由。

![折线图：英伟达公布的同一 GPU 性能随时间的变化。B200 运行 DeepSeek-R1 的最低延迟速度从每用户 67 提升到 368 tokens/s（5.5 倍，2025 年 1–5 月）；B200 运行 DeepSeek-R1 的最大吞吐量从每 GPU 2,000 提升到 4,600 tokens/s（2.3 倍）；GB300 NVL72 MLPerf DeepSeek-R1 Server 一年提升 2.9 倍；而 B200 运行 Llama 3.3 70B 的最大吞吐量在四个 TensorRT-LLM 版本中变化不超过 8%。MoE 模型从软件中获益最多。](../../../assets/charts/11-software-gains-same-gpu.svg)

**[Q3 · 代际进步]** 两条轴线相互叠加。**硬件代际**把每用户 50 tokens/s 下 DeepSeek-R1 的前沿从 H200 的每 GPU ~308 tokens/s 推升到 GB300 NVL72 的 ~6,261，提升 ~20× [[S621]](../../../sources/bibliography.md#s621)。**软件代际**又在同一 GB300 上一年内追加了 ~2.9× [[S603]](../../../sources/bibliography.md#s603)。

<details>
<summary>🔧 技术细节：MLPerf 的“Server”场景测量什么</summary>

MLPerf Inference 的封闭组（closed division）固定模型和精度目标，因此提交方无法以牺牲质量换取速度 [[S600]](../../../sources/bibliography.md#s600)。*Offline* 场景在所有查询都已就绪的情况下测量原始吞吐量。*Server* 场景在随机时间发送查询，并强制执行延迟上限，包括首 token 延迟和每输出 token 时间。英伟达在 v6.0 的 GB300 提交中把 Dynamo 加入了软件清单 [[S602]](../../../sources/bibliography.md#s602)。

</details>

## 2–3× 的软件增益价值几何

> [!TIP]
> **算例 —— 一个 1,008 块 GPU 的 GB300 机群（14 个 NVL72 机架）。**
>
> | | 2025 年 9 月软件 | 2026 年 9 月软件 |
> |---|---|---|
> | MLPerf DeepSeek-R1 Server，每 GPU tokens/s | 2,907 | 8,291 |
> | 每 GPU 小时所有者成本（估计） | $2.31 | $2.31 |
> | 机群年度成本（× 8,760 h） | ~$20.4M | ~$20.4M |
> | 70% 利用率下的年 token 产量 | ~65 万亿 | ~185 万亿 |
> | 每百万 token 成本 | ~$0.32 | ~$0.11 |
> | 按示意价格每百万 $0.40 计算的毛利 | ~$5.5M | ~$53M |
>
> 输入数据 [[S601]](../../../sources/bibliography.md#s601)[[S603]](../../../sources/bibliography.md#s603)[[S622]](../../../sources/bibliography.md#s622)；利用率和价格为 🔴 示意性假设；计算过程 [[S11000]](../../../sources/bibliography.md#s11000)。若使用旧软件，同样的产出需要 ~2,870 块 GPU，即多出 ~1,865 块。按每机架 ~$4.0M（每 GPU ~$55K，估计，摩根士丹利）[[S332]](../../../sources/bibliography.md#s332) 计算，相当于避免了 ~$100M 的资本开支。**商业解读：**软件能把一个勉强划算的部署变成一个回报可观的部署，并使英伟达的存量设备不易被更便宜的芯片替代。

有两股力量限制了客户的意外之财。其一，随着所有人的软件都在进步，token 价格随之下降，增益被传导给终端用户。其二，许多增益来自竞争对手同样在用的开源引擎（SGLang、[vLLM](../../glossary.md#vllm)）[[S621]](../../../sources/bibliography.md#s621)[[S580]](../../../sources/bibliography.md#s580)[[S582]](../../../sources/bibliography.md#s582)。英伟达的持久收益更为微妙：每一次提升，都会抬高竞争芯片在每 token 成本上必须跨越的门槛。

> [!WARNING]
> **误区与事实：**“软件增益本身就是英伟达的护城河。”AMD 同样能获得这些增益：MI355X 在 SGLang 上六个月内提升 29% [[S621]](../../../sources/bibliography.md#s621)，在 Qwen3.5 397B 上三个月内最高提升 19× [[S632]](../../../sources/bibliography.md#s632)。英伟达的优势在于，它的增益通常最先到来，在新模型发布的第 0 天就已就绪（[第 09 层](../09-cuda-and-system-software/index.md)）。

![折线图：2025 年 12 月至 2026 年 6 月，InferenceX 在硬件和设置均不变情况下的每晚测试结果。B200 · SGLang FP4（并发 128）+34%；B200 · TensorRT-LLM FP4（并发 256）+17%；H200 · SGLang FP8（并发 64）+7%；MI355X · SGLang FP4（并发 64）+29%；MI300X · SGLang FP8（并发 64）+1%。开源引擎更新（SGLang、TensorRT-LLM、ROCm/AITER）在两家厂商的固定芯片上都带来了两位数的增益，而较老的 CDNA 3 产品曾出现性能回退，之后才恢复。](../../../assets/charts/11-inferencex-same-hardware-history.svg)

## 如何解读厂商的基准测试

| 宣传类型 | 需要核查什么 | 示例 |
|---|---|---|
| “快 N×” | 与基线是否为同一硬件？ | Dynamo 的“7×”是使用 Dynamo 的 GB200 NVL72 对比未使用 Dynamo 的 B200 [[S11001]](../../../sources/bibliography.md#s11001) |
| 峰值吞吐量 | 在每用户多少 tokens/s 下？ | GB300 在 50 下为 ~6,261，但在 100 下仅 ~562 [[S621]](../../../sources/bibliography.md#s621) |
| 每 GPU 数值 | 是否同时计入预填充池和解码池？ | 分离式 B200 数据点用了 44 块 GPU [[S621]](../../../sources/bibliography.md#s621) |
| 精度 | FP4 还是 FP8？精度是否保持？ | MLPerf 封闭组固定精度要求 [[S600]](../../../sources/bibliography.md#s600) |
| token 口径 | 输入加输出，还是仅输出？ | InferenceX 两者都计；英伟达博客往往只计输出 [[S621]](../../../sources/bibliography.md#s621)[[S646]](../../../sources/bibliography.md#s646) |
| 每 token 成本 | 所有者 TCO 还是租用 TCO？ | 每 GB300 小时所有者成本 $2.31，租用 ~$5.00 [[S622]](../../../sources/bibliography.md#s622) |

> [!TIP]
> **算例 —— 把一个宣传数字拆分为硬件与软件贡献。** Dynamo 的 README 称，在 DeepSeek-R1 上每 GPU 吞吐量提高 7×，对比对象是使用 Dynamo 的 GB200 NVL72 与未使用 Dynamo 的 B200 [[S11001]](../../../sources/bibliography.md#s11001)。InferenceX 显示，在每用户 ~49 tokens/s 下，仅 72-GPU NVLink 域一项相对 8-GPU B200 就带来 ~3.5× [[S621]](../../../sources/bibliography.md#s621)。剩下的 ~2× 归于 Dynamo、分离式服务和调优（🔴 粗略拆分；工作点不同）。**商业解读：**对每一个“N×”宣传都要追问：多少需要新硬件，多少是软件更新就能为存量机群带来的？

## 🎯 企业发展视角

1. **软件提升是留住客户的工具。** 已部署 GPU 上 2–3× 的提升 [[S603]](../../../sources/bibliography.md#s603) 推迟了更换周期。这会如何改变挑战者为替换一个已部署机架所必须承诺的投资回收期？
2. **基准测试是兵家必争之地。** MLPerf、InferenceX 和厂商博客测量的是不同的东西 [[S600]](../../../sources/bibliography.md#s600)[[S621]](../../../sources/bibliography.md#s621)[[S646]](../../../sources/bibliography.md#s646)。支持中立的基准测试或调优服务是否有价值？
3. **第 0 天调优能力是稀缺资产。** 增益集中在模型发布后的几个月内 [[S645]](../../../sources/bibliography.md#s645)[[S646]](../../../sources/bibliography.md#s646)。能在新架构上快速推进的内核团队才是关键的人才池。
4. **折旧逻辑发生变化。** 购买后 2–3× 的提升，支撑了多数[超大规模云厂商](../../glossary.md#hyperscaler)目前采用的 5–6 年服务器使用寿命 [[S382]](../../../sources/bibliography.md#s382)[[S383]](../../../sources/bibliography.md#s383)[[S384]](../../../sources/bibliography.md#s384)。亚马逊在 2025 年将部分服务器的折旧年限缩回 5 年 [[S385]](../../../sources/bibliography.md#s385)。对于增益较少的 Hopper 机群，这一逻辑是否依然成立 [[S621]](../../../sources/bibliography.md#s621)？

## 📚 来源（Sources）

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S332**](../../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S382**](../../../sources/bibliography.md#s382) Microsoft via SEC EDGAR, *Microsoft Corporation Form 10-K filings (FY2021, FY2023) - property and equipment useful lives*, 2023-07-27. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000789019&type=10-K&dateb=&owner=include&count=40)
- [**S383**](../../../sources/bibliography.md#s383) Alphabet via SEC EDGAR, *Alphabet Inc. Form 10-K filings (FY2020, FY2022) - useful lives of servers and network equipment*, 2023-02-03. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001652044&type=10-K&dateb=&owner=include&count=40)
- [**S384**](../../../sources/bibliography.md#s384) Meta via SEC EDGAR, *Meta Platforms Form 10-K filings (FY2022, FY2024) - useful lives of servers and network assets*, 2025-01-30. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001326801&type=10-K&dateb=&owner=include&count=40)
- [**S385**](../../../sources/bibliography.md#s385) Amazon via SEC EDGAR, *Amazon.com Form 10-K filings (FY2019-FY2024) - useful lives of servers*, 2025-02-07. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K&dateb=&owner=include&count=40)
- [**S580**](../../../sources/bibliography.md#s580) vLLM project (GitHub), *vLLM README and installation docs — supported hardware*, 2026-11. [Link](https://github.com/vllm-project/vllm/blob/main/docs/getting_started/installation/README.md)
- [**S582**](../../../sources/bibliography.md#s582) SGLang project (GitHub: sgl-project/sglang), *SGLang README — supported hardware*, 2026-11. [Link](https://github.com/sgl-project/sglang/blob/main/README.md)
- [**S600**](../../../sources/bibliography.md#s600) MLCommons, *MLPerf Inference v5.0 results (summary_results.json and per-submitter logs)*, 2025-04-02. [Link](https://github.com/mlcommons/inference_results_v5.0)
- [**S601**](../../../sources/bibliography.md#s601) MLCommons, *MLPerf Inference v5.1 results (summary_results.json and per-submitter logs)*, 2025-09-09. [Link](https://github.com/mlcommons/inference_results_v5.1)
- [**S602**](../../../sources/bibliography.md#s602) MLCommons, *MLPerf Inference v6.0 results (summary_results.json and per-submitter logs)*, 2026-04-01. [Link](https://github.com/mlcommons/inference_results_v6.0)
- [**S603**](../../../sources/bibliography.md#s603) MLCommons, *MLPerf Inference v6.1 results (summary.csv and per-submitter logs)*, 2026-09. [Link](https://github.com/mlcommons/inference_results_v6.1)
- [**S621**](../../../sources/bibliography.md#s621) SemiAnalysis (InferenceX-app repository), *InferenceX public API snapshot (benchmarks.json and benchmarks-history.json fixtures)*, 2026-10-17. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/tree/main/packages/app/cypress/fixtures/api)
- [**S622**](../../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S632**](../../../sources/bibliography.md#s632) SemiAnalysis, *AMD MI355X Qwen3.5 397B-A17B Inference: Up to 19x Throughput per GPU in 3 Months on SGLang FP8*, 2026-05-25. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/mi355x-qwen3-5-sglang-v0-5-12-up-to-17x.mdx)
- [**S641**](../../../sources/bibliography.md#s641) NVIDIA, *TensorRT-LLM performance overview (release 0.19)*, 2025-05-16. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/df1943062933caad9c72c615d0fde9f3df591eb2/docs/source/performance/perf-overview.md)
- [**S642**](../../../sources/bibliography.md#s642) NVIDIA, *TensorRT-LLM performance overview (release 0.21)*, 2025-07-30. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/18d19410831ecdec0d97c76401a1bf40b935c992/docs/source/performance/perf-overview.md)
- [**S643**](../../../sources/bibliography.md#s643) NVIDIA, *TensorRT-LLM performance overview (release 1.0)*, 2025-09-21. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/c38d4cf6a66370f8fd58a517f398e12c7981fcf8/docs/source/legacy/performance/perf-overview.md)
- [**S644**](../../../sources/bibliography.md#s644) NVIDIA, *TensorRT-LLM performance overview (release 1.1)*, 2025-12-09. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/1ffa2c893720ca2c3c6d245829b0c493485d21a6/docs/source/developer-guide/perf-overview.md)
- [**S645**](../../../sources/bibliography.md#s645) NVIDIA TensorRT-LLM team, *Pushing Latency Boundaries: Optimizing DeepSeek-R1 Performance on NVIDIA B200 GPUs (TensorRT-LLM tech blog 1)*, 2025-05-16. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/blogs/tech_blog/blog01_Pushing_Latency_Boundaries_Optimizing_DeepSeek-R1_Performance_on_NVIDIA_B200_GPUs.md)
- [**S646**](../../../sources/bibliography.md#s646) NVIDIA TensorRT-LLM team, *Optimizing DeepSeek R1 Throughput on NVIDIA Blackwell GPUs: A Deep Dive for Developers (TensorRT-LLM tech blog 3)*, 2025-05-30. [Link](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/blogs/tech_blog/blog03_Optimizing_DeepSeek_R1_Throughput_on_NVIDIA_Blackwell_GPUs.md)
- [**S11000**](../../../sources/bibliography.md#s11000) nvidia_deep_dive_claude repository, *Repo analysis: layer 11 inference models (disaggregation comparison, cost per million tokens across software releases, implied inference revenue, tokens per MW and per-request economics)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/layers/11-inference-and-ai-software/index.md)
- [**S11001**](../../../sources/bibliography.md#s11001) NVIDIA (GitHub), *NVIDIA Dynamo README (ai-dynamo/dynamo)*, 2026-11. [Link](https://github.com/ai-dynamo/dynamo/blob/main/README.md)
