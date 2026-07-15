from __future__ import annotations

from typing import Any

from .schema import ImplementationEvaluationReport


class PhaseVIIIImplementationIndependenceMarkdownReport:
    def __init__(self, report: ImplementationEvaluationReport, config: dict[str, Any]):
        self.report = report
        self.config = config

    def _table(self, headers: list[str], rows: list[list[str]]) -> str:
        if not rows:
            rows = [["-", "-"]]
        header_line = "| " + " | ".join(headers) + " |"
        separator = "| " + " | ".join("---" for _ in headers) + " |"
        body = "\n".join("| " + " | ".join(row) + " |" for row in rows)
        return "\n".join([header_line, separator, body])

    def render(self) -> str:
        summary = self.report.summary
        backend_summary = self.report.backend_summary
        mode_summary = self.report.mode_summary
        implementation_summary = self.report.implementation_summary
        analysis = self.report.analysis

        backend_rows = [
            [
                backend,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_drift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
                f"{metrics['mean_evidence_cost']}",
            ]
            for backend, metrics in sorted(backend_summary.items())
        ]
        mode_rows = [
            [
                mode,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_drift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
                f"{metrics['mean_hallucinated_relation_rate']}",
            ]
            for mode, metrics in sorted(mode_summary.items())
        ]
        implementation_rows = [
            [
                key,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_drift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
            ]
            for key, metrics in sorted(implementation_summary.items())
        ]
        analysis_rows = [
            [
                backend,
                str(analysis["hierarchy_consistency_by_backend"].get(backend, 0)),
                str(analysis["governance_consistency_by_backend"].get(backend, 0)),
            ]
            for backend in sorted(analysis["hierarchy_consistency_by_backend"])
        ]

        generated_at = self.config.get("generated_at", "unknown")

        return f"""# SRP Phase VIII-C Implementation Independence Report

This report freezes the Phase VIII-C implementation-independence evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new mechanism design.

## 1. Purpose

Phase VIII-C evaluates whether SRP preserves its governance semantics when the storage backend changes.
The study uses standard recovery metrics plus SRP-specific analysis metrics to test whether the recovery hierarchy remains stable when implementation choices change.

## 2. Frozen Scope

| Setting | Value |
| --- | --- |
| Phase | `phase_viii_implementation_independence` |
| Evaluation mode | `implementation_independence` |
| Backends | `{", ".join(self.config.get("backend_names", []))}` |
| Recovery modes | `{", ".join(self.config.get("recovery_modes", []))}` |
| Baseline top_k | `{self.config.get("top_k", 2)}` |
| Baseline relation depth | `{self.config.get("relation_depth", 1)}` |
| Baseline closure validation | `{self.config.get("closure_validation", True)}` |

The protocol keeps the semantic workloads, recovery hierarchy, governance rules, and evaluation metrics fixed.
Only the storage backend layer changes across tracks.

## 3. Metrics Schema

- Schema version: `{self.report.metric_schema.schema_version}`
- Coverage definition: {self.report.metric_schema.coverage_definition}
- Drift definition: {self.report.metric_schema.drift_definition}
- Hierarchy definition: {self.report.metric_schema.hierarchy_definition}
- Governance definition: {self.report.metric_schema.governance_definition}
- Implementation definition: {self.report.metric_schema.implementation_definition}
- Evidence cost definition: {self.report.metric_schema.evidence_cost_definition}

## 4. Summary

| Metric | Value |
| --- | ---: |
| Case count | `{summary.get("case_count", 0)}` |
| Mean semantic coverage | `{summary.get("mean_semantic_coverage", 0.0)}` |
| Mean semantic drift | `{summary.get("mean_semantic_drift", 0.0)}` |
| Mean fact accuracy | `{summary.get("mean_fact_accuracy", 0.0)}` |
| Mean relation accuracy | `{summary.get("mean_relation_accuracy", 0.0)}` |
| Mean recovery accuracy | `{summary.get("mean_recovery_accuracy", 0.0)}` |
| Mean closure accuracy | `{summary.get("mean_closure_accuracy", 0.0)}` |
| Mean path preservation | `{summary.get("mean_path_preservation", 0.0)}` |
| Mean neighborhood completeness | `{summary.get("mean_neighborhood_completeness", 0.0)}` |
| Mean hallucinated relation rate | `{summary.get("mean_hallucinated_relation_rate", 0.0)}` |
| Mean evidence cost | `{summary.get("mean_evidence_cost", 0.0)}` |
| Hierarchy consistency rate | `{summary.get("hierarchy_consistency_rate", 0.0)}` |
| Governance consistency rate | `{summary.get("governance_consistency_rate", 0.0)}` |

## 5. Backend Summary

{self._table(
    ["Backend", "Coverage", "Drift", "Relation Acc.", "Closure Acc.", "Evidence Cost"],
    backend_rows,
)}

## 6. Mode Summary

{self._table(
    ["Mode", "Coverage", "Drift", "Relation Acc.", "Closure Acc.", "Hallucinated Rel."],
    mode_rows,
)}

## 7. Backend-Mode Summary

{self._table(
    ["Implementation", "Coverage", "Drift", "Relation Acc.", "Closure Acc."],
    implementation_rows,
)}

## 8. Implementation Analysis

To evaluate implementation independence, we additionally report two SRP-specific analysis metrics:

### 8.1 Hierarchy Consistency Rate

Hierarchy Consistency Rate (HCR) measures whether the recovery ordering remains intact under a backend setting.
The per-backend HCR values are summarized below.

{self._table(
    ["Backend", "HCR", "GCR"],
    analysis_rows,
)}

### 8.2 Governance Consistency Rate

Governance Consistency Rate (GCR) measures whether the governance pipeline and parameter semantics remain unchanged across backend variants.

The parameter semantics are evaluated qualitatively according to predefined functional-role definitions rather than optimized numerically.

## 9. Interpretation

The implementation experiment evaluates whether SRP preserves its recovery hierarchy and governance semantics under backend changes.
The report does not claim identical absolute performance across implementations.

## 10. Relation to the Paper

Phase VIII-C extends the paper's evidence chain by testing whether SRP's recovery hierarchy preserves its relative ordering under implementation changes.

Generated: `{generated_at}`
"""
