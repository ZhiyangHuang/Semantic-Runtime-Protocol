from __future__ import annotations

from typing import Dict, List

from ...budgeting import get_budget_config
from ...prompting import build_recovery_prompt
from ..semantic_parser import stable_semantic_object_id
from ..recover_runtime import (
    attach_recovery_diagnostics,
    build_recovered_state,
    build_structured_state_package,
    budget_recovery_inputs,
    recover_memory_from_package,
)
from .policy import ReconstructionMetrics, ReconstructionPolicy, ReconstructionResult


def _objects_from_package(package: Dict) -> List[Dict[str, object]]:
    structured = package.get("structured_state_package") or package.get("recovered_state_package") or {}
    typed_representation = structured.get("typed_representation") or {}
    return list(typed_representation.get("objects", []))


def _important_objects_from_package(package: Dict) -> List[Dict[str, object]]:
    structured = package.get("structured_state_package") or package.get("recovered_state_package") or {}
    inventory = structured.get("semantic_object_inventory") or package.get("semantic_object_inventory") or {}
    return list(inventory.get("important_objects", []))


def _select_objects(objects: List[Dict[str, object]], *, limit: int | None = None, allowed_types: set[str] | None = None) -> List[Dict[str, object]]:
    selected: List[Dict[str, object]] = []
    seen: set[str] = set()
    for item in objects:
        if not isinstance(item, dict):
            continue
        object_type = str(item.get("type", "fact")).strip() or "fact"
        if allowed_types is not None and object_type not in allowed_types:
            continue
        value = str(item.get("value", "")).strip()
        if not value:
            continue
        object_id = stable_semantic_object_id(object_type, value)
        if object_id in seen:
            continue
        selected.append(item)
        seen.add(object_id)
        if limit is not None and len(selected) >= limit:
            break
    return selected


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


def _reconstruct_with_policy(
    package: Dict,
    *,
    client=None,
    anchor_memory: str = "",
    policy_name: str,
    object_limit: int | None = None,
    allowed_types: set[str] | None = None,
) -> ReconstructionResult:
    budget = get_budget_config()
    recovery_inputs = budget_recovery_inputs(package, anchor_memory)
    structured = package.get("structured_state_package") or package.get("recovered_state_package") or {}
    objects = _objects_from_package(package)
    important_objects = _important_objects_from_package(package)
    if object_limit is None:
        selected_objects = list(objects)
    else:
        selected_objects = _select_objects(objects, limit=object_limit, allowed_types=allowed_types)
    if policy_name == "minimal":
        selected_objects = _select_objects(
            important_objects + objects,
            limit=object_limit or max(1, len(important_objects)),
            allowed_types=allowed_types or {"question", "constraint", "anchor", "fact", "answer"},
        )
    elif policy_name == "constrained":
        selected_objects = _select_objects(
            objects,
            limit=object_limit,
            allowed_types=allowed_types or {"question", "constraint", "anchor", "fact", "answer"},
        )
    if client is None:
        if policy_name == "unrestricted":
            memory = package["memory"]
            if not memory.endswith("."):
                memory = f"{memory}."
        else:
            memory = _memory_from_objects(selected_objects, package.get("memory", ""))
            if not memory.endswith("."):
                memory = f"{memory}." if memory else package.get("memory", "")
        usage = None
    else:
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
        prompt = f"{prompt}\n\nReconstruction policy: {policy_name}"
        model_result = client.generate_with_usage(
            prompt,
            system_prompt="You reconstruct operational semantic state from compact structured memory.",
            max_output_tokens=min(90, budget.output_tokens),
        )
        memory = model_result["text"]
        usage = model_result.get("usage")
    reconstructed_state = build_recovered_state(package, memory, usage)
    reconstructed_state = attach_recovery_diagnostics(
        reconstructed_state,
        package,
        prompt if client is not None else memory,
        anchor_memory=anchor_memory,
        usage=usage,
    )
    structured_state_package = build_structured_state_package(reconstructed_state, package, anchor_memory=anchor_memory)
    structured_state_package["reconstruction_policy"] = policy_name
    structured_state_package["selected_objects"] = selected_objects
    structured_state_package["rejected_objects"] = [item for item in objects if item not in selected_objects]
    metrics = ReconstructionMetrics(
        selected_object_count=len(selected_objects),
        rejected_object_count=max(0, len(objects) - len(selected_objects)),
        available_object_count=len(objects),
        policy_name=policy_name,
    )
    return ReconstructionResult(
        structured_state_package=structured_state_package,
        recovered_objects=objects,
        selected_objects=selected_objects,
        rejected_objects=[item for item in objects if item not in selected_objects],
        policy_name=policy_name,
        memory=reconstructed_state.memory,
        usage=usage,
        metrics=metrics,
    )


class UnrestrictedReconstructionPolicy(ReconstructionPolicy):
    name = "unrestricted"

    def reconstruct(self, package: Dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        return _reconstruct_with_policy(
            package,
            client=client,
            anchor_memory=anchor_memory,
            policy_name=self.name,
        )


class ConstrainedReconstructionPolicy(ReconstructionPolicy):
    name = "constrained"

    def reconstruct(self, package: Dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        return _reconstruct_with_policy(
            package,
            client=client,
            anchor_memory=anchor_memory,
            policy_name=self.name,
            object_limit=24,
        )


class MinimalSufficientReconstructionPolicy(ReconstructionPolicy):
    name = "minimal"

    def reconstruct(self, package: Dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        return _reconstruct_with_policy(
            package,
            client=client,
            anchor_memory=anchor_memory,
            policy_name=self.name,
            object_limit=12,
            allowed_types={"question", "constraint", "anchor", "answer"},
        )
