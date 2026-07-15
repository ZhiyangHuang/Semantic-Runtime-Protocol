from __future__ import annotations

import tempfile
import unittest

from experiments.calibration.archive_relations_round1 import run_archive_relations_round1
from experiments.calibration.index import CalibrationIndex
from experiments.calibration.storage import CalibrationResultStore


class ArchiveRelationsRound1Tests(unittest.TestCase):
    def test_round1_returns_region_summary(self) -> None:
        result = run_archive_relations_round1([False, True])

        self.assertEqual(result["experiment"]["parameter"], "archive_relations")
        self.assertEqual(result["experiment"]["round"], "1D")
        self.assertEqual(result["summary"]["tested_region"], [False, True])
        self.assertEqual(result["summary"]["acceptable_region"], [False, True])
        self.assertEqual(result["summary"]["rejected_region"], [])
        self.assertEqual(result["summary"]["result_count"], 2)
        self.assertEqual(len(result["results"]), 2)

    def test_round1_persists_results_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = CalibrationResultStore(tmpdir)
            index = CalibrationIndex(f"{tmpdir}/calibration_index.json")
            result = run_archive_relations_round1([False, True], store=store, index=index)

            self.assertEqual(len(result["stored_paths"]), 2)
            self.assertEqual(len(store.list_results("archive_relations")), 2)
            self.assertEqual(index.list_parameters(status="accepted"), ["archive_relations"])
            false_case = index.load("archive_relations_false_round1")
            true_case = index.load("archive_relations_true_round1")
            self.assertTrue(false_case.accepted)
            self.assertTrue(true_case.accepted)
            self.assertEqual(false_case.status, "accepted")
            self.assertEqual(true_case.status, "accepted")

    def test_round1_observes_archive_enrichment_boundary(self) -> None:
        result = run_archive_relations_round1([False, True])
        false_case = next(item for item in result["results"] if item["candidate_value"] is False)
        true_case = next(item for item in result["results"] if item["candidate_value"] is True)

        self.assertEqual(false_case["metrics"]["evidence_enrichment_count"], 0)
        self.assertGreater(true_case["metrics"]["evidence_enrichment_count"], false_case["metrics"]["evidence_enrichment_count"])
        self.assertTrue(false_case["metrics"]["replay_equivalent"])
        self.assertTrue(true_case["metrics"]["replay_equivalent"])
        self.assertTrue(false_case["metrics"]["archive_not_state_authority"])
        self.assertTrue(true_case["metrics"]["archive_not_state_authority"])


if __name__ == "__main__":
    unittest.main()

