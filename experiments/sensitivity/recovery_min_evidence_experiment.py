from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .metrics import SensitivityMetrics, metrics_to_dict
from .results import SensitivityResult
from .storage import SensitivityResultStore


def build_recovery_state() -> SemanticState:
    state = SemanticState(state_id="sensitivity:recovery", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.2,
        confidence=0.5,
        lifecycle_state="approximated",
        version_id="v0",
    )
    return state


def build_recovery_event(evidence_count: int) -> RuntimeEvent:
    evidence_refs = [f"ev:{index}" for index in range(1, evidence_count + 1)]
    return RuntimeEvent(
        event_id=f"event:sensitivity:recovery:{evidence_count}",
        event_type="Recovery",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={
            "evidence_refs": evidence_refs,
            "recovery_source": "lineage",
            "recovery_mode": "restore",
            "restored_lifecycle_state": "active",
            "restored_activation": 0.8,
            "restored_confidence": 0.7,
            "restored_provenance": ["ev:0"],
        },
        mutation_mode="update",
        operator_name="Recovery",
    )


def run_single_recovery_min_evidence_case(value: int, *, baseline: RuntimeConfig | None = None) -> SensitivityResult:
    runtime_config = baseline or load_default_profile()
    runtime_config = RuntimeConfig(**{**asdict(runtime_config), "recovery_min_evidence": value})
    kernel = RuntimeKernel(state=build_recovery_state(), config=None)
    kernel._config.runtime_config = runtime_config
    kernel._recovery_operator.runtime_config = runtime_config
    transition = kernel.apply_event(build_recovery_event(max(value, 1)))
    metrics = SensitivityMetrics(
        successful_transitions=1 if transition.success else 0,
        replay_equivalent=True,
        runtime_event_count=len(kernel.event_stream),
        final_activation=kernel._state.units["u1"].activation if "u1" in kernel._state.units else None,
        evidence_usage_count=len(transition.mutation_summary.get("evidence_refs", [])),
    )
    observations = [
        f"recovery_min_evidence={value}",
        f"transition_success={transition.success}",
        f"evidence_usage_count={metrics.evidence_usage_count}",
    ]
    return SensitivityResult(
        experiment_id=f"recovery_min_evidence_{value}",
        baseline_version="default",
        timestamp=datetime.now(timezone.utc).isoformat(),
        parameter="recovery_min_evidence",
        value=value,
        metrics=metrics_to_dict(metrics),
        observations=observations,
    )


def run_recovery_min_evidence_sensitivity(
    values: Iterable[int] | None = None,
    *,
    store: SensitivityResultStore | None = None,
) -> dict[str, Any]:
    candidate_values = list(values) if values is not None else [1, 2, 3]
    results = [run_single_recovery_min_evidence_case(value) for value in candidate_values]
    stored_paths = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]
    return {
        "experiment": {
            "parameter": "recovery_min_evidence",
            "values": list(candidate_values),
            "baseline": "default",
            "scenario": "recovery",
            "dataset": "fixed_kernel_state",
        },
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }

