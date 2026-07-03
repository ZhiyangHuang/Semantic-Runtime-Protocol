import argparse
import json
import os
from pathlib import Path
from typing import Dict, List

from collect_batch_summary import collect_rows, resolve_path as resolve_batch_path
from build_main_figure import build_figure
from paper_table_formatter import (
    group_rows,
    write_markdown,
    write_latex,
    write_quality_markdown,
    write_quality_latex,
    write_efficiency_markdown,
    write_efficiency_latex,
    write_token_breakdown_markdown,
    write_token_breakdown_latex,
    write_guardrail_markdown,
    write_guardrail_latex,
    write_camera_ready_markdown,
    write_camera_ready_latex,
    resolve_path as resolve_table_path,
)


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DEFAULT_RUNS_DIR = RESULTS_DIR / "batch_runs" / "first_paper_formal_local"
DEFAULT_BATCH_SUMMARY = RESULTS_DIR / "batch_summary_table.json"
DEFAULT_OUTPUT_DIR = RESULTS_DIR / "evidence_pipeline"
DEFAULT_MANIFEST = DEFAULT_OUTPUT_DIR / "evidence_manifest.json"
DEFAULT_TRACE_LOG = DEFAULT_OUTPUT_DIR / "execution_trace_log.json"
DEFAULT_TRACE_TABLE = DEFAULT_OUTPUT_DIR / "execution_trace_table.json"
DEFAULT_MAIN_FIGURE = RESULTS_DIR / "paper_figure_pack" / "main_3panel_figure.png"


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    repo_relative = ROOT.parent / path
    if repo_relative.exists() or "srp_experiment" in value:
        return repo_relative
    return ROOT / path


def parse_args():
    parser = argparse.ArgumentParser(description="Build the SRP evidence pipeline artifacts.")
    parser.add_argument("--runs-dir", default=os.getenv("SRP_BATCH_RUNS_DIR", str(DEFAULT_RUNS_DIR)))
    parser.add_argument("--batch-summary", default=os.getenv("SRP_BATCH_SUMMARY", str(DEFAULT_BATCH_SUMMARY)))
    parser.add_argument("--output-dir", default=os.getenv("SRP_EVIDENCE_OUTPUT_DIR", str(DEFAULT_OUTPUT_DIR)))
    parser.add_argument("--manifest", default=os.getenv("SRP_EVIDENCE_MANIFEST", str(DEFAULT_MANIFEST)))
    parser.add_argument("--trace-log", default=os.getenv("SRP_EVIDENCE_TRACE_LOG", str(DEFAULT_TRACE_LOG)))
    parser.add_argument("--trace-table", default=os.getenv("SRP_EVIDENCE_TRACE_TABLE", str(DEFAULT_TRACE_TABLE)))
    parser.add_argument("--main-figure", default=os.getenv("SRP_MAIN_FIGURE", str(DEFAULT_MAIN_FIGURE)))
    parser.add_argument("--task-id", default=None, help="Optional task id to isolate in the trace log.")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def collect_trace_rows(runs_dir: Path, task_id: str | None = None) -> List[Dict]:
    trace_rows: List[Dict] = []
    for results_path in sorted(runs_dir.rglob("results.json")):
        payload = load_json(results_path)
        if not isinstance(payload, list):
            continue
        for row in payload:
            if task_id and row.get("task_id") != task_id:
                continue
            trace_rows.append(row)
    trace_rows.sort(key=lambda row: (row.get("task_id", ""), row.get("method", ""), int(row.get("cycle", 0))))
    return trace_rows


def build_execution_trace_table(results_rows: List[Dict], task_id: str | None = None) -> List[Dict]:
    if task_id:
        results_rows = [row for row in results_rows if row.get("task_id") == task_id]
    trace_rows = []
    for row in results_rows:
        trace_rows.append(
            {
                "task_id": row.get("task_id"),
                "method": row.get("method"),
                "cycle": row.get("cycle"),
                "runtime": {
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
                },
                "usage": {
                    "prompt_tokens": row.get("prompt_tokens"),
                    "completion_tokens": row.get("completion_tokens"),
                    "total_tokens": row.get("total_tokens"),
                    "latency_seconds": row.get("latency_seconds"),
                },
                "evaluation": {
                    "evaluation_query": row.get("evaluation_query"),
                    "query_answer": row.get("query_answer"),
                    "query_success": row.get("query_success"),
                    "judge_score": row.get("judge_score"),
                },
                "notes": row.get("notes"),
            }
        )
    return trace_rows


