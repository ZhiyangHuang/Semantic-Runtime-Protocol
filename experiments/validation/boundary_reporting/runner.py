from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .evaluator import evaluate_cases
from .adapters import resolve_adapter
from .generator import case_fingerprint, load_cases_from_jsonl
from .reporter import generate_report
from .schemas import BoundaryReportMetadata


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate reproducible SRP governance boundary reports."
    )
    parser.add_argument("--cases", type=Path, required=True, help="Input case bundle.")
    parser.add_argument("--output", type=Path, required=True, help="Output directory for the report.")
    parser.add_argument("--adapter", type=str, default="fixture", help="Input adapter name.")
    parser.add_argument("--contract", type=str, required=True, help="Runtime contract identifier.")
    parser.add_argument(
        "--contract-version",
        type=str,
        default="boundary-v1",
        help="Version of the governance contract family.",
    )
    parser.add_argument(
        "--schema-version",
        type=str,
        default="1.0",
        help="Boundary report schema version.",
    )
    parser.add_argument(
        "--evaluator-version",
        type=str,
        default="0.1",
        help="Boundary evaluator version.",
    )
    parser.add_argument("--seed", type=int, default=0, help="Reproducibility seed.")
    parser.add_argument(
        "--generated-at",
        type=str,
        default="2026-07-19T00:00:00Z",
        help="Deterministic generation timestamp for the artifact bundle.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_cases = load_cases_from_jsonl(args.cases)
    adapter = resolve_adapter(args.adapter)
    cases = adapter(raw_cases, args.contract)
    decisions = evaluate_cases(cases)
    replay_decisions = evaluate_cases(cases)

    replay_consistency = 1.0 if [d.as_dict() for d in decisions] == [d.as_dict() for d in replay_decisions] else 0.0

    metadata = BoundaryReportMetadata(
        version="boundary-report-v0",
        contract_version=args.contract_version,
        schema_version=args.schema_version,
        evaluator_version=args.evaluator_version,
        adapter_name=args.adapter,
        runtime_contract=args.contract,
        seed=args.seed,
        generated_at=args.generated_at,
    )

    result = generate_report(
        cases=cases,
        decisions=decisions,
        output_dir=args.output,
        metadata=metadata,
        replay_consistency=replay_consistency,
    )

    manifest = {
        "adapter_name": args.adapter,
        "contract_version": args.contract_version,
        "schema_version": args.schema_version,
        "evaluator_version": args.evaluator_version,
        "case_count": len(cases),
        "decision_count": len(decisions),
        "replay_consistency": replay_consistency,
        "case_input_hash": case_fingerprint(cases),
        "decision_hash": result["decision_hash"],
        "report_hash": result["report_hash"],
    }
    (Path(result["output_dir"]) / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
