# Anatomy of an NVL72 rack

<sub>Layer 08 · Systems, racks and AI factories · ~9 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **One rack, one computer.** An [NVL72](../../glossary.md#nvl72) rack holds 18 1U [compute trays](../../glossary.md#compute-tray) (2 CPUs + 4 GPUs each = 72 GPUs, 36 CPUs) and 9 [NVLink switch trays](../../glossary.md#nvlink-switch-tray), all wired to every other GPU through a copper backplane [[S8000]](../../sources/bibliography.md#s8000)[[S396]](../../sources/bibliography.md#s396).
- **The spine is the trick:** ~5,000 copper cables (~2 miles) give each GPU 1.8 TB/s to all 72 (~130 TB/s in total), and avoiding optics saves ~20 kW of transceivers per rack [[S5000]](../../sources/bibliography.md#s5000)[[S5001]](../../sources/bibliography.md#s5001).
- **It is a power and plumbing product:** eight 33 kW [power shelves](../../glossary.md#power-shelf) feed a ~50 V DC [busbar](../../glossary.md#busbar); cold plates on every GPU and CPU connect to rack manifolds and a [CDU](../../glossary.md#cdu) [[S8000]](../../sources/bibliography.md#s8000)[[S5007]](../../sources/bibliography.md#s5007).
- **Size:** ~120 kW (GB200), ~132 kW (GB300), ~190–230 kW (Vera Rubin, reported); ~1.36 t (GB200) [[S336]](../../sources/bibliography.md#s336)[[S337]](../../sources/bibliography.md#s337)[[S303]](../../sources/bibliography.md#s303)[[S335]](../../sources/bibliography.md#s335).
- **Vera Rubin redesigned the tray:** cable-free, hose-free and fanless, assembled in ~5 minutes instead of ~2 hours (NVIDIA claim), with switch chips doubled from 18 to 36 per rack [[S8002]](../../sources/bibliography.md#s8002)[[S301]](../../sources/bibliography.md#s301)[[S332]](../../sources/bibliography.md#s332).
- **Weakness:** density concentrates risk. Early GB200 racks hit copper-backplane reliability problems during ramp, and one rack is now a ~$4–8M unit that must be serviced as a whole (Est.) [[S626]](../../sources/bibliography.md#s626)[[S332]](../../sources/bibliography.md#s332).

![Diagram of an NVL72 rack. Front view top to bottom: out-of-band management switch, top group of power shelves (each six 5.5 kW supplies, up to 33 kW, AC in and about 50 V DC out), compute trays 1 to 10, nine NVLink switch trays with two switch chips each (18 per rack, 36 on Vera Rubin), compute trays 11 to 18 (72 GPUs and 36 CPUs in total) and a bottom group of power shelves, eight in NVIDIA's DGX configuration. Rear: the NVLink copper spine of about 5,000 cables giving each GPU 1.8 TB/s to all 72, a DC busbar carrying about 2,600 amps at 50 volts for a 132 kW rack, liquid supply and return manifolds with quick-disconnects, and scale-out cables to separate network racks. Outside: coolant distribution unit, facility power chain and leaf-spine network racks. Key numbers: GB200 NVL72 about 120 kW and 1.36 tonnes, GB300 NVL72 about 132 kW, Vera Rubin NVL72 about 190 to 230 kW, fully liquid-cooled.](../../assets/diagrams/08-nvl72-rack-anatomy.svg)

## 1. The rack: four systems hidden behind 27 trays

**[Q1 · Job & failure mode]** The rack's job is to make 72 GPUs act as one machine and keep them powered and cool at ~130 kW. If a hidden system fails (spine cable, coolant connector, power shelf), the NVLink domain degrades and the whole rack slows, not one server [[S5007]](../../sources/bibliography.md#s5007)[[S626]](../../sources/bibliography.md#s626).

The front is trays stacked like drawers; the work happens at the back. The [NVLink spine](../../glossary.md#nvlink-spine) takes every tray blind into copper cable cartridges, 144 NVLink ports per switch tray, copper because at ~1 metre it needs no power-hungry optics ([copper spines](../05-scale-up-nvlink-nvswitch/copper-spines-and-why-copper-wins.md)) [[S5007]](../../sources/bibliography.md#s5007)[[S5008]](../../sources/bibliography.md#s5008). The busbar carries ~50 V DC from the power shelves [[S8000]](../../sources/bibliography.md#s8000). Manifolds with quick-disconnects feed [cold plates](../../glossary.md#cold-plate) on GPUs, CPUs and switch chips [[S334]](../../sources/bibliography.md#s334). Each tray has a [BMC](../../glossary.md#bmc) on an out-of-band management network [[S5007]](../../sources/bibliography.md#s5007).

| Rack element (GB200/GB300) | Count | Key numbers |
|---|---|---|
| Compute trays | 18 | 72 GPUs, 36 Grace CPUs [[S8000]](../../sources/bibliography.md#s8000) |
| NVLink switch trays | 9 | 18 switch chips (36 on Vera Rubin) [[S8000]](../../sources/bibliography.md#s8000)[[S332]](../../sources/bibliography.md#s332) |
| Power shelves | 8 (DGX configuration) | 6 × 5.5 kW supplies, up to 33 kW each [[S8000]](../../sources/bibliography.md#s8000) |
| NVLink copper cables | ~5,000 | ~2 miles in total [[S5000]](../../sources/bibliography.md#s5000) |
| SuperNICs / DPUs (GB300) | 72 / 18 | 800 Gb/s per GPU; one BlueField-3 per tray [[S8001]](../../sources/bibliography.md#s8001) |
| Liquid-cooling content | per tray | ~$50K per GB300 rack (Morgan Stanley Est.) [[S334]](../../sources/bibliography.md#s334) |
| Weight | 1 rack | ~1.36 t for GB200 (reported) [[S335]](../../sources/bibliography.md#s335) |

> [!TIP]
> **Worked example — counting the parts.** Silicon: 72 GPUs + 36 CPUs + 18 switch chips + 72 SuperNICs + 18 DPUs = **216 major chips** per GB300 rack [[S8000]](../../sources/bibliography.md#s8000)[[S8001]](../../sources/bibliography.md#s8001). Power: 8 shelves × 6 supplies = **48 power supplies** with 8 × 33 kW = 264 kW of nameplate capacity for a ~132 kW load, roughly 2× headroom for redundancy (repo arithmetic) [[S8000]](../../sources/bibliography.md#s8000)[[S337]](../../sources/bibliography.md#s337). Wiring: ~5,000 spine cables [[S5000]](../../sources/bibliography.md#s5000). **Conclusion:** an NVL72 is closer to a small mainframe than a server, which is why rack integration and burn-in moved to specialist ODM lines.

<details>
<summary>🔧 Under the hood: the busbar current problem</summary>

A 132 kW rack at ~50 V draws 132,000 ÷ 50 ≈ **2,640 A** (repo arithmetic) [[S337]](../../sources/bibliography.md#s337). Resistive loss scales with current squared, so megawatt racks need [800 V DC](../../glossary.md#hvdc-800v) ([power and cooling](power-and-cooling.md)) [[S8016]](../../sources/bibliography.md#s8016).

</details>

## 2. The compute tray: where 5.6 kW of GPUs live

Each 1U compute tray carries two superchip boards. On GB300 a board pairs one 72-core Grace CPU (~480 GB LPDDR5X) with two Blackwell Ultra GPUs (288 GB HBM3E each) over a 900 GB/s coherent [NVLink-C2C](../../glossary.md#nvlink-c2c) link [[S337]](../../sources/bibliography.md#s337)[[S129]](../../sources/bibliography.md#s129). The tray's front holds four ConnectX-8 [SuperNICs](../../glossary.md#supernic) (one 800 Gb/s port per GPU for scale-out) and one BlueField-3 [DPU](../../glossary.md#dpu) for storage and tenancy traffic [[S8001]](../../sources/bibliography.md#s8001).

![Diagram of one NVL72 compute tray, top view. Rear edge: NVLink connectors (4 GPUs times 18 NVLink 5 links, 1.8 TB/s per GPU into the spine), busbar clip delivering about 50 V DC (4 GPUs times 1.4 kW = 5.6 kW of GPU load) and liquid quick-disconnects. Middle: two superchip boards, each with two Blackwell Ultra GPUs (288 GB HBM3E, about 1.4 kW, cold plate) and one Grace CPU (72 Arm cores, about 480 GB LPDDR5X, 900 GB/s NVLink-C2C). Front edge: four ConnectX-8 SuperNICs at 800 Gb/s, one BlueField-3 DPU, local NVMe SSDs and a BMC management port. Vera Rubin tray changes: 2 Vera CPUs with 88 cores and up to 1.5 TB LPDDR5X each, 4 Rubin GPUs with 288 GB HBM4 at about 1.8 to 2.3 kW, NVLink 6 at 3.0 TB/s per GPU, ConnectX-9 at 1.6 Tb/s per GPU and BlueField-4, and a cable-free, hose-free, fanless tray assembled in about 5 minutes.](../../assets/diagrams/08-compute-tray-anatomy.svg)

> [!TIP]
> **Worked example — where the rack's power goes.** Four GPUs at ~1.4 kW = **5.6 kW** per tray [[S32004]](../../sources/bibliography.md#s32004); × 18 trays = **~101 kW of GPU power**, ~76% of a ~132 kW GB300 rack [[S337]](../../sources/bibliography.md#s337). The other ~31 kW covers 36 CPUs, 18 switch chips, 90 NICs and DPUs, pumps and fans, and conversion losses (repo arithmetic). **Conclusion:** cooling design is GPU design; three-quarters of the rack's heat comes off 72 cold plates.

**Vera Rubin changes the tray more than the rack.** The Oberon frame and spine stay, but the tray carries 2 Vera CPUs (88 cores, up to 1.5 TB LPDDR5X each) and 4 Rubin GPUs, NVLink 6 at 3.0 TB/s per GPU after NVIDIA's 2026 spec revision (from 3.6) and ConnectX-9 SuperNICs at 1.6 Tb/s per GPU with a BlueField-4 DPU (🟡 per-tray counts reported) [[S102]](../../sources/bibliography.md#s102)[[S90006]](../../sources/bibliography.md#s90006)[[S511]](../../sources/bibliography.md#s511). The tray is cable-free, hose-free and fanless [[S301]](../../sources/bibliography.md#s301); NVIDIA claims assembly drops from ~2 hours to ~5 minutes [[S8002]](../../sources/bibliography.md#s8002)[[S303]](../../sources/bibliography.md#s303).

> [!TIP]
> **Worked example — what a 5-minute tray is worth.** 18 trays × 2 hours = **36 labour-hours** per rack on GB-class trays versus 18 × 5 minutes = **1.5 hours** on Vera Rubin (NVIDIA claim) [[S8002]](../../sources/bibliography.md#s8002). Across 1,000 racks that saves ~34,500 labour-hours, and fewer internal cables mean fewer burn-in failures; SemiAnalysis expects a faster Rubin ramp partly for this reason [[S626]](../../sources/bibliography.md#s626). **Conclusion:** manufacturability is now a competitive spec.

<details>
<summary>🔧 Under the hood: why the switch chips doubled</summary>

NVLink 6 roughly doubles per-GPU bandwidth, so the rack needs 36 switch chips (four per tray) instead of 18 [[S332]](../../sources/bibliography.md#s332). At the revised 3.0 TB/s per GPU, rack all-to-all bandwidth is ~72 × 3.0 ≈ 216 TB/s versus the 260 TB/s quoted at launch (repo arithmetic) [[S90003]](../../sources/bibliography.md#s90003)[[S90006]](../../sources/bibliography.md#s90006).

</details>

## 3. Weight, power and serviceability

At ~1.36 t a GB200 rack weighs about as much as a car, so floors and delivery routes must be checked first [[S335]](../../sources/bibliography.md#s335). Power climbs each generation: ~120 kW (GB200), ~132 kW (GB300; estimates 120–140 kW), then ~190 kW (Max-Q) to ~230 kW (Max-P) power profiles for Vera Rubin (reported) [[S336]](../../sources/bibliography.md#s336)[[S337]](../../sources/bibliography.md#s337)[[S303]](../../sources/bibliography.md#s303). AMD's double-wide Helios rack (72 MI455X) is estimated at ~225–245 kW [[S344]](../../sources/bibliography.md#s344)[[S346]](../../sources/bibliography.md#s346).

> [!TIP]
> **Worked example — what one idle rack costs.** SemiAnalysis puts a GB300 GPU at ~$2.31 per hour to own and ~$5.00 to rent [[S622]](../../sources/bibliography.md#s622). A rack down for a day loses 72 × 24 × $2.31 ≈ **$4,000 of owner cost** or ≈ **$8,600 of rental revenue** (repo arithmetic). **Conclusion:** reliability and fast swaps of trays, cartridges and quick-disconnects are worth real money at fleet scale.

> [!WARNING]
> **🐻 Bear view:** a 72-GPU NVLink domain is a single failure domain. A coolant leak or a bad spine cartridge can idle ~$4M of hardware until fixed, and SemiAnalysis notes the GB200 copper backplane "faced many reliability challenges" during its ramp [[S626]](../../sources/bibliography.md#s626). Scale-out designs built from 8-GPU nodes (TPU cubes, Trainium UltraServers, HGX) lose less when one node fails.

## 🎯 Corp Dev Lens

1. **Interconnect and power hardware are the rack's new chokepoints.** The spine cartridges, busbars, quick-disconnects and cold plates are low-glamour parts with high qualification barriers; which suppliers are designed into Vera Rubin and Kyber?
2. **Serviceability is becoming a moat.** Tray assembly and burn-in time decide how fast a new generation ramps [[S8002]](../../sources/bibliography.md#s8002)[[S626]](../../sources/bibliography.md#s626). Rivals entering rack-scale must solve manufacturing, not just silicon.
3. **Qualcomm question (public information only):** AI200/AI250 racks use PCIe scale-up and Ethernet scale-out at ~160 kW [[S173]](../../sources/bibliography.md#s173); would joining [NVLink Fusion](../../glossary.md#nvlink-fusion) for CPUs [[S90031]](../../sources/bibliography.md#s90031) or partnering on an MGX-style rack shorten the path to a validated rack?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S102**](../../sources/bibliography.md#s102) NVIDIA, *NVIDIA DGX Vera Rubin NVL72*, 2026. [Link](https://www.nvidia.com/en-us/data-center/dgx-vera-rubin-nvl72/)
- [**S129**](../../sources/bibliography.md#s129) NVIDIA, *NVIDIA Grace CPU*, 2023. [Link](https://www.nvidia.com/en-us/data-center/grace-cpu/)
- [**S173**](../../sources/bibliography.md#s173) Qualcomm, *Qualcomm Unveils AI200 and AI250 - Redefining Rack-Scale Data Center Inference*, 2025-10-27. [Link](https://www.qualcomm.com/news/releases/2025/10/qualcomm-unveils-ai200-and-ai250-redefining-rack-scale-data-cent)
- [**S301**](../../sources/bibliography.md#s301) StorageReview, *NVIDIA launches Vera Rubin architecture at CES 2026: the VR NVL72 rack*, 2026-01. [Link](https://www.storagereview.com/news/nvidia-launches-vera-rubin-architecture-at-ces-2026-the-vr-nvl72-rack)
- [**S303**](../../sources/bibliography.md#s303) Commercial Times (ctee.com.tw), *Vera Rubin NVL72 Max-Q / Max-P rack power (Commercial Times report)*, 2026-01-07. [Link](https://www.ctee.com.tw/news/20260107701081-430704)
- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S334**](../../sources/bibliography.md#s334) Tom's Hardware, *Cooling system for a single Nvidia Blackwell Ultra NVL72 rack costs $50,000 - set to increase to $56,000 with next-generation NVL144 racks*, 2025-09. [Link](https://www.tomshardware.com/pc-components/cooling/cooling-system-for-a-single-nvidia-blackwell-ultra-nvl72-rack-costs-a-staggering-usd50-000-set-to-increase-to-usd56-000-with-next-generation-nvl144-racks)
- [**S335**](../../sources/bibliography.md#s335) Spheron, *NVIDIA GB200 NVL72 guide*, 2026. [Link](https://www.spheron.network/blog/nvidia-gb200-nvl72-guide/)
- [**S336**](../../sources/bibliography.md#s336) eeNews Europe, *Nvidia offers 120kW liquid-cooled Blackwell rack as industry standard*, 2024-10. [Link](https://www.eenewseurope.com/en/nvidia-offers-120kw-liquid-cooled-blackwell-rack-as-industry-standard)
- [**S337**](../../sources/bibliography.md#s337) Spheron, *NVIDIA GB300 (rental and specifications)*, 2026. [Link](https://spheron.network/gpu-rental/gb300/)
- [**S344**](../../sources/bibliography.md#s344) AMD, *AMD Helios rack-scale AI infrastructure (product page)*, 2026. [Link](https://www.amd.com/ja/products/rackscale-solutions/helios.html)
- [**S346**](../../sources/bibliography.md#s346) Kad8, *AMD Helios AI rack: MI455X, Zen 6 EPYC and Pensando*, 2026. [Link](https://www.kad8.com/server/amd-helios-ai-rack-mi455x-zen-6-epyc-and-pensando/)
- [**S396**](../../sources/bibliography.md#s396) NVIDIA Newsroom, *NVIDIA Blackwell platform arrives to power a new era of computing*, 2024-03-18. [Link](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing)
- [**S511**](../../sources/bibliography.md#s511) Tom's Hardware, *Examining Nvidia's 60 exaflop Vera Rubin POD — how seven chips underpin company's 40 rack AI factory supercomputer*, 2026-03. [Link](https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidias-seven-chip-vera-rubin-platforms-turns-the-data-center-into-an-ai-factory)
- [**S622**](../../sources/bibliography.md#s622) SemiAnalysis (InferenceX-app repository), *InferenceX hardware registry: TCO per GPU-hour by SKU (SemiAnalysis July 2026 pricing surveys and AI Cloud TCO Model)*, 2026-07. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/constants/src/gpu-keys.ts)
- [**S626**](../../sources/bibliography.md#s626) SemiAnalysis, *Vera Rubin NVL72 vs GB200 NVL72? Inference TCO & Architecture Analysis*, 2026-07-23. [Link](https://github.com/SemiAnalysisAI/InferenceX-app/blob/main/packages/app/content/blog/vera-rubin-nvl72-vs-gb200-nvl72-inference.mdx)
- [**S5000**](../../sources/bibliography.md#s5000) SemiAnalysis, *Nvidia's Optical Boogeyman - NVL72, InfiniBand Scale Out, 800G & 1.6T Ramp*, 2024-03. [Link](https://newsletter.semianalysis.com/p/nvidias-optical-boogeyman-nvl72-infiniband)
- [**S5001**](../../sources/bibliography.md#s5001) SiliconANGLE, *Nvidia aims to boost Blackwell by donating platform design to the Open Compute Project*, 2024-10-15. [Link](https://siliconangle.com/2024/10/15/nvidia-aims-boost-blackwell-donating-platform-design-open-compute-project)
- [**S5007**](../../sources/bibliography.md#s5007) NVIDIA Docs, *DGX SuperPOD reference architecture (GB200): key components of the DGX SuperPOD*, 2025. [Link](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-gb200/latest/dgx-superpod-components.html)
- [**S5008**](../../sources/bibliography.md#s5008) NVIDIA Docs, *NVIDIA Mission Control: NVLink information (nvlinkinfo)*, 2025. [Link](https://docs.nvidia.com/base-command-manager/product-manuals/nvidia-mission-control/nvlinkinfo)
- [**S8000**](../../sources/bibliography.md#s8000) NVIDIA Docs, *NVIDIA DGX GB200 User Guide: hardware overview*, 2025. [Link](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html)
- [**S8001**](../../sources/bibliography.md#s8001) NVIDIA Docs, *NVIDIA Enterprise Reference Architecture: NVL72 AI factory - system hardware and components*, 2025. [Link](https://docs.nvidia.com/enterprise-reference-architectures/nvl72-ai-factory/latest/components.html)
- [**S8002**](../../sources/bibliography.md#s8002) COMPUTEX Taipei (TAITRA), *NVIDIA Vera Rubin NVL72 (COMPUTEX 2026 Best Choice Award entry)*, 2026-05. [Link](https://bcaward.computex.biz/download/2026/winnerPdf/10905.pdf)
- [**S8016**](../../sources/bibliography.md#s8016) NVIDIA Technical Blog, *NVIDIA 800 V HVDC Architecture Will Power the Next Generation of AI Factories*, 2025-05-20. [Link](https://developer.nvidia.com/blog/nvidia-800-v-hvdc-architecture-will-power-the-next-generation-of-ai-factories/)
- [**S32004**](../../sources/bibliography.md#s32004) NVIDIA, *NVIDIA GB300 NVL72 / Blackwell Ultra (product page)*, 2025-03. [Link](https://www.nvidia.com/en-us/data-center/gb300-nvl72/)
- [**S90003**](../../sources/bibliography.md#s90003) eWeek, *Everything Nvidia Just Announced at GTC 2026: 7 Chips, 5 Racks, 1 Giant Bet on Agentic AI*, 2026-03-17. [Link](https://www.eweek.com/news/nvidia-gtc-2026-ai-inference-vera-rubin-neuron/)
- [**S90006**](../../sources/bibliography.md#s90006) TweakTown, *Nvidia cuts Vera Rubin's memory bandwidth by up to 26% and AMD's Helios now leads in memory bandwidth*, 2026-10. [Link](https://www.tweaktown.com/news/114304/nvidia-cuts-vera-rubins-memory-bandwidth-by-up-to-26-percent-and-amds-helios-now-leads-in-memory-bandwidth/index.html)
- [**S90031**](../../sources/bibliography.md#s90031) ServeTheHome, *NVIDIA announces NVLink Fusion bringing NVLink to third-party CPUs and accelerators*, 2025-05-19. [Link](https://www.servethehome.com/nvidia-announces-nvlink-fusion-bringing-nvlink-to-third-party-cpus-and-accelerators/nvlink-fusion-partners/)
