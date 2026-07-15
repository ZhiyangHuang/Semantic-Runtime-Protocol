from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence


GRAPH_ATTRIBUTE_GAPS = ("identity", "properties", "state")
GRAPH_LIFECYCLE_GAPS = ("created", "modified", "compressed", "recovered", "verified", "retained")


@dataclass(frozen=True)
class GapExample:
    gap_type: str
    subtype: str | None
    task_id: str | None
    scenario: str | None
    severity: str
    count: int
    evidence: Dict[str, Any]


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
            paths.extend(sorted(path.rglob("*graph_recovery_ablation_records.jsonl")))
            paths.extend(sorted(path.rglob("*_records.jsonl")))
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


def _get_graph(record: Dict[str, Any]) -> Dict[str, Any]:
    graph = record.get("semantic_runtime_graph")
    return graph if isinstance(graph, dict) else {}


def _get_graph_validation(record: Dict[str, Any]) -> Dict[str, Any]:
    validation = record.get("semantic_graph_validation")
    return validation if isinstance(validation, dict) else {}


def _get_graph_recovery_result(record: Dict[str, Any]) -> Dict[str, Any]:
    result = record.get("graph_recovery_result")
    return result if isinstance(result, dict) else {}


def _severity_for_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "medium"
    if ratio >= 0.5:
        return "high"
    if ratio >= 0.2:
        return "medium"
    return "low"


