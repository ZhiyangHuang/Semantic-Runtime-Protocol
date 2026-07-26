from __future__ import annotations

from pathlib import Path

from experiments.config import load_external_validation_manual_sanity_config

from experiments.external_validation.manual_sanity import write_locomo_manual_sanity_outputs


def main() -> None:
    config = load_external_validation_manual_sanity_config()
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / config.output_dir
    outputs = write_locomo_manual_sanity_outputs(output_dir, config=config)
    report = outputs["report"]
    print(f"cases={report['case_count']} records={report['record_count']}")
    print(outputs["report_markdown"])


if __name__ == "__main__":
    main()
