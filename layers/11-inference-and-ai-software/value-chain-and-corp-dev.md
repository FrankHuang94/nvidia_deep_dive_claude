# Inference and AI software: Value chain and corp dev angles

<sub>Layer 11 · Inference and AI software · ~12 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **Labs keep most of each API dollar:** OpenAI's reported [compute margin](../../glossary.md#compute-margin) was ~70% in October 2025; Est. ~16¢ goes to the cloud and ~5¢ to NVIDIA as gross profit 🔴 [[S11537]](../../sources/bibliography.md#s11537)[[S622]](../../sources/bibliography.md#s622)[[S3]](../../sources/bibliography.md#s3).
- **Fixed-quality token prices deflate fast** ($20 → $0.07 per million in two years at GPT-3.5 level), yet GPT-5.5 launched at twice GPT-5.4's price 🟡 [[S11526]](../../sources/bibliography.md#s11526)[[S11535]](../../sources/bibliography.md#s11535).
- **NVIDIA's software line is small:** AI Enterprise lists at $4,500 per GPU-year; a ~$2B run rate exiting FY2025 is under 1% of FY2026 revenue [[S9515]](../../sources/bibliography.md#s9515)[[S11011]](../../sources/bibliography.md#s11011)[[S1]](../../sources/bibliography.md#s1).
- **[Inference providers](../../glossary.md#inference-provider) price like chip start-ups:** Fireworks ~$15B (talks), Together AI $8.3B, Baseten $5B; NVIDIA invested in the latter two [[S11514]](../../sources/bibliography.md#s11514)[[S11516]](../../sources/bibliography.md#s11516)[[S11518]](../../sources/bibliography.md#s11518).
- **Deals:** NVIDIA–Groq (~$20B), NVIDIA–Hugging Face (~$12.9B, pending), Qualcomm–Modular ($3.9B), AMD–Silo AI ($665M) [[S90019]](../../sources/bibliography.md#s90019)[[S11026]](../../sources/bibliography.md#s11026)[[S90057]](../../sources/bibliography.md#s90057)[[S9506]](../../sources/bibliography.md#s9506).
- **[Q8 · Value pools & M&A angles]** Pools: lab margin, cloud rental margin, NVIDIA hardware. Angles: portable software, [decode](../../glossary.md#decode) silicon and the inference clouds that pick hardware.

![Waterfall chart splitting $1.00 of API revenue: the model lab's compute margin leaves ~70 cents of gross profit (reported ~70% for OpenAI, Oct 2025); the remaining 30 cents of compute splits into the cloud operator's gross margin (~16 cents, from rental $5.00 vs owner TCO $2.31 per GB300 GPU-hour), electricity (~2 cents), facility, operations and financing (~3 cents), other IT hardware (~2 cents), NVIDIA's cost of goods (~2 cents) and NVIDIA's gross profit (~5 cents). The lab's share must still fund training compute and R&D, much of which also flows to NVIDIA.](../../assets/charts/11-token-revenue-value-pools.svg)

## Who earns the margin on a token

Think of a token as a restaurant meal: the model lab owns the recipe and brand, the cloud rents the kitchen, NVIDIA sold the ovens. The brand sets the menu price, so the lab keeps most of the bill while customers want its model.

> [!TIP]
> **Worked example — one million DeepSeek-R1 tokens on GB300 [NVL72](../../glossary.md#nvl72).** At 50 tokens/s per user a GB300 GPU emits ~6,261 tokens/s, or ~22.5M an hour [[S621]](../../sources/bibliography.md#s621). At SemiAnalysis's $5.00 rental price that is ~$0.22 per million tokens; at the owner's $2.31 [TCO](../../glossary.md#tco), ~$0.10 [[S622]](../../sources/bibliography.md#s622). NVIDIA's revenue is ~23% of the rental (~$1.13 per [GPU-hour](../../glossary.md#gpu-hour)): ~$0.05 per million tokens, ~$0.04 of it gross profit 🔴 [[S3]](../../sources/bibliography.md#s3). If compute is 30% of revenue, the lab charges ~$0.74 per million.

<details>
<summary>🔧 Under the hood: assumptions and sensitivity</summary>

Inputs: OpenAI's ~70% compute margin [[S11537]](../../sources/bibliography.md#s11537)[[S11538]](../../sources/bibliography.md#s11538), SemiAnalysis rental vs owner TCO [[S622]](../../sources/bibliography.md#s622), power ~15% of owner TCO, NVIDIA ~75% of IT hardware (GPUs are ~63% of a GB300 rack's price) [[S332]](../../sources/bibliography.md#s332) and a 75.0% NVIDIA gross margin [[S3]](../../sources/bibliography.md#s3). At the end-2024 lab margin of 52%, NVIDIA's gross profit is ~8¢; contract rates below list shrink the cloud's share; training compute is excluded. Data: `l11_token_value_pools.csv`.

</details>

## Token price deflation, and its limits

![Log-scale chart of API prices per million tokens. The cheapest model at GPT-3.5-level quality fell from $20 (Nov 2022) to $0.07 (Oct 2024), ~286x. OpenAI's flagship fell from GPT-4 at $37.50 blended (Mar 2023) through GPT-4 Turbo ($15), GPT-4o ($7.50, then $4.38) to GPT-5 at $3.44 (Aug 2025), ~11x cheaper, then GPT-5.5 launched at $11.25 (Apr 2026, reported), 3.3x GPT-5. OpenAI's small tier fell from gpt-3.5-turbo at $2.00 (2023) to GPT-4o mini ($0.26) and GPT-5 nano ($0.14).](../../assets/charts/11-api-token-price-trend.svg)

[Token price deflation](../../glossary.md#token-price-deflation) comes from better hardware, software and smaller models. An MIT study puts frontier-quality declines at 5–10× a year [[S11527]](../../sources/bibliography.md#s11527). Prices here are [blended](../../glossary.md#blended-token-price) 3:1 input to output, Epoch's convention [[S11525]](../../sources/bibliography.md#s11525). Cheaper tokens have so far meant more tokens: Google's monthly volume rose from 9.7 trillion (April 2024) to over 1.3 quadrillion (October 2025), a [Jevons paradox](../../glossary.md#jevons-paradox) [[S32018]](../../sources/bibliography.md#s32018)[[S32020]](../../sources/bibliography.md#s32020). The same squeeze hit GPU rentals, which fell ~75% for H100 in two years [[S393]](../../sources/bibliography.md#s393)[[S395]](../../sources/bibliography.md#s395).

![Scatter chart of GPU rental prices over time. H100: AWS p5 on-demand $12.29 per GPU-hour at launch in July 2023 and $6.88 after the June 2025 cut; neocloud H100 about $8 in 2023, marketplaces under $2 by late 2024, Lambda $2.99 and CoreWeave $6.16 list in 2025. Blackwell list prices in 2025: B200 $4.99 (Lambda) to $8.60 (CoreWeave), GB200 $10.50 (CoreWeave).](../../assets/charts/14-gpu-rental-price-trend.svg)

> [!TIP]
> **Worked example — who absorbs deflation.** A provider sells tokens at a 50% gross margin. Next year price falls 50% and cost per token 30%: cost is 0.5 × 0.7 = 0.35 of the old price against revenue of 0.5, so margin drops to 30%. To hold 50%, cost must fall as fast as price, so providers chase every software gain and each new GPU.

## NVIDIA AI Enterprise economics

> [!TIP]
> **Worked example — what the licence adds per rack.** A GB300 NVL72 rack of 72 GPUs at the $4,500 list is $324K a year, ~8% of a ~$4M rack price per year [[S9515]](../../sources/bibliography.md#s9515)[[S332]](../../sources/bibliography.md#s332); NIM in production needs this licence, or ~$1 per GPU-hour in the cloud [[S11013]](../../sources/bibliography.md#s11013). Huang floated ~$2,000 per GPU a year for agent software in October 2026 [[S11016]](../../sources/bibliography.md#s11016). The bear point: software was a ~$1B run rate in Q4 FY2024 [[S9516]](../../sources/bibliography.md#s9516), tiny next to hardware, and open engines let buyers skip the fee ([competition](competition.md)).

## Private companies and M&A in the layer

| Company | What they do | Stage / last public funding | Why it matters |
|---|---|---|---|
| Fireworks AI | Open-model inference cloud | Talks at ~$15B (May 2026); $30–40B talks reported 🟡 | Largest independent token seller by value [[S11514]](../../sources/bibliography.md#s11514)[[S11515]](../../sources/bibliography.md#s11515) |
| Together AI | Inference and training cloud | Series C $800M at $8.3B (Jul 2026); NVIDIA in round | Dynamo 1.0 adopter [[S11516]](../../sources/bibliography.md#s11516)[[S90066]](../../sources/bibliography.md#s90066) |
| Baseten | Inference platform | Series E $300M at $5B (Jan 2026); NVIDIA anchor | 2× faster TTFT with Dynamo routing [[S11518]](../../sources/bibliography.md#s11518)[[S11001]](../../sources/bibliography.md#s11001) |
| Modal Labs | Serverless GPU compute | Talks at ~$2.5B (Feb 2026) 🟡 | Developer on-ramp [[S11519]](../../sources/bibliography.md#s11519) |
| Inferact | Company behind vLLM | Seed $150M at $800M (Jan 2026) | Steers the most portable engine [[S11511]](../../sources/bibliography.md#s11511)[[S11540]](../../sources/bibliography.md#s11540) |
| RadixArk | Company behind SGLang | Seed $100M at $400M (May 2026); NVIDIA, AMD reported in round | Engine behind many InferenceX frontiers [[S11513]](../../sources/bibliography.md#s11513) |
| Cerebras (listed May 2026) | Wafer-scale systems and cloud | IPO raised $5.55B at ~$40B | OpenAI up to 750 MW [[S2505]](../../sources/bibliography.md#s2505)[[S11523]](../../sources/bibliography.md#s11523) |
| Groq | GroqCloud API | ~$6.9B (Sep 2025), then ~$20B NVIDIA licence | Can a licensor keep competing? [[S90019]](../../sources/bibliography.md#s90019) |
| Etched | Transformer-only ASIC | Series C $300M at $10.3B (Jul 2026) | Specialisation bet; ~$1B pre-orders reported [[S2507]](../../sources/bibliography.md#s2507) |
| Positron | Memory-first inference ASIC | Series C $875M at $5B (Sep 2026) | ~5× step-up since Feb 2026 [[S11521]](../../sources/bibliography.md#s11521)[[S11520]](../../sources/bibliography.md#s11520) |
| d-Matrix | Digital in-memory compute | Series C $275M at $2B (Nov 2025) | SRAM decode without a wafer [[S2511]](../../sources/bibliography.md#s2511) |
| Tenstorrent | RISC-V AI chips, open stack | Series D $693M at ~$2.7B (Dec 2024) | Licensable IP [[S2509]](../../sources/bibliography.md#s2509) |
| MatX | LLM accelerators | Series B $500M (Feb 2026); valuation undisclosed | Shipments planned 2027 [[S2508]](../../sources/bibliography.md#s2508) |
| SambaNova | Dataflow chips and cloud | Intel talks at ~$1.6B incl. debt stalled | Possible distressed asset [[S2512]](../../sources/bibliography.md#s2512) |
| Rebellions, FuriosaAI | Korean inference NPUs | FuriosaAI bridge ~$122M (Jul 2025) | Already supported by Ray [[S11522]](../../sources/bibliography.md#s11522)[[S584]](../../sources/bibliography.md#s584) |

<sub>Public information only; valuations are post-money unless marked as talks or offers.</sub>

![Log-scale horizontal bar chart of inference start-up valuations. Inference clouds: Fireworks AI ~$15,000M (talks, May 2026), Together AI $8,300M (Jul 2026), Baseten $5,000M (Jan 2026), Modal ~$2,500M (talks). Serving software: Hugging Face $12,930M (NVIDIA acquisition announced Sep 2026, pending), Modular $3,900M (acquired by Qualcomm, 2026), Inferact (vLLM) $800M and RadixArk (SGLang) $400M seed valuations. Silicon: Cerebras ~$40,000M at its May 2026 IPO, Etched $10,300M, Groq $6,900M before its ~$20B NVIDIA licence, Positron $5,000M, Tenstorrent ~$2,700M, d-Matrix $2,000M, SambaNova ~$1,600M (Intel offer talks); MatX and FuriosaAI valuations undisclosed.](../../assets/charts/11-inference-startup-valuations.svg)

### M&A history in the layer

| Acquirer | Deals (year, value) | Logic |
|---|---|---|
| NVIDIA | Deci, Run:ai, OctoAI (2024; ~$300M, ~$700M, ~$250M); CentML (2025, >$400M with earn-outs); Groq licence + team (2025, ~$20B); Hugging Face (2026, ~$12.9B, pending) | Compiler and serving talent, SRAM decode, model distribution [[S478]](../../sources/bibliography.md#s478)[[S476]](../../sources/bibliography.md#s476)[[S11510]](../../sources/bibliography.md#s11510)[[S11509]](../../sources/bibliography.md#s11509)[[S90019]](../../sources/bibliography.md#s90019)[[S11026]](../../sources/bibliography.md#s11026) |
| AMD | Nod.ai (2023); Silo AI (2024, $665M); Brium and the Untether AI team (2025); MK1 (2025) | Close the software gap on ROCm [[S9508]](../../sources/bibliography.md#s9508)[[S9506]](../../sources/bibliography.md#s9506)[[S9507]](../../sources/bibliography.md#s9507)[[S9509]](../../sources/bibliography.md#s9509) |
| Qualcomm | Modular (announced at $3.9B, closed 2026-07-29) | Hardware-portable runtime (Mojo, MAX) [[S90057]](../../sources/bibliography.md#s90057)[[S9511]](../../sources/bibliography.md#s9511) |
| Red Hat (IBM) | Neural Magic (2024) | Commercial vLLM; later co-founded llm-d [[S9533]](../../sources/bibliography.md#s9533)[[S11503]](../../sources/bibliography.md#s11503) |
| Intel | SambaNova (talks, ~$1.6B incl. debt, stalled) | Inference silicon re-entry [[S2512]](../../sources/bibliography.md#s2512) |

> [!TIP]
> **Worked example — what a token seller is worth.** Together AI's $8.3B valuation is ~2.5× its ~$3.3B Series B of February 2025 [[S11516]](../../sources/bibliography.md#s11516); on the NVIDIA side, the ~$20B Groq price was ~2.9× Groq's last private mark of ~$6.9B [[S90019]](../../sources/bibliography.md#s90019). Buyers are paying for scarcity in inference, not for current revenue.

The full deal chart is on [History and how NVIDIA built it](history-and-how-built.md).

**[Q8 · Value pools & M&A angles]** The largest pool is the model lab's margin (~70% of API revenue, before training costs), then the cloud's rental margin, then NVIDIA's hardware margin; NVIDIA's own software is under 1% of revenue [[S11537]](../../sources/bibliography.md#s11537)[[S622]](../../sources/bibliography.md#s622)[[S11011]](../../sources/bibliography.md#s11011). M&A followed scarcity: NVIDIA paid little for engine teams and a lot for decode silicon and distribution; AMD and Qualcomm bought portability. Open angles: portable serving companies (Inferact, RadixArk), [SRAM](../../glossary.md#sram) or near-memory decode IP (d-Matrix, Positron, Etched) and the inference clouds that choose hardware for [open-weight models](../../glossary.md#open-weight-model).

## 🎯 Corp Dev Lens

1. Qualcomm ships a [vLLM](../../glossary.md#vllm) container for AI 100 and now owns Modular [[S596]](../../sources/bibliography.md#s596)[[S9511]](../../sources/bibliography.md#s9511): should AI200/AI250 software lean on upstream vLLM/llm-d for reach, on MAX for differentiation, or both?
2. NVIDIA holds stakes in Together AI and Baseten [[S11516]](../../sources/bibliography.md#s11516)[[S11518]](../../sources/bibliography.md#s11518). What would make an inference cloud qualify a second platform?
3. NVIDIA licensed Groq rather than buying it. Would licences or minority stakes in SRAM and near-memory start-ups beat $2–10B acquisitions?
4. If labs keep ~70¢ of each API dollar, is co-design with a token buyer (a HUMAIN-style sovereign or a lab) worth more than a merchant sale [[S90030]](../../sources/bibliography.md#s90030)?
5. If regulators condition NVIDIA's Hugging Face deal, could neutral model distribution become a partnership opportunity [[S11027]](../../sources/bibliography.md#s11027)?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S1**](../../sources/bibliography.md#s1) NVIDIA Corporation via SEC EDGAR, *NVIDIA Announces Financial Results for Fourth Quarter and Fiscal 2026 (Form 8-K exhibit 99.1)*, 2026-02-25. [Link](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000019/q4fy26pr.htm)
- [**S3**](../../sources/bibliography.md#s3) StorageNewsletter, *NVIDIA Q2 Fiscal 2027 results coverage: revenue $96.2B*, 2026-08-27. [Link](https://www.storagenewsletter.com/2026/08/27/nvidia-fiscal-2q27-financial-results/)
- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S393**](../../sources/bibliography.md#s393) Latent Space (Eugene Cheah), *$2 H100s: how the GPU bubble burst*, 2024-10. [Link](https://www.latent.space/p/gpu-bubble)
- [**S395**](../../sources/bibliography.md#s395) Lambda, *Lambda GPU cloud pricing*, 2025. [Link](https://lambda.ai/pricing)
- [**S476**](../../sources/bibliography.md#s476) NVIDIA Blog, *NVIDIA to Acquire GPU Orchestration Software Provider Run:ai*, 2024-04-24. [Link](https://blogs.nvidia.com/blog/runai/)
- [**S478**](../../sources/bibliography.md#s478) NVIDIA, *NVIDIA Blog and Newsroom acquisition announcements (Cumulus, SwiftStack, DeepMap, Bright Computing, Excelero, Shoreline, Brev.dev, OctoAI, VinBrain, Gretel, Lepton AI, CentML, SchedMD)*, 2025-12. [Link](https://blogs.nvidia.com/)
- [**S584**](../../sources/bibliography.md#s584) Ray project (GitHub: ray-project/ray), *Ray accelerator managers (python/ray/_private/accelerators)*, 2026-11. [Link](https://github.com/ray-project/ray/blob/master/python/ray/_private/accelerators/__init__.py)
- [**S596**](../../sources/bibliography.md#s596) Qualcomm (GitHub: quic), *Qualcomm Cloud AI SDK and Efficient Transformers repositories*, 2026-11. [Link](https://github.com/quic/cloud-ai-sdk)
- [**S621**](../../sources/bibliography.md#s621) SemiAnalysis (InferenceX-app repository), *InferenceX public API snapshot (benchmarks.json and benchmarks-history.json fixtures)*, 2026-10-17. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/tree/main/packages/app/cypress/fixtures/api)
- [**S622**](../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S2505**](../../sources/bibliography.md#s2505) Dealroom, *Cerebras raises $5.55B in biggest US IPO of 2026*, 2026-05. [Link](https://dealroom.co/news/128936-cerebras-raises-5-55b-in-biggest-us-ipo-of-2026/)
- [**S2507**](../../sources/bibliography.md#s2507) AI Weekly, *Etched closes $300M Series C at $10.3B led by Sequoia, books ~$1B in pre-orders for Sohu*, 2026-07. [Link](https://aiweekly.co/alerts/etched-closes-300m-series-c-at-103b-led-by-sequoia-books-1b-in-pre-orders-for)
- [**S2508**](../../sources/bibliography.md#s2508) AI2.Work, *MatX raises $500M to build AI chips*, 2026-02-24. [Link](https://ai2.work/blog/matx-raises-500m-to-build-ai-chips-that-beat-nvidia-by-10x)
- [**S2509**](../../sources/bibliography.md#s2509) TechPowerUp, *Tenstorrent closes $693M+ of Series D funding led by Samsung Securities and AFW Partners*, 2024-12-02. [Link](https://techpowerup.com/329396/tenstorrent-closes-usd-693m-of-series-d-funding-led-by-samsung-securities-and-afw-partners)
- [**S2511**](../../sources/bibliography.md#s2511) Converge Digest, *d-Matrix raises $275 million to accelerate the age of AI inference*, 2025-11-12. [Link](https://convergedigest.com/d-matrix-raises-275-million-to-accelerate-the-age-of-ai-inference/)
- [**S2512**](../../sources/bibliography.md#s2512) Verdict, *Intel pursues SambaNova acquisition amid AI expansion plans*, 2025-12. [Link](https://www.verdict.co.uk/intel-sambanova-acquisition/)
- [**S9506**](../../sources/bibliography.md#s9506) Converge Digest, *AMD completes $665 million acquisition of Silo AI*, 2024-08. [Link](https://convergedigest.com/amd-completes-665-million-acquisition-of-silo-ai/?amp=1)
- [**S9507**](../../sources/bibliography.md#s9507) DatacenterDynamics, *AMD extends acquisition run: brings software optimization firm Brium and staff from recently shuttered Untether AI into the fold*, 2025-06. [Link](https://www.datacenterdynamics.com/en/news/amd-extends-acquisition-run-brings-software-optimization-firm-brium-and-staff-from-recently-shuttered-untether-ai-into-the-fold/)
- [**S9508**](../../sources/bibliography.md#s9508) PrivSource (deal record of AMD press release), *AMD to Acquire Nod.ai to Expand Open-Source AI Software Capabilities*, 2023-10. [Link](https://www.privsource.com/acquisitions/deal/amd-to-acquire-nod-ai-to-expand-open-source-ai-software-capabilities-bWSr8y)
- [**S9509**](../../sources/bibliography.md#s9509) PrivSource (deal record), *AMD Acquires MK1*, 2025-11. [Link](https://www.privsource.com/acquisitions/deal/y3S4jb)
- [**S9511**](../../sources/bibliography.md#s9511) Nasdaq (Qualcomm press release), *Qualcomm Completes Acquisition of Modular*, 2026-07-29. [Link](https://www.nasdaq.com/press-release/qualcomm-completes-acquisition-modular-2026-07-29)
- [**S9515**](../../sources/bibliography.md#s9515) The Register (Tobias Mann), *Nvidia's software empire (NVIDIA AI Enterprise licensing)*, 2024-08-06. [Link](https://www.theregister.com/2024/08/06/nvidia_software_empire/)
- [**S9516**](../../sources/bibliography.md#s9516) MarketBeat, *NVIDIA Q4 FY2024 earnings call transcript*, 2024-02-21. [Link](https://www.marketbeat.com/earnings/reports/2024-2-21-nvidia-co-stock)
- [**S9533**](../../sources/bibliography.md#s9533) Red Hat Blog, *FAQ: Red Hat to acquire Neural Magic*, 2024-11-12. [Link](https://www.redhat.com/en/blog/red-hat-acquire-neural-magic-FAQ)
- [**S11001**](../../sources/bibliography.md#s11001) NVIDIA (GitHub), *NVIDIA Dynamo README (ai-dynamo/dynamo)*, 2026-11. [Link](https://github.com/ai-dynamo/dynamo/blob/main/README.md)
- [**S11011**](../../sources/bibliography.md#s11011) MarketBeat, *NVIDIA Q2 Fiscal 2025 earnings call transcript (28 August 2024)*, 2024-08-28. [Link](https://www.marketbeat.com/earnings/transcripts/110080/)
- [**S11013**](../../sources/bibliography.md#s11013) NVIDIA (docs.api.nvidia.com), *NVIDIA NIM FAQ*, 2025. [Link](https://docs.api.nvidia.com/nim/docs/faq)
- [**S11016**](../../sources/bibliography.md#s11016) TweakTown, *Jensen Huang puts a $2000 per GPU yearly price on NVIDIA's AI agent software*, 2026-10. [Link](https://www.tweaktown.com/news/114285/jensen-huang-puts-a-dollars2000-per-gpu-yearly-price-on-nvidias-ai-agent-software/index.html)
- [**S11026**](../../sources/bibliography.md#s11026) Implicator.ai, *Nvidia confirms $12.9 billion Hugging Face deal, says its chips won't be required*, 2026-09. [Link](https://www.implicator.ai/nvidia-confirms-12-9-billion-hugging-face-deal-says-its-chips-wont-be-required/)
- [**S11027**](../../sources/bibliography.md#s11027) MLex, *Nvidia may seek EU review of Hugging Face deal amid filing uncertainty*, 2026-09-23. [Link](https://www.mlex.com/mlex/articles/2528556/nvidia-may-seek-eu-review-of-hugging-face-deal-amid-european-filing-uncertainty)
- [**S11503**](../../sources/bibliography.md#s11503) llm-d project (GitHub: llm-d/llm-d), *llm-d README (distributed inference on Kubernetes)*, 2026-11. [Link](https://github.com/llm-d/llm-d/blob/main/README.md)
- [**S11509**](../../sources/bibliography.md#s11509) The Logic, *Nvidia's deal for CentML could be worth more than US$400M*, 2025-06. [Link](https://thelogic.co/news/exclusive/nvidias-deal-centml-us400m/)
- [**S11510**](../../sources/bibliography.md#s11510) Analytics Insight, *Top AI acquisitions of 2024: a detailed analysis*, 2024-12. [Link](https://www.analyticsinsight.net/amp/story/artificial-intelligence/top-ai-acquisitions-of-2024-a-detailed-analysis)
- [**S11511**](../../sources/bibliography.md#s11511) TechCrunch, *Inference startup Inferact lands $150M to commercialize vLLM*, 2026-01-22. [Link](https://techcrunch.com/2026/01/22/inference-startup-inferact-lands-150m-to-commercialize-vllm/)
- [**S11513**](../../sources/bibliography.md#s11513) Doolpa, *RadixArk raises $100M seed to grow the SGLang inference engine*, 2026-05-05. [Link](https://doolpa.com/news/radixark-100m-seed-accel-spark-nvidia-amd-sglang-may-5-2026)
- [**S11514**](../../sources/bibliography.md#s11514) Bloomberg Government (Bloomberg), *Fireworks AI in talks for funding at $15 billion valuation*, 2026-05. [Link](https://news.bgov.com/private-equity/fireworks-ai-in-talks-for-funding-at-15-billion-valuation)
- [**S11515**](../../sources/bibliography.md#s11515) Tech Funding News, *Nvidia-backed Fireworks AI eyes $30B to $40B valuation roughly double its July price*, 2026. [Link](https://techfundingnews.com/nvidia-backed-fireworks-ai-eyes-30b-to-40b-valuation-roughly-double-its-july-price/)
- [**S11516**](../../sources/bibliography.md#s11516) DatacenterDynamics, *Together AI raises $800m in Series C funding round*, 2026-07. [Link](https://www.datacenterdynamics.com/en/news/together-ai-raises-800m-in-series-c-funding-round/)
- [**S11518**](../../sources/bibliography.md#s11518) Pulse (venture deals aggregator), *Baseten Labs raises $300M in growth-stage round, valuation hits $5B*, 2026-01-23. [Link](https://www.pulse.bot/ai/deals/baseten-labs-raises-300m-in-growth-stage-round-valuation-hits-5b-7b6470b8-a313-4df3-a2a6-7cb9d288dd92/)
- [**S11519**](../../sources/bibliography.md#s11519) Creati.ai, *Modal Labs negotiates funding at $2.5B valuation as AI inference market heats up*, 2026-02-12. [Link](https://creati.ai/ai-news/2026-02-12/modal-labs-2-5b-valuation-funding-ai-inference)
- [**S11520**](../../sources/bibliography.md#s11520) eWeek, *Positron secures $230M AI funding for $1B valuation*, 2026-02-04. [Link](https://www.eweek.com/news/positron-230m-ai-funding/)
- [**S11521**](../../sources/bibliography.md#s11521) Latham & Watkins, *Latham & Watkins advises Positron AI on Series C*, 2026-09. [Link](https://www.lw.com/en/news/2026/09/latham-watkins-advises-positron-ai-on-series-c)
- [**S11522**](../../sources/bibliography.md#s11522) CB Insights, *FuriosaAI financials (funding rounds)*, 2026. [Link](https://www.cbinsights.com/company/furiosaai/financials)
- [**S11523**](../../sources/bibliography.md#s11523) DatacenterDynamics, *OpenAI signs $10 billion deal with Cerebras with 750MW of big chip compute*, 2026-01-14. [Link](https://www.datacenterdynamics.com/en/news/openai-signs-10-billion-deal-with-cerebras-with-750mw-of-big-chip-compute/)
- [**S11525**](../../sources/bibliography.md#s11525) Epoch AI, *LLM inference prices have fallen rapidly but unequally across tasks*, 2025-03. [Link](https://epoch.ai/data-insights/llm-inference-price-trends)
- [**S11526**](../../sources/bibliography.md#s11526) Stanford HAI, *The 2025 AI Index Report*, 2025-04. [Link](https://hai.stanford.edu/ai-index/2025-ai-index-report)
- [**S11527**](../../sources/bibliography.md#s11527) arXiv 2511.23455 (MIT FutureTech), *The Price of Progress: Algorithmic Efficiency and the Falling Cost of AI Inference*, 2025-11. [Link](https://arxiv.org/abs/2511.23455)
- [**S11535**](../../sources/bibliography.md#s11535) Doolpa, *OpenAI launches GPT-5.5 with state-of-the-art agentic coding and doubles API prices (April 2026)*, 2026-04. [Link](https://doolpa.com/news/openai-gpt-5-5-launch-agentic-coding-pricing-april-2026)
- [**S11537**](../../sources/bibliography.md#s11537) The Decoder, *OpenAI reportedly dramatically improved its compute profit margins*, 2025-12. [Link](https://the-decoder.com/openai-reportedly-dramatically-improved-its-compute-profit-margins/)
- [**S11538**](../../sources/bibliography.md#s11538) Bloomberg, *OpenAI sees better margins on business sales; report says*, 2025-12-21. [Link](https://www.bloomberg.com/news/articles/2025-12-21/openai-sees-better-margins-on-business-sales-report-says)
- [**S11540**](../../sources/bibliography.md#s11540) Pulse 2.0, *Inferact launches with $150 million funding at $800M valuation to commercialize vLLM*, 2026-01-22. [Link](https://pulse2.com/inferact-launches-with-150-million-funding-at-800m-valuation-to-commercialize-vllm-as-inference-demand-surges/)
- [**S32018**](../../sources/bibliography.md#s32018) Google (The Keyword) (Sundar Pichai), *Google I/O 2025 keynote remarks (Sundar Pichai)*, 2025-05-20. [Link](https://blog.google/technology/ai/io-2025-keynote/)
- [**S32020**](../../sources/bibliography.md#s32020) Alphabet / Google (The Keyword) (Sundar Pichai), *Alphabet CEO remarks on token volume (October 2025)*, 2025-10. [Link](https://blog.google/inside-google/message-ceo/alphabet-earnings-q3-2025/)
- [**S90019**](../../sources/bibliography.md#s90019) TechSpot, *Nvidia's $20 billion Groq deal looks a lot like an acquisition*, 2025-12. [Link](https://www.techspot.com/news/110723-nvidia-20-billion-groq-deal-looks-lot-like.html)
- [**S90030**](../../sources/bibliography.md#s90030) Morningstar, *Qualcomm: Humain deal provides some AI upside*, 2025-10. [Link](https://www.morningstar.com/stocks/qualcomm-humain-deal-provides-some-ai-upside)
- [**S90057**](../../sources/bibliography.md#s90057) StorageReview, *Qualcomm unveils Dragonfly data center roadmap: C1000 CPU, AI300 accelerator and Modular acquisition*, 2026-06-24. [Link](https://www.storagereview.com/es/news/qualcomm-unveils-dragonfly-data-center-roadmap-c1000-cpu-ai300-accelerator-and-modular-acquisition)
- [**S90066**](../../sources/bibliography.md#s90066) HPCwire (NVIDIA press release), *NVIDIA enters production with Dynamo, the broadly adopted inference operating system for AI factories*, 2026-03-17. [Link](https://www.hpcwire.com/aiwire/tag/dynamo-1-0/)
