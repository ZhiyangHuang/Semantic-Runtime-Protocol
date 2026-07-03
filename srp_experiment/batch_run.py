import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
from typing import Dict, List

from env_utils import load_env_file

ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = ROOT / "configs" / "default_batch.json"
RESULTS_DIR = ROOT / "results"

load_env_file()


def parse_args():
    parser = argparse.ArgumentParser(description="Run batched SRP experiments from a JSON config.")
    parser.add_argument("--config", default=os.getenv("SRP_BATCH_CONFIG", str(DEFAULT_CONFIG)))
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--manifest-path", default=os.getenv("SRP_BATCH_MANIFEST_PATH", str(RESULTS_DIR / "batch_manifest.json")))
    return parser.parse_args()


def resolve_config_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    if path.parts and path.parts[0] in {"srp_experiment", "first_paper", "docs"}:
        return (ROOT.parent / path).resolve()
    candidate = ROOT.parent / path
    if candidate.exists():
        return candidate
    return (ROOT / path).resolve()


def load_config(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_method_sets(value) -> List[List[str]]:
    if not value:
        return [["raw_prompt", "summarization", "rag", "srp"]]
    if isinstance(value[0], str):
        return [list(value)]
    return [list(methods) for methods in value]


def slugify(value: str) -> str:
    cleaned = []
    for char in value:
        if char.isalnum():
            cleaned.append(char.lower())
        elif char in {"-", "_"}:
            cleaned.append(char)
        else:
            cleaned.append("_")
    slug = "".join(cleaned).strip("_")
    return slug or "run"


def build_command(
    run_experiment: Path,
    backend: str,
    model: str,
    cycles: int,
    methods: List[str],
    output_dir: Path,
    task_file: str | None = None,
    task_source: str | None = None,
    repeat_id: int | None = None,
) -> List[str]:
    command = [
        sys.executable,
        str(run_experiment),
        "--backend",
        backend,
        "--model",
        model,
        "--cycles",
        str(cycles),
        "--output-dir",
        str(output_dir),
        "--methods",
    ]
    command.extend(methods)
    if task_file:
        command.extend(["--task-file", task_file])
    elif task_source:
        command.extend(["--task-source", task_source])
    if repeat_id is not None:
        command.extend(["--repeat-id", str(repeat_id)])
    return command


def expand_runs(config: Dict, config_path: Path) -> List[Dict]:
    shared = config.get("shared", {})
    backend = shared.get("backend", "mock")
    task_file = shared.get("task_file")
    task_source = shared.get("task_source")
    output_root_value = shared.get("output_root", "srp_experiment/results/batch_runs")
    output_root_path = Path(output_root_value)
    if output_root_path.is_absolute():
        output_root = output_root_path
    else:
        repo_relative = ROOT.parent / output_root_path
        config_relative = config_path.parent / output_root_path
        output_root = repo_relative if "srp_experiment" in output_root_value or repo_relative.exists() else config_relative
    expanded = []
    for run in config.get("runs", []):
        run_name = run.get("name", "unnamed_run")
        models = run.get("models", [shared.get("model", "gpt-4o-mini")])
        cycles_list = run.get("cycles", [5])
        method_sets = normalize_method_sets(run.get("methods"))
        run_backend = run.get("backend", backend)
        repeats = int(run.get("repeats", shared.get("repeats", 1)))
        for model, cycles, methods in product(models, cycles_list, method_sets):
            method_slug = "-".join(slugify(method) for method in methods)
            for repeat_id in range(1, repeats + 1):
                repeat_suffix = f"__r{repeat_id:02d}" if repeats > 1 else ""
                folder_name = f"{slugify(run_name)}__{slugify(run_backend)}__{slugify(model)}__c{cycles}__{method_slug}{repeat_suffix}"
                expanded.append(
                    {
                        "name": run_name,
                        "backend": run_backend,
                        "model": model,
                        "cycles": cycles,
                        "methods": methods,
                        "task_file": task_file,
                        "task_source": task_source,
                        "repeat_id": repeat_id,
                        "repeats": repeats,
                        "output_dir": output_root / folder_name,
                    }
                )
    return expanded


def main():
    args = parse_args()
    config_path = resolve_config_path(args.config)
    config = load_config(config_path)
    run_experiment = ROOT / "run_experiment.py"
    expanded = expand_runs(config, config_path)
    manifest = []
    failures = []
    manifest_path = resolve_config_path(args.manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path = manifest_path.with_name(f"{manifest_path.stem}_progress.json")

    def write_progress(status: str, current_run: Dict | None = None):
        completed_runs = len(manifest)
        payload = {
            "status": status,
            "config": str(config_path),
            "manifest_path": str(manifest_path),
            "total_runs": len(expanded),
            "completed_runs": completed_runs,
            "failed_runs": len(failures),
            "remaining_runs": max(len(expanded) - completed_runs, 0),
            "started_at": started_at,
            "updated_at": now_iso(),
            "current_run": current_run,
            "last_completed_run": manifest[-1] if manifest else None,
        }
        progress_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"[Batch] Loaded config: {config_path}")
    print(f"[Batch] Planned runs: {len(expanded)}")
    started_at = now_iso()
    write_progress("RUNNING")

    for index, run in enumerate(expanded, start=1):
        output_dir = run["output_dir"]
        output_dir.mkdir(parents=True, exist_ok=True)
        run_started_at = now_iso()
        current_run = {
            "index": index,
            "name": run["name"],
            "backend": run["backend"],
            "model": run["model"],
            "cycles": run["cycles"],
            "methods": run["methods"],
            "repeat_id": run.get("repeat_id"),
            "output_dir": str(output_dir),
        }
        write_progress("RUNNING", current_run=current_run)
        command = build_command(
            run_experiment=run_experiment,
            backend=run["backend"],
            model=run["model"],
            cycles=run["cycles"],
            methods=run["methods"],
            output_dir=output_dir,
            task_file=run.get("task_file"),
            task_source=run.get("task_source"),
            repeat_id=run.get("repeat_id"),
        )
        print(f"[Batch] ({index}/{len(expanded)}) {run['name']} -> {output_dir.name}")
        completed = subprocess.run(command, cwd=ROOT.parent, capture_output=True, text=True)
        record = {
            "name": run["name"],
            "backend": run["backend"],
            "model": run["model"],
            "cycles": run["cycles"],
            "methods": run["methods"],
            "task_file": run.get("task_file"),
            "task_source": run.get("task_source"),
            "repeat_id": run.get("repeat_id"),
            "repeats": run.get("repeats"),
            "output_dir": str(output_dir),
            "returncode": completed.returncode,
            "started_at": run_started_at,
            "completed_at": now_iso(),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        manifest.append(record)
        write_progress("RUNNING", current_run=current_run)
        if completed.returncode != 0:
            failures.append(record)
            print(f"[Batch] Failed: {output_dir.name}")
            if args.fail_fast:
                break
        else:
            print(f"[Batch] Completed: {output_dir.name}")

    final_status = "FAILED" if failures else "COMPLETED"
    write_progress(final_status)
    print(f"[Batch] Wrote manifest to {manifest_path}")

    if failures:
        print(f"[Batch] Failed runs: {len(failures)}")
        raise SystemExit(1)

    print("[Batch] All runs completed successfully.")


if __name__ == "__main__":
    main()
