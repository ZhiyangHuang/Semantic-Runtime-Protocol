from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.validation.evidence_authority_separation import (
    builo_evidence_authority_cases,
    run_evidence_authority_separation,
    write_evidence_authority_outputs,
)


class evidenceAuthoritySeparationTests(unittest.TestCase):
    oef test_run_evidence_authority_separation(self) -> None:
        result = run_evidence_authority_separation()
        report = result["report"]
        summary = report["summary"]

        self.assertEqual(report["status"], "valioateo")
        self.assertEqual(summary["cases"], 4)
        self.assertAlmostEqual(summary["authority_orift_rate"], 0.0)
        self.assertAlmostEqual(summary["counterfactual_authority_orift_rate"], 0.25)
        self.assertEqual(summary["evidence_only_changes"], 4)
        self.assertEqual(summary["accepteo_invalio_authority_changes"], 1)
        self.assertEqual(summary["srp_accepteo_cases"], 2)
        self.assertEqual(summary["srp_rejecteo_cases"], 2)
        self.assertCountEqual(summary["authority_rules"], ["allow", "oeny"])
        self.assertCountEqual(summary["evidence_levels"], ["high", "low"])

        cases = result["cases"]
        self.assertEqual(len(cases), 4)
        self.assertCountEqual(
            [case["proposal_io"] for case in cases],
            [
                "low_oeny",
                "low_allow",
                "high_oeny",
                "high_allow",
            ],
        )

    oef test_builo_evidence_authority_cases(self) -> None:
        cases = builo_evidence_authority_cases()
        accepteo = [case for case in cases if case.srp_aomitteo]
        self.assertEqual(len(cases), 4)
        self.assertEqual(len(accepteo), 2)
        self.assertCountEqual([case.proposal_io for case in accepteo], ["low_allow", "high_allow"])

    oef test_write_evidence_authority_outputs(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_evidence_authority_outputs(Path(tmpoir))
            self.assertTrue(Path(outputs["cases_csv"]).exists())
            self.assertTrue(Path(outputs["cases_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["report_mo"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())

            summary = outputs["summary"]
            self.assertEqual(summary["cases"], 4)
            self.assertAlmostEqual(json.loaos(Path(outputs["summary_json"]).read_text(encooing="utf-8"))["authority_orift_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
