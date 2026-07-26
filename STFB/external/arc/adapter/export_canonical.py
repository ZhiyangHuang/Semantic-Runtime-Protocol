from __future__ import annotations

import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from STFB.external.arc.adapter.mapper import map_arc_case


RAW_CASES = [
    {
        "output_id": "001",
        "case_id": "Mercury_7037258",
        "failure_type": "unsupported_mutation",
        "subset": "ARC-Easy",
        "question": "Which best describes the structure of an atom?",
        "choice_labels": ["A", "B", "C", "D"],
        "choices": {
            "A": "a lightweight core surrounded by neutral particles",
            "B": "a massive core surrounded by negatively-charged particles",
            "C": "a network of interacting positive and negative particles",
            "D": "overlapping layers of neutral, positive, and negative particles",
        },
        "reference_answer": "a massive core surrounded by negatively-charged particles",
        "prediction": "a network of interacting positive and negative particles",
        "score": 0.92,
        "variant": "unsupported_inference",
        "authority": {
            "allowed_mutation": False,
        },
        "expected_transition": {
            "should_commit": False,
        },
    },
    {
        "output_id": "002",
        "case_id": "Mercury_417466",
        "failure_type": "valid_transition",
        "subset": "ARC-Easy",
        "question": "Which statement best explains why photosynthesis is the foundation of most food webs?",
        "choice_labels": ["A", "B", "C", "D"],
        "choices": {
            "A": "Sunlight is the source of energy for nearly all ecosystems.",
            "B": "Most ecosystems are found on land instead of in water.",
            "C": "Carbon dioxide is more available than other gases.",
            "D": "The producers in all ecosystems are plants.",
        },
        "reference_answer": "Sunlight is the source of energy for nearly all ecosystems.",
        "prediction": "Sunlight is the source of energy for nearly all ecosystems.",
        "score": 0.97,
        "variant": "supported_reasoning",
        "authority": {
            "allowed_mutation": True,
        },
        "expected_transition": {
            "should_commit": True,
        },
    },
]


def main() -> int:
    output_dir = Path(__file__).resolve().parents[1] / "cases" / "canonical"
    output_dir.mkdir(parents=True, exist_ok=True)

    last_mapped = None
    for raw_case in RAW_CASES:
        mapped = map_arc_case(raw_case, raw_case["output_id"])
        output_path = output_dir / f"arc_{raw_case['output_id']}.json"
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(mapped, f, indent=2, sort_keys=True)
        last_mapped = mapped

    if last_mapped is not None:
        print(json.dumps(last_mapped, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

