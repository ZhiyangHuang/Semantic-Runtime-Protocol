from __future__ import annotations

from math import sqrt
from statistics import mean, pstdev
from typing import Iterable


def summarize_values(values: Iterable[float]) -> dict[str, float]:
    items = [float(value) for value in values]
    if not items:
        return {"mean": 0.0, "std": 0.0, "ci95": 0.0, "count": 0.0}
    avg = mean(items)
    std = pstdev(items) if len(items) > 1 else 0.0
    ci95 = 1.96 * (std / sqrt(len(items))) if len(items) > 1 else 0.0
    return {
        "mean": round(avg, 6),
        "std": round(std, 6),
        "ci95": round(ci95, 6),
        "count": float(len(items)),
    }


def summarize_metric(records: Iterable[dict[str, float]], field: str) -> dict[str, float]:
    return summarize_values(record[field] for record in records if field in record)


def summarize_metric_collection(records: Iterable[dict[str, float]], fields: Iterable[str]) -> dict[str, dict[str, float]]:
    return {field: summarize_metric(records, field) for field in fields}
