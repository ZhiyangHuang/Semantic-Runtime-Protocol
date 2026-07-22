from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ..ablation.variants import default_runtime_governance_ablation_variants
from ..core import execute_transition, summarize_governance_latencies, summarize_governance_results
from ..reports import write_csv, write_json, write_jsonl, write_markdown
from .attacks import FailureInjectionAttack, build_failure_injection_cases, default_failure_injection_attacks


def run_failure_injection_suite(
    *,
    cases: Iterable[Any] | None = None,
    attacks: Iterable[FailureInjectionAttack] | None = None,
    variants: Iterable[Any] | None = None,
) -> dict[str, Any]:
    selected_cases = list(cases) if cases is not None else build_failure_injection_cases()
    selected_attacks = list(attacks) if attacks is not None else default_failure_injection_attacks()
    selected_variants = list(variants) if variants is not None else default_runtime_governance_ablation_variants()

    records: list[dict[str, Any]] = []
    attack_summaries: dict[str, dict[str, Any]] = {}

    for attack in selected_attacks:
        attack_records: list[dict[str, Any]] = []
        for variant in selected_variants:
            for base_case in selected_cases:
                case = attack.apply(base_case)
                result = execute_transition(case, variant.policy)
                record = {
                    "attack": attack.name,
                    "variant": variant.name,
                    "policy": variant.policy.as_dict(),
                    "case": case.as_dict(),
                    "result": result.as_dict(),
                }
                attack_records.append(record)
                records.append(record)
        attack_summaries[attack.name] = {
            "attack": attack.as_dict(),
            "metrics": summarize_governance_results(attack_records).as_dict(),
            "record_count": len(attack_records),
        }

    combined_metrics = summarize_governance_results(records)
    return {
        "records": records,
        "summary": {
            "record_count": len(records),
            "attack_count": len(selected_attacks),
            "variant_count": len(selected_variants),
            "case_count": len(selected_cases),
            "metrics": combined_metrics.as_dict(),
            "latency": summarize_governance_latencies(records).as_dict(),
            "attacks": attack_summaries,
        },
    }


def _render_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary") or {}
    attacks = summary.get("attacks") or {}
    lines = [
        "# Runtime Governance Failure Injection",
        "",
        "## Summary",
        f"- `record_count`: {summary.get('record_count')}",
        f"- `attack_count`: {summary.get('attack_count')}",
        f"- `variant_count`: {summary.get('variant_count')}",
        f"- `case_count`: {summary.get('case_count')}",
        "",
        "| Attack | Invalid Accept | State Corruption | Authority Escalation | Rollback Success | Verification Delta |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, payload in attacks.items():
        metrics = payload.get("metrics") or {}
        lines.append(
            f"| {name} | {metrics.get('invalid_accept_rate', 0.0):.3f} | {metrics.get('state_corruption_rate', 0.0):.3f} | {metrics.get('authority_escalation_rate', 0.0):.3f} | {metrics.get('rollback_success_rate', 0.0):.3f} | {metrics.get('verification_delta', 0.0):.3f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "The relevant property is containment of invalid transitions, authority escalation, and corruption after reject.",
        ]
    )
    return "\n".join(lines)


def write_failure_injection_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    records = list(report.get("records") or [])
    summary = dict(report.get("summary") or {})
    json_path = write_json(output_path / "failure_injection_report.json", report)
    records_jsonl = write_jsonl(output_path / "failure_injection_records.jsonl", records)
    csv_path = write_csv(output_path / "failure_injection_records.csv", records)
    markdown_path = write_markdown(output_path / "failure_injection_report.md", _render_markdown(report))
    summary_json = write_json(output_path / "failure_injection_summary.json", summary)
    return {
        "failure_injection_report_json": json_path,
        "failure_injection_records_jsonl": records_jsonl,
        "failure_injection_records_csv": csv_path,
        "failure_injection_report_md": markdown_path,
        "failure_injection_summary_json": summary_json,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP failure injection suite.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "runtime_governance" / "failure_injection",
        help="Directory to write failure injection outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_failure_injection_suite()
    outputs = write_failure_injection_outputs(report, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
