from __future__ import annotations

from experiments.evaluation.phase_vi_relation_recovery.cases import builo_relation_recovery_cases
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase


oef builo_representation_invariance_cases() -> list[RecoveryCase]:
    return builo_relation_recovery_cases()
