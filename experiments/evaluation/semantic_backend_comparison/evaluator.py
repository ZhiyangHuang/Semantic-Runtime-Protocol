from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .backend import BackendOutcome, ComparisonBackend, ComparisonCase


@dataclass(frozen=True)
class BackendComparisonRecord:
    case: ComparisonCase
    vector_outcome: BackendOutcome
    variant_outcome: BackendOutcome
    agreement: bool
    final_decision: str
    expected_verdict: bool

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BackendComparisonReport:
    report_id: str
    status: str
    baseline_backend: str
    variant_backend: str
    records: list[BackendComparisonRecord] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _final_decision(vector_decision: str, variant_decision: str) -> str:
    if vector_decision == variant_decision and vector_decision in {"accept", "reject"}:
        return vector_decision
    return "review"


def _is_correct(decision: str, expected_verdict: bool) -> bool:
    if decision == "review":
        return False
    return (decision == "accept") == expected_verdict


class SemanticBackendComparator:
    def __init__(self, baseline_backend: ComparisonBackend, variant_backend: ComparisonBackend) -> None:
        self.baseline_backend = baseline_backend
        self.variant_backend = variant_backend

    def compare(self, cases: list[ComparisonCase]) -> BackendComparisonReport:
        records: list[BackendComparisonRecord] = []
        repeat_vector_matches = 0
        repeat_variant_matches = 0
        for case in cases:
            vector_outcome = self.baseline_backend.evaluate(case)
            variant_outcome = self.variant_backend.evaluate(case)
            repeat_vector_outcome = self.baseline_backend.evaluate(case)
            repeat_variant_outcome = self.variant_backend.evaluate(case)
            if vector_outcome.decision == repeat_vector_outcome.decision:
                repeat_vector_matches += 1
            if variant_outcome.decision == repeat_variant_outcome.decision:
                repeat_variant_matches += 1
            records.append(
                BackendComparisonRecord(
                    case=case,
                    vector_outcome=vector_outcome,
                    variant_outcome=variant_outcome,
                    agreement=vector_outcome.decision == variant_outcome.decision,
                    final_decision=_final_decision(vector_outcome.decision, variant_outcome.decision),
                    expected_verdict=case.expected_verdict,
                )
            )

        summary = self._summarize(records, repeat_vector_matches, repeat_variant_matches)
        return BackendComparisonReport(
            report_id=f"semantic_backend_comparison_{len(records)}",
            status="compared",
            baseline_backend=self.baseline_backend.backend_name,
            variant_backend=self.variant_backend.backend_name,
            records=records,
            summary=summary,
        )

    def _summarize(
        self,
        records: list[BackendComparisonRecord],
        repeat_vector_matches: int,
        repeat_variant_matches: int,
    ) -> dict[str, Any]:
        total = len(records)
        agreement_count = sum(1 for record in records if record.agreement)
        vector_correct = sum(1 for record in records if _is_correct(record.vector_outcome.decision, record.expected_verdict))
        variant_correct = sum(1 for record in records if _is_correct(record.variant_outcome.decision, record.expected_verdict))
        final_correct = sum(1 for record in records if _is_correct(record.final_decision, record.expected_verdict))
        vector_false_acceptance = sum(
            1 for record in records if record.vector_outcome.decision == "accept" and not record.expected_verdict
        )
        vector_false_rejection = sum(
            1 for record in records if record.vector_outcome.decision == "reject" and record.expected_verdict
        )
        variant_false_acceptance = sum(
            1 for record in records if record.variant_outcome.decision == "accept" and not record.expected_verdict
        )
        variant_false_rejection = sum(
            1 for record in records if record.variant_outcome.decision == "reject" and record.expected_verdict
        )
        escalated = sum(1 for record in records if record.final_decision == "review")
        review_count = sum(1 for record in records if record.final_decision == "review")
        review_rate = review_count / total if total else 0.0
        vector_latency = sum(record.vector_outcome.latency_seconds for record in records)
        variant_latency = sum(record.variant_outcome.latency_seconds for record in records)
        authority_violation_records = [record for record in records if record.case.category == "authority_violation"]
        boundary_records = [record for record in records if record.case.category == "boundary_case"]
        paraphrase_records = [record for record in records if record.case.category == "paraphrase"]
        contradiction_records = [record for record in records if record.case.category == "contradiction"]
        authority_violation_final_accept_count = sum(1 for record in authority_violation_records if record.final_decision == "accept")
        authority_violation_final_reject_count = sum(1 for record in authority_violation_records if record.final_decision == "reject")
        authority_violation_review_count = sum(1 for record in authority_violation_records if record.final_decision == "review")
        boundary_review_count = sum(1 for record in boundary_records if record.final_decision == "review")
        variant_local_model_count = sum(1 for record in records if record.variant_outcome.mode == "local_model")
        variant_offline_heuristic_count = sum(1 for record in records if record.variant_outcome.mode == "offline_heuristic")
        variant_fallback_count = sum(1 for record in records if record.variant_outcome.fallback_used)
        authority_violation_final_accept_rate = (
            authority_violation_final_accept_count / len(authority_violation_records) if authority_violation_records else 0.0
        )
        return {
            "case_count": total,
            "agreement_count": agreement_count,
            "agreement_rate": round(agreement_count / total, 4) if total else 0.0,
            "disagreement_count": total - agreement_count,
            "vector_accuracy": round(vector_correct / total, 4) if total else 0.0,
            "variant_accuracy": round(variant_correct / total, 4) if total else 0.0,
            "final_accuracy": round(final_correct / total, 4) if total else 0.0,
            "vector_false_acceptance": vector_false_acceptance,
            "vector_false_rejection": vector_false_rejection,
            "variant_false_acceptance": variant_false_acceptance,
            "variant_false_rejection": variant_false_rejection,
            "escalated_case_count": escalated,
            "review_count": review_count,
            "review_rate": round(review_rate, 4),
            "mean_vector_latency_seconds": round(vector_latency / total, 6) if total else 0.0,
            "mean_variant_latency_seconds": round(variant_latency / total, 6) if total else 0.0,
            "vector_repeat_stability_rate": round(repeat_vector_matches / total, 4) if total else 0.0,
            "variant_repeat_stability_rate": round(repeat_variant_matches / total, 4) if total else 0.0,
            "authority_violation_case_count": len(authority_violation_records),
            "authority_violation_final_accept_count": authority_violation_final_accept_count,
            "authority_violation_final_reject_count": authority_violation_final_reject_count,
            "authority_violation_review_count": authority_violation_review_count,
            "authority_violation_final_accept_rate": round(authority_violation_final_accept_rate, 4),
            "boundary_case_count": len(boundary_records),
            "boundary_review_count": boundary_review_count,
            "paraphrase_case_count": len(paraphrase_records),
            "contradiction_case_count": len(contradiction_records),
            "variant_local_model_count": variant_local_model_count,
            "variant_offline_heuristic_count": variant_offline_heuristic_count,
            "variant_fallback_count": variant_fallback_count,
        }
