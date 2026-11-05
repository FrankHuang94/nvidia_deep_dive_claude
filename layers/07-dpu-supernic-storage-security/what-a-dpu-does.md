# What a DPU does

<sub>Layer 07 · DPU, SuperNIC, storage, security · ~8 min read · Last verified: 2026-11-05</sub>

## ⚡ The Executive Take

- **A [DPU](../../glossary.md#dpu) is a network card with its own computer on board**: Arm cores, memory and fixed-function engines that run the cloud operator's plumbing instead of the host CPU [[S270]](../../sources/bibliography.md#s270)[[S7001]](../../sources/bibliography.md#s7001).
- **That plumbing is expensive in software:** estimates put this [infrastructure tax](../../glossary.md#infrastructure-tax) at ~19–33% of host CPU cores; three of the four come from NVIDIA, which sells DPUs [[S7005]](../../sources/bibliography.md#s7005)[[S7006]](../../sources/bibliography.md#s7006)[[S7007]](../../sources/bibliography.md#s7007).
- **In a GPU server, freed cores are cheap:** ~$375–650 a year per Vera Rubin compute tray (Est.), against $1.7–5.2K for every 1–3% of GPU time recovered [[S7000]](../../sources/bibliography.md#s7000). The AI case rests on isolation and line-rate data movement.
- **BlueField-4** (announced 2025-10-28): 64 Arm Neoverse V2 cores (the core inside Grace), 128 GB LPDDR5, 800 Gb/s, [PCIe](../../glossary.md#pcie) Gen6 x16; NVIDIA claims 6× BlueField-3's compute [[S7001]](../../sources/bibliography.md#s7001)[[S512]](../../sources/bibliography.md#s512). 🟢 Listed in full production at GTC 2026, with volume tied to Vera Rubin in H2 2026 [[S501]](../../sources/bibliography.md#s501)[[S7511]](../../sources/bibliography.md#s7511).
- **Weakness:** AWS (Nitro) and Google (Titanium) build their own offload [[S292]](../../sources/bibliography.md#s292)[[S7520]](../../sources/bibliography.md#s7520), AMD and Intel sell P4-programmable alternatives [[S289]](../../sources/bibliography.md#s289)[[S291]](../../sources/bibliography.md#s291), and NVIDIA's "replaces 30 to 300 CPU cores" claims are marketing, not benchmarks [[S7008]](../../sources/bibliography.md#s7008).

![Diagram comparing a GPU server without and with a DPU. Without a DPU, the host CPU spends roughly 19-33% of its cores on infrastructure software (virtual switch, overlays, firewall, IPsec/TLS, NVMe-oF initiator, telemetry, provider agents) and the provider's control plane runs where the tenant can reach it. With a BlueField DPU, tenant and AI work gets about 100% of the host cores, and the DPU's Arm cores and accelerators run networking, storage, security, multi-tenancy isolation and telemetry at 400-800 Gb/s; BlueField-3 has 16 Arm A78 cores at 400 Gb/s and BlueField-4 64 Neoverse V2 cores, 128 GB and 800 Gb/s.](../../assets/diagrams/07-dpu-offload.svg)

## 1. What a DPU offloads

Think of an office building. Someone has to run the lobby: security, mailroom, switchboard. Without a DPU, that staff works from the tenants' own desks. A DPU moves the lobby downstairs, run by the landlord on hardware the tenant cannot enter. It takes five families of work:

- **Networking:** a [virtual switch](../../glossary.md#virtual-switch) and [overlay networks](../../glossary.md#overlay-network) give each tenant a private network on shared cables.
- **Storage:** the DPU speaks [NVMe-oF](../../glossary.md#nvme-of) to remote flash and presents it to the host as a local [NVMe](../../glossary.md#nvme) drive.
- **Security:** inline [IPsec](../../glossary.md#ipsec)/TLS encryption, a stateful firewall and a [hardware root of trust](../../glossary.md#root-of-trust).
- **[Multi-tenancy](../../glossary.md#multi-tenancy):** the operator's control plane lives on the DPU, so a [bare-metal](../../glossary.md#bare-metal) tenant who owns the host OS still cannot change network policy; BlueField-4's ASTRA design enforces policy from the DPU [[S7024]](../../sources/bibliography.md#s7024).
- **[Telemetry](../../glossary.md#telemetry):** flow and congestion counters at line rate, used to find stragglers.

**[Q1 · Job & failure mode]** The layer's job is to move every byte into and out of each GPU at line rate, securely and with tenants isolated, without spending GPU or host-CPU cycles. When it is weak, GPUs wait on I/O, ~19–33% of host cores vanish into plumbing, clouds cannot safely rent bare metal, checkpoints and context reloads slow (see [storage for AI](storage-for-ai.md)), and data in use is exposed (see [confidential computing](confidential-computing.md)).

![Horizontal range chart of estimates of the host-CPU infrastructure tax: NVIDIA's BlueField-2 Redis test freed 12 of 64 cores (18.75%); NVIDIA's cluster power model frees 26 of 80 cores per server (32.5%); NVIDIA's DPU white paper says up to 30% of cycles; academic work on the 'datacenter tax' cites 25-30% of data-center CPU cycles. Three of the four estimates come from NVIDIA, which sells DPUs.](../../assets/charts/07-infrastructure-tax-estimates.svg)

> [!TIP]
> **Worked example — host cores a Vera Rubin tray would lose without offload.** A compute tray has 2 Vera CPUs × 88 cores = **176 host cores** [[S100]](../../sources/bibliography.md#s100). At NVIDIA's measured 18.75% to modelled 32.5% [[S7005]](../../sources/bibliography.md#s7005)[[S7006]](../../sources/bibliography.md#s7006), infrastructure software would absorb **33–57 cores**. At ~$5,000 per Vera (Est., Morgan Stanley) [[S331]](../../sources/bibliography.md#s331), ~$57 per core, that is **~$1,900–3,250 of CPU silicon per tray**. **Conclusion:** against ~$430K of rack price per compute tray (Est., $7.8M ÷ 18) [[S330]](../../sources/bibliography.md#s330), the CPU saving is under 1% of the hardware bill.

<details>
<summary>🔧 Under the hood: fast path and slow path inside a DPU</summary>

- **Slow path:** the first packet of a new connection goes to the Arm cores, which look up tenant policy and program a rule into the [NIC](../../glossary.md#nic)'s hardware switch.
- **Fast path:** later packets of that flow match the rule and are rewritten, encrypted or forwarded by fixed-function hardware without touching a core.
- **Why:** at 800 Gb/s a 1,500-byte packet arrives every ~15 ns, far too fast for software to inspect each one.
- **Programmability:** NVIDIA exposes this through [DOCA](../../glossary.md#doca); AMD Pensando and Intel's IPU expose P4 pipelines [[S289]](../../sources/bibliography.md#s289)[[S291]](../../sources/bibliography.md#s291).

</details>

## 2. Why it matters more in an AI cloud

In an AI cloud three things change from the general-cloud case. **GPU-hours dwarf CPU-hours:** four Blackwell-class GPUs rent for ~$175K a year at Lambda's $4.99/GPU-hour list price [[S395]](../../sources/bibliography.md#s395). **Bare metal is the norm:** [neoclouds](../../glossary.md#neocloud) rent whole servers, so the operator's control software must live where the tenant cannot reach it, the DPU's [zero-trust](../../glossary.md#zero-trust) role. **Line rates outran software:** at 400–800 Gb/s, encryption and storage protocols must run in hardware.

![Range bar chart (estimates) of the annual value of DPU offload per Vera Rubin compute tray: freed host cores, 33-57 of 176 Vera cores valued at about $57 per core over 5 years, are worth about $375-650 a year; best-case power savings of 247 W are worth about $202; recovering 1-3% of GPU time on four GPUs rented at $4.99 per hour is worth about $1,748-5,245. In AI servers the DPU's value lies in GPU utilization and tenant isolation, not in CPU cycles.](../../assets/charts/07-offload-value-per-tray.svg)

> [!TIP]
> **Worked example — what a DPU is worth per tray and per rack.** Over a 5-year server life [[S385]](../../sources/bibliography.md#s385), the freed cores are worth **~$375–650 a year** per tray. NVIDIA's best-case power saving (247 W) [[S7005]](../../sources/bibliography.md#s7005) is worth ~$200 a year at $0.081/kWh [[S389]](../../sources/bibliography.md#s389) and a [PUE](../../glossary.md#pue) of 1.15 [[S387]](../../sources/bibliography.md#s387)[[S388]](../../sources/bibliography.md#s388). Recovering 1–3% of GPU time on four GPUs at $4.99/hour [[S395]](../../sources/bibliography.md#s395) is worth **$1,750–5,250 a year**. Across an 18-tray [NVL72](../../glossary.md#nvl72) that is ~$7–12K from cores versus **~$31–94K from GPU time** (Est.) [[S7000]](../../sources/bibliography.md#s7000). **Conclusion:** judge a DPU by the GPU idle time and tenant risk it removes, figures vendors rarely measure independently.

> [!WARNING]
> **Myth vs. reality.** *Myth:* "A DPU pays for itself by freeing CPU cores." *Reality:* in GPU servers the freed cores are worth a few hundred dollars a year per tray; the value is isolation, line-rate crypto and storage, and fewer GPU stalls, which are harder to prove. NVIDIA's own white paper did not value the freed cores [[S7006]](../../sources/bibliography.md#s7006).

## 3. BlueField generations and DOCA

**[Q3 · Generational progress]** Bandwidth doubled every generation, 100 → 800 Gb/s. Compute per bit did not: BlueField-2 and -3 both had 4 Arm cores per 100 Gb/s, and BlueField-4 doubles that to 8 with server-class cores [[S7001]](../../sources/bibliography.md#s7001). The DPU is no longer just a packet engine; BlueField-4 also runs storage and KV-cache services (see [storage for AI](storage-for-ai.md)).

![Three-panel bar chart of NVIDIA BlueField DPUs. Arm cores: BlueField-1 16 (Cortex-A72, 2018), BlueField-2 8 (A72, 2020), BlueField-3 16 (A78, 2022), BlueField-4 64 (Neoverse V2, Grace-class, 2026). Network bandwidth: 100, 200, 400 and 800 Gb/s. Cores per 100 Gb/s: 16, 4, 4 and 8, so BlueField-4 doubles compute per bit, signalling that it runs services such as storage and KV-cache management, not just packet offload. NVIDIA claims BlueField-2 replaced ~30 CPU cores, BlueField-3 up to 300 and BlueField-4 has 6x BlueField-3's compute.](../../assets/charts/07-bluefield-generations.svg)

| Generation (year) | Arm cores | Network | Host link | NVIDIA claim |
|---|---|---|---|---|
| BlueField-1 (2018) | 16 × Cortex-A72 | 2 × 100 Gb/s | PCIe Gen3/4 | Mellanox design [[S273]](../../sources/bibliography.md#s273) |
| BlueField-2 (2020) | 8 × Cortex-A72 | up to 200 Gb/s | PCIe Gen4 | ~30 core-equivalents; DOCA launched [[S270]](../../sources/bibliography.md#s270)[[S7008]](../../sources/bibliography.md#s7008) |
| BlueField-3 (2022) | 16 × Cortex-A78 | 400 Gb/s | PCIe Gen5 | up to 300 core-equivalents (security) [[S269]](../../sources/bibliography.md#s269)[[S7008]](../../sources/bibliography.md#s7008) |
| BlueField-4 (2026) | 64 × Neoverse V2, 128 GB | 800 Gb/s | PCIe Gen6 x16 | 6× BlueField-3 compute [[S7001]](../../sources/bibliography.md#s7001)[[S512]](../../sources/bibliography.md#s512) |
| BlueField-5 (2028) | not disclosed | not disclosed | not disclosed | 🟡 on the Feynman roadmap [[S90004]](../../sources/bibliography.md#s90004)[[S502]](../../sources/bibliography.md#s502) |

**DOCA** does for the DPU what [CUDA](../../glossary.md#cuda) does for the GPU: libraries and services that let operators program offloads without NIC firmware. By October 2026 NVIDIA ships DOCA microservices such as Weave, which isolates tenants' traffic on BlueField-4 and ConnectX-9 with hardware VXLAN [[S7024]](../../sources/bibliography.md#s7024). Each service written for DOCA raises the cost of moving to a P4-programmed AMD or Intel part [[S289]](../../sources/bibliography.md#s289)[[S291]](../../sources/bibliography.md#s291).

> [!TIP]
> **Worked example — why 64 cores still cannot touch every packet.** At 800 Gb/s, full-size 1,500-byte packets arrive at ~**67 million per second**: ~1 million per second per core, or **~1 µs per packet**, a few thousand cycles at typical 2–3 GHz clocks (Est.; BlueField-4's clock is undisclosed) [[S7001]](../../sources/bibliography.md#s7001)[[S7000]](../../sources/bibliography.md#s7000). **Conclusion:** hardware forwards the packets; the 64 cores serve control, storage and KV-cache software, so core count tracks new software jobs, not bandwidth.

<details>
<summary>🔧 Under the hood: BlueField-4 specifics and open questions</summary>

- **Composition:** a Grace-class CPU plus ConnectX-9 networking; 64 Neoverse V2 cores, 128 GB LPDDR5, 800 Gb/s, PCIe 6.0 x16 [[S7001]](../../sources/bibliography.md#s7001)[[S7002]](../../sources/bibliography.md#s7002).
- **Unresolved:** reported transistor counts conflict (64B vs 126B) [[S7002]](../../sources/bibliography.md#s7002); clock, power and price are undisclosed.

</details>

## 🎯 Corp Dev Lens

1. **Attach rate is the swing factor.** AWS and Google run their own offload silicon [[S292]](../../sources/bibliography.md#s292)[[S7520]](../../sources/bibliography.md#s7520); how many neoclouds, sovereigns and enterprises standardise on BlueField-4 decides the value pool (see [competition](competition.md)).
2. **DOCA vs P4 tests the software moat.** Infrastructure written as DOCA services makes [BlueField](../../glossary.md#bluefield) sticky; open P4 and Linux tooling make it a commodity NIC with cores.
3. **The DPU is becoming a storage-server CPU.** BlueField-4 runs STX storage enclosures [[S7511]](../../sources/bibliography.md#s7511), a socket [x86](../../glossary.md#x86) CPUs used to fill (see [value chain](value-chain-and-corp-dev.md)).
4. **Qualcomm question (public information only):** AI200/AI250 racks use Ethernet [scale-out](../../glossary.md#scale-out) [[S173]](../../sources/bibliography.md#s173)[[S90029]](../../sources/bibliography.md#s90029). Would rack-scale inference need its own offload and isolation story, a partner DPU, or the customer's existing NIC?

## 📚 Sources

<!-- Auto-generated from the [S…] citations on this page by `make build`. Edit sources/registry/*.csv, not this list. -->

- [**S100**](../../sources/bibliography.md#s100) NVIDIA Technical Blog, *Inside the NVIDIA Vera Rubin Platform: Six New Chips, One AI Supercomputer*, 2026-01-05. [Link](https://developer.nvidia.com/blog/inside-the-nvidia-rubin-platform-six-new-chips-one-ai-supercomputer/)
- [**S173**](../../sources/bibliography.md#s173) Qualcomm, *Qualcomm Unveils AI200 and AI250 - Redefining Rack-Scale Data Center Inference*, 2025-10-27. [Link](https://www.qualcomm.com/news/releases/2025/10/qualcomm-unveils-ai200-and-ai250-redefining-rack-scale-data-cent)
- [**S269**](../../sources/bibliography.md#s269) NVIDIA Newsroom, *NVIDIA Extends Data Center Infrastructure Processing Roadmap with BlueField-3*, 2021-04-12. [Link](https://nvidianews.nvidia.com/news/nvidia-extends-data-center-infrastructure-processing-roadmap-with-bluefield-3)
- [**S270**](../../sources/bibliography.md#s270) NVIDIA Newsroom, *NVIDIA Introduces New Family of BlueField DPUs to Bring Breakthrough Networking, Storage and Security Performance to Every Data Center*, 2020-10-05. [Link](https://nvidianews.nvidia.com/news/nvidia-introduces-new-family-of-bluefield-dpus-to-bring-breakthrough-networking-storage-and-security-performance-to-every-data-center)
- [**S273**](../../sources/bibliography.md#s273) NVIDIA Docs, *NVIDIA Networking documentation hub (ConnectX adapter, Quantum and Spectrum switch product briefs and user manuals)*, 2025. [Link](https://docs.nvidia.com/networking/)
- [**S289**](../../sources/bibliography.md#s289) AMD, *AMD Advancing AI 2024: Pensando Pollara 400 AI NIC and Salina DPU*, 2024-10-10. [Link](https://www.amd.com/en/newsroom.html)
- [**S291**](../../sources/bibliography.md#s291) Intel, *Intel Infrastructure Processing Unit (IPU) E2100 (Mount Evans)*, 2022. [Link](https://www.intel.com/content/www/us/en/products/details/network-io/ipu.html)
- [**S292**](../../sources/bibliography.md#s292) Amazon Web Services, *Elastic Fabric Adapter (EFA) and AWS Nitro System documentation*, 2025. [Link](https://aws.amazon.com/hpc/efa/)
- [**S330**](../../sources/bibliography.md#s330) PC Gamer, *A single Nvidia Vera Rubin rack is estimated to cost $7,803,148 with over $2 million of that figure spent on memory alone*, 2026-05. [Link](https://pcgamer.com/hardware/a-single-nvidia-vera-rubin-rack-is-estimated-to-cost-usd7-803-148-with-over-usd2-million-of-that-figure-spent-on-memory-alone)
- [**S331**](../../sources/bibliography.md#s331) Wccftech, *NVIDIA's Vera Rubin rack hit with 435% memory price surge, pushing HBM4 & LPDDR5X bill to $2M of $7.8M total*, 2026-05. [Link](https://wccftech.com/nvidia-vera-rubin-rack-hit-with-memory-price-surge-pushing-hbm4-lpddr5x-bill-to-2m-of-7-8m-total/)
- [**S385**](../../sources/bibliography.md#s385) Amazon via SEC EDGAR, *Amazon.com Form 10-K filings (FY2019-FY2024) - useful lives of servers*, 2025-02-07. [Link](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001018724&type=10-K&dateb=&owner=include&count=40)
- [**S387**](../../sources/bibliography.md#s387) Uptime Institute, *Uptime Institute Global Data Center Survey 2024*, 2024-07. [Link](https://uptimeinstitute.com/resources/research-and-reports/uptime-institute-global-data-center-survey-results-2024)
- [**S388**](../../sources/bibliography.md#s388) Google, *Google data centers: efficiency (fleet-wide PUE)*, 2025. [Link](https://datacenters.google/efficiency/)
- [**S389**](../../sources/bibliography.md#s389) U.S. Energy Information Administration, *EIA Electric Power Monthly, Table 5.6.A: average price of electricity to ultimate customers by end-use sector*, 2025. [Link](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a)
- [**S395**](../../sources/bibliography.md#s395) Lambda, *Lambda GPU cloud pricing*, 2025. [Link](https://lambda.ai/pricing)
- [**S501**](../../sources/bibliography.md#s501) eWeek, *Everything Nvidia Just Announced at GTC 2026: 7 Chips, 5 Racks, 1 Giant Bet on Agentic AI*, 2026-03-17. [Link](https://www.eweek.com/news/nvidia-gtc-2026-ai-inference-vera-rubin-neuron/)
- [**S502**](../../sources/bibliography.md#s502) Tom's Hardware, *Nvidia updates data center roadmap with Rosa CPU and stacked Feynman GPUs; optical NVLink; Groq LPUs with NVFP4 and NVLink also on deck*, 2026-03-17. [Link](https://www.tomshardware.com/pc-components/gpus/nvidia-updates-data-center-roadmap-with-rosa-cpu-and-stacked-feynman-gpus-optical-nvlink-groq-lpus-with-nvfp4-and-nvlink-also-on-deck)
- [**S512**](../../sources/bibliography.md#s512) NVIDIA Blog, *NVIDIA Launches BlueField-4: The Processor Powering the Operating System of AI Factories*, 2025-10-28. [Link](https://blogs.nvidia.com/blog/bluefield-4-ai-factory/)
- [**S7000**](../../sources/bibliography.md#s7000) nvidia_deep_dive_claude repository, *Repo analysis: layer 07 models (DPU offload value per compute tray, checkpoint write time, KV-cache reload time by tier)*, 2026-11-05. [Link](https://github.com/FrankHuang94/nvidia_deep_dive_claude/blob/main/layers/07-dpu-supernic-storage-security/index.md)
- [**S7001**](../../sources/bibliography.md#s7001) NVIDIA, *NVIDIA BlueField-4 DPU datasheet*, 2026-05. [Link](https://dam-cdn.nvd.orangelogic.com/AssetLink/m8w7t64m2k40j51sx8xb4ok712b743ux.pdf)
- [**S7002**](../../sources/bibliography.md#s7002) ServeTheHome, *NVIDIA BlueField-4 with 64 Arm cores and 800G networking announced for 2026*, 2025-10-28. [Link](https://www.servethehome.com/nvidia-bluefield-4-with-64-arm-cores-and-800g-networking-announced-for-2026/)
- [**S7005**](../../sources/bibliography.md#s7005) NVIDIA, *NVIDIA DPU Power Efficiency (white paper)*, 2022-11. [Link](https://dcmag.fr/wp-content/uploads/2022/11/nvidia-dpu-power-efficiency-white-paper-2508650.pdf)
- [**S7006**](../../sources/bibliography.md#s7006) The Next Platform, *Economics and the inevitability of the DPU*, 2022-11-03. [Link](https://www.nextplatform.com/connect/2022/11/03/economics-and-the-inevitability-of-the-dpu/1635681)
- [**S7007**](../../sources/bibliography.md#s7007) arXiv:2511.06558, *Offloading Data Center Tax*, 2025-11. [Link](https://arxiv.org/html/2511.06558v1)
- [**S7008**](../../sources/bibliography.md#s7008) SDxCentral, *Nvidia unveils next-gen BlueField DPU*, 2021-04. [Link](https://www.sdxcentral.com/articles/news/nvidia-unveils-next-gen-bluefield-dpu/2021/04)
- [**S7024**](../../sources/bibliography.md#s7024) NVIDIA NGC Catalog, *DOCA Weave Service (dpf-weave Helm chart v26.8.0)*, 2026-10-12. [Link](https://catalog.ngc.nvidia.com/orgs/nvidia/doca/helm-charts/dpf-weave/v26.8.0)
- [**S7511**](../../sources/bibliography.md#s7511) NVIDIA Newsroom, *NVIDIA Launches BlueField-4 STX Storage Architecture With Broad Industry Adoption*, 2026-03-16. [Link](https://nvidianews.nvidia.com/news/nvidia-launches-bluefield-4-stx-storage-architecture-with-broad-industry-adoption)
- [**S7520**](../../sources/bibliography.md#s7520) Google Cloud, *Titanium (Google Cloud product page)*, 2024. [Link](https://cloud.google.com/titanium)
- [**S90004**](../../sources/bibliography.md#s90004) TrendForce, *Key GTC takeaways: how Samsung, Micron, Intel and more power NVIDIA's Vera Rubin and Feynman*, 2026-03-17. [Link](https://www.trendforce.com/news/2026/03/17/news-key-gtc-takeaways-how-samsung-micron-intel-more-power-nvidias-vera-rubin-and-feynman/)
- [**S90029**](../../sources/bibliography.md#s90029) Verdict, *Qualcomm AI200 and AI250 racks for AI inference*, 2025-10. [Link](https://www.verdict.co.uk/qualcomm-ai200-ai250-racks-ai-inference/)
