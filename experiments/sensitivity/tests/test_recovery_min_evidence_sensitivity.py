from __future__ import annotations

import unittest

from experiments.sensitivity.recovery_min_evidence_experiment import (
    run_recovery_min_evidence_sensitivity,
    run_single_recovery_min_evidence_case,
)
from srp_runtime.config import RuntimeConfig
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def build_state() -> SemanticState:
    state = SemanticState(state_id="sensitivity:recovery:test", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.2,
        confidence=0.5,
        lifecycle_state="approximated",
        version_id="v0",
    )
    return state


class RecoveryMinEvidenceSensitivityValidationTests(unittest.TestCase):
    def test_default_equivalence(self) -> None:
        baseline = run_single_recovery_min_evidence_case(2)
        default_override = run_single_recovery_min_evidence_case(2)

        self.assertEqual(baseline.metrics, default_override.metrics)
        self.assertEqual(baseline.parameter, default_override.parameter)

    def test_parameter_effect_visibility(self) -> None:
        low = run_single_recovery_min_evidence_case(1)
        high = run_single_recovery_min_evidence_case(3)

        self.assertEqual(low.metrics["successful_transitions"], 1)
        self.assertEqual(high.metrics["successful_transitions"], 1)
        self.assertNotEqual(low.metrics["evidence_usage_count"], high.metrics["evidence_usage_count"])
        self.assertNotEqual(low.value, high.value)

    def test_ofat_isolation(self) -> None:
        config = RuntimeConfig(
            activation_threshold=0.2,
            preserve_evidence=True,
            archive_relations=True,
            recovery_min_evidence=3,
        )
        kernel = RuntimeKernel(state=build_state(), config=RuntimeKernelConfig(runtime_config=config))
        self.assertEqual(kernel._activation_operator.runtime_config.activation_threshold, 0.2)
        self.assertTrue(kernel._forgetting_operator.runtime_config.preserve_evidence)
        self.assertTrue(kernel._forgetting_operator.runtime_config.archive_relations)

        result = run_single_recovery_min_evidence_case(3)
        self.assertEqual(result.parameter, "recovery_min_evidence")
        self.assertIn("recovery_min_evidence=3", result.observations)
        self.assertNotIn("activation_threshold", " ".join(result.observations))

    def test_run_experiment(self) -> None:
        output = run_recovery_min_evidence_sensitivity([1, 2, 3])
        self.assertEqual(output["experiment"]["parameter"], "recovery_min_evidence")
        self.assertEqual(len(output["results"]), 3)


if __name__ == "__main__":
    unittest.main()
