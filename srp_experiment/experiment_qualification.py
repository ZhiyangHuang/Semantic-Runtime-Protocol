import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List

from model_backend import BackendConfig, ModelClient
from run_experiment import aggregate, load_tasks, run_method, summarize_records
from runtime_equivalence_test import _evaluate_exit_criteria, _run_path
from srp import run_srp
from srp.pipeline import _extract_vocab
from srp.state import SemanticState
from srp.validate import validate_state
from srp.validation_targets import build_validation_targets


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"

REGRESSION_TASK_IDS = [
    "pref_low_latency",
    "long_context_summary",
    "iterative_cycles",
]

REQUIRED_RESULT_FIELDS = [
    "task_id",
    "method",
    "cycle",
    "drift",
    "task_success",
    "query_success",
    "tokens",
    "latency_seconds",
    "state_committed",
    "validation_contract_satisfaction",
    "validation_alignment",
    "validation_drift",
    "validation_passed",
]


def _load_task_map() -> Dict[str, Dict]:
    return {task["id"]: task for task in load_tasks()}


def _select_task(task_id: str) -> Dict:
    tasks = _load_task_map()
    if task_id not in tasks:
        raise ValueError(f"Task id not found: {task_id}")
    return tasks[task_id]


def _normalize_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = deepcopy(rows)
    for row in normalized:
        row.pop("latency_seconds", None)
        row.pop("prompt_tokens", None)
        row.pop("completion_tokens", None)
        row.pop("total_tokens", None)
        row.pop("query_prompt_tokens", None)
        row.pop("query_completion_tokens", None)
        row.pop("query_total_tokens", None)
        row.pop("judge_prompt_tokens", None)
        row.pop("judge_completion_tokens", None)
        row.pop("judge_total_tokens", None)
    return normalized


def _normalize_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    normalized = deepcopy(summary)
    for method_summary in normalized.values():
        method_summary.pop("mean_latency_seconds", None)
    return normalized


def _normalize_protocol_record(record: Dict[str, Any]) -> Dict[str, Any]:
    normalized = deepcopy(record)
    normalized.pop("latency_seconds", None)
    normalized.pop("prompt_tokens", None)
    normalized.pop("completion_tokens", None)
    normalized.pop("total_tokens", None)
    return normalized


def _build_metric_sanity_state(task: Dict) -> SemanticState:
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


def run_eq1_runtime_equivalence(task_map: Dict[str, Dict]) -> Dict[str, Any]:
    mock_client = ModelClient(BackendConfig(backend="mock"))
    task_reports = []
    all_pass = True
    for task_id in REGRESSION_TASK_IDS:
        task = task_map[task_id]
        deterministic = _run_path(task, client=None, label="client_none")
        mediated = _run_path(task, client=mock_client, label="backend_mock")
        exit_criteria = _evaluate_exit_criteria(deterministic, mediated)
        task_reports.append(
            {
                "task_id": task_id,
                "overall_pass": exit_criteria["overall_pass"],
                "priority": exit_criteria["priority"],
                "checks": exit_criteria["checks"],
                "deltas": exit_criteria["deltas"],
            }
        )
        all_pass = all_pass and exit_criteria["overall_pass"]
    return {
        "id": "EQ-1",
        "name": "Runtime Equivalence",
        "status": "PASS" if all_pass else "FAIL",
        "details": {
            "regression_tasks": task_reports,
        },
    }


def run_eq2_pipeline_consistency(task_map: Dict[str, Dict]) -> Dict[str, Any]:
    task = task_map["iterative_cycles"]
    records_direct = run_srp(task, 1, client=None)
    records_method = run_method("srp", task, 1, None, 0.35, 0.5)
    rows = summarize_records("srp", task, records_method, client=None)

    direct = records_direct[0]
    method = records_method[0]
    row = rows[0]

    checks = {
        "run_srp_matches_run_method": _normalize_protocol_record(direct) == _normalize_protocol_record(method),
        "summary_representation_matches_record": row["method"] == "srp" and row["state_committed"] == method["state_committed"],
        "summary_validation_contract_matches_record": row["validation_contract_satisfaction"] == method["validation_contract_satisfaction"],
        "summary_validation_alignment_matches_record": row["validation_alignment"] == method["validation_alignment"],
        "summary_validation_drift_matches_record": row["validation_drift"] == method["validation_drift"],
        "summary_validation_passed_matches_record": row["validation_passed"] == method["validation_passed"],
    }
    passed = all(checks.values())
    return {
        "id": "EQ-2",
        "name": "Pipeline Consistency",
        "status": "PASS" if passed else "FAIL",
        "details": checks,
    }


