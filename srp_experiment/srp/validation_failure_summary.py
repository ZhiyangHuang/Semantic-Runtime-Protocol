import re
from typing import Dict, List

LEAKAGE_PATTERNS = [
    r"\bthe answer is\b",
    r"\bfinal answer\b",
    r"\bthe solution is\b",
    r"\btask completed\b",
    r"\btherefore the answer\b",
    r"\bwe should answer\b",
]

STRONG_ALIGNMENT_SCORE = 0.8
DEFAULT_BLOCKING_DRIFT = 0.9


def detect_answer_leakage(text: str) -> Dict[str, object]:
    lowered = text.lower()
    matches: List[str] = []
    for pattern in LEAKAGE_PATTERNS:
        if re.search(pattern, lowered):
            matches.append(pattern)
    return {
        "detected": bool(matches),
        "matches": matches,
    }


def assess_drift_risk(
    drift: float,
    soft_drift_budget: float,
    alignment_score: float,
) -> Dict[str, object]:
    blocking_drift = max(DEFAULT_BLOCKING_DRIFT, soft_drift_budget * 2.0)
    if drift <= soft_drift_budget:
        return {
            "risk": "low",
            "blocks_commit": False,
            "soft_drift_budget": soft_drift_budget,
            "blocking_drift": blocking_drift,
        }
    if drift <= blocking_drift and alignment_score >= STRONG_ALIGNMENT_SCORE:
        return {
            "risk": "medium",
            "blocks_commit": False,
            "soft_drift_budget": soft_drift_budget,
            "blocking_drift": blocking_drift,
        }
    return {
        "risk": "high",
        "blocks_commit": True,
        "soft_drift_budget": soft_drift_budget,
        "blocking_drift": blocking_drift,
    }


def build_failure_summary(
    critical_failures: List[Dict[str, object]],
    leakage: Dict[str, object],
    drift_risk: Dict[str, object],
) -> Dict[str, object]:
    failure_object_ids = [
        str(item.get("source_object_id")) for item in critical_failures if item.get("source_object_id")
    ]
    failure_types = {}
    for item in critical_failures:
        object_type = str(item.get("object_type", "unknown"))
        failure_types[object_type] = failure_types.get(object_type, 0) + 1
    return {
        "schema_version": "failure_summary.v1",
        "critical_failure_count": len(critical_failures),
        "critical_failure_object_ids": failure_object_ids[:10],
        "critical_failure_types": failure_types,
        "leakage_detected": leakage["detected"],
        "leakage_matches": list(leakage.get("matches", [])),
        "drift_risk": drift_risk["risk"],
        "blocks_commit": drift_risk["blocks_commit"],
        "has_critical_failure": bool(critical_failures),
    }


def build_failure_summary_flat(failure_summary: Dict[str, object]) -> Dict[str, object]:
    failure_object_ids = list(failure_summary.get("critical_failure_object_ids", []))
    failure_types = dict(failure_summary.get("critical_failure_types", {}))
    failure_type_labels = [f"{key}:{value}" for key, value in sorted(failure_types.items())]
    return {
        "schema_version": "failure_summary_flat.v1",
        "critical_failure_count": failure_summary.get("critical_failure_count"),
        "critical_failure_object_ids": failure_object_ids,
        "critical_failure_object_id_joined": "|".join(str(item) for item in failure_object_ids if str(item)),
        "critical_failure_types": failure_types,
        "critical_failure_type_count": len(failure_types),
        "critical_failure_type_labels": failure_type_labels,
        "leakage_detected": failure_summary.get("leakage_detected"),
        "leakage_match_count": len(failure_summary.get("leakage_matches", [])),
        "leakage_matches": failure_summary.get("leakage_matches", []),
        "leakage_matches_joined": "|".join(
            str(item) for item in failure_summary.get("leakage_matches", []) if str(item)
        ),
        "drift_risk": failure_summary.get("drift_risk"),
        "blocks_commit": failure_summary.get("blocks_commit"),
        "has_critical_failure": failure_summary.get("has_critical_failure"),
    }
