from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.validation.admissibility_boundary_validation import (
    build_admissibility_cases,
    run_admissibility_boundary_validation,
    write_admissibility_boundary_outputs,
)


class AdmissibilityBoundaryValidationTests(unittest.TestCase):
    def test_run_admissibility_boundary_validation(self) -> None:
        result = run_admissibility_boundary_validation()
        report = result["report"]
        summary = report["summary"]

        self.assertEqual(report["status"], "validated")
        self.assertEqual(summary["total_cases"], 5)
        self.assertEqual(summary["admissible_cases"], 1)
        self.assertEqual(summary["inadmissible_cases"], 4)
        self.assertAlmostEqual(summary["admissibility_precision"], 1.0)
        self.assertAlmostEqual(summary["boundary_violation_rate"], 0.0)
        self.assertAlmostEqual(summary["rejection_accuracy"], 1.0)
        self.assertAlmostEqual(summary["policy_invalid_acceptance_rates"]["direct_update"], 1.0)
        self.assertAlmostEqual(summary["policy_invalid_acceptance_rates"]["evidence_as_authority"], 0.5)
        self.assertAlmostEqual(summary["policy_invalid_acceptance_rates"]["authority_only"], 0.5)

        cases = result["cases"]
        self.assertEqual(len(cases), 5)
        self.assertCountEqual(
            [case["case_id"] for case in cases],
            [
                "low_evidence_low_authority",
                "high_evidence_low_authority",
                "low_evidence_high_authority",
                "high_evidence_high_authority",
                "optimization_override",
            ],
        )

    def test_build_admissibility_cases(self) -> None:
        cases = build_admissibility_cases()
        admissible = [case for case in cases if case.srp_admitted]
        self.assertEqual(len(cases), 5)
        self.assertEqual(len(admissible), 1)
        self.assertEqual(admissible[0].case_id, "high_evidence_high_authority")

    def test_write_admissibility_boundary_outputs(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_admissibility_boundary_outputs(Path(tmpdir))
            self.assertTrue(Path(outputs["cases_csv"]).exists())
            self.assertTrue(Path(outputs["cases_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["report_md"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())

            summary = outputs["summary"]
            self.assertEqual(summary["total_cases"], 5)
            self.assertAlmostEqual(json.loads(Path(outputs["summary_json"]).read_text(encoding="utf-8"))["boundary_violation_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
