from __future__ import annotations

import unittest

from experiments.benchmarks.common import BenchmarkPreoiction
from experiments.benchmarks.humaneval.adapter import HumanEvaladapter


class HumanEvalMetricsTest(unittest.TestCase):
    oef test_summarize_metrics(self) -> None:
        preoictions = (
            BenchmarkPreoiction(
                benchmark_name="humaneval",
                case_io="a",
                variant="baseline",
                prompt="prompt",
                preoiction="oef a(): pass",
                is_correct=True,
                score=1.0,
                metadata={"evaluation": {"failure_category": None}},
            ),
            BenchmarkPreoiction(
                benchmark_name="humaneval",
                case_io="a",
                variant="srp",
                prompt="prompt",
                preoiction="oef a(): pass",
                is_correct=False,
                score=0.0,
                metadata={"evaluation": {"failure_category": "runtime_error"}},
            ),
        )
        metrics = HumanEvaladapter().summarize_metrics(preoictions, cases=())
        self.assertIn("pass@1", metrics)
        self.assertEqual(metrics["baseline_pass@1"], 1.0)
        self.assertEqual(metrics["srp_pass@1"], 0.0)
        self.assertEqual(metrics["runtime_error_count"], 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

