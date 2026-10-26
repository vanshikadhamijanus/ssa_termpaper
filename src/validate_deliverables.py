"""Check the report tables and presentation contents against saved model results."""
import json
from pathlib import Path
import re
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from docx import Document
from pypdf import PdfReader
import pandas as pd
from report_data import context

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables'
NS = {'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}


def main():
    checks = []
    doc = Document(OUT/'DSS5202_Group29_TermPaper.docx')
    prose = '\n'.join(p.text for p in doc.paragraphs)
    assert 'A0328872R' in prose and 'A0328873R' not in prose
    assert '{{' not in prose and '![' not in prose
    assert len(doc.inline_shapes) == 7
    values = context()
    template = (ROOT/'paper/report_template.md').read_text()
    table_keys = re.findall(r'\{\{(table_\w+)\}\}', template)
    assert len(doc.tables) == len(table_keys)
    cells_checked = 0
    for table, key in zip(doc.tables, table_keys):
        expected = [[v.strip() for v in line.strip('|').split('|')] for line in values[key].splitlines()]
        expected = [r for r in expected if not all(re.fullmatch(r':?-+:?', v) for v in r)]
        actual = [[c.text for c in row.cells] for row in table.rows]
        assert actual == expected, f'Report table differs from current results: {key}'
        cells_checked += sum(len(r) for r in actual)
    checks.append({'name':'report_tables_and_identity', 'status':'pass', 'tables':len(table_keys), 'cells':cells_checked, 'images':len(doc.inline_shapes)})
    for filename, required in [('TermPaper',None), ('Poster_preview',1), ('Video_Slides_preview',10)]:
        reader = PdfReader(OUT/f'DSS5202_Group29_{filename}.pdf')
        if required:
            assert len(reader.pages) == required
        assert all(len(p.extract_text().strip()) > 100 for p in reader.pages), f'Empty PDF page: {filename}'
        checks.append({'name':filename+'_pdf', 'status':'pass', 'pages':len(reader.pages)})
    lca = pd.read_csv(ROOT/'outputs/tables/lca_inventory.csv', index_col='strategy')
    lcc = pd.read_csv(ROOT/'outputs/tables/lcc_per_mwh.csv', index_col='strategy')
    with ZipFile(OUT/'DSS5202_Group29_Poster.pptx') as archive:
        xml = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
        table = xml.find('.//a:tbl', NS)
        rows = [[''.join(c.itertext()) for c in row.findall('a:tc',NS)] for row in table.findall('a:tr',NS)]
        expected = [[f'{frame.loc[a,key]:.2f}' for a in ['A1','A2','A3','A4']]
                    for frame,key in [(lca,'wue'),(lca,'gwp_total'),(lcc,'social_cost'),(lcc,'operator_cost')]]
        assert [r[1:] for r in rows[1:]] == expected, 'Poster table differs from results'
    checks.append({'name':'poster_result_table', 'status':'pass', 'numeric_cells':16})
    with ZipFile(OUT/'DSS5202_Group29_Video_Slides.pptx') as archive:
        slides = sorted(n for n in archive.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
        assert len(slides) == 10
        text = ' '.join(''.join(ET.fromstring(archive.read(n)).itertext()) for n in slides)
        assert 'A0328872R' in text and 'A0328873R' not in text
        for a in ['A1','A2','A3','A4']:
            for col in ['social_cost','operator_cost']:
                assert f'{lcc.loc[a,col]:.2f}' in text
    checks.append({'name':'video_slide_count_identity_and_cost_values', 'status':'pass', 'slides':10})
    dest = ROOT/'outputs/validation/deliverable_checks.json'
    dest.write_text(json.dumps({'overall':'pass', 'scope':'Content and package checks; visual inspection is recorded separately.', 'checks':checks}, indent=2)+'\n')
    print(f'Passed {len(checks)} deliverable checks; {cells_checked} report table cells match current outputs.')


if __name__ == '__main__':
    main()
