from .reconstruction import build_reconstruction_policy


def recover_state(package: dict, client=None, anchor_memory: str = ""):
    policy = build_reconstruction_policy()
    result = policy.reconstruct(package, client=client, anchor_memory=anchor_memory)
    recovered_state = result
    # Preserve the historical SemanticState return type while keeping policy metadata available.
    from .recover_runtime import attach_recovery_diagnostics, build_recovered_state

    state_model = build_recovered_state(package, recovered_state.memory, recovered_state.usage)
    state_model.recovered_state_package = dict(result.structured_state_package)
    state_model.recovered_state_package["structured_state_package"] = result.structured_state_package
    state_model.reconstruction_result = {
        "schema_version": "reconstruction_result.v1",
        "policy_name": result.policy_name,
        "selected_object_count": result.metrics.selected_object_count,
        "rejected_object_count": result.metrics.rejected_object_count,
        "available_object_count": result.metrics.available_object_count,
    }
    return attach_recovery_diagnostics(
        state_model,
        package,
        recovered_state.memory,
        anchor_memory=anchor_memory,
        usage=recovered_state.usage,
    )
