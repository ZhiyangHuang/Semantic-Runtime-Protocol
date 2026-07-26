from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .conflict import VersionConflict
from .conflict_detector import ConflictDetector
from .conflict_archive_adapter import ConflictArchiveEvidenceAdapter
from .version_graph import SemanticVersionGraph


@dataclass
class ConflictQuery:
    query_id: str = ""
    conflict_type: str | None = None
    version_id: str | None = None
    transition_id: str | None = None
    evidence_ref: str | None = None


@dataclass
class ConflictQueryResult:
    query_id: str
    conflict_refs: list[str] = field(default_factory=list)
    version_refs: list[str] = field(default_factory=list)
    transition_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    archive_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    verification_status: str = "unknown"
    complete: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class ConflictQueryService:
    conflict_detector: ConflictDetector = field(default_factory=ConflictDetector)
    archive_adapter: ConflictArchiveEvidenceAdapter | None = None
    archive_query_service: Any | None = None

    def lookup_conflicts(
        self,
        version_graph: SemanticVersionGraph,
        query: ConflictQuery,
    ) -> ConflictQueryResult:
        conflicts = self.conflict_detector.detect_all(version_graph)
        matched_conflicts = [conflict for conflict in conflicts if self._matches(query, conflict)]

        result = ConflictQueryResult(query_id=query.query_id or self._query_id(query))
        if not matched_conflicts:
            result.verification_status = "missing"
            return result

        archive_verifications: list[str] = []
        for conflict in matched_conflicts:
            self._append_unique(result.conflict_refs, conflict.conflict_id)
            for ref in conflict.version_refs:
                self._append_unique(result.version_refs, ref)
            for ref in conflict.transition_refs:
                self._append_unique(result.transition_refs, ref)
            for ref in conflict.trace_refs:
                self._append_unique(result.trace_refs, ref)
            for ref in conflict.evidence_refs:
                self._append_unique(result.evidence_refs, ref)

            bundle = self._lookup_conflict_evidence(conflict)
            archive_verifications.append(bundle.verification_status)
            for ref in bundle.archive_refs:
                self._append_unique(result.archive_refs, ref)
            for ref in bundle.evidence_refs:
                self._append_unique(result.evidence_refs, ref)
            for ref in bundle.trace_refs:
                self._append_unique(result.trace_refs, ref)
            for warning in bundle.warnings:
                self._append_unique(result.warnings, warning)

        result.verification_status = self._merge_verification_status(
            matched_conflicts=matched_conflicts,
            archive_verifications=archive_verifications,
            archive_enabled=self.archive_query_service is not None,
        )
        result.complete = result.verification_status == "verified"
        return result

    def query(
        self,
        version_graph: SemanticVersionGraph,
        query: ConflictQuery,
    ) -> ConflictQueryResult:
        return self.lookup_conflicts(version_graph, query)

    def _matches(self, query: ConflictQuery, conflict: VersionConflict) -> bool:
        if query.conflict_type and query.conflict_type != conflict.conflict_type:
            return False
        if query.version_id and query.version_id not in conflict.version_refs:
            return False
        if query.transition_id and query.transition_id not in conflict.transition_refs:
            return False
        if query.evidence_ref and query.evidence_ref not in conflict.evidence_refs:
            return False
        return True

    def _query_id(self, query: ConflictQuery) -> str:
        target = query.transition_id or query.version_id or query.evidence_ref or query.conflict_type or "all"
        return f"conflict-query:{target}"

    def _append_unique(self, items: list[str], value: str) -> None:
        if value and value not in items:
            items.append(value)

    def _lookup_conflict_evidence(self, conflict: VersionConflict):
        adapter = self.archive_adapter
        if adapter is None and self.archive_query_service is not None:
            adapter = ConflictArchiveEvidenceAdapter(self.archive_query_service)
        if adapter is None:
            adapter = ConflictArchiveEvidenceAdapter(None)
        return adapter.lookup_conflict_evidence(conflict)

    def _merge_verification_status(
        self,
        *,
        matched_conflicts: list[VersionConflict],
        archive_verifications: list[str],
        archive_enabled: bool,
    ) -> str:
        if not matched_conflicts:
            return "missing"
        if not archive_enabled:
            return "partial"
        if not archive_verifications:
            return "partial"
        if any(status not in {"verified", "partial"} for status in archive_verifications):
            return "partial"
        if any(status != "verified" for status in archive_verifications):
            return "partial"
        return "verified"
