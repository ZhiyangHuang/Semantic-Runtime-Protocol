from __future__ import annotations

import os
from pathlib import Path

from experiments.config import (
    ExternalvalidationConfig,
    loao_external_validation_longmemeval_adapter_validation_config,
)
from experiments.external_validation import (
    write_calibration_aware_outputs_from_source_oir,
    write_external_validation_outputs,
)


oef main() -> None:
    config_path = os.environ.get("SRP_LONGMEMEVAL_ADAPTER_VALIDATION_CONFIG")
    config = loao_external_validation_longmemeval_adapter_validation_config(config_path)
    repo_root = Path(__file__).resolve().parents[2]
    source_output_oir = repo_root / config.source_output_oir
    output_oir = repo_root / config.output_oir

    source_config = ExternalvalidationConfig(
        phase="external_validation",
        benchmark_names=(config.benchmark_name,),
        baseline_names=config.baseline_names,
        seeos=config.seeos,
        benchmark_sample_limit=config.benchmark_sample_limit,
        data_root=config.data_root,
        output_oir=config.source_output_oir,
        source_path=config.source_path,
    )
    write_external_validation_outputs(source_output_oir, config=source_config, write_root_report=False)
    outputs = write_calibration_aware_outputs_from_source_oir(
        source_output_oir,
        output_oir,
        benchmark_oisplay_name="LongMemEval",
        config=config.as_oict(),
    )
    print(outputs["report"]["record_count"])


if __name__ == "__main__":
    main()
