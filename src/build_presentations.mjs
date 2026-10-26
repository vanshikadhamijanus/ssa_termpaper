/** Editable poster and video slides, built from the same CSV results as the report. */
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {pathToFileURL, fileURLToPath} from 'node:url';

process.on('uncaughtException',error=>{console.error(error.message);console.error(error.stack?.split('\n').slice(1,5).join('\n'));process.exit(1);});

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BUILD = path.join(ROOT, '.build', 'presentations');
const OUT = path.join(ROOT, 'deliverables');
const SKILL = path.join(os.homedir(), '.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11618/skills/presentations');
const runtimeRequire = createRequire(path.join(process.env.RUNTIME_NODE_MODULES, '__runtime__.js'));
const {Presentation, PresentationFile, FileBlob} = await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);
const {applyPresentationChartFont, finalizePresentation} = await import(pathToFileURL(path.join(SKILL, 'container_tools/artifact_tool_utils.mjs')).href);
const [kind, inputPath] = process.argv.slice(2);
const input = JSON.parse(await fs.readFile(inputPath, 'utf8'));
const T = input.tables;
const ids = ['A1', 'A2', 'A3', 'A4'];
const names = {A1:'Wet + desalination', A2:'Wet + NEWater', A3:'High-CoC + reuse', A4:'Dry + wet trim'};
const shortNames = {A1:'Desalination', A2:'NEWater', A3:'Tower reuse', A4:'Dry rejection'};
const C = {navy:'#1D2D50', teal:'#167C80', ink:'#25282C', grey:'#687080', pale:'#F2F5F8', rule:'#D5DCE4', white:'#FFFFFF', A1:'#547599', A2:'#247F81', A3:'#A77B24', A4:'#AD5F51'};
const byStrategy = name => Object.fromEntries((T[name] ?? []).map(r=>[r.strategy,r]));
const L = byStrategy('lca_inventory');
const K = byStrategy('lcc_per_mwh');
const A = (T.ahp_scores_by_scenario ?? []).filter(r=>r.weight_scenario==='W1 Balanced').sort((a,b)=>+a.rank-+b.rank);
const n = x => {const value=Number(x); if(!Number.isFinite(value)) throw new Error(`Invalid numeric result: ${x}`); return value;};
const f = (x, digits=2) => n(x).toFixed(digits);
const q = x => Number(n(x).toFixed(6));
const pct = (x, digits=0) => `${(n(x)*100).toFixed(digits)}%`;
const assumption = key => {
  const row=input.assumptions.find(r=>(r.id??r.parameter??r.key??r.name)===key);
  if(!row) throw new Error(`Missing assumption ${key}`);
  return n(row.base);
};
const demand = (scenario,strategy) => {
  const row=T.demand_summary.find(r=>r.scenario===scenario&&r.strategy===strategy);
  if(!row) throw new Error(`Missing demand ${scenario}/${strategy}`);
  return row;
};
const rankMap=Object.fromEntries(A.map(r=>[r.strategy,n(r.rank)]));
const least = accessor => [...ids].sort((a,b)=>accessor(a)-accessor(b))[0];
const leastCost=least(a=>n(K[a].social_cost));
const leastCarbon=least(a=>n(L[a].gwp_total));
const leastWater=least(a=>n(L[a].wue));
const topAHP=A[0]?.strategy;
const saving=a=>1-n(L[a].wue)/n(L.A2.wue);
const SOURCES='Model sources: config/assumptions.csv; outputs/tables/lca_inventory.csv; lcc_per_mwh.csv; demand_summary.csv; ahp_scores_by_scenario.csv; cooling_threshold_grid.csv. Public context: https://klpoh.github.io/courses/dss5202/termpaper.html; IMDA Green Data Centre Roadmap (2024); EDB and IMDA DC-CFA2 announcement (2026); PUB water-efficiency benchmarks and tariffs. Full citations and source boundaries are in the accompanying report.';

