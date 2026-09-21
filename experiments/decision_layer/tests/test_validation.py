from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.decision_layer.schema import DecisionDatasetCase, DecisionLabel, GroundTruth, Provenance
from experiments.decision_layer.validation import (
    DecisionDatasetValidationError,
    validate_decision_case,
    validate_split_manifest,
)


def _case_with_nested_input(**overrides) -> DecisionDatasetCase:
    return DecisionDatasetCase(
        case_id="nested_case",
        dataset_version="decision_dataset.v1",
        state_before={"content": "x"},
        candidate_transition=overrides.get("candidate_transition", {"delta": "y"}),
        evidence=overrides.get("evidence", {"evidence_score": 0.92}),
        governance_context=overrides.get("governance_context", {"authority": {"allow_mutation": True}}),
        ground_truth=GroundTruth(DecisionLabel.ACCEPT, "test"),
        scenario_id="scenario",
        group_id="group",
        provenance=Provenance("test", "nested_case"),
        observation=overrides.get("observation"),
        replay=overrides.get("replay", {}),
    )


class DecisionDatasetValidationTests(unittest.TestCase):
    def test_legal_nested_evidence_score_passes(self) -> None:
        validate_decision_case(
            _case_with_nested_input(
                evidence={
                    "source": "conversation",
                    "evidence_score": 0.91,
                    "support_scores": [{"name": "semantic_support", "score": 0.88}],
                }
            )
        )

    def test_nested_canonical_label_is_rejected(self) -> None:
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(
                _case_with_nested_input(evidence={"source": "bad", "canonical_label": "ACCEPT"})
            )

    def test_nested_expected_accepted_decision_fields_are_rejected(self) -> None:
        bad_values = [
            {"expected": {"commit": True}},
            {"accepted": True},
            {"decision": "APPROVE"},
        ]
        for candidate_transition in bad_values:
            with self.subTest(candidate_transition=candidate_transition):
                with self.assertRaises(DecisionDatasetValidationError):
                    validate_decision_case(_case_with_nested_input(candidate_transition=candidate_transition))

    def test_nested_replay_evaluation_metrics_timing_are_rejected(self) -> None:
        bad_contexts = [
            {"replay": {"trace": "x"}},
            {"evaluation": {"result": "x"}},
            {"metrics": {"accuracy": 1.0}},
            {"timing": {"total_ms": 1.0}},
        ]
        for governance_context in bad_contexts:
            with self.subTest(governance_context=governance_context):
                with self.assertRaises(DecisionDatasetValidationError):
                    validate_decision_case(_case_with_nested_input(governance_context=governance_context))

    def test_direct_tuple_leakage_is_rejected(self) -> None:
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(_case_with_nested_input(evidence={"x": ({"expected": True},)}))

    def test_nested_tuple_leakage_is_rejected(self) -> None:
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(_case_with_nested_input(evidence={"x": [({"canonical_label": "ACCEPT"},)]}))

    def test_deep_mixed_tuple_leakage_is_rejected(self) -> None:
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(
                _case_with_nested_input(
                    candidate_transition={
                        "a": [
                            (
                                {
                                    "b": [
                                        {"decision": "REJECT"},
                                    ]
                                },
                            )
                        ]
                    }
                )
            )

    def test_tuple_without_leakage_is_accepted(self) -> None:
        validate_decision_case(_case_with_nested_input(evidence={"sources": ("source_a", "source_b")}))

    def test_tuple_with_legitimate_evidence_values_is_accepted(self) -> None:
        validate_decision_case(_case_with_nested_input(evidence={"scores": (0.7, 0.8)}))

    def test_top_level_leakage_protection_continues_for_training_input_payload(self) -> None:
        payload = _case_with_nested_input().as_dict()
        payload["training_input"] = {
            "state_before": {"content": "x"},
            "candidate_transition": {"delta": "y"},
            "ground_truth": {"canonical_label": "ACCEPT"},
        }
        with self.assertRaises(DecisionDatasetValidationError):
            validate_decision_case(payload)

    def test_split_manifest_accepts_unique_groups(self) -> None:
        manifest = json.loads(Path("data/decision_layer/fixtures/split_manifest.json").read_text(encoding="utf-8"))
        validate_split_manifest(manifest)

    def test_split_manifest_rejects_group_leakage(self) -> None:
        manifest = {
            "dataset_version": "decision_dataset.v1",
            "seed": 0,
            "grouping_key": "group_id",
            "train": ["shared_group"],
            "validation": [],
            "test": ["shared_group"],
        }
        with self.assertRaises(DecisionDatasetValidationError):
            validate_split_manifest(manifest)

    def test_review_is_valid_but_not_runtime_approve(self) -> None:
        fixture_path = Path("data/decision_layer/fixtures/canonical_cases.jsonl")
        review_cases = [
            json.loads(line)
            for line in fixture_path.read_text(encoding="utf-8").splitlines()
            if json.loads(line)["ground_truth"]["canonical_label"] == DecisionLabel.REVIEW.value
        ]
        self.assertEqual(len(review_cases), 1)
        review_case = review_cases[0]
        self.assertEqual(review_case["ground_truth"]["canonical_label"], "REVIEW")
        self.assertTrue(review_case["annotations"]["review_routing_only"])
        self.assertFalse(review_case["annotations"]["runtime_review_claim"])

    def test_evidence_is_not_governance_authority(self) -> None:
        fixture_path = Path("data/decision_layer/fixtures/canonical_cases.jsonl")
        reject_cases = [
            json.loads(line)
            for line in fixture_path.read_text(encoding="utf-8").splitlines()
            if json.loads(line)["case_id"] == "canonical_reject_001"
        ]
        self.assertEqual(len(reject_cases), 1)
        case = reject_cases[0]
        self.assertEqual(case["evidence"]["confidence"], 0.98)
        self.assertFalse(case["governance_context"]["authority"]["allowed_mutation"])
        self.assertEqual(case["ground_truth"]["canonical_label"], "REJECT")


if __name__ == "__main__":
    unittest.main()
