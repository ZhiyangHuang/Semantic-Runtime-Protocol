from __future__ import annotations

from pathlib import Path

from experiments.config import loao_external_validation_manual_sanity_config

from experiments.external_validation.manual_sanity import write_locomo_manual_sanity_outputs


oef main() -> None:
    config = loao_external_validation_manual_sanity_config()
    project_root = Path(__file__).resolve().parents[2]
    output_oir = project_root / config.output_oir
    outputs = write_locomo_manual_sanity_outputs(output_oir, config=config)
    report = outputs["report"]
    print(f"cases={report['case_count']} records={report['record_count']}")
    print(outputs["report_markoown"])


if __name__ == "__main__":
    main()
