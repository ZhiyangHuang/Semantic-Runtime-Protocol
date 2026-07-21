from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from experiments.benchmarks.common import (
    BenchmarkAdapter,
    BenchmarkCase,
    BenchmarkGenerationBackend,
    BenchmarkRunConfig,
    BenchmarkRunner,
    assert_no_prompt_leakage,
    write_benchmark_artifact,
)


class _DummyBackend:
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_output_tokens: int = 128,
        temperature: float = 0.0,
    ) -> dict[str, object]:
        return {
            "text": prompt,
            "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": 1, "total_tokens": len(prompt.split()) + 1},
            "latency_seconds": 0.01,
            "model": "dummy-model",
        }


class _DummyAdapter:
    name = "dummy-benchmark"

    def load_dataset(self, data_root=None, sample_limit=None):
        return [
            {"case_id": "case-1", "prompt": "alpha", "expected_answer": "alpha"},
            {"case_id": "case-2", "prompt": "beta", "expected_answer": "beta"},
        ]

    def create_cases(self, dataset, config=None):
        return [
            BenchmarkCase(
                benchmark_name=self.name,
                case_id=str(item["case_id"]),
                prompt=str(item["prompt"]),
                expected_answer=str(item["expected_answer"]),
                reference_answer=str(item["expected_answer"]),
                metadata={"source": "dummy"},
            )
            for item in dataset
        ]

    def build_prompt(self, case, variant, config=None):
        if variant == "baseline":
            return case.expected_answer
        return f"{case.expected_answer}-srp"

    def evaluate_prediction(self, case, prediction, variant, config=None):
        is_correct = prediction == case.expected_answer
        return {"is_correct": is_correct, "score": 1.0 if is_correct else 0.0}

    def summarize_metrics(self, predictions, cases=None, config=None):
        return {"adapter_metric_name": "dummy_accuracy"}


class BenchmarkCommonTest(unittest.TestCase):
    def test_runner_and_artifact_writer(self) -> None:
        config = BenchmarkRunConfig(
            benchmark_name="dummy-benchmark",
            dataset_version="v1",
            model="dummy-model",
            prompt_format="plain",
            variants=("baseline", "srp"),
            sample_limit=2,
        )
        runner = BenchmarkRunner(adapter=_DummyAdapter(), backend=_DummyBackend(), config=config)
        bundle = runner.run()

        self.assertEqual(len(bundle.cases), 2)
        self.assertEqual(len(bundle.predictions), 4)
        self.assertIn("accuracy", bundle.metrics)
        self.assertIn("adapter_metric_name", bundle.metrics)
        self.assertTrue(bundle.report_markdown.startswith("# dummy-benchmark Benchmark Report"))

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_benchmark_artifact(tmpdir, bundle)
            for key in ("config_json", "raw_predictions_jsonl", "metrics_json", "report_md", "metadata_json"):
                self.assertTrue(Path(outputs[key]).exists())
            metadata = json.loads(Path(outputs["metadata_json"]).read_text(encoding="utf-8"))
            self.assertIn("artifact_hashes", metadata)
            self.assertIn("report_md", metadata["artifact_hashes"])

    def test_case_serialization_round_trip(self) -> None:
        case = BenchmarkCase(
            benchmark_name="dummy",
            case_id="c1",
            prompt="prompt",
            reference_answer="ref",
            expected_answer="exp",
            choices=("a", "b"),
            srp_input_context={"context": "original"},
            srp_recovered_context={"context": "recovered"},
            metadata={"split": "test"},
        )

        payload = case.as_dict()
        self.assertEqual(payload["case_id"], "c1")
        self.assertEqual(payload["choices"], ("a", "b"))
        self.assertEqual(payload["metadata"]["split"], "test")

    def test_prompt_leakage_guard(self) -> None:
        with self.assertRaises(ValueError):
            assert_no_prompt_leakage(
                "Recovered semantic context: expected_answer: B",
                context={"expected_answer": "B"},
            )

        assert_no_prompt_leakage(
            "Subject: math\nQuestion: What is 2 + 2?\nA. 1\nB. 4",
            context={"subject": "math", "question": "What is 2 + 2?", "choices": ("1", "4")},
        )


if __name__ == "__main__":
    unittest.main()
