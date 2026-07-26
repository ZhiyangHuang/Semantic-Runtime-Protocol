from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.sensitivity.runner import run_single_activation_threshold_case, run_activation_threshold_sensitivity
from experiments.sensitivity.storage import SensitivityResultStore


class SensitivityResultStorageTests(unittest.TestCase):
    def test_save_and_load_roundtrip(self) -> None:
        result = run_single_activation_threshold_case(0.3)
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SensitivityResultStore(tmpdir)
            path = store.save(result)

            self.assertTrue(path.exists())

            loaded = store.load(result.experiment_id)
            self.assertEqual(loaded.experiment_id, result.experiment_id)
            self.assertEqual(loaded.parameter, result.parameter)
            self.assertEqual(loaded.value, result.value)
            self.assertEqual(loaded.metrics, result.metrics)
            self.assertEqual(loaded.observations, result.observations)

    def test_list_results_keeps_parameter_isolation(self) -> None:
        low = run_single_activation_threshold_case(0.5)
        high = run_single_activation_threshold_case(0.8)
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SensitivityResultStore(tmpdir)
            store.save(low)
            store.save(high)

            listed = store.list_results("activation_threshold")
            self.assertEqual(len(listed), 2)
            self.assertEqual({item.value for item in listed}, {0.5, 0.8})

    def test_runner_can_write_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SensitivityResultStore(tmpdir)
            output = run_activation_threshold_sensitivity([0.2, 0.4], store=store)

            self.assertEqual(len(output["results"]), 2)
            self.assertEqual(len(output["stored_paths"]), 2)
            for stored_path in output["stored_paths"]:
                self.assertTrue(Path(stored_path).exists())


if __name__ == "__main__":
    unittest.main()
