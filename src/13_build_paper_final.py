"""Build the final report (November 2026) from report_final.md (project root)
and the current numerical outputs.

Reads report_final.md and report_data_final.context(); captions sit above
tables and figures (APA 7); bullet paragraphs use the List Bullet style;
literal pipe tables in the markdown are rendered as well as generated ones. Writes
deliverables/DSS5202_Group29_TermPaper.docx and .build/report/paper_final_resolved.md
(the resolved text, not versioned).
"""
from pathlib import Path
import json
import re

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

from report_data_final import context

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables'
SOURCE = ROOT / 'report_final.md'
RESOLVED = ROOT / '.build/report/paper_final_resolved.md'
NAVY = '1B2B4B'
TEAL = '137D7C'
GREY = '667085'

def shade(element, colour):
    node = OxmlElement('w:shd')
    node.set(qn('w:fill'), colour)
    element.append(node)


def inline(paragraph, text):
    """Bold, italic and code spans from the markdown source."""
    for piece in re.split(r'(\*\*.+?\*\*|\*[^*]+\*|`[^`]+`)', text):
        run = paragraph.add_run(piece.strip('*`') if piece.startswith(('*', '`')) else piece)
        if piece.startswith('**'):
            run.bold = True
        elif piece.startswith('*'):
            run.italic = True
        elif piece.startswith('`'):
            run.font.name = 'Consolas'
            run.font.size = Pt(9)


def page_field(paragraph, name):
    field = OxmlElement('w:fldSimple')
    field.set(qn('w:instr'), name)
    paragraph._p.append(field)


def make_table(doc, lines, total_cm=17.3):
    """Shaded header, banded rows, column widths from the longest entry in
    each column so long first-column labels fit."""
    rows = [[v.strip() for v in line.strip('|').split('|')] for line in lines]
    rows = [r for r in rows if not all(re.fullmatch(r':?-+:?', c) for c in r)]
    cols = len(rows[0])
    longest = [max(len(r[j]) for r in rows) for j in range(cols)]
    weights = [min(max(l, 4), 60) ** 0.75 for l in longest]
    widths = [total_cm * w / sum(weights) for w in weights]
    table = doc.add_table(rows=0, cols=cols)
    table.autofit = False
    for col, width in zip(table.columns, widths):
        col.width = Cm(width)
    for i, row in enumerate(rows):
        cells = table.add_row().cells
        props = table.rows[-1]._tr.get_or_add_trPr()
        props.append(OxmlElement('w:cantSplit'))
        if i == 0:
            props.append(OxmlElement('w:tblHeader'))
        for j, (cell, value) in enumerate(zip(cells, row)):
            cell.width = Cm(widths[j])
            tc = cell._tc.get_or_add_tcPr()
            shade(tc, NAVY if i == 0 else ('F0F3F6' if i % 2 else 'FFFFFF'))
            margins = OxmlElement('w:tcMar')
            for side in ['top', 'left', 'bottom', 'right']:
                el = OxmlElement('w:' + side)
                el.set(qn('w:w'), '65')
                el.set(qn('w:type'), 'dxa')
                margins.append(el)
            tc.append(margins)
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(1.5)
            para.paragraph_format.space_before = Pt(1.5)
            para.paragraph_format.line_spacing = 1.05
            if len(rows) <= 7 or i in (0, len(rows) - 1):
                para.paragraph_format.keep_with_next = True
            inline(para, value)
            for run in para.runs:
                run.font.size = Pt(9)
                if i == 0:
                    run.bold = True
                    run.font.color.rgb = RGBColor.from_string('FFFFFF')


