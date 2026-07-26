from __future__ import annotations

import tempfile
import unittest

from experiments.calibration.index import CalibrationIndex
from experiments.calibration.preserve_evidence_round1 import run_preserve_evidence_round1
from experiments.calibration.storage import CalibrationResultStore


class PreserveEvidenceRound1Tests(unittest.TestCase):
    def test_round1_returns_region_summary(self) -> None:
        result = run_preserve_evidence_round1([False, True])

        self.assertEqual(result["experiment"]["parameter"], "preserve_evidence")
        self.assertEqual(result["experiment"]["round"], "1C")
        self.assertEqual(result["summary"]["tested_region"], [False, True])
        self.assertEqual(result["summary"]["acceptable_region"], [False, True])
        self.assertEqual(result["summary"]["rejected_region"], [])
        self.assertEqual(result["summary"]["result_count"], 2)
        self.assertEqual(len(result["results"]), 2)

    def test_round1_persists_results_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = CalibrationResultStore(tmpdir)
            index = CalibrationIndex(f"{tmpdir}/calibration_index.json")
            result = run_preserve_evidence_round1([False, True], store=store, index=index)

            self.assertEqual(len(result["stored_paths"]), 2)
            self.assertEqual(len(store.list_results("preserve_evidence")), 2)
            self.assertEqual(index.list_parameters(status="accepted"), ["preserve_evidence"])
            accepted_false = index.load("preserve_evidence_false_round1")
            accepted_true = index.load("preserve_evidence_true_round1")
            self.assertTrue(accepted_false.accepted)
            self.assertTrue(accepted_true.accepted)
            self.assertEqual(accepted_false.status, "accepted")
            self.assertEqual(accepted_true.status, "accepted")

    def test_round1_observes_history_tradeoff(self) -> None:
        result = run_preserve_evidence_round1([False, True])
        false_case = next(item for item in result["results"] if item["candidate_value"] is False)
        true_case = next(item for item in result["results"] if item["candidate_value"] is True)

        self.assertEqual(false_case["metrics"]["evidence_record_count"], 0)
        self.assertGreater(true_case["metrics"]["evidence_record_count"], false_case["metrics"]["evidence_record_count"])
        self.assertGreater(true_case["metrics"]["history_preservation_delta"], false_case["metrics"]["history_preservation_delta"])
        self.assertTrue(false_case["metrics"]["state_reconstruction_independence"])
        self.assertTrue(true_case["metrics"]["state_reconstruction_independence"])


if __name__ == "__main__":
    unittest.main()