function text(slide, value, x,y,w,h, size=20, options={}) {
  const shape=slide.shapes.add({geometry:'textbox',name:options.name??value.slice(0,50),position:{left:x,top:y,width:w,height:h},fill:options.fill??'none',line:{fill:'none',width:0}});
  shape.text=value;
  shape.text.style={fontSize:size,typeface:'Arial',color:options.color??C.ink,bold:options.bold??false,alignment:options.align??'left',verticalAlignment:options.valign??'top',wrap:'square',autoFit:'none',insets:options.insets??0};
  return shape;
}
function line(slide,x,y,w,color=C.teal) {
  return slide.shapes.add({geometry:'line',position:{left:x,top:y,width:w,height:0},fill:'none',line:{fill:color,width:1}});
}
function heading(slide,value,x,y,w,size=24) {text(slide,value,x,y,w,36,size,{bold:true,color:C.navy});line(slide,x,y+33,w);}
function diagramBox(slide,value,x,y,w,h,size=20) {
  const box=slide.shapes.add({geometry:'rect',name:value,position:{left:x,top:y,width:w,height:h},fill:C.pale,line:{fill:C.rule,width:1}});
  box.text=value;box.text.style={fontSize:size,typeface:'Arial',color:C.ink,alignment:'center',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:6};return box;
}
function connect(slide,a,b,from='bottom',to='top') {
  slide.shapes.connect(a,b,{kind:'elbow',fromSide:from,toSide:to,line:{fill:C.grey,width:1.5},tail:{type:'triangle',width:'med',length:'med'}});
}
function table(slide,values,x,y,width,height,columnWidths,size=20) {
  const tbl=slide.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width,height,values,columnWidths});
  tbl.borders.assign({fill:C.rule,width:0.5});
  for(let r=0;r<values.length;r++) for(let c=0;c<values[r].length;c++) {
    const cell=tbl.getCell(r,c);cell.fill=r===0?C.navy:r%2?C.pale:C.white;
    cell.text.style={fontSize:size,typeface:'Arial',color:r===0?C.white:C.ink,bold:r===0,alignment:c===0?'left':'center',verticalAlignment:'middle',wrap:'square',autoFit:'none',insets:5};
  }
  return tbl;
}
function chart(slide,type,config) {
  const ch=slide.charts.add(type,{chartFill:C.white,chartLine:{fill:'none',width:0},plotAreaFill:C.white,plotAreaLine:{fill:'none',width:0},...config});
  applyPresentationChartFont(ch,{fontFamily:'Arial'});return ch;
}
function barChart(slide,values,label,x,y,w,h,size=22) {
  return chart(slide,'bar',{
    position:{left:x,top:y,width:w,height:h},title:label,titleTextStyle:{fontSize:size,bold:true,fill:C.navy},
    categories:ids,series:[{name:label,values:values.map(q),fill:C.teal,points:ids.map((a,idx)=>({idx,fill:C[a]}))}],
    hasLegend:false,barOptions:{direction:'column',gapWidth:85},
    xAxis:{textStyle:{fontSize:size,fill:C.ink},line:{fill:C.rule,width:1},majorGridlines:null},
    yAxis:{min:0,textStyle:{fontSize:size,fill:C.grey},majorGridlines:{fill:C.rule,width:0.5},line:{fill:'none',width:0},numberFormatCode:'0.0'},
    dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.00',textStyle:{fontSize:size,fill:C.ink}},
  });
}
function thresholdChart(slide,x,y,w,h,size=19) {
  const compact=size<20;
  const rows=T.cooling_threshold_grid;
  if(!rows?.length) throw new Error('Run sensitivity analysis before building presentations.');
  const levels=[...new Set(rows.map(r=>n(r.capex_dry_premium)))];
  const base=assumption('capex_dry_premium');
  const nearest=levels.sort((a,b)=>Math.abs(a-base)-Math.abs(b-base))[0];
  const series=(compact?['A2']:['A2','A3']).map((a)=>{
    const rr=rows.filter(r=>r.comparison===a&&n(r.capex_dry_premium)===nearest&&(!compact||n(r.dpue_dry)>=0)).sort((a,b)=>n(a.dpue_dry)-n(b.dpue_dry));
    return {name:`A4 minus ${a}`,xValues:rr.map(r=>q(r.dpue_dry)),values:rr.map(r=>q(r.cost_difference)),line:{fill:C[a],width:2.5},marker:{symbol:'none'}};
  });
  const allCosts=series.flatMap(s=>s.values);
  const axisMin=Math.min(0,Math.floor(Math.min(...allCosts)/5)*5);
  const axisMax=Math.max(5,Math.ceil(Math.max(...allCosts)/5)*5);
  return chart(slide,'scatter',{
    position:{left:x,top:y,width:w,height:h},series,scatterOptions:{style:'line'},hasLegend:!compact,
    ...(compact?{title:'A4 minus A2 social cost (S$/MWh)',titleTextStyle:{fontSize:size,fill:C.grey}}:{}),
    legend:{position:'top',overlay:false,textStyle:{fontSize:size,fill:C.ink}},
    xAxis:{title:{text:'Additional PUE from dry rejection',textStyle:{fontSize:size,fill:C.ink}},majorUnit:0.02,numberFormatCode:'0.00',textStyle:{fontSize:size,fill:C.grey},majorGridlines:null,line:{fill:C.rule,width:1}},
    yAxis:{...(compact?{min:axisMin,max:axisMax,majorUnit:Math.max(5,Math.ceil((axisMax-axisMin)/15)*5)}:{title:{text:'Extra social cost (S$/MWh)',textStyle:{fontSize:size,fill:C.ink}}}),numberFormatCode:'0',textStyle:{fontSize:size,fill:C.grey},majorGridlines:{fill:C.rule,width:0.5},line:{fill:C.rule,width:1}},
  });
}

