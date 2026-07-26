from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .schema import RetentionEvaluationReport


@dataclass(frozen=True)
class PhaseVRetentionMarkdownReport:
    report: RetentionEvaluationReport
    config: dict[str, Any]

    def render(self) -> str:
        baseline = self.report.baseline_parameters
        schema = self.report.metric_schema
        summary = self.report.summary
        lines: list[str] = []
        lines.append("# SRP Phase V Retention and Drift Evaluation")
        lines.append("")
        lines.append("This report freezes the Phase V semantic retention and drift evidence package for SRP.")
        lines.append("It is an evaluation report, not a calibration artifact and not a runtime optimization artifact.")
        lines.append("")
        lines.append("## 1. Purpose")
        lines.append("")
        lines.append(
            "Phase V measures semantic fidelity after governed transition. "
            "It evaluates whether semantic coverage and semantic drift can be measured at the meaning level rather than only at the parameter level."
        )
        lines.append("")
        lines.append("## 2. Frozen Protocol")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Phase | `{self.config.get('phase', 'phase_v_retention')}` |")
        lines.append(f"| Evaluation mode | `{self.config.get('evaluation_mode', 'retention_drift')}` |")
        lines.append(f"| Baseline activation threshold | `{baseline.activation_threshold}` |")
        lines.append(f"| Baseline recovery minimum evidence | `{baseline.recovery_min_evidence}` |")
        lines.append(f"| Baseline preserve evidence | `{baseline.preserve_evidence}` |")
        lines.append(f"| Baseline archive relations | `{baseline.archive_relations}` |")
        lines.append("")
        lines.append("The protocol keeps workload, objective, and evidence backend fixed.")
        lines.append("Only the retention-related settings are interpreted as evaluation axes.")
        lines.append("")
        lines.append("## 3. Metrics Schema")
        lines.append("")
        lines.append(f"- Schema version: `{schema.schema_version}`")
        lines.append(f"- Coverage definition: {schema.coverage_definition}")
        lines.append(f"- Drift definition: {schema.drift_definition}")
        lines.append(f"- Drift weights: `{schema.semantic_drift_weights}`")
        lines.append(f"- Recovery definition: {schema.recovery_definition}")
        lines.append(f"- Evidence cost definition: {schema.evidence_cost_definition}")
        lines.append("")
        lines.append("## 4. Single-Transition Output Fields")
        lines.append("")
        lines.append("| Field | Meaning |")
        lines.append("| --- | --- |")
        lines.append("| `semantic_coverage` | Recall-like preserved meaning fraction |")
        lines.append("| `semantic_drift` | Weighted semantic loss over facts, relations, and confidence |")
        lines.append("| `fact_accuracy` | Fraction of original facts recovered |")
        lines.append("| `relation_accuracy` | Fraction of original relations recovered |")
        lines.append("| `recovery_accuracy` | Jaccard-like fidelity over original and recovered semantic units |")
        lines.append("| `evidence_cost` | Cost attached to the transition case |")
        lines.append("")
        lines.append("## 5. Experimental Cases")
        lines.append("")
        lines.append(f"- Case count: `{summary.get('case_count', 0)}`")
        lines.append(f"- Category counts: `{summary.get('category_counts', {})}`")
        lines.append("")
        lines.append("## 6. Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | ---: |")
        lines.append(f"| Mean semantic coverage | `{summary.get('mean_semantic_coverage', 0.0)}` |")
        lines.append(f"| Mean semantic drift | `{summary.get('mean_semantic_drift', 0.0)}` |")
        lines.append(f"| Mean fact accuracy | `{summary.get('mean_fact_accuracy', 0.0)}` |")
        lines.append(f"| Mean relation accuracy | `{summary.get('mean_relation_accuracy', 0.0)}` |")
        lines.append(f"| Mean recovery accuracy | `{summary.get('mean_recovery_accuracy', 0.0)}` |")
        lines.append(f"| Mean evidence cost | `{summary.get('mean_evidence_cost', 0.0)}` |")
        lines.append(f"| Total missing units | `{summary.get('total_missing_count', 0)}` |")
        lines.append(f"| Total hallucinated units | `{summary.get('total_hallucination_count', 0)}` |")
        lines.append(f"| Coverage range | `{summary.get('coverage_min', 0.0)}` .. `{summary.get('coverage_max', 0.0)}` |")
        lines.append(f"| Drift range | `{summary.get('drift_min', 0.0)}` .. `{summary.get('drift_max', 0.0)}` |")
        lines.append(f"| Recovery accuracy range | `{summary.get('recovery_accuracy_min', 0.0)}` .. `{summary.get('recovery_accuracy_max', 0.0)}` |")
        lines.append("")
        lines.append("## 7. Per-Case Results")
        lines.append("")
        lines.append("| Case | Category | Coverage | Drift | Fact Acc. | Relation Acc. | Recovery Acc. | Evidence Cost |")
        lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for record in self.report.records:
            metrics = record.metrics
            lines.append(
                "| "
                f"`{record.case.case_id}` | `{record.case.category}` | `{metrics.semantic_coverage}` | `{metrics.semantic_drift}` | "
                f"`{metrics.fact_accuracy}` | `{metrics.relation_accuracy}` | `{metrics.recovery_accuracy}` | `{metrics.evidence_cost}` |"
            )
        lines.append("")
        lines.append("## 8. Interpretation")
        lines.append("")
        lines.append(
            "The baseline protocol is intended to expose the tradeoff surface between semantic coverage and semantic stability. "
            "It does not claim a universally optimal retention setting."
        )
        lines.append("")
        lines.append("## 9. Limitations")
        lines.append("")
        lines.append("- The case suite is intentionally small and frozen")
        lines.append("- The current report is a single baseline protocol, not a parameter sweep")
        lines.append("- The metrics are meaning-level unit matching, not raw text overlap")
        lines.append("")
        lines.append("## 10. Relation to the Paper")
        lines.append("")
        lines.append(
            "Phase V extends the paper's evidence chain with semantic fidelity measurement after governed transition, "
            "complementing observability, boundary validation, governed optimization, and evidence escalation."
        )
        lines.append("")
        lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
