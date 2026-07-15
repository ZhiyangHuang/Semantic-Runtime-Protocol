from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel
from srp_runtime.replay import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .metrics import SensitivityMetrics, metrics_to_dict
from .results import SensitivityResult
from .storage import SensitivityResultStore


def build_preserve_state() -> SemanticState:
    state = SemanticState(state_id="sensitivity:preserve", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.2,
        confidence=0.5,
        lifecycle_state="active",
        version_id="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_id="u2",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.1,
        confidence=0.5,
        lifecycle_state="active",
        version_id="v0",
    )
    state.graph.add_unit(state.units["u1"])
    state.graph.add_unit(state.units["u2"])
    state.graph.relation_index["u1"] = ["u2"]
    state.graph.relation_index["u2"] = ["u1"]
    state.units["u1"].relation_ids = ["r:u1->u2"]
    state.units["u2"].relation_ids = ["r:u2->u1"]
    return state


def build_forgetting_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:sensitivity:preserve:1",
        event_type="Forgetting",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payload={
            "target_unit_id": "u2",
            "evidence_refs": ["trace:f1", "trace:f2"],
        },
        mutation_mode="update",
        operator_name="Forgetting",
    )


def _evidence_retention_score(state: SemanticState) -> float:
    unit = state.units.get("u2")
    if unit is None:
        return 0.0
    evidence_refs = [str(item) for item in unit.semantic_payload.get("forgetting_evidence_refs", [])]
    provenance = [str(item) for item in unit.provenance]
    if not evidence_refs:
        return 0.0
    retained = sum(1 for item in evidence_refs if item in provenance)
    return retained / len(evidence_refs)


def run_single_preserve_evidence_case(value: bool, *, baseline: RuntimeConfig | None = None) -> SensitivityResult:
    runtime_config = baseline or load_default_profile()
    runtime_config = RuntimeConfig(**{**asdict(runtime_config), "preserve_evidence": value})
    initial_state = build_preserve_state()
    kernel = RuntimeKernel(state=initial_state, config=None)
    kernel._config.runtime_config = runtime_config
    kernel._forgetting_operator.runtime_config = runtime_config
    transition = kernel.apply_event(build_forgetting_event())
    replay_result = ReplayEngine().replay(initial_state.snapshot(), [build_forgetting_event()])
    evidence_record_count = len(kernel._state.units["u2"].provenance)
    audit_completeness = _evidence_retention_score(kernel._state)
    metrics = SensitivityMetrics(
        successful_transitions=1 if transition.success else 0,
        replay_equivalent=replay_result.reconstructed_state.state_ref() == kernel._state.state_ref(),
        runtime_event_count=len(kernel.event_stream),
        final_activation=kernel._state.units["u2"].activation if "u2" in kernel._state.units else None,
        evidence_usage_count=len(transition.mutation_summary.get("evidence_refs", [])),
        evidence_record_count=evidence_record_count,
        audit_completeness_score=audit_completeness,
    )
    observations = [
        f"preserve_evidence={value}",
        f"transition_success={transition.success}",
        f"evidence_record_count={evidence_record_count}",
        f"audit_completeness_score={audit_completeness}",
    ]
    return SensitivityResult(
        experiment_id=f"preserve_evidence_{str(value).lower()}",
        baseline_version="default",
        timestamp=datetime.now(timezone.utc).isoformat(),
        parameter="preserve_evidence",
        value=value,
        metrics=metrics_to_dict(metrics),
        observations=observations,
    )


def run_preserve_evidence_sensitivity(
    values: Iterable[bool] | None = None,
    *,
    store: SensitivityResultStore | None = None,
) -> dict[str, Any]:
    candidate_values = list(values) if values is not None else [True, False]
    results = [run_single_preserve_evidence_case(value) for value in candidate_values]
    stored_paths = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]
    return {
        "experiment": {
            "parameter": "preserve_evidence",
            "values": list(candidate_values),
            "baseline": "default",
            "scenario": "forgetting",
            "dataset": "fixed_kernel_state",
        },
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }

