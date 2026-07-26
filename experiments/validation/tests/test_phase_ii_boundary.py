from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.validation.phase_ii_boundary import run_phase_ii_boundary_validation, write_phase_ii_boundary_outputs


class PhaseIIBoundaryValidationTests(unittest.TestCase):
    def test_boundary_validation_report_structure(self) -> None:
        result = run_phase_ii_boundary_validation()
        report = result["report"]

        self.assertEqual(report["status"], "validated")
        self.assertEqual(report["summary"]["observation_count"], 16)
        self.assertEqual(report["summary"]["closure_observation_count"], 32)
        self.assertEqual(report["summary"]["boundary_class_count"], 4)
        self.assertIn("boundary_stability", report["sections"])
        self.assertIn("closure_validation", report["sections"])

        boundary_classes = report["sections"]["boundary_stability"]["validated_boundary_classes"]
        self.assertEqual(len(boundary_classes), 4)
        self.assertCountEqual(
            boundary_classes,
            [
                "semantic mutation boundary",
                "evidence acceptance boundary",
                "history preservation boundary",
                "archive enrichment boundary",
            ],
        )

    def test_write_phase_ii_boundary_outputs(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_phase_ii_boundary_outputs(Path(tmpdir))
            self.assertTrue(Path(outputs["csv"]).exists())
            self.assertTrue(Path(outputs["jsonl"]).exists())
            self.assertTrue(Path(outputs["feasible_region"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())
            self.assertTrue(Path(outputs["figures"]["heatmap_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["heatmap_pdf"]).exists())
            self.assertTrue(Path(outputs["figures"]["coverage_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["coverage_pdf"]).exists())
            self.assertEqual(outputs["candidate_count"], 25)
            self.assertEqual(outputs["feasible_candidate_count"], 10)
            feasible_region = outputs["feasible_region_summary"]
            self.assertEqual(feasible_region["activation_threshold"]["min"], 0.1)
            self.assertEqual(feasible_region["activation_threshold"]["max"], 0.9)
            self.assertEqual(feasible_region["recovery_min_evidence"]["min"], 1)
            self.assertEqual(feasible_region["recovery_min_evidence"]["max"], 2)
            self.assertAlmostEqual(json.loads(Path(outputs["metadata"]).read_text(encoding="utf-8"))["coverage"], 0.4)


if __name__ == "__main__":
    unittest.main()
