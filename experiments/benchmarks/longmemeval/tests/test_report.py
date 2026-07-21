from __future__ import annotations

import unittest

from experiments.benchmarks.common import BenchmarkCase, BenchmarkPrediction, BenchmarkRunBundle, BenchmarkRunConfig
from experiments.benchmarks.longmemeval.config import LongMemEvalBridgeConfig
from experiments.benchmarks.longmemeval.metrics import build_longmemeval_bridge_metrics
from experiments.benchmarks.longmemeval.report import render_longmemeval_bridge_report


class LongMemEvalBridgeReportTests(unittest.TestCase):
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

    def _build_bundle(self) -> tuple[BenchmarkRunBundle, dict[str, object], LongMemEvalBridgeConfig, dict[str, object]]:
        config = LongMemEvalBridgeConfig(
            bridge_name="longmemeval",
            bridge_version="bridge_migration_v1",
            bridge_output_dir="experiments/results/longmemeval_full_v1",
            source_path="tests/bridge.env",
        )
        benchmark_config = BenchmarkRunConfig(
            benchmark_name="longmemeval",
            dataset_version="2025",
            model="Qwen/Qwen3-4B-AWQ",
            prompt_format="longmemeval_shared_generation_prompt_v1",
        )
        cases = (
            BenchmarkCase(
                benchmark_name="longmemeval",
                case_id="case",
                prompt="What is the answer?",
                expected_answer="answer",
                reference_answer="answer",
                metadata={"release_source": {"version": "2025"}},
            ),
        )
        predictions = (
            BenchmarkPrediction(
                benchmark_name="longmemeval",
                case_id="case",
                variant="srp",
                prompt="What is the answer?",
                prediction="answer",
                reference_answer="answer",
                expected_answer="answer",
                is_correct=True,
                score=1.0,
            ),
        )
        outputs = self._fake_outputs()
        base_metrics = {
            "bridge_accuracy": 1.0,
            "bridge_srp_accuracy": 1.0,
            "bridge_accuracy_gap": 0.0,
        }
        metrics = build_longmemeval_bridge_metrics(
            base_metrics,
            outputs,
            config,
            sample_count=1,
            prediction_count=1,
            trace_count=1,
        )
        bundle = BenchmarkRunBundle(
            config=benchmark_config,
            cases=cases,
            predictions=predictions,
            metrics=metrics,
            metadata={
                "bridge_name": config.bridge_name,
                "bridge_version": config.bridge_version,
                "bridge_config_path": config.source_path,
                "bridge_output_dir": config.bridge_output_dir,
                "official_scorer_owner": "external_validation",
                "runtime_contract_owner": "external_validation",
                "payload_policy": "not_stored_in_repository",
                "trace_count": 1,
            },
        )
        return bundle, outputs, config, metrics

    def test_report_separates_official_score_and_diagnostics(self) -> None:
        bundle, outputs, config, metrics = self._build_bundle()
        report = render_longmemeval_bridge_report(bundle, outputs, config, metrics)

        self.assertIn("## Evaluation Authority", report)
        self.assertIn("official scorer owner: `external_validation`", report)
        self.assertIn("srp diagnostics owner: `longmemeval_bridge`", report)
        self.assertIn("## Official Result", report)
        self.assertIn("## SRP Diagnostics", report)
        self.assertIn("## Provenance", report)
        self.assertIn("payload policy", report)
        self.assertNotIn("combined_value", report)
        self.assertNotIn("merged_score", report)


if __name__ == "__main__":
    unittest.main()
