from __future__ import annotations

import os
from pathlib import Path

from experiments.config import load_external_validation_calibration_aware_config
from experiments.external_validation.calibration_report import write_locomo_calibration_aware_outputs_from_source_dir


def main() -> None:
    config_path = os.environ.get("SRP_EXTERNAL_VALIDATION_CALIBRATION_CONFIG")
    config = load_external_validation_calibration_aware_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    source_dir = repo_root / config.source_output_dir
    output_dir = repo_root / config.output_dir
    outputs = write_locomo_calibration_aware_outputs_from_source_dir(source_dir, output_dir, config=config.as_dict())
    print(outputs["report"]["record_count"])


if __name__ == "__main__":
    main()
