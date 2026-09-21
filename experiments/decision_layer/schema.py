from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping

DEFAULT_SCHEMA_VERSION = "decision_dataset_case.v1"


class DecisionLabel(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    REVIEW = "REVIEW"


@dataclass(frozen=True)
class GroundTruth:
    canonical_label: DecisionLabel
    label_source: str
    label_reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "canonical_label": self.canonical_label.value,
            "label_source": self.label_source,
        }
        if self.label_reason is not None:
            payload["label_reason"] = self.label_reason
        return payload


@dataclass(frozen=True)
class Provenance:
    source_type: str
    source_id: str
    source_path: str | None = None
    git_commit: str | None = None
    generator_version: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "source_type": self.source_type,
            "source_id": self.source_id,
        }
        for key in ("source_path", "git_commit", "generator_version"):
            value = getattr(self, key)
            if value is not None:
                payload[key] = value
        return payload


@dataclass(frozen=True)
class DecisionDatasetCase:
    case_id: str
    dataset_version: str
    state_before: Any
    candidate_transition: Any
    evidence: Any
    governance_context: Mapping[str, Any]
    ground_truth: GroundTruth
    scenario_id: str
    group_id: str
    provenance: Provenance
    schema_version: str = DEFAULT_SCHEMA_VERSION
    observation: Any | None = None
    expected_state_after: Any | None = None
    actual_state_after: Any | None = None
    annotations: Mapping[str, Any] = field(default_factory=dict)
    replay: Mapping[str, Any] = field(default_factory=dict)
    evaluation: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "case_id": self.case_id,
            "schema_version": self.schema_version,
            "dataset_version": self.dataset_version,
            "state_before": self.state_before,
            "candidate_transition": self.candidate_transition,
            "evidence": self.evidence,
            "governance_context": dict(self.governance_context),
            "ground_truth": self.ground_truth.as_dict(),
            "scenario_id": self.scenario_id,
            "group_id": self.group_id,
            "provenance": self.provenance.as_dict(),
        }
        optional_fields = {
            "observation": self.observation,
            "expected_state_after": self.expected_state_after,
            "actual_state_after": self.actual_state_after,
            "annotations": dict(self.annotations),
            "replay": dict(self.replay),
            "evaluation": dict(self.evaluation),
        }
        for key, value in optional_fields.items():
            if value not in (None, {}, []):
                payload[key] = value
        return payload

    def training_input(self) -> dict[str, Any]:
        return {
            "state_before": self.state_before,
            "candidate_transition": self.candidate_transition,
            "evidence": self.evidence,
            "governance_context": dict(self.governance_context),
            **({"observation": self.observation} if self.observation is not None else {}),
        }

    def target(self) -> dict[str, Any]:
        return self.ground_truth.as_dict()


def label_from_bool(value: bool | None) -> DecisionLabel | None:
    if value is True:
        return DecisionLabel.ACCEPT
    if value is False:
        return DecisionLabel.REJECT
    return None


def normalize_label(value: str | DecisionLabel) -> DecisionLabel:
    if isinstance(value, DecisionLabel):
        return value
    return DecisionLabel(str(value).upper())
