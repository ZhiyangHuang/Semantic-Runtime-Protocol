from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Sequence

from .semantic_delta import SemanticDelta


def build_stagewise_loss_matrix(deltas: Sequence[SemanticDelta]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for delta in deltas:
        row = delta.as_dict()
        row["stage_transition"] = f"{delta.from_stage}->{delta.to_stage}"
        row["total_loss"] = (
            row["object_loss_count"]
            + row["relation_loss_count"]
            + row["constraint_loss_count"]
            + row["frame_loss_count"]
            + row["provenance_loss_count"]
            + row["lifecycle_loss_count"]
        )
        grouped[row["stage_transition"]].append(row)

    rows: List[Dict[str, Any]] = []
    for stage_transition, grouped_rows in grouped.items():
        aggregate: Dict[str, Any] = {"stage_transition": stage_transition, "occurrences": len(grouped_rows)}
        numeric_fields = [
            "object_loss_count",
            "relation_loss_count",
            "constraint_loss_count",
            "frame_loss_count",
            "provenance_loss_count",
            "lifecycle_loss_count",
            "total_loss",
        ]
        for field in numeric_fields:
            values = [float(row.get(field) or 0.0) for row in grouped_rows]
            aggregate[f"{field}_mean"] = sum(values) / len(values) if values else 0.0
            aggregate[f"{field}_sum"] = sum(values)
        rows.append(aggregate)
    rows.sort(key=lambda item: item["stage_transition"])
    return rows
