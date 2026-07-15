from __future__ import annotations

import unittest

from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionEngine
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig, RuntimeServices
from srp_runtime.config import RuntimeConfig
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


def _build_state() -> SemanticState:
    state = SemanticState(state_id="state:1", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    return state


def _build_event(operator_name: str | None = None) -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={"activation_delta": 0.1},
        mutation_mode="update",
        operator_name=operator_name,
    )


class KernelMilestone2OverlayTests(unittest.TestCase):
    def test_default_behavior_remains_unchanged(self) -> None:
        state_a = _build_state()
        state_b = _build_state()
        event = _build_event(operator_name="ActivationUpdate")

        kernel_a = RuntimeKernel(state=state_a)
        kernel_b = RuntimeKernel(
            state=state_b,
            services=RuntimeServices(
                decision_engine=DecisionEngine(),
                commit_manager=CommitManager(),
                checkpoint_manager=CheckpointManager(),
            ),
            config=RuntimeKernelConfig(),
        )

        transition_a = kernel_a.apply_event(event)
        transition_b = kernel_b.apply_event(event)

        self.assertEqual(transition_a.operator_name, transition_b.operator_name)
        self.assertEqual(transition_a.changed_unit_ids, transition_b.changed_unit_ids)
        self.assertEqual(kernel_a.get_state(), kernel_b.get_state())
        self.assertEqual(len(kernel_a.event_stream), len(kernel_b.event_stream))
        self.assertEqual(len(kernel_b.decision_results), 0)
        self.assertEqual(len(kernel_b.commits), 0)
        self.assertEqual(len(kernel_b.checkpoints), 0)

    def test_decision_commit_and_checkpoint_overlay(self) -> None:
        state = _build_state()
        services = RuntimeServices(
            decision_engine=DecisionEngine(),
            commit_manager=CommitManager(),
            checkpoint_manager=CheckpointManager(),
        )
        config = RuntimeKernelConfig(
            enable_decision_layer=True,
            enable_commit_layer=True,
            enable_checkpoint_layer=True,
        )
        kernel = RuntimeKernel(state=state, services=services, config=config)
        event = _build_event(operator_name=None)

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(kernel.decision_results[0].selected_operator, "ActivationUpdate")
        self.assertEqual(len(kernel.commits), 1)
        self.assertEqual(len(kernel.checkpoints), 1)

        commit = kernel.commits[0]
        checkpoint = kernel.checkpoints[0]
        self.assertEqual(commit.transition_id, transition.transition_id)
        self.assertEqual(commit.new_version_id, transition.after_state_ref)
        self.assertEqual(checkpoint.version_id, commit.new_version_id)
        self.assertEqual(checkpoint.commit_id, commit.commit_id)

        version_graph = services.commit_manager.version_graph
        self.assertTrue(version_graph.has_version("v0"))
        self.assertTrue(version_graph.has_version(transition.after_state_ref))
        self.assertEqual(len(version_graph.nodes), 2)

    def test_checkpoint_does_not_pollute_version_history(self) -> None:
        state = _build_state()
        services = RuntimeServices(
            decision_engine=DecisionEngine(),
            commit_manager=CommitManager(),
            checkpoint_manager=CheckpointManager(),
        )
        config = RuntimeKernelConfig(
            enable_decision_layer=True,
            enable_commit_layer=True,
            enable_checkpoint_layer=True,
        )
        kernel = RuntimeKernel(state=state, services=services, config=config)

        kernel.apply_event(_build_event(operator_name=None))
        version_count_before = len(services.commit_manager.version_graph.nodes)
        checkpoint_count_before = len(kernel.checkpoints)

        self.assertEqual(version_count_before, 2)
        self.assertEqual(checkpoint_count_before, 1)

    def test_runtime_config_propagates_to_operators(self) -> None:
        state = _build_state()
        config = RuntimeKernelConfig(
            runtime_config=RuntimeConfig(
                activation_threshold=0.75,
                preserve_evidence=False,
                archive_relations=False,
                recovery_min_evidence=1,
            )
        )
        kernel = RuntimeKernel(state=state, config=config)

        self.assertEqual(kernel._activation_operator.runtime_config.activation_threshold, 0.75)
        self.assertFalse(kernel._forgetting_operator.runtime_config.preserve_evidence)
        self.assertFalse(kernel._forgetting_operator.runtime_config.archive_relations)
        self.assertEqual(kernel._recovery_operator.runtime_config.recovery_min_evidence, 1)

        activation_event = RuntimeEvent(
            event_id="event:config:1",
            event_type="ActivationUpdate",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={},
            mutation_mode="update",
            operator_name="ActivationUpdate",
        )
        transition = kernel.apply_event(activation_event)

        self.assertTrue(transition.success)
        self.assertEqual(transition.mutation_summary["runtime_activation_threshold"], 0.75)
        self.assertEqual(kernel._state.units["u1"].activation, 0.75)


if __name__ == "__main__":
    unittest.main()
