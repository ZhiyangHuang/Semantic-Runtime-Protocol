from .recovery import build_recovery_policy


def recover_state(package: dict, client=None, anchor_memory: str = ""):
    policy = build_recovery_policy()
    result = policy.recover(package, client=client, anchor_memory=anchor_memory)
    recovered_state = result
    # Preserve the historical SemanticState return type while keeping policy metadata available.
    from .recover_runtime import attach_recovery_diagnostics, build_recovered_state

    state_model = build_recovered_state(package, recovered_state.memory, recovered_state.usage)
    state_model.recovered_state_package = dict(result.structured_state_package)
    state_model.recovered_state_package["structured_state_package"] = result.structured_state_package
    if "graph_recovery_result" in result.structured_state_package:
        state_model.graph_recovery_result = result.structured_state_package["graph_recovery_result"]
        state_model.recovered_state_package["graph_recovery_result"] = result.structured_state_package["graph_recovery_result"]
    if "semantic_runtime_graph" in result.structured_state_package:
        state_model.semantic_runtime_graph = result.structured_state_package["semantic_runtime_graph"]
        state_model.recovered_state_package["semantic_runtime_graph"] = result.structured_state_package["semantic_runtime_graph"]
    state_model.reconstruction_result = {
        "schema_version": "reconstruction_result.v1",
        "policy_name": result.policy_name,
        "selected_object_count": result.metrics.selected_object_count,
        "rejected_object_count": result.metrics.rejected_object_count,
        "available_object_count": result.metrics.available_object_count,
    }
    if "graph_recovery_result" in result.structured_state_package:
        state_model.reconstruction_result["graph_recovery_result"] = result.structured_state_package["graph_recovery_result"]
    return attach_recovery_diagnostics(
        state_model,
        package,
        recovered_state.memory,
        anchor_memory=anchor_memory,
        usage=recovered_state.usage,
    )
