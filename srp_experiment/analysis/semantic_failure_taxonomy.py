from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


@dataclass(frozen=True)
class FailureExample:
    failure_type: str
    subtype: str | None
    task_id: str | None
    scenario: str | None
    stage: str | None
    severity: str
    count: int
    evidence: Dict[str, Any]


TEMPORAL_HINTS = {
    "before",
    "after",
    "during",
    "when",
    "while",
    "then",
    "earlier",
    "later",
    "moved",
    "worked",
    "founded",
    "changed",
    "shifted",
    "remained",
    "stayed",
}

CONSTRAINT_HINTS = {
    "only",
    "must",
    "require",
    "required",
    "cannot",
    "can't",
    "never",
    "always",
    "preserve",
    "keep",
    "retain",
    "unless",
}

RELATION_HINTS = {
    "works at",
    "owns",
    "keeps",
    "depends on",
    "linked for",
    "located in",
    "moved to",
    "reports to",
    "belongs to",
    "assigned to",
    "responsible for",
}

_DATE_RE = re.compile(r"\b\d{1,2}/\d{4}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{4}\b", re.I)


def _load_records_from_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            data = json.loads(text)
            if isinstance(data, dict):
                records.append(data)
    return records


def load_records_from_inputs(inputs: Sequence[str | Path]) -> List[Dict[str, Any]]:
    paths: List[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            paths.extend(sorted(path.rglob("*_records.jsonl")))
            paths.extend(sorted(path.rglob("*.jsonl")))
        elif path.suffix.lower() == ".jsonl" and path.exists():
            paths.append(path)
        elif path.suffix.lower() == ".json" and path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                return [item for item in payload if isinstance(item, dict)]
            if isinstance(payload, dict):
                return [payload]
        elif path.exists():
            paths.append(path)
    records: List[Dict[str, Any]] = []
    seen = set()
    for path in paths:
        if path in seen or not path.exists():
            continue
        seen.add(path)
        if path.suffix.lower() == ".jsonl":
            records.extend(_load_records_from_jsonl(path))
    return records


def _get_experiment_result(record: Dict[str, Any]) -> Dict[str, Any]:
    result = record.get("experiment_result")
    if isinstance(result, dict):
        return result
    return {}


def _get_lifecycle(record: Dict[str, Any]) -> Dict[str, Any]:
    result = _get_experiment_result(record)
    lifecycle = result.get("lifecycle_attribution")
    if isinstance(lifecycle, dict):
        return lifecycle
    lifecycle = record.get("object_lifecycle")
    if isinstance(lifecycle, dict):
        return lifecycle
    return {}


def _get_validation(record: Dict[str, Any]) -> Dict[str, Any]:
    validation = record.get("validation")
    if isinstance(validation, dict):
        return validation
    result = _get_experiment_result(record)
    validation = result.get("validation")
    if isinstance(validation, dict):
        return validation
    return {}


def _get_allocation(record: Dict[str, Any]) -> Dict[str, Any]:
    allocation = record.get("state_allocation_result")
    if isinstance(allocation, dict):
        return allocation
    result = _get_experiment_result(record)
    allocation = result.get("allocation")
    if isinstance(allocation, dict):
        return allocation.get("result") if isinstance(allocation.get("result"), dict) else allocation
    return {}


def _flatten_missing_labels(labels: Iterable[str]) -> List[str]:
    return [str(label).strip() for label in labels if str(label).strip()]


def _classify_dependency_subtype(label: str, scenario: str | None = None) -> str:
    lowered = label.lower()
    if scenario and "collision" in scenario.lower():
        return "identity_collision"
    if _DATE_RE.search(lowered) or any(token in lowered for token in TEMPORAL_HINTS):
        return "temporal_loss"
    if any(token in lowered for token in CONSTRAINT_HINTS):
        return "constraint_loss"
    if any(token in lowered for token in RELATION_HINTS):
        return "relation_loss"
    return "dependency_break"


def _severity_for_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "medium"
    if ratio >= 0.5:
        return "high"
    if ratio >= 0.2:
        return "medium"
    return "low"


def _add_issue(
    issues: List[FailureExample],
    counts: Counter,
    subtype_counts: Dict[str, Counter],
    failure_type: str,
    *,
    subtype: str | None = None,
    task_id: str | None = None,
    scenario: str | None = None,
    stage: str | None = None,
    severity: str = "medium",
    count: int = 1,
    evidence: Dict[str, Any] | None = None,
) -> None:
    counts[failure_type] += count
    if subtype:
        subtype_counts[failure_type][subtype] += count
    issues.append(
        FailureExample(
            failure_type=failure_type,
            subtype=subtype,
            task_id=task_id,
            scenario=scenario,
            stage=stage,
            severity=severity,
            count=count,
            evidence=evidence or {},
        )
    )


def build_semantic_failure_taxonomy(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    issues: List[FailureExample] = []
    counts: Counter = Counter()
    subtype_counts: Dict[str, Counter] = defaultdict(Counter)
    task_buckets: Dict[str, Dict[str, Any]] = {}

    for record in records:
        task_id = str(record.get("task_id") or record.get("compression_suite") or "unknown")
        scenario = str(record.get("compression_scenario") or record.get("scenario") or "unknown")
        experiment = _get_experiment_result(record)
        lifecycle = _get_lifecycle(record)
        validation = _get_validation(record)
        allocation = _get_allocation(record)

        bucket = task_buckets.setdefault(
            task_id,
            {
                "task_id": task_id,
                "scenario": scenario,
                "records": 0,
                "validation_failures": 0,
            },
        )
        bucket["records"] += 1

        # Object loss across the lifecycle chain.
        transitions = (lifecycle.get("transitions") or {}) if isinstance(lifecycle, dict) else {}
        for transition_name, transition in transitions.items():
            if not isinstance(transition, dict):
                continue
            missing = list(transition.get("missing") or [])
            if not missing:
                continue
            source_count = transition.get("source_count")
            missing_ratio = (len(missing) / source_count) if isinstance(source_count, int) and source_count else None
            stage_name = str(transition_name)
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "object_loss",
                subtype=stage_name,
                task_id=task_id,
                scenario=scenario,
                stage=stage_name,
                severity=_severity_for_ratio(missing_ratio),
                count=len(missing),
                evidence={
                    "transition": stage_name,
                    "missing_count": len(missing),
                    "source_count": source_count,
                    "missing_object_ids": [item.get("object_id") for item in missing[:5]],
                },
            )

        # Dependency break, decomposed by subtype.
        dependency_audit = validation.get("dependency_audit") or record.get("dependency_audit") or {}
        expected_labels = _flatten_missing_labels(dependency_audit.get("expected_labels") or [])
        matched_ids = set(str(item) for item in dependency_audit.get("matched_object_ids") or [])
        recovered_ids = set(str(item) for item in dependency_audit.get("recovered_object_ids") or [])
        dependency_missing_count = max(0, int(dependency_audit.get("expected_count") or len(expected_labels)) - int(dependency_audit.get("matched_count") or 0))
        if expected_labels and dependency_missing_count > 0:
            subtype_counter: Counter = Counter()
            for label in expected_labels:
                subtype = _classify_dependency_subtype(label, scenario)
                subtype_counter[subtype] += 1
                _add_issue(
                    issues,
                    counts,
                    subtype_counts,
                    "dependency_break",
                    subtype=subtype,
                    task_id=task_id,
                    scenario=scenario,
                    stage="validation",
                    severity="high" if subtype in {"identity_collision", "constraint_loss"} else "medium",
                    count=1,
                    evidence={
                        "expected_label": label,
                        "expected_count": dependency_audit.get("expected_count"),
                        "matched_count": dependency_audit.get("matched_count"),
                        "recovered_count": dependency_audit.get("recovered_count"),
                        "matched_object_ids": sorted(matched_ids)[:5],
                        "recovered_object_ids": sorted(recovered_ids)[:5],
                    },
                )
            bucket["validation_failures"] += dependency_missing_count

        # Hallucinated reconstruction.
        retention_v2 = record.get("object_retention_breakdown_v2") or {}
        all_objects = retention_v2.get("all_objects") or {}
        hallucinated = list(all_objects.get("hallucinated") or [])
        if hallucinated:
            hallucinated_ratio = None
            recovered_count = all_objects.get("recovered_count")
            source_count = all_objects.get("source_count")
            if isinstance(source_count, int) and source_count:
                hallucinated_ratio = len(hallucinated) / source_count
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "hallucinated_reconstruction",
                subtype="unsupported_reconstruction",
                task_id=task_id,
                scenario=scenario,
                stage="recovery",
                severity=_severity_for_ratio(hallucinated_ratio),
                count=len(hallucinated),
                evidence={
                    "hallucinated_count": len(hallucinated),
                    "hallucinated_object_ids": [item.get("object_id") for item in hallucinated[:5]],
                    "source_count": source_count,
                    "recovered_count": recovered_count,
                },
            )

        # Allocation failure.
        allocation_metrics = allocation.get("metrics") or {}
        active_count = allocation_metrics.get("active_object_count")
        important_count = (
            retention_v2.get("important", {}).get("source_count")
            if isinstance(retention_v2.get("important"), dict)
            else None
        )
        active_retention_ratio = allocation_metrics.get("active_retention_ratio")
        if important_count is not None and active_count is not None and active_count < important_count:
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "allocation_failure",
                subtype="budget_pressure",
                task_id=task_id,
                scenario=scenario,
                stage="allocation",
                severity=_severity_for_ratio(active_retention_ratio),
                count=important_count - active_count,
                evidence={
                    "active_object_count": active_count,
                    "important_object_count": important_count,
                    "active_retention_ratio": active_retention_ratio,
                    "policy_name": allocation_metrics.get("policy_name") or allocation.get("policy_name"),
                },
            )

        # Temporal drift.
        semantic_drift_from_initial = record.get("semantic_drift_from_initial")
        runtime_round = record.get("runtime_round")
        if isinstance(runtime_round, int) and runtime_round > 1 and semantic_drift_from_initial is not None:
            drift_value = float(semantic_drift_from_initial)
            if drift_value > 0.15:
                _add_issue(
                    issues,
                    counts,
                    subtype_counts,
                    "temporal_drift",
                    subtype="round_drift",
                    task_id=task_id,
                    scenario=scenario,
                    stage="runtime",
                    severity="high" if drift_value > 0.35 else "medium",
                    count=1,
                    evidence={
                        "runtime_round": runtime_round,
                        "semantic_drift_from_initial": drift_value,
                        "validation_drift": record.get("validation_drift"),
                        "validation_drift_risk": record.get("validation_drift_risk"),
                    },
                )

    summary_types = {}
    for failure_type in sorted(counts):
        summary_types[failure_type] = {
            "count": counts[failure_type],
            "subtypes": dict(subtype_counts.get(failure_type, {})),
            "examples": [
                {
                    "subtype": issue.subtype,
                    "task_id": issue.task_id,
                    "scenario": issue.scenario,
                    "stage": issue.stage,
                    "severity": issue.severity,
                    "count": issue.count,
                    "evidence": issue.evidence,
                }
                for issue in issues
                if issue.failure_type == failure_type
            ][:5],
        }

    return {
        "schema_version": "semantic_failure_taxonomy.v1",
        "records_processed": len(records),
        "failure_types": summary_types,
        "issues": [
            {
                "failure_type": issue.failure_type,
                "subtype": issue.subtype,
                "task_id": issue.task_id,
                "scenario": issue.scenario,
                "stage": issue.stage,
                "severity": issue.severity,
                "count": issue.count,
                "evidence": issue.evidence,
            }
            for issue in issues
        ],
        "task_buckets": list(task_buckets.values()),
    }


