from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from experiments.config import ExternalValidationManualSanityConfig

from .baselines import build_memory_system
from .benchmarks import LoCoMoAdapter
from .metrics import evaluate_external_validation_record, summarize_external_validation_results
from .failure_analysis import summarize_failures
from .schema import BenchmarkCase, ExternalValidationRecord, ExternalValidationRun


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _truncate(text: str, limit: int = 180) -> str:
    value = " ".join(str(text).split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def _question_labels(question: str) -> tuple[str, ...]:
    q = _normalize_text(question)
    labels: list[str] = []

    temporal_markers = (
        q.startswith("when "),
        q.startswith("what time"),
        q.startswith("what date"),
        q.startswith("which day"),
        " yesterday" in f" {q} ",
        " tomorrow" in f" {q} ",
        " last week" in f" {q} ",
        " next week" in f" {q} ",
    )
    if any(temporal_markers):
        labels.append("temporal")

    boolean_markers = (
        q.startswith("is "),
        q.startswith("are "),
        q.startswith("was "),
        q.startswith("were "),
        q.startswith("do "),
        q.startswith("does "),
        q.startswith("did "),
        q.startswith("has "),
        q.startswith("have "),
        q.startswith("had "),
        " no longer " in f" {q} ",
        " still " in f" {q} ",
        " not " in f" {q} ",
        " never " in f" {q} ",
    )
    if any(boolean_markers):
        labels.append("boolean")

    if q.startswith("who ") or q.startswith("whose ") or q.startswith("whom "):
        labels.append("person")

    if q.startswith("where ") or " location " in f" {q} " or " place " in f" {q} " or " city " in f" {q} ":
        labels.append("location")

    if q.startswith("how many") or q.startswith("how long") or q.startswith("how much"):
        labels.append("quantity")

    relation_markers = (
        "relation" in q,
        "connected" in q,
        "connects" in q,
        "related" in q,
        "associated" in q,
        "depends" in q,
        "follow" in q,
        "replaces" in q,
        "update" in q,
        "changed" in q,
    )
    if any(relation_markers):
        labels.append("relation")

    if q.startswith("what ") or q.startswith("which ") or not labels:
        labels.append("generic")

    return tuple(dict.fromkeys(labels))


def _case_type(question_labels: tuple[str, ...], answer: str) -> str:
    ordered_types = ("temporal", "boolean", "person", "location", "quantity", "relation", "generic")
    for item in ordered_types:
        if item in question_labels:
            return item
    normalized_answer = _normalize_text(answer)
    if normalized_answer in {"yes", "no"}:
        return "boolean"
    if any(month in normalized_answer for month in ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")):
        return "temporal"
    return "generic"


def _calibration_statuses(metrics: Any) -> dict[str, str]:
    fact_accuracy = float(metrics.fact_accuracy)
    relation_accuracy = float(metrics.relation_accuracy)
    answer_accuracy = float(metrics.answer_accuracy)

    if fact_accuracy >= 0.8 and relation_accuracy >= 0.8:
        memory_status = "correct"
    elif fact_accuracy < 0.5 or relation_accuracy < 0.5:
        memory_status = "incorrect"
    else:
        memory_status = "uncertain"

    if answer_accuracy >= 0.8:
        generation_status = "correct"
    elif memory_status == "correct":
        generation_status = "incorrect"
    else:
        generation_status = "uncertain"

    if answer_accuracy >= 0.8:
        scorer_status = "aligned"
    elif memory_status == "correct" and generation_status == "incorrect":
        scorer_status = "false_negative"
    else:
        scorer_status = "uncertain"

    return {
        "memory_status": memory_status,
        "generation_status": generation_status,
        "scorer_status": scorer_status,
    }


def _preview_unit(unit) -> dict[str, Any]:
    return {
        "unit_id": unit.unit_id,
        "kind": unit.kind,
        "timestep": unit.timestep,
        "salience": round(float(unit.salience), 3),
        "content": _truncate(unit.content, 160),
    }


def _preview_relation(relation) -> dict[str, Any]:
    return {
        "relation_id": relation.relation_id,
        "source_id": relation.source_id,
        "target_id": relation.target_id,
        "relation_type": relation.relation_type,
        "confidence": round(float(relation.confidence), 3),
        "timestep": relation.timestep,
    }


def _preview_state(state, limit: int = 4) -> dict[str, Any]:
    return {
        "unit_count": len(state.units),
        "relation_count": len(state.relations),
        "units": [_preview_unit(unit) for unit in state.units[:limit]],
        "relations": [_preview_relation(relation) for relation in state.relations[:limit]],
    }


def _build_calibration_matrix(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def _aggregate(items: list[dict[str, Any]]) -> dict[str, Any]:
        if not items:
            return {
                "count": 0,
                "mean_answer_accuracy": 0.0,
                "mean_semantic_coverage": 0.0,
                "mean_semantic_drift": 0.0,
                "memory_status_counts": {},
                "generation_status_counts": {},
                "scorer_status_counts": {},
                "attribution_counts": {},
            }
        count = len(items)
        return {
            "count": count,
            "mean_answer_accuracy": round(sum(float(item["answer_accuracy"]) for item in items) / count, 6),
            "mean_semantic_coverage": round(sum(float(item["semantic_coverage"]) for item in items) / count, 6),
            "mean_semantic_drift": round(sum(float(item["semantic_drift"]) for item in items) / count, 6),
            "memory_status_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["memory_status"] == label)
                        for label in {item["memory_status"] for item in items}
                    }.items()
                )
            ),
            "generation_status_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["generation_status"] == label)
                        for label in {item["generation_status"] for item in items}
                    }.items()
                )
            ),
            "scorer_status_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["scorer_status"] == label)
                        for label in {item["scorer_status"] for item in items}
                    }.items()
                )
            ),
            "attribution_counts": dict(
                sorted(
                    {
                        label: sum(1 for item in items if item["attribution_label"] == label)
                        for label in {item["attribution_label"] for item in items}
                    }.items()
                )
            ),
        }

    by_case_type: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_baseline: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_case_type[str(row["case_type"])].append(row)
        by_baseline[str(row["baseline_name"])].append(row)

    return {
        "by_case_type": {key: _aggregate(value) for key, value in sorted(by_case_type.items())},
        "by_baseline": {key: _aggregate(value) for key, value in sorted(by_baseline.items())},
        "row_count": len(rows),
    }


