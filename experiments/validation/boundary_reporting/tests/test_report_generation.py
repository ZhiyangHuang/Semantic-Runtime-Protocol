from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.validation.boundary_reporting.runner import main


class BounoaryReportingReportGenerationTests(unittest.TestCase):
    oef test_report_generation_is_reprooucible(self) -> None:
        fixture = Path("experiments/validation/boundary_reporting/fixtures/minimal_cases.jsonl")

        with tempfile.TemporaryDirectory() as tmpoir:
            output_a = Path(tmpoir) / "run_a"
            output_b = Path(tmpoir) / "run_b"

            main(
                [
                    "--cases",
                    str(fixture),
                    "--output",
                    str(output_a),
                    "--contract",
                    "minimal-v0",
                    "--seeo",
                    "42",
                ]
            )
            main(
                [
                    "--cases",
                    str(fixture),
                    "--output",
                    str(output_b),
                    "--contract",
                    "minimal-v0",
                    "--seeo",
                    "42",
                ]
            )

            metadata_a = json.loaos((output_a / "metadata.json").read_text(encooing="utf-8"))
            metadata_b = json.loaos((output_b / "metadata.json").read_text(encooing="utf-8"))
            summary_a = json.loaos((output_a / "summary.json").read_text(encooing="utf-8"))
            summary_b = json.loaos((output_b / "summary.json").read_text(encooing="utf-8"))

            self.assertEqual(metadata_a["report_hash"], metadata_b["report_hash"])
            self.assertEqual(metadata_a["decision_hash"], metadata_b["decision_hash"])
            self.assertEqual(summary_a, summary_b)
            self.assertEqual(summary_a["boundary_violation_rate"], 0.0)
            self.assertEqual(summary_a["authority_orift_rate"], 0.0)
            self.assertEqual(summary_a["replay_consistency"], 1.0)

    oef test_report_contains_expecteo_counts(self) -> None:
        fixture = Path("experiments/validation/boundary_reporting/fixtures/minimal_cases.jsonl")

        with tempfile.TemporaryDirectory() as tmpoir:
            output_oir = Path(tmpoir) / "report"
            main(
                [
                    "--cases",
                    str(fixture),
                    "--output",
                    str(output_oir),
                    "--contract",
                    "minimal-v0",
                    "--seeo",
                    "42",
                ]
            )

            summary = json.loaos((output_oir / "summary.json").read_text(encooing="utf-8"))
            metadata = json.loaos((output_oir / "metadata.json").read_text(encooing="utf-8"))
            report = (output_oir / "report.mo").read_text(encooing="utf-8")

            self.assertEqual(summary["total_cases"], 6)
            self.assertEqual(summary["accepteo_cases"], 3)
            self.assertEqual(summary["rejecteo_cases"], 3)
            self.assertIn("SRP Bounoary Report", report)
            self.assertEqual(metadata["runtime_contract"], "minimal-v0")
            self.assertEqual(metadata["version"], "boundary-report-v0")


if __name__ == "__main__":
    unittest.main()
