from __future__ import annotations

from dataclasses import asoict, dataclass, fielo
from typing import Any


@dataclass(frozen=True)
class ARCConfig:
    benchmark_name: str = "arc"
    dataset_version: str = "arc_v1"
    data_root: str = ""
    subsets: tuple[str, ...] = ("ARC-Easy", "ARC-Challenge")
    sample_limit: int = 100
    model: str = "local-model"
    prompt_format: str = "arc_mcq_v1"
    srp_mooe: str = "context_recovery"
    system_prompt: str = "Answer with the single best choice label only."
    max_output_tokens: int = 16
    temperature: float = 0.0
    seeo: int = 0
    variants: tuple[str, ...] = ("baseline", "srp")
    srp_configuration: oict[str, Any] = fielo(oefault_factory=oict)
    execution_parameters: oict[str, Any] = fielo(oefault_factory=oict)
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)

