#!/usr/bin/env python3
"""Chapter 14 TCO model: owner cost per accelerator-hour, per million tokens and tokens per MW.

Transparent by design: every input lives in ``data/x14_tco_scenarios.csv`` (base / low / high, unit,
basis, confidence and source ids). Rows with a ``ref`` pull their base value from another repo CSV
(``data/tco_model_inputs.csv``, ``data/l08_power_per_gpu.csv``, ``data/cs3_tpu_economics.csv``) or from
the InferenceX throughput frontier in ``data/inference_benchmarks.csv``, so the model never silently
diverges from the rest of the repository. See ``scripts/tco/README.md`` for formulas and caveats.

Run:  ``make tco``  (or ``python3 scripts/tco/tco_model.py``). Outputs go to ``scripts/tco/outputs/``.
Pure Python + pandas; Monte Carlo uses the standard-library ``random`` module with a fixed seed.

Every output is an ESTIMATE. Throughput for Vera Rubin, Helios, TPU and Trainium is modelled, not
measured (flagged "modelled" in the outputs and 🔴 in chapter 14).
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DATA = REPO / "data"
OUT = HERE / "outputs"

SCENARIOS = "x14_tco_scenarios.csv"
WORKLOAD = "DeepSeek-R1-0528 (1k in/1k out)"
SUITE = "SemiAnalysis InferenceX (Pareto frontier, no speculative decoding)"
SUITE_MTP = "SemiAnalysis InferenceX (Pareto frontier, with MTP speculative decoding)"
OPERATING_POINTS = [35, 50, 75, 100]          # tokens/s per user reported in x14_tco_operating_points.csv
GRID = dict(utilisation_pct=[30, 40, 50, 60, 70, 80, 90], electricity_usd_per_kwh=[0.05, 0.081, 0.10, 0.15],
            it_life_years=[3, 4, 5, 6, 7], wacc_pct=[0, 8, 12])
N_DRAWS = 4000
SEED = 14
NVIDIA_GM = 0.75                               # GAAP gross margin, Q2 FY2027 [S405] - used for the price-cut test
REFERENCE = "GB300 NVL72"                      # comparison anchor and calibration reference

SYSTEMS = [  # display order (anchors before the systems that use them is handled by recursion)
    "H200 HGX", "B200 HGX", "GB300 NVL72", "Vera Rubin NVL72", "MI355X platform", "Helios (MI455X)",
    "TPU v7 Ironwood (external)", "TPU v7 Ironwood (Google internal)",
    "Trainium2 (Trn2 UltraServer)", "Trainium3 (Trn3 UltraServer)",
]
COMPONENTS = [  # (key, label) in cost-stack order
    ("hardware", "Accelerator system at cost"),
    ("vendor_margin", "Vendor gross margin in price"),
    ("network_storage", "Scale-out network & storage"),
    ("cost_of_capital", "Cost of capital (IT)"),
    ("facility", "Facility (shell, power & cooling plant)"),
    ("power", "Electricity"),
    ("ops", "Operations & maintenance"),
]
UNCERTAIN_GLOBALS = ["utilisation_pct", "electricity_usd_per_kwh", "pue", "wacc_pct", "it_life_years",
                     "facility_capex_usd_m_per_mw", "network_storage_ratio", "ops_pct_of_it_capex",
                     "power_draw_floor", "training_goodput"]
PER_SYSTEM_DRAWN = ["system_price_usd_m", "capex_per_accelerator_usd_k", "it_kw_per_accelerator",
                    "vendor_margin_share", "training_mfu", "pue"]


# --------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------
def crf(rate: float, years: float) -> float:
    """Capital recovery factor: the constant annual payment that repays 1 over `years` at `rate`."""
    if rate <= 0:
        return 1.0 / years
    return rate / (1.0 - (1.0 + rate) ** (-years))


def _num(x) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return math.nan
    return v


def _frontier(points):
    """Upper envelope of (interactivity, throughput) points (same rule as charts 08/11)."""
    pts = sorted(points)
    env = []
    for x, y in pts:
        if any((x2 >= x and y2 > y) or (x2 > x and y2 >= y) for x2, y2 in pts):
            continue
        env.append((x, y))
    return sorted(env)


def _interp_log(env, target: float) -> float:
    """Log-linear interpolation along the frontier; NaN outside the measured range (no extrapolation)."""
    if len(env) < 2 or target < env[0][0] or target > env[-1][0]:
        return math.nan
    for (x0, y0), (x1, y1) in zip(env, env[1:]):
        if x0 <= target <= x1:
            if x1 == x0:
                return y1
            w = (target - x0) / (x1 - x0)
            return math.exp(math.log(y0) + w * (math.log(y1) - math.log(y0)))
    return math.nan


class Bench:
    """Reads data/inference_benchmarks.csv once and interpolates InferenceX frontiers."""

    def __init__(self) -> None:
        self.df = pd.read_csv(DATA / "inference_benchmarks.csv")

    def tps(self, system: str, interactivity: float, suite: str = SUITE) -> float:
        g = self.df[(self.df.benchmark_suite == suite) & (self.df.model == WORKLOAD) & (self.df.system == system)]
        env = _frontier(list(zip(g.interactivity_tok_s_per_user, g.throughput_tok_s_per_gpu)))
        return _interp_log(env, interactivity)


# --------------------------------------------------------------------------------------
# inputs
# --------------------------------------------------------------------------------------
def _resolve_ref(ref: str) -> float:
    kind, *rest = ref.split(":")
    if kind == "tco_model_inputs":
        t = pd.read_csv(DATA / "tco_model_inputs.csv")
        system, inp = rest[0], rest[1]
        r = t[(t.system == system) & (t.input == inp)]
        if len(rest) > 2:
            r = r[r.basis.astype(str).str.contains(rest[2], regex=False)]
        if r.empty:
            raise KeyError(f"ref not found: {ref}")
        return float(r.value.iloc[0])
    if kind == "l08_power_per_gpu":
        t = pd.read_csv(DATA / "l08_power_per_gpu.csv").set_index("system")
        return float(t.loc[rest[0], "all_in_kw_per_gpu"])
    if kind == "cs3_tpu_economics":
        t = pd.read_csv(DATA / "cs3_tpu_economics.csv")
        r = t[(t.system == rest[0]) & (t.metric == rest[1])]
        if r.empty:
            raise KeyError(f"ref not found: {ref}")
        return float(r.value.iloc[0])
    raise ValueError(f"unknown ref kind {kind!r} in {ref!r}")


class Inputs:
    """Parsed scenario file: globals[param] = (base, low, high); systems[name][param] = (base, low, high)."""

    def __init__(self, path: Path = DATA / SCENARIOS) -> None:
        self.raw = pd.read_csv(path)
        need = {"system", "vendor", "parameter", "base", "low", "high", "unit", "ref", "basis", "confidence",
                "source_id", "notes"}
        missing = need - set(self.raw.columns)
        if missing:
            raise ValueError(f"{path.name}: missing columns {sorted(missing)}")
        self.globals: dict[str, tuple[float, float, float]] = {}
        self.systems: dict[str, dict[str, tuple[float, float, float]]] = {}
        self.vendor: dict[str, str] = {}
        self.anchor: dict[str, str] = {}
        self.frontier: dict[str, str] = {}
        self.warnings: list[str] = []
        for r in self.raw.itertuples(index=False):
            base, low, high = _num(r.base), _num(r.low), _num(r.high)
            ref = r.ref if isinstance(r.ref, str) and r.ref.strip() else ""
            if ref.startswith("anchor:"):
                self.anchor[r.system] = ref.split(":", 1)[1]
            elif ref.startswith("frontier:"):
                self.frontier[r.system] = ref.split(":", 1)[1]
                continue
            elif ref:
                v = _resolve_ref(ref)
                if not math.isnan(base) and abs(base - v) > 1e-9 * max(1.0, abs(v)):
                    self.warnings.append(f"{r.system}/{r.parameter}: base {base} differs from {ref} = {v}; using {v}")
                base = v
            if math.isnan(base):
                continue
            low = base if math.isnan(low) else low
            high = base if math.isnan(high) else high
            if r.system == "All":
                self.globals[r.parameter] = (base, low, high)
            else:
                self.systems.setdefault(r.system, {})[r.parameter] = (base, low, high)
                self.vendor[r.system] = r.vendor
        for s in SYSTEMS:
            if s not in self.systems:
                raise ValueError(f"system {s!r} missing from {SCENARIOS}")

    def base_point(self) -> dict:
        g = {k: v[0] for k, v in self.globals.items()}
        sysp = {s: {k: v[0] for k, v in p.items()} for s, p in self.systems.items()}
        return {"g": g, "s": sysp}


# --------------------------------------------------------------------------------------
# core model
# --------------------------------------------------------------------------------------
class Model:
    def __init__(self, inputs: Inputs | None = None, bench: Bench | None = None) -> None:
        self.inp = inputs or Inputs()
        self.bench = bench or Bench()
        self._tps_cache: dict[tuple[str, float], float] = {}
        self.calibrated: dict[str, float] = {}
        self._calibrate()

    # ---- throughput -------------------------------------------------------------------
    def measured_tps(self, system: str, interactivity: float, suite: str = SUITE) -> float:
        key = (system, interactivity, suite)
        if key not in self._tps_cache:
            self._tps_cache[key] = self.bench.tps(self.inp.frontier[system], interactivity, suite)
        return self._tps_cache[key]

    def tokens_per_s(self, system: str, pt: dict, interactivity: float | None = None) -> float:
        x = interactivity if interactivity is not None else pt["g"]["ref_interactivity_tok_s_per_user"]
        p = pt["s"][system]
        if system in self.inp.frontier:
            meas = p.get("tokens_measurement_factor", pt["g"]["tokens_measurement_factor"])
            return self.measured_tps(system, x) * meas
        anchor = self.inp.anchor[system]
        tps = self.tokens_per_s(anchor, pt, x)
        for k, v in p.items():
            if k.startswith("tokens_factor_"):
                tps *= v
        return tps

    def is_measured(self, system: str) -> bool:
        return system in self.inp.frontier

    # ---- capex ------------------------------------------------------------------------
    def capex_per_accelerator(self, system: str, pt: dict) -> float:
        p = pt["s"][system]
        if "system_price_usd_m" in p:
            return p["system_price_usd_m"] * 1e6 / p["accelerators_per_unit"]
        if "capex_per_accelerator_usd_k" in p:
            return p["capex_per_accelerator_usd_k"] * 1e3
        if system in self.calibrated:
            return self.calibrated[system] * p.get("capex_uncertainty_calibrated", pt["g"]["capex_uncertainty_calibrated"])
        raise KeyError(f"{system}: no capex input")

    def _calibrate(self) -> None:
        """Back out capex for systems with no public price so that hourly owner cost / GB300's equals the
        SemiAnalysis ratio. Done once, at the base point; the result is then held fixed."""
        pt = self.inp.base_point()
        ref_hour = self.evaluate(REFERENCE, pt)["usd_per_hour_installed"]
        for s, p in pt["s"].items():
            if "calibrate_tco_ratio_vs_gb300" not in p:
                continue
            target = ref_hour * p["calibrate_tco_ratio_vs_gb300"] * pt["g"]["hours_per_year"]
            self.calibrated[s] = 1.0  # probe: annual cost is linear in capex, so solve from two points
            a1 = self.evaluate(s, pt)["total"]
            self.calibrated[s] = 2.0
            a2 = self.evaluate(s, pt)["total"]
            slope = a2 - a1
            self.calibrated[s] = (target - (a1 - slope)) / slope

    # ---- one system at one point ------------------------------------------------------
    def evaluate(self, system: str, pt: dict, util_override: float | None = None) -> dict:
        g, p = pt["g"], pt["s"][system]
        gv = lambda k: p.get(k, g.get(k))  # system-level override of a global (e.g. Google's PUE)
        hours = gv("hours_per_year")
        util = (util_override if util_override is not None else gv("utilisation_pct")) / 100.0
        capex = self.capex_per_accelerator(system, pt)
        net = capex * gv("network_storage_ratio")
        it_capex = capex + net
        life, rate = gv("it_life_years"), gv("wacc_pct") / 100.0
        dep_sys, dep_net = capex / life, net / life
        coc = it_capex * (crf(rate, life) - 1.0 / life)
        margin = dep_sys * p["vendor_margin_share"]
        hw = dep_sys - margin
        fac_kw = p["it_kw_per_accelerator"] * gv("pue")
        fac_capex = fac_kw * gv("facility_capex_usd_m_per_mw") * 1e3        # US$ M per MW == US$ K per kW
        facility = fac_capex * crf(rate, gv("facility_life_years"))
        load = gv("power_draw_floor") + (1.0 - gv("power_draw_floor")) * util
        power = fac_kw * load * hours * gv("electricity_usd_per_kwh")
        ops = it_capex * gv("ops_pct_of_it_capex") / 100.0
        comp = dict(hardware=hw, vendor_margin=margin, network_storage=dep_net, cost_of_capital=coc,
                    facility=facility, power=power, ops=ops)
        total = sum(comp.values())
        tps = self.tokens_per_s(system, pt) if system in self.inp.frontier or system in self.inp.anchor else math.nan
        tokens_year = tps * 3600.0 * hours * util
        res = dict(system=system, capex_per_accelerator=capex, it_capex_per_accelerator=it_capex,
                   facility_kw_per_accelerator=fac_kw, facility_capex_per_accelerator=fac_capex,
                   load_factor=load, total=total, usd_per_hour_installed=total / hours,
                   usd_per_hour_useful=total / hours / util, tokens_per_s=tps, tokens_per_year=tokens_year,
                   usd_per_m_tokens=total / tokens_year * 1e6 if tokens_year > 0 else math.nan,
                   tokens_per_s_per_mw=tps / fac_kw * 1000.0,
                   useful_tokens_per_year_per_mw=tokens_year / fac_kw * 1000.0,
                   vendor_margin_share_of_cost=margin / total, **comp)
        # training run on this platform (cluster fully allocated: power at full load)
        if "fp8_dense_pflops" in p and "training_mfu" in p:
            eff = p["fp8_dense_pflops"] * 1e15 * p["training_mfu"] * gv("training_goodput")
            acc_hours = gv("training_run_flop") / eff / 3600.0
            full = power / load if load > 0 else power  # power at 100% draw
            hourly_full = (total - power + full) / hours
            res.update(train_accel_hours=acc_hours, train_usd_per_accel_hour=hourly_full,
                       train_cost_usd=acc_hours * hourly_full,
                       train_days_on_cluster=acc_hours / gv("training_cluster_accelerators") / 24.0,
                       train_cluster_mw=fac_kw * gv("training_cluster_accelerators") / 1000.0,
                       train_days_per_100mw=acc_hours / (100_000.0 / fac_kw) / 24.0)
        return res

    def evaluate_all(self, pt: dict) -> dict[str, dict]:
        return {s: self.evaluate(s, pt) for s in SYSTEMS}

    # ---- derived tests ----------------------------------------------------------------
    def free_chip_and_breakeven(self, pt: dict, res: dict[str, dict]) -> dict[str, dict]:
        """(a) $/M tokens if the accelerator system were free (network, facility, power, ops still paid);
        (b) the accelerator-system capex that would match GB300's $/M tokens; (c) for rivals cheaper than
        GB300, the GB300 price cut needed to match and NVIDIA's implied gross margin after it."""
        g = pt["g"]
        ref = res[REFERENCE]
        out = {}
        for s, r in res.items():
            p = pt["s"][s]
            gv = lambda k: p.get(k, g.get(k))
            life, rate = gv("it_life_years"), gv("wacc_pct") / 100.0
            capex = r["capex_per_accelerator"]
            sys_part = capex * crf(rate, life)            # depreciation + cost of capital on the system itself
            free_total = r["total"] - sys_part
            k = (1 + gv("network_storage_ratio")) * (crf(rate, life) + gv("ops_pct_of_it_capex") / 100.0)
            fixed = r["facility"] + r["power"]
            target = ref["usd_per_m_tokens"] * r["tokens_per_year"] / 1e6
            be = (target - fixed) / k
            row = dict(usd_per_m_tokens_if_system_free=free_total / r["tokens_per_year"] * 1e6,
                       breakeven_capex_per_accelerator_vs_gb300=be,
                       breakeven_vs_current_capex=be / capex if capex else math.nan)
            if s != REFERENCE and r["usd_per_m_tokens"] < ref["usd_per_m_tokens"]:
                pr = pt["s"][REFERENCE]
                kk = (1 + g["network_storage_ratio"]) * (crf(g["wacc_pct"] / 100, g["it_life_years"]) +
                                                         g["ops_pct_of_it_capex"] / 100.0)
                need = (r["usd_per_m_tokens"] * ref["tokens_per_year"] / 1e6 - ref["facility"] - ref["power"]) / kk
                cut = 1 - need / ref["capex_per_accelerator"]
                content = pr["vendor_margin_share"] / NVIDIA_GM * ref["capex_per_accelerator"]
                cost = content * (1 - NVIDIA_GM)
                rev_after = content - (ref["capex_per_accelerator"] - need)
                gm_after = (rev_after - cost) / rev_after if rev_after > 0 else math.nan
                row.update(gb300_price_cut_to_match=cut, nvidia_gm_after_cut=gm_after)
            out[s] = row
        return out


