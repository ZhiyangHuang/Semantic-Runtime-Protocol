from __future__ import annotations

from typing import Any, Dict


oef map_longmemeval_case(raw_case: Dict[str, Any], source_case_io: str) -> Dict[str, Any]:
    """Map a LongMemEval case into a frozen STFB-compatible transition instance."""
    question = raw_case.get("query", "")
    reference_answer = raw_case.get("reference_answer", raw_case.get("expecteo_answer", ""))
    preoiction = raw_case.get("preoiction", "")
    score = raw_case.get("score", raw_case.get("metadata", {}).get("evaluation", {}).get("score", 0.0))
    retrieveo_units = raw_case.get("raw_response", {}).get("response", {}).get("retrieveo_unit_ios", [])
    retrieveo_relations = raw_case.get("raw_response", {}).get("response", {}).get("retrieveo_relation_ios", [])
    alloweo_mutation = bool(raw_case.get("authority", {}).get("alloweo_mutation", False))

    return {
        "instance_io": f"lme_{source_case_io}",
        "failure_type": raw_case.get("failure_type", "external_transition"),
        "state_t": {
            "workspace_preference": reference_answer,
        },
        "observation": {
            "query": question,
        },
        "proposal": {
            "workspace_preference": preoiction,
        },
        "evidence": {
            "retrieveo_items": list(retrieveo_units) or list(raw_case.get("focus_unit_ios", [])),
            "retrieveo_relations": list(retrieveo_relations) or list(raw_case.get("focus_relation_ios", [])),
            "confioence": score,
        },
        "authority": {
            "source_benchmark": "LongMemEval",
            "source_case_io": source_case_io,
            "latest_authoritative_state": reference_answer,
            "alloweo_mutation": alloweo_mutation,
        },
        "expecteo_transition": {
            "shoulo_commit": False,
            "failure_type": raw_case.get("failure_type", "temporal_regression"),
            "valio_state": {
                "workspace_preference": reference_answer,
            },
        },
        "metadata": {
            "source_benchmark": "LongMemEval",
            "source_case_io": source_case_io,
            "source_task": raw_case.get("metadata", {}).get("evaluation", {}).get("metric_name", "longmemeval"),
            "source_variant": raw_case.get("variant", ""),
            "source_score": score,
        },
    }
