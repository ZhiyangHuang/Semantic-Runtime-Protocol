from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from experiments.benchmarks.humaneval.adapter import HumanEvalAdapter
from experiments.benchmarks.humaneval.config import HumanEvalConfig
from experiments.benchmarks.humaneval.executor import HumanEvalExecutionResult
from experiments.benchmarks.humaneval.runner import HumanEvalRunner


class _FakeBackend:
    def generate(self, prompt: str, system_prompt: str = "", max_output_tokens: int = 128, temperature: float = 0.0):
        del system_prompt, max_output_tokens, temperature
        return {
            "text": "```python\ndef add_one(x):\n    return x + 1\n```",
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            "latency_seconds": 0.01,
            "model": "fake-model",
        }


class _FakeExecutor:
    def execute(self, *, task_id: str, variant: str, generated_code: str, test_specification: str, metadata=None):
        del generated_code, test_specification, metadata
        return HumanEvalExecutionResult(
            task_id=task_id,
            variant=variant,
            passed=True,
            execution_time_seconds=0.01,
        )


class HumanEvalRunnerTest(unittest.TestCase):
    def test_runner_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset_path = root / "humaneval.jsonl"
            dataset_path.write_text(
                '{"task_id":"add_one","prompt":"Write add_one(x).","entry_point":"add_one","reference_solution":"def add_one(x): return x + 1","test_code":"assert add_one(1) == 2"}\n',
                encoding="utf-8",
            )
            config = HumanEvalConfig(
                data_root=str(dataset_path),
                sample_limit=1,
                execution_timeout_seconds=1.0,
            )
            runner = HumanEvalRunner(
                config=config,
                adapter=HumanEvalAdapter(),
                backend=_FakeBackend(),
                executor=_FakeExecutor(),
            )
            result = runner.run(output_dir=root / "out")
            out_dir = Path(result["output_dir"])
            self.assertTrue((out_dir / "config.json").exists())
            self.assertTrue((out_dir / "raw_predictions.jsonl").exists())
            self.assertTrue((out_dir / "execution_results.json").exists())
            self.assertTrue((out_dir / "metrics.json").exists())
            self.assertTrue((out_dir / "metadata.json").exists())
            self.assertTrue((out_dir / "report.md").exists())
            metadata = (out_dir / "metadata.json").read_text(encoding="utf-8")
            self.assertIn("execution_results_json", metadata)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

