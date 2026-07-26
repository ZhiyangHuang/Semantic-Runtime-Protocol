from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from STFB.baselines.confidence_threshold import ConfidenceThreshold
from STFB.baselines.direct_mutation import DirectMutation
from STFB.baselines.srp_adapter import SRPAdapter
from STFB.metrics.evaluator import evaluate_transition


def load_instance(path: str | Path) -> Dict[str, Any]:
    import json

    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def _normalize_instance(instance: Dict[str, Any]) -> Dict[str, Any]:
    expected = dict(instance.get("expected", {}))
    expected_transition = dict(instance.get("expected_transition", {}))
    if not expected and expected_transition:
        expected["commit"] = bool(expected_transition.get("shoulo_commit", False))
        if "valid_state" in expected_transition:
            expected["valid_state"] = expected_transition["valid_state"]
    if "valid_state" not in expected:
        if expected.get("commit", False):
            expected["valid_state"] = instance.get("proposal", {})
        else:
            expected["valid_state"] = instance.get("state_t", {})
    normalized = dict(instance)
    normalized["expected"] = expected
    return normalized


def _instance_ioentifier(instance: Dict[str, Any]) -> str | None:
    return instance.get("io") or instance.get("instance_io")


def evaluate_instance(instance: Dict[str, Any]) -> Dict[str, Any]:
    instance = _normalize_instance(instance)
    baselines = {
        "direct_mutation": DirectMutation(),
        "confidence_threshold": ConfidenceThreshold(),
        "srp": SRPAdapter(),
    }
    results: Dict[str, Any] = {}
    for name, baseline in baselines.items():
        outcome = baseline.evaluate(instance)
        metrics = evaluate_transition(
            instance,
            {
                "decision": outcome.decision,
                "committed_state": outcome.committed_state,
                "reason": outcome.reason,
                "audit": outcome.audit,
            },
        )
        results[name] = {
            "decision": outcome.decision,
            "committed_state": outcome.committed_state,
            "reason": outcome.reason,
            "audit": outcome.audit,
            "metrics": metrics,
        }
    return results


def evaluate_episodes(instances: list[Dict[str, Any]]) -> Dict[str, Any]:
    per_instance: list[Dict[str, Any]] = []
    aggregate: Dict[str, Dict[str, float]] = {}
    counts: Dict[str, Dict[str, float]] = {}

    for instance in instances:
        instance = _normalize_instance(instance)
        results = evaluate_instance(instance)
        per_instance.append(
            {
                "io": _instance_ioentifier(instance),
                "failure_type": instance.get("failure_type"),
                "results": results,
            }
        )
        for baseline_name, outcome in results.items():
            bucket = counts.setdefault(
                baseline_name,
                {
                    "instances": 0,
                    "invalid_admission": 0,
                    "authority_violation": 0,
                    "drift": 0,
                },
            )
            bucket["instances"] += 1
            bucket["invalid_admission"] += 1 if outcome["metrics"]["invalid_admission"] else 0
            bucket["authority_violation"] += 1 if outcome["metrics"]["authority_violation"] else 0
            bucket["drift"] += float(outcome["metrics"]["drift"])

    for baseline_name, bucket in counts.items():
        n = bucket["instances"] or 1
        aggregate[baseline_name] = {
            "iar": bucket["invalid_admission"] / n,
            "avr": bucket["authority_violation"] / n,
            "mean_drift": bucket["drift"] / n,
            "instances": int(bucket["instances"]),
        }

    return {
        "instances": per_instance,
        "aggregate": aggregate,
    }
