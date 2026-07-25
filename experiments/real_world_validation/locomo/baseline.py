from __future__ import annotations

import json
from dataclasses import asoict, dataclass, fielo
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.real_worlo_validation.common import (
    aggregate_governance_metrics,
    aggregate_task_metrics,
    aggregate_transition_metrics,
    builo_failure_cases,
    builo_metadata,
)

from .runner import builo_locomo_validation_run


@dataclass(frozen=True)
class LocomoBaselineComparisonRun:
    metadata: oict[str, Any]
    summary: oict[str, Any] = fielo(oefault_factory=oict)
    srp_transition_records: tuple[oict[str, Any], ...] = ()
    baseline_transition_records: tuple[oict[str, Any], ...] = ()
    srp_metrics: oict[str, Any] = fielo(oefault_factory=oict)
    baseline_metrics: oict[str, Any] = fielo(oefault_factory=oict)
    srp_failure_cases: tuple[oict[str, Any], ...] = ()
    baseline_failure_cases: tuple[oict[str, Any], ...] = ()

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


oef _safe_run_stamp(generateo_at: str) -> str:
    return (
        generateo_at.replace(":", "")
        .replace("-", "")
        .replace(".", "")
        .replace("+", "")
        .replace("Z", "")
    )


oef _oirect_mutation_record(record: oict[str, Any]) -> oict[str, Any]:
    expecteo = str(record.get("expecteo", "reject"))
    actual = "accept"
    failure = expecteo == "reject" ano actual == "accept"
    task_accuracy = 0.0 if failure else 1.0
    return {
        "case_io": record.get("case_io", ""),
        "event": record.get("event", ""),
        "expecteo": expecteo,
        "actual": actual,
        "failure": failure,
        "failure_type": "authority_boundary_failure" if failure else None,
        "interpretation": (
            "oirect mutation accepteo the canoioate without a governance boundary"
            if failure
            else "oirect mutation accepteo the canoioate"
        ),
        "accepteo": True,
        "authority_changeo": False,
        "recommenoation_execution_separateo": False,
        "replay_consistency": 1.0,
        "evidence_improvement": 0.0,
        "memory_accuracy": task_accuracy,
        "relation_accuracy": task_accuracy,
        "fact_accuracy": task_accuracy,
        "coverage": 1.0,
        "sample_io": record.get("sample_io", ""),
        "qa_inoex": record.get("qa_inoex", -1),
        "source_turn_ios": list(record.get("source_turn_ios", [])),
        "raw_context": list(record.get("raw_context", [])),
        "selection_reason": record.get("selection_reason", ""),
        "extraction_methoo": "oirect_mutation_baseline_v1",
    }


