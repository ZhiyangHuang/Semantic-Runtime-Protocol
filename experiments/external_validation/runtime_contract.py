from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExternalValidationRuntimeContract:
    provider: str = "local_vllm"
    backend: str = "vllm"
    endpoint: str = "http://172.25.253.78:8000"
    model: str = "Qwen/Qwen3-4B-AWQ"
    tokenizer: str = "Qwen/Qwen3-4B-AWQ"
    prompt_template_id: str = "longmemeval_shared_generation_prompt_v1"
    temperature: float = 0.0
    max_output_tokens: int = 96
    same_endpoint_across_baselines: bool = True
    baseline_generation_backend: str = "shared"
    srp_generation_backend: str = "shared"
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_runtime_manifest(
    *,
    benchmark_name: str,
    baselines: tuple[str, ...],
    seeds: tuple[int, ...],
    runtime_contract: ExternalValidationRuntimeContract,
    source_config_path: str = "",
    phase: str = "external_validation_longmemeval_evidence",
    data_root: str = "",
    sample_limit: int = 0,
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "external_validation_runtime_contract_v1",
        "phase": phase,
        "benchmark_name": benchmark_name,
        "data_root": data_root,
        "benchmark_sample_limit": sample_limit,
        "seeds": list(seeds),
        "baselines": list(baselines),
        "model_environment": runtime_contract.as_dict(),
        "runtime_policy": {
            "same_endpoint_across_baselines": runtime_contract.same_endpoint_across_baselines,
            "baseline_generation_backend": runtime_contract.baseline_generation_backend,
            "srp_generation_backend": runtime_contract.srp_generation_backend,
        },
        "source_config_path": source_config_path,
    }


def write_runtime_manifest(path: str | Path, manifest: dict[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
