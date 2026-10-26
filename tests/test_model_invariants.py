"""Physical and accounting checks for the screening model; no output writers."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import model as m


class ModelInvariants(unittest.TestCase):
    def setUp(self):
        self.p = m.load_params()

    def test_recovery_conserves_water_and_charges_only_recovered_flow(self):
        for coc in (6, 8, 12):
            for recovery in (0, 0.5, 1):
                p = {**self.p, "coc_best": coc, "blowdown_recovery": recovery}
                f = m.tower_flows(p)
                self.assertAlmostEqual(f["gross_blowdown"], f["recovered"] + f["discharge"])
                self.assertAlmostEqual(f["makeup"], f["evaporation"] + f["discharge"])
                L = m.lca(p)
                self.assertAlmostEqual(L.loc["A3", "kwh_onsite"], f["recovered"] * p["sec_hicoc"])
                self.assertAlmostEqual(L.loc["A3", "blowdown_discharge_m3"], f["discharge"])
        f = m.tower_flows(self.p)
        self.assertAlmostEqual(f["recovered"], 0.14)
        self.assertAlmostEqual(f["discharge"], 0.06)

    def test_weather_uses_exact_archive_exceedance(self):
        raw = pd.read_csv(m.ROOT / "data/raw/weather/openmeteo_jurong_island_hourly_2015_2025.csv")
        for threshold in (28, 29, 30, 31):
            self.assertAlmostEqual(m.trim_hour_share({**self.p, "trim_threshold": threshold}),
                                   (raw.temperature_2m > threshold).mean())

    def test_it_capacity_is_not_divided_by_pue(self):
        self.assertEqual(self.p["mw_basis_it_share"], 1)
        self.assertAlmostEqual(m.it_energy(self.p, "S1")[2035],
                               200 * self.p["util"] * 8760)
        self.assertEqual(m.commissioned_it_mw(self.p, "S1", 2027), 200)
        self.assertEqual(m.commissioned_it_mw(self.p, "S1", 2026), 0)

    def test_common_liquid_cooling_has_no_exclusive_energy_credit(self):
        p = {**self.p, "dpue_liquid": -0.9, "dc_green_share": 1}
        L = m.lca(p)
        self.assertAlmostEqual(L.loc["A4", "kwh_dc_delta"], p["dpue_dry"] * 1000)
        self.assertAlmostEqual(L.loc["A4", "gwp_dc_delta"],
                               L.loc["A4", "kwh_dc_delta"] * L.loc["A4", "ef_grid"])
        self.assertTrue((L.gwp_total >= 0).all())

    def test_green_pathway_requires_explicit_nonzero_factor(self):
        with self.assertRaises(ValueError):
            m.lca({**self.p, "dc_green_share_scenario": 0.5})
        p = {**self.p, "dc_green_share_scenario": 0.5, "dc_green_ef_scenario": 0.15}
        L = m.lca(p)
        self.assertAlmostEqual(L.loc["A4", "ef_dc"], 0.5 * (L.loc["A4", "ef_grid"] + 0.15))
        self.assertGreater(L.loc["A4", "gwp_dc_delta"], 0)

    def test_residual_source_changes_only_reducing_options_supply(self):
        Ln = m.lca(self.p)
        Ld = m.lca(self.p, residual_source="desal")
        np.testing.assert_allclose(Ln.wue, Ld.wue)
        pd.testing.assert_frame_equal(Ln.loc[["A1", "A2"]], Ld.loc[["A1", "A2"]])
        self.assertTrue((Ld.loc[["A3", "A4"], "kwh_production"] > Ln.loc[["A3", "A4"], "kwh_production"]).all())

    def test_operator_and_social_energy_use_their_own_prices(self):
        L = m.lca(self.p)
        C = m.lcc(self.p, L)
        self.assertAlmostEqual(C.loc["A4", "dc_energy_delta"], L.loc["A4", "kwh_dc_delta"] * self.p["price_elec_plant"])
        self.assertAlmostEqual(C.loc["A4", "dc_energy_delta_operator"], L.loc["A4", "kwh_dc_delta"] * self.p["price_elec"])
        self.assertTrue((C.discharge_cost == 0).all())

    def test_capital_present_value_does_not_shrink_with_utilisation(self):
        # Difference between equipment and zero-equipment cases isolates
        # capital from energy and water costs, even in ramp years.
        caps = []
        for util in (0.5, 0.85):
            p = {**self.p, "util": util}
            with_cap = m.npc(p).set_index(["scenario", "strategy"])
            without_cap = m.npc({**p, "capex_dry_premium": 0}).set_index(["scenario", "strategy"])
            caps.append(with_cap.loc[("S1", "A4"), "npc_sgd"] - without_cap.loc[("S1", "A4"), "npc_sgd"])
        self.assertAlmostEqual(caps[0], caps[1], places=6)
        annual = 200 * self.p["capex_dry_premium"] * m.crf(self.p["disc_social"], self.p["life_dc_cooling"])
        expected = sum(annual / (1 + self.p["disc_social"] / 100) ** (y - 2026) for y in m.YEARS)
        self.assertAlmostEqual(caps[0], expected, places=6)

    def test_service_annuity_equals_capital_less_residual_value(self):
        r = self.p["disc_social"] / 100
        n = int(self.p["life_dc_cooling"])
        h = len(m.YEARS)
        cap = self.p["capex_dry_premium"]
        annuity = cap * m.crf(self.p["disc_social"], n)
        residual_at_h = sum(annuity / (1 + r) ** k for k in range(1, n - h + 1))
        pv_service = sum(annuity / (1 + r) ** k for k in range(1, h + 1))
        self.assertAlmostEqual(pv_service, cap - residual_at_h / (1 + r) ** h)


if __name__ == "__main__":
    unittest.main()
