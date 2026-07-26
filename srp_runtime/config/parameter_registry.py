from __future__ import annotations

from typing import Dict, Iterable

from .defaults import RuntimeConfig
from .parameter_definition import ParameterDefinition, ParameterRange


PARAMETER_REGISTRY: Dict[str, ParameterDefinition] = {
    "lifecycle_retained_importance": ParameterDefinition(
        name="lifecycle_retained_importance",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=0.35,
        value_type="float",
        valid_range=ParameterRange(0.0, 1.0, "minimum importance for retention"),
        metric="retention quality",
        description="Minimum importance for an object to be eligible for retention.",
    ),
    "lifecycle_retained_passes": ParameterDefinition(
        name="lifecycle_retained_passes",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=2,
        value_type="int",
        valid_range=ParameterRange(1, None, "minimum verification passes"),
        metric="stability / retention",
        description="Minimum verification passes for an object to be considered active enough for retention.",
    ),
    "lifecycle_archived_importance": ParameterDefinition(
        name="lifecycle_archived_importance",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=0.3,
        value_type="float",
        valid_range=ParameterRange(0.0, 1.0, "archive-risk threshold"),
        metric="archival precision",
        description="Importance threshold below which risky objects may be archived.",
    ),
    "lifecycle_archived_drift_count": ParameterDefinition(
        name="lifecycle_archived_drift_count",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=2,
        value_type="int",
        valid_range=ParameterRange(0, None, "archival-risk drift count"),
        metric="archive recall",
        description="Minimum drift count that marks an object as archival-risky.",
    ),
    "lifecycle_archived_failure_count": ParameterDefinition(
        name="lifecycle_archived_failure_count",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=2,
        value_type="int",
        valid_range=ParameterRange(0, None, "archival-risk failure count"),
        metric="archive recall",
        description="Minimum failure count that marks an object as archival-risky.",
    ),
    "lifecycle_decayed_floor": ParameterDefinition(
        name="lifecycle_decayed_floor",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=0.05,
        value_type="float",
        valid_range=ParameterRange(0.0, 1.0, "lower bound for decay"),
        metric="stability",
        description="Lower bound applied when decaying importance.",
    ),
    "lifecycle_decayed_multiplier": ParameterDefinition(
        name="lifecycle_decayed_multiplier",
        owner="LifecyclePolicy",
        parameter_class="Tunable",
        status="Frozen",
        default=0.92,
        value_type="float",
        valid_range=ParameterRange(0.0, 1.0, "decay multiplier"),
        metric="stability / drift",
        description="Multiplier applied to importance during decay.",
    ),
    "activation_threshold": ParameterDefinition(
        name="activation_threshold",
        owner="ApproximationOperator",
        parameter_class="Tunable",
        status="Experimental",
        default=0.2,
        value_type="float",
        valid_range=ParameterRange(0.0, 1.0, "sweep candidate for approximation"),
        metric="semantic fidelity / compression",
        description="Activation threshold used by approximation to preserve or remove a unit.",
        experimental=True,
    ),
    "preserve_evidence": ParameterDefinition(
        name="preserve_evidence",
        owner="ForgettingOperator",
        parameter_class="Tunable",
        status="Experimental",
        default=True,
        value_type="bool",
        valid_range=None,
        metric="traceability",
        description="Whether forgetting requires evidence references to be preserved.",
        experimental=True,
    ),
    "archive_relations": ParameterDefinition(
        name="archive_relations",
        owner="ForgettingOperator",
        parameter_class="Tunable",
        status="Experimental",
        default=True,
        value_type="bool",
        valid_range=None,
        metric="archive completeness",
        description="Whether relation markers are archived during forgetting.",
        experimental=True,
    ),
}


def get_parameter_definition(name: str) -> ParameterDefinition:
    return PARAMETER_REGISTRY[name]


def iter_parameter_definitions() -> Iterable[ParameterDefinition]:
    return PARAMETER_REGISTRY.values()


def build_runtime_config(overrides: dict[str, object] | None = None) -> RuntimeConfig:
    overrides = overrides or {}
    base = RuntimeConfig()
    values = dict(base.__dict__)
    values.update({key: value for key, value in overrides.items() if key in values})
    return RuntimeConfig(**values)

