# 推理与 AI 软件：价值链与企业发展视角

> [!NOTE]
> 本页为英文原文的简体中文参考译文，仅供参考；如有出入，以[英文原文](../../../layers/11-inference-and-ai-software/value-chain-and-corp-dev.md "English original")为准。

<sub>第 11 层 · 推理与 AI 软件 · 约 12 分钟阅读 · 最近核实：2026-11-05</sub>

## ⚡ 要点速览

- **每 1 美元 API 收入中，大部分留在模型实验室：** 据报道，OpenAI 在 2025 年 10 月的[算力毛利率（compute margin）](../../glossary.md#compute-margin)为 ~70%；估计其中 ~16¢ 流向云厂商，~5¢ 作为毛利流向英伟达（NVIDIA）🔴 [[S11537]](../../../sources/bibliography.md#s11537)[[S622]](../../../sources/bibliography.md#s622)[[S3]](../../../sources/bibliography.md#s3)。
- **固定质量下的 token 价格快速通缩**（GPT-3.5 水平的价格两年内从每百万 $20 降至 $0.07），但 GPT-5.5 上市定价却是 GPT-5.4 的两倍 🟡 [[S11526]](../../../sources/bibliography.md#s11526)[[S11535]](../../../sources/bibliography.md#s11535)。
- **英伟达的软件业务线规模很小：** AI Enterprise 标价为每 GPU 每年 $4,500；FY2025 末 ~$2B 的年化收入不到 FY2026 收入的 1% [[S9515]](../../../sources/bibliography.md#s9515)[[S11011]](../../../sources/bibliography.md#s11011)[[S1]](../../../sources/bibliography.md#s1)。
- **[推理服务商](../../glossary.md#inference-provider)的估值堪比芯片初创公司：** Fireworks ~$15B（洽谈中）、Together AI $8.3B、Baseten $5B；英伟达投资了后两家 [[S11514]](../../../sources/bibliography.md#s11514)[[S11516]](../../../sources/bibliography.md#s11516)[[S11518]](../../../sources/bibliography.md#s11518)。
- **交易：** 英伟达–Groq（~$20B）、英伟达–Hugging Face（~$12.9B，尚待完成）、高通（Qualcomm）–Modular（$3.9B）、AMD–Silo AI（$665M）[[S90019]](../../../sources/bibliography.md#s90019)[[S11026]](../../../sources/bibliography.md#s11026)[[S90057]](../../../sources/bibliography.md#s90057)[[S9506]](../../../sources/bibliography.md#s9506)。
- **[Q8 · 价值池与并购机会]** 价值池：实验室利润、云厂商租赁利润、英伟达硬件利润。切入点：可移植软件、[解码（decode）](../../glossary.md#decode)芯片，以及决定硬件选型的推理云。

![拆分 $1.00 API 收入的瀑布图：模型实验室的算力毛利率留下约 70 美分的毛利（据报道 OpenAI 在 2025 年 10 月约为 70%）；剩余 30 美分的算力成本拆分为：云运营商毛利（约 16 美分，依据每 GB300 GPU 小时租价 $5.00 对比所有者 TCO $2.31）、电费（约 2 美分）、设施、运营与融资（约 3 美分）、其他 IT 硬件（约 2 美分）、英伟达销售成本（约 2 美分）以及英伟达毛利（约 5 美分）。实验室所得部分仍需支付训练算力和研发，其中很大一部分同样流向英伟达。](../../../assets/charts/11-token-revenue-value-pools.svg)

## 谁赚走了一个 token 的利润

把一个 token 想象成一份餐厅的菜：模型实验室拥有菜谱和品牌，云厂商出租厨房，英伟达卖出了烤箱。菜单价格由品牌决定，因此只要客户还想要它的模型，实验室就能拿走账单的大头。

> [!TIP]
> **算例 —— 在 GB300 [NVL72](../../glossary.md#nvl72) 上生成一百万个 DeepSeek-R1 token。** 在每用户 50 tokens/s 下，一块 GB300 GPU 每秒输出 ~6,261 个 token，即每小时 ~22.5M [[S621]](../../../sources/bibliography.md#s621)。按 SemiAnalysis 的 $5.00 租价计算，相当于每百万 token ~$0.22；按所有者 $2.31 的[总拥有成本（TCO）](../../glossary.md#tco)计算，为 ~$0.10 [[S622]](../../../sources/bibliography.md#s622)。英伟达的收入占租金的 ~23%（每 [GPU 小时](../../glossary.md#gpu-hour) ~$1.13）：每百万 token ~$0.05，其中 ~$0.04 为毛利 🔴 [[S3]](../../../sources/bibliography.md#s3)。若算力占收入的 30%，实验室对每百万 token 收费 ~$0.74。

<details>
<summary>🔧 技术细节：假设与敏感性</summary>

输入：OpenAI ~70% 的算力毛利率 [[S11537]](../../../sources/bibliography.md#s11537)[[S11538]](../../../sources/bibliography.md#s11538)、SemiAnalysis 的租价与所有者 TCO 对比 [[S622]](../../../sources/bibliography.md#s622)、电力占所有者 TCO 的 ~15%、英伟达占 IT 硬件的 ~75%（GPU 占 GB300 机架价格的 ~63%）[[S332]](../../../sources/bibliography.md#s332)，以及英伟达 75.0% 的毛利率 [[S3]](../../../sources/bibliography.md#s3)。若按 2024 年底实验室 52% 的利润率计算，英伟达的毛利为 ~8¢；低于标价的合同价会压缩云厂商的份额；训练算力不计入。数据：`l11_token_value_pools.csv`。

</details>

## token 价格通缩及其极限

![每百万 token API 价格的对数坐标图。GPT-3.5 质量水平最便宜模型的价格从 $20（2022 年 11 月）降至 $0.07（2024 年 10 月），约下降 286 倍。OpenAI 旗舰模型从 GPT-4 的混合价 $37.50（2023 年 3 月），经 GPT-4 Turbo（$15）、GPT-4o（$7.50，后降至 $4.38），降至 GPT-5 的 $3.44（2025 年 8 月），便宜约 11 倍；随后 GPT-5.5 以 $11.25 上市（2026 年 4 月，据报道），为 GPT-5 的 3.3 倍。OpenAI 小模型档从 gpt-3.5-turbo 的 $2.00（2023 年）降至 GPT-4o mini（$0.26）和 GPT-5 nano（$0.14）。](../../../assets/charts/11-api-token-price-trend.svg)

[token 价格通缩](../../glossary.md#token-price-deflation)源于更好的硬件、软件和更小的模型。MIT 的一项研究估计，前沿质量模型的价格每年下降 5–10× [[S11527]](../../../sources/bibliography.md#s11527)。此处价格按 Epoch 的惯例，以输入与输出 3:1 的比例[混合计价](../../glossary.md#blended-token-price) [[S11525]](../../../sources/bibliography.md#s11525)。迄今为止，更便宜的 token 意味着更多的 token：谷歌的月度 token 量从 9.7 万亿（2024 年 4 月）增至超过 1.3 千万亿（2025 年 10 月），这是典型的[杰文斯悖论](../../glossary.md#jevons-paradox) [[S32018]](../../../sources/bibliography.md#s32018)[[S32020]](../../../sources/bibliography.md#s32020)。同样的挤压也冲击了 GPU 租赁市场：H100 租价两年内下降了 ~75% [[S393]](../../../sources/bibliography.md#s393)[[S395]](../../../sources/bibliography.md#s395)。

![GPU 租价随时间变化的散点图。H100：AWS p5 按需价格在 2023 年 7 月上市时为每 GPU 小时 $12.29，2025 年 6 月降价后为 $6.88；新兴云服务商的 H100 在 2023 年约为 $8，到 2024 年底各交易市场已低于 $2，2025 年 Lambda 标价 $2.99、CoreWeave 标价 $6.16。2025 年 Blackwell 标价：B200 从 $4.99（Lambda）到 $8.60（CoreWeave），GB200 为 $10.50（CoreWeave）。](../../../assets/charts/14-gpu-rental-price-trend.svg)

> [!TIP]
> **算例 —— 谁来消化通缩。** 某服务商以 50% 的毛利率销售 token。第二年价格下降 50%，每 token 成本下降 30%：成本为旧价格的 0.5 × 0.7 = 0.35，而收入为 0.5，因此毛利率降至 30%。要维持 50% 的毛利率，成本下降速度必须与价格同步，所以服务商会追逐每一次软件增益和每一代新 GPU。

## NVIDIA AI Enterprise 的经济账

> [!TIP]
> **算例 —— 许可费给每个机架增加多少成本。** 一个 72 块 GPU 的 GB300 NVL72 机架，按 $4,500 标价计每年 $324K，相当于每年 ~$4M 机架价格的 ~8% [[S9515]](../../../sources/bibliography.md#s9515)[[S332]](../../../sources/bibliography.md#s332)；在生产环境中使用 NIM 需要此许可，或在云上按每 GPU 小时 ~$1 计费 [[S11013]](../../../sources/bibliography.md#s11013)。黄仁勋在 2026 年 10 月提出智能体软件每 GPU 每年 ~$2,000 的设想 [[S11016]](../../../sources/bibliography.md#s11016)。看空要点：Q4 FY2024 软件年化收入仅 ~$1B [[S9516]](../../../sources/bibliography.md#s9516)，与硬件相比微不足道，而开源引擎让买家可以绕开这笔费用（[竞争格局](competition.md)）。

## 本层的非上市公司与并购

| 公司 | 业务 | 阶段 / 最近一次公开融资 | 为何重要 |
|---|---|---|---|
| Fireworks AI | 开放模型推理云 | 以 ~$15B 估值洽谈融资（2026 年 5 月）；另有报道称正以 $30–40B 洽谈 🟡 | 按估值计最大的独立 token 销售商 [[S11514]](../../../sources/bibliography.md#s11514)[[S11515]](../../../sources/bibliography.md#s11515) |
| Together AI | 推理与训练云 | C 轮 $800M，估值 $8.3B（2026 年 7 月）；英伟达参投 | Dynamo 1.0 采用者 [[S11516]](../../../sources/bibliography.md#s11516)[[S90066]](../../../sources/bibliography.md#s90066) |
| Baseten | 推理平台 | E 轮 $300M，估值 $5B（2026 年 1 月）；英伟达为基石投资者 | 采用 Dynamo 路由后 TTFT 快 2× [[S11518]](../../../sources/bibliography.md#s11518)[[S11001]](../../../sources/bibliography.md#s11001) |
| Modal Labs | 无服务器 GPU 算力 | 以 ~$2.5B 估值洽谈融资（2026 年 2 月）🟡 | 开发者入口 [[S11519]](../../../sources/bibliography.md#s11519) |
| Inferact | vLLM 背后的公司 | 种子轮 $150M，估值 $800M（2026 年 1 月） | 主导可移植性最强的引擎 [[S11511]](../../../sources/bibliography.md#s11511)[[S11540]](../../../sources/bibliography.md#s11540) |
| RadixArk | SGLang 背后的公司 | 种子轮 $100M，估值 $400M（2026 年 5 月）；据报道英伟达、AMD 参投 | 许多 InferenceX 前沿数据点背后的引擎 [[S11513]](../../../sources/bibliography.md#s11513) |
| Cerebras（2026 年 5 月上市） | 晶圆级系统与云服务 | IPO 募资 $5.55B，估值 ~$40B | OpenAI 最多 750 MW [[S2505]](../../../sources/bibliography.md#s2505)[[S11523]](../../../sources/bibliography.md#s11523) |
| Groq | GroqCloud API | ~$6.9B（2025 年 9 月），随后获英伟达 ~$20B 授权交易 | 授权方还能继续竞争吗？[[S90019]](../../../sources/bibliography.md#s90019) |
| Etched | 专用于 Transformer 的 ASIC | C 轮 $300M，估值 $10.3B（2026 年 7 月） | 押注专用化；据报道预订单 ~$1B [[S2507]](../../../sources/bibliography.md#s2507) |
| Positron | 内存优先的推理 ASIC | C 轮 $875M，估值 $5B（2026 年 9 月） | 较 2026 年 2 月上涨 ~5× [[S11521]](../../../sources/bibliography.md#s11521)[[S11520]](../../../sources/bibliography.md#s11520) |
| d-Matrix | 数字存内计算 | C 轮 $275M，估值 $2B（2025 年 11 月） | 无需晶圆级芯片的 SRAM 解码 [[S2511]](../../../sources/bibliography.md#s2511) |
| Tenstorrent | RISC-V AI 芯片，开放软件栈 | D 轮 $693M，估值 ~$2.7B（2024 年 12 月） | 可授权的 IP [[S2509]](../../../sources/bibliography.md#s2509) |
| MatX | 大语言模型加速器 | B 轮 $500M（2026 年 2 月）；估值未披露 | 计划 2027 年出货 [[S2508]](../../../sources/bibliography.md#s2508) |
| SambaNova | 数据流芯片与云服务 | 英特尔以 ~$1.6B（含债务）洽谈收购，已停滞 | 可能成为困境资产 [[S2512]](../../../sources/bibliography.md#s2512) |
| Rebellions、FuriosaAI | 韩国推理 NPU | FuriosaAI 过桥融资 ~$122M（2025 年 7 月） | 已获 Ray 支持 [[S11522]](../../../sources/bibliography.md#s11522)[[S584]](../../../sources/bibliography.md#s584) |

<sub>仅限公开信息；除标注为洽谈或要约者外，估值均为投后估值。</sub>

![推理初创公司估值的对数坐标水平柱状图。推理云：Fireworks AI 约 $15,000M（洽谈中，2026 年 5 月）、Together AI $8,300M（2026 年 7 月）、Baseten $5,000M（2026 年 1 月）、Modal 约 $2,500M（洽谈中）。推理服务软件：Hugging Face $12,930M（英伟达于 2026 年 9 月宣布收购，尚待完成）、Modular $3,900M（2026 年被高通收购）、Inferact（vLLM）$800M 与 RadixArk（SGLang）$400M 的种子轮估值。芯片：Cerebras 在 2026 年 5 月 IPO 时约 $40,000M、Etched $10,300M、Groq 在获英伟达约 $20B 授权前为 $6,900M、Positron $5,000M、Tenstorrent 约 $2,700M、d-Matrix $2,000M、SambaNova 约 $1,600M（英特尔要约洽谈）；MatX 和 FuriosaAI 估值未披露。](../../../assets/charts/11-inference-startup-valuations.svg)

### 本层的并购历史

| 收购方 | 交易（年份，金额） | 逻辑 |
|---|---|---|
| 英伟达 | Deci、Run:ai、OctoAI（2024；~$300M、~$700M、~$250M）；CentML（2025，含业绩对赌付款 >$400M）；Groq 授权 + 团队（2025，~$20B）；Hugging Face（2026，~$12.9B，尚待完成） | 编译器与推理服务人才、SRAM 解码、模型分发 [[S478]](../../../sources/bibliography.md#s478)[[S476]](../../../sources/bibliography.md#s476)[[S11510]](../../../sources/bibliography.md#s11510)[[S11509]](../../../sources/bibliography.md#s11509)[[S90019]](../../../sources/bibliography.md#s90019)[[S11026]](../../../sources/bibliography.md#s11026) |
| AMD | Nod.ai（2023）；Silo AI（2024，$665M）；Brium 与 Untether AI 团队（2025）；MK1（2025） | 弥补 ROCm 的软件短板 [[S9508]](../../../sources/bibliography.md#s9508)[[S9506]](../../../sources/bibliography.md#s9506)[[S9507]](../../../sources/bibliography.md#s9507)[[S9509]](../../../sources/bibliography.md#s9509) |
| 高通 | Modular（宣布金额 $3.9B，2026-07-29 完成交割） | 可跨硬件移植的运行时（Mojo、MAX）[[S90057]](../../../sources/bibliography.md#s90057)[[S9511]](../../../sources/bibliography.md#s9511) |
| 红帽（IBM） | Neural Magic（2024） | 商业化 vLLM；后来联合发起 llm-d [[S9533]](../../../sources/bibliography.md#s9533)[[S11503]](../../../sources/bibliography.md#s11503) |
| 英特尔 | SambaNova（洽谈中，~$1.6B 含债务，已停滞） | 重返推理芯片市场 [[S2512]](../../../sources/bibliography.md#s2512) |

> [!TIP]
> **算例 —— 一家 token 销售商值多少钱。** Together AI $8.3B 的估值是其 2025 年 2 月 B 轮 ~$3.3B 估值的 ~2.5× [[S11516]](../../../sources/bibliography.md#s11516)；在英伟达这边，~$20B 的 Groq 交易价格是 Groq 最近一次私募估值 ~$6.9B 的 ~2.9× [[S90019]](../../../sources/bibliography.md#s90019)。买家支付的是推理领域的稀缺性溢价，而非当前收入。

完整的交易图表见[发展历程：英伟达如何建成这一层](history-and-how-built.md)。

**[Q8 · 价值池与并购机会]** 最大的价值池是模型实验室的利润（扣除训练成本前占 API 收入的 ~70%），其次是云厂商的租赁利润，再次是英伟达的硬件利润；英伟达自身的软件收入不到其总收入的 1% [[S11537]](../../../sources/bibliography.md#s11537)[[S622]](../../../sources/bibliography.md#s622)[[S11011]](../../../sources/bibliography.md#s11011)。并购追随稀缺性：英伟达为引擎团队花钱不多，却为解码芯片和分发渠道一掷千金；AMD 和高通买的是可移植性。尚存的切入点：可移植推理服务公司（Inferact、RadixArk）、[SRAM](../../glossary.md#sram) 或近存解码 IP（d-Matrix、Positron、Etched），以及为[开放权重模型](../../glossary.md#open-weight-model)选择硬件的推理云。

## 🎯 企业发展视角

1. 高通为 AI 100 提供了 [vLLM](../../glossary.md#vllm) 容器，如今又拥有 Modular [[S596]](../../../sources/bibliography.md#s596)[[S9511]](../../../sources/bibliography.md#s9511)：AI200/AI250 的软件应依靠上游 vLLM/llm-d 扩大覆盖面，依靠 MAX 实现差异化，还是两者兼顾？
2. 英伟达持有 Together AI 和 Baseten 的股份 [[S11516]](../../../sources/bibliography.md#s11516)[[S11518]](../../../sources/bibliography.md#s11518)。什么条件能促使一家推理云认证第二个硬件平台？
3. 英伟达选择授权 Groq 而非收购。对 SRAM 和近存计算初创公司而言，授权或少数股权投资是否优于 $2–10B 的收购？
4. 如果实验室保留每 1 美元 API 收入中的 ~70¢，与 token 买家（HUMAIN 式的主权机构或模型实验室）联合设计，是否比商用芯片销售更有价值 [[S90030]](../../../sources/bibliography.md#s90030)？
5. 如果监管机构对英伟达的 Hugging Face 交易附加条件，中立的模型分发是否可能成为一个合作机会 [[S11027]](../../../sources/bibliography.md#s11027)？

## 📚 来源（Sources）

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S1**](../../../sources/bibliography.md#s1) NVIDIA Corporation via SEC EDGAR, *NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2026 (Form 8-K exhibit 99.1)*, 2026-02-25. [Link](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000019/q4fy26pr.htm)
- [**S3**](../../../sources/bibliography.md#s3) StorageNewsletter, *NVIDIA Q2 Fiscal 2027 results coverage: revenue $96.2B*, 2026-08-27. [Link](https://www.storagenewsletter.com/2026/08/27/nvidia-fiscal-2q27-financial-results/)
- [**S332**](../../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S393**](../../../sources/bibliography.md#s393) Latent Space (Eugene Cheah), *$2 H100s: how the GPU bubble burst*, 2024-10. [Link](https://www.latent.space/p/gpu-bubble)
- [**S395**](../../../sources/bibliography.md#s395) Lambda, *Lambda GPU cloud pricing*, 2025. [Link](https://lambda.ai/pricing)
- [**S476**](../../../sources/bibliography.md#s476) NVIDIA Blog, *NVIDIA to Acquire GPU Orchestration Software Provider Run:ai*, 2024-04-24. [Link](https://blogs.nvidia.com/blog/runai/)
- [**S478**](../../../sources/bibliography.md#s478) NVIDIA, *NVIDIA Blog and Newsroom acquisition announcements (Cumulus, SwiftStack, DeepMap, Bright Computing, Excelero, Shoreline, Brev.dev, OctoAI, VinBrain, Gretel, Lepton AI, CentML, SchedMD)*, 2025-12. [Link](https://blogs.nvidia.com/)
- [**S584**](../../../sources/bibliography.md#s584) Ray project (GitHub: ray-project/ray), *Ray accelerator managers (python/ray/_private/accelerators)*, 2026-11. [Link](https://github.com/ray-project/ray/blob/master/python/ray/_private/accelerators/__init__.py)
- [**S596**](../../../sources/bibliography.md#s596) Qualcomm (GitHub: quic), *Qualcomm Cloud AI SDK and Efficient Transformers repositories*, 2026-11. [Link](https://github.com/quic/cloud-ai-sdk)
- [**S621**](../../../sources/bibliography.md#s621) SemiAnalysis (InferenceX-app repository), *InferenceX public API snapshot (benchmarks.json and benchmarks-history.json fixtures)*, 2026-10-17. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/tree/main/packages/app/cypress/fixtures/api)
- [**S622**](../../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S2505**](../../../sources/bibliography.md#s2505) Dealroom, *Cerebras raises $5.55B in biggest US IPO of 2026*, 2026-05. [Link](https://dealroom.co/news/128936-cerebras-raises-5-55b-in-biggest-us-ipo-of-2026/)
- [**S2507**](../../../sources/bibliography.md#s2507) AI Weekly, *Etched closes $300M Series C at $10.3B led by Sequoia, books ~$1B in pre-orders for Sohu*, 2026-07. [Link](https://aiweekly.co/alerts/etched-closes-300m-series-c-at-103b-led-by-sequoia-books-1b-in-pre-orders-for)
- [**S2508**](../../../sources/bibliography.md#s2508) AI2.Work, *MatX raises $500M to build AI chips*, 2026-02-24. [Link](https://ai2.work/blog/matx-raises-500m-to-build-ai-chips-that-beat-nvidia-by-10x)
- [**S2509**](../../../sources/bibliography.md#s2509) TechPowerUp, *Tenstorrent closes $693M+ of Series D funding led by Samsung Securities and AFW Partners*, 2024-12-02. [Link](https://techpowerup.com/329396/tenstorrent-closes-usd-693m-of-series-d-funding-led-by-samsung-securities-and-afw-partners)
- [**S2511**](../../../sources/bibliography.md#s2511) Converge Digest, *d-Matrix raises $275 million to accelerate the age of AI inference*, 2025-11-12. [Link](https://convergedigest.com/d-matrix-raises-275-million-to-accelerate-the-age-of-ai-inference/)
- [**S2512**](../../../sources/bibliography.md#s2512) Verdict, *Intel pursues SambaNova acquisition amid AI expansion plans*, 2025-12. [Link](https://www.verdict.co.uk/intel-sambanova-acquisition/)
- [**S9506**](../../../sources/bibliography.md#s9506) Converge Digest, *AMD completes $665 million acquisition of Silo AI*, 2024-08. [Link](https://convergedigest.com/amd-completes-665-million-acquisition-of-silo-ai/?amp=1)
- [**S9507**](../../../sources/bibliography.md#s9507) DatacenterDynamics, *AMD extends acquisition run: brings software optimization firm Brium and staff from recently shuttered Untether AI into the fold*, 2025-06. [Link](https://www.datacenterdynamics.com/en/news/amd-extends-acquisition-run-brings-software-optimization-firm-brium-and-staff-from-recently-shuttered-untether-ai-into-the-fold/)
- [**S9508**](../../../sources/bibliography.md#s9508) PrivSource (deal record of AMD press release), *AMD to Acquire Nod.ai to Expand Open-Source AI Software Capabilities*, 2023-10. [Link](https://www.privsource.com/acquisitions/deal/amd-to-acquire-nod-ai-to-expand-open-source-ai-software-capabilities-bWSr8y)
- [**S9509**](../../../sources/bibliography.md#s9509) PrivSource (deal record), *AMD Acquires MK1*, 2025-11. [Link](https://www.privsource.com/acquisitions/deal/y3S4jb)
- [**S9511**](../../../sources/bibliography.md#s9511) Nasdaq (Qualcomm press release), *Qualcomm Completes Acquisition of Modular*, 2026-07-29. [Link](https://www.nasdaq.com/press-release/qualcomm-completes-acquisition-modular-2026-07-29)
- [**S9515**](../../../sources/bibliography.md#s9515) The Register (Tobias Mann), *Nvidia's software empire (NVIDIA AI Enterprise licensing)*, 2024-08-06. [Link](https://www.theregister.com/2024/08/06/nvidia_software_empire/)
- [**S9516**](../../../sources/bibliography.md#s9516) MarketBeat, *NVIDIA Q4 FY2024 earnings call transcript*, 2024-02-21. [Link](https://www.marketbeat.com/earnings/reports/2024-2-21-nvidia-co-stock)
- [**S9533**](../../../sources/bibliography.md#s9533) Red Hat Blog, *FAQ: Red Hat to acquire Neural Magic*, 2024-11-12. [Link](https://www.redhat.com/en/blog/red-hat-acquire-neural-magic-FAQ)
- [**S11001**](../../../sources/bibliography.md#s11001) NVIDIA (GitHub), *NVIDIA Dynamo README (ai-dynamo/dynamo)*, 2026-11. [Link](https://github.com/ai-dynamo/dynamo/blob/main/README.md)
- [**S11011**](../../../sources/bibliography.md#s11011) MarketBeat, *NVIDIA Q2 Fiscal 2025 earnings call transcript (28 August 2024)*, 2024-08-28. [Link](https://www.marketbeat.com/earnings/transcripts/110080/)
- [**S11013**](../../../sources/bibliography.md#s11013) NVIDIA (docs.api.nvidia.com), *NVIDIA NIM FAQ*, 2025. [Link](https://docs.api.nvidia.com/nim/docs/faq)
- [**S11016**](../../../sources/bibliography.md#s11016) TweakTown, *Jensen Huang puts a $2000 per GPU yearly price on NVIDIA's AI agent software*, 2026-10. [Link](https://www.tweaktown.com/news/114285/jensen-huang-puts-a-dollars2000-per-gpu-yearly-price-on-nvidias-ai-agent-software/index.html)
- [**S11026**](../../../sources/bibliography.md#s11026) Implicator.ai, *Nvidia confirms $12.9 billion Hugging Face deal, says its chips won't be required*, 2026-09. [Link](https://www.implicator.ai/nvidia-confirms-12-9-billion-hugging-face-deal-says-its-chips-wont-be-required/)
- [**S11027**](../../../sources/bibliography.md#s11027) MLex, *Nvidia may seek EU review of Hugging Face deal amid filing uncertainty*, 2026-09-23. [Link](https://www.mlex.com/mlex/articles/2528556/nvidia-may-seek-eu-review-of-hugging-face-deal-amid-european-filing-uncertainty)
- [**S11503**](../../../sources/bibliography.md#s11503) llm-d project (GitHub: llm-d/llm-d), *llm-d README (distributed inference on Kubernetes)*, 2026-11. [Link](https://github.com/llm-d/llm-d/blob/main/README.md)
- [**S11509**](../../../sources/bibliography.md#s11509) The Logic, *Nvidia's deal for CentML could be worth more than US$400M*, 2025-06. [Link](https://thelogic.co/news/exclusive/nvidias-deal-centml-us400m/)
- [**S11510**](../../../sources/bibliography.md#s11510) Analytics Insight, *Top AI acquisitions of 2024: a detailed analysis*, 2024-12. [Link](https://www.analyticsinsight.net/amp/story/artificial-intelligence/top-ai-acquisitions-of-2024-a-detailed-analysis)
- [**S11511**](../../../sources/bibliography.md#s11511) TechCrunch, *Inference startup Inferact lands $150M to commercialize vLLM*, 2026-01-22. [Link](https://techcrunch.com/2026/01/22/inference-startup-inferact-lands-150m-to-commercialize-vllm/)
- [**S11513**](../../../sources/bibliography.md#s11513) Doolpa, *RadixArk raises $100M seed to grow the SGLang inference engine*, 2026-05-05. [Link](https://doolpa.com/news/radixark-100m-seed-accel-spark-nvidia-amd-sglang-may-5-2026)
- [**S11514**](../../../sources/bibliography.md#s11514) Bloomberg Government (Bloomberg), *Fireworks AI in talks for funding at $15 billion valuation*, 2026-05. [Link](https://news.bgov.com/private-equity/fireworks-ai-in-talks-for-funding-at-15-billion-valuation)
- [**S11515**](../../../sources/bibliography.md#s11515) Tech Funding News, *Nvidia-backed Fireworks AI eyes $30B to $40B valuation roughly double its July price*, 2026. [Link](https://techfundingnews.com/nvidia-backed-fireworks-ai-eyes-30b-to-40b-valuation-roughly-double-its-july-price/)
- [**S11516**](../../../sources/bibliography.md#s11516) DatacenterDynamics, *Together AI raises $800m in Series C funding round*, 2026-07. [Link](https://www.datacenterdynamics.com/en/news/together-ai-raises-800m-in-series-c-funding-round/)
- [**S11518**](../../../sources/bibliography.md#s11518) Pulse (venture deals aggregator), *Baseten Labs raises $300M in growth-stage round, valuation hits $5B*, 2026-01-23. [Link](https://www.pulse.bot/ai/deals/baseten-labs-raises-300m-in-growth-stage-round-valuation-hits-5b-7b6470b8-a313-4df3-a2a6-7cb9d288dd92/)
- [**S11519**](../../../sources/bibliography.md#s11519) Creati.ai, *Modal Labs negotiates funding at $2.5B valuation as AI inference market heats up*, 2026-02-12. [Link](https://creati.ai/ai-news/2026-02-12/modal-labs-2-5b-valuation-funding-ai-inference)
- [**S11520**](../../../sources/bibliography.md#s11520) eWeek, *Positron secures $230M AI funding for $1B valuation*, 2026-02-04. [Link](https://www.eweek.com/news/positron-230m-ai-funding/)
- [**S11521**](../../../sources/bibliography.md#s11521) Latham & Watkins, *Latham & Watkins advises Positron AI on Series C*, 2026-09. [Link](https://www.lw.com/en/news/2026/09/latham-watkins-advises-positron-ai-on-series-c)
- [**S11522**](../../../sources/bibliography.md#s11522) CB Insights, *FuriosaAI financials (funding rounds)*, 2026. [Link](https://www.cbinsights.com/company/furiosaai/financials)
- [**S11523**](../../../sources/bibliography.md#s11523) DatacenterDynamics, *OpenAI signs $10 billion deal with Cerebras with 750MW of big chip compute*, 2026-01-14. [Link](https://www.datacenterdynamics.com/en/news/openai-signs-10-billion-deal-with-cerebras-with-750mw-of-big-chip-compute/)
- [**S11525**](../../../sources/bibliography.md#s11525) Epoch AI, *LLM inference prices have fallen rapidly but unequally across tasks*, 2025-03. [Link](https://epoch.ai/data-insights/llm-inference-price-trends)
- [**S11526**](../../../sources/bibliography.md#s11526) Stanford HAI, *The 2025 AI Index Report*, 2025-04. [Link](https://hai.stanford.edu/ai-index/2025-ai-index-report)
- [**S11527**](../../../sources/bibliography.md#s11527) arXiv 2511.23455 (MIT FutureTech), *The Price of Progress: Algorithmic Efficiency and the Falling Cost of AI Inference*, 2025-11. [Link](https://arxiv.org/abs/2511.23455)
- [**S11535**](../../../sources/bibliography.md#s11535) Doolpa, *OpenAI launches GPT-5.5 with state-of-the-art agentic coding and doubles API prices (April 2026)*, 2026-04. [Link](https://doolpa.com/news/openai-gpt-5-5-launch-agentic-coding-pricing-april-2026)
- [**S11537**](../../../sources/bibliography.md#s11537) The Decoder, *OpenAI reportedly dramatically improved its compute profit margins*, 2025-12. [Link](https://the-decoder.com/openai-reportedly-dramatically-improved-its-compute-profit-margins/)
- [**S11538**](../../../sources/bibliography.md#s11538) Bloomberg, *OpenAI sees better margins on business sales; report says*, 2025-12-21. [Link](https://www.bloomberg.com/news/articles/2025-12-21/openai-sees-better-margins-on-business-sales-report-says)
- [**S11540**](../../../sources/bibliography.md#s11540) Pulse 2.0, *Inferact launches with $150 million funding at $800M valuation to commercialize vLLM*, 2026-01-22. [Link](https://pulse2.com/inferact-launches-with-150-million-funding-at-800m-valuation-to-commercialize-vllm-as-inference-demand-surges/)
- [**S32018**](../../../sources/bibliography.md#s32018) Google (The Keyword) (Sundar Pichai), *Google I/O 2025 keynote remarks (Sundar Pichai)*, 2025-05-20. [Link](https://blog.google/technology/ai/io-2025-keynote/)
- [**S32020**](../../../sources/bibliography.md#s32020) Alphabet / Google (The Keyword) (Sundar Pichai), *Alphabet CEO remarks on token volume (October 2025)*, 2025-10. [Link](https://blog.google/inside-google/message-ceo/alphabet-earnings-q3-2025/)
- [**S90019**](../../../sources/bibliography.md#s90019) TechSpot, *Nvidia's $20 billion Groq deal looks a lot like an acquisition*, 2025-12. [Link](https://www.techspot.com/news/110723-nvidia-20-billion-groq-deal-looks-lot-like.html)
- [**S90030**](../../../sources/bibliography.md#s90030) Morningstar, *Qualcomm: Humain deal provides some AI upside*, 2025-10. [Link](https://www.morningstar.com/stocks/qualcomm-humain-deal-provides-some-ai-upside)
- [**S90057**](../../../sources/bibliography.md#s90057) StorageReview, *Qualcomm unveils Dragonfly data center roadmap: C1000 CPU, AI300 accelerator and Modular acquisition*, 2026-06-24. [Link](https://www.storagereview.com/es/news/qualcomm-unveils-dragonfly-data-center-roadmap-c1000-cpu-ai300-accelerator-and-modular-acquisition)
- [**S90066**](../../../sources/bibliography.md#s90066) HPCwire (NVIDIA press release), *NVIDIA enters production with Dynamo, the broadly adopted inference operating system for AI factories*, 2026-03-17. [Link](https://www.hpcwire.com/aiwire/tag/dynamo-1-0/)