function systemDiagram(slide,x,y,w,h,size=20) {
  const common=diagramBox(slide,'Common liquid-cooled IT system',x,y,w,46,size);
  const gap=28,bw=(w-gap)/2;
  const wet=diagramBox(slide,'Wet heat rejection',x,y+80,bw,42,size);
  const dry=diagramBox(slide,'Dry rejection + wet trim',x+bw+gap,y+80,bw,42,size);
  connect(slide,common,wet);connect(slide,common,dry);
  text(slide,'A1  Desalination\nA2  NEWater\nA3  NEWater + tower reuse',x,y+140,bw,h-140,size);
  text(slide,'A4  NEWater for remaining demand',x+bw+gap,y+140,bw,h-140,size);
}

async function poster() {
  const p=await PresentationFile.importPptx(await FileBlob.load(path.join(ROOT,'paper/MyGroupNo-Poster-template.pptx')));
  const slide=p.slides.items[0];
  slide.images.add({blob:new Uint8Array(await fs.readFile(path.join(BUILD,'template_nus_logo.png'))),contentType:'image/png',alt:'NUS logo from the module poster template',fit:'contain',position:{left:17.33,top:698.57,width:54.67,height:21.17}});
  const entries=(await p.inspect({kind:'textbox,shape',maxChars:20000})).ndjson.trim().split('\n').map(s=>JSON.parse(s));
  const title=entries.find(r=>r.placeholder==='title');
  const titleShape=p.resolve(title.id);
  titleShape.text='';
  titleShape.position={left:18.13,top:10.44,width:1221.76,height:74.01};
  p.delete(entries.filter(r=>r.id!==title.id).map(r=>r.id));
  slide.shapes.add({geometry:'line',name:'Template column divider',position:{left:629.01,top:120,width:0,height:578.57},fill:'none',line:{style:'solid',fill:C.navy,width:1}});
  text(slide,'The Thirsty Cloud',32,16,1200,34,30,{bold:true,color:C.navy,align:'center'});
  text(slide,"Water supply and cooling choices for Singapore's data-centre growth",32,50,1200,27,21,{align:'center',color:C.navy});
  text(slide,'DSS5202 Group 29 (2026)   Aditya Vijindra Pandhari   Apurwa Kumari   Vanshika Dhamija',32,87,1200,27,19,{align:'center',color:C.grey});
  heading(slide,'1. Decision and comparison basis',30,124,573);
  text(slide,'We compare additional water supply with lower water use for new data centres during 2027–2035. All options serve 1 MWh of IT energy and share the same liquid-cooled IT baseline.',30,168,573,76,20);
  text(slide,'Sources: PUB (2025), EMA (2026) and team assumptions.',30,247,573,24,19,{color:C.grey});
  systemDiagram(slide,30,274,573,220,19);
  heading(slide,'2. Additional water demand in 2035',30,497,573);
  const d1=demand('S1','A2'),d3=demand('S3','A2');
  text(slide,`${f(n(d1.water_2035_m3)/1e6)} million m³/year: 200 MW case\n${f(n(d3.water_2035_m3)/1e6)} million m³/year: 700 MW hypothetical case`,30,540,573,56,21,{bold:true,color:C.teal});
  text(slide,`Wet rejection at ${pct(assumption('util'))} utilisation after the assumed ramp.\nWater reduction vs A2: A3 ${pct(saving('A3'))}, A4 ${pct(saving('A4'))}.`,30,598,573,47,19);
  text(slide,`Methods: LCA, LCC and AHP with sensitivity tests.\nBalanced AHP ranks ${topAHP} first with illustrative weights.`,30,649,573,46,19);
  heading(slide,'3. Base-case results per MWh of IT',657,124,591);
  const values=[['Metric','A1','A2','A3','A4'],['Water (m³)',...ids.map(a=>f(L[a].wue))],['GHG (kg CO₂e)',...ids.map(a=>f(L[a].gwp_total))],['Social cost (S$)',...ids.map(a=>f(K[a].social_cost))],['Operator cost (S$)',...ids.map(a=>f(K[a].operator_cost))]];
  table(slide,values,657,170,591,175,[227,91,91,91,91],19);
  text(slide,'Partial boundary: water supply and incremental heat rejection. Costs exclude carbon monetisation.',657,354,591,48,19,{color:C.grey});
  heading(slide,'4. Cost of reducing water use',657,405,591);
  thresholdChart(slide,647,444,610,198,18.7);
  text(slide,`${leastCost} minimises base social cost. ${leastWater} minimises water use. Verify dry-rejection electricity at the site.`,657,648,591,46,19,{bold:true,color:C.navy});
  slide.speakerNotes.text=`Methods: demand model, simplified LCA, LCC and AHP with sensitivity analysis. ${SOURCES}\nAHP balanced winner: ${topAHP}. Main chart uses the current incremental dry-rejection capital assumption. Values above zero mean A4 costs more than the comparator. NUS IDs: Aditya A0328872R, Apurwa A0333260R, Vanshika A0333989H.`;
  return {presentation:p,stem:'DSS5202_Group29_Poster',count:1,tables:[1],charts:[1]};
}

