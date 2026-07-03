from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DEFAULT_OUTPUT_DIR = RESULTS_DIR / "long_horizon_report"
DEFAULT_STAGE_BINS = "1-10,11-50,51-100,101-250,251-500,501-1000"


@dataclass
class StageBin:
    label: str
    start: int
    end: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a long-horizon SRP report from 1000-round evidence.")
    parser.add_argument(
        "--input-dir",
        action="append",
        default=[],
        help="Directory that contains a results.json file. Can be repeated.",
    )
    parser.add_argument(
        "--input-glob",
        default=None,
        help="Optional glob for results.json files, e.g. srp_experiment/results/batch_runs/**/results.json",
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--stage-bins", default=DEFAULT_STAGE_BINS)
    parser.add_argument("--task-id", default=None)
    return parser.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return ROOT.parent / path


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_stage_bins(spec: str) -> list[StageBin]:
    bins: list[StageBin] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        start_text, end_text = chunk.split("-", 1)
        bins.append(StageBin(label=chunk, start=int(start_text), end=int(end_text)))
    return bins


def discover_result_files(args: argparse.Namespace) -> list[Path]:
    files: list[Path] = []
    for entry in args.input_dir:
        path = resolve_path(entry)
        if path.is_dir():
            candidate = path / "results.json"
            if candidate.exists():
                files.append(candidate)
            else:
                files.extend(sorted(path.rglob("results.json")))
        elif path.is_file() and path.name == "results.json":
            files.append(path)
    if args.input_glob:
        files.extend(sorted(resolve_path(args.input_glob).parent.glob(Path(args.input_glob).name)))
    uniq: list[Path] = []
    seen = set()
    for path in files:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        uniq.append(resolved)
    return uniq


def load_trace_rows(result_files: list[Path], task_id: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in result_files:
        payload = load_json(path)
        if not isinstance(payload, list):
            continue
        for row in payload:
            if task_id and row.get("task_id") != task_id:
                continue
            cycle = row.get("cycle")
            method = row.get("method")
            if cycle is None or method is None:
                continue
            rows.append(
                {
                    "source_file": str(path),
                    "task_id": row.get("task_id"),
                    "method": method,
                    "cycle": int(cycle),
                    "state_committed": row.get("state_committed"),
                    "validation_passed": row.get("validation_passed"),
                    "validation_score": row.get("validation_score"),
                    "validation_contract_satisfaction": row.get("validation_contract_satisfaction"),
                    "validation_coverage": row.get("validation_coverage"),
                    "validation_alignment": row.get("validation_alignment"),
                    "validation_drift": row.get("validation_drift"),
                    "validation_drift_risk": row.get("validation_drift_risk"),
                    "validation_drift_blocks_commit": row.get("validation_drift_blocks_commit"),
                    "validation_leakage_detected": row.get("validation_leakage_detected"),
                    "drift": row.get("drift"),
                    "task_success": row.get("task_success"),
                    "tokens": row.get("tokens"),
                    "latency_seconds": row.get("latency_seconds"),
                    "query_success": row.get("query_success"),
                    "judge_score": row.get("judge_score"),
                }
            )
    return rows


def mean_or_none(values: list[float]) -> float | None:
    return round(mean(values), 4) if values else None


def mean_rate(values: list[bool]) -> float | None:
    return round(mean([1.0 if value else 0.0 for value in values]), 4) if values else None


def aggregate_by_cycle(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["method"], row["cycle"])].append(row)
    aggregated: list[dict[str, Any]] = []
    for (method, cycle), bucket in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        def collect(field: str) -> list[float]:
            values = [float(row[field]) for row in bucket if row.get(field) is not None]
            return values

        committed = [bool(row["state_committed"]) for row in bucket if row.get("state_committed") is not None]
        validated = [bool(row["validation_passed"]) for row in bucket if row.get("validation_passed") is not None]
        aggregated.append(
            {
                "method": method,
                "cycle": cycle,
                "n": len(bucket),
                "mean_drift": mean_or_none(collect("drift")),
                "mean_task_success": mean_or_none(collect("task_success")),
                "mean_tokens": mean_or_none(collect("tokens")),
                "mean_latency_seconds": mean_or_none(collect("latency_seconds")),
                "mean_contract_satisfaction": mean_or_none(collect("validation_contract_satisfaction")),
                "mean_alignment": mean_or_none(collect("validation_alignment")),
                "mean_validation_drift": mean_or_none(collect("validation_drift")),
                "mean_coverage": mean_or_none(collect("validation_coverage")),
                "mean_validation_score": mean_or_none(collect("validation_score")),
                "commit_rate": mean([1.0 if value else 0.0 for value in committed]) if committed else None,
                "validation_pass_rate": mean([1.0 if value else 0.0 for value in validated]) if validated else None,
            }
        )
    return aggregated


def parse_stage(label: str) -> StageBin:
    start_text, end_text = label.split("-", 1)
    return StageBin(label=label, start=int(start_text), end=int(end_text))


def summarize_stages(cycle_rows: list[dict[str, Any]], bins: list[StageBin]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in cycle_rows:
        for bin_ in bins:
            if bin_.start <= row["cycle"] <= bin_.end:
                grouped[(row["method"], bin_.label)].append(row)
                break
    summaries: list[dict[str, Any]] = []
    for (method, label), bucket in sorted(grouped.items(), key=lambda item: (item[0][0], parse_stage(item[0][1]).start)):
        baseline_cycle = min(row["cycle"] for row in bucket)
        baseline_rows = [row for row in bucket if row["cycle"] == baseline_cycle]
        summaries.append(
            {
                "method": method,
                "stage": label,
                "start_cycle": parse_stage(label).start,
                "end_cycle": parse_stage(label).end,
                "rows": len(bucket),
                "baseline_cycle": baseline_cycle,
                "baseline_drift": mean_or_none([float(row["drift"]) for row in baseline_rows if row.get("drift") is not None]),
                "mean_drift": mean_or_none([float(row["drift"]) for row in bucket if row.get("drift") is not None]),
                "drift_offset": None,
                "mean_contract_satisfaction": mean_or_none([float(row["validation_contract_satisfaction"]) for row in bucket if row.get("validation_contract_satisfaction") is not None]),
                "mean_alignment": mean_or_none([float(row["validation_alignment"]) for row in bucket if row.get("validation_alignment") is not None]),
                "mean_validation_drift": mean_or_none([float(row["validation_drift"]) for row in bucket if row.get("validation_drift") is not None]),
                "mean_tokens": mean_or_none([float(row["tokens"]) for row in bucket if row.get("tokens") is not None]),
                "commit_rate": mean_rate([bool(row["state_committed"]) for row in bucket if row.get("state_committed") is not None]),
            }
        )
    for summary in summaries:
        if summary["baseline_drift"] is not None and summary["mean_drift"] is not None:
            summary["drift_offset"] = round(summary["mean_drift"] - summary["baseline_drift"], 4)
    return summaries


def summarize_consistency(cycle_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in cycle_rows:
        grouped[(row["method"], row["cycle"])].append(row)
    summaries: list[dict[str, Any]] = []
    for (method, cycle), bucket in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        drifts = [float(row["drift"]) for row in bucket if row.get("drift") is not None]
        contracts = [float(row["validation_contract_satisfaction"]) for row in bucket if row.get("validation_contract_satisfaction") is not None]
        if not drifts and not contracts:
            continue
        summaries.append(
            {
                "method": method,
                "cycle": cycle,
                "n": len(bucket),
                "drift_mean": mean_or_none(drifts),
                "drift_std": round(pstdev(drifts), 4) if len(drifts) > 1 else 0.0 if drifts else None,
                "contract_mean": mean_or_none(contracts),
                "contract_std": round(pstdev(contracts), 4) if len(contracts) > 1 else 0.0 if contracts else None,
                "commit_rate": mean_rate([bool(row["state_committed"]) for row in bucket if row.get("state_committed") is not None]),
            }
        )
    return summaries


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


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


def write_markdown_table(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    if not rows:
        path.write_text(f"# {title}\n\nNo rows available.\n", encoding="utf-8")
        return
    headers = list(rows[0].keys())
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        values = [str(row.get(header, "")) for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_report(path: Path, payload: dict[str, Any]) -> None:
    lines = [
        "# Long Horizon SRP Report",
        "",
        f"- Status: `{payload['status']}`",
        f"- Input files: `{payload['input_count']}`",
        f"- Total trace rows: `{payload['trace_rows']}`",
        f"- Methods: `{', '.join(payload['methods'])}`",
        f"- Task filter: `{payload['task_id'] or 'all'}`",
        "",
        "## Interpretation",
        "",
        "SRP is evaluated as a state-transition validity space: models act as executors of the constraint system, not as evaluators or reasoners over it.",
        "The long-horizon curves are used to inspect whether repeated compression and recovery preserve validity under extended scheduling.",
        "",
        "## Stage Offsets",
        "",
    ]
    for row in payload["stage_summaries"]:
        lines.append(
            f"- {row['method']} @ {row['stage']}: drift={row['mean_drift']} offset={row['drift_offset']} contract={row['mean_contract_satisfaction']} commit={row['commit_rate']}"
        )
    lines.append("")
    lines.append("## Consistency Snapshot")
    for row in payload["consistency"]:
        lines.append(
            f"- {row['method']} c{row['cycle']}: drift_mean={row['drift_mean']} drift_std={row['drift_std']} contract_mean={row['contract_mean']} contract_std={row['contract_std']}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_plots(output_dir: Path, cycle_rows: list[dict[str, Any]]) -> list[str]:
    import matplotlib.pyplot as plt

    methods = sorted({row["method"] for row in cycle_rows})
    colors = plt.get_cmap("tab10")
    color_map = {method: colors(i % 10) for i, method in enumerate(methods)}
    figure_paths: list[str] = []

    def series(field: str, method: str) -> tuple[list[int], list[float]]:
        points = [row for row in cycle_rows if row["method"] == method and row.get(field) is not None]
        points.sort(key=lambda row: row["cycle"])
        return [row["cycle"] for row in points], [float(row[field]) for row in points]

    # Drift + contract figure
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True, constrained_layout=True)
    for method in methods:
        xs, ys = series("mean_drift", method)
        if xs:
            axes[0].plot(xs, ys, label=method, color=color_map[method], linewidth=2)
    axes[0].set_title("Long-Horizon Mean Drift by Cycle")
    axes[0].set_ylabel("Mean Drift")
    axes[0].legend(frameon=False, ncol=2)
    for method in methods:
        xs, ys = series("mean_contract_satisfaction", method)
        if xs:
            axes[1].plot(xs, ys, label=method, color=color_map[method], linewidth=2)
    axes[1].set_title("Long-Horizon Contract Satisfaction by Cycle")
    axes[1].set_xlabel("Cycle")
    axes[1].set_ylabel("Mean Contract Satisfaction")
    axes[1].set_ylim(0, 1.05)
    path = output_dir / "long_horizon_drift_contract.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    figure_paths.append(str(path))

    # Consistency band figure
    fig, ax = plt.subplots(figsize=(12, 4.8), constrained_layout=True)
    for method in methods:
        xs, ys = series("mean_drift", method)
        if not xs:
            continue
        ax.plot(xs, ys, label=method, color=color_map[method], linewidth=2)
    ax.set_title("Long-Horizon Drift Curve")
    ax.set_xlabel("Cycle")
    ax.set_ylabel("Mean Drift")
    ax.legend(frameon=False, ncol=2)
    path = output_dir / "long_horizon_drift_curve.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    figure_paths.append(str(path))

    return figure_paths


def main() -> int:
    args = parse_args()
    output_dir = resolve_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    result_files = discover_result_files(args)
    cycle_rows = load_trace_rows(result_files, task_id=args.task_id)
    if not cycle_rows:
        payload = {
            "status": "NOT_READY",
            "input_count": len(result_files),
            "trace_rows": 0,
            "methods": [],
            "task_id": args.task_id,
            "stage_summaries": [],
            "consistency": [],
        }
        write_report(output_dir / "long_horizon_report.md", payload)
        write_json(output_dir / "long_horizon_report.json", payload)
        return 1

    methods = sorted({row["method"] for row in cycle_rows})
    stage_bins = parse_stage_bins(args.stage_bins)
    cycle_summary = aggregate_by_cycle(cycle_rows)
    stage_summaries = summarize_stages(cycle_rows, stage_bins)
    consistency = summarize_consistency(cycle_rows)
    figure_paths = build_plots(output_dir, cycle_summary)

    payload = {
        "status": "READY_TO_ANALYZE",
        "input_count": len(result_files),
        "trace_rows": len(cycle_rows),
        "methods": methods,
        "task_id": args.task_id,
        "stage_bins": [bin_.__dict__ for bin_ in stage_bins],
        "cycle_summary_rows": cycle_summary,
        "stage_summaries": stage_summaries,
        "consistency": consistency,
        "figure_paths": figure_paths,
        "result_files": [str(path) for path in result_files],
    }

    write_json(output_dir / "long_horizon_report.json", payload)
    write_csv(output_dir / "cycle_summary.csv", cycle_summary)
    write_csv(output_dir / "stage_summary.csv", stage_summaries)
    write_csv(output_dir / "consistency.csv", consistency)
    write_markdown_table(output_dir / "cycle_summary.md", cycle_summary, "Cycle Summary")
    write_markdown_table(output_dir / "stage_summary.md", stage_summaries, "Stage Summary")
    write_markdown_table(output_dir / "consistency.md", consistency, "Consistency Summary")
    write_report(output_dir / "long_horizon_report.md", payload)

    print(f"[Long Horizon] Inputs: {len(result_files)}")
    print(f"[Long Horizon] Trace rows: {len(cycle_rows)}")
    print(f"[Long Horizon] Report: {output_dir / 'long_horizon_report.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
