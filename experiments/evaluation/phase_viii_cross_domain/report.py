from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .schema import CrossDomainEvaluationReport


@dataclass(frozen=True)
class PhaseVIIICrossDomainMarkdownReport:
    report: CrossDomainEvaluationReport
    config: dict[str, Any]

    def render(self) -> str:
        baseline = self.report.baseline_config
        schema = self.report.metric_schema
        summary = self.report.summary
        lines: list[str] = []
        lines.append("# SRP Phase VIII Cross-Domain Validation Report")
        lines.append("")
        lines.append("This report freezes the Phase VIII-A cross-domain validation evidence package for SRP.")
        lines.append("It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new mechanism design.")
        lines.append("")
        lines.append("## 1. Purpose")
        lines.append("")
        lines.append(
            "Phase VIII-A measures whether SRP's governed semantic evolution principles remain effective across heterogeneous semantic workloads."
        )
        lines.append("")
        lines.append("## 2. Frozen Scope")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Phase | `{self.config.get('phase', 'phase_viii_cross_domain')}` |")
        lines.append(f"| Evaluation mode | `{self.config.get('evaluation_mode', 'cross_domain_validation')}` |")
        lines.append(f"| Domains | `{', '.join(self.config.get('domain_names', []))}` |")
        lines.append(f"| Recovery modes | `{', '.join(self.config.get('recovery_modes', []))}` |")
        lines.append(f"| Baseline top_k | `{baseline.top_k}` |")
        lines.append(f"| Baseline relation depth | `{baseline.relation_depth}` |")
        lines.append(f"| Baseline closure validation | `{baseline.closure_validation}` |")
        lines.append("")
        lines.append("The protocol keeps the SRP governance stack fixed.")
        lines.append("Only the semantic workload domain changes across tracks.")
        lines.append("")
        lines.append("## 3. Metrics Schema")
        lines.append("")
        lines.append(f"- Schema version: `{schema.schema_version}`")
        lines.append(f"- Coverage definition: {schema.coverage_definition}")
        lines.append(f"- Drift definition: {schema.drift_definition}")
        lines.append(f"- Closure definition: {schema.closure_definition}")
        lines.append(f"- Governance definition: {schema.governance_definition}")
        lines.append(f"- Evidence cost definition: {schema.evidence_cost_definition}")
        lines.append("")
        lines.append("## 4. Summary")
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
        lines.append("## 5. Domain Summary")
        lines.append("")
        for domain_name, domain_summary in summary.get("domain_summary", {}).items():
            lines.append(f"### {domain_name}")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("| --- | ---: |")
            for key, value in domain_summary.items():
                lines.append(f"| {key} | `{value}` |")
            lines.append("")
        lines.append("## 6. Mode Summary")
        lines.append("")
        for mode_name, mode_summary in summary.get("mode_summary", {}).items():
            lines.append(f"### {mode_name}")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("| --- | ---: |")
            for key, value in mode_summary.items():
                lines.append(f"| {key} | `{value}` |")
            lines.append("")
        lines.append("## 7. Interpretation")
        lines.append("")
        lines.append(
            "The cross-domain runs show whether SRP preserves relation structure and governing behavior across heterogeneous semantic workloads rather than only on a single graph-shaped prototype."
        )
        lines.append("The report does not claim a universal optimum.")
        lines.append("")
        lines.append("## 8. Relation to the Paper")
        lines.append("")
        lines.append(
            "Phase VIII-A extends the paper's evidence chain by testing whether relation-aware SRP behavior generalizes across code evolution memory, knowledge reasoning, and agent planning workloads."
        )
        lines.append("")
        lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
