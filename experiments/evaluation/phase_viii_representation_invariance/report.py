from __future__ import annotations

from typing import Any

from .schema import RepresentationEvaluationReport


class PhaseVIIIRepresentationInvarianceMarkdownReport:
    def __init__(self, report: RepresentationEvaluationReport, config: dict[str, Any]):
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
        encoder_summary = self.report.encoder_summary
        parser_summary = self.report.parser_summary
        mode_summary = self.report.mode_summary
        analysis = self.report.analysis
        representation_summary = self.report.representation_summary

        encoder_rows = [
            [
                encoder,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_drift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
            ]
            for encoder, metrics in sorted(encoder_summary.items())
        ]
        parser_rows = [
            [
                parser,
                f"{metrics['mean_semantic_coverage']}",
                f"{metrics['mean_semantic_drift']}",
                f"{metrics['mean_relation_accuracy']}",
                f"{metrics['mean_closure_accuracy']}",
            ]
            for parser, metrics in sorted(parser_summary.items())
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
        representation_rows = [
            [
                key,
                str(analysis["hierarchy_consistency_by_representation"].get(key, 0)),
                str(analysis["governance_consistency_by_representation"].get(key, 0)),
            ]
            for key in sorted(analysis["hierarchy_consistency_by_representation"])
        ]

        generated_at = self.config.get("generated_at", "unknown")

        return f"""# SRP Phase VIII-B Representation Invariance Report

This report freezes the Phase VIII-B representation-invariance evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new mechanism design.

## 1. Purpose

Phase VIII-B evaluates whether SRP preserves its governance semantics under representation changes.
The study uses standard recovery metrics plus SRP-specific analysis metrics to test whether the recovery hierarchy remains stable when encoder and parser choices change.

## 2. Frozen Scope

| Setting | Value |
| --- | --- |
| Phase | `phase_viii_representation_invariance` |
| Evaluation mode | `representation_invariance` |
| Encoders | `{", ".join(self.config.get("encoder_names", []))}` |
| Parsers | `{", ".join(self.config.get("parser_names", []))}` |
| Recovery modes | `{", ".join(self.config.get("recovery_modes", []))}` |
| Baseline top_k | `{self.config.get("top_k", 2)}` |
| Baseline relation depth | `{self.config.get("relation_depth", 1)}` |
| Baseline closure validation | `{self.config.get("closure_validation", True)}` |

The protocol keeps the semantic workloads, recovery hierarchy, governance rules, and evaluation metrics fixed.
Only the representation layer changes across tracks.

## 3. Metrics Schema

- Schema version: `{self.report.metric_schema.schema_version}`
- Coverage definition: {self.report.metric_schema.coverage_definition}
- Drift definition: {self.report.metric_schema.drift_definition}
- Hierarchy definition: {self.report.metric_schema.hierarchy_definition}
- Governance definition: {self.report.metric_schema.governance_definition}
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

## 5. Encoder Summary

{self._table(
    ["Encoder", "Coverage", "Drift", "Relation Acc.", "Closure Acc."],
    encoder_rows,
)}

## 6. Parser Summary

{self._table(
    ["Parser", "Coverage", "Drift", "Relation Acc.", "Closure Acc."],
    parser_rows,
)}

## 7. Mode Summary

{self._table(
    ["Mode", "Coverage", "Drift", "Relation Acc.", "Closure Acc.", "Hallucinated Rel."],
    mode_rows,
)}

## 8. Representation Summary

{self._table(
    ["Representation", "Coverage", "Drift", "Relation Acc.", "Closure Acc."],
    [
        [
            key,
            f"{metrics['mean_semantic_coverage']}",
            f"{metrics['mean_semantic_drift']}",
            f"{metrics['mean_relation_accuracy']}",
            f"{metrics['mean_closure_accuracy']}",
        ]
        for key, metrics in sorted(representation_summary.items())
    ],
)}

## 9. Representation Analysis

To evaluate representation invariance, we additionally report two SRP-specific analysis metrics:

### 8.1 Hierarchy Consistency Rate

Hierarchy Consistency Rate (HCR) measures whether the recovery ordering remains intact under a representation setting.
The per-representation HCR values are summarized below.

{self._table(
    ["Representation", "HCR", "GCR"],
    representation_rows,
)}

### 8.2 Governance Consistency Rate

Governance Consistency Rate (GCR) measures whether the governance pipeline and parameter semantics remain unchanged across representation variants.

The parameter semantics are evaluated qualitatively according to predefined functional-role definitions rather than optimized numerically.

## 10. Interpretation

The representation experiment evaluates whether SRP preserves its recovery hierarchy and governance semantics under encoder and parser changes.
The report does not claim identical absolute performance across representations.

## 11. Relation to the Paper

Phase VIII-B extends the paper's evidence chain by testing whether SRP's recovery hierarchy preserves its relative ordering under representation changes.

Generated: `{generated_at}`
"""
