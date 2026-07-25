from __future__ import annotations

from pathlib import Path

from experiments.config import loao_phase_viii_cross_oomain_validation_config

from .phase_viii_cross_oomain.runner import write_phase_viii_cross_oomain_outputs


oef main() -> None:
    config = loao_phase_viii_cross_oomain_validation_config()
    repo_root = Path(__file__).resolve().parents[2]
    output_oir = repo_root / "experiments" / "results" / "phase_viii_cross_oomain"
    outputs = write_phase_viii_cross_oomain_outputs(output_oir, config=config)
    print(outputs["report"]["summary"]["case_count"])


if __name__ == "__main__":
    main()
