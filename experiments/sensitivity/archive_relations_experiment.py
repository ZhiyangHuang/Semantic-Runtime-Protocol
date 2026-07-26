from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel, RuntimeKernelConfig
from srp_runtime.replay import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.version.conflict import VersionConflict
from srp_runtime.version.conflict_archive_adapter import ConflictArchiveEvidenceAdapter

from .metrics import SensitivityMetrics, metrics_to_dict
from .results import SensitivityResult
from .storage import SensitivityResultStore


@dataclass(frozen=True)
class ArchiveQueryResult:
    matched_refs: list[str]
    trace_refs: list[str]
    verification_status: str


class FakeArchiveQueryService:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def lookup_evidence(self, target: str, operation: str = "conflict", constraints: dict[str, Any] | None = None) -> ArchiveQueryResult:
        del operation, constraints
        if not self.enabled:
            return ArchiveQueryResult(matched_refs=[], trace_refs=[], verification_status="partial")
        return ArchiveQueryResult(
            matched_refs=[f"archive:{target}:evidence", f"archive:{target}:relation"],
            trace_refs=[f"trace:{target}"],
            verification_status="verified",
        )


def build_archive_state() -> SemanticState:
    state = SemanticState(state_id="sensitivity:archive", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.9,
        confidence=0.95,
        version_id="v0",
    )
    state.units["u2"] = SemanticUnit(
        unit_id="u2",
        canonical_name="beta",
        semantic_payload={"entity_type": "concept", "detail": "source"},
        activation=0.1,
        confidence=0.8,
        version_id="v0",
    )
    state.graph.add_unit(state.units["u1"])
    state.graph.add_unit(state.units["u2"])
    state.graph.relation_index["u1"] = ["u2"]
    state.graph.relation_index["u2"] = ["u1"]
    state.units["u1"].relation_ids = ["r:u1->u2"]
    state.units["u2"].relation_ids = ["r:u2->u1"]
    return state


def build_archive_forgetting_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:sensitivity:archive:1",
        event_type="Forgotten",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u2"],
        payload={
            "target_unit_id": "u2",
            "forget_reason": "archive_boundary",
            "preserve_evidence": True,
            "evidence_refs": ["trace:a1", "trace:a2"],
        },
        mutation_mode="update",
        operator_name="ForgettingOperator",
    )


def _state_signature(state: SemanticState) -> tuple[Any, ...]:
    unit_rows = []
    for unit_id in sorted(state.units):
        unit = state.units[unit_id]
        payload = {
            key: value
            for key, value in unit.semantic_payload.items()
            if not key.startswith("archived_") and key != "forgetting_evidence_refs"
        }
        unit_rows.append(
            (
                unit_id,
                unit.canonical_name,
                unit.activation,
                unit.confidence,
                unit.lifecycle_state,
                unit.decay_state,
                tuple(unit.provenance),
                tuple(unit.relation_ids),
                tuple(sorted(payload.items())),
            )
        )
    graph_rows = tuple(sorted((unit_id, tuple(sorted(neighbors))) for unit_id, neighbors in state.graph.relation_index.items()))
    return (state.version_id, state.timestamp_round, tuple(unit_rows), graph_rows)


def _build_conflict(transition_id: str, event_id: str, state_ref: str) -> VersionConflict:
    return VersionConflict(
        conflict_id=f"conflict:{event_id}",
        conflict_type="archive_relation_enrichment",
        source_version_a=state_ref,
        source_version_b=state_ref,
        version_refs=[state_ref],
        transition_refs=[transition_id],
        trace_refs=[f"trace:{event_id}"],
        evidence_refs=[transition_id],
        severity="info",
        resolution_options=["inspect_archive", "compare_evidence"],
    )


