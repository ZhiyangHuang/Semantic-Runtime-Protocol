import unittest
import os
from pathlib import Path

from srp_experiment.srp.pipeline import run_srp
from srp_experiment.srp.compress import chunk_memory, compress_state
from srp_experiment.srp.encoder import build_encoder
from srp_experiment.srp.export import flatten_record_for_csv, write_records_csv
from srp_experiment.srp.semantic_parser import canonicalize_semantic_value, stable_semantic_object_id
from srp_experiment.srp.saliency import rank_memory_chunks
from srp_experiment.srp.state import SemanticObjectMetadata, SemanticState
from srp_experiment.srp.recover import recover_state
from srp_experiment.srp.recover_runtime import budget_recovery_inputs, recover_memory_from_package
from srp_experiment.srp.state_lifecycle import apply_object_lifecycle as apply_object_lifecycle_rule
from srp_experiment.srp.state_summaries import (
    build_object_update_summary_flat,
    build_recovery_template_summary_flat,
    build_state_continuity_summary,
    lifecycle_summary_flat,
)
from srp_experiment.srp.validate import validate_state
from srp_experiment.srp.validation_failure_summary import (
    assess_drift_risk,
    build_failure_summary,
    build_failure_summary_flat,
    detect_answer_leakage,
)
from srp_experiment.srp.validation_targets import build_validation_targets
from srp_experiment.srp.compress_parse import parse_compressed_payload
from srp_experiment.srp.object_retention import build_object_retention_breakdown, build_object_retention_breakdown_v2
from srp_experiment.srp.repair import build_repair_package
from srp_experiment.srp.state_allocation import build_state_allocation_policy


