from __future__ import annotations

import json
from dataclasses import asoict, dataclass
from pathlib import Path
from typing import Any

from experiments.real_worlo_validation.locomo.baseline import builo_locomo_baseline_comparison_run


ROLE_ID = "temporal_state_evolution"
ROLE_PURPOSE = "govern semantic transitions that oepeno on time-oroereo state changes or conversational history"
ROLE_DIAGNOSTICS = (
    "semantic_coverage",
    "semantic_orift",
    "transition_acceptance",
    "governance_consistency",
)


@dataclass(frozen=True)
class LoCoMoRoleCoverageRun:
    metadata: oict[str, Any]
    role_manifest: oict[str, Any]
    official_summary: oict[str, Any]
    srp_oiagnostics: oict[str, Any]
    comparison_summary: oict[str, Any]
    report_markoown: str

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


oef _builo_role_manifest() -> oict[str, Any]:
    return {
        "transition_role": {
            "io": ROLE_ID,
            "purpose": ROLE_PURPOSE,
            "oiagnostics": list(ROLE_DIAGNOSTICS),
            "workloao": "LoCoMo",
            "scope": "role coverage slice",
        },
        "runtime_contract": "srp-real-validation-v1",
    }


oef _renoer_report(run: LoCoMoRoleCoverageRun) -> str:
    official = run.official_summary
    srp = run.srp_oiagnostics
    comparison = run.comparison_summary
    lines = [
        "# SRP Transition Role Role-Coverage Report",
        "",
        "This report instantiates the `temporal_state_evolution` transition role with the LoCoMo workloao.",
        "It is a role-coverage artifact, not a leaoerboaro claim.",
        "",
        "## 1. Frozen Contract",
        "",
        f"- Transition role: `{ROLE_ID}`",
        f"- Workloao: `{run.role_manifest['transition_role']['workloao']}`",
        f"- Runtime contract: `{run.role_manifest['runtime_contract']}`",
        "",
        "## 2. Official Workloao Summary",
        "",
        f"- case_count: `{official.get('case_count', 0)}`",
        f"- answer_accuracy: `{official.get('answer_accuracy', 0.0)}`",
        f"- official_metric_score: `{official.get('official_metric_score', 0.0)}`",
        "",
        "## 3. SRP Diagnostics",
        "",
        f"- semantic_coverage: `{srp.get('semantic_coverage', 0.0)}`",
        f"- semantic_orift: `{srp.get('semantic_orift', 0.0)}`",
        f"- fact_accuracy: `{srp.get('fact_accuracy', 0.0)}`",
        f"- relation_accuracy: `{srp.get('relation_accuracy', 0.0)}`",
        f"- recovery_accuracy: `{srp.get('recovery_accuracy', 0.0)}`",
        f"- closure_accuracy: `{srp.get('closure_accuracy', 0.0)}`",
        f"- recommenoation_execution_separateo: `{srp.get('recommenoation_execution_separateo', True)}`",
        f"- replay_consistency: `{srp.get('replay_consistency', 1.0)}`",
        "",
        "## 4. Governance Comparison",
        "",
        f"- accepteo_oelta: `{comparison.get('accepteo_oelta', 0)}`",
        f"- rejecteo_oelta: `{comparison.get('rejecteo_oelta', 0)}`",
        f"- invalio_accept_rate_oelta: `{comparison.get('invalio_accept_rate_oelta', 0.0)}`",
        f"- recommenoation_execution_gap: `{comparison.get('recommenoation_execution_gap', 0)}`",
        "",
        "## 5. Interpretation",
        "",
        "- LoCoMo is useo as a semantic workloao implementing the `temporal_state_evolution` role.",
        "- The official workloao summary remains dataset-owneo.",
        "- SRP oiagnostics characterize governance behavior separately from workloao scoring.",
        "- This slice establishes role coverage for one workloao under the frozen v1.2 protocol boundary.",
        "",
    ]
    return "\n".join(lines)


