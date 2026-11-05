# QA: glossary coverage

<sub>Phase 9 independent QA (QA-B) · checked 2026-11-05 · glossary source: `docs/glossary/*.csv` → [`glossary.md`](../../glossary.md)</sub>

The style guide asks every page to define a technical term on first use and link it to the glossary
(`[HBM](glossary:hbm)`). This page records what QA checked, what it changed and what is still open.

## Summary

| Check | Result | Action |
|---|---|---|
| Entries with empty or one-word definitions | **0** of 651 (shortest definition: 6+ words) | none needed |
| Duplicate concepts under different slugs | **5 pairs** | merged, keeping one slug; 8 page links and 2 `see_also` references retargeted, 3 `see_also` lists merged |
| Same slug defined in two fragment files | 32 slugs (e.g. `rocm`, `vllm`, `nim`, `sovereign-ai`) | harmless by design (first definition wins in `glossary.py`); left as is |
| 60 most frequent technical terms with a glossary entry | **55 of 60** before QA; **60 of 60** after | 12 entries added in `docs/glossary/QA.csv` (5 of them top-60 terms) |
| Pages that use a top-60 term and link it to the glossary | **406 of 2041** page-term pairs (20%) before; **580** (28%) after | first-use links added on the 12 layer index pages, 5 primers, 00 and 01 (176 links); remaining pages **open** |

Glossary size after QA: **658 terms** (651 − 5 merged + 12 added).

## (a) Duplicates merged

| Kept slug | Dropped slug | Why this one was kept | Links retargeted |
|---|---|---|---|
| `nvidia-ai-enterprise` | `ai-enterprise` (11-strategy.csv) | product's full name; more inbound links | layer 11 competition and history pages; `nim` see-also |
| `tokens-per-megawatt` | `tokens-per-mw` (11-core.csv) | descriptive slug, defined first (08-core.csv) | layer 11 the-inference-shift; chapters 14, 18 and 19; `cost-per-million-tokens` see-also |
| `gsi` | `global-systems-integrator` (13-strategy.csv) | acronym slug, consistent with `hbm`, `oem`, `odm` | layer 13 competition |
| `efa` | `elastic-fabric-adapter` (06-strategy.csv) | AWS's own name for the product is EFA | layer 06 competition; `see_also` merged (`packet-spraying`) |
| `kyber` | `kyber-rack` (08-strategy.csv) | only `kyber` had inbound links | `see_also` merged (`rack-scale-system`, `hvdc-800v`) |

