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


def _stage_snapshot(task: Dict, client: ModelClient | None, label: str) -> Dict[str, Any]:
    state = _build_initial_state(task)
    anchor_memory = task["initial_state"]["memory"]
    validation_targets = build_validation_targets(task)
    compressed = compress_state(state, client=client)
    recovered = recover_state(compressed, client=client, anchor_memory=anchor_memory)
    validation = validate_state(state.memory, recovered.memory, validation_targets)
    return {
        "label": label,
        "input_state": state.as_dict(),
        "validation_targets": validation_targets.as_dict(),
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
            "drift_blocks_commit": validation.get("drift_blocks_commit"),
            "passed": validation.get("passed"),
        },
    }


def _diff(left: Any, right: Any) -> Any:
    if left == right:
        return None
    if isinstance(left, dict) and isinstance(right, dict):
        out: Dict[str, Any] = {}
        for key in sorted(set(left) | set(right)):
            nested = _diff(left.get(key), right.get(key))
            if nested is not None:
                out[key] = nested
        return out or None
    if isinstance(left, list) and isinstance(right, list):
        if left == right:
            return None
        return {"left": left, "right": right}
    return {"left": left, "right": right}


def _first_divergence(trace_a: Dict[str, Any], trace_b: Dict[str, Any]) -> Dict[str, Any]:
    ordered_stages = [
        "input_state",
        "validation_targets",
        "compressed_state",
        "recovered_state",
        "validation",
    ]
    for stage in ordered_stages:
        stage_diff = _diff(trace_a[stage], trace_b[stage])
        if stage_diff is not None:
            return {
                "stage": stage,
                "diff": stage_diff,
            }
    return {
        "stage": None,
        "diff": None,
    }


def _select_task(task_id: str) -> Dict:
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise ValueError(f"Task id not found: {task_id}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trace first divergence between deterministic and backend-mock SRP paths.")
    parser.add_argument("--task-id", required=True, help="Task id to inspect.")
    parser.add_argument(
        "--output",
        default=str(RESULTS_DIR / "protocol_behavior_trace.json"),
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    task = _select_task(args.task_id)
    deterministic = _stage_snapshot(task, client=None, label="client_none")
    backend_mock = _stage_snapshot(task, client=ModelClient(BackendConfig(backend="mock")), label="backend_mock")
    report = {
        "task_id": task["id"],
        "deterministic_path": deterministic,
        "backend_mock_path": backend_mock,
        "first_divergence": _first_divergence(deterministic, backend_mock),
    }
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote protocol behavior trace to {output_path}")


if __name__ == "__main__":
    main()