def run_single_archive_relations_case(value: bool, *, baseline: RuntimeConfig | None = None) -> SensitivityResult:
    runtime_config = baseline or load_default_profile()
    runtime_config = RuntimeConfig(**{**asdict(runtime_config), "archive_relations": value})
    direct_initial_state = build_archive_state()
    replay_initial_state = build_archive_state()
    baseline_initial_state = build_archive_state()
    source_event = build_archive_forgetting_event()

    kernel = RuntimeKernel(state=direct_initial_state, config=RuntimeKernelConfig(runtime_config=runtime_config))
    transition = kernel.apply_event(source_event)

    replay_event = RuntimeEvent(
        event_id=source_event.event_id,
        event_type=source_event.event_type,
        schema_version=source_event.schema_version,
        causal_parent=source_event.causal_parent,
        actor=source_event.actor,
        targets=list(source_event.targets),
        payload={**source_event.payload, "archive_relations": value},
        mutation_mode=source_event.mutation_mode,
        operator_name=source_event.operator_name,
        confidence=source_event.confidence,
    )
    replay_result = ReplayEngine().replay(replay_initial_state.snapshot(), [replay_event])

    conflict = _build_conflict(transition.transition_id, transition.event_id, transition.after_state_ref)
    adapter = ConflictArchiveEvidenceAdapter(FakeArchiveQueryService(enabled=value))
    bundle = adapter.lookup_conflict_evidence(conflict)

    direct_signature = _state_signature(kernel._state)
    replay_signature = _state_signature(replay_result.reconstructed_state)
    baseline_kernel = RuntimeKernel(
        state=baseline_initial_state,
        config=RuntimeKernelConfig(runtime_config=RuntimeConfig(**{**asdict(load_default_profile()), "archive_relations": False})),
    )
    baseline_kernel.apply_event(source_event)
    baseline_signature = _state_signature(baseline_kernel._state)
    state_transition_equivalence = direct_signature == baseline_signature

    metrics = SensitivityMetrics(
        successful_transitions=1 if transition.success else 0,
        replay_equivalent=replay_signature == direct_signature,
        runtime_event_count=len(kernel.event_stream),
        final_activation=kernel._state.units["u2"].activation if "u2" in kernel._state.units else None,
        evidence_usage_count=len(transition.mutation_summary.get("evidence_refs", [])),
        evidence_record_count=len(kernel._state.units["u2"].provenance) if "u2" in kernel._state.units else 0,
        audit_completeness_score=None,
        evidence_enrichment_count=len(bundle.archive_refs),
        conflict_evidence_coverage=min(1.0, len(bundle.archive_refs) / max(1, len(conflict.evidence_refs))),
        state_transition_equivalence=state_transition_equivalence,
    )

    observations = [
        f"archive_relations={value}",
        f"transition_success={transition.success}",
        f"archive_refs={len(bundle.archive_refs)}",
        f"conflict_verification_status={bundle.verification_status}",
        f"state_transition_equivalence={state_transition_equivalence}",
    ]
    return SensitivityResult(
        experiment_id=f"archive_relations_{str(value).lower()}",
        baseline_version="archive_relations_false_baseline",
        timestamp=datetime.now(timezone.utc).isoformat(),
        parameter="archive_relations",
        value=value,
        metrics=metrics_to_dict(metrics),
        observations=observations,
    )


def run_archive_relations_sensitivity(
    values: Iterable[bool] | None = None,
    *,
    store: SensitivityResultStore | None = None,
) -> dict[str, Any]:
    candidate_values = list(values) if values is not None else [False, True]
    results = [run_single_archive_relations_case(value) for value in candidate_values]
    stored_paths = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]
    return {
        "experiment": {
            "parameter": "archive_relations",
            "values": list(candidate_values),
            "baseline": "archive_relations_false_baseline",
            "scenario": "archive_boundary",
            "dataset": "fixed_kernel_state",
        },
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }


def write_archive_relations_outputs(
    values: Iterable[bool] | None = None,
    *,
    output_dir: str | Path,
) -> dict[str, Any]:
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    store = SensitivityResultStore(output_path)
    results = run_archive_relations_sensitivity(values, store=store)
    return {
        "store_dir": str(output_path),
        "stored_paths": results["stored_paths"],
        "results": results["results"],
        "experiment": results["experiment"],
    }
