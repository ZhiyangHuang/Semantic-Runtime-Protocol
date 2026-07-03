import argparse
import csv
import json
import os
from pathlib import Path
from typing import Dict, List
from statistics import mean

from env_utils import load_env_file

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DEFAULT_RUNS_DIR = RESULTS_DIR / "batch_runs"
DEFAULT_OUTPUT_JSON = RESULTS_DIR / "batch_summary_table.json"
DEFAULT_OUTPUT_CSV = RESULTS_DIR / "batch_summary_table.csv"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "batch_summary_table.md"

load_env_file()


def parse_args():
    parser = argparse.ArgumentParser(description="Collect batch run summaries into a paper-ready table.")
    parser.add_argument("--runs-dir", default=os.getenv("SRP_BATCH_RUNS_DIR", str(DEFAULT_RUNS_DIR)))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-csv", default=str(DEFAULT_OUTPUT_CSV))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    repo_relative = ROOT.parent / path
    if repo_relative.exists() or "srp_experiment" in value:
        return repo_relative
    return ROOT / path


def safe_load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_guardrail_metrics(results_payload, method_name: str) -> Dict:
    if not isinstance(results_payload, list):
        return {
            "commit_rate": "",
            "mean_validation_drift": "",
            "rollback_count": "",
        }

    method_rows = [row for row in results_payload if row.get("method") == method_name]
    if not method_rows:
        return {
            "commit_rate": "",
            "mean_validation_drift": "",
            "rollback_count": "",
        }

    committed_values = [row.get("state_committed") for row in method_rows if row.get("state_committed") is not None]
    validation_drifts = [row.get("validation_drift") for row in method_rows if row.get("validation_drift") is not None]

    commit_rate = ""
    rollback_count = ""
    if committed_values:
        commit_rate = round(sum(1 for value in committed_values if value) / len(committed_values), 4)
        rollback_count = sum(1 for value in committed_values if value is False)

    mean_validation_drift = ""
    if validation_drifts:
        mean_validation_drift = round(mean(float(value) for value in validation_drifts), 4)

    return {
        "commit_rate": commit_rate,
        "mean_validation_drift": mean_validation_drift,
        "rollback_count": rollback_count,
    }


def collect_rows(runs_dir: Path) -> List[Dict]:
    rows: List[Dict] = []
    for summary_path in sorted(runs_dir.rglob("summary.json")):
        run_dir = summary_path.parent
        metadata_path = run_dir / "run_metadata.json"
        results_path = run_dir / "results.json"
        if not metadata_path.exists():
            continue
        metadata = safe_load_json(metadata_path)
        summary = safe_load_json(summary_path)
        results_payload = safe_load_json(results_path) if results_path.exists() else None
        backend_info = metadata.get("backend", {})
        methods = metadata.get("methods", [])
        method_bundle = ",".join(methods)
        for method_name, metrics in summary.items():
            guardrail_metrics = compute_guardrail_metrics(results_payload, method_name)
            method_rows = []
            if isinstance(results_payload, list):
                method_rows = [row for row in results_payload if row.get("method") == method_name]
            prompt_tokens = [row.get("prompt_tokens") for row in method_rows if row.get("prompt_tokens") is not None]
            completion_tokens = [row.get("completion_tokens") for row in method_rows if row.get("completion_tokens") is not None]
            total_tokens = [row.get("total_tokens") for row in method_rows if row.get("total_tokens") is not None]
            query_prompt_tokens = [row.get("query_prompt_tokens") for row in method_rows if row.get("query_prompt_tokens") is not None]
            query_completion_tokens = [row.get("query_completion_tokens") for row in method_rows if row.get("query_completion_tokens") is not None]
            query_total_tokens = [row.get("query_total_tokens") for row in method_rows if row.get("query_total_tokens") is not None]
            judge_prompt_tokens = [row.get("judge_prompt_tokens") for row in method_rows if row.get("judge_prompt_tokens") is not None]
            judge_completion_tokens = [row.get("judge_completion_tokens") for row in method_rows if row.get("judge_completion_tokens") is not None]
            judge_total_tokens = [row.get("judge_total_tokens") for row in method_rows if row.get("judge_total_tokens") is not None]
            rows.append(
                {
                    "run_dir": str(run_dir),
                    "backend": backend_info.get("backend", ""),
                    "model": backend_info.get("model", ""),
                    "cycles": metadata.get("cycles", ""),
                    "repeat_id": metadata.get("repeat_id", ""),
                    "method_bundle": method_bundle,
                    "method": method_name,
                    "mean_drift": metrics.get("mean_drift", ""),
                    "mean_task_success": metrics.get("mean_task_success", ""),
                    "mean_query_success": metrics.get("mean_query_success", ""),
                    "mean_tokens": metrics.get("mean_tokens", ""),
                    "mean_latency_seconds": metrics.get("mean_latency_seconds", ""),
                    "mean_prompt_tokens": round(mean(prompt_tokens), 2) if prompt_tokens else "",
                    "mean_completion_tokens": round(mean(completion_tokens), 2) if completion_tokens else "",
                    "mean_total_tokens": round(mean(total_tokens), 2) if total_tokens else "",
                    "mean_query_prompt_tokens": round(mean(query_prompt_tokens), 2) if query_prompt_tokens else "",
                    "mean_query_completion_tokens": round(mean(query_completion_tokens), 2) if query_completion_tokens else "",
                    "mean_query_total_tokens": round(mean(query_total_tokens), 2) if query_total_tokens else "",
                    "mean_judge_prompt_tokens": round(mean(judge_prompt_tokens), 2) if judge_prompt_tokens else "",
                    "mean_judge_completion_tokens": round(mean(judge_completion_tokens), 2) if judge_completion_tokens else "",
                    "mean_judge_total_tokens": round(mean(judge_total_tokens), 2) if judge_total_tokens else "",
                    "commit_rate": guardrail_metrics["commit_rate"],
                    "mean_validation_drift": guardrail_metrics["mean_validation_drift"],
                    "rollback_count": guardrail_metrics["rollback_count"],
                }
            )
    return rows


