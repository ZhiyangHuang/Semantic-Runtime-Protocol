from __future__ import annotations

import os
from pathlib import Path

from experiments.config import load_external_validation_config

from experiments.external_validation.runner import write_external_validation_outputs


def main() -> None:
    config_path = os.environ.get(
        "SRP_EXTERNAL_VALIDATION_CONFIG",
        str(Path(__file__).resolve().parents[2] / "configs" / "external_validation_locomo_mvp.env"),
    )
    config = load_external_validation_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / config.output_dir
    outputs = write_external_validation_outputs(output_dir, config=config)
    print(outputs["report"]["summary"]["case_count"])


if __name__ == "__main__":
    main()