# --------------------------------------------------------------------------------------
# Monte Carlo, tornado, grids
# --------------------------------------------------------------------------------------
def _tri(rng: random.Random, triple: tuple[float, float, float]) -> float:
    base, low, high = triple
    if high <= low:
        return base
    return rng.triangular(low, high, min(max(base, low), high))


def monte_carlo(m: Model, n: int = N_DRAWS, seed: int = SEED) -> pd.DataFrame:
    rng = random.Random(seed)
    inp = m.inp
    rows = []
    for d in range(n):
        g = {k: v[0] for k, v in inp.globals.items()}
        for k in UNCERTAIN_GLOBALS:
            g[k] = _tri(rng, inp.globals[k])
        g["it_life_years"] = round(g["it_life_years"] * 2) / 2   # half-year steps
        sysp = {}
        for s, params in inp.systems.items():
            p = {k: v[0] for k, v in params.items()}
            for k, v in params.items():
                if k in PER_SYSTEM_DRAWN or k.startswith("tokens_factor_"):
                    p[k] = _tri(rng, v)
            if s in inp.frontier:
                p["tokens_measurement_factor"] = _tri(rng, inp.globals["tokens_measurement_factor"])
            if s in m.calibrated:
                p["capex_uncertainty_calibrated"] = _tri(rng, inp.globals["capex_uncertainty_calibrated"])
            sysp[s] = p
        pt = {"g": g, "s": sysp}
        for s in SYSTEMS:
            r = m.evaluate(s, pt)
            rows.append(dict(draw=d, system=s, usd_per_m_tokens=r["usd_per_m_tokens"],
                             usd_per_hour_installed=r["usd_per_hour_installed"],
                             tokens_per_s_per_mw=r["tokens_per_s_per_mw"], tokens_per_s=r["tokens_per_s"],
                             train_cost_usd=r.get("train_cost_usd", math.nan),
                             train_days_on_cluster=r.get("train_days_on_cluster", math.nan)))
    return pd.DataFrame(rows)


