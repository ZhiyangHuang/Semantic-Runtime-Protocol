from __future__ import annotations

import unittest

from experiments.benchmarks.common import BenchmarkPrediction
from experiments.benchmarks.humaneval.adapter import HumanEvalAdapter


class HumanEvalMetricsTest(unittest.TestCase):
    def test_summarize_metrics(self) -> None:
        predictions = (
            BenchmarkPrediction(
                benchmark_name="humaneval",
                case_id="a",
                variant="baseline",
                prompt="prompt",
                prediction="def a(): pass",
                is_correct=True,
                score=1.0,
                metadata={"evaluation": {"failure_category": None}},
            ),
            BenchmarkPrediction(
                benchmark_name="humaneval",
                case_id="a",
                variant="srp",
                prompt="prompt",
                prediction="def a(): pass",
                is_correct=False,
                score=0.0,
                metadata={"evaluation": {"failure_category": "runtime_error"}},
            ),
        )
        metrics = HumanEvalAdapter().summarize_metrics(predictions, cases=())
        self.assertIn("pass@1", metrics)
        self.assertEqual(metrics["baseline_pass@1"], 1.0)
        self.assertEqual(metrics["srp_pass@1"], 0.0)
        self.assertEqual(metrics["runtime_error_count"], 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