def render_semantic_failure_taxonomy_markdown(taxonomy: Dict[str, Any]) -> str:
    lines = [
        "# Semantic Failure Taxonomy",
        "",
        "This report summarizes the failure modes observed in the current SRP records.",
        "",
        "The categories are inference-based and derived from existing lifecycle, validation, allocation, and drift signals.",
        "",
        "| Failure Type | Count | Subtypes |",
        "| --- | --- | --- |",
    ]
    for failure_type, payload in sorted((taxonomy.get("failure_types") or {}).items()):
        subtypes = payload.get("subtypes") or {}
        subtype_text = ", ".join(f"{name}:{value}" for name, value in sorted(subtypes.items())) or "-"
        lines.append(f"| {failure_type} | {payload.get('count')} | {subtype_text} |")

    lines.extend(["", "## Representative Evidence", ""])
    for failure_type, payload in sorted((taxonomy.get("failure_types") or {}).items()):
        examples = payload.get("examples") or []
        if not examples:
            continue
        lines.extend([f"### {failure_type}", ""])
        lines.append("| Subtype | Task | Scenario | Stage | Severity | Count | Evidence |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for example in examples[:3]:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(example.get("subtype") or ""),
                        str(example.get("task_id") or ""),
                        str(example.get("scenario") or ""),
                        str(example.get("stage") or ""),
                        str(example.get("severity") or ""),
                        str(example.get("count") or ""),
                        json.dumps(example.get("evidence") or {}, ensure_ascii=False),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def write_semantic_failure_taxonomy_outputs(taxonomy: Dict[str, Any], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "semantic_failure_taxonomy.json"
    markdown_path = output_path / "semantic_failure_taxonomy.md"
    json_path.write_text(json.dumps(taxonomy, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_semantic_failure_taxonomy_markdown(taxonomy), encoding="utf-8")
    return {
        "json": json_path,
        "markdown": markdown_path,
    }

