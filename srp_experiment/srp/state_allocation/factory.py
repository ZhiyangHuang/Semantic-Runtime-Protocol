from __future__ import annotations

import os

from .policy import StateAllocationPolicy
from .policies import (
    ConstrainedAllocationPolicy,
    DependencyAwareAllocationPolicy,
    DependencyAwareV2AllocationPolicy,
    DependencyAwareV3AllocationPolicy,
    MinimalSufficientAllocationPolicy,
    RecoveredAllocationPolicy,
    RandomAllocationPolicy,
    UnrestrictedAllocationPolicy,
)
from ...mechanism_ablation.variants.baseline import MechanismAblationBaselinePolicy
from ...mechanism_ablation.variants.remove_importance_weighting import MechanismAblationNoImportancePolicy
from ...mechanism_ablation.variants.remove_dependency_retention import MechanismAblationNoDependencyPolicy


def state_allocation_policy_name() -> str:
    return str(os.getenv("SRP_STATE_ALLOCATION_POLICY", "minimal")).strip().lower()


def build_state_allocation_policy() -> StateAllocationPolicy:
    name = state_allocation_policy_name()
    if name == "recovered":
        return RecoveredAllocationPolicy()
    if name == "unrestricted":
        return UnrestrictedAllocationPolicy()
    if name == "constrained":
        return ConstrainedAllocationPolicy()
    if name == "random":
        return RandomAllocationPolicy()
    if name in {"dependency-aware", "dependency"}:
        return DependencyAwareAllocationPolicy()
    if name in {"dependency-aware-v2", "dependency-v2", "dependency2"}:
        return DependencyAwareV2AllocationPolicy()
    if name in {"dependency-aware-v3", "dependency-v3", "dependency3"}:
        return DependencyAwareV3AllocationPolicy()
    if name in {"mechanism-ablation-baseline", "mechanism-ablation-baseline-v1"}:
        return MechanismAblationBaselinePolicy()
    if name in {"mechanism-ablation-no-importance", "mechanism-ablation-no-importance-v1"}:
        return MechanismAblationNoImportancePolicy()
    if name in {"mechanism-ablation-no-dependency", "mechanism-ablation-importance-only"}:
        return MechanismAblationNoDependencyPolicy()
    return MinimalSufficientAllocationPolicy()