def write_csv(path: Path, rows: List[Dict]):
    fieldnames = [
        "backend",
        "model",
        "cycles",
        "repeat_id",
        "method_bundle",
        "method",
        "mean_drift",
        "mean_task_success",
        "mean_query_success",
        "mean_tokens",
        "mean_latency_seconds",
        "mean_prompt_tokens",
        "mean_completion_tokens",
        "mean_total_tokens",
        "mean_query_prompt_tokens",
        "mean_query_completion_tokens",
        "mean_query_total_tokens",
        "mean_judge_prompt_tokens",
        "mean_judge_completion_tokens",
        "mean_judge_total_tokens",
        "commit_rate",
        "mean_validation_drift",
        "rollback_count",
        "run_dir",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown(path: Path, rows: List[Dict]):
    lines = [
        "| Backend | Model | Cycles | Repeat | Method Bundle | Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens | Mean Latency (s) | Mean Prompt Tokens | Mean Completion Tokens | Mean Total Tokens | Mean Query Prompt Tokens | Mean Query Completion Tokens | Mean Query Total Tokens | Mean Judge Prompt Tokens | Mean Judge Completion Tokens | Mean Judge Total Tokens | Commit Rate | Mean Validation Drift | Rollback Count |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['backend']} | {row['model']} | {row['cycles']} | {row['repeat_id']} | {row['method_bundle']} | "
            f"{row['method']} | {row['mean_drift']} | {row['mean_task_success']} | {row['mean_query_success']} | "
            f"{row['mean_tokens']} | {row['mean_latency_seconds']} | {row['mean_prompt_tokens']} | {row['mean_completion_tokens']} | "
            f"{row['mean_total_tokens']} | {row['mean_query_prompt_tokens']} | {row['mean_query_completion_tokens']} | {row['mean_query_total_tokens']} | "
            f"{row['mean_judge_prompt_tokens']} | {row['mean_judge_completion_tokens']} | {row['mean_judge_total_tokens']} | "
            f"{row['commit_rate']} | {row['mean_validation_drift']} | {row['rollback_count']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    runs_dir = resolve_path(args.runs_dir)
    rows = collect_rows(runs_dir)
    rows.sort(key=lambda row: (row["backend"], row["model"], row["cycles"], row["method_bundle"], row["method"]))

    output_json = resolve_path(args.output_json)
    output_csv = resolve_path(args.output_csv)
    output_md = resolve_path(args.output_md)

    output_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_csv(output_csv, rows)
    write_markdown(output_md, rows)

    print(f"[Collect] Runs dir: {runs_dir}")
    print(f"[Collect] Rows written: {len(rows)}")
    print(f"[Collect] JSON: {output_json}")
    print(f"[Collect] CSV: {output_csv}")
    print(f"[Collect] Markdown: {output_md}")


if __name__ == "__main__":
    main()
