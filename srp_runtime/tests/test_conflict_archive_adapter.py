from __future__ import annotations

import unittest
from types import SimpleNamespace

from srp_runtime.version import (
    ConflictArchiveEvidenceAdapter,
    VersionConflict,
)


class FakeArchiveQueryService:
    def __init__(self, verification_status: str = "verified", refs: list[str] | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self.verification_status = verification_status
        self.refs = refs or []

    def lookup_evidence(self, target: str, operation: str = "conflict", constraints=None):
        self.calls.append((target, operation))
        return SimpleNamespace(
            matched_refs=list(self.refs) or [f"archive:{target}"],
            trace_refs=[f"trace:{target}"],
            verification_status=self.verification_status,
            completeness=1.0 if self.verification_status == "verified" else 0.5,
        )


class ConflictArchiveEvidenceAdapterTests(unittest.TestCase):
    def test_evidence_enrichment(self) -> None:
        archive_service = FakeArchiveQueryService()
        adapter = ConflictArchiveEvidenceAdapter(archive_service)
        conflict = VersionConflict(
            conflict_id="conflict:duplicate:t1",
            conflict_type="duplicate_transition",
            version_refs=["v1", "v2"],
            transition_refs=["t1"],
            evidence_refs=["trace:t1"],
        )

        bundle = adapter.lookup_conflict_evidence(conflict)

        self.assertEqual(bundle.conflict_id, conflict.conflict_id)
        self.assertIn("archive:trace:t1", bundle.archive_refs)
        self.assertIn("trace:trace:t1", bundle.trace_refs)
        self.assertEqual(bundle.verification_status, "verified")
        self.assertTrue(bundle.complete)
        self.assertTrue(archive_service.calls)

    def test_missing_archive_evidence_reports_partial(self) -> None:
        adapter = ConflictArchiveEvidenceAdapter(None)
        conflict = VersionConflict(
            conflict_id="conflict:divergence:v0",
            conflict_type="semantic_divergence",
            version_refs=["v0", "v1"],
            evidence_refs=["trace:v1"],
        )

        bundle = adapter.lookup_conflict_evidence(conflict)

        self.assertEqual(bundle.verification_status, "partial")
        self.assertFalse(bundle.complete)
        self.assertIn("missing archive query service", bundle.warnings)

    def test_no_mutation_invariant(self) -> None:
        archive_service = FakeArchiveQueryService()
        adapter = ConflictArchiveEvidenceAdapter(archive_service)
        conflict = VersionConflict(
            conflict_id="conflict:divergence:v0",
            conflict_type="semantic_divergence",
            version_refs=["v0", "v1"],
            trace_refs=["trace:v1"],
            evidence_refs=["trace:v1"],
        )

        before_calls = len(archive_service.calls)
        bundle = adapter.lookup_conflict_evidence(conflict)
        after_calls = len(archive_service.calls)

        self.assertEqual(after_calls, before_calls + 1)
        self.assertEqual(bundle.verification_status, "verified")
        self.assertEqual(conflict.version_refs, ["v0", "v1"])


if __name__ == "__main__":
    unittest.main()
