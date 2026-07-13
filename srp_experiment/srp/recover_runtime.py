import os
from dataclasses import dataclass
from typing import Dict, Optional

from ..budgeting import available_memory_budget, clip_tail_to_budget
from .state import SemanticState


@dataclass
class RecoveryInputs:
    compressed_memory: str
    anchor_tail: str


def recovery_template_summary(prompt: str, anchor_memory: str) -> Dict[str, object]:
    return {
        "schema_version": "recovery_template.v1",
        "sections": [
            "system",
            "policy",
            "semantic_object_inventory",
            "structured_state_package",
            "constraints",
            "vocabulary",
            "term_map",
            "known_loss_risks",
            "anchor_memory_tail",
            "compressed_memory",
        ],
        "prompt_word_count": len(prompt.split()),
        "anchor_memory_word_count": len(str(anchor_memory).split()) if anchor_memory else 0,
    }


def env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def budget_recovery_inputs(package: Dict, anchor_memory: str) -> RecoveryInputs:
    total_budget = available_memory_budget(constraints=package.get("constraints", []))
    anchor_cap = min(env_int("SRP_RECOVERY_ANCHOR_TOKENS", 96), max(24, total_budget // 3))
    compressed_cap = max(48, total_budget - anchor_cap)
    return RecoveryInputs(
        compressed_memory=clip_tail_to_budget(package.get("memory", ""), compressed_cap),
        anchor_tail=clip_tail_to_budget(anchor_memory, anchor_cap),
    )


def recover_memory_from_package(
    package: Dict,
    prompt: str,
    budget,
    client=None,
) -> tuple[str, Optional[Dict]]:
    if client is None:
        memory = package["memory"]
        if not memory.endswith("."):
            memory = f"{memory}."
        return memory, None
    model_result = client.generate_with_usage(
        prompt,
        system_prompt="You reconstruct operational semantic state from compact structured memory.",
        max_output_tokens=min(90, budget.output_tokens),
    )
    return model_result["text"], model_result.get("usage")


def build_recovered_state(package: Dict, memory: str, usage: Optional[Dict]) -> SemanticState:
    state = SemanticState(
        memory=memory,
        constraints=list(package.get("constraints", [])),
        global_vocabulary=list(package.get("global_vocab", [])),
        local_vocabulary=list(package.get("local_vocab", [])),
        term_map=dict(package.get("term_map", {})),
        loss_notes=list(package.get("loss_notes", [])),
        policy=dict(package.get("policy", {})),
    )
    state.usage = usage
    return state


def build_structured_state_package(state: SemanticState, package: Dict, anchor_memory: str = "") -> Dict[str, object]:
    representation = state.ensure_typed_representation(anchor_memory=anchor_memory)
    semantic_object_inventory = package.get("semantic_object_inventory") or {}
    return {
        "schema_version": "structured_state_package.v1",
        "memory": state.memory,
        "constraints": list(state.constraints),
        "global_vocabulary": list(state.global_vocabulary),
        "local_vocabulary": list(state.local_vocabulary),
        "term_map": dict(state.term_map),
        "policy": dict(state.policy),
        "semantic_object_inventory": semantic_object_inventory,
        "typed_representation": representation.as_dict(),
        "object_count": semantic_object_inventory.get("object_count", len(representation.objects)),
        "object_ids": semantic_object_inventory.get("object_ids", [item.stable_id() for item in representation.objects]),
        "type_counts": semantic_object_inventory.get("type_counts", {}),
        "important_objects": semantic_object_inventory.get("important_objects", []),
        "runtime_summary": state.runtime_summary(),
    }


def attach_recovery_diagnostics(
    state: SemanticState,
    package: Dict,
    prompt: str,
    anchor_memory: str,
    usage: Optional[Dict],
) -> SemanticState:
    state.ensure_typed_representation(anchor_memory=anchor_memory)
    semantic_object_inventory = package.get("semantic_object_inventory") or {}
    state.recovered_state_package = build_structured_state_package(state, package, anchor_memory=anchor_memory)
    if getattr(state, "graph_recovery_result", None) is not None:
        state.recovered_state_package["graph_recovery_result"] = state.graph_recovery_result
    if getattr(state, "semantic_runtime_graph", None) is not None:
        state.recovered_state_package["semantic_runtime_graph"] = state.semantic_runtime_graph
    reconstruction_result = getattr(state, "reconstruction_result", None)
    if reconstruction_result is not None:
        state.recovered_state_package["reconstruction_result"] = reconstruction_result
        state.recovered_state_package["structured_state_package"] = dict(state.recovered_state_package)
        state.recovered_state_package["structured_state_package"].pop("structured_state_package", None)
    state.recovery_summary = state.build_recovery_summary(package, anchor_memory=anchor_memory)
    state.state_continuity_summary = state.build_state_continuity_summary(package, anchor_memory=anchor_memory)
    state.recovery_template_summary = recovery_template_summary(prompt, anchor_memory)
    state.recovery_template_summary_flat = state.build_recovery_template_summary_flat(state.recovery_template_summary)
    state.recovery_template_summary["semantic_object_inventory_present"] = bool(semantic_object_inventory)
    state.recovery_template_summary["semantic_object_count"] = semantic_object_inventory.get("object_count")
    state.recovery_template_summary["semantic_object_type_counts"] = semantic_object_inventory.get("type_counts", {})
    state.recovery_template_summary["structured_state_package_present"] = bool(state.recovered_state_package)
    state.recovery_template_summary["structured_state_package_version"] = (
        state.recovered_state_package.get("schema_version") if state.recovered_state_package else None
    )
    state.lifecycle_summary = state.build_lifecycle_summary()
    state.lifecycle_summary["flat"] = state.lifecycle_summary_flat(state.lifecycle_summary)
    state.object_update_summary = {
        "schema_version": "object_update_summary.v1",
        "round_id": state.round_id,
        "committed": usage is not None,
        "update_count": 0,
        "updates": [],
    }
    state.object_update_summary_flat = state.build_object_update_summary_flat(state.object_update_summary)
    return state
