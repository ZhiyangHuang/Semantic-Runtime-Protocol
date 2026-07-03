import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"


def load_results(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def filter_rows(rows, task_id: str | None):
    if not task_id:
        return rows
    return [row for row in rows if row.get("task_id") == task_id]


def aggregate_rows(rows):
    grouped = {}
    for row in rows:
        key = (row["method"], row["cycle"])
        grouped.setdefault(key, []).append(row["drift"])
    aggregated = []
    for (method, cycle), drifts in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        aggregated.append(
            {
                "method": method,
                "cycle": cycle,
                "drift": round(sum(drifts) / len(drifts), 4),
            }
        )
    return aggregated


def plot_contract_with_commit(rows, output_dir: Path, title_suffix: str = ""):
    import matplotlib.pyplot as plt

    srp_rows = [row for row in rows if row.get("method") == "srp"]
    if not srp_rows:
        raise ValueError("No SRP rows found for contract plot.")

    srp_rows = sorted(srp_rows, key=lambda row: row["cycle"])
    cycles = [row["cycle"] for row in srp_rows]
    contract = [row.get("validation_contract_satisfaction") for row in srp_rows]
    committed = [1 if row.get("state_committed") else 0 for row in srp_rows]

    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(cycles, contract, marker="o", color="#1f77b4", label="contract satisfaction")
    ax1.set_xlabel("Cycle")
    ax1.set_ylabel("Contract Satisfaction", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.set_ylim(0, 1.05)

    ax2 = ax1.twinx()
    ax2.step(cycles, committed, where="mid", color="#d62728", label="commit decision")
    ax2.set_ylabel("Commit Decision", color="#d62728")
    ax2.tick_params(axis="y", labelcolor="#d62728")
    ax2.set_yticks([0, 1])
    ax2.set_yticklabels(["rollback", "commit"])

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="lower right")
    plt.title(f"SRP Contract Satisfaction and Commit Decisions{title_suffix}")
    fig.tight_layout()
    output = output_dir / "contract_commit_plot.png"
    fig.savefig(output)
    print(f"Wrote plot to {output}")


def plot_with_matplotlib(rows, output_dir: Path, title_suffix: str = ""):
    import matplotlib.pyplot as plt

    grouped = {}
    for row in rows:
        grouped.setdefault(row["method"], {"x": [], "y": []})
        grouped[row["method"]]["x"].append(row["cycle"])
        grouped[row["method"]]["y"].append(row["drift"])

    plt.figure(figsize=(8, 5))
    for method, values in grouped.items():
        plt.plot(values["x"], values["y"], marker="o", label=method)
    plt.xlabel("Cycle")
    plt.ylabel("Semantic Drift")
    plt.title(f"Drift Over Iterations{title_suffix}")
    plt.legend()
    plt.tight_layout()
    output = output_dir / "drift_plot.png"
    plt.savefig(output)
    print(f"Wrote plot to {output}")


def plot_ascii(rows, output_dir: Path, title_suffix: str = ""):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["method"], [])
        grouped[row["method"]].append((row["cycle"], row["drift"]))
    output = output_dir / "drift_plot.txt"
    lines = [f"Drift Over Iterations{title_suffix}"]
    for method, values in grouped.items():
        points = ", ".join(f"c{cycle}={drift}" for cycle, drift in values)
        lines.append(f"{method}: {points}")
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote ascii plot to {output}")


def parse_args():
    parser = argparse.ArgumentParser(description="Plot drift curves from experiment results.")
    parser.add_argument("--results-file", default=str(RESULTS_DIR / "results.json"))
    parser.add_argument("--output-dir", default=str(RESULTS_DIR))
    parser.add_argument("--task-id", default=None, help="Optional task id filter.")
    parser.add_argument(
        "--kind",
        choices=["drift", "contract"],
        default="drift",
        help="Select which paper-facing figure to generate.",
    )
    parser.add_argument(
        "--aggregate",
        action="store_true",
        help="Aggregate mean drift by method and cycle before plotting.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    results_file = Path(args.results_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = filter_rows(load_results(results_file), args.task_id)
    if args.aggregate:
        rows = aggregate_rows(rows)
    title_suffix = f" ({args.task_id})" if args.task_id else ""
    try:
        if args.kind == "contract":
            plot_contract_with_commit(rows, output_dir, title_suffix=title_suffix)
        else:
            plot_with_matplotlib(rows, output_dir, title_suffix=title_suffix)
    except Exception:
        plot_ascii(rows, output_dir, title_suffix=title_suffix)


if __name__ == "__main__":
    main()
