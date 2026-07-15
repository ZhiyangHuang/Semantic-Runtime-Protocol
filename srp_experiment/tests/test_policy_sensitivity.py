from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from srp_experiment.policy_sensitivity import run_policy_sensitivity, summarize_policy_sensitivity, write_policy_sensitivity_outputs


class PolicySensitivityAnalysisTest(unittest.TestCase):
    def test_summarize_policy_sensitivity(self) -> None:
        records = [
            {
                "sensitivity_axis": "importance_threshold",
                "sensitivity_value": 0.2,
                "experiment_result": {"metrics": {"validation_coverage": 0.5, "graph_integrity_score": 0.6, "object_retention": 0.7, "weighted_object_retention": 0.75, "token_overhead": 1.0}},
            },
            {
                "sensitivity_axis": "importance_threshold",
                "sensitivity_value": 0.35,
                "experiment_result": {"metrics": {"validation_coverage": 0.45, "graph_integrity_score": 0.65, "object_retention": 0.8, "weighted_object_retention": 0.82, "token_overhead": 1.2}},
            },
            {
                "sensitivity_axis": "budget_pressure",
                "sensitivity_value": 64,
                "experiment_result": {"metrics": {"validation_coverage": 0.4, "graph_integrity_score": 0.55, "object_retention": 0.75, "weighted_object_retention": 0.78, "token_overhead": 2.0}},
            },
        ]
        summary = summarize_policy_sensitivity(records)
        self.assertEqual(summary["records"], 3)
        self.assertIn("importance_threshold", summary["axes"])
        self.assertIn("budget_pressure", summary["axes"])
        self.assertGreaterEqual(len(summary["axes"]["importance_threshold"]["values"]), 2)

    def test_run_and_write_outputs(self) -> None:
        records = run_policy_sensitivity(task_suites=["structured_recovery"], cycles=1)
        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_policy_sensitivity_outputs(records, tmp)
            for path in outputs.values():
                self.assertTrue(Path(path).exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
