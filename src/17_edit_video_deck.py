"""Text edits to the 20-slide video deck (7 November 2026 review).

The deck deliverables/DSS5202_Group29_Video_Slides.pptx was prepared in
PowerPoint from the report figures and tables. This script records the
wording changes made after review so they can be re-applied: bounded
robustness claims, the three separate A4 break-evens, the cross-location
weather caveat, and the recommendation caveats. It is idempotent.

Run from the project root:  python src/17_edit_video_deck.py
"""
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / 'deliverables/DSS5202_Group29_Video_Slides.pptx'


def replace_paragraphs(frame_owner, old, new, size=None, exact=False):
    """Replace text inside paragraphs of one text frame; keeps the first run's format."""
    hits = 0
    for para in frame_owner.text_frame.paragraphs:
        full = ''.join(r.text for r in para.runs)
        match = full == old if exact else old in full
        if match and para.runs:
            para.runs[0].text = full.replace(old, new)
            for r in para.runs[1:]:
                r._r.getparent().remove(r._r)
            if size:
                para.runs[0].font.size = Pt(size)
            hits += 1
    return hits


def edit_slide_text(slide, old, new, size=None, exact=False):
    hits = 0
    for sh in slide.shapes:
        if sh.has_text_frame:
            n = replace_paragraphs(sh, old, new, size, exact)
            if n and size:
                sh.text_frame.word_wrap = True
            hits += n
    return hits


class _Notes:
    def __init__(self, slide):
        self.text_frame = slide.notes_slide.notes_text_frame


def edit_notes(slide, old, new):
    return replace_paragraphs(_Notes(slide), old, new)


# (slide number, kind, old, new, font size, marker). The marker is a phrase that
# shows the edit is already present, for decks that were edited by hand first.
EDITS = [
    (6, 'text', '4 criteria, 11 sub-criteria, 5 stakeholder viewpoints', '4 criteria, 11 sub-criteria, 5 illustrative viewpoints', None),
    (13, 'notes', 'It is a good all-rounder, with the lowest carbon, a reasonable cost and a real water saving.',
     'It ranks first because its lower withdrawals and emissions offset its higher resource cost under the linear rule.', None),
    (15, 'text', 'The key results hold in all 10,000 draws', 'Two rankings held in all 10,000 sampled combinations', None),
    (15, 'notes', 'Two results are firm: A2 has the lowest resource cost in every draw, and A3 has the lowest carbon in every draw.',
     'Two rankings held in every sampled combination: A2 has the lowest resource cost and A3 the lowest carbon, although joint boundary cases inside the ranges can reverse them.', None),
    (15, 'notes', 'joint boundary cases inside the ranges can reverse them: A2 has the lowest resource cost in every draw, and A3 has the lowest carbon in every draw.',
     'Two rankings held in every sampled combination: A2 has the lowest resource cost and A3 the lowest carbon, although joint boundary cases inside the ranges can reverse them.', None),
    (16, 'text', 'A4 matches A2 on cost', 'A4 matches A2 on resource cost', None),
    (16, 'text', 'Impossible: A4 never matches A2 on cost',
     'Needs a net electricity advantage at the assumed S$100k/MW premium. Even at zero penalty A4 costs S$1.60 against S$1.00.', 11),
    (16, 'notes', 'To match A2 on cost it would need a negative value, which cannot happen, so A4 never matches A2 on cost.',
     'To match A2 on resource cost it would need a net electricity advantage, because even with no penalty its capital premium leaves it at 1.60 dollars against 1.00. Operator-cost parity needs an extra PUE below about 0.008.', None),
    (17, 'text', 'Firm, size open', 'Held; size open', None),
    (17, 'text', 'Every draw, structural and weather case; even low-carbon fan power gives 6.1–17.5 kg',
     'Every draw, structural and weather case within the 0.02–0.10 PUE range; low-carbon fan power still gives 6.1–17.5 kg', None),
    (17, 'notes', 'A4 having the highest cost and carbon is firm, in every draw, structural case and weather case',
     'A4 having the highest cost and carbon held in every draw, structural case and weather case within the tested PUE range', None),
    (17, 'notes', 'A4 using the least water is firm', 'A4 using the least water held in every case', None),
    (17, 'notes', 'A2 being cheapest for society is firm unless', 'A2 being cheapest for society held unless', None),
    (17, 'notes', 'A3 having the lowest carbon is firm unless', 'A3 having the lowest carbon held unless', None),
    (18, 'text', 'per MWh as a screening condition for new wet-cooled sites', 'per MWh as a level to test new wet-cooled sites against, pending site evidence', None),
    (18, 'text', 'per MWh saved by blowdown recovery at today', 'per MWh saved by recovery, before maintenance, at today', None),
    (18, 'text', 'Check it against supplier quotes and measured recovery rates', 'Higher cycles alone give 78% of the saving; check recovery against quotes', None),
    (18, 'notes', 'a screening condition of about 1.5 cubic metres per MWh for new wet-cooled sites is achievable with known equipment',
     'about 1.5 cubic metres per MWh is a level to test new wet-cooled sites against, pending site evidence; it is achievable with known equipment', None),
    (19, 'text', 'About 1.37 °C cooler than the nearest station record; shown as a range, not corrected',
     'About 1.37 °C cooler than the Changi station series, a cross-location gap; shown as a range, not corrected', None),
    (19, 'notes', 'The weather record runs cooler than the nearest station.', 'The weather record runs cooler than the Changi station, a cross-location comparison.', None),
    (20, 'text', 'Saves the most water, but pays off only with a far smaller power penalty',
     'Saves the most water, but matches A2 only below an extra PUE of about 0.008 for cost and 0.002 for carbon', None),
    (20, 'notes', 'Dry cooling saves the most water but only pays off with a far smaller electricity penalty.',
     'Dry cooling saves the most water but matches A2 on the operator bill only below an extra PUE of about 0.008, and on carbon below 0.002.', None),
]


