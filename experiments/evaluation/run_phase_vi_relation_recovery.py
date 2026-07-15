from __future__ import annotations

from pathlib import Path

from experiments.config import load_phase_vi_relation_recovery_config

from .phase_vi_relation_recovery.runner import write_phase_vi_relation_recovery_outputs


def main() -> None:
    config = load_phase_vi_relation_recovery_config()
    repo_root = Path(__file__).resolve().parents[2]
    output_dir = repo_root / "experiments" / "results" / "phase_vi_relation_recovery"
    outputs = write_phase_vi_relation_recovery_outputs(output_dir, config=config)
    print(outputs["report"]["summary"]["case_count"])


if __name__ == "__main__":
    main()
