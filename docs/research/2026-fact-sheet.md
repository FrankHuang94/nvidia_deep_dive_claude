# 2026 fact sheet (orchestrator research, verified by web search on 2026-11-05)

Shared baseline of the most volatile 2026 facts for all chapter authors. Cite the `S9xxxx` ids (registered in
`sources/registry/S90000-orchestrator-research.csv`). Confidence tags follow the style guide:
🟢 company-confirmed · 🟡 credible reporting · 🔴 speculative / unresolved. Where sources conflict, the conflict
is stated — keep it visible in the text rather than picking silently.

## NVIDIA — financials and demand

| Fact | Tag | Sources |
|---|---|---|
| FY2026 revenue $215.9B (+65 %); Q4 FY2026 revenue $68.1B | 🟢 | S1 |
| Q1 FY2027 (reported May 2026): revenue $81.6B; networking a record $14.8B; NVIDIA began reporting **Data Center** (hyperscale vs. AI clouds/industrial/enterprise) and **Edge Computing** platforms | 🟢/🟡 | S90014 |
| Q2 FY2027 (reported 2026-08-26): revenue $96.2B (+106 % y/y); Data Center ~$89.0B (+18 % q/q); hyperscale ~$48.7–49B (+13 % q/q); networking record, +18 % q/q (≈ $17.5B implied); Spectrum-X Ethernet 2.6× y/y; GAAP gross margin 75.0 % | 🟢/🟡 | S3, S90011, S90012, S90013 |
| Q3 FY2027 guidance $108B ± 2 % and GAAP gross margin 74 % ± 50 bp, excluding any China Data Center compute revenue | 🟢 | S3, S90012, S90085 |
| **FY2028 preliminary outlook (Q2 FY2027 call):** revenue growth ~70 % y/y, explicitly **supply-constrained**; gross margin to bottom at **71–72 % in Q4 FY2027** (memory costs above plan) and run **72–73 % in FY2028** as price increases take effect | 🟢 (management guidance) | S90085, S90086 |
| Hopper shipments to China < 1 % of Q2 FY2027 Data Center revenue | 🟡 | S90011 |
| GTC 2026 (2026-03-16): Huang sized Blackwell + Vera Rubin demand at **$1 trillion through 2027**, up from the **$500B through 2026** cited in Feb 2026; outlets differ on "orders" vs "revenue opportunity" | 🟢 (statement) / 🟡 (wording) | S90001, S90002 |

## NVIDIA — products and roadmap

| Fact | Tag | Sources |
|---|---|---|
| Vera Rubin NVL72 is the 2026 platform (NVIDIA renamed the "NVL144" count to package-based NVL72); production shipments from Q3 2026, volume ramp Q4 2026, growth through H1 2027 | 🟢/🟡 | S90009, S90010 |
| **Rubin spec revision (Sep–Oct 2026):** HBM4 bandwidth per GPU listed at **19.2 TB/s** (was 22 TB/s); NVLink 6 **3.0 TB/s** per GPU (was 3.6); NVL72 HBM bandwidth 1,400 TB/s (was 1,580); capacity unchanged at 288 GB HBM4. NVIDIA has not explained the change; an analyst attributes it to ~9.4 vs ~10.7 Gb/s HBM4 pin speeds | 🟢 (spec page) / 🔴 (cause) | S90006, S90007, S90008 |
| GTC 2026 rack line-up: Vera Rubin NVL72 (3.6 EF NVFP4 inference, NVLink all-to-all originally 260 TB/s), **Groq 3 LPX** rack (256 LPUs) beside Vera Rubin, standalone **Vera CPU** ("multi-billion-dollar business"), **Kyber** rack (144 GPU packages, vertical trays) for **Rubin Ultra (H2 2027)**; NVL576 framing persists in some reports | 🟢/🟡 | S90003, S90005 |
| **Feynman (2028)** reported with an LP40 LPU, **Rosa** CPU, BlueField-5 and ConnectX-10 | 🟡 | S90004 |
| Rubin CPX was absent from the GTC 2026 roadmap; a revival is reported but not confirmed | 🟡/🔴 | (see data/roadmap.csv notes) |
| GTC DC 2026 runs Nov 30 – Dec 3, 2026 (keynote Dec 1) — **after** this repo's as-of date | 🟢 | S90047 |

