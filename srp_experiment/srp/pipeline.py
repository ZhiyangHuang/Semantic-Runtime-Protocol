import os
from time import perf_counter
from typing import Dict, List

from .compress import compress_state
from .recover import recover_state
from .state import SemanticState
from .validate import validate_state
from .validation_targets import build_validation_targets


def _extract_vocab(text: str) -> List[str]:
    words = [word.strip(".,").lower() for word in text.split()]
    unique = []
    for word in words:
        if len(word) > 4 and word not in unique:
            unique.append(word)
    return unique[:12]


def _merge_vocab(existing: List[str], additions: List[str], limit: int = 12) -> List[str]:
    merged = list(existing)
    for item in additions:
        cleaned = str(item).strip().lower()
        if cleaned and cleaned not in merged:
            merged.append(cleaned)
    return merged[:limit]


def run_srp(
    task: Dict,
    cycles: int,
    client=None,
    max_cycle_drift: float = 0.35,
    min_keyword_score: float = 0.5,
) -> List[Dict]:
    constraint_state = list(task["initial_state"].get("constraints", []))
    anchor_memory = task["initial_state"]["memory"]
    effective_max_cycle_drift = float(os.getenv("SRP_MAX_CYCLE_DRIFT", str(max_cycle_drift)))
    effective_min_keyword_score = float(os.getenv("SRP_MIN_KEYWORD_SCORE", str(min_keyword_score)))
    state = SemanticState(
        memory=anchor_memory,
        constraints=constraint_state,
        global_vocabulary=_extract_vocab(anchor_memory),
        local_vocabulary=_extract_vocab(" ".join(constraint_state)),
        term_map={},
        loss_notes=[],
        policy={
            "compression_goal": "preserve task memory under bounded drift",
            "anti_leakage": "do not introduce query verbs or protocol terms unless they are already in memory",
            "recovery_goal": "recover the original task memory as directly as possible by aligning to a stable semantic anchor",
        },
    )
    records = []
    for cycle in range(1, cycles + 1):
        started_at = perf_counter()
        pre_cycle_memory = state.memory
        pre_cycle_constraints = list(state.constraints)
        pre_cycle_global_vocabulary = list(state.global_vocabulary)
        pre_cycle_local_vocabulary = list(state.local_vocabulary)
        pre_cycle_term_map = dict(state.term_map)
        pre_cycle_loss_notes = list(state.loss_notes)
        package = compress_state(state, client=client)
        recovered = recover_state(package, client=client, anchor_memory=anchor_memory)
        validation_targets = build_validation_targets(task)
        validation = validate_state(
            pre_cycle_memory,
            recovered.memory,
            validation_targets,
            max_drift=effective_max_cycle_drift,
            min_keyword_score=effective_min_keyword_score,
        )
        committed = validation["passed"]
        committed_memory = recovered.memory if committed else pre_cycle_memory
        committed_constraints = recovered.constraints if committed else pre_cycle_constraints
        committed_term_map = recovered.term_map if committed else pre_cycle_term_map
        committed_loss_notes = recovered.loss_notes if committed else pre_cycle_loss_notes
        committed_global_vocabulary = (
            _merge_vocab(pre_cycle_global_vocabulary, package.get("global_vocab", []) + _extract_vocab(pre_cycle_memory))
            if committed
            else pre_cycle_global_vocabulary
        )
        committed_local_vocabulary = (
            _merge_vocab(pre_cycle_local_vocabulary, pre_cycle_constraints + _extract_vocab(" ".join(pre_cycle_memory.split()[:12])), limit=12)
            if committed
            else pre_cycle_local_vocabulary
        )
        package_usage = package.get("usage") or {}
        recovered_usage = getattr(recovered, "usage", None) or {}
        usage = {
            "prompt_tokens": sum(value for value in [package_usage.get("prompt_tokens"), recovered_usage.get("prompt_tokens")] if value is not None) or None,
            "completion_tokens": sum(value for value in [package_usage.get("completion_tokens"), recovered_usage.get("completion_tokens")] if value is not None) or None,
            "total_tokens": sum(value for value in [package_usage.get("total_tokens"), recovered_usage.get("total_tokens")] if value is not None) or None,
        }
        records.append(
            {
                "cycle": cycle,
                "representation": package["memory"],
                "recovered_text": recovered.memory,
                "committed_memory": committed_memory,
                "tokens": len(package["memory"].split()) + len(package["global_vocab"]) + 8,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "latency_seconds": round(perf_counter() - started_at, 4),
                "validation_score": validation["score"],
                "validation_contract_satisfaction": validation["contract_satisfaction"],
                "validation_drift": validation["drift"],
                "validation_drift_risk": validation["drift_risk"],
                "validation_drift_blocks_commit": validation["drift_blocks_commit"],
                "validation_coverage": validation["coverage_score"],
                "validation_alignment": validation["alignment_score"],
                "validation_leakage_detected": validation["leakage_detected"],
                "max_cycle_drift": validation["max_drift"],
                "blocking_drift": validation["blocking_drift"],
                "min_keyword_score": validation["min_keyword_score"],
                "min_coverage_score": validation["min_coverage_score"],
                "validation_passed": validation["passed"],
                "state_committed": committed,
                "notes": "semantic runtime protocol" if committed else "semantic runtime protocol (rollback to pre-compression memory)",
            }
        )
        state = SemanticState(
            memory=committed_memory,
            constraints=committed_constraints,
            global_vocabulary=committed_global_vocabulary,
            local_vocabulary=committed_local_vocabulary,
            term_map=committed_term_map,
            loss_notes=committed_loss_notes,
            policy=state.policy,
        )
    return records
