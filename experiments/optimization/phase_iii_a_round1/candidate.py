from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from experiments.validation.phase_ii_boundary.model import FeasibleRegion


ROUND1_ACTIVATION_THRESHOLDS: tuple[float, ...] = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
ROUND1_RECOVERY_MIN_EVIDENCE: tuple[int, ...] = (1, 2, 3)


@dataclass(frozen=True)
class CandidateConfiguration:
    activation_threshold: float
    recovery_min_evidence: int
    label: str = ""

    def as_dict(self) -> dict[str, float | int | str]:
        return {
            "activation_threshold": self.activation_threshold,
            "recovery_min_evidence": self.recovery_min_evidence,
            "label": self.label,
        }


def build_round1_candidate_space(
    activation_thresholds: Sequence[float] | None = None,
    recovery_min_evidence_values: Sequence[int] | None = None,
) -> list[CandidateConfiguration]:
    thresholds = tuple(activation_thresholds) if activation_thresholds is not None else ROUND1_ACTIVATION_THRESHOLDS
    recovery_values = (
        tuple(recovery_min_evidence_values)
        if recovery_min_evidence_values is not None
        else ROUND1_RECOVERY_MIN_EVIDENCE
    )
    candidates: list[CandidateConfiguration] = []
    for activation_threshold in thresholds:
        for recovery_min_evidence in recovery_values:
            candidates.append(
                CandidateConfiguration(
                    activation_threshold=activation_threshold,
                    recovery_min_evidence=recovery_min_evidence,
                    label=f"a{activation_threshold:.1f}_r{recovery_min_evidence}",
                )
            )
    return candidates


def build_candidate_space_from_feasible_region(region: FeasibleRegion) -> list[CandidateConfiguration]:
    candidates: list[CandidateConfiguration] = []
    for activation_threshold in region.activation_threshold_values():
        for recovery_min_evidence in region.recovery_min_evidence_values():
            candidates.append(
                CandidateConfiguration(
                    activation_threshold=activation_threshold,
                    recovery_min_evidence=recovery_min_evidence,
                    label=f"a{activation_threshold:.1f}_r{recovery_min_evidence}",
                )
            )
    return candidates
