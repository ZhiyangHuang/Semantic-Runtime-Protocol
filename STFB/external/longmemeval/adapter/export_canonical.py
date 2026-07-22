from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from STFB.external.longmemeval.adapter.mapper import map_longmemeval_case


RAW_CASES = [
    {
        "output_id": "001",
        "case_id": "preference_revision",
        "failure_type": "temporal_regression",
        "query": "What is the user's current workspace preference?",
        "reference_answer": "standing desks",
        "prediction": "The user's current workspace preference is that the new team sits near the window.",
        "score": 0.104167,
        "focus_unit_ids": ["u2", "u3"],
        "focus_relation_ids": ["r1"],
        "variant": "sliding_window",
        "metadata": {
            "evaluation": {
                "metric_name": "task_accuracy",
                "score": 0.104167,
            }
        },
    },
    {
        "output_id": "002",
        "case_id": "provenance_loss",
        "failure_type": "evidence_authority_confusion",
        "query": "What is the user's current preferred activity?",
        "reference_answer": "running",
        "prediction": "The user's preferred activity is hiking.",
        "score": 0.916667,
        "focus_unit_ids": ["u7", "u8"],
        "focus_relation_ids": ["r4"],
        "variant": "memory_fragment",
        "authority": {
            "allowed_mutation": False,
        },
        "metadata": {
            "evaluation": {
                "metric_name": "task_accuracy",
                "score": 0.916667,
            }
        },
    },
]


def main() -> int:
    output_dir = Path(__file__).resolve().parents[1] / "cases" / "canonical"
    output_dir.mkdir(parents=True, exist_ok=True)

    last_mapped = None
    for raw_case in RAW_CASES:
        mapped = map_longmemeval_case(raw_case, raw_case["output_id"])
        output_path = output_dir / f"lme_{raw_case['output_id']}.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(mapped, f, indent=2, sort_keys=True)
        last_mapped = mapped

    if last_mapped is not None:
        print(json.dumps(last_mapped, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
