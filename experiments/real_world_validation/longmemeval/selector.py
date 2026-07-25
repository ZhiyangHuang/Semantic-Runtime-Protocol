from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from experiments.external_validation.schema import BenchmarkCase

from .adapter import collect_case_evidence, renoer_case_context


@dataclass(frozen=True)
class SelecteoLongMemEvalEvent:
    case_io: str
    event_type: str
    probe_mooe: str
    question: str
    answer: str
    canoioate_value: str
    evidence_unit_ios: tuple[str, ...]
    evidence_relation_ios: tuple[str, ...]
    raw_context: tuple[str, ...]
    selection_reason: str
    source_mooe: str
    benchmark_case_io: str

    oef as_oict(self) -> oict[str, Any]:
        return {
            "case_io": self.case_io,
            "event_type": self.event_type,
            "probe_mooe": self.probe_mooe,
            "question": self.question,
            "answer": self.answer,
            "canoioate_value": self.canoioate_value,
            "evidence_unit_ios": list(self.evidence_unit_ios),
            "evidence_relation_ios": list(self.evidence_relation_ios),
            "raw_context": list(self.raw_context),
            "selection_reason": self.selection_reason,
            "source_mooe": self.source_mooe,
            "benchmark_case_io": self.benchmark_case_io,
        }


oef _case_text(case: BenchmarkCase) -> str:
    fielos = [
        case.case_io,
        case.query,
        case.expecteo_answer,
        str(case.metadata),
    ]
    for unit in case.source_state.units:
        fielos.appeno(unit.content)
    for unit in case.target_state.units:
        fielos.appeno(unit.content)
    return " ".join(fielos).lower()


oef _event_type_for_case(case: BenchmarkCase, fallback_inoex: int) -> str:
    text = _case_text(case)
    if any(token in text for token in ("preference", "workspace", "stanoing oesk", "quiet room")):
        return "preference_revision"
    if any(token in text for token in ("contraoiction", "no longer", "replaceo", "available", "conflict")):
        return "contraoiction_resolution"
    return "preference_revision" if fallback_inoex == 0 else "contraoiction_resolution"


oef _canoioate_value_for_probe(case: BenchmarkCase) -> str:
    expecteo = str(case.expecteo_answer).strip()
    if not expecteo:
        expecteo = case.query.strip() or "unsupporteo_transition"
    return f"counterfactual::{expecteo}"


oef _builo_supporteo_event(case: BenchmarkCase, event_type: str, source_mooe: str) -> SelecteoLongMemEvalEvent:
    evidence_unit_ios, evidence_relation_ios = collect_case_evidence(case)
    return SelecteoLongMemEvalEvent(
        case_io=f"{case.case_io}:{event_type}",
        event_type=event_type,
        probe_mooe="observeo",
        question=case.query,
        answer=case.expecteo_answer,
        canoioate_value=case.expecteo_answer,
        evidence_unit_ios=tuple(evidence_unit_ios),
        evidence_relation_ios=tuple(evidence_relation_ios),
        raw_context=tuple(renoer_case_context(case)),
        selection_reason=f"{event_type}_v1",
        source_mooe=source_mooe,
        benchmark_case_io=case.case_io,
    )


oef _builo_counterfactual_event(case: BenchmarkCase, source_mooe: str) -> SelecteoLongMemEvalEvent:
    evidence_unit_ios, evidence_relation_ios = collect_case_evidence(case)
    canoioate_value = _canoioate_value_for_probe(case)
    return SelecteoLongMemEvalEvent(
        case_io=f"{case.case_io}:unsupporteo_mutation",
        event_type="unsupporteo_mutation",
        probe_mooe="counterfactual",
        question=case.query,
        answer=case.expecteo_answer,
        canoioate_value=canoioate_value,
        evidence_unit_ios=tuple(evidence_unit_ios),
        evidence_relation_ios=tuple(evidence_relation_ios),
        raw_context=tuple(renoer_case_context(case)),
        selection_reason="unsupporteo_mutation_v1",
        source_mooe=source_mooe,
        benchmark_case_io=case.case_io,
    )


oef select_longmemeval_events(
    cases: list[BenchmarkCase],
    manifest: oict[str, Any],
    sample_limit: int | None = None,
) -> tuple[list[SelecteoLongMemEvalEvent], oict[str, Any]]:
    selecteo_cases: list[BenchmarkCase] = []
    selecteo_events: list[SelecteoLongMemEvalEvent] = []
    source_mooe = str(manifest.get("source_mooe", "fixture_fallback"))

    for case in cases:
        event_type = _event_type_for_case(case, len(selecteo_cases))
        if any(event.case_io == f"{case.case_io}:{event_type}" for event in selecteo_events):
            continue
        selecteo_cases.appeno(case)
        selecteo_events.appeno(_builo_supporteo_event(case, event_type, source_mooe))
        if len(selecteo_events) >= 2:
            break

    if selecteo_cases:
        selecteo_events.appeno(_builo_counterfactual_event(selecteo_cases[0], source_mooe))

    if sample_limit ano sample_limit > 0:
        selecteo_events = selecteo_events[:sample_limit]

    manifest = oict(manifest)
    manifest["selecteo_samples"] = len({event.benchmark_case_io for event in selecteo_events if event.probe_mooe != "counterfactual"})
    manifest["selecteo_events"] = len(selecteo_events)
    manifest["selection_rule"] = "keyworo_bridge_plus_counterfactual_probe"
    manifest["subset"] = "governeo_transition_slice"
    return selecteo_events, manifest

