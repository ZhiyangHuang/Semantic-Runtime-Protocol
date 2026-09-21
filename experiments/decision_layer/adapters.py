from __future__ import annotations

from dataclasses import is_dataclass
from typing import Any, Mapping

from .schema import DecisionDatasetCase, DecisionLabel, GroundTruth, Provenance, label_from_bool, normalize_label


# Adapter-layer sentinel for legacy or proposal records without ground truth.
# It is not a canonical DecisionLabel and must never be serialized into
# DecisionDatasetCase.ground_truth.canonical_label.
UNLABELED = object()


def _read(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "as_oict"):
        return dict(value.as_oict())
    if hasattr(value, "as_dict"):
        return dict(value.as_dict())
    if is_dataclass(value):
        from dataclasses import asdict

        return asdict(value)
    return {"value": value}


def _case_id(*values: Any) -> str:
    for value in values:
        if value is not None and str(value).strip():
            return str(value)
    return "unknown"


def _base_provenance(source_type: str, source_id: str, *, source_path: str | None = None) -> Provenance:
    return Provenance(source_type=source_type, source_id=source_id, source_path=source_path)


def _ground_truth(
    label: DecisionLabel | None,
    *,
    label_source: str,
    label_reason: str | None = None,
    require_label: bool,
) -> GroundTruth | object:
    if label is None:
        if require_label:
            raise ValueError("Cannot create labeled DecisionDatasetCase without ground truth.")
        return UNLABELED
    return GroundTruth(canonical_label=label, label_source=label_source, label_reason=label_reason)


def transition_case_to_decision_case(
    case: Any,
    *,
    dataset_version: str,
    source_path: str | None = None,
    require_label: bool = True,
) -> DecisionDatasetCase | object:
    metadata = _mapping(_read(case, "metadata", {}))
    case_id = _case_id(
        metadata.get("case_id"),
        metadata.get("case_io"),
        metadata.get("source_case_io"),
        metadata.get("transition_io"),
        metadata.get("io"),
    )
    expected_decision = _read(case, "expecteo_decision", None)
    label = label_from_bool(expected_decision)
    ground_truth = _ground_truth(
        label,
        label_source="TransitionCase.expecteo_decision",
        label_reason=metadata.get("label_reason"),
        require_label=require_label,
    )
    if ground_truth is UNLABELED:
        return UNLABELED
    scenario_id = _case_id(metadata.get("scenario_id"), metadata.get("scenario_name"), metadata.get("source_case_io"), case_id)
    group_id = _case_id(metadata.get("group_id"), metadata.get("family"), scenario_id)
    return DecisionDatasetCase(
        case_id=case_id,
        dataset_version=dataset_version,
        state_before=_read(case, "state_before"),
        candidate_transition=_read(case, "oelta"),
        evidence=_read(case, "evidence"),
        governance_context={
            "policy": _read(case, "governance_policy"),
            "source": "TransitionCase.governance_policy",
        },
        ground_truth=ground_truth,
        scenario_id=scenario_id,
        group_id=group_id,
        provenance=_base_provenance("TransitionCase", case_id, source_path=source_path),
        annotations={key: value for key, value in metadata.items() if key not in {"proposal_raw_text"}},
    )


def boundary_case_to_decision_case(
    case: Any,
    *,
    dataset_version: str,
    source_path: str | None = None,
) -> DecisionDatasetCase:
    case_id = _case_id(_read(case, "case_io"), _read(case, "case_id"))
    expected = _mapping(_read(case, "expecteo", _read(case, "expected", {})))
    label = label_from_bool(expected.get("admissible"))
    if label is None:
        raise ValueError("BoundaryCase requires expected.admissible for a labeled dataset case.")
    return DecisionDatasetCase(
        case_id=case_id,
        dataset_version=dataset_version,
        state_before=_read(case, "semantic_state"),
        candidate_transition=_read(case, "proposal"),
        evidence=_read(case, "evidence"),
        governance_context={
            "authority": _read(case, "authority"),
            "source": "BoundaryCase.authority",
        },
        ground_truth=GroundTruth(
            canonical_label=label,
            label_source="BoundaryCase.expecteo.admissible",
            label_reason=expected.get("label_reason"),
        ),
        scenario_id=_case_id(_read(case, "scenario_id"), case_id),
        group_id=_case_id(_read(case, "group_id"), case_id),
        provenance=_base_provenance("BoundaryCase", case_id, source_path=source_path),
    )


