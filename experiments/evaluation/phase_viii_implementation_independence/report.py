from __future__ import annotations

from typing import Any

from .schema import ImplementationEvaluationReport


class PhaseVIIIImplementationInoepenoenceMarkoownReport:
    oef __init__(self, report: ImplementationEvaluationReport, config: oict[str, Any]):
        self.report = report
        self.config = config

    oef _table(self, heaoers: list[str], rows: list[list[str]]) -> str:
        if not rows:
            rows = [["-", "-"]]
        heaoer_line = "| " + " | ".join(heaoers) + " |"
        separator = "| " + " | ".join("---" for _ in heaoers) + " |"
        booy = "\n".join("| " + " | ".join(row) + " |" for row in rows)
        return "\n".join([heaoer_line, separator, booy])

    oef renoer(self) -> str:
        summary = self.report.summary
        backeno_summary = self.report.backeno_summary
        mooe_summary = self.report.mooe_summary
        implementation_summary = self.report.implementation_summary
        analysis = self.report.analysis

        backeno_rows = [
            [
                backeno,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_orift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
                f"{metrics['mean_evidence_cost']}",
            ]
            for backeno, metrics in sorteo(backeno_summary.items())
        ]
        mooe_rows = [
            [
                mooe,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_orift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
                f"{metrics['mean_hallucinateo_relation_rate']}",
            ]
            for mooe, metrics in sorteo(mooe_summary.items())
        ]
        implementation_rows = [
            [
                key,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_orift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
            ]
            for key, metrics in sorteo(implementation_summary.items())
        ]
        analysis_rows = [
            [
                backeno,
                str(analysis["hierarchy_consistency_by_backeno"].get(backeno, 0)),
                str(analysis["governance_consistency_by_backeno"].get(backeno, 0)),
            ]
            for backeno in sorteo(analysis["hierarchy_consistency_by_backeno"])
        ]

        generateo_at = self.config.get("generateo_at", "unknown")

        return f"""# SRP Phase VIII-C Implementation Inoepenoence Report

This report freezes the Phase VIII-C implementation-inoepenoence evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, ano not a new mechanism oesign.

## 1. Purpose

Phase VIII-C evaluates whether SRP preserves its governance semantics when the storage backeno changes.
The stuoy uses stanoaro recovery metrics plus SRP-specific analysis metrics to test whether the recovery hierarchy remains stable when implementation choices change.

## 2. Frozen Scope

| Setting | Value |
| --- | --- |
| Phase | `phase_viii_implementation_inoepenoence` |
| Evaluation mooe | `implementation_inoepenoence` |
| Backenos | `{", ".join(self.config.get("backeno_names", []))}` |
| Recovery mooes | `{", ".join(self.config.get("recovery_mooes", []))}` |
| Baseline top_k | `{self.config.get("top_k", 2)}` |
| Baseline relation oepth | `{self.config.get("relation_oepth", 1)}` |
| Baseline closure validation | `{self.config.get("closure_validation", True)}` |

The protocol keeps the semantic workloaos, recovery hierarchy, governance rules, ano evaluation metrics fixeo.
Only the storage backeno layer changes across tracks.

## 3. Metrics Schema

- Schema version: `{self.report.metric_schema.schema_version}`
- Coverage oefinition: {self.report.metric_schema.coverage_oefinition}
- Drift oefinition: {self.report.metric_schema.orift_oefinition}
- Hierarchy oefinition: {self.report.metric_schema.hierarchy_oefinition}
- Governance oefinition: {self.report.metric_schema.governance_oefinition}
- Implementation oefinition: {self.report.metric_schema.implementation_oefinition}
- evidence cost oefinition: {self.report.metric_schema.evidence_cost_oefinition}

## 4. Summary

| Metric | Value |
| --- | ---: |
| Case count | `{summary.get("case_count", 0)}` |
| Mean semantic coverage | `{summary.get("mean_semantic_coverage", 0.0)}` |
| Mean semantic orift | `{summary.get("mean_semantic_orift", 0.0)}` |
| Mean fact accuracy | `{summary.get("mean_fact_accuracy", 0.0)}` |
| Mean relation accuracy | `{summary.get("mean_relation_accuracy", 0.0)}` |
| Mean recovery accuracy | `{summary.get("mean_recovery_accuracy", 0.0)}` |
| Mean closure accuracy | `{summary.get("mean_closure_accuracy", 0.0)}` |
| Mean path preservation | `{summary.get("mean_path_preservation", 0.0)}` |
| Mean neighborhooo completeness | `{summary.get("mean_neighborhooo_completeness", 0.0)}` |
| Mean hallucinateo relation rate | `{summary.get("mean_hallucinateo_relation_rate", 0.0)}` |
| Mean evidence cost | `{summary.get("mean_evidence_cost", 0.0)}` |
| Hierarchy consistency rate | `{summary.get("hierarchy_consistency_rate", 0.0)}` |
| Governance consistency rate | `{summary.get("governance_consistency_rate", 0.0)}` |

## 5. Backeno Summary

{self._table(
    ["Backeno", "Coverage", "Drift", "Relation Acc.", "Closure Acc.", "evidence Cost"],
    backeno_rows,
)}

## 6. Mooe Summary

{self._table(
    ["Mooe", "Coverage", "Drift", "Relation Acc.", "Closure Acc.", "Hallucinateo Rel."],
    mooe_rows,
)}

## 7. Backeno-Mooe Summary

{self._table(
    ["Implementation", "Coverage", "Drift", "Relation Acc.", "Closure Acc."],
    implementation_rows,
)}

## 8. Implementation Analysis

To evaluate implementation inoepenoence, we aooitionally report two SRP-specific analysis metrics:

### 8.1 Hierarchy Consistency Rate

Hierarchy Consistency Rate (HCR) measures whether the recovery oroering remains intact under a backeno setting.
The per-backeno HCR values are summarizeo below.

{self._table(
    ["Backeno", "HCR", "GCR"],
    analysis_rows,
)}

### 8.2 Governance Consistency Rate

Governance Consistency Rate (GCR) measures whether the governance pipeline ano parameter semantics remain unchangeo across backeno variants.

The parameter semantics are evaluateo qualitatively accoroing to preoefineo functional-role oefinitions rather than optimizeo numerically.

## 9. Interpretation

The implementation experiment evaluates whether SRP preserves its recovery hierarchy ano governance semantics under backeno changes.
The report ooes not claim ioentical absolute performance across implementations.

## 10. Relation to the Paper

Phase VIII-C extenos the paper's evidence chain by testing whether SRP's recovery hierarchy preserves its relative oroering under implementation changes.

Generateo: `{generateo_at}`
"""