Pairs reviewed and **kept separate** because they are different concepts: `cowos` / `cowos-s` (family vs one
variant), `warp` / `nvidia-warp` (32-thread group vs NVIDIA's Python simulation framework), `sharp` /
`nvlink-sharp`, `gpudirect-rdma` / `gpudirect-storage`, `memory-bound` / `compute-bound`.

## (b) The 60 most frequent technical terms

Method: every content page (prose only — code, Mermaid, image alt text and citation tokens removed) was scanned
for acronyms and a curated list of ~300 technical terms; company names, SKUs and codenames (B200, Rubin,
Helios…), fiscal periods and callout labels were excluded, and the 60 most frequent remaining terms were kept.
"Linked" = the page links that glossary slug anywhere; "first use linked" = the first prose mention is itself
the link.

| Term | Mentions | Pages using it | Glossary slug | Pages linking it (before) | After | First use linked (after) |
|---|---:|---:|---|---:|---:|---:|
| GPU | 1528 | 140 | [`gpu`](../../glossary.md#gpu) | 2 | 2 | 0 |
| NVLink | 573 | 88 | [`nvlink`](../../glossary.md#nvlink) | 16 | 26 | 16 |
| CPU | 474 | 64 | [`cpu`](../../glossary.md#cpu) (added by QA) | 0 | 0 | 0 |
| CUDA | 451 | 56 | [`cuda`](../../glossary.md#cuda) | 17 | 21 | 12 |
| HBM | 401 | 68 | [`hbm`](../../glossary.md#hbm) | 25 | 30 | 22 |
| NVL72 | 394 | 97 | [`nvl72`](../../glossary.md#nvl72) | 11 | 23 | 16 |
| FP8 | 263 | 59 | [`fp8`](../../glossary.md#fp8) | 8 | 15 | 10 |
| NIC | 250 | 38 | [`nic`](../../glossary.md#nic) (added by QA) | 0 | 6 | 6 |
| scale-up | 226 | 64 | [`scale-up`](../../glossary.md#scale-up) | 9 | 14 | 10 |
| CoWoS | 183 | 41 | [`cowos`](../../glossary.md#cowos) | 16 | 18 | 10 |
| UALink | 160 | 39 | [`ualink`](../../glossary.md#ualink) | 8 | 12 | 8 |
| decode | 159 | 40 | [`decode`](../../glossary.md#decode) | 16 | 20 | 12 |
| KV cache | 70 | 32 | [`kv-cache`](../../glossary.md#kv-cache) | 25 | 25 | 22 |
| HBM4 | 149 | 49 | [`hbm4`](../../glossary.md#hbm4) (added by QA) | 0 | 9 | 7 |
| PFLOPS | 148 | 42 | [`flops`](../../glossary.md#flops) | 1 | 6 | 5 |
| NCCL | 142 | 30 | [`nccl`](../../glossary.md#nccl) | 9 | 14 | 11 |
| DPU | 132 | 30 | [`dpu`](../../glossary.md#dpu) | 8 | 8 | 3 |
| NVLink Fusion | 128 | 45 | [`nvlink-fusion`](../../glossary.md#nvlink-fusion) | 20 | 22 | 19 |
| hyperscaler | 126 | 53 | [`hyperscaler`](../../glossary.md#hyperscaler) | 9 | 13 | 6 |
| BlueField | 118 | 22 | [`bluefield`](../../glossary.md#bluefield) | 1 | 1 | 1 |
| scale-out | 115 | 49 | [`scale-out`](../../glossary.md#scale-out) | 5 | 10 | 9 |
| ConnectX | 113 | 27 | [`connectx`](../../glossary.md#connectx) | 1 | 2 | 2 |
| FP4 | 111 | 43 | [`fp4`](../../glossary.md#fp4) | 1 | 8 | 7 |
| SRAM | 110 | 29 | [`sram`](../../glossary.md#sram) | 4 | 6 | 2 |
| ROCm | 109 | 26 | [`rocm`](../../glossary.md#rocm) | 8 | 11 | 8 |
| vLLM | 109 | 33 | [`vllm`](../../glossary.md#vllm) | 8 | 11 | 9 |
| BF16 | 107 | 30 | [`bf16`](../../glossary.md#bf16) | 2 | 8 | 7 |
| x86 | 101 | 28 | [`x86`](../../glossary.md#x86) | 4 | 5 | 2 |
| Dynamo | 100 | 31 | [`dynamo`](../../glossary.md#dynamo) | 4 | 10 | 8 |
| ASIC | 97 | 34 | [`asic`](../../glossary.md#asic) | 8 | 10 | 7 |
| InfiniBand | 96 | 23 | [`infiniband`](../../glossary.md#infiniband) | 6 | 8 | 6 |
| PCIe | 92 | 25 | [`pcie`](../../glossary.md#pcie) | 2 | 4 | 4 |
| Spectrum-X | 90 | 28 | [`spectrum-x`](../../glossary.md#spectrum-x) | 6 | 8 | 5 |
| Triton | 88 | 26 | [`triton`](../../glossary.md#triton) | 7 | 10 | 6 |
| PyTorch | 88 | 28 | [`pytorch`](../../glossary.md#pytorch) | 3 | 5 | 4 |
| NVFP4 | 84 | 32 | [`nvfp4`](../../glossary.md#nvfp4) | 9 | 14 | 12 |
| SerDes | 78 | 27 | [`serdes`](../../glossary.md#serdes) | 10 | 11 | 10 |
| MoE | 78 | 21 | [`mixture-of-experts`](../../glossary.md#mixture-of-experts) | 11 | 11 | 2 |
| neocloud | 69 | 23 | [`neocloud`](../../glossary.md#neocloud) | 8 | 8 | 0 |
| SuperNIC | 66 | 24 | [`supernic`](../../glossary.md#supernic) | 12 | 12 | 5 |
| LPDDR | 66 | 22 | [`lpddr`](../../glossary.md#lpddr) | 4 | 5 | 2 |
| ESUN | 65 | 22 | [`esun`](../../glossary.md#esun) | 6 | 9 | 7 |
| GPU-hour | 62 | 31 | [`gpu-hour`](../../glossary.md#gpu-hour) | 2 | 5 | 4 |
| SGLang | 61 | 26 | [`sglang`](../../glossary.md#sglang) | 4 | 7 | 7 |
| CPO | 58 | 12 | [`co-packaged-optics`](../../glossary.md#co-packaged-optics) | 8 | 8 | 0 |
| XLA | 57 | 15 | [`xla`](../../glossary.md#xla) | 6 | 7 | 7 |
| prefill | 55 | 18 | [`prefill`](../../glossary.md#prefill) | 10 | 12 | 9 |
| LLM | 55 | 10 | [`llm`](../../glossary.md#llm) (added by QA) | 0 | 1 | 1 |
| HGX | 55 | 22 | [`hgx`](../../glossary.md#hgx) | 4 | 7 | 5 |
| CUDA-X | 52 | 18 | [`cuda-x`](../../glossary.md#cuda-x) | 3 | 5 | 3 |
| all-reduce | 52 | 12 | [`all-reduce`](../../glossary.md#all-reduce) | 5 | 7 | 6 |
| HBM3E | 51 | 27 | [`hbm3e`](../../glossary.md#hbm3e) (added by QA) | 0 | 1 | 1 |
| MFU | 51 | 9 | [`mfu`](../../glossary.md#mfu) | 8 | 9 | 7 |
| HBM4E | 49 | 14 | [`hbm4e`](../../glossary.md#hbm4e) | 2 | 3 | 2 |
| agentic | 47 | 25 | [`agentic-ai`](../../glossary.md#agentic-ai) | 4 | 7 | 3 |
| UEC | 45 | 14 | [`ultra-ethernet`](../../glossary.md#ultra-ethernet) | 6 | 8 | 1 |
| TensorRT-LLM | 44 | 18 | [`tensorrt-llm`](../../glossary.md#tensorrt-llm) | 2 | 7 | 6 |
| NVSwitch | 43 | 19 | [`nvswitch`](../../glossary.md#nvswitch) | 5 | 6 | 2 |
| PUE | 28 | 12 | [`pue`](../../glossary.md#pue) | 5 | 7 | 6 |
| TCO | 22 | 11 | [`tco`](../../glossary.md#tco) | 2 | 2 | 2 |

`PFLOPS`/`TFLOPS` are defined inside the [`flops`](../../glossary.md#flops) entry; `MoE` and `CPO` resolve to
`mixture-of-experts` and `co-packaged-optics`; `UEC` to `ultra-ethernet`.

### Entries added (`docs/glossary/QA.csv`)

Top-60 terms that had no entry: **CPU, NIC, LLM, HBM3E, HBM4**. Also added because they are frequent outside
the top 60 and undefined: **DRAM** (52 mentions on 17 pages), **FP32** (32), **FP16** (22), **MXFP4** (18),
**HPC** (37), **TOPS** (13) and **JEDEC** (20). Definitions are one or two plain-English sentences and contain
no figures that need a citation beyond the standards themselves.

## First-use linking — what was done and what is open

- QA inserted a glossary link at the **first eligible prose mention** of each top-60 term (except GPU and CPU,
  which every reader knows) on pages that did not link the term at all: the 12 layer `index.md` pages, primers
  P1–P5, `00-executive-summary.md` and `01-the-nvidia-flywheel.md` — **176 links**. Headings, tables, image
  alt text, HTML, code/Mermaid and existing link text were never touched.
- **Open (Low):** ~945 further first-use links would be needed on the other ~100 content pages (layer
  sub-pages, cross-cutting chapters, case studies, README, cheat sheet) for full compliance. QA did not apply
  them while another QA agent was editing figures on those pages. The same linker can be re-run in one pass
  once number fixes are merged; it adds only `[term](glossary:slug)` wrappers, and `make build` normalises them.
