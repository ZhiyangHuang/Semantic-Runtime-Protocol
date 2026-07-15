from __future__ import annotations

import unittest
import tempfile
from pathlib import Path

from experiments.sensitivity.archive_relations_experiment import (
    run_archive_relations_sensitivity,
    run_single_archive_relations_case,
    write_archive_relations_outputs,
)
from experiments.sensitivity.experiment_index import SensitivityExperimentIndex, register_validated_sensitivity_experiments
from experiments.sensitivity.storage import SensitivityResultStore


class ArchiveRelationsSensitivityValidationTests(unittest.TestCase):
    def test_default_equivalence(self) -> None:
        baseline = run_single_archive_relations_case(False)
        default_override = run_single_archive_relations_case(False)

        self.assertEqual(baseline.metrics, default_override.metrics)
        self.assertEqual(baseline.parameter, default_override.parameter)

    def test_parameter_effect_visibility(self) -> None:
        off = run_single_archive_relations_case(False)
        on = run_single_archive_relations_case(True)

        self.assertEqual(off.metrics["state_transition_equivalence"], True)
        self.assertEqual(on.metrics["state_transition_equivalence"], True)
        self.assertLess(off.metrics["evidence_enrichment_count"], on.metrics["evidence_enrichment_count"])
        self.assertLess(off.metrics["conflict_evidence_coverage"], on.metrics["conflict_evidence_coverage"])

    def test_authority_isolation(self) -> None:
        off = run_single_archive_relations_case(False)
        on = run_single_archive_relations_case(True)

        self.assertEqual(off.metrics["replay_equivalent"], True)
        self.assertEqual(on.metrics["replay_equivalent"], True)
        self.assertEqual(off.metrics["successful_transitions"], on.metrics["successful_transitions"])

    def test_run_experiment(self) -> None:
        output = run_archive_relations_sensitivity([False, True])
        self.assertEqual(output["experiment"]["parameter"], "archive_relations")
        self.assertEqual(len(output["results"]), 2)
        self.assertEqual({item["value"] for item in output["results"]}, {False, True})

    def test_run_experiment_and_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = write_archive_relations_outputs([False, True], output_dir=tmpdir)
            self.assertEqual(len(output["stored_paths"]), 2)
            for stored_path in output["stored_paths"]:
                self.assertTrue(Path(stored_path).exists())

    def test_register_archive_relations_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            store = SensitivityResultStore(root / "results")
            index = SensitivityExperimentIndex(root / "index.json")
            results = run_archive_relations_sensitivity([False, True])
            for record in results["results"]:
                result_path = store.save(run_single_archive_relations_case(record["value"]))
                index.register_from_result(
                    experiment_id=record["experiment_id"],
                    parameter=record["parameter"],
                    experiment_type="OFAT",
                    result_location=str(result_path),
                    status="validated",
                    result_count=2,
                )
            register_validated_sensitivity_experiments(index, root / "results")
            self.assertIn("archive_relations", index.list_parameters(status="validated"))


if __name__ == "__main__":
    unittest.main()
