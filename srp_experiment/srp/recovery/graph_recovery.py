from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Set

from ..semantic_graph import build_semantic_runtime_graph_by_version
from ..semantic_parser import stable_semantic_object_id
from ..recover_runtime import build_recovered_state, build_structured_state_package, attach_recovery_diagnostics
from ..reconstruction.policy import ReconstructionMetrics, ReconstructionResult
from .policy import RecoveryPolicy


def _extract_objects(package: Dict) -> List[Dict[str, object]]:
    inventory = package.get("semantic_object_inventory") or {}
    typed = package.get("typed_representation") or {}
    objects = inventory.get("objects") or package.get("semantic_objects") or typed.get("objects") or []
    return [item for item in objects if isinstance(item, dict)]


def _important_objects(package: Dict) -> List[Dict[str, object]]:
    inventory = package.get("semantic_object_inventory") or {}
    return [item for item in list(inventory.get("important_objects", [])) if isinstance(item, dict)]


def _constraint_objects(package: Dict) -> List[Dict[str, object]]:
    constraint_objects: List[Dict[str, object]] = []
    for index, value in enumerate(package.get("constraints", []) or [], start=1):
        label = str(value).strip()
        if not label:
            continue
        constraint_objects.append(
            {
                "object_id": stable_semantic_object_id("constraint", label),
                "type": "constraint",
                "value": label,
                "confidence": 1.0,
                "evidence_pointer": f"constraint:{index}",
            }
        )
    return constraint_objects


def _dependency_ids(package: Dict) -> Set[str]:
    dependency_ids: Set[str] = set()
    dependencies = package.get("semantic_dependencies") or {}
    if not isinstance(dependencies, dict):
        return dependency_ids
    for dependency in dependencies.get("required_dependency_objects", []) or []:
        if not isinstance(dependency, dict):
            continue
        subject = dependency.get("subject") or {}
        relation = dependency.get("relation") or {}
        obj = dependency.get("object") or {}
        for part_type, part in [("entity", subject), ("relation", relation), ("entity", obj)]:
            value = str(part.get("canonical") or part.get("value") or "").strip()
            if not value:
                continue
            dependency_ids.add(stable_semantic_object_id(part_type, value))
    return dependency_ids


def _object_id(item: Dict[str, object]) -> str:
    object_type = str(item.get("type", "fact")).strip() or "fact"
    value = str(item.get("value", "")).strip()
    return str(item.get("object_id") or item.get("id") or "").strip() or stable_semantic_object_id(object_type, value)


def _memory_from_objects(objects: List[Dict[str, object]], fallback: str) -> str:
    lines = []
    for item in objects:
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


@dataclass
class GraphRecoveryResult:
    selected_object_ids: List[str]
    required_object_ids: List[str]
    blocked_object_ids: List[str]
    dependency_closure_rate: float | None
    graph_recovery_precision: float | None
    repair_cost: int
    dependency_edge_count: int
    blocked_count: int

    def as_dict(self) -> Dict[str, object]:
        return {
            "selected_object_ids": list(self.selected_object_ids),
            "required_object_ids": list(self.required_object_ids),
            "blocked_object_ids": list(self.blocked_object_ids),
            "dependency_closure_rate": self.dependency_closure_rate,
            "graph_recovery_precision": self.graph_recovery_precision,
            "repair_cost": self.repair_cost,
            "dependency_edge_count": self.dependency_edge_count,
            "blocked_count": self.blocked_count,
        }


