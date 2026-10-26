"""Validate calculations and source preservation without changing source files.

Run after run_all.py. Writes checks.json and source_inventory.csv under
outputs/validation. These checks establish reproducibility and stated physical
invariants, not that illustrative inputs have been empirically validated.
"""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

import ahp as H
import model as M
import sources as S

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def source_inventory(protected, approved_changes=None):
    """All source bytes on disk, including every wildcard registry match."""
    registry = {}
    approved_changes = approved_changes or {}
    for ds_id, name, title, _ in S.DATAGOVSG:
        registry[f"data/raw/datagovsg/{name}"] = (title, f"https://data.gov.sg/datasets/{ds_id}/view")
    for url, name, title, _ in S.DOCUMENTS:
        registry[f"data/raw/docs/{name}"] = (title, url)
    for url, name, title, _ in S.CSV:
        registry[f"data/raw/csv/{name}"] = (title, url)
    for title, url, pattern, _ in S.MANUAL:
        for path in (ROOT / "data/manual").glob(pattern):
            registry[str(path.relative_to(ROOT))] = (title, url)
    paths = set(ROOT / p for p in protected)
    for folder in ("data/raw", "data/manual", "data/verification"):
        if (ROOT / folder).exists():
            paths.update(p for p in (ROOT / folder).rglob("*")
                         if p.is_file() and p.suffix.lower() in {".pdf", ".csv", ".xlsx", ".html", ".json"})
    records = []
    for path in sorted(paths):
        relative = str(path.relative_to(ROOT))
        title, url = registry.get(relative, ("", ""))
        if "/weather/" in relative:
            title, url = "Open-Meteo hourly archive for Jurong Island", "https://archive-api.open-meteo.com/v1/archive"
        exists = path.exists()
        current_hash = digest(path) if exists else ""
        baseline_hash = protected.get(relative, "")
        approved = approved_changes.get(relative, {})
        acknowledged = bool(baseline_hash and approved.get("baseline_sha256") == baseline_hash
                            and approved.get("approved_sha256") == current_hash
                            and current_hash != baseline_hash)
        preservation = ("unchanged" if baseline_hash == current_hash and baseline_hash
                        else "acknowledged_external_change" if acknowledged
                        else "unapproved_change_or_missing" if baseline_hash
                        else "not_in_pre_edit_snapshot")
        records.append(dict(file=relative, bytes=path.stat().st_size if exists else 0,
                            sha256=current_hash, title=title, registry_url=url,
                            provenance_status="registry mapped" if url else "local source; exact URL not mapped here",
                            protected=bool(baseline_hash), baseline_sha256=baseline_hash,
                            unchanged=(current_hash == baseline_hash) if baseline_hash else "not in pre-edit snapshot",
                            preservation_status=preservation,
                            acknowledged_change_reason=approved.get("reason", "") if acknowledged else "",
                            exists=exists))
    return pd.DataFrame(records)


