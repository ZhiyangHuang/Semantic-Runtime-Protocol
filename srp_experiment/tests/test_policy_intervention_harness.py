from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.policy_intervention_harness import (
    run_policy_intervention_harness,
    summarize_policy_intervention_records,
    write_policy_intervention_outputs,
)


class PolicyInterventionHarnessTest(unittest.TestCase):
    def test_summarize_policy_intervention_records(self) -> None:
        records = [
            {
                "policy_suite": "baseline",
                "experiment_result": {
                    "metrics": {
                        "validation_coverage": 0.31,
                        "important_object_recall": 0.9,
                        "task_critical_object_recall": 0.8,
                        "graph_integrity_score": 0.5,
                        "graph_repair_cost": 12.0,
                        "token_overhead": 3.0,
                        "object_retention": 0.6,
                    }
                },
                "validation_passed": False,
            },
            {
                "policy_suite": "permissive",
                "experiment_result": {
                    "metrics": {
                        "validation_coverage": 0.35,
                        "important_object_recall": 0.95,
                        "task_critical_object_recall": 0.85,
                        "graph_integrity_score": 0.55,
                        "graph_repair_cost": 10.0,
                        "token_overhead": 4.0,
                        "object_retention": 0.7,
                    }
                },
                "validation_passed": True,
            },
        ]
        summary = summarize_policy_intervention_records(records)
        self.assertEqual(summary["records"], 2)
        self.assertIn("baseline", summary["policy_suites"])
        self.assertIn("permissive", summary["policy_suites"])
        self.assertAlmostEqual(summary["policy_suites"]["permissive"]["delta_validation_coverage"], 0.04)
        self.assertEqual(summary["best_by_validation_coverage"], "permissive")
        self.assertEqual(summary["best_by_object_retention"], "permissive")
        self.assertIn("object_retention_mean", summary["policy_suites"]["permissive"])

    def test_run_and_write_outputs(self) -> None:
        records = run_policy_intervention_harness(policy_suites=["baseline"], task_suites=["structured_recovery"], cycles=1)
        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_policy_intervention_outputs(records, tmp)
            for key in ["jsonl", "csv", "markdown", "summary", "policy_attribution_dir"]:
                path = Path(outputs[key])
                self.assertTrue(path.exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
