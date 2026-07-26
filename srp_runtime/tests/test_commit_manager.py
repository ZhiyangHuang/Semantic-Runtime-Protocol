from __future__ import annotations

import unittest

from srp_runtime.commit import CommitManager
from srp_runtime.decision import DecisionResult
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.trace.trace_builder import TraceRecord


class CommitManagerTests(unittest.TestCase):
    def test_commit_transition_updates_version_graph(self) -> None:
        manager = CommitManager()
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

        commit = manager.commit_transition(transition, trace, decision)

        self.assertEqual(commit.transition_id, "transition:1")
        self.assertEqual(commit.trace_id, "trace:1")
        self.assertEqual(commit.parent_version_id, "v0")
        self.assertEqual(commit.new_version_id, "v1")
        self.assertEqual(commit.version_ref, "v1")
        self.assertEqual(commit.commit_reason, "merge")
        self.assertTrue(manager.version_graph.has_version("v0"))
        self.assertTrue(manager.version_graph.has_version("v1"))
        self.assertEqual(manager.version_graph.get_version("v1").commit_id, commit.commit_id)

    def test_commit_transition_rejects_mismatched_event_ids(self) -> None:
        manager = CommitManager()
        transition = TransitionResult(
            transition_id="transition:1",
            event_id="event:1",
            operator_name="Merge",
            before_state_ref="v0",
            after_state_ref="v1",
            success=True,
        )
        trace = TraceRecord(
            trace_id="trace:1",
            event_id="event:2",
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
        )

        with self.assertRaises(ValueError):
            manager.commit_transition(transition, trace, decision)

    def test_commit_transition_rejects_duplicate_transition(self) -> None:
        manager = CommitManager()
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

        manager.commit_transition(transition, trace, decision)
        with self.assertRaises(ValueError):
            manager.commit_transition(transition, trace, decision)


if __name__ == "__main__":
    unittest.main()