def _graph_nodes(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [item for item in list(graph.get("nodes", [])) if isinstance(item, dict)]


def _graph_edges(graph: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [item for item in list(graph.get("edges", [])) if isinstance(item, dict)]


def _node_id(node: Dict[str, Any]) -> str | None:
    value = node.get("id") or node.get("node_id")
    value = str(value).strip() if value is not None else ""
    return value or None


def _missing_graph_attributes(node: Dict[str, Any]) -> List[str]:
    attributes = node.get("attributes") or {}
    if not isinstance(attributes, dict):
        attributes = {}
    missing = [field for field in GRAPH_ATTRIBUTE_GAPS if not str(attributes.get(field, "")).strip()]
    return missing


def _missing_graph_lifecycle(node: Dict[str, Any]) -> List[str]:
    lifecycle = node.get("lifecycle") or {}
    if not isinstance(lifecycle, dict):
        lifecycle = {}
    missing = [field for field in GRAPH_LIFECYCLE_GAPS if field not in lifecycle]
    return missing


def _add_issue(
    issues: List[GapExample],
    counts: Counter,
    subtype_counts: Dict[str, Counter],
    gap_type: str,
    *,
    subtype: str | None = None,
    task_id: str | None = None,
    scenario: str | None = None,
    severity: str = "medium",
    count: int = 1,
    evidence: Dict[str, Any] | None = None,
) -> None:
    counts[gap_type] += count
    if subtype:
        subtype_counts[gap_type][subtype] += count
    issues.append(
        GapExample(
            gap_type=gap_type,
            subtype=subtype,
            task_id=task_id,
            scenario=scenario,
            severity=severity,
            count=count,
            evidence=evidence or {},
        )
    )


def build_graph_information_gap_analysis(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    issues: List[GapExample] = []
    counts: Counter = Counter()
    subtype_counts: Dict[str, Counter] = defaultdict(Counter)
    task_buckets: Dict[str, Dict[str, Any]] = {}

    for record in records:
        task_id = str(record.get("task_id") or record.get("graph_recovery_suite") or "unknown")
        scenario = str(record.get("graph_recovery_scenario") or record.get("scenario") or "unknown")
        graph = _get_graph(record)
        validation = _get_graph_validation(record)
        graph_result = _get_graph_recovery_result(record)
        nodes = _graph_nodes(graph)
        edges = _graph_edges(graph)
        bucket = task_buckets.setdefault(
            task_id,
            {
                "task_id": task_id,
                "scenario": scenario,
                "records": 0,
            },
        )
        bucket["records"] += 1

        # Node gaps: source nodes that failed to recover.
        missing_nodes = [
            node
            for node in nodes
            if bool((node.get("lifecycle") or {}).get("source_present", False))
            and not bool((node.get("lifecycle") or {}).get("recovered_present", False))
        ]
        if missing_nodes:
            source_node_count = validation.get("source_node_count")
            missing_ratio = (len(missing_nodes) / source_node_count) if isinstance(source_node_count, int) and source_node_count else None
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "missing_node",
                subtype="node_absence",
                task_id=task_id,
                scenario=scenario,
                severity=_severity_for_ratio(missing_ratio),
                count=len(missing_nodes),
                evidence={
                    "missing_node_ids": [_node_id(node) for node in missing_nodes[:5]],
                    "source_node_count": source_node_count,
                    "recovered_node_count": validation.get("recovered_node_count"),
                },
            )

        # Edge gaps: missing dependency edges and weak closure.
        missing_dependency_count = int(validation.get("missing_dependency_count") or 0)
        if missing_dependency_count > 0:
            dependency_edge_count = int(validation.get("dependency_edge_count") or 0)
            total = dependency_edge_count + missing_dependency_count
            missing_ratio = (missing_dependency_count / total) if total else None
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "missing_edge",
                subtype="dependency_edge",
                task_id=task_id,
                scenario=scenario,
                severity=_severity_for_ratio(missing_ratio),
                count=missing_dependency_count,
                evidence={
                    "dependency_edge_count": dependency_edge_count,
                    "missing_dependency_count": missing_dependency_count,
                    "graph_repair_cost": graph_result.get("repair_cost"),
                },
            )

        # Constraint gaps: source constraint nodes that do not survive recovery.
        constraint_issues = list((validation.get("issues") or {}).get("constraint", []))
        if constraint_issues:
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "missing_constraint",
                subtype="constraint_survival",
                task_id=task_id,
                scenario=scenario,
                severity="high" if len(constraint_issues) > 1 else "medium",
                count=len(constraint_issues),
                evidence={
                    "constraint_issue_count": len(constraint_issues),
                    "labels": [item.get("label") for item in constraint_issues[:5]],
                },
            )

        # Attribute gaps: the graph nodes currently do not expose the richer node schema we want.
        attribute_gaps: Counter[str] = Counter()
        attribute_gap_nodes = 0
        for node in nodes:
            missing = _missing_graph_attributes(node)
            if missing:
                attribute_gap_nodes += 1
                for field in missing:
                    attribute_gaps[field] += 1
        if attribute_gap_nodes:
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "missing_attribute",
                subtype="node_schema",
                task_id=task_id,
                scenario=scenario,
                severity="high",
                count=attribute_gap_nodes,
                evidence={
                    "missing_attribute_fields": dict(attribute_gaps),
                    "node_count": len(nodes),
                    "required_fields": list(GRAPH_ATTRIBUTE_GAPS),
                },
            )

        # Lifecycle gaps: v1 does not yet encode the modified stage explicitly.
        lifecycle_gap_nodes = 0
        lifecycle_missing_fields: Counter[str] = Counter()
        for node in nodes:
            missing = _missing_graph_lifecycle(node)
            if missing:
                lifecycle_gap_nodes += 1
                for field in missing:
                    lifecycle_missing_fields[field] += 1
        if lifecycle_gap_nodes:
            _add_issue(
                issues,
                counts,
                subtype_counts,
                "missing_lifecycle",
                subtype="node_lifecycle",
                task_id=task_id,
                scenario=scenario,
                severity=_severity_for_ratio(lifecycle_gap_nodes / len(nodes) if nodes else None),
                count=lifecycle_gap_nodes,
                evidence={
                    "missing_lifecycle_fields": dict(lifecycle_missing_fields),
                    "node_count": len(nodes),
                    "required_fields": list(GRAPH_LIFECYCLE_GAPS),
                },
            )

    failure_types: Dict[str, Any] = {}
    for gap_type, total in counts.items():
        failure_types[gap_type] = {
            "count": total,
            "subtypes": dict(subtype_counts.get(gap_type, {})),
        }

    return {
        "schema_version": "graph_information_gap_analysis.v1",
        "records_processed": len(records),
        "failure_types": failure_types,
        "issues": [issue.__dict__ for issue in issues],
        "task_summaries": list(task_buckets.values()),
    }


def render_graph_information_gap_analysis_markdown(analysis: Dict[str, Any]) -> str:
    lines = ["# Graph Information Gap Analysis", ""]
    lines.extend(
        [
            "| Gap Type | Count | Subtypes |",
            "| --- | --- | --- |",
        ]
    )
    for gap_type, payload in sorted((analysis.get("failure_types") or {}).items()):
        subtypes = payload.get("subtypes") or {}
        subtype_text = ", ".join(f"{key}:{value}" for key, value in sorted(subtypes.items())) if subtypes else ""
        lines.append(f"| {gap_type} | {payload.get('count')} | {subtype_text} |")

    lines.extend(["", "## Representative Evidence", ""])
    for issue in (analysis.get("issues") or [])[:12]:
        lines.append(
            f"- {issue.get('gap_type')} / {issue.get('subtype') or '-'} / {issue.get('scenario') or 'unknown'}: "
            f"{issue.get('evidence')}"
        )
    lines.append("")
    return "\n".join(lines)


def write_graph_information_gap_outputs(analysis: Dict[str, Any], output_dir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "graph_information_gap_analysis.json"
    markdown_path = output_path / "graph_information_gap_analysis.md"
    json_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(render_graph_information_gap_analysis_markdown(analysis), encoding="utf-8")
    return {"json": json_path, "markdown": markdown_path}
