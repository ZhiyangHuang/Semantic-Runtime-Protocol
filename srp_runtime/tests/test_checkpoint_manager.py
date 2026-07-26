from __future__ import annotations

import unittest

from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionResult
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.trace.trace_builder import TraceRecord


class CheckpointManagerTests(unittest.TestCase):
    def _build_commit(self):
        commit_manager = CommitManager()
        transition = TransitionResult(
            transition_id="transition:1",
            event_id="event:1",
            operator_name="Merge",
            before_state_ref="v0",
            after_state_ref="v1",
            success=True,
            timestamp_round=10,
            mutation_summary={"operation": "merge"},
        )
        trace = TraceRecord(
            trace_id="trace:1",
            event_id="event:1",
            transition_id="transition:1",
            causal_parent=None,
            rule_id=None,
            operator_name="Merge",
            metric_evidence_ref=None,
            mutation_mode="merge",
            before_version="v0",
            after_version="v1",
        )
        decision = DecisionResult(
            decision_id="decision:1",
            event_id="event:1",
            selected_operator="Merge",
            semantic_time=9,
            version_id="v0",
            explanation="merge selected",
        )
        commit = commit_manager.commit_transition(transition, trace, decision)
        return commit_manager, commit

    def test_checkpoint_binds_commit_and_version(self) -> None:
        _, commit = self._build_commit()
        checkpoint_manager = CheckpointManager()

        checkpoint = checkpoint_manager.create_checkpoint(
            semantic_commit=commit,
            state_ref="state:v1",
            event_position=2,
        )

        self.assertEqual(checkpoint.version_id, commit.new_version_id)
        self.assertEqual(checkpoint.commit_id, commit.commit_id)
        self.assertEqual(checkpoint.state_ref, "state:v1")
        self.assertEqual(checkpoint.event_offset, 2)
        self.assertIs(checkpoint_manager.find_checkpoint(commit.new_version_id), checkpoint)

    def test_checkpoint_does_not_change_version_history(self) -> None:
        commit_manager, commit = self._build_commit()
        before_versions = set(commit_manager.version_graph.nodes.keys())
        checkpoint_manager = CheckpointManager()

        checkpoint_manager.create_checkpoint(
            semantic_commit=commit,
            state_ref="state:v1",
            event_position=2,
        )

        after_versions = set(commit_manager.version_graph.nodes.keys())
        self.assertEqual(before_versions, after_versions)
        self.assertEqual(sorted(after_versions), ["v0", "v1"])

    def test_checkpoint_anchor_is_reference_only(self) -> None:
        _, commit = self._build_commit()
        checkpoint_manager = CheckpointManager()

        checkpoint = checkpoint_manager.create_checkpoint(
            semantic_commit=commit,
            state_ref="state:v1",
            event_position=2,
        )

        self.assertEqual(checkpoint.replay_boundary, "v1@2")
        self.assertIn("trace_id", checkpoint.metadata)
        self.assertEqual(checkpoint.metadata["commit_reason"], "merge")


if __name__ == "__main__":
    unittest.main()

