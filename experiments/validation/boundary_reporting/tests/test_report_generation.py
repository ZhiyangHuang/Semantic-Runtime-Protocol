from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.validation.boundary_reporting.runner import main


class BoundaryReportingReportGenerationTests(unittest.TestCase):
    def test_report_generation_is_reproducible(self) -> None:
        fixture = Path("experiments/validation/boundary_reporting/fixtures/minimal_cases.jsonl")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_a = Path(tmpdir) / "run_a"
            output_b = Path(tmpdir) / "run_b"

            main(
                [
                    "--cases",
                    str(fixture),
                    "--output",
                    str(output_a),
                    "--contract",
                    "minimal-v0",
                    "--seed",
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
                    "--seed",
                    "42",
                ]
            )

            metadata_a = json.loads((output_a / "metadata.json").read_text(encoding="utf-8"))
            metadata_b = json.loads((output_b / "metadata.json").read_text(encoding="utf-8"))
            summary_a = json.loads((output_a / "summary.json").read_text(encoding="utf-8"))
            summary_b = json.loads((output_b / "summary.json").read_text(encoding="utf-8"))

            self.assertEqual(metadata_a["report_hash"], metadata_b["report_hash"])
            self.assertEqual(metadata_a["decision_hash"], metadata_b["decision_hash"])
            self.assertEqual(summary_a, summary_b)
            self.assertEqual(summary_a["boundary_violation_rate"], 0.0)
            self.assertEqual(summary_a["authority_drift_rate"], 0.0)
            self.assertEqual(summary_a["replay_consistency"], 1.0)

    def test_report_contains_expected_counts(self) -> None:
        fixture = Path("experiments/validation/boundary_reporting/fixtures/minimal_cases.jsonl")

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "report"
            main(
                [
                    "--cases",
                    str(fixture),
                    "--output",
                    str(output_dir),
                    "--contract",
                    "minimal-v0",
                    "--seed",
                    "42",
                ]
            )

            summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
            metadata = json.loads((output_dir / "metadata.json").read_text(encoding="utf-8"))
            report = (output_dir / "report.md").read_text(encoding="utf-8")

            self.assertEqual(summary["total_cases"], 6)
            self.assertEqual(summary["accepted_cases"], 3)
            self.assertEqual(summary["rejected_cases"], 3)
            self.assertIn("SRP Boundary Report", report)
            self.assertEqual(metadata["runtime_contract"], "minimal-v0")
            self.assertEqual(metadata["version"], "boundary-report-v0")


if __name__ == "__main__":
    unittest.main()
