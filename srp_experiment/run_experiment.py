import argparse
import json
import os
from pathlib import Path
from statistics import mean

from baselines import run_rag, run_rag_srp, run_rag_srp_anchor, run_rag_srp_v2, run_raw_prompt, run_summarization
from env_utils import env_float, env_list, load_env_file
from eval import compute_drift, compute_task_success, run_shared_query_evaluation
from eval.llm_judge import score_semantic_equivalence
from model_backend import BackendConfig, ModelClient
from srp import run_srp


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
DEFAULT_LONGBENCH_TASK_FILE = DATA_DIR / "longbench_v2" / "tasks.json"

load_env_file()


def load_tasks(task_file: str | None = None, task_source: str = "all"):
    tasks = []
    candidate_paths = []

    if task_file:
        path = Path(task_file)
        if not path.is_absolute():
            path = ROOT.parent / path
        payload = json.loads(path.read_text(encoding="utf-8"))
        return _normalize_payload(payload, source_file=path)

    if task_source == "longbench_v2":
        payload = json.loads(DEFAULT_LONGBENCH_TASK_FILE.read_text(encoding="utf-8"))
        return _normalize_payload(payload, source_file=DEFAULT_LONGBENCH_TASK_FILE)

    if task_source == "toy":
        candidate_paths.extend(sorted(DATA_DIR.glob("task_*.json")))
    else:
        candidate_paths.extend(sorted(DATA_DIR.glob("task_*.json")))
        candidate_paths.extend(sorted(DATA_DIR.rglob("tasks.json")))

    seen = set()
    for path in candidate_paths:
        if path in seen:
            continue
        seen.add(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        tasks.extend(_normalize_payload(payload, source_file=path))
    return tasks


def _normalize_payload(payload, source_file: Path):
    if isinstance(payload, list):
        return [_normalize_task(task, source_file, container={}) for task in payload]
    if isinstance(payload, dict):
        if "tasks" in payload and isinstance(payload["tasks"], list):
            container = {k: v for k, v in payload.items() if k != "tasks"}
            return [_normalize_task(task, source_file, container=container) for task in payload["tasks"]]
        if "task" in payload and isinstance(payload["task"], dict):
            container = {k: v for k, v in payload.items() if k != "task"}
            return [_normalize_task(payload["task"], source_file, container=container)]
        if "initial_state" in payload and "queries" in payload:
            return [_normalize_task(payload, source_file, container={})]
    raise ValueError(f"Unsupported task payload format in {source_file}")


def _normalize_task(task, source_file: Path, container: dict):
    normalized = dict(task)
    metadata = dict(normalized.get("metadata", {}))
    for key in ("benchmark", "family", "split", "subset", "source"):
        if key in container and key not in metadata:
            metadata[key] = container[key]
    metadata.setdefault("source_file", str(source_file))
    if metadata:
        normalized["metadata"] = metadata
    return normalized


def _resolve_query_expectations(task: dict, cycle: int):
    query_expectations = task.get("query_expectations", [])
    if not query_expectations:
        return task["expected_keywords"]
    index = (cycle - 1) % len(query_expectations)
    value = query_expectations[index]
    return value if value else task["expected_keywords"]


def run_method(name, task, cycles, client, srp_max_cycle_drift, srp_min_keyword_score):
    if name == "raw_prompt":
        return run_raw_prompt(task, cycles, client=client)
    if name == "summarization":
        return run_summarization(task, cycles, client=client)
    if name == "rag":
        return run_rag(task, cycles, client=client)
    if name == "rag_srp":
        return run_rag_srp(task, cycles, client=client)
    if name == "rag_srp_anchor":
        return run_rag_srp_anchor(task, cycles, client=client)
    if name == "rag_srp_v2":
        return run_rag_srp_v2(task, cycles, client=client)
    if name == "srp":
        return run_srp(
            task,
            cycles,
            client=client,
            max_cycle_drift=srp_max_cycle_drift,
            min_keyword_score=srp_min_keyword_score,
        )
    raise ValueError(f"Unknown method: {name}")


def summarize_records(method, task, records, client):
    summary = []
    reference = task["initial_state"]["memory"]
    queries = list(task.get("queries", [])) or ["Restate the task-relevant memory."]
    for record in records:
        candidate = record.get("committed_memory", record.get("recovered_text", record["representation"]))
        usage = record.get("usage") or {}
        drift = compute_drift(reference, candidate)
        success = compute_task_success(candidate, task["expected_keywords"])
        judge = score_semantic_equivalence(reference, candidate, task["expected_keywords"], client=client)
        evaluation_query = queries[(record["cycle"] - 1) % len(queries)]
        query_expectations = _resolve_query_expectations(task, record["cycle"])
        query_eval = run_shared_query_evaluation(
            candidate,
            evaluation_query,
            query_expectations,
            record["cycle"],
            client=client,
        )
        query_usage = query_eval.get("usage") or {}
        judge_usage = judge.get("usage") or {}
        summary.append(
            {
                "task_id": task["id"],
                "method": method,
                "cycle": record["cycle"],
                "tokens": record["tokens"],
                "prompt_tokens": record.get("prompt_tokens"),
                "completion_tokens": record.get("completion_tokens"),
                "total_tokens": record.get("total_tokens"),
                "query_prompt_tokens": query_usage.get("prompt_tokens"),
                "query_completion_tokens": query_usage.get("completion_tokens"),
                "query_total_tokens": query_usage.get("total_tokens"),
                "judge_prompt_tokens": judge_usage.get("prompt_tokens"),
                "judge_completion_tokens": judge_usage.get("completion_tokens"),
                "judge_total_tokens": judge_usage.get("total_tokens"),
                "latency_seconds": record.get("latency_seconds"),
                "drift": drift,
                "task_success": success,
                "state_committed": record.get("state_committed"),
                "validation_score": record.get("validation_score"),
                "validation_contract_satisfaction": record.get("validation_contract_satisfaction"),
                "validation_passed": record.get("validation_passed"),
                "validation_drift": record.get("validation_drift"),
                "validation_drift_risk": record.get("validation_drift_risk"),
                "validation_drift_blocks_commit": record.get("validation_drift_blocks_commit"),
                "validation_coverage": record.get("validation_coverage"),
                "validation_alignment": record.get("validation_alignment"),
                "validation_leakage_detected": record.get("validation_leakage_detected"),
                "max_cycle_drift": record.get("max_cycle_drift"),
                "blocking_drift": record.get("blocking_drift"),
                "min_keyword_score": record.get("min_keyword_score"),
                "min_coverage_score": record.get("min_coverage_score"),
                "evaluation_query": query_eval["query"],
                "query_answer": query_eval["answer"],
                "query_success": query_eval["query_success"],
                "judge_score": round(judge["score"], 4),
                "notes": record["notes"],
            }
        )
    return summary


def summarize_record(method, task, record, client):
    reference = task["initial_state"]["memory"]
    queries = list(task.get("queries", [])) or ["Restate the task-relevant memory."]
    candidate = record.get("committed_memory", record.get("recovered_text", record["representation"]))
    usage = record.get("usage") or {}
    drift = compute_drift(reference, candidate)
    success = compute_task_success(candidate, task["expected_keywords"])
    judge = score_semantic_equivalence(reference, candidate, task["expected_keywords"], client=client)
    evaluation_query = queries[(record["cycle"] - 1) % len(queries)]
    query_expectations = _resolve_query_expectations(task, record["cycle"])
    query_eval = run_shared_query_evaluation(
        candidate,
        evaluation_query,
        query_expectations,
        record["cycle"],
        client=client,
    )
    query_usage = query_eval.get("usage") or {}
    judge_usage = judge.get("usage") or {}
    return {
        "task_id": task["id"],
        "method": method,
        "cycle": record["cycle"],
        "tokens": record["tokens"],
        "prompt_tokens": record.get("prompt_tokens"),
        "completion_tokens": record.get("completion_tokens"),
        "total_tokens": record.get("total_tokens"),
        "query_prompt_tokens": query_usage.get("prompt_tokens"),
        "query_completion_tokens": query_usage.get("completion_tokens"),
        "query_total_tokens": query_usage.get("total_tokens"),
        "judge_prompt_tokens": judge_usage.get("prompt_tokens"),
        "judge_completion_tokens": judge_usage.get("completion_tokens"),
        "judge_total_tokens": judge_usage.get("total_tokens"),
        "latency_seconds": record.get("latency_seconds"),
        "drift": drift,
        "task_success": success,
        "state_committed": record.get("state_committed"),
        "validation_score": record.get("validation_score"),
        "validation_contract_satisfaction": record.get("validation_contract_satisfaction"),
        "validation_passed": record.get("validation_passed"),
        "validation_drift": record.get("validation_drift"),
        "validation_drift_risk": record.get("validation_drift_risk"),
        "validation_drift_blocks_commit": record.get("validation_drift_blocks_commit"),
        "validation_coverage": record.get("validation_coverage"),
        "validation_alignment": record.get("validation_alignment"),
        "validation_leakage_detected": record.get("validation_leakage_detected"),
        "max_cycle_drift": record.get("max_cycle_drift"),
        "blocking_drift": record.get("blocking_drift"),
        "min_keyword_score": record.get("min_keyword_score"),
        "min_coverage_score": record.get("min_coverage_score"),
        "evaluation_query": query_eval["query"],
        "query_answer": query_eval["answer"],
        "query_success": query_eval["query_success"],
        "judge_score": round(judge["score"], 4),
        "notes": record["notes"],
    }


def aggregate(rows):
    grouped = {}
    for row in rows:
        key = row["method"]
        grouped.setdefault(
            key,
            {
                "drift": [],
                "task_success": [],
                "query_success": [],
                "tokens": [],
                "latency_seconds": [],
                "prompt_tokens": [],
                "completion_tokens": [],
                "total_tokens": [],
                "query_prompt_tokens": [],
                "query_completion_tokens": [],
                "query_total_tokens": [],
                "judge_prompt_tokens": [],
                "judge_completion_tokens": [],
                "judge_total_tokens": [],
            },
        )
        grouped[key]["drift"].append(row["drift"])
        grouped[key]["task_success"].append(row["task_success"])
        grouped[key]["query_success"].append(row["query_success"])
        grouped[key]["tokens"].append(row["tokens"])
        if row.get("latency_seconds") is not None:
            grouped[key]["latency_seconds"].append(row["latency_seconds"])
        for field in (
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "query_prompt_tokens",
            "query_completion_tokens",
            "query_total_tokens",
            "judge_prompt_tokens",
            "judge_completion_tokens",
            "judge_total_tokens",
        ):
            if row.get(field) is not None:
                grouped[key][field].append(row[field])
    return {
        method: {
            "mean_drift": round(mean(values["drift"]), 4),
            "mean_task_success": round(mean(values["task_success"]), 4),
            "mean_query_success": round(mean(values["query_success"]), 4),
            "mean_tokens": round(mean(values["tokens"]), 2),
            "mean_latency_seconds": round(mean(values["latency_seconds"]), 4) if values["latency_seconds"] else None,
            "mean_prompt_tokens": round(mean(values["prompt_tokens"]), 2) if values["prompt_tokens"] else None,
            "mean_completion_tokens": round(mean(values["completion_tokens"]), 2) if values["completion_tokens"] else None,
            "mean_total_tokens": round(mean(values["total_tokens"]), 2) if values["total_tokens"] else None,
            "mean_query_prompt_tokens": round(mean(values["query_prompt_tokens"]), 2) if values["query_prompt_tokens"] else None,
            "mean_query_completion_tokens": round(mean(values["query_completion_tokens"]), 2) if values["query_completion_tokens"] else None,
            "mean_query_total_tokens": round(mean(values["query_total_tokens"]), 2) if values["query_total_tokens"] else None,
            "mean_judge_prompt_tokens": round(mean(values["judge_prompt_tokens"]), 2) if values["judge_prompt_tokens"] else None,
            "mean_judge_completion_tokens": round(mean(values["judge_completion_tokens"]), 2) if values["judge_completion_tokens"] else None,
            "mean_judge_total_tokens": round(mean(values["judge_total_tokens"]), 2) if values["judge_total_tokens"] else None,
        }
        for method, values in grouped.items()
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Run SRP baseline experiments.")
    parser.add_argument("--backend", choices=["mock", "openai", "local"], default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--task-file", default=None, help="Explicit task payload file to run instead of scanning srp_experiment/data.")
    parser.add_argument(
        "--task-source",
        choices=["all", "toy", "longbench_v2"],
        default="all",
        help="Task family selector used when --task-file is not provided.",
    )
    parser.add_argument("--repeat-id", type=int, default=None, help="Optional repeat index for batch reruns.")
    parser.add_argument("--cycles", type=int, default=int(os.getenv("SRP_CYCLES", "5")))
    parser.add_argument(
        "--methods",
        nargs="*",
        default=env_list("SRP_METHODS", ["raw_prompt", "summarization", "rag", "srp"]),
    )
    parser.add_argument(
        "--srp-max-cycle-drift",
        type=float,
        default=env_float("SRP_MAX_CYCLE_DRIFT", 0.35),
        help="Maximum allowed per-cycle SRP drift before the state rolls back to the pre-compression memory.",
    )
    parser.add_argument(
        "--srp-min-keyword-score",
        type=float,
        default=env_float("SRP_MIN_KEYWORD_SCORE", 0.5),
        help="Minimum accepted per-cycle SRP keyword retention score before the state rolls back to the pre-compression memory.",
    )
    parser.add_argument("--output-dir", default=os.getenv("SRP_OUTPUT_DIR", str(RESULTS_DIR)))
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    tasks = load_tasks(task_file=args.task_file, task_source=args.task_source)
    methods = args.methods
    cycles = args.cycles
    srp_max_cycle_drift = args.srp_max_cycle_drift
    srp_min_keyword_score = args.srp_min_keyword_score
    config = BackendConfig.from_env(backend=args.backend, model=args.model)
    client = ModelClient(config)
    rows = []
    progress = {
        "status": "RUNNING",
        "last_completed": None,
        "current": None,
    }

    def write_checkpoint(status: str, error: str | None = None):
        output_dir.mkdir(exist_ok=True)
        checkpoint_results = output_dir / "results.partial.json"
        checkpoint_summary = output_dir / "summary.partial.json"
        crash_report = output_dir / "crash_report.json"
        checkpoint_results.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        checkpoint_summary.write_text(json.dumps(aggregate(rows), indent=2), encoding="utf-8")
        payload = {
            "status": status,
            "error": error,
            "progress": progress,
            "backend": client.describe(),
            "cycles": cycles,
            "methods": methods,
            "task_source": args.task_source,
            "task_file": args.task_file,
            "repeat_id": args.repeat_id,
            "task_count": len(tasks),
            "partial_results_file": str(checkpoint_results),
            "partial_summary_file": str(checkpoint_summary),
        }
        crash_report.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    try:
        for task in tasks:
            for method in methods:
                progress["current"] = {"task_id": task["id"], "method": method, "phase": "run_method"}
                records = run_method(method, task, cycles, client, srp_max_cycle_drift, srp_min_keyword_score)
                for record in records:
                    progress["current"] = {
                        "task_id": task["id"],
                        "method": method,
                        "phase": "summarize_record",
                        "cycle": record["cycle"],
                    }
                    row = summarize_record(method, task, record, client)
                    rows.append(row)
                    progress["last_completed"] = {
                        "task_id": task["id"],
                        "method": method,
                        "cycle": record["cycle"],
                    }
                    write_checkpoint("RUNNING")
        progress["status"] = "COMPLETED"
    except KeyboardInterrupt:
        progress["status"] = "INTERRUPTED"
        write_checkpoint("INTERRUPTED", error="KeyboardInterrupt")
        raise
    except Exception as exc:
        progress["status"] = "CRASHED"
        write_checkpoint("CRASHED", error=str(exc))
        raise

    detailed_path = output_dir / "results.json"
    summary_path = output_dir / "summary.json"
    metadata_path = output_dir / "run_metadata.json"
    detailed_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(aggregate(rows), indent=2), encoding="utf-8")
    metadata = {
        "backend": client.describe(),
        "cycles": cycles,
        "methods": methods,
        "task_source": args.task_source,
        "task_file": args.task_file,
        "repeat_id": args.repeat_id,
        "srp_max_cycle_drift": srp_max_cycle_drift,
        "srp_min_keyword_score": srp_min_keyword_score,
        "task_count": len(tasks),
        "results_file": str(detailed_path),
        "summary_file": str(summary_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Backend: {config.backend}")
    print(f"Model: {config.model}")
    print(f"Wrote detailed results to {detailed_path}")
    print(f"Wrote summary results to {summary_path}")
    print(f"Wrote run metadata to {metadata_path}")


if __name__ == "__main__":
    main()
