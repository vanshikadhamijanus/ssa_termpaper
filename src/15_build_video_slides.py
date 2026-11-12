"""Build the editable video slide deck from the report figures and result tables.

Fifteen narrated 16:9 slides plus two backup slides for a ten-minute recording: one idea per slide, the
report's own figures, and numbers filled from outputs/tables through
report_data_final.context(). Speaker notes carry only a suggested timing and
the source of each number; the team writes its own words.

    python src/15_build_video_slides.py   ->  deliverables/DSS5202_Group29_Video_Slides.pptx
"""
from pathlib import Path
import re

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

from report_data_final import context

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / 'outputs/figures'
# Legacy generated deck. The submitted deck is the team's 20-slide PowerPoint file in
# deliverables/, patched by 17_edit_video_deck.py; this builder writes to .build/legacy/ only.
OUT = ROOT / '.build/legacy/DSS5202_Group29_Video_Slides_generated.pptx'
NAVY, TEAL, INK, GREY, PALE = RGBColor(0x1D, 0x2D, 0x50), RGBColor(0x16, 0x7C, 0x80), RGBColor(0x25, 0x28, 0x2C), RGBColor(0x68, 0x70, 0x80), RGBColor(0xF2, 0xF5, 0xF8)
W, H = Inches(13.333), Inches(7.5)
MARGIN = Inches(0.55)


def rows_of(md):
    rows = [[v.strip() for v in line.strip('|').split('|')] for line in md.splitlines() if line.strip().startswith('|')]
    return [[c.replace('**', '') for c in r] for r in rows if not all(re.fullmatch(r':?-+:?', c) for c in r)]


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = W, H
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    # ---- primitives
    def text(self, slide, left, top, width, height, lines, size=18, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, space_after=6):
        box = slide.shapes.add_textbox(left, top, width, height)
        tf = box.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = anchor
        for k, line in enumerate(lines if isinstance(lines, list) else [lines]):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.alignment = align
            p.space_after = Pt(space_after)
            if isinstance(line, tuple):
                txt, opts = line
            else:
                txt, opts = line, {}
            r = p.add_run()
            r.text = txt
            r.font.size = Pt(opts.get('size', size))
            r.font.bold = opts.get('bold', bold)
            r.font.color.rgb = opts.get('color', color)
            r.font.name = 'Arial'
        return box

    def bullets(self, slide, left, top, width, height, items, size=17):
        box = slide.shapes.add_textbox(left, top, width, height)
        tf = box.text_frame
        tf.word_wrap = True
        for k, item in enumerate(items):
            p = tf.paragraphs[0] if k == 0 else tf.add_paragraph()
            p.space_after = Pt(8)
            lead, rest = (item if isinstance(item, tuple) else (None, item))
            r0 = p.add_run()
            r0.text = '•  '
            r0.font.size = Pt(size)
            r0.font.color.rgb = TEAL
            r0.font.name = 'Arial'
            if lead:
                r1 = p.add_run()
                r1.text = lead + ' '
                r1.font.bold = True
                r1.font.size = Pt(size)
                r1.font.color.rgb = NAVY
                r1.font.name = 'Arial'
            r2 = p.add_run()
            r2.text = rest
            r2.font.size = Pt(size)
            r2.font.color.rgb = INK
            r2.font.name = 'Arial'
        return box

    def picture(self, slide, name, left, top, width, height):
        path = FIG / name
        with Image.open(path) as im:
            w, h = im.size
        scale = min(width / w, height / h)
        pw, ph = int(w * scale), int(h * scale)
        return slide.shapes.add_picture(str(path), left + (width - pw) // 2, top + (height - ph) // 2, pw, ph)

    def table(self, slide, left, top, width, rows, size=14, col_widths=None, row_height=Inches(0.42)):
        shape = slide.shapes.add_table(len(rows), len(rows[0]), left, top, width, row_height * len(rows))
        tbl = shape.table
        if col_widths:
            total = sum(col_widths)
            for j, cw in enumerate(col_widths):
                tbl.columns[j].width = int(width * cw / total)
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                cell = tbl.cell(i, j)
                cell.text = val
                cell.margin_left = cell.margin_right = Inches(0.08)
                cell.margin_top = cell.margin_bottom = Inches(0.04)
                p = cell.text_frame.paragraphs[0]
                p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
                for r in p.runs:
                    r.font.size = Pt(size)
                    r.font.name = 'Arial'
                    r.font.bold = i == 0
                    r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF) if i == 0 else INK
                cell.fill.solid()
                cell.fill.fore_color.rgb = NAVY if i == 0 else (PALE if i % 2 else RGBColor(0xFF, 0xFF, 0xFF))
        return shape

    # ---- slide scaffolding
    def slide(self, title, notes_seconds, note_source):
        self.n += 1
        s = self.prs.slides.add_slide(self.blank)
        self.text(s, MARGIN, Inches(0.3), W - 2 * MARGIN, Inches(0.7), title, size=28, color=NAVY, bold=True)
        rule = s.shapes.add_connector(1, MARGIN, Inches(1.05), W - MARGIN, Inches(1.05))
        rule.line.color.rgb = TEAL
        rule.line.width = Pt(1.25)
        self.text(s, MARGIN, H - Inches(0.45), Inches(8), Inches(0.3), 'DSS5202 Group 29   The Thirsty Cloud', size=11, color=GREY)
        s.notes_slide.notes_text_frame.text = f'Suggested time: about {notes_seconds} s. Numbers from: {note_source}.' if notes_seconds else ''
        s._footer_box = None
        return s

    def finish(self):
        total = len(self.prs.slides)
        for k, s in enumerate(self.prs.slides, 1):
            self.text(s, W - MARGIN - Inches(1.4), H - Inches(0.45), Inches(1.4), Inches(0.3), f'{k} / {total}', size=11, color=GREY, align=PP_ALIGN.RIGHT)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        self.prs.save(OUT)
        print(OUT, total, 'slides')


