from budgeting import available_memory_budget, clip_tail_to_budget, get_budget_config
from .state import SemanticState
from prompting import build_recovery_prompt


def recover_state(package: dict, client=None, anchor_memory: str = "") -> SemanticState:
    if client is None:
        memory = package["memory"]
        if not memory.endswith("."):
            memory = f"{memory}."
        usage = None
    else:
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
    return state
