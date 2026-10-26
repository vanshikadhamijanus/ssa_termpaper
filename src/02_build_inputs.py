"""
Step 2 - turn data/raw/ into tidy, analysis-ready tables in data/processed/.

    python src/02_build_inputs.py

Outputs
-------
grid_emission_factor.csv        EMA grid EF 2005-2024 (+ OWID carbon intensity for comparison)
water_sales.csv                 National potable / NEWater sales, million m3/yr (long format)
water_tariffs.csv               NEWater and industrial water tariffs + waterborne fee
water_prices_current.csv        All-in operator prices used by the model, before GST
electricity_tariff_annual.csv   SingStat electricity tariffs, cents/kWh (long format)
electricity_gen_consumption.csv SingStat electricity generation & consumption, GWh (long format)
weather_monthly.csv             Monthly dry-bulb / wet-bulb stats for the DC site (Jurong Island)
weather_climatology.csv         Average year (by calendar month) + dry-cooler feasibility hours
wue_heat_balance.csv            First-principles WUE vs cycles of concentration (calibration check)
scale_check.txt                 Order-of-magnitude check: DC-CFA2 water vs national water sales
"""
from pathlib import Path

import numpy as np
import pandas as pd

from model import load_params, wue_by_strategy, STRATEGY_NAME

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
CFG = ROOT / "config"


def singstat_wide_to_long(path, value_name):
    """SingStat tables on data.gov.sg are wide: DataSeries x year columns."""
    df = pd.read_csv(path)
    df["DataSeries"] = df["DataSeries"].str.strip()
    long = df.melt(id_vars="DataSeries", var_name="period", value_name=value_name)
    long[value_name] = pd.to_numeric(long[value_name], errors="coerce")
    return long.dropna(subset=[value_name])


def build_grid_ef():
    ema = pd.read_csv(RAW / "datagovsg" / "ema_grid_emission_factor.csv")
    ema = ema.rename(columns={"avg_opt_margin_kgco2-per-kwh": "avg_opt_margin_kgco2_per_kwh",
                              "build_margin_kgco2-per-kwh": "build_margin_kgco2_per_kwh"})
    ema = ema[["year", "avg_opt_margin_kgco2_per_kwh", "build_margin_kgco2_per_kwh"]]
    ema["source"] = "data.gov.sg (EMA)"
    sup = pd.read_csv(CFG / "grid_ef_ema_2021_2024.csv")[["year", "avg_opt_margin_kgco2_per_kwh", "source"]]
    ef = pd.concat([ema, sup], ignore_index=True).sort_values("year")

    owid = pd.read_csv(RAW / "csv" / "owid_energy_data.csv",
                       usecols=["country", "year", "carbon_intensity_elec", "electricity_generation",
                                "gas_share_elec", "oil_share_elec", "solar_share_elec", "renewables_share_elec"])
    owid = owid[owid["country"] == "Singapore"].drop(columns="country")
    owid["owid_lifecycle_kgco2e_per_kwh"] = owid.pop("carbon_intensity_elec") / 1000.0
    owid.to_csv(OUT / "owid_singapore_electricity.csv", index=False)

    ef = ef.merge(owid[["year", "owid_lifecycle_kgco2e_per_kwh"]], on="year", how="left")
    ef.to_csv(OUT / "grid_emission_factor.csv", index=False)
    return ef


def build_water():
    sales = singstat_wide_to_long(RAW / "datagovsg" / "singstat_water_sales_annual.csv", "million_m3")
    sales = sales.rename(columns={"DataSeries": "series", "period": "year"})
    sales["year"] = sales["year"].astype(int)
    sales.sort_values(["series", "year"]).to_csv(OUT / "water_sales.csv", index=False)

    rows = []
    for f in ["pub_newater_tariff.csv", "pub_industrial_water_tariff.csv"]:
        rows.append(pd.read_csv(RAW / "datagovsg" / f))
    tariffs = pd.concat(rows, ignore_index=True)
    tariffs["as_of"] = "2021 (data.gov.sg); add 2024-25 increases from PUB 2023 release"
    tariffs.to_csv(OUT / "water_tariffs.csv", index=False)
    p = load_params()
    pd.DataFrame([
        dict(source="potable_non_domestic", all_in_sgd_per_m3=p["tariff_potable_nd"],
             effective="April 2025", basis="PUB Annex A; tariff plus conservation and waterborne taxes; before GST"),
        dict(source="newater", all_in_sgd_per_m3=p["tariff_newater"],
             effective="April 2025", basis="PUB Annex B live verification 25 October 2026; 1.28 tariff + 0.13 conservation tax + 1.09 waterborne tax; before GST"),
    ]).to_csv(OUT / "water_prices_current.csv", index=False)
    return sales


def build_electricity():
    tar = singstat_wide_to_long(RAW / "datagovsg" / "singstat_electricity_tariff_annual.csv", "cents_per_kwh")
    tar.rename(columns={"DataSeries": "tariff", "period": "year"}).to_csv(OUT / "electricity_tariff_annual.csv", index=False)
    gen = singstat_wide_to_long(RAW / "datagovsg" / "singstat_electricity_gen_consumption.csv", "gwh")
    gen.rename(columns={"DataSeries": "series", "period": "year"}).to_csv(OUT / "electricity_gen_consumption.csv", index=False)


