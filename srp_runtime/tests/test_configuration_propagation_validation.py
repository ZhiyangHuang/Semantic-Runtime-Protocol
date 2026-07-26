from __future__ import annotations

import unittest

from srp_runtime.config import RuntimeConfig
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def build_state() -> SemanticState:
    state = SemanticState(state_id="state:propagation", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_id="u2",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept"},
        activation=0.8,
        confidence=0.7,
        version_id="v0",
        lifecycle_state="approximated",
    )
    state.units["u1"].relation_ids = ["rel:u1->u2"]
    state.graph.relation_index["u1"] = ["u2"]
    state.graph.relation_index["u2"] = ["u1"]
    return state


class ConfigurationPropagationValidationTests(unittest.TestCase):
    def test_default_equivalence(self) -> None:
        state_a = build_state()
        state_b = build_state()
        event = RuntimeEvent(
            event_id="event:default:1",
            event_type="ActivationUpdate",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={"activation_delta": 0.1},
            mutation_mode="update",
            operator_name="ActivationUpdate",
        )

        kernel_a = RuntimeKernel(state=state_a)
        kernel_b = RuntimeKernel(state=state_b, config=RuntimeKernelConfig(runtime_config=RuntimeConfig()))

        transition_a = kernel_a.apply_event(event)
        transition_b = kernel_b.apply_event(event)

        self.assertEqual(transition_a.operator_name, transition_b.operator_name)
        self.assertEqual(transition_a.changed_unit_ids, transition_b.changed_unit_ids)
        self.assertEqual(kernel_a.get_state(), kernel_b.get_state())

    def test_matrix_propagation_and_behavior(self) -> None:
        cases = [
            {
                "parameter": "activation_threshold",
                "config": RuntimeConfig(activation_threshold=0.75),
                "event": RuntimeEvent(
                    event_id="event:param:activation",
                    event_type="ActivationUpdate",
                    schema_version="1",
                    causal_parent=None,
                    actor="tester",
                    targets=["u1"],
                    payload={},
                    mutation_mode="update",
                    operator_name="ActivationUpdate",
                ),
                "operator_attr": ("_activation_operator", "runtime_config", "activation_threshold"),
                "expected_value": 0.75,
                "behavior_check": lambda transition, kernel: (
                    transition.mutation_summary["runtime_activation_threshold"] == 0.75
                    and kernel._state.units["u1"].activation == 0.75
                ),
            },
            {
                "parameter": "preserve_evidence",
                "config": RuntimeConfig(preserve_evidence=False),
                "event": RuntimeEvent(
                    event_id="event:param:forget",
                    event_type="Forgetting",
                    schema_version="1",
                    causal_parent=None,
                    actor="tester",
                    targets=["u1"],
                    payload={"evidence_refs": ["ev:1"], "preserve_evidence": True},
                    mutation_mode="update",
                    operator_name="Forgetting",
                ),
                "operator_attr": ("_forgetting_operator", "runtime_config", "preserve_evidence"),
                "expected_value": False,
                "behavior_check": lambda transition, kernel: transition.mutation_summary["runtime_preserve_evidence"] is False,
            },
            {
                "parameter": "archive_relations",
                "config": RuntimeConfig(archive_relations=False),
                "event": RuntimeEvent(
                    event_id="event:param:forget-archive",
                    event_type="Forgetting",
                    schema_version="1",
                    causal_parent=None,
                    actor="tester",
                    targets=["u1"],
                    payload={"evidence_refs": ["ev:1"], "preserve_evidence": True},
                    mutation_mode="update",
                    operator_name="Forgetting",
                ),
                "operator_attr": ("_forgetting_operator", "runtime_config", "archive_relations"),
                "expected_value": False,
                "behavior_check": lambda transition, kernel: transition.mutation_summary["runtime_archive_relations"] is False
                and all(not item.startswith("archive:u1:") for item in transition.changed_relation_ids),
            },
            {
                "parameter": "recovery_min_evidence",
                "config": RuntimeConfig(recovery_min_evidence=1),
                "event": RuntimeEvent(
                    event_id="event:param:recovery",
                    event_type="Recovery",
                    schema_version="1",
                    causal_parent=None,
                    actor="tester",
                    targets=["u2"],
                    payload={
                        "evidence_refs": ["ev:1"],
                        "recovery_source": "lineage",
                        "recovery_mode": "restore",
                        "restored_lifecycle_state": "active",
                        "restored_activation": 0.8,
                        "restored_confidence": 0.7,
                        "restored_provenance": ["ev:0"],
                    },
                    mutation_mode="update",
                    operator_name="Recovery",
                ),
                "operator_attr": ("_recovery_operator", "runtime_config", "recovery_min_evidence"),
                "expected_value": 1,
                "behavior_check": lambda transition, kernel: transition.success
                and transition.mutation_summary["runtime_minimum_evidence"] == 1,
            },
        ]

        for case in cases:
            with self.subTest(parameter=case["parameter"]):
                kernel = RuntimeKernel(state=build_state(), config=RuntimeKernelConfig(runtime_config=case["config"]))
                operator = getattr(kernel, case["operator_attr"][0])
                runtime_config = getattr(operator, case["operator_attr"][1])
                self.assertEqual(getattr(runtime_config, case["operator_attr"][2]), case["expected_value"])
                transition = kernel.apply_event(case["event"])
                self.assertTrue(case["behavior_check"](transition, kernel))

    def test_owner_isolation(self) -> None:
        activation_kernel = RuntimeKernel(
            state=build_state(),
            config=RuntimeKernelConfig(runtime_config=RuntimeConfig(activation_threshold=0.9)),
        )
        recovery_kernel = RuntimeKernel(
            state=build_state(),
            config=RuntimeKernelConfig(runtime_config=RuntimeConfig(recovery_min_evidence=1)),
        )

        self.assertEqual(activation_kernel._recovery_operator.runtime_config.recovery_min_evidence, 2)
        self.assertEqual(recovery_kernel._activation_operator.runtime_config.activation_threshold, 0.2)


if __name__ == "__main__":
    unittest.main()
