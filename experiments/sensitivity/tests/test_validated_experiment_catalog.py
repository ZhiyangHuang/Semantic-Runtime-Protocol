from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.sensitivity.experiment_index import SensitivityExperimentIndex, register_validated_sensitivity_experiments
from experiments.sensitivity.recovery_min_evidence_experiment import run_single_recovery_min_evidence_case
from experiments.sensitivity.runner import run_single_activation_threshold_case
from experiments.sensitivity.storage import SensitivityResultStore


class ValidatedExperimentCatalogTests(unittest.TestCase):
    def test_current_validated_experiments_are_discoverable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            store = SensitivityResultStore(root / "results")
            index = SensitivityExperimentIndex(root / "index.json")

            activation_result = run_single_activation_threshold_case(0.3)
            recovery_result = run_single_recovery_min_evidence_case(2)
            store.save(activation_result)
            store.save(recovery_result)

            register_validated_sensitivity_experiments(index, root / "results")

            validated_records = index.list_experiments(status="validated")
            self.assertEqual(
                [record.experiment_id for record in validated_records],
                [
                    "activation_threshold_ofat_v1",
                    "archive_relations_ofat_v1",
                    "preserve_evidence_ofat_v1",
                    "recovery_min_evidence_ofat_v1",
                ],
            )
            self.assertEqual(
                index.list_parameters(status="validated"),
                ["activation_threshold", "archive_relations", "preserve_evidence", "recovery_min_evidence"],
            )

    def test_parameter_query_is_isolated(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            index = SensitivityExperimentIndex(Path(tmpdir) / "index.json")
            register_validated_sensitivity_experiments(index, Path(tmpdir) / "results")

            activation_records = index.list_experiments(parameter="activation_threshold", status="validated")
            recovery_records = index.list_experiments(parameter="recovery_min_evidence", status="validated")

            self.assertEqual([record.experiment_id for record in activation_records], ["activation_threshold_ofat_v1"])
            self.assertEqual([record.experiment_id for record in recovery_records], ["recovery_min_evidence_ofat_v1"])


if __name__ == "__main__":
    unittest.main()
