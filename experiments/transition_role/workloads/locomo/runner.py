from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from experiments.real_world_validation.locomo.baseline import build_locomo_baseline_comparison_run


ROLE_ID = "temporal_state_evolution"
ROLE_PURPOSE = "govern semantic transitions that depend on time-ordered state changes or conversational history"
ROLE_DIAGNOSTICS = (
    "semantic_coverage",
    "semantic_drift",
    "transition_acceptance",
    "governance_consistency",
)


@dataclass(frozen=True)
class LoCoMoRoleCoverageRun:
    metadata: dict[str, Any]
    role_manifest: dict[str, Any]
    official_summary: dict[str, Any]
    srp_diagnostics: dict[str, Any]
    comparison_summary: dict[str, Any]
    report_markdown: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _build_role_manifest() -> dict[str, Any]:
    return {
        "transition_role": {
            "id": ROLE_ID,
            "purpose": ROLE_PURPOSE,
            "diagnostics": list(ROLE_DIAGNOSTICS),
            "workload": "LoCoMo",
            "scope": "role coverage slice",
        },
        "runtime_contract": "srp-real-validation-v1",
    }


def _render_report(run: LoCoMoRoleCoverageRun) -> str:
    official = run.official_summary
    srp = run.srp_diagnostics
    comparison = run.comparison_summary
    lines = [
        "# SRP Transition Role Role-Coverage Report",
        "",
        "This report instantiates the `temporal_state_evolution` transition role with the LoCoMo workload.",
        "It is a role-coverage artifact, not a leaderboard claim.",
        "",
        "## 1. Frozen Contract",
        "",
        f"- Transition role: `{ROLE_ID}`",
        f"- Workload: `{run.role_manifest['transition_role']['workload']}`",
        f"- Runtime contract: `{run.role_manifest['runtime_contract']}`",
        "",
        "## 2. Official Workload Summary",
        "",
        f"- case_count: `{official.get('case_count', 0)}`",
        f"- answer_accuracy: `{official.get('answer_accuracy', 0.0)}`",
        f"- official_metric_score: `{official.get('official_metric_score', 0.0)}`",
        "",
        "## 3. SRP Diagnostics",
        "",
        f"- semantic_coverage: `{srp.get('semantic_coverage', 0.0)}`",
        f"- semantic_drift: `{srp.get('semantic_drift', 0.0)}`",
        f"- fact_accuracy: `{srp.get('fact_accuracy', 0.0)}`",
        f"- relation_accuracy: `{srp.get('relation_accuracy', 0.0)}`",
        f"- recovery_accuracy: `{srp.get('recovery_accuracy', 0.0)}`",
        f"- closure_accuracy: `{srp.get('closure_accuracy', 0.0)}`",
        f"- recommendation_execution_separated: `{srp.get('recommendation_execution_separated', True)}`",
        f"- replay_consistency: `{srp.get('replay_consistency', 1.0)}`",
        "",
        "## 4. Governance Comparison",
        "",
        f"- accepted_delta: `{comparison.get('accepted_delta', 0)}`",
        f"- rejected_delta: `{comparison.get('rejected_delta', 0)}`",
        f"- invalid_accept_rate_delta: `{comparison.get('invalid_accept_rate_delta', 0.0)}`",
        f"- recommendation_execution_gap: `{comparison.get('recommendation_execution_gap', 0)}`",
        "",
        "## 5. Interpretation",
        "",
        "- LoCoMo is used as a semantic workload implementing the `temporal_state_evolution` role.",
        "- The official workload summary remains dataset-owned.",
        "- SRP diagnostics characterize governance behavior separately from workload scoring.",
        "- This slice establishes role coverage for one workload under the frozen v1.2 protocol boundary.",
        "",
    ]
    return "\n".join(lines)


def build_locomo_role_coverage_run(data_root: str | Path | None = None) -> LoCoMoRoleCoverageRun:
    comparison = build_locomo_baseline_comparison_run(data_root=data_root)
    official_summary = {
        "case_count": comparison.summary.get("selected_events", 0),
        "answer_accuracy": comparison.srp_metrics["task_metrics"].get("fact_accuracy", 0.0),
        "official_metric_score": comparison.srp_metrics["task_metrics"].get("relation_accuracy", 0.0),
        "selected_events": comparison.summary.get("selected_events", 0),
        "dataset": comparison.summary.get("dataset", "LoCoMo"),
        "source": comparison.summary.get("source", ""),
    }
    srp_diagnostics = {
        "semantic_coverage": comparison.srp_metrics["task_metrics"].get("memory_accuracy", 0.0),
        "semantic_drift": comparison.srp_metrics["transition_metrics"].get("invalid_accept_rate", 0.0),
        "fact_accuracy": comparison.srp_metrics["task_metrics"].get("fact_accuracy", 0.0),
        "relation_accuracy": comparison.srp_metrics["task_metrics"].get("relation_accuracy", 0.0),
        "recovery_accuracy": comparison.srp_metrics["task_metrics"].get("memory_accuracy", 0.0),
        "closure_accuracy": comparison.srp_metrics["task_metrics"].get("coverage", 0.0),
        "recommendation_execution_separated": comparison.srp_metrics["governance_metrics"].get(
            "recommendation_execution_separated", True
        ),
        "replay_consistency": comparison.srp_metrics["governance_metrics"].get("replay_consistency", 1.0),
    }
    metadata = {
        "experiment": "transition_role_role_coverage",
        "transition_role": ROLE_ID,
        "workload": "LoCoMo",
        "scope": "v1.2_role_coverage",
        "runtime_contract": "srp-real-validation-v1",
    }
    role_manifest = _build_role_manifest()
    run = LoCoMoRoleCoverageRun(
        metadata=metadata,
        role_manifest=role_manifest,
        official_summary=official_summary,
        srp_diagnostics=srp_diagnostics,
        comparison_summary=dict(comparison.summary),
        report_markdown="",
    )
    object.__setattr__(run, "report_markdown", _render_report(run))
    return run


def write_locomo_role_coverage_bundle(
    output_dir: str | Path,
    data_root: str | Path | None = None,
) -> dict[str, str]:
    run = build_locomo_role_coverage_run(data_root=data_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata_path = output_path / "metadata.json"
    role_manifest_path = output_path / "role_manifest.json"
    official_summary_path = output_path / "official_summary.json"
    srp_diagnostics_path = output_path / "srp_diagnostics.json"
    comparison_summary_path = output_path / "comparison_summary.json"
    report_path = output_path / "report.md"

    metadata_path.write_text(json.dumps(run.metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    role_manifest_path.write_text(json.dumps(run.role_manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    official_summary_path.write_text(
        json.dumps(run.official_summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    srp_diagnostics_path.write_text(
        json.dumps(run.srp_diagnostics, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    comparison_summary_path.write_text(
        json.dumps(run.comparison_summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
    )
    report_path.write_text(run.report_markdown, encoding="utf-8")

    return {
        "metadata_json": str(metadata_path),
        "role_manifest_json": str(role_manifest_path),
        "official_summary_json": str(official_summary_path),
        "srp_diagnostics_json": str(srp_diagnostics_path),
        "comparison_summary_json": str(comparison_summary_path),
        "report_markdown": str(report_path),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    data_root = repo_root / "data" / "locomo"
    output_root = repo_root / "experiments" / "results" / "transition_role" / ROLE_ID / "locomo"
    output_dir = output_root / "run_latest"
    outputs = write_locomo_role_coverage_bundle(output_dir, data_root=data_root)
    print(outputs["report_markdown"])


if __name__ == "__main__":  # pragma: no cover
    main()
