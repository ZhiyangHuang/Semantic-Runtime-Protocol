from __future__ import annotations

import unittest

from experiments.benchmarks.humaneval.executor import HumanEvalExecutor


class HumanEvalExecutorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.executor = HumanEvalExecutor(timeout_seconds=2.0)

    def test_passes_simple_assertion(self) -> None:
        result = self.executor.execute(
            task_id="add_one",
            variant="baseline",
            generated_code="def add_one(x):\n    return x + 1\n",
            test_specification="assert add_one(1) == 2",
        )
        self.assertTrue(result.passed)
        self.assertIsNone(result.failure_category)

    def test_reports_assertion_failure(self) -> None:
        result = self.executor.execute(
            task_id="add_one",
            variant="baseline",
            generated_code="def add_one(x):\n    return x\n",
            test_specification="assert add_one(1) == 2",
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.failure_category, "failed_assertion")

    def test_reports_syntax_error(self) -> None:
        result = self.executor.execute(
            task_id="broken",
            variant="baseline",
            generated_code="def broken(x)\n    return x",
            test_specification="assert True",
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.failure_category, "syntax_error")

    def test_reports_timeout(self) -> None:
        result = HumanEvalExecutor(timeout_seconds=0.5).execute(
            task_id="slow",
            variant="baseline",
            generated_code="while True:\n    pass\n",
            test_specification="assert True",
        )
        self.assertFalse(result.passed)
        self.assertEqual(result.failure_category, "timeout")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