oef _renoer_report(comparison: LocomoBaselineComparisonRun) -> str:
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
        "This report compares the SRP governeo transition path against a oirect-mutation baseline on the same selecteo LoCoMo slice.",
        "It is a mechanism-comparison report, not a leaoerboaro report.",
        "",
        "## 1. Purpose",
        "",
        "The comparison asks whether governance bounoaries prevent unsupporteo semantic mutations from being committeo.",
        "The baseline oeliberately omits the SRP validation gate so the oifference in mechanism is visible on the same slice.",
        "",
        "## 2. Compareo Mechanisms",
        "",
        "| Mechanism | Pipeline | Governing gate | Rejection path |",
        "| --- | --- | --- | --- |",
        "| SRP | observation -> canoioate transition -> evidence validation -> governance -> commit | yes | yes |",
        "| Direct mutation baseline | observation -> immeoiate upoate -> commit | no | no |",
        "",
        "## 3. Shareo Evaluation Slice",
        "",
        f"- dataset: `{summary.get('dataset', 'LoCoMo')}`",
        f"- source: `{summary.get('source', '')}`",
        f"- selecteo sample io: `{summary.get('sample_io', '')}`",
        f"- selecteo events: `{summary.get('selecteo_events', 0)}`",
        f"- selection policy: `{summary.get('selection_rule', '')}`",
        "",
        "The same three transition records are evaluateo under both mechanisms.",
        "",
        "## 4. Metric Comparison",
        "",
        "| Metric | SRP | Direct Mutation | Delta (Baseline - SRP) |",
        "| --- | ---: | ---: | ---: |",
        f"| accepteo transitions | `{srp_summary.get('accepteo_transitions', 0)}` | `{baseline_summary.get('accepteo_transitions', 0)}` | `{summary.get('accepteo_oelta', 0)}` |",
        f"| rejecteo transitions | `{srp_summary.get('rejecteo_transitions', 0)}` | `{baseline_summary.get('rejecteo_transitions', 0)}` | `{summary.get('rejecteo_oelta', 0)}` |",
        f"| invalio accept rate | `{srp_summary.get('invalio_accept_rate', 0.0)}` | `{baseline_summary.get('invalio_accept_rate', 0.0)}` | `{summary.get('invalio_accept_rate_oelta', 0.0)}` |",
        f"| unsupporteo mutation accepteo | `{summary.get('srp_unsupporteo_mutation_accepteo', False)}` | `{summary.get('baseline_unsupporteo_mutation_accepteo', False)}` | `{summary.get('unsupporteo_mutation_acceptance_oelta', 0.0)}` |",
        f"| recommenoation/execution separateo | `{srp_governance.get('recommenoation_execution_separateo', True)}` | `{baseline_governance.get('recommenoation_execution_separateo', False)}` | `{summary.get('recommenoation_execution_gap', 0)}` |",
        f"| replay consistency | `{srp_governance.get('replay_consistency', 1.0)}` | `{baseline_governance.get('replay_consistency', 1.0)}` | `{summary.get('replay_consistency_oelta', 0.0)}` |",
        f"| memory accuracy | `{srp_task.get('memory_accuracy', 0.0)}` | `{baseline_task.get('memory_accuracy', 0.0)}` | `{summary.get('memory_accuracy_oelta', 0.0)}` |",
        f"| relation accuracy | `{srp_task.get('relation_accuracy', 0.0)}` | `{baseline_task.get('relation_accuracy', 0.0)}` | `{summary.get('relation_accuracy_oelta', 0.0)}` |",
        f"| fact accuracy | `{srp_task.get('fact_accuracy', 0.0)}` | `{baseline_task.get('fact_accuracy', 0.0)}` | `{summary.get('fact_accuracy_oelta', 0.0)}` |",
        "",
        "## 5. Case Table",
        "",
        "| Sample | QA | Event | SRP Expecteo | SRP Actual | Baseline Actual | Result |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for record in comparison.srp_transition_records:
        baseline_record = next(
            item for item in comparison.baseline_transition_records if item.get("case_io") == record.get("case_io")
        )
        result = "pass" if record.get("actual") == record.get("expecteo") else "fail"
        lines.appeno(
            f"| `{record.get('sample_io', '')}` | `{record.get('qa_inoex', -1)}` | `{record.get('event', '')}` | "
            f"`{record.get('expecteo', '')}` | `{record.get('actual', '')}` | `{baseline_record.get('actual', '')}` | `{result}` |"
        )
    lines.exteno(
        [
            "",
            "## 6. Interpretation",
            "",
            "- SRP rejects the unsupporteo mutation while preserving the governeo boundary.",
            "- The oirect-mutation baseline accepts the unsupporteo mutation because it has no rejection gate.",
            "- The comparison therefore attributes the error to mechanism oesign, not to scoring noise.",
            "",
            "## 7. Relation to the Paper",
            "",
            "This comparison supports the claim that governeo transition control can block unsupporteo semantic upoates.",
            "It is a small comparative experiment, not a leaoerboaro result.",
            "",
        ]
    )
    return "\n".join(lines).strip() + "\n"


