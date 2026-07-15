import tempfile
import unittest
from pathlib import Path

from srp_experiment.object_aware_compression_harness import (
    build_object_aware_compression_suites,
    render_object_aware_compression_summary_markdown,
    run_object_aware_compression,
    summarize_object_aware_compression,
    write_object_aware_compression_outputs,
)


class TestObjectAwareCompressionHarness(unittest.TestCase):
    def test_object_aware_compression_exposes_fixed_suite_names(self):
        suites = build_object_aware_compression_suites()
        self.assertEqual(
            [suite.name for suite in suites],
            [
                "branching_dependency_chunk_score_only",
                "branching_dependency_chunk_score_plus_object_support",
                "subject_collision_chunk_score_only",
                "subject_collision_chunk_score_plus_object_support",
                "budget_pressure_chunk_score_only",
                "budget_pressure_chunk_score_plus_object_support",
            ],
        )
        self.assertFalse(suites[0].object_support_enabled)
        self.assertTrue(suites[1].object_support_enabled)
        self.assertEqual(suites[0].scenario, "branching_dependency")
        self.assertEqual(suites[0].task["task_type"], "object_aware_compression")

    def test_object_aware_compression_toggles_object_support_scoring(self):
        records = run_object_aware_compression(
            [
                "branching_dependency_chunk_score_only",
                "branching_dependency_chunk_score_plus_object_support",
            ],
            cycles=1,
        )
        self.assertEqual(len(records), 2)
        record_by_suite = {record["compression_suite"]: record for record in records}

        disabled = record_by_suite["branching_dependency_chunk_score_only"]
        enabled = record_by_suite["branching_dependency_chunk_score_plus_object_support"]

        self.assertFalse(disabled["object_support_enabled"])
        self.assertTrue(enabled["object_support_enabled"])
        self.assertEqual(disabled["compression_scenario"], "branching_dependency")
        self.assertEqual(enabled["compression_scenario"], "branching_dependency")
        self.assertTrue(all("object_support_score" in (factor.get("scores") or {}) for factor in disabled["chunk_selection_factors"]))
        self.assertTrue(all("object_support_score" in (factor.get("scores") or {}) for factor in enabled["chunk_selection_factors"]))
        self.assertIn("mechanism_verification", disabled)
        self.assertEqual(disabled["mechanism_verification"]["schema_version"], "object_support_mechanism_verification.v1")
        self.assertIn("decision_boundary", disabled)
        self.assertEqual(disabled["decision_boundary"]["schema_version"], "object_support_decision_boundary.v1")
        self.assertIsInstance(disabled["decision_boundary"]["sweeps"], list)
        self.assertIn("decision_flip_distance_mean", disabled["decision_boundary"])
        self.assertIn("experiment_result", disabled)
        self.assertIn("experiment_result", enabled)
        self.assertIn("weighted_object_retention", enabled["experiment_result"]["metrics"])
        self.assertIn("critical_failures_before", enabled)

    def test_object_aware_compression_summary_and_outputs(self):
        records = run_object_aware_compression(
            [
                "branching_dependency_chunk_score_only",
                "branching_dependency_chunk_score_plus_object_support",
            ],
            cycles=1,
        )
        summary = summarize_object_aware_compression(records)
        self.assertEqual(summary["records"], 2)
        self.assertIn("branching_dependency_chunk_score_only", summary["suites"])
        self.assertIn("weighted_object_retention", summary["suites"]["branching_dependency_chunk_score_only"])
        self.assertIn("branching_dependency", summary["mechanism_verification"])
        self.assertIn("branching_dependency", summary["decision_boundary"])
        self.assertIn("decision_flip_distance_mean", summary["decision_boundary"]["branching_dependency"])
        self.assertIn("branching_dependency", summary["scenarios"])
        self.assertIn("delta_weighted_object_retention", summary["scenarios"]["branching_dependency"]["delta"])
        markdown = render_object_aware_compression_summary_markdown(summary)
        self.assertIn("# Object-Aware Compression Ablation", markdown)
        self.assertIn("Mechanism Verification", markdown)
        self.assertIn("Decision Boundary Sweep", markdown)
        self.assertIn("Flip Distance", markdown)
        self.assertIn("Scenario Deltas", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_object_aware_compression_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())


if __name__ == "__main__":
    unittest.main()
