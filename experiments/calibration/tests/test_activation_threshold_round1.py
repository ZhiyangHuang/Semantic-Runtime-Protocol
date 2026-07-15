from __future__ import annotations

import tempfile
import unittest

from experiments.calibration.activation_threshold_round1 import run_activation_threshold_round1
from experiments.calibration.index import CalibrationIndex
from experiments.calibration.storage import CalibrationResultStore


class ActivationThresholdRound1Tests(unittest.TestCase):
    def test_round1_returns_region_summary(self) -> None:
        result = run_activation_threshold_round1([0.3, 0.4, 0.5, 0.6, 0.7, 0.8])

        self.assertEqual(result["experiment"]["parameter"], "activation_threshold")
        self.assertEqual(result["experiment"]["round"], "1A")
        self.assertEqual(result["summary"]["tested_region"], [0.3, 0.8])
        self.assertEqual(result["summary"]["acceptable_region"], [0.3, 0.8])
        self.assertEqual(result["summary"]["rejected_region"], [])
        self.assertEqual(result["summary"]["result_count"], 6)
        self.assertEqual(len(result["results"]), 6)

    def test_round1_persists_results_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = CalibrationResultStore(tmpdir)
            index = CalibrationIndex(f"{tmpdir}/calibration_index.json")
            result = run_activation_threshold_round1([0.3, 0.5], store=store, index=index)

            self.assertEqual(len(result["stored_paths"]), 2)
            self.assertEqual(len(store.list_results("activation_threshold")), 2)
            self.assertEqual(index.list_parameters(status="accepted"), ["activation_threshold"])
            loaded = index.load("activation_threshold_0p5_round1")
            self.assertEqual(loaded.parameter, "activation_threshold")
            self.assertEqual(loaded.status, "accepted")
            self.assertTrue(loaded.accepted)


if __name__ == "__main__":
    unittest.main()

