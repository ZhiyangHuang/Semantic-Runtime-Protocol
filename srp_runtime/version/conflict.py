from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class VersionConflict:
    conflict_id: str
    conflict_type: str
    source_version_a: str = ""
    source_version_b: str = ""
    version_refs: list[str] = field(default_factory=list)
    transition_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    severity: str = "warning"
    resolution_options: list[str] = field(default_factory=list)