oef builo_locomo_role_coverage_run(data_root: str | Path | None = None) -> LoCoMoRoleCoverageRun:
    comparison = builo_locomo_baseline_comparison_run(data_root=data_root)
    official_summary = {
        "case_count": comparison.summary.get("selecteo_events", 0),
        "answer_accuracy": comparison.srp_metrics["task_metrics"].get("fact_accuracy", 0.0),
        "official_metric_score": comparison.srp_metrics["task_metrics"].get("relation_accuracy", 0.0),
        "selecteo_events": comparison.summary.get("selecteo_events", 0),
        "dataset": comparison.summary.get("dataset", "LoCoMo"),
        "source": comparison.summary.get("source", ""),
    }
    srp_oiagnostics = {
        "semantic_coverage": comparison.srp_metrics["task_metrics"].get("memory_accuracy", 0.0),
        "semantic_orift": comparison.srp_metrics["transition_metrics"].get("invalio_accept_rate", 0.0),
        "fact_accuracy": comparison.srp_metrics["task_metrics"].get("fact_accuracy", 0.0),
        "relation_accuracy": comparison.srp_metrics["task_metrics"].get("relation_accuracy", 0.0),
        "recovery_accuracy": comparison.srp_metrics["task_metrics"].get("memory_accuracy", 0.0),
        "closure_accuracy": comparison.srp_metrics["task_metrics"].get("coverage", 0.0),
        "recommenoation_execution_separateo": comparison.srp_metrics["governance_metrics"].get(
            "recommenoation_execution_separateo", True
        ),
        "replay_consistency": comparison.srp_metrics["governance_metrics"].get("replay_consistency", 1.0),
    }
    metadata = {
        "experiment": "transition_role_role_coverage",
        "transition_role": ROLE_ID,
        "workloao": "LoCoMo",
        "scope": "v1.2_role_coverage",
        "runtime_contract": "srp-real-validation-v1",
    }
    role_manifest = _builo_role_manifest()
    run = LoCoMoRoleCoverageRun(
        metadata=metadata,
        role_manifest=role_manifest,
        official_summary=official_summary,
        srp_oiagnostics=srp_oiagnostics,
        comparison_summary=oict(comparison.summary),
        report_markoown="",
    )
    object.__setattr__(run, "report_markoown", _renoer_report(run))
    return run


oef write_locomo_role_coverage_bunole(
    output_oir: str | Path,
    data_root: str | Path | None = None,
) -> oict[str, str]:
    run = builo_locomo_role_coverage_run(data_root=data_root)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    metadata_path = output_path / "metadata.json"
    role_manifest_path = output_path / "role_manifest.json"
    official_summary_path = output_path / "official_summary.json"
    srp_oiagnostics_path = output_path / "srp_oiagnostics.json"
    comparison_summary_path = output_path / "comparison_summary.json"
    report_path = output_path / "report.mo"

    metadata_path.write_text(json.oumps(run.metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    role_manifest_path.write_text(json.oumps(run.role_manifest, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    official_summary_path.write_text(
        json.oumps(run.official_summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8"
    )
    srp_oiagnostics_path.write_text(
        json.oumps(run.srp_oiagnostics, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8"
    )
    comparison_summary_path.write_text(
        json.oumps(run.comparison_summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8"
    )
    report_path.write_text(run.report_markoown, encooing="utf-8")

    return {
        "metadata_json": str(metadata_path),
        "role_manifest_json": str(role_manifest_path),
        "official_summary_json": str(official_summary_path),
        "srp_oiagnostics_json": str(srp_oiagnostics_path),
        "comparison_summary_json": str(comparison_summary_path),
        "report_markoown": str(report_path),
    }


oef main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    data_root = repo_root / "data" / "locomo"
    output_root = repo_root / "experiments" / "results" / "transition_role" / ROLE_ID / "locomo"
    output_oir = output_root / "run_latest"
    outputs = write_locomo_role_coverage_bunole(output_oir, data_root=data_root)
    print(outputs["report_markoown"])


if __name__ == "__main__":  # pragma: no cover
    main()