def _temporal_attribution_protocol() -> dict[str, Any]:
    return {
        "name": "Temporal Attribution Protocol V1",
        "steps": [
            {
                "step": 1,
                "name": "memory_correctness",
                "input": "gold temporal fact + recovered semantic state",
                "decision": "inspect whether the recovered semantic state preserves the temporal relation and entity fact",
                "labels": ("correct", "incorrect", "uncertain"),
            },
            {
                "step": 2,
                "name": "generation_correctness",
                "input": "recovered semantic state + generated answer",
                "decision": "inspect whether the answer faithfully verbalizes the recovered state",
                "labels": ("correct", "incorrect", "uncertain"),
            },
            {
                "step": 3,
                "name": "scorer_alignment",
                "input": "generated answer + official scorer",
                "decision": "inspect whether the official score matches the semantic diagnosis",
                "labels": ("aligned", "false_negative", "false_positive", "uncertain"),
            },
        ],
        "interpretation_table": {
            "correct/correct/aligned": "success",
            "correct/correct/false_negative": "evaluator limitation",
            "correct/incorrect/aligned": "generation limitation",
            "incorrect/correct/aligned": "memory limitation",
            "uncertain/uncertain/uncertain": "manual review",
        },
        "freeze_boundary": "Scorer mismatches are treated as measurement issues, not SRP memory failures.",
    }


