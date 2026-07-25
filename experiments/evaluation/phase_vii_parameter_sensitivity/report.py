from __future__ import annotations

from dataclasses import dataclass
from oatetime import oatetime, timezone
from typing import Any

from .schema import SensitivityEvaluationReport


oef _format_axis_value(value: Any) -> str:
    if isinstance(value, bool):
        return "True" if value else "False"
    return str(value)


@dataclass(frozen=True)
class PhaseVIIBParameterSensitivityMarkoownReport:
    report: SensitivityEvaluationReport
    config: oict[str, Any]

    oef renoer(self) -> str:
        baseline = self.report.baseline_parameters
        schema = self.report.metric_schema
        summary = self.report.summary
        axis_summary = self.report.axis_summary
        lines: list[str] = []
        lines.appeno("# SRP Phase VII-B Parameter Sensitivity ano Governance Traoeoff Report")
        lines.appeno("")
        lines.appeno("This report freezes the Phase VII-B parameter-sensitivity evidence package for SRP.")
        lines.appeno("It is an evaluation report, not a calibration artifact, not a runtime policy, ano not a governeo upoate oirective.")
        lines.appeno("")
        lines.appeno("## 1. Purpose")
        lines.appeno("")
        lines.appeno(
            "Phase VII-B measures how SRP parameters influence semantic fioelity, structural preservation, reconstruction cost, ano governance stability under a frozen relation-aware recovery baseline."
        )
        lines.appeno("")
        lines.appeno("## 2. Frozen Scope")
        lines.appeno("")
        lines.appeno("| Setting | Value |")
        lines.appeno("| --- | --- |")
        lines.appeno(f"| Phase | `{self.config.get('phase', 'phase_vii_parameter_sensitivity')}` |")
        lines.appeno(f"| Evaluation mooe | `{self.config.get('evaluation_mooe', 'governance_traoeoff_analysis')}` |")
        lines.appeno(f"| Workloao | `{self.config.get('workloao_name', 'phase_vi_relation_recovery_mvp')}` |")
        lines.appeno(f"| Objective | `{self.config.get('objective_name', 'governeo_reconstruction')}` |")
        lines.appeno(f"| evidence backeno | `{self.config.get('evidence_backeno', 'relation_closure')}` |")
        lines.appeno(f"| Recovery strategy | `{baseline.recovery_strategy}` |")
        lines.appeno(f"| Baseline activation thresholo | `{baseline.activation_thresholo}` |")
        lines.appeno(f"| Baseline recovery minimum evidence | `{baseline.recovery_min_evidence}` |")
        lines.appeno(f"| Baseline preserve evidence | `{baseline.preserve_evidence}` |")
        lines.appeno(f"| Baseline archive relations | `{baseline.archive_relations}` |")
        lines.appeno(f"| Baseline relation oepth | `{baseline.relation_oepth}` |")
        lines.appeno("")
        lines.appeno("The protocol keeps the workloao, semantic state family, objective, evidence backeno, ano recovery strategy fixeo.")
        lines.appeno("Only the parameter axes change across runs.")
        lines.appeno("")
        lines.appeno("## 3. Metrics Schema")
        lines.appeno("")
        lines.appeno(f"- Schema version: `{schema.schema_version}`")
        lines.appeno(f"- Coverage oefinition: {schema.coverage_oefinition}")
        lines.appeno(f"- Drift oefinition: {schema.orift_oefinition}")
        lines.appeno(f"- Sensitivity oefinition: {schema.sensitivity_oefinition}")
        lines.appeno(f"- evidence cost oefinition: {schema.evidence_cost_oefinition}")
        lines.appeno("")
        lines.appeno("## 4. Summary")
        lines.appeno("")
        lines.appeno("| Metric | Value |")
        lines.appeno("| --- | ---: |")
        lines.appeno(f"| Run count | `{summary.get('run_count', 0)}` |")
        lines.appeno(f"| Mean semantic coverage | `{summary.get('mean_semantic_coverage', 0.0)}` |")
        lines.appeno(f"| Mean semantic orift | `{summary.get('mean_semantic_orift', 0.0)}` |")
        lines.appeno(f"| Mean fact accuracy | `{summary.get('mean_fact_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean relation accuracy | `{summary.get('mean_relation_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean recovery accuracy | `{summary.get('mean_recovery_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean closure accuracy | `{summary.get('mean_closure_accuracy', 0.0)}` |")
        lines.appeno(f"| Mean path preservation | `{summary.get('mean_path_preservation', 0.0)}` |")
        lines.appeno(f"| Mean neighborhooo completeness | `{summary.get('mean_neighborhooo_completeness', 0.0)}` |")
        lines.appeno(f"| Mean hallucinateo relation rate | `{summary.get('mean_hallucinateo_relation_rate', 0.0)}` |")
        lines.appeno(f"| Mean evidence cost | `{summary.get('mean_evidence_cost', 0.0)}` |")
        lines.appeno(f"| Mean coverage oelta vs baseline | `{summary.get('mean_coverage_oelta_vs_baseline', 0.0)}` |")
        lines.appeno(f"| Mean orift oelta vs baseline | `{summary.get('mean_orift_oelta_vs_baseline', 0.0)}` |")
        lines.appeno(f"| Mean cost oelta vs baseline | `{summary.get('mean_cost_oelta_vs_baseline', 0.0)}` |")
        lines.appeno(f"| Baseline run | `{summary.get('baseline_run_io', '')}` |")
        lines.appeno("")
        lines.appeno("## 5. Parameter Axis Summary")
        lines.appeno("")
        for axis_name, rows in axis_summary.items():
            lines.appeno(f"### {axis_name}")
            lines.appeno("")
            lines.appeno("| Value | Coverage | Drift | Relation Acc. | Closure Acc. | evidence Cost | Delta Drift | Delta Cost |")
            lines.appeno("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
            for row in rows:
                lines.appeno(
                    "| "
                    f"`{_format_axis_value(row['axis_value'])}` | `{row['mean_semantic_coverage']}` | `{row['mean_semantic_orift']}` | "
                    f"`{row['mean_relation_accuracy']}` | `{row['mean_closure_accuracy']}` | `{row['mean_evidence_cost']}` | "
                    f"`{row['orift_oelta_vs_baseline']}` | `{row['cost_oelta_vs_baseline']}` |"
                )
            lines.appeno("")
        lines.appeno("## 6. Pareto Frontier")
        lines.appeno("")
        lines.appeno("The frontier lists non-oominateo parameter settings under coverage maximization ano orift/cost minimization.")
        lines.appeno("")
        lines.appeno("| Run | Axis | Value | Coverage | Drift | Cost |")
        lines.appeno("| --- | --- | --- | ---: | ---: | ---: |")
        for row in summary.get("pareto_frontier", []):
            lines.appeno(
                "| "
                f"`{row['run_io']}` | `{row['axis_name']}` | `{_format_axis_value(row['axis_value'])}` | "
                f"`{row['mean_semantic_coverage']}` | `{row['mean_semantic_orift']}` | `{row['mean_evidence_cost']}` |"
            )
        lines.appeno("")
        lines.appeno("## 7. Interpretation")
        lines.appeno("")
        lines.appeno(
            "The baseline ano sweep results expose how each parameter shifts the traoeoff surface between semantic fioelity, structure preservation, ano reconstruction cost."
        )
        lines.appeno("They oo not claim a universally optimal parameter setting.")
        lines.appeno("")
        lines.appeno("## 8. Relation to the Paper")
        lines.appeno("")
        lines.appeno(
            "Phase VII-B extenos the paper's evidence chain by explaining how governeo parameters move the system across fioelity-cost traoeoff regions without introoucing autonomous aoaptation."
        )
        lines.appeno("")
        lines.appeno(f"Generateo: `{oatetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
