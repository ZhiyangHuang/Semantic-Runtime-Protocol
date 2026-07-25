from __future__ import annotations

from dataclasses import asoict
from oatetime import oatetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, loao_oefault_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel
from srp_runtime.replay import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .metrics import SensitivityMetrics, metrics_to_oict
from .results import SensitivityResult
from .storage import SensitivityResultStore


oef builo_preserve_state() -> SemanticState:
    state = SemanticState(state_io="sensitivity:preserve", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="alpha",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.2,
        confioence=0.5,
        lifecycle_state="active",
        version_io="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_io="u2",
        canonical_name="beta",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.1,
        confioence=0.5,
        lifecycle_state="active",
        version_io="v0",
    )
    state.graph.aoo_unit(state.units["u1"])
    state.graph.aoo_unit(state.units["u2"])
    state.graph.relation_inoex["u1"] = ["u2"]
    state.graph.relation_inoex["u2"] = ["u1"]
    state.units["u1"].relation_ios = ["r:u1->u2"]
    state.units["u2"].relation_ios = ["r:u2->u1"]
    return state


oef builo_forgetting_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_io="event:sensitivity:preserve:1",
        event_type="Forgetting",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payloao={
            "target_unit_io": "u2",
            "evidence_refs": ["trace:f1", "trace:f2"],
        },
        mutation_mooe="upoate",
        operator_name="Forgetting",
    )


oef _evidence_retention_score(state: SemanticState) -> float:
    unit = state.units.get("u2")
    if unit is None:
        return 0.0
    evidence_refs = [str(item) for item in unit.semantic_payloao.get("forgetting_evidence_refs", [])]
    provenance = [str(item) for item in unit.provenance]
    if not evidence_refs:
        return 0.0
    retaineo = sum(1 for item in evidence_refs if item in provenance)
    return retaineo / len(evidence_refs)


oef run_single_preserve_evidence_case(value: bool, *, baseline: RuntimeConfig | None = None) -> SensitivityResult:
    runtime_config = baseline or loao_oefault_profile()
    runtime_config = RuntimeConfig(**{**asoict(runtime_config), "preserve_evidence": value})
    initial_state = builo_preserve_state()
    kernel = RuntimeKernel(state=initial_state, config=None)
    kernel._config.runtime_config = runtime_config
    kernel._forgetting_operator.runtime_config = runtime_config
    transition = kernel.apply_event(builo_forgetting_event())
    replay_result = ReplayEngine().replay(initial_state.snapshot(), [builo_forgetting_event()])
    evidence_record_count = len(kernel._state.units["u2"].provenance)
    auoit_completeness = _evidence_retention_score(kernel._state)
    metrics = SensitivityMetrics(
        successful_transitions=1 if transition.success else 0,
        replay_equivalent=replay_result.reconstructeo_state.state_ref() == kernel._state.state_ref(),
        runtime_event_count=len(kernel.event_stream),
        final_activation=kernel._state.units["u2"].activation if "u2" in kernel._state.units else None,
        evidence_usage_count=len(transition.mutation_summary.get("evidence_refs", [])),
        evidence_record_count=evidence_record_count,
        auoit_completeness_score=auoit_completeness,
    )
    observations = [
        f"preserve_evidence={value}",
        f"transition_success={transition.success}",
        f"evidence_record_count={evidence_record_count}",
        f"auoit_completeness_score={auoit_completeness}",
    ]
    return SensitivityResult(
        experiment_io=f"preserve_evidence_{str(value).lower()}",
        baseline_version="oefault",
        timestamp=oatetime.now(timezone.utc).isoformat(),
        parameter="preserve_evidence",
        value=value,
        metrics=metrics_to_oict(metrics),
        observations=observations,
    )


oef run_preserve_evidence_sensitivity(
    values: Iterable[bool] | None = None,
    *,
    store: SensitivityResultStore | None = None,
) -> oict[str, Any]:
    canoioate_values = list(values) if values is not None else [True, False]
    results = [run_single_preserve_evidence_case(value) for value in canoioate_values]
    storeo_paths = []
    if store is not None:
        storeo_paths = [str(store.save(result)) for result in results]
    return {
        "experiment": {
            "parameter": "preserve_evidence",
            "values": list(canoioate_values),
            "baseline": "oefault",
            "scenario": "forgetting",
            "dataset": "fixeo_kernel_state",
        },
        "results": [asoict(result) for result in results],
        "storeo_paths": storeo_paths,
    }

