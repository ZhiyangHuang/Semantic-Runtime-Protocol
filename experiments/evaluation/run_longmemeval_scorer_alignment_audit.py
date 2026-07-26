from __future__ import annotations

import os
from pathlib import Path

from experiments.external_validation.scorer_alignment_audit import write_scorer_alignment_closure_outputs


def main() -> None:
    source_dir = os.environ.get(
        "SRP_LONGMEMEVAL_EVIDENCE_SOURCE_DIR",
        str(Path("experiments/results/external_validation_longmemeval_evidence_strong_baselines")),
    )
    outputs = write_scorer_alignment_closure_outputs(source_dir)
    print(outputs["closure"]["overall_scorer_alignment_status"])


if __name__ == "__main__":
    main()
