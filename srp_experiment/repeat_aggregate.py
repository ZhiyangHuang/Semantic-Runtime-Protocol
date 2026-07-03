import argparse
import csv
import json
import os
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

from env_utils import load_env_file


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DEFAULT_INPUT_JSON = RESULTS_DIR / "batch_summary_table.json"
DEFAULT_OUTPUT_JSON = RESULTS_DIR / "repeat_aggregate_table.json"
DEFAULT_OUTPUT_CSV = RESULTS_DIR / "repeat_aggregate_table.csv"
DEFAULT_OUTPUT_MD = RESULTS_DIR / "repeat_aggregate_table.md"

load_env_file()


NUMERIC_FIELDS = [
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
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate repeated batch runs into mean/std/count tables.")
    parser.add_argument("--input-json", default=os.getenv("SRP_PAPER_TABLE_INPUT", str(DEFAULT_INPUT_JSON)))
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


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected a list in {path}")
    return payload


def parse_numeric(value: Any) -> float | None:
    if value in ("", None):
        return None
    return float(value)


def safe_mean(values: list[float]) -> float | None:
    return round(mean(values), 6) if values else None


def safe_std(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    return round(pstdev(values), 6)


def aggregate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, int, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            str(row.get("backend", "")),
            str(row.get("model", "")),
            int(row.get("cycles", 0)),
            str(row.get("method_bundle", "")),
            str(row.get("method", "")),
        )
        grouped.setdefault(key, []).append(row)

    aggregated: list[dict[str, Any]] = []
    for key, bucket in sorted(grouped.items(), key=lambda item: item[0]):
        backend, model, cycles, method_bundle, method = key
        repeat_ids = sorted(
            {
                int(row["repeat_id"])
                for row in bucket
                if row.get("repeat_id") not in ("", None)
            }
        )
        result: dict[str, Any] = {
            "backend": backend,
            "model": model,
            "cycles": cycles,
            "method_bundle": method_bundle,
            "method": method,
            "repeat_count": len(bucket),
            "repeat_ids": repeat_ids,
        }
        for field in NUMERIC_FIELDS:
            values = [parse_numeric(row.get(field)) for row in bucket]
            numeric_values = [value for value in values if value is not None]
            result[f"{field}_mean"] = safe_mean(numeric_values)
            result[f"{field}_std"] = safe_std(numeric_values)
            result[f"{field}_count"] = len(numeric_values)
        aggregated.append(result)
    return aggregated


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fmt(value: Any, digits: int = 4) -> str:
    if value in ("", None):
        return "-"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "| Backend | Model | Cycles | Method Bundle | Method | Repeats | Drift Mean | Drift Std | Success Mean | Success Std | Query Mean | Query Std | Tokens Mean | Tokens Std | Latency Mean | Latency Std | Commit Mean | Commit Std | Validation Drift Mean | Validation Drift Std | Rollback Mean | Rollback Std |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["backend"],
                    row["model"],
                    str(row["cycles"]),
                    row["method_bundle"],
                    row["method"],
                    str(row["repeat_count"]),
                    fmt(row["mean_drift_mean"]),
                    fmt(row["mean_drift_std"]),
                    fmt(row["mean_task_success_mean"]),
                    fmt(row["mean_task_success_std"]),
                    fmt(row["mean_query_success_mean"]),
                    fmt(row["mean_query_success_std"]),
                    fmt(row["mean_tokens_mean"], digits=2),
                    fmt(row["mean_tokens_std"], digits=2),
                    fmt(row["mean_latency_seconds_mean"]),
                    fmt(row["mean_latency_seconds_std"]),
                    fmt(row["commit_rate_mean"]),
                    fmt(row["commit_rate_std"]),
                    fmt(row["mean_validation_drift_mean"]),
                    fmt(row["mean_validation_drift_std"]),
                    fmt(row["rollback_count_mean"]),
                    fmt(row["rollback_count_std"]),
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    input_json = resolve_path(args.input_json)
    output_json = resolve_path(args.output_json)
    output_csv = resolve_path(args.output_csv)
    output_md = resolve_path(args.output_md)

    rows = load_rows(input_json)
    aggregated = aggregate_rows(rows)

    write_json(output_json, aggregated)
    write_csv(output_csv, aggregated)
    write_markdown(output_md, aggregated)

    print(f"[Repeat Aggregate] Input: {input_json}")
    print(f"[Repeat Aggregate] Grouped rows: {len(aggregated)}")
    print(f"[Repeat Aggregate] JSON: {output_json}")
    print(f"[Repeat Aggregate] CSV: {output_csv}")
    print(f"[Repeat Aggregate] Markdown: {output_md}")


if __name__ == "__main__":
    main()
