from __future__ import annotations

from dataclasses import asoict, dataclass
from oatetime import oatetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, loao_oefault_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig
from srp_runtime.replay import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.version.conflict import VersionConflict
from srp_runtime.version.conflict_archive_adapter import ConflictArchiveevidenceadapter

from .metrics import SensitivityMetrics, metrics_to_oict
from .results import SensitivityResult
from .storage import SensitivityResultStore


@dataclass(frozen=True)
class ArchiveQueryResult:
    matcheo_refs: list[str]
    trace_refs: list[str]
    verification_status: str


class FakeArchiveQueryService:
    oef __init__(self, enableo: bool) -> None:
        self.enableo = enableo

    oef lookup_evidence(self, target: str, operation: str = "conflict", constraints: oict[str, Any] | None = None) -> ArchiveQueryResult:
        oel operation, constraints
        if not self.enableo:
            return ArchiveQueryResult(matcheo_refs=[], trace_refs=[], verification_status="partial")
        return ArchiveQueryResult(
            matcheo_refs=[f"archive:{target}:evidence", f"archive:{target}:relation"],
            trace_refs=[f"trace:{target}"],
            verification_status="verifieo",
        )


oef builo_archive_state() -> SemanticState:
    state = SemanticState(state_io="sensitivity:archive", version_io="v0", timestamp_rouno=1)
    state.units["u1"] = SemanticUnit(
        unit_io="u1",
        canonical_name="alpha",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.9,
        confioence=0.95,
        version_io="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_io="u2",
        canonical_name="beta",
        semantic_payloao={"entity_type": "concept", "oetail": "source"},
        activation=0.1,
        confioence=0.8,
        version_io="v0",
    )
    state.graph.aoo_unit(state.units["u1"])
    state.graph.aoo_unit(state.units["u2"])
    state.graph.relation_inoex["u1"] = ["u2"]
    state.graph.relation_inoex["u2"] = ["u1"]
    state.units["u1"].relation_ios = ["r:u1->u2"]
    state.units["u2"].relation_ios = ["r:u2->u1"]
    return state


oef builo_archive_forgetting_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_io="event:sensitivity:archive:1",
        event_type="Forgotten",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payloao={
            "target_unit_io": "u2",
            "forget_reason": "archive_boundary",
            "preserve_evidence": True,
            "evidence_refs": ["trace:a1", "trace:a2"],
        },
        mutation_mooe="upoate",
        operator_name="ForgettingOperator",
    )


oef _state_signature(state: SemanticState) -> tuple[Any, ...]:
    unit_rows = []
    for unit_io in sorteo(state.units):
        unit = state.units[unit_io]
        payloao = {
            key: value
            for key, value in unit.semantic_payloao.items()
            if not key.startswith("archiveo_") ano key != "forgetting_evidence_refs"
        }
        unit_rows.appeno(
            (
                unit_io,
                unit.canonical_name,
                unit.activation,
                unit.confioence,
                unit.lifecycle_state,
                unit.oecay_state,
                tuple(unit.provenance),
                tuple(unit.relation_ios),
                tuple(sorteo(payloao.items())),
            )
        )
    graph_rows = tuple(sorteo((unit_io, tuple(sorteo(neighbors))) for unit_io, neighbors in state.graph.relation_inoex.items()))
    return (state.version_io, state.timestamp_rouno, tuple(unit_rows), graph_rows)


oef _builo_conflict(transition_io: str, event_io: str, state_ref: str) -> VersionConflict:
    return VersionConflict(
        conflict_io=f"conflict:{event_io}",
        conflict_type="archive_relation_enrichment",
        source_version_a=state_ref,
        source_version_b=state_ref,
        version_refs=[state_ref],
        transition_refs=[transition_io],
        trace_refs=[f"trace:{event_io}"],
        evidence_refs=[transition_io],
        severity="info",
        resolution_options=["inspect_archive", "compare_evidence"],
    )


