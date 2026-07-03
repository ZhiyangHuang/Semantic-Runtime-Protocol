import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
DEFAULT_BATCH_SUMMARY = RESULTS_DIR / "batch_summary_table.json"
DEFAULT_BATCH_RUNS_DIR = RESULTS_DIR / "batch_runs" / "first_paper_formal_local"
DEFAULT_OUTPUT = RESULTS_DIR / "main_figure_3panel.png"

METHOD_ORDER = ["raw_prompt", "summarization", "rag", "srp"]
METHOD_COLORS = {
    "raw_prompt": "#8c564b",
    "summarization": "#7f7f7f",
    "rag": "#1f77b4",
    "srp": "#d62728",
}
METHOD_MARKERS = {
    "raw_prompt": "o",
    "summarization": "s",
    "rag": "^",
    "srp": "D",
}


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    repo_relative = ROOT.parent / path
    if repo_relative.exists() or "srp_experiment" in value:
        return repo_relative
    return ROOT / path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find_summary_rows(rows: List[Dict], cycles: int) -> List[Dict]:
    filtered = [row for row in rows if int(row.get("cycles", 0)) == cycles and row.get("method") in METHOD_ORDER]
    filtered.sort(key=lambda row: METHOD_ORDER.index(row["method"]))
    return filtered


def load_cycle_rows_from_batch_summary(batch_summary: List[Dict], cycles: int) -> List[Dict]:
    rows = [row for row in batch_summary if int(row.get("cycles", 0)) == cycles and row.get("method") in METHOD_ORDER]
    rows.sort(key=lambda row: METHOD_ORDER.index(row["method"]))
    return rows


def get_run_results(runs_dir: Path, cycles: int) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = {}
    for summary_path in sorted(runs_dir.rglob("summary.json")):
        run_dir = summary_path.parent
        metadata_path = run_dir / "run_metadata.json"
        results_path = run_dir / "results.json"
        if not metadata_path.exists() or not results_path.exists():
            continue
        metadata = load_json(metadata_path)
        if int(metadata.get("cycles", -1)) != cycles:
            continue
        payload = load_json(results_path)
        if not isinstance(payload, list):
            continue
        for method in METHOD_ORDER:
            method_rows = [row for row in payload if row.get("method") == method]
            if method_rows:
                grouped.setdefault(method, []).extend(method_rows)
    return grouped


def aggregate_drift_vs_cycle(rows: List[Dict]) -> Dict[str, Dict[str, List[float]]]:
    grouped: Dict[str, Dict[int, List[float]]] = {}
    for row in rows:
        method = row["method"]
        cycle = int(row["cycles"])
        grouped.setdefault(method, {}).setdefault(cycle, []).append(float(row["mean_drift"]))
    result: Dict[str, Dict[str, List[float]]] = {}
    for method in METHOD_ORDER:
        cycle_map = grouped.get(method, {})
        cycles = sorted(cycle_map)
        values = [mean(cycle_map[cycle]) for cycle in cycles]
        result[method] = {"cycles": cycles, "values": values}
    return result


def pareto_points(rows: List[Dict]) -> List[Tuple[str, float, float, int]]:
    points = []
    for row in rows:
        method = row["method"]
        if method not in METHOD_ORDER:
            continue
        points.append(
            (
                method,
                float(row["mean_tokens"]),
                float(row["mean_drift"]),
                int(row["cycles"]),
            )
        )
    return points


def load_srp_contract_rows(runs_dir: Path) -> Dict[int, Dict[str, float]]:
    contract_rows: Dict[int, Dict[str, List[float]]] = {}
    for summary_path in sorted(runs_dir.rglob("summary.json")):
        run_dir = summary_path.parent
        metadata_path = run_dir / "run_metadata.json"
        results_path = run_dir / "results.json"
        if not metadata_path.exists() or not results_path.exists():
            continue
        metadata = load_json(metadata_path)
        cycles = int(metadata.get("cycles", -1))
        payload = load_json(results_path)
        if not isinstance(payload, list):
            continue
        srp_rows = [row for row in payload if row.get("method") == "srp"]
        if not srp_rows:
            continue
        contract_rows.setdefault(cycles, {"contract": [], "commit": []})
        contract_rows[cycles]["contract"].extend(float(row["validation_contract_satisfaction"]) for row in srp_rows if row.get("validation_contract_satisfaction") is not None)
        contract_rows[cycles]["commit"].extend(1.0 if row.get("state_committed") else 0.0 for row in srp_rows if row.get("state_committed") is not None)
    aggregated = {}
    for cycle, buckets in contract_rows.items():
        aggregated[cycle] = {
            "contract": mean(buckets["contract"]) if buckets["contract"] else 0.0,
            "commit": mean(buckets["commit"]) if buckets["commit"] else 0.0,
        }
    return aggregated


