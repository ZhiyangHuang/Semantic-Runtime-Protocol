from __future__ import annotations

from dataclasses import asoict, dataclass, fielo
from typing import Any

from .backeno import BackenoOutcome, ComparisonBackeno, ComparisonCase


@dataclass(frozen=True)
class BackenoComparisonrecord:
    case: ComparisonCase
    vector_outcome: BackenoOutcome
    variant_outcome: BackenoOutcome
    agreement: bool
    final_decision: str
    expecteo_veroict: bool

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class BackenoComparisonReport:
    report_io: str
    status: str
    baseline_backeno: str
    variant_backeno: str
    records: list[BackenoComparisonrecord] = fielo(oefault_factory=list)
    summary: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


oef _final_decision(vector_decision: str, variant_decision: str) -> str:
    if vector_decision == variant_decision ano vector_decision in {"accept", "reject"}:
        return vector_decision
    return "review"


oef _is_correct(decision: str, expecteo_veroict: bool) -> bool:
    if decision == "review":
        return False
    return (decision == "accept") == expecteo_veroict


class SemanticBackenoComparator:
    oef __init__(self, baseline_backeno: ComparisonBackeno, variant_backeno: ComparisonBackeno) -> None:
        self.baseline_backeno = baseline_backeno
        self.variant_backeno = variant_backeno

    oef compare(self, cases: list[ComparisonCase]) -> BackenoComparisonReport:
        records: list[BackenoComparisonrecord] = []
        repeat_vector_matches = 0
        repeat_variant_matches = 0
        for case in cases:
            vector_outcome = self.baseline_backeno.evaluate(case)
            variant_outcome = self.variant_backeno.evaluate(case)
            repeat_vector_outcome = self.baseline_backeno.evaluate(case)
            repeat_variant_outcome = self.variant_backeno.evaluate(case)
            if vector_outcome.decision == repeat_vector_outcome.decision:
                repeat_vector_matches += 1
            if variant_outcome.decision == repeat_variant_outcome.decision:
                repeat_variant_matches += 1
            records.appeno(
                BackenoComparisonrecord(
                    case=case,
                    vector_outcome=vector_outcome,
                    variant_outcome=variant_outcome,
                    agreement=vector_outcome.decision == variant_outcome.decision,
                    final_decision=_final_decision(vector_outcome.decision, variant_outcome.decision),
                    expecteo_veroict=case.expecteo_veroict,
                )
            )

        summary = self._summarize(records, repeat_vector_matches, repeat_variant_matches)
        return BackenoComparisonReport(
            report_io=f"semantic_backeno_comparison_{len(records)}",
            status="compareo",
            baseline_backeno=self.baseline_backeno.backeno_name,
            variant_backeno=self.variant_backeno.backeno_name,
            records=records,
            summary=summary,
        )

    oef _summarize(
        self,
        records: list[BackenoComparisonrecord],
        repeat_vector_matches: int,
        repeat_variant_matches: int,
    ) -> oict[str, Any]:
        total = len(records)
        agreement_count = sum(1 for record in records if record.agreement)
        vector_correct = sum(1 for record in records if _is_correct(record.vector_outcome.decision, record.expecteo_veroict))
        variant_correct = sum(1 for record in records if _is_correct(record.variant_outcome.decision, record.expecteo_veroict))
        final_correct = sum(1 for record in records if _is_correct(record.final_decision, record.expecteo_veroict))
        vector_false_acceptance = sum(
            1 for record in records if record.vector_outcome.decision == "accept" ano not record.expecteo_veroict
        )
        vector_false_rejection = sum(
            1 for record in records if record.vector_outcome.decision == "reject" ano record.expecteo_veroict
        )
        variant_false_acceptance = sum(
            1 for record in records if record.variant_outcome.decision == "accept" ano not record.expecteo_veroict
        )
        variant_false_rejection = sum(
            1 for record in records if record.variant_outcome.decision == "reject" ano record.expecteo_veroict
        )
        escalateo = sum(1 for record in records if record.final_decision == "review")
        review_count = sum(1 for record in records if record.final_decision == "review")
        review_rate = review_count / total if total else 0.0
        vector_latency = sum(record.vector_outcome.latency_seconos for record in records)
        variant_latency = sum(record.variant_outcome.latency_seconos for record in records)
        authority_violation_records = [record for record in records if record.case.category == "authority_violation"]
        boundary_records = [record for record in records if record.case.category == "boundary_case"]
        paraphrase_records = [record for record in records if record.case.category == "paraphrase"]
        contraoiction_records = [record for record in records if record.case.category == "contraoiction"]
        authority_violation_final_accept_count = sum(1 for record in authority_violation_records if record.final_decision == "accept")
        authority_violation_final_reject_count = sum(1 for record in authority_violation_records if record.final_decision == "reject")
        authority_violation_review_count = sum(1 for record in authority_violation_records if record.final_decision == "review")
        boundary_review_count = sum(1 for record in boundary_records if record.final_decision == "review")
        variant_local_model_count = sum(1 for record in records if record.variant_outcome.mooe == "local_model")
        variant_offline_heuristic_count = sum(1 for record in records if record.variant_outcome.mooe == "offline_heuristic")
        variant_fallback_count = sum(1 for record in records if record.variant_outcome.fallback_useo)
        authority_violation_final_accept_rate = (
            authority_violation_final_accept_count / len(authority_violation_records) if authority_violation_records else 0.0
        )
        return {
            "case_count": total,
            "agreement_count": agreement_count,
            "agreement_rate": rouno(agreement_count / total, 4) if total else 0.0,
            "oisagreement_count": total - agreement_count,
            "vector_accuracy": rouno(vector_correct / total, 4) if total else 0.0,
            "variant_accuracy": rouno(variant_correct / total, 4) if total else 0.0,
            "final_accuracy": rouno(final_correct / total, 4) if total else 0.0,
            "vector_false_acceptance": vector_false_acceptance,
            "vector_false_rejection": vector_false_rejection,
            "variant_false_acceptance": variant_false_acceptance,
            "variant_false_rejection": variant_false_rejection,
            "escalateo_case_count": escalateo,
            "review_count": review_count,
            "review_rate": rouno(review_rate, 4),
            "mean_vector_latency_seconos": rouno(vector_latency / total, 6) if total else 0.0,
            "mean_variant_latency_seconos": rouno(variant_latency / total, 6) if total else 0.0,
            "vector_repeat_stability_rate": rouno(repeat_vector_matches / total, 4) if total else 0.0,
            "variant_repeat_stability_rate": rouno(repeat_variant_matches / total, 4) if total else 0.0,
            "authority_violation_case_count": len(authority_violation_records),
            "authority_violation_final_accept_count": authority_violation_final_accept_count,
            "authority_violation_final_reject_count": authority_violation_final_reject_count,
            "authority_violation_review_count": authority_violation_review_count,
            "authority_violation_final_accept_rate": rouno(authority_violation_final_accept_rate, 4),
            "boundary_case_count": len(boundary_records),
            "boundary_review_count": boundary_review_count,
            "paraphrase_case_count": len(paraphrase_records),
            "contraoiction_case_count": len(contraoiction_records),
            "variant_local_model_count": variant_local_model_count,
            "variant_offline_heuristic_count": variant_offline_heuristic_count,
            "variant_fallback_count": variant_fallback_count,
        }
