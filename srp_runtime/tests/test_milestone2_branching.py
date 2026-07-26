from __future__ import annotations

import unittest

from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionResult
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.replay import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.trace.trace_builder import TraceRecord
from srp_runtime.version import SemanticVersionNode


def _make_decision(event_id: str, version_id: str, selected_operator: str) -> DecisionResult:
    return DecisionResult(
        decision_id=f"decision:{event_id}",
        event_id=event_id,
        selected_operator=selected_operator,
        candidate_operators=[selected_operator],
        accepted_candidates=[selected_operator],
        rejected_candidates=[],
        explanation=f"selected {selected_operator}",
        success=True,
        semantic_time=10,
        version_id=version_id,
    )


def _make_transition(
    event_id: str,
    transition_id: str,
    before_state_ref: str,
    after_state_ref: str,
    operator_name: str,
    timestamp_round: int = 10,
) -> TransitionResult:
    return TransitionResult(
        transition_id=transition_id,
        event_id=event_id,
        operator_name=operator_name,
        before_state_ref=before_state_ref,
        after_state_ref=after_state_ref,
        changed_unit_ids=["u1"],
        changed_relation_ids=[],
        mutation_summary={"operation": operator_name.lower()},
        invariant_checks=[],
        success=True,
        timestamp_round=timestamp_round,
    )


def _make_trace(
    event_id: str,
    transition_id: str,
    operator_name: str,
    before_version: str,
    after_version: str,
) -> TraceRecord:
    return TraceRecord(
        trace_id=f"trace:{transition_id}",
        event_id=event_id,
        transition_id=transition_id,
        causal_parent=None,
        rule_id=None,
        operator_name=operator_name,
        metric_evidence_ref=None,
        mutation_mode="update",
        before_version=before_version,
        after_version=after_version,
        changed_objects=["u1"],
        changed_relations=[],
        explanation=f"trace for {transition_id}",
    )


def _build_state(version_id: str = "v0", activation: float = 0.4) -> SemanticState:
    state = SemanticState(state_id="state:branch", version_id=version_id, timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=activation,
        confidence=0.5,
        version_id=version_id,
    )
    return state


