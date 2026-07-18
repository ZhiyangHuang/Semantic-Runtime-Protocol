from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .controlled_harness import run_controlled_harness, summarize_controlled_records, write_controlled_outputs
from .object_aware_compression_harness import (
    run_object_aware_compression,
    summarize_object_aware_compression,
    write_object_aware_compression_outputs,
)
from .reconstruction_policy_harness import (
    run_reconstruction_policy_comparison,
    summarize_reconstruction_policy_comparison,
    write_reconstruction_policy_outputs,
)
from .recovery_ablation_harness import (
    run_recovery_ablation,
    summarize_recovery_ablation,
    write_recovery_ablation_outputs,
)


HARNESS_RUNNERS: Dict[str, Dict[str, Any]] = {
    "controlled": {
        "runner": run_controlled_harness,
        "summarizer": summarize_controlled_records,
        "writer": write_controlled_outputs,
    },
    "recovery": {
        "runner": run_recovery_ablation,
        "summarizer": summarize_recovery_ablation,
        "writer": write_recovery_ablation_outputs,
    },
    "reconstruction": {
        "runner": run_reconstruction_policy_comparison,
        "summarizer": summarize_reconstruction_policy_comparison,
        "writer": write_reconstruction_policy_outputs,
    },
    "object_aware_compression": {
        "runner": run_object_aware_compression,
        "summarizer": summarize_object_aware_compression,
        "writer": write_object_aware_compression_outputs,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the fixed SRP harness suite bundle.")
    parser.add_argument(
        "--harness",
        action="append",
        choices=["all", *HARNESS_RUNNERS.keys()],
        default=[],
        help="Harness to run. Repeatable. Defaults to all harnesses.",
    )
    parser.add_argument("--cycles", type=int, default=1, help="Cycles per task.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "srp_experiment" / "tmp" / "fixed_harnesses",
        help="Directory for the per-harness outputs and manifest.",
    )
    parser.add_argument("--no-write", action="store_true", help="Run without writing output files.")
    return parser.parse_args()


def _select_harnesses(requested: list[str]) -> list[str]:
    if not requested:
        return list(HARNESS_RUNNERS.keys())
    normalized = {str(item).strip() for item in requested if str(item).strip()}
    if not normalized or "all" in normalized:
        return list(HARNESS_RUNNERS.keys())
    missing = normalized - set(HARNESS_RUNNERS.keys())
    if missing:
        raise ValueError(f"Unknown harness(es): {', '.join(sorted(missing))}")
    return [name for name in HARNESS_RUNNERS.keys() if name in normalized]


def run_fixed_harness_bundle(harnesses: list[str] | None = None, *, cycles: int = 1) -> Dict[str, Any]:
    requested = _select_harnesses(harnesses or [])
    bundle: Dict[str, Any] = {"cycles": cycles, "harnesses": {}}
    for harness_name in requested:
        runner = HARNESS_RUNNERS[harness_name]["runner"]
        summarizer = HARNESS_RUNNERS[harness_name]["summarizer"]
        records = runner(cycles=cycles)
        bundle["harnesses"][harness_name] = {
            "records": records,
            "summary": summarizer(records),
        }
    return bundle


def write_fixed_harness_bundle_outputs(bundle: Dict[str, Any], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    manifest_path = output_path / "fixed_harness_bundle_manifest.json"
    manifest: Dict[str, Any] = {"cycles": bundle.get("cycles"), "harnesses": {}}
    for harness_name, harness_bundle in (bundle.get("harnesses") or {}).items():
        harness_output_dir = output_path / harness_name
        writer = HARNESS_RUNNERS[harness_name]["writer"]
        outputs = writer(harness_bundle.get("records") or [], harness_output_dir)
        manifest["harnesses"][harness_name] = {
            "summary": harness_bundle.get("summary"),
            "outputs": {key: str(value) for key, value in outputs.items()},
        }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"manifest": manifest_path}


def main() -> int:
    args = parse_args()
    harnesses = args.harness or ["all"]
    bundle = run_fixed_harness_bundle(harnesses, cycles=args.cycles)
    if not args.no_write:
        outputs = write_fixed_harness_bundle_outputs(bundle, args.output_dir)
        bundle["outputs"] = {key: str(value) for key, value in outputs.items()}
    print(json.dumps(bundle, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

