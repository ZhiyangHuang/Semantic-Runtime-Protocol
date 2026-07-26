from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import PhaseVRetentionConfig, load_phase_v_retention_config

from .metrics import evaluate_retention_case, summarize_retention_results
from .report import PhaseVRetentionMarkdownReport
from .schema import (
    RetentionCase,
    RetentionEvaluationReport,
    RetentionMetricSchema,
    RetentionParameters,
    SemanticFact,
    SemanticRelation,
    SemanticStateSnapshot,
)


def build_retention_cases(config: PhaseVRetentionConfig | None = None) -> list[RetentionCase]:
    config = config or load_phase_v_retention_config()
    baseline = RetentionParameters(
        activation_threshold=config.baseline_activation_threshold,
        recovery_min_evidence=config.baseline_recovery_min_evidence,
        preserve_evidence=config.baseline_preserve_evidence,
        archive_relations=config.baseline_archive_relations,
    )

    return [
        RetentionCase(
            case_id="retention_case_1_exact",
            category="exact_preservation",
            source_state=SemanticStateSnapshot(
                state_id="source_exact",
                facts=(
                    SemanticFact("Alice", "prefers", "Python", confidence=0.95, critical=True),
                    SemanticFact("Alice", "works_at", "OpenAI", confidence=0.93, critical=True),
                    SemanticFact("Alice", "shares_notes_with", "Bob", confidence=0.80),
                ),
                relations=(
                    SemanticRelation("Alice", "collaborates_with", "Bob", confidence=0.90, critical=True),
                ),
                evidence_refs=("source:1", "source:2", "source:3", "source:4"),
                notes="Exact preservation baseline.",
            ),
            recovered_state=SemanticStateSnapshot(
                state_id="recovered_exact",
                facts=(
                    SemanticFact("Alice", "prefers", "Python", confidence=0.95, critical=True),
                    SemanticFact("Alice", "works_at", "OpenAI", confidence=0.93, critical=True),
                    SemanticFact("Alice", "shares_notes_with", "Bob", confidence=0.80),
                ),
                relations=(
                    SemanticRelation("Alice", "collaborates_with", "Bob", confidence=0.90, critical=True),
                ),
                evidence_refs=("recovered:1", "recovered:2", "recovered:3", "recovered:4"),
                notes="Recovered state matches source semantics.",
            ),
            parameters=baseline,
            evidence_cost=1.0,
            notes="No semantic loss.",
        ),
        RetentionCase(
            case_id="retention_case_2_fact_loss",
            category="fact_loss",
            source_state=SemanticStateSnapshot(
                state_id="source_fact_loss",
                facts=(
                    SemanticFact("Alice", "prefers", "Python", confidence=0.92, critical=True),
                    SemanticFact("Alice", "works_at", "OpenAI", confidence=0.90, critical=True),
                    SemanticFact("Alice", "keeps", "a private notebook", confidence=0.70),
                    SemanticFact("Alice", "reviews", "transition logs nightly", confidence=0.65),
                ),
                relations=(
                    SemanticRelation("Alice", "collaborates_with", "Bob", confidence=0.88, critical=True),
                ),
                evidence_refs=("source:1", "source:2", "source:3", "source:4", "source:5"),
                notes="A low-frequency fact should not dominate retention.",
            ),
            recovered_state=SemanticStateSnapshot(
                state_id="recovered_fact_loss",
                facts=(
                    SemanticFact("Alice", "prefers", "Python", confidence=0.92, critical=True),
                    SemanticFact("Alice", "works_at", "OpenAI", confidence=0.90, critical=True),
                    SemanticFact("Alice", "keeps", "a private notebook", confidence=0.58),
                ),
                relations=(
                    SemanticRelation("Alice", "collaborates_with", "Bob", confidence=0.74, critical=True),
                ),
                evidence_refs=("recovered:1", "recovered:2", "recovered:3", "recovered:4"),
                notes="One noncritical fact was lost during retention.",
            ),
            parameters=baseline,
            evidence_cost=1.2,
            notes="Shows recall loss without relation damage.",
        ),
        RetentionCase(
            case_id="retention_case_3_relation_drift",
            category="relation_drift",
            source_state=SemanticStateSnapshot(
                state_id="source_relation_drift",
                facts=(
                    SemanticFact("SRP", "validates", "boundaries", confidence=0.95, critical=True),
                    SemanticFact("SRP", "ranks", "candidates", confidence=0.92, critical=True),
                    SemanticFact("Governance", "approves", "execution", confidence=0.93, critical=True),
                ),
                relations=(
                    SemanticRelation("validation", "precedes", "optimization", confidence=0.94, critical=True),
                ),
                evidence_refs=("source:1", "source:2", "source:3", "source:4"),
                notes="Boundary order should remain stable.",
            ),
            recovered_state=SemanticStateSnapshot(
                state_id="recovered_relation_drift",
                facts=(
                    SemanticFact("SRP", "validates", "boundaries", confidence=0.95, critical=True),
                    SemanticFact("SRP", "ranks", "candidates", confidence=0.92, critical=True),
                    SemanticFact("Governance", "approves", "execution", confidence=0.93, critical=True),
                ),
                relations=(
                    SemanticRelation("optimization", "precedes", "validation", confidence=0.60, critical=True),
                ),
                evidence_refs=("recovered:1", "recovered:2", "recovered:3", "recovered:4"),
                notes="Relation direction was inverted.",
            ),
            parameters=baseline,
            evidence_cost=1.5,
            notes="Captures relation drift with preserved facts.",
        ),
        RetentionCase(
            case_id="retention_case_4_boundary_hallucination",
            category="boundary_hallucination",
            source_state=SemanticStateSnapshot(
                state_id="source_boundary_hallucination",
                facts=(
                    SemanticFact("Evidence", "strengthens", "verification", confidence=0.90, critical=True),
                    SemanticFact("Authority", "remains", "separate", confidence=0.93, critical=True),
                    SemanticFact("Runtime", "does_not", "self_modify", confidence=0.96, critical=True),
                ),
                relations=(
                    SemanticRelation("evidence", "supports", "verification", confidence=0.91, critical=True),
                    SemanticRelation("governance", "authorizes", "execution", confidence=0.92, critical=True),
                ),
                evidence_refs=("source:1", "source:2", "source:3", "source:4", "source:5"),
                notes="Boundary-sensitive case with execution authority.",
            ),
            recovered_state=SemanticStateSnapshot(
                state_id="recovered_boundary_hallucination",
                facts=(
                    SemanticFact("Evidence", "strengthens", "verification", confidence=0.90, critical=True),
                    SemanticFact("Authority", "remains", "separate", confidence=0.93, critical=True),
                    SemanticFact("Runtime", "does_not", "self_modify", confidence=0.96, critical=True),
                    SemanticFact("Runtime", "may", "self_modify", confidence=0.40),
                ),
                relations=(
                    SemanticRelation("evidence", "supports", "verification", confidence=0.91, critical=True),
                ),
                evidence_refs=("recovered:1", "recovered:2", "recovered:3", "recovered:4", "recovered:5"),
                notes="Recovered state keeps most meaning but adds a hallucinated transition claim.",
            ),
            parameters=baseline,
            evidence_cost=1.8,
            notes="Boundary-adjacent case with extra recovered content.",
        ),
    ]


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def run_phase_v_retention(config: PhaseVRetentionConfig | None = None) -> dict[str, Any]:
    config = config or load_phase_v_retention_config()
    cases = build_retention_cases(config)
    records = [evaluate_retention_case(case, weights=config.semantic_drift_weights) for case in cases]
    summary = summarize_retention_results(records)
    report = RetentionEvaluationReport(
        report_id=f"phase_v_retention_{len(records)}",
        status="evaluated",
        baseline_parameters=RetentionParameters(
            activation_threshold=config.baseline_activation_threshold,
            recovery_min_evidence=config.baseline_recovery_min_evidence,
            preserve_evidence=config.baseline_preserve_evidence,
            archive_relations=config.baseline_archive_relations,
        ),
        metric_schema=RetentionMetricSchema(semantic_drift_weights=config.semantic_drift_weights),
        records=records,
        summary=summary,
    )
    markdown = PhaseVRetentionMarkdownReport(report=report, config=asdict(config)).render()
    return {
        "config": asdict(config),
        "report": report.as_dict(),
        "markdown": markdown,
        "cases": [case.as_dict() for case in cases],
    }


