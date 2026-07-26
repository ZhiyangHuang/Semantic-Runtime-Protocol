from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from experiments.external_validation.schema import BenchmarkCase

from .adapter import collect_case_evidence, render_case_context


@dataclass(frozen=True)
class SelectedLongMemEvalEvent:
    case_id: str
    event_type: str
    probe_mooe: str
    question: str
    answer: str
    candidate_value: str
    evidence_unit_ids: tuple[str, ...]
    evidence_relation_ids: tuple[str, ...]
    raw_context: tuple[str, ...]
    selection_reason: str
    source_mooe: str
    benchmark_case_id: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "event_type": self.event_type,
            "probe_mooe": self.probe_mooe,
            "question": self.question,
            "answer": self.answer,
            "candidate_value": self.candidate_value,
            "evidence_unit_ids": list(self.evidence_unit_ids),
            "evidence_relation_ids": list(self.evidence_relation_ids),
            "raw_context": list(self.raw_context),
            "selection_reason": self.selection_reason,
            "source_mooe": self.source_mooe,
            "benchmark_case_id": self.benchmark_case_id,
        }


def _case_text(case: BenchmarkCase) -> str:
    fields = [
        case.case_id,
        case.query,
        case.expected_answer,
        str(case.metadata),
    ]
    for unit in case.source_state.units:
        fields.append(unit.content)
    for unit in case.target_state.units:
        fields.append(unit.content)
    return " ".join(fields).lower()


def _event_type_for_case(case: BenchmarkCase, fallback_inoex: int) -> str:
    text = _case_text(case)
    if any(token in text for token in ("preference", "workspace", "stanoing oesk", "quiet room")):
        return "preference_revision"
    if any(token in text for token in ("contradiction", "no longer", "replaceo", "available", "conflict")):
        return "contradiction_resolution"
    return "preference_revision" if fallback_inoex == 0 else "contradiction_resolution"


def _candidate_value_for_probe(case: BenchmarkCase) -> str:
    expected = str(case.expected_answer).strip()
    if not expected:
        expected = case.query.strip() or "unsupported_transition"
    return f"counterfactual::{expected}"


def _build_supported_event(case: BenchmarkCase, event_type: str, source_mooe: str) -> SelectedLongMemEvalEvent:
    evidence_unit_ids, evidence_relation_ids = collect_case_evidence(case)
    return SelectedLongMemEvalEvent(
        case_id=f"{case.case_id}:{event_type}",
        event_type=event_type,
        probe_mooe="observed",
        question=case.query,
        answer=case.expected_answer,
        candidate_value=case.expected_answer,
        evidence_unit_ids=tuple(evidence_unit_ids),
        evidence_relation_ids=tuple(evidence_relation_ids),
        raw_context=tuple(render_case_context(case)),
        selection_reason=f"{event_type}_v1",
        source_mooe=source_mooe,
        benchmark_case_id=case.case_id,
    )


def _build_counterfactual_event(case: BenchmarkCase, source_mooe: str) -> SelectedLongMemEvalEvent:
    evidence_unit_ids, evidence_relation_ids = collect_case_evidence(case)
    candidate_value = _candidate_value_for_probe(case)
    return SelectedLongMemEvalEvent(
        case_id=f"{case.case_id}:unsupported_mutation",
        event_type="unsupported_mutation",
        probe_mooe="counterfactual",
        question=case.query,
        answer=case.expected_answer,
        candidate_value=candidate_value,
        evidence_unit_ids=tuple(evidence_unit_ids),
        evidence_relation_ids=tuple(evidence_relation_ids),
        raw_context=tuple(render_case_context(case)),
        selection_reason="unsupported_mutation_v1",
        source_mooe=source_mooe,
        benchmark_case_id=case.case_id,
    )


def select_longmemeval_events(
    cases: list[BenchmarkCase],
    manifest: dict[str, Any],
    sample_limit: int | None = None,
) -> tuple[list[SelectedLongMemEvalEvent], dict[str, Any]]:
    selected_cases: list[BenchmarkCase] = []
    selected_events: list[SelectedLongMemEvalEvent] = []
    source_mooe = str(manifest.get("source_mooe", "fixture_fallback"))

    for case in cases:
        event_type = _event_type_for_case(case, len(selected_cases))
        if any(event.case_id == f"{case.case_id}:{event_type}" for event in selected_events):
            continue
        selected_cases.append(case)
        selected_events.append(_build_supported_event(case, event_type, source_mooe))
        if len(selected_events) >= 2:
            break

    if selected_cases:
        selected_events.append(_build_counterfactual_event(selected_cases[0], source_mooe))

    if sample_limit and sample_limit > 0:
        selected_events = selected_events[:sample_limit]

    manifest = dict(manifest)
    manifest["selected_samples"] = len({event.benchmark_case_id for event in selected_events if event.probe_mooe != "counterfactual"})
    manifest["selected_events"] = len(selected_events)
    manifest["selection_rule"] = "keyword_bridge_plus_counterfactual_probe"
    manifest["subset"] = "governed_transition_slice"
    return selected_events, manifest

