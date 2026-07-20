from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.validation.evidence_authority_separation import (
    build_evidence_authority_cases,
    run_evidence_authority_separation,
    write_evidence_authority_outputs,
)


class EvidenceAuthoritySeparationTests(unittest.TestCase):
    def test_run_evidence_authority_separation(self) -> None:
        result = run_evidence_authority_separation()
        report = result["report"]
        summary = report["summary"]

        self.assertEqual(report["status"], "validated")
        self.assertEqual(summary["cases"], 4)
        self.assertAlmostEqual(summary["authority_drift_rate"], 0.0)
        self.assertAlmostEqual(summary["counterfactual_authority_drift_rate"], 0.25)
        self.assertEqual(summary["evidence_only_changes"], 4)
        self.assertEqual(summary["accepted_invalid_authority_changes"], 1)
        self.assertEqual(summary["srp_accepted_cases"], 2)
        self.assertEqual(summary["srp_rejected_cases"], 2)
        self.assertCountEqual(summary["authority_rules"], ["allow", "deny"])
        self.assertCountEqual(summary["evidence_levels"], ["high", "low"])

        cases = result["cases"]
        self.assertEqual(len(cases), 4)
        self.assertCountEqual(
            [case["proposal_id"] for case in cases],
            [
                "low_deny",
                "low_allow",
                "high_deny",
                "high_allow",
            ],
        )

    def test_build_evidence_authority_cases(self) -> None:
        cases = build_evidence_authority_cases()
        accepted = [case for case in cases if case.srp_admitted]
        self.assertEqual(len(cases), 4)
        self.assertEqual(len(accepted), 2)
        self.assertCountEqual([case.proposal_id for case in accepted], ["low_allow", "high_allow"])

    def test_write_evidence_authority_outputs(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_evidence_authority_outputs(Path(tmpdir))
            self.assertTrue(Path(outputs["cases_csv"]).exists())
            self.assertTrue(Path(outputs["cases_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["report_md"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())

            summary = outputs["summary"]
            self.assertEqual(summary["cases"], 4)
            self.assertAlmostEqual(json.loads(Path(outputs["summary_json"]).read_text(encoding="utf-8"))["authority_drift_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
