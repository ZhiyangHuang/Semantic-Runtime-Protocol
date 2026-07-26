from __future__ import annotations

import os
from pathlib import Path

from experiments.config import (
    ExternalValidationConfig,
    load_external_validation_longmemeval_adapter_validation_config,
)
from experiments.external_validation import (
    write_calibration_aware_outputs_from_source_dir,
    write_external_validation_outputs,
)


def main() -> None:
    config_path = os.environ.get("SRP_LONGMEMEVAL_ADAPTER_VALIDATION_CONFIG")
    config = load_external_validation_longmemeval_adapter_validation_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    source_output_dir = repo_root / config.source_output_dir
    output_dir = repo_root / config.output_dir

    source_config = ExternalValidationConfig(
        phase="external_validation",
        benchmark_names=(config.benchmark_name,),
        baseline_names=config.baseline_names,
        seeds=config.seeds,
        benchmark_sample_limit=config.benchmark_sample_limit,
        data_root=config.data_root,
        output_dir=config.source_output_dir,
        source_path=config.source_path,
    )
    write_external_validation_outputs(source_output_dir, config=source_config, write_root_report=False)
    outputs = write_calibration_aware_outputs_from_source_dir(
        source_output_dir,
        output_dir,
        benchmark_display_name="LongMemEval",
        config=config.as_dict(),
    )
    print(outputs["report"]["record_count"])


if __name__ == "__main__":
    main()
