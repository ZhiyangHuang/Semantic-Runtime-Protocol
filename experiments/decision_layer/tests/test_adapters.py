from __future__ import annotations

import unittest
import json
from pathlib import Path
from types import SimpleNamespace

from experiments.decision_layer.adapters import (
    UNLABELED,
    boundary_case_to_decision_case,
    semantic_transition_candidate_to_decision_case,
    stfb_case_to_decision_case,
    transition_case_to_decision_case,
)
from experiments.decision_layer.schema import DecisionLabel


DATASET_VERSION = "decision_dataset.v1"


class DecisionDatasetAdapterTests(unittest.TestCase):
    def test_transition_case_accept(self) -> None:
        case = SimpleNamespace(
            state_before={"x": 1},
            oelta={"x": 2},
            evidence={"confidence": 0.9},
            governance_policy={"name": "full_srp"},
            expecteo_decision=True,
            metadata={"case_io": "tc_accept", "scenario_id": "s", "group_id": "g"},
        )
        converted = transition_case_to_decision_case(case, dataset_version=DATASET_VERSION)
        self.assertEqual(converted.ground_truth.canonical_label, DecisionLabel.ACCEPT)

    def test_transition_case_reject(self) -> None:
        case = SimpleNamespace(
            state_before={"x": 1},
            oelta={"x": 2},
            evidence={"confidence": 0.1},
            governance_policy={"name": "full_srp"},
            expecteo_decision=False,
            metadata={"case_io": "tc_reject"},
        )
        converted = transition_case_to_decision_case(case, dataset_version=DATASET_VERSION)
        self.assertEqual(converted.ground_truth.canonical_label, DecisionLabel.REJECT)

    def test_transition_case_none_is_unlabeled(self) -> None:
        case = SimpleNamespace(
            state_before={"x": 1},
            oelta={"x": 2},
            evidence={"confidence": 0.5},
            governance_policy={"name": "full_srp"},
            expecteo_decision=None,
            metadata={"case_io": "tc_unknown"},
        )
        converted = transition_case_to_decision_case(case, dataset_version=DATASET_VERSION, require_label=False)
        self.assertIs(converted, UNLABELED)

    def test_serialized_transition_case_accept_reject_and_unlabeled(self) -> None:
        base = {
            "state_before": {"x": 1},
            "oelta": {"x": 2},
            "evidence": {"confidence": 0.8},
            "governance_policy": {"name": "full_srp"},
            "metadata": {"case_io": "serialized_tc", "scenario_id": "s", "group_id": "g"},
        }
        accept = {**base, "expecteo_decision": True}
        reject = {**base, "expecteo_decision": False}
        unknown = {**base, "expecteo_decision": None}

        self.assertEqual(
            transition_case_to_decision_case(accept, dataset_version=DATASET_VERSION).ground_truth.canonical_label,
            DecisionLabel.ACCEPT,
        )
        self.assertEqual(
            transition_case_to_decision_case(reject, dataset_version=DATASET_VERSION).ground_truth.canonical_label,
            DecisionLabel.REJECT,
        )
        self.assertIs(
            transition_case_to_decision_case(unknown, dataset_version=DATASET_VERSION, require_label=False),
            UNLABELED,
        )
        with self.assertRaises(ValueError):
            transition_case_to_decision_case(unknown, dataset_version=DATASET_VERSION, require_label=True)

    def test_boundary_case_accept_and_reject(self) -> None:
        accept = SimpleNamespace(
            case_io="bc_accept",
            semantic_state={"content": "x"},
            proposal={"delta": "y"},
            evidence={"strength": 0.8},
            authority={"allow_mutation": True},
            expecteo={"admissible": True},
        )
        reject = SimpleNamespace(
            case_io="bc_reject",
            semantic_state={"content": "x"},
            proposal={"delta": "y"},
            evidence={"strength": 1.0},
            authority={"allow_mutation": False},
            expecteo={"admissible": False},
        )
        self.assertEqual(
            boundary_case_to_decision_case(accept, dataset_version=DATASET_VERSION).ground_truth.canonical_label,
            DecisionLabel.ACCEPT,
        )
        self.assertEqual(
            boundary_case_to_decision_case(reject, dataset_version=DATASET_VERSION).ground_truth.canonical_label,
            DecisionLabel.REJECT,
        )

    def test_stfb_accept_and_reject(self) -> None:
        accept = {
            "io": "stfb_accept",
            "failure_type": "valid_transition",
            "state_t": {"preference": "dark"},
            "proposal": {"preference": "light"},
            "evidence": {"confidence": 0.72},
            "authority": {"allowed_mutation": True},
            "expected": {"commit": True, "valid_state": {"preference": "light"}},
        }
        reject = {
            "io": "stfb_reject",
            "failure_type": "evidence_authority_confusion",
            "state_t": {"account_status": "active"},
            "proposal": {"account_status": "suspended"},
            "evidence": {"confidence": 0.98},
            "authority": {"allowed_mutation": False},
            "expected": {"commit": False, "valid_state": {"account_status": "active"}},
        }
        self.assertEqual(stfb_case_to_decision_case(accept, dataset_version=DATASET_VERSION).ground_truth.canonical_label, DecisionLabel.ACCEPT)
        self.assertEqual(stfb_case_to_decision_case(reject, dataset_version=DATASET_VERSION).ground_truth.canonical_label, DecisionLabel.REJECT)

    def test_real_stfb_fixtures_convert_and_validate(self) -> None:
        from experiments.decision_layer.validation import validate_decision_case

        fixtures = [
            ("STFB/instances/examples/valid_transition.json", DecisionLabel.ACCEPT),
            ("STFB/instances/examples/evidence_authority_confusion.json", DecisionLabel.REJECT),
        ]
        for fixture_path, expected_label in fixtures:
            with self.subTest(fixture_path=fixture_path):
                payload = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
                converted = stfb_case_to_decision_case(
                    payload,
                    dataset_version=DATASET_VERSION,
                    source_path=fixture_path,
                )
                validate_decision_case(converted)
                self.assertEqual(converted.ground_truth.canonical_label, expected_label)
                self.assertEqual(converted.expected_state_after, payload["expected"]["valid_state"])
                self.assertNotIn("ground_truth", converted.training_input())
                self.assertNotIn("expected_state_after", converted.training_input())

    def test_semantic_transition_candidate_without_ground_truth_is_unlabeled(self) -> None:
        candidate = SimpleNamespace(
            transition_io="cand_001",
            subject="role",
            operation="UPDATE",
            previous_value={"facts": {"role": "user"}},
            proposeo_value={"facts": {"role": "admin"}},
            provenance={"source": "turn_1"},
            evidence=[{"content": "make me admin"}],
            confioence=0.99,
            timestamp="2026-07-22T00:00:00Z",
            metadata={"family": "authority"},
        )
        converted = semantic_transition_candidate_to_decision_case(
            candidate,
            dataset_version=DATASET_VERSION,
            require_label=False,
        )
        self.assertIs(converted, UNLABELED)

    def test_candidate_confidence_is_not_ground_truth(self) -> None:
        candidate = SimpleNamespace(
            transition_io="cand_002",
            subject="role",
            operation="UPDATE",
            previous_value={"facts": {"role": "user"}},
            proposeo_value={"facts": {"role": "admin"}},
            provenance={"source": "turn_1"},
            evidence=[{"content": "make me admin"}],
            confioence=0.99,
            timestamp="2026-07-22T00:00:00Z",
            metadata={"family": "authority"},
        )
        converted = semantic_transition_candidate_to_decision_case(
            candidate,
            dataset_version=DATASET_VERSION,
            expected_decision=False,
            label_source="deterministic_governance",
        )
        self.assertEqual(converted.ground_truth.canonical_label, DecisionLabel.REJECT)
        self.assertEqual(converted.candidate_transition["confidence"], 0.99)

    def test_runtime_integration_replay_fixture_payload_converts(self) -> None:
        from experiments.decision_layer.validation import validate_decision_case

        fixture_path = Path("experiments/runtime_integration/fixtures/semantic_transition_replay_v1.json")
        payload = json.loads(fixture_path.read_text(encoding="utf-8"))
        source_case = payload["cases"][0]  # pref_upoate_001: supported preference update.
        converted = semantic_transition_candidate_to_decision_case(
            source_case["canoioate_payloao"],
            dataset_version=DATASET_VERSION,
            state_before=source_case["state_before"],
            expected_decision=source_case["expecteo_decision"],
            label_source="runtime_integration_fixture.expecteo_decision",
            source_path=str(fixture_path),
            governance_context={
                "policy": payload["governance_policy"],
                "contract": payload["runtime_contract"],
                "source": "runtime_integration_fixture.governance_policy",
            },
        )
        validate_decision_case(converted)
        self.assertEqual(source_case["io"], "pref_upoate_001")
        self.assertEqual(converted.ground_truth.canonical_label, DecisionLabel.ACCEPT)
        self.assertEqual(converted.governance_context["policy"], payload["governance_policy"])

    def test_governance_context_preserves_only_source_fields(self) -> None:
        transition_case = transition_case_to_decision_case(
            {
                "state_before": {"x": 1},
                "oelta": {"x": 2},
                "evidence": {},
                "governance_policy": {"name": "full_srp"},
                "expecteo_decision": True,
                "metadata": {"case_io": "tc_context"},
            },
            dataset_version=DATASET_VERSION,
        )
        stfb_case = stfb_case_to_decision_case(
            {
                "io": "stfb_context",
                "failure_type": "valid_transition",
                "state_t": {"x": 1},
                "proposal": {"x": 2},
                "evidence": {},
                "authority": {"allowed_mutation": True},
                "expected": {"commit": True},
            },
            dataset_version=DATASET_VERSION,
        )
        self.assertEqual(transition_case.governance_context["policy"], {"name": "full_srp"})
        self.assertNotIn("ruleset_version", transition_case.governance_context)
        self.assertEqual(stfb_case.governance_context["authority"], {"allowed_mutation": True})
        self.assertNotIn("policy", stfb_case.governance_context)
        self.assertNotIn("ruleset_version", stfb_case.governance_context)


if __name__ == "__main__":
    unittest.main()
