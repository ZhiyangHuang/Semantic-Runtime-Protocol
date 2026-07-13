import unittest
import os
import json
from pathlib import Path

from srp_experiment.srp.pipeline import run_srp
from srp_experiment.srp.compress import chunk_memory, compress_state
from srp_experiment.srp.encoder import build_encoder
from srp_experiment.srp.export import flatten_record_for_csv, write_records_csv
from srp_experiment.srp.export import render_record_markdown, render_records_markdown, write_records_markdown
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
from srp_experiment.srp.object_lifecycle import build_object_lifecycle_artifact
from srp_experiment.srp.object_retention import build_object_retention_breakdown, build_object_retention_breakdown_v2
from srp_experiment.srp.object_retention import build_integrity_retention_metrics
from srp_experiment.srp.repair_diagnostics import build_repair_diagnostics
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


    def test_pipeline_record_includes_canonical_experiment_result(self):
        task = {
            "id": "experiment-result-task",
            "initial_state": {
                "constraints": ["Keep the key fact."],
                "memory": "Keep the key fact and preserve the answer B.",
            },
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact", "answer"],
        }
        record = run_srp(task, cycles=1, client=None)[0]
        experiment_result = record["experiment_result"]
        self.assertEqual(experiment_result["schema_version"], "experiment_result.v1")
        self.assertIn("representation", experiment_result)
        self.assertIn("compression", experiment_result)
        self.assertIn("reconstruction", experiment_result)
        self.assertIn("allocation", experiment_result)
        self.assertIn("repair", experiment_result)
        self.assertIn("diagnostics", experiment_result["repair"])
        self.assertIn("execution", experiment_result)
        self.assertIn("validation", experiment_result)
        self.assertIn("lifecycle_attribution", experiment_result)
        self.assertIn("metrics", experiment_result)
        self.assertEqual(experiment_result["validation"]["passed"], record["validation_passed"])
        self.assertEqual(experiment_result["metrics"]["state_committed"], record["state_committed"])
        self.assertEqual(experiment_result["metrics"]["semantic_similarity"], record["semantic_similarity"])
        self.assertIn("structured_state_package_present", experiment_result["reconstruction"])
        self.assertIn("compressed_size", experiment_result["compression"])
        self.assertIn("compression_ratio", experiment_result["compression"])
        self.assertIn("lifecycle_inflation", experiment_result["metrics"])
        self.assertIn("integrity_gap", experiment_result["metrics"])
        self.assertIn("semantic_compression_loss", experiment_result["metrics"])
        self.assertIn("weighted_object_retention", experiment_result["metrics"])
        self.assertIn("semantic_graph", experiment_result)
        self.assertIn("graph", experiment_result["semantic_graph"])
        self.assertIn("validation", experiment_result["semantic_graph"])
        self.assertEqual(experiment_result["allocation"]["result"], record["state_allocation_result"])


    def test_csv_flatten_includes_canonical_experiment_result_columns(self):
        task = {
            "id": "experiment-result-csv-task",
            "initial_state": {
                "constraints": ["Keep the key fact."],
                "memory": "Keep the key fact and preserve the answer B.",
            },
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact", "answer"],
        }
        record = run_srp(task, cycles=1, client=None)[0]
        flat_record = flatten_record_for_csv(record)
        self.assertIn("experiment_result_schema_version", flat_record)
        self.assertIn("experiment_result_validation_passed", flat_record)
        self.assertIn("experiment_result_lifecycle_attribution_source_object_count", flat_record)
        self.assertIn("experiment_result_lifecycle_attribution_allocated_allocated_object_count", flat_record)
        self.assertIn("experiment_result_lifecycle_attribution_lifecycle_inflation", flat_record)
        self.assertIn("experiment_result_metrics_state_committed", flat_record)
        self.assertIn("experiment_result_metrics_structured_state_package_present", flat_record)
        self.assertIn("experiment_result_metrics_compressed_size", flat_record)
        self.assertIn("experiment_result_metrics_compression_ratio", flat_record)
        self.assertIn("repair_diagnostics_repair_attempted", flat_record)
        self.assertIn("experiment_result_metrics_integrity_gap", flat_record)
        self.assertIn("experiment_result_metrics_semantic_compression_loss", flat_record)
        self.assertIn("experiment_result_metrics_lost_important_object_count", flat_record)
        self.assertIn("experiment_result_compression_chunk_selection_method", flat_record)
        self.assertEqual(flat_record["experiment_result_validation_passed"], record["validation_passed"])


    def test_markdown_audit_renders_from_experiment_result(self):
        task = {
            "id": "markdown-audit-task",
            "initial_state": {
                "constraints": ["Keep the key fact."],
                "memory": "Keep the key fact and preserve the answer B.",
            },
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact", "answer"],
        }
        record = run_srp(task, cycles=1, client=None)[0]
        record["task_id"] = task["id"]
        markdown = render_record_markdown(record)
        self.assertIn("## markdown-audit-task", markdown)
        self.assertIn("### Core Metrics", markdown)
        self.assertIn("### Repair Diagnostics", markdown)
        self.assertIn("### Lifecycle Stages", markdown)
        self.assertIn("### Lifecycle Transitions", markdown)
        self.assertIn("### Lifecycle Transition Details", markdown)
        self.assertIn("#### source_to_compressed", markdown)
        self.assertIn("**Retained**", markdown)
        self.assertIn("Object ID", markdown)
        self.assertIn("validation_coverage", markdown)
        self.assertIn("structured_state_package_present", markdown)
        self.assertIn("compressed_size", markdown)
        self.assertIn("compression_ratio", markdown)
        self.assertIn("lifecycle_inflation", markdown)
        self.assertIn(str(record["experiment_result"]["schema_version"]), markdown)


    def test_markdown_audit_writer_persists_combined_report(self):
        task = {
            "id": "markdown-audit-write-task",
            "initial_state": {
                "constraints": ["Keep the key fact."],
                "memory": "Keep the key fact and preserve the answer B.",
            },
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact", "answer"],
        }
        records = run_srp(task, cycles=2, client=None)
        for index, record in enumerate(records, start=1):
            record["task_id"] = f"{task['id']}-c{index}"
        markdown = render_records_markdown(records)
        self.assertIn("# SRP Experiment Audit", markdown)
        self.assertIn("## markdown-audit-write-task-c1", markdown)
        self.assertIn("## markdown-audit-write-task-c2", markdown)
        output_path = write_records_markdown(records, Path("srp_experiment") / "tmp" / "srp_audit_test.md")
        self.assertTrue(output_path.exists())
        written = output_path.read_text(encoding="utf-8")
        self.assertIn("### Lifecycle Transitions", written)
        self.assertIn("### Lifecycle Transition Details", written)


    def test_markdown_audit_expands_transition_object_details(self):
        validation_targets = build_validation_targets(
            {
                "id": "markdown-detail-task",
                "initial_state": {
                    "constraints": ["Keep the key constraint."],
                    "memory": "Keep the key constraint. The answer is B.",
                },
                "query_expectations": [[["Keep the key constraint."]]],
                "expected_keywords": ["constraint", "answer"],
            }
        )
        artifact = build_object_lifecycle_artifact(
            {
                "semantic_object_inventory": {
                    "objects": [
                        {"object_id": stable_semantic_object_id("constraint", "Keep the key constraint."), "type": "constraint", "value": "Keep the key constraint."},
                        {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                    ]
                }
            },
            {
                "semantic_object_inventory": {
                    "objects": [
                        {"object_id": stable_semantic_object_id("constraint", "Keep the key constraint."), "type": "constraint", "value": "Keep the key constraint."},
                    ]
                }
            },
            {
                "typed_representation": {
                    "objects": [
                        {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                        {"type": "fact", "value": "Recovered extra detail.", "confidence": 0.6, "evidence_pointer": "memory:3"},
                    ]
                }
            },
            validation_targets=validation_targets,
        ).as_dict()
        record = {
            "cycle": 1,
            "experiment_result": {
                "schema_version": "experiment_result.v1",
                "runtime": {"round": 1},
                "validation": {"passed": False, "coverage": 0.5, "alignment": 0.5},
                "repair": {"diagnostics": {}, "attempted": False},
                "metrics": {
                    "state_committed": False,
                    "integrity_gap": 0.5,
                    "semantic_compression_loss": 0.5,
                    "object_retention": 0.5,
                    "weighted_object_retention": 0.5,
                    "lost_important_object_count": 1,
                    "object_inflation_ratio": 1.0,
                    "semantic_similarity": None,
                    "semantic_drift": None,
                },
                "lifecycle_attribution": artifact,
            },
        }
        markdown = render_record_markdown(record)
        self.assertIn("Keep the key constraint.", markdown)
        self.assertIn("The answer is B.", markdown)
        self.assertIn("Recovered extra detail.", markdown)
        self.assertIn("memory:3", markdown)
        self.assertIn(stable_semantic_object_id("constraint", "Keep the key constraint."), markdown)


    def test_experiment_result_schema_file_matches_runtime_contract(self):
        schema_path = Path("srp_experiment") / "schemas" / "experiment_result_schema_v1.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schema_version"]["const"], "experiment_result.v1")
        self.assertEqual(
            schema["required"],
            [
                "schema_version",
                "cycle",
                "runtime",
                "representation",
                "semantic_graph",
                "compression",
                "reconstruction",
                "allocation",
                "repair",
                "execution",
                "validation",
                "lifecycle_attribution",
                "metrics",
            ],
        )
        self.assertEqual(
            schema["properties"]["repair"]["required"],
            ["attempted", "context", "context_flat", "diagnostics"],
        )
        self.assertEqual(
            schema["properties"]["semantic_graph"]["$ref"],
            "#/$defs/semantic_graph",
        )
        self.assertEqual(
            schema["$defs"]["semantic_graph"]["properties"]["graph"]["type"],
            "object",
        )
        self.assertIn("token_overhead", schema["properties"]["repair"]["properties"])
        self.assertEqual(
            schema["$defs"]["repair_diagnostics"]["properties"]["schema_version"]["const"],
            "repair_diagnostics.v1",
        )
        self.assertEqual(
            schema["$defs"]["integrity_retention_metrics"]["properties"]["schema_version"]["const"],
            "integrity_retention_metrics.v1",
        )
        self.assertIn("integrity_gap", schema["properties"]["metrics"]["required"])
        self.assertIn("semantic_compression_loss", schema["properties"]["metrics"]["required"])
        self.assertIn("weighted_object_retention", schema["properties"]["metrics"]["required"])
        self.assertIn("lost_important_object_count", schema["properties"]["metrics"]["required"])
        self.assertIn("structured_state_package_present", schema["properties"]["metrics"]["required"])
        self.assertIn("compressed_size", schema["properties"]["metrics"]["required"])
        self.assertIn("compression_ratio", schema["properties"]["metrics"]["required"])
        self.assertIn("lifecycle_inflation", schema["properties"]["metrics"]["required"])
        self.assertEqual(
            schema["properties"]["metrics"]["properties"]["integrity_retention_metrics"]["$ref"],
            "#/$defs/integrity_retention_metrics",
        )
        self.assertIn("source_size", schema["properties"]["compression"]["required"])
        self.assertIn("compressed_size", schema["properties"]["compression"]["required"])
        self.assertIn("compression_ratio", schema["properties"]["compression"]["required"])
        self.assertIn("graph_dependency_closure_rate", schema["properties"]["metrics"]["required"])
        self.assertIn("graph_recovery_precision", schema["properties"]["metrics"]["required"])
        self.assertIn("graph_repair_cost", schema["properties"]["metrics"]["required"])
        self.assertIn("structured_state_package_present", schema["properties"]["reconstruction"]["required"])
        self.assertIn("lifecycle_inflation", schema["properties"]["lifecycle_attribution"]["required"])
        self.assertEqual(
            schema["properties"]["repair"]["properties"]["diagnostics"]["$ref"],
            "#/$defs/repair_diagnostics",
        )
        self.assertEqual(
            schema["properties"]["lifecycle_attribution"]["properties"]["source"]["$ref"],
            "#/$defs/lifecycle_stage_summary",
        )
        self.assertEqual(
            schema["properties"]["lifecycle_attribution"]["properties"]["transitions"]["properties"]["source_to_compressed"]["$ref"],
            "#/$defs/lifecycle_transition_summary",
        )
        self.assertEqual(
            schema["$defs"]["lifecycle_stage_summary"]["required"],
            ["stage", "present", "retained", "missing", "hallucinated", "object_count", "raw_object_count"],
        )
        self.assertEqual(
            schema["$defs"]["lifecycle_transition_summary"]["required"],
            [
                "source_stage",
                "target_stage",
                "present",
                "retained",
                "missing",
                "hallucinated",
                "retained_count",
                "missing_count",
                "hallucinated_count",
                "recall",
                "precision",
            ],
        )
        self.assertEqual(
            schema["$defs"]["lifecycle_object_detail"]["required"],
            ["object_id", "type", "value", "confidence", "evidence_pointer"],
        )
        self.assertEqual(
            schema["$defs"]["lifecycle_stage_summary"]["properties"]["retained"]["$ref"],
            "#/$defs/lifecycle_object_detail_array",
        )
        self.assertEqual(
            schema["$defs"]["lifecycle_transition_summary"]["properties"]["hallucinated"]["$ref"],
            "#/$defs/lifecycle_object_detail_array",
        )
        self.assertIn("total_tokens_before_repair", schema["$defs"]["repair_diagnostics"]["required"])
        self.assertIn("total_tokens_after_repair", schema["$defs"]["repair_diagnostics"]["required"])
        self.assertIn("token_overhead", schema["$defs"]["repair_diagnostics"]["required"])


    def test_experiment_result_runtime_shape_matches_nested_schema_expectations(self):
        record = run_srp(
            {
                "id": "schema-shape-task",
                "initial_state": {
                    "constraints": ["Keep the key fact."],
                    "memory": "Keep the key fact and preserve the answer B.",
                },
                "query_expectations": [[["Keep the key fact."]]],
                "expected_keywords": ["fact", "answer"],
            },
            cycles=1,
            client=None,
        )[0]
        result = record["experiment_result"]
        self.assertIsInstance(result["repair"]["attempted"], bool)
        self.assertIn("schema_version", result["repair"]["diagnostics"])
        self.assertEqual(result["repair"]["diagnostics"]["schema_version"], "repair_diagnostics.v1")
        self.assertIn("token_overhead", result["repair"])
        self.assertIn("token_overhead", result["repair"]["diagnostics"])
        self.assertIn("integrity_retention_metrics", result["metrics"])
        self.assertEqual(
            result["metrics"]["integrity_retention_metrics"]["schema_version"],
            "integrity_retention_metrics.v1",
        )
        self.assertIsInstance(result["metrics"]["lost_important_object_count"], int)
        self.assertIsInstance(result["metrics"]["recovered_object_type_counts"], dict)
        self.assertIsInstance(result["compression"]["compressed_size"], int)
        self.assertIsInstance(result["compression"]["compression_ratio"], float)
        self.assertIsInstance(result["reconstruction"]["structured_state_package_present"], bool)
        self.assertIsInstance(result["validation"]["passed"], bool)
        self.assertIsInstance(result["metrics"]["validation_passed"], bool)
        self.assertIsInstance(result["metrics"]["state_committed"], bool)
        self.assertIsInstance(result["metrics"]["structured_state_package_present"], bool)
        self.assertIsInstance(result["metrics"]["compressed_size"], int)
        self.assertIsInstance(result["metrics"]["compression_ratio"], float)
        self.assertIsInstance(result["metrics"]["lifecycle_inflation"], float)
        self.assertIsInstance(result["repair"]["token_overhead"], (int, type(None)))
        self.assertEqual(result["lifecycle_attribution"]["schema_version"], "object_lifecycle.v1")
        self.assertIsInstance(result["lifecycle_attribution"]["source"]["present"], bool)
        self.assertIsInstance(result["lifecycle_attribution"]["source"]["object_count"], int)
        self.assertIsInstance(result["lifecycle_attribution"]["source"]["raw_object_count"], int)
        self.assertIsInstance(result["lifecycle_attribution"]["source_object_count"], int)
        self.assertIsInstance(result["lifecycle_attribution"]["compressed_object_count"], int)
        self.assertIsInstance(result["lifecycle_attribution"]["lifecycle_inflation"], float)
        self.assertIsInstance(result["lifecycle_attribution"]["source"]["retained"], list)
        self.assertIsInstance(result["lifecycle_attribution"]["source"]["missing"], list)
        self.assertIsInstance(result["lifecycle_attribution"]["source"]["hallucinated"], list)
        self.assertIn("source_to_compressed", result["lifecycle_attribution"]["transitions"])
        self.assertIsInstance(
            result["lifecycle_attribution"]["transitions"]["source_to_compressed"]["present"],
            bool,
        )
        self.assertIsInstance(
            result["lifecycle_attribution"]["transitions"]["source_to_compressed"]["retained"],
            list,
        )


    def test_object_lifecycle_artifact_tracks_allocation_and_execution_transitions(self):
        validation_targets = build_validation_targets(
            {
                "id": "lifecycle-attribution-task",
                "initial_state": {
                    "constraints": ["Keep the key constraint."],
                    "memory": "Keep the key constraint. The answer is B.",
                },
                "query_expectations": [[["Keep the key constraint."]]],
                "expected_keywords": ["constraint", "answer"],
            }
        )
        source_package = {
            "semantic_object_inventory": {
                "objects": [
                    {"object_id": stable_semantic_object_id("constraint", "Keep the key constraint."), "type": "constraint", "value": "Keep the key constraint."},
                    {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                ],
                "important_objects": [
                    {"object_id": stable_semantic_object_id("constraint", "Keep the key constraint."), "type": "constraint", "value": "Keep the key constraint."},
                ],
            }
        }
        compressed_package = {
            "semantic_object_inventory": {
                "objects": [
                    {"object_id": stable_semantic_object_id("constraint", "Keep the key constraint."), "type": "constraint", "value": "Keep the key constraint."},
                ]
            }
        }
        recovered_package = {
            "typed_representation": {
                "objects": [
                    {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                    {"type": "fact", "value": "The answer is B.", "confidence": 0.8, "evidence_pointer": "memory:2"},
                ]
            }
        }
        repaired_package = {
            "typed_representation": {
                "objects": [
                    {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                ]
            }
        }
        allocation_result = {
            "active_objects": [
                {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
            ]
        }
        execution_payload = {
            "objects": [
                {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
            ],
            "object_count": 1,
            "source": "active",
        }

        artifact = build_object_lifecycle_artifact(
            source_package,
            compressed_package,
            recovered_package,
            repaired_package,
            validation_targets=validation_targets,
            state_allocation_result=allocation_result,
            execution_payload=execution_payload,
        ).as_dict()
        self.assertEqual(artifact["source"]["object_count"], 2)
        self.assertEqual(artifact["compressed"]["compressed_object_count"], 1)
        self.assertEqual(artifact["recovered"]["recovered_object_count"], 2)
        self.assertEqual(artifact["repaired"]["repaired_object_count"], 1)
        self.assertEqual(artifact["allocated"]["allocated_object_count"], 1)
        self.assertEqual(artifact["executed"]["executed_object_count"], 1)
        self.assertTrue(artifact["repaired"]["present"])
        self.assertTrue(artifact["allocated"]["present"])
        self.assertTrue(artifact["executed"]["present"])
        self.assertEqual(artifact["source_object_count"], 2)
        self.assertEqual(artifact["compressed_object_count"], 1)
        self.assertEqual(artifact["recovered_object_count"], 2)
        self.assertEqual(artifact["repaired_object_count"], 1)
        self.assertEqual(artifact["allocated_object_count"], 1)
        self.assertEqual(artifact["executed_object_count"], 1)
        self.assertEqual(artifact["lifecycle_inflation"], 1.0)
        self.assertEqual(artifact["transitions"]["source_to_compressed"]["recall"], 0.5)
        self.assertEqual(artifact["transitions"]["compressed_to_recovered"]["recall"], 1.0)
        self.assertEqual(artifact["transitions"]["recovered_to_repaired"]["recall"], 0.5)
        self.assertEqual(artifact["transitions"]["repaired_to_allocated"]["recall"], 1.0)
        self.assertEqual(artifact["transitions"]["allocated_to_executed"]["recall"], 1.0)
        self.assertEqual(artifact["transitions"]["source_to_compressed"]["source_stage"], "source")
        self.assertEqual(artifact["transitions"]["source_to_compressed"]["target_stage"], "compressed")
        self.assertTrue(artifact["transitions"]["source_to_compressed"]["present"])
        self.assertEqual(
            artifact["transitions"]["source_to_compressed"]["retained"][0]["object_id"],
            stable_semantic_object_id("constraint", "Keep the key constraint."),
        )
        self.assertEqual(
            artifact["transitions"]["source_to_compressed"]["missing"][0]["object_id"],
            stable_semantic_object_id("fact", "The answer is B."),
        )


    def test_integrity_retention_metrics_capture_loss_and_weighting(self):
        source_package = {
            "typed_representation": {
                "objects": [
                    {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                    {"type": "fact", "value": "The answer is B.", "confidence": 0.8, "evidence_pointer": "memory:2"},
                ]
            },
            "semantic_object_inventory": {
                "important_objects": [
                    {"object_id": stable_semantic_object_id("constraint", "Keep the key constraint."), "type": "constraint", "value": "Keep the key constraint."},
                    {"object_id": stable_semantic_object_id("fact", "The answer is B."), "type": "fact", "value": "The answer is B."},
                ]
            },
            "runtime_metadata": {
                stable_semantic_object_id("constraint", "Keep the key constraint."): {"importance": 0.9},
                stable_semantic_object_id("fact", "The answer is B."): {"importance": 0.3},
            },
        }
        compressed_package = {
            "typed_representation": {
                "objects": [
                    {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                ]
            }
        }
        recovered_package = {
            "typed_representation": {
                "objects": [
                    {"type": "constraint", "value": "Keep the key constraint.", "confidence": 1.0, "evidence_pointer": "constraint:1"},
                ]
            }
        }
        validation_targets = build_validation_targets(
            {
                "id": "integrity-metrics-task",
                "initial_state": {
                    "constraints": ["Keep the key constraint."],
                    "memory": "Keep the key constraint. The answer is B.",
                },
                "query_expectations": [[["Keep the key constraint."]]],
                "expected_keywords": ["constraint", "answer"],
            }
        )
        validation = {"coverage_score": 0.75, "passed": False}
        metrics = build_integrity_retention_metrics(
            source_package,
            compressed_package,
            recovered_package,
            validation=validation,
            validation_targets=validation_targets,
            committed=False,
        ).as_dict()
        self.assertEqual(metrics["schema_version"], "integrity_retention_metrics.v1")
        self.assertAlmostEqual(metrics["semantic_compression_loss"], 0.5, places=6)
        self.assertAlmostEqual(metrics["object_retention"], 0.5, places=6)
        self.assertAlmostEqual(metrics["weighted_object_retention"], 0.75, places=6)
        self.assertAlmostEqual(metrics["integrity_gap"], 0.25, places=6)
        self.assertEqual(metrics["lost_important_object_count"], 1)
        self.assertEqual(metrics["recovered_object_type_counts"], {"constraint": 1})
        self.assertFalse(metrics["validation_passed"])
        self.assertFalse(metrics["state_committed"])


    def test_repair_diagnostics_capture_before_after_and_gain(self):
        diagnostics = build_repair_diagnostics(
            repair_attempted=True,
            validation_before_repair={
                "coverage_score": 0.4,
                "critical_failures": [{"id": "a"}, {"id": "b"}],
                "passed": False,
            },
            validation_after_repair={
                "coverage_score": 0.7,
                "critical_failures": [{"id": "a"}],
                "passed": True,
            },
        ).as_dict()
        self.assertEqual(diagnostics["schema_version"], "repair_diagnostics.v1")
        self.assertTrue(diagnostics["repair_attempted"])
        self.assertAlmostEqual(diagnostics["coverage_before_repair"], 0.4, places=6)
        self.assertAlmostEqual(diagnostics["coverage_after_repair"], 0.7, places=6)
        self.assertAlmostEqual(diagnostics["repair_gain"], 0.3, places=6)
        self.assertEqual(diagnostics["critical_failures_before"], 2)
        self.assertEqual(diagnostics["critical_failures_after"], 1)
        self.assertFalse(diagnostics["validation_passed_before"])
        self.assertTrue(diagnostics["validation_passed_after"])


    def test_repair_diagnostics_remain_null_when_not_attempted(self):
        diagnostics = build_repair_diagnostics(
            repair_attempted=False,
            validation_before_repair={"coverage_score": 0.9, "critical_failures": [], "passed": True},
            validation_after_repair={"coverage_score": 0.9, "critical_failures": [], "passed": True},
        ).as_dict()
        self.assertFalse(diagnostics["repair_attempted"])
        self.assertIsNone(diagnostics["coverage_before_repair"])
        self.assertIsNone(diagnostics["coverage_after_repair"])
        self.assertIsNone(diagnostics["repair_gain"])
        self.assertIsNone(diagnostics["critical_failures_before"])
        self.assertIsNone(diagnostics["critical_failures_after"])


    def test_pipeline_experiment_result_lifecycle_attribution_separates_recovery_and_allocation(self):
        task = {
            "id": "pipeline-lifecycle-attribution-task",
            "initial_state": {
                "constraints": ["Keep the key fact."],
                "memory": "Keep the key fact and preserve the answer B.",
            },
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact", "answer"],
        }
        record = run_srp(task, cycles=1, client=None)[0]
        lifecycle = record["experiment_result"]["lifecycle_attribution"]
        self.assertIn("source", lifecycle)
        self.assertIn("compressed", lifecycle)
        self.assertIn("recovered", lifecycle)
        self.assertIn("repaired", lifecycle)
        self.assertIn("allocated", lifecycle)
        self.assertIn("executed", lifecycle)
        self.assertIn("transitions", lifecycle)
        self.assertGreaterEqual(lifecycle["source"]["object_count"], 1)
        self.assertGreaterEqual(lifecycle["compressed"]["compressed_object_count"], 1)
        self.assertGreaterEqual(lifecycle["recovered"]["recovered_object_count"], 1)
        self.assertEqual(
            lifecycle["allocated"]["allocated_object_count"],
            len((record.get("state_allocation_result") or {}).get("active_objects", [])),
        )
        self.assertEqual(
            lifecycle["executed"]["raw_object_count"],
            record.get("execution_state_object_count"),
        )
        self.assertLessEqual(
            lifecycle["executed"]["executed_object_count"],
            lifecycle["executed"]["raw_object_count"],
        )
        self.assertEqual(lifecycle["source_object_count"], lifecycle["source"]["object_count"])
        self.assertEqual(lifecycle["compressed_object_count"], lifecycle["compressed"]["compressed_object_count"])
        self.assertEqual(lifecycle["recovered_object_count"], lifecycle["recovered"]["recovered_object_count"])
        self.assertIsNotNone(lifecycle["lifecycle_inflation"])
        self.assertGreaterEqual(lifecycle["lifecycle_inflation"], 0.0)
        self.assertTrue(lifecycle["transitions"]["source_to_compressed"]["present"])
        self.assertTrue(lifecycle["transitions"]["compressed_to_recovered"]["present"])
        self.assertIn("precision", lifecycle["transitions"]["source_to_compressed"])
        self.assertIn("recall", lifecycle["transitions"]["compressed_to_recovered"])
        self.assertIn("retained", lifecycle["transitions"]["source_to_compressed"])
        self.assertIn("missing", lifecycle["transitions"]["source_to_compressed"])
        self.assertIn("hallucinated", lifecycle["transitions"]["source_to_compressed"])
        self.assertIn("object_id", lifecycle["transitions"]["source_to_compressed"]["retained"][0])
        self.assertIn("type", lifecycle["transitions"]["source_to_compressed"]["retained"][0])
        self.assertIn("value", lifecycle["transitions"]["source_to_compressed"]["retained"][0])
        self.assertTrue(
            lifecycle["transitions"]["recovered_to_allocated"]["present"]
            or lifecycle["transitions"]["repaired_to_allocated"]["present"]
        )


    def test_pipeline_experiment_result_metrics_include_integrity_retention_fields(self):
        task = {
            "id": "pipeline-integrity-metrics-task",
            "initial_state": {
                "constraints": ["Keep the key fact."],
                "memory": "Keep the key fact and preserve the answer B.",
            },
            "query_expectations": [[["Keep the key fact."]]],
            "expected_keywords": ["fact", "answer"],
        }
        record = run_srp(task, cycles=1, client=None)[0]
        metrics = record["experiment_result"]["metrics"]
        self.assertIn("integrity_gap", metrics)
        self.assertIn("semantic_compression_loss", metrics)
        self.assertIn("object_retention", metrics)
        self.assertIn("weighted_object_retention", metrics)
        self.assertIn("lost_important_object_count", metrics)
        self.assertIn("recovered_object_type_counts", metrics)
        self.assertIn("integrity_retention_metrics", metrics)
        self.assertIn("structured_state_package_present", metrics)
        self.assertIn("compressed_size", metrics)
        self.assertIn("compression_ratio", metrics)
        self.assertIn("lifecycle_inflation", metrics)
        self.assertIn("graph_node_count", metrics)
        self.assertIn("graph_edge_count", metrics)
        self.assertIn("graph_integrity_score", metrics)
        self.assertEqual(metrics["validation_passed"], record["validation_passed"])
        self.assertEqual(metrics["state_committed"], record["state_committed"])


    def test_pipeline_repair_diagnostics_are_attached_to_experiment_result(self):
        previous_encoder = os.environ.get("SRP_ENCODER")
        try:
            os.environ["SRP_ENCODER"] = "none"
            task = {
                "id": "repair-diagnostics-task",
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

            record = run_srp(task, cycles=1, client=FailingThenStructuredClient())[0]
            diagnostics = record["experiment_result"]["repair"]["diagnostics"]
            self.assertEqual(diagnostics["schema_version"], "repair_diagnostics.v1")
            self.assertTrue(diagnostics["repair_attempted"])
            self.assertIsNotNone(diagnostics["coverage_before_repair"])
            self.assertIsNotNone(diagnostics["coverage_after_repair"])
            self.assertIsNotNone(diagnostics["repair_gain"])
            self.assertIsNotNone(diagnostics["critical_failures_before"])
            self.assertIsNotNone(diagnostics["critical_failures_after"])
            self.assertIsNotNone(diagnostics["total_tokens_before_repair"])
            self.assertIsNotNone(diagnostics["total_tokens_after_repair"])
            self.assertIsNotNone(diagnostics["token_overhead"])
            self.assertEqual(record["repair_attempted"], diagnostics["repair_attempted"])
            self.assertEqual(record["coverage_before_repair"], diagnostics["coverage_before_repair"])
            self.assertEqual(record["coverage_after_repair"], diagnostics["coverage_after_repair"])
        finally:
            if previous_encoder is None:
                os.environ.pop("SRP_ENCODER", None)
            else:
                os.environ["SRP_ENCODER"] = previous_encoder




if __name__ == "__main__":
    unittest.main()
