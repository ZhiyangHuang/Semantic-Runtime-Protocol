from __future__ import annotations

from typing import Any, Mapping

from .schema import DecisionDatasetCase, DecisionLabel


class DecisionDatasetValidationError(ValueError):
    pass


_PROHIBITED_TRAINING_KEYS = {
    "ground_truth",
    "canonical_label",
    "label_source",
    "label_reason",
    "expected_state_after",
    "actual_state_after",
    "governance_result",
    "transition_trace",
    "decision",
    "metrics",
    "timing",
    "replay",
    "evaluation",
}

_PROHIBITED_NESTED_TRAINING_KEYS = {
    "canonical_label",
    "label",
    "ground_truth",
    "expected",
    "expected_decision",
    "expecteo_decision",
    "accepted",
    "accepteo",
    "decision",
    "actual_state_after",
    "expected_state_after",
    "replay",
    "evaluation",
    "metrics",
    "timing",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DecisionDatasetValidationError(message)


def _training_input_from_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    keys = ("state_before", "candidate_transition", "evidence", "governance_context", "observation")
    return {key: payload[key] for key in keys if key in payload and payload[key] is not None}


def _scan_nested_training_value(value: Any, path: str = "training_input") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().lower()
            if normalized in _PROHIBITED_NESTED_TRAINING_KEYS:
                raise DecisionDatasetValidationError(f"training input contains prohibited nested field: {path}.{key}")
            _scan_nested_training_value(item, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _scan_nested_training_value(item, f"{path}[{index}]")


def validate_decision_case(case: DecisionDatasetCase | Mapping[str, Any]) -> None:
    payload = case.as_dict() if isinstance(case, DecisionDatasetCase) else dict(case)
    required = (
        "case_id",
        "schema_version",
        "dataset_version",
        "state_before",
        "candidate_transition",
        "evidence",
        "governance_context",
        "ground_truth",
        "scenario_id",
        "group_id",
        "provenance",
    )
    for key in required:
        _require(key in payload, f"missing required field: {key}")
    _require(str(payload["case_id"]).strip() != "", "case_id must be non-empty")
    _require(str(payload["scenario_id"]).strip() != "", "scenario_id must be non-empty")
    _require(str(payload["group_id"]).strip() != "", "group_id must be non-empty")

    ground_truth = payload.get("ground_truth")
    _require(isinstance(ground_truth, Mapping), "ground_truth must be an object")
    _require("canonical_label" in ground_truth, "ground_truth.canonical_label is required")
    _require("label_source" in ground_truth, "ground_truth.label_source is required")
    try:
        DecisionLabel(str(ground_truth["canonical_label"]))
    except ValueError as exc:
        raise DecisionDatasetValidationError("invalid canonical label") from exc

    provenance = payload.get("provenance")
    _require(isinstance(provenance, Mapping), "provenance must be an object")
    _require(str(provenance.get("source_type", "")).strip() != "", "provenance.source_type is required")
    _require(str(provenance.get("source_id", "")).strip() != "", "provenance.source_id is required")

    if isinstance(case, DecisionDatasetCase):
        training_input = case.training_input()
    else:
        training = payload.get("training_input")
        training_input = dict(training) if isinstance(training, Mapping) else _training_input_from_payload(payload)
    training_keys = set(training_input)
    leaked = training_keys & _PROHIBITED_TRAINING_KEYS
    _require(not leaked, f"training input contains prohibited fields: {sorted(leaked)}")
    _scan_nested_training_value(training_input)


def validate_split_manifest(manifest: Mapping[str, Any]) -> None:
    for key in ("dataset_version", "seed", "grouping_key", "train", "validation", "test"):
        _require(key in manifest, f"missing split manifest field: {key}")
    split_groups: dict[str, str] = {}
    for split_name in ("train", "validation", "test"):
        groups = manifest.get(split_name)
        _require(isinstance(groups, list), f"{split_name} must be a list")
        for group_id in groups:
            key = str(group_id)
            if key in split_groups:
                raise DecisionDatasetValidationError(
                    f"group_id {key!r} appears in both {split_groups[key]} and {split_name}"
                )
            split_groups[key] = split_name
