"""Hand edits applied to the pre-built poster (7 November 2026).

The poster was generated on 25 October by a toolchain outside this
environment. This script records every later edit so it can be re-applied to
the original: one term for the society perspective ("resource cost"), a
trimmed chart axis, a break-even note and the AHP viewpoint result. After the
7 November review the straight-line cost chart was replaced by a freshly drawn
AHP viewpoint figure (poster_ahp.png), the stakeholder wording was qualified,
the ratio-rule tie was added and the matriculation numbers were put on the
face of the poster. Numbers are read from outputs/tables; nothing is typed in.
The video deck edits are in 17_edit_video_deck.py.

Run from the project root:  python src/14_edit_presentations.py
"""
from pathlib import Path

import sys

import pandas as pd
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import COLORS, SHORT, STRATEGIES

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
    CT = pd.read_csv(TAB / 'cooling_thresholds.csv')
    cfg = pd.read_csv(ROOT / 'config/assumptions.csv').set_index('id')['base']
    op = CT[(CT.comparison == 'A2') & ((CT.capex_dry_premium - cfg['capex_dry_premium']).abs() < 1)].operator_cost_equal_dpue.iloc[0]
    VS = pd.read_csv(TAB / 'validation_ahp_scoring.csv')
    tie = VS[(VS.rule.str.startswith('Inverse')) & (VS.weight_scenario.str.startswith('W3'))].tie_within_0_005.iloc[0]
    return dict(ghg_threshold=f'{ghg:.4f}'.rstrip('0'), op_threshold=f'{op:.4f}'.rstrip('0'), a3_first=a3_first,
                n_views=len(first), ratio_tie=bool(tie), scores=S)


def draw_ahp_figure(S):
    """Compact viewpoint chart for the poster, drawn from the current scores."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    views = list(dict.fromkeys(S.weight_scenario))
    labels = [v.split(' ', 1)[1].split(' /')[0].split(' (')[0] for v in views]
    fig, ax = plt.subplots(figsize=(6.4, 2.35), dpi=220)
    fig.subplots_adjust(left=.09, right=.995, top=.82, bottom=.2)
    x = np.arange(len(views)); w = .2
    for k, a in enumerate(STRATEGIES):
        vals = [S[(S.weight_scenario == v) & (S.strategy == a)].score.iloc[0] for v in views]
        ax.bar(x + (k - 1.5) * w, vals, w, color=COLORS[a], label=f'{a} {SHORT[a]}', edgecolor='white', linewidth=.6)
        for xi, val in zip(x, vals):
            ax.text(xi + (k - 1.5) * w, val + .004, f'{val:.2f}', ha='center', fontsize=5.6)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, .38); ax.set_yticks([0, .1, .2, .3]); ax.tick_params(axis='y', labelsize=7.5)
    ax.set_ylabel('AHP score', fontsize=8)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    ax.legend(ncol=4, fontsize=7, loc='upper center', bbox_to_anchor=(.5, 1.22), frameon=False, handlelength=1.2, columnspacing=1.1)
    path = ROOT / 'outputs/figures/poster_ahp.png'
    fig.savefig(path); plt.close(fig)
    return path


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
    figure = draw_ahp_figure(v['scores'])
    ids = 'Aditya Vijindra Pandhari (A0328872R)   Apurwa Kumari (A0333260R)   Vanshika Dhamija (A0333989H)'
    tie_note = ' (operator view ties under a ratio rule).' if v['ratio_tie'] else '.'
    chart_box = None
    summary_box = None
    for sh in list(slide.shapes):
        if sh.has_table:
            for row in sh.table.rows:
                if row.cells[0].text.startswith('Social cost'):
                    set_text(row.cells[0], 'Resource cost (S$)')
        if getattr(sh, 'has_chart', False) and sh.has_chart:
            chart_box = (sh.left, sh.top, sh.width, sh.height)
            sh._element.getparent().remove(sh._element)
        elif sh.name in ('Break-even note', 'Poster AHP figure'):
            if sh.shape_type == 13:
                chart_box = chart_box or (sh.left, sh.top, sh.width, sh.height)
            sh._element.getparent().remove(sh._element)
        elif sh.has_text_frame:
            t = sh.text_frame.text
            if t.startswith('Methods: LCA, LCC and AHP'):
                set_text(sh, f'AHP: A3 first in {v["a3_first"]} of {v["n_views"]} views; A4 first only on water security.', paragraph=1)
            elif t.startswith('A2'):
                set_text(sh, f'A2: lowest resource cost. A3: top balanced AHP score{tie_note} '
                             f'A4: least water; matches A2 on carbon only below extra PUE {v["ghg_threshold"]}.')
                for r in sh.text_frame.paragraphs[0].runs:
                    r.font.size = Pt(11.5)
                summary_box = sh
            elif t.startswith('4. Cost of reducing water use') or t.startswith('4. AHP ranking'):
                set_text(sh, '4. AHP ranking under five viewpoints')
            elif t.startswith('A1  Desalination'):
                set_text(sh, 'A3  NEWater, 8 cycles, reuse', paragraph=2)
            elif t.startswith('DSS5202 Group 29 (2026)'):
                set_text(sh, f'DSS5202 Group 29 (2026)   {ids}')
                for r in sh.text_frame.paragraphs[0].runs:
                    r.font.size = Pt(11)
    assert chart_box, 'chart area not found on the poster'
    left, top, width, height = chart_box
    with __import__('PIL.Image', fromlist=['Image']).open(figure) as im:
        aspect = im.size[1] / im.size[0]
    pic_width = min(width, int(height / aspect))
    pic = slide.shapes.add_picture(str(figure), left + (width - pic_width) // 2, top, width=pic_width)
    pic.name = 'Poster AHP figure'
    if summary_box is not None:
        # sit the summary directly under the figure so it stays clear of the footer
        summary_box.top = pic.top + pic.height + Inches(0.05)
        summary_box.text_frame.word_wrap = True
    prs.save(path)
    print('poster edited:', path)


if __name__ == '__main__':
    v = values()
    edit_poster(v)