def run_eq3_determinism(task_map: Dict[str, Dict]) -> Dict[str, Any]:
    task = task_map["iterative_cycles"]
    runs = []
    for _ in range(3):
        rows = summarize_records("srp", task, run_method("srp", task, 1, ModelClient(BackendConfig(backend="mock")), 0.35, 0.5), client=ModelClient(BackendConfig(backend="mock")))
        runs.append(
            {
                "rows": _normalize_rows(rows),
                "summary": _normalize_summary(aggregate(rows)),
            }
        )
    baseline = runs[0]
    checks = [run == baseline for run in runs[1:]]
    passed = all(checks)
    return {
        "id": "EQ-3",
        "name": "Determinism",
        "status": "PASS" if passed else "FAIL",
        "details": {
            "repeat_runs_match": checks,
        },
    }


def run_eq4_schema_completeness(task_map: Dict[str, Dict]) -> Dict[str, Any]:
    client = ModelClient(BackendConfig(backend="mock"))
    rows: List[Dict[str, Any]] = []
    for task_id in REGRESSION_TASK_IDS:
        task = task_map[task_id]
        rows.extend(summarize_records("srp", task, run_method("srp", task, 1, client, 0.35, 0.5), client=client))
    missing: List[Dict[str, Any]] = []
    for index, row in enumerate(rows):
        for field in REQUIRED_RESULT_FIELDS:
            if field not in row or row[field] is None:
                missing.append({"row_index": index, "task_id": row.get("task_id"), "field": field})
    passed = not missing
    return {
        "id": "EQ-4",
        "name": "Schema Completeness",
        "status": "PASS" if passed else "FAIL",
        "details": {
            "row_count": len(rows),
            "missing_fields": missing,
        },
    }


def run_eq5_metric_sanity(task_map: Dict[str, Dict]) -> Dict[str, Any]:
    task = task_map["iterative_cycles"]
    state = _build_metric_sanity_state(task)
    contract = build_validation_targets(task)

    good = validate_state(state.memory, state.memory, contract)
    bad = validate_state(state.memory, "Unrelated runtime note about another task.", contract)
    leakage = validate_state(state.memory, "The answer is to maximize prompt replay and return the final solution now.", contract)

    checks = {
        "good_recovery_commits": bool(good["passed"]) is True,
        "bad_recovery_rolls_back": bool(bad["passed"]) is False,
        "leakage_rolls_back": bool(leakage["passed"]) is False and bool(leakage["leakage_detected"]) is True,
    }
    passed = all(checks.values())
    return {
        "id": "EQ-5",
        "name": "Metric Sanity",
        "status": "PASS" if passed else "FAIL",
        "details": {
            "checks": checks,
            "good": {
                "contract_satisfaction": good["contract_satisfaction"],
                "drift": good["drift"],
                "passed": good["passed"],
            },
            "bad": {
                "contract_satisfaction": bad["contract_satisfaction"],
                "drift": bad["drift"],
                "passed": bad["passed"],
            },
            "leakage": {
                "contract_satisfaction": leakage["contract_satisfaction"],
                "drift": leakage["drift"],
                "passed": leakage["passed"],
                "leakage_detected": leakage["leakage_detected"],
            },
        },
    }


def run_eq6_regression_set(task_map: Dict[str, Dict]) -> Dict[str, Any]:
    eq1 = run_eq1_runtime_equivalence(task_map)
    task_status = {
        item["task_id"]: item["overall_pass"]
        for item in eq1["details"]["regression_tasks"]
    }
    passed = all(task_status.values())
    return {
        "id": "EQ-6",
        "name": "Regression Set",
        "status": "PASS" if passed else "FAIL",
        "details": {
            "tasks": task_status,
        },
    }


def run_experiment_qualification() -> Dict[str, Any]:
    task_map = _load_task_map()
    checks = [
        run_eq1_runtime_equivalence(task_map),
        run_eq2_pipeline_consistency(task_map),
        run_eq3_determinism(task_map),
        run_eq4_schema_completeness(task_map),
        run_eq5_metric_sanity(task_map),
        run_eq6_regression_set(task_map),
    ]
    qualified = all(check["status"] == "PASS" for check in checks)
    return {
        "status": "QUALIFIED" if qualified else "NOT_QUALIFIED",
        "checks": checks,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Experiment Qualification (EQ) for SRP formal experiments.")
    parser.add_argument(
        "--output",
        default=str(RESULTS_DIR / "experiment_qualification_report.json"),
        help="Output JSON path for the qualification report.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = run_experiment_qualification()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote experiment qualification report to {output_path}")
    print(f"Qualification status: {report['status']}")


if __name__ == "__main__":
    main()