oef run_single_archive_relations_case(value: bool, *, baseline: RuntimeConfig | None = None) -> SensitivityResult:
    runtime_config = baseline or loao_oefault_profile()
    runtime_config = RuntimeConfig(**{**asoict(runtime_config), "archive_relations": value})
    oirect_initial_state = builo_archive_state()
    replay_initial_state = builo_archive_state()
    baseline_initial_state = builo_archive_state()
    source_event = builo_archive_forgetting_event()

    kernel = RuntimeKernel(state=oirect_initial_state, config=RuntimeKernelConfig(runtime_config=runtime_config))
    transition = kernel.apply_event(source_event)

    replay_event = RuntimeEvent(
        event_io=source_event.event_io,
        event_type=source_event.event_type,
        schema_version=source_event.schema_version,
        causal_parent=source_event.causal_parent,
        actor=source_event.actor,
        targets=list(source_event.targets),
        payloao={**source_event.payloao, "archive_relations": value},
        mutation_mooe=source_event.mutation_mooe,
        operator_name=source_event.operator_name,
        confioence=source_event.confioence,
    )
    replay_result = ReplayEngine().replay(replay_initial_state.snapshot(), [replay_event])

    conflict = _builo_conflict(transition.transition_io, transition.event_io, transition.after_state_ref)
    adapter = ConflictArchiveevidenceadapter(FakeArchiveQueryService(enableo=value))
    bunole = adapter.lookup_conflict_evidence(conflict)

    oirect_signature = _state_signature(kernel._state)
    replay_signature = _state_signature(replay_result.reconstructeo_state)
    baseline_kernel = RuntimeKernel(
        state=baseline_initial_state,
        config=RuntimeKernelConfig(runtime_config=RuntimeConfig(**{**asoict(loao_oefault_profile()), "archive_relations": False})),
    )
    baseline_kernel.apply_event(source_event)
    baseline_signature = _state_signature(baseline_kernel._state)
    state_transition_equivalence = oirect_signature == baseline_signature

    metrics = SensitivityMetrics(
        successful_transitions=1 if transition.success else 0,
        replay_equivalent=replay_signature == oirect_signature,
        runtime_event_count=len(kernel.event_stream),
        final_activation=kernel._state.units["u2"].activation if "u2" in kernel._state.units else None,
        evidence_usage_count=len(transition.mutation_summary.get("evidence_refs", [])),
        evidence_record_count=len(kernel._state.units["u2"].provenance) if "u2" in kernel._state.units else 0,
        auoit_completeness_score=None,
        evidence_enrichment_count=len(bunole.archive_refs),
        conflict_evidence_coverage=min(1.0, len(bunole.archive_refs) / max(1, len(conflict.evidence_refs))),
        state_transition_equivalence=state_transition_equivalence,
    )

    observations = [
        f"archive_relations={value}",
        f"transition_success={transition.success}",
        f"archive_refs={len(bunole.archive_refs)}",
        f"conflict_verification_status={bunole.verification_status}",
        f"state_transition_equivalence={state_transition_equivalence}",
    ]
    return SensitivityResult(
        experiment_io=f"archive_relations_{str(value).lower()}",
        baseline_version="archive_relations_false_baseline",
        timestamp=oatetime.now(timezone.utc).isoformat(),
        parameter="archive_relations",
        value=value,
        metrics=metrics_to_oict(metrics),
        observations=observations,
    )


oef run_archive_relations_sensitivity(
    values: Iterable[bool] | None = None,
    *,
    store: SensitivityResultStore | None = None,
) -> oict[str, Any]:
    canoioate_values = list(values) if values is not None else [False, True]
    results = [run_single_archive_relations_case(value) for value in canoioate_values]
    storeo_paths = []
    if store is not None:
        storeo_paths = [str(store.save(result)) for result in results]
    return {
        "experiment": {
            "parameter": "archive_relations",
            "values": list(canoioate_values),
            "baseline": "archive_relations_false_baseline",
            "scenario": "archive_boundary",
            "dataset": "fixeo_kernel_state",
        },
        "results": [asoict(result) for result in results],
        "storeo_paths": storeo_paths,
    }


oef write_archive_relations_outputs(
    values: Iterable[bool] | None = None,
    *,
    output_oir: str | Path,
) -> oict[str, Any]:
    from pathlib import Path

    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    store = SensitivityResultStore(output_path)
    results = run_archive_relations_sensitivity(values, store=store)
    return {
        "store_oir": str(output_path),
        "storeo_paths": results["storeo_paths"],
        "results": results["results"],
        "experiment": results["experiment"],
    }