TORNADO_GB300 = [  # (scope, parameter, label)
    ("g", "utilisation_pct", "Utilization (%)"),
    ("s", "tokens_measurement_factor", "Tokens/s per GPU (× measured)"),
    ("s", "system_price_usd_m", "Rack price (US$ M)"),
    ("g", "it_life_years", "Depreciation life (years)"),
    ("g", "wacc_pct", "Cost of capital (%)"),
    ("g", "electricity_usd_per_kwh", "Electricity (US$/kWh)"),
    ("g", "facility_capex_usd_m_per_mw", "Facility capex (US$ M/MW)"),
    ("g", "network_storage_ratio", "Network & storage (× rack price)"),
    ("g", "ops_pct_of_it_capex", "Operations (% of IT capex/yr)"),
    ("g", "pue", "PUE"),
    ("s", "it_kw_per_accelerator", "Power per GPU (kW, all-in IT)"),
    ("g", "power_draw_floor", "Idle power floor (share)"),
]
TORNADO_RATIO = [  # (scope, system, parameter, label) for TPU-external $/M ÷ GB300 $/M
    ("s", "TPU v7 Ironwood (external)", "tokens_factor_topology", "TPU pod topology bonus (×)"),
    ("s", "TPU v7 Ironwood (external)", "tokens_factor_fp8_vs_fp4", "TPU FP8 vs Blackwell FP4 (×)"),
    ("s", "GB300 NVL72", "tokens_measurement_factor", "GB300 tokens/s (× measured)"),
    ("s", "B200 HGX", "tokens_measurement_factor", "B200 anchor tokens/s (× measured)"),
    ("s", "TPU v7 Ironwood (external)", "tokens_factor_vs_b200_same_precision", "TPU vs B200 at equal precision (×)"),
    ("s", "GB300 NVL72", "system_price_usd_m", "GB300 rack price (US$ M)"),
    ("s", "TPU v7 Ironwood (external)", "capex_uncertainty_calibrated", "TPU capex (× calibrated)"),
    ("g", None, "wacc_pct", "Cost of capital (%)"),
    ("g", None, "it_life_years", "Depreciation life (years)"),
    ("g", None, "electricity_usd_per_kwh", "Electricity (US$/kWh)"),
    ("g", None, "utilisation_pct", "Utilization (%)"),
    ("g", None, "facility_capex_usd_m_per_mw", "Facility capex (US$ M/MW)"),
]


