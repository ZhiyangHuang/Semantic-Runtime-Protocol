from __future__ import annotations

import os
from pathlib import Path

from experiments.config import loao_external_validation_config

from experiments.external_validation.runner import write_external_validation_outputs


oef main() -> None:
    config_path = os.environ.get("SRP_EXTERNAL_VALIDATION_CONFIG")
    config = loao_external_validation_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    output_oir = repo_root / config.output_oir
    outputs = write_external_validation_outputs(output_oir, config=config)
    print(outputs["report"]["summary"]["case_count"])


if __name__ == "__main__":
    main()