def build_figure(batch_summary_path: Path, batch_runs_dir: Path, output_path: Path) -> None:
    import matplotlib.pyplot as plt

    batch_summary = load_json(batch_summary_path)

    cycles_order = [3, 5, 7]
    drift_by_cycle = {cycle: load_cycle_rows_from_batch_summary(batch_summary, cycle) for cycle in cycles_order}
    combined_rows = [row for rows in drift_by_cycle.values() for row in rows]
    drift_series = aggregate_drift_vs_cycle(combined_rows)
    pareto = pareto_points(combined_rows)
    contract = load_srp_contract_rows(batch_runs_dir)

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), constrained_layout=True)

    ax = axes[0]
    for method in METHOD_ORDER:
        series = drift_series.get(method, {"cycles": [], "values": []})
        ax.plot(
            series["cycles"],
            series["values"],
            marker=METHOD_MARKERS[method],
            linewidth=2.4,
            markersize=6,
            color=METHOD_COLORS[method],
            label=method.replace("_", " ").title(),
        )
    ax.set_title("A. Drift vs Cycles")
    ax.set_xlabel("Cycles")
    ax.set_ylabel("Mean Drift")
    ax.set_xticks(cycles_order)
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False, fontsize=9)

    ax = axes[1]
    for method in METHOD_ORDER:
        points = [(token, drift, cycle) for m, token, drift, cycle in pareto if m == method]
        if not points:
            continue
        tokens = [item[0] for item in points]
        drifts = [item[1] for item in points]
        cycles = [item[2] for item in points]
        ax.scatter(
            tokens,
            drifts,
            s=70,
            color=METHOD_COLORS[method],
            marker=METHOD_MARKERS[method],
            alpha=0.9,
            label=method.replace("_", " ").title(),
        )
        for token, drift, cycle in points:
            ax.annotate(
                f"c{cycle}",
                (token, drift),
                textcoords="offset points",
                xytext=(5, 4),
                fontsize=8,
                color=METHOD_COLORS[method],
            )
    ax.set_title("B. Pareto Frontier")
    ax.set_xlabel("Mean Tokens")
    ax.set_ylabel("Mean Drift")
    ax.set_ylim(bottom=0)
    ax.invert_xaxis()
    ax.legend(frameon=False, fontsize=9)

    ax = axes[2]
    srp_cycles = sorted(contract)
    contract_vals = [contract[cycle]["contract"] for cycle in srp_cycles]
    commit_vals = [contract[cycle]["commit"] for cycle in srp_cycles]
    ax.plot(srp_cycles, contract_vals, color="#1f77b4", marker="o", linewidth=2.4, label="Contract Satisfaction")
    ax.set_title("C. Contract Stability")
    ax.set_xlabel("Cycles")
    ax.set_ylabel("Contract Satisfaction", color="#1f77b4")
    ax.set_xticks(cycles_order)
    ax.set_ylim(0, 1.05)
    ax.tick_params(axis="y", labelcolor="#1f77b4")

    ax2 = ax.twinx()
    ax2.step(srp_cycles, commit_vals, where="mid", color="#d62728", linewidth=2.0, label="Commit Rate")
    ax2.set_ylabel("Commit Rate", color="#d62728")
    ax2.set_ylim(0, 1.05)
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.set_yticks([0, 0.5, 1.0])

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, frameon=False, loc="lower right", fontsize=9)

    fig.suptitle("SRP: Drift, Efficiency Frontier, and Contract Stability", fontsize=14, y=1.03)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"Wrote main figure to {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Build a 3-panel paper figure from formal SRP evidence.")
    parser.add_argument("--batch-summary", default=str(DEFAULT_BATCH_SUMMARY))
    parser.add_argument("--batch-runs-dir", default=str(DEFAULT_BATCH_RUNS_DIR))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_figure(
        batch_summary_path=resolve_path(args.batch_summary),
        batch_runs_dir=resolve_path(args.batch_runs_dir),
        output_path=resolve_path(args.output),
    )


if __name__ == "__main__":
    main()
