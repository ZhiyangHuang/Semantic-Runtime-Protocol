from typing import Dict


def apply_object_lifecycle(state) -> Dict[str, int]:
    retained_importance = state._policy_float("lifecycle_retained_importance", 0.35)
    retained_passes = state._policy_int("lifecycle_retained_passes", 2)
    archived_importance = state._policy_float("lifecycle_archived_importance", 0.3)
    archived_drift_count = state._policy_int("lifecycle_archived_drift_count", 2)
    archived_failure_count = state._policy_int("lifecycle_archived_failure_count", 2)
    decayed_floor = state._policy_float("lifecycle_decayed_floor", 0.05)
    decayed_multiplier = state._policy_float("lifecycle_decayed_multiplier", 0.92)
    retained = 0
    decayed = 0
    archived = 0
    for metadata in state.runtime_metadata.values():
        previous_state = metadata.lifecycle_state
        stable = metadata.verification_passes > metadata.verification_failures and metadata.drift_count == 0
        active = metadata.importance >= retained_importance or metadata.verification_passes >= retained_passes
        risky = (
            metadata.drift_count >= archived_drift_count
            or metadata.verification_failures >= archived_failure_count
        )
        if active and stable:
            metadata.lifecycle_state = "retained"
            retained += 1
        elif risky and metadata.importance < archived_importance:
            metadata.lifecycle_state = "archived"
            metadata.archived_round = state.round_id
            metadata.importance = 0.0
            metadata.confidence = min(metadata.confidence, 0.25)
            archived += 1
        else:
            metadata.lifecycle_state = "decayed"
            metadata.importance = max(decayed_floor, metadata.importance * decayed_multiplier)
            decayed += 1
        if metadata.lifecycle_state != previous_state:
            metadata.lifecycle_actions += 1
    return {
        "retained": retained,
        "decayed": decayed,
        "archived": archived,
    }
