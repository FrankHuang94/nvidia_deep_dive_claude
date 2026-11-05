# TCO model (chapter 14)

A small, transparent owner-cost model behind
[chapter 14 · Training vs. inference economics](../../cross-cutting/14-training-vs-inference-economics.md).
It answers three questions for each accelerator platform:

1. What does one installed **accelerator-hour** cost its owner, all-in?
2. What does a **million tokens** cost at a stated workload and interactivity?
3. How many **tokens per second per MW** of facility power does the platform deliver?

It also prices a **frontier-scale training run** on each platform. **Every output is an estimate.**
Throughput for Vera Rubin NVL72, AMD Helios, Google TPU v7 and AWS Trainium is *modelled* from anchors and
multipliers, not measured, and is flagged `modelled` in the outputs (🔴 in the chapter).

## How to run

```bash
make tco                                  # = python3 scripts/tco/tco_model.py
python3 scripts/tco/tco_model.py --no-write   # print the summary without writing outputs
python3 scripts/charts/run_all.py ch_x14_tco  # rebuild the chapter-14 charts (re-runs the model)
```

Pure Python + pandas. The Monte Carlo uses the standard-library `random` module with a fixed seed (14),
so results are reproducible. Runtime is about one second.

## Inputs

| File | What the model takes from it |
|---|---|
| `data/x14_tco_scenarios.csv` | **Every assumption**: one row per system × parameter with `base`, `low`, `high`, unit, basis, confidence and source ids. `system = All` rows are global (utilization, $/kWh, PUE, cost of capital, life, facility capex, …). |
| `data/tco_model_inputs.csv` | Rack and server prices (Morgan Stanley, Bernstein, resellers), electricity price, PUE, useful life, GB300 rack kW — pulled through the `ref` column so the two files cannot drift apart. |
| `data/l08_power_per_gpu.csv` | SemiAnalysis all-in IT power per accelerator (host, network share). |
| `data/cs3_tpu_economics.csv` | SemiAnalysis owner TCO per accelerator-hour: cross-check for every system and calibration target for the TPU. |
| `data/inference_benchmarks.csv` | InferenceX Pareto frontiers (DeepSeek-R1-0528, 1k in / 1k out, no speculative decoding; the MTP frontier for the speculative-decoding columns). |

