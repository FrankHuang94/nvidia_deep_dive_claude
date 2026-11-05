# Grace and the superchip

<sub>Layer 04 · CPU (Grace, Vera) · ~10 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **Grace is a CPU built to feed GPUs.** Announced in April 2021 [[S537]](../../sources/bibliography.md#s537), it has 72 Arm [Neoverse](../../glossary.md#neoverse) V2 cores and up to 480 GB of [LPDDR5X](../../glossary.md#lpddr5x) at up to ~512 GB/s [[S129]](../../sources/bibliography.md#s129); NVIDIA's tuning guide expects 80–95% of that peak in practice [[S4020]](../../sources/bibliography.md#s4020).
- **The differentiator is the link, not the cores.** [NVLink-C2C](../../glossary.md#nvlink-c2c) moves 900 GB/s between Grace and its GPUs, ~7× a [PCIe](../../glossary.md#pcie) Gen5 x16 link (128 GB/s), and it is [cache-coherent](../../glossary.md#cache-coherence) [[S129]](../../sources/bibliography.md#s129)[[S222]](../../sources/bibliography.md#s222).
- **Coherence makes CPU memory a second GPU memory tier:** ~17 TB of LPDDR5X beside 13.4 TB of [HBM3E](../../glossary.md#hbm3e) in a GB200 [NVL72](../../glossary.md#nvl72) rack [[S121]](../../sources/bibliography.md#s121); 54 TB beside 20.7 TB of [HBM4](../../glossary.md#hbm4) in Vera Rubin NVL72 [[S102]](../../sources/bibliography.md#s102)[[S362]](../../sources/bibliography.md#s362).
- **The [superchip](../../glossary.md#superchip) ratio has moved.** GH200 gives each GPU a whole Grace and 900 GB/s [[S128]](../../sources/bibliography.md#s128); in GB200 two GPUs share one 900 GB/s link (~450 GB/s each) [[S4019]](../../sources/bibliography.md#s4019); Vera Rubin doubles the link to 1.8 TB/s (~900 GB/s per GPU) [[S100]](../../sources/bibliography.md#s100)[[S209]](../../sources/bibliography.md#s209).
- **Payoff: KV-cache offload.** NVIDIA reports up to 14× faster time-to-first-token from reloading cached context instead of recomputing it on x86-hosted H100, and up to 2× more on GH200 [[S4016]](../../sources/bibliography.md#s4016).
- **Weaknesses:** soldered LPDDR5X caps Grace at 480 GB per CPU, fixed at purchase [[S129]](../../sources/bibliography.md#s129); coherence works only with NVIDIA CPUs or [NVLink Fusion](../../glossary.md#nvlink-fusion) partners; many buyers still choose [x86](../../glossary.md#x86) [HGX](../../glossary.md#hgx) servers [[S319]](../../sources/bibliography.md#s319).

![Horizontal bar chart of CPU-to-GPU bandwidth per GPU: PCIe Gen3 x16 about 32 GB/s (DGX-1), Gen4 64 GB/s (DGX A100), Gen5 128 GB/s (DGX H100) and Gen6 256 GB/s (2026 x86 CPUs such as EPYC Venice), versus NVLink-C2C at 900 GB/s on Grace and 1,800 GB/s on Vera - 14 times a Gen5 x16 link, which lets the GPU treat CPU LPDDR as a coherent second memory tier.](../../assets/charts/04-cpu-gpu-bandwidth-pcie-vs-c2c.svg)

## 1. Grace: a CPU designed around memory bandwidth

Grace's main customer is the GPU beside it, so it trades a server CPU's flexibility for bandwidth. LPDDR5X, phone memory, sits on the module next to the CPU; short traces let it run fast at low power, giving ~512 GB/s per Grace [[S129]](../../sources/bibliography.md#s129) versus ~307 GB/s for an 8-channel DDR5 Xeon 8480 [[S33022]](../../sources/bibliography.md#s33022). The price: capacity is fixed at the factory. The cores are Arm's off-the-shelf Neoverse V2, also used in AWS Graviton4 and Google Axion [[S181]](../../sources/bibliography.md#s181)[[S182]](../../sources/bibliography.md#s182); NVIDIA differentiated on memory and the link.

![Diagram comparing two host attachments. Left: in a DGX H100, an Intel Xeon 8480C with DDR5 memory (about 1 TB per socket, 307 GB/s) reaches four H100 GPUs through PCIe Gen5 switches shared with NICs and SSDs, 128 GB/s per x16 link, with separate memory pools and no cache coherence. Right: in a GB200 superchip, a 72-core Grace with 480 GB of LPDDR5X at about 512 GB/s connects to two B200 GPUs over a 900 GB/s cache-coherent NVLink-C2C link (about 450 GB/s per GPU when both pull), creating one address space so LPDDR5X becomes a second memory tier.](../../assets/diagrams/04-host-attach-pcie-vs-superchip.svg)

> [!TIP]
> **Worked example — what "up to 512 GB/s" delivers.** NVIDIA's Grace guide lists 820–972 GB/s on the STREAM memory benchmark for a two-CPU Grace Superchip, 80–95% of peak [[S4020]](../../sources/bibliography.md#s4020): **410–486 GB/s per CPU**, or ~5.7–6.8 GB/s per core, versus ~5.5 GB/s of *peak* per core on a 56-core Xeon 8480 (307 ÷ 56) [[S33022]](../../sources/bibliography.md#s33022). **Conclusion:** Grace's edge over the x86 host it replaced is moderate on CPU work; its decisive advantage is how fast the *GPU* reaches that memory.

## 2. NVLink-C2C and coherence: the GPU can use CPU memory directly

With PCIe, CPU memory is a warehouse across a border: the GPU must arrange a shipment (a copy) at ≤128 GB/s for Gen5 x16 and keep its own copy, which can go stale. With coherent NVLink-C2C the warehouse is next door, with one shared inventory system:

- **One address space ([unified memory](../../glossary.md#unified-memory)):** a pointer created by CPU code works in a GPU kernel.
- **Hardware coherence:** if the CPU changes data the GPU has cached, hardware invalidates the stale copy.
- **Fine granularity:** the GPU can fetch a 64-byte line instead of a page, which suits sparse lookups such as embedding tables.

The clearest use is [KV-cache offload](../../glossary.md#kv-cache-offload): parking idle conversations' attention cache in CPU memory and reloading it when the user returns (the [KV cache](../../glossary.md#kv-cache) is explained in [P2](../../primers/P2-how-ai-inference-works.md)).

> [!TIP]
> **Worked example — reloading a parked conversation.** Llama 3.1 70B has 80 layers, 8 key/value heads and 128-wide heads [[S32006]](../../sources/bibliography.md#s32006). In [FP8](../../glossary.md#fp8) each token stores 2 × 80 × 8 × 128 bytes = **163,840 bytes**, so a 32,768-token conversation holds **5.4 GB**. Reload over PCIe Gen5 x16 (~64 GB/s each way) [[S222]](../../sources/bibliography.md#s222): **~84 ms**. Over GB200's C2C share (~225 GB/s each way) [[S4019]](../../sources/bibliography.md#s4019): **~24 ms**. Over a full GH200 or Vera Rubin per-GPU share (~450 GB/s) [[S128]](../../sources/bibliography.md#s128)[[S100]](../../sources/bibliography.md#s100): **~12 ms**. Recomputing instead (~6.0 × 10¹⁵ FLOPs on one H100-class GPU at 50% of 1,979 dense FP8 TFLOPS) [[S33002]](../../sources/bibliography.md#s33002)[[S32025]](../../sources/bibliography.md#s32025): **~6 s** (Est.). **Conclusion:** any offload beats recomputation ~70×; C2C cuts the reload another ~7×, which matters for agents resuming many long contexts per second. NVIDIA's measured gains are smaller because real time-to-first-token includes other work [[S4016]](../../sources/bibliography.md#s4016).

![Log-scale horizontal bar chart. A 32,768-token Llama 3.1 70B conversation has a 5.4 GB FP8 KV cache. Recomputing it on one H100-class GPU at 50% of dense FP8 peak takes about 6.1 seconds (estimate); copying it back from CPU memory takes about 168 ms over PCIe Gen4 x16, 84 ms over Gen5, 42 ms over Gen6, 24 ms over GB200's shared NVLink-C2C and 12 ms over a full GH200 or Vera Rubin per-GPU C2C share, versus about 1.1 ms to read it from HBM3E.](../../assets/charts/04-kv-cache-reload-time.svg)

<details>
<summary>🔧 Under the hood: how coherent CPU–GPU memory works</summary>

- **Address translation:** the GPU's memory-management unit resolves CPU virtual addresses through the CPU's page tables, so both processors find the same physical byte.
- **NUMA view:** the operating system sees LPDDR5X and [HBM](../../glossary.md#hbm) as separate memory nodes; software places data explicitly or lets the driver migrate hot pages into HBM.
- **Asymmetry:** a GPU reads its HBM at 4.8–8 TB/s [[S32002]](../../sources/bibliography.md#s32002)[[S33003]](../../sources/bibliography.md#s33003) but CPU memory at ≤0.45 TB/s each way, so offloaded data must be warm, not hot: idle KV cache, optimizer state, embeddings.
- **On x86 hosts** unified memory exists in software, but each miss costs a page transfer at PCIe speed.

</details>

## 3. The superchip family: GH200 → GB200 → GB300 → Vera Rubin

| Superchip (first volume) | CPU | GPUs per CPU | C2C per GPU | CPU memory per GPU | HBM per GPU |
|---|---|---|---|---|---|
| GH200 (2023–24) | Grace, 72 cores | 1 | 900 GB/s | 480 GB | 96–144 GB [[S128]](../../sources/bibliography.md#s128) |
| GB200 (2024–25) | Grace, 72 cores | 2 | ~450 GB/s | ~240 GB | 186 GB [[S396]](../../sources/bibliography.md#s396)[[S4019]](../../sources/bibliography.md#s4019) |
| GB300 (2025–26) | Grace, 72 cores | 2 | ~450 GB/s | ~240 GB | 288 GB [[S32004]](../../sources/bibliography.md#s32004) |
| Vera Rubin (H2 2026) | Vera, 88 cores | 2 | ~900 GB/s | ~750 GB | 288 GB [[S102]](../../sources/bibliography.md#s102)[[S100]](../../sources/bibliography.md#s100) |

GB200 saved sockets by halving each GPU's host bandwidth and CPU memory; Vera restores both.

![Grouped bar chart of memory per accelerator. CPU-attached memory: DGX-1 V100 64 GB, DGX A100 128, DGX H100 and DGX B200 256, GH200 480, GB200 and GB300 NVL72 240, Vera Rubin NVL72 about 750 GB; HBM per GPU: 16, 40, 80, 180, 144, 186, 288 and 288 GB. AWS Trn2 has 128 GB of host memory per Trainium2 (96 GB HBM) and Trn3 192 GB (144 GB HBM). Grace and Vera memory is reachable by the GPU over coherent NVLink-C2C.](../../assets/charts/04-host-memory-per-accelerator.svg)

> [!TIP]
> **Worked example — how many parked conversations fit?** Serve Llama 3.1 70B in FP8 (~70 GB of weights) on one GH200 [[S128]](../../sources/bibliography.md#s128): ~74 GB of HBM is left for KV cache, about **13** of the 5.4 GB conversations above. Its 480 GB of LPDDR5X holds **~89** more, each reloadable in ~12 ms. A Vera Rubin GPU's ~750 GB share [[S102]](../../sources/bibliography.md#s102) holds ~139. **Conclusion:** the CPU tier multiplies the "warm" users a GPU can hold by ~7–10×.

**[Q2 · Metrics that matter]** Five numbers decide whether the host helps or hurts:

1. **CPU↔GPU bandwidth per GPU, and coherence:** 128 GB/s on PCIe Gen5 hosts vs ~450–900 GB/s on C2C [[S222]](../../sources/bibliography.md#s222)[[S4019]](../../sources/bibliography.md#s4019)[[S100]](../../sources/bibliography.md#s100).
2. **CPU memory per GPU:** 256 GB (DGX H100), ~240 GB (GB200), ~750 GB (Vera Rubin) [[S102]](../../sources/bibliography.md#s102).
3. **CPU memory bandwidth per core:** Grace ~7.1 GB/s, Vera ~13.6 GB/s [[S129]](../../sources/bibliography.md#s129)[[S4000]](../../sources/bibliography.md#s4000).
4. **Host threads per GPU:** 28, 36 and 88 on DGX H100, GB200 and Vera Rubin ([Why AI needs a CPU](why-ai-needs-a-cpu.md)).
5. **Performance per watt on CPU work:** Meta reports up to 2× on some workloads after moving to standalone Grace (company claim) [[S4007]](../../sources/bibliography.md#s4007).

> [!WARNING]
> **Myth vs. reality:** "Grace makes the GPU faster." When the model and data fit in HBM, the host link is mostly idle and an x86 HGX server performs similarly; NVIDIA still sells x86 DGX B200 and B300 [[S319]](../../sources/bibliography.md#s319)[[S321]](../../sources/bibliography.md#s321). Grace pays off when work spills out of HBM or when rack-scale integration matters.

## 🎯 Corp Dev Lens

1. **Coherence is the moat, not the CPU.** Any Arm licensee can build a 72-core CPU; few can attach it coherently to the leading GPU. [NVLink](../../glossary.md#nvlink) Fusion licenses that attach to Qualcomm and Fujitsu [[S90031]](../../sources/bibliography.md#s90031): what does each side keep?
2. **Memory value shifts.** 54 TB of LPDDR5X per Vera Rubin rack [[S102]](../../sources/bibliography.md#s102) makes NVIDIA a major [LPDDR](../../glossary.md#lpddr) buyer, a new outlet for memory makers ([Layer 03](../03-memory-packaging-supply-chain/index.md)).
3. **Qualcomm question (public information only):** as an announced Fusion CPU partner [[S131]](../../sources/bibliography.md#s131), could an Oryon-based CPU with LPDDR5X match Grace's memory-per-watt profile, and would NVIDIA allow C2C-class bandwidth to a third-party host?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S100**](../../sources/bibliography.md#s100) NVIDIA Technical Blog, *Inside the NVIDIA Vera Rubin Platform: Six New Chips, One AI Supercomputer*, 2026-01-05. [Link](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)
- [**S102**](../../sources/bibliography.md#s102) NVIDIA, *NVIDIA DGX Vera Rubin NVL72*, 2026. [Link](https://www.nvidia.com/en-us/data-center/dgx-vera-rubin-nvl72/)
- [**S121**](../../sources/bibliography.md#s121) NVIDIA, *NVIDIA GB200 NVL72*, 2024-03. [Link](https://www.nvidia.com/en-us/data-center/gb200-nvl72/)
- [**S128**](../../sources/bibliography.md#s128) NVIDIA, *NVIDIA GH200 Grace Hopper Superchip*, 2023-08. [Link](https://www.nvidia.com/en-us/data-center/grace-hopper-superchip/)
- [**S129**](../../sources/bibliography.md#s129) NVIDIA, *NVIDIA Grace CPU*, 2023. [Link](https://www.nvidia.com/en-us/data-center/grace-cpu/)
- [**S131**](../../sources/bibliography.md#s131) NVIDIA Newsroom, *NVIDIA NVLink Fusion: semi-custom AI infrastructure partner ecosystem (Computex 2025)*, 2025-05-19. [Link](https://nvidianews.nvidia.com/news/nvidia-nvlink-fusion-semi-custom-ai-infrastructure-partner-ecosystem)
- [**S181**](../../sources/bibliography.md#s181) Amazon Web Services, *AWS Graviton Processor*, 2024. [Link](https://aws.amazon.com/ec2/graviton/)
- [**S182**](../../sources/bibliography.md#s182) Google Cloud Blog, *Introducing Google Axion Processors, our new Arm-based CPUs*, 2024-04-09. [Link](https://cloud.google.com/blog/products/compute/introducing-googles-new-arm-based-cpu)
- [**S209**](../../sources/bibliography.md#s209) DatacenterDynamics, *Nvidia announces Vera Rubin superchip for late 2026*, 2025-10-28. [Link](https://datacenterdynamics.com/en/news/nvidia-announces-vera-rubin-superchip-for-late-2026)
- [**S222**](../../sources/bibliography.md#s222) Tom's Hardware, *PCI Express roadmap: the path to 1TB/s with PCIe 8.0, the challenges of integration, and beyond*, 2025. [Link](https://www.tomshardware.com/pc-components/motherboards/pci-express-roadmap-the-path-to-1tb-s-with-pci-8-0-the-challenges-of-integration-and-beyond)
- [**S319**](../../sources/bibliography.md#s319) NVIDIA (mirror hosted by OpenZeka), *NVIDIA DGX B200 datasheet*, 2024. [Link](https://openzeka.com/wp-content/uploads/2024/11/dgx-scale-ai-infrastructure-dgx-b200-datasheet-nvidia-web-1-1.pdf)
- [**S321**](../../sources/bibliography.md#s321) Colfax International, *NVIDIA DGX B300 (specification page)*, 2025. [Link](https://www.colfax-intl.com/nvidia/nvidia-dgx-b300)
- [**S362**](../../sources/bibliography.md#s362) Digital Citizen, *NVIDIA Vera Rubin pushes memory costs higher as NVL72 rack reaches 74.7 TB of DRAM*, 2026-05. [Link](https://www.digitalcitizen.life/nvidia-vera-rubin-pushes-memory-costs-higher-as-nvl72-rack-reaches-74-7-tb-of-dram/)
- [**S396**](../../sources/bibliography.md#s396) NVIDIA Newsroom, *NVIDIA Blackwell platform arrives to power a new era of computing*, 2024-03-18. [Link](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing)
- [**S537**](../../sources/bibliography.md#s537) NVIDIA press release via Yahoo Finance, *NVIDIA Announces CPU for Giant AI and High Performance Computing Workloads*, 2021-04-12. [Link](https://sg.finance.yahoo.com/news/nvidia-announces-cpu-giant-ai-161900753.html)
- [**S4000**](../../sources/bibliography.md#s4000) NVIDIA Newsroom, *NVIDIA Launches Vera CPU, Purpose-Built for Agentic AI*, 2026-03-16. [Link](https://nvidianews.nvidia.com/news/nvidia-launches-vera-cpu-purpose-built-for-agentic-ai)
- [**S4007**](../../sources/bibliography.md#s4007) Tom's Hardware (mirror at 3dtested.com), *Meta will deploy standalone Nvidia Grace CPUs in production with Vera to follow*, 2026-02. [Link](https://www.3dtested.com/pc-components/cpus/meta-will-deploy-standalone-nvidia-grace-cpus-in-production-with-vera-to-follow-company-sees-perf-per-watt-improvements-of-up-to-2x-in-some-cpu-workloads)
- [**S4016**](../../sources/bibliography.md#s4016) NVIDIA Technical Blog, *NVIDIA GH200 Superchip Accelerates Inference by 2x in Multiturn Interactions with Llama Models*, 2024. [Link](https://developer.nvidia.com/blog/nvidia-gh200-superchip-accelerates-inference-by-2x-in-multiturn-interactions-with-llama-models/)
- [**S4019**](../../sources/bibliography.md#s4019) heise online, *Blackwell: Nvidia unveils its next generation of AI accelerators*, 2024-03-19. [Link](https://heise.de/en/news/Blackwell-Nvidia-unveils-its-next-generation-of-AI-accelerators-9782399.html)
- [**S4020**](../../sources/bibliography.md#s4020) NVIDIA (GitHub), *NVIDIA Grace CPU Benchmarking Guide: STREAM*, 2024. [Link](https://github.com/NVIDIA/grace-cpu-benchmarking-guide/blob/main/src/foundations/STREAM/index.md)
- [**S32002**](../../sources/bibliography.md#s32002) NVIDIA, *NVIDIA H200 Tensor Core GPU (product page)*, 2023-11. [Link](https://www.nvidia.com/en-us/data-center/h200/)
- [**S32004**](../../sources/bibliography.md#s32004) NVIDIA, *NVIDIA GB300 NVL72 / Blackwell Ultra (product page)*, 2025-03. [Link](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)
- [**S32006**](../../sources/bibliography.md#s32006) Meta via Hugging Face, *Llama 3.1 70B configuration (config.json)*, 2024-07-23. [Link](https://huggingface.co/meta-llama/Llama-3.1-70B/blob/main/config.json)
- [**S32025**](../../sources/bibliography.md#s32025) nvidia_deep_dive_claude repository, *Repo analysis: inference token-budget scenarios and roofline serving model (Primer P2)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/primers/P2-how-ai-inference-works.md)
- [**S33002**](../../sources/bibliography.md#s33002) NVIDIA, *NVIDIA H100 Tensor Core GPU (product page and datasheet)*, 2022-03-22. [Link](https://www.nvidia.com/en-us/data-center/h100/)
- [**S33003**](../../sources/bibliography.md#s33003) Lenovo Press, *ThinkSystem NVIDIA B200 180GB 1000W GPU product guide*, 2025. [Link](https://lenovopress.lenovo.com/lp2226-thinksystem-nvidia-b200-180gb-1000w-gpu)
- [**S33022**](../../sources/bibliography.md#s33022) NVIDIA Docs, *NVIDIA DGX H100 User Guide — Introduction (system specifications)*, 2023. [Link](https://docs.nvidia.com/dgx/dgxh100-user-guide/introduction-to-dgxh100.html)
- [**S90031**](../../sources/bibliography.md#s90031) ServeTheHome, *NVIDIA announces NVLink Fusion bringing NVLink to third-party CPUs and accelerators*, 2025-05-19. [Link](https://www.servethehome.com/nvidia-announces-nvlink-fusion-bringing-nvlink-to-third-party-cpus-and-accelerators/nvlink-fusion-partners/)
