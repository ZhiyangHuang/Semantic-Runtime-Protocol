from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from experiments.config import ExternalValidationLongMemEvalEvidenceConfig
from experiments.config import load_external_validation_longmemeval_evidence_config
from experiments.config import read_env_file


DEFAULT_BRIDGE_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "external_validation_longmemeval_evidence.env"


@dataclass(frozen=True)
class LongMemEvalBridgeConfig:
    bridge_name: str = "longmemeval"
    bridge_version: str = "bridge_migration_v1"
    bridge_output_dir: str = "experiments/results/longmemeval_full_v1"
    external_validation: ExternalValidationLongMemEvalEvidenceConfig | None = None
    source_path: str = ""

    @property
    def benchmark_name(self) -> str:
        external = self.external_validation or load_external_validation_longmemeval_evidence_config()
        return external.benchmark_name

    @property
    def output_dir(self) -> str:
        return self.bridge_output_dir

    @property
    def data_root(self) -> str:
        external = self.external_validation or load_external_validation_longmemeval_evidence_config()
        return external.data_root

    def as_dict(self) -> dict[str, Any]:
        external = self.external_validation or load_external_validation_longmemeval_evidence_config()
        return {
            "bridge_name": self.bridge_name,
            "bridge_version": self.bridge_version,
            "bridge_output_dir": self.bridge_output_dir,
            "external_validation": external.as_dict(),
            "source_path": self.source_path,
        }

    def external_config(self) -> ExternalValidationLongMemEvalEvidenceConfig:
        return self.external_validation or load_external_validation_longmemeval_evidence_config()


def load_longmemeval_bridge_config(path: str | Path | None = None) -> LongMemEvalBridgeConfig:
    config_path = Path(path) if path is not None else DEFAULT_BRIDGE_CONFIG_PATH
    external_config = load_external_validation_longmemeval_evidence_config(config_path)
    values = read_env_file(config_path)
    bridge_output_dir = values.get("BRIDGE_OUTPUT_DIR", "") or "experiments/results/longmemeval_full_v1"
    bridge_version = values.get("BRIDGE_VERSION", "") or "bridge_migration_v1"
    return LongMemEvalBridgeConfig(
        bridge_name=external_config.benchmark_name,
        bridge_version=bridge_version,
        bridge_output_dir=bridge_output_dir,
        external_validation=external_config,
        source_path=str(config_path),
    )

