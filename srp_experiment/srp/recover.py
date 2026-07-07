from ..budgeting import available_memory_budget, clip_tail_to_budget, get_budget_config
from ..prompting import build_recovery_prompt
from .state import SemanticState

RECOVERY_TEMPLATE_VERSION = "recovery_template.v1"
RECOVERY_TEMPLATE_SECTIONS = [
    "system",
    "policy",
    "constraints",
    "vocabulary",
    "term_map",
    "known_loss_risks",
    "anchor_memory_tail",
    "compressed_memory",
]


def _build_recovery_template_summary(prompt: str, anchor_memory: str) -> dict:
    return {
        "schema_version": RECOVERY_TEMPLATE_VERSION,
        "sections": list(RECOVERY_TEMPLATE_SECTIONS),
        "prompt_word_count": len(prompt.split()),
        "anchor_memory_word_count": len(str(anchor_memory).split()) if anchor_memory else 0,
    }


def recover_state(package: dict, client=None, anchor_memory: str = "") -> SemanticState:
    budget = get_budget_config()
    prompt = build_recovery_prompt(
        package["memory"],
        package.get("constraints", []),
        package.get("global_vocab", []),
        package.get("local_vocab", []),
        package.get("term_map", {}),
        package.get("loss_notes", []),
        package.get("policy", {}),
        anchor_memory=clip_tail_to_budget(anchor_memory, available_memory_budget(constraints=package.get("constraints", []))),
    )
    if client is None:
        memory = package["memory"]
        if not memory.endswith("."):
            memory = f"{memory}."
        usage = None
    else:
        model_result = client.generate_with_usage(
            prompt,
            system_prompt="You reconstruct operational semantic state from compact structured memory.",
            max_output_tokens=min(90, budget.output_tokens),
        )
        memory = model_result["text"]
        usage = model_result.get("usage")
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
    state.ensure_typed_representation(anchor_memory=anchor_memory)
    state.recovery_summary = state.build_recovery_summary(package, anchor_memory=anchor_memory)
    state.state_continuity_summary = state.build_state_continuity_summary(package, anchor_memory=anchor_memory)
    state.recovery_template_summary = _build_recovery_template_summary(prompt, anchor_memory)
    state.recovery_template_summary_flat = state.build_recovery_template_summary_flat(state.recovery_template_summary)
    state.lifecycle_summary = state.build_lifecycle_summary()
    state.lifecycle_summary["flat"] = state.lifecycle_summary_flat(state.lifecycle_summary)
    state.object_update_summary = {
        "schema_version": "object_update_summary.v1",
        "round_id": state.round_id,
        "committed": True if usage is not None else False,
        "update_count": 0,
        "updates": [],
    }
    state.object_update_summary_flat = state.build_object_update_summary_flat(state.object_update_summary)
    return state
