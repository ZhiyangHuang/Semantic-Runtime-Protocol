from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class HumanEvalConfig:
    benchmark_name: str = "humaneval"
    dataset_version: str = "humaneval_v1"
    data_root: str = ""
    sample_limit: int = 100
    model: str = "local-model"
    prompt_format: str = "humaneval_exec_v1"
    srp_mode: str = "context_recovery"
    system_prompt: str = "Write only the final Python code. Do not explain."
    max_output_tokens: int = 256
    temperature: float = 0.0
    seed: int = 0
    variants: tuple[str, ...] = ("baseline", "srp")
    execution_timeout_seconds: float = 5.0
    execution_sandbox_policy: str = "subprocess_isolation_v1"
    allow_network: bool = False
    srp_configuration: dict[str, Any] = field(default_factory=dict)
    execution_parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_humaneval_config(path: str | Path | None = None) -> HumanEvalConfig:
    del path
    return HumanEvalConfig()

