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
| Q3 FY2027 guidance $108B ± 2 %, excluding any China Data Center compute revenue; CFO called the FY2028 outlook "supply-constrained" | 🟢 | S3, S90012 |
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
| **NVLink Fusion:** launched May 2025 with MediaTek, Marvell, Alchip, Astera Labs, Synopsys, Cadence (custom silicon) and **Qualcomm, Fujitsu** (CPUs); Arm Neoverse support (Nov 2025); AWS Trainium4 to support it; reported **$2B NVIDIA investment in Marvell** (Mar 2026); Ayar Labs and Lightmatter reported joining (Jun 2026). AMD, Broadcom and Intel back UALink instead | 🟢/🟡 | S90031, S90036, S90037, S90038, S90034 |
| **China:** Dec 2025 US decision to allow H200 sales to approved Chinese buyers with **25 % of revenue to the US government**; BIS licensing framework Jan 2026; NVIDIA licensed for a small volume (Feb 2026); purchase orders received and manufacturing restarted (GTC, Mar 2026); guidance still excludes China DC compute | 🟢/🟡 | S90032, S90033 |

## Competitors

| Fact | Tag | Sources |
|---|---|---|
| **AMD Helios:** 72 × MI455X + EPYC "Venice"; 1.4 EF FP8 / 2.9 EF FP4 / 31 TB HBM4 per rack; in production, first shipments ~end Q3 2026; OpenAI large-scale deployment from Q4 2026 into 2027 (6 GW deal, Oct 2025); Oracle 50,000 MI450; Azure reported as first major Helios deployment; MI500 in customer engagement | 🟢/🟡 | S90020, S90021, S90022, S90023, S90024 |
| **Google TPU:** Ironwood (v7) GA; Anthropic up to **1M TPUs** (>1 GW in 2026, tens of $B); Meta multibillion rental of Ironwood capacity (Feb 2026) and talks to buy TPUs for its own datacenters; Google selling TPUs into customer datacenters | 🟢/🟡 | S90025, S90026, S90027 |
| **AWS:** Trn3 UltraServers GA (re:Invent, Dec 2025; 3 nm); **Trainium4** designed to support NVLink Fusion; AWS claims 6× FP4, 3× FP8, 4× memory bandwidth vs Trn3; Project Rainier ~500k Trainium2 for Anthropic (Oct 2025) | 🟢 | S90034, S90035 |
| **Microsoft:** Maia 200 announced 2026-01-27, deployed in US/Europe/Australia and running Copilot; **Maia 300** production deployments 2027; multi-gigawatt Maia expansion from 2027 (Oct 2026 reports) | 🟢/🟡 | S90044, S90045, S90046 |
| **Huawei:** Ascend 950PR (Q1 2026; mass production reportedly Apr 2026), 950DT (Q4 2026); Atlas 950 SuperPoD 8,192 chips, 8 EF FP8 / 16 EF FP4 (Q4 2026); Ascend 960 (2027), 970 (2028) — shipments of the SuperPoD not yet confirmed | 🟢 (roadmap) / 🔴 (shipments) | S90042, S90043 |
| **Qualcomm (public information only):** AI200 (2026) and AI250 (2027) rack-scale inference systems, 768 GB LPDDR per card, direct liquid cooling, annual cadence; HUMAIN plans 200 MW from 2026; NVLink Fusion partner for its server CPUs (May 2025). No 2026 shipment confirmation found as of 2026-11-05 | 🟢 (announcements) / 🔴 (status) | S90028, S90029, S90030, S90031 |

## Memory and packaging

| Fact | Tag | Sources |
|---|---|---|
| Samsung and SK hynix on NVIDIA's Rubin HBM4 supplier list (Mar 2026); SK hynix expected to supply > 50 % of NVIDIA's total 2026 HBM; NVIDIA pushed HBM4 pin speeds above 10–11 Gb/s | 🟡 | S90039, S90040, S90041 |
| TSMC CoWoS capacity estimates: ~65–80k wafers/month end-2025; ~105k (JPMorgan) to ~110–130k end-2026; NVIDIA reported at ~60 % of allocation; 2026 capacity fully booked | 🟡 (estimates vary widely) | S90039 + data/hbm_and_packaging.csv |
