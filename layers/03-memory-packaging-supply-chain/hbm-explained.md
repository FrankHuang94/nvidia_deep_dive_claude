# HBM explained

<sub>Layer 03 · Memory, packaging and supply chain · ~9 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **[HBM](../../glossary.md#hbm) is DRAM built as a skyscraper next to the GPU.** 8–16 thinned DRAM dies sit on a base die, wired vertically by [through-silicon vias](../../glossary.md#through-silicon-via), and talk to the GPU over 1,024 data wires ([HBM3E](../../glossary.md#hbm3e)) or 2,048 ([HBM4](../../glossary.md#hbm4)) [[S368]](../../sources/bibliography.md#s368)[[S369]](../../sources/bibliography.md#s369).
- **[Q3 · Generational progress]** Per-stack peak bandwidth rose 16×, from 128 GB/s (2013) to 2,048 GB/s (JEDEC HBM4) [[S370]](../../sources/bibliography.md#s370)[[S369]](../../sources/bibliography.md#s369). Per GPU, P100 → Rubin went 0.73 → 19.2 TB/s (26×) and 16 → 288 GB (18×), with 16 stacks planned for Rubin Ultra [[S125]](../../sources/bibliography.md#s125)[[S33007]](../../sources/bibliography.md#s33007)[[S35041]](../../sources/bibliography.md#s35041).
- **HBM is costly because it is wasteful to make.** HBM3E needs ~3× DDR5's wafer area per GB (Micron) [[S3006]](../../sources/bibliography.md#s3006), and one bad die scraps a whole stack. HBM was ~45% of a B200's build cost (Est.) [[S35020]](../../sources/bibliography.md#s35020).
- 🟡 **HBM4 moves the base die to a logic process, often at TSMC** [[S3011]](../../sources/bibliography.md#s3011)[[S3007]](../../sources/bibliography.md#s3007), shifting part of the value pool to the foundry and the GPU designer.
- 🟡 **Three suppliers, one leader.** SK hynix is expected to supply over half of NVIDIA's 2026 HBM; Samsung joined it on the Rubin HBM4 list [[S90039]](../../sources/bibliography.md#s90039)[[S90041]](../../sources/bibliography.md#s90041).

![Original schematic cross-section comparing an HBM3E and an HBM4 stack: each has a mold cap, 12 DRAM core dies joined by through-silicon vias and micro-bumps, and a base die. HBM3E's base die is made in the DRAM maker's process with 1,024 data wires at about 9.2 to 9.8 Gb/s, about 1.2 TB/s per stack. HBM4's base die moves to a logic process such as TSMC 12 nm, with 2,048 wires at about 9.4 Gb/s in Rubin, about 2.4 TB/s per stack, and an optional custom base die from HBM4E. Stacks connect to the GPU through a silicon interposer or CoWoS-L bridge only 1 to 2 mm away; eight stacks give 8 TB/s on B200 and 19.2 TB/s on Rubin. A footer explains why HBM is expensive: about 3 times DDR5's wafer area per GB, stack-level yield loss and known-good-die testing.](../../assets/diagrams/03-hbm-stack-cross-section.svg)

## What HBM is, mechanically

**Analogy.** Server DDR5 is a suburb: chips spread across DIMMs, joined to the CPU by a 64-bit road per channel. HBM is a skyscraper next door: dies stacked a dozen high, lift shafts (TSVs) through every floor, and a 1,024- or 2,048-lane bridge to the GPU a millimetre or two away.

- **Core dies** hold the bits. A 24 Gb die stores 3 GB, so a 12-high stack holds 36 GB; JEDEC HBM4 allows 16-high stacks of 32 Gb dies, or 64 GB [[S369]](../../sources/bibliography.md#s369). [Stack height](../../glossary.md#stack-height) sets capacity.
- **TSVs and [micro-bumps](../../glossary.md#microbump)** carry data and power between layers. [Hybrid bonding](../../glossary.md#hybrid-bonding), a bumpless copper-to-copper join, is being explored for 16-high stacks.
- **The [base die](../../glossary.md#hbm-base-die)** holds the interface and test logic. The [interposer](../../glossary.md#interposer) carries its thousands of wires to the GPU, which is why HBM must be co-packaged (see [CoWoS](cowos-and-advanced-packaging.md)).

Bandwidth per stack = [pin speed](../../glossary.md#pin-speed) × bus width ÷ 8.

> [!TIP]
> **Worked example — one HBM4 stack vs DDR5 channels.** A DDR5-6400 channel moves 6.4 Gb/s × 64 ÷ 8 = 51.2 GB/s [[S179]](../../sources/bibliography.md#s179). Each Rubin stack moves 19.2 TB/s ÷ 8 = 2,400 GB/s, or ~47 DDR5 channels, implying ~9.4 Gb/s per pin on 2,048 wires (the 22 TB/s launch spec implied ~10.7) [[S33006]](../../sources/bibliography.md#s33006)[[S33007]](../../sources/bibliography.md#s33007)[[S90006]](../../sources/bibliography.md#s90006). **Business reading:** the wider bus, not faster pins, delivered HBM4's gain; 🔴 per one analyst, NVIDIA's push for 10–11 Gb/s bins [[S90040]](../../sources/bibliography.md#s90040) ran into what suppliers ship in volume [[S90006]](../../sources/bibliography.md#s90006).

## Generations: HBM2E → HBM4E

| Generation | Volume | Pin speed | Bus | Peak per stack | Largest stack | NVIDIA products |
|---|---|---|---|---|---|---|
| HBM2E | 2020 | ~3.6 Gb/s | 1,024 | ~460 GB/s | 16 GB | A100 80GB [[S370]](../../sources/bibliography.md#s370)[[S365]](../../sources/bibliography.md#s365) |
| HBM3 | 2022 | 6.4 Gb/s | 1,024 | ~819 GB/s | 24 GB | H100 [[S368]](../../sources/bibliography.md#s368) |
| HBM3E | 2024 | 9.2–9.8 Gb/s | 1,024 | ~1.2–1.28 TB/s | 36 GB (48 GB sampled) | H200, B200, B300 [[S371]](../../sources/bibliography.md#s371)[[S372]](../../sources/bibliography.md#s372)[[S375]](../../sources/bibliography.md#s375) |
| HBM4 | 2026 | 8 (JEDEC) to >10; ~9.4 in Rubin | 2,048 | 2.0–2.56 TB/s | 36 GB in Rubin; 64 GB max | Rubin [[S369]](../../sources/bibliography.md#s369)[[S374]](../../sources/bibliography.md#s374)[[S33007]](../../sources/bibliography.md#s33007) |
| HBM4E | 🟡 2027 | up to ~12.8 GT/s targeted | 2,048 | not published | ~64 GB planned | Rubin Ultra [[S3009]](../../sources/bibliography.md#s3009)[[S35041]](../../sources/bibliography.md#s35041) |

![Bar chart of peak bandwidth per HBM stack: HBM 128 GB/s (2013), HBM2 256, HBM2E 460, HBM3 819, HBM3E about 1,280, JEDEC HBM4 2,048 and SK hynix HBM4 at over 10 Gb/s about 2,560 GB/s, a 16-fold rise. Diamonds show NVIDIA's as-shipped rates per stack, from about 183 GB/s on P100 to about 2,400 GB/s on Rubin; HBM4 doubled the interface from 1,024 to 2,048 bits.](../../assets/charts/03-hbm-stack-bandwidth-by-generation.svg)

![Bar chart of maximum HBM capacity per stack: HBM 1 GB (4-high), HBM2 8 GB, HBM2E 16 GB, HBM3 24 GB, 12-high HBM3E 36 GB, 16-high HBM3E 48 GB (sampling), HBM4 as used in Rubin 36 GB and HBM4E planned for Rubin Ultra about 64 GB per stack (1 TB in 16 stacks); JEDEC's HBM3 and HBM4 standards allow up to 64 GB.](../../assets/charts/03-hbm-stack-capacity-by-generation.svg)

GPU-level gains multiply pin speed, bus width and stack count: 4 stacks on P100, 8 on B200 and Rubin, 16 planned; AMD's MI455X uses 12 [[S35041]](../../sources/bibliography.md#s35041)[[S144]](../../sources/bibliography.md#s144)[[S361]](../../sources/bibliography.md#s361).

![Bar chart of HBM stacks per package: NVIDIA P100 4, V100 4, A100 5, H100 5, H200 6, B200 8, B300 8, Rubin 8 and Rubin Ultra 16 (roadmap, 1 TB); AMD MI300X 8, MI355X 8 and MI455X 12 (432 GB). NVIDIA moved from CoWoS-S silicon interposers to CoWoS-L bridges with the two-die B200; TSMC targets about 5.5x reticle interposers in 2026 and 9.5x in 2027.](../../assets/charts/03-hbm-stacks-per-package.svg)

## Why HBM costs several times DDR per GB, and why yields are hard

1. **Silicon per bit:** ~3× DDR5's wafer area per GB, a gap Micron says is not narrowing [[S3006]](../../sources/bibliography.md#s3006).
2. **Compounding yield:** one bad die or bond scraps the stack; [known-good-die](../../glossary.md#known-good-die) testing limits the damage at a cost.
3. **Packaging:** every stack then needs scarce [CoWoS](../../glossary.md#cowos).

> [!TIP]
> **Worked example — stack yield and the HBM bill.** 🔴 At 99% yield per die-and-bond step, a 12-high stack yields ~89% and a 16-high ~85%. HBM3E at ~$15/GB puts a B200's 192 GB at ~$2,900, ~45% of its ~$6,400 build cost (Est., Epoch AI) [[S35020]](../../sources/bibliography.md#s35020); 🟡 at Bernstein's ~$53/GB 2027 HBM4 forecast [[S333]](../../sources/bibliography.md#s333), Rubin's 288 GB would top $15,000. **Business reading:** memory makers now set a GPU's largest cost line.

![Two bar panels: HBM share of unit cost rose from about 14% for the A100 to about 33% for the H100 and about 45% for the B200; across all AI accelerators memory's share of component spend rose from 52% in Q1 2024 to 63% in Q4 2025.](../../assets/charts/P5-hbm-cost-share.svg)

> [!WARNING]
> **Myth vs. reality:** "HBM gets cheaper every year." In 2025–26 DDR5 profitability competed for wafers [[S3016]](../../sources/bibliography.md#s3016) and memory's share of a Rubin rack roughly tripled (Est.) [[S330]](../../sources/bibliography.md#s330)[[S332]](../../sources/bibliography.md#s332); 🟡 Micron targets ~100k HBM wafers a month by end-2026 [[S3017]](../../sources/bibliography.md#s3017).

## HBM4's custom base die: logic moves into the memory stack

To drive 2,048 wires, the HBM4 base die moves from a DRAM process to a logic process [[S3009]](../../sources/bibliography.md#s3009). 🟡 SK hynix reportedly uses TSMC 12 nm; Samsung uses its own 4 nm [[S3011]](../../sources/bibliography.md#s3011). Micron says TSMC will make its [HBM4E](../../glossary.md#hbm4e) base dies from 2027, with custom designs for customers who pay a premium [[S3007]](../../sources/bibliography.md#s3007). TSMC offers custom HBM4E base dies on N3P [[S3008]](../../sources/bibliography.md#s3008).

> [!TIP]
> **Worked example — wider and slower beats narrow and fast.** JEDEC HBM4 at only 8 Gb/s gives 8 × 2,048 ÷ 8 = 2,048 GB/s; the fastest HBM3E, 9.8 Gb/s on 1,024 wires, gives ~1,280 GB/s [[S369]](../../sources/bibliography.md#s369)[[S372]](../../sources/bibliography.md#s372). That is +60% bandwidth at an 18% lower pin speed, easing power and signal integrity. **Business reading:** the base die now decides speed, so whoever designs it gains leverage.

**What it means for memory makers:** a TSMC-made base die moves a slice of every stack's value to the foundry (Samsung's in-house foundry is the counter-pitch) [[S3011]](../../sources/bibliography.md#s3011); a custom base die ties a stack to one buyer's GPU, lengthening qualification and favouring incumbents; and GPU vendors gain a lever to move controller logic into the stack.

<details>
<summary>🔧 Under the hood: channels, bonding and the height limit</summary>

- **Channels.** HBM3 splits 1,024 bits into 16 independent channels; HBM4 has 32 [[S368]](../../sources/bibliography.md#s368)[[S369]](../../sources/bibliography.md#s369). More channels keep more requests in flight, which helps scattered KV-cache reads.
- **Height.** Stacks must fit a fixed package height, so taller stacks need thinner, more fragile dies, one reason 16-high lags 12-high [[S375]](../../sources/bibliography.md#s375)[[S369]](../../sources/bibliography.md#s369).

</details>

## 🎯 Corp Dev Lens

1. **The base die is a new value pool.** Custom HBM4E logic made at TSMC [[S3007]](../../sources/bibliography.md#s3007)[[S3008]](../../sources/bibliography.md#s3008) needs PHY, controller and interface IP. Which IP and design-services firms gain?
2. **Supplier concentration cuts both ways.** 🟡 SK hynix's >50% of NVIDIA's 2026 HBM [[S90041]](../../sources/bibliography.md#s90041) means a deep partner and a single point of pricing power. How exposed are rivals relying on the second and third suppliers?
3. **Wafer-trade economics set everyone's bill.** If DDR5 margins stay high [[S3016]](../../sources/bibliography.md#s3016), HBM supply grows slowly, favouring designs that need less HBM per token (see [memory tiering](memory-tiering-and-rubin-cpx.md)).

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S125**](../../sources/bibliography.md#s125) NVIDIA, *NVIDIA Tesla P100 (Pascal GP100) Architecture Whitepaper*, 2016-04. [Link](https://images.nvidia.com/content/pdf/tesla/whitepaper/pascal-architecture-whitepaper.pdf)
- [**S144**](../../sources/bibliography.md#s144) AMD Newsroom, *AMD Unveils Vision for an Open AI Ecosystem, Detailing New Silicon, Software and Systems at Advancing AI 2025*, 2025-06-12. [Link](https://www.amd.com/en/newsroom/press-releases/2025-6-12-amd-unveils-vision-for-an-open-ai-ecosystem-detai.html)
- [**S179**](../../sources/bibliography.md#s179) Intel, *Intel Xeon 6 processors with P-cores (Granite Rapids, 6900P/6700P)*, 2024-09-24. [Link](https://www.intel.com/content/www/us/en/products/details/processors/xeon/xeon6-p-cores.html)
- [**S330**](../../sources/bibliography.md#s330) PC Gamer, *A single Nvidia Vera Rubin rack is estimated to cost $7,803,148 with over $2 million of that figure spent on memory alone*, 2026-05. [Link](https://pcgamer.com/hardware/a-single-nvidia-vera-rubin-rack-is-estimated-to-cost-usd7-803-148-with-over-usd2-million-of-that-figure-spent-on-memory-alone)
- [**S332**](../../sources/bibliography.md#s332) Tiger Brokers (iTiger), *Morgan Stanley's BOM analysis of NVIDIA's Rubin: GPU share declines; PCB, MLCC and ABF substrate values soar*, 2026-05-20. [Link](https://www.itiger.com/news/1188068712)
- [**S333**](../../sources/bibliography.md#s333) Wccftech, *Bernstein warns NVIDIA's Vera Rubin racks will hit $9.1 million as HBM4 prices triple to $53 per gigabyte*, 2026-07. [Link](https://wccftech.com/bernstein-warns-nvidias-vera-rubin-racks-will-hit-9-1-million-as-hbm4-prices-triple-to-53-per-gigabyte/)
- [**S361**](../../sources/bibliography.md#s361) Digital Citizen, *AMD Instinct MI455X brings 432GB of HBM4 and 40 PFLOPs of AI compute to Helios*, 2026-01. [Link](https://www.digitalcitizen.life/amd-instinct-mi455x-brings-432gb-of-hbm4-and-40-pflops-of-ai-compute-to-helios/)
- [**S365**](../../sources/bibliography.md#s365) NVIDIA, *NVIDIA A100 Tensor Core GPU architecture whitepaper*, 2020. [Link](https://images.nvidia.com/aem-dam/en-zz/Solutions/data-center/nvidia-ampere-architecture-whitepaper.pdf)
- [**S368**](../../sources/bibliography.md#s368) JEDEC, *JEDEC publishes HBM3 update to High Bandwidth Memory (HBM) standard (JESD238)*, 2022-01-27. [Link](https://www.jedec.org/news/pressreleases/jedec-publishes-hbm3-update-high-bandwidth-memory-hbm-standard)
- [**S369**](../../sources/bibliography.md#s369) JEDEC, *JESD270-4: High Bandwidth Memory (HBM4) standard*, 2025-04-16. [Link](https://www.jedec.org/standards-documents/docs/jesd270-4)
- [**S370**](../../sources/bibliography.md#s370) JEDEC, *JESD235 High Bandwidth Memory (HBM / HBM2 / HBM2E) DRAM standard family*, 2013-10. [Link](https://www.jedec.org/standards-documents/docs/jesd235a)
- [**S371**](../../sources/bibliography.md#s371) Micron Technology, *Micron commences volume production of industry-leading HBM3E solution*, 2024-02-26. [Link](https://investors.micron.com/news-releases/news-release-details/micron-commences-volume-production-industry-leading-hbm3e-solution)
- [**S372**](../../sources/bibliography.md#s372) Samsung Electronics, *Samsung develops industry-first 36GB HBM3E 12H DRAM*, 2024-02-27. [Link](https://news.samsung.com/global/samsung-develops-industry-first-36gb-hbm3e-12h-dram)
- [**S374**](../../sources/bibliography.md#s374) SK hynix Newsroom, *SK hynix completes world-first HBM4 development and readies mass production*, 2025-09-12. [Link](https://news.skhynix.com/sk-hynix-completes-worlds-first-hbm4-development-and-readies-mass-production/)
- [**S375**](../../sources/bibliography.md#s375) SK hynix Newsroom, *SK hynix newsroom: 16-high 48GB HBM3E unveiled at SK AI Summit 2024*, 2024-11-04. [Link](https://news.skhynix.com/)
- [**S3006**](../../sources/bibliography.md#s3006) Tom's Hardware, *Micron says the silicon gap between HBM and DDR5 is widening with every generation*, 2026-08. [Link](https://www.tomshardware.com/tech-industry/semiconductors/micron-says-the-silicon-gap-between-hbm-and-ddr5-is-widening-with-every-generation)
- [**S3007**](../../sources/bibliography.md#s3007) Tom's Hardware, *Micron teams up with TSMC to deliver HBM4E, targeted for 2027*, 2025-09. [Link](https://www.tomshardware.com/micron-hands-tsmc-the-keys-to-hbm4e)
- [**S3008**](../../sources/bibliography.md#s3008) TrendForce, *TSMC unveils custom C-HBM4E details: N3P logic dies reportedly target 2x efficiency gain*, 2025-12-01. [Link](https://www.trendforce.com/news/2025/12/01/news-tsmc-unveils-custom-c-hbm4e-details-n3p-logic-dies-reportedly-target-2x-efficiency-gain/)
- [**S3009**](../../sources/bibliography.md#s3009) Tom's Hardware, *HBM undergoes major architectural shakeup as TSMC and GUC detail HBM4, HBM4E and C-HBM4E 3nm base dies, up to 12.8 GT/s by 2027*, 2025. [Link](https://www.tomshardware.com/pc-components/dram/hbm-undergoes-major-architectural-shakeup-as-tsmc-and-guc-detail-hbm4-hbm4e-and-c-hbm4e-3nm-base-dies-to-enable-2-5x-performance-boost-with-speeds-of-up-to-12-8gt-s-by-2027)
- [**S3011**](../../sources/bibliography.md#s3011) TrendForce, *Samsung's custom HBM4E design reportedly aimed for mid-2026, parallels SK hynix and Micron*, 2026-01-23. [Link](https://www.trendforce.com/news/2026/01/23/news-samsungs-custom-hbm4e-design-reportedly-aimed-for-mid-2026-parallels-sk-hynix-and-micron/)
- [**S3016**](../../sources/bibliography.md#s3016) I-Connect007 (TrendForce), *Higher DDR5 profitability intensifies capacity crowding, strengthening HBM3e pricing momentum in 2026*, 2025-12. [Link](https://iconnect007.com/article/148160/higher-ddr5-profitability-intensifies-capacity-crowding-strengthening-hbm3e-pricing-momentum-in-2026/148157/ein)
- [**S3017**](../../sources/bibliography.md#s3017) TrendForce, *Micron reportedly to add 60K HBM wafers/month, reaching 100K by year-end to narrow gap with Samsung, SK hynix*, 2026-09-04. [Link](https://www.trendforce.com/news/2026/09/04/news-micron-reportedly-to-add-60k-hbm-wafersm-reaching-100k-by-year-end-to-narrow-gap-with-samsung-sk-hynix/)
- [**S33006**](../../sources/bibliography.md#s33006) Tom's Hardware, *Nvidia launches Vera Rubin NVL72 AI supercomputer at CES*, 2026-01-05. [Link](https://www.tomshardware.com/pc-components/gpus/nvidia-launches-vera-rubin-nvl72-ai-supercomputer-at-ces-promises-up-to-5x-greater-inference-performance-and-10x-lower-cost-per-token-than-blackwell-coming-2h-2026)
- [**S33007**](../../sources/bibliography.md#s33007) Dataconomy, *Nvidia Quietly Cuts Vera Rubin HBM4 And NVLink Bandwidth Specs*, 2026-11-02. [Link](https://dataconomy.com/2026/11/02/nvidia-quietly-cuts-vera-rubin-hbm4-and-nvlink-bandwidth/)
- [**S35020**](../../sources/bibliography.md#s35020) Epoch AI, *NVIDIA's B200 costs around $6,400 to produce, with memory accounting for half*, 2025-12. [Link](https://epoch.ai/data-insights/b200-cost-breakdown)
- [**S35041**](../../sources/bibliography.md#s35041) Glenn K. Lockwood (Glenn K. Lockwood), *Rubin Ultra (R300) notes*, 2026. [Link](https://glennklockwood.com/garden/processors/R300)
- [**S90006**](../../sources/bibliography.md#s90006) TweakTown, *Nvidia cuts Vera Rubin's memory bandwidth by up to 26% and AMD's Helios now leads in memory bandwidth*, 2026-10. [Link](https://www.tweaktown.com/news/114304/nvidia-cuts-vera-rubins-memory-bandwidth-by-up-to-26-percent-and-amds-helios-now-leads-in-memory-bandwidth/index.html)
- [**S90039**](../../sources/bibliography.md#s90039) TrendForce, *Samsung, SK hynix reportedly tapped as NVIDIA Rubin HBM4 suppliers; shipments could start in March*, 2026-03-09. [Link](https://www.trendforce.com/news/2026/03/09/news-samsung-sk%E2%80%AFhynix-reportedly-tapped-as-nvidia-rubin-hbm4-suppliers-shipments-could-start-in-march/)
- [**S90040**](../../sources/bibliography.md#s90040) Tom's Hardware, *HBM4 mass production delayed as Nvidia pushes memory specs higher*, 2025. [Link](https://www.tomshardware.com/tech-industry/hbm4-mass-production-delayed-as-nvidia-pushes-memory-specs-higher)
- [**S90041**](../../sources/bibliography.md#s90041) I-Connect007 (TrendForce), *NVIDIA seeks to raise HBM4 specs in response to AMD competition; SK hynix expected to remain largest supplier in 2026*, 2025-09. [Link](https://iconnect007.com/article/146969/nvidia-seeks-to-raise-hbm4-specs-in-response-to-amd-competition-sk-hynix-expected-to-remain-largest-supplier-in-2026/146966/aep)