def compare_frame(path, expected, keys):
    actual = pd.read_csv(path)
    if set(expected.columns) - set(actual.columns):
        raise AssertionError(f"Missing columns: {sorted(set(expected.columns) - set(actual.columns))}")
    actual = actual.sort_values(keys).reset_index(drop=True)
    expected = expected.sort_values(keys).reset_index(drop=True)
    if len(actual) != len(expected):
        raise AssertionError(f"Row count {len(actual)} versus expected {len(expected)}")
    max_diff = 0.0
    for col in expected.columns:
        if pd.api.types.is_numeric_dtype(expected[col]):
            np.testing.assert_allclose(actual[col], expected[col], rtol=1e-10, atol=1e-8,
                                       equal_nan=True, err_msg=f"Mismatch in {path.name}:{col}")
            diff = np.abs(actual[col].to_numpy() - expected[col].to_numpy())
            if np.isfinite(diff).any():
                max_diff = max(max_diff, float(np.nanmax(diff)))
        else:
            if actual[col].fillna("").tolist() != expected[col].fillna("").tolist():
                raise AssertionError(f"Mismatch in {path.name}:{col}")
    return {"rows": len(expected), "columns_checked": len(expected.columns), "max_absolute_difference": max_diff}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protected-manifest", type=Path,
                        default=None)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/validation")
    parser.add_argument("--approved-changes", type=Path, default=ROOT / "config/approved_source_changes.json")
    parser.add_argument("--skip-saved-tables", action="store_true", help="For a pre-build core check only")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.protected_manifest is None:
        original = Path("/tmp/ssa_rebuild/protected_sources.json")
        retained = args.output_dir / "protected_sources.json"
        args.protected_manifest = retained if retained.exists() else original
    checks = []

    def check(name, fn):
        try:
            details = fn()
            checks.append(dict(name=name, status="pass", details=details))
        except Exception as exc:
            checks.append(dict(name=name, status="fail", details=f"{type(exc).__name__}: {exc}"))

    p = M.load_params()
    L, C, D = M.lca(p), M.lcc(p), M.demand(p)

    def source_check():
        if not args.protected_manifest.exists():
            raise FileNotFoundError(f"Pre-edit source snapshot missing: {args.protected_manifest}")
        protected = json.loads(args.protected_manifest.read_text())
        # Preserve the original baseline alongside the report for a portable
        # recheck. Never replace it with current file hashes after a mismatch.
        baseline_copy = args.output_dir / "protected_sources.json"
        if baseline_copy.resolve() != args.protected_manifest.resolve():
            baseline_copy.write_text(json.dumps(protected, indent=2) + "\n")
        approved = json.loads(args.approved_changes.read_text()) if args.approved_changes.exists() else {}
        inventory = source_inventory(protected, approved)
        inventory.to_csv(args.output_dir / "source_inventory.csv", index=False)
        selected = inventory[inventory.protected]
        bad = selected[selected.preservation_status == "unapproved_change_or_missing"]
        if len(bad):
            raise AssertionError(f"Protected source files changed or missing: {bad.file.tolist()}")
        acknowledged = selected[selected.preservation_status == "acknowledged_external_change"]
        return {"protected_files_unchanged": int((selected.preservation_status == "unchanged").sum()),
                "acknowledged_external_changes": acknowledged[["file", "baseline_sha256", "sha256", "acknowledged_change_reason"]].to_dict("records"),
                "original_baseline_retained": True, "inventory_files": len(inventory),
                "unmapped_exact_urls": int((inventory.registry_url == "").sum()),
                "scope": "Byte preservation only; a matching hash does not verify source claims"}
    check("protected_source_hashes", source_check)

    def weather_check():
        weather = pd.read_csv(ROOT / "data/raw/weather/openmeteo_jurong_island_hourly_2015_2025.csv")
        time = pd.to_datetime(weather.time)
        expected = pd.date_range("2015-01-01", "2025-12-31 23:00", freq="h")
        if not pd.DatetimeIndex(time).equals(expected):
            raise AssertionError("Missing, duplicate or out-of-order hourly timestamps")
        if weather.isna().any().any():
            raise AssertionError("Missing hourly values")
        if not weather.relative_humidity_2m.between(0, 100).all():
            raise AssertionError("Relative humidity outside 0-100 percent")
        for threshold in (27, 28, 29, 30, 31, 32, 35):
            np.testing.assert_allclose(M.trim_hour_share({**p, "trim_threshold": threshold}),
                                       (weather.temperature_2m > threshold).mean(), atol=1e-14)
        return {"hourly_records": len(weather), "missing_values": 0,
                "exact_exceedance_thresholds_checked": [27, 28, 29, 30, 31, 32, 35]}
    check("weather_completeness_and_exceedance", weather_check)

    def water_balance():
        combinations = 0
        for coc in (6, 8, 12):
            for recovery in (0, 0.5, 0.7, 1):
                q = {**p, "coc_best": coc, "blowdown_recovery": recovery}
                f = M.tower_flows(q)
                np.testing.assert_allclose(f["makeup"], f["evaporation"] + f["discharge"])
                np.testing.assert_allclose(f["gross_blowdown"], f["recovered"] + f["discharge"])
                np.testing.assert_allclose(M.lca(q).loc["A3", "kwh_onsite"], f["recovered"] * q["sec_hicoc"])
                combinations += 1
        return {"water_balance_cases": combinations, "base_flows": M.tower_flows(p)}
    check("tower_water_and_recovery_energy_balance", water_balance)

    def accounting_check():
        np.testing.assert_allclose(C.social_cost,
            C.water_cost_social + C.onsite_capex + C.onsite_energy + C.dc_energy_delta + C.discharge_cost)
        np.testing.assert_allclose(C.operator_cost,
            C.operator_water + C.operator_capex + C.operator_onsite_energy + C.operator_dc_energy_delta)
        np.testing.assert_allclose(L.gwp_total, L.gwp_water_energy + L.gwp_nonenergy + L.gwp_dc_delta)
        np.testing.assert_allclose(L.gwp_dc_delta, L.kwh_dc_delta * L.ef_grid)
        np.testing.assert_allclose(M.it_energy(p, "S1")[2035], 200 * p["util"] * 8760)
        if p["mw_basis_it_share"] != 1 or p["tariff_newater"] != 2.5:
            raise AssertionError("Verified IT-load basis or all-in NEWater tariff regressed")
        return {"four_strategies_balanced": True, "primary_grid_credit": "none",
                "mature_annual_S1_MWh_IT": M.it_energy(p, "S1")[2035]}
    check("energy_ghg_cost_accounting", accounting_check)

    def capital_check():
        capital_pv = []
        for utilisation in (0.5, 0.85):
            q = {**p, "util": utilisation}
            full = M.npc(q).set_index(["scenario", "strategy"])
            zero = M.npc({**q, "capex_dry_premium": 0}).set_index(["scenario", "strategy"])
            capital_pv.append(float(full.loc[("S1", "A4"), "npc_sgd"] - zero.loc[("S1", "A4"), "npc_sgd"]))
        np.testing.assert_allclose(capital_pv[0], capital_pv[1], rtol=1e-10)
        annual = 200 * p["capex_dry_premium"] * M.crf(p["disc_social"], p["life_dc_cooling"])
        expected = sum(annual / (1 + p["disc_social"] / 100) ** (y - 2026) for y in M.YEARS)
        np.testing.assert_allclose(capital_pv, expected, rtol=1e-10)
        return {"fixed_A4_S1_capital_service_PV_SGD": capital_pv[0],
                "residual_basis": "Remaining service annuities; not an estimated resale value"}
    check("fixed_commissioned_capital_during_ramp", capital_check)

    def monotonicity_check():
        larger_water = M.demand({**p, "wue_base": p["wue_base"] * 1.1})
        np.testing.assert_allclose(larger_water.water_m3, D.water_m3 * 1.1)
        high_desal = M.lca({**p, "sec_desal": p["sec_desal"] * 1.1})
        if high_desal.loc["A1", "gwp_total"] <= L.loc["A1", "gwp_total"]:
            raise AssertionError("Higher desal energy did not raise GHG")
        if M.wue_by_strategy({**p, "trim_threshold": 31})[0]["A4"] >= L.loc["A4", "wue"]:
            raise AssertionError("Higher trim threshold did not lower water demand")
        costly_dry = M.lcc({**p, "dpue_dry": p["dpue_dry"] + 0.01})
        if costly_dry.loc["A4", "social_cost"] <= C.loc["A4", "social_cost"]:
            raise AssertionError("Higher dry-rejection penalty did not increase cost")
        residual = M.lca(p, residual_source="desal")
        np.testing.assert_allclose(residual.wue, L.wue)
        if not (residual.loc[["A3", "A4"], "gwp_total"] > L.loc[["A3", "A4"], "gwp_total"]).all():
            raise AssertionError("Desal residual source did not increase modeled GHG")
        return {"checks": ["demand linearity", "desal energy", "trim exposure", "dry cost", "residual source"]}
    check("input_response_sanity", monotonicity_check)

    def ahp_check():
        matrices = {"main:" + key: H.pairwise(value) for key, value in H.WEIGHT_SCENARIOS.items()}
        matrices.update({"sub:" + key: H.pairwise(value[0]) for key, value in H.SUB_PAIRWISE.items()})
        matrices.update({"qualitative:" + key: H.pairwise(value[0]) for key, value in H.QUAL_PAIRWISE.items()})
        max_cr = 0.0
        for name, matrix in matrices.items():
            w, lam, ci, cr = H.AHPmat(matrix)
            vals, vecs = np.linalg.eig(matrix)
            k = np.argmax(vals.real)
            independent = np.abs(vecs[:, k].real)
            independent /= independent.sum()
            np.testing.assert_allclose(w, independent, atol=1e-10, err_msg=name)
            np.testing.assert_allclose(matrix @ w, lam * w, atol=1e-9, err_msg=name)
            np.testing.assert_allclose(matrix * matrix.T, 1, atol=1e-12, err_msg=name)
            if np.any(w <= 0) or cr > 0.1:
                raise AssertionError(f"Invalid priorities or CR above 0.1: {name}")
            max_cr = max(max_cr, float(cr))
        # A consistent matrix has an exact priority oracle, independent of the solver.
        oracle = np.array([0.1, 0.2, 0.3, 0.4])
        w, _, _, cr = H.AHPmat(oracle[:, None] / oracle[None, :])
        np.testing.assert_allclose(w, oracle, atol=1e-10)
        np.testing.assert_allclose(cr, 0, atol=1e-10)
        return {"judgment_matrices": len(matrices), "maximum_CR": max_cr,
                "consistent_ratio_oracle": "passed", "meaning": "Consistency does not establish stakeholder validity"}
    check("ahp_eigenvectors_reciprocity_and_consistency", ahp_check)

    if not args.skip_saved_tables:
        check("saved_demand_reproduction", lambda: compare_frame(M.TAB / "demand_annual.csv", D, ["scenario", "strategy", "year"]))
        check("saved_lca_reproduction", lambda: compare_frame(M.TAB / "lca_inventory.csv", L.reset_index(), ["strategy"]))
        check("saved_lcc_reproduction", lambda: compare_frame(M.TAB / "lcc_per_mwh.csv", C.reset_index(), ["strategy"]))
        expected_npc = pd.concat([M.npc(p, D, perspective=view) for view in ("social", "operator")], ignore_index=True)
        check("saved_npc_reproduction", lambda: compare_frame(M.TAB / "npc_by_scenario.csv", expected_npc, ["perspective", "scenario", "strategy"]))
        def saved_ahp():
            saved = pd.read_csv(M.TAB / "ahp_scores_by_scenario.csv")
            maximum = 0.0
            for scenario in H.WEIGHT_SCENARIOS:
                expected = H.ahp_scores(L, C, scenario)
                actual = saved[saved.weight_scenario == scenario].set_index("strategy").loc[M.STRATEGIES]
                np.testing.assert_allclose(actual.score, expected, atol=1e-9)
                np.testing.assert_array_equal(actual["rank"].to_numpy(), np.argsort(np.argsort(-expected)) + 1)
                maximum = max(maximum, float(np.abs(actual.score.to_numpy() - expected).max()))
            return {"scenario_scores_checked": len(saved), "max_absolute_difference": maximum}
        check("saved_ahp_reproduction", saved_ahp)

    report = dict(run_time_singapore=datetime.now(ZoneInfo("Asia/Singapore")).isoformat(),
                  overall="pass" if all(c["status"] == "pass" for c in checks) else "fail",
                  build_scope="core-only; saved outputs not checked" if args.skip_saved_tables else "core and saved output reproduction",
                  model_scope=M.MODEL_SCOPE, checks=checks,
                  limitations=["Checks do not validate illustrative capex, PUE penalties or future commissioning dates.",
                               "AHP judgments and Monte Carlo distributions are analyst assumptions, not elicited probabilities.",
                               "Common facility impacts and differential cooling-equipment embodied emissions remain outside the screening boundary."])
    (args.output_dir / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"overall": report["overall"], "passed": sum(c["status"] == "pass" for c in checks),
                      "failed": [c for c in checks if c["status"] == "fail"], "report": str(args.output_dir / "checks.json")}, indent=2))
    return 0 if report["overall"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
