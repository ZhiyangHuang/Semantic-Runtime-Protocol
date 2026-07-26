from __future__ import annotations

import os
from pathlib import Path

from experiments.config import load_external_validation_longmemeval_evidence_config
from experiments.external_validation.evidence import write_longmemeval_evidence_outputs


def main() -> None:
    config_path = os.environ.get(
        "SRP_LONGMEMEVAL_EVIDENCE_CONFIG",
        str(Path(__file__).resolve().parents[2] / "configs" / "external_validation_longmemeval_evidence_strong_baselines.env"),
    )
    config = load_external_validation_longmemeval_evidence_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / config.output_dir
    outputs = write_longmemeval_evidence_outputs(output_dir, config=config)
    print(outputs["report"]["summary"]["case_count"])


if __name__ == "__main__":
    main()