def _copy(pt: dict) -> dict:
    return {"g": dict(pt["g"]), "s": {k: dict(v) for k, v in pt["s"].items()}}


def tornado(m: Model) -> pd.DataFrame:
    base = m.inp.base_point()
    rows = []
    b0 = m.evaluate(REFERENCE, base)["usd_per_m_tokens"]
    for scope, k, label in TORNADO_GB300:
        triple = (m.inp.globals["tokens_measurement_factor"] if k == "tokens_measurement_factor"
                  else (m.inp.globals[k] if scope == "g" else m.inp.systems[REFERENCE][k]))
        vals = []
        for v in (triple[1], triple[2]):
            pt = _copy(base)
            (pt["g"] if scope == "g" else pt["s"][REFERENCE])[k] = v
            vals.append(m.evaluate(REFERENCE, pt)["usd_per_m_tokens"])
        rows.append(dict(case="GB300 NVL72 $/M tokens", parameter=k, label=label, base_input=triple[0],
                         low_input=triple[1], high_input=triple[2], base_result=b0, result_at_low=vals[0],
                         result_at_high=vals[1], swing=abs(vals[1] - vals[0])))
    tpu = "TPU v7 Ironwood (external)"
    r0 = m.evaluate(tpu, base)["usd_per_m_tokens"] / b0
    for scope, system, k, label in TORNADO_RATIO:
        if k in ("tokens_measurement_factor", "capex_uncertainty_calibrated"):
            triple = m.inp.globals[k]
        elif scope == "g":
            triple = m.inp.globals[k]
        else:
            triple = m.inp.systems[system][k]
        vals = []
        for v in (triple[1], triple[2]):
            pt = _copy(base)
            (pt["g"] if scope == "g" else pt["s"][system])[k] = v
            vals.append(m.evaluate(tpu, pt)["usd_per_m_tokens"] / m.evaluate(REFERENCE, pt)["usd_per_m_tokens"])
        rows.append(dict(case="TPU v7 (external) $/M ÷ GB300 $/M", parameter=f"{system or 'All'}:{k}", label=label,
                         base_input=triple[0], low_input=triple[1], high_input=triple[2], base_result=r0,
                         result_at_low=vals[0], result_at_high=vals[1], swing=abs(vals[1] - vals[0])))
    return pd.DataFrame(rows)