# Edits the team made by hand before this script existed; any of these phrases
# counts as "already applied" for the corresponding entry.
MARKERS = {
    (16, 'Impossible: A4 never matches A2 on cost'): 'electricity advantage',
    (15, 'Two results are firm'): 'Two rankings held',
    (15, 'joint boundary cases inside the ranges can reverse them: A2'): 'Two rankings held',
}


def marker_for(number, old):
    for (n, prefix), marker in MARKERS.items():
        if n == number and old.startswith(prefix):
            return marker
    return None


def main():
    prs = Presentation(DECK)
    slides = list(prs.slides)
    applied = skipped = 0
    deferred = []
    for number, kind, old, new, size in EDITS:
        slide = slides[number - 1]
        n = edit_slide_text(slide, old, new, size) if kind == 'text' else edit_notes(slide, old, new)
        if n:
            applied += 1
        else:
            deferred.append((number, kind, old, new))
    # Entries whose old text was absent must already be present in their final form
    # (the deck was partly edited by hand before this script existed).
    for number, kind, old, new in deferred:
        slide = slides[number - 1]
        haystack = ' '.join(''.join(r.text for r in p.runs) for sh in slide.shapes if sh.has_text_frame
                            for p in sh.text_frame.paragraphs) if kind == 'text' else slide.notes_slide.notes_text_frame.text
        marker = marker_for(number, old) or new
        assert marker in haystack, f'slide {number}: neither old nor new text found: {old[:60]!r}'
        skipped += 1
    # slide 17: the bare "Firm" labels
    applied += bool(edit_slide_text(slides[16], 'Firm', 'Held in all tests', exact=True))
    # slide 15: the hand-edited title lost its explicit size
    for sh in slides[14].shapes:
        if sh.has_text_frame:
            for para in sh.text_frame.paragraphs:
                if ''.join(r.text for r in para.runs).startswith('Two rankings held'):
                    for r in para.runs:
                        r.font.size = Pt(32)
    # slide 16: keep the resource-cost reading to two lines
    for sh in slides[15].shapes:
        if sh.has_text_frame and 'electricity advantage' in sh.text_frame.text:
            for para in sh.text_frame.paragraphs:
                if 'electricity advantage' in ''.join(r.text for r in para.runs):
                    para.runs[0].text = 'Needs a net electricity advantage at the S$100k/MW premium; even at zero penalty A4 costs S$1.60 vs S$1.00'
                    for r in para.runs[1:]:
                        r._r.getparent().remove(r._r)
                    para.runs[0].font.size = Pt(11)
    # slide 9: the break-even figure must stay on one line
    for sh in slides[8].shapes:
        if sh.has_text_frame and sh.text_frame.text.strip() == '0.0019':
            sh.text_frame.word_wrap = False
    # slide 9: readable font sizes
    for sh in slides[8].shapes:
        if not sh.has_text_frame:
            continue
        for para in sh.text_frame.paragraphs:
            for r in para.runs:
                if r.font.size is None:
                    continue
                pt = r.font.size.pt
                if pt < 8:
                    r.font.size = Pt(11)
                    sh.text_frame.word_wrap = True
                elif abs(pt - 10.5) < .01:
                    r.font.size = Pt(12)
                elif abs(pt - 27.5) < .01:
                    r.font.size = Pt(32)
    prs.save(DECK)
    print(f'deck edited: {DECK.name}; {applied} edits applied, {skipped} already present')


if __name__ == '__main__':
    main()
