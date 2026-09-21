from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.decision_layer.schema import DecisionDatasetCase, DecisionLabel, GroundTruth, Provenance
from experiments.decision_layer.validation import DecisionDatasetValidationError, validate_decision_case


def _case(label: DecisionLabel = DecisionLabel.ACCEPT) -> DecisionDatasetCase:
    return DecisionDatasetCase(
        case_id="case_001",
        dataset_version="decision_dataset.v1",
        state_before={"content": "x"},
        candidate_transition={"delta": "y"},
        evidence={"strength": 0.9},
        governance_context={"authority": {"allow_mutation": True}},
        ground_truth=GroundTruth(label, "test"),
        scenario_id="scenario",
        group_id="group",
        provenance=Provenance("test", "case_001"),
    )


class DecisionDatasetSchemaTests(unittest.TestCase):
    def test_valid_accept_reject_review(self) -> None:
        for label in (DecisionLabel.ACCEPT, DecisionLabel.REJECT, DecisionLabel.REVIEW):
            validate_decision_case(_case(label))

    def test_missing_required_field(self) -> None:
        payload = _case().as_dict()
        payload.pop("state_before")
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(payload)

    def test_invalid_label(self) -> None:
        payload = _case().as_dict()
        payload["ground_truth"]["canonical_label"] = "ABSTAIN"
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(payload)

    def test_missing_provenance(self) -> None:
        payload = _case().as_dict()
        payload["provenance"] = {"source_type": "test"}
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(payload)

    def test_missing_group_id(self) -> None:
        payload = _case().as_dict()
        payload["group_id"] = ""
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(payload)

    def test_training_input_excludes_ground_truth_and_replay_fields(self) -> None:
        case = _case()
        training_input = case.training_input()
        self.assertNotIn("ground_truth", training_input)
        self.assertNotIn("expected_state_after", training_input)
        self.assertNotIn("actual_state_after", training_input)
        self.assertNotIn("replay", training_input)
        self.assertNotIn("evaluation", training_input)

    def test_unlabeled_is_not_a_canonical_label(self) -> None:
        with self.assertRaises(ValueError):
            DecisionLabel("UNLABELED")

    def test_fixture_cases_validate(self) -> None:
        fixture_path = Path("data/decision_layer/fixtures/canonical_cases.jsonl")
        labels = []
        for line in fixture_path.read_text(encoding="utf-8").splitlines():
            payload = json.loads(line)
            validate_decision_case(payload)
            labels.append(payload["ground_truth"]["canonical_label"])
        self.assertIn("ACCEPT", labels)
        self.assertIn("REJECT", labels)
        self.assertIn("REVIEW", labels)


if __name__ == "__main__":
    unittest.main()
