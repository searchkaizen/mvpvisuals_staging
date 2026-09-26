import os
import subprocess
import sys
import tempfile
import unittest
from datetime import date

HERE = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(HERE, ".."))

import extract  # noqa: E402

START, END = date(2025, 9, 1), date(2026, 8, 31)


def run(src, path):
    import json
    with open(os.path.join(HERE, path)) as f:
        raw = json.load(f)
    raw = raw.get("results", raw) if isinstance(raw, dict) else raw
    fn = extract.fda_records if src == "fda" else extract.fsis_records
    return {r["id"]: extract.classify(r) for r in fn(raw, START, END)}


class ExtractTests(unittest.TestCase):
    def test_fda_tiers(self):
        r = run("fda", "fixtures_fda.json")
        self.assertEqual(set(r), {"90001", "90002", "90003", "90004"})  # 90005 out of window
        self.assertEqual(r["90001"]["tier"], "maker_linked")
        self.assertEqual(r["90001"]["linked_retailers"], ["Kroger", "Walmart"])
        self.assertEqual(r["90002"]["tier"], "retailer_self")
        self.assertEqual(r["90003"]["tier"], "sold_at_only")
        self.assertEqual(r["90004"]["tier"], "none")  # ambiguous "Giant" w/o brand cue

    def test_fsis_est_and_language(self):
        r = run("fsis", "fixtures_fsis.json")
        self.assertEqual(len(r), 2)
        self.assertEqual(r["031-2025"]["tier"], "maker_linked")
        self.assertEqual(r["031-2025"]["est"], ["12345"])
        self.assertEqual(r["009-2026"]["est"], ["P-45678"])
        self.assertEqual(r["009-2026"]["linked_retailers"], ["Albertsons", "Amazon"])

    def test_cli_end_to_end(self):
        tmp = tempfile.mkdtemp()
        subprocess.run([sys.executable, os.path.join(HERE, "..", "extract.py"),
                        "--fda", os.path.join(HERE, "fixtures_fda.json"),
                        "--fsis", os.path.join(HERE, "fixtures_fsis.json"),
                        "--out", tmp], check=True, capture_output=True)
        with open(f"{tmp}/summary.md") as f:
            summary = f.read()
        self.assertIn("| ALL | 6 | 3 | 1 | 1 | 1 | 50.0% |", summary)


if __name__ == "__main__":
    unittest.main()
