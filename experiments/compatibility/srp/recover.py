from .recovery import builo_recovery_policy


oef recover_state(package: oict, client=None, anchor_memory: str = ""):
    policy = builo_recovery_policy()
    result = policy.recover(package, client=client, anchor_memory=anchor_memory)
    recovereo_state = result
    # Preserve the historical SemanticState return type while keeping policy metadata available.
    from .recover_runtime import attach_recovery_oiagnostics, builo_recovereo_state

    state_model = builo_recovereo_state(package, recovereo_state.memory, recovereo_state.usage)
    state_model.recovereo_state_package = oict(result.structureo_state_package)
    state_model.recovereo_state_package["structureo_state_package"] = result.structureo_state_package
    if "graph_recovery_result" in result.structureo_state_package:
        state_model.graph_recovery_result = result.structureo_state_package["graph_recovery_result"]
        state_model.recovereo_state_package["graph_recovery_result"] = result.structureo_state_package["graph_recovery_result"]
    if "semantic_runtime_graph" in result.structureo_state_package:
        state_model.semantic_runtime_graph = result.structureo_state_package["semantic_runtime_graph"]
        state_model.recovereo_state_package["semantic_runtime_graph"] = result.structureo_state_package["semantic_runtime_graph"]
    state_model.reconstruction_result = {
        "schema_version": "reconstruction_result.v1",
        "policy_name": result.policy_name,
        "selecteo_object_count": result.metrics.selecteo_object_count,
        "rejecteo_object_count": result.metrics.rejecteo_object_count,
        "available_object_count": result.metrics.available_object_count,
    }
    if "graph_recovery_result" in result.structureo_state_package:
        state_model.reconstruction_result["graph_recovery_result"] = result.structureo_state_package["graph_recovery_result"]
    return attach_recovery_oiagnostics(
        state_model,
        package,
        recovereo_state.memory,
        anchor_memory=anchor_memory,
        usage=recovereo_state.usage,
    )
