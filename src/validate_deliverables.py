"""Check the report tables and presentation contents against saved model results.

The report is the final build (report_final.md through
13_build_paper_final.py). Every table in the resolved markdown, whether
generated from the result tables or written as a literal pipe table, must
match the Word document cell for cell.
"""
import json
from pathlib import Path
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from docx import Document
from pypdf import PdfReader
import pandas as pd
from report_data_final import context

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables'
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
EXPECTED_IMAGES = 16   # logo plus 15 figures
EXPECTED_SLIDES = 20


def markdown_tables(resolved):
    tables, block = [], []
    for line in resolved.splitlines() + ['']:
        if line.strip().startswith('|'):
            block.append(line.strip())
        elif block:
            rows = [[v.strip() for v in l.strip('|').split('|')] for l in block]
            tables.append([r for r in rows if not all(re.fullmatch(r':?-+:?', v) for v in r)])
            block = []
    return tables


def main():
    checks = []
    doc = Document(OUT/'DSS5202_Group29_TermPaper.docx')
    prose = '\n'.join(p.text for p in doc.paragraphs)
    assert 'A0328872R' in prose and 'A0328873R' not in prose
    assert '{{' not in prose and '![' not in prose
    assert len(doc.inline_shapes) == EXPECTED_IMAGES, f'{len(doc.inline_shapes)} images'
    values = context()
    source = (ROOT/'report_final.md').read_text()
    resolved = re.sub(r'\{\{(\w+)\}\}', lambda m: values[m[1]], source)
    expected_tables = markdown_tables(resolved)
    assert len(doc.tables) == len(expected_tables), f'{len(doc.tables)} docx tables vs {len(expected_tables)} in markdown'
    cells_checked = 0
    strip = lambda s: s.replace('**', '').replace('*', '')
    for k, (table, expected) in enumerate(zip(doc.tables, expected_tables)):
        actual = [[c.text for c in row.cells] for row in table.rows]
        expected = [[strip(v) for v in r] for r in expected]
        assert actual == expected, f'Report table {k+1} differs from current results'
        cells_checked += sum(len(r) for r in actual)
    # every reference-list entry must be cited in the text and vice versa
    body, refs = resolved.split('# References', 1)
    refs = refs.split('# Supplementary', 1)[0]
    uncited = []
    for entry in [e for e in refs.strip().split('\n\n') if e.strip()]:
        m = re.match(r'(.+?)\. \((\d{4}[ab]?|n\.d\.)', entry)
        author, year = m.group(1), m.group(2)
        surname = author.split(',')[0]
        initials = ''.join(w[0] for w in re.sub(r'[^A-Za-z ]', ' ', author).split() if w[0].isupper() and w.lower() not in ('and', 'of', 'for'))
        # abbreviations the text defines itself, e.g. "Public Utilities Board (PUB)" or "[ISO]"
        defined = re.findall(rf'{re.escape(author.split(", &")[0])}[^\n]{{0,80}}?[\[(]([A-Z][A-Z &]{{1,12}})[\])]', body)
        keys = {surname, initials, author, *defined}
        hit = any(re.search(rf'\b{re.escape(key)}\b.{{0,60}}{re.escape(year)}', body) for key in keys if key)
        if not hit:
            uncited.append(f'{author} ({year})')
    assert not uncited, f'Reference entries not cited in text: {uncited}'
    checks.append({'name':'report_tables_identity_and_citations', 'status':'pass', 'tables':len(expected_tables), 'cells':cells_checked, 'images':len(doc.inline_shapes), 'reference_entries':len(refs.strip().split('\n\n'))})
    reader = PdfReader(OUT/'DSS5202_Group29_TermPaper.pdf')
    assert all(len(p.extract_text().strip()) > 100 for p in reader.pages), 'Empty page in the report PDF'
    checks.append({'name':'TermPaper_pdf', 'status':'pass', 'pages':len(reader.pages)})
    pdf_text = ' '.join(p.extract_text() for p in PdfReader(OUT/'DSS5202_Group29_TermPaper.pdf').pages)
    assert 'Table 15.' in pdf_text and 'S11. Reproducibility' in pdf_text, 'Report PDF is not the final build'
    lca = pd.read_csv(ROOT/'outputs/tables/lca_inventory.csv', index_col='strategy')
    lcc = pd.read_csv(ROOT/'outputs/tables/lcc_per_mwh.csv', index_col='strategy')
    with ZipFile(OUT/'DSS5202_Group29_Poster.pptx') as archive:
        xml = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
        table = xml.find('.//a:tbl', NS)
        rows = [[''.join(c.itertext()) for c in row.findall('a:tc',NS)] for row in table.findall('a:tr',NS)]
        expected = [[f'{frame.loc[a,key]:.2f}' for a in ['A1','A2','A3','A4']]
                    for frame,key in [(lca,'wue'),(lca,'gwp_total'),(lcc,'social_cost'),(lcc,'operator_cost')]]
        assert [r[1:] for r in rows[1:]] == expected, 'Poster table differs from results'
        assert rows[3][0].startswith('Resource cost'), 'Poster uses the old cost label'
        text = ''.join(xml.itertext())
        assert 'social cost' not in text.lower(), 'Poster still says social cost'
    checks.append({'name':'poster_result_table_and_terms', 'status':'pass', 'numeric_cells':16})
    with ZipFile(OUT/'DSS5202_Group29_Video_Slides.pptx') as archive:
        slides = sorted(n for n in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
        assert len(slides) == EXPECTED_SLIDES, f'{len(slides)} slides'
        text = ' '.join(''.join(ET.fromstring(archive.read(n)).itertext()) for n in slides)
        charts = ' '.join(''.join(ET.fromstring(archive.read(n)).itertext()) for n in archive.namelist() if re.search(r'charts/chart\d+\.xml$', n))
        assert 'A0328872R' in text and 'A0328873R' not in text
        for a in ['A1','A2','A3','A4']:
            for col in ['social_cost','operator_cost']:
                assert f'{lcc.loc[a,col]:.2f}' in text
        assert 'social cost' not in (text + charts).lower(), 'Slides still say social cost'
    checks.append({'name':'video_slide_count_identity_cost_values_and_terms', 'status':'pass', 'slides':EXPECTED_SLIDES})
    dest = ROOT/'outputs/validation/deliverable_checks.json'
    from datetime import datetime
    dest.write_text(json.dumps({'run_time': datetime.now().astimezone().isoformat(timespec='seconds'), 'overall':'pass', 'scope':'Agreement between documents and saved model outputs; not a check of the assumptions.', 'checks':checks}, indent=2)+'\n')
    print(f'Passed {len(checks)} deliverable checks; {cells_checked} report table cells match current outputs.')


if __name__ == '__main__':
    main()