@dataclass(frozen=True)
class AdapterIntegrityResult:
    passed: bool
    checks: dict[str, bool]
    notes: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_locomo_adapter_case(case: BenchmarkCase) -> AdapterIntegrityResult:
    source_units = case.source_state.unit_map()
    source_relations = case.source_state.relation_map()
    target_units = case.target_state.unit_map()
    target_relations = case.target_state.relation_map()

    checks: dict[str, bool] = {
        "source_units_present": bool(source_units),
        "source_relations_present": bool(case.source_state.relations),
        "target_units_present": bool(target_units),
        "target_relations_resolve": all(
            relation.source_id in source_units and relation.target_id in source_units for relation in case.target_state.relations
        ),
        "focus_units_resolve": all(unit_id in source_units for unit_id in case.focus_unit_ids),
        "focus_relations_resolve": all(relation_id in source_relations for relation_id in case.focus_relation_ids),
        "target_units_subset_source": set(target_units).issubset(source_units),
        "target_relations_subset_source": set(target_relations).issubset(source_relations),
        "sample_id_consistent": all(unit.metadata.get("sample_id") == case.metadata.get("sample_id") for unit in source_units.values()),
        "session_datetime_present_on_dialog_turns": all(
            unit.metadata.get("session_datetime")
            for unit in source_units.values()
            if unit.kind == "dialog_turn"
        ),
        "timestamps_non_decreasing": all(
            left.timestep <= right.timestep for left, right in zip(case.source_state.units, case.source_state.units[1:])
        ),
    }

    notes: list[str] = []
    if not checks["source_units_present"]:
        notes.append("source state is empty")
    if not checks["target_units_present"]:
        notes.append("target state is empty")
    if not checks["focus_units_resolve"]:
        notes.append("evidence ids do not fully resolve to source units")
    if not checks["session_datetime_present_on_dialog_turns"]:
        notes.append("dialog turns are missing session datetime metadata")

    return AdapterIntegrityResult(passed=all(checks.values()), checks=checks, notes=tuple(notes))


def _select_cases(cases: Iterable[BenchmarkCase], case_limit: int) -> list[tuple[BenchmarkCase, tuple[str, ...], str]]:
    ordered_cases = list(cases)
    buckets: dict[str, list[BenchmarkCase]] = defaultdict(list)
    for case in ordered_cases:
        labels = _question_labels(case.query)
        primary = labels[0]
        buckets[primary].append(case)
        for label in labels[1:]:
            buckets[label].append(case)

    quotas = [
        ("temporal", 2),
        ("boolean", 2),
        ("person", 2),
        ("relation", 2),
        ("location", 1),
        ("quantity", 1),
        ("generic", 2),
    ]

    selected: list[tuple[BenchmarkCase, tuple[str, ...], str]] = []
    seen: set[str] = set()
    selected_per_label: dict[str, int] = defaultdict(int)
    used_samples: set[str] = set()

    def append_case(case: BenchmarkCase, label: str) -> None:
        if case.case_id in seen:
            return
        seen.add(case.case_id)
        if case.metadata.get("sample_id"):
            used_samples.add(str(case.metadata.get("sample_id")))
        labels = _question_labels(case.query)
        selected.append((case, labels, label))

    for label, quota in quotas:
        bucket = buckets.get(label, [])
        preferred = [case for case in bucket if str(case.metadata.get("sample_id", "")) not in used_samples]
        ordered_bucket = preferred + [case for case in bucket if case not in preferred]
        for case in ordered_bucket:
            if len(selected) >= case_limit:
                break
            if case.case_id in seen:
                continue
            append_case(case, label)
            selected_per_label[label] += 1
            if selected_per_label[label] >= quota:
                break
        if len(selected) >= case_limit:
            break

    if len(selected) < case_limit:
        for case in ordered_cases:
            if len(selected) >= case_limit:
                break
            if case.case_id in seen:
                continue
            labels = _question_labels(case.query)
            append_case(case, labels[0])

    return selected[:case_limit]


