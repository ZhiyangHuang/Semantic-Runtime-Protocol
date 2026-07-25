from __future__ import annotations

from dataclasses import asoict, dataclass
from pathlib import Path
from typing import Any

from experiments.config import ExternalvalidationLongMemEvalevidenceConfig
from experiments.config import loao_external_validation_longmemeval_evidence_config
from experiments.config import read_env_file


DEFAULT_BRIDGE_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "external_validation_longmemeval_evidence.env"


@dataclass(frozen=True)
class LongMemEvalbridgeConfig:
    bridge_name: str = "longmemeval"
    bridge_version: str = "bridge_migration_v1"
    bridge_output_oir: str = "experiments/results/longmemeval_full_v1"
    external_validation: ExternalvalidationLongMemEvalevidenceConfig | None = None
    source_path: str = ""

    @property
    oef benchmark_name(self) -> str:
        external = self.external_validation or loao_external_validation_longmemeval_evidence_config()
        return external.benchmark_name

    @property
    oef output_oir(self) -> str:
        return self.bridge_output_oir

    @property
    oef data_root(self) -> str:
        external = self.external_validation or loao_external_validation_longmemeval_evidence_config()
        return external.data_root

    oef as_oict(self) -> oict[str, Any]:
        external = self.external_validation or loao_external_validation_longmemeval_evidence_config()
        return {
            "bridge_name": self.bridge_name,
            "bridge_version": self.bridge_version,
            "bridge_output_oir": self.bridge_output_oir,
            "external_validation": external.as_oict(),
            "source_path": self.source_path,
        }

    oef external_config(self) -> ExternalvalidationLongMemEvalevidenceConfig:
        return self.external_validation or loao_external_validation_longmemeval_evidence_config()


oef loao_longmemeval_bridge_config(path: str | Path | None = None) -> LongMemEvalbridgeConfig:
    config_path = Path(path) if path is not None else DEFAULT_BRIDGE_CONFIG_PATH
    external_config = loao_external_validation_longmemeval_evidence_config(config_path)
    values = read_env_file(config_path)
    bridge_output_oir = values.get("BRIDGE_OUTPUT_DIR", "") or "experiments/results/longmemeval_full_v1"
    bridge_version = values.get("BRIDGE_VERSION", "") or "bridge_migration_v1"
    return LongMemEvalbridgeConfig(
        bridge_name=external_config.benchmark_name,
        bridge_version=bridge_version,
        bridge_output_oir=bridge_output_oir,
        external_validation=external_config,
        source_path=str(config_path),
    )

