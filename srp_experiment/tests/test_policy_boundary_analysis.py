from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.policy_boundary_analysis import (
    build_policy_boundary_tasks,
    render_policy_boundary_markdown,
    run_policy_boundary_analysis,
    summarize_policy_boundary_records,
    write_policy_boundary_outputs,
)


class TestPolicyBoundaryAnalysis(unittest.TestCase):
    def test_build_policy_boundary_tasks(self) -> None:
        tasks = build_policy_boundary_tasks()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(
            [task.name for task in tasks],
            ["memory_saturation", "validation_pressure", "dependency_f1_pressure"],
        )
        self.assertTrue(all(task.semantic_unit_count > 0 for task in tasks))

    def test_summarize_policy_boundary_records_detects_boundary(self) -> None:
        records = [
            {
                "policy_boundary_suite": "memory_saturation",
                "policy_boundary_budget": 32,
                "policy_boundary": {
                    "benchmark": "memory_saturation",
                    "budget": 32,
                    "seed": 0,
                    "semantic_unit_count": 48,
                    "semantic_pressure_index": 1.5,
                },
                "state_allocation_result": {
                    "metrics": {
                        "active_object_count": 32,
                        "active_state_efficiency": 0.2,
                        "active_retention_ratio": 0.8,
                        "latent_preservation": 0.7,
                        "hallucination_isolation": 0.9,
                    }
                },
                "validation_coverage": 0.91,
                "dependency_coverage": 0.82,
                "dependency_precision": 0.74,
                "dependency_f1": 0.77,
                "graph_integrity_score": 0.88,
                "object_retention": 0.85,
                "weighted_object_retention": 0.84,
                "token_overhead": 0.0,
            },
            {
                "policy_boundary_suite": "memory_saturation",
                "policy_boundary_budget": 16,
                "policy_boundary": {
                    "benchmark": "memory_saturation",
                    "budget": 16,
                    "seed": 1,
                    "semantic_unit_count": 48,
                    "semantic_pressure_index": 3.0,
                },
                "state_allocation_result": {
                    "metrics": {
                        "active_object_count": 16,
                        "active_state_efficiency": 0.1,
                        "active_retention_ratio": 0.45,
                        "latent_preservation": 0.55,
                        "hallucination_isolation": 0.75,
                    }
                },
                "validation_coverage": 0.71,
                "dependency_coverage": 0.66,
                "dependency_precision": 0.48,
                "dependency_f1": 0.56,
                "graph_integrity_score": 0.68,
                "object_retention": 0.63,
                "weighted_object_retention": 0.61,
                "token_overhead": 0.0,
            },
        ]
        summary = summarize_policy_boundary_records(records)
        self.assertEqual(summary["records"], 2)
        benchmark = summary["benchmarks"]["memory_saturation"]
        self.assertEqual(benchmark["baseline_budget"], 32)
        self.assertTrue(benchmark["boundary"]["transition_detected"])
        self.assertEqual(benchmark["boundary"]["dominant_metric"], "active_retention_ratio")
        self.assertTrue(benchmark["dependency_f1_boundary"]["transition_detected"])
        markdown = render_policy_boundary_markdown(summary)
        self.assertIn("# Policy Boundary Analysis", markdown)
        self.assertIn("memory_saturation", markdown)

    def test_run_and_write_outputs(self) -> None:
        records = run_policy_boundary_analysis(budgets=[4], seeds=[0], cycles=1)
        self.assertEqual(len(records), 3)
        self.assertIn("policy_boundary", records[0])
        self.assertEqual(records[0]["policy_boundary"]["execution_state_source"], "active")
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_policy_boundary_outputs(records, Path(tmpdir))
            self.assertTrue(outputs["jsonl"].exists())
            self.assertTrue(outputs["csv"].exists())
            self.assertTrue(outputs["markdown"].exists())
            self.assertTrue(outputs["summary"].exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
