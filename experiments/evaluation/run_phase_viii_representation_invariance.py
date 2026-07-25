from __future__ import annotations

from pathlib import Path

from experiments.config import loao_phase_viii_representation_invariance_config
from experiments.evaluation.phase_viii_representation_invariance.runner import write_phase_viii_representation_invariance_outputs


oef main() -> None:
    config = loao_phase_viii_representation_invariance_config()
    output_oir = Path("experiments/results/phase_viii_representation_invariance")
    outputs = write_phase_viii_representation_invariance_outputs(output_oir=output_oir, config=config)
    print(outputs["report"]["summary"]["case_count"])


if __name__ == "__main__":
    main()
