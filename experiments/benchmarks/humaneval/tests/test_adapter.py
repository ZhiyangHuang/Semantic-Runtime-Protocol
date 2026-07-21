from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from experiments.benchmarks.humaneval.adapter import HumanEvalAdapter
from experiments.benchmarks.humaneval.config import HumanEvalConfig


class HumanEvalAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = HumanEvalAdapter()

    def _write_dataset(self, tmpdir: Path) -> Path:
        path = tmpdir / "humaneval.jsonl"
        path.write_text(
            "\n".join(
                [
                    '{"task_id":"add_one","prompt":"Write add_one(x) that returns x + 1.","entry_point":"add_one","reference_solution":"def add_one(x):\\n    return x + 1","test_code":"assert add_one(1) == 2","public_test":"assert add_one(0) == 1"}',
                    '{"task_id":"mul_two","prompt":"Write mul_two(x) that returns x * 2.","entry_point":"mul_two","reference_solution":"def mul_two(x):\\n    return x * 2","test_code":"assert mul_two(2) == 4","public_test":"assert mul_two(3) == 6"}',
                ]
            ),
            encoding="utf-8",
        )
        return path

    def test_load_dataset_and_create_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_dataset(Path(tmp))
            dataset = self.adapter.load_dataset(path)
            self.assertEqual(len(dataset), 2)
            cases = self.adapter.create_cases(dataset, HumanEvalConfig())
            self.assertEqual(len(cases), 2)
            self.assertEqual(cases[0].case_id, "add_one")
            self.assertEqual(cases[0].metadata["entry_point"], "add_one")
            self.assertTrue(cases[0].metadata["test_specification_digest"])

    def test_build_prompt_and_leakage_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write_dataset(Path(tmp))
            cases = self.adapter.create_cases(self.adapter.load_dataset(path), HumanEvalConfig())
            prompt = self.adapter.build_prompt(cases[0], "srp", HumanEvalConfig())
            self.assertIn("Recovered semantic context", prompt)
            self.assertNotIn("reference_solution", prompt.lower())
            self.assertNotIn("test_code", prompt.lower())
            self.adapter.validate_prompt_leakage(cases[0], "srp", prompt, HumanEvalConfig())

    def test_extract_code(self) -> None:
        code, status = self.adapter.extract_code("Here is code:\n```python\ndef add_one(x):\n    return x + 1\n```")
        self.assertEqual(status, "fenced")
        self.assertIn("def add_one", code)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
