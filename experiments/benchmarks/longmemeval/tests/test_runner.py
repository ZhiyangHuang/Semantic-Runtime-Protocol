from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.benchmarks.longmemeval.config import LongMemEvalBridgeConfig
from experiments.benchmarks.longmemeval.metrics import build_longmemeval_bridge_metrics
from experiments.benchmarks.longmemeval.runner import LongMemEvalBridgeRunner


class LongMemEvalBridgeRunnerTests(unittest.TestCase):
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
                "pairwise_summary": {},
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
                "records": [
                    {
                        "run": {
                            "run_id": "longmemeval_srp_11_case",
                            "benchmark_name": "longmemeval",
                            "baseline_name": "srp",
                            "seed": 11,
                            "case": {
                                "case_id": "case",
                                "query": "What is the answer?",
                                "expected_answer": "answer",
                                "official_metric_name": "task_accuracy",
                                "metadata": {
                                    "release_source": {"version": "2025"},
                                },
                            },
                        },
                        "response": {"predicted_answer": "answer"},
                        "metrics": {
                            "semantic_coverage": 1.0,
                            "semantic_drift": 0.0,
                            "fact_accuracy": 1.0,
                            "relation_accuracy": 1.0,
                            "recovery_accuracy": 1.0,
                            "closure_accuracy": 1.0,
                            "neighborhood_completeness": 1.0,
                            "hallucinated_relation_rate": 0.0,
                            "evidence_cost": 1.0,
                            "answer_accuracy": 1.0,
                            "official_metric_score": 1.0,
                        },
                        "failure_categories": (),
                        "failure_notes": (),
                    }
                ],
            },
            "traces": [
                {
                    "run_id": "longmemeval_srp_11_case",
                    "generation_latency_seconds": 0.42,
                    "usage": {
                        "prompt_tokens": 12,
                        "completion_tokens": 4,
                        "total_tokens": 16,
                    },
                }
            ],
            "config": {
                "benchmark_name": "longmemeval",
                "baseline_names": ["full_context", "sliding_window", "vector_rag", "srp"],
                "seeds": [11, 23, 37],
                "data_root": "data/external/longmemeval",
                "benchmark_sample_limit": 1,
                "output_dir": "experiments/results/external_validation_longmemeval_evidence",
            },
        }

    def test_runner_delegates_and_writes_shared_artifacts(self) -> None:
        config = LongMemEvalBridgeConfig(
            bridge_name="longmemeval",
            bridge_version="bridge_migration_v1",
            bridge_output_dir="experiments/results/longmemeval_full_v1",
            source_path="tests/bridge.env",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("experiments.benchmarks.longmemeval.runner.run_longmemeval_evidence", return_value=self._fake_outputs()) as mocked_run:
                runner = LongMemEvalBridgeRunner(config=config)
                result = runner.run(output_dir=tmpdir)

            mocked_run.assert_called_once()
            self.assertEqual(result["bridge_version"], "bridge_migration_v1")
            self.assertEqual(result["bridge_name"], "longmemeval")

            output_path = Path(tmpdir)
            self.assertTrue((output_path / "config.json").exists())
            self.assertTrue((output_path / "raw_predictions.jsonl").exists())
            self.assertTrue((output_path / "metrics.json").exists())
            self.assertTrue((output_path / "metadata.json").exists())
            self.assertTrue((output_path / "report.md").exists())

            metadata = json.loads((output_path / "metadata.json").read_text(encoding="utf-8"))
            metrics = json.loads((output_path / "metrics.json").read_text(encoding="utf-8"))
            raw_predictions = (output_path / "raw_predictions.jsonl").read_text(encoding="utf-8").strip().splitlines()

            self.assertEqual(metadata["official_scorer_owner"], "external_validation")
            self.assertEqual(metadata["runtime_contract_owner"], "external_validation")
            self.assertEqual(metadata["payload_policy"], "not_stored_in_repository")
            self.assertEqual(metrics["official_metric_name"], "task_accuracy")
            self.assertEqual(metrics["official_score"]["source"], "external_validation")
            self.assertEqual(metrics["official_score"]["value"], 1.0)
            self.assertEqual(metrics["srp_diagnostics"]["source"], "longmemeval_bridge")
            self.assertEqual(metrics["official_summary"]["official_metric_score"], 1.0)
            self.assertEqual(len(raw_predictions), 1)
            self.assertIn("official_scorer_owner", raw_predictions[0])
            self.assertIn("longmemeval", raw_predictions[0])

    def test_bundle_preserves_official_score_and_diagnostics(self) -> None:
        config = LongMemEvalBridgeConfig(
            bridge_name="longmemeval",
            bridge_version="bridge_migration_v1",
            bridge_output_dir="experiments/results/longmemeval_full_v1",
            source_path="tests/bridge.env",
        )
        runner = LongMemEvalBridgeRunner(config=config)
        base_bundle = runner.build_bundle(self._fake_outputs())
        metrics = build_longmemeval_bridge_metrics(
            base_bundle.metrics,
            self._fake_outputs(),
            config,
            sample_count=1,
            prediction_count=1,
            trace_count=1,
        )

        self.assertEqual(metrics["official_score"]["value"], 1.0)
        self.assertEqual(metrics["official_score"]["source"], "external_validation")
        self.assertEqual(metrics["srp_diagnostics"]["case_count"], 1)
        self.assertEqual(metrics["srp_diagnostics"]["source"], "longmemeval_bridge")
        self.assertEqual(base_bundle.predictions[0].metadata["official_scorer_owner"], "external_validation")
        self.assertEqual(base_bundle.predictions[0].metadata["runtime_contract_owner"], "external_validation")


if __name__ == "__main__":
    unittest.main()
