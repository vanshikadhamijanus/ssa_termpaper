"""Hand edits applied to the pre-built poster (7 November 2026).

The poster was generated on 25 October by a toolchain outside this
environment. This script records every later edit so it can be re-applied to
the original: one term for the society perspective ("resource cost"), a
trimmed chart axis, a break-even note and the AHP viewpoint result. Numbers
are read from outputs/tables; nothing is typed in. The video deck is built
separately by 15_build_video_slides.py.

Run from the project root:  python src/14_edit_presentations.py
"""
from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

ROOT = Path(__file__).resolve().parents[1]
DELIV = ROOT / 'deliverables'
TAB = ROOT / 'outputs/tables'


def values():
    B = pd.read_csv(TAB / 'breakeven.csv')
    S = pd.read_csv(TAB / 'ahp_scores_by_scenario.csv')
    ghg = B[B.question.str.contains('A4 versus A2:.*GHG')].breakeven.iloc[0]
    first = {sc: g.sort_values('rank').strategy.iloc[0] for sc, g in S.groupby('weight_scenario')}
    a3_first = sum(v == 'A3' for v in first.values())
    assert first['W2 PUB / water security'] == 'A4', 'Poster text assumes A4 leads the PUB viewpoint'
    return dict(ghg_threshold=f'{ghg:.4f}'.rstrip('0'), a3_first=a3_first, n_views=len(first))


def set_text(shape_or_cell, new_text, paragraph=0):
    """Replace the text of one paragraph while keeping the first run's formatting."""
    tf = shape_or_cell.text_frame
    para = tf.paragraphs[paragraph]
    runs = para.runs
    runs[0].text = new_text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def edit_poster(v):
    path = DELIV / 'DSS5202_Group29_Poster.pptx'
    prs = Presentation(path)
    slide = prs.slides[0]
    for sh in slide.shapes:
        if sh.has_table:
            for row in sh.table.rows:
                if row.cells[0].text.startswith('Social cost'):
                    set_text(row.cells[0], 'Resource cost (S$)')
        if getattr(sh, 'has_chart', False) and sh.has_chart:
            ch = sh.chart
            set_text(ch.chart_title, 'A4 minus A2 resource cost (S$/MWh)')
            # Identify the axes by position in the XML: the bottom axis (axPos b)
            # carries the PUE values, the left axis the cost difference.
            axes = {ax._element.xpath('./c:axPos')[0].get('val'): ax for ax in (ch.category_axis, ch.value_axis)}
            pue_axis, cost_axis = axes['b'], axes['l']
            pue_axis.minimum_scale, pue_axis.maximum_scale, pue_axis.major_unit = 0.0, 0.10, 0.02
            cost_axis.minimum_scale, cost_axis.maximum_scale, cost_axis.major_unit = 0.0, 25.0, 5.0
            chart_left, chart_top = sh.left, sh.top
        if sh.has_text_frame:
            t = sh.text_frame.text
            if t.startswith('Methods: LCA, LCC and AHP'):
                set_text(sh, f'AHP: A3 first in {v["a3_first"]} of {v["n_views"]} views; A4 leads only in PUB\'s view.', paragraph=1)
            elif t.startswith('A2'):
                set_text(sh, f'A2: lowest resource cost. A3: best all-rounder. A4: least water, but needs extra PUE below {v["ghg_threshold"]} to match A2 on carbon.')
    for sh in list(slide.shapes):
        if sh.name == 'Break-even note':
            sh._element.getparent().remove(sh._element)
    note = slide.shapes.add_textbox(chart_left + Inches(0.95), chart_top + Inches(0.36), Inches(4.6), Inches(0.42))
    note.name = 'Break-even note'
    tf = note.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f'Base: extra PUE 0.05. A4 dearer than A2 across the tested range.\nEqual carbon needs extra PUE ≤ {v["ghg_threshold"]}.'
    for r in p.runs:
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(0x66, 0x70, 0x85)
    prs.save(path)
    print('poster edited:', path)


if __name__ == '__main__':
    v = values()
    edit_poster(v)