class GraphRecoveryPolicy(RecoveryPolicy):
    name = "graph"

    def recover(self, package: dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        package = package or {}
        source_objects = _extract_objects(package)
        important_objects = _important_objects(package)
        constraint_objects = _constraint_objects(package)
        dependency_ids = _dependency_ids(package)
        graph_version = str(os.getenv("SRP_SEMANTIC_GRAPH_VERSION", "v1")).strip().lower()
        graph = build_semantic_runtime_graph_by_version(package, None, None, version=graph_version)

        required_object_ids: Set[str] = set()
        for item in important_objects:
            required_object_ids.add(_object_id(item))
        for item in constraint_objects:
            required_object_ids.add(_object_id(item))
        required_object_ids |= dependency_ids
        if not required_object_ids:
            for item in source_objects:
                required_object_ids.add(_object_id(item))

        selected_objects: List[Dict[str, object]] = []
        blocked_object_ids: List[str] = []
        seen: Set[str] = set()
        for item in source_objects:
            object_id = _object_id(item)
            if object_id in seen:
                continue
            if object_id in required_object_ids:
                selected_objects.append(item)
                seen.add(object_id)
            else:
                blocked_object_ids.append(object_id)

        if not selected_objects:
            selected_objects = list(important_objects[:])
            seen = {_object_id(item) for item in selected_objects}
        for item in constraint_objects:
            object_id = _object_id(item)
            if object_id not in seen:
                selected_objects.append(item)
                seen.add(object_id)

        dependency_edge_count = len(dependency_ids)
        dependency_closure_rate = (
            len(required_object_ids & seen) / len(required_object_ids)
            if required_object_ids
            else None
        )
        graph_recovery_precision = (
            len(required_object_ids & seen) / len(seen)
            if seen
            else None
        )
        repair_cost = len(blocked_object_ids)
        memory = _memory_from_objects(selected_objects, package.get("memory", ""))
        if client is not None:
            # Keep the graph policy deterministic by default; allow the client to refine only the surface text.
            memory = _memory_from_objects(selected_objects, package.get("memory", ""))

        from ...budgeting import get_budget_config
        from ...prompting import build_recovery_prompt
        from ..recover_runtime import budget_recovery_inputs

        budget = get_budget_config()
        recovery_inputs = budget_recovery_inputs(package, anchor_memory)
        prompt = build_recovery_prompt(
            recovery_inputs.compressed_memory,
            package.get("constraints", []),
            package.get("global_vocab", []),
            package.get("local_vocab", []),
            package.get("term_map", {}),
            package.get("loss_notes", []),
            package.get("policy", {}),
            semantic_object_inventory=package.get("semantic_object_inventory"),
            anchor_memory=recovery_inputs.anchor_tail,
        )
        prompt = f"{prompt}\n\nRecovery policy: graph"
        if client is not None:
            model_result = client.generate_with_usage(
                prompt,
                system_prompt="You reconstruct operational semantic state from compact structured memory.",
                max_output_tokens=min(90, budget.output_tokens),
            )
            memory = model_result["text"]
            usage = model_result.get("usage")
        else:
            usage = None

        state = build_recovered_state(package, memory, usage)
        state = attach_recovery_diagnostics(state, package, prompt, anchor_memory=anchor_memory, usage=usage)
        structured_state_package = build_structured_state_package(state, package, anchor_memory=anchor_memory)
        structured_state_package["recovery_policy"] = self.name
        structured_state_package["selected_objects"] = selected_objects
        structured_state_package["rejected_objects"] = [
            item for item in source_objects if _object_id(item) not in seen
        ]
        structured_state_package["semantic_runtime_graph"] = graph.as_dict()
        graph_result = GraphRecoveryResult(
            selected_object_ids=sorted(seen),
            required_object_ids=sorted(required_object_ids),
            blocked_object_ids=sorted(blocked_object_ids),
            dependency_closure_rate=dependency_closure_rate,
            graph_recovery_precision=graph_recovery_precision,
            repair_cost=repair_cost,
            dependency_edge_count=dependency_edge_count,
            blocked_count=len(blocked_object_ids),
        )
        structured_state_package["graph_recovery_result"] = graph_result.as_dict()
        metrics = ReconstructionMetrics(
            selected_object_count=len(selected_objects),
            rejected_object_count=max(0, len(source_objects) - len(selected_objects)),
            available_object_count=len(source_objects),
            policy_name=self.name,
        )
        return ReconstructionResult(
            structured_state_package=structured_state_package,
            recovered_objects=source_objects,
            selected_objects=selected_objects,
            rejected_objects=[item for item in source_objects if _object_id(item) not in seen],
            policy_name=self.name,
            memory=state.memory,
            usage=usage,
            metrics=metrics,
        )
