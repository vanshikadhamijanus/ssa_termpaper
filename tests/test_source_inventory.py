"""The manual-source registry must retain every matching local report."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SRC = Path(__file__).resolve().parents[1] / "src"
spec = importlib.util.spec_from_file_location("fetch_data", SRC / "01_fetch_data.py")
fetch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetch)
validation_spec = importlib.util.spec_from_file_location("validate_project", SRC / "validate_project.py")
validation = importlib.util.module_from_spec(validation_spec)
validation_spec.loader.exec_module(validation)


class ManualInventory(unittest.TestCase):
    def test_all_wildcard_matches_and_unmapped_sources_are_recorded(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manual = root / "data/manual"
            manual.mkdir(parents=True)
            for filename in ("operator_one.pdf", "operator_two.pdf", "unmapped.xlsx"):
                (manual / filename).write_bytes(b"source fixture")
            registry = [("Operators", "https://example.org/reports", "operator_*.pdf", "fixture")]
            rows = []
            with patch.object(fetch, "ROOT", root), patch.object(fetch, "MANUAL_DIR", manual), patch.object(fetch.S, "MANUAL", registry):
                fetch.check_manual(rows)
            self.assertEqual({r["file"] for r in rows},
                             {"data/manual/operator_one.pdf", "data/manual/operator_two.pdf", "data/manual/unmapped.xlsx"})
            unmapped = next(r for r in rows if r["file"].endswith("unmapped.xlsx"))
            self.assertEqual(unmapped["url"], "")
            self.assertIn("mapping needed", unmapped["status"])

    def test_authorized_external_edit_requires_exact_before_and_after_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "proposal.docx"
            path.write_bytes(b"original")
            before = validation.digest(path)
            path.write_bytes(b"user-corrected ID")
            after = validation.digest(path)
            approved = {"proposal.docx": {"baseline_sha256": before, "approved_sha256": after,
                                           "reason": "user-confirmed external correction"}}
            with patch.object(validation, "ROOT", root):
                inventory = validation.source_inventory({"proposal.docx": before}, approved)
                self.assertEqual(inventory.iloc[0].preservation_status, "acknowledged_external_change")
                self.assertEqual(inventory.iloc[0].unchanged, False)
                path.write_bytes(b"a later unapproved edit")
                changed = validation.source_inventory({"proposal.docx": before}, approved)
                self.assertEqual(changed.iloc[0].preservation_status, "unapproved_change_or_missing")


if __name__ == "__main__":
    unittest.main()
