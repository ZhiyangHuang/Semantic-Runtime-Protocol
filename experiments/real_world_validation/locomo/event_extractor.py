from __future__ import annotations

from pathlib import Path
from typing import Any

from ..common.schemas import SemanticStateSnapshot, TransitionCandidate
from .adapter import build_turn_index, collect_raw_context, load_locomo_samples
from .selector import SelectedLoCoMoEvent, select_locomo_events


def build_transition_candidate(sample: dict[str, Any], event: SelectedLoCoMoEvent) -> TransitionCandidate:
    turn_index = build_turn_index(sample)
    raw_context, source_turn_ids = collect_raw_context(turn_index, list(event.evidence_ids), window=1)
    sample_id = str(sample.get("sample_id", event.sample_id))

    old_state = SemanticStateSnapshot(
        state_id=f"{sample_id}:{event.event_type}:old",
        facts=tuple(raw_context) if raw_context else tuple(event.evidence_ids),
        relations=(f"evidence_support::{event.event_type}",),
        provenance={
            "dataset": "LoCoMo",
            "sample_id": sample_id,
            "qa_index": event.qa_index,
            "source_turn_ids": list(source_turn_ids),
            "raw_context": list(raw_context),
            "extraction_method": "rule_based_v1",
        },
    )

    new_information = SemanticStateSnapshot(
        state_id=f"{sample_id}:{event.event_type}:new",
        facts=(event.candidate_value,),
        relations=(f"candidate::{event.event_type}",),
        provenance={
            "dataset": "LoCoMo",
            "sample_id": sample_id,
            "qa_index": event.qa_index,
            "probe_mode": event.probe_mode,
        },
    )

    return TransitionCandidate(
        event_id=f"{sample_id}:qa:{event.qa_index}",
        event_type=event.event_type,
        claim_id={
            "contradiction_update": "evidence_improves_verification_without_authority",
            "temporal_refinement": "rejected_transition_preserves_state",
            "unsupported_mutation": "recommendation_execution_separation",
        }[event.event_type],
        dataset_event=event.selection_reason,
        old_state=old_state,
        new_information=new_information,
        evidence=event.evidence_ids,
        provenance={
            "dataset": "LoCoMo",
            "sample_id": sample_id,
            "qa_index": event.qa_index,
            "question": event.question,
            "answer": event.answer,
            "candidate_value": event.candidate_value,
            "category": event.category,
            "probe_mode": event.probe_mode,
            "selection_reason": event.selection_reason,
            "source_turn_ids": list(source_turn_ids),
            "raw_context": list(raw_context),
            "extraction_method": "rule_based_v1",
            "real_sample": True,
        },
        expected_decision="reject" if event.probe_mode == "counterfactual" else "accept",
    )


def load_locomo_transition_candidates(data_root: str | Path | None = None, sample_limit: int | None = None) -> tuple[list[TransitionCandidate], dict[str, Any], list[SelectedLoCoMoEvent], list[dict[str, Any]]]:
    selected_events, manifest = select_locomo_events(data_root=data_root, sample_limit=sample_limit)
    samples, _ = load_locomo_samples(data_root=data_root, sample_limit=sample_limit)
    sample_map = {str(sample.get("sample_id", f"sample_{index}")): sample for index, sample in enumerate(samples)}
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
                "qa_index": event.qa_index,
                "category": event.category,
                "event_type": event.event_type,
                "probe_mode": event.probe_mode,
                "question": event.question,
                "answer": event.answer,
                "candidate_value": event.candidate_value,
                "evidence_ids": list(event.evidence_ids),
                "source_turn_ids": list(event.source_turn_ids),
                "raw_context": list(event.raw_context),
                "selection_reason": event.selection_reason,
                "extraction_method": "rule_based_v1",
            }
        )
    return candidates, manifest, selected_events, records

