# Grace 与超级芯片

> [!NOTE]
> 本页为英文原文的简体中文参考译文，仅供参考；如有出入，以[英文原文](../../../layers/04-cpu-grace-vera/grace-and-the-superchip.md "English original")为准。

<sub>第 04 层 · CPU（Grace、Vera）· 阅读约 10 分钟 · 最近核实：2026-11-05</sub>

## ⚡ 要点速览

- **Grace 是一颗为“喂饱”GPU 而生的 CPU。** 它于 2021 年 4 月发布 [[S537]](../../../sources/bibliography.md#s537)，拥有 72 个 Arm [Neoverse](../../glossary.md#neoverse) V2 核心，最高配 480 GB [LPDDR5X](../../glossary.md#lpddr5x)，带宽最高约 512 GB/s [[S129]](../../../sources/bibliography.md#s129)；英伟达（NVIDIA）的调优指南预计实际可达峰值的 80–95% [[S4020]](../../../sources/bibliography.md#s4020)。
- **差异化在于链路，而非核心。** [NVLink-C2C](../../glossary.md#nvlink-c2c) 在 Grace 与其 GPU 之间提供 900 GB/s 带宽，约为 [PCIe](../../glossary.md#pcie) Gen5 x16 链路（128 GB/s）的 7 倍，并且具备[缓存一致性（cache coherence）](../../glossary.md#cache-coherence) [[S129]](../../../sources/bibliography.md#s129)[[S222]](../../../sources/bibliography.md#s222)。
- **缓存一致性使 CPU 内存成为 GPU 的第二个内存层级：**一个 GB200 [NVL72](../../glossary.md#nvl72) 机架中，约 17 TB 的 LPDDR5X 与 13.4 TB 的 [HBM3E](../../glossary.md#hbm3e) 并存 [[S121]](../../../sources/bibliography.md#s121)；Vera Rubin NVL72 中则是 54 TB LPDDR5X 配 20.7 TB [HBM4](../../glossary.md#hbm4) [[S102]](../../../sources/bibliography.md#s102)[[S362]](../../../sources/bibliography.md#s362)。
- **[超级芯片（superchip）](../../glossary.md#superchip)的配比在变化。** GH200 为每块 GPU 配一整颗 Grace 和 900 GB/s 带宽 [[S128]](../../../sources/bibliography.md#s128)；GB200 中两块 GPU 共享一条 900 GB/s 链路（每块约 450 GB/s）[[S4019]](../../../sources/bibliography.md#s4019)；Vera Rubin 把链路翻倍至 1.8 TB/s（每块 GPU 约 900 GB/s）[[S100]](../../../sources/bibliography.md#s100)[[S209]](../../../sources/bibliography.md#s209)。
- **回报：KV 缓存卸载。** 英伟达称，与在 x86 主机的 H100 上重新计算相比，改为重新加载已缓存的上下文可使首 token 时间（time-to-first-token）最多加快 14 倍，在 GH200 上还可最多再快 2 倍 [[S4016]](../../../sources/bibliography.md#s4016)。
- **弱点：**焊接式 LPDDR5X 将 Grace 的内存上限锁定在每颗 CPU 480 GB，购买时即已固定 [[S129]](../../../sources/bibliography.md#s129)；缓存一致性只适用于英伟达自家 CPU 或 [NVLink Fusion](../../glossary.md#nvlink-fusion) 合作伙伴；许多买家仍选择 [x86](../../glossary.md#x86) [HGX](../../glossary.md#hgx) 服务器 [[S319]](../../../sources/bibliography.md#s319)。

![每 GPU 的 CPU 至 GPU 带宽横向柱状图：PCIe Gen3 x16 约 32 GB/s（DGX-1），Gen4 为 64 GB/s（DGX A100），Gen5 为 128 GB/s（DGX H100），Gen6 为 256 GB/s（EPYC Venice 等 2026 年 x86 CPU）；相比之下，NVLink-C2C 在 Grace 上为 900 GB/s，在 Vera 上为 1,800 GB/s —— 是 Gen5 x16 链路的 14 倍，使 GPU 能把 CPU 的 LPDDR 当作缓存一致的第二内存层级。](../../../assets/charts/04-cpu-gpu-bandwidth-pcie-vs-c2c.svg)

## 1. Grace：一颗围绕内存带宽设计的 CPU

Grace 的主要“客户”是它身旁的 GPU，因此它以牺牲服务器 CPU 的灵活性为代价换取带宽。LPDDR5X 这种手机内存被放在模组上、紧挨着 CPU；走线短，使其能以低功耗高速运行，每颗 Grace 带宽约 512 GB/s [[S129]](../../../sources/bibliography.md#s129)，而 8 通道 DDR5 的 Xeon 8480 约为 307 GB/s [[S33022]](../../../sources/bibliography.md#s33022)。代价是：容量在出厂时即已固定。核心采用 Arm 现成的 Neoverse V2，AWS Graviton4 和谷歌（Google）Axion 用的也是它 [[S181]](../../../sources/bibliography.md#s181)[[S182]](../../../sources/bibliography.md#s182)；英伟达的差异化体现在内存和链路上。

![两种主机挂接方式对比图。左：在 DGX H100 中，一颗配 DDR5 内存（每路约 1 TB，307 GB/s）的英特尔 Xeon 8480C 通过与网卡和 SSD 共享的 PCIe Gen5 交换芯片连接四块 H100 GPU，每条 x16 链路 128 GB/s，内存池相互独立，没有缓存一致性。右：在 GB200 超级芯片中，一颗 72 核 Grace 配 480 GB LPDDR5X（约 512 GB/s），通过 900 GB/s 的缓存一致 NVLink-C2C 链路连接两块 B200 GPU（两者同时读取时每块约 450 GB/s），形成统一地址空间，使 LPDDR5X 成为第二内存层级。](../../../assets/diagrams/04-host-attach-pcie-vs-superchip.svg)

> [!TIP]
> **算例 —— “最高 512 GB/s”实际能交付多少。** 英伟达的 Grace 指南列出，双 CPU 的 Grace Superchip 在 STREAM 内存基准测试中达 820–972 GB/s，为峰值的 80–95% [[S4020]](../../../sources/bibliography.md#s4020)：即**每颗 CPU 410–486 GB/s**，或每核约 5.7–6.8 GB/s；而 56 核 Xeon 8480 每核的*峰值*约为 5.5 GB/s（307 ÷ 56）[[S33022]](../../../sources/bibliography.md#s33022)。**结论：**在 CPU 工作负载上，Grace 相对于其所取代的 x86 主机优势有限；其决定性优势在于 *GPU* 访问这部分内存的速度。

## 2. NVLink-C2C 与缓存一致性：GPU 可以直接使用 CPU 内存

在 PCIe 下，CPU 内存就像一座隔着国境的仓库：GPU 必须安排一次“发货”（一次拷贝），Gen5 x16 的速度不超过 128 GB/s，而且还要自留一份副本，这份副本可能过时。而在缓存一致的 NVLink-C2C 下，仓库就在隔壁，并且共用一套库存系统：

- **统一地址空间（[统一内存](../../glossary.md#unified-memory)）：**CPU 代码创建的指针可以直接在 GPU 内核中使用。
- **硬件一致性：**如果 CPU 修改了 GPU 已缓存的数据，硬件会使过时的副本失效。
- **细粒度访问：**GPU 可以按 64 字节的缓存行而非整页读取，适合嵌入表等稀疏查找。

最典型的应用是 [KV 缓存卸载（KV-cache offload）](../../glossary.md#kv-cache-offload)：把空闲会话的注意力缓存暂存到 CPU 内存，待用户回来时再重新加载（[KV 缓存](../../glossary.md#kv-cache)的原理见 [P2](../../primers/P2-how-ai-inference-works.md)）。

> [!TIP]
> **算例 —— 重新加载一个暂存的会话。** Llama 3.1 70B 有 80 层、8 个键/值头，每个头宽 128 [[S32006]](../../../sources/bibliography.md#s32006)。在 [FP8](../../glossary.md#fp8) 精度下，每个 token 需存储 2 × 80 × 8 × 128 字节 = **163,840 字节**，因此一个 32,768-token 的会话占 **5.4 GB**。经 PCIe Gen5 x16（单向约 64 GB/s）[[S222]](../../../sources/bibliography.md#s222) 重新加载：**约 84 ms**。经 GB200 分摊的 C2C 带宽（单向约 225 GB/s）[[S4019]](../../../sources/bibliography.md#s4019)：**约 24 ms**。经 GH200 或 Vera Rubin 每 GPU 的完整份额（约 450 GB/s）[[S128]](../../../sources/bibliography.md#s128)[[S100]](../../../sources/bibliography.md#s100)：**约 12 ms**。若改为重新计算（约 6.0 × 10¹⁵ FLOPs，在一块 H100 级 GPU 上以 1,979 dense FP8 TFLOPS 的 50% 运行）[[S33002]](../../../sources/bibliography.md#s33002)[[S32025]](../../../sources/bibliography.md#s32025)：**约 6 s**（估计）。**结论：**任何形式的卸载都比重新计算快约 70 倍；C2C 还能再把重新加载时间缩短约 7 倍，这对每秒需要恢复大量长上下文的智能体至关重要。英伟达的实测收益更小，因为真实的首 token 延迟还包含其他工作 [[S4016]](../../../sources/bibliography.md#s4016)。

![对数刻度横向柱状图。一个 32,768-token 的 Llama 3.1 70B 会话拥有 5.4 GB 的 FP8 KV 缓存。在一块 H100 级 GPU 上以 dense FP8 峰值的 50% 重新计算约需 6.1 秒（估计）；从 CPU 内存拷回则分别约需：PCIe Gen4 x16 168 ms、Gen5 84 ms、Gen6 42 ms、GB200 共享的 NVLink-C2C 24 ms、GH200 或 Vera Rubin 每 GPU 完整 C2C 份额 12 ms；相比之下从 HBM3E 读取约 1.1 ms。](../../../assets/charts/04-kv-cache-reload-time.svg)

<details>
<summary>🔧 技术细节：缓存一致的 CPU–GPU 内存如何工作</summary>

- **地址转换：**GPU 的内存管理单元通过 CPU 的页表解析 CPU 虚拟地址，使两种处理器找到同一个物理字节。
- **NUMA 视图：**操作系统把 LPDDR5X 和 [HBM](../../glossary.md#hbm) 视为不同的内存节点；软件可以显式放置数据，也可以让驱动把热页迁移到 HBM。
- **不对称性：**GPU 读取自身 HBM 的速度为 4.8–8 TB/s [[S32002]](../../../sources/bibliography.md#s32002)[[S33003]](../../../sources/bibliography.md#s33003)，而读取 CPU 内存的单向速度不超过 0.45 TB/s，因此卸载的数据应是“温”数据而非“热”数据：空闲的 KV 缓存、优化器状态、嵌入向量。
- **在 x86 主机上**，统一内存靠软件实现，但每次缺页都要以 PCIe 速度传输一整页。

</details>

## 3. 超级芯片家族：GH200 → GB200 → GB300 → Vera Rubin

| 超级芯片（首次量产） | CPU | 每 CPU 配 GPU 数 | 每 GPU C2C 带宽 | 每 GPU CPU 内存 | 每 GPU HBM |
|---|---|---|---|---|---|
| GH200（2023–24） | Grace，72 核 | 1 | 900 GB/s | 480 GB | 96–144 GB [[S128]](../../../sources/bibliography.md#s128) |
| GB200（2024–25） | Grace，72 核 | 2 | ~450 GB/s | ~240 GB | 186 GB [[S396]](../../../sources/bibliography.md#s396)[[S4019]](../../../sources/bibliography.md#s4019) |
| GB300（2025–26） | Grace，72 核 | 2 | ~450 GB/s | ~240 GB | 288 GB [[S32004]](../../../sources/bibliography.md#s32004) |
| Vera Rubin（2026 年下半年） | Vera，88 核 | 2 | ~900 GB/s | ~750 GB | 288 GB [[S102]](../../../sources/bibliography.md#s102)[[S100]](../../../sources/bibliography.md#s100) |

GB200 通过把每块 GPU 的主机带宽和 CPU 内存减半来节省 CPU 插槽；Vera 则把两者都恢复了。

![每个加速器内存分组柱状图。CPU 侧内存：DGX-1 V100 为 64 GB，DGX A100 为 128，DGX H100 与 DGX B200 为 256，GH200 为 480，GB200 与 GB300 NVL72 为 240，Vera Rubin NVL72 约 750 GB；每 GPU HBM 依次为 16、40、80、180、144、186、288 和 288 GB。AWS Trn2 每颗 Trainium2 配 128 GB 主机内存（96 GB HBM），Trn3 为 192 GB（144 GB HBM）。GPU 可经缓存一致的 NVLink-C2C 访问 Grace 和 Vera 的内存。](../../../assets/charts/04-host-memory-per-accelerator.svg)

> [!TIP]
> **算例 —— 能暂存多少个会话？** 在一块 GH200 上以 FP8 部署 Llama 3.1 70B（权重约 70 GB）[[S128]](../../../sources/bibliography.md#s128)：剩余约 74 GB HBM 可用于 KV 缓存，约能容纳 **13** 个上文所述的 5.4 GB 会话。其 480 GB LPDDR5X 还能再容纳 **约 89** 个，每个约 12 ms 即可重新加载。一块 Vera Rubin GPU 约 750 GB 的份额 [[S102]](../../../sources/bibliography.md#s102) 可容纳约 139 个。**结论：**CPU 内存层级可使一块 GPU 能保持“温”状态的用户数提高约 7–10 倍。

**[Q2 · 关键指标]** 五个数字决定主机是助力还是拖累：

1. **每 GPU 的 CPU↔GPU 带宽，以及是否缓存一致：**PCIe Gen5 主机为 128 GB/s，C2C 为约 450–900 GB/s [[S222]](../../../sources/bibliography.md#s222)[[S4019]](../../../sources/bibliography.md#s4019)[[S100]](../../../sources/bibliography.md#s100)。
2. **每 GPU 的 CPU 内存：**256 GB（DGX H100）、约 240 GB（GB200）、约 750 GB（Vera Rubin）[[S102]](../../../sources/bibliography.md#s102)。
3. **每核 CPU 内存带宽：**Grace 约 7.1 GB/s，Vera 约 13.6 GB/s [[S129]](../../../sources/bibliography.md#s129)[[S4000]](../../../sources/bibliography.md#s4000)。
4. **每 GPU 主机线程数：**DGX H100、GB200 和 Vera Rubin 分别为 28、36 和 88（[AI 为什么需要 CPU](why-ai-needs-a-cpu.md)）。
5. **CPU 工作负载的每瓦性能：**Meta 称改用独立 Grace 后部分工作负载最高提升 2 倍（公司自述）[[S4007]](../../../sources/bibliography.md#s4007)。

> [!WARNING]
> **误区与事实：**“Grace 能让 GPU 变快。”当模型和数据都能放进 HBM 时，主机链路大多处于空闲，x86 HGX 服务器的表现相差无几；英伟达至今仍在销售 x86 版 DGX B200 和 B300 [[S319]](../../../sources/bibliography.md#s319)[[S321]](../../../sources/bibliography.md#s321)。只有当工作溢出 HBM，或机架级集成至关重要时，Grace 才物有所值。

## 🎯 企业发展视角

1. **护城河是缓存一致性，而非 CPU 本身。** 任何 Arm 授权厂商都能做出一颗 72 核 CPU；但能把它以缓存一致方式接到领先 GPU 上的寥寥无几。[NVLink](../../glossary.md#nvlink) Fusion 把这种挂接能力授权给了高通（Qualcomm）和富士通 [[S90031]](../../../sources/bibliography.md#s90031)：双方各自保留了什么？
2. **内存价值发生转移。** 每个 Vera Rubin 机架 54 TB 的 LPDDR5X [[S102]](../../../sources/bibliography.md#s102) 使英伟达成为 [LPDDR](../../glossary.md#lpddr) 的大买家，为内存厂商开辟了新的出货渠道（[第 03 层](../03-memory-packaging-supply-chain/index.md)）。
3. **高通问题（仅基于公开信息）：**作为已官宣的 Fusion CPU 合作伙伴 [[S131]](../../../sources/bibliography.md#s131)，基于 Oryon、配 LPDDR5X 的 CPU 能否达到 Grace 的“每瓦内存”水平？英伟达又是否会向第三方主机开放 C2C 级别的带宽？

## 📚 来源（Sources）

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S100**](../../../sources/bibliography.md#s100) NVIDIA Technical Blog, *Inside the NVIDIA Vera Rubin Platform: Six New Chips, One AI Supercomputer*, 2026-01-05. [Link](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)
- [**S102**](../../../sources/bibliography.md#s102) NVIDIA, *NVIDIA DGX Vera Rubin NVL72*, 2026. [Link](https://www.nvidia.com/en-us/data-center/dgx-vera-rubin-nvl72/)
- [**S121**](../../../sources/bibliography.md#s121) NVIDIA, *NVIDIA GB200 NVL72*, 2024-03. [Link](https://www.nvidia.com/en-us/data-center/gb200-nvl72/)
- [**S128**](../../../sources/bibliography.md#s128) NVIDIA, *NVIDIA GH200 Grace Hopper Superchip*, 2023-08. [Link](https://www.nvidia.com/en-us/data-center/grace-hopper-superchip/)
- [**S129**](../../../sources/bibliography.md#s129) NVIDIA, *NVIDIA Grace CPU*, 2023. [Link](https://www.nvidia.com/en-us/data-center/grace-cpu/)
- [**S131**](../../../sources/bibliography.md#s131) NVIDIA Newsroom, *NVIDIA NVLink Fusion: semi-custom AI infrastructure partner ecosystem (Computex 2025)*, 2025-05-19. [Link](https://nvidianews.nvidia.com/news/nvidia-nvlink-fusion-semi-custom-ai-infrastructure-partner-ecosystem)
- [**S181**](../../../sources/bibliography.md#s181) Amazon Web Services, *AWS Graviton Processor*, 2024. [Link](https://aws.amazon.com/ec2/graviton/)
- [**S182**](../../../sources/bibliography.md#s182) Google Cloud Blog, *Introducing Google Axion Processors, our new Arm-based CPUs*, 2024-04-09. [Link](https://cloud.google.com/blog/products/compute/introducing-googles-new-arm-based-cpu)
- [**S209**](../../../sources/bibliography.md#s209) DatacenterDynamics, *Nvidia announces Vera Rubin superchip for late 2026*, 2025-10-28. [Link](https://datacenterdynamics.com/en/news/nvidia-announces-vera-rubin-superchip-for-late-2026)
- [**S222**](../../../sources/bibliography.md#s222) Tom's Hardware, *PCI Express roadmap: the path to 1TB/s with PCIe 8.0, the challenges of integration, and beyond*, 2025. [Link](https://www.tomshardware.com/pc-components/motherboards/pci-express-roadmap-the-path-to-1tb-s-with-pci-8-0-the-challenges-of-integration-and-beyond)
- [**S319**](../../../sources/bibliography.md#s319) NVIDIA (mirror hosted by OpenZeka), *NVIDIA DGX B200 datasheet*, 2024. [Link](https://openzeka.com/wp-content/uploads/2024/11/dgx-scale-ai-infrastructure-dgx-b200-datasheet-nvidia-web-1-1.pdf)
- [**S321**](../../../sources/bibliography.md#s321) Colfax International, *NVIDIA DGX B300 (specification page)*, 2025. [Link](https://www.colfax-intl.com/nvidia/nvidia-dgx-b300)
- [**S362**](../../../sources/bibliography.md#s362) Digital Citizen, *NVIDIA Vera Rubin pushes memory costs higher as NVL72 rack reaches 74.7 TB of DRAM*, 2026-05. [Link](https://www.digitalcitizen.life/nvidia-vera-rubin-pushes-memory-costs-higher-as-nvl72-rack-reaches-74-7-tb-of-dram/)
- [**S396**](../../../sources/bibliography.md#s396) NVIDIA Newsroom, *NVIDIA Blackwell platform arrives to power a new era of computing*, 2024-03-18. [Link](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing)
- [**S537**](../../../sources/bibliography.md#s537) NVIDIA press release via Yahoo Finance, *NVIDIA Announces CPU for Giant AI and High Performance Computing Workloads*, 2021-04-12. [Link](https://sg.finance.yahoo.com/news/nvidia-announces-cpu-giant-ai-161900753.html)
- [**S4000**](../../../sources/bibliography.md#s4000) NVIDIA Newsroom, *NVIDIA Launches Vera CPU, Purpose-Built for Agentic AI*, 2026-03-16. [Link](https://nvidianews.nvidia.com/news/nvidia-launches-vera-cpu-purpose-built-for-agentic-ai)
- [**S4007**](../../../sources/bibliography.md#s4007) Tom's Hardware (mirror at 3dtested.com), *Meta will deploy standalone Nvidia Grace CPUs in production with Vera to follow*, 2026-02. [Link](https://www.3dtested.com/pc-components/cpus/meta-will-deploy-standalone-nvidia-grace-cpus-in-production-with-vera-to-follow-company-sees-perf-per-watt-improvements-of-up-to-2x-in-some-cpu-workloads)
- [**S4016**](../../../sources/bibliography.md#s4016) NVIDIA Technical Blog, *NVIDIA GH200 Superchip Accelerates Inference by 2x in Multiturn Interactions with Llama Models*, 2024. [Link](https://developer.nvidia.com/blog/nvidia-gh200-superchip-accelerates-inference-by-2x-in-multiturn-interactions-with-llama-models/)
- [**S4019**](../../../sources/bibliography.md#s4019) heise online, *Blackwell: Nvidia unveils its next generation of AI accelerators*, 2024-03-19. [Link](https://heise.de/en/news/Blackwell-Nvidia-unveils-its-next-generation-of-AI-accelerators-9782399.html)
- [**S4020**](../../../sources/bibliography.md#s4020) NVIDIA (GitHub), *NVIDIA Grace CPU Benchmarking Guide: STREAM*, 2024. [Link](https://github.com/NVIDIA/grace-cpu-benchmarking-guide/blob/main/src/foundations/STREAM/index.md)
- [**S32002**](../../../sources/bibliography.md#s32002) NVIDIA, *NVIDIA H200 Tensor Core GPU (product page)*, 2023-11. [Link](https://www.nvidia.com/en-us/data-center/h200/)
- [**S32004**](../../../sources/bibliography.md#s32004) NVIDIA, *NVIDIA GB300 NVL72 / Blackwell Ultra (product page)*, 2025-03. [Link](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)
- [**S32006**](../../../sources/bibliography.md#s32006) Meta via Hugging Face, *Llama 3.1 70B configuration (config.json)*, 2024-07-23. [Link](https://huggingface.co/meta-llama/Llama-3.1-70B/blob/main/config.json)
- [**S32025**](../../../sources/bibliography.md#s32025) nvidia_deep_dive_claude repository, *Repo analysis: inference token-budget scenarios and roofline serving model (Primer P2)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/primers/P2-how-ai-inference-works.md)
- [**S33002**](../../../sources/bibliography.md#s33002) NVIDIA, *NVIDIA H100 Tensor Core GPU (product page and datasheet)*, 2022-03-22. [Link](https://www.nvidia.com/en-us/data-center/h100/)
- [**S33003**](../../../sources/bibliography.md#s33003) Lenovo Press, *ThinkSystem NVIDIA B200 180GB 1000W GPU product guide*, 2025. [Link](https://lenovopress.lenovo.com/lp2226-thinksystem-nvidia-b200-180gb-1000w-gpu)
- [**S33022**](../../../sources/bibliography.md#s33022) NVIDIA Docs, *NVIDIA DGX H100 User Guide — Introduction (system specifications)*, 2023. [Link](https://docs.nvidia.com/dgx/dgxh100-user-guide/introduction-to-dgxh100.html)
- [**S90031**](../../../sources/bibliography.md#s90031) ServeTheHome, *NVIDIA announces NVLink Fusion bringing NVLink to third-party CPUs and accelerators*, 2025-05-19. [Link](https://www.servethehome.com/nvidia-announces-nvlink-fusion-bringing-nvlink-to-third-party-cpus-and-accelerators/nvlink-fusion-partners/)