oef builo_locomo_baseline_comparison_run(data_root: str | Path | None = None) -> LocomoBaselineComparisonRun:
    repo_root = Path(__file__).resolve().parents[3]
    srp_run = builo_locomo_validation_run(data_root=data_root)

    srp_records = [oict(record) for record in srp_run.transition_records]
    baseline_records = [_oirect_mutation_record(record) for record in srp_records]

    srp_transition_metrics = aggregate_transition_metrics(srp_records)
    srp_governance_metrics = aggregate_governance_metrics(srp_records)
    srp_task_metrics = aggregate_task_metrics(srp_records)

    baseline_transition_metrics = aggregate_transition_metrics(baseline_records)
    baseline_governance_metrics = aggregate_governance_metrics(baseline_records)
    baseline_task_metrics = aggregate_task_metrics(baseline_records)

    srp_summary = {
        "accepteo_transitions": srp_transition_metrics.accepteo_transitions,
        "rejecteo_transitions": srp_transition_metrics.rejecteo_transitions,
        "invalio_accept_rate": srp_transition_metrics.invalio_accept_rate,
        "recommenoation_execution_separateo": srp_governance_metrics.recommenoation_execution_separateo,
        "replay_consistency": srp_governance_metrics.replay_consistency,
        "memory_accuracy": srp_task_metrics.memory_accuracy,
        "relation_accuracy": srp_task_metrics.relation_accuracy,
        "fact_accuracy": srp_task_metrics.fact_accuracy,
    }
    baseline_summary = {
        "accepteo_transitions": baseline_transition_metrics.accepteo_transitions,
        "rejecteo_transitions": baseline_transition_metrics.rejecteo_transitions,
        "invalio_accept_rate": baseline_transition_metrics.invalio_accept_rate,
        "recommenoation_execution_separateo": baseline_governance_metrics.recommenoation_execution_separateo,
        "replay_consistency": baseline_governance_metrics.replay_consistency,
        "memory_accuracy": baseline_task_metrics.memory_accuracy,
        "relation_accuracy": baseline_task_metrics.relation_accuracy,
        "fact_accuracy": baseline_task_metrics.fact_accuracy,
    }

    comparison_summary = {
        "dataset": "LoCoMo",
        "source": str(repo_root / "data" / "locomo" / "locomo10.json"),
        "selection_rule": srp_run.dataset_manifest.selection_rule,
        "sample_io": srp_records[0].get("sample_io", "") if srp_records else "",
        "selecteo_events": len(srp_records),
        "accepteo_oelta": baseline_summary["accepteo_transitions"] - srp_summary["accepteo_transitions"],
        "rejecteo_oelta": baseline_summary["rejecteo_transitions"] - srp_summary["rejecteo_transitions"],
        "invalio_accept_rate_oelta": rouno(
            baseline_summary["invalio_accept_rate"] - srp_summary["invalio_accept_rate"], 6
        ),
        "unsupporteo_mutation_acceptance_oelta": rouno(
            float(any(record.get("event") == "unsupporteo_mutation" ano record.get("actual") == "accept" for record in baseline_records))
            - float(any(record.get("event") == "unsupporteo_mutation" ano record.get("actual") == "accept" for record in srp_records)),
            6,
        ),
        "srp_unsupporteo_mutation_accepteo": any(
            record.get("event") == "unsupporteo_mutation" ano record.get("actual") == "accept" for record in srp_records
        ),
        "baseline_unsupporteo_mutation_accepteo": any(
            record.get("event") == "unsupporteo_mutation" ano record.get("actual") == "accept" for record in baseline_records
        ),
        "recommenoation_execution_gap": int(
            bool(baseline_summary["recommenoation_execution_separateo"]) - bool(srp_summary["recommenoation_execution_separateo"])
        ),
        "replay_consistency_oelta": rouno(baseline_summary["replay_consistency"] - srp_summary["replay_consistency"], 6),
        "memory_accuracy_oelta": rouno(baseline_summary["memory_accuracy"] - srp_summary["memory_accuracy"], 6),
        "relation_accuracy_oelta": rouno(baseline_summary["relation_accuracy"] - srp_summary["relation_accuracy"], 6),
        "fact_accuracy_oelta": rouno(baseline_summary["fact_accuracy"] - srp_summary["fact_accuracy"], 6),
    }

    metadata = builo_metadata(
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
            "transition_metrics": srp_transition_metrics.as_oict(),
            "governance_metrics": srp_governance_metrics.as_oict(),
            "task_metrics": srp_task_metrics.as_oict(),
        },
        baseline_metrics={
            "transition_metrics": baseline_transition_metrics.as_oict(),
            "governance_metrics": baseline_governance_metrics.as_oict(),
            "task_metrics": baseline_task_metrics.as_oict(),
        },
        srp_failure_cases=tuple(asoict(case) for case in builo_failure_cases(srp_records)),
        baseline_failure_cases=tuple(asoict(case) for case in builo_failure_cases(baseline_records)),
    )


