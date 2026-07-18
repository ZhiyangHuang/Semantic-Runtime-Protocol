from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.analysis.policy_pareto import summarize_policy_pareto, write_policy_pareto_outputs


class PolicyParetoAnalysisTest(unittest.TestCase):
    def test_summarize_policy_pareto(self) -> None:
        records = [
            {
                "policy_suite": "baseline",
                "experiment_result": {"metrics": {"validation_coverage": 0.45, "graph_integrity_score": 0.59, "object_retention": 0.75, "weighted_object_retention": 0.80, "graph_repair_cost": 12.0, "token_overhead": 0.0}},
            },
            {
                "policy_suite": "permissive",
                "experiment_result": {"metrics": {"validation_coverage": 0.46, "graph_integrity_score": 0.59, "object_retention": 0.75, "weighted_object_retention": 0.80, "graph_repair_cost": 12.0, "token_overhead": 0.0}},
            },
            {
                "policy_suite": "balanced",
                "experiment_result": {"metrics": {"validation_coverage": 0.37, "graph_integrity_score": 0.66, "object_retention": 1.0, "weighted_object_retention": 0.81, "graph_repair_cost": 12.0, "token_overhead": 0.0}},
            },
            {
                "policy_suite": "conservative",
                "experiment_result": {"metrics": {"validation_coverage": 0.37, "graph_integrity_score": 0.66, "object_retention": 1.0, "weighted_object_retention": 0.81, "graph_repair_cost": 12.0, "token_overhead": 0.0}},
            },
        ]
        summary = summarize_policy_pareto(records)
        self.assertIn("pareto_front", summary)
        self.assertTrue(summary["pareto_front"])
        self.assertIn("balanced", summary["pareto_front"])
        self.assertIn("conservative", summary["pareto_front"])
        self.assertEqual(summary["policy_suites"]["balanced"]["metrics"]["graph_integrity_score"], 0.66)

    def test_write_policy_pareto_outputs(self) -> None:
        records = [
            {
                "policy_suite": "baseline",
                "experiment_result": {"metrics": {"validation_coverage": 0.45, "graph_integrity_score": 0.59, "object_retention": 0.75, "weighted_object_retention": 0.80, "graph_repair_cost": 12.0, "token_overhead": 0.0}},
            },
            {
                "policy_suite": "permissive",
                "experiment_result": {"metrics": {"validation_coverage": 0.46, "graph_integrity_score": 0.59, "object_retention": 0.75, "weighted_object_retention": 0.80, "graph_repair_cost": 12.0, "token_overhead": 0.0}},
            },
        ]
        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_policy_pareto_outputs(records, tmp)
            for path in outputs.values():
                self.assertTrue(Path(path).exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
