from __future__ import annotations

import unittest

from experiments.benchmarks.longmemeval.config import LongMemEvalBridgeConfig
from experiments.benchmarks.longmemeval.metrics import build_longmemeval_bridge_metrics, summarize_bridge_coverage


class LongMemEvalBridgeMetricsTests(unittest.TestCase):
    def _fake_outputs(self) -> dict[str, object]:
        return {
            "runtime_manifest": {
                "benchmark_name": "longmemeval",
                "model_environment": {
                    "provider": "local_vllm",
                    "backend": "vllm",
                    "endpoint": "http://localhost:8000",
                    "model": "Qwen/Qwen3-4B-AWQ",
                    "tokenizer": "Qwen/Qwen3-4B-AWQ",
                    "prompt_template_id": "longmemeval_shared_generation_prompt_v1",
                    "temperature": 0.0,
                    "max_output_tokens": 96,
                },
                "runtime_policy": {
                    "same_endpoint_across_baselines": True,
                    "baseline_generation_backend": "shared",
                    "srp_generation_backend": "shared",
                },
            },
            "report": {
                "summary": {
                    "case_count": 1,
                    "answer_accuracy": 1.0,
                    "official_metric_score": 1.0,
                    "official_metric_name": "task_accuracy",
                },
                "benchmark_summary": {"longmemeval": {"case_count": 1, "answer_accuracy": 1.0}},
                "baseline_summary": {"srp": {"case_count": 1, "answer_accuracy": 1.0}},
                "failure_summary": {"none": 1},
                "srp_diagnostics": {
                    "case_count": 1,
                    "semantic_coverage_mean": 1.0,
                    "semantic_drift_mean": 0.0,
                    "fact_accuracy_mean": 1.0,
                    "relation_accuracy_mean": 1.0,
                    "recovery_accuracy_mean": 1.0,
                    "closure_accuracy_mean": 1.0,
                    "hallucinated_relation_rate_mean": 0.0,
                    "evidence_cost_mean": 1.0,
                    "answer_accuracy_mean": 1.0,
                    "official_metric_score_mean": 1.0,
                },
            },
            "traces": [{"run_id": "longmemeval_srp_11_case"}],
        }

    def test_metrics_keep_official_score_and_diagnostics_separate(self) -> None:
        config = LongMemEvalBridgeConfig(
            bridge_name="longmemeval",
            bridge_version="bridge_migration_v1",
            bridge_output_dir="experiments/results/longmemeval_full_v1",
            source_path="tests/bridge.env",
        )
        base_metrics = {
            "bridge_accuracy": 0.5,
            "bridge_srp_accuracy": 1.0,
            "bridge_accuracy_gap": 0.5,
        }

        metrics = build_longmemeval_bridge_metrics(
            base_metrics,
            self._fake_outputs(),
            config,
            sample_count=1,
            prediction_count=2,
            trace_count=1,
        )

        self.assertEqual(metrics["official_score"]["source"], "external_validation")
        self.assertEqual(metrics["official_score"]["value"], 1.0)
        self.assertEqual(metrics["srp_diagnostics"]["source"], "longmemeval_bridge")
        self.assertEqual(metrics["srp_diagnostics"]["case_count"], 1)
        self.assertNotIn("score", metrics)
        self.assertEqual(metrics["artifact_contract"]["source"], "shared_benchmark_artifact_contract")
        self.assertEqual(metrics["artifact_contract"]["files"], ["config.json", "raw_predictions.jsonl", "metrics.json", "metadata.json", "report.md"])

    def test_bridge_coverage_summary(self) -> None:
        config = LongMemEvalBridgeConfig(
            bridge_name="longmemeval",
            bridge_version="bridge_migration_v1",
            bridge_output_dir="experiments/results/longmemeval_full_v1",
            source_path="tests/bridge.env",
        )
        metrics = build_longmemeval_bridge_metrics(
            {"bridge_accuracy": 0.5, "bridge_srp_accuracy": 0.75, "bridge_accuracy_gap": 0.25},
            self._fake_outputs(),
            config,
            sample_count=1,
            prediction_count=2,
            trace_count=1,
        )
        coverage = summarize_bridge_coverage(metrics)

        self.assertEqual(coverage["official_score_source"], "external_validation")
        self.assertEqual(coverage["srp_diagnostics_source"], "longmemeval_bridge")
        self.assertEqual(coverage["artifact_files_count"], 5)
        self.assertEqual(coverage["metric_schema_version"], "benchmark_metrics_schema.v1")


if __name__ == "__main__":
    unittest.main()

