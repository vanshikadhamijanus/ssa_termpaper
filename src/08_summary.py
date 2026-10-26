"""Step 8 - one summary table of the headline numbers used in the paper and poster (outputs/tables/headline.csv)."""
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import TAB, STRATEGIES, SHORT

def main():
    d = pd.read_csv(TAB / "demand_summary.csv"); L = pd.read_csv(TAB / "lca_inventory.csv").set_index("strategy")
    C = pd.read_csv(TAB / "lcc_per_mwh.csv").set_index("strategy"); S = pd.read_csv(TAB / "ahp_scores_by_scenario.csv")
    M = pd.read_csv(TAB / "mc_rank_probability.csv").set_index("strategy"); N = pd.read_csv(TAB / "npc_by_scenario.csv")
    rows = []
    for a in STRATEGIES:
        s1 = d[(d.scenario == "S1") & (d.strategy == a)].iloc[0]; s3 = d[(d.scenario == "S3") & (d.strategy == a)].iloc[0]
        rows.append(dict(strategy=a, name=SHORT[a], wue=round(L.loc[a, "wue"], 2),
            water_2035_S1_Mm3=round(s1.water_2035_m3 / 1e6, 2), water_2035_S3_Mm3=round(s3.water_2035_m3 / 1e6, 2),
            kwh_per_mwh=round(L.loc[a, "kwh_total"], 1), gwp_kg_per_mwh=round(L.loc[a, "gwp_total"], 2), gwp_water_only=round(L.loc[a, "gwp_water_only"], 2),
            social_cost_sgd_per_mwh=round(C.loc[a, "social_cost"], 2),
            social_elcc_sgd_per_mwh=round(C.loc[a, "elcc_social_eco"], 2), operator_sgd_per_mwh=round(C.loc[a, "operator_cost"], 2),
            npc_social_S1_Msgd=round(N[(N.perspective == "social") & (N.scenario == "S1") & (N.strategy == a)].npc_sgd.iloc[0] / 1e6, 2),
            ahp_W1=round(S[(S.weight_scenario == "W1 Balanced") & (S.strategy == a)].score.iloc[0], 3),
            ahp_rank_W1=int(S[(S.weight_scenario == "W1 Balanced") & (S.strategy == a)]["rank"].iloc[0]),
            p_rank1_mc=round(M.loc[a, "p_rank1_ahp_W1"], 3)))
    H = pd.DataFrame(rows); H.to_csv(TAB / "headline.csv", index=False); print(H.to_string(index=False))

if __name__ == "__main__":
    main()
