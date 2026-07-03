import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from env_utils import load_env_file
from model_backend import BackendConfig, ModelClient
from run_experiment import load_tasks
from srp.compress import compress_state
from srp.pipeline import _extract_vocab
from srp.recover import recover_state
from srp.state import SemanticState
from srp.validate import validate_state
from srp.validation_targets import build_validation_targets


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"

load_env_file()

CONTRACT_TOLERANCE = 0.05
ALIGNMENT_TOLERANCE = 0.02
DRIFT_TOLERANCE = 0.05


def _build_initial_state(task: Dict) -> SemanticState:
    memory = task["initial_state"]["memory"]
    constraints = list(task["initial_state"].get("constraints", []))
    return SemanticState(
        memory=memory,
        constraints=constraints,
        global_vocabulary=_extract_vocab(memory),
        local_vocabulary=_extract_vocab(" ".join(constraints)),
        term_map={},
        loss_notes=[],
        policy={
            "compression_goal": "preserve task memory under bounded drift",
            "anti_leakage": "do not introduce query verbs or protocol terms unless they are already in memory",
            "recovery_goal": "recover the original task memory as directly as possible by aligning to a stable semantic anchor",
        },
    )


def _run_path(task: Dict, client: ModelClient | None, label: str) -> Dict[str, Any]:
    state = _build_initial_state(task)
    anchor_memory = task["initial_state"]["memory"]
    validation_targets = build_validation_targets(task)

    compressed = compress_state(state, client=client)
    recovered = recover_state(compressed, client=client, anchor_memory=anchor_memory)
    validation = validate_state(
        state.memory,
        recovered.memory,
        validation_targets,
    )

    return {
        "label": label,
        "compressed_state": {
            "memory": compressed.get("memory"),
            "constraints": compressed.get("constraints"),
            "global_vocab": compressed.get("global_vocab"),
            "local_vocab": compressed.get("local_vocab"),
            "typed_representation": compressed.get("typed_representation"),
        },
        "recovered_state": {
            "memory": recovered.memory,
            "constraints": recovered.constraints,
            "typed_representation": recovered.ensure_typed_representation(anchor_memory=anchor_memory).as_dict(),
        },
        "validation": {
            "contract_satisfaction": validation.get("contract_satisfaction"),
            "alignment": validation.get("alignment_score"),
            "coverage": validation.get("coverage_score"),
            "drift": validation.get("drift"),
            "drift_risk": validation.get("drift_risk"),
            "passed": validation.get("passed"),
        },
    }


def _diff_values(left: Any, right: Any) -> Any:
    if left == right:
        return None
    if isinstance(left, dict) and isinstance(right, dict):
        diff: Dict[str, Any] = {}
        keys = sorted(set(left) | set(right))
        for key in keys:
            nested = _diff_values(left.get(key), right.get(key))
            if nested is not None:
                diff[key] = nested
        return diff or None
    if isinstance(left, list) and isinstance(right, list):
        if left == right:
            return None
        return {"left": left, "right": right}
    return {"left": left, "right": right}


def _compare_paths(deterministic: Dict[str, Any], backend_mock: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "compressed_state": _diff_values(deterministic["compressed_state"], backend_mock["compressed_state"]),
        "recovered_state": _diff_values(deterministic["recovered_state"], backend_mock["recovered_state"]),
        "validation": _diff_values(deterministic["validation"], backend_mock["validation"]),
    }


def _evaluate_exit_criteria(deterministic: Dict[str, Any], backend_mock: Dict[str, Any]) -> Dict[str, Any]:
    left = deterministic["validation"]
    right = backend_mock["validation"]

    contract_delta = round(abs(float(left["contract_satisfaction"]) - float(right["contract_satisfaction"])), 4)
    alignment_delta = round(abs(float(left["alignment"]) - float(right["alignment"])), 4)
    drift_delta = round(abs(float(left["drift"]) - float(right["drift"])), 4)
    commit_equal = bool(left["passed"]) == bool(right["passed"])

    checks = {
        "commit_decision_match": commit_equal,
        "contract_satisfaction_within_tolerance": contract_delta <= CONTRACT_TOLERANCE,
        "alignment_within_tolerance": alignment_delta <= ALIGNMENT_TOLERANCE,
        "drift_within_tolerance": drift_delta <= DRIFT_TOLERANCE,
    }

    overall_pass = all(checks.values())
    if not commit_equal:
        priority = "protocol_behavior_mismatch"
    elif not checks["contract_satisfaction_within_tolerance"] or not checks["alignment_within_tolerance"]:
        priority = "semantic_equivalence_mismatch"
    elif not checks["drift_within_tolerance"]:
        priority = "compression_fidelity_mismatch"
    else:
        priority = "equivalent"

    return {
        "tolerances": {
            "contract_satisfaction": CONTRACT_TOLERANCE,
            "alignment": ALIGNMENT_TOLERANCE,
            "drift": DRIFT_TOLERANCE,
        },
        "deltas": {
            "contract_satisfaction": contract_delta,
            "alignment": alignment_delta,
            "drift": drift_delta,
        },
        "checks": checks,
        "overall_pass": overall_pass,
        "priority": priority,
    }


def _select_tasks(tasks: List[Dict], task_id: str | None) -> List[Dict]:
    if not task_id:
        return tasks
    selected = [task for task in tasks if task["id"] == task_id]
    if not selected:
        raise ValueError(f"Task id not found: {task_id}")
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare deterministic SRP path with backend-mediated mock path.")
    parser.add_argument("--task-id", default=None, help="Optional single task id to inspect.")
    parser.add_argument(
        "--output",
        default=str(RESULTS_DIR / "runtime_equivalence_test.json"),
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks = _select_tasks(load_tasks(), args.task_id)
    mock_client = ModelClient(BackendConfig(backend="mock"))
    reports = []

    for task in tasks:
        deterministic = _run_path(task, client=None, label="client_none")
        mediated = _run_path(task, client=mock_client, label="backend_mock")
        reports.append(
            {
                "task_id": task["id"],
                "deterministic_path": deterministic,
                "backend_mock_path": mediated,
                "diff": _compare_paths(deterministic, mediated),
                "exit_criteria": _evaluate_exit_criteria(deterministic, mediated),
            }
        )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(reports, indent=2), encoding="utf-8")
    print(f"Wrote runtime equivalence report to {output_path}")


if __name__ == "__main__":
    main()
