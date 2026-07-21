from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from experiments.benchmarks.common import BenchmarkCase, BenchmarkPrediction, BenchmarkRunConfig
from experiments.benchmarks.mmlu.adapter import MMLUAdapter


class MMLUAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = MMLUAdapter()

    def test_dataset_record_conversion(self) -> None:
        dataset = [
            {
                "id": "mmlu-1",
                "subject": "math",
                "question": "What is 2 + 2?",
                "choices": ["1", "4", "5", "6"],
                "answer": 1,
                "split": "test",
                "srp_context": {"evidence": "addition facts"},
                "recovered_context": {"evidence": "recovered addition facts"},
            }
        ]
        cases = self.adapter.create_cases(dataset, BenchmarkRunConfig(benchmark_name="mmlu", dataset_version="v1", model="m", prompt_format="p"))
        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertEqual(case.case_id, "mmlu-1")
        self.assertEqual(case.expected_answer, "B")
        self.assertEqual(case.choices, ("1", "4", "5", "6"))
        self.assertEqual(case.metadata["subject"], "math")
        self.assertNotIn("expected_answer", case.srp_recovered_context)

    def test_prompt_leakage_guard(self) -> None:
        dataset = [
            {
                "id": "mmlu-1",
                "subject": "math",
                "question": "What is 2 + 2?",
                "choices": ["1", "4", "5", "6"],
                "answer": 1,
                "split": "test",
            }
        ]
        cases = self.adapter.create_cases(dataset, BenchmarkRunConfig(benchmark_name="mmlu", dataset_version="v1", model="m", prompt_format="p"))
        case = cases[0]
        prompt = self.adapter.build_prompt(case, "srp")
        self.adapter.validate_prompt_leakage(case, "srp", prompt)

    def test_choice_extraction(self) -> None:
        choices = ("red", "blue", "green", "yellow")
        self.assertEqual(self.adapter.extract_choice("I think the answer is B.", choices), "B")
        self.assertEqual(self.adapter.extract_choice("blue", choices), "B")
        self.assertIsNone(self.adapter.extract_choice("cannot parse", choices))

    def test_answer_parsing(self) -> None:
        labels = ("A", "B", "C", "D")
        self.assertEqual(self.adapter.normalize_answer("2", labels, ("x", "y", "z", "w")), "C")
        self.assertEqual(self.adapter.normalize_answer("b", labels, ("x", "y", "z", "w")), "B")
        self.assertEqual(self.adapter.normalize_answer("Green", labels, ("red", "blue", "green", "yellow")), "C")

    def test_accuracy_calculation(self) -> None:
        case = BenchmarkCase(
            benchmark_name="mmlu",
            case_id="case-1",
            prompt="prompt",
            expected_answer="B",
            reference_answer="4",
            choices=("1", "4", "5", "6"),
            metadata={"subject": "math"},
        )
        correct = self.adapter.evaluate_prediction(case, "B", "baseline")
        wrong = self.adapter.evaluate_prediction(case, "A", "baseline")
        invalid = self.adapter.evaluate_prediction(case, "maybe", "baseline")

        self.assertTrue(correct["is_correct"])
        self.assertFalse(wrong["is_correct"])
        self.assertTrue(invalid["invalid_output"])

    def test_load_dataset_from_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "mmlu.jsonl").write_text(
                '{"id":"x1","subject":"history","question":"Q?","choices":["a","b"],"answer":"B"}\n',
                encoding="utf-8",
            )
            records = self.adapter.load_dataset(root, sample_limit=1)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["id"], "x1")


if __name__ == "__main__":
    unittest.main()
