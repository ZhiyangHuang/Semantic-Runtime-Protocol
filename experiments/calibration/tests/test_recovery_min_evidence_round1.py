from __future__ import annotations

import tempfile
import unittest

from experiments.calibration.index import CalibrationIndex
from experiments.calibration.recovery_min_evidence_round1 import run_recovery_min_evidence_round1
from experiments.calibration.storage import CalibrationResultStore


class RecoveryMinEvidenceRound1Tests(unittest.TestCase):
    def test_round1_returns_region_summary(self) -> None:
        result = run_recovery_min_evidence_round1([1, 2, 3, 4, 5])

        self.assertEqual(result["experiment"]["parameter"], "recovery_min_evidence")
        self.assertEqual(result["experiment"]["round"], "1B")
        self.assertEqual(result["summary"]["tested_region"], [1, 5])
        self.assertEqual(result["summary"]["acceptable_region"], [1, 3])
        self.assertEqual(result["summary"]["rejected_region"], [4, 5])
        self.assertEqual(result["summary"]["result_count"], 5)
        self.assertEqual(len(result["results"]), 5)

    def test_round1_persists_results_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = CalibrationResultStore(tmpdir)
            index = CalibrationIndex(f"{tmpdir}/calibration_index.json")
            result = run_recovery_min_evidence_round1([1, 4], store=store, index=index)

            self.assertEqual(len(result["stored_paths"]), 2)
            self.assertEqual(len(store.list_results("recovery_min_evidence")), 2)
            self.assertEqual(index.list_parameters(status="accepted"), ["recovery_min_evidence"])
            accepted = index.load("recovery_min_evidence_1_round1")
            rejected = index.load("recovery_min_evidence_4_round1")
            self.assertTrue(accepted.accepted)
            self.assertEqual(accepted.status, "accepted")
            self.assertFalse(rejected.accepted)
            self.assertEqual(rejected.status, "rejected")


if __name__ == "__main__":
    unittest.main()