def sensitivity_grid(m: Model) -> pd.DataFrame:
    base = m.inp.base_point()
    rows = []
    for s in SYSTEMS:
        for u in GRID["utilisation_pct"]:
            for e in GRID["electricity_usd_per_kwh"]:
                for life in GRID["it_life_years"]:
                    for w in GRID["wacc_pct"]:
                        pt = _copy(base)
                        pt["g"].update(utilisation_pct=u, electricity_usd_per_kwh=e, it_life_years=life, wacc_pct=w)
                        r = m.evaluate(s, pt)
                        rows.append(dict(system=s, utilisation_pct=u, electricity_usd_per_kwh=e, it_life_years=life,
                                         wacc_pct=w, usd_per_hour_installed=r["usd_per_hour_installed"],
                                         usd_per_hour_useful=r["usd_per_hour_useful"],
                                         usd_per_m_tokens=r["usd_per_m_tokens"]))
    return pd.DataFrame(rows)


def operating_points(m: Model, points=OPERATING_POINTS) -> pd.DataFrame:
    """$/M tokens at several interactivity targets. Modelled systems keep their 50 tok/s/user multipliers
    (a simplification flagged in the README); MTP columns use the speculative-decoding frontier."""
    base = m.inp.base_point()
    rows = []
    for x in points:
        pt = _copy(base)
        pt["g"]["ref_interactivity_tok_s_per_user"] = x
        res = m.evaluate_all(pt)
        ok = {s: r for s, r in res.items() if r["usd_per_m_tokens"] == r["usd_per_m_tokens"]}
        extra = m.free_chip_and_breakeven(pt, ok) if REFERENCE in ok else {}
        for s in SYSTEMS:
            r = res[s]
            e = extra.get(s, {})
            mtp = m.measured_tps(s, x, SUITE_MTP) if m.is_measured(s) else math.nan
            rows.append(dict(system=s, interactivity_tok_s_per_user=x, basis="measured" if m.is_measured(s) else "modelled",
                             tokens_per_s=r["tokens_per_s"], usd_per_m_tokens=r["usd_per_m_tokens"],
                             usd_per_m_tokens_if_system_free=e.get("usd_per_m_tokens_if_system_free", math.nan),
                             gb300_price_cut_to_match=e.get("gb300_price_cut_to_match", math.nan),
                             nvidia_gm_after_cut=e.get("nvidia_gm_after_cut", math.nan),
                             tokens_per_s_mtp=mtp,
                             usd_per_m_tokens_mtp=(r["total"] / (mtp * 3600 * pt["g"]["hours_per_year"] *
                                                                 pt["g"]["utilisation_pct"] / 100) * 1e6)
                             if mtp == mtp else math.nan))
    return pd.DataFrame(rows)


