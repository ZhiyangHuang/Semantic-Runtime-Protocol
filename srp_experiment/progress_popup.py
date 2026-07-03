import argparse
import json
import tkinter as tk
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show a lightweight progress popup for SRP batch experiments.")
    parser.add_argument("--progress-file", required=True)
    parser.add_argument("--title", default="SRP Experiment Progress")
    parser.add_argument("--poll-ms", type=int, default=3000)
    return parser.parse_args()


def load_progress(path: Path) -> dict:
    if not path.exists():
        return {
            "status": "WAITING",
            "total_runs": 0,
            "completed_runs": 0,
            "failed_runs": 0,
            "remaining_runs": 0,
            "current_run": None,
            "last_completed_run": None,
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
            "status": "WAITING",
            "total_runs": 0,
            "completed_runs": 0,
            "failed_runs": 0,
            "remaining_runs": 0,
            "current_run": None,
            "last_completed_run": None,
        }


def render_text(progress: dict) -> str:
    status = progress.get("status", "WAITING")
    total = progress.get("total_runs", 0)
    completed = progress.get("completed_runs", 0)
    failed = progress.get("failed_runs", 0)
    remaining = progress.get("remaining_runs", 0)
    current = progress.get("current_run") or {}
    last_completed = progress.get("last_completed_run") or {}

    lines = [
        f"Status: {status}",
        f"Progress: {completed}/{total} completed",
        f"Remaining: {remaining}",
        f"Failed: {failed}",
        "",
    ]

    if current:
        methods = ", ".join(current.get("methods", []))
        lines.extend(
            [
                "Current run:",
                f"  #{current.get('index', '-')}: {current.get('name', '-')}",
                f"  model={current.get('model', '-')}",
                f"  cycles={current.get('cycles', '-')}, repeat={current.get('repeat_id', '-')}",
                f"  methods={methods or '-'}",
                "",
            ]
        )

    if last_completed:
        methods = ", ".join(last_completed.get("methods", []))
        lines.extend(
            [
                "Last completed:",
                f"  {last_completed.get('name', '-')}",
                f"  model={last_completed.get('model', '-')}",
                f"  cycles={last_completed.get('cycles', '-')}, repeat={last_completed.get('repeat_id', '-')}",
                f"  methods={methods or '-'}",
            ]
        )

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    progress_path = Path(args.progress_file)

    root = tk.Tk()
    root.title(args.title)
    root.attributes("-topmost", True)
    root.resizable(False, False)
    root.geometry("460x240")

    frame = tk.Frame(root, padx=12, pady=12)
    frame.pack(fill="both", expand=True)

    label = tk.Label(frame, text="Waiting for experiment progress...", justify="left", anchor="nw", font=("Consolas", 10))
    label.pack(fill="both", expand=True)

    footer = tk.Label(frame, text=str(progress_path), justify="left", anchor="w", fg="gray40")
    footer.pack(fill="x")

    def refresh():
        progress = load_progress(progress_path)
        label.config(text=render_text(progress))
        status = progress.get("status")
        if status in {"COMPLETED", "FAILED"}:
            root.after(15000, root.destroy)
            return
        root.after(args.poll_ms, refresh)

    refresh()
    root.mainloop()


if __name__ == "__main__":
    main()
