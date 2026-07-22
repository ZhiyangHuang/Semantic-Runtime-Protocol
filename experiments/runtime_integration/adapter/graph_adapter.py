from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Mapping

from .candidate import SemanticTransitionCandidate


def _coerce_mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    return {"value": value}


def _merge_patch(state: Any, patch: Any) -> Any:
    if not isinstance(patch, Mapping):
        return deepcopy(patch)
    if not isinstance(state, Mapping):
        state = {}
    merged = deepcopy(dict(state))
    for key, value in patch.items():
        current = merged.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            merged[key] = _merge_patch(current, value)
        else:
            merged[key] = deepcopy(value)
    return merged


@dataclass
class InMemoryGraphStore:
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[dict[str, Any]] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    def read_state(self, entity: str | None = None) -> dict[str, Any]:
        if entity is None:
            return self.export_state()
        return deepcopy(self.nodes.get(entity, {}))

    def snapshot(self) -> dict[str, Any]:
        return self.export_state()

    def propose_transition(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]:
        return {
            "transition_id": candidate.transition_id,
            "entity": candidate.subject,
            "operation": candidate.operation,
            "state_before": self.read_state(candidate.subject),
            "candidate": candidate.as_dict(),
        }

    def commit_transition(self, candidate: SemanticTransitionCandidate) -> dict[str, Any]:
        subject = candidate.subject
        before = deepcopy(self.nodes.get(subject, {}))
        proposed = deepcopy(candidate.proposed_value)
        if candidate.operation.upper() == "DELETE":
            self.nodes.pop(subject, None)
            after = {}
        else:
            current = self.nodes.get(subject)
            if isinstance(current, Mapping) and isinstance(proposed, Mapping):
                after = _merge_patch(current, proposed)
            else:
                after = deepcopy(proposed)
            self.nodes[subject] = after
        edge = {
            "transition_id": candidate.transition_id,
            "subject": subject,
            "operation": candidate.operation,
            "from": before,
            "to": deepcopy(after),
            "provenance": dict(candidate.provenance),
            "authority": _coerce_mapping(candidate.metadata.get("authority")) or {},
            "timestamp": candidate.timestamp,
        }
        self.edges.append(edge)
        record = {
            "transition_id": candidate.transition_id,
            "candidate": candidate.as_dict(),
            "state": self.snapshot(),
        }
        self.history.append(record)
        return self.snapshot()

    def rollback_transition(self, transition_id: str) -> dict[str, Any]:
        retained: list[dict[str, Any]] = []
        rebuilt_nodes: dict[str, dict[str, Any]] = {}
        rebuilt_edges: list[dict[str, Any]] = []
        for record in self.history:
            candidate = record.get("candidate") or {}
            if str(candidate.get("transition_id") or record.get("transition_id")) == transition_id:
                continue
            retained.append(record)
            subject = str(candidate.get("subject") or "")
            if not subject:
                continue
            operation = str(candidate.get("operation") or "UPDATE").upper()
            proposed_value = deepcopy(candidate.get("proposed_value") or {})
            if operation == "DELETE":
                rebuilt_nodes.pop(subject, None)
            else:
                current = rebuilt_nodes.get(subject)
                if isinstance(current, Mapping) and isinstance(proposed_value, Mapping):
                    rebuilt_nodes[subject] = _merge_patch(current, proposed_value)
                else:
                    rebuilt_nodes[subject] = deepcopy(proposed_value)
            rebuilt_edges.append(
                {
                    "transition_id": candidate.get("transition_id"),
                    "subject": subject,
                    "operation": operation,
                    "from": {},
                    "to": deepcopy(rebuilt_nodes.get(subject, {})),
                    "provenance": dict(candidate.get("provenance") or {}),
                    "authority": _coerce_mapping(candidate.get("metadata", {}).get("authority")) or {},
                    "timestamp": candidate.get("timestamp"),
                }
            )
        self.history = retained
        self.nodes = rebuilt_nodes
        self.edges = rebuilt_edges
        return self.snapshot()

    def export_state(self) -> dict[str, Any]:
        return {
            "nodes": deepcopy(self.nodes),
            "edges": deepcopy(self.edges),
            "history_length": len(self.history),
        }
