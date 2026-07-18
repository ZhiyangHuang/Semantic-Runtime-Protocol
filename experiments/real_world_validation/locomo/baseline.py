from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.real_world_validation.common import (
    aggregate_governance_metrics,
    aggregate_task_metrics,
    aggregate_transition_metrics,
    build_failure_cases,
    build_metadata,
)

from .runner import build_locomo_validation_run


@dataclass(frozen=True)
class LocomoBaselineComparisonRun:
    metadata: dict[str, Any]
    summary: dict[str, Any] = field(default_factory=dict)
    srp_transition_records: tuple[dict[str, Any], ...] = ()
    baseline_transition_records: tuple[dict[str, Any], ...] = ()
    srp_metrics: dict[str, Any] = field(default_factory=dict)
    baseline_metrics: dict[str, Any] = field(default_factory=dict)
    srp_failure_cases: tuple[dict[str, Any], ...] = ()
    baseline_failure_cases: tuple[dict[str, Any], ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _safe_run_stamp(generated_at: str) -> str:
    return (
        generated_at.replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("+", "")
        .replace("Z", "")
    )


def _direct_mutation_record(record: dict[str, Any]) -> dict[str, Any]:
    expected = str(record.get("expected", "reject"))
    actual = "accept"
    failure = expected == "reject" and actual == "accept"
    task_accuracy = 0.0 if failure else 1.0
    return {
        "case_id": record.get("case_id", ""),
        "event": record.get("event", ""),
        "expected": expected,
        "actual": actual,
        "failure": failure,
        "failure_type": "authority_boundary_failure" if failure else None,
        "interpretation": (
            "direct mutation accepted the candidate without a governance boundary"
            if failure
            else "direct mutation accepted the candidate"
        ),
        "accepted": True,
        "authority_changed": False,
        "recommendation_execution_separated": False,
        "replay_consistency": 1.0,
        "evidence_improvement": 0.0,
        "memory_accuracy": task_accuracy,
        "relation_accuracy": task_accuracy,
        "fact_accuracy": task_accuracy,
        "coverage": 1.0,
        "sample_id": record.get("sample_id", ""),
        "qa_index": record.get("qa_index", -1),
        "source_turn_ids": list(record.get("source_turn_ids", [])),
        "raw_context": list(record.get("raw_context", [])),
        "selection_reason": record.get("selection_reason", ""),
        "extraction_method": "direct_mutation_baseline_v1",
    }


def _render_report(comparison: LocomoBaselineComparisonRun) -> str:
    srp_summary = comparison.srp_metrics["transition_metrics"]
    srp_governance = comparison.srp_metrics["governance_metrics"]
    srp_task = comparison.srp_metrics["task_metrics"]
    baseline_summary = comparison.baseline_metrics["transition_metrics"]
    baseline_governance = comparison.baseline_metrics["governance_metrics"]
    baseline_task = comparison.baseline_metrics["task_metrics"]
    summary = comparison.summary
    lines = [
        "# LoCoMo Baseline Comparison Report",
        "",
        "This report compares the SRP governed transition path against a direct-mutation baseline on the same selected LoCoMo slice.",
        "It is a mechanism-comparison report, not a leaderboard report.",
        "",
        "## 1. Purpose",
        "",
        "The comparison asks whether governance boundaries prevent unsupported semantic mutations from being committed.",
        "The baseline deliberately omits the SRP validation gate so the difference in mechanism is visible on the same slice.",
        "",
        "## 2. Compared Mechanisms",
        "",
        "| Mechanism | Pipeline | Governing gate | Rejection path |",
        "| --- | --- | --- | --- |",
        "| SRP | observation -> candidate transition -> evidence validation -> governance -> commit | yes | yes |",
        "| Direct mutation baseline | observation -> immediate update -> commit | no | no |",
        "",
        "## 3. Shared Evaluation Slice",
        "",
        f"- dataset: `{summary.get('dataset', 'LoCoMo')}`",
        f"- source: `{summary.get('source', '')}`",
        f"- selected sample id: `{summary.get('sample_id', '')}`",
        f"- selected events: `{summary.get('selected_events', 0)}`",
        f"- selection policy: `{summary.get('selection_rule', '')}`",
        "",
        "The same three transition records are evaluated under both mechanisms.",
        "",
        "## 4. Metric Comparison",
        "",
        "| Metric | SRP | Direct Mutation | Delta (Baseline - SRP) |",
        "| --- | ---: | ---: | ---: |",
        f"| accepted transitions | `{srp_summary.get('accepted_transitions', 0)}` | `{baseline_summary.get('accepted_transitions', 0)}` | `{summary.get('accepted_delta', 0)}` |",
        f"| rejected transitions | `{srp_summary.get('rejected_transitions', 0)}` | `{baseline_summary.get('rejected_transitions', 0)}` | `{summary.get('rejected_delta', 0)}` |",
        f"| invalid accept rate | `{srp_summary.get('invalid_accept_rate', 0.0)}` | `{baseline_summary.get('invalid_accept_rate', 0.0)}` | `{summary.get('invalid_accept_rate_delta', 0.0)}` |",
        f"| unsupported mutation accepted | `{summary.get('srp_unsupported_mutation_accepted', False)}` | `{summary.get('baseline_unsupported_mutation_accepted', False)}` | `{summary.get('unsupported_mutation_acceptance_delta', 0.0)}` |",
        f"| recommendation/execution separated | `{srp_governance.get('recommendation_execution_separated', True)}` | `{baseline_governance.get('recommendation_execution_separated', False)}` | `{summary.get('recommendation_execution_gap', 0)}` |",
        f"| replay consistency | `{srp_governance.get('replay_consistency', 1.0)}` | `{baseline_governance.get('replay_consistency', 1.0)}` | `{summary.get('replay_consistency_delta', 0.0)}` |",
        f"| memory accuracy | `{srp_task.get('memory_accuracy', 0.0)}` | `{baseline_task.get('memory_accuracy', 0.0)}` | `{summary.get('memory_accuracy_delta', 0.0)}` |",
        f"| relation accuracy | `{srp_task.get('relation_accuracy', 0.0)}` | `{baseline_task.get('relation_accuracy', 0.0)}` | `{summary.get('relation_accuracy_delta', 0.0)}` |",
        f"| fact accuracy | `{srp_task.get('fact_accuracy', 0.0)}` | `{baseline_task.get('fact_accuracy', 0.0)}` | `{summary.get('fact_accuracy_delta', 0.0)}` |",
        "",
        "## 5. Case Table",
        "",
        "| Sample | QA | Event | SRP Expected | SRP Actual | Baseline Actual | Result |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for record in comparison.srp_transition_records:
        baseline_record = next(
            item for item in comparison.baseline_transition_records if item.get("case_id") == record.get("case_id")
        )
        result = "pass" if record.get("actual") == record.get("expected") else "fail"
        lines.append(
            f"| `{record.get('sample_id', '')}` | `{record.get('qa_index', -1)}` | `{record.get('event', '')}` | "
            f"`{record.get('expected', '')}` | `{record.get('actual', '')}` | `{baseline_record.get('actual', '')}` | `{result}` |"
        )
    lines.extend(
        [
            "",
            "## 6. Interpretation",
            "",
            "- SRP rejects the unsupported mutation while preserving the governed boundary.",
            "- The direct-mutation baseline accepts the unsupported mutation because it has no rejection gate.",
            "- The comparison therefore attributes the error to mechanism design, not to scoring noise.",
            "",
            "## 7. Relation to the Paper",
            "",
            "This comparison supports the claim that governed transition control can block unsupported semantic updates.",
            "It is a small comparative experiment, not a leaderboard result.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def build_locomo_baseline_comparison_run(data_root: str | Path | None = None) -> LocomoBaselineComparisonRun:
    repo_root = Path(__file__).resolve().parents[3]
    srp_run = build_locomo_validation_run(data_root=data_root)

    srp_records = [dict(record) for record in srp_run.transition_records]
    baseline_records = [_direct_mutation_record(record) for record in srp_records]

    srp_transition_metrics = aggregate_transition_metrics(srp_records)
    srp_governance_metrics = aggregate_governance_metrics(srp_records)
    srp_task_metrics = aggregate_task_metrics(srp_records)

    baseline_transition_metrics = aggregate_transition_metrics(baseline_records)
    baseline_governance_metrics = aggregate_governance_metrics(baseline_records)
    baseline_task_metrics = aggregate_task_metrics(baseline_records)

    srp_summary = {
        "accepted_transitions": srp_transition_metrics.accepted_transitions,
        "rejected_transitions": srp_transition_metrics.rejected_transitions,
        "invalid_accept_rate": srp_transition_metrics.invalid_accept_rate,
        "recommendation_execution_separated": srp_governance_metrics.recommendation_execution_separated,
        "replay_consistency": srp_governance_metrics.replay_consistency,
        "memory_accuracy": srp_task_metrics.memory_accuracy,
        "relation_accuracy": srp_task_metrics.relation_accuracy,
        "fact_accuracy": srp_task_metrics.fact_accuracy,
    }
    baseline_summary = {
        "accepted_transitions": baseline_transition_metrics.accepted_transitions,
        "rejected_transitions": baseline_transition_metrics.rejected_transitions,
        "invalid_accept_rate": baseline_transition_metrics.invalid_accept_rate,
        "recommendation_execution_separated": baseline_governance_metrics.recommendation_execution_separated,
        "replay_consistency": baseline_governance_metrics.replay_consistency,
        "memory_accuracy": baseline_task_metrics.memory_accuracy,
        "relation_accuracy": baseline_task_metrics.relation_accuracy,
        "fact_accuracy": baseline_task_metrics.fact_accuracy,
    }

    comparison_summary = {
        "dataset": "LoCoMo",
        "source": str(repo_root / "data" / "locomo" / "locomo10.json"),
        "selection_rule": srp_run.dataset_manifest.selection_rule,
        "sample_id": srp_records[0].get("sample_id", "") if srp_records else "",
        "selected_events": len(srp_records),
        "accepted_delta": baseline_summary["accepted_transitions"] - srp_summary["accepted_transitions"],
        "rejected_delta": baseline_summary["rejected_transitions"] - srp_summary["rejected_transitions"],
        "invalid_accept_rate_delta": round(
            baseline_summary["invalid_accept_rate"] - srp_summary["invalid_accept_rate"], 6
        ),
        "unsupported_mutation_acceptance_delta": round(
            float(any(record.get("event") == "unsupported_mutation" and record.get("actual") == "accept" for record in baseline_records))
            - float(any(record.get("event") == "unsupported_mutation" and record.get("actual") == "accept" for record in srp_records)),
            6,
        ),
        "srp_unsupported_mutation_accepted": any(
            record.get("event") == "unsupported_mutation" and record.get("actual") == "accept" for record in srp_records
        ),
        "baseline_unsupported_mutation_accepted": any(
            record.get("event") == "unsupported_mutation" and record.get("actual") == "accept" for record in baseline_records
        ),
        "recommendation_execution_gap": int(
            bool(baseline_summary["recommendation_execution_separated"]) - bool(srp_summary["recommendation_execution_separated"])
        ),
        "replay_consistency_delta": round(baseline_summary["replay_consistency"] - srp_summary["replay_consistency"], 6),
        "memory_accuracy_delta": round(baseline_summary["memory_accuracy"] - srp_summary["memory_accuracy"], 6),
        "relation_accuracy_delta": round(baseline_summary["relation_accuracy"] - srp_summary["relation_accuracy"], 6),
        "fact_accuracy_delta": round(baseline_summary["fact_accuracy"] - srp_summary["fact_accuracy"], 6),
    }

    metadata = build_metadata(
        experiment="locomo_baseline_comparison",
        dataset="LoCoMo",
        scope="external_validation",
        runtime_contract="srp-real-validation-v1",
    )

    return LocomoBaselineComparisonRun(
        metadata=metadata,
        summary=comparison_summary,
        srp_transition_records=tuple(srp_records),
        baseline_transition_records=tuple(baseline_records),
        srp_metrics={
            "transition_metrics": srp_transition_metrics.as_dict(),
            "governance_metrics": srp_governance_metrics.as_dict(),
            "task_metrics": srp_task_metrics.as_dict(),
        },
        baseline_metrics={
            "transition_metrics": baseline_transition_metrics.as_dict(),
            "governance_metrics": baseline_governance_metrics.as_dict(),
            "task_metrics": baseline_task_metrics.as_dict(),
        },
        srp_failure_cases=tuple(asdict(case) for case in build_failure_cases(srp_records)),
        baseline_failure_cases=tuple(asdict(case) for case in build_failure_cases(baseline_records)),
    )


def write_locomo_baseline_comparison_bundle(
    output_dir: str | Path,
    data_root: str | Path | None = None,
) -> dict[str, str]:
    comparison = build_locomo_baseline_comparison_run(data_root=data_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata_path = output_path / "metadata.json"
    summary_path = output_path / "comparison_summary.json"
    srp_metrics_path = output_path / "srp_metrics.json"
    baseline_metrics_path = output_path / "baseline_metrics.json"
    srp_records_path = output_path / "srp_transition_records.json"
    baseline_records_path = output_path / "baseline_transition_records.json"
    srp_failures_path = output_path / "srp_failure_cases.json"
    baseline_failures_path = output_path / "baseline_failure_cases.json"
    report_path = output_path / "report.md"

    metadata_path.write_text(json.dumps(comparison.metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    summary_path.write_text(json.dumps(comparison.summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    srp_metrics_path.write_text(json.dumps(comparison.srp_metrics, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    baseline_metrics_path.write_text(
        json.dumps(comparison.baseline_metrics, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    srp_records_path.write_text(
        json.dumps([dict(record) for record in comparison.srp_transition_records], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    baseline_records_path.write_text(
        json.dumps([dict(record) for record in comparison.baseline_transition_records], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    srp_failures_path.write_text(
        json.dumps([dict(record) for record in comparison.srp_failure_cases], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    baseline_failures_path.write_text(
        json.dumps([dict(record) for record in comparison.baseline_failure_cases], ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    report_path.write_text(_render_report(comparison), encoding="utf-8")

    return {
        "metadata_json": str(metadata_path),
        "comparison_summary_json": str(summary_path),
        "srp_metrics_json": str(srp_metrics_path),
        "baseline_metrics_json": str(baseline_metrics_path),
        "srp_transition_records_json": str(srp_records_path),
        "baseline_transition_records_json": str(baseline_records_path),
        "srp_failure_cases_json": str(srp_failures_path),
        "baseline_failure_cases_json": str(baseline_failures_path),
        "report_markdown": str(report_path),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    data_root = repo_root / "data" / "locomo"
    output_root = repo_root / "experiments" / "results" / "real_world_validation" / "locomo" / "baseline_comparison"
    comparison = build_locomo_baseline_comparison_run(data_root=data_root)
    output_dir = output_root / f"run_{_safe_run_stamp(str(comparison.metadata['generated_at']))}"
    outputs = write_locomo_baseline_comparison_bundle(output_dir, data_root=data_root)
    print(outputs["report_markdown"])


if __name__ == "__main__":
    main()
