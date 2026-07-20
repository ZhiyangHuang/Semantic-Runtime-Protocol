from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionPayload:
    context: str
    objects: List[Dict[str, Any]] = field(default_factory=list)
    object_count: int = 0
    source: str = "recovered"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "context": self.context,
            "objects": self.objects,
            "object_count": self.object_count,
            "source": self.source,
        }


def _memory_from_objects(objects: List[Dict[str, Any]], fallback: str) -> str:
    lines: List[str] = []
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        line = f"[{object_type}] {value}"
        evidence_pointer = str(item.get("evidence_pointer", "")).strip()
        if evidence_pointer:
            line += f" ({evidence_pointer})"
        lines.append(line)
    return "\n".join(lines) if lines else fallback


def _coerce_objects(payload: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    objects = payload.get("active_objects")
    if isinstance(objects, list):
        return [item for item in objects if isinstance(item, dict)]
    objects = payload.get("typed_representation", {}).get("objects")
    if isinstance(objects, list):
        return [item for item in objects if isinstance(item, dict)]
    return []


def build_execution_payload(selected_state: Optional[Dict[str, Any]], *, source: str) -> ExecutionPayload:
    if not isinstance(selected_state, dict):
        selected_state = {}
    objects = _coerce_objects(selected_state)
    fallback_context = str(selected_state.get("memory", ""))
    if source == "active" and objects:
        context = _memory_from_objects(objects, fallback_context)
    else:
        context = fallback_context
    return ExecutionPayload(
        context=context,
        objects=objects,
        object_count=len(objects),
        source=source,
    )
