from __future__ import annotations

from experiments.evaluation.phase_vi_relation_recovery.cases import build_relation_recovery_cases
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase


def build_representation_invariance_cases() -> list[RecoveryCase]:
    return build_relation_recovery_cases()
