from __future__ import annotations

import unittest

from experiments.sensitivity.runner import run_single_activation_threshold_case
from srp_runtime.config import RuntimeConfig
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def build_state() -> SemanticState:
    state = SemanticState(state_id="sensitivity:test", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    return state


def build_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:sensitivity:test:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={},
        mutation_mode="update",
        operator_name="ActivationUpdate",
    )


class ActivationThresholdSensitivityValidationTests(unittest.TestCase):
    def test_default_equivalence(self) -> None:
        baseline = run_single_activation_threshold_case(0.2)
        default_override = run_single_activation_threshold_case(0.2)

        self.assertEqual(baseline.metrics, default_override.metrics)
        self.assertEqual(baseline.parameter, default_override.parameter)

    def test_parameter_effect_visibility(self) -> None:
        low = run_single_activation_threshold_case(0.1)
        high = run_single_activation_threshold_case(0.9)

        self.assertNotEqual(low.metrics["final_activation"], high.metrics["final_activation"])
        self.assertEqual(low.metrics["successful_transitions"], high.metrics["successful_transitions"])

    def test_ofat_isolation(self) -> None:
        config = RuntimeConfig(
            activation_threshold=0.8,
            preserve_evidence=True,
            archive_relations=True,
            recovery_min_evidence=2,
        )
        kernel = RuntimeKernel(state=build_state(), config=RuntimeKernelConfig(runtime_config=config))
        self.assertTrue(kernel._forgetting_operator.runtime_config.preserve_evidence)
        self.assertTrue(kernel._forgetting_operator.runtime_config.archive_relations)
        self.assertEqual(kernel._recovery_operator.runtime_config.recovery_min_evidence, 2)

        result = run_single_activation_threshold_case(0.8)
        self.assertEqual(result.parameter, "activation_threshold")
        self.assertIn("activation_threshold=0.8", result.observations)
        self.assertNotIn("preserve_evidence", " ".join(result.observations))
        self.assertNotIn("recovery_min_evidence", " ".join(result.observations))


if __name__ == "__main__":
    unittest.main()
