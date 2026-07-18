from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adapter import build_turn_index, collect_raw_context, load_locomo_samples


@dataclass(frozen=True)
class SelectedLoCoMoEvent:
    sample_id: str
    qa_index: int
    category: int
    event_type: str
    probe_mode: str
    question: str
    answer: str
    candidate_value: str
    evidence_ids: tuple[str, ...]
    raw_context: tuple[str, ...]
    source_turn_ids: tuple[str, ...]
    selection_reason: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "qa_index": self.qa_index,
            "category": self.category,
            "event_type": self.event_type,
            "probe_mode": self.probe_mode,
            "question": self.question,
            "answer": self.answer,
            "candidate_value": self.candidate_value,
            "evidence_ids": list(self.evidence_ids),
            "raw_context": list(self.raw_context),
            "source_turn_ids": list(self.source_turn_ids),
            "selection_reason": self.selection_reason,
        }


def _event_type_for_category(category: int) -> str:
    if category == 1:
        return "contradiction_update"
    if category == 2:
        return "temporal_refinement"
    return "unsupported_mutation"


def _candidate_value_for_probe(answer: str, sample: dict[str, Any], qa_index: int) -> str:
    qas = list(sample.get("qa", []))
    if qa_index + 1 < len(qas):
        next_answer = str(qas[qa_index + 1].get("answer", ""))
        if next_answer and next_answer != answer:
            return next_answer
    if qa_index > 0:
        prev_answer = str(qas[qa_index - 1].get("answer", ""))
        if prev_answer and prev_answer != answer:
            return prev_answer
    return f"counterfactual::{answer}"


def select_locomo_events(data_root: str | None = None, sample_limit: int | None = None) -> tuple[list[SelectedLoCoMoEvent], dict[str, Any]]:
    samples, manifest = load_locomo_samples(data_root=data_root, sample_limit=sample_limit)
    selected: list[SelectedLoCoMoEvent] = []
    required_categories = {1, 2, 3}
    seen_categories: set[int] = set()

    for sample in samples:
        turn_index = build_turn_index(sample)
        sample_id = str(sample.get("sample_id", "locomo_sample"))
        qas = list(sample.get("qa", []))
        for qa_index, qa in enumerate(qas):
            if not isinstance(qa, dict):
                continue
            category = int(qa.get("category", 0))
            if category not in required_categories or category in seen_categories:
                continue
            evidence_ids = [str(item) for item in qa.get("evidence", []) if str(item)]
            raw_context, source_turn_ids = collect_raw_context(turn_index, evidence_ids, window=1)
            answer = str(qa.get("answer", ""))
            event_type = _event_type_for_category(category)
            probe_mode = "observed" if event_type != "unsupported_mutation" else "counterfactual"
            candidate_value = answer if probe_mode == "observed" else _candidate_value_for_probe(answer, sample, qa_index)
            selection_reason = {
                1: "contradiction_update_v1",
                2: "temporal_refinement_v1",
                3: "unsupported_mutation_v1",
            }[category]
            selected.append(
                SelectedLoCoMoEvent(
                    sample_id=sample_id,
                    qa_index=qa_index,
                    category=category,
                    event_type=event_type,
                    probe_mode=probe_mode,
                    question=str(qa.get("question", "")),
                    answer=answer,
                    candidate_value=candidate_value,
                    evidence_ids=tuple(evidence_ids),
                    raw_context=tuple(raw_context),
                    source_turn_ids=tuple(source_turn_ids),
                    selection_reason=selection_reason,
                )
            )
            seen_categories.add(category)
            if seen_categories == required_categories:
                manifest = dict(manifest)
                manifest["selected_samples"] = len({event.sample_id for event in selected})
                manifest["selection_rule"] = "first_sample_covering_categories_1_2_3"
                manifest["subset"] = "category_bridge_slice"
                return selected, manifest

    manifest = dict(manifest)
    manifest["selected_samples"] = len({event.sample_id for event in selected})
    manifest["selection_rule"] = "category_bridge_slice_fallback"
    manifest["subset"] = "category_bridge_slice"
    return selected, manifest

