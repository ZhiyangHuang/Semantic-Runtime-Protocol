from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Iterable

from ..adapter import SemanticTransitionCandidate
from ..workloads import RuntimeIntegrationExample, build_runtime_integration_workload_family

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURE_PATH = PROJECT_ROOT / "experiments" / "runtime_integration" / "fixtures" / "semantic_transition_replay_v1.json"


def load_runtime_integration_examples() -> list[RuntimeIntegrationExample]:
    return build_runtime_integration_workload_family()


def load_runtime_integration_fixture_payload(
    fixture_path: str | Path | None = None,
) -> dict[str, object]:
    selected_path = Path(fixture_path) if fixture_path is not None else DEFAULT_FIXTURE_PATH
    return json.loads(selected_path.read_text(encoding="utf-8"))


def load_runtime_integration_examples_from_fixture(fixture_path: str | Path | None = None) -> list[RuntimeIntegrationExample]:
    selected_path = Path(fixture_path) if fixture_path is not None else DEFAULT_FIXTURE_PATH
    payload = load_runtime_integration_fixture_payload(selected_path)
    cases = payload.get("cases") or []
    examples: list[RuntimeIntegrationExample] = []
    for case in cases:
        if not isinstance(case, dict):
            continue
        examples.append(
            RuntimeIntegrationExample(
                example_id=str(case.get("id") or "unknown"),
                family=str(case.get("family") or "runtime"),
                category=str(case.get("category") or "unknown"),
                description=str(case.get("description") or ""),
                conversation=str(case.get("conversation") or ""),
                state_before=dict(case.get("state_before") or {}),
                candidate_payload=dict(case.get("candidate_payload") or {}),
                expected_decision=bool(case.get("expected_decision", False)),
                metadata={
                    "runtime_contract": payload.get("runtime_contract"),
                    "version": payload.get("version"),
                    "adapter": payload.get("adapter"),
                    "fixture_path": str(selected_path),
                },
            )
        )
    return examples


def build_candidate_from_example(example: RuntimeIntegrationExample) -> SemanticTransitionCandidate:
    payload = deepcopy(example.candidate_payload)
    payload.setdefault("metadata", {})
    metadata = payload.get("metadata") or {}
    metadata.setdefault("example_id", example.example_id)
    metadata.setdefault("family", example.family)
    metadata.setdefault("category", example.category)
    metadata.setdefault("description", example.description)
    metadata.setdefault("conversation", example.conversation)
    payload["metadata"] = metadata
    return SemanticTransitionCandidate.from_mapping(payload)
