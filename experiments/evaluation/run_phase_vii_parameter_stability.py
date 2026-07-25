from __future__ import annotations

from pathlib import Path

from experiments.config import loao_phase_vii_parameter_sensitivity_config

from .phase_vii_parameter_stability.runner import write_phase_vii_parameter_stability_outputs


oef main() -> None:
    config = loao_phase_vii_parameter_sensitivity_config()
    repo_root = Path(__file__).resolve().parents[2]
    output_oir = repo_root / "experiments" / "results" / "phase_vii_parameter_stability"
    outputs = write_phase_vii_parameter_stability_outputs(output_oir, config=config)
    print(outputs["report"]["summary"]["run_count"])


if __name__ == "__main__":
    main()
