from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.sensitivity.experiment_index import SensitivityExperimentIndex
from experiments.sensitivity.recovery_min_evidence_experiment import run_single_recovery_min_evidence_case
from experiments.sensitivity.runner import run_single_activation_threshold_case
from experiments.sensitivity.storage import SensitivityResultStore


class SensitivityExperimentIndexTests(unittest.TestCase):
    def test_register_and_load_experiments(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "index.json"
            index = SensitivityExperimentIndex(index_path)

            index.register_from_result(
                experiment_id="activation_threshold_ofat_v1",
                parameter="activation_threshold",
                experiment_type="OFAT",
                result_location="results/activation_threshold_ofat_v1.json",
                status="validated",
                result_count=5,
            )
            record = index.load("activation_threshold_ofat_v1")

            self.assertEqual(record.parameter, "activation_threshold")
            self.assertEqual(record.experiment_type, "OFAT")
            self.assertEqual(record.status, "validated")
            self.assertEqual(record.result_count, 5)

    def test_parameter_and_status_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            index = SensitivityExperimentIndex(Path(tmpdir) / "index.json")
            index.register_from_result(
                experiment_id="activation_threshold_ofat_v1",
                parameter="activation_threshold",
                experiment_type="OFAT",
                result_location="results/activation_threshold_ofat_v1.json",
                status="validated",
                result_count=5,
            )
            index.register_from_result(
                experiment_id="recovery_min_evidence_ofat_v1",
                parameter="recovery_min_evidence",
                experiment_type="OFAT",
                result_location="results/recovery_min_evidence_ofat_v1.json",
                status="draft",
                result_count=3,
            )

            activation_records = index.list_experiments(parameter="activation_threshold")
            validated_records = index.list_experiments(status="validated")
            self.assertEqual([record.experiment_id for record in activation_records], ["activation_threshold_ofat_v1"])
            self.assertEqual([record.experiment_id for record in validated_records], ["activation_threshold_ofat_v1"])

    def test_index_and_result_store_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            store = SensitivityResultStore(root / "results")
            index = SensitivityExperimentIndex(root / "index.json")

            activation_result = run_single_activation_threshold_case(0.3)
            recovery_result = run_single_recovery_min_evidence_case(2)
            activation_path = store.save(activation_result)
            recovery_path = store.save(recovery_result)

            index.register_from_result(
                experiment_id=activation_result.experiment_id,
                parameter=activation_result.parameter,
                experiment_type="OFAT",
                result_location=str(activation_path),
                status="validated",
                result_count=1,
            )
            index.register_from_result(
                experiment_id=recovery_result.experiment_id,
                parameter=recovery_result.parameter,
                experiment_type="OFAT",
                result_location=str(recovery_path),
                status="validated",
                result_count=1,
            )

            loaded_activation = index.load(activation_result.experiment_id)
            loaded_recovery = index.load(recovery_result.experiment_id)

            self.assertIn("activation_threshold", loaded_activation.result_location)
            self.assertIn("recovery_min_evidence", loaded_recovery.result_location)
            self.assertEqual(len(index.list_experiments(status="validated")), 2)


if __name__ == "__main__":
    unittest.main()
