from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from .ablation import run_runtime_governance_ablation, write_runtime_governance_ablation_outputs
from .core import summarize_governance_latencies
from .failure_injection import run_failure_injection_suite, write_failure_injection_outputs
from .llm_transition import run_llm_transition_integration, write_llm_transition_outputs
from .reports import write_csv, write_json, write_markdown


def run_runtime_governance_validation() -> dict[str, Any]:
    ablation_report = run_runtime_governance_ablation()
    failure_injection_report = run_failure_injection_suite()
    llm_transition_report = run_llm_transition_integration()
    return {
        "ablation": ablation_report,
        "failure_injection": failure_injection_report,
        "llm_transition": llm_transition_report,
    }


def _render_markdown(report: dict[str, Any]) -> str:
    ablation_summary = (report.get("ablation") or {}).get("summary") or {}
    failure_summary = (report.get("failure_injection") or {}).get("summary") or {}
    llm_summary = (report.get("llm_transition") or {}).get("summary") or {}
    latency_summary = report.get("latency") or {}
    lines = [
        "# Runtime Governance Validation",
        "",
        "## Ablation",
        f"- `record_count`: {ablation_summary.get('record_count')}",
        f"- `variant_count`: {ablation_summary.get('variant_count')}",
        f"- `latency_sample_count`: {(ablation_summary.get('latency') or {}).get('sample_count', 0)}",
        "",
        "## Failure Injection",
        f"- `record_count`: {failure_summary.get('record_count')}",
        f"- `attack_count`: {failure_summary.get('attack_count')}",
        f"- `latency_sample_count`: {(failure_summary.get('latency') or {}).get('sample_count', 0)}",
        "",
        "## LLM Transition",
        f"- `scenario_count`: {llm_summary.get('scenario_count')}",
        f"- `record_count`: {llm_summary.get('record_count')}",
        f"- `proposal_acceptance_rate`: {llm_summary.get('proposal_acceptance_rate', 0.0):.3f}",
        f"- `srp_invalid_accept_rate`: {(llm_summary.get('srp_metrics') or {}).get('invalid_accept_rate', 0.0):.3f}",
        "",
        "## Latency",
        f"- `sample_count`: {latency_summary.get('sample_count', 0)}",
        f"- `mean_total_ms`: {(latency_summary.get('mean_ms') or {}).get('total_ms', 0.0):.3f}",
        "",
        "## Summary",
        "The shared contract keeps ablation and failure injection on the same evaluation surface.",
    ]
    return "\n".join(lines)


def write_runtime_governance_validation_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    ablation_dir = output_path / "ablation"
    failure_dir = output_path / "failure_injection"
    llm_dir = output_path / "llm_transition"
    ablation_outputs = write_runtime_governance_ablation_outputs(report["ablation"], ablation_dir)
    failure_outputs = write_failure_injection_outputs(report["failure_injection"], failure_dir)
    llm_outputs = write_llm_transition_outputs(report["llm_transition"], llm_dir)

    combined_records = (
        list(report["ablation"].get("records") or [])
        + list(report["failure_injection"].get("records") or [])
        + list(report["llm_transition"].get("records") or [])
    )
    latency_summary = summarize_governance_latencies(combined_records).as_dict()
    combined_summary = {
        "ablation": report["ablation"].get("summary") or {},
        "failure_injection": report["failure_injection"].get("summary") or {},
        "llm_transition": report["llm_transition"].get("summary") or {},
        "latency": latency_summary,
    }
    summary_json = write_json(output_path / "governance_summary.json", combined_summary)
    latency_json = write_json(output_path / "runtime_latency_summary.json", latency_summary)
    markdown_path = write_markdown(output_path / "governance_report.md", _render_markdown(report))

    combined_rows = [
        {"section": "ablation", **(report["ablation"].get("summary") or {}).get("metrics", {})},
        {"section": "failure_injection", **(report["failure_injection"].get("summary") or {}).get("metrics", {})},
        {"section": "llm_transition", **(report["llm_transition"].get("summary") or {}).get("srp_metrics", {})},
    ]
    csv_path = write_csv(output_path / "governance_summary.csv", combined_rows)

    output_map: dict[str, Path] = {
        "governance_summary_json": summary_json,
        "runtime_latency_summary_json": latency_json,
        "governance_report_md": markdown_path,
        "governance_summary_csv": csv_path,
    }
    output_map.update(ablation_outputs)
    output_map.update(failure_outputs)
    output_map.update(llm_outputs)
    return output_map


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SRP runtime governance validation suite.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "results" / "runtime_governance",
        help="Directory to write runtime governance outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = run_runtime_governance_validation()
    outputs = write_runtime_governance_validation_outputs(report, args.output_dir)
    print(json.dumps({key: str(value) for key, value in outputs.items()}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
