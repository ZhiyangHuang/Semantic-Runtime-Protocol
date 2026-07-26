from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .conflict import VersionConflict
from .version_graph import SemanticVersionGraph

if TYPE_CHECKING:
    from srp_runtime.commit import CommitManager


@dataclass
class ConflictDetector:
    """Reference conflict detector for semantic version history.

    The first pass only detects evidence; it does not resolve conflicts.
    """

    commit_manager: CommitManager | None = None
    conflict_log: list[VersionConflict] = field(default_factory=list)

    def detect_duplicate_transition(self, version_graph: SemanticVersionGraph) -> list[VersionConflict]:
        conflicts: list[VersionConflict] = []
        seen: dict[str, str] = {}
        for version in version_graph.nodes.values():
            commit_id = version.commit_id
            if not commit_id:
                continue
            transition_id = self._transition_id_from_commit(commit_id)
            existing_version_id = seen.get(transition_id)
            if existing_version_id is None:
                seen[transition_id] = version.version_id
                continue
            if existing_version_id == version.version_id:
                continue
            conflict = VersionConflict(
                conflict_id=f"conflict:duplicate:{transition_id}",
                conflict_type="duplicate_transition",
                source_version_a=existing_version_id,
                source_version_b=version.version_id,
                version_refs=[existing_version_id, version.version_id],
                transition_refs=[transition_id],
                evidence_refs=[existing_version_id, version.version_id],
                severity="error",
                resolution_options=["reject_branch", "accept_branch", "merge_branch"],
            )
            conflicts.append(conflict)
            self.conflict_log.append(conflict)
        return conflicts

    def detect_divergence(self, version_graph: SemanticVersionGraph) -> list[VersionConflict]:
        conflicts: list[VersionConflict] = []
        for parent_id, child_ids in self._branch_children(version_graph).items():
            if len(child_ids) < 2:
                continue
            child_nodes = [version_graph.get_version(child_id) for child_id in child_ids if version_graph.has_version(child_id)]
            conflict_evidence = [
                node
                for node in child_nodes
                if node.metadata.get("conflict_type") == "semantic_divergence"
                or node.metadata.get("conflict_evidence_refs")
            ]
            if not conflict_evidence:
                continue
            conflict = VersionConflict(
                conflict_id=f"conflict:divergence:{parent_id}",
                conflict_type="semantic_divergence",
                source_version_a=parent_id,
                source_version_b=child_ids[0],
                version_refs=[parent_id, *child_ids],
                transition_refs=[node.commit_id for node in child_nodes if node.commit_id],
                trace_refs=[],
                evidence_refs=[
                    *[
                        ref
                        for node in conflict_evidence
                        for ref in node.metadata.get("conflict_evidence_refs", [])
                    ],
                    *[node.commit_id for node in conflict_evidence if node.commit_id],
                ],
                severity="warning",
                resolution_options=["accept_branch", "merge_branch", "reject_branch"],
            )
            conflicts.append(conflict)
            self.conflict_log.append(conflict)
        return conflicts

    def detect_all(self, version_graph: SemanticVersionGraph) -> list[VersionConflict]:
        conflicts = []
        conflicts.extend(self.detect_duplicate_transition(version_graph))
        conflicts.extend(self.detect_divergence(version_graph))
        return conflicts

    def _branch_children(self, version_graph: SemanticVersionGraph) -> dict[str, list[str]]:
        parents_to_children: dict[str, list[str]] = {}
        for version in version_graph.nodes.values():
            for parent_id in version.parent_versions:
                parents_to_children.setdefault(parent_id, []).append(version.version_id)
        return parents_to_children

    def _transition_id_from_commit(self, commit_id: str) -> str:
        if commit_id.startswith("commit:"):
            return commit_id.removeprefix("commit:")
        return commit_id
