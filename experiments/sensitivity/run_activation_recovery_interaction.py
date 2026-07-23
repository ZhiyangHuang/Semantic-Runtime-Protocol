from __future__ import annotations

from experiments.sensitivity.interaction.runner import run_activation_recovery_interaction


def main() -> None:
    outputs = run_activation_recovery_interaction()
    print(len(outputs["matrix"]))


if __name__ == "__main__":
    main()
