from __future__ import annotations

import unittest
from types import SimpleNamespace

from srp_runtime.version import ConflictQuery, ConflictQueryService, SemanticVersionGraph, SemanticVersionNode


class FakeArchiveQueryService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def lookup_evidence(self, target: str, operation: str = "conflict", constraints=None):
        self.calls.append((target, operation))
        return SimpleNamespace(
            matched_refs=[f"archive:{target}"],
            trace_refs=[f"trace:{target}"],
            verification_status="verified",
            completeness=1.0,
        )


class VersionConflictQueryTests(unittest.TestCase):
    def _divergent_graph(self) -> SemanticVersionGraph:
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
        return graph

    def test_query_duplicate_transition_conflict(self) -> None:
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

        service = ConflictQueryService()
        result = service.lookup_conflicts(graph, ConflictQuery(transition_id="t100"))

        self.assertEqual(result.conflict_refs, ["conflict:duplicate:t100"])
        self.assertIn("v1", result.version_refs)
        self.assertIn("v2", result.version_refs)
        self.assertEqual(result.verification_status, "partial")
        self.assertFalse(result.complete)

    def test_query_semantic_divergence(self) -> None:
        graph = self._divergent_graph()
        service = ConflictQueryService()

        result = service.lookup_conflicts(graph, ConflictQuery(version_id="v0"))

        self.assertEqual(result.conflict_refs, ["conflict:divergence:v0"])
        self.assertIn("v0", result.version_refs)
        self.assertIn("v1", result.version_refs)
        self.assertIn("trace:v1", result.evidence_refs)
        self.assertEqual(result.verification_status, "partial")
        self.assertFalse(result.complete)

    def test_query_does_not_resolve(self) -> None:
        graph = self._divergent_graph()
        version_count_before = len(graph.nodes)

        service = ConflictQueryService()
        result = service.lookup_conflicts(graph, ConflictQuery(conflict_type="semantic_divergence"))

        self.assertEqual(len(graph.nodes), version_count_before)
        self.assertEqual(result.conflict_refs, ["conflict:divergence:v0"])
        self.assertNotIn("v3", graph.nodes)

    def test_archive_boundary_uses_archive_query_service(self) -> None:
        graph = self._divergent_graph()
        archive_service = FakeArchiveQueryService()
        service = ConflictQueryService(archive_query_service=archive_service)

        result = service.lookup_conflicts(graph, ConflictQuery(evidence_ref="trace:v1"))

        self.assertTrue(archive_service.calls)
        self.assertEqual(archive_service.calls[0][1], "conflict")
        self.assertIn("archive:trace:v1", result.evidence_refs)
        self.assertIn("trace:trace:v1", result.trace_refs)
        self.assertEqual(result.verification_status, "verified")
        self.assertTrue(result.complete)

    def test_query_is_deterministic(self) -> None:
        graph = self._divergent_graph()
        service = ConflictQueryService()

        first = service.lookup_conflicts(graph, ConflictQuery(conflict_type="semantic_divergence"))
        second = service.lookup_conflicts(graph, ConflictQuery(conflict_type="semantic_divergence"))

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
