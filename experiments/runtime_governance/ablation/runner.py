from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ..core import (
    GovernanceMetrics,
    execute_transition,
    summarize_governance_latencies,
    summarize_governance_results,
)
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from .variants import (
    RuntimeGovernanceAblationVariant,
    build_runtime_governance_ablation_cases,
    default_runtime_governance_ablation_variants,
)


def run_runtime_governance_ablation(
    *,
    cases: Iterable[Any] | None = None,
    variants: Iterable[RuntimeGovernanceAblationVariant] | None = None,
) -> dict[str, Any]:
    selected_cases = list(cases) if cases is not None else build_runtime_governance_ablation_cases()
    selected_variants = list(variants) if variants is not None else default_runtime_governance_ablation_variants()

    records: list[dict[str, Any]] = []
    variant_summaries: dict[str, dict[str, Any]] = {}

    for variant in selected_variants:
        variant_records: list[dict[str, Any]] = []
        for case in selected_cases:
            result = execute_transition(case, variant.policy)
            record = {
                "variant": variant.name,
                "policy": variant.policy.as_dict(),
                "case": case.as_dict(),
                "result": result.as_dict(),
            }
            variant_records.append(record)
            records.append(record)
        variant_metrics = summarize_governance_results(variant_records)
        variant_summaries[variant.name] = {
            "variant": variant.as_dict(),
            "metrics": variant_metrics.as_dict(),
            "record_count": len(variant_records),
        }

    combined_metrics = summarize_governance_results(records)
    combined_latency = summarize_governance_latencies(records)
    return {
        "contract": {
            "case_schema": "transition_case.v1",
            "result_schema": "governance_result.v1",
        },
        "records": records,
        "summary": {
            "record_count": len(records),
            "case_count": len(selected_cases),
            "variant_count": len(selected_variants),
            "metrics": combined_metrics.as_dict(),
            "latency": combined_latency.as_dict(),
            "variants": variant_summaries,
        },
    }


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    variants = summary.get("variants") or {}
    lines = [
        "# Runtime Governance Ablation",
        "",
        "## Summary",
        f"- `record_count`: {summary.get('record_count')}",
        f"- `case_count`: {summary.get('case_count')}",
        f"- `variant_count`: {summary.get('variant_count')}",
        "",
        "| Variant | Invalid Accept | State Corruption | Authority Escalation | Rollback Success | Verification Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, payload in variants.items():
        metrics = payload.get("metrics") or {}
        lines.append(
            f"| {name} | {metrics.get('invalid_accept_rate', 0.0):.3f} | {metrics.get('state_corruption_rate', 0.0):.3f} | {metrics.get('authority_escalation_rate', 0.0):.3f} | {metrics.get('rollback_success_rate', 0.0):.3f} | {metrics.get('verification_delta', 0.0):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "Full SRP should keep invalid acceptance, state corruption, and authority escalation at zero in the evaluated contract.",
            "",
            "## Latency",
            f"- `sample_count`: {(summary.get('latency') or {}).get('sample_count', 0)}",
        ]
    )
    return "\n".join(lines)


def write_runtime_governance_ablation_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    records = list(report.get("records") or [])
    summary = dict(report.get("summary") or {})
    json_path = write_json(output_path / "ablation_report.json", report)
    records_jsonl = write_jsonl(output_path / "ablation_records.jsonl", records)
    csv_path = write_csv(output_path / "ablation_records.csv", records)
    markdown_path = write_markdown(output_path / "ablation_report.md", _render_markdown(report))
    summary_json = write_json(output_path / "ablation_summary.json", summary)
    return {
        "ablation_report_json": json_path,
        "ablation_records_jsonl": records_jsonl,
        "ablation_records_csv": csv_path,
        "ablation_report_md": markdown_path,
        "ablation_summary_json": summary_json,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP runtime governance ablation study.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "runtime_governance" / "ablation",
        help="Directory to write ablation outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_runtime_governance_ablation()
    outputs = write_runtime_governance_ablation_outputs(report, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