def build():
    q = context()
    d = Deck()
    full_w = W - 2 * MARGIN
    body_top = Inches(1.25)
    body_h = H - body_top - Inches(0.6)

    # 1 Title
    s = d.prs.slides.add_slide(d.blank); d.n += 1
    band = s.shapes.add_shape(1, 0, Inches(2.2), W, Inches(2.0))
    band.fill.solid(); band.fill.fore_color.rgb = NAVY; band.line.fill.background()
    d.text(s, MARGIN, Inches(2.35), full_w, Inches(0.9), 'The Thirsty Cloud', size=44, color=RGBColor(0xFF, 0xFF, 0xFF), bold=True, align=PP_ALIGN.CENTER)
    d.text(s, MARGIN, Inches(3.25), full_w, Inches(0.7), "Meeting the water needs of Singapore's data-centre growth", size=22, color=RGBColor(0xFF, 0xFF, 0xFF), align=PP_ALIGN.CENTER)
    d.text(s, MARGIN, Inches(4.6), full_w, Inches(0.5), 'DSS5202 Sustainable Systems Analysis  |  Term Paper  |  Group 29', size=18, color=TEAL, align=PP_ALIGN.CENTER)
    d.text(s, MARGIN, Inches(5.2), full_w, Inches(1.2), ['Aditya Vijindra Pandhari  A0328872R', 'Apurwa Kumari  A0333260R', 'Vanshika Dhamija  A0333989H'], size=16, color=INK, align=PP_ALIGN.CENTER, space_after=2)
    d.text(s, MARGIN, Inches(6.5), full_w, Inches(0.4), 'November 2026', size=14, color=GREY, align=PP_ALIGN.CENTER)
    s.notes_slide.notes_text_frame.text = 'Suggested time: about 20 s. Introduce the team and the title.'

    # 2 Question
    s = d.slide('1. The question', 35, 'Section 1 and 4 of the report; demand_summary.csv')
    d.bullets(s, MARGIN, body_top, Inches(7.4), body_h, [
        ('200 MW', 'of new IT capacity was provisionally allocated under DC-CFA2 in 2026, within a planned 1.6 GW maximum IT load.'),
        ('Cooling towers', 'reject heat by evaporating water. In Singapore that water is imported, desalinated or reclaimed, all at a cost.'),
        ('Our question:', 'how can Singapore meet the cooling-water needs of new data centres at reasonable cost, with low carbon, and without straining the water system?'),
        ('Basis:', 'every option is compared per 1 MWh of IT energy, 2027 to 2035, then stress-tested.'),
    ], size=18)
    panel = s.shapes.add_shape(1, Inches(8.3), body_top, Inches(4.5), Inches(4.6)); panel.fill.solid(); panel.fill.fore_color.rgb = PALE; panel.line.fill.background()
    d.text(s, Inches(8.5), Inches(1.45), Inches(4.1), Inches(4.3), [
        ('Ordinary towers, 200 MW, 2035', {'size': 15, 'color': GREY}),
        (f"{q['water_A2']} million m³ a year", {'size': 34, 'color': NAVY, 'bold': True}),
        (f"about {q['national_share']}% of the {q['national_water']} million m³ of potable water and NEWater sold in {q['national_year']}", {'size': 15, 'color': INK}),
        ('', {'size': 8}),
        ('With recovery (A3)', {'size': 15, 'color': GREY}),
        (f"{q['water_A3']} million m³", {'size': 26, 'color': TEAL, 'bold': True}),
        ('With dry cooling (A4)', {'size': 15, 'color': GREY}),
        (f"{q['water_A4']} million m³", {'size': 26, 'color': TEAL, 'bold': True}),
    ], space_after=2)

    # 3 Options
    s = d.slide('2. Four ways to supply and use the water', 35, 'Figure 1 of the report')
    d.picture(s, 'fig_report_options.png', MARGIN, body_top, full_w, body_h - Inches(0.5))
    d.text(s, MARGIN, H - Inches(1.05), full_w, Inches(0.5), 'All four share the same liquid-cooled IT equipment. They differ only in where the water comes from and how heat is rejected.', size=16, color=GREY, align=PP_ALIGN.CENTER)

    # 4 Boundary
    s = d.slide('3. What is inside the comparison', 30, 'Figure 3 and Section 2 of the report')
    d.picture(s, 'fig_report_boundary.png', MARGIN, body_top, Inches(8.4), body_h)
    d.bullets(s, Inches(9.2), body_top + Inches(0.2), Inches(3.7), body_h, [
        ('Functional unit:', 'heat rejection for 1 MWh of IT energy, including the make-up water it needs.'),
        ('Counted:', 'water production, conveyance, heat rejection, blowdown recovery, extra fan electricity.'),
        ('Not counted:', 'the IT equipment, building and liquid loop (common to all), upstream wastewater treatment, embodied emissions of the cooling kit.'),
        ('Impacts:', 'climate change and water use; brine and blowdown as volumes only.'),
    ], size=15)

    # 5 Method
    s = d.slide('4. Method: demand model, LCA, LCC, AHP, sensitivity', 30, 'Figure 2 of the report')
    d.picture(s, 'fig_report_method.png', MARGIN, body_top, Inches(7.6), body_h)
    d.bullets(s, Inches(8.4), body_top + Inches(0.2), Inches(4.5), body_h, [
        ('Demand:', 'capacity × utilisation × ramp × 8,760 h × WUE.'),
        ('LCA:', 'electricity for water and fans × grid factor, plus a small non-energy term.'),
        ('LCC:', 'resource cost to society (3%, no taxes) and the operator bill (8%, tariffs).'),
        ('AHP:', f"4 criteria, 11 sub-criteria, 5 viewpoints; consistency ratio at most {q['max_cr']}."),
        ('Tests:', f"tornado, {q['n_mc']} Monte Carlo draws, break-evens, structural cases, {q['n_pref']} preference trials."),
    ], size=15)

    # 6 Water demand
    s = d.slide('5. Water use per option', 40, 'Figure 4 and Table 4 of the report')
    d.picture(s, 'fig_wue_ladder.png', MARGIN, body_top, Inches(7.3), body_h)
    demand = rows_of(q['table_demand'])
    d.text(s, Inches(8.2), body_top, Inches(4.7), Inches(0.4), 'Annual make-up water in 2035, million m³', size=15, color=GREY)
    d.table(s, Inches(8.2), body_top + Inches(0.45), Inches(4.7), demand, size=14, col_widths=[1.2, 1.4, 1.1, 1, 1])
    d.bullets(s, Inches(8.2), Inches(3.9), Inches(4.7), Inches(2.5), [
        ('A1 and A2:', f"PUB benchmark {q['wue_base']} m³/MWh; the model is calibrated to it at an assumed 3 cycles of concentration."),
        ('A3:', f"8 cycles plus 70% blowdown recovery, {q['wue_A3']} m³/MWh, {q['a3_water_saving_r']}% less water; 8 cycles alone already give {q['coc8_wue']}."),
        ('A4:', f"dry loop with a 20% wet share, {q['wue_A4']} m³/MWh, {q['a4_water_saving_r']}% less water."),
    ], size=14)

    # 7 Where A4's water comes from
    s = d.slide("6. Where A4's water comes from, and the weather check", 40, 'Section 4, Tables S5 and S6 of the report')
    d.bullets(s, MARGIN, body_top, Inches(6.0), body_h, [
        ('80 / 20 split:', f"the dry loop takes 80% of the heat; the other 20% goes through wet towers all year, which alone is {q['a4_wet_remainder']} m³/MWh."),
        ('Hot-hour trim:', f"the dry loop needs water above 30°C, {q['trim_percent']}% of hours in the gridded record, adding {q['a4_trim_part']} m³/MWh."),
        ('So', f"{q['a4_wet_share_pct']}% of A4's water follows from an assumed split, not from the weather."),
        ('Weather check:', f"the Open-Meteo record runs {q['weather_bias']}°C cooler than the SingStat series from the Changi climate station over {q['weather_months']} months, a cross-location gap."),
        ('Hypothetical warming case:', f"warming every hour by {q['weather_bias']}°C lifts A4 to {q['a4_wue_bias']} m³/MWh; the saving falls from {q['a4_water_saving_r']}% to {q['a4_saving_bias']}%. A4 still uses the least water; cost and carbon barely move while the extra PUE is held fixed."),
    ], size=15)
    a4 = rows_of(q['table_a4_weather'])
    keep = [a4[0]] + [r for r in a4[1:] if r[0].startswith(('Base', 'Hypothetical warming', 'Register'))]
    short = [[r[0].replace('Hypothetical warming by the cross-location difference', 'Hypothetical warming').replace('Register low bound: ', '').replace('Register high bound: ', '').replace(' (30 °C threshold, record as archived)', ' (30 °C)'), r[1], r[2], r[3]] for r in keep]
    short[0] = ['Case', 'Hours needing trim', 'A4 WUE, m³/MWh IT', 'Saving vs A2']
    d.text(s, Inches(6.9), body_top, Inches(6.0), Inches(0.4), 'A4 under warmer conditions', size=15, color=GREY)
    d.table(s, Inches(6.9), body_top + Inches(0.45), Inches(6.0), short, size=13, col_widths=[2.3, 1.3, 1, 1.1])

    # 8 Carbon
    s = d.slide('7. Carbon: fan electricity decides it', 40, 'Table 5, Figure 5 and Table 11 of the report')
    d.picture(s, 'fig_lca_hotspots.png', MARGIN, body_top, Inches(7.4), body_h)
    d.bullets(s, Inches(8.2), body_top + Inches(0.1), Inches(4.7), body_h, [
        ('A3 lowest:', f"{q['gwp_A3']} kg CO₂e/MWh, {q['a3_carbon_saving_r']}% below A2 ({q['gwp_A2']})."),
        ('A1:', f"{q['gwp_A1']} kg, because desalination needs five times the energy of NEWater."),
        ('A4:', f"{q['gwp_A4']} kg, about {q['a4_gwp_multiple']} times A2; its assumed extra {q['dry_kwh']} kWh of fan electricity dwarfs the water energy saved."),
        ('Break-even:', f"A4 matches A2 on carbon only if its extra PUE is {q['ghg_threshold']} or lower."),
        ('Grid factor:', f"{q['base_grid_factor']} kg CO₂/kWh, the 2027 to 2035 average; green-energy pledges are not treated as zero emissions."),
    ], size=15)

    # 9 Cost
    s = d.slide('8. Cost: society and the operator see different answers', 45, 'Table 6, Figure 7 and Table 11 of the report')
    d.picture(s, 'fig_lcc_stack.png', MARGIN, body_top, full_w, Inches(3.3))
    d.bullets(s, MARGIN, Inches(4.7), Inches(6.0), Inches(2.2), [
        ('Resource cost:', f"A2 cheapest at S${q['cost_A2']}/MWh; A1 S${q['cost_A1']}; A3 S${q['cost_A3']}; A4 S${q['cost_A4']}, about {q['a4_cost_multiple']} times A2."),
        ('A3 vs A2:', f"costs society S${q['a3_social_premium']} more, but saves the operator S${q['a3_operator_saving']} per MWh at today's tariff, before any maintenance, chemicals or membranes; about S${q['maint_breakeven']} per MW-year of those would remove the saving."),
    ], size=15)
    d.bullets(s, Inches(6.9), Inches(4.7), Inches(6.0), Inches(2.2), [
        ('Tariff break-even:', f"recovery stops paying for the operator below a NEWater price of S${q['reuse_tariff_threshold']}/m³ (now S${q['newater_tariff']})."),
        ('Discharge:', 'with an assumed discharge-cost proxy of S$1.09/m³ (the waterborne fee, not an established resource cost), A3 becomes cheaper than A2 for society too.'),
    ], size=15)

    # 11 AHP hierarchy
    s = d.slide('9. Bringing the criteria together: AHP', 30, 'Figure 8 and Tables S7 and S8 of the report')
    d.picture(s, 'fig_ahp_hierarchy.png', MARGIN, body_top, Inches(7.8), body_h)
    d.bullets(s, Inches(8.6), body_top + Inches(0.1), Inches(4.3), body_h, [
        ('Four criteria:', 'economic, environmental, water security, implementation.'),
        ('Six sub-criteria [Q]', 'are scored from the model; five [P] are our pairwise judgements on the 1 to 9 scale.'),
        ('Consistency:', f"every judgement matrix has a consistency ratio of at most {q['max_cr']}."),
        ('Weights:', 'five illustrative viewpoints: balanced, PUB, operator, climate, growth. They are not surveys.'),
    ], size=15)

    # 12 AHP results
    s = d.slide('10. AHP result: A3 leads; A4 only on water security', 45, 'Table 9, Table 14 and Figure 9 of the report')
    d.picture(s, 'fig_ahp_scores.png', MARGIN, body_top, Inches(7.8), body_h)
    d.bullets(s, Inches(8.6), body_top + Inches(0.1), Inches(4.3), body_h, [
        ('Balanced weights:', 'A3, then A2, A1, A4.'),
        ('Four of five viewpoints', 'put A3 first under our linear scoring rule.'),
        ('PUB viewpoint:', f"A4 first, because water security carries 54% of the weight; A4 overtakes A3 once that weight passes about {q['c3_crossing']}."),
        ('Scoring rule test:', f"with Saaty's ratio rule the operator viewpoint becomes a near tie, {q['ratio_w3_lead']} numerically first (A2 {q['ratio_w3_a2']}, A3 {q['ratio_w3_a3']}); the other four viewpoints keep their leader."),
        ('Random weights:', '2,000 trials with random weights and perturbed judgements put A3 first in 76% and A4 in 20%.'),
    ], size=15)

    # 13 Tornado
    s = d.slide('11. Which inputs move the cost most', 30, 'Figure 10 and Table S1 of the report')
    d.picture(s, 'fig_tornado_cost_top5.png', MARGIN, body_top, Inches(8.6), body_h)
    d.bullets(s, Inches(9.4), body_top + Inches(0.1), Inches(3.5), body_h, [
        ('A1:', 'desalination energy and the plant electricity price.'),
        ('A2:', 'NEWater operating and capital cost.'),
        ('A3:', 'the recovery equipment cost, a team assumption.'),
        ('A4:', 'the extra dry-cooling PUE alone moves the cost from S$6 lower to S$10 higher per MWh.'),
        ('Register:', f"{q['n_parameters']} inputs, {q['n_verified']} verified, {q['n_judgment']} team judgements."),
    ], size=15)

    # 14 Break-evens and Monte Carlo
    s = d.slide('12. Break-evens and 10,000 draws', 45, 'Tables 10 and 11 and Figure S4 of the report')
    d.picture(s, 'fig_cooling_thresholds.png', MARGIN, body_top, Inches(6.2), Inches(3.6))
    be = rows_of(q['table_breakeven'])
    pick = [be[0]] + [r for r in be[1:] if any(k in r[0] for k in ('on cost', 'on carbon', 'NEWater tariff', 'recovery capex'))]
    pick = [[r[0].replace('A4 matches A2 on cost: extra dry-cooling PUE of', 'A4 = A2 on cost: extra PUE').replace('A4 matches A2 on carbon: extra dry-cooling PUE of', 'A4 = A2 on carbon: extra PUE').replace('Operator is no better off with A3 than A2: NEWater tariff, S$/m³', 'A3 = A2 for operator: NEWater tariff S$/m³').replace('A3 costs society the same as A2: recovery capex, S$/MW IT', 'A3 = A2 for society: recovery capex S$/MW'), r[1], r[2]] for r in pick]
    d.table(s, Inches(7.0), body_top, Inches(5.9), pick, size=13, col_widths=[3.4, 1.1, 1.4])
    d.bullets(s, MARGIN, Inches(5.0), full_w, Inches(1.8), [
        ('Monte Carlo, 10,000 draws:', f"A2 has the lowest resource cost in every draw; A3 the lowest carbon in every draw; A3 has the lower operator cost in {q['p_a3_cheaper_operator']}% of the sampled parameter combinations."),
        ('Negative PUE break-even:', 'at the assumed capital premium, cost parity would need an electricity advantage over wet cooling, outside the positive-penalty range used in the main analysis.'),
    ], size=15)

    # 16 Recommendations
    s = d.slide('13. What we recommend', 45, 'Section 9 of the report')
    cols = [
        ('PUB', [f"The model gives a level to test against: {q['coc8_wue']} m³/MWh at 8 cycles and {q['wue_A3']} with recovery, versus the 2.0 Roadmap target. Site evidence on cycles and water quality is needed before any figure becomes a condition.",
                 'Treat water saved and money saved as separate questions; recovery lowers national demand but raises the resource cost.']),
        ('IMDA and EDB', ['Ask bidders to report annual PUE and WUE together so the water-energy trade-off is visible.',
                          f"Use the {q['ghg_threshold']} extra-PUE break-even to decide what performance evidence a dry-cooling proposal must bring."]),
        ('Operators', [f"Look first at higher cycles of concentration, which give about {q['share_before_recovery']}% of A3's water saving, then at recovery. The modelled operator saving of S${q['a3_operator_saving']}/MWh is small and excludes maintenance.",
                       'Choose dry cooling only if its measured electricity penalty is far below our assumption or water carries a much higher value.']),
    ]
    cw = (full_w - Inches(0.6)) // 3
    for k, (head, items) in enumerate(cols):
        left = MARGIN + k * (cw + Inches(0.3))
        panel = s.shapes.add_shape(1, left, body_top, cw, Inches(5.3)); panel.fill.solid(); panel.fill.fore_color.rgb = PALE; panel.line.fill.background()
        d.text(s, left + Inches(0.2), body_top + Inches(0.15), cw - Inches(0.4), Inches(0.5), head, size=20, color=TEAL, bold=True)
        d.bullets(s, left + Inches(0.2), body_top + Inches(0.75), cw - Inches(0.4), Inches(4.4), items, size=14)

    # 17 Conclusion and limits
    s = d.slide('14. Conclusion, and what we do not know', 40, 'Sections 10 and 11 of the report')
    d.text(s, MARGIN, body_top, Inches(6.1), Inches(0.4), 'Conclusion', size=18, color=TEAL, bold=True)
    d.bullets(s, MARGIN, body_top + Inches(0.5), Inches(6.1), body_h, [
        ('A2', 'is the cheapest for society.'),
        ('A3', 'saves water and carbon, can save the operator money, and ranks first in four of five viewpoints under the linear rule.'),
        ('A4', 'saves the most water but only pays off if its electricity penalty is far smaller than assumed.'),
        ('The useful output', 'is the set of thresholds: the dry-cooling PUE, the NEWater tariff, the discharge price and the wet share that would change the answer.'),
    ], size=15)
    d.text(s, Inches(7.0), body_top, Inches(5.9), Inches(0.4), 'Limitations', size=18, color=TEAL, bold=True)
    d.bullets(s, Inches(7.0), body_top + Inches(0.5), Inches(5.9), body_h, [
        ('Borrowed benchmarks:', 'the wet-cooling figure comes from an existing fleet; dry-cooling energy, cost and the 80/20 split are our assumptions.'),
        ('Partial boundary:', 'cooling-equipment embodied emissions and upstream wastewater treatment excluded; climate and water only.'),
        ('Weather:', f"gridded data about {q['weather_bias']}°C cooler than the Changi station series; a cross-location gap, shown as a hypothetical warming case, not corrected."),
        ('Judgements:', 'the AHP weights and scoring rule are ours; site measurements and quotations would settle more than further modelling.'),
    ], size=15)

    # 10 Summary table
    s = d.slide('Backup A. Base case at a glance', 0, 'Tables 6 and 7 of the report')
    s.notes_slide.notes_text_frame.text = 'Backup slide, not narrated; show if asked. Tables 6 and 7 of the report.'
    summary = rows_of(q['table_summary'])
    d.text(s, MARGIN, body_top, Inches(7.2), Inches(0.4), 'Per MWh of IT energy', size=15, color=GREY)
    d.table(s, MARGIN, body_top + Inches(0.45), Inches(7.2), summary, size=14, col_widths=[2.2, 1.2, 1.4, 1.5, 1.5])
    npc = rows_of(q['table_npc'])
    d.text(s, Inches(8.1), body_top, Inches(4.8), Inches(0.4), 'Discounted cost 2027–35, 200 MW, S$ million', size=13, color=GREY)
    d.table(s, Inches(8.1), body_top + Inches(0.45), Inches(4.8), npc, size=14, col_widths=[2, 1, 1, 1, 1])
    d.bullets(s, MARGIN, Inches(4.6), full_w, Inches(2.0), [
        ('Reading the table:', 'A2 wins on resource cost, A3 on carbon and on the operator bill, A4 on water. No option wins everywhere, which is why the AHP follows.'),
        ('Caveat:', 'costs are before GST and exclude carbon pricing; emissions cover only the modelled water and heat-rejection components.'),
    ], size=15)

    # 15 Preference sensitivity
    s = d.slide('Backup B. How far the ranking depends on the weights', 0, 'Table 13 and Figure S2 of the report')
    s.notes_slide.notes_text_frame.text = 'Backup slide, not narrated; show if asked. Table 13 and Figure S2 of the report.'
    d.picture(s, 'fig_ahp_rainbow.png', MARGIN, body_top, full_w, Inches(3.4))
    d.bullets(s, MARGIN, Inches(4.8), full_w, Inches(2.0), [
        ('2,000 trials', 'with random weights and perturbed judgements: A3 first in 76%, A4 in 20%; with overlapping sub-criteria removed, A3 first in 65%.'),
        ('Rainbow plots:', f"A4 overtakes A3 only when water security weighs more than about {q['c3_crossing']}; A2 leads only when the economic weight is close to 1."),
    ], size=15)

    d.finish()


if __name__ == '__main__':
    build()