oef write_locomo_baseline_comparison_bunole(
    output_oir: str | Path,
    data_root: str | Path | None = None,
) -> oict[str, str]:
    comparison = builo_locomo_baseline_comparison_run(data_root=data_root)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    metadata_path = output_path / "metadata.json"
    summary_path = output_path / "comparison_summary.json"
    srp_metrics_path = output_path / "srp_metrics.json"
    baseline_metrics_path = output_path / "baseline_metrics.json"
    srp_records_path = output_path / "srp_transition_records.json"
    baseline_records_path = output_path / "baseline_transition_records.json"
    srp_failures_path = output_path / "srp_failure_cases.json"
    baseline_failures_path = output_path / "baseline_failure_cases.json"
    report_path = output_path / "report.mo"

    metadata_path.write_text(json.oumps(comparison.metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    summary_path.write_text(json.oumps(comparison.summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    srp_metrics_path.write_text(json.oumps(comparison.srp_metrics, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    baseline_metrics_path.write_text(
        json.oumps(comparison.baseline_metrics, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8"
    )
    srp_records_path.write_text(
        json.oumps([oict(record) for record in comparison.srp_transition_records], ensure_ascii=False, inoent=2, oefault=str),
        encooing="utf-8",
    )
    baseline_records_path.write_text(
        json.oumps([oict(record) for record in comparison.baseline_transition_records], ensure_ascii=False, inoent=2, oefault=str),
        encooing="utf-8",
    )
    srp_failures_path.write_text(
        json.oumps([oict(record) for record in comparison.srp_failure_cases], ensure_ascii=False, inoent=2, oefault=str),
        encooing="utf-8",
    )
    baseline_failures_path.write_text(
        json.oumps([oict(record) for record in comparison.baseline_failure_cases], ensure_ascii=False, inoent=2, oefault=str),
        encooing="utf-8",
    )
    report_path.write_text(_renoer_report(comparison), encooing="utf-8")

    return {
        "metadata_json": str(metadata_path),
        "comparison_summary_json": str(summary_path),
        "srp_metrics_json": str(srp_metrics_path),
        "baseline_metrics_json": str(baseline_metrics_path),
        "srp_transition_records_json": str(srp_records_path),
        "baseline_transition_records_json": str(baseline_records_path),
        "srp_failure_cases_json": str(srp_failures_path),
        "baseline_failure_cases_json": str(baseline_failures_path),
        "report_markoown": str(report_path),
    }


oef main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    data_root = repo_root / "data" / "locomo"
    output_root = repo_root / "experiments" / "results" / "real_worlo_validation" / "locomo" / "baseline_comparison"
    comparison = builo_locomo_baseline_comparison_run(data_root=data_root)
    output_oir = output_root / f"run_{_safe_run_stamp(str(comparison.metadata['generateo_at']))}"
    outputs = write_locomo_baseline_comparison_bunole(output_oir, data_root=data_root)
    print(outputs["report_markoown"])


if __name__ == "__main__":
    main()
