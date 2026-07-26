from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .schema import SensitivityEvaluationReport


def _format_axis_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


@dataclass(frozen=True)
class PhaseVIIBParameterSensitivityMarkdownReport:
    report: SensitivityEvaluationReport
    config: dict[str, Any]

    def render(self) -> str:
        baseline = self.report.baseline_parameters
        schema = self.report.metric_schema
        summary = self.report.summary
        axis_summary = self.report.axis_summary
        lines: list[str] = []
        lines.append("# SRP Phase VII-B Parameter Sensitivity and Governance Tradeoff Report")
        lines.append("")
        lines.append("This report freezes the Phase VII-B parameter-sensitivity evidence package for SRP.")
        lines.append("It is an evaluation report, not a calibration artifact, not a runtime policy, and not a governed update directive.")
        lines.append("")
        lines.append("## 1. Purpose")
        lines.append("")
        lines.append(
            "Phase VII-B measures how SRP parameters influence semantic fidelity, structural preservation, reconstruction cost, and governance stability under a frozen relation-aware recovery baseline."
        )
        lines.append("")
        lines.append("## 2. Frozen Scope")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Phase | `{self.config.get('phase', 'phase_vii_parameter_sensitivity')}` |")
        lines.append(f"| Evaluation mode | `{self.config.get('evaluation_mode', 'governance_tradeoff_analysis')}` |")
        lines.append(f"| Workload | `{self.config.get('workload_name', 'phase_vi_relation_recovery_mvp')}` |")
        lines.append(f"| Objective | `{self.config.get('objective_name', 'governed_reconstruction')}` |")
        lines.append(f"| Evidence backend | `{self.config.get('evidence_backend', 'relation_closure')}` |")
        lines.append(f"| Recovery strategy | `{baseline.recovery_strategy}` |")
        lines.append(f"| Baseline activation threshold | `{baseline.activation_threshold}` |")
        lines.append(f"| Baseline recovery minimum evidence | `{baseline.recovery_min_evidence}` |")
        lines.append(f"| Baseline preserve evidence | `{baseline.preserve_evidence}` |")
        lines.append(f"| Baseline archive relations | `{baseline.archive_relations}` |")
        lines.append(f"| Baseline relation depth | `{baseline.relation_depth}` |")
        lines.append("")
        lines.append("The protocol keeps the workload, semantic state family, objective, evidence backend, and recovery strategy fixed.")
        lines.append("Only the parameter axes change across runs.")
        lines.append("")
        lines.append("## 3. Metrics Schema")
        lines.append("")
        lines.append(f"- Schema version: `{schema.schema_version}`")
        lines.append(f"- Coverage definition: {schema.coverage_definition}")
        lines.append(f"- Drift definition: {schema.drift_definition}")
        lines.append(f"- Sensitivity definition: {schema.sensitivity_definition}")
        lines.append(f"- Evidence cost definition: {schema.evidence_cost_definition}")
        lines.append("")
        lines.append("## 4. Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | ---: |")
        lines.append(f"| Run count | `{summary.get('run_count', 0)}` |")
        lines.append(f"| Mean semantic coverage | `{summary.get('mean_semantic_coverage', 0.0)}` |")
        lines.append(f"| Mean semantic drift | `{summary.get('mean_semantic_drift', 0.0)}` |")
        lines.append(f"| Mean fact accuracy | `{summary.get('mean_fact_accuracy', 0.0)}` |")
        lines.append(f"| Mean relation accuracy | `{summary.get('mean_relation_accuracy', 0.0)}` |")
        lines.append(f"| Mean recovery accuracy | `{summary.get('mean_recovery_accuracy', 0.0)}` |")
        lines.append(f"| Mean closure accuracy | `{summary.get('mean_closure_accuracy', 0.0)}` |")
        lines.append(f"| Mean path preservation | `{summary.get('mean_path_preservation', 0.0)}` |")
        lines.append(f"| Mean neighborhood completeness | `{summary.get('mean_neighborhood_completeness', 0.0)}` |")
        lines.append(f"| Mean hallucinated relation rate | `{summary.get('mean_hallucinated_relation_rate', 0.0)}` |")
        lines.append(f"| Mean evidence cost | `{summary.get('mean_evidence_cost', 0.0)}` |")
        lines.append(f"| Mean coverage delta vs baseline | `{summary.get('mean_coverage_delta_vs_baseline', 0.0)}` |")
        lines.append(f"| Mean drift delta vs baseline | `{summary.get('mean_drift_delta_vs_baseline', 0.0)}` |")
        lines.append(f"| Mean cost delta vs baseline | `{summary.get('mean_cost_delta_vs_baseline', 0.0)}` |")
        lines.append(f"| Baseline run | `{summary.get('baseline_run_id', '')}` |")
        lines.append("")
        lines.append("## 5. Parameter Axis Summary")
        lines.append("")
        for axis_name, rows in axis_summary.items():
            lines.append(f"### {axis_name}")
            lines.append("")
            lines.append("| Value | Coverage | Drift | Relation Acc. | Closure Acc. | Evidence Cost | Delta Drift | Delta Cost |")
            lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            for row in rows:
                lines.append(
                    "| "
                    f"`{_format_axis_value(row['axis_value'])}` | `{row['mean_semantic_coverage']}` | `{row['mean_semantic_drift']}` | "
                    f"`{row['mean_relation_accuracy']}` | `{row['mean_closure_accuracy']}` | `{row['mean_evidence_cost']}` | "
                    f"`{row['drift_delta_vs_baseline']}` | `{row['cost_delta_vs_baseline']}` |"
                )
            lines.append("")
        lines.append("## 6. Pareto Frontier")
        lines.append("")
        lines.append("The frontier lists non-dominated parameter settings under coverage maximization and drift/cost minimization.")
        lines.append("")
        lines.append("| Run | Axis | Value | Coverage | Drift | Cost |")
        lines.append("| --- | --- | --- | ---: | ---: | ---: |")
        for row in summary.get("pareto_frontier", []):
            lines.append(
                "| "
                f"`{row['run_id']}` | `{row['axis_name']}` | `{_format_axis_value(row['axis_value'])}` | "
                f"`{row['mean_semantic_coverage']}` | `{row['mean_semantic_drift']}` | `{row['mean_evidence_cost']}` |"
            )
        lines.append("")
        lines.append("## 7. Interpretation")
        lines.append("")
        lines.append(
            "The baseline and sweep results expose how each parameter shifts the tradeoff surface between semantic fidelity, structure preservation, and reconstruction cost."
        )
        lines.append("They do not claim a universally optimal parameter setting.")
        lines.append("")
        lines.append("## 8. Relation to the Paper")
        lines.append("")
        lines.append(
            "Phase VII-B extends the paper's evidence chain by explaining how governed parameters move the system across fidelity-cost tradeoff regions without introducing autonomous adaptation."
        )
        lines.append("")
        lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
