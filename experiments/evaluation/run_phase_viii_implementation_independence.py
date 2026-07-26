from __future__ import annotations

from pathlib import Path

from experiments.config import load_phase_viii_implementation_independence_config
from experiments.evaluation.phase_viii_implementation_independence.runner import (
    write_phase_viii_implementation_independence_outputs,
)


def main() -> None:
    config = load_phase_viii_implementation_independence_config()
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "experiments" / "results" / "phase_viii_implementation_independence"
    write_phase_viii_implementation_independence_outputs(output_dir, config=config)


if __name__ == "__main__":
    main()
