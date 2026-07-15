from __future__ import annotations

from pathlib import Path

from experiments.config import load_phase_vii_parameter_sensitivity_config

from .phase_vii_parameter_stability.runner import write_phase_vii_parameter_stability_outputs


def main() -> None:
    config = load_phase_vii_parameter_sensitivity_config()
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "experiments" / "results" / "phase_vii_parameter_stability"
    outputs = write_phase_vii_parameter_stability_outputs(output_dir, config=config)
    print(outputs["report"]["summary"]["run_count"])


if __name__ == "__main__":
    main()
