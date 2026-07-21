from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from experiments.benchmarks.common import BenchmarkCase, BenchmarkRunConfig
from experiments.benchmarks.arc.adapter import ARCAdapter


class ARCAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = ARCAdapter()

    def test_record_conversion(self) -> None:
        dataset = [
            {
                "id": "arc-1",
                "subset": "ARC-Easy",
                "question": "Which color is the sky?",
                "choices": ["red", "blue", "green", "yellow"],
                "answerKey": "B",
                "split": "test",
                "srp_context": {"evidence": "common knowledge"},
                "recovered_context": {"evidence": "recovered common knowledge"},
            }
        ]
        cases = self.adapter.create_cases(dataset, BenchmarkRunConfig(benchmark_name="arc", dataset_version="v1", model="m", prompt_format="p"))
        self.assertEqual(len(cases), 1)
        case = cases[0]
        self.assertEqual(case.case_id, "arc-1")
        self.assertEqual(case.expected_answer, "B")
        self.assertEqual(case.choices, ("red", "blue", "green", "yellow"))
        self.assertEqual(case.metadata["subset"], "ARC-Easy")
        self.assertNotIn("expected_answer", case.srp_recovered_context)

    def test_prompt_leakage_guard(self) -> None:
        dataset = [
            {
                "id": "arc-1",
                "subset": "ARC-Easy",
                "question": "Which color is the sky?",
                "choices": ["red", "blue", "green", "yellow"],
                "answerKey": "B",
                "split": "test",
            }
        ]
        cases = self.adapter.create_cases(dataset, BenchmarkRunConfig(benchmark_name="arc", dataset_version="v1", model="m", prompt_format="p"))
        case = cases[0]
        prompt = self.adapter.build_prompt(case, "srp")
        self.adapter.validate_prompt_leakage(case, "srp", prompt)

    def test_choice_handling(self) -> None:
        choices = ("red", "blue", "green", "yellow")
        self.assertEqual(self.adapter.extract_choice("I choose B.", choices), "B")
        self.assertEqual(self.adapter.extract_choice("green", choices), "C")
        self.assertIsNone(self.adapter.extract_choice("unknown", choices))

    def test_answer_normalization(self) -> None:
        labels = ("A", "B", "C", "D")
        self.assertEqual(self.adapter.normalize_answer("1", labels, ("a", "b", "c", "d")), "B")
        self.assertEqual(self.adapter.normalize_answer("c", labels, ("a", "b", "c", "d")), "C")
        self.assertEqual(self.adapter.normalize_answer("yellow", labels, ("red", "blue", "green", "yellow")), "D")

    def test_scoring(self) -> None:
        case = BenchmarkCase(
            benchmark_name="arc",
            case_id="case-1",
            prompt="prompt",
            expected_answer="C",
            reference_answer="green",
            choices=("red", "blue", "green", "yellow"),
            metadata={"subset": "ARC-Easy"},
        )
        correct = self.adapter.evaluate_prediction(case, "C", "baseline")
        wrong = self.adapter.evaluate_prediction(case, "A", "baseline")
        invalid = self.adapter.evaluate_prediction(case, "maybe", "baseline")
        self.assertTrue(correct["is_correct"])
        self.assertFalse(wrong["is_correct"])
        self.assertTrue(invalid["invalid_output"])

    def test_load_dataset_from_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "arc_easy.jsonl").write_text(
                '{"id":"x1","subset":"ARC-Easy","question":"Q?","choices":["a","b"],"answerKey":"B"}\n',
                encoding="utf-8",
            )
            records = self.adapter.load_dataset(root, sample_limit=1)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["id"], "x1")


if __name__ == "__main__":
    unittest.main()
