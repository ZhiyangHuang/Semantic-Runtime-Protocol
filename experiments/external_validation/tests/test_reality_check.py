from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from experiments.external_validation.reality_check import (
    build_longmemeval_reality_check_report,
    load_longmemeval_reality_check_config,
    write_longmemeval_reality_check_outputs,
)


class LongMemEvalRealityCheckTests(unittest.TestCase):
    def test_load_reality_check_config(self) -> None:
        config = load_longmemeval_reality_check_config(Path("configs/external_validation_longmemeval_reality_check.env"))
        self.assertEqual(config.benchmark_name, "longmemeval")
        self.assertEqual(config.benchmark_sample_limit, 2)
        self.assertEqual(config.model_name, "Qwen/Qwen3-4B-AWQ")

    def test_build_reality_check_report(self) -> None:
        outputs = {
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
                "summary": {"case_count": 2, "answer_accuracy": 1.0, "official_metric_score": 1.0},
                "benchmark_summary": {"longmemeval": {"case_count": 2, "answer_accuracy": 1.0}},
                "baseline_summary": {"srp": {"case_count": 2}},
                "pairwise_summary": {},
                "failure_summary": {"none": 2},
                "records": [
                    {
                        "run": {"baseline_name": "srp"},
                        "metrics": {
                            "semantic_coverage": 1.0,
                            "semantic_drift": 0.0,
                            "fact_accuracy": 1.0,
                            "relation_accuracy": 1.0,
                            "recovery_accuracy": 1.0,
                            "closure_accuracy": 1.0,
                            "hallucinated_relation_rate": 0.0,
                            "evidence_cost": 1.0,
                            "answer_accuracy": 1.0,
                            "official_metric_score": 1.0,
                        },
                    }
                ],
            },
            "traces": [],
            "config": {
                "benchmark_name": "longmemeval",
                "baseline_names": ["full_context", "sliding_window", "vector_rag", "srp"],
                "seeds": [11, 23, 37],
                "data_root": "data/longmemeval",
                "benchmark_sample_limit": 2,
            },
        }
        report = build_longmemeval_reality_check_report(outputs)
        self.assertEqual(report["report_type"], "reality_check")
        self.assertEqual(report["srp_diagnostics"]["case_count"], 1)
        self.assertIn("negative_transition_signals", report)
        self.assertNotIn("artifact_integrity", report)

    def test_write_reality_check_outputs_with_mocked_run(self) -> None:
        fake_outputs = {
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
                "summary": {"case_count": 1, "answer_accuracy": 1.0, "official_metric_score": 1.0},
                "benchmark_summary": {"longmemeval": {"case_count": 1, "answer_accuracy": 1.0}},
                "baseline_summary": {"srp": {"case_count": 1}},
                "pairwise_summary": {},
                "failure_summary": {"none": 1},
                "records": [
                    {
                        "run": {
                            "run_id": "longmemeval_srp_11_case",
                            "benchmark_name": "longmemeval",
                            "baseline_name": "srp",
                            "seed": 11,
                            "case": {
                                "case_id": "case",
                                "query": "q",
                                "expected_answer": "a",
                            },
                        },
                        "response": {"predicted_answer": "a"},
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
                    }
                ],
            },
            "traces": [],
            "config": {
                "benchmark_name": "longmemeval",
                "baseline_names": ["full_context", "sliding_window", "vector_rag", "srp"],
                "seeds": [11, 23, 37],
                "data_root": "data/longmemeval",
                "benchmark_sample_limit": 2,
                "output_dir": "experiments/results/external_validation_longmemeval_reality_check",
            },
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("experiments.external_validation.reality_check.run_longmemeval_evidence", return_value=fake_outputs):
                outputs = write_longmemeval_reality_check_outputs(tmpdir)
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["runtime_manifest_json"]).exists())
            self.assertTrue(Path(outputs["artifact_integrity_json"]).exists())


if __name__ == "__main__":
    unittest.main()
