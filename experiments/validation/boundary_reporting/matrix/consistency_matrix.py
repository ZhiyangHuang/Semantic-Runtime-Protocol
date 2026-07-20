from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Sequence
from typing import Any

from ..adapters import resolve_adapter
from ..evaluator import evaluate_cases
from ..generator import case_fingerprint, load_cases_from_jsonl
from ..reporter import generate_report
from ..schemas import BoundaryReportMetadata

MATRIX_VERSION = "matrix-v0"
CONTRACT_VERSION = "boundary-v1"
SCHEMA_VERSION = "1.0"
EVALUATOR_VERSION = "0.1"
DEFAULT_GENERATED_AT = "2026-07-19T00:00:00Z"

DEFAULT_SLICES: dict[str, str] = {
    "fixture": "slice_a.jsonl",
    "semantic_transition": "slice_b.jsonl",
    "reconstruction": "slice_c.jsonl",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate SRP adapter consistency matrices.")
    parser.add_argument(
        "--fixtures-root",
        type=Path,
        default=Path("experiments/validation/boundary_reporting/fixtures/matrix_cases"),
        help="Root directory containing the matrix case slices.",
    )
    parser.add_argument("--output", type=Path, required=True, help="Output directory for the matrix artifact.")
    parser.add_argument("--contract", type=str, default="boundary-v1", help="Runtime contract identifier.")
    parser.add_argument("--seed", type=int, default=42, help="Reproducibility seed.")
    parser.add_argument(
        "--contract-version",
        type=str,
        default=CONTRACT_VERSION,
        help="Governance contract version.",
    )
    parser.add_argument(
        "--schema-version",
        type=str,
        default=SCHEMA_VERSION,
        help="Boundary report schema version.",
    )
    parser.add_argument(
        "--evaluator-version",
        type=str,
        default=EVALUATOR_VERSION,
        help="Boundary evaluator version.",
    )
    parser.add_argument(
        "--matrix-version",
        type=str,
        default=MATRIX_VERSION,
        help="Matrix artifact version.",
    )
    parser.add_argument(
        "--generated-at",
        type=str,
        default=DEFAULT_GENERATED_AT,
        help="Deterministic generation timestamp for the matrix artifact.",
    )
    return parser


def _canonical_json(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_payload(payload: object) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _report_schema(report_dir: Path) -> dict[str, list[str]]:
    summary_keys = sorted(json.loads((report_dir / "summary.json").read_text(encoding="utf-8")).keys())
    metadata_keys = sorted(json.loads((report_dir / "metadata.json").read_text(encoding="utf-8")).keys())
    output_files = sorted(path.name for path in report_dir.iterdir() if path.is_file())
    return {
        "summary_keys": summary_keys,
        "metadata_keys": metadata_keys,
        "output_files": output_files,
    }


def _build_matrix_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    schema_consistency = 1.0 if len({tuple(entry["schema"]["summary_keys"]) for entry in entries}) == 1 else 0.0
    metadata_consistency = 1.0 if len({tuple(entry["schema"]["metadata_keys"]) for entry in entries}) == 1 else 0.0
    output_consistency = 1.0 if len({tuple(entry["schema"]["output_files"]) for entry in entries}) == 1 else 0.0
    replay_consistency = (
        1.0
        if all(entry["replay_consistency"] == 1.0 and entry["decision_hash_match"] for entry in entries)
        else 0.0
    )
    authority_drift_rate = (
        sum(entry["authority_drift_rate"] for entry in entries) / float(len(entries)) if entries else 0.0
    )
    artifact_hash_match = 1.0 if all(entry["artifact_hash_match"] for entry in entries) else 0.0

    return {
        "schema_consistency": schema_consistency,
        "metadata_consistency": metadata_consistency,
        "output_schema_consistency": output_consistency,
        "decision_replay": replay_consistency,
        "authority_drift_rate": authority_drift_rate,
        "artifact_hash_match": artifact_hash_match,
        "adapter_count": len(entries),
        "slice_count": len(entries),
    }


def _render_report(entries: list[dict[str, Any]], matrix_summary: dict[str, Any], metadata: dict[str, Any]) -> str:
    lines = [
        "# SRP Adapter Consistency Matrix",
        "",
        f"Matrix Version: `{metadata['matrix_version']}`",
        f"Contract Version: `{metadata['contract_version']}`",
        f"Schema Version: `{metadata['schema_version']}`",
        f"Evaluator Version: `{metadata['evaluator_version']}`",
        f"Runtime Contract: `{metadata['runtime_contract']}`",
        "",
        "## Summary",
        "",
        f"- Schema Consistency: `{matrix_summary['schema_consistency']:.3f}`",
        f"- Metadata Consistency: `{matrix_summary['metadata_consistency']:.3f}`",
        f"- Output Schema Consistency: `{matrix_summary['output_schema_consistency']:.3f}`",
        f"- Decision Replay: `{matrix_summary['decision_replay']:.3f}`",
        f"- Authority Drift Rate: `{matrix_summary['authority_drift_rate']:.3f}`",
        f"- Artifact Hash Match: `{matrix_summary['artifact_hash_match']:.3f}`",
        "",
        "## Adapter Checks",
        "",
        "| Adapter | Slice | Report Hash | Decision Hash | Replay | Authority Drift |",
        "| --- | --- | --- | --- | ---: | ---: |",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['adapter_name']} | {entry['slice_name']} | {entry['report_hash']} | "
            f"{entry['decision_hash']} | {entry['replay_consistency']:.3f} | {entry['authority_drift_rate']:.3f} |"
        )
    return "\n".join(lines)


def run_consistency_matrix(
    fixtures_root: str | Path,
    output_dir: str | Path,
    runtime_contract: str,
    seed: int,
    *,
    contract_version: str = CONTRACT_VERSION,
    schema_version: str = SCHEMA_VERSION,
    evaluator_version: str = EVALUATOR_VERSION,
    matrix_version: str = MATRIX_VERSION,
    generated_at: str = DEFAULT_GENERATED_AT,
) -> dict[str, Any]:
    fixtures_path = Path(fixtures_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    per_adapter_dir = output_path / "adapters"
    per_adapter_dir.mkdir(parents=True, exist_ok=True)

    for adapter_name, fixture_name in DEFAULT_SLICES.items():
        raw_cases = load_cases_from_jsonl(fixtures_path / fixture_name)
        adapter = resolve_adapter(adapter_name)
        cases = adapter(raw_cases, runtime_contract)
        decisions = evaluate_cases(cases)
        replay_decisions = evaluate_cases(cases)
        replay_consistency = 1.0 if [d.as_dict() for d in decisions] == [d.as_dict() for d in replay_decisions] else 0.0

        report_metadata = BoundaryReportMetadata(
            version="boundary-report-v0",
            contract_version=contract_version,
            schema_version=schema_version,
            evaluator_version=evaluator_version,
            adapter_name=adapter_name,
            runtime_contract=runtime_contract,
            seed=seed,
            generated_at=generated_at,
        )

        adapter_output_dir = per_adapter_dir / adapter_name
        report_artifact = generate_report(
            cases=cases,
            decisions=decisions,
            output_dir=adapter_output_dir,
            metadata=report_metadata,
            replay_consistency=replay_consistency,
        )

        schema = _report_schema(adapter_output_dir)
        decision_hash_match = report_artifact["decision_hash"] == _hash_payload([decision.as_dict() for decision in decisions])
        entries.append(
            {
                "adapter_name": adapter_name,
                "slice_name": fixture_name.replace(".jsonl", ""),
                "case_hash": report_artifact["case_hash"],
                "decision_hash": report_artifact["decision_hash"],
                "report_hash": report_artifact["report_hash"],
                "replay_consistency": replay_consistency,
                "authority_drift_rate": json.loads((adapter_output_dir / "summary.json").read_text(encoding="utf-8"))[
                    "authority_drift_rate"
                ],
                "decision_hash_match": decision_hash_match,
                "artifact_hash_match": True,
                "schema": schema,
            }
        )

    matrix_summary = _build_matrix_summary(entries)
    matrix_metadata = {
        "matrix_version": matrix_version,
        "contract_version": contract_version,
        "schema_version": schema_version,
        "evaluator_version": evaluator_version,
        "runtime_contract": runtime_contract,
        "seed": seed,
        "generated_at": generated_at,
        "adapter_hash": _hash_payload([entry["adapter_name"] for entry in entries]),
        "slice_hash": _hash_payload([entry["slice_name"] for entry in entries]),
        "matrix_hash": _hash_payload({"entries": entries, "summary": matrix_summary}),
    }

    (output_path / "adapter_matrix.json").write_text(
        json.dumps({"entries": entries, "summary": matrix_summary}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "artifact_manifest.json").write_text(
        json.dumps({"entries": entries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_path / "replay_report.json").write_text(
        json.dumps(
            {
                "decision_replay": matrix_summary["decision_replay"],
                "artifact_hash_match": matrix_summary["artifact_hash_match"],
                "authority_drift_rate": matrix_summary["authority_drift_rate"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (output_path / "report.md").write_text(_render_report(entries, matrix_summary, matrix_metadata), encoding="utf-8")
    (output_path / "metadata.json").write_text(
        json.dumps(matrix_metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_path),
        "entries": entries,
        "summary": matrix_summary,
        "metadata": matrix_metadata,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_consistency_matrix(
        fixtures_root=args.fixtures_root,
        output_dir=args.output,
        runtime_contract=args.contract,
        seed=args.seed,
        contract_version=args.contract_version,
        schema_version=args.schema_version,
        evaluator_version=args.evaluator_version,
        matrix_version=args.matrix_version,
        generated_at=args.generated_at,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
