from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .schema import RelationRecoveryEvaluationReport


@dataclass(frozen=True)
class PhaseVIRelationRecoveryMarkdownReport:
    report: RelationRecoveryEvaluationReport
    config: dict

    def render(self) -> str:
        baseline = self.report.baseline_config
        schema = self.report.metric_schema
        summary = self.report.summary
        lines: list[str] = []
        lines.append("# SRP Phase VI Relation-Aware Recovery Report")
        lines.append("")
        lines.append("This report freezes the Phase VI-A relation-aware recovery evidence package for SRP.")
        lines.append("It is an evaluation report, not a calibration artifact and not a runtime optimization artifact.")
        lines.append("")
        lines.append("## 1. Purpose")
        lines.append("")
        lines.append(
            "Phase VI-A measures whether relation-aware recovery can preserve semantic structure during reconstruction under the same information budget."
        )
        lines.append("")
        lines.append("## 2. Frozen Protocol")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Phase | `{self.config.get('phase', 'phase_vi_relation_recovery')}` |")
        lines.append(f"| Experiment name | `{self.config.get('experiment_name', 'relation_aware_recovery')}` |")
        lines.append(f"| Recovery modes | `{', '.join(self.config.get('recovery_modes', baseline.mode))}` |")
        lines.append(f"| Baseline top_k | `{baseline.top_k}` |")
        lines.append(f"| Baseline relation depth | `{baseline.relation_depth}` |")
        lines.append(f"| Baseline closure validation | `{baseline.closure_validation}` |")
        lines.append("")
        lines.append("The protocol keeps the original semantic state, available memory units, evidence budget, workload family, and evaluation schema fixed.")
        lines.append("Only the recovery strategy changes across modes.")
        lines.append("")
        lines.append("## 3. Metrics Schema")
        lines.append("")
        lines.append(f"- Schema version: `{schema.schema_version}`")
        lines.append(f"- Coverage definition: {schema.coverage_definition}")
        lines.append(f"- Drift definition: {schema.drift_definition}")
        lines.append(f"- Drift weights: `{schema.semantic_drift_weights}`")
        lines.append(f"- Closure definition: {schema.closure_definition}")
        lines.append(f"- Evidence cost definition: {schema.evidence_cost_definition}")
        lines.append("")
        lines.append("## 4. Recovery Modes")
        lines.append("")
        lines.append("- vector-only recovery")
        lines.append("- vector + relation expansion")
        lines.append("- relation-closure recovery")
        lines.append("")
        lines.append("## 5. Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | ---: |")
        lines.append(f"| Case count | `{summary.get('case_count', 0)}` |")
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
        lines.append("")
        lines.append("## 6. Mode Summary")
        lines.append("")
        for mode, mode_summary in summary.get("mode_summary", {}).items():
            lines.append(f"### {mode}")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("| --- | ---: |")
            for key, value in mode_summary.items():
                lines.append(f"| {key} | `{value}` |")
            lines.append("")
        lines.append("## 7. Per-Case Results")
        lines.append("")
        lines.append("| Case | Category | Mode | Coverage | Drift | Fact Acc. | Relation Acc. | Closure Acc. | Path Pres. | Neighborhood | Hallucinated Rel. | Cost |")
        lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for record in self.report.records:
            metrics = record.metrics
            lines.append(
                "| "
                f"`{record.case.case_id}` | `{record.case.category}` | `{record.config.mode}` | `{metrics.semantic_coverage}` | `{metrics.semantic_drift}` | "
                f"`{metrics.fact_accuracy}` | `{metrics.relation_accuracy}` | `{metrics.closure_accuracy}` | `{metrics.path_preservation}` | "
                f"`{metrics.neighborhood_completeness}` | `{metrics.hallucinated_relation_rate}` | `{metrics.evidence_cost}` |"
            )
        lines.append("")
        lines.append("## 8. Interpretation")
        lines.append("")
        lines.append(
            "The baseline protocol is intended to expose the tradeoff surface between semantic fidelity and reconstruction cost."
        )
        lines.append("It does not claim a universally optimal recovery mode.")
        lines.append("")
        lines.append("## 9. Relation to the Paper")
        lines.append("")
        lines.append(
            "Phase VI-A extends the paper's evidence chain by testing whether semantic neighborhoods can be reconstructed more faithfully than isolated units."
        )
        lines.append("")
        lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