## NVIDIA — deals and capital

| Fact | Tag | Sources |
|---|---|---|
| **OpenAI:** Sept 2025 LOI (up to $100B as 10 GW comes online) was shelved in Feb 2026 in favour of a **~$30B direct equity investment** in OpenAI's funding round, with no deployment milestones (FT/Reuters). Valuation reported at $730B pre-money (FT) or ~$830B incl. new money (Reuters). Final close not confirmed in the sources found | 🟡 | S90015, S90016, S90017 |
| **Groq (2025-12-24):** non-exclusive licence of Groq's inference technology; founder Jonathan Ross, president Sunny Madra and team joined NVIDIA; Groq continues independently (CEO Simon Edwards). Price undisclosed, **~$20B reported**; Groq's last round (Sep 2025) valued it at ~$6.9B | 🟢 (structure) / 🟡 (price) | S90018, S90019 |
| **NVLink Fusion:** launched May 2025 with MediaTek, Marvell, Alchip, Astera Labs, Synopsys, Cadence (custom silicon) and **Qualcomm, Fujitsu** (CPUs); Arm Neoverse support (Nov 2025); AWS Trainium4 to support it; reported **$2B NVIDIA investment in Marvell** (Mar 2026); Ayar Labs and Lightmatter reported joining (Jun 2026). AMD and Broadcom back UALink instead; Intel sits on both sides (UALink promoter, and NVLink-attached custom x86 CPUs under its Sept 2025 NVIDIA deal — see layer-05 sources S130, S519) | 🟢/🟡 | S90031, S90036, S90037, S90038, S90034 |
| **China:** Dec 2025 US decision to allow H200 sales to approved Chinese buyers with **25 % of revenue to the US government**; BIS licensing framework Jan 2026; NVIDIA licensed for a small volume (Feb 2026); purchase orders received and manufacturing restarted (GTC, Mar 2026); guidance still excludes China DC compute | 🟢/🟡 | S90032, S90033 |
| **Hugging Face:** NVIDIA agreed to acquire Hugging Face for **$12.9B** (reported by The Information 2026-08-27; confirmed ~2026-09-03/04): ~$11.9B to investors + up to $1B stock incentives; Hugging Face to remain an open platform and NVIDIA chips not required; close targeted H1 2027; possible EU review and DOJ interest reported. Largest NVIDIA acquisition since Mellanox ($6.9B) | 🟢 (deal) / 🟡 (regulatory) | S11500, S11025, S90084, S11027, S11028 |
| **Other 2026 capital deployment:** xAI $20B Series E participation (Jan 2026); ~$4B into datacenter optics suppliers incl. Lumentum and Coherent (Mar 2026, reported); ~$2B into Marvell (Mar 2026, reported) | 🟡 | S13039, S13529, S90037 |

## Competitors

