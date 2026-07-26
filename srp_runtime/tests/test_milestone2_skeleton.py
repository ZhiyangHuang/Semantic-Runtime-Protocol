from __future__ import annotations

import unittest

from srp_runtime.checkpoint import RuntimeCheckpoint
from srp_runtime.commit import SemanticCommit
from srp_runtime.decision import DecisionContext, DecisionResult, OperatorCandidate
from srp_runtime.version import SemanticVersionGraph, SemanticVersionNode


class Milestone2SkeletonTests(unittest.TestCase):
    def test_decision_dataclasses(self) -> None:
        context = DecisionContext(event_ref="event:1", state_ref="state:1")
        candidate = OperatorCandidate(operator_name="Merge", applicability=True)
        result = DecisionResult(
            decision_id="decision:1",
            event_id="event:1",
            selected_operator="Merge",
        )

        self.assertEqual(context.event_ref, "event:1")
        self.assertEqual(candidate.operator_name, "Merge")
        self.assertEqual(result.selected_operator, "Merge")

    def test_commit_and_checkpoint_dataclasses(self) -> None:
        commit = SemanticCommit(
            commit_id="commit:1",
            parent_version_id="v0",
            new_version_id="v1",
            event_id="event:1",
            decision_id="decision:1",
            transition_id="transition:1",
        )
        checkpoint = RuntimeCheckpoint(
            checkpoint_id="checkpoint:1",
            version_id="v1",
            commit_id="commit:1",
            state_ref="state:1",
            event_offset=10,
        )

        self.assertEqual(commit.new_version_id, "v1")
        self.assertEqual(checkpoint.version_id, "v1")

    def test_version_graph_minimal_operations(self) -> None:
        graph = SemanticVersionGraph()
        parent = SemanticVersionNode(version_id="v0")
        child = SemanticVersionNode(version_id="v1", parent_versions=["v0"], commit_id="commit:1")

        graph.add_version(parent)
        graph.add_version(child)

        self.assertEqual(graph.get_version("v1").commit_id, "commit:1")
        self.assertEqual([node.version_id for node in graph.get_parents("v1")], ["v0"])
        self.assertEqual([node.version_id for node in graph.get_children("v0")], ["v1"])


if __name__ == "__main__":
    unittest.main()

