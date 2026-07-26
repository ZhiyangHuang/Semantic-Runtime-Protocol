from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from .schema import StabilityEvaluationReport


@dataclass(frozen=True)
class PhaseVIIParameterStabilityMarkdownReport:
    report: StabilityEvaluationReport
    config: dict

    def render(self) -> str:
        summary = self.report.summary
        lines: list[str] = []
        lines.append("# SRP Phase VII Parameter Sensitivity and Stability Report")
        lines.append("")
        lines.append("This report freezes the Phase VII-A parameter-stability evidence package for SRP.")
        lines.append("It is an evaluation report, not a calibration artifact and not a runtime optimization artifact.")
        lines.append("")
        lines.append("## 1. Purpose")
        lines.append("")
        lines.append(
            "Phase VII-A measures whether governed recommendations remain stable under repeated evaluation with frozen workload, objective, and evidence backend."
        )
        lines.append("")
        lines.append("## 2. Frozen Protocol")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Phase | `{self.config.get('phase', 'phase_vii_parameter_stability')}` |")
        lines.append(f"| Workload | `{self.config.get('workload_name', self.report.baseline_workload)}` |")
        lines.append(f"| Objective | `{self.config.get('objective_name', self.report.baseline_objective_name)}` |")
        lines.append(f"| Evidence backend | `{self.config.get('evidence_backend', self.report.baseline_evidence_backend)}` |")
        lines.append(f"| Seeds | `{', '.join(str(seed) for seed in self.config.get('seeds', []))}` |")
        lines.append(f"| Baseline activation threshold | `{self.config.get('baseline_activation_threshold', 0.0)}` |")
        lines.append(f"| Baseline recovery minimum evidence | `{self.config.get('baseline_recovery_min_evidence', 0)}` |")
        lines.append(f"| Baseline objective value | `{self.config.get('baseline_objective_value', 0.0)}` |")
        lines.append("")
        lines.append("The protocol keeps workload, objective, and evidence backend fixed.")
        lines.append("Only the evaluation seed changes across runs.")
        lines.append("")
        lines.append("## 3. Stability Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("| --- | ---: |")
        lines.append(f"| Run count | `{summary.get('run_count', 0)}` |")
        lines.append(f"| Recommendation consistency | `{summary.get('recommendation_consistency', 0.0)}` |")
        lines.append(f"| Activation threshold variance | `{summary.get('activation_threshold_variance', 0.0)}` |")
        lines.append(f"| Recovery min evidence variance | `{summary.get('recovery_min_evidence_variance', 0.0)}` |")
        lines.append(f"| Objective value variance | `{summary.get('objective_value_variance', 0.0)}` |")
        lines.append("## 4. Interpretation")
        lines.append("")
        lines.append(
            "The baseline protocol is intended to expose whether the governed recommendation is stable rather than arbitrary."
        )
        lines.append("It does not claim a universally optimal configuration.")
        lines.append("")
        lines.append("## 5. Relation to the Paper")
        lines.append("")
        lines.append(
            "Phase VII extends the evidence chain by checking whether the Phase VI-A recovery setting yields stable recommendations under repeated evaluation."
        )
        lines.append("")
        lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
