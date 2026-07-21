from __future__ import annotations

from collections import Counter
from dataclasses import asdict
from statistics import mean
from typing import Any, Sequence

from .schema import BenchmarkMetricsSchema, BenchmarkPrediction


def _token_total(predictions: Sequence[BenchmarkPrediction], field_name: str) -> int:
    total = 0
    for prediction in predictions:
        token_usage = prediction.token_usage if isinstance(prediction.token_usage, dict) else {}
        value = token_usage.get(field_name)
        if isinstance(value, (int, float)):
            total += int(value)
    return total


def summarize_prediction_records(predictions: Sequence[BenchmarkPrediction]) -> dict[str, Any]:
    total = len(predictions)
    successful = [prediction for prediction in predictions if prediction.error is None]
    scored = [prediction for prediction in predictions if prediction.score is not None]
    correct = [prediction for prediction in predictions if prediction.is_correct is True]

    variant_counts = Counter(prediction.variant for prediction in predictions)
    latency_values = [prediction.latency_seconds for prediction in predictions if prediction.latency_seconds is not None]
    score_values = [prediction.score for prediction in scored if prediction.score is not None]

    return {
        "prediction_count": total,
        "successful_prediction_count": len(successful),
        "failed_prediction_count": total - len(successful),
        "accuracy": len(correct) / float(total) if total else 0.0,
        "score_mean": mean(score_values) if score_values else 0.0,
        "latency_mean_seconds": mean(latency_values) if latency_values else 0.0,
        "latency_total_seconds": sum(latency_values) if latency_values else 0.0,
        "prompt_tokens_total": _token_total(predictions, "prompt_tokens"),
        "completion_tokens_total": _token_total(predictions, "completion_tokens"),
        "total_tokens_total": _token_total(predictions, "total_tokens"),
        "variant_counts": dict(variant_counts),
        "metric_schema": asdict(BenchmarkMetricsSchema()),
    }

