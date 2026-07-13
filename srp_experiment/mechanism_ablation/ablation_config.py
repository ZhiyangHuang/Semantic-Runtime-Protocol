from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class MechanismAblationVariant:
    name: str
    policy_name: str
    removed_component: str
    description: str
    env_overrides: Dict[str, str]


@dataclass(frozen=True)
class MechanismAblationConfig:
    budgets: Sequence[int]
    seeds: Sequence[int]
    cycles: int = 1
    variants: Sequence[MechanismAblationVariant] = ()


def default_mechanism_ablation_variants() -> List[MechanismAblationVariant]:
    return [
        MechanismAblationVariant(
            name="baseline",
            policy_name="mechanism-ablation-baseline",
            removed_component="none",
            description="Dependency-aware retention baseline with importance and dependency signals.",
            env_overrides={
                "SRP_STATE_ALLOCATION_POLICY": "mechanism-ablation-baseline",
            },
        ),
        MechanismAblationVariant(
            name="remove_importance_weighting",
            policy_name="mechanism-ablation-no-importance",
            removed_component="importance weighting",
            description="Dependency-aware retention without importance weighting.",
            env_overrides={
                "SRP_STATE_ALLOCATION_POLICY": "mechanism-ablation-no-importance",
            },
        ),
        MechanismAblationVariant(
            name="remove_dependency_retention",
            policy_name="mechanism-ablation-no-dependency",
            removed_component="dependency-aware retention",
            description="Importance-only retention without dependency-aware selection.",
            env_overrides={
                "SRP_STATE_ALLOCATION_POLICY": "mechanism-ablation-no-dependency",
            },
        ),
    ]