def reconciliation(m: Model) -> pd.DataFrame:
    """Walk from layer 12's 'floor' ($1.50 per installed GB300 GPU-hour) to this model's full owner cost."""
    base = m.inp.base_point()
    g = base["g"]
    r = m.evaluate(REFERENCE, base)
    t = pd.read_csv(DATA / "tco_model_inputs.csv")
    rack_kw = float(t[(t.system == REFERENCE) & (t.input == "rack_power_kw")].value.iloc[0])
    n = base["s"][REFERENCE]["accelerators_per_unit"]
    hours = g["hours_per_year"]
    dep = r["it_capex_per_accelerator"] / g["it_life_years"] / hours
    pw_floor = rack_kw / n * g["pue"] * g["electricity_usd_per_kwh"]
    steps = [("Layer 12 floor: straight-line IT depreciation", dep),
             ("Layer 12 floor: power at rack kW, 100% draw", pw_floor),
             ("+ cost of capital on IT (8%)", r["cost_of_capital"] / hours),
             ("+ facility capex, annualised", r["facility"] / hours),
             ("+ operations & maintenance", r["ops"] / hours),
             ("± power on all-in kW at the load factor", r["power"] / hours - pw_floor)]
    df = pd.DataFrame(steps, columns=["step", "usd_per_hour"])
    df["cumulative"] = df.usd_per_hour.cumsum()
    df.loc[len(df)] = ["= model owner cost per installed GPU-hour", r["usd_per_hour_installed"], r["usd_per_hour_installed"]]
    return df


