from __future__ import annotations

from collections import defaultdict
from typing import Any

from .schema import ExternalValidationRecord


def summarize_failures(records: list[ExternalValidationRecord]) -> dict[str, Any]:
    counts: dict[str, int] = defaultdict(int)
    examples: dict[str, list[str]] = defaultdict(list)

    for record in records:
        if not record.failure_categories:
            counts["none"] += 1
            continue
        for category in record.failure_categories:
            counts[category] += 1
            if len(examples[category]) < 3:
                examples[category].append(
                    f"{record.run.benchmark_name}:{record.run.baseline_name}:{record.run.case.case_id}"
                )

    return {
        "counts": dict(sorted(counts.items())),
        "examples": {key: value for key, value in sorted(examples.items())},
    }
