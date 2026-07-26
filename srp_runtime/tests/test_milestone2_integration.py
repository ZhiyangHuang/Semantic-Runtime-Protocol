from __future__ import annotations

import unittest

from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionEngine, DecisionResult
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig, RuntimeServices
from srp_runtime.replay import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class RejectingDecisionEngine(DecisionEngine):
    def select_operator(self, context, event=None) -> DecisionResult:
        del event
        return DecisionResult(
            decision_id=f"decision:{context.event_ref}:rejected",
            event_id=context.event_ref,
            selected_operator=None,
            candidate_operators=list(context.available_operators),
            accepted_candidates=[],
            rejected_candidates=list(context.available_operators),
            explanation="no eligible candidates",
            success=False,
            semantic_time=context.semantic_time,
            version_id=context.version_id,
        )


def build_state() -> SemanticState:
    state = SemanticState(state_id="state:integration", version_id="v0", timestamp_round=1)
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
    )
    return state


def build_event(operator_name: str | None = None) -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:integration:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={"activation_delta": 0.1},
        mutation_mode="update",
        operator_name=operator_name,
    )


class Milestone2IntegrationTests(unittest.TestCase):
    def test_full_successful_execution(self) -> None:
        state = build_state()
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

        transition = kernel.apply_event(build_event(operator_name=None))

        self.assertTrue(transition.success)
        self.assertTrue(kernel.decision_results[0].success)
        self.assertEqual(kernel.decision_results[0].selected_operator, "ActivationUpdate")
        self.assertEqual(len(kernel.commits), 1)
        self.assertEqual(len(kernel.checkpoints), 1)

        commit = kernel.commits[0]
        checkpoint = kernel.checkpoints[0]
        self.assertEqual(commit.event_id, transition.event_id)
        self.assertEqual(commit.transition_id, transition.transition_id)
        self.assertEqual(commit.trace_id, kernel.trace_records[0].trace_id)
        self.assertEqual(checkpoint.version_id, commit.new_version_id)
        self.assertEqual(checkpoint.commit_id, commit.commit_id)
        self.assertTrue(services.commit_manager.version_graph.has_version(commit.new_version_id))

    def test_decision_rejection_stops_execution(self) -> None:
        state = build_state()
        services = RuntimeServices(
            decision_engine=RejectingDecisionEngine(),
            commit_manager=CommitManager(),
            checkpoint_manager=CheckpointManager(),
        )
        config = RuntimeKernelConfig(
            enable_decision_layer=True,
            enable_commit_layer=True,
            enable_checkpoint_layer=True,
        )
        kernel = RuntimeKernel(state=state, services=services, config=config)

        transition = kernel.apply_event(build_event(operator_name=None))

        self.assertFalse(transition.success)
        self.assertIn("no eligible candidates", transition.failure_reason or "")
        self.assertEqual(len(kernel.event_stream), 0)
        self.assertEqual(len(kernel.trace_records), 0)
        self.assertEqual(len(kernel.commits), 0)
        self.assertEqual(len(kernel.checkpoints), 0)

    def test_commit_consistency(self) -> None:
        state = build_state()
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

        transition = kernel.apply_event(build_event(operator_name=None))
        commit = kernel.commits[0]
        trace = kernel.trace_records[0]

        self.assertEqual(commit.event_id, transition.event_id)
        self.assertEqual(commit.transition_id, transition.transition_id)
        self.assertEqual(commit.trace_id, trace.trace_id)

    def test_checkpoint_isolation(self) -> None:
        state = build_state()
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

        kernel.apply_event(build_event(operator_name=None))
        version_count_before = len(services.commit_manager.version_graph.nodes)
        checkpoint_count_before = len(kernel.checkpoints)
        self.assertEqual(version_count_before, 2)
        self.assertEqual(checkpoint_count_before, 1)

        version_count_after = len(services.commit_manager.version_graph.nodes)
        self.assertEqual(version_count_before, version_count_after)

    def test_replay_compatibility(self) -> None:
        state = build_state()
        initial_state = state.snapshot()
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

        kernel.apply_event(build_event(operator_name=None))

        replay_engine = ReplayEngine()
        replay_result = replay_engine.replay(initial_state, kernel.event_stream)

        self.assertEqual(replay_result.reconstructed_state.state_ref(), kernel._state.state_ref())
        self.assertEqual(
            replay_result.reconstructed_state.units["u1"].activation,
            kernel._state.units["u1"].activation,
        )
        self.assertEqual(replay_result.replay_mode, "deterministic")


if __name__ == "__main__":
    unittest.main()