def build():
    OUT.mkdir(exist_ok=True)
    values = context()
    source = SOURCE.read_text()
    missing = set(re.findall(r'\{\{(\w+)\}\}', source)) - values.keys()
    if missing:
        raise ValueError(f'Missing report fields: {sorted(missing)}')
    source = re.sub(r'\{\{(\w+)\}\}', lambda m: values[m[1]], source)
    RESOLVED.parent.mkdir(parents=True, exist_ok=True)
    RESOLVED.write_text(source)
    (ROOT / 'outputs/tables/report_values_final.json').write_text(
        json.dumps({k: v for k, v in values.items() if not k.startswith('table_') and k != 'references'}, indent=2) + '\n')
    meta, body = {}, []
    for line in source.splitlines():
        if line.startswith('%'):
            key, value = line[1:].split(' ', 1)
            meta[key] = value
        else:
            body.append(line)

    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(1.7), Cm(1.65)
    section.left_margin = section.right_margin = Cm(1.85)
    section.header_distance = section.footer_distance = Cm(.65)
    section.different_first_page_header_footer = True
    style = doc.styles['Normal']
    style.font.name, style.font.size = 'Arial', Pt(10.5)
    style.font.color.rgb = RGBColor.from_string('222B38')
    style.paragraph_format.space_after = Pt(7)
    style.paragraph_format.line_spacing = 1.12
    style.paragraph_format.widow_control = True
    for name, size, colour in [('Title', 22, NAVY), ('Subtitle', 16, TEAL), ('Heading 1', 15, NAVY), ('Heading 2', 11.5, TEAL)]:
        s = doc.styles[name]
        s.font.name, s.font.size = 'Arial', Pt(size)
        s.font.color.rgb = RGBColor.from_string(colour)
        s.font.bold = name != 'Subtitle'
        s.paragraph_format.keep_with_next = True
        s.paragraph_format.space_before = Pt(13)
        s.paragraph_format.space_after = Pt(7)
    cap = doc.styles['Caption']
    cap.font.name, cap.font.size = 'Arial', Pt(9)
    cap.font.italic = True
    cap.font.bold = False
    cap.font.color.rgb = RGBColor.from_string(GREY)
    cap.paragraph_format.space_before = Pt(6)
    cap.paragraph_format.space_after = Pt(4)
    cap.paragraph_format.keep_with_next = True
    bullet = doc.styles['List Bullet']
    bullet.font.name, bullet.font.size = 'Arial', Pt(10.5)
    bullet.paragraph_format.space_after = Pt(5)
    head = section.header.paragraphs[0]
    head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = head.add_run('The Thirsty Cloud  |  DSS5202 · Group 29')
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor.from_string(GREY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run('Page ')
    page_field(footer, 'PAGE')
    footer.add_run(' of ')
    page_field(footer, 'NUMPAGES')
    for r in footer.runs:
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor.from_string(GREY)
    # No w:updateFields flag: Word updates PAGE/NUMPAGES on layout anyway, and the
    # flag makes Word ask a blocking question when the file is opened for PDF export.
    doc.core_properties.title = meta['title']
    doc.core_properties.subject = meta['subtitle']
    doc.core_properties.author = 'Group 29: Aditya Vijindra Pandhari; Apurwa Kumari; Vanshika Dhamija'

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.add_run().add_picture(str(ROOT / 'assets/nus_logo.jpg'), width=Cm(2.4))
    for key, sty in [('title', 'Title'), ('subtitle', 'Subtitle')]:
        p = doc.add_paragraph(meta[key], sty)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(meta['course'])
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(16)
    for author in meta['authors'].split(';'):
        p = doc.add_paragraph(author.strip())
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
    p = doc.add_paragraph(meta['date'])
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(22)
    p = doc.add_paragraph()
    shade(p._p.get_or_add_pPr(), 'E8F2F2')
    p.paragraph_format.left_indent = p.paragraph_format.right_indent = Cm(.35)
    p.paragraph_format.space_before = p.paragraph_format.space_after = Pt(10)
    p.add_run('ABSTRACT\n').bold = True
    p.add_run(meta['abstract'])
    doc.add_page_break()

    i = 0
    in_references = False
    while i < len(body):
        line = body[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('# '):
            title = line[2:]
            in_references = title == 'References'
            p = doc.add_paragraph(title, 'Heading 1')
            if title == 'References':
                p.paragraph_format.page_break_before = True
            border = OxmlElement('w:pBdr')
            bottom = OxmlElement('w:bottom')
            for k, v in [('val', 'single'), ('sz', '8'), ('space', '5'), ('color', TEAL)]:
                bottom.set(qn('w:' + k), v)
            border.append(bottom)
            p._p.get_or_add_pPr().append(border)
        elif line.startswith('## '):
            doc.add_paragraph(line[3:], 'Heading 2')
        elif line.startswith('|'):
            lines = []
            while i < len(body) and body[i].strip().startswith('|'):
                lines.append(body[i].strip())
                i += 1
            make_table(doc, lines)
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue
        elif line.startswith('!['):
            match = re.fullmatch(r'!\[(.*?)\]\(([^)]+)\)', line)
            if not match:
                raise ValueError(f'Invalid figure: {line}')
            caption, filename = match.groups()
            path = ROOT / 'outputs/figures' / filename
            with Image.open(path) as image:
                w, h = image.size
            width = min(17.3, (14.0 if 'hierarchy' in filename else 10.5) * w / h)
            c = doc.add_paragraph(caption, 'Caption')
            c.paragraph_format.keep_with_next = True
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(8)
            p.add_run().add_picture(str(path), width=Cm(width))
        elif re.match(r'Table S?\d+\.', line):
            doc.add_paragraph(line, 'Caption')
        elif line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            inline(p, line[2:])
        else:
            p = doc.add_paragraph()
            inline(p, line)
            if in_references:
                p.paragraph_format.left_indent = Cm(1.0)
                p.paragraph_format.first_line_indent = Cm(-1.0)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.05
                for run in p.runs:
                    run.font.size = Pt(9.5)
        i += 1
    dest = OUT / 'DSS5202_Group29_TermPaper.docx'
    doc.save(dest)
    print(dest)


if __name__ == '__main__':
    build()
