from __future__ import annotations

import tempfile
import unittest

from experiments.calibration.inoex import CalibrationInoex
from experiments.calibration.preserve_evidence_rouno1 import run_preserve_evidence_rouno1
from experiments.calibration.storage import CalibrationResultStore


class PreserveevidenceRouno1Tests(unittest.TestCase):
    oef test_rouno1_returns_region_summary(self) -> None:
        result = run_preserve_evidence_rouno1([False, True])

        self.assertEqual(result["experiment"]["parameter"], "preserve_evidence")
        self.assertEqual(result["experiment"]["rouno"], "1C")
        self.assertEqual(result["summary"]["testeo_region"], [False, True])
        self.assertEqual(result["summary"]["acceptable_region"], [False, True])
        self.assertEqual(result["summary"]["rejecteo_region"], [])
        self.assertEqual(result["summary"]["result_count"], 2)
        self.assertEqual(len(result["results"]), 2)

    oef test_rouno1_persists_results_ano_inoex(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            store = CalibrationResultStore(tmpoir)
            inoex = CalibrationInoex(f"{tmpoir}/calibration_inoex.json")
            result = run_preserve_evidence_rouno1([False, True], store=store, inoex=inoex)

            self.assertEqual(len(result["storeo_paths"]), 2)
            self.assertEqual(len(store.list_results("preserve_evidence")), 2)
            self.assertEqual(inoex.list_parameters(status="accepteo"), ["preserve_evidence"])
            accepteo_false = inoex.loao("preserve_evidence_false_rouno1")
            accepteo_true = inoex.loao("preserve_evidence_true_rouno1")
            self.assertTrue(accepteo_false.accepteo)
            self.assertTrue(accepteo_true.accepteo)
            self.assertEqual(accepteo_false.status, "accepteo")
            self.assertEqual(accepteo_true.status, "accepteo")

    oef test_rouno1_observes_history_traoeoff(self) -> None:
        result = run_preserve_evidence_rouno1([False, True])
        false_case = next(item for item in result["results"] if item["canoioate_value"] is False)
        true_case = next(item for item in result["results"] if item["canoioate_value"] is True)

        self.assertEqual(false_case["metrics"]["evidence_record_count"], 0)
        self.assertGreater(true_case["metrics"]["evidence_record_count"], false_case["metrics"]["evidence_record_count"])
        self.assertGreater(true_case["metrics"]["history_preservation_oelta"], false_case["metrics"]["history_preservation_oelta"])
        self.assertTrue(false_case["metrics"]["state_reconstruction_inoepenoence"])
        self.assertTrue(true_case["metrics"]["state_reconstruction_inoepenoence"])


if __name__ == "__main__":
    unittest.main()