| Fact | Tag | Sources |
|---|---|---|
| **AMD–Meta (2026-02-24):** a second 6 GW chips-for-stock agreement mirroring the OpenAI deal — warrant for up to 160M AMD shares; AMD shares later passed the $600 hurdle reported for the final tranche (Sep 2026, single source) | 🟢 / 🟡 | S24004, S24003 |
| **AMD Helios:** 72 × MI455X + EPYC "Venice"; 1.4 EF FP8 / 2.9 EF FP4 / 31 TB HBM4 per rack; in production, first shipments ~end Q3 2026; OpenAI large-scale deployment from Q4 2026 into 2027 (6 GW deal, Oct 2025); Oracle 50,000 MI450; Azure reported as first major Helios deployment; MI500 in customer engagement | 🟢/🟡 | S90020, S90021, S90022, S90023, S90024 |
| **Google TPU:** Ironwood (v7) GA; Anthropic up to **1M TPUs** (>1 GW in 2026, tens of $B); Meta multibillion rental of Ironwood capacity (Feb 2026) and talks to buy TPUs for its own datacenters; Google selling TPUs into customer datacenters | 🟢/🟡 | S90025, S90026, S90027 |
| **AWS:** Trn3 UltraServers GA (re:Invent, Dec 2025; 3 nm); **Trainium4** designed to support NVLink Fusion; AWS claims 6× FP4, 3× FP8, 4× memory bandwidth vs Trn3; Project Rainier ~500k Trainium2 for Anthropic (Oct 2025) | 🟢 | S90034, S90035 |
| **Microsoft:** Maia 200 announced 2026-01-27, deployed in US/Europe/Australia and running Copilot; **Maia 300** production deployments 2027; multi-gigawatt Maia expansion from 2027 (Oct 2026 reports) | 🟢/🟡 | S90044, S90045, S90046 |
| **Huawei:** Ascend 950PR (Q1 2026; mass production reportedly Apr 2026), 950DT (Q4 2026); Atlas 950 SuperPoD 8,192 chips, 8 EF FP8 / 16 EF FP4 (Q4 2026); Ascend 960 (2027), 970 (2028) — shipments of the SuperPoD not yet confirmed | 🟢 (roadmap) / 🔴 (shipments) | S90042, S90043 |
| **Qualcomm Investor Day (2026-06-24), public information only:** **Dragonfly C1000** server CPU (custom Oryon, > 250 cores, chiplets, > 5 GHz target, PCIe Gen 7, CXL) for agentic orchestration / AI head nodes — **Meta** first named customer (multi-generation agreement), production deployments from **H2 2028**; **Dragonfly AI300** inference accelerator with High Bandwidth Compute (HBC) Gen 2, vendor-claimed 54× memory bandwidth vs AI200, UALink and ESUN scale-up, 2028 timing; agreement to **acquire Modular (Mojo/MAX AI software) for $3.9B**, expected to close H2 2026; target of **$15B data-center revenue by FY2029** | 🟢 (announced) / 🟡 (Modular price, timing details) | S90056, S90057, S90058, S90059, S90060 |
| **Qualcomm–AWS (2026-09-08), public information only:** multi-generation agreement for **custom AI silicon for AWS (inference first) and 1.6T optical connectivity**; AWS receives a warrant for up to **25M Qualcomm shares at $161.26** (~$4B at issuance; 3.75M initially) vesting as AWS purchases reach up to **$60B through 2036** (a ceiling, not a commitment); revenue from Qualcomm fiscal Q1 2027; structure mirrors AMD's chips-for-equity warrants. Qualcomm also targets ~$5B datacenter revenue in FY2027 (per chapter-15 sources) | 🟢 (8-K-backed terms) / 🟡 (targets) | S90087, S90088, S90089 |
| **Qualcomm (public information only):** AI200 (2026) and AI250 (2027) rack-scale inference systems, 768 GB LPDDR per card, direct liquid cooling, annual cadence; HUMAIN plans 200 MW from 2026; NVLink Fusion partner for its server CPUs (May 2025). No 2026 shipment confirmation found as of 2026-11-05 | 🟢 (announcements) / 🔴 (status) | S90028, S90029, S90030, S90031 |

## Memory and packaging

| Fact | Tag | Sources |
|---|---|---|
| Samsung and SK hynix on NVIDIA's Rubin HBM4 supplier list (Mar 2026); SK hynix expected to supply > 50 % of NVIDIA's total 2026 HBM; NVIDIA pushed HBM4 pin speeds above 10–11 Gb/s | 🟡 | S90039, S90040, S90041 |
| TSMC CoWoS capacity estimates: ~65–80k wafers/month end-2025; ~105k (JPMorgan) to ~110–130k end-2026; NVIDIA reported at ~60 % of allocation; 2026 capacity fully booked | 🟡 (estimates vary widely) | S90039 + data/hbm_and_packaging.csv |

## Networking and interconnect standards

