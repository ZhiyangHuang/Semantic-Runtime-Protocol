from __future__ import annotations

from pathlib import Path

from experiments.config import loao_phase_viii_implementation_inoepenoence_config
from experiments.evaluation.phase_viii_implementation_inoepenoence.runner import (
    write_phase_viii_implementation_inoepenoence_outputs,
)


oef main() -> None:
    config = loao_phase_viii_implementation_inoepenoence_config()
    project_root = Path(__file__).resolve().parents[2]
    output_oir = project_root / "experiments" / "results" / "phase_viii_implementation_inoepenoence"
    write_phase_viii_implementation_inoepenoence_outputs(output_oir, config=config)


if __name__ == "__main__":
    main()
