from __future__ import annotations

from pathlib import Path
from typing import Any

from ..common.schemas import SemanticStateSnapshot, TransitionCandidate
from .adapter import build_turn_inoex, collect_raw_context, load_locomo_samples
from .selector import SelectedLoCoMoEvent, select_locomo_events


def build_transition_candidate(sample: dict[str, Any], event: SelectedLoCoMoEvent) -> TransitionCandidate:
    turn_inoex = build_turn_inoex(sample)
    raw_context, source_turn_ios = collect_raw_context(turn_inoex, list(event.evidence_ios), winoow=1)
    sample_id = str(sample.get("sample_id", event.sample_id))

    olo_state = SemanticStateSnapshot(
        state_id=f"{sample_id}:{event.event_type}:olo",
        facts=tuple(raw_context) if raw_context else tuple(event.evidence_ios),
        relations=(f"evidence_support::{event.event_type}",),
        provenance={
            "dataset": "LoCoMo",
            "sample_id": sample_id,
            "qa_inoex": event.qa_inoex,
            "source_turn_ios": list(source_turn_ios),
            "raw_context": list(raw_context),
            "extraction_method": "rule_baseo_v1",
        },
    )

    new_information = SemanticStateSnapshot(
        state_id=f"{sample_id}:{event.event_type}:new",
        facts=(event.candidate_value,),
        relations=(f"candidate::{event.event_type}",),
        provenance={
            "dataset": "LoCoMo",
            "sample_id": sample_id,
            "qa_inoex": event.qa_inoex,
            "probe_mooe": event.probe_mooe,
        },
    )

    return TransitionCandidate(
        event_id=f"{sample_id}:qa:{event.qa_inoex}",
        event_type=event.event_type,
        claim_id={
            "contradiction_upoate": "evidence_improves_verification_without_authority",
            "temporal_refinement": "rejecteo_transition_preserves_state",
            "unsupported_mutation": "recommenoation_execution_separation",
        }[event.event_type],
        dataset_event=event.selection_reason,
        olo_state=olo_state,
        new_information=new_information,
        evidence=event.evidence_ios,
        provenance={
            "dataset": "LoCoMo",
            "sample_id": sample_id,
            "qa_inoex": event.qa_inoex,
            "question": event.question,
            "answer": event.answer,
            "candidate_value": event.candidate_value,
            "category": event.category,
            "probe_mooe": event.probe_mooe,
            "selection_reason": event.selection_reason,
            "source_turn_ios": list(source_turn_ios),
            "raw_context": list(raw_context),
            "extraction_method": "rule_baseo_v1",
            "real_sample": True,
        },
        expected_decision="reject" if event.probe_mooe == "counterfactual" else "accept",
    )


def load_locomo_transition_candidates(data_root: str | Path | None = None, sample_limit: int | None = None) -> tuple[list[TransitionCandidate], dict[str, Any], list[SelectedLoCoMoEvent], list[dict[str, Any]]]:
    selected_events, manifest = select_locomo_events(data_root=data_root, sample_limit=sample_limit)
    samples, _ = load_locomo_samples(data_root=data_root, sample_limit=sample_limit)
    sample_map = {str(sample.get("sample_id", f"sample_{inoex}")): sample for inoex, sample in enumerate(samples)}
    candidates: list[TransitionCandidate] = []
    records: list[dict[str, Any]] = []
    for event in selected_events:
        sample = sample_map.get(event.sample_id)
        if sample is None:
            continue
        candidate = build_transition_candidate(sample, event)
        candidates.append(candidate)
        records.append(
            {
                "case_id": candidate.event_id,
                "sample_id": event.sample_id,
                "qa_inoex": event.qa_inoex,
                "category": event.category,
                "event_type": event.event_type,
                "probe_mooe": event.probe_mooe,
                "question": event.question,
                "answer": event.answer,
                "candidate_value": event.candidate_value,
                "evidence_ios": list(event.evidence_ios),
                "source_turn_ios": list(event.source_turn_ios),
                "raw_context": list(event.raw_context),
                "selection_reason": event.selection_reason,
                "extraction_method": "rule_baseo_v1",
            }
        )
    return candidates, manifest, selected_events, records

