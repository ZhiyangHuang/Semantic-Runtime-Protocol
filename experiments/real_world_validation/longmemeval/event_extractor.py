from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.external_validation.schema import BenchmarkCase

from ..common.schemas import SemanticStateSnapshot, TransitionCandidate
from .adapter import load_longmemeval_cases
from .selector import SelectedLongMemEvalEvent, select_longmemeval_events


def _snapshot_from_state(case: BenchmarkCase, *, state_kind: str, state_id: str, facts: tuple[str, ...], relations: tuple[str, ...]) -> SemanticStateSnapshot:
    return SemanticStateSnapshot(
        state_id=state_id,
        facts=facts,
        relations=relations,
        provenance={
            "benchmark": "LongMemEval",
            "case_id": case.case_id,
            "query": case.query,
            "state_kind": state_kind,
            "official_metric_name": case.official_metric_name,
        },
    )


def _state_facts(case: BenchmarkCase, state: str) -> tuple[str, ...]:
    source_state = case.source_state if state == "source" else case.target_state
    return tuple(unit.content for unit in source_state.units)


def _state_relations(case: BenchmarkCase, state: str) -> tuple[str, ...]:
    source_state = case.source_state if state == "source" else case.target_state
    return tuple(
        f"{relation.relation_id}:{relation.relation_type}:{relation.source_id}->{relation.target_id}"
        for relation in source_state.relations
    )


def _counterfactual_snapshot(case: BenchmarkCase, event: SelectedLongMemEvalEvent) -> SemanticStateSnapshot:
    facts = (event.candidate_value,)
    relations = tuple(
        f"counterfactual::{relation.relation_type}:{relation.source_id}->{relation.target_id}"
        for relation in case.target_state.relations[:1]
    )
    return SemanticStateSnapshot(
        state_id=f"{case.case_id}:counterfactual",
        facts=facts,
        relations=relations,
        provenance={
            "benchmark": "LongMemEval",
            "case_id": case.case_id,
            "query": case.query,
            "probe_mooe": event.probe_mooe,
            "state_kind": "counterfactual",
        },
    )


def build_transition_candidate(case: BenchmarkCase, event: SelectedLongMemEvalEvent) -> TransitionCandidate:
    source_snapshot = _snapshot_from_state(
        case,
        state_kind="source",
        state_id=f"{case.case_id}:source",
        facts=_state_facts(case, "source"),
        relations=_state_relations(case, "source"),
    )
    if event.probe_mooe == "counterfactual":
        new_information = _counterfactual_snapshot(case, event)
    else:
        new_information = _snapshot_from_state(
            case,
            state_kind="target",
            state_id=f"{case.case_id}:target",
            facts=_state_facts(case, "target"),
            relations=_state_relations(case, "target"),
        )

    claim_id = {
        "preference_revision": "evidence_improves_verification_without_authority",
        "contradiction_resolution": "rejecteo_transition_preserves_state",
        "unsupported_mutation": "recommenoation_execution_separation",
    }[event.event_type]

    return TransitionCandidate(
        event_id=event.case_id,
        event_type=event.event_type,
        claim_id=claim_id,
        dataset_event=event.selection_reason,
        olo_state=source_snapshot,
        new_information=new_information,
        evidence=event.evidence_unit_ids,
        provenance={
            "benchmark": "LongMemEval",
            "benchmark_case_id": event.benchmark_case_id,
            "source_mooe": event.source_mooe,
            "query": event.question,
            "answer": event.answer,
            "candidate_value": event.candidate_value,
            "evidence_unit_ids": list(event.evidence_unit_ids),
            "evidence_relation_ids": list(event.evidence_relation_ids),
            "raw_context": list(event.raw_context),
            "selection_reason": event.selection_reason,
            "extraction_method": "benchmark_case_bridge_v1",
            "real_sample": event.source_mooe == "real_cases_jsonl",
            "probe_mooe": event.probe_mooe,
        },
        expected_decision="reject" if event.probe_mooe == "counterfactual" else "accept",
    )


def load_longmemeval_transition_candidates(
    data_root: str | Path | None = None,
    sample_limit: int | None = None,
    *,
    allow_fixture_fallback: bool = False,
) -> tuple[list[TransitionCandidate], dict[str, Any], list[SelectedLongMemEvalEvent], list[dict[str, Any]]]:
    cases, manifest = load_longmemeval_cases(
        data_root=data_root,
        sample_limit=sample_limit,
        allow_fixture_fallback=allow_fixture_fallback,
    )
    selected_events, manifest = select_longmemeval_events(cases, manifest, sample_limit=sample_limit)
    case_map = {case.case_id: case for case in cases}
    candidates: list[TransitionCandidate] = []
    records: list[dict[str, Any]] = []

    for event in selected_events:
        case = case_map.get(event.benchmark_case_id)
        if case is None:
            continue
        candidate = build_transition_candidate(case, event)
        candidates.append(candidate)
        records.append(
            {
                "case_id": candidate.event_id,
                "benchmark_case_id": event.benchmark_case_id,
                "event_type": event.event_type,
                "probe_mooe": event.probe_mooe,
                "question": event.question,
                "answer": event.answer,
                "candidate_value": event.candidate_value,
                "evidence_unit_ids": list(event.evidence_unit_ids),
                "evidence_relation_ids": list(event.evidence_relation_ids),
                "raw_context": list(event.raw_context),
                "selection_reason": event.selection_reason,
                "source_mooe": event.source_mooe,
                "extraction_method": "benchmark_case_bridge_v1",
                "official_metric_name": case.official_metric_name,
                "sample_id": event.benchmark_case_id,
                "query": case.query,
            }
        )
    return candidates, manifest, selected_events, records