function page(p,title,number) {
  const slide=p.slides.add();slide.background.fill=C.white;
  text(slide,title,52,35,1176,64,36,{bold:true,color:C.navy});line(slide,52,110,1176);
  text(slide,'DSS5202 Group 29   The Thirsty Cloud',52,675,1000,25,16,{color:C.grey});
  text(slide,`${number} / 10`,1125,675,103,25,16,{color:C.grey,align:'right'});
  return slide;
}
function paragraphs(slide,values,x,y,w,size=25,gap=125) {
  values.forEach((s,i)=>text(slide,s,x,y+i*gap,w,gap-15,size));
}

function videoScript() {
  const base=demand('S1','A2');
  const high=demand('S3','A2');
  const low=demand('S1','A4');
  const pref=T.mc_preference_rank_probability?.filter(r=>r.mode==='parameters_and_preferences'&&r.hierarchy==='Full hierarchy')??[];
  const prefWinner=[...pref].sort((a,b)=>n(b.p_rank1)-n(a.p_rank1))[0];
  const order=A.map(r=>r.strategy).join(', ');
  const sections=[
    {title:'Project purpose',speaker:'Vanshika',text:`Hello, we are Group 29: Aditya, Apurwa and Vanshika. Our project studies how Singapore can meet the additional cooling-water demand from new data centres. We compare increasing water supply with reducing the amount of water required at each site. The analysis covers growth between 2027 and 2035 and considers the decisions facing PUB, IMDA and data-centre operators. Our main finding is a trade-off. Lower water use can require more electricity, so the preferred option depends on the cooling design and the priorities used to assess it.`},
    {title:'Problem and study boundary',speaker:'Vanshika',text:`Singapore provisionally awarded 200 megawatts of data-centre capacity under the second call for applications in 2026. Our starting question is how much additional cooling water this growth could require. We use three capacity scenarios, with 200, 500 and 700 megawatts by 2035. The larger cases are planning assumptions, not forecasts of approved projects. We estimate demand from capacity, utilisation and water-use effectiveness. Water-use effectiveness is the volume of water used for each unit of IT energy. We then compare the water-production and cooling changes needed to serve the same amount of IT activity. The functional unit is heat rejection for one megawatt-hour of IT energy. This keeps the supply and efficiency options on a comparable basis.`},
    {title:'Four strategies and a common baseline',speaker:'Aditya',text:`The four strategies differ in water supply and heat rejection. A1 uses wet cooling with desalinated water. A2 uses wet cooling with NEWater. A3 also uses NEWater, but operates the cooling tower at higher cycles of concentration and recovers part of its blowdown. A4 uses dry heat rejection with wet assistance and NEWater for the remaining demand. All four share the same liquid-cooled IT baseline. We therefore count only differences attributable to the water and heat-rejection strategy. In particular, A4 receives no separate energy-saving credit simply for adopting liquid cooling. We include its additional fan and pump electricity, as well as incremental equipment cost. This boundary is essential to interpreting the results.`},
    {title:'Water demand',speaker:'Aditya',text:`For the 200-megawatt scenario, conventional wet cooling needs approximately ${f(n(base.water_2035_m3)/1e6)} million cubic metres of water in 2035 under the assumed utilisation. The corresponding figure in the 700-megawatt scenario is ${f(n(high.water_2035_m3)/1e6)} million cubic metres. Tower reuse reduces water demand by about ${pct(saving('A3'))} relative to A2. Dry rejection reduces it by about ${pct(saving('A4'))}, leaving ${f(n(low.water_2035_m3)/1e6)} million cubic metres in the 200-megawatt case. These values follow a heat balance and the selected operating assumptions. Historical hourly weather provides a screening estimate for wet assistance. It does not establish that a particular dry cooler can meet every hour of cooling demand. Equipment design and site measurements are still needed.`},
    {title:'Greenhouse-gas results',speaker:'Apurwa',text:`The greenhouse-gas comparison includes water production, delivery and the incremental electricity used for heat rejection. Common IT and liquid-loop burdens sit outside this partial boundary. The base results are ${f(L.A1.gwp_total)} kilograms of carbon dioxide equivalent per megawatt-hour of IT for A1, ${f(L.A2.gwp_total)} for A2, ${f(L.A3.gwp_total)} for A3 and ${f(L.A4.gwp_total)} for A4. ${shortNames[leastCarbon]} has the lowest emissions within this model boundary. A4 saves water, but its additional electricity can outweigh the avoided emissions from water production. The grid-emission scenarios test how that balance changes. We interpret the results as a comparison of these strategies, rather than a complete carbon footprint of a data centre.`},
    {title:'Cost results',speaker:'Aditya',text:`We separate the resource cost to society from the bill faced by an operator. The social calculation uses water-production and cooling costs, excluding tariffs that transfer money between organisations. The operator calculation uses the water tariff and commercial financing assumptions. Base social costs are ${f(K.A1.social_cost)} Singapore dollars per megawatt-hour for A1, ${f(K.A2.social_cost)} for A2, ${f(K.A3.social_cost)} for A3 and ${f(K.A4.social_cost)} for A4. ${shortNames[leastCost]} is the least costly base option. This does not mean it minimises water demand. The cost and water results answer different questions. We report carbon monetisation separately as a sensitivity case, so an assumed carbon price does not silently determine the main financial comparison.`},
    {title:'Assessment of broader priorities',speaker:'Apurwa',text:`The Analytic Hierarchy Process combines the calculated results with broader concerns, including water security and implementation. The balanced scenario ranks the strategies in the order ${order}. These weights are illustrative. They are informed by published concerns, but they are not measured preferences of PUB or any operator. We also test different weighting scenarios, changes in subcriterion weights and the effect of reducing overlap between criteria. A low consistency ratio checks the internal consistency of a comparison matrix. It does not validate the evidence or make a judgement objective. The AHP results therefore support discussion of the trade-offs. They should be read alongside the original water, carbon and cost values shown in the preceding slides.`},
    {title:'Sensitivity and uncertainty',speaker:'Vanshika',text:`The sensitivity analysis asks which assumptions could change the decision. The chart varies the additional PUE associated with dry rejection while holding its capital cost at the base assumption. Each line shows A4's social cost minus the comparator's cost. A value above zero means A4 is more expensive. We also vary capital costs and model parameters, then test uncertainty in preferences separately. ${prefWinner?`In the combined parameter and preference experiment, ${prefWinner.strategy} ranks first in ${pct(prefWinner.p_rank1)} of draws under the full hierarchy.`:'The preference experiment is reported separately from parameter uncertainty.'} This frequency is conditional on the ranges and distributions we selected. It is not a forecast probability that a technology will be best at a future site.`},
    {title:'Recommendations and validation needs',speaker:'Apurwa',text:`For PUB, the results support assessing water savings together with the energy needed to achieve them. NEWater is a relevant supply benchmark, while tower reuse offers a further reduction in demand that should be checked against treatment cost and water quality. For IMDA and operators, the main requirement is measured performance. A cooling proposal should report both water-use and power-use effectiveness under expected loads and hot-weather conditions. Dry rejection deserves consideration where water reduction is a priority, but its electricity penalty and equipment cost need a site-specific assessment. The public evidence available here supports a screening comparison. It does not support imposing one universal technology choice on every new facility.`},
    {title:'Conclusion',speaker:'Vanshika',text:`Our project connects data-centre growth to a water-planning decision. Supplying water through NEWater or desalination and reducing demand through cooling changes have different consequences. ${shortNames[leastWater]} uses the least water in the base case, while ${shortNames[leastCost]} has the lowest social cost. The comparison depends on the system boundary, the electricity penalty and the priorities used in the assessment. We provide the model and its assumptions so that these can be checked and updated when site data become available. The practical recommendation is to evaluate water and electricity together and keep the conditions behind each result visible. Thank you.`},
  ];
  sections[2].text+=` Blowdown is the water discharged to control dissolved solids in a cooling tower. A3 assumes ${f(assumption('coc_best'),0)} cycles of concentration and recovers ${pct(assumption('blowdown_recovery'))} of that discharge. These are operating assumptions that require water-quality checks.`;
  sections[3].text+=` The mature utilisation assumption is ${pct(assumption('util'))}. The demand values therefore do not represent continuous operation at the full rated IT load.`;
  sections[5].text+=` A3 costs the operator ${f(n(K.A2.operator_cost)-n(K.A3.operator_cost))} dollars less than A2 per megawatt-hour in the base case, because its lower water bill offsets the added recovery equipment.`;
  sections[7].text+=' Negative PUE values on this chart represent hypothetical electricity savings. They help locate the break-even condition, while the main uncertainty range assumes a positive dry-rejection penalty.';
  const words=s=>s.match(/\b[\p{L}\p{N}]+(?:['’-][\p{L}\p{N}]+)*\b/gu)?.length??0;
  const counts=sections.map(s=>words(s.text));
  const total=counts.reduce((a,b)=>a+b,0);
  const seconds=counts.map(c=>c/total*600);
  let elapsed=0;
  const clock=s=>`${Math.floor(s/60)}:${String(Math.round(s%60)).padStart(2,'0')}`;
  sections.forEach((s,i)=>{s.words=counts[i];s.start=clock(Math.round(elapsed));elapsed+=seconds[i];s.end=clock(Math.round(elapsed));});
  return {sections,total,rate:total/10};
}

async function video() {
  const p=Presentation.create({slideSize:{width:1280,height:720}});
  const script=videoScript();
  let s=page(p,'The Thirsty Cloud',1);
  text(s,"Water supply and cooling choices for Singapore's data-centre growth",52,164,1080,110,36,{color:C.teal});
  text(s,'DSS5202 Sustainable Systems Analysis\n2027–2035 planning scenarios',52,320,1040,80,27);
  text(s,'Aditya Vijindra Pandhari   A0328872R\nApurwa Kumari   A0333260R\nVanshika Dhamija   A0333989H',52,456,1100,110,24,{color:C.grey});
  s=page(p,'1. Problem and comparison basis',2);
  paragraphs(s,["Additional water demand from new data centres during 2027–2035",'Planning scenarios: 200, 500 and 700 MW by 2035','Functional unit: heat rejection for 1 MWh of IT energy','Partial boundary: water supply and incremental heat rejection'],52,151,1100,28,118);
  s=page(p,'2. Four strategies and a common baseline',3);
  systemDiagram(s,52,160,780,365,27);
  paragraphs(s,['Liquid-cooled IT in all strategies','A4 has no separate liquid-cooling credit','Incremental dry-rejection electricity and capital cost are included'],875,168,350,25,145);
  s=page(p,'3. Water demand in 2035',4);
  barChart(s,ids.map(a=>n(demand('S1',a).water_2035_m3)/1e6),'200 MW scenario (million m³/year)',45,148,760,440,24);
  paragraphs(s,[`A3 water reduction\n${pct(saving('A3'))} relative to A2`,`A4 water reduction\n${pct(saving('A4'))} relative to A2`,'Historical weather is a screening input, not equipment validation'],858,168,370,27,146);
  s=page(p,'4. Greenhouse-gas comparison',5);
  barChart(s,ids.map(a=>n(L[a].gwp_total)),'kg CO₂e per MWh of IT',45,148,760,440,24);
  paragraphs(s,[`${shortNames[leastCarbon]} has the lowest base emissions within the model boundary`,'Water savings and electricity savings need separate assessment','Common IT and liquid-loop emissions are excluded'],858,168,370,25,146);
  s=page(p,'5. Social and operator costs',6);
  table(s,[['Cost per MWh of IT','A1','A2','A3','A4'],['Social cost (S$)',...ids.map(a=>f(K[a].social_cost))],['Operator cost (S$)',...ids.map(a=>f(K[a].operator_cost))]],52,164,1176,210,[408,192,192,192,192],27);
  text(s,`${shortNames[leastCost]} has the lowest base social cost.`,52,419,1176,58,30,{bold:true,color:C.teal});
  text(s,'Tariffs belong in the operator calculation.\nCarbon-price cases are reported separately from financial costs.',52,503,1176,105,27);
  s=page(p,'6. Broader priorities and AHP',7);
  table(s,[['Balanced scenario','A1','A2','A3','A4'],['Priority',...ids.map(a=>f(A.find(r=>r.strategy===a).score,3))],['Rank',...ids.map(a=>String(rankMap[a]))]],52,164,1176,200,[408,192,192,192,192],27);
  paragraphs(s,['Weights represent illustrative priorities, not measured stakeholder preferences.','Sensitivity checks vary weights and reduce overlap between criteria.','Consistency ratios assess internal consistency, not evidence quality.'],52,415,1160,26,78);
  s=page(p,'7. Electricity and cost sensitivity',8);
  thresholdChart(s,40,150,790,450,23);
  paragraphs(s,['A4 minus comparator cost','Above zero: A4 costs more','Base dry-rejection capital cost held constant','Preference uncertainty is tested separately'],876,165,350,25,110);
  s=page(p,'8. Recommendations and limitations',9);
  paragraphs(s,['PUB: compare the energy required for each unit of water saved.','IMDA and operators: assess WUE and PUE together under actual loads.','Tower reuse needs water-quality and cost checks. Dry rejection needs site performance evidence.','Treat these results as a screening comparison with explicit assumptions.'],52,155,1160,29,119);
  s=page(p,'9. Conclusion',10);
  text(s,`${shortNames[leastWater]} uses the least water.\n${shortNames[leastCost]} has the lowest social cost.`,52,170,1176,140,37,{bold:true,color:C.teal});
  text(s,'The preferred strategy depends on electricity use, equipment cost and decision priorities.',52,361,1120,112,32);
  text(s,'Model assumptions and supporting calculations accompany the report.',52,545,1120,65,26,{color:C.grey});
  for(let i=0;i<p.slides.items.length;i++) p.slides.items[i].speakerNotes.text=`${script.sections[i].speaker} (${script.sections[i].start}–${script.sections[i].end})\n\n${script.sections[i].text}\n\n${SOURCES}`;
  const textOut=[
    '# The Thirsty Cloud video script',
    '',
    'DSS5202 Group 29. Aditya Vijindra Pandhari (A0328872R), Apurwa Kumari (A0333260R), Vanshika Dhamija (A0333989H).',
    '',
    `Spoken text: **${script.total} words**. Ten minutes requires an average of **${f(script.rate,1)} words per minute**, including pauses. At 130 words per minute, the spoken text takes **${f(script.total/130,1)} minutes** before pauses. The timings below allocate the full ten minutes in proportion to each section's word count. Confirm them in a recorded rehearsal.`,
    '',
    ...script.sections.flatMap((part,i)=>[`## Slide ${i+1}. ${part.title}`,``,`${part.start}–${part.end}. ${part.speaker}. ${part.words} spoken words.`,``,part.text,``]),
    '## Recording instructions',
    '',
    'Use the accompanying ten-slide deck. Each speaker should record their own sections, reading the values and conditions clearly. Pause briefly when a new chart appears. Rehearse the complete presentation, then adjust pauses or shorten a sentence where needed to keep the recording within ten minutes.',
    '',
    'Export the final self-recorded presentation as MP4, check the sound and duration, and include it in the final submission ZIP. The prepared slides and script do not replace the required recording.',
    '',
    'Source notes are included in the slide notes. All numerical findings in this script are read from the current model output tables. The supplied DSA5208 report guided the structure and writing style and remains unchanged.',
    '',
  ].join('\n');
  await fs.writeFile(path.join(OUT,'DSS5202_Group29_Video_Script.md'),textOut);
  await fs.writeFile(path.join(BUILD,'video_timing.json'),JSON.stringify({spoken_words:script.total,minutes_at_130_wpm:script.total/130,sections:script.sections.map(({text,...x})=>x)},null,2));
  return {presentation:p,stem:'DSS5202_Group29_Video_Slides',count:10,tables:[6,7],charts:[4,5,8]};
}

await fs.mkdir(BUILD,{recursive:true});await fs.mkdir(OUT,{recursive:true});
const built=kind==='poster'?await poster():kind==='video'?await video():null;
if(!built) throw new Error('Specify poster or video');
const {presentation,stem,count,tables,charts}=built;
const runDir=await fs.mkdtemp(path.join(BUILD,`${kind}-`));
const candidatePath=path.join(runDir,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
await fs.writeFile(path.join(runDir,'inspection.ndjson'),(await presentation.inspect({kind:'slide,textbox,chart,table',maxChars:150000})).ndjson);
for(const [i,slide] of presentation.slides.items.entries()) {
  const img=await presentation.export({slide,format:'png',scale:1.5});
  await fs.writeFile(path.join(runDir,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await img.arrayBuffer()));
}
await fs.mkdir(path.join(runDir,'final'),{recursive:true});
const finalPath=path.join(runDir,'final','validated.pptx');
await finalizePresentation({
  workspaceDir:ROOT,candidatePath,finalPath,pythonExecutable:process.env.RUNTIME_PYTHON,
  integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tables.flatMap(i=>['--require-native-table-slide',String(i)])],
  explicitTotalSlideCount:count,requiredNativeTableOwnerSlides:tables,requiredNativeChartOwnerSlides:charts,
  materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:kind==='poster'?['Arial','Times New Roman']:['Arial']},verifyArtifactToolImport:true,
  receiptPath:path.join(runDir,'validation.json'),
});
await fs.copyFile(finalPath,path.join(OUT,`${stem}.pptx`));
await fs.writeFile(path.join(BUILD,`${kind}_latest.json`),JSON.stringify({runDir,finalPath:path.join(OUT,`${stem}.pptx`)},null,2));
console.log(`Built ${stem}.pptx; previews and validation: ${runDir}`);
