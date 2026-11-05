# Cluster topologies for 100,000 GPUs

<sub>Layer 06 · Scale-out and scale-across networking · ~8 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **AI clusters are built as [rail-optimized](../../glossary.md#rail-optimized) [fat trees](../../glossary.md#fat-tree):** NIC k of every server plugs into the rail-k leaf, and every leaf reaches every spine [[S34022]](../../sources/bibliography.md#s34022)[[S294]](../../sources/bibliography.md#s294).
- **[Switch radix](../../glossary.md#switch-radix) sets the size limit.** Two tiers hold R²/2 GPUs: 10,368 with 144-port Quantum-X800, 131,072 with 512-port 102.4 Tb/s switches; three tiers hold R³/4 (Est.) [[S264]](../../sources/bibliography.md#s264)[[S274]](../../sources/bibliography.md#s274).
- **A 100,000-GPU back-end fabric needs ~3,500–3,900 switches and ~350,000 optical modules in three tiers,** or ~2,350 switches and ~250,000 modules as a four-plane two-tier design (Est.) [[S294]](../../sources/bibliography.md#s294).
- **Networking is ~17–21% of AI cluster hardware capex** in most estimates (13% of a whole site including buildings) [[S6025]](../../sources/bibliography.md#s6025)[[S6026]](../../sources/bibliography.md#s6026)[[S324]](../../sources/bibliography.md#s324); optics alone are ~$6,000 per GPU by NVIDIA's own math [[S6016]](../../sources/bibliography.md#s6016).
- **The biggest disclosed fabrics since 2024 are Ethernet:** xAI's 100,000-GPU Colossus on Spectrum-X [[S6000]](../../sources/bibliography.md#s6000), Meta's RoCE clusters [[S6002]](../../sources/bibliography.md#s6002) and Oracle's multi-plane design targeting up to 800,000 GPUs [[S6008]](../../sources/bibliography.md#s6008).
- **Weakness for NVIDIA:** 512-port merchant silicon (Broadcom's Tomahawk 6 claims two tiers for 100k+ accelerators [[S274]](../../sources/bibliography.md#s274)) makes flat, multi-vendor designs viable without NVIDIA switches.

![Stacked horizontal bar chart (estimates) of switches needed for 100,000 GPUs: 3-tier designs need 3,473 to 3,908 switches and about 350k optical modules with 5 switch hops worst case; a 4-plane 2-tier design on 512-port 102.4T switches needs 2,348 switches, 250k modules (29% fewer) and 3 hops.](../../assets/charts/06-switches-for-100k-gpu-cluster.svg)

## 1. Rail-optimized fat trees

In a fat tree each switch uses half its ports down and half up, so bandwidth never narrows toward the top ([full bisection bandwidth](../../glossary.md#bisection-bandwidth)). Rail optimization adds a twist: NIC 1 of every 8-GPU server connects to the "rail 1" leaf, NIC 2 to rail 2, and so on. Collective libraries move data over NVLink to the GPU on the right rail first, so most cross-server traffic crosses one switch [[S34022]](../../sources/bibliography.md#s34022).

![Diagram of a rail-optimized two-tier fat tree: four servers, each with four GPUs joined by NVLink and one NIC per GPU; NIC 1 of every server connects to the rail-1 leaf switch, NIC 2 to rail 2 and so on; each of the four rail leaves has one uplink to each of four spine switches, so same-rail GPUs are one switch hop apart and any two GPUs at most three.](../../assets/diagrams/06-rail-optimized-fat-tree.svg)

> [!TIP]
> **Worked example — hops on a rail.** GPU 3 in server 1 sends to GPU 3 in server 9 under the same leaf: NIC 3 → rail-3 leaf → NIC 3, **one switch hop**. To GPU 5 in that server: either 3 hops (leaf → spine → leaf) or one NVLink hop to GPU 5 at home, then one switch hop on rail 5.
>
> **Conclusion:** the bigger the NVLink domain (72 GPUs in NVL72), the less traffic touches upper tiers.

## 2. Radix math: two tiers or three

![Grouped log-scale bar chart: a two-tier non-blocking fat tree supports 800 GPUs with 40-port HDR switches, 2,048 with 64-port Quantum-2, 8,192 with 128-port 51.2T, 10,368 with 144-port Quantum-X800 and 131,072 with 512-port 102.4T switches; three tiers reach 65,536, 524,288 and 746,496; a 100,000-GPU cluster therefore needs three tiers unless switches have 512-port radix (or multiple planes).](../../assets/charts/06-fat-tree-max-gpus-by-radix.svg)

| | Two-tier (leaf–spine) | Three-tier (leaf–spine–core) | Multi-plane two-tier |
|---|---|---|---|
| Max GPUs for radix R | R²/2 | R³/4 | R²/2 per plane; NIC split across planes |
| Example | 10,368 on Quantum-X800 | 746,496 on Quantum-X800 | 131,072 on 512 × 200G planes |
| Switches for 100k GPUs (Est.) | Not possible at R = 144 | 3,473–3,908 | 2,348 (4 planes) |
| Optical modules per GPU (Est.) | 2.5 | 3.5 | 2.5 |
| Worst-case switch hops | 3 | 5 | 3 |

Repo calculations in `network_topology_estimates.csv` from [[S264]](../../sources/bibliography.md#s264)[[S265]](../../sources/bibliography.md#s265)[[S274]](../../sources/bibliography.md#s274)[[S294]](../../sources/bibliography.md#s294).

> [!TIP]
> **Worked example — switch count for 100,000 GPUs.** On Quantum-X800 (R = 144 at 800G) each leaf has 72 ports down and 72 up:
> - Leaves 100,000 ÷ 72 = **1,389**; spines **1,389**; core 100,000 ÷ 144 = **695**: **3,473 switches**, 5 hops worst case.
> - Alternative: split each 800G NIC into 4 × 200G and build four independent planes of 512-port 102.4 Tb/s switches: 391 leaves + 196 spines per plane, **2,348 switches** in all, 3 hops, and a failed plane only removes a quarter of the bandwidth ([multi-plane network](../../glossary.md#multi-plane-network)).
>
> **Conclusion:** high radix drops a tier, saving ~1,100–1,600 switches and ~100,000 modules (Est.); Oracle's Acceleron design takes this multi-plane route [[S6008]](../../sources/bibliography.md#s6008).

<details>
<summary>🔧 Under the hood: why R²/2 and R³/4</summary>

In two tiers, each spine connects once to every leaf, so there are at most R leaves, each giving R/2 ports to GPUs: R × R/2 = R²/2. A third tier uses R two-tier pods of R²/4 GPUs: R³/4. [Oversubscription](../../glossary.md#oversubscription) (more ports down than up) stretches the same switches further at the cost of bisection bandwidth; Meta's RoCE design reportedly oversubscribes its aggregation tier about 7:1 (Lockwood's reading) [[S6031]](../../sources/bibliography.md#s6031).

</details>

## 3. How many optics, and what the network costs

![Stacked bar chart (estimates): with all-optical links a GPU needs 2.5 pluggable modules in a two-tier fat tree and 3.5 in three tiers (one NIC-side module, half a twin-port leaf module, one module per upper tier), the same count at 400G and 800G; counted as optical port-ends it is 4 and 6, matching NVIDIA's '6 transceivers per GPU'; co-packaged-optics switches leave only the NIC-side module, 1 per GPU.](../../assets/charts/06-optics-per-gpu.svg)

Counted as port-ends, three tiers need six per GPU, matching Huang's "six transceivers" [[S6016]](../../sources/bibliography.md#s6016); co-packaged optics remove the switch-side modules ([Co-packaged optics](co-packaged-optics.md)).

![Horizontal bar chart of estimates of the network's share of AI spending: switches alone about 3% and all networking about 13% of a whole 1 GW data center's spend (Reuters); optics alone about 11% of a GB300 NVL72's per-GPU price using Jensen Huang's six $1,000 transceivers per GPU; about 17% (576 GPUs) and 19% (24,576 GPUs) of cluster capex in one bottom-up blog estimate; NVIDIA networking at about 20% of its Data Center revenue in Q2 FY2027; and about 20.5% networking plus storage in SemiAnalysis's all-in GB200 NVL72 cost.](../../assets/charts/06-network-share-of-cluster-capex.svg)

> [!TIP]
> **Worked example — the network bill for 100,000 GB300-class GPUs.** Morgan Stanley puts a GB300 NVL72 at ~$3.99M, ~$55,400 per GPU [[S332]](../../sources/bibliography.md#s332): ~**$5.5B** of racks. If networking is 17–21% of the total [[S6026]](../../sources/bibliography.md#s6026)[[S324]](../../sources/bibliography.md#s324), the cluster costs ~$6.6–7.0B and the network **~$1.1–1.5B**, or ~$11,000–15,000 per GPU, of which Huang's ~$6,000 of optics [[S6016]](../../sources/bibliography.md#s6016) is roughly half (Est.).
>
> **Conclusion:** the network is a ~$1B+ line item per 100k GPUs. NVIDIA's networking revenue near ~20% of its Data Center revenue [[S408]](../../sources/bibliography.md#s408)[[S3]](../../sources/bibliography.md#s3) suggests it captures a large share, though that figure includes NVLink scale-up switches.

## 4. What real clusters use

![Horizontal log-scale bar chart of disclosed AI clusters: Microsoft Azure Eagle 14,400 H100 on InfiniBand NDR (2023 TOP500 run); Meta's two 24,576-GPU H100 clusters, one InfiniBand and one RoCE Ethernet (2024); xAI Colossus 100,000 H100 on NVIDIA Spectrum-X Ethernet (2024) with a reported expansion to 200,000; Oracle's Zettascale10 RoCE multiplanar design targeting up to 800,000 GPUs (announced for 2026). The largest fabrics since 2024 are Ethernet.](../../assets/charts/06-ai-cluster-fabrics.svg)

| Cluster | GPUs | Back-end fabric | What it shows |
|---|---|---|---|
| Microsoft Azure Eagle (2023) | 14,400 H100 (TOP500 run) | Quantum-2 NDR InfiniBand | 561 PFLOPS, #3 on TOP500 [[S6006]](../../sources/bibliography.md#s6006) |
| Meta GenAI clusters (2024) | 2 × 24,576 H100 | RoCE (Arista 7800) and Quantum-2 InfiniBand; 400G | Llama 3 trained on RoCE [[S6002]](../../sources/bibliography.md#s6002)[[S34006]](../../sources/bibliography.md#s34006) |
| xAI Colossus (2024) | 100,000 H100; 200,000 reported 🟡 | Spectrum-X, three tiers, 400G | 95% throughput claim [[S6000]](../../sources/bibliography.md#s6000)[[S6001]](../../sources/bibliography.md#s6001) |
| Microsoft Fairwater (2025) | GB200/GB300 NVL72; undisclosed | 800G InfiniBand and Ethernet; two-tier Ethernet (SONiC) in Atlanta | AI WAN joins sites [[S6004]](../../sources/bibliography.md#s6004)[[S6005]](../../sources/bibliography.md#s6005) |
| Oracle Zettascale10 (H2 2026 target) | Up to 800,000 🟢 announced | Acceleron RoCE, multi-plane | First built at Stargate Abilene [[S6008]](../../sources/bibliography.md#s6008) |

## 🎯 Corp Dev Lens

1. **The ~$1B-per-100k-GPU network pool** (Est.) is split among switch silicon, NICs, optics, cables and integrators; tiers, planes and CPO move dollars between them.
2. **Radix is strategic.** 512-port merchant switches let hyperscalers build flat multi-vendor fabrics [[S274]](../../sources/bibliography.md#s274); NVIDIA's counter is the switch-plus-SuperNIC bundle and CPO timing.
3. **Multi-plane designs favor NIC owners.** When the NIC splits traffic across planes and steers around failures [[S6008]](../../sources/bibliography.md#s6008), intelligence moves into the NIC, raising the value of NIC/DPU franchises ([Layer 07](../07-dpu-supernic-storage-security/index.md)).
4. **Qualcomm question (public information only):** for a 2027–2028 inference rack [[S90056]](../../sources/bibliography.md#s90056), is a merchant-Ethernet back end with a third-party NIC enough, or does winning large deployments require owning a NIC or networking partner?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S3**](../../sources/bibliography.md#s3) StorageNewsletter, *NVIDIA Q2 Fiscal 2027 results coverage: revenue $96.2B*, 2026-08-27. [Link](https://www.storagenewsletter.com/2026/08/27/nvidia-fiscal-2q27-financial-results/)
- [**S264**](../../sources/bibliography.md#s264) NVIDIA Newsroom, *NVIDIA Announces New Switches Optimized for Trillion-Parameter GPU Computing and AI Infrastructure (Quantum-X800, Spectrum-X800, ConnectX-8)*, 2024-03-18. [Link](https://nvidianews.nvidia.com/news/networking-switches-gpu-computing-ai)
- [**S265**](../../sources/bibliography.md#s265) NVIDIA Newsroom, *NVIDIA Announces Spectrum-X Photonics, Co-Packaged Optics Networking Switches to Scale AI Factories to Millions of GPUs*, 2025-03-18. [Link](https://nvidianews.nvidia.com/news/nvidia-spectrum-x-co-packaged-optics-networking-switches-ai-factories)
- [**S274**](../../sources/bibliography.md#s274) Broadcom, *Broadcom ships Tomahawk 6: world's first 102.4 Tbps switch*, 2025-06-03. [Link](https://investors.broadcom.com/news-releases/news-release-details/broadcom-ships-tomahawk-6-worlds-first-1024-tbps-switch)
- [**S294**](../../sources/bibliography.md#s294) SemiAnalysis (Dylan Patel et al.), *100,000 H100 Clusters: Power, Network Topology, Ethernet vs InfiniBand, Reliability, Failures, Checkpointing*, 2024-06-17. [Link](https://semianalysis.com/2024/06/17/100000-h100-clusters-power-network/)
- [**S324**](../../sources/bibliography.md#s324) fal.ai, *NVIDIA GB200 price in 2026: what a GPU, a tray and an NVL72 rack cost*, 2026. [Link](https://fal.ai/learn/serverless/nvidia-gb200-price)
- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S408**](../../sources/bibliography.md#s408) NVIDIA Corporation, *NVIDIA Corp. (NVDA) Q2 Fiscal 2027 earnings call transcript (26 August 2026)*, 2026-08-26. [Link](https://s201.q4cdn.com/141608511/files/content_files/TRANSCRIPT_-NVIDIA-Corp-NVDA-US-Q2-2027-Earnings-Call-26-August-2026-5_00-PM-ET.pdf)
- [**S6000**](../../sources/bibliography.md#s6000) TechPowerUp (NVIDIA press release), *NVIDIA Ethernet Networking Accelerates World's Largest AI Supercomputer, Built by xAI*, 2024-10-29. [Link](https://techpowerup.com/328227/nvidia-ethernet-networking-accelerates-worlds-largest-ai-supercomputer-built-by-xai)
- [**S6001**](../../sources/bibliography.md#s6001) DatacenterDynamics, *xAI to double Colossus compute capacity, reveals cluster uses Nvidia Spectrum-X Ethernet*, 2024-10. [Link](https://datacenterdynamics.com/en/news/xai-to-double-colossus-compute-capacity-reveals-cluster-uses-nvidia-spectrum-x-ethernet)
- [**S6002**](../../sources/bibliography.md#s6002) Engineering at Meta, *Building Meta's GenAI Infrastructure*, 2024-03-12. [Link](https://engineering.fb.com/2024/03/12/data-center-engineering/building-metas-genai-infrastructure/)
- [**S6004**](../../sources/bibliography.md#s6004) Microsoft Official Blog, *Inside the world's most powerful AI datacenter (Fairwater)*, 2025-09-18. [Link](https://blogs.microsoft.com/blog/2025/09/18/inside-the-worlds-most-powerful-ai-datacenter/)
- [**S6005**](../../sources/bibliography.md#s6005) Microsoft Official Blog, *Infinite scale: the architecture behind the Azure AI superfactory*, 2025-11-12. [Link](https://blogs.microsoft.com/blog/2025/11/12/infinite-scale-the-architecture-behind-the-azure-ai-superfactory/)
- [**S6006**](../../sources/bibliography.md#s6006) The New Stack, *SC23: Microsoft now has the third-fastest computer in the world*, 2023-11. [Link](https://thenewstack.io/sc500-microsoft-now-has-the-third-fastest-computer-in-the-world/)
- [**S6008**](../../sources/bibliography.md#s6008) Oracle, *Oracle Unveils Next-Generation Oracle Cloud Infrastructure Zettascale10 Cluster for AI*, 2025-10-14. [Link](https://www.oracle.com/news/announcement/ai-world-oracle-unveils-next-generation-oci-zettascale10-cluster-for-ai-2025-10-14/)
- [**S6016**](../../sources/bibliography.md#s6016) optics.org, *NVIDIA reveals plan to scale AI factories with co-packaged optics*, 2025-03-19. [Link](https://www.optics.org/news/16/3/26)
- [**S6025**](../../sources/bibliography.md#s6025) Reuters (via Investing.com), *How much does a GW of data center capacity actually cost?*, 2025-10. [Link](https://ng.investing.com/news/stock-market-news/how-much-does-a-gw-of-data-center-capacity-actually-cost-2169144)
- [**S6026**](../../sources/bibliography.md#s6026) AMCompute (blog), *AI Cluster Cost Breakdown: CapEx (2026)*, 2026. [Link](https://www.amcompute.com/blog/ai-cluster-cost-breakdown-capex)
- [**S6031**](../../sources/bibliography.md#s6031) glennklockwood.com (Glenn K. Lockwood), *Meta's H100 clusters (digital garden notes)*, 2024. [Link](https://glennklockwood.com/garden/systems/meta's-h100-clusters)
- [**S34006**](../../sources/bibliography.md#s34006) arXiv:2407.21783 (Llama Team (AI @ Meta)), *The Llama 3 Herd of Models*, 2024-07-31. [Link](https://arxiv.org/abs/2407.21783)
- [**S34022**](../../sources/bibliography.md#s34022) ACM SIGCOMM 2024 (Adithya Gangidi, Rui Miao, Shengbao Zheng et al. (Meta)), *RDMA over Ethernet for Distributed AI Training at Meta Scale*, 2024-08. [Link](https://doi.org/10.1145/3651890.3672233)
- [**S90056**](../../sources/bibliography.md#s90056) HPCwire (Qualcomm press release), *Qualcomm unveils data center roadmap for the agentic AI era with new Dragonfly portfolio*, 2026-06-24. [Link](https://www.hpcwire.com/off-the-wire/qualcomm-unveils-data-center-roadmap-for-the-agentic-ai-era-with-new-dragonfly-portfolio/)
