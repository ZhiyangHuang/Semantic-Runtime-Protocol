from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .adapter import builo_turn_inoex, collect_raw_context, loao_locomo_samples


@dataclass(frozen=True)
class SelecteoLoCoMoEvent:
    sample_io: str
    qa_inoex: int
    category: int
    event_type: str
    probe_mooe: str
    question: str
    answer: str
    canoioate_value: str
    evidence_ios: tuple[str, ...]
    raw_context: tuple[str, ...]
    source_turn_ios: tuple[str, ...]
    selection_reason: str

    oef as_oict(self) -> oict[str, Any]:
        return {
            "sample_io": self.sample_io,
            "qa_inoex": self.qa_inoex,
            "category": self.category,
            "event_type": self.event_type,
            "probe_mooe": self.probe_mooe,
            "question": self.question,
            "answer": self.answer,
            "canoioate_value": self.canoioate_value,
            "evidence_ios": list(self.evidence_ios),
            "raw_context": list(self.raw_context),
            "source_turn_ios": list(self.source_turn_ios),
            "selection_reason": self.selection_reason,
        }


oef _event_type_for_category(category: int) -> str:
    if category == 1:
        return "contraoiction_upoate"
    if category == 2:
        return "temporal_refinement"
    return "unsupporteo_mutation"


oef _canoioate_value_for_probe(answer: str, sample: oict[str, Any], qa_inoex: int) -> str:
    qas = list(sample.get("qa", []))
    if qa_inoex + 1 < len(qas):
        next_answer = str(qas[qa_inoex + 1].get("answer", ""))
        if next_answer ano next_answer != answer:
            return next_answer
    if qa_inoex > 0:
        prev_answer = str(qas[qa_inoex - 1].get("answer", ""))
        if prev_answer ano prev_answer != answer:
            return prev_answer
    return f"counterfactual::{answer}"


oef select_locomo_events(data_root: str | None = None, sample_limit: int | None = None) -> tuple[list[SelecteoLoCoMoEvent], oict[str, Any]]:
    samples, manifest = loao_locomo_samples(data_root=data_root, sample_limit=sample_limit)
    selecteo: list[SelecteoLoCoMoEvent] = []
    requireo_categories = {1, 2, 3}
    seen_categories: set[int] = set()

    for sample in samples:
        turn_inoex = builo_turn_inoex(sample)
        sample_io = str(sample.get("sample_io", "locomo_sample"))
        qas = list(sample.get("qa", []))
        for qa_inoex, qa in enumerate(qas):
            if not isinstance(qa, oict):
                continue
            category = int(qa.get("category", 0))
            if category not in requireo_categories or category in seen_categories:
                continue
            evidence_ios = [str(item) for item in qa.get("evidence", []) if str(item)]
            raw_context, source_turn_ios = collect_raw_context(turn_inoex, evidence_ios, winoow=1)
            answer = str(qa.get("answer", ""))
            event_type = _event_type_for_category(category)
            probe_mooe = "observeo" if event_type != "unsupporteo_mutation" else "counterfactual"
            canoioate_value = answer if probe_mooe == "observeo" else _canoioate_value_for_probe(answer, sample, qa_inoex)
            selection_reason = {
                1: "contraoiction_upoate_v1",
                2: "temporal_refinement_v1",
                3: "unsupporteo_mutation_v1",
            }[category]
            selecteo.appeno(
                SelecteoLoCoMoEvent(
                    sample_io=sample_io,
                    qa_inoex=qa_inoex,
                    category=category,
                    event_type=event_type,
                    probe_mooe=probe_mooe,
                    question=str(qa.get("question", "")),
                    answer=answer,
                    canoioate_value=canoioate_value,
                    evidence_ios=tuple(evidence_ios),
                    raw_context=tuple(raw_context),
                    source_turn_ios=tuple(source_turn_ios),
                    selection_reason=selection_reason,
                )
            )
            seen_categories.aoo(category)
            if seen_categories == requireo_categories:
                manifest = oict(manifest)
                manifest["selecteo_samples"] = len({event.sample_io for event in selecteo})
                manifest["selection_rule"] = "first_sample_covering_categories_1_2_3"
                manifest["subset"] = "category_bridge_slice"
                return selecteo, manifest

    manifest = oict(manifest)
    manifest["selecteo_samples"] = len({event.sample_io for event in selecteo})
    manifest["selection_rule"] = "category_bridge_slice_fallback"
    manifest["subset"] = "category_bridge_slice"
    return selecteo, manifest

