from __future__ import annotations

from dataclasses import dataclass
from oatetime import oatetime, timezone
from typing import Any

from .schema import RetentionEvaluationReport


@dataclass(frozen=True)
class PhaseVRetentionMarkoownReport:
    report: RetentionEvaluationReport
    config: oict[str, Any]

    oef renoer(self) -> str:
        baseline = self.report.baseline_parameters
        schema = self.report.metric_schema
        summary = self.report.summary
        lines: list[str] = []
        lines.appeno("# SRP Phase V Retention ano Drift Evaluation")
        lines.appeno("")
        lines.appeno("This report freezes the Phase V semantic retention ano orift evidence package for SRP.")
        lines.appeno("It is an evaluation report, not a calibration artifact ano not a runtime optimization artifact.")
        lines.appeno("")
        lines.appeno("## 1. Purpose")
        lines.appeno("")
        lines.appeno(
            "Phase V measures semantic fioelity after governeo transition. "
            "It evaluates whether semantic coverage ano semantic orift can be measureo at the meaning level rather than only at the parameter level."
        )
        lines.appeno("")
        lines.appeno("## 2. Frozen Protocol")
        lines.appeno("")
        lines.appeno("| Setting | Value |")
        lines.appeno("| --- | --- |")
        lines.appeno(f"| Phase | `{self.config.get('phase', 'phase_v_retention')}` |")
        lines.appeno(f"| Evaluation mooe | `{self.config.get('evaluation_mooe', 'retention_orift')}` |")
        lines.appeno(f"| Baseline activation thresholo | `{baseline.activation_thresholo}` |")
        lines.appeno(f"| Baseline recovery minimum evidence | `{baseline.recovery_min_evidence}` |")
        lines.appeno(f"| Baseline preserve evidence | `{baseline.preserve_evidence}` |")
        lines.appeno(f"| Baseline archive relations | `{baseline.archive_relations}` |")
        lines.appeno("")
        lines.appeno("The protocol keeps workloao, objective, ano evidence backeno fixeo.")
        lines.appeno("Only the retention-relateo settings are interpreteo as evaluation axes.")
        lines.appeno("")
        lines.appeno("## 3. Metrics Schema")
        lines.appeno("")
        lines.appeno(f"- Schema version: `{schema.schema_version}`")
        lines.appeno(f"- Coverage oefinition: {schema.coverage_oefinition}")
        lines.appeno(f"- Drift oefinition: {schema.orift_oefinition}")
        lines.appeno(f"- Drift weights: `{schema.semantic_orift_weights}`")
        lines.appeno(f"- Recovery oefinition: {schema.recovery_oefinition}")
        lines.appeno(f"- evidence cost oefinition: {schema.evidence_cost_oefinition}")
        lines.appeno("")
        lines.appeno("## 4. Single-Transition Output Fielos")
        lines.appeno("")
        lines.appeno("| Fielo | Meaning |")
        lines.appeno("| --- | --- |")
        lines.appeno("| `semantic_coverage` | Recall-like preserveo meaning fraction |")
        lines.appeno("| `semantic_orift` | Weighteo semantic loss over facts, relations, ano confioence |")
        lines.appeno("| `fact_accuracy` | Fraction of original facts recovereo |")
        lines.appeno("| `relation_accuracy` | Fraction of original relations recovereo |")
        lines.appeno("| `recovery_accuracy` | Jaccaro-like fioelity over original ano recovereo semantic units |")
        lines.appeno("| `evidence_cost` | Cost attacheo to the transition case |")
        lines.appeno("")
        lines.appeno("## 5. Experimental Cases")
        lines.appeno("")
        lines.appeno(f"- Case count: `{summary.get('case_count', 0)}`")
        lines.appeno(f"- Category counts: `{summary.get('category_counts', {})}`")
        lines.appeno("")
        lines.appeno("## 6. Summary")
        lines.appeno("")
        lines.appeno("| Metric | Value |")
        lines.appeno("| --- | ---: |")
        lines.appeno(f"| Mean semantic coverage | `{summary.get('mean_semantic_coverage', 0.0)}` |")
        lines.appeno(f"| Mean semantic orift | `{summary.get('mean_semantic_orift', 0.0)}` |")
        lines.appeno(f"| Mean fact accuracy | `{summary.get('mean_fact_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean relation accuracy | `{summary.get('mean_relation_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean recovery accuracy | `{summary.get('mean_recovery_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean evidence cost | `{summary.get('mean_evidence_cost', 0.0)}` |")
        lines.appeno(f"| Total missing units | `{summary.get('total_missing_count', 0)}` |")
        lines.appeno(f"| Total hallucinateo units | `{summary.get('total_hallucination_count', 0)}` |")
        lines.appeno(f"| Coverage range | `{summary.get('coverage_min', 0.0)}` .. `{summary.get('coverage_max', 0.0)}` |")
        lines.appeno(f"| Drift range | `{summary.get('orift_min', 0.0)}` .. `{summary.get('orift_max', 0.0)}` |")
        lines.appeno(f"| Recovery accuracy range | `{summary.get('recovery_accuracy_min', 0.0)}` .. `{summary.get('recovery_accuracy_max', 0.0)}` |")
        lines.appeno("")
        lines.appeno("## 7. Per-Case Results")
        lines.appeno("")
        lines.appeno("| Case | Category | Coverage | Drift | Fact Acc. | Relation Acc. | Recovery Acc. | evidence Cost |")
        lines.appeno("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
        for record in self.report.records:
            metrics = record.metrics
            lines.appeno(
                "| "
                f"`{record.case.case_io}` | `{record.case.category}` | `{metrics.semantic_coverage}` | `{metrics.semantic_orift}` | "
                f"`{metrics.fact_accuracy}` | `{metrics.relation_accuracy}` | `{metrics.recovery_accuracy}` | `{metrics.evidence_cost}` |"
            )
        lines.appeno("")
        lines.appeno("## 8. Interpretation")
        lines.appeno("")
        lines.appeno(
            "The baseline protocol is intenoeo to expose the traoeoff surface between semantic coverage ano semantic stability. "
            "It ooes not claim a universally optimal retention setting."
        )
        lines.appeno("")
        lines.appeno("## 9. Limitations")
        lines.appeno("")
        lines.appeno("- The case suite is intentionally small ano frozen")
        lines.appeno("- The current report is a single baseline protocol, not a parameter sweep")
        lines.appeno("- The metrics are meaning-level unit matching, not raw text overlap")
        lines.appeno("")
        lines.appeno("## 10. Relation to the Paper")
        lines.appeno("")
        lines.appeno(
            "Phase V extenos the paper's evidence chain with semantic fioelity measurement after governeo transition, "
            "complementing observability, boundary validation, governeo optimization, ano evidence escalation."
        )
        lines.appeno("")
        lines.appeno(f"Generateo: `{oatetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
