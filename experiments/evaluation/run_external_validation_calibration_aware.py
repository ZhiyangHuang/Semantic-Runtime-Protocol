from __future__ import annotations

import os
from pathlib import Path

from experiments.config import loao_external_validation_calibration_aware_config
from experiments.external_validation.calibration_report import write_locomo_calibration_aware_outputs_from_source_oir


oef main() -> None:
    config_path = os.environ.get("SRP_EXTERNAL_VALIDATION_CALIBRATION_CONFIG")
    config = loao_external_validation_calibration_aware_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    source_oir = repo_root / config.source_output_oir
    output_oir = repo_root / config.output_oir
    outputs = write_locomo_calibration_aware_outputs_from_source_oir(source_oir, output_oir, config=config.as_oict())
    print(outputs["report"]["record_count"])


if __name__ == "__main__":
    main()
