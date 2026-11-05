# DPU, SuperNIC, storage, security: Value chain and corp dev angles

<sub>Layer 07 · DPU, SuperNIC, storage, security · ~9 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **Four value pools, four owners:** the AI [back-end network](../../glossary.md#back-end-network) NIC (one per GPU), the front-end [DPU](../../glossary.md#dpu), AI storage and context memory, and security / [confidential computing](../../glossary.md#confidential-computing). NVIDIA leads only the first outright [[S264]](../../sources/bibliography.md#s264)[[S7503]](../../sources/bibliography.md#s7503)[[S7511]](../../sources/bibliography.md#s7511).
- **The NIC is a small slice of the rack:** Est. 🔴 $0.1–0.6M of [SuperNICs](../../glossary.md#supernic) and DPUs per NVL72 rack, ~3–11% of its price, yet it decides whose network, software and storage path the rack uses [[S326]](../../sources/bibliography.md#s326)[[S332]](../../sources/bibliography.md#s332)[[S330]](../../sources/bibliography.md#s330).
- **The front-end DPU dollar is mostly captive:** AWS (Nitro), Microsoft (Azure Boost DPU) and Google (Titanium) build their own; BlueField sells to neoclouds, enterprises and storage vendors [[S7503]](../../sources/bibliography.md#s7503)[[S7504]](../../sources/bibliography.md#s7504)[[S7520]](../../sources/bibliography.md#s7520)[[S7530]](../../sources/bibliography.md#s7530).
- **Private value has pooled in storage software:** VAST Data was valued at $30B in April 2026 (~$9.1B in 2023), DDN at $5B, WEKA at $1.6B [[S7512]](../../sources/bibliography.md#s7512)[[S7513]](../../sources/bibliography.md#s7513)[[S7514]](../../sources/bibliography.md#s7514)[[S7515]](../../sources/bibliography.md#s7515).
- **Almost every DPU team has been bought** (Annapurna, EZchip, Pensando, Fungible, Enfabrica); Xsight Labs ($2.8B mark) is a rare independent [[S4540]](../../sources/bibliography.md#s4540)[[S7507]](../../sources/bibliography.md#s7507)[[S7527]](../../sources/bibliography.md#s7527)[[S7504]](../../sources/bibliography.md#s7504)[[S475]](../../sources/bibliography.md#s475)[[S7517]](../../sources/bibliography.md#s7517).
- **[Q8 · Value pools & M&A angles]** The scarce assets are RDMA-transport and SerDes teams, not NIC silicon; at today's marks storage is a partnership market.

![Stacked bar chart of estimated SuperNIC and DPU content per NVL72 rack: GB200 about $108K-$324K (3.6-10.8% of a ~$3.0M rack), GB300 $144K-$396K (3.6-9.9% of ~$3.99M) and Vera Rubin $252K-$612K (3.2-7.8% of ~$7.8M). Unit prices are repo assumptions anchored on BlueField-3 retail listings of $1.9K-$6.0K; NIC count is one per GPU.](../../assets/charts/07-nic-dpu-content-per-rack.svg)

## Who captures the dollars

Picture the data path as a toll road: the SuperNIC is the **toll booth** every packet leaving a GPU passes, the DPU the **border checkpoint** to storage and tenants, storage the **warehouse** at the end. The booth owner sets transport rules; the warehouse owner earns software margin.

| Value pool | What is bought | Who captures it today | NVIDIA position | How contestable |
|---|---|---|---|---|
| AI back-end NIC (1 per GPU) | ConnectX-8/9, Vulcano, Thor Ultra, EFA | NVIDIA in HGX/NVL72; AWS in-house; AMD in Helios [[S264]](../../sources/bibliography.md#s264)[[S292]](../../sources/bibliography.md#s292)[[S7500]](../../sources/bibliography.md#s7500) | 🟩 default in its racks | 🟡 [Ultra Ethernet](../../glossary.md#ultra-ethernet) lowers switching cost [[S7528]](../../sources/bibliography.md#s7528) |
| Front-end DPU / cloud offload | Nitro, Azure Boost DPU, Titanium, BlueField-3 | Hyperscalers' [captive silicon](../../glossary.md#captive-silicon) [[S7503]](../../sources/bibliography.md#s7503)[[S7504]](../../sources/bibliography.md#s7504)[[S7520]](../../sources/bibliography.md#s7520) | 🟥 locked out of the top three clouds | Low for NVIDIA |
| Storage and [context memory](../../glossary.md#context-memory-storage) | VAST, DDN, WEKA, NetApp and others; BlueField-4 STX nodes | Storage vendors (software margin) [[S7511]](../../sources/bibliography.md#s7511) | 🟦 enabler: STX, [GPUDirect Storage](../../glossary.md#gpudirect-storage) | High; vendors can use merchant NICs |
| Security and confidential computing | GPU trusted execution, DPU isolation, HSMs | Platform owners (NVIDIA, Azure, AWS) [[S7505]](../../sources/bibliography.md#s7505)[[S4527]](../../sources/bibliography.md#s4527) | 🟨 GPU TEE plus BlueField isolation | Unclear; few independents |

> [!TIP]
> **Worked example — sanity-checking the NIC estimate against a rack BOM.** Morgan Stanley prices a Vera Rubin NVL72 at ~$7.8M; subtracting its GPU, CPU and memory figures plus cooling and ODM margin leaves ~$1.46M for NVSwitch trays, NICs, DPUs, PCB, power and chassis ([layer 04 value chain](../04-cpu-grace-vera/value-chain-and-corp-dev.md)) [[S330]](../../sources/bibliography.md#s330)[[S331]](../../sources/bibliography.md#s331)[[S332]](../../sources/bibliography.md#s332). This repo's NIC + DPU range of $252–612K is 17–42% of that bucket (Est., repo 🔴), plausible beside 36 NVSwitch chips, power shelves and boards. At the midpoint (~$430K) 1,000 racks carry ~$0.43B of NIC and DPU silicon.

<details>
<summary>🔧 Under the hood: how the per-rack estimate is built</summary>

SuperNIC count is one per GPU (72), per NVIDIA's rack specifications [[S266]](../../sources/bibliography.md#s266)[[S264]](../../sources/bibliography.md#s264)[[S33004]](../../sources/bibliography.md#s33004). DPU count is assumed at 18–36 (one or two per compute tray). Unit prices are repo assumptions: ConnectX-7 $1.0–2.0K, ConnectX-8 $1.5–3.0K, ConnectX-9 $2.5–4.5K, BlueField-3 $2.0–5.0K, BlueField-4 $4.0–8.0K (it adds a 64-core Grace). Public anchors: retail BlueField-3 listings of $1,949–5,959, above contract prices [[S7531]](../../sources/bibliography.md#s7531)[[S7532]](../../sources/bibliography.md#s7532). Rack prices are HSBC (GB200, ~$3M) and Morgan Stanley (GB300 ~$3.99M, Vera Rubin ~$7.8M) estimates [[S326]](../../sources/bibliography.md#s326)[[S332]](../../sources/bibliography.md#s332)[[S330]](../../sources/bibliography.md#s330).

</details>

**Suppliers and partners.** Cisco, DDN, Dell, HPE, IBM, Lenovo, Supermicro, VAST Data and WEKA build BlueField-4 platforms, and OCI and xAI build on DOCA [[S7530]](../../sources/bibliography.md#s7530); STX adds twelve storage co-design partners and eight context-memory adopters [[S7511]](../../sources/bibliography.md#s7511). As with CUDA, NVIDIA writes the reference design.

## Private companies worth knowing

| Company | What it does | Stage / last public funding | Why it matters |
|---|---|---|---|
| VAST Data | AI storage and data platform | ~$1B Series F at $30B (April 2026); IPO considered [[S7512]](../../sources/bibliography.md#s7512)[[S7513]](../../sources/bibliography.md#s7513) | Largest private mark here; NVIDIA invested in 2023 [[S482]](../../sources/bibliography.md#s482) |
| DDN | AI and HPC parallel storage | $300M from Blackstone at $5B (January 2025) [[S7514]](../../sources/bibliography.md#s7514) | GPU-cluster storage incumbent; STX partner [[S7511]](../../sources/bibliography.md#s7511) |
| WEKA | Parallel file system for AI | $140M Series E at $1.6B (May 2024) [[S7515]](../../sources/bibliography.md#s7515) | No later priced round found |
| Hammerspace | Data orchestration across silos | $100M at >$500M (April 2025) [[S7516]](../../sources/bibliography.md#s7516) | Software layer above storage |
| Xsight Labs | 800G E1 DPU, Ethernet switches | >$300M at $2.8B (July 2026) [[S7517]](../../sources/bibliography.md#s7517) | A rare independent DPU team |
| Enfabrica (now NVIDIA) | SuperNIC / memory fabric | Team and licence, >$900M (Sept 2025) [[S475]](../../sources/bibliography.md#s475) | Price of RDMA-fabric talent |
| Fungible (now Microsoft) | DPU | ~$190M (January 2023) [[S7504]](../../sources/bibliography.md#s7504)[[S7506]](../../sources/bibliography.md#s7506) | Became Azure Boost DPU |
| Pensando (now AMD) | DPU and AI NIC | ~$1.9B (May 2022) [[S7527]](../../sources/bibliography.md#s7527) | Became AMD's AI NIC line |

![Log-scale horizontal bar chart: VAST Data valued at $30,000M (2026, up from $9,100M in 2023), DDN $5,000M (2025), Xsight Labs $2,800M (2026), WEKA $1,600M (2024) and Hammerspace more than $500M (2025); for comparison, DPU and NIC start-ups were bought for $1,900M (Pensando by AMD), >$900M (Enfabrica team by NVIDIA) and ~$190M (Fungible by Microsoft).](../../assets/charts/07-ai-storage-and-dpu-valuations.svg)

> [!TIP]
> **Worked example — what VAST's re-rating says about value capture.** VAST went from ~$9.1B (late 2023) to $30B (April 2026), ~3.3× in about 2.5 years, or ~60% a year compounded [[S7513]](../../sources/bibliography.md#s7513). For a buyer, storage is priced as a platform (partner); independent NIC and DPU silicon is scarce and priced as talent (acquire or license).

## M&A history in the layer

| Year | Deal | Value | What it became |
|---|---|---|---|
| 2014 | EZchip buys Tilera | up to $130M [[S7510]](../../sources/bibliography.md#s7510) | Many-core processors behind BlueField |
| 2015 | Amazon buys Annapurna Labs | ~$350–370M reported [[S4540]](../../sources/bibliography.md#s4540) | Nitro, then Graviton and Trainium |
| 2016 | Mellanox buys EZchip | $811M [[S7507]](../../sources/bibliography.md#s7507) | BlueField DPU line |
| 2019–20 | NVIDIA buys Mellanox | $6.9B [[S464]](../../sources/bibliography.md#s464) | ConnectX, BlueField, InfiniBand, Spectrum |
| 2022 | NVIDIA buys Excelero | undisclosed [[S478]](../../sources/bibliography.md#s478) | NVMesh storage software |
| 2022 | AMD buys Pensando | ~$1.9B [[S7527]](../../sources/bibliography.md#s7527) | Salina DPU, Pollara and Vulcano NICs |
| 2023 | Microsoft buys Fungible | ~$190M reported [[S7504]](../../sources/bibliography.md#s7504) | Azure Boost DPU |
| 2025 | NVIDIA hires Enfabrica team, licenses IP | >$900M reported [[S475]](../../sources/bibliography.md#s475) | SuperNIC and memory-fabric know-how |
| 2025 | Qualcomm buys Alphawave Semi | $2.4B [[S4513]](../../sources/bibliography.md#s4513)[[S4514]](../../sources/bibliography.md#s4514) | SerDes and chiplet connectivity IP |

Deal values are charted in [history and how NVIDIA built it](history-and-how-built.md).

## [Q8 · Value pools & M&A angles]

**Where the value is.** The back-end NIC is a modest BOM line but the control point for transport and attach; the front-end DPU pool is captive at the three biggest clouds; storage and context memory is where private value has accrued and where STX tries to set the reference design [[S7511]](../../sources/bibliography.md#s7511); security is mostly bundled into platforms.

**Angles (public information only, framed as options).** With independent RDMA and NIC teams rare, the paths are a high-priced acquisition, an IP licence plus team hire on the Enfabrica model, or a merchant partnership with Broadcom, AMD or Marvell [[S7517]](../../sources/bibliography.md#s7517)[[S475]](../../sources/bibliography.md#s475)[[S7529]](../../sources/bibliography.md#s7529). Qualcomm, for example, owns SerDes IP through Alphawave and has announced AI200/AI250 racks and a Dragonfly AI300 with UALink and ESUN scale-up; no Qualcomm scale-out NIC has been announced [[S4513]](../../sources/bibliography.md#s4513)[[S90028]](../../sources/bibliography.md#s90028)[[S90060]](../../sources/bibliography.md#s90060).

> [!TIP]
> **Worked example — build, license or partner for a scale-out NIC.** Pensando cost AMD ~$1.9B and ~4 years to reach an 800G AI NIC [[S7527]](../../sources/bibliography.md#s7527)[[S7500]](../../sources/bibliography.md#s7500); Enfabrica cost NVIDIA >$900M for a team and licence [[S475]](../../sources/bibliography.md#s475). Buying two merchant 800G NICs per accelerator instead costs ~$0.2–0.4M per 72-accelerator rack (Est., repo 🔴; [roadmap](roadmap.md)), or $0.2–0.4B a year at 1,000 racks: the same order as building a team. The answer turns on volume and on whether NIC control wins racks.

## 🎯 Corp Dev Lens

1. Is the back-end NIC a profit pool or a control point? If Ultra Ethernet makes it interchangeable, does value shift to whoever writes the rack reference design?
2. With Annapurna, EZchip, Pensando, Fungible and Enfabrica absorbed, which independent RDMA, SerDes or DPU teams remain, and what does Xsight Labs' $2.8B mark imply for their price?
3. Storage software (VAST at $30B) sits beside the GPU without making chips: is partnering on context-memory designs a cheaper route into AI data paths than owning silicon?
4. For an accelerator entrant with SerDes IP (Qualcomm via Alphawave, for example), what are the cost and time of a UEC NIC versus a Broadcom or AMD partnership?
5. Confidential computing on GPUs and DPUs is bundled by platform owners today; is there room for an independent security layer, or does it stay a feature?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S264**](../../sources/bibliography.md#s264) NVIDIA Newsroom, *NVIDIA Announces New Switches Optimized for Trillion-Parameter GPU Computing and AI Infrastructure (Quantum-X800, Spectrum-X800, ConnectX-8)*, 2024-03-18. [Link](https://nvidianews.nvidia.com/news/networking-switches-gpu-computing-ai)
- [**S266**](../../sources/bibliography.md#s266) NVIDIA Newsroom, *NVIDIA Quantum-2 Takes Supercomputing to New Heights, Into the Cloud*, 2021-11-09. [Link](https://nvidianews.nvidia.com/news/nvidia-quantum-2-takes-supercomputing-to-new-heights-into-the-cloud)
- [**S292**](../../sources/bibliography.md#s292) Amazon Web Services, *Elastic Fabric Adapter (EFA) and AWS Nitro System documentation*, 2025. [Link](https://aws.amazon.com/hpc/efa/)
- [**S326**](../../sources/bibliography.md#s326) TweakTown, *NVIDIA's new GB200 Superchip costs up to $70,000: full B200 NVL72 AI server costs $3 million*, 2024-05. [Link](https://www.tweaktown.com/news/98292/nvidias-new-gb200-superchip-costs-up-to-70-000-full-b200-nvl72-ai-server-3-million/index.html)
- [**S330**](../../sources/bibliography.md#s330) PC Gamer, *A single Nvidia Vera Rubin rack is estimated to cost $7,803,148 with over $2 million of that figure spent on memory alone*, 2026-05. [Link](https://pcgamer.com/hardware/a-single-nvidia-vera-rubin-rack-is-estimated-to-cost-usd7-803-148-with-over-usd2-million-of-that-figure-spent-on-memory-alone)
- [**S331**](../../sources/bibliography.md#s331) Wccftech, *NVIDIA's Vera Rubin rack hit with 435% memory price surge, pushing HBM4 & LPDDR5X bill to $2M of $7.8M total*, 2026-05. [Link](https://wccftech.com/nvidia-vera-rubin-rack-hit-with-memory-price-surge-pushing-hbm4-lpddr5x-bill-to-2m-of-7-8m-total/)
- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S464**](../../sources/bibliography.md#s464) NVIDIA Newsroom, *NVIDIA to Acquire Mellanox for $6.9 Billion*, 2019-03-11. [Link](https://nvidianews.nvidia.com/news/nvidia-to-acquire-mellanox-for-6-9-billion)
- [**S475**](../../sources/bibliography.md#s475) CNBC, *Nvidia spends over $900 million on Enfabrica CEO, AI startup technology*, 2025-09-18. [Link](https://www.cnbc.com/technology/)
- [**S478**](../../sources/bibliography.md#s478) NVIDIA, *NVIDIA Blog and Newsroom acquisition announcements (Cumulus, SwiftStack, DeepMap, Bright Computing, Excelero, Shoreline, Brev.dev, OctoAI, VinBrain, Gretel, Lepton AI, CentML, SchedMD)*, 2025-12. [Link](https://blogs.nvidia.com/)
- [**S482**](../../sources/bibliography.md#s482) Various (company announcements; Reuters, Bloomberg), *Reporting on NVIDIA participation in robotics, autonomy, photonics, storage and energy rounds (Figure AI, Wayve, Scale AI, Ayar Labs, Enfabrica, VAST Data, Sakana AI, TerraPower, Commonwealth Fusion Systems, Applied Digital, Recursion)*, 2025-09. [Link](https://www.reuters.com/technology/)
- [**S4513**](../../sources/bibliography.md#s4513) I-Connect007, *Qualcomm completes acquisition of Alphawave Semi*, 2025-12-18. [Link](https://iconnect007.com/article/148161/qualcomm-completes-acquisition-of-alphawave-semi/148158/ein)
- [**S4514**](../../sources/bibliography.md#s4514) CRN Asia, *Qualcomm: US$2.4 billion Alphawave Semi buy to boost data center push*, 2025-06. [Link](https://www.crnasia.com/news-network/2025/qualcomm-us-2)
- [**S4527**](../../sources/bibliography.md#s4527) Converge Digest, *AWS debuts Graviton5: 192 cores, bigger caches and new Nitro security*, 2025-12. [Link](https://convergedigest.com/aws-debuts-graviton5-192-cores-bigger-caches-and-new-nitro-security/?amp=1)
- [**S4540**](../../sources/bibliography.md#s4540) Global Venturing, *Arm exits Annapurna Labs in $370m acquisition*, 2015-01-23. [Link](https://globalventuring.com/blog/2015/01/23/arm-exits-annapurna-labs-in-370m-acquisition/)
- [**S7500**](../../sources/bibliography.md#s7500) AMD, *AMD Pensando Vulcano 800 AI NIC: Built to Scale-Out and Across*, 2026. [Link](https://www.amd.com/en/blogs/2026/amd-pensando-vulcano-800-ai-nic-scale-out-and-across.html)
- [**S7503**](../../sources/bibliography.md#s7503) Amazon Web Services, *Instances built on the AWS Nitro System (Amazon EC2 documentation)*, 2026. [Link](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-nitro-instances.html)
- [**S7504**](../../sources/bibliography.md#s7504) Blocks & Files, *Microsoft boosts Azure infrastructure with Fungible-derived DPU*, 2024-11-20. [Link](https://blocksandfiles.com/2024/11/20/microsoft-boosts-azure-infrastructure-with-fungible-derived-dpu/)
- [**S7505**](../../sources/bibliography.md#s7505) InfoQ, *Microsoft's Azure Boost DPU and in-house security chip*, 2024-12. [Link](https://www.infoq.com/news/2024/12/azure-boost-dpu-inhouse-chips)
- [**S7506**](../../sources/bibliography.md#s7506) TechRadar, *Microsoft snaps up Fungible for Azure cloud and data center boost*, 2023-01. [Link](https://www.techradar.com/news/microsoft-snaps-up-fungible-for-azure-cloud-and-data-center-boost)
- [**S7507**](../../sources/bibliography.md#s7507) Mellanox Technologies via SEC EDGAR, *Mellanox Technologies Form 8-K exhibit 99.1: Mellanox completes acquisition of EZchip*, 2016-02-23. [Link](https://www.sec.gov/Archives/edgar/data/0001356104/000110465916099040/a16-5002_1ex99d1.htm)
- [**S7510**](../../sources/bibliography.md#s7510) Converge Digest, *EZchip to acquire Tilera for its multicore processors*, 2014-07. [Link](https://convergedigest.com/ezchip-to-acquire-tilera-for-its-multi/)
- [**S7511**](../../sources/bibliography.md#s7511) NVIDIA Newsroom, *NVIDIA Launches BlueField-4 STX Storage Architecture With Broad Industry Adoption*, 2026-03-16. [Link](https://nvidianews.nvidia.com/news/nvidia-launches-bluefield-4-stx-storage-architecture-with-broad-industry-adoption)
- [**S7512**](../../sources/bibliography.md#s7512) Bloomberg Law, *Nvidia-backed Vast Data triples value to $30 billion, mulls IPO*, 2026-04. [Link](https://news.bloomberglaw.com/private-equity/nvidia-backed-vast-data-triples-value-to-30-billion-mulls-ipo)
- [**S7513**](../../sources/bibliography.md#s7513) Built In, *VAST Data raises $1B Series F at $30B valuation*, 2026-04-23. [Link](https://builtin.com/articles/vast-data-raises-1b-series-f-30b-valuation-20260423)
- [**S7514**](../../sources/bibliography.md#s7514) Blackstone, *Blackstone invests $300 million at a $5 billion valuation in DDN*, 2025-01-08. [Link](https://www.blackstone.com/news/press/blackstone-invests-300-million-at-a-5-billion-valuation-in-ddn-ai-and-data-intelligence-solutions-leader-to-fuel-further-rapid-growth/)
- [**S7515**](../../sources/bibliography.md#s7515) Data Phoenix, *WEKA reached unicorn status after raising its Series E at a $1.6B valuation*, 2024-05. [Link](https://dataphoenix.info/weka-reached-unicorn-status-after-raising-its-series-e-at-a-1-6b-valuation)
- [**S7516**](../../sources/bibliography.md#s7516) TechCrunch, *Hammerspace, an unstructured data wrangler used by Nvidia, Meta and Tesla, raises $100M at $500M+ valuation*, 2025-04-16. [Link](https://techcrunch.com/2025/04/16/hammerspace-an-unstructured-data-wrangler-100m/)
- [**S7517**](../../sources/bibliography.md#s7517) StorageNewsletter, *Xsight Labs raises more than $300 million at $2.8 billion valuation to power next-generation AI and cloud networks*, 2026-08-06. [Link](https://www.storagenewsletter.com/2026/08/06/fms-2026-xsight-labs-raises-more-than-300-million-at-2-8-billion-valuation-to-power-next-generation-ai-and-cloud-networks/)
- [**S7520**](../../sources/bibliography.md#s7520) Google Cloud, *Titanium (Google Cloud product page)*, 2024. [Link](https://cloud.google.com/titanium)
- [**S7527**](../../sources/bibliography.md#s7527) AMD Investor Relations, *AMD expands data center solutions capabilities with acquisition of Pensando*, 2022-05-26. [Link](https://ir.amd.com/news-events/press-releases/detail/1071/amd-expands-data-center-solutions-capabilities-with)
- [**S7528**](../../sources/bibliography.md#s7528) Converge Digest, *Ultra Ethernet Consortium releases Specification 1.0*, 2025-06. [Link](https://convergedigest.com/ultra-ethernet-consortium-releases-specification-1-0/)
- [**S7529**](../../sources/bibliography.md#s7529) StreetInsider (Broadcom press release), *Broadcom introduces industry's first 800G AI Ethernet NIC (Thor Ultra)*, 2025-10-14. [Link](https://www.streetinsider.com/Press+Releases/Broadcom+Introduces+Industry%E2%80%99s+First+800G+AI+Ethernet+NIC/25451603.html)
- [**S7530**](../../sources/bibliography.md#s7530) StorageNewsletter (NVIDIA release), *NVIDIA launches BlueField-4, the processor powering the operating system of AI factories*, 2025-11-04. [Link](https://www.storagenewsletter.com/2025/11/04/nvidia-launches-bluefield-4-the-processor-powering-the-operating-system-of-ai-factories/)
- [**S7531**](../../sources/bibliography.md#s7531) NADDOD, *NVIDIA BlueField-3 DPUs and SuperNICs (distributor listings)*, 2026. [Link](https://www.naddod.com/ko/collections/nvidia-networking/nvidia-bluefield-3-dpus-and-supernics)
- [**S7532**](../../sources/bibliography.md#s7532) ICD, *NVIDIA BlueField-3 B3220 DPU 200GbE listing (900-9D3B6-00SV-AA0)*, 2026. [Link](https://icd3s.com/product/900-9d3b6-00sv-aa0-nvidia-bluefield-3-b3220-dpu-200gbendr200-vpi-dual-port-qsfp112-pcie-50-x16-crypto-disabled-16-core-arm-32gb-ddr5/)
- [**S33004**](../../sources/bibliography.md#s33004) NVIDIA Newsroom, *NVIDIA Kicks Off the Next Generation of AI With Rubin — Six New Chips; One Incredible AI Supercomputer*, 2026-01-05. [Link](https://nvidianews.nvidia.com/news/rubin-platform-ai-supercomputer)
- [**S90028**](../../sources/bibliography.md#s90028) TechRepublic, *Qualcomm unveils AI chips to rival Nvidia, AMD*, 2025-10-27. [Link](https://techrepublic.com/article/news-qualcomm-unveils-ai-chips-to-rival-nvidia-amd)
- [**S90060**](../../sources/bibliography.md#s90060) Qualcomm, *Qualcomm Dragonfly AI300 (product page)*, 2026-06. [Link](https://www.qualcomm.com/data-center/products/qualcomm-dragonfly-ai300)