`ref` syntax in the scenario file: `tco_model_inputs:<system>:<input>[:<basis substring>]`,
`l08_power_per_gpu:<system>`, `cs3_tpu_economics:<system>:<metric>`, `frontier:<benchmark system>` (measured
throughput) and `anchor:<model system>` (modelled throughput = anchor × the system's `tokens_factor_*` rows).
If a `base` value is typed in and also referenced, the model uses the referenced value and prints a warning.

## Formulas (per accelerator, per year)

| Line | Formula |
|---|---|
| Accelerator-system capex *C* | rack or server price ÷ accelerators, or a direct per-accelerator estimate, or (TPU) calibrated — see below |
| Scale-out network & storage *N* | *C* × `network_storage_ratio` (0.26 base, SemiAnalysis GB200 all-in vs rack) |
| Depreciation | (*C* + *N*) ÷ life (straight line) |
| Cost of capital | (*C* + *N*) × [CRF(*r*, life) − 1/life], where CRF(*r*, *n*) = *r* ÷ (1 − (1 + *r*)⁻ⁿ) |
| Vendor margin in price | (*C* ÷ life) × `vendor_margin_share` — a **split** of depreciation, not an extra cost |
| Facility | IT kW × PUE × facility $/MW × CRF(*r*, facility life) |
| Electricity | IT kW × PUE × [floor + (1 − floor) × utilization] × 8,760 h × $/kWh |
| Operations | (*C* + *N*) × `ops_pct_of_it_capex` |
| **$/accelerator-hour (installed)** | sum ÷ 8,760; **useful hour** = ÷ utilization |
| **$/M tokens** | annual cost ÷ (tokens/s × 3,600 × 8,760 × utilization) × 10⁶ — per million *total* (input + output) tokens |
| **Tokens/s per MW** | tokens/s per accelerator ÷ (IT kW × PUE) × 1,000 — at the utility meter, at the reference operating point |
| **Training run** | accelerator-hours = FLOP ÷ (dense FP8 peak × MFU × goodput × 3,600); cost = hours × hourly cost at full power draw |

Calibration (TPU v7 only): Google publishes no price, so capex per chip is solved so that the model's hourly
cost ÷ GB300's equals SemiAnalysis's owner-TCO ratio ($1.21 ÷ $2.31 external; $1.03 ÷ $2.31 for Google itself).
The calibrated capex is then held fixed (± 20 % in the Monte Carlo).

Derived tests in `x14_tco_results.csv` / `x14_tco_operating_points.csv`:

- **Free-chip test:** $/M tokens if the accelerator system cost nothing (network, facility, power and operations still paid).
- **Break-even capex:** the accelerator-system capex that would match GB300's $/M tokens (negative = no price works).
- **Price-cut test:** for rivals cheaper than GB300, the GB300 price cut that matches them and NVIDIA's implied gross
  margin afterwards (content share = vendor margin share ÷ 75 % GAAP gross margin; the cut comes out of NVIDIA's revenue).

## Base-case assumptions (all editable in the scenario file)

| Parameter | Base | Low – high | Basis |
|---|---|---|---|
| Utilization | 70 % | 40 – 90 % | Alibaba 68 %→93 % allocation; Meta ~89 % |
| Electricity | $0.081/kWh | $0.05 – 0.10 | EIA US industrial 2024; PPA; constrained grid |
| PUE | 1.15 | 1.09 – 1.40 | new liquid-cooled hall; Google fleet; air-cooled colo |
| Cost of capital | 8 % | 0 – 12 % | hyperscaler; accounting view; leveraged neocloud |
| IT life | 6 years | 4 – 7 | Microsoft/Alphabet/CoreWeave policy; economic-life cases |
| Facility capex | $12M/MW | $6.6 – 13M | CS7 range; Morgan Stanley (retracted) |
| Network & storage | 0.26 × system | 0.20 – 0.32 | SemiAnalysis GB200; AMCompute |
| Operations | 3 % of IT capex/yr | 2 – 5 % | repo assumption |
| Reference workload | DeepSeek-R1-0528, 1k/1k, 50 tok/s/user | 35 – 100 | InferenceX, as in charts 08/11 |

## Outputs (`scripts/tco/outputs/`)

| File | Content |
|---|---|
| `x14_tco_results.csv` | one row per system: capex, $/hour (installed, useful), SemiAnalysis cross-check, tokens/s, $/M tokens (base, P10/P50/P90), tokens/s per MW, margin share, free-chip / break-even / price-cut tests, training run |
| `x14_tco_cost_stack.csv` | seven cost components per system in $/year, $/hour and $/M tokens |
| `x14_tco_tornado.csv` | one-at-a-time sensitivities: GB300 $/M tokens, and TPU v7 (external) ÷ GB300 $/M |
| `x14_tco_sensitivity_grid.csv` | every system × utilization × $/kWh × life × cost of capital |
| `x14_tco_operating_points.csv` | $/M tokens at 35/50/75/100 tok/s/user, with and without MTP speculative decoding |
| `x14_tco_training_run.csv` | 10²⁷-FLOP run: accelerator-hours, cost, days on 100k accelerators, days per 100 MW |
| `x14_tco_ranking_probability.csv` | Monte Carlo probability that system A is cheaper per token than system B |
| `x14_tco_reconciliation.csv` | walk from layer 12's $1.50/hour GB300 floor to this model's full owner cost |
| `x14_tco_inputs_resolved.csv` | every input after `ref` resolution and calibration (audit trail) |

## What the model leaves out (read before quoting a number)

- **Throughput is the dominant uncertainty.** Only H200, B200, GB300 and MI355X are measured (InferenceX). Rankings
  change with the workload, the interactivity target and the software configuration — speculative decoding (MTP)
  alone cuts measured cost per token 2–10×. Modelled systems keep their 50 tok/s/user multipliers at other points.
- **Prices are analyst estimates**, not list prices; AMD, Google and AWS publish none. Volume discounts, prepayments and
  equity-linked deals (e.g. AMD warrants to OpenAI and Meta) are not modelled.
- No software licences beyond the operations allowance, no taxes or insurance, no residual (resale) value, no
  revenue side except the illustrative token price used in chapter 14's power-constrained example.
- Training MFU for non-NVIDIA platforms at frontier scale is a repo assumption; MI455X's 20 PFLOPS FP8 is not stated
  as dense or sparse.
- The Monte Carlo draws each uncertain input from a triangular distribution (low, base, high) independently; it
  shows how wide the plausible band is, not a calibrated probability.
