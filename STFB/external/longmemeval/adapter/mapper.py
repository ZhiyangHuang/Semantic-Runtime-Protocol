from __future__ import annotations

from typing import Any, Dict


def map_longmemeval_case(raw_case: Dict[str, Any], source_case_id: str) -> Dict[str, Any]:
    """Map a LongMemEval case into a frozen STFB-compatible transition instance."""
    question = raw_case.get("query", "")
    reference_answer = raw_case.get("reference_answer", raw_case.get("expected_answer", ""))
    prediction = raw_case.get("prediction", "")
    score = raw_case.get("score", raw_case.get("metadata", {}).get("evaluation", {}).get("score", 0.0))
    retrieved_units = raw_case.get("raw_response", {}).get("response", {}).get("retrieved_unit_ids", [])
    retrieved_relations = raw_case.get("raw_response", {}).get("response", {}).get("retrieved_relation_ids", [])
    allowed_mutation = bool(raw_case.get("authority", {}).get("allowed_mutation", False))

    return {
        "instance_io": f"lme_{source_case_id}",
        "failure_type": raw_case.get("failure_type", "external_transition"),
        "state_t": {
            "workspace_preference": reference_answer,
        },
        "observation": {
            "query": question,
        },
        "proposal": {
            "workspace_preference": prediction,
        },
        "evidence": {
            "retrieved_unit_ids": list(retrieved_units) or list(raw_case.get("focus_unit_ids", [])),
            "retrieved_relation_ids": list(retrieved_relations) or list(raw_case.get("focus_relation_ids", [])),
            "confidence": score,
        },
        "authority": {
            "source_benchmark": "LongMemEval",
            "source_case_id": source_case_id,
            "latest_authoritative_state": reference_answer,
            "allowed_mutation": allowed_mutation,
        },
        "expected_transition": {
            "should_commit": False,
            "failure_type": raw_case.get("failure_type", "temporal_regression"),
            "valid_state": {
                "workspace_preference": reference_answer,
            },
        },
        "metadata": {
            "source_benchmark": "LongMemEval",
            "source_case_id": source_case_id,
            "source_task": raw_case.get("metadata", {}).get("evaluation", {}).get("metric_name", "longmemeval"),
            "source_variant": raw_case.get("variant", ""),
            "source_score": score,
        },
    }
