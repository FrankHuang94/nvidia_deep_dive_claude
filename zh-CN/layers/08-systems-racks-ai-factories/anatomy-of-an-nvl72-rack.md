# NVL72 机架解剖

> [!NOTE]
> 本页为英文原文的简体中文参考译文，仅供参考；如有出入，以[英文原文](../../../layers/08-systems-racks-ai-factories/anatomy-of-an-nvl72-rack.md "English original")为准。

<sub>第 08 层 · 系统、机架与 AI 工厂 · 约 9 分钟阅读 · 最后核实：2026-11-05</sub>

## ⚡ 要点速览

- **一个机架，一台计算机。** 一个 [NVL72](../../../glossary.md#nvl72) 机架容纳 18 个 1U [计算托盘](../../../glossary.md#compute-tray)（每个托盘 2 颗 CPU + 4 颗 GPU，合计 72 颗 GPU、36 颗 CPU）和 9 个 [NVLink 交换托盘](../../../glossary.md#nvlink-switch-tray)，所有 GPU 通过铜缆背板与其他每一颗 GPU 互连 [[S8000]](../../../sources/bibliography.md#s8000)[[S396]](../../../sources/bibliography.md#s396)。
- **背板（spine）是关键所在：** 约 5,000 根铜缆（总长约 2 英里）让每颗 GPU 以 1.8 TB/s 的带宽连通全部 72 颗 GPU（合计约 130 TB/s）；不用光器件，每个机架可省下约 20 kW 的光模块功耗 [[S5000]](../../../sources/bibliography.md#s5000)[[S5001]](../../../sources/bibliography.md#s5001)。
- **它本质上是一个供电与管路产品：** 8 个 33 kW 的[电源架](../../../glossary.md#power-shelf)为约 50 V 直流[母排](../../../glossary.md#busbar)供电；每颗 GPU 和 CPU 上的冷板连接到机架分液歧管和[冷却液分配单元（CDU）](../../../glossary.md#cdu) [[S8000]](../../../sources/bibliography.md#s8000)[[S5007]](../../../sources/bibliography.md#s5007)。
- **规模：** 约 120 kW（GB200）、约 132 kW（GB300）、约 190–230 kW（Vera Rubin，有报道）；重约 1.36 吨（GB200）[[S336]](../../../sources/bibliography.md#s336)[[S337]](../../../sources/bibliography.md#s337)[[S303]](../../../sources/bibliography.md#s303)[[S335]](../../../sources/bibliography.md#s335)。
- **Vera Rubin 重新设计了托盘：** 无线缆、无软管、无风扇，组装时间从约 2 小时缩短到约 5 分钟（英伟达（NVIDIA）的说法），每机架交换芯片数量从 18 颗翻倍至 36 颗 [[S8002]](../../../sources/bibliography.md#s8002)[[S301]](../../../sources/bibliography.md#s301)[[S332]](../../../sources/bibliography.md#s332)。
- **弱点：** 高密度意味着风险集中。早期 GB200 机架在上量阶段遇到铜缆背板的可靠性问题，而如今单个机架是价值约 $4–8M、必须作为整体维护的单元（估计）[[S626]](../../../sources/bibliography.md#s626)[[S332]](../../../sources/bibliography.md#s332)。

![NVL72 机架示意图。正面从上到下：带外管理交换机；上部电源架组（每个电源架含 6 个 5.5 kW 电源模块，最高 33 kW，交流输入、约 50 V 直流输出）；计算托盘 1 至 10；9 个 NVLink 交换托盘，每个含 2 颗交换芯片（每机架 18 颗，Vera Rubin 为 36 颗）；计算托盘 11 至 18（合计 72 颗 GPU 和 36 颗 CPU）；以及下部电源架组，在英伟达的 DGX 配置中共 8 个电源架。背面：由约 5,000 根线缆组成的 NVLink 铜缆背板，让每颗 GPU 以 1.8 TB/s 连通全部 72 颗 GPU；直流母排，在 50 伏电压下为 132 kW 机架输送约 2,600 安培电流；带快插接头的液冷供回液分液歧管；以及连接到独立网络机架的横向扩展线缆。机架外部：冷却液分配单元、设施供电链路以及叶脊（leaf-spine）网络机架。关键数字：GB200 NVL72 约 120 kW、约 1.36 吨，GB300 NVL72 约 132 kW，Vera Rubin NVL72 约 190 至 230 kW，全液冷。](../../../assets/diagrams/08-nvl72-rack-anatomy.svg)

## 1. 机架：27 个托盘背后隐藏的四大系统

**[Q1 · 职能与失效后果]** 机架的职能是让 72 颗 GPU 像一台机器一样工作，并在约 130 kW 的功耗下保持供电与冷却。一旦某个隐藏系统失效（背板线缆、冷却液接头、电源架），[NVLink](../../../glossary.md#nvlink) 域就会降级，拖慢的是整个机架，而不只是一台服务器 [[S5007]](../../../sources/bibliography.md#s5007)[[S626]](../../../sources/bibliography.md#s626)。

机架正面是像抽屉一样堆叠的托盘；真正的工作在背面完成。[NVLink 背板](../../../glossary.md#nvlink-spine)把每个托盘盲插接入铜缆卡匣，每个交换托盘有 144 个 NVLink 端口；之所以用铜缆，是因为在约 1 米的距离上不需要耗电的光器件（[铜缆背板](../05-scale-up-nvlink-nvswitch/copper-spines-and-why-copper-wins.md)）[[S5007]](../../../sources/bibliography.md#s5007)[[S5008]](../../../sources/bibliography.md#s5008)。母排承载来自电源架的约 50 V 直流电 [[S8000]](../../../sources/bibliography.md#s8000)。带快插接头的分液歧管为 GPU、CPU 和交换芯片上的[冷板](../../../glossary.md#cold-plate)供液 [[S334]](../../../sources/bibliography.md#s334)。每个托盘都有一个接入带外管理网络的[基板管理控制器（BMC）](../../../glossary.md#bmc) [[S5007]](../../../sources/bibliography.md#s5007)。

| 机架组成（GB200/GB300） | 数量 | 关键数字 |
|---|---|---|
| 计算托盘 | 18 | 72 颗 GPU、36 颗 Grace CPU [[S8000]](../../../sources/bibliography.md#s8000) |
| NVLink 交换托盘 | 9 | 18 颗交换芯片（Vera Rubin 为 36 颗）[[S8000]](../../../sources/bibliography.md#s8000)[[S332]](../../../sources/bibliography.md#s332) |
| 电源架 | 8（DGX 配置） | 每个含 6 × 5.5 kW 电源模块，最高 33 kW [[S8000]](../../../sources/bibliography.md#s8000) |
| NVLink 铜缆 | 约 5,000 根 | 总长约 2 英里 [[S5000]](../../../sources/bibliography.md#s5000) |
| SuperNIC / DPU（GB300） | 72 / 18 | 每颗 GPU 800 Gb/s；每个托盘一颗 BlueField-3 [[S8001]](../../../sources/bibliography.md#s8001) |
| 液冷部件价值 | 按托盘 | 每个 GB300 机架约 $50K（摩根士丹利估计）[[S334]](../../../sources/bibliography.md#s334) |
| 重量 | 1 个机架 | GB200 约 1.36 吨（有报道）[[S335]](../../../sources/bibliography.md#s335) |

> [!TIP]
> **算例 —— 清点部件。** 芯片：72 颗 GPU + 36 颗 CPU + 18 颗交换芯片 + 72 颗 SuperNIC + 18 颗 DPU = 每个 GB300 机架 **216 颗主要芯片** [[S8000]](../../../sources/bibliography.md#s8000)[[S8001]](../../../sources/bibliography.md#s8001)。供电：8 个电源架 × 6 个电源模块 = **48 个电源模块**，铭牌容量 8 × 33 kW = 264 kW，对应约 132 kW 的负载，约为 2 倍的冗余余量（本资料库测算）[[S8000]](../../../sources/bibliography.md#s8000)[[S337]](../../../sources/bibliography.md#s337)。布线：约 5,000 根背板线缆 [[S5000]](../../../sources/bibliography.md#s5000)。**结论：**NVL72 更像一台小型大型机而非一台服务器，这正是机架集成与老化测试转移到专业 ODM 产线的原因。

<details>
<summary>🔧 技术细节：母排电流问题</summary>

一个 132 kW 的机架在约 50 V 电压下需要 132,000 ÷ 50 ≈ **2,640 A** 电流（本资料库测算）[[S337]](../../../sources/bibliography.md#s337)。电阻损耗与电流的平方成正比，因此兆瓦级机架需要 [800 V 直流](../../../glossary.md#hvdc-800v)（[电力与散热](power-and-cooling.md)）[[S8016]](../../../sources/bibliography.md#s8016)。

</details>

## 2. 计算托盘：5.6 kW GPU 功耗的所在

每个 1U 计算托盘承载两块超级芯片板。在 GB300 上，每块板通过 900 GB/s 的一致性 [NVLink-C2C](../../../glossary.md#nvlink-c2c) 链路，将一颗 72 核 Grace CPU（约 480 GB LPDDR5X）与两颗 Blackwell Ultra GPU（每颗 288 GB [HBM3E](../../../glossary.md#hbm3e)）配对 [[S337]](../../../sources/bibliography.md#s337)[[S129]](../../../sources/bibliography.md#s129)。托盘前部有 4 颗 ConnectX-8 [SuperNIC](../../../glossary.md#supernic)（每颗 GPU 一个 800 Gb/s 端口，用于[横向扩展](../../../glossary.md#scale-out)）和 1 颗 BlueField-3 [DPU](../../../glossary.md#dpu)，用于存储和多租户流量 [[S8001]](../../../sources/bibliography.md#s8001)。

![单个 NVL72 计算托盘俯视示意图。后沿：NVLink 连接器（4 颗 GPU × 18 条 NVLink 5 链路，每颗 GPU 以 1.8 TB/s 接入背板）、输送约 50 V 直流电的母排卡扣（4 颗 GPU × 1.4 kW = 5.6 kW 的 GPU 负载）以及液冷快插接头。中部：两块超级芯片板，每块含两颗 Blackwell Ultra GPU（288 GB HBM3E，约 1.4 kW，冷板）和一颗 Grace CPU（72 个 Arm 核心，约 480 GB LPDDR5X，900 GB/s NVLink-C2C）。前沿：4 颗 800 Gb/s 的 ConnectX-8 SuperNIC、1 颗 BlueField-3 DPU、本地 NVMe SSD 以及一个 BMC 管理端口。Vera Rubin 托盘的变化：2 颗 Vera CPU，每颗 88 核、最高 1.5 TB LPDDR5X；4 颗 Rubin GPU，每颗 288 GB HBM4、约 1.8 至 2.3 kW；NVLink 6 每颗 GPU 3.0 TB/s；ConnectX-9 每颗 GPU 1.6 Tb/s，并配 BlueField-4；托盘无线缆、无软管、无风扇，组装约需 5 分钟。](../../../assets/diagrams/08-compute-tray-anatomy.svg)

> [!TIP]
> **算例 —— 机架的电力去了哪里。** 4 颗 GPU × 约 1.4 kW = 每托盘 **5.6 kW** [[S32004]](../../../sources/bibliography.md#s32004)；× 18 个托盘 = **约 101 kW 的 GPU 功耗**，约占一个约 132 kW 的 GB300 机架的 76% [[S337]](../../../sources/bibliography.md#s337)。其余约 31 kW 用于 36 颗 CPU、18 颗交换芯片、90 颗网卡与 DPU、水泵和风扇以及电能转换损耗（本资料库测算）。**结论：**散热设计就是 GPU 设计；机架四分之三的热量来自 72 块冷板。

**Vera Rubin 对托盘的改动大于对机架的改动。** Oberon 机架框架和背板保持不变，但托盘承载 2 颗 Vera CPU（每颗 88 核、最高 1.5 TB LPDDR5X）和 4 颗 Rubin GPU；在英伟达 2026 年的规格修订后，NVLink 6 为每颗 GPU 3.0 TB/s（原为 3.6）；ConnectX-9 SuperNIC 为每颗 GPU 1.6 Tb/s，并配一颗 BlueField-4 DPU（🟡 每托盘数量为报道数据）[[S102]](../../../sources/bibliography.md#s102)[[S90006]](../../../sources/bibliography.md#s90006)[[S511]](../../../sources/bibliography.md#s511)。该托盘无线缆、无软管、无风扇 [[S301]](../../../sources/bibliography.md#s301)；英伟达称组装时间从约 2 小时降至约 5 分钟 [[S8002]](../../../sources/bibliography.md#s8002)[[S303]](../../../sources/bibliography.md#s303)。

> [!TIP]
> **算例 —— 5 分钟组装一个托盘值多少钱。** GB 系列托盘每个机架需要 18 个托盘 × 2 小时 = **36 个工时**，而 Vera Rubin 为 18 × 5 分钟 = **1.5 小时**（英伟达的说法）[[S8002]](../../../sources/bibliography.md#s8002)。1,000 个机架可节省约 34,500 个工时；内部线缆更少也意味着老化测试中的故障更少；SemiAnalysis 预计 Rubin 上量更快，部分原因正在于此 [[S626]](../../../sources/bibliography.md#s626)。**结论：**可制造性如今已成为一项竞争性规格。

<details>
<summary>🔧 技术细节：交换芯片为何翻倍</summary>

NVLink 6 将每颗 GPU 的带宽大约翻倍，因此机架需要 36 颗交换芯片（每个交换托盘 4 颗），而不是 18 颗 [[S332]](../../../sources/bibliography.md#s332)。按修订后的每颗 GPU 3.0 TB/s 计，机架的全交换（all-to-all）带宽约为 72 × 3.0 ≈ 216 TB/s，而发布时公布的是 260 TB/s（本资料库测算）[[S90003]](../../../sources/bibliography.md#s90003)[[S90006]](../../../sources/bibliography.md#s90006)。

</details>

## 3. 重量、功耗与可维护性

一个 GB200 机架重约 1.36 吨，与一辆汽车相当，因此必须先核查楼板承重和运输路线 [[S335]](../../../sources/bibliography.md#s335)。功耗逐代攀升：约 120 kW（GB200）、约 132 kW（GB300；各方估计为 120–140 kW），再到 Vera Rubin 的约 190 kW（Max-Q）至约 230 kW（Max-P）功耗档位（有报道）[[S336]](../../../sources/bibliography.md#s336)[[S337]](../../../sources/bibliography.md#s337)[[S303]](../../../sources/bibliography.md#s303)。AMD 的双宽 Helios 机架（72 颗 MI455X）估计约 225–245 kW [[S344]](../../../sources/bibliography.md#s344)[[S346]](../../../sources/bibliography.md#s346)。

> [!TIP]
> **算例 —— 一个机架闲置的代价。** SemiAnalysis 估算一颗 GB300 GPU 的持有成本约为每小时 $2.31，租赁价格约为每小时 $5.00 [[S622]](../../../sources/bibliography.md#s622)。一个机架停机一天，损失 72 × 24 × $2.31 ≈ **$4,000 的持有成本**，或 ≈ **$8,600 的租赁收入**（本资料库测算）。**结论：**在机群规模下，可靠性以及托盘、卡匣和快插接头的快速更换都价值不菲。

> [!WARNING]
> **🐻 看空观点：**72 颗 GPU 的 NVLink 域是单一故障域。一次冷却液泄漏或一个有缺陷的背板卡匣，就可能让价值约 $4M 的硬件闲置直至修复；SemiAnalysis 指出，GB200 铜缆背板在上量期间“面临诸多可靠性挑战”[[S626]](../../../sources/bibliography.md#s626)。由 8 GPU 节点构建的横向扩展设计（TPU 立方体、Trainium UltraServer、[HGX](../../../glossary.md#hgx)）在单个节点故障时损失更小。

## 🎯 企业发展视角

1. **互连与供电硬件是机架的新卡脖子环节。** 背板卡匣、母排、快插接头和冷板都是不起眼但认证门槛很高的部件；哪些供应商已被设计进 Vera Rubin 和 Kyber？
2. **可维护性正在成为护城河。** 托盘组装与老化测试时间决定了新一代产品的上量速度 [[S8002]](../../../sources/bibliography.md#s8002)[[S626]](../../../sources/bibliography.md#s626)。进入机架级市场的竞争者必须解决制造问题，而不仅是芯片问题。
3. **高通（Qualcomm）的问题（仅基于公开信息）：** AI200/AI250 机架采用 [PCIe](../../../glossary.md#pcie) [纵向扩展](../../../glossary.md#scale-up)和以太网横向扩展，功耗约 160 kW [[S173]](../../../sources/bibliography.md#s173)；若在 CPU 方面加入 [NVLink Fusion](../../../glossary.md#nvlink-fusion) [[S90031]](../../../sources/bibliography.md#s90031)，或在 MGX 式机架上开展合作，能否缩短打造一款经过验证的机架的路径？

## 📚 来源（Sources）

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S102**](../../../sources/bibliography.md#s102) NVIDIA, *NVIDIA DGX Vera Rubin NVL72*, 2026. [Link](https://www.nvidia.com/en-us/data-center/dgx-vera-rubin-nvl72/)
- [**S129**](../../../sources/bibliography.md#s129) NVIDIA, *NVIDIA Grace CPU*, 2023. [Link](https://www.nvidia.com/en-us/data-center/grace-cpu/)
- [**S173**](../../../sources/bibliography.md#s173) Qualcomm, *Qualcomm Unveils AI200 and AI250 - Redefining Rack-Scale Data Center Inference*, 2025-10-27. [Link](https://www.qualcomm.com/news/releases/2025/10/qualcomm-unveils-ai200-and-ai250-redefining-rack-scale-data-cent)
- [**S301**](../../../sources/bibliography.md#s301) StorageReview, *NVIDIA launches Vera Rubin architecture at CES 2026: the VR NVL72 rack*, 2026-01. [Link](https://www.storagereview.com/news/nvidia-launches-vera-rubin-architecture-at-ces-2026-the-vr-nvl72-rack)
- [**S303**](../../../sources/bibliography.md#s303) Commercial Times (ctee.com.tw), *Vera Rubin NVL72 Max-Q / Max-P rack power (Commercial Times report)*, 2026-01-07. [Link](https://www.ctee.com.tw/news/20260107701081-430704)
- [**S332**](../../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S334**](../../../sources/bibliography.md#s334) Tom's Hardware, *Cooling system for a single Nvidia Blackwell Ultra NVL72 rack costs $50,000 - set to increase to $56,000 with next-generation NVL144 racks*, 2025-09. [Link](https://www.tomshardware.com/pc-components/cooling/cooling-system-for-a-single-nvidia-blackwell-ultra-nvl72-rack-costs-a-staggering-usd50-000-set-to-increase-to-usd56-000-with-next-generation-nvl144-racks)
- [**S335**](../../../sources/bibliography.md#s335) Spheron, *NVIDIA GB200 NVL72 guide*, 2026. [Link](https://www.spheron.network/blog/nvidia-gb200-nvl72-guide/)
- [**S336**](../../../sources/bibliography.md#s336) eeNews Europe, *Nvidia offers 120kW liquid-cooled Blackwell rack as industry standard*, 2024-10. [Link](https://www.eenewseurope.com/en/nvidia-offers-120kw-liquid-cooled-blackwell-rack-as-industry-standard)
- [**S337**](../../../sources/bibliography.md#s337) Spheron, *NVIDIA GB300 (rental and specifications)*, 2026. [Link](https://spheron.network/gpu-rental/gb300/)
- [**S344**](../../../sources/bibliography.md#s344) AMD, *AMD Helios rack-scale AI infrastructure (product page)*, 2026. [Link](https://www.amd.com/ja/products/rackscale-solutions/helios.html)
- [**S346**](../../../sources/bibliography.md#s346) Kad8, *AMD Helios AI rack: MI455X, Zen 6 EPYC and Pensando*, 2026. [Link](https://www.kad8.com/server/amd-helios-ai-rack-mi455x-zen-6-epyc-and-pensando/)
- [**S396**](../../../sources/bibliography.md#s396) NVIDIA Newsroom, *NVIDIA Blackwell platform arrives to power a new era of computing*, 2024-03-18. [Link](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing)
- [**S511**](../../../sources/bibliography.md#s511) Tom's Hardware, *Examining Nvidia's 60 exaflop Vera Rubin POD — how seven chips underpin company's 40 rack AI factory supercomputer*, 2026-03. [Link](https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidias-seven-chip-vera-rubin-platforms-turns-the-data-center-into-an-ai-factory)
- [**S622**](../../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S626**](../../../sources/bibliography.md#s626) SemiAnalysis, *Vera Rubin NVL72 vs GB200 NVL72? Inference TCO & Architecture Analysis*, 2026-07-23. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/vera-rubin-nvl72-vs-gb200-nvl72-inference.mdx)
- [**S5000**](../../../sources/bibliography.md#s5000) SemiAnalysis, *Nvidia's Optical Boogeyman - NVL72, InfiniBand Scale Out, 800G & 1.6T Ramp*, 2024-03. [Link](https://newsletter.semianalysis.com/p/nvidias-optical-boogeyman-nvl72-infiniband)
- [**S5001**](../../../sources/bibliography.md#s5001) SiliconANGLE, *Nvidia aims to boost Blackwell by donating platform design to the Open Compute Project*, 2024-10-15. [Link](https://siliconangle.com/2024/10/15/nvidia-aims-boost-blackwell-donating-platform-design-open-compute-project)
- [**S5007**](../../../sources/bibliography.md#s5007) NVIDIA Docs, *DGX SuperPOD reference architecture (GB200): key components of the DGX SuperPOD*, 2025. [Link](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-gb200/latest/dgx-superpod-components.html)
- [**S5008**](../../../sources/bibliography.md#s5008) NVIDIA Docs, *NVIDIA Mission Control: NVLink information (nvlinkinfo)*, 2025. [Link](https://docs.nvidia.com/base-command-manager/product-manuals/nvidia-mission-control/nvlinkinfo)
- [**S8000**](../../../sources/bibliography.md#s8000) NVIDIA Docs, *NVIDIA DGX GB200 User Guide: hardware overview*, 2025. [Link](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html)
- [**S8001**](../../../sources/bibliography.md#s8001) NVIDIA Docs, *NVIDIA Enterprise Reference Architecture: NVL72 AI factory - system hardware and components*, 2025. [Link](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html)
- [**S8002**](../../../sources/bibliography.md#s8002) COMPUTEX Taipei (TAITRA), *NVIDIA Vera Rubin NVL72 (COMPUTEX 2026 Best Choice Award entry)*, 2026-05. [Link](https://bcaward.computex.biz/download/2026/winnerPdf/10905.pdf)
- [**S8016**](../../../sources/bibliography.md#s8016) NVIDIA Technical Blog, *NVIDIA 800 V HVDC Architecture Will Power the Next Generation of AI Factories*, 2025-05-20. [Link](https://developer.nvidia.com/blog/nvidia-800-v-hvdc-architecture-will-power-the-next-generation-of-ai-factories/)
- [**S32004**](../../../sources/bibliography.md#s32004) NVIDIA, *NVIDIA GB300 NVL72 / Blackwell Ultra (product page)*, 2025-03. [Link](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)
- [**S90003**](../../../sources/bibliography.md#s90003) eWeek, *Everything Nvidia Just Announced at GTC 2026: 7 Chips, 5 Racks, 1 Giant Bet on Agentic AI*, 2026-03-17. [Link](https://www.eweek.com/news/nvidia-gtc-2026-ai-inference-vera-rubin-neuron/)
- [**S90006**](../../../sources/bibliography.md#s90006) TweakTown, *Nvidia cuts Vera Rubin's memory bandwidth by up to 26% and AMD's Helios now leads in memory bandwidth*, 2026-10. [Link](https://www.tweaktown.com/news/114304/nvidia-cuts-vera-rubins-memory-bandwidth-by-up-to-26-percent-and-amds-helios-now-leads-in-memory-bandwidth/index.html)
- [**S90031**](../../../sources/bibliography.md#s90031) ServeTheHome, *NVIDIA announces NVLink Fusion bringing NVLink to third-party CPUs and accelerators*, 2025-05-19. [Link](https://www.servethehome.com/nvidia-announces-nvlink-fusion-bringing-nvlink-to-third-party-cpus-and-accelerators/nvlink-fusion-partners/)