class Milestone2BranchingValidationTests(unittest.TestCase):
    def test_version_branch_creation(self) -> None:
        manager = CommitManager()
        manager.version_graph.add_version(
            SemanticVersionNode(
                version_id="v1",
                parent_versions=["v0"],
                commit_id="commit:root",
                state_ref="state:v1",
                created_round=1,
            )
        )

        transition_x = _make_transition("event:x", "transition:x", "v1", "v2-x", "Merge")
        trace_x = _make_trace("event:x", "transition:x", "Merge", "v1", "v2-x")
        decision_x = _make_decision("event:x", "v1", "Merge")
        commit_x = manager.commit_transition(transition_x, trace_x, decision_x)

        transition_y = _make_transition("event:y", "transition:y", "v1", "v2-y", "Split")
        trace_y = _make_trace("event:y", "transition:y", "Split", "v1", "v2-y")
        decision_y = _make_decision("event:y", "v1", "Split")
        commit_y = manager.commit_transition(transition_y, trace_y, decision_y)

        self.assertEqual(commit_x.parent_version_id, "v1")
        self.assertEqual(commit_y.parent_version_id, "v1")
        self.assertEqual(sorted(node.version_id for node in manager.version_graph.get_children("v1")), ["v2-x", "v2-y"])
        self.assertEqual(len(manager.version_graph.nodes), 3)

    def test_branch_replay_isolation(self) -> None:
        checkpoint_manager = CheckpointManager()
        commit_manager = CommitManager()

        root_transition = _make_transition("event:root", "transition:root", "v0", "v1", "ActivationUpdate")
        root_trace = _make_trace("event:root", "transition:root", "ActivationUpdate", "v0", "v1")
        root_decision = _make_decision("event:root", "v0", "ActivationUpdate")
        root_commit = commit_manager.commit_transition(root_transition, root_trace, root_decision)
        checkpoint = checkpoint_manager.create_checkpoint(root_commit, state_ref="state:v1", event_position=1)

        parent_state = _build_state(version_id="v1", activation=0.4)
        branch_a_stream = [
            RuntimeEvent(
                event_id="event:a",
                event_type="ActivationUpdate",
                schema_version="1",
                causal_parent="event:root",
                actor="tester",
                targets=["u1"],
                payload={"activation_delta": 0.1},
                mutation_mode="update",
                operator_name="ActivationUpdate",
            )
        ]
        branch_b_stream = [
            RuntimeEvent(
                event_id="event:b",
                event_type="ActivationUpdate",
                schema_version="1",
                causal_parent="event:root",
                actor="tester",
                targets=["u1"],
                payload={"activation_delta": -0.1},
                mutation_mode="update",
                operator_name="ActivationUpdate",
            )
        ]

        replay_engine = ReplayEngine()
        branch_a = replay_engine.replay(parent_state.snapshot(), branch_a_stream)
        branch_b = replay_engine.replay(parent_state.snapshot(), branch_b_stream)

        self.assertEqual(checkpoint.version_id, "v1")
        self.assertNotEqual(branch_a.reconstructed_state.units["u1"].activation, branch_b.reconstructed_state.units["u1"].activation)
        self.assertEqual(checkpoint_manager.find_checkpoint("v1"), checkpoint)

    def test_commit_conflict_detection(self) -> None:
        manager = CommitManager()
        transition = _make_transition("event:dup", "transition:dup", "v0", "v1", "Merge")
        trace = _make_trace("event:dup", "transition:dup", "Merge", "v0", "v1")
        decision = _make_decision("event:dup", "v0", "Merge")

        manager.commit_transition(transition, trace, decision)
        with self.assertRaises(ValueError):
            manager.commit_transition(transition, trace, decision)

    def test_merge_split_version_flow(self) -> None:
        manager = CommitManager()
        manager.version_graph.add_version(
            SemanticVersionNode(
                version_id="v0",
                parent_versions=[],
                commit_id="commit:seed",
                state_ref="state:v0",
                created_round=1,
            )
        )

        merge_transition = _make_transition("event:merge", "transition:merge", "v0", "v1", "Merge")
        merge_trace = _make_trace("event:merge", "transition:merge", "Merge", "v0", "v1")
        merge_decision = _make_decision("event:merge", "v0", "Merge")
        manager.commit_transition(merge_transition, merge_trace, merge_decision)

        split_transition = _make_transition("event:split", "transition:split", "v1", "v2", "Split")
        split_trace = _make_trace("event:split", "transition:split", "Split", "v1", "v2")
        split_decision = _make_decision("event:split", "v1", "Split")
        manager.commit_transition(split_transition, split_trace, split_decision)

        self.assertEqual([node.version_id for node in manager.version_graph.get_parents("v2")], ["v1"])
        self.assertEqual([node.version_id for node in manager.version_graph.get_children("v0")], ["v1"])
        self.assertEqual([node.version_id for node in manager.version_graph.get_children("v1")], ["v2"])

    def test_checkpoint_branch_binding(self) -> None:
        checkpoint_manager = CheckpointManager()
        commit_manager = CommitManager()

        root_transition = _make_transition("event:root", "transition:root", "v0", "v1", "ActivationUpdate")
        root_trace = _make_trace("event:root", "transition:root", "ActivationUpdate", "v0", "v1")
        root_decision = _make_decision("event:root", "v0", "ActivationUpdate")
        root_commit = commit_manager.commit_transition(root_transition, root_trace, root_decision)

        branch_transition = _make_transition("event:branch", "transition:branch", "v1", "v2-branch", "ActivationUpdate")
        branch_trace = _make_trace("event:branch", "transition:branch", "ActivationUpdate", "v1", "v2-branch")
        branch_decision = _make_decision("event:branch", "v1", "ActivationUpdate")
        branch_commit = commit_manager.commit_transition(branch_transition, branch_trace, branch_decision)

        checkpoint = checkpoint_manager.create_checkpoint(root_commit, state_ref="state:v1", event_position=1)

        self.assertEqual(checkpoint.version_id, "v1")
        self.assertIsNone(checkpoint_manager.find_checkpoint(branch_commit.new_version_id))
        self.assertIs(checkpoint_manager.find_checkpoint("v1"), checkpoint)


if __name__ == "__main__":
    unittest.main()
