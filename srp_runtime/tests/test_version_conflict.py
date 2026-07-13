from __future__ import annotations

import unittest

from srp_runtime.checkpoint import CheckpointManager
from srp_runtime.commit import SemanticCommit
from srp_runtime.version import ConflictDetector, SemanticVersionGraph, SemanticVersionNode


class VersionConflictValidationTests(unittest.TestCase):
    def test_branch_is_not_conflict(self) -> None:
        graph = SemanticVersionGraph()
        graph.add_version(
            SemanticVersionNode(
                version_id="v0",
                parent_versions=[],
                commit_id="commit:seed",
                state_ref="state:v0",
                created_round=1,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v1",
                parent_versions=["v0"],
                commit_id="commit:1",
                state_ref="state:v1",
                created_round=2,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v2",
                parent_versions=["v0"],
                commit_id="commit:2",
                state_ref="state:v2",
                created_round=2,
            )
        )

        detector = ConflictDetector()
        conflicts = detector.detect_all(graph)

        self.assertEqual(conflicts, [])

    def test_duplicate_transition_produces_conflict(self) -> None:
        graph = SemanticVersionGraph()
        graph.add_version(
            SemanticVersionNode(
                version_id="v0",
                parent_versions=[],
                commit_id="commit:seed",
                state_ref="state:v0",
                created_round=1,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v1",
                parent_versions=["v0"],
                commit_id="commit:t100",
                state_ref="state:v1",
                created_round=2,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v2",
                parent_versions=["v0"],
                commit_id="commit:t100",
                state_ref="state:v2",
                created_round=2,
            )
        )

        detector = ConflictDetector()
        conflicts = detector.detect_duplicate_transition(graph)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, "duplicate_transition")
        self.assertEqual(conflicts[0].source_version_a, "v1")
        self.assertEqual(conflicts[0].source_version_b, "v2")

    def test_divergent_semantic_update_produces_conflict(self) -> None:
        graph = SemanticVersionGraph()
        graph.add_version(
            SemanticVersionNode(
                version_id="v0",
                parent_versions=[],
                commit_id="commit:seed",
                state_ref="state:v0",
                created_round=1,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v1",
                parent_versions=["v0"],
                commit_id="commit:1",
                state_ref="state:v1",
                created_round=2,
                metadata={
                    "conflict_type": "semantic_divergence",
                    "conflict_evidence_refs": ["trace:v1"],
                },
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v2",
                parent_versions=["v0"],
                commit_id="commit:2",
                state_ref="state:v2",
                created_round=2,
            )
        )

        detector = ConflictDetector()
        conflicts = detector.detect_divergence(graph)

        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].conflict_type, "semantic_divergence")
        self.assertEqual(conflicts[0].source_version_a, "v0")
        self.assertEqual(conflicts[0].source_version_b, "v1")
        self.assertIn("trace:v1", conflicts[0].evidence_refs)

    def test_checkpoint_does_not_resolve_conflict(self) -> None:
        graph = SemanticVersionGraph()
        graph.add_version(
            SemanticVersionNode(
                version_id="v0",
                parent_versions=[],
                commit_id="commit:seed",
                state_ref="state:v0",
                created_round=1,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v1",
                parent_versions=["v0"],
                commit_id="commit:1",
                state_ref="state:v1",
                created_round=2,
                metadata={
                    "conflict_type": "semantic_divergence",
                    "conflict_evidence_refs": ["trace:v1"],
                },
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v2",
                parent_versions=["v0"],
                commit_id="commit:2",
                state_ref="state:v2",
                created_round=2,
            )
        )

        detector = ConflictDetector()
        conflicts_before = detector.detect_divergence(graph)
        self.assertEqual(len(conflicts_before), 1)

        checkpoint_manager = CheckpointManager()
        semantic_commit = SemanticCommit(
            commit_id="commit:checkpoint",
            parent_version_id="v1",
            new_version_id="v3",
            event_id="event:checkpoint",
            decision_id="decision:checkpoint",
            transition_id="transition:checkpoint",
            trace_id="trace:checkpoint",
            state_ref="state:v3",
            version_ref="v3",
            semantic_time=11,
            commit_reason="checkpoint"
        )
        checkpoint_manager.create_checkpoint(
            semantic_commit=semantic_commit,
            state_ref="state:v3",
            event_position=1,
        )

        conflicts_after = detector.detect_divergence(graph)
        self.assertEqual(conflicts_before, conflicts_after)

    def test_conflict_detection_deterministic(self) -> None:
        graph = SemanticVersionGraph()
        graph.add_version(
            SemanticVersionNode(
                version_id="v0",
                parent_versions=[],
                commit_id="commit:seed",
                state_ref="state:v0",
                created_round=1,
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v1",
                parent_versions=["v0"],
                commit_id="commit:1",
                state_ref="state:v1",
                created_round=2,
                metadata={
                    "conflict_type": "semantic_divergence",
                    "conflict_evidence_refs": ["trace:v1"],
                },
            )
        )
        graph.add_version(
            SemanticVersionNode(
                version_id="v2",
                parent_versions=["v0"],
                commit_id="commit:2",
                state_ref="state:v2",
                created_round=2,
            )
        )

        detector = ConflictDetector()
        first = detector.detect_all(graph)
        second = detector.detect_all(graph)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
