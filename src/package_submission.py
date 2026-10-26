"""Package current deliverables with the code, retained inputs and audit records."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables/DSS5202_Group29_Submission.zip'
REQUIRED = [
    'DSS5202_Group29_TermPaper.docx', 'DSS5202_Group29_TermPaper.pdf',
    'DSS5202_Group29_Poster.pptx', 'DSS5202_Group29_Poster_preview.pdf',
    'DSS5202_Group29_Video_Slides.pptx', 'DSS5202_Group29_Video_Slides_preview.pdf',
    'DSS5202_Group29_Video_Script.md',
]


def main():
    missing = [name for name in REQUIRED if not (ROOT/'deliverables'/name).exists()]
    if missing:
        raise SystemExit('Missing deliverables: '+', '.join(missing))
    checks = json.loads((ROOT/'outputs/validation/checks.json').read_text())
    rows = checks.get('checks', checks) if isinstance(checks, dict) else checks
    if any(c['status'] != 'pass' for c in rows):
        raise SystemExit('Resolve numerical validation failures before packaging.')
    content_checks = json.loads((ROOT/'outputs/validation/deliverable_checks.json').read_text())
    if content_checks.get('overall') != 'pass':
        raise SystemExit('Resolve deliverable validation failures before packaging.')
    files = []
    for folder in ['src', 'config', 'tests', 'data', 'paper', 'outputs', 'deliverables']:
        for path in (ROOT/folder).rglob('*'):
            relative = path.relative_to(ROOT)
            if (path.is_file() and not any(p.startswith('.') or p == '__pycache__' for p in relative.parts)
                    and path.suffix.lower() not in {'.pyc', '.zip'}):
                files.append(path)
    files += [ROOT/'README.md', ROOT/'PROJECT_PLAN.md', ROOT/'requirements.txt']
    files = sorted(set(files))
    names = {str(p.relative_to(ROOT)) for p in files}
    baseline_path = ROOT/'outputs/validation/protected_sources.json'
    original_baseline = json.loads(baseline_path.read_text())
    # The workspace audit retains the submitted proposal and style reference.
    # They are not model inputs and are deliberately omitted from the course ZIP.
    archive_baseline = {k:v for k,v in original_baseline.items() if k in names}
    extra = {
        'outputs/validation/workspace_protected_sources.json': json.dumps(original_baseline, indent=2)+'\n',
        'outputs/validation/protected_sources.json': json.dumps(archive_baseline, indent=2)+'\n',
    }
    recording = any(p.suffix.lower() == '.mp4' for p in files)
    status = ('Team recording included; verify its length and audio before submission.' if recording else
              'TEAM ACTION REQUIRED: Record the ten-minute presentation and add the MP4 before submission. Slides and a timed script are included.')
    extra['SUBMISSION_STATUS.txt'] = status+'\n\nThe ZIP contains the model, retained source data and generated deliverables. The original proposal and the DSA5208 style-reference PDF are omitted. The portable protected-source manifest covers included files; the complete workspace baseline is retained separately for the original audit.\n'
    manifest = []
    temp = OUT.with_suffix('.zip.tmp')
    with ZipFile(temp, 'w', compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for path in files:
            name = str(path.relative_to(ROOT))
            content = extra.pop(name, None)
            data = content.encode() if content is not None else path.read_bytes()
            archive.writestr(name, data)
            manifest.append({'file':name, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()})
        for name, content in extra.items():
            data = content.encode()
            archive.writestr(name, data)
            manifest.append({'file':name, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest()})
        archive.writestr('PACKAGE_MANIFEST.json', json.dumps({'created_at':datetime.now().astimezone().isoformat(), 'recording_included':recording, 'files':manifest}, indent=2)+'\n')
    with ZipFile(temp) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError('ZIP integrity failure: '+bad)
    temp.replace(OUT)
    print(f'{OUT.name}: {len(manifest)} files, {OUT.stat().st_size/1e6:.1f} MB. {status}')


if __name__ == '__main__':
    main()
