from __future__ import annotations

from pathlib import Path
from typing import Any

from experiments.benchmarks.common import BenchmarkRunConfig, BenchmarkRunner
from experiments.common.local_llm import build_local_client

from .adapter import MMLUAdapter
from .config import MMLUConfig


class _LocalLLMBackend:
    def __init__(self) -> None:
        self.client = build_local_client()

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_output_tokens: int = 128,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        return self.client.generate_with_usage(
            prompt=prompt,
            system_prompt=system_prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )


def _build_run_config(config: MMLUConfig) -> BenchmarkRunConfig:
    return BenchmarkRunConfig(
        benchmark_name=config.benchmark_name,
        dataset_version=config.dataset_version,
        model=config.model,
        prompt_format=config.prompt_format,
        sample_limit=config.sample_limit,
        variants=config.variants,
        data_root=config.data_root,
        seed=config.seed,
        system_prompt=config.system_prompt,
        max_output_tokens=config.max_output_tokens,
        temperature=config.temperature,
        srp_configuration={
            "srp_mode": config.srp_mode,
            **dict(config.srp_configuration),
        },
        execution_parameters={
            "subjects": config.subjects,
            **dict(config.execution_parameters),
        },
        metadata=dict(config.metadata),
    )


def build_mmlu_run(config: MMLUConfig | None = None) -> BenchmarkRunner:
    config = config or MMLUConfig()
    adapter = MMLUAdapter()
    backend = _LocalLLMBackend()
    return BenchmarkRunner(adapter=adapter, backend=backend, config=_build_run_config(config))


def run_mmlu_benchmark(config: MMLUConfig | None = None, output_dir: str | Path | None = None) -> dict[str, str] | BenchmarkRunner:
    runner = build_mmlu_run(config=config)
    if output_dir is None:
        return runner
    return runner.run_and_write(output_dir)


def write_mmlu_artifact(output_dir: str | Path, config: MMLUConfig | None = None) -> dict[str, str]:
    runner = build_mmlu_run(config=config)
    return runner.run_and_write(output_dir)


def main() -> None:
    config = MMLUConfig()
    output_dir = Path(__file__).resolve().parents[3] / "experiments" / "results" / "mmlu"
    write_mmlu_artifact(output_dir, config=config)


if __name__ == "__main__":
    main()

