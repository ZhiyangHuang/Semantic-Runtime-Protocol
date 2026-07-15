from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .conflict import VersionConflict


class ArchiveEvidenceLookup(Protocol):
    def lookup_evidence(
        self,
        target: str,
        operation: str = "conflict",
        constraints: dict[str, Any] | None = None,
    ) -> Any:
        ...


@dataclass
class ConflictEvidenceBundle:
    conflict_id: str
    version_refs: list[str] = field(default_factory=list)
    transition_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    archive_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    verification_status: str = "unknown"
    complete: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class ConflictArchiveEvidenceAdapter:
    archive_query_service: ArchiveEvidenceLookup | None = None

    def lookup_conflict_evidence(
        self,
        conflict: VersionConflict,
        constraints: dict[str, Any] | None = None,
    ) -> ConflictEvidenceBundle:
        bundle = ConflictEvidenceBundle(
            conflict_id=conflict.conflict_id,
            version_refs=list(conflict.version_refs),
            transition_refs=list(conflict.transition_refs),
            trace_refs=list(conflict.trace_refs),
            evidence_refs=list(conflict.evidence_refs),
            verification_status="partial" if self.archive_query_service is None else "unknown",
            complete=False,
        )

        if self.archive_query_service is None:
            bundle.warnings.append("missing archive query service")
            return bundle

        archive_verifications: list[str] = []
        for evidence_ref in conflict.evidence_refs or conflict.version_refs:
            archive_result = self.archive_query_service.lookup_evidence(
                target=evidence_ref,
                operation="conflict",
                constraints={
                    "conflict_id": conflict.conflict_id,
                    **(constraints or {}),
                },
            )
            archive_status = getattr(archive_result, "verification_status", "unknown")
            archive_verifications.append(archive_status)
            for ref in getattr(archive_result, "matched_refs", []) or []:
                self._append_unique(bundle.archive_refs, ref)
                self._append_unique(bundle.evidence_refs, ref)
            for ref in getattr(archive_result, "trace_refs", []) or []:
                self._append_unique(bundle.trace_refs, ref)

        bundle.verification_status = self._merge_verification_status(archive_verifications)
        bundle.complete = bundle.verification_status == "verified"
        if bundle.verification_status != "verified":
            bundle.warnings.append("missing archive evidence")
        return bundle

    def _append_unique(self, items: list[str], value: str) -> None:
        if value and value not in items:
            items.append(value)

    def _merge_verification_status(self, statuses: list[str]) -> str:
        if not statuses:
            return "partial"
        if any(status not in {"verified", "partial"} for status in statuses):
            return "partial"
        if any(status != "verified" for status in statuses):
            return "partial"
        return "verified"