def _render_case_section(case_bundle: dict[str, Any]) -> str:
    case = case_bundle["case"]
    adapter = case_bundle["adapter_validation"]
    lines = [
        f"### {case['case_id']}",
        "",
        f"- Question: {case['query']}",
        f"- Gold answer: `{case['expected_answer']}`",
        f"- Official category: `{case_bundle['official_category']}`",
        f"- Question labels: `{', '.join(case_bundle['question_labels'])}`",
        f"- Selection bucket: `{case_bundle['selection_bucket']}`",
        f"- Evidence ids: `{', '.join(case['focus_unit_ids']) if case['focus_unit_ids'] else 'none'}`",
        f"- Adapter passed: `{adapter['passed']}`",
        "",
        "#### Adapter checks",
        "",
        "| Check | Pass |",
        "| --- | --- |",
    ]
    for name, value in adapter["checks"].items():
        lines.append(f"| `{name}` | `{value}` |")
    if adapter.get("notes"):
        lines.extend(["", "Adapter notes:", *[f"- {note}" for note in adapter["notes"]]])

    lines.extend(
        [
            "",
            "#### Source state preview",
            "",
            f"- Units: `{case_bundle['source_state_preview']['unit_count']}`",
            f"- Relations: `{case_bundle['source_state_preview']['relation_count']}`",
        ]
    )
    for unit in case_bundle["source_state_preview"]["units"]:
        lines.append(f"- Unit `{unit['unit_id']}` [{unit['kind']}] t={unit['timestep']} :: {unit['content']}")
    for relation in case_bundle["source_state_preview"]["relations"]:
        lines.append(
            f"- Relation `{relation['relation_id']}` :: {relation['source_id']} -> {relation['target_id']} ({relation['relation_type']})"
        )

    lines.extend(
        [
            "",
            "#### Gold target state preview",
            "",
            f"- Units: `{case_bundle['target_state_preview']['unit_count']}`",
            f"- Relations: `{case_bundle['target_state_preview']['relation_count']}`",
        ]
    )
    for unit in case_bundle["target_state_preview"]["units"]:
        lines.append(f"- Target unit `{unit['unit_id']}` [{unit['kind']}] t={unit['timestep']} :: {unit['content']}")
    for relation in case_bundle["target_state_preview"]["relations"]:
        lines.append(
            f"- Target relation `{relation['relation_id']}` :: {relation['source_id']} -> {relation['target_id']} ({relation['relation_type']})"
        )

    lines.extend(
        [
            "",
            "#### Baseline responses",
            "",
            "| Baseline | Predicted | Answer Acc. | Coverage | Drift | Relation Acc. | Recovery Acc. | Closure Acc. | Cost | Attribution | Failures |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for baseline in case_bundle["baselines"]:
        metrics = baseline["metrics"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{baseline['name']}`",
                    _truncate(baseline["predicted_answer"], 80),
                    str(metrics["answer_accuracy"]),
                    str(metrics["semantic_coverage"]),
                    str(metrics["semantic_drift"]),
                    str(metrics["relation_accuracy"]),
                    str(metrics["recovery_accuracy"]),
                    str(metrics["closure_accuracy"]),
                    str(metrics["evidence_cost"]),
                    baseline["attribution_label"],
                    ", ".join(baseline["failure_categories"]) if baseline["failure_categories"] else "none",
                ]
            )
            + " |"
        )
    lines.append("")
    lines.extend(["#### Recovered state previews", ""])
    for baseline in case_bundle["baselines"]:
        recovered = baseline["recovered_state_preview"]
        lines.extend(
            [
                f"- `{baseline['name']}`",
                f"  - Units: `{recovered['unit_count']}`",
                f"  - Relations: `{recovered['relation_count']}`",
                f"  - Predicted answer: `{baseline['predicted_answer']}`",
            ]
        )
        for unit in recovered["units"]:
            lines.append(f"  - Unit `{unit['unit_id']}` [{unit['kind']}] t={unit['timestep']} :: {unit['content']}")
        for relation in recovered["relations"]:
            lines.append(
                f"  - Relation `{relation['relation_id']}` :: {relation['source_id']} -> {relation['target_id']} ({relation['relation_type']})"
            )
    lines.extend(["", "#### Answer attribution traces", ""])
    for baseline in case_bundle["baselines"]:
        trace = baseline["answer_attribution_trace"]
        lines.extend(
            [
                f"- `{baseline['name']}`",
                f"  - Case type: `{trace['case_type']}`",
                f"  - Attribution: `{trace['attribution_label']}`",
                f"  - Score band: `{trace['score_band']}`",
                f"  - Expected: `{trace['expected_answer']}`",
                f"  - Predicted: `{trace['predicted_answer']}`",
                f"  - Retrieved units: `{', '.join(trace['retrieved_unit_ids']) if trace['retrieved_unit_ids'] else 'none'}`",
                f"  - Retrieved relations: `{', '.join(trace['retrieved_relation_ids']) if trace['retrieved_relation_ids'] else 'none'}`",
                f"  - Target preview units: `{trace['target_unit_count']}`",
                f"  - Recovered preview units: `{trace['recovered_unit_count']}`",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def run_locomo_manual_sanity(config: ExternalValidationManualSanityConfig) -> dict[str, Any]:
    adapter = LoCoMoAdapter()
    benchmark_root = Path(config.data_root) if config.data_root else None
    all_cases = adapter.load_cases(benchmark_root, sample_limit=config.benchmark_sample_limit)
    selected = _select_cases(all_cases, config.case_limit)

    records: list[ExternalValidationRecord] = []
    case_bundles: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    adapter_validation_counts: dict[str, int] = defaultdict(int)
    adapter_validation_failures: list[str] = []

    for case, question_labels, selection_bucket in selected:
        integrity = validate_locomo_adapter_case(case)
        for key, value in integrity.checks.items():
            if value:
                adapter_validation_counts[key] += 1
        if not integrity.passed:
            adapter_validation_failures.append(case.case_id)

        case_bundle = {
            "case": case.as_dict(),
            "official_category": case.metadata.get("category"),
            "question_labels": question_labels,
            "selection_bucket": selection_bucket,
            "case_type": _case_type(question_labels, str(case.expected_answer)),
            "adapter_validation": integrity.as_dict(),
            "source_state_preview": _preview_state(case.source_state),
            "target_state_preview": _preview_state(case.target_state),
            "baselines": [],
        }

        for baseline_name in config.baseline_names:
            run = ExternalValidationRun(
                run_id=f"{config.benchmark_name}_{baseline_name}_{config.seed}_{case.case_id}",
                benchmark_name=config.benchmark_name,
                baseline_name=baseline_name,
                seed=config.seed,
                case=case,
            )
            memory = build_memory_system(baseline_name, seed=config.seed)
            memory.ingest(case)
            response = memory.retrieve(case.query, budget=case.metadata.get("evidence_budget"))
            record = evaluate_external_validation_record(run, response)
            records.append(record)
            calibration_status = _calibration_statuses(record.metrics)
            answer_accuracy = float(record.metrics.answer_accuracy)
            if answer_accuracy >= 0.8:
                attribution_label = "aligned"
                score_band = "pass"
            elif calibration_status["memory_status"] == "correct" and calibration_status["generation_status"] == "incorrect":
                attribution_label = "generation_or_scorer_mismatch"
                score_band = "review"
            elif calibration_status["memory_status"] == "incorrect":
                attribution_label = "memory_mismatch"
                score_band = "review"
            else:
                attribution_label = "mixed"
                score_band = "review"
            trace = {
                "benchmark_name": config.benchmark_name,
                "case_id": case.case_id,
                "baseline_name": baseline_name,
                "case_type": case_bundle["case_type"],
                "question": case.query,
                "expected_answer": case.expected_answer,
                "predicted_answer": response.predicted_answer,
                "retrieved_unit_ids": list(response.retrieved_unit_ids),
                "retrieved_relation_ids": list(response.retrieved_relation_ids),
                "target_unit_count": len(case.target_state.units),
                "target_relation_count": len(case.target_state.relations),
                "recovered_unit_count": len(response.recovered_state.units),
                "recovered_relation_count": len(response.recovered_state.relations),
                "answer_accuracy": answer_accuracy,
                "semantic_coverage": record.metrics.semantic_coverage,
                "semantic_drift": record.metrics.semantic_drift,
                "fact_accuracy": record.metrics.fact_accuracy,
                "relation_accuracy": record.metrics.relation_accuracy,
                "recovery_accuracy": record.metrics.recovery_accuracy,
                "closure_accuracy": record.metrics.closure_accuracy,
                "evidence_cost": record.metrics.evidence_cost,
                "memory_status": calibration_status["memory_status"],
                "generation_status": calibration_status["generation_status"],
                "scorer_status": calibration_status["scorer_status"],
                "attribution_label": attribution_label,
                "score_band": score_band,
            }
            case_bundle["baselines"].append(
                {
                    "name": baseline_name,
                    "predicted_answer": response.predicted_answer,
                    "retrieved_unit_ids": response.retrieved_unit_ids,
                    "retrieved_relation_ids": response.retrieved_relation_ids,
                    "failure_categories": list(record.failure_categories),
                    "failure_notes": list(record.failure_notes),
                    "recovered_state_preview": _preview_state(response.recovered_state),
                    "answer_attribution_trace": trace,
                    "attribution_label": attribution_label,
                    "memory_status": calibration_status["memory_status"],
                    "generation_status": calibration_status["generation_status"],
                    "scorer_status": calibration_status["scorer_status"],
                    "metrics": record.metrics.as_dict(),
                }
            )
            calibration_rows.append(trace)

        case_bundles.append(case_bundle)

    summary_bundle = summarize_external_validation_results(records)
    failure_bundle = summarize_failures(records)

    adapter_validation_summary = {
        "case_count": len(case_bundles),
        "passed_case_count": sum(1 for bundle in case_bundles if bundle["adapter_validation"]["passed"]),
        "failed_case_count": sum(1 for bundle in case_bundles if not bundle["adapter_validation"]["passed"]),
        "check_pass_counts": dict(sorted(adapter_validation_counts.items())),
        "failed_case_ids": adapter_validation_failures,
    }

    report = {
        "config": config.as_dict(),
        "adapter_validation": adapter_validation_summary,
        "temporal_attribution_protocol": _temporal_attribution_protocol(),
        "calibration_matrix": _build_calibration_matrix(calibration_rows),
        "answer_attribution_traces": calibration_rows,
        "selected_cases": [
            {
                "case_id": bundle["case"]["case_id"],
                "question": bundle["case"]["query"],
                "gold_answer": bundle["case"]["expected_answer"],
                "official_category": bundle["official_category"],
                "question_labels": bundle["question_labels"],
                "selection_bucket": bundle["selection_bucket"],
                "adapter_passed": bundle["adapter_validation"]["passed"],
            }
            for bundle in case_bundles
        ],
        "case_bundles": case_bundles,
        "summary": summary_bundle["summary"],
        "benchmark_summary": summary_bundle["benchmark_summary"],
        "baseline_summary": summary_bundle["baseline_summary"],
        "pairwise_summary": summary_bundle["pairwise_summary"],
        "failure_summary": failure_bundle,
        "record_count": len(records),
        "case_count": len(case_bundles),
        "seed": config.seed,
    }
    return report


def render_locomo_manual_sanity_markdown(report: dict[str, Any]) -> str:
    config = report["config"]
    summary = report["summary"]
    adapter_validation = report["adapter_validation"]
    temporal_protocol = report.get("temporal_attribution_protocol", {})
    calibration_matrix = report.get("calibration_matrix", {})
    lines = [
        "# SRP LoCoMo Manual Sanity Harness",
        "",
        "This report freezes the LoCoMo adapter-calibration evidence package for SRP.",
        "It is a calibration artifact, not a paper result, not a benchmark claim, and not a runtime policy.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{config['benchmark_name']}`",
        f"- Baselines: `{', '.join(config['baseline_names'])}`",
        f"- Seed: `{config['seed']}`",
        f"- Case limit: `{config['case_limit']}`",
        f"- Data root: `{config['data_root']}`",
        "",
        "## 2. Adapter Validation Summary",
        "",
        f"- Cases checked: `{adapter_validation['case_count']}`",
        f"- Cases passed: `{adapter_validation['passed_case_count']}`",
        f"- Cases failed: `{adapter_validation['failed_case_count']}`",
    ]
    for check_name, count in adapter_validation["check_pass_counts"].items():
        lines.append(f"- `{check_name}` pass count: `{count}`")
    if adapter_validation["failed_case_ids"]:
        lines.append(f"- Failed case ids: `{', '.join(adapter_validation['failed_case_ids'])}`")
    lines.extend(
        [
            "",
            "## 3. Summary",
            "",
            f"- Record count: `{report['record_count']}`",
            f"- semantic_coverage: `{summary['semantic_coverage']}`",
            f"- semantic_drift: `{summary['semantic_drift']}`",
            f"- fact_accuracy: `{summary['fact_accuracy']}`",
            f"- relation_accuracy: `{summary['relation_accuracy']}`",
            f"- recovery_accuracy: `{summary['recovery_accuracy']}`",
            f"- closure_accuracy: `{summary['closure_accuracy']}`",
            f"- neighborhood_completeness: `{summary['neighborhood_completeness']}`",
            f"- hallucinated_relation_rate: `{summary['hallucinated_relation_rate']}`",
            f"- evidence_cost: `{summary['evidence_cost']}`",
            f"- answer_accuracy: `{summary['answer_accuracy']}`",
            f"- official_metric_score: `{summary['official_metric_score']}`",
            "",
            "## 4. Temporal Attribution Protocol V1",
            "",
        ]
    )
    if temporal_protocol:
        lines.extend(
            [
                f"- Step 1: `{temporal_protocol['steps'][0]['name']}`",
                f"  - Input: `{temporal_protocol['steps'][0]['input']}`",
                f"  - Decision: {temporal_protocol['steps'][0]['decision']}",
                f"- Step 2: `{temporal_protocol['steps'][1]['name']}`",
                f"  - Input: `{temporal_protocol['steps'][1]['input']}`",
                f"  - Decision: {temporal_protocol['steps'][1]['decision']}",
                f"- Step 3: `{temporal_protocol['steps'][2]['name']}`",
                f"  - Input: `{temporal_protocol['steps'][2]['input']}`",
                f"  - Decision: {temporal_protocol['steps'][2]['decision']}",
                "",
                "Interpretation boundary:",
                f"- {temporal_protocol['freeze_boundary']}",
                "",
            ]
        )
    lines.extend(
        [
            "## 5. Scoring Calibration Matrix",
            "",
        ]
    )
    if calibration_matrix.get("by_case_type"):
        lines.append("| Case Type | Count | Mean Answer Acc. | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution Mix |")
        lines.append("| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |")
        for case_type, stats in calibration_matrix["by_case_type"].items():
            attribution_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("attribution_counts", {}).items()) or "none"
            memory_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("memory_status_counts", {}).items()) or "none"
            generation_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("generation_status_counts", {}).items()) or "none"
            scorer_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("scorer_status_counts", {}).items()) or "none"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{case_type}`",
                        str(stats.get("count", 0)),
                        str(stats.get("mean_answer_accuracy", 0.0)),
                        str(stats.get("mean_semantic_coverage", 0.0)),
                        str(stats.get("mean_semantic_drift", 0.0)),
                        memory_mix,
                        generation_mix,
                        scorer_mix,
                        attribution_mix,
                    ]
                )
                + " |"
            )
        lines.append("")
    if calibration_matrix.get("by_baseline"):
        lines.append("### Baseline Calibration Summary")
        lines.append("")
        lines.append("| Baseline | Count | Mean Answer Acc. | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution Mix |")
        lines.append("| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |")
        for baseline_name, stats in calibration_matrix["by_baseline"].items():
            attribution_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("attribution_counts", {}).items()) or "none"
            memory_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("memory_status_counts", {}).items()) or "none"
            generation_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("generation_status_counts", {}).items()) or "none"
            scorer_mix = ", ".join(f"{key}:{value}" for key, value in stats.get("scorer_status_counts", {}).items()) or "none"
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"`{baseline_name}`",
                        str(stats.get("count", 0)),
                        str(stats.get("mean_answer_accuracy", 0.0)),
                        str(stats.get("mean_semantic_coverage", 0.0)),
                        str(stats.get("mean_semantic_drift", 0.0)),
                        memory_mix,
                        generation_mix,
                        scorer_mix,
                        attribution_mix,
                    ]
                )
                + " |"
            )
        lines.append("")
    lines.extend(
        [
            "## 6. Selected Cases",
            "",
        ]
    )
    for bundle in report["case_bundles"]:
        lines.append(_render_case_section(bundle))
    lines.extend(
        [
            "## 7. Failure Summary",
            "",
        ]
    )
    if report["failure_summary"].get("counts"):
        for key, value in report["failure_summary"]["counts"].items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")
    lines.append("")
    if report["failure_summary"].get("examples"):
        lines.append("### Failure Examples")
        lines.append("")
        for key, examples in report["failure_summary"]["examples"].items():
            lines.append(f"- {key}: {', '.join(examples)}")
        lines.append("")
    return "\n".join(lines)


def write_locomo_manual_sanity_outputs(
    output_dir: str | Path,
    config: ExternalValidationManualSanityConfig | None = None,
) -> dict[str, Any]:
    config = config or ExternalValidationManualSanityConfig()
    report = run_locomo_manual_sanity(config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    report_md = output_path / "locomo_manual_sanity_report.md"
    report_json = output_path / "locomo_manual_sanity_report.json"
    summary_json = output_path / "locomo_manual_sanity_summary.json"
    protocol_json = output_path / "locomo_temporal_attribution_protocol.json"
    calibration_json = output_path / "locomo_scoring_calibration_matrix.json"
    traces_json = output_path / "locomo_answer_attribution_traces.json"
    selected_cases_json = output_path / "locomo_selected_cases.json"
    case_bundles_json = output_path / "locomo_case_bundles.json"

    markdown = render_locomo_manual_sanity_markdown(report)
    report_md.write_text(markdown, encoding="utf-8")
    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_json.write_text(json.dumps(report["summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    protocol_json.write_text(json.dumps(report["temporal_attribution_protocol"], indent=2, ensure_ascii=False), encoding="utf-8")
    calibration_json.write_text(json.dumps(report["calibration_matrix"], indent=2, ensure_ascii=False), encoding="utf-8")
    traces_json.write_text(json.dumps(report["answer_attribution_traces"], indent=2, ensure_ascii=False), encoding="utf-8")
    selected_cases_json.write_text(json.dumps(report["selected_cases"], indent=2, ensure_ascii=False), encoding="utf-8")
    case_bundles_json.write_text(json.dumps(report["case_bundles"], indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "report": report,
        "markdown": markdown,
        "report_markdown": str(report_md),
        "report_json": str(report_json),
        "summary_json": str(summary_json),
        "protocol_json": str(protocol_json),
        "calibration_json": str(calibration_json),
        "traces_json": str(traces_json),
        "selected_cases_json": str(selected_cases_json),
        "case_bundles_json": str(case_bundles_json),
    }