class TestSRPRuntime(unittest.TestCase):
# Core runtime coverage only. Legacy query_expectations-based coverage lives in test_srp_runtime_legacy_compat.py.
    def test_canonicalization_equivalences(self):
        self.assertEqual(canonicalize_semantic_value("May 2026"), canonicalize_semantic_value("5/2026"))
        self.assertEqual(canonicalize_semantic_value("NYC"), canonicalize_semantic_value("New York City"))
        self.assertEqual(canonicalize_semantic_value("Prof."), canonicalize_semantic_value("Professor"))
        self.assertEqual(canonicalize_semantic_value("CS"), canonicalize_semantic_value("Computer Science"))
        self.assertGreaterEqual(
            validate_state(
                "May 2026",
                "5/2026",
                build_validation_targets(
                    {
                        "id": "canon",
                        "initial_state": {"constraints": ["May 2026"], "memory": "May 2026"},
                        "query_expectations": [[["May 2026"]]],
                        "expected_keywords": [],
                    }
                ),
            )["coverage_score"],
            0.99,
        )


    def test_stable_object_id_depends_on_type(self):
        same_value = "shared value"
        self.assertEqual(stable_semantic_object_id("fact", same_value), stable_semantic_object_id("fact", same_value))
        self.assertNotEqual(stable_semantic_object_id("fact", same_value), stable_semantic_object_id("anchor", same_value))


    def test_runtime_metadata_and_history_update(self):
        state = SemanticState(
            memory="A constraint and one fact.",
            constraints=["Preserve the constraint."],
        )
        metadata = state.ensure_runtime_metadata()
        self.assertTrue(metadata)
        validation = {
            "object_alignment": {
                "constraint": {
                    "matches": [
                        {
                            "object_type": "constraint",
                            "source_value": "Preserve the constraint.",
                            "recovered_value": "Preserve the constraint.",
                            "similarity": 1.0,
                            "source_object_id": stable_semantic_object_id("constraint", "Preserve the constraint."),
                        }
                    ]
                },
                "fact": {"matches": []},
                "anchor": {"matches": []},
            },
            "coverage_score": 1.0,
            "drift": 0.0,
            "alignment_score": 1.0,
            "passed": True,
        }
        state.observe_verification(validation, committed=True)
        self.assertEqual(state.round_id, 1)
        self.assertEqual(len(state.history), 1)
        self.assertGreaterEqual(state.runtime_metadata[stable_semantic_object_id("constraint", "Preserve the constraint.")].verification_passes, 1)
        self.assertIn(
            state.runtime_metadata[stable_semantic_object_id("constraint", "Preserve the constraint.")].lifecycle_state,
            {"active", "retained", "decayed", "archived"},
        )
        self.assertIn("object_update_summary", state.as_dict())
        self.assertEqual(state.as_dict()["object_update_summary"]["schema_version"], "object_update_summary.v1")
        self.assertIn("object_update_summary_flat", state.as_dict())
        self.assertEqual(state.as_dict()["object_update_summary_flat"], None)


    def test_lifecycle_thresholds_follow_policy(self):
        state = SemanticState(
            memory="Keep the key fact.",
            constraints=["Keep the key fact."],
            policy={
                "lifecycle_retained_importance": 0.95,
                "lifecycle_retained_passes": 4,
                "lifecycle_archived_importance": 0.2,
                "lifecycle_archived_drift_count": 10,
                "lifecycle_archived_failure_count": 10,
                "lifecycle_decayed_floor": 0.01,
                "lifecycle_decayed_multiplier": 0.5,
            },
        )
        state.ensure_runtime_metadata()
        metadata = next(iter(state.runtime_metadata.values()))
        metadata.importance = 0.4
        metadata.verification_passes = 1
        metadata.verification_failures = 0
        metadata.drift_count = 0
        state.round_id = 1
        result = state.apply_object_lifecycle()
        self.assertEqual(result["retained"], 0)
        self.assertEqual(result["archived"], 0)
        self.assertEqual(metadata.lifecycle_state, "decayed")
        self.assertLess(metadata.importance, 0.4)


    def test_importance_updates_increase_on_stable_passes_and_drop_on_drift(self):
        state = SemanticState(memory="Keep the key fact.", constraints=["Keep the key fact."])
        state.ensure_runtime_metadata()
        metadata = next(iter(state.runtime_metadata.values()))
        metadata.importance = 0.6
        metadata.confidence = 0.8
        metadata.verification_passes = 3
        metadata.verification_failures = 0
        metadata.drift_count = 0
        stable_before = metadata.importance
        state.update_importance()
        self.assertGreaterEqual(metadata.importance, stable_before)
        self.assertGreaterEqual(metadata.confidence, 0.0)

        metadata.importance = 0.9
        metadata.confidence = 0.9
        metadata.verification_passes = 1
        metadata.verification_failures = 3
        metadata.drift_count = 2
        drifting_before = metadata.importance
        drifting_confidence_before = metadata.confidence
        state.update_importance()
        self.assertLessEqual(metadata.importance, drifting_before)
        self.assertLessEqual(metadata.confidence, drifting_confidence_before)
        self.assertGreaterEqual(metadata.importance, 0.0)
        self.assertLessEqual(metadata.importance, 1.0)


    def test_policy_spec_includes_lifecycle_schema(self):
        state = SemanticState(memory="Keep the key fact.")
        state_dict = state.as_dict()
        self.assertIn("policy_spec", state_dict)
        self.assertIn("policy_flat", state_dict)
        self.assertEqual(state_dict["policy_spec"]["schema_version"], "policy_spec.v1")
        self.assertEqual(state_dict["policy_flat"]["schema_version"], "policy_spec_flat.v1")
        self.assertIn("lifecycle", state_dict["policy_spec"])
        self.assertIn("lifecycle_retained_importance", state_dict["policy_spec"]["lifecycle"])
        self.assertIn("meaning", state_dict["policy_spec"]["lifecycle"]["lifecycle_retained_importance"])
        self.assertIn("lifecycle_retained_importance", state_dict["policy_flat"])


    def test_encoder_factory_respects_configuration(self):
        previous_encoder = os.environ.get("SRP_ENCODER")
        previous_model = os.environ.get("SRP_ENCODER_MODEL")
        try:
            os.environ["SRP_ENCODER"] = "none"
            self.assertIsNone(build_encoder())
            os.environ["SRP_ENCODER"] = "hashing"
            encoder = build_encoder()
            self.assertIsNotNone(encoder)
            self.assertEqual(encoder.name, "hashing")
            self.assertEqual(encoder.dimension, 256)
            self.assertEqual(len(encoder.encode_passage("hello")), 256)
        finally:
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder
            if previous_model is None:
                os.environ.pop("SRP_ENCODER_MODEL", None)
            else:
                os.environ["SRP_ENCODER_MODEL"] = previous_model


    def test_state_vector_decay_uses_environment_configuration(self):
        previous_encoder = os.environ.get("SRP_ENCODER")
        previous_decay = os.environ.get("SRP_STATE_DECAY")
        try:
            os.environ["SRP_ENCODER"] = "hashing"
            os.environ["SRP_STATE_DECAY"] = "0.5"
            state = SemanticState(memory="Keep the key fact.", constraints=["Keep the key fact."])
            state.ensure_runtime_metadata()
            first = state.ensure_state_vector()
            self.assertIsNotNone(first)
            self.assertEqual(len(first), 256)
            state.memory = "Keep the key fact and the key constraint."
            second = state.ensure_state_vector()
            self.assertIsNotNone(second)
            self.assertEqual(len(second), 256)
            self.assertAlmostEqual(sum(value * value for value in second), 1.0, places=5)
        finally:
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder
            if previous_decay is None:
                os.environ.pop("SRP_STATE_DECAY", None)
            else:
                os.environ["SRP_STATE_DECAY"] = previous_decay


    def test_object_retention_breakdown_separates_retained_missing_and_hallucinated(self):
        source_inventory = {
            "important_objects": [
                {
                    "object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                    "type": "constraint",
                    "value": "Preserve the key constraint.",
                    "confidence": 1.0,
                    "evidence_pointer": "constraint:1",
                },
                {
                    "object_id": stable_semantic_object_id("fact", "The answer is B."),
                    "type": "fact",
                    "value": "The answer is B.",
                    "confidence": 0.9,
                    "evidence_pointer": "memory:2",
                },
            ]
        }
        recovered_package = {
            "typed_representation": {
                "objects": [
                    {
                        "type": "constraint",
                        "value": "Preserve the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                        "metadata": {},
                    },
                    {
                        "type": "query_expectation",
                        "value": "Preserve the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "query:1",
                        "metadata": {},
                    },
                    {
                        "type": "fact",
                        "value": "Recovered extra detail.",
                        "confidence": 0.6,
                        "evidence_pointer": "memory:3",
                        "metadata": {},
                    },
                ]
            }
        }
        breakdown = build_object_retention_breakdown(source_inventory, recovered_package)
        self.assertEqual(breakdown.schema_version, "object_retention_breakdown.v1")
        self.assertEqual(len(breakdown.retained), 1)
        self.assertEqual(len(breakdown.missing), 1)
        self.assertEqual(len(breakdown.hallucinated), 2)
        self.assertEqual(breakdown.retained[0]["type"], "constraint")
        self.assertEqual(breakdown.missing[0]["type"], "fact")
        self.assertEqual({item["type"] for item in breakdown.hallucinated}, {"query_expectation", "fact"})
        self.assertIn("Recovered extra detail.", {item["value"] for item in breakdown.hallucinated})


    def test_object_retention_breakdown_v2_separates_three_views(self):
        task = {
            "id": "retention-v2-task",
            "initial_state": {
                "constraints": ["Preserve the key constraint."],
                "memory": "Preserve the key constraint. The answer is B.",
            },
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": ["constraint", "answer"],
        }
        source_inventory = {
            "objects": [
                {
                    "object_id": stable_semantic_object_id("fact", "Preserve the key constraint."),
                    "type": "fact",
                    "value": "Preserve the key constraint.",
                    "confidence": 0.65,
                    "evidence_pointer": "memory:1",
                },
                {
                    "object_id": stable_semantic_object_id("fact", "The answer is B."),
                    "type": "fact",
                    "value": "The answer is B.",
                    "confidence": 0.65,
                    "evidence_pointer": "memory:2",
                },
            ],
            "important_objects": [
                {
                    "object_id": stable_semantic_object_id("fact", "Preserve the key constraint."),
                    "type": "fact",
                    "value": "Preserve the key constraint.",
                    "confidence": 0.65,
                    "evidence_pointer": "memory:1",
                }
            ],
        }
        recovered_package = {
            "typed_representation": {
                "objects": [
                    {
                        "type": "fact",
                        "value": "Preserve the key constraint.",
                        "confidence": 0.9,
                        "evidence_pointer": "memory:1",
                        "metadata": {},
                    },
                    {
                        "type": "constraint",
                        "value": "Preserve the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                        "metadata": {},
                    },
                    {
                        "type": "query_expectation",
                        "value": "Preserve the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "query:1",
                        "metadata": {},
                    },
                    {
                        "type": "fact",
                        "value": "Recovered extra detail.",
                        "confidence": 0.6,
                        "evidence_pointer": "memory:3",
                        "metadata": {},
                    },
                ]
            }
        }
        breakdown = build_object_retention_breakdown_v2(
            source_inventory,
            recovered_package,
            build_validation_targets(task),
        )
        self.assertEqual(breakdown.schema_version, "object_retention_breakdown.v2")
        self.assertIn("important", breakdown.as_dict())
        self.assertIn("all_objects", breakdown.as_dict())
        self.assertIn("task_critical", breakdown.as_dict())
        self.assertGreaterEqual(breakdown.important["retained_count"], 1)
        self.assertGreaterEqual(breakdown.all_objects["retained_count"], 1)
        self.assertGreaterEqual(breakdown.task_critical["retained_count"], 1)




if __name__ == "__main__":
    unittest.main()
