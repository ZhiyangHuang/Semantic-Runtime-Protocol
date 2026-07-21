from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class MMLUConfig:
    benchmark_name: str = "mmlu"
    dataset_version: str = "mmlu_v1"
    data_root: str = ""
    subjects: tuple[str, ...] = ()
    sample_limit: int = 100
    model: str = "local-model"
    prompt_format: str = "mmlu_mcq_v1"
    srp_mode: str = "context_recovery"
    system_prompt: str = "Answer with the single best choice label only."
    max_output_tokens: int = 16
    temperature: float = 0.0
    seed: int = 0
    variants: tuple[str, ...] = ("baseline", "srp")
    srp_configuration: dict[str, Any] = field(default_factory=dict)
    execution_parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

