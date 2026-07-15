from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.sensitivity.experiment_index import SensitivityExperimentIndex, register_validated_sensitivity_experiments
from experiments.sensitivity.preserve_evidence_experiment import (
    run_preserve_evidence_sensitivity,
    run_single_preserve_evidence_case,
)
from experiments.sensitivity.storage import SensitivityResultStore


class PreserveEvidenceSensitivityValidationTests(unittest.TestCase):
    def test_default_equivalence(self) -> None:
        baseline = run_single_preserve_evidence_case(True)
        default_override = run_single_preserve_evidence_case(True)

        self.assertEqual(baseline.metrics, default_override.metrics)
        self.assertEqual(baseline.parameter, default_override.parameter)

    def test_parameter_effect_visibility(self) -> None:
        preserved = run_single_preserve_evidence_case(True)
        not_preserved = run_single_preserve_evidence_case(False)

        self.assertNotEqual(preserved.metrics["evidence_record_count"], not_preserved.metrics["evidence_record_count"])
        self.assertNotEqual(preserved.metrics["audit_completeness_score"], not_preserved.metrics["audit_completeness_score"])
        self.assertTrue(preserved.metrics["replay_equivalent"])
        self.assertTrue(not_preserved.metrics["replay_equivalent"])

    def test_ofat_isolation(self) -> None:
        result = run_single_preserve_evidence_case(True)
        self.assertEqual(result.parameter, "preserve_evidence")
        self.assertIn("preserve_evidence=True", result.observations)
        self.assertNotIn("recovery_min_evidence", " ".join(result.observations))

    def test_run_experiment_and_register(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            store = SensitivityResultStore(root / "results")
            index = SensitivityExperimentIndex(root / "index.json")

            output = run_preserve_evidence_sensitivity([True, False], store=store)
            self.assertEqual(output["experiment"]["parameter"], "preserve_evidence")
            self.assertEqual(len(output["results"]), 2)
            self.assertEqual(len(output["stored_paths"]), 2)

            register_validated_sensitivity_experiments(index, root / "results")
            index.register_from_result(
                experiment_id="preserve_evidence_ofat_v1",
                parameter="preserve_evidence",
                experiment_type="OFAT",
                result_location=str(root / "results" / "preserve_evidence_ofat_v1.json"),
                status="validated",
                result_count=2,
            )
            self.assertIn("preserve_evidence", index.list_parameters(status="validated"))


if __name__ == "__main__":
    unittest.main()