def build_manifest(runs_dir: Path, batch_summary_path: Path, output_dir: Path, trace_log: Path, trace_table: Path, main_figure: Path, row_count: int, trace_count: int) -> Dict:
    return {
        "runs_dir": str(runs_dir),
        "batch_summary": str(batch_summary_path),
        "output_dir": str(output_dir),
        "trace_log": str(trace_log),
        "trace_table": str(trace_table),
        "main_figure": str(main_figure),
        "row_count": row_count,
        "trace_count": trace_count,
        "artifacts": {
            "batch_summary_table": str(resolve_path("srp_experiment/results/batch_summary_table.json")),
            "paper_table": str(resolve_path("srp_experiment/results/paper_table.md")),
            "quality_table": str(resolve_path("srp_experiment/results/quality_table.md")),
            "efficiency_table": str(resolve_path("srp_experiment/results/efficiency_table.md")),
            "guardrail_table": str(resolve_path("srp_experiment/results/guardrail_table.md")),
            "camera_ready_table": str(resolve_path("srp_experiment/results/camera_ready_table.md")),
            "drift_plot": str(resolve_path("srp_experiment/results/paper_figure_pack/drift_plot.png")),
            "contract_commit_plot": str(resolve_path("srp_experiment/results/paper_figure_pack/contract_commit_plot.png")),
            "main_3panel_figure": str(main_figure),
        },
        "layers": {
            "trace_writer": "results.json and summary.json emitted per run",
            "results_reducer": "collect_batch_summary.py",
            "benchmark_aggregator": "batch_summary_table.json + paper tables",
            "figure_generator": "build_main_figure.py + plot_results.py",
            "reviewer_ready_logging": "execution_trace_log.json + execution_trace_table.json + manifest",
        },
    }


def main():
    args = parse_args()
    runs_dir = resolve_batch_path(args.runs_dir)
    batch_summary_path = resolve_table_path(args.batch_summary)
    output_dir = resolve_path(args.output_dir)
    manifest_path = resolve_path(args.manifest)
    trace_log_path = resolve_path(args.trace_log)
    trace_table_path = resolve_path(args.trace_table)
    main_figure_path = resolve_path(args.main_figure)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = collect_rows(runs_dir)
    rows.sort(key=lambda row: (row["backend"], row["model"], row["cycles"], row["method_bundle"], row["method"]))
    write_json(batch_summary_path, rows)

    methods, grouped_rows = group_rows(rows)
    write_markdown(resolve_table_path("srp_experiment/results/paper_table.md"), methods, grouped_rows)
    write_latex(resolve_table_path("srp_experiment/results/paper_table.tex"), methods, grouped_rows)
    write_quality_markdown(resolve_table_path("srp_experiment/results/quality_table.md"), methods, grouped_rows)
    write_quality_latex(resolve_table_path("srp_experiment/results/quality_table.tex"), methods, grouped_rows)
    write_efficiency_markdown(resolve_table_path("srp_experiment/results/efficiency_table.md"), methods, grouped_rows)
    write_efficiency_latex(resolve_table_path("srp_experiment/results/efficiency_table.tex"), methods, grouped_rows)
    write_token_breakdown_markdown(resolve_table_path("srp_experiment/results/token_breakdown_table.md"), methods, grouped_rows)
    write_token_breakdown_latex(resolve_table_path("srp_experiment/results/token_breakdown_table.tex"), methods, grouped_rows)
    write_guardrail_markdown(resolve_table_path("srp_experiment/results/guardrail_table.md"), methods, grouped_rows)
    write_guardrail_latex(resolve_table_path("srp_experiment/results/guardrail_table.tex"), methods, grouped_rows)
    write_camera_ready_markdown(resolve_table_path("srp_experiment/results/camera_ready_table.md"), grouped_rows)
    write_camera_ready_latex(resolve_table_path("srp_experiment/results/camera_ready_table.tex"), grouped_rows)

    build_figure(
        batch_summary_path=batch_summary_path,
        batch_runs_dir=runs_dir,
        output_path=main_figure_path,
    )

    trace_rows = collect_trace_rows(runs_dir, args.task_id)
    trace_table = build_execution_trace_table(trace_rows, args.task_id)
    write_json(trace_log_path, trace_rows)
    write_json(trace_table_path, trace_table)

    manifest = build_manifest(
        runs_dir=runs_dir,
        batch_summary_path=batch_summary_path,
        output_dir=output_dir,
        trace_log=trace_log_path,
        trace_table=trace_table_path,
        main_figure=main_figure_path,
        row_count=len(rows),
        trace_count=len(trace_table),
    )
    write_json(manifest_path, manifest)

    print(f"[Evidence] Runs dir: {runs_dir}")
    print(f"[Evidence] Rows: {len(rows)}")
    print(f"[Evidence] Trace rows: {len(trace_rows)}")
    print(f"[Evidence] Manifest: {manifest_path}")
    print(f"[Evidence] Trace log: {trace_log_path}")
    print(f"[Evidence] Trace table: {trace_table_path}")
    print(f"[Evidence] Main figure: {main_figure_path}")


if __name__ == "__main__":
    main()