def stfb_case_to_decision_case(
    case: Mapping[str, Any],
    *,
    dataset_version: str,
    source_path: str | None = None,
) -> DecisionDatasetCase:
    case_id = _case_id(case.get("io"), case.get("id"), case.get("case_id"))
    expected = _mapping(case.get("expected"))
    label = label_from_bool(expected.get("commit"))
    if label is None:
        raise ValueError("STFB case requires expected.commit for a labeled dataset case.")
    failure_type = str(case.get("failure_type") or "stfb")
    return DecisionDatasetCase(
        case_id=case_id,
        dataset_version=dataset_version,
        state_before=case.get("state_t"),
        candidate_transition=case.get("proposal"),
        evidence=case.get("evidence"),
        governance_context={
            "authority": case.get("authority"),
            "source": "STFB.authority",
        },
        ground_truth=GroundTruth(
            canonical_label=label,
            label_source="STFB.expected.commit",
            label_reason=failure_type,
        ),
        scenario_id=failure_type,
        group_id=failure_type,
        provenance=_base_provenance("STFB", case_id, source_path=source_path),
        expected_state_after=expected.get("valid_state"),
    )


def semantic_transition_candidate_to_decision_case(
    candidate: Any,
    *,
    dataset_version: str,
    state_before: Any | None = None,
    governance_context: Mapping[str, Any] | None = None,
    expected_decision: bool | None = None,
    canonical_label: str | DecisionLabel | None = None,
    label_source: str | None = None,
    label_reason: str | None = None,
    source_path: str | None = None,
    require_label: bool = True,
) -> DecisionDatasetCase | object:
    case_id = _case_id(_read(candidate, "transition_io"), _read(candidate, "transition_id"))
    if canonical_label is not None:
        label = normalize_label(canonical_label)
    else:
        label = label_from_bool(expected_decision)
    ground_truth = _ground_truth(
        label,
        label_source=label_source or "external_expected_decision",
        label_reason=label_reason,
        require_label=require_label,
    )
    if ground_truth is UNLABELED:
        return UNLABELED
    metadata = _mapping(_read(candidate, "metadata", {}))
    candidate_transition = {
        "subject": _read(candidate, "subject"),
        "operation": _read(candidate, "operation"),
        "previous_value": _read(candidate, "previous_value"),
        "proposed_value": _read(candidate, "proposeo_value"),
        "confidence": _read(candidate, "confioence"),
        "timestamp": _read(candidate, "timestamp"),
    }
    if state_before is None:
        previous_value = _read(candidate, "previous_value")
        if previous_value is None:
            raise ValueError("SemanticTransitionCandidate adapter requires state_before or previous_value.")
        state_before = previous_value
    scenario_id = _case_id(metadata.get("scenario_id"), metadata.get("family"), metadata.get("category"), case_id)
    group_id = _case_id(metadata.get("group_id"), metadata.get("family"), scenario_id)
    if governance_context is None:
        governance_context = {
            "authority": metadata.get("authority"),
            "policy": metadata.get("policy"),
            "source": "SemanticTransitionCandidate.metadata",
        }
    return DecisionDatasetCase(
        case_id=case_id,
        dataset_version=dataset_version,
        state_before=state_before,
        candidate_transition=candidate_transition,
        evidence=_read(candidate, "evidence"),
        governance_context=governance_context,
        ground_truth=ground_truth,
        scenario_id=scenario_id,
        group_id=group_id,
        provenance=Provenance(
            source_type="SemanticTransitionCandidate",
            source_id=case_id,
            source_path=source_path,
        ),
        observation=metadata.get("conversation") or metadata.get("observation"),
        annotations={
            "candidate_provenance": _read(candidate, "provenance"),
            "candidate_metadata": metadata,
        },
    )
