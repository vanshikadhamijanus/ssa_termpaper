"""Package current deliverables with the code, retained inputs and audit records.

Refuses to package when the saved validation receipts are older than the
deliverables they vouch for. Use --require-recording for the final package.
"""
import argparse
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'deliverables/DSS5202_Group29_Submission.zip'
REQUIRED = [
    'DSS5202_Group29_TermPaper.docx', 'DSS5202_Group29_TermPaper.pdf',
    'DSS5202_Group29_Poster.pptx', 'DSS5202_Group29_Video_Slides.pptx',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-recording', action='store_true', help='fail unless an MP4 is in deliverables/')
    args = parser.parse_args()
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
    # Rerun the numerical validation now, then require fresh receipts.
    import subprocess, sys
    run = subprocess.run([sys.executable, str(ROOT/'src/validate_project.py')], cwd=ROOT, capture_output=True, text=True)
    if run.returncode != 0 or '"overall": "pass"' not in run.stdout:
        raise SystemExit('validate_project.py did not pass; see outputs/validation/checks.json')
    # Receipts must be newer than the files they vouch for.
    newest = max((ROOT/'deliverables'/n).stat().st_mtime for n in REQUIRED)
    for receipt in ('checks.json', 'deliverable_checks.json'):
        path = ROOT/'outputs/validation'/receipt
        if path.stat().st_mtime < newest - 5:
            raise SystemExit(f'{receipt} is older than the deliverables; rerun the validation scripts before packaging.')
    recordings = [p for p in (ROOT/'deliverables').glob('*.mp4')]
    if args.require_recording and not recordings:
        raise SystemExit('No MP4 recording in deliverables/. Record it, then package again.')
    files = []
    for folder in ['src', 'config', 'tests', 'data', 'assets', 'outputs', 'deliverables']:
        for path in (ROOT/folder).rglob('*'):
            relative = path.relative_to(ROOT)
            if (path.is_file() and not any(p.startswith(('.', '~$')) or p == '__pycache__' for p in relative.parts)
                    and path.suffix.lower() not in {'.pyc', '.zip'}):
                files.append(path)
    files += [ROOT/'README.md', ROOT/'PROJECT_PLAN.md', ROOT/'PROJECT_WALKTHROUGH.md', ROOT/'requirements.txt',
              ROOT/'report_final.md', ROOT/'references.md']
    not_distributed = {'data/manual/operator_digitalrealty_2024.pdf', 'data/manual/operator_equinix_2024.pdf', 'data/manual/operator_keppeldc_2024.pdf', 'data/manual/operator_sttgdc_2024.pdf', 'data/manual/kit_ar_2024.pdf', 'data/manual/lit_santos_2026.pdf', 'data/manual/pub_annual_report_2026.pdf'}
    stale = {'outputs/validation/visual_review.json', 'outputs/validation/writing_review.json',
             'outputs/validation/poster_package_validation.json', 'outputs/validation/video_package_validation.json',
             'outputs/validation/archive_checks.json'}
    files = [f for f in files if str(f.relative_to(ROOT)) not in stale | not_distributed]
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
              'TEAM ACTION REQUIRED: Record the ten-minute presentation in the team\'s own voices and add the MP4 to deliverables/ before packaging. The 20-slide deck is included; speaker notes give a suggested timing per slide.')
    extra['SUBMISSION_STATUS.txt'] = status+'\n\nThe ZIP contains the model, retained source data and generated deliverables. The original proposal, the DSA5208 style-reference PDF, the earlier hand-made draft and the study notes are omitted. The portable protected-source manifest covers included files; the complete workspace baseline is retained separately for the original audit.\n'
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
