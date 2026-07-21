from __future__ import annotations

import unittest

from experiments.benchmarks.common import BenchmarkCase, BenchmarkPrediction, BenchmarkRunBundle, BenchmarkRunConfig
from experiments.benchmarks.humaneval.report import render_humaneval_report


class HumanEvalReportTest(unittest.TestCase):
    def test_report_separates_execution_artifacts(self) -> None:
        bundle = BenchmarkRunBundle(
            config=BenchmarkRunConfig(
                benchmark_name="humaneval",
                dataset_version="humaneval_v1",
                model="model",
                prompt_format="humaneval_exec_v1",
            ),
            cases=(
                BenchmarkCase(
                    benchmark_name="humaneval",
                    case_id="task",
                    prompt="Write code.",
                ),
            ),
            predictions=(
                BenchmarkPrediction(
                    benchmark_name="humaneval",
                    case_id="task",
                    variant="baseline",
                    prompt="Write code.",
                    prediction="def f(): pass",
                    is_correct=True,
                    score=1.0,
                    metadata={"evaluation": {"failure_category": None}},
                ),
            ),
            metrics={
                "pass@1": 1.0,
                "baseline_pass@1": 1.0,
                "srp_pass@1": 1.0,
                "artifact_contract": {"files": ["config.json", "raw_predictions.jsonl", "execution_results.json", "metrics.json", "metadata.json", "report.md"]},
            },
            metadata={"generated_by": "test"},
        )
        report = render_humaneval_report(bundle, [{"task_id": "task", "variant": "baseline", "passed": True, "execution_time_seconds": 0.1}])
        self.assertIn("HumanEval Benchmark Report", report)
        self.assertIn("execution_results.json", report)
        self.assertIn("pass@1", report)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

