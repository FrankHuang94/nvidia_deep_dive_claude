# Honest assessment: how strong is the CUDA moat?

<sub>Layer 09 · CUDA and system software · ~9 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **🔴 Verdict: real but uneven.** By our scoring, lock-in is highest in academia (4.75/5) and self-hosting enterprises (4.5), and lowest for frontier labs (2.75) and export-constrained Chinese labs (2.5).
- **Inference on popular models is the thinnest part** (2.7/5 vs ~3.9 for training and new architectures). It needs few kernels, it is cost-sensitive, and it runs at a scale that pays for porting.
- **Erosion is real at the top.** Anthropic committed to up to 1M TPUs [[S653]](../../sources/bibliography.md#s653); OpenAI signed for 6 GW of AMD [[S546]](../../sources/bibliography.md#s546) and 10 GW of Broadcom-built accelerators [[S174]](../../sources/bibliography.md#s174); Meta runs MTIA and rents TPUs [[S561]](../../sources/bibliography.md#s561)[[S90025]](../../sources/bibliography.md#s90025).
- **So is NVIDIA's pull.** Q2 FY2027 revenue was $96.2B, Data Center ~$89.0B [[S3]](../../sources/bibliography.md#s3)[[S90011]](../../sources/bibliography.md#s90011). Anthropic also took up to 1 GW of NVIDIA systems [[S654]](../../sources/bibliography.md#s654), and Meta agreed to buy millions of NVIDIA chips [[S4006]](../../sources/bibliography.md#s4006).
- **DeepSeek cuts both ways.** It went *below* [CUDA](../../glossary.md#cuda) to PTX and SASS [[S5005]](../../sources/bibliography.md#s5005)[[S9010]](../../sources/bibliography.md#s9010), then released Ascend versions of its kernel libraries in September 2026 [[S9009]](../../sources/bibliography.md#s9009)[[S9010]](../../sources/bibliography.md#s9010).
- **Software is only part of the lead.** GB300 [NVL72](../../glossary.md#nvl72) served DeepSeek-V4-Pro at ~$0.156 per million output tokens at 50 tokens/s per user, helped by its 72-GPU [NVLink](../../glossary.md#nvlink) domain [[S633]](../../sources/bibliography.md#s633).

![Heatmap scoring CUDA lock-in from 1 to 5 for seven customer segments across four workloads. Averages: academia 4.75, enterprises 4.50, sovereign AI 3.75, startups and neoclouds 3.75, hyperscalers 3.00, frontier labs 2.75, Chinese labs 2.50. Inference on popular models is the weakest column (average 2.7) versus about 3.9 for pre-training and new architectures.](../../assets/charts/09-moat-strength-by-segment.svg)

## 1. Training vs inference

**Training** is long and fragile: kernels, [NCCL](../../glossary.md#nccl) collectives and numerics must stay stable for months, so switching mid-generation is risky. Google and Anthropic manage it only by co-designing chip, compiler and model [[S653]](../../sources/bibliography.md#s653)[[S656]](../../sources/bibliography.md#s656).

**Popular-model inference** is narrow: one model, a fixed kernel set, measured cost per token, and fleets big enough to fund a port. AMD's DeepSeek-V4 sprint, Modular's MI355X port and [vLLM](../../glossary.md#vllm)'s TPU back end all target serving [[S631]](../../sources/bibliography.md#s631)[[S9022]](../../sources/bibliography.md#s9022)[[S9015]](../../sources/bibliography.md#s9015). **New and [agentic](../../glossary.md#agentic-ai) inference** swings back to NVIDIA: day-0 kernels and KV-offload libraries matured on CUDA [[S627]](../../sources/bibliography.md#s627).

> [!TIP]
> **Worked example — who can afford to leave?** Ironwood TPU served Qwen3.5 397B at **$0.181** per million tokens vs **$0.222** on B200 at 100 tokens/s per user [[S625]](../../sources/bibliography.md#s625), **~18% cheaper**. A lab spending an illustrative $10B a year on inference (🔴) would save **~$1.8B**. A 200-engineer porting team at ~$0.6M a head [[S401]](../../sources/bibliography.md#s401) costs **~$0.12B**, so it pays back in weeks. An enterprise spending $5M saves ~$0.9M, enough for ~1.5 engineers, far short of one ~1.8–5.5 engineer-year kernel port. **Conclusion:** lock-in falls as compute spend rises, so NVIDIA's largest customers have the strongest incentive to leave.

## 2. By customer segment

- **Frontier labs (2.75) and [hyperscalers](../../glossary.md#hyperscaler) (3.0)** run several stacks: Anthropic on TPU, Trainium and NVIDIA [[S653]](../../sources/bibliography.md#s653), Microsoft's Maia 200 on Copilot [[S90044]](../../sources/bibliography.md#s90044). Their exposure is research prototyping, which still starts on NVIDIA.
- **Chinese labs (2.5)** are pushed off by export controls. DeepSeek-V4 had day-0 Ascend support [[S633]](../../sources/bibliography.md#s633), and TileLang added an Ascend 950 back end [[S9011]](../../sources/bibliography.md#s9011).
- **Sovereign AI (3.75)** bought >$30B of NVIDIA systems in FY2026 (management commentary) [[S90071]](../../sources/bibliography.md#s90071) and rarely employs kernel engineers.
- **Startups and [neoclouds](../../glossary.md#neocloud) (3.75)** switch for price on popular models (MI355X up to 29.6% cheaper per token than B200 on GLM-5 [FP8](../../glossary.md#fp8) [[S637]](../../sources/bibliography.md#s637)) but stay on NVIDIA for anything new.
- **Enterprises (4.5) and academia (4.75)** depend on the long tail, tutorials and tools; for them the moat is close to absolute.

> [!TIP]
> **Worked example — how a library port moves a segment.** DeepSeek-V3 was trained on 2,048 H800 GPUs [[S34007]](../../sources/bibliography.md#s34007) with hand-tuned PTX in its communication library [[S5005]](../../sources/bibliography.md#s5005). In 2026 DeepEP announced an Ascend version with "the same API and full performance" [[S9009]](../../sources/bibliography.md#s9009), and DeepGEMM-Ascend followed on 2026-09-30 [[S9010]](../../sources/bibliography.md#s9010). **Conclusion:** once the libraries port, models built on them can move without code changes. A library moat falls library by library, which is why Chinese-lab scores are 2–3 despite DeepSeek's deep NVIDIA tuning.

## 3. The evidence, both ways

| Actor | Evidence for erosion | Evidence against |
|---|---|---|
| Anthropic | Up to 1M TPUs, >1 GW in 2026 [[S653]](../../sources/bibliography.md#s653); Trainium as primary training partner [[S656]](../../sources/bibliography.md#s656); 2 GW AMD Helios plan [[S9538]](../../sources/bibliography.md#s9538) | Up to 1 GW of NVIDIA Grace Blackwell / Vera Rubin, joint engineering [[S654]](../../sources/bibliography.md#s654) |
| OpenAI | 6 GW AMD from MI450 [[S546]](../../sources/bibliography.md#s546); 10 GW Broadcom-built accelerators [[S174]](../../sources/bibliography.md#s174); in-house ASIC vs Rubin [[S628]](../../sources/bibliography.md#s628) | NVIDIA's ~$30B equity investment (reported) [[S90015]](../../sources/bibliography.md#s90015) |
| Meta | MTIA 300 in production, three more generations through 2027 [[S561]](../../sources/bibliography.md#s561); rents TPUs [[S90025]](../../sources/bibliography.md#s90025) | Agreed to buy millions of NVIDIA chips (Feb 2026) [[S4006]](../../sources/bibliography.md#s4006) |
| DeepSeek / China | Ascend ports of DeepEP and DeepGEMM [[S9009]](../../sources/bibliography.md#s9009)[[S9010]](../../sources/bibliography.md#s9010) | DeepGEMM remains a CUDA codebase [[S9010]](../../sources/bibliography.md#s9010) |
| AMD software | Native in vLLM and SGLang [[S580]](../../sources/bibliography.md#s580)[[S582]](../../sources/bibliography.md#s582); MiniMax-M3 disaggregation on day 0 [[S627]](../../sources/bibliography.md#s627) | B200 ~5× MI355X on DeepSeek-V4 after 26 days [[S631]](../../sources/bibliography.md#s631); NVIDIA up to 5× cheaper per token on agentic GLM 5.3 [[S636]](../../sources/bibliography.md#s636) |
| Google TPU | ~18% cheaper per token than B200 on Qwen3.5 [[S625]](../../sources/bibliography.md#s625); sold into customer datacenters [[S90027]](../../sources/bibliography.md#s90027) | Framework breadth 14/36 vs CUDA 36/36 [[S577]](../../sources/bibliography.md#s577)[[S587]](../../sources/bibliography.md#s587) |

> [!WARNING]
> **Myth vs. reality: "CUDA is the moat."** On DeepSeek-V4, GB300 NVL72's lead came largely from keeping expert-parallel traffic inside one 72-GPU NVLink domain [[S633]](../../sources/bibliography.md#s633), and NVIDIA reportedly holds ~60% of TSMC's [CoWoS](../../glossary.md#cowos) allocation [[S90039]](../../sources/bibliography.md#s90039). **Reality:** the moat is software + [scale-up](../../glossary.md#scale-up) networking + supply. Matching CUDA without NVLink-class racks or CoWoS volume still loses deals ([Layer 05](../05-scale-up-nvlink-nvswitch/index.md), [Layer 03](../03-memory-packaging-supply-chain/index.md)).

> [!WARNING]
> **Myth vs. reality: "DeepSeek proved you don't need CUDA."** DeepSeek's 2025 code went *deeper* into NVIDIA-specific PTX and SASS [[S5005]](../../sources/bibliography.md#s5005)[[S9010]](../../sources/bibliography.md#s9010); its Ascend ports came in 2026 under export controls. **Reality:** it proved that efficiency beats raw GPU count ([CS5](../../case-studies/CS5-deepseek-moment-and-efficiency-shock.md)), not that CUDA is optional.

> [!NOTE]
> **🐂 Bull view.** Every vector leaks back to CUDA at the frontier, and new models run on CUDA first [[S633]](../../sources/bibliography.md#s633). NVIDIA adopts abstractions rather than fighting them, and ~$89B of quarterly Data Center revenue [[S90011]](../../sources/bibliography.md#s90011) funds more kernel engineers than any rival.

> [!WARNING]
> **🐻 Bear view.** The biggest buyers no longer need the moat: Anthropic, Google, Meta and OpenAI all run or are building non-NVIDIA stacks [[S653]](../../sources/bibliography.md#s653)[[S561]](../../sources/bibliography.md#s561)[[S174]](../../sources/bibliography.md#s174). Portable DSLs cut AMD's bring-up from months to weeks [[S631]](../../sources/bibliography.md#s631)[[S627]](../../sources/bibliography.md#s627), and AI agents may cut it further [[S9538]](../../sources/bibliography.md#s9538). As inference takes most compute, the moat covers a shrinking share of dollars.

> [!TIP]
> **Worked example — multi-sourcing, not exit.** Add up the announced non-NVIDIA commitments in the table: Anthropic >1 GW of TPUs in 2026 [[S653]](../../sources/bibliography.md#s653) plus 2 GW of AMD [[S9538]](../../sources/bibliography.md#s9538), and OpenAI 6 GW of AMD [[S546]](../../sources/bibliography.md#s546) plus 10 GW of Broadcom-built chips [[S174]](../../sources/bibliography.md#s174). That is **≥19 GW**, delivered over several years. The same labs also signed with NVIDIA (Anthropic up to 1 GW [[S654]](../../sources/bibliography.md#s654)), and NVIDIA sized Blackwell plus Vera Rubin demand at **$1 trillion** through 2027 [[S90001]](../../sources/bibliography.md#s90001). **Conclusion:** frontier labs are adding second and third sources, not leaving; erosion shows up first as lost *share of growth* and pricing power.

> [!IMPORTANT]
> **Bottom line.** 🔴 Our assessment: the CUDA moat is a **time tax plus a breadth tax**, not a wall. Frontier labs, hyperscalers and Chinese labs can now pay it when price, supply or politics justify; for everyone else it is prohibitive, which keeps NVIDIA the default. It weakens fastest if high-volume inference settles on a few architectures every rival can tune once.

<details>
<summary>🔧 Under the hood: how the segment scores were built</summary>

- Scores (1 = can move in months, 5 = prohibitive) weigh kernel-engineering capacity, head-vs-tail workloads, alternative stacks and public evidence of moves; each row's rationale and sources are in `data/l09_moat_by_segment.csv` (all speculative).
- They are relative: a 2 means the business *can* move, not that NVIDIA loses it.

</details>

## 🎯 Corp Dev Lens

1. **Segment the opportunity.** A challenger only needs the low-lock-in cells: popular-model inference at hyperscalers, frontier labs and price-sensitive neoclouds. Which can a newcomer reach without a top lab as anchor?
2. **Buy breadth, not just speed.** The bring-up gap is weeks; the breadth gap (36 vs 26 vs 4) is years. Upstream maintainers and packaging/CI teams compound fastest.
3. **Qualcomm question (public information only):** after the Modular deal [[S9511]](../../sources/bibliography.md#s9511), is the goal first-class status in the open stack (vLLM, [Triton](../../glossary.md#triton), [PyTorch](../../glossary.md#pytorch)) or a parallel Mojo/MAX stack? The first rides the erosion vectors; the second must win developers from zero.
4. **Watch anchor deals.** Each 1–10 GW deal (Anthropic–TPU, OpenAI–AMD, OpenAI–Broadcom) funds software that lowers lock-in for everyone after it.

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S3**](../../sources/bibliography.md#s3) StorageNewsletter, *NVIDIA Q2 Fiscal 2027 results coverage: revenue $96.2B*, 2026-08-27. [Link](https://www.storagenewsletter.com/2026/08/27/nvidia-fiscal-2q27-financial-results/)
- [**S174**](../../sources/bibliography.md#s174) OpenAI, *OpenAI and Broadcom announce strategic collaboration to deploy 10 gigawatts of OpenAI-designed AI accelerators*, 2025-10-13. [Link](https://openai.com/index/openai-and-broadcom-announce-strategic-collaboration/)
- [**S401**](../../sources/bibliography.md#s401) NVIDIA Corporation via SEC EDGAR, *NVIDIA Corporation Form 10-K for fiscal year ended January 25, 2026*, 2026-02-25. [Link](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm)
- [**S546**](../../sources/bibliography.md#s546) TechWire Asia, *AMD Advancing AI 2026: Helios, OpenAI, Meta, Anthropic*, 2026-07. [Link](https://techwireasia.com/2026/07/amd-advancing-ai-2026-helios-openai-meta-anthropic/)
- [**S561**](../../sources/bibliography.md#s561) DatacenterDynamics, *Meta unveils next four generations of its MTIA chip*, 2026-03-11. [Link](https://www.datacenterdynamics.com/en/news/meta-unveils-next-four-generations-of-its-mtia-chip/)
- [**S577**](../../sources/bibliography.md#s577) JAX (GitHub: jax-ml/jax docs/installation.md), *JAX installation guide — supported platforms*, 2026-11. [Link](https://github.com/jax-ml/jax/blob/main/docs/installation.md)
- [**S580**](../../sources/bibliography.md#s580) vLLM project (GitHub), *vLLM README and installation docs — supported hardware*, 2026-11. [Link](https://github.com/vllm-project/vllm/blob/main/docs/getting_started/installation/README.md)
- [**S582**](../../sources/bibliography.md#s582) SGLang project (GitHub: sgl-project/sglang), *SGLang README — supported hardware*, 2026-11. [Link](https://github.com/sgl-project/sglang/blob/main/README.md)
- [**S587**](../../sources/bibliography.md#s587) PyTorch (GitHub: pytorch/pytorch), *PyTorch README — building with CUDA, ROCm and Intel GPU support*, 2026-11. [Link](https://github.com/pytorch/pytorch/blob/main/README.md)
- [**S625**](../../sources/bibliography.md#s625) SemiAnalysis, *TPU Inference Externalization Full Steam Ahead*, 2026-09-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/tpu-inferencex-full-steam.mdx)
- [**S627**](../../sources/bibliography.md#s627) SemiAnalysis, *AgentX - InferenceXv3: Does the CUDA Moat Hold Up in Agentic Inferencing?*, 2026-08-24. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/agentx-inferencexv3-does-cuda-moat.mdx)
- [**S628**](../../sources/bibliography.md#s628) SemiAnalysis, *OpenAI Jalapeño: Better Than Nvidia Blackwell*, 2026-08-25. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/openai-jalapeno-better-than-nvidia.mdx)
- [**S631**](../../sources/bibliography.md#s631) SemiAnalysis, *MI355X DeepSeek-V4-Pro on SGLang: 110.5x Throughput per GPU in 26 Days*, 2026-05-26. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/mi355x-deepseek-v4-pro-sglang-110x-in-26-days.mdx)
- [**S633**](../../sources/bibliography.md#s633) SemiAnalysis, *DeepSeekV4 1.6T Day 0 to Day 43 Performance Over Time — Huawei, GB300 NVL72, MI355X, B200*, 2026-06-09. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/deepseekv4-16t-day-0-to-day-43-performance.mdx)
- [**S636**](../../sources/bibliography.md#s636) SemiAnalysis, *GLM 5.3 on AgentX: NVIDIA Is Up to 5x Cheaper per Token at 150 tok/s/user*, 2026-08-25. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/glm-5-3-agentx-nvidia-vs-amd-sglang-150-toks.mdx)
- [**S637**](../../sources/bibliography.md#s637) SemiAnalysis, *AMD MI355X GLM-5 Inference: Up to 29.6% Lower Cost per Million Tokens than B200 on SGLang FP8*, 2026-05-25. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/mi355x-glm5-fp8-sglang-40-cheaper-than-b200.mdx)
- [**S653**](../../sources/bibliography.md#s653) Anthropic, *Expanding our use of Google Cloud TPUs and Services*, 2025-10-23. [Link](https://www.anthropic.com/news/expanding-our-use-of-google-cloud-tpus-and-services)
- [**S654**](../../sources/bibliography.md#s654) Anthropic, *Microsoft, NVIDIA, and Anthropic announce strategic partnerships*, 2025-11-18. [Link](https://www.anthropic.com/news/microsoft-nvidia-anthropic-announce-strategic-partnerships)
- [**S656**](../../sources/bibliography.md#s656) Anthropic, *Powering the next generation of AI development with AWS (expanded Amazon partnership and Trainium)*, 2024-11-22. [Link](https://www.anthropic.com/news/anthropic-amazon-trainium)
- [**S4006**](../../sources/bibliography.md#s4006) SiliconANGLE, *Meta agrees to buy millions of AI chips from Nvidia, raising doubts about its in-house hardware*, 2026-02-17. [Link](https://siliconangle.com/2026/02/17/meta-agrees-buy-millions-ai-chips-nvidia-raising-doubts-house-hardware/)
- [**S5005**](../../sources/bibliography.md#s5005) DeepSeek-AI (GitHub) (DeepSeek-AI), *DeepEP: an efficient expert-parallel communication library (README v1.2.1)*, 2025. [Link](https://github.com/deepseek-ai/DeepEP/blob/v1.2.1/README.md)
- [**S9009**](../../sources/bibliography.md#s9009) DeepSeek-AI (GitHub) (DeepSeek-AI), *DeepEP README (main branch: V2.5 and Ascend version)*, 2026-11. [Link](https://github.com/deepseek-ai/DeepEP/blob/main/README.md)
- [**S9010**](../../sources/bibliography.md#s9010) DeepSeek-AI (GitHub) (DeepSeek-AI), *DeepGEMM README*, 2026-09-30. [Link](https://github.com/deepseek-ai/DeepGEMM/blob/main/README.md)
- [**S9011**](../../sources/bibliography.md#s9011) tile-ai (GitHub), *TileLang README (news and backends)*, 2026-09-30. [Link](https://github.com/tile-ai/tilelang/blob/main/README.md)
- [**S9015**](../../sources/bibliography.md#s9015) vLLM project (GitHub: vllm-project/tpu-inference), *vLLM JAX (formerly tpu-inference) README*, 2026-11. [Link](https://github.com/vllm-project/tpu-inference/blob/main/README.md)
- [**S9022**](../../sources/bibliography.md#s9022) Modular, *Achieving state-of-the-art performance on AMD MI355 in just 14 days*, 2025-10-17. [Link](https://www.modular.com/blog/achieving-state-of-the-art-performance-on-amd-mi355----in-just-14-days)
- [**S9511**](../../sources/bibliography.md#s9511) Nasdaq (Qualcomm press release), *Qualcomm Completes Acquisition of Modular*, 2026-07-29. [Link](https://www.nasdaq.com/press-release/qualcomm-completes-acquisition-modular-2026-07-29)
- [**S9538**](../../sources/bibliography.md#s9538) The Next Web, *AMD is investing $5 billion in Anthropic and deploying 2 gigawatts of Helios GPUs to run Claude*, 2026. [Link](https://thenextweb.com/news/amd-anthropic-5-billion-investment-2gw-helios-mi450)
- [**S34007**](../../sources/bibliography.md#s34007) arXiv:2412.19437 (DeepSeek-AI), *DeepSeek-V3 Technical Report*, 2024-12-27. [Link](https://arxiv.org/abs/2412.19437)
- [**S90001**](../../sources/bibliography.md#s90001) The Star (Reuters), *Nvidia bets on AI inference as chip revenue opportunity hits $1 trillion (Reuters)*, 2026-03-17. [Link](https://www.thestar.com.my/tech/tech-news/2026/03/17/nvidia-bets-on-ai-inference-as-chip-revenue-opportunity-hits-1-trillion)
- [**S90011**](../../sources/bibliography.md#s90011) Nasdaq (Zacks), *NVIDIA Q2 earnings beat on Blackwell Ultra and Data Center strength*, 2026-08-27. [Link](https://www.nasdaq.com/articles/nvidia-q2-earnings-beat-blackwell-ultra-data-center-strength)
- [**S90015**](../../sources/bibliography.md#s90015) DatacenterDynamics, *Nvidia plans $30bn investment in upcoming OpenAI funding round*, 2026-02. [Link](https://www.datacenterdynamics.com/en/news/nvidia-plans-30bn-investment-in-upcoming-openai-funding-round/)
- [**S90025**](../../sources/bibliography.md#s90025) SiliconANGLE, *Google and Meta reportedly strike new multibillion-dollar AI chip deal*, 2026-02-26. [Link](https://siliconangle.com/2026/02/26/google-meta-reportedly-strike-new-multibillion-dollar-ai-chip-deal/)
- [**S90027**](../../sources/bibliography.md#s90027) The Next Web, *Google is building a four-partner chip supply chain to challenge Nvidia in AI inference*, 2026. [Link](https://thenextweb.com/news/google-inference-chips-nvidia-challenge-supply-chain)
- [**S90039**](../../sources/bibliography.md#s90039) TrendForce, *Samsung, SK hynix reportedly tapped as NVIDIA Rubin HBM4 suppliers; shipments could start in March*, 2026-03-09. [Link](https://www.trendforce.com/news/2026/03/09/news-samsung-sk%E2%80%AFhynix-reportedly-tapped-as-nvidia-rubin-hbm4-suppliers-shipments-could-start-in-march/)
- [**S90044**](../../sources/bibliography.md#s90044) eWeek, *Microsoft introduces Maia 200, its most powerful AI chip yet*, 2026-01-27. [Link](https://www.eweek.com/news/microsoft-maia-200-ai-chip/)
- [**S90071**](../../sources/bibliography.md#s90071) Crypto Briefing, *Nvidia CFO emphasizes neutral partnership with AI customers as company diversifies beyond hyperscalers*, 2026. [Link](https://cryptobriefing.com/nvidia-cfo-neutral-ai-partnership/)