def write_phase_v_retention_outputs(
    output_dir: str | Path,
    config: PhaseVRetentionConfig | None = None,
) -> dict[str, Any]:
    config = config or load_phase_v_retention_config()
    outputs = run_phase_v_retention(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report = outputs["report"]
    records = report.get("records", [])
    summary = report.get("summary", {})
    baseline = report.get("baseline_parameters", {})

    records_csv = output_path / "retention_records.csv"
    records_jsonl = output_path / "retention_records.jsonl"
    summary_json = output_path / "retention_summary.json"
    metadata_json = output_path / "metadata.json"
    report_md = output_path / "retention_report.md"
    report_json = output_path / "retention_report.json"
    root_report = Path(__file__).resolve().parents[3] / "SRP_PHASE_V_RETENTION_REPORT.md"

    if records:
        fieldnames = [
            "case_id",
            "category",
            "source_state_id",
            "recovered_state_id",
            "semantic_coverage",
            "semantic_drift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "fact_drift",
            "relation_drift",
            "confidence_drift",
            "evidence_cost",
            "original_fact_count",
            "original_relation_count",
            "recovered_fact_count",
            "recovered_relation_count",
            "matched_fact_count",
            "matched_relation_count",
            "missing_count",
            "hallucination_count",
            "original_unit_count",
            "recovered_unit_count",
            "matched_unit_count",
            "activation_threshold",
            "recovery_min_evidence",
            "preserve_evidence",
            "archive_relations",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                case = record["case"]
                metrics = record["metrics"]
                writer.writerow(
                    {
                        "case_id": case["case_id"],
                        "category": case["category"],
                        "source_state_id": case["source_state"]["state_id"],
                        "recovered_state_id": case["recovered_state"]["state_id"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_drift": metrics["semantic_drift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "fact_drift": metrics["fact_drift"],
                        "relation_drift": metrics["relation_drift"],
                        "confidence_drift": metrics["confidence_drift"],
                        "evidence_cost": metrics["evidence_cost"],
                        "original_fact_count": metrics["original_fact_count"],
                        "original_relation_count": metrics["original_relation_count"],
                        "recovered_fact_count": metrics["recovered_fact_count"],
                        "recovered_relation_count": metrics["recovered_relation_count"],
                        "matched_fact_count": metrics["matched_fact_count"],
                        "matched_relation_count": metrics["matched_relation_count"],
                        "missing_count": metrics["missing_count"],
                        "hallucination_count": metrics["hallucination_count"],
                        "original_unit_count": metrics["original_unit_count"],
                        "recovered_unit_count": metrics["recovered_unit_count"],
                        "matched_unit_count": metrics["matched_unit_count"],
                        "activation_threshold": case["parameters"]["activation_threshold"],
                        "recovery_min_evidence": case["parameters"]["recovery_min_evidence"],
                        "preserve_evidence": case["parameters"]["preserve_evidence"],
                        "archive_relations": case["parameters"]["archive_relations"],
                    }
                )

        with records_jsonl.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, default=str))
                handle.write("\n")

    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "phase_v_retention_v1",
        "experiment": "phase_v_retention",
        "version": "v1",
        "git_commit": _git_commit(),
        "case_count": summary.get("case_count", 0),
        "baseline_activation_threshold": baseline.get("activation_threshold"),
        "baseline_recovery_min_evidence": baseline.get("recovery_min_evidence"),
        "baseline_preserve_evidence": baseline.get("preserve_evidence"),
        "baseline_archive_relations": baseline.get("archive_relations"),
    }
    metadata_json.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    markdown = outputs["markdown"]
    report_md.write_text(markdown, encoding="utf-8")
    root_report.write_text(markdown, encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "metadata_json": str(metadata_json),
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "root_report_markdown": str(root_report),
        "report": report,
        "config": outputs["config"],
        "cases": outputs["cases"],
    }
