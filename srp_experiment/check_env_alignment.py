import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
ENV_PATH = ROOT / ".env"
FROZEN_CONFIG_PATH = ROOT / "configs" / "longbench_v2_multimodel_100_1000.json"
MANIFEST_PATH = ROOT / "data" / "longbench_v2" / "manifest.json"


def _normalize_repo_path(value: str) -> str:
    value = value.strip().replace("\\", "/")
    if len(value) >= 2 and value[1] == ":":
        try:
            value = Path(value).resolve().relative_to(REPO_ROOT.resolve()).as_posix()
        except Exception:
            value = Path(value).resolve().as_posix()
    return value


def _read_dotenv(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_task_count(task_file: str) -> int:
    path = (REPO_ROOT / task_file).resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict) and isinstance(data.get("tasks"), list):
        return len(data["tasks"])
    raise ValueError(f"Unsupported task payload shape in {path}")


def _check(name: str, passed: bool, expected, actual, details: str | None = None) -> dict:
    return {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "expected": expected,
        "actual": actual,
        "details": details,
    }


def build_alignment_report() -> dict:
    env_values = _read_dotenv(ENV_PATH)
    checks: list[dict] = []

    if not ENV_PATH.exists():
        checks.append(
            _check(
                ".env file exists",
                False,
                str(ENV_PATH),
                "missing",
                "Create srp_experiment/.env before running formal experiments.",
            )
        )
        return {"status": "NOT_ALIGNED", "checks": checks}

    config = _load_json(FROZEN_CONFIG_PATH)
    manifest = _load_json(MANIFEST_PATH)

    runs = config.get("runs", [])
    expected_methods = runs[0]["methods"][0] if runs else []
    expected_cycles = sorted({int(cycle) for run in runs for cycle in run.get("cycles", [])})
    expected_models = sorted({model for run in runs for model in run.get("models", [])})
    expected_backend = config.get("shared", {}).get("backend")
    expected_runs_dir = config.get("shared", {}).get("output_root")
    expected_batch_config = FROZEN_CONFIG_PATH.relative_to(REPO_ROOT).as_posix()
    expected_manifest_path = f"{expected_runs_dir}/batch_manifest.json"
    expected_task_file = manifest["task_file"]
    expected_selection_limit = int(manifest["selection_limit"])
    expected_imported_count = int(manifest["imported_count"])
    actual_task_count = _load_task_count(expected_task_file)

    checks.append(
        _check(
            "SRP_BATCH_CONFIG",
            _normalize_repo_path(env_values.get("SRP_BATCH_CONFIG", "")) == expected_batch_config,
            expected_batch_config,
            _normalize_repo_path(env_values.get("SRP_BATCH_CONFIG", "")),
        )
    )
    checks.append(
        _check(
            "SRP_BACKEND",
            env_values.get("SRP_BACKEND") == expected_backend,
            expected_backend,
            env_values.get("SRP_BACKEND"),
        )
    )
    checks.append(
        _check(
            "SRP_BATCH_RUNS_DIR",
            _normalize_repo_path(env_values.get("SRP_BATCH_RUNS_DIR", "")) == _normalize_repo_path(expected_runs_dir),
            expected_runs_dir,
            env_values.get("SRP_BATCH_RUNS_DIR"),
        )
    )
    checks.append(
        _check(
            "SRP_BATCH_MANIFEST_PATH",
            _normalize_repo_path(env_values.get("SRP_BATCH_MANIFEST_PATH", "")) == _normalize_repo_path(expected_manifest_path),
            expected_manifest_path,
            env_values.get("SRP_BATCH_MANIFEST_PATH"),
        )
    )
    checks.append(
        _check(
            "SRP_METHODS",
            [item.strip() for item in env_values.get("SRP_METHODS", "").split(",") if item.strip()] == expected_methods,
            ",".join(expected_methods),
            env_values.get("SRP_METHODS"),
        )
    )

    env_cycles = env_values.get("SRP_CYCLES", "")
    try:
        env_cycle_value = int(env_cycles)
        cycle_ok = env_cycle_value in expected_cycles
    except ValueError:
        env_cycle_value = env_cycles
        cycle_ok = False
    checks.append(
        _check(
            "SRP_CYCLES",
            cycle_ok,
            f"one of {expected_cycles}",
            env_cycle_value,
        )
    )
    checks.append(
        _check(
            "SRP_MODEL",
            env_values.get("SRP_MODEL") in expected_models,
            expected_models,
            env_values.get("SRP_MODEL"),
        )
    )
    checks.append(
        _check(
            "LongBench task file",
            Path(REPO_ROOT / expected_task_file).exists(),
            expected_task_file,
            expected_task_file,
        )
    )
    checks.append(
        _check(
            "LongBench frozen selection_limit",
            expected_selection_limit == 300,
            300,
            expected_selection_limit,
        )
    )
    checks.append(
        _check(
            "LongBench imported_count",
            expected_imported_count == 300,
            300,
            expected_imported_count,
        )
    )
    checks.append(
        _check(
            "LongBench tasks.json row count",
            actual_task_count == expected_imported_count,
            expected_imported_count,
            actual_task_count,
        )
    )

    override_warnings = []
    tracked = [
        "SRP_BACKEND",
        "SRP_MODEL",
        "SRP_CYCLES",
        "SRP_METHODS",
        "SRP_BATCH_CONFIG",
        "SRP_BATCH_RUNS_DIR",
    ]
    for key in tracked:
        current = os.getenv(key)
        file_value = env_values.get(key)
        if current and file_value and current != file_value:
            override_warnings.append(
                {
                    "key": key,
                    "env_file": file_value,
                    "process_env": current,
                }
            )

    status = "ALIGNED" if all(item["status"] == "PASS" for item in checks) else "NOT_ALIGNED"
    return {
        "status": status,
        "env_path": str(ENV_PATH),
        "frozen_config_path": str(FROZEN_CONFIG_PATH),
        "manifest_path": str(MANIFEST_PATH),
        "checks": checks,
        "warnings": override_warnings,
    }


def print_report(report: dict) -> None:
    print(f"Env alignment status: {report['status']}")
    for item in report["checks"]:
        print(f"[{item['status']}] {item['name']}")
        print(f"  expected: {item['expected']}")
        print(f"  actual:   {item['actual']}")
        if item.get("details"):
            print(f"  details:  {item['details']}")
    if report.get("warnings"):
        print("Warnings:")
        for warning in report["warnings"]:
            print(
                f"  - process env overrides {warning['key']}: "
                f".env={warning['env_file']} | process={warning['process_env']}"
            )


def enforce_alignment() -> dict:
    report = build_alignment_report()
    print_report(report)
    if report["status"] != "ALIGNED":
        raise SystemExit("Startup blocked: srp_experiment/.env is not aligned with the frozen LongBench v2 config.")
    return report


def main() -> None:
    enforce_alignment()


if __name__ == "__main__":
    main()
