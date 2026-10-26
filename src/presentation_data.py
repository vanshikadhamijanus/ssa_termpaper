"""Pass the current model tables to the editable presentation builder."""

import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / ".build" / "presentations"


def run(kind):
    runtime = Path(os.environ.get(
        "DSS5202_PRESENTATION_RUNTIME",
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime",
    ))
    node = runtime / "dependencies/node/bin/node"
    modules = runtime / "dependencies/node/node_modules"
    if not node.exists() or not (modules / "@oai/artifact-tool").exists():
        raise SystemExit(
            "The presentation builder needs the Codex artifact-tool runtime. "
            "Set DSS5202_PRESENTATION_RUNTIME to its root directory. "
            "The existing PPTX files remain usable without this runtime."
        )
    BUILD.mkdir(parents=True, exist_ok=True)
    # Preserve the module logo embedded as an OLE preview in the source template.
    with ZipFile(ROOT / "paper/MyGroupNo-Poster-template.pptx") as archive:
        (BUILD / "template_nus_logo.png").write_bytes(archive.read("ppt/media/image1.png"))
    tables = {}
    for path in sorted((ROOT / "outputs/tables").glob("*.csv")):
        with path.open(newline="") as handle:
            tables[path.stem] = list(csv.DictReader(handle))
    with (ROOT / "config/assumptions.csv").open(newline="") as handle:
        assumptions = list(csv.DictReader(handle))
    snapshot = BUILD / f"{kind}_model_tables.json"
    snapshot.write_text(json.dumps({"tables": tables, "assumptions": assumptions}, indent=2))
    env = dict(os.environ)
    env["RUNTIME_NODE_MODULES"] = str(modules)
    env["RUNTIME_PYTHON"] = str(runtime / "dependencies/python/bin/python3.12")
    env["PATH"] = str(runtime / "dependencies/bin/override") + os.pathsep + env.get("PATH", "")
    subprocess.run(
        [str(node), str(ROOT / "src/build_presentations.mjs"), kind, str(snapshot)],
        check=True, cwd=ROOT, env=env,
    )
    latest = json.loads((BUILD / f"{kind}_latest.json").read_text())
    deck = Path(latest["finalPath"])
    pdf_dir = Path(latest["runDir"]) / "pdf"
    pdf_dir.mkdir()
    soffice = runtime / "dependencies/bin/override/soffice"
    env["XDG_CACHE_HOME"] = str(BUILD / "cache")
    with TemporaryDirectory(prefix="render-profile-", dir=BUILD) as profile:
        subprocess.run(
            [str(soffice), f"-env:UserInstallation={Path(profile).as_uri()}",
             "--headless", "--convert-to", "pdf", "--outdir", str(pdf_dir), str(deck)],
            check=True, cwd=ROOT, env=env,
        )
    rendered = pdf_dir / f"{deck.stem}.pdf"
    if not rendered.exists():
        raise RuntimeError(f"Presentation PDF export did not produce {rendered}")
    shutil.copy2(rendered, deck.with_name(f"{deck.stem}_preview.pdf"))
