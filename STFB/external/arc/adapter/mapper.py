from __future__ import annotations

from typing import Any, Dict


def map_arc_case(raw_case: Dict[str, Any], source_case_id: str) -> Dict[str, Any]:
    """Map an ARC case into a frozen STFB-compatible transition instance."""
    question = raw_case.get("question", "")
    reference_answer = raw_case.get("reference_answer", raw_case.get("expected_answer", ""))
    prediction = raw_case.get("prediction", "")
    score = float(raw_case.get("score", raw_case.get("metadata", {}).get("evaluation", {}).get("score", 0.0)))
    choices = raw_case.get("choices", {})
    choice_labels = raw_case.get("choice_labels", ["A", "B", "C", "D"])
    allowed_mutation = bool(raw_case.get("authority", {}).get("allowed_mutation", False))

    valid_state = {
        "knowledge_state": reference_answer,
    }
    expected_commit = bool(raw_case.get("expected_transition", {}).get("should_commit", False))
    if expected_commit:
        valid_state = {
            "knowledge_state": prediction,
        }

    return {
        "instance_id": f"arc_{source_case_id}",
        "failure_type": raw_case.get("failure_type", "unsupported_mutation"),
        "state_t": {
            "knowledge_state": reference_answer,
        },
        "observation": {
            "question": question,
            "choice_labels": list(choice_labels),
            "choices": dict(choices),
        },
        "proposal": {
            "knowledge_state": prediction,
        },
        "evidence": {
            "choice_labels": list(choice_labels),
            "choices": dict(choices),
            "confidence": score,
        },
        "authority": {
            "source_benchmark": "ARC",
            "source_case_id": source_case_id,
            "allowed_mutation": allowed_mutation,
            "reference_answer": reference_answer,
        },
        "expected_transition": {
            "should_commit": expected_commit,
            "failure_type": raw_case.get("failure_type", "unsupported_mutation"),
            "valid_state": valid_state,
        },
        "metadata": {
            "source_benchmark": "ARC",
            "source_case_id": source_case_id,
            "source_task": raw_case.get("subset", "ARC-Easy"),
            "source_variant": raw_case.get("variant", ""),
            "source_score": score,
        },
    }

