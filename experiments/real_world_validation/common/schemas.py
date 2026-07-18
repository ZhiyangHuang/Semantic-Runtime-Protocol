from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SemanticStateSnapshot:
    state_id: str
    facts: tuple[str, ...] = ()
    relations: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionCandidate:
    event_id: str
    event_type: str
    claim_id: str
    dataset_event: str
    old_state: SemanticStateSnapshot
    new_information: SemanticStateSnapshot
    evidence: tuple[str, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)
    expected_decision: str = "reject"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ClaimMapping:
    claim_id: str
    paper_section: str
    observable_behavior: str
    experiment_events: tuple[str, ...]
    promotion_level: str
    claim_scope: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetManifest:
    dataset: str
    version: str
    source: str
    subset: str
    samples: int
    selection_rule: str
    source_hash: str = ""
    selected_samples: int = 0
    excluded_cases: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RunConfig:
    seed: int
    encoder: str
    threshold: float
    relation_depth: int
    evidence_policy: str
    governance_mode: str
    baseline_set: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionMetrics:
    accepted_transitions: int
    rejected_transitions: int
    invalid_accept_rate: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GovernanceMetrics:
    authority_changed_with_evidence: bool
    recommendation_execution_separated: bool
    replay_consistency: float
    authority_escalation_rate: float
    evidence_improvement: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaskMetrics:
    memory_accuracy: float
    relation_accuracy: float
    fact_accuracy: float
    coverage: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FailureCase:
    case_id: str
    event: str
    expected: str
    actual: str
    failure: bool
    failure_type: str | None
    interpretation: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Decision:
    claim_supported: bool
    support_level: str
    scope: str
    promotion: str
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ValidationRun:
    metadata: dict[str, Any]
    claim_mapping: ClaimMapping
    dataset_manifest: DatasetManifest
    run_config: RunConfig
    transition_metrics: TransitionMetrics
    governance_metrics: GovernanceMetrics
    task_metrics: TaskMetrics
    failure_cases: tuple[FailureCase, ...]
    decision: Decision
    transition_records: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "metadata": dict(self.metadata),
            "claim_mapping": self.claim_mapping.as_dict(),
            "dataset_manifest": self.dataset_manifest.as_dict(),
            "run_config": self.run_config.as_dict(),
            "metrics": {
                "transition_metrics": self.transition_metrics.as_dict(),
                "governance_metrics": self.governance_metrics.as_dict(),
                "task_metrics": self.task_metrics.as_dict(),
            },
            "failure_cases": [failure.as_dict() for failure in self.failure_cases],
            "decision": self.decision.as_dict(),
            "transition_records": [dict(record) for record in self.transition_records],
        }