def build_weather():
    path = next((RAW / "weather").glob("openmeteo_*_hourly_*.csv"))
    w = pd.read_csv(path, parse_dates=["time"])
    w = w.rename(columns={"temperature_2m": "tdb", "relative_humidity_2m": "rh",
                          "dew_point_2m": "tdp", "wet_bulb_temperature_2m": "twb"})
    w["year"], w["month"] = w["time"].dt.year, w["time"].dt.month

    # Weather-exposure proxy: thresholds reflect an assumed loop temperature
    # and approach. These counts do not validate an installed cooler's capacity.
    for thr in (27, 30, 32, 35):
        w[f"hrs_tdb_gt_{thr}"] = (w["tdb"] > thr).astype(int)

    agg = {"tdb": ["mean", "max"], "twb": ["mean", lambda s: s.quantile(0.99)], "rh": "mean"}
    monthly = w.groupby(["year", "month"]).agg(agg)
    monthly.columns = ["tdb_mean", "tdb_max", "twb_mean", "twb_p99", "rh_mean"]
    hrs = w.groupby(["year", "month"])[[c for c in w if c.startswith("hrs_")]].sum()
    monthly = monthly.join(hrs).reset_index()
    monthly.round(2).to_csv(OUT / "weather_monthly.csv", index=False)

    clim = monthly.drop(columns="year").groupby("month").mean().round(2)
    clim.to_csv(OUT / "weather_climatology.csv")
    return w


def build_wue_check():
    """WUE [m3/MWh_IT] = 3.6 / L * HRF * f_evap * CoC / (CoC - 1)

    3.6/L converts 1 kWh of heat to kg of water evaporated (L in MJ/kg), so
    kg/kWh == m3/MWh. CoC/(CoC-1) adds blowdown to evaporation.
    """
    a = pd.read_csv(CFG / "assumptions.csv").set_index("id")
    L = a.loc["latent_heat", "base"]
    rows = []
    for coc in [2, 2.5, 3, 4, 5, 6, 8, 10, 12]:
        for case in ("low", "base", "high"):
            hrf = a.loc["heat_reject_factor", case]
            fe = a.loc["evap_fraction", case]
            evap = 3.6 / L * hrf * fe
            rows.append({"coc": coc, "case": case, "evaporation_m3_per_mwh": round(evap, 3),
                         "blowdown_m3_per_mwh": round(evap / (coc - 1), 3),
                         "wue_m3_per_mwh": round(evap * coc / (coc - 1), 3)})
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "wue_heat_balance.csv", index=False)
    return df, a


def scale_check(sales, a):
    nat = sales[sales["year"] == sales["year"].max()]
    total = nat[nat["series"].isin(["Sales Of Potable Water", "Sales Of Newater"])]["million_m3"].sum()
    p = a["base"].astype(float).to_dict()
    it_mw = p["cap_cfa2"] * p["mw_basis_it_share"]
    mwh = it_mw * p["util"] * 8760
    wue, trim = wue_by_strategy(p)
    lines = [f"National water sales {int(nat['year'].iloc[0])}: {total:.1f} million m3/yr (potable + NEWater)",
             f"DC-CFA2 basis: {it_mw:g} MW IT; mature average utilisation {p['util']:.0%}; {mwh:,.0f} MWh IT/year.",
             "Commissioning in 2027 and the 2028/2029 hypothetical tranches are team schedule assumptions, not verified opening dates.",
             "WUE is benchmark-calibrated; weather trim is an exposure proxy, not a validated equipment simulation."]
    for strategy, intensity in wue.items():
        m3 = mwh * intensity
        lines.append(f"{STRATEGY_NAME[strategy]}: WUE {intensity:.4f} m3/MWh IT; {m3/1e6:.3f} million m3/yr "
                     f"= {100*m3/1e6/total:.2f}% of national sales, {m3/365:,.0f} m3/day")
    lines.extend([f"Exact archived-hour trim share at {p['trim_threshold']:g} C: {trim:.4%}.",
                  f"Operator all-in water prices before GST: potable S${p['tariff_potable_nd']:.2f}/m3; NEWater S${p['tariff_newater']:.2f}/m3.",
                  f"Electricity price proxies: social S${p['price_elec_plant']:.2f}/kWh; operator S${p['price_elec']:.2f}/kWh."])
    (OUT / "scale_check.txt").write_text("\n".join(lines) + "\n")
    return lines


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ef = build_grid_ef()
    sales = build_water()
    build_electricity()
    build_weather()
    wue, a = build_wue_check()

    print("Grid EF (EMA, kgCO2/kWh), last 6 years:")
    print(ef.tail(6)[["year", "avg_opt_margin_kgco2_per_kwh"]].to_string(index=False))
    print("\nHeat-balance WUE (base case) vs PUB median 2.1 m3/MWh:")
    print(wue[wue.case == "base"][["coc", "wue_m3_per_mwh"]].to_string(index=False))
    print("\nScale check:")
    print("\n".join(scale_check(sales, a)))
    clim = pd.read_csv(OUT / "weather_climatology.csv")
    print(f"\nJurong Island climate: mean wet-bulb {clim.twb_mean.mean():.1f} C, "
          f"hours/yr with dry-bulb > 32 C: {clim.hrs_tdb_gt_32.sum():.0f}")
    print(f"\nWrote {len(list(OUT.glob('*')))} files to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