| Fact | Tag | Sources |
|---|---|---|
| Co-packaged optics: **Quantum-X Photonics** (InfiniBand, 144 × 800G) slated for H2 2025 and **Spectrum-X Photonics** (Ethernet, up to 400 Tb/s across 2,048 ports in its largest configuration) for H2 2026; built on TSMC COUPE micro-ring modulators with partners TSMC, Coherent, Corning, Foxconn, Lumentum, SENKO. Shipments in 2026 reported by Focus Taiwan (Jun 2026) and StorageReview (Aug 2026, "full production", ~5× lower optics power) — see layer-06 registry S6019/S6020; Quantum-X Photonics timing cited as early 2026 in S515 | 🟢 (announced) / 🟡 (shipments) | S90048, S90049 |
| **UALink 2.0** ratified 2026-04-07 (in-network compute, chiplet definition, manageability, 200G DL/PL); UALink 1.0 silicon reaching labs H2 2026, products expected 2027 | 🟢 / 🟡 | S90050, S90051 |
| **ESUN** (Ethernet for Scale-Up Networking) launched as an OCP workstream at OCP Global Summit 2025; Broadcom's **SUE** v1.0 contributed to OCP (2025-09-05); coordination with IEEE 802.3 and UEC | 🟢 | S90052 |
| **AI back-end networks:** InfiniBand was ~80 % of AI back-end DC switch sales two years before 2025; Ethernet more than doubled InfiniBand in 2025 and was ~two-thirds of AI back-end switch sales in 1Q 2026 (Dell'Oro); vendor ranking 1Q26: Celestica, NVIDIA, Arista (Arista close once deferred revenue counted); Ethernet expanding into scale-up | 🟡 (analyst) | S90053, S90054, S90055 |
| NVIDIA networking: Q1 FY2027 $14.8B record; Q2 FY2027 +18 % q/q; Spectrum-X Ethernet 2.6× y/y (Q2 FY2027) | 🟢/🟡 | S90012, S90014 |

## Systems, power and software

| Fact | Tag | Sources |
|---|---|---|
| **800 VDC power:** ~20 partners showed 800 VDC components at GTC DC 2025 (Delta, Schneider, Vertiv, Infineon, ST, ABB, Eaton, GE Vernova, Hitachi Energy, Siemens, Navitas, TI); neoclouds (CoreWeave, Lambda, Nebius, OCI, Together AI) designing for 800 V; MGX-compatible 800 VDC power rack H2 2026; 800 VDC row power center (overhead busway, up to 2 MW per row) 2027; Kyber reported at ~600 kW per rack; Omniverse **DSX** blueprint generally available for digital-twin datacenter design. Dell'Oro: a reference architecture for high-density AI factories, not yet a universal standard | 🟢/🟡 | S90061, S90062, S90063 |
| **CUDA 13.x:** CUDA 13.2 released 2026-03-05 per NVIDIA release notes (S527; a secondary source says May 2026); CUDA 13 drops Maxwell, Pascal and Volta. No reliable 2026 CUDA developer count found beyond NVIDIA's ~6M (2025) — see data/software_ecosystem.csv | 🟡 | S90065 |
| **ROCm 7.0** (Sept 2025): AITER tuned operators, FP4/FP6, Windows support; 7.x point releases through 2026 | 🟢 | S90064 |
| **Dynamo 1.0** production release (GTC, 2026-03-16/17), open source under Apache 2.0, adopters incl. CoreWeave, Nebius, Together AI, Cursor, Perplexity, PayPal, Pinterest, ByteDance, Meituan, AstraZeneca; up to 7× inference on GB200 NVL (partner claim); relies on NIXL / NVIDIA networking stack | 🟢 / 🟡 (perf) | S90066 |
| **Qualcomm–Modular** ($3.9B announced 2026-06-24; reported closed 2026-07-29 and Mojo open-sourced Aug 2026 (Qualcomm press release S9511; Phoronix S9512); one low-tier source cites ~$3.1B recorded): Modular's Mojo language and MAX engine are a hardware-portable AI software stack — directly relevant to the CUDA-moat discussion | 🟡 | S90057 |

## Customers, cloud and capital deployment

| Fact | Tag | Sources |
|---|---|---|
| **Customer concentration (Q2 FY2027 10-Q):** one direct customer = 16 % of quarterly revenue; in H1 FY2027 three direct customers = 16 %, 15 %, 13 %; several indirect customers ≥ 10 % (estimated). Q1 FY2027: non-US-headquartered customers 22 % of revenue (42 % a year earlier); one AI research lab contributed meaningfully via cloud providers | 🟢 | S90069, S90070 |
| **Customer mix:** sovereign AI revenue > ~$30B in FY2026 (+80 % y/y, management commentary); AI clouds/industrial/enterprise (ACIE) ~$37B in Q1 FY2027, roughly matching hyperscale; regional neoclouds +35 % q/q and > 3× y/y in Q2 FY2027 | 🟡 | S90071 |
| **Equity portfolio (Jul 2026 10-Q, secondary reading):** non-marketable equity ~$51.2B, marketable equity ~$42.8B, ~$5.0B locked-up public equity (≈ $99B combined, a CNBC aggregation); H1 FY2027 purchases of equity securities $42.4B (vs $1.2B a year earlier); Q2 FY2027 net equity gains $7.8B (H1 $23.7B) — much of the portfolio growth is mark-to-market; further equity commitments ~$25B | 🟢 (filing) / 🟡 (reading) | S90069, S90070, S90072, S90073 |
| **Circular-financing response:** Aug 10, 2026 partnership with Apollo, BlackRock, Blackstone, Brookfield, Goldman Sachs and KKR to mobilise > $500B of third-party capital for AI infrastructure (reported) | 🟡 | S90074 |
| **CoreWeave backstop:** Sept 2025 amended agreement — NVIDIA to buy up to $6.3B of CoreWeave's unsold capacity through 2032-04-13 | 🟢 | S90067 |
| **DGX Cloud pivot:** most DGX Cloud capacity reportedly redirected to NVIDIA's internal research (2025); DGX Cloud **Lepton** positioned as a marketplace routing developers to partner GPU clouds | 🟡 | S90068 |
| **Anthropic (Nov 2025):** NVIDIA up to $10B and Microsoft up to $5B investment; Anthropic commits $30B to Azure compute and up to 1 GW on Grace Blackwell / Vera Rubin; joint engineering on Claude performance | 🟢 | S90075 |

## Case-study facts (China, DeepSeek, gigawatt factories)

| Fact | Tag | Sources |
|---|---|---|
| **China export controls (from NVIDIA filings):** Apr 2025 — H20 (and equivalent-bandwidth chips) required a licence "for the indefinite future"; H20 charge ~$4.5B recorded in Q1 FY2026 (~$5.5B initially warned); Aug 2025 — licences granted for certain H20 shipments; 2025-09-15 — China's antitrust regulator issued a preliminary finding against NVIDIA; Dec 2025 — H200 allowed with 25 % of revenue to the US government; Feb 2026 — licence to ship small amounts of H200; **no H200 revenue recognised to date** and guidance excludes China DC compute | 🟢 | S90081, S90082, S90083, S90032, S90033 |
| **DeepSeek V4** preview (2026-04-24): V4-Pro ~1.6T parameters and V4-Flash 284B, open weights; Huawei Ascend used for part of Flash training; Ascend SuperNodes adapted for V4 inference; DeepSeek cites high-end compute constraints; V4-Pro priced ~$3.48 per million output tokens (reported) | 🟢 / 🟡 | S90079, S90080 |
| **xAI Colossus 2:** Musk declared it operational in Jan 2026 as the first gigawatt training cluster (~550k GB200/GB300; 1.5 GW upgrade planned; third building toward ~2 GW) — contested by satellite-imagery analysis showing ~350 MW of cooling capacity in Jan 2026 | 🟡 (company claim) / 🔴 (contested) | S90076, S90077, S90078 |
