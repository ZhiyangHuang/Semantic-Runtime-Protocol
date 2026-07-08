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

    def test_validate_state_flags_critical_failure(self):
        task = {
            "id": "unit",
            "initial_state": {"constraints": ["Preserve the key constraint."], "memory": "Preserve the key constraint."},
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": [],
        }
        validation = validate_state(
            "Preserve the key constraint.",
            "irrelevant output",
            build_validation_targets(task),
            runtime_metadata={
                stable_semantic_object_id("constraint", "Preserve the key constraint."): SemanticObjectMetadata(
                    importance=0.9
                )
            },
        )
        self.assertFalse(validation["passed"])
        self.assertTrue(validation["critical_failures"])
        self.assertIn("failure_summary", validation)
        self.assertEqual(validation["failure_summary"]["schema_version"], "failure_summary.v1")
        self.assertIn("failure_summary_flat", validation)
        self.assertEqual(validation["failure_summary_flat"]["schema_version"], "failure_summary_flat.v1")
        self.assertIn("critical_failure_count", validation["failure_summary"])
        self.assertIn("blocks_commit", validation["failure_summary"])
        self.assertIn("critical_failure_object_id_joined", validation["failure_summary_flat"])
        self.assertIn("critical_failure_type_count", validation["failure_summary_flat"])
        self.assertIn("critical_failure_type_labels", validation["failure_summary_flat"])
        self.assertIn("leakage_match_count", validation["failure_summary_flat"])
        self.assertIn("leakage_matches_joined", validation["failure_summary_flat"])

    def test_validate_state_reports_coverage_weights(self):
        task = {
            "id": "coverage-task",
            "initial_state": {"constraints": ["Preserve the key constraint."], "memory": "Preserve the key constraint."},
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": ["constraint"],
        }
        validation = validate_state(
            "Preserve the key constraint.",
            "Preserve the key constraint.",
            build_validation_targets(task),
            runtime_metadata={
                stable_semantic_object_id("constraint", "Preserve the key constraint."): SemanticObjectMetadata(
                    importance=0.9
                )
            },
        )
        self.assertIn("coverage_details", validation)
        self.assertIn("constraint", validation["coverage_details"])
        self.assertIn("average_importance", validation["coverage_details"]["constraint"])
        self.assertIn("average_effective_weight", validation["coverage_details"]["constraint"])

    def test_validate_state_similarity_stays_low_for_unrelated_text(self):
        task = {
            "id": "unrelated-task",
            "initial_state": {"constraints": ["Preserve the key constraint."], "memory": "Preserve the key constraint."},
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": [],
        }
        validation = validate_state(
            "Preserve the key constraint.",
            "Completely unrelated weather report with different entities.",
            build_validation_targets(task),
        )
        self.assertLess(validation["coverage_score"], 0.7)

    def test_validate_state_without_metadata_uses_legacy_weighting_path(self):
        task = {
            "id": "legacy-weight-task",
            "initial_state": {"constraints": ["Preserve the key constraint."], "memory": "Preserve the key constraint."},
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": ["constraint"],
        }
        validation = validate_state(
            "Preserve the key constraint.",
            "Preserve the key constraint.",
            build_validation_targets(task),
            runtime_metadata=None,
        )
        self.assertGreaterEqual(validation["coverage_score"], 0.99)
        self.assertIn("constraint", validation["coverage_details"])

    def test_validate_state_uses_structured_recovery_package_for_alignment(self):
        task = {
            "id": "structured-package-task",
            "initial_state": {
                "constraints": ["Preserve the key constraint."],
                "memory": "Preserve the key constraint. The answer is B.",
            },
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": ["constraint", "answer"],
        }
        validation = validate_state(
            "Preserve the key constraint. The answer is B.",
            "Recovered placeholder text.",
            build_validation_targets(task),
            recovered_state_package={
                "typed_representation": {
                    "objects": [
                        {
                            "type": "fact",
                            "value": "Preserve the key constraint",
                            "confidence": 0.9,
                            "evidence_pointer": "memory:0",
                            "metadata": {},
                        },
                        {
                            "type": "fact",
                            "value": "The answer is B",
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
                    ]
                }
            },
        )
        self.assertGreaterEqual(validation["alignment_score"], 0.5)
        self.assertEqual(validation["typed_validation"]["recovered"]["objects"][0]["type"], "fact")

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

    def test_pipeline_repair_loop_uses_structured_package(self):
        previous_encoder = os.environ.get("SRP_ENCODER")
        try:
            os.environ["SRP_ENCODER"] = "none"
            task = {
                "id": "repair-loop-task",
                "initial_state": {
                    "constraints": ["Preserve the key constraint."],
                    "memory": "Preserve the key constraint. The answer is B.",
                },
                "query_expectations": [[["Preserve the key constraint."]]],
                "expected_keywords": ["constraint", "answer"],
            }

            class FailingThenStructuredClient:
                def __init__(self):
                    self.calls = 0

                def generate_with_usage(self, prompt, **kwargs):
                    self.calls += 1
                    if "Compress semantic state" in prompt:
                        return {
                            "text": '{"memory_summary":"The answer is B.","constraints":["Preserve the key constraint."],"anchor_terms":["answer","constraint"],"loss_risks":[]}',
                            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                            "raw_text": '{"memory_summary":"The answer is B.","constraints":["Preserve the key constraint."],"anchor_terms":["answer","constraint"],"loss_risks":[]}',
                            "stripped_thinking": None,
                        }
                    if "Recover concise semantic state." in prompt:
                        return {
                            "text": "Preserve the key constraint. The answer is B.",
                            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                            "raw_text": "Preserve the key constraint. The answer is B.",
                            "stripped_thinking": None,
                        }
                    return {
                        "text": "Preserve the key constraint. The answer is B.",
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                        "raw_text": "Preserve the key constraint. The answer is B.",
                        "stripped_thinking": None,
                    }

            records = run_srp(task, cycles=1, client=FailingThenStructuredClient())
            self.assertEqual(len(records), 1)
            self.assertIn("recovery_template_summary", records[0])
            self.assertIn("structured_state_package_present", records[0]["recovery_template_summary"])
            self.assertIn("recovered_state_package", records[0])
            self.assertIn("repair_context", records[0])
            self.assertIn("repair_context_flat", records[0])
        finally:
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder

    def test_task_critical_filter_flag_is_visible_in_repair_context(self):
        previous_filter = os.environ.get("SRP_TASK_CRITICAL_FILTER")
        try:
            os.environ["SRP_TASK_CRITICAL_FILTER"] = "true"
            task = {
                "id": "task-filter-task",
                "initial_state": {
                    "constraints": ["Preserve the key constraint."],
                    "memory": "Preserve the key constraint. The answer is B.",
                },
                "query_expectations": [[["Preserve the key constraint."]]],
                "expected_keywords": ["constraint", "answer"],
            }

            class DummyClient:
                def generate_with_usage(self, *args, **kwargs):
                    return {
                        "text": '{"memory_summary":"Preserve the key constraint.","constraints":["Preserve the key constraint."],"anchor_terms":["constraint"],"loss_risks":[]}',
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                        "raw_text": '{"memory_summary":"Preserve the key constraint.","constraints":["Preserve the key constraint."],"anchor_terms":["constraint"],"loss_risks":[]}',
                        "stripped_thinking": None,
                    }

            records = run_srp(task, cycles=1, client=DummyClient())
            self.assertEqual(len(records), 1)
            self.assertIn("repair_context", records[0])
            self.assertIn("task_critical_filter_enabled", records[0]["repair_context"])
        finally:
            if previous_filter is None:
                os.environ.pop("SRP_TASK_CRITICAL_FILTER", None)
            else:
                os.environ["SRP_TASK_CRITICAL_FILTER"] = previous_filter

    def test_repair_constraint_mode_is_reflected_in_repair_context(self):
        previous_mode = os.environ.get("SRP_REPAIR_CONSTRAINT_MODE")
        try:
            package = {
                "memory": "Preserve the key constraint. The answer is B.",
                "constraints": ["Preserve the key constraint."],
                "semantic_object_inventory": {
                    "schema_version": "semantic_object_inventory.v1",
                    "objects": [
                        {"object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."), "type": "constraint", "value": "Preserve the key constraint."},
                        {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                    ],
                    "important_objects": [
                        {"object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."), "type": "constraint", "value": "Preserve the key constraint."},
                        {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                    ],
                    "object_count": 2,
                    "important_object_count": 2,
                    "object_ids": [
                        stable_semantic_object_id("constraint", "Preserve the key constraint."),
                        stable_semantic_object_id("fact", "The answer is B."),
                    ],
                    "type_counts": {"constraint": 1, "fact": 1},
                },
                "typed_representation": {
                    "objects": [
                        {"type": "constraint", "value": "Preserve the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                        {"type": "fact", "value": "The answer is B.", "confidence": 0.6, "evidence_pointer": "memory:1"},
                    ]
                },
            }
            validation = {
                "critical_failures": [
                    {
                        "source_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                        "recovered_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                        "source_value": "Preserve the key constraint.",
                        "recovered_value": "Preserve the key constraint.",
                        "similarity": 0.2,
                        "object_type": "constraint",
                    }
                ],
                "object_alignment": {
                    "constraint": {
                        "matches": [
                            {
                                "source_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                                "recovered_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                                "source_value": "Preserve the key constraint.",
                                "recovered_value": "Preserve the key constraint.",
                                "similarity": 0.2,
                                "object_type": "constraint",
                            }
                        ]
                    }
                },
                "leakage_detected": False,
                "drift_blocks_commit": False,
            }

            os.environ["SRP_REPAIR_CONSTRAINT_MODE"] = "constrained"
            constrained = build_repair_package(package, package, validation)
            self.assertIn("repair_context", constrained)
            self.assertEqual(constrained["repair_context"]["repair_constraint_mode"], "constrained")
            self.assertEqual(constrained["repair_context_flat"]["repair_constraint_mode"], "constrained")
            self.assertEqual(constrained["structured_state_package"]["typed_representation"]["objects"], [
                {"type": "constraint", "value": "Preserve the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"}
            ])

            os.environ["SRP_REPAIR_CONSTRAINT_MODE"] = "strict"
            strict = build_repair_package(package, package, validation)
            self.assertEqual(strict["repair_context"]["repair_constraint_mode"], "strict")
            self.assertEqual(strict["repair_context_flat"]["repair_constraint_mode"], "strict")
            self.assertEqual(strict["structured_state_package"]["typed_representation"]["objects"], [
                {"type": "constraint", "value": "Preserve the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"}
            ])
        finally:
            if previous_mode is None:
                os.environ.pop("SRP_REPAIR_CONSTRAINT_MODE", None)
            else:
                os.environ["SRP_REPAIR_CONSTRAINT_MODE"] = previous_mode

    def test_repair_objective_mode_is_reflected_in_repair_context(self):
        previous_objective = os.environ.get("SRP_REPAIR_OBJECTIVE")
        previous_constraint = os.environ.get("SRP_REPAIR_CONSTRAINT_MODE")
        try:
            package = {
                "memory": "Preserve the key constraint. The answer is B.",
                "constraints": ["Preserve the key constraint."],
                "semantic_object_inventory": {
                    "schema_version": "semantic_object_inventory.v1",
                    "objects": [
                        {"object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."), "type": "constraint", "value": "Preserve the key constraint."},
                        {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                    ],
                    "important_objects": [
                        {"object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."), "type": "constraint", "value": "Preserve the key constraint."},
                        {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                    ],
                    "object_count": 2,
                    "important_object_count": 2,
                    "object_ids": [
                        stable_semantic_object_id("constraint", "Preserve the key constraint."),
                        stable_semantic_object_id("fact", "The answer is B."),
                    ],
                    "type_counts": {"constraint": 1, "fact": 1},
                },
                "typed_representation": {
                    "objects": [
                        {"type": "constraint", "value": "Preserve the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                        {"type": "fact", "value": "The answer is B.", "confidence": 0.6, "evidence_pointer": "memory:1"},
                    ]
                },
            }
            validation = {
                "critical_failures": [
                    {
                        "source_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                        "recovered_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                        "source_value": "Preserve the key constraint.",
                        "recovered_value": "Preserve the key constraint.",
                        "similarity": 0.2,
                        "object_type": "constraint",
                    }
                ],
                "object_alignment": {
                    "constraint": {
                        "matches": [
                            {
                                "source_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                                "recovered_object_id": stable_semantic_object_id("constraint", "Preserve the key constraint."),
                                "source_value": "Preserve the key constraint.",
                                "recovered_value": "Preserve the key constraint.",
                                "similarity": 0.2,
                                "object_type": "constraint",
                            }
                        ]
                    }
                },
                "leakage_detected": False,
                "drift_blocks_commit": False,
            }

            os.environ["SRP_REPAIR_CONSTRAINT_MODE"] = "constrained"
            os.environ["SRP_REPAIR_OBJECTIVE"] = "patch"
            patched = build_repair_package(package, package, validation)
            self.assertEqual(patched["repair_context"]["repair_constraint_mode"], "constrained")
            self.assertEqual(patched["repair_context"]["repair_objective"], "patch")
            self.assertEqual(patched["repair_context_flat"]["repair_objective"], "patch")
            self.assertGreaterEqual(patched["repair_context"]["repair_patch_count"], 1)
            self.assertGreaterEqual(patched["repair_context"]["repair_applied_count"], 1)
            self.assertGreaterEqual(patched["repair_context_flat"]["repair_patch_count"], 1)

            os.environ["SRP_REPAIR_OBJECTIVE"] = "minimal_patch"
            minimal = build_repair_package(package, package, validation)
            self.assertEqual(minimal["repair_context"]["repair_objective"], "minimal_patch")
            self.assertEqual(minimal["repair_context_flat"]["repair_objective"], "minimal_patch")
            self.assertLessEqual(
                minimal["repair_context"]["repair_patch_count"],
                len(validation["critical_failures"]),
            )
        finally:
            if previous_objective is None:
                os.environ.pop("SRP_REPAIR_OBJECTIVE", None)
            else:
                os.environ["SRP_REPAIR_OBJECTIVE"] = previous_objective
            if previous_constraint is None:
                os.environ.pop("SRP_REPAIR_CONSTRAINT_MODE", None)
            else:
                os.environ["SRP_REPAIR_CONSTRAINT_MODE"] = previous_constraint

    def test_state_summary_helpers_build_stable_flattened_shapes(self):
        flat = lifecycle_summary_flat(
            {
                "history_length": 2,
                "round_id": 3,
                "global_history": {"coverage_mean": 0.8, "last_passed": True},
                "per_object": {"object_count": 4, "lifecycle_state_counts": {"retained": 1}},
            }
        )
        self.assertEqual(flat["schema_version"], "lifecycle_summary_flat.v1")
        self.assertEqual(flat["history_length"], 2)
        self.assertEqual(flat["global_history_coverage_mean"], 0.8)
        self.assertEqual(flat["per_object_object_count"], 4)

        template_flat = build_recovery_template_summary_flat(
            {
                "schema_version": "recovery_template.v1",
                "sections": ["system", "compressed_memory"],
                "prompt_word_count": 42,
                "anchor_memory_word_count": 7,
            }
        )
        self.assertEqual(template_flat["schema_version"], "recovery_template_summary_flat.v1")
        self.assertEqual(template_flat["recover_prompt_word_count"], 42)
        self.assertEqual(template_flat["recover_template_sections"], ["system", "compressed_memory"])

    def test_state_continuity_summary_helper_reflects_overlap_and_history(self):
        state = SemanticState(
            memory="Keep the key fact.",
            constraints=["Keep the key fact."],
            global_vocabulary=["keep", "fact"],
            local_vocabulary=["constraint"],
        )
        package = {
            "memory": "Keep the key fact.",
            "constraints": ["Keep the key fact."],
            "global_vocab": ["keep", "fact"],
            "local_vocab": ["constraint"],
            "runtime_summary": {"history_length": 0},
            "selected_chunk_ids": [1, 2],
        }
        summary = build_state_continuity_summary(state, package, anchor_memory="Keep the key fact.")
        self.assertEqual(summary["schema_version"], "state_continuity_summary.v1")
        self.assertEqual(summary["constraint_overlap_rate"], 1.0)
        self.assertEqual(summary["vocab_overlap_rate"], 1.0)
        self.assertEqual(summary["memory_delta"], 0)

    def test_object_update_summary_flat_aggregates_counts(self):
        flat = build_object_update_summary_flat(
            {
                "schema_version": "object_update_summary.v1",
                "round_id": 2,
                "committed": False,
                "update_count": 3,
                "updates": [
                    {"source_object_id": "a", "action": "pass", "lifecycle_state": "retained", "object_type": "constraint", "similarity": 1.0},
                    {"source_object_id": "b", "action": "drift", "lifecycle_state": "decayed", "object_type": "fact", "similarity": 0.2},
                    {"source_object_id": "c", "action": "drift", "lifecycle_state": "archived", "object_type": "anchor", "similarity": 0.0},
                ],
            }
        )
        self.assertEqual(flat["schema_version"], "object_update_summary_flat.v1")
        self.assertEqual(flat["update_count_pass"], 1)
        self.assertEqual(flat["update_count_drift"], 2)
        self.assertIn("a:pass:1.0", flat["updates_joined"])

    def test_failure_summary_helpers_capture_leakage_and_labels(self):
        leakage = detect_answer_leakage("Therefore the answer is clearly 42.")
        self.assertTrue(leakage["detected"])
        risk = assess_drift_risk(1.0, 0.35, 0.2)
        self.assertEqual(risk["risk"], "high")
        summary = build_failure_summary(
            [{"source_object_id": "constraint:1", "object_type": "constraint"}],
            leakage,
            risk,
        )
        flat = build_failure_summary_flat(summary)
        self.assertEqual(summary["schema_version"], "failure_summary.v1")
        self.assertEqual(flat["schema_version"], "failure_summary_flat.v1")
        self.assertEqual(flat["critical_failure_type_labels"], ["constraint:1"])
        self.assertGreaterEqual(flat["leakage_match_count"], 1)

    def test_compress_parse_partial_json_fallback_extracts_memory_summary(self):
        state = SemanticState(
            memory="Keep the key fact.",
            constraints=["Keep the key fact."],
            global_vocabulary=["keep", "fact"],
            local_vocabulary=["constraint"],
        )
        parsed = parse_compressed_payload(
            '{"memory_summary":"Keep the key fact.","constraints":["Keep the key fact."],"anchor_terms":["fact"]',
            state,
        )
        self.assertEqual(parsed["parse_status"], "partial_json")
        self.assertEqual(parsed["memory"], "Keep the key fact.")
        self.assertEqual(parsed["global_vocab"], ["fact"])

    def test_state_lifecycle_helper_archives_risky_low_importance_objects(self):
        state = SemanticState(memory="Keep the key fact.", constraints=["Keep the key fact."])
        state.ensure_runtime_metadata()
        metadata = next(iter(state.runtime_metadata.values()))
        metadata.importance = 0.1
        metadata.verification_passes = 0
        metadata.verification_failures = 3
        metadata.drift_count = 3
        state.round_id = 5
        result = apply_object_lifecycle_rule(state)
        self.assertEqual(result["archived"], 1)
        self.assertEqual(metadata.lifecycle_state, "archived")
        self.assertEqual(metadata.archived_round, 5)

    def test_recovery_budget_helper_splits_anchor_and_compressed_inputs(self):
        package = {
            "memory": " ".join(["compressed"] * 400),
            "constraints": ["keep this constraint"],
        }
        inputs = budget_recovery_inputs(package, " ".join(["anchor"] * 400))
        self.assertTrue(inputs.compressed_memory)
        self.assertTrue(inputs.anchor_tail)
        self.assertLess(len(inputs.anchor_tail.split()), 400)
        self.assertLess(len(inputs.compressed_memory.split()), 400)

    def test_recover_memory_from_package_offline_appends_terminal_period(self):
        class DummyBudget:
            output_tokens = 32

        memory, usage = recover_memory_from_package({"memory": "Recovered memory"}, "prompt", DummyBudget(), client=None)
        self.assertEqual(memory, "Recovered memory.")
        self.assertIsNone(usage)

    def test_pipeline_offline_records_runtime_fields(self):
        task = {
            "id": "unit-task",
            "initial_state": {"constraints": ["Keep the key fact."], "memory": "Keep the key fact."},
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact"],
        }
        records = run_srp(task, cycles=1, client=None)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertIn("runtime_round", record)
        self.assertIn("runtime_history_length", record)
        self.assertIn("critical_failures", record)
        self.assertIn("failure_summary", record)
        self.assertEqual(record["failure_summary"]["schema_version"], "failure_summary.v1")
        self.assertIn("failure_summary_flat", record)
        self.assertEqual(record["failure_summary_flat"]["schema_version"], "failure_summary_flat.v1")
        self.assertIn("critical_failure_object_id_joined", record["failure_summary_flat"])
        self.assertIn("critical_failure_type_count", record["failure_summary_flat"])
        self.assertIn("critical_failure_type_labels", record["failure_summary_flat"])

    def test_pipeline_offline_records_drift_fields(self):
        task = {
            "id": "unit-task-2",
            "initial_state": {"constraints": ["Keep the key fact."], "memory": "Keep the key fact."},
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact"],
        }
        records = run_srp(task, cycles=1, client=None)
        record = records[0]
        self.assertIn("encoder_name", record)
        self.assertIn("semantic_similarity", record)
        self.assertIn("semantic_drift", record)
        self.assertIn("semantic_drift_rate", record)
        self.assertIn("semantic_drift_from_initial", record)
        self.assertIn("semantic_drift_baseline", record)
        self.assertIn("semantic_stability", record)
        self.assertIn("chunk_selection_method", record)
        self.assertIn("selected_chunk_ids", record)
        self.assertIn("chunk_selection", record)
        self.assertIn("chunk_selection_scores", record)
        self.assertIn("chunk_selection_reasons", record)
        self.assertIn("chunk_selection_factors", record)
        self.assertIn("semantic_object_inventory", record)
        self.assertEqual(record["semantic_object_inventory"]["schema_version"], "semantic_object_inventory.v1")
        self.assertIn("semantic_objects", record)
        self.assertIn("structured_state_package", record)
        self.assertIn("recovered_state_package", record)
        self.assertIn("repair_context", record)
        self.assertIn("repair_context_flat", record)
        self.assertEqual(record["chunk_selection_factors"][0]["schema_version"], "saliency_factors.v1")
        self.assertIn("scores", record["chunk_selection_factors"][0])
        self.assertIn("signals", record["chunk_selection_factors"][0])
        self.assertIn("flags", record["chunk_selection_factors"][0])
        self.assertIn("state_continuity_summary", record)
        self.assertEqual(record["state_continuity_summary"]["schema_version"], "state_continuity_summary.v1")
        self.assertIn("recovery_template_summary", record)
        self.assertEqual(record["recovery_template_summary"]["schema_version"], "recovery_template.v1")
        self.assertIn("semantic_object_inventory_present", record["recovery_template_summary"])
        self.assertTrue(record["recovery_template_summary"]["semantic_object_inventory_present"])
        self.assertIn("structured_state_package_present", record["recovery_template_summary"])
        self.assertTrue(record["recovery_template_summary"]["structured_state_package_present"])
        self.assertIn("recovery_template_summary_flat", record)
        self.assertEqual(record["recovery_template_summary_flat"]["schema_version"], "recovery_template_summary_flat.v1")
        self.assertIn("object_update_summary", record)
        self.assertEqual(record["object_update_summary"]["schema_version"], "object_update_summary.v1")
        self.assertIn("object_update_summary_flat", record)
        self.assertEqual(record["object_update_summary_flat"]["schema_version"], "object_update_summary_flat.v1")
        self.assertIn("lifecycle_summary", record)
        self.assertEqual(record["lifecycle_summary"]["schema_version"], "lifecycle_summary.v1")
        self.assertIn("global_history", record["lifecycle_summary"])
        self.assertIn("global_history_spec", record["lifecycle_summary"])
        self.assertIn("per_object", record["lifecycle_summary"])
        self.assertIn("per_object_spec", record["lifecycle_summary"])
        self.assertIn("policy_spec", record["lifecycle_summary"])
        self.assertIn("policy_flat", record["lifecycle_summary"])
        self.assertIn("flat", record["lifecycle_summary"])
        self.assertIn("history_length", record["lifecycle_summary"])
        self.assertIn("round_id", record["lifecycle_summary"])
        self.assertIn("lifecycle_state_counts", record["lifecycle_summary"]["per_object"])
        self.assertEqual(record["lifecycle_summary"]["global_history_spec"]["schema_version"], "lifecycle_history_spec.v1")
        self.assertEqual(record["lifecycle_summary"]["per_object_spec"]["schema_version"], "lifecycle_object_spec.v1")
        self.assertEqual(record["lifecycle_summary"]["flat"]["schema_version"], "lifecycle_summary_flat.v1")
        self.assertIn("global_history_coverage_mean", record["lifecycle_summary"]["flat"])
        self.assertIn("per_object_object_count", record["lifecycle_summary"]["flat"])
        self.assertEqual(record["lifecycle_summary"]["policy_flat"]["schema_version"], "policy_spec_flat.v1")

    def test_compress_and_recover_include_runtime_summary(self):
        state = SemanticState(
            memory="Keep the key fact.",
            constraints=["Keep the key fact."],
        )
        state.ensure_runtime_metadata()
        package = compress_state(state, client=None)
        self.assertIn("runtime_summary", package)
        self.assertIn("object_count", package["runtime_summary"])
        self.assertIn("semantic_object_inventory", package)
        self.assertEqual(package["semantic_object_inventory"]["schema_version"], "semantic_object_inventory.v1")
        self.assertIn("semantic_objects", package)
        self.assertTrue(package["semantic_objects"])
        self.assertIn("object_ids", package["semantic_object_inventory"])
        self.assertIn("type_counts", package["semantic_object_inventory"])
        self.assertIn("selected_chunk_ids", package)
        self.assertIn("chunk_selection_method", package)
        self.assertIn("chunk_selection_scores", package)
        self.assertIn("chunk_selection_reasons", package)
        self.assertIn("chunk_selection_factors", package)
        self.assertEqual(package["chunk_selection_factors"][0]["schema_version"], "saliency_factors.v1")
        recovered = recover_state(package, client=None)
        recovered_dict = recovered.as_dict()
        self.assertIn("runtime_summary", recovered_dict)
        self.assertIn("history_length", recovered_dict["runtime_summary"])
        self.assertIn("recovery_summary", recovered_dict)
        self.assertEqual(recovered_dict["recovery_summary"]["schema_version"], "recovery_summary.v1")
        self.assertIn("source_memory_length", recovered_dict["recovery_summary"])
        self.assertIn("recovered_memory_length", recovered_dict["recovery_summary"])
        self.assertIn("memory_delta", recovered_dict["recovery_summary"])
        self.assertIn("constraint_overlap_rate", recovered_dict["recovery_summary"])
        self.assertIn("vocab_overlap_rate", recovered_dict["recovery_summary"])
        self.assertIn("history_continuity_ok", recovered_dict["recovery_summary"])
        self.assertIn("state_continuity_summary", recovered_dict)
        self.assertEqual(recovered_dict["state_continuity_summary"]["schema_version"], "state_continuity_summary.v1")
        self.assertIn("recovery_template_summary", recovered_dict)
        self.assertEqual(recovered_dict["recovery_template_summary"]["schema_version"], "recovery_template.v1")
        self.assertIn("semantic_object_inventory_present", recovered_dict["recovery_template_summary"])
        self.assertTrue(recovered_dict["recovery_template_summary"]["semantic_object_inventory_present"])
        self.assertIn("structured_state_package_present", recovered_dict["recovery_template_summary"])
        self.assertTrue(recovered_dict["recovery_template_summary"]["structured_state_package_present"])
        self.assertIn("structured_state_package_version", recovered_dict["recovery_template_summary"])
        self.assertEqual(recovered_dict["recovery_template_summary"]["structured_state_package_version"], "structured_state_package.v1")
        self.assertIn("semantic_object_count", recovered_dict["recovery_template_summary"])
        self.assertIn("semantic_object_type_counts", recovered_dict["recovery_template_summary"])
        self.assertIn("recovered_state_package", recovered_dict)
        self.assertEqual(recovered_dict["recovered_state_package"]["schema_version"], "structured_state_package.v1")
        self.assertIn("typed_representation", recovered_dict["recovered_state_package"])
        self.assertIn("semantic_object_inventory", recovered_dict["recovered_state_package"])
        self.assertIn("recovery_template_summary_flat", recovered_dict)
        self.assertEqual(recovered_dict["recovery_template_summary_flat"]["schema_version"], "recovery_template_summary_flat.v1")
        self.assertIn("recover_template_sections", recovered_dict["recovery_template_summary_flat"])
        self.assertIn("recover_prompt_word_count", recovered_dict["recovery_template_summary_flat"])
        self.assertIn("object_update_summary", recovered_dict)
        self.assertEqual(recovered_dict["object_update_summary"]["schema_version"], "object_update_summary.v1")
        self.assertIn("object_update_summary_flat", recovered_dict)
        self.assertEqual(recovered_dict["object_update_summary_flat"]["schema_version"], "object_update_summary_flat.v1")
        self.assertIn("update_count", recovered_dict["object_update_summary_flat"])
        self.assertIn("sections", recovered_dict["recovery_template_summary"])
        self.assertIn("prompt_word_count", recovered_dict["recovery_template_summary"])
        self.assertIn("lifecycle_summary", recovered_dict)
        self.assertEqual(recovered_dict["lifecycle_summary"]["schema_version"], "lifecycle_summary.v1")
        self.assertIn("global_history", recovered_dict["lifecycle_summary"])
        self.assertIn("global_history_spec", recovered_dict["lifecycle_summary"])
        self.assertIn("per_object", recovered_dict["lifecycle_summary"])
        self.assertIn("per_object_spec", recovered_dict["lifecycle_summary"])
        self.assertIn("policy_spec", recovered_dict["lifecycle_summary"])
        self.assertIn("policy_flat", recovered_dict["lifecycle_summary"])
        self.assertIn("flat", recovered_dict["lifecycle_summary"])
        self.assertIn("history_length", recovered_dict["lifecycle_summary"])
        self.assertIn("round_id", recovered_dict["lifecycle_summary"])
        self.assertIn("lifecycle_state_counts", recovered_dict["lifecycle_summary"]["per_object"])
        self.assertEqual(recovered_dict["lifecycle_summary"]["global_history_spec"]["schema_version"], "lifecycle_history_spec.v1")
        self.assertEqual(recovered_dict["lifecycle_summary"]["per_object_spec"]["schema_version"], "lifecycle_object_spec.v1")
        self.assertEqual(recovered_dict["lifecycle_summary"]["flat"]["schema_version"], "lifecycle_summary_flat.v1")
        self.assertIn("global_history_drift_delta", recovered_dict["lifecycle_summary"]["flat"])
        self.assertIn("per_object_lifecycle_state_counts", recovered_dict["lifecycle_summary"]["flat"])
        self.assertEqual(recovered_dict["lifecycle_summary"]["policy_flat"]["schema_version"], "policy_spec_flat.v1")

    def test_recover_state_uses_reconstruction_policy_and_records_result(self):
        previous_policy = os.environ.get("SRP_RECONSTRUCTION_POLICY")
        try:
            os.environ["SRP_RECONSTRUCTION_POLICY"] = "minimal"
            state = SemanticState(
                memory="Question: which option is correct? Answer: B. Extra chatter.",
                constraints=["Preserve the answer and the question."],
            )
            state.ensure_runtime_metadata()
            package = compress_state(state, client=None)
            recovered = recover_state(package, client=None)
            recovered_dict = recovered.as_dict()
            self.assertIn("reconstruction_result", recovered_dict)
            self.assertEqual(recovered_dict["reconstruction_result"]["schema_version"], "reconstruction_result.v1")
            self.assertEqual(recovered_dict["reconstruction_result"]["policy_name"], "minimal")
            self.assertIn("selected_object_count", recovered_dict["reconstruction_result"])
            self.assertIn("recovered_state_package", recovered_dict)
            self.assertIn("structured_state_package", recovered_dict["recovered_state_package"])
        finally:
            if previous_policy is None:
                os.environ.pop("SRP_RECONSTRUCTION_POLICY", None)
            else:
                os.environ["SRP_RECONSTRUCTION_POLICY"] = previous_policy

    def test_minimal_state_allocation_policy_partitions_objects(self):
        previous_policy = os.environ.get("SRP_STATE_ALLOCATION_POLICY")
        try:
            os.environ["SRP_STATE_ALLOCATION_POLICY"] = "minimal"
            state = SemanticState(
                memory="Question: which option is correct? Answer: B. Extra chatter.",
                constraints=["Preserve the answer and the question."],
            )
            state.ensure_runtime_metadata()
            package = compress_state(state, client=None)
            recovered = recover_state(package, client=None)
            allocation_policy = build_state_allocation_policy()
            allocation = allocation_policy.allocate(
                recovered.recovered_state_package,
                {
                    "task": {
                        "id": "allocation-task",
                        "initial_state": state.as_dict(),
                        "query_expectations": [[["Answer: B"]]],
                        "expected_keywords": ["answer"],
                    },
                    "validation": {"coverage_score": 0.5},
                    "validation_targets": build_validation_targets(
                        {
                            "id": "allocation-task",
                            "initial_state": {"constraints": ["Preserve the answer and the question."]},
                            "query_expectations": [[["Answer: B"]]],
                            "expected_keywords": ["answer"],
                        }
                    ),
                    "recovered_state_package": recovered.recovered_state_package,
                },
            )
            self.assertEqual(allocation.policy_name, "minimal")
            self.assertIsNotNone(allocation.metrics.active_object_count)
            self.assertIsNotNone(allocation.metrics.latent_object_count)
            self.assertIsNotNone(allocation.metrics.discard_object_count)
            self.assertGreaterEqual(allocation.metrics.active_object_count, 1)
        finally:
            if previous_policy is None:
                os.environ.pop("SRP_STATE_ALLOCATION_POLICY", None)
            else:
                os.environ["SRP_STATE_ALLOCATION_POLICY"] = previous_policy

    def test_csv_export_flattens_lifecycle_and_policy(self):
        task = {
            "id": "csv-task",
            "initial_state": {"constraints": ["Keep the key fact."], "memory": "Keep the key fact."},
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact"],
        }
        records = run_srp(task, cycles=1, client=None)
        flat_record = flatten_record_for_csv(records[0])
        self.assertIn("lifecycle_summary_flat_schema_version", flat_record)
        self.assertIn("lifecycle_summary_policy_flat_schema_version", flat_record)
        self.assertIn("lifecycle_summary_per_object_object_count", flat_record)
        self.assertIn("lifecycle_summary_global_history_coverage_mean", flat_record)
        self.assertIn("policy_flat_schema_version", flat_record)
        self.assertIn("state_allocation_result", records[0])
        output_path = write_records_csv(records, Path("srp_experiment") / "tmp" / "srp_records_test.csv")
        self.assertTrue(output_path.exists())

    def test_csv_export_preserves_task_metadata(self):
        task = {
            "id": "csv-task-2",
            "initial_state": {"constraints": ["Keep the key fact."], "memory": "Keep the key fact."},
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact"],
        }
        records = run_srp(task, cycles=1, client=None)
        for record in records:
            record["task_id"] = task["id"]
        flat_record = flatten_record_for_csv(records[0])
        self.assertEqual(flat_record["task_id"], "csv-task-2")

    def test_chunk_memory_produces_stable_prefixed_chunks(self):
        memory = "First sentence. Second sentence is longer than the first. Third sentence remains here."
        chunks = chunk_memory(memory, max_words=5)
        self.assertTrue(chunks)
        self.assertTrue(all(chunk.startswith(f"{index}:") for index, chunk in enumerate(chunks, start=1)))
        self.assertEqual(chunk_memory(memory, max_words=5), chunks)

    def test_object_inventory_boosts_chunk_saliency_for_preserved_content(self):
        memory = "Question: which option is correct? Evidence: the answer is B. Extra chatter follows."
        state = SemanticState(
            memory=memory,
            constraints=["Preserve the correct answer and evidence."],
        )
        inventory = {
            "important_objects": [
                {
                    "object_id": "question:1",
                    "type": "question",
                    "value": "which option is correct",
                    "confidence": 1.0,
                    "evidence_pointer": "memory:1",
                },
                {
                    "object_id": "answer:2",
                    "type": "answer",
                    "value": "the answer is B",
                    "confidence": 0.9,
                    "evidence_pointer": "memory:2",
                },
            ]
        }
        selected, _ = rank_memory_chunks(
            state.memory,
            state.constraints,
            expected_keywords=["answer", "evidence"],
            semantic_object_inventory=inventory,
            top_k=2,
        )
        self.assertTrue(selected)
        self.assertTrue(any(item["saliency_factors"]["scores"]["object_support_score"] is not None for item in selected))
        self.assertTrue(any("objects=" in item["reason"] for item in selected))

    def test_chunk_selection_degrades_without_encoder_and_records_method(self):
        task = {
            "id": "chunk-method-task",
            "initial_state": {
                "constraints": ["Preserve the key constraint."],
                "memory": "Preserve the key constraint. Extra context appears here. Another extra sentence.",
            },
            "query_expectations": [[["Preserve the key constraint."]]],
            "expected_keywords": ["constraint"],
        }
        previous_encoder = os.environ.get("SRP_ENCODER")
        try:
            os.environ["SRP_ENCODER"] = "none"
            offline_package = compress_state(
                SemanticState(
                    memory=task["initial_state"]["memory"],
                    constraints=task["initial_state"]["constraints"],
                ),
                client=None,
            )
            self.assertEqual(offline_package["chunk_selection_method"], "rule")

            os.environ["SRP_ENCODER"] = "hashing"

            class DummyClient:
                def generate_with_usage(self, *args, **kwargs):
                    return {
                        "text": "Preserve the key constraint.",
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                        "raw_text": "Preserve the key constraint.",
                        "stripped_thinking": None,
                    }

            hybrid_package = compress_state(
                SemanticState(
                    memory=task["initial_state"]["memory"],
                    constraints=task["initial_state"]["constraints"],
                ),
                client=DummyClient(),
            )
            self.assertIn(hybrid_package["chunk_selection_method"], {"rule", "embedding", "hybrid"})
            self.assertIn("selected_chunk_ids", hybrid_package)
            self.assertIn("chunk_selection_scores", hybrid_package)
        finally:
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder

    def test_llm_chunk_judge_failure_does_not_block_pipeline(self):
        previous_judge = os.environ.get("SRP_USE_LLM_JUDGE")
        previous_encoder = os.environ.get("SRP_ENCODER")
        try:
            os.environ["SRP_USE_LLM_JUDGE"] = "true"
            os.environ["SRP_ENCODER"] = "none"

            class DummyClient:
                def __init__(self):
                    self.calls = 0

                def generate_with_usage(self, prompt, **kwargs):
                    self.calls += 1
                    if "score whether this chunk is answer-critical" in prompt:
                        return {
                            "text": "not json",
                            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                        }
                    return {
                        "text": '{"memory_summary":"Keep the key constraint.","constraints":["Preserve the key constraint."],"anchor_terms":["constraint"],"loss_risks":[]}',
                        "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                        "raw_text": '{"memory_summary":"Keep the key constraint.","constraints":["Preserve the key constraint."],"anchor_terms":["constraint"],"loss_risks":[]}',
                        "stripped_thinking": None,
                    }

            package = compress_state(
                SemanticState(
                    memory="Preserve the key constraint. Extra context appears here.",
                    constraints=["Preserve the key constraint."],
                ),
                client=DummyClient(),
            )
            self.assertIn("llm_judge_calls", package)
            self.assertIn("llm_judge_failures", package)
            self.assertGreaterEqual(package["llm_judge_calls"], 1)
            self.assertGreaterEqual(package["llm_judge_failures"], 1)
            self.assertIn("chunk_selection_method", package)
        finally:
            if previous_judge is None:
                os.environ.pop("SRP_USE_LLM_JUDGE", None)
            else:
                os.environ["SRP_USE_LLM_JUDGE"] = previous_judge
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder

    def test_csv_export_jsonl_task_stream(self):
        jsonl_path = Path("srp_experiment") / "tmp" / "srp_tasks_test.jsonl"
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_path.write_text(
            '{"id":"jsonl-task-a","initial_state":{"constraints":["Keep A."],"memory":"Keep A."},"query_expectations":[[["Keep A."]]],"expected_keywords":["keep"]}\n'
            '{"id":"jsonl-task-b","initial_state":{"constraints":["Keep B."],"memory":"Keep B."},"query_expectations":[[["Keep B."]]],"expected_keywords":["keep"]}\n',
            encoding="utf-8",
        )
        from srp_experiment.srp.export import flatten_records_for_csv

        tasks = []
        with jsonl_path.open("r", encoding="utf-8-sig") as handle:
            for line in handle:
                if line.strip():
                    tasks.append(line)
        self.assertEqual(len(tasks), 2)
        records = []
        for task_id in ["jsonl-task-a", "jsonl-task-b"]:
            records.extend(run_srp({
                "id": task_id,
                "initial_state": {"constraints": [f"Keep {task_id[-1].upper()}."], "memory": f"Keep {task_id[-1].upper()}."},
                "query_expectations": [[ [f"Keep {task_id[-1].upper()}." ]]],
                "expected_keywords": ["keep"],
            }, cycles=1, client=None))
        flattened = flatten_records_for_csv(records)
        self.assertEqual(len(flattened), 2)

    def test_task_id_prefix_is_applied(self):
        from srp_experiment.export_csv import _apply_task_identity

        record = {}
        task = {"id": "alpha"}
        _apply_task_identity(record, task, Path("srp_experiment") / "tmp" / "task.json", "batch1-")
        self.assertEqual(record["task_id"], "batch1-alpha")
        self.assertIn("task_source", record)

    def test_two_cycle_offline_roundtrip_stays_connected(self):
        task = {
            "id": "roundtrip-task",
            "initial_state": {
                "constraints": ["Preserve the original constraint."],
                "memory": "Preserve the original constraint and keep the key fact in view.",
            },
            "query_expectations": [[["Preserve the original constraint."]]],
            "expected_keywords": ["constraint", "fact"],
        }
        records = run_srp(task, cycles=2, client=None)
        self.assertEqual(len(records), 2)
        self.assertGreaterEqual(records[-1]["runtime_history_length"], 2)
        self.assertIn("runtime_round", records[-1])
        self.assertIn("runtime_summary", compress_state(SemanticState(memory=task["initial_state"]["memory"], constraints=task["initial_state"]["constraints"]), client=None))

    def test_multi_cycle_pipeline_records_validation_fields(self):
        task = {
            "id": "multi-cycle-task",
            "initial_state": {
                "constraints": ["Preserve the original constraint."],
                "memory": "Preserve the original constraint and keep the key fact in view.",
            },
            "query_expectations": [[["Preserve the original constraint."]]],
            "expected_keywords": ["constraint", "fact"],
        }
        records = run_srp(task, cycles=3, client=None)
        self.assertEqual(len(records), 3)
        history_lengths = [record["runtime_history_length"] for record in records]
        self.assertTrue(all(value is not None for value in history_lengths))
        self.assertTrue(all(curr >= prev for prev, curr in zip(history_lengths, history_lengths[1:])))
        for record in records:
            self.assertIn("validation_passed", record)
            self.assertIn("validation_coverage", record)
            self.assertIn("validation_drift", record)
            self.assertIn("critical_failures", record)
            self.assertIn("failure_summary", record)
            self.assertIn("failure_summary_flat", record)
            self.assertIn("critical_failure_object_id_joined", record["failure_summary_flat"])

    def test_three_cycle_state_continuity(self):
        previous_encoder = os.environ.get("SRP_ENCODER")
        os.environ["SRP_ENCODER"] = "hashing"
        task = {
            "id": "continuity-task",
            "initial_state": {
                "constraints": ["Preserve the original constraint."],
                "memory": "Preserve the original constraint and keep the key fact in view.",
            },
            "query_expectations": [[["Preserve the original constraint."]]],
            "expected_keywords": ["constraint", "fact"],
        }
        try:
            records = run_srp(task, cycles=3, client=None)
            self.assertEqual(len(records), 3)
            history_lengths = [record["runtime_history_length"] for record in records]
            rounds = [record["runtime_round"] for record in records]
            stabilities = [record["semantic_stability"] for record in records]
            self.assertEqual(rounds, sorted(rounds))
            self.assertTrue(all(curr >= prev for prev, curr in zip(history_lengths, history_lengths[1:])))
            self.assertTrue(all(value is not None for value in stabilities))
            self.assertTrue(all(0.0 <= value <= 1.0 for value in stabilities))
            self.assertGreaterEqual(history_lengths[-1], 3)
        finally:
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder


if __name__ == "__main__":
    unittest.main()
