"""Numerical report fields read from the current analysis tables."""
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
TAB=ROOT/'outputs/tables'
IDS=['A1','A2','A3','A4']
def read(name,index=None):return pd.read_csv(TAB/f'{name}.csv',index_col=index)
def fmt(x,n=2):return f'{float(x):,.{n}f}'
def input_value(row, column):
    value=getattr(row,column)
    if row.unit=='year':return str(int(value))
    if row.unit in ('years','MW_IT') or row.id.startswith(('capex_','cap_')):return fmt(value,0)
    return fmt(value,3)
def mdtable(headers,rows):
    def line(row):return '| '+' | '.join(str(v).replace('|','/').replace('\n',' ') for v in row)+' |'
    return '\n'.join([line(headers),line(['---']*len(headers))]+[line(r) for r in rows])

def context():
    cfg=pd.read_csv(ROOT/'config/assumptions.csv');p=cfg.set_index('id')['base'].to_dict()
    L,C=read('lca_inventory','strategy'),read('lcc_per_mwh','strategy')
    D,N,S=read('demand_summary'),read('npc_by_scenario'),read('ahp_scores_by_scenario')
    M,P=read('mc_rank_probability','strategy'),read('mc_preference_rank_probability')
    B,W=read('breakeven'),read('lcow','source')
    meta=read('uncertainty_metadata').set_index('setting')['value'].to_dict()
    annual=D[D.scenario=='S1'].set_index('strategy');wue=L.loc['A2','wue'];recovered=L.loc['A3','recovered_blowdown_m3']
    weather=pd.read_csv(ROOT/'data/raw/weather/openmeteo_jurong_island_hourly_2015_2025.csv',usecols=['temperature_2m'])
    national=pd.read_csv(ROOT/'data/processed/water_sales.csv')
    national_year=int(national.year.max())
    national=national[(national.year==national_year)&national.series.isin(['Sales Of Potable Water','Sales Of Newater'])].million_m3.sum()
    q={'util':fmt(p['util']*100,0),'ramp_years':fmt(p['ramp_years'],0),'n_parameters':len(cfg),
       'n_verified':(cfg.status=='verified').sum(),'n_unverified':(cfg.status=='to-verify').sum(),'n_judgment':(cfg.status=='team-judgement').sum(),
       'newater_tariff':fmt(p['tariff_newater']),'potable_tariff':fmt(p['tariff_potable_nd']),
       'weather_rows':fmt(len(weather),0),'evap':fmt(wue*(p['coc_current']-1)/p['coc_current']),
       'coc_current':fmt(p['coc_current'],0),'coc_best':fmt(p['coc_best'],0),
       'blowdown_before':fmt(recovered/p['blowdown_recovery']),'recovered':fmt(recovered),
       'discharge':fmt(L.loc['A3','blowdown_discharge_m3']),'recovery':fmt(p['blowdown_recovery']*100,0),
       'wue_base':fmt(wue),'liquid_share':fmt(p['liquid_heat_share']*100,0),'trim_threshold':fmt(p['trim_threshold'],0),
       'trim_percent':fmt((weather.temperature_2m>p['trim_threshold']).mean()*100),
       'national_share':fmt(annual.loc['A2','water_2035_m3']/1e6/national*100),'national_water':fmt(national,0),'national_year':national_year,
       'a3_water_saving':fmt((1-L.loc['A3','wue']/wue)*100,1),'a4_water_saving':fmt((1-L.loc['A4','wue']/wue)*100,1),
       'a3_carbon_saving':fmt((1-L.loc['A3','gwp_total']/L.loc['A2','gwp_total'])*100,1),
       'a3_social_premium':fmt(C.loc['A3','social_cost']-C.loc['A2','social_cost']),
       'a3_operator_saving':fmt(C.loc['A2','operator_cost']-C.loc['A3','operator_cost']),
       'dry_kwh':fmt(L.loc['A4','kwh_dc_delta'],0),'lcow_desal':fmt(W.loc['desal','bottom_up_total']),
       'lcow_newater':fmt(W.loc['newater','bottom_up_total']),'max_cr':fmt(read('ahp_consistency').CR.max(),3),'base_grid_factor':fmt(L.loc['A2','ef_grid'],4),
       'n_mc':fmt(meta['parameter_draws'],0),'mc_seed':meta['parameter_seed'],'n_mc_inputs':meta['active_triangular_inputs'],
       'n_pref':fmt(meta['preference_draws_per_case'],0),'pref_seed':meta['preference_seed'],
       'ghg_threshold':fmt(B[B.question.str.contains('A4 versus A2:.*equal screening GHG')].breakeven.iloc[0],4),
       'reuse_tariff_threshold':fmt(B[B.parameter=='tariff_newater'].breakeven.iloc[0])}
    for a in IDS:
        q[f'water_{a}']=fmt(annual.loc[a,'water_2035_m3']/1e6);q[f'wue_{a}']=fmt(L.loc[a,'wue']);q[f'gwp_{a}']=fmt(L.loc[a,'gwp_total'])
    for a in ['A3','A4']:q[f'{a.lower()}_water_avoided']=fmt((annual.loc['A2','water_2035_m3']-annual.loc[a,'water_2035_m3'])/1e6)
    q['table_summary']=mdtable(['Configuration','Water m³','GHG kg CO₂e','Resource cost S$','Operator cost S$'],
       [[a+' '+label,fmt(L.loc[a,'wue']),fmt(L.loc[a,'gwp_total']),fmt(C.loc[a,'social_cost']),fmt(C.loc[a,'operator_cost'])]
        for a,label in zip(IDS,['Wet + desal','Wet + NEWater','Towers + reuse','Dry + wet trim'])])
    q['table_questions']=mdtable(['Question','Assessment','Reported metric'],[
       ['Q1 Additional water required','Capacity and utilisation model','Annual and cumulative m³'],['Q2 Water demand avoided','Tower balance and weather exposure','WUE and avoided m³'],
       ['Q3 Cost and carbon','LCC and simplified LCA','S$/MWh and kg CO₂e/MWh'],['Q4 Wider decision factors','AHP with stated judgments','Priorities by weighting case'],
       ['Q5 Dependence on assumptions','Parameter, preference and structural tests','Intervals, rank frequencies and thresholds']])
    keys=[('cap_cfa2','IT capacity, MW'),('util','Average utilisation, fraction'),('wue_base','Wet-rejection WUE, m³/MWh'),('coc_best','High cycles of concentration'),
       ('blowdown_recovery','Blowdown recovery, fraction'),('dpue_dry','Additional dry-rejection PUE'),('capex_hicoc','Recovery capex, S$/MW IT'),
       ('capex_dry_premium','Dry-rejection premium, S$/MW IT'),('sec_desal','Desalination energy, kWh/m³'),('sec_newater','NEWater energy, kWh/m³'),
       ('price_elec_plant','Resource electricity proxy, S$/kWh'),('price_elec','Operator electricity, S$/kWh'),('disc_social','Social discount rate, %'),('disc_private','Operator discount rate, %')]
    lookup=cfg.set_index('id')
    q['table_parameters']=mdtable(['Parameter','Base','Low–high','Evidence status'],[[label,fmt(lookup.loc[k,'base']),fmt(lookup.loc[k,'low'])+'–'+fmt(lookup.loc[k,'high']),lookup.loc[k,'status']] for k,label in keys])
    q['table_alternatives']=mdtable(['ID','Heat rejection','Make-up source'],[
       ['A1','Wet towers, CoC '+q['coc_current'],'Desalinated water'],['A2','Wet towers, CoC '+q['coc_current'],'NEWater'],
       ['A3','CoC '+q['coc_best']+' and '+q['recovery']+'% blowdown recovery','NEWater'],['A4','Dry loop with wet assistance; wet residual load','NEWater']])
    capacities=[p['cap_cfa2'],p['cap_cfa2']+p['cap_roadmap'],p['cap_cfa2']+p['cap_roadmap']+p['cap_future_cfa']]
    q['table_demand']=mdtable(['Scenario','Total MW IT','A1 / A2','A3','A4'],[[s,fmt(capacity,0)]+[fmt(D[(D.scenario==s)&(D.strategy==a)].water_2035_m3.iloc[0]/1e6) for a in ['A2','A3','A4']] for s,capacity in zip(['S1','S2','S3'],capacities)])
    q['table_npc']=mdtable(['Perspective']+IDS,[[label]+[fmt(N[(N.scenario=='S1')&(N.perspective==pers)&(N.strategy==a)].npc_sgd.iloc[0]/1e6) for a in IDS] for pers,label in [('social','Resource costs'),('operator','Operator costs')]])
    ranks=[];score_rows=[]
    for sc,group in S.groupby('weight_scenario',sort=False):
        ranks.append((sc,group.sort_values('rank').strategy.tolist()))
        score_rows.append([sc.split(' / ')[0]]+[fmt(group[group.strategy==a].score.iloc[0],3) for a in IDS])
    q['table_ahp']=mdtable(['Weighting']+IDS,score_rows)
    balanced=S[S.weight_scenario=='W1 Balanced'].sort_values('rank')
    q['ahp_interpretation']='Under balanced weights, the order is '+', '.join(balanced.strategy)+'. '+balanced.iloc[0].strategy+' receives a priority of '+fmt(balanced.iloc[0].score,3)+'. Across the other illustrative perspectives, the first-ranked option is '+ '; '.join(sc.split(' / ')[0]+': '+order[0] for sc,order in ranks[1:])+'. These priorities should be read alongside the separate water, cost and emissions results, rather than as a universal equipment recommendation.'
    rows=[]
    for a in IDS:
        row=[a,fmt(M.loc[a,'p_rank1_ahp_W1']*100,1)+'%']
        for mode,hier in [('preferences_only','Full hierarchy'),('parameters_and_preferences','Full hierarchy'),('parameters_and_preferences','Reduced overlap')]:
            row.append(fmt(P[(P.strategy==a)&(P['mode']==mode)&(P.hierarchy==hier)].p_rank1.iloc[0]*100,1)+'%')
        rows.append(row)
    q['table_uncertainty']=mdtable(['Option','Parameters only','Preferences only','Combined full','Combined reduced'],rows)
    comb=P[(P['mode']=='parameters_and_preferences')&(P.hierarchy=='Full hierarchy')].set_index('strategy')
    q['uncertainty_interpretation']=f"With fixed balanced preferences, A3 ranks first in {fmt(M.loc['A3','p_rank1_ahp_W1']*100,1)}% of parameter draws. When both parameters and preferences vary, that frequency is {fmt(comb.loc['A3','p_rank1']*100,1)}%, while A4 ranks first in {fmt(comb.loc['A4','p_rank1']*100,1)}%. Parameter uncertainty alone therefore does not establish preference robustness. A3 costs less than A2 for the operator in {fmt(M.loc['A3','p_A3_cheaper_than_A2_operator']*100,1)}% of parameter draws, which qualifies the base-case saving."
    demand_mc=read('mc_demand_summary')
    demand_mc=demand_mc[(demand_mc.scenario=='S1')&(demand_mc.metric=='water_2035_m3')].set_index('strategy')
    costs_mc=read('mc_summary')
    costs_mc=costs_mc[costs_mc.metric=='social_cost_per_mwh'].set_index('strategy')
    q['table_parameter_intervals']=mdtable(['Option','S1 water in 2035, million m³','Resource cost, S$/MWh'],[
        [a,fmt(demand_mc.loc[a,'p5']/1e6)+'–'+fmt(demand_mc.loc[a,'p95']/1e6),
         fmt(costs_mc.loc[a,'p5'])+'–'+fmt(costs_mc.loc[a,'p95'])] for a in IDS])
    active=cfg[cfg.role.isin(['model','scenario-definition'])]
    q['table_active_assumptions']=mdtable(['Parameter and unit','Low / base / high','Status'],[[r.parameter+' ('+r.unit+')',' / '.join(input_value(r,c) for c in ('low','base','high')),r.status] for r in active.itertuples()])
    wt=read('ahp_weights');wt=wt[wt.weight_scenario=='W1 Balanced']
    q['table_ahp_weights']=mdtable(['Subcriterion','Global weight'],[[r.sub_criterion,fmt(r.global_weight,3)] for r in wt.itertuples()])
    notes=read('ahp_judgement_notes')
    q['table_ahp_notes']=mdtable(['Comparison group','Judgment basis'],[[r.matrix,r.note] for r in notes.itertuples()])
    q['references']=(ROOT/'references.md').read_text()
    return {k:str(v) for k,v in q.items()}
