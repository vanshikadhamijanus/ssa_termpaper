"""Build the report, presentation files and submission archive from saved results."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-presentations', action='store_true')
    parser.add_argument('--skip-package', action='store_true')
    args = parser.parse_args()
    runtime = Path(os.environ.get('DSS5202_PRESENTATION_RUNTIME', Path.home()/'.cache/codex-runtimes/codex-primary-runtime'))
    python = runtime/'dependencies/python/bin/python3.12'
    if not python.exists():
        raise SystemExit('Set DSS5202_PRESENTATION_RUNTIME to the bundled artifact runtime root. The numerical model and existing deliverables do not require it.')
    configured_renderer = os.environ.get('DSS5202_DOCX_RENDERER')
    candidates = sorted((Path.home()/'.codex/plugins/cache/openai-primary-runtime/documents').glob('*/skills/documents/render_docx.py'))
    renderer = Path(configured_renderer) if configured_renderer else (candidates[-1] if candidates else None)
    if renderer is None or not renderer.exists():
        raise SystemExit('Set DSS5202_DOCX_RENDERER to the documents skill render_docx.py script.')
    subprocess.run([str(python), '-B', str(ROOT/'src/09_build_paper.py')], cwd=ROOT, check=True)
    render_dir = ROOT/'.build/report'
    render_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(python), str(renderer), str(ROOT/'deliverables/DSS5202_Group29_TermPaper.docx'), '--output_dir', str(render_dir), '--emit_pdf'], cwd=ROOT, check=True)
    shutil.copy2(render_dir/'DSS5202_Group29_TermPaper.pdf', ROOT/'deliverables/DSS5202_Group29_TermPaper.pdf')
    if not args.skip_presentations:
        for builder in ['10_build_poster.py', '11_build_video_slides.py']:
            subprocess.run([sys.executable, '-B', str(ROOT/'src'/builder)], cwd=ROOT, check=True)
    subprocess.run([str(python), '-B', str(ROOT/'src/validate_deliverables.py')], cwd=ROOT, check=True)
    if not args.skip_package:
        subprocess.run([sys.executable, '-B', str(ROOT/'src/package_submission.py')], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