# --------------------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------------------
def run(write: bool = True, verbose: bool = True) -> dict[str, pd.DataFrame]:
    m = Model()
    base = m.inp.base_point()
    res = m.evaluate_all(base)
    extra = m.free_chip_and_breakeven(base, res)
    mc = monte_carlo(m)
    q = mc.groupby("system").quantile([0.1, 0.5, 0.9]).unstack()
    ref_draws = mc[mc.system == REFERENCE].set_index("draw").usd_per_m_tokens
    rows, stack = [], []
    for s in SYSTEMS:
        r = res[s]
        p = base["s"][s]
        sa = p.get("sa_owner_tco_usd_per_hour", math.nan)
        other = mc[mc.system == s].set_index("draw").usd_per_m_tokens
        row = dict(system=s, vendor=m.inp.vendor[s], throughput_basis="measured" if m.is_measured(s) else "modelled",
                   anchor=m.inp.anchor.get(s, ""), accelerators_per_unit=p["accelerators_per_unit"],
                   capex_per_accelerator_usd=r["capex_per_accelerator"], capex_calibrated=s in m.calibrated,
                   it_capex_per_accelerator_usd=r["it_capex_per_accelerator"],
                   facility_kw_per_accelerator=r["facility_kw_per_accelerator"],
                   usd_per_hour_installed=r["usd_per_hour_installed"], usd_per_hour_useful=r["usd_per_hour_useful"],
                   sa_owner_tco_usd_per_hour=sa,
                   model_vs_sa_owner_tco=r["usd_per_hour_installed"] / sa if sa == sa else math.nan,
                   tokens_per_s=r["tokens_per_s"], usd_per_m_tokens=r["usd_per_m_tokens"],
                   usd_per_m_tokens_p10=q.loc[s, ("usd_per_m_tokens", 0.1)],
                   usd_per_m_tokens_p50=q.loc[s, ("usd_per_m_tokens", 0.5)],
                   usd_per_m_tokens_p90=q.loc[s, ("usd_per_m_tokens", 0.9)],
                   usd_per_hour_p10=q.loc[s, ("usd_per_hour_installed", 0.1)],
                   usd_per_hour_p90=q.loc[s, ("usd_per_hour_installed", 0.9)],
                   tokens_per_s_per_mw=r["tokens_per_s_per_mw"],
                   tokens_per_s_per_mw_p10=q.loc[s, ("tokens_per_s_per_mw", 0.1)],
                   tokens_per_s_per_mw_p90=q.loc[s, ("tokens_per_s_per_mw", 0.9)],
                   useful_tokens_per_year_per_mw=r["useful_tokens_per_year_per_mw"],
                   vendor_margin_share_of_cost=r["vendor_margin_share_of_cost"],
                   p_gb300_cheaper_per_token=float((ref_draws < other).mean()) if s != REFERENCE else math.nan,
                   train_accel_hours_m=r.get("train_accel_hours", math.nan) / 1e6,
                   train_cost_usd_m=r.get("train_cost_usd", math.nan) / 1e6,
                   train_cost_usd_m_p10=q.loc[s, ("train_cost_usd", 0.1)] / 1e6,
                   train_cost_usd_m_p90=q.loc[s, ("train_cost_usd", 0.9)] / 1e6,
                   train_days_on_cluster=r.get("train_days_on_cluster", math.nan),
                   train_days_p10=q.loc[s, ("train_days_on_cluster", 0.1)],
                   train_days_p90=q.loc[s, ("train_days_on_cluster", 0.9)],
                   train_cluster_mw=r.get("train_cluster_mw", math.nan),
                   train_days_per_100mw=r.get("train_days_per_100mw", math.nan),
                   **extra[s])
        rows.append(row)
        for key, label in COMPONENTS:
            stack.append(dict(system=s, component=key, label=label, usd_per_year=r[key],
                              usd_per_accelerator_hour=r[key] / base["g"]["hours_per_year"],
                              usd_per_m_tokens=r[key] / r["tokens_per_year"] * 1e6, share=r[key] / r["total"]))
    results = pd.DataFrame(rows)
    stack_df = pd.DataFrame(stack)
    resolved = []
    for s in SYSTEMS:
        for k, v in m.inp.systems[s].items():
            resolved.append(dict(system=s, parameter=k, base=v[0], low=v[1], high=v[2]))
        if s in m.calibrated:
            resolved.append(dict(system=s, parameter="capex_per_accelerator_usd (calibrated)", base=m.calibrated[s],
                                 low=m.calibrated[s] * m.inp.globals["capex_uncertainty_calibrated"][1],
                                 high=m.calibrated[s] * m.inp.globals["capex_uncertainty_calibrated"][2]))
    for k, v in m.inp.globals.items():
        resolved.append(dict(system="All", parameter=k, base=v[0], low=v[1], high=v[2]))
    out = dict(results=results, cost_stack=stack_df, tornado=tornado(m), sensitivity_grid=sensitivity_grid(m),
               operating_points=operating_points(m), reconciliation=reconciliation(m),
               inputs_resolved=pd.DataFrame(resolved))
    out["training_run"] = results[["system", "vendor", "train_accel_hours_m", "train_cost_usd_m", "train_cost_usd_m_p10",
                                   "train_cost_usd_m_p90", "train_days_on_cluster", "train_days_p10", "train_days_p90",
                                   "train_cluster_mw", "train_days_per_100mw"]].copy()
    wide = mc.pivot(index="draw", columns="system", values="usd_per_m_tokens")
    out["ranking_probability"] = pd.DataFrame(
        [dict(system=a, **{f"p_cheaper_than::{b}": float((wide[a] < wide[b]).mean()) if a != b else math.nan
                           for b in SYSTEMS}) for a in SYSTEMS])
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        for name, df in out.items():
            df.to_csv(OUT / f"x14_tco_{name}.csv", index=False, float_format="%.6g")
    if verbose:
        for w in m.inp.warnings:
            print("warning:", w)
        cols = ["system", "throughput_basis", "capex_per_accelerator_usd", "usd_per_hour_installed",
                "sa_owner_tco_usd_per_hour", "tokens_per_s", "usd_per_m_tokens", "usd_per_m_tokens_p10",
                "usd_per_m_tokens_p90", "tokens_per_s_per_mw", "vendor_margin_share_of_cost"]
        with pd.option_context("display.width", 220, "display.max_columns", 20, "display.float_format", "{:,.3f}".format):
            print(results[cols].to_string(index=False))
        print(f"\nwrote {len(out)} files to {OUT.relative_to(REPO)}/ (all values are estimates)")
    return out


if __name__ == "__main__":
    run(write="--no-write" not in sys.argv[1:])
