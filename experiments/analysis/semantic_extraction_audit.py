from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from ..common.export_support import write_records_csv, write_records_markdown


_DEPENDENCY_EDGE_RELATIONS = {"depends_on", "constrains", "derived_from", "temporal_before", "same_entity", "refers_to", "causes"}


def _as_dict_list(value: Any) -> List[Dict[str, Any]]:
    return [item for item in list(value or []) if isinstance(item, dict)]


def _safe_len(value: Any) -> int:
    return len(list(value or []))


def _node_has_v1_5_fields(node: Dict[str, Any]) -> bool:
    identity = node.get("identity") if isinstance(node, dict) else None
    attributes = node.get("attributes") if isinstance(node, dict) else None
    lifecycle = node.get("lifecycle") if isinstance(node, dict) else None
    has_identity = isinstance(identity, dict) and bool(identity.get("canonical_name")) and bool(identity.get("entity_key"))
    has_attributes = (
        isinstance(attributes, dict)
        and isinstance(attributes.get("properties"), dict)
        and isinstance(attributes.get("state"), dict)
    )
    has_lifecycle = isinstance(lifecycle, dict) and all(
        key in lifecycle for key in ["created", "modified", "compressed", "recovered", "verified", "retained"]
    )
    return has_identity and has_attributes and has_lifecycle


def _metric_average(records: Sequence[Dict[str, Any]], key_path: Sequence[str]) -> float | None:
    values: List[float] = []
    for record in records:
        current: Any = record
        for key in key_path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if current is not None:
            values.append(float(current))
    if not values:
        return None
    return sum(values) / len(values)


def _delta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(float(left) - float(right), 6)


def _summarize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    semantic_inventory = source_package.get("semantic_object_inventory") or {}
    source_objects = _as_dict_list(semantic_inventory.get("objects"))
    source_dependencies = _as_dict_list((source_package.get("semantic_dependencies") or {}).get("required_dependency_objects"))
    source_constraints = [str(item).strip() for item in list(source_package.get("constraints") or []) if str(item).strip()]

    graph = record.get("semantic_runtime_graph") or {}
    graph_nodes = _as_dict_list(graph.get("nodes"))
    graph_edges = _as_dict_list(graph.get("edges"))
    source_graph_nodes = [node for node in graph_nodes if bool((node.get("attributes") or {}).get("source_present", False))]
    dependency_clause_nodes = [node for node in graph_nodes if str(node.get("type", "")).strip() == "contract_semantic_dependency_tuple"]
    constraint_clause_nodes = [node for node in graph_nodes if str(node.get("type", "")).strip() == "contract_constraint"]
    recovered_package = record.get("recovered_state_package") or {}
    recovered_objects = _as_dict_list((recovered_package.get("typed_representation") or {}).get("objects"))

    graph_validation = record.get("semantic_graph_validation") or {}
    source_object_ids = {
        str(item.get("object_id") or item.get("id") or "").strip()
        for item in source_objects
        if str(item.get("object_id") or item.get("id") or "").strip()
    }
    recovered_object_ids = {
        str(item.get("object_id") or item.get("id") or "").strip()
        for item in recovered_objects
        if str(item.get("object_id") or item.get("id") or "").strip()
    }
    graph_source_object_ids = {
        str(node.get("id") or node.get("node_id") or "").strip()
        for node in source_graph_nodes
        if str(node.get("id") or node.get("node_id") or "").strip()
    }
    source_graph_object_nodes = [node for node in source_graph_nodes if str(node.get("id") or node.get("node_id") or "") in source_object_ids]
    graph_object_with_v1_5_fields = [node for node in source_graph_object_nodes if _node_has_v1_5_fields(node)]
    graph_object_with_v1_fields = [node for node in source_graph_object_nodes if bool(node.get("lifecycle"))]
    hallucinated_objects = [object_id for object_id in recovered_object_ids if object_id not in source_object_ids]

    source_information = {
        "objects": len(source_objects),
        "relations": len(source_dependencies),
        "constraints": len(source_constraints),
    }
    extracted_information = {
        "graph_nodes": len(source_graph_nodes),
        "graph_edges": len([edge for edge in graph_edges if str(edge.get("relation", "")) in _DEPENDENCY_EDGE_RELATIONS]),
        "dependency_nodes": len(dependency_clause_nodes),
        "constraint_nodes": len(constraint_clause_nodes),
        "recovered_objects": len(recovered_objects),
    }
    completeness = {
        "node_capture_rate": min(1.0, len(source_graph_object_nodes) / len(source_objects)) if source_objects else None,
        "relation_capture_rate": min(1.0, len(dependency_clause_nodes) / len(source_dependencies)) if source_dependencies else None,
        "constraint_capture_rate": min(1.0, len(constraint_clause_nodes) / len(source_constraints)) if source_constraints else None,
        "attribute_completeness": (len(graph_object_with_v1_5_fields) / len(source_graph_object_nodes)) if source_graph_object_nodes else None,
        "lifecycle_completeness": (len(graph_object_with_v1_fields) / len(source_graph_object_nodes)) if source_graph_object_nodes else None,
        "provenance_completeness": 0.0,
    }
    loss = {
        "node_loss": max(0, len(source_objects) - len(source_graph_object_nodes)),
        "edge_loss": max(0, len(source_dependencies) - len(dependency_clause_nodes)),
        "constraint_loss": max(0, len(source_constraints) - len(constraint_clause_nodes)),
        "hallucinated_object_count": len(hallucinated_objects),
    }
    recovery = {
        "recovered_object_recall": (len(source_object_ids & recovered_object_ids) / len(source_object_ids)) if source_object_ids else None,
        "hallucinated_object_count": len(hallucinated_objects),
        "validation_coverage": record.get("validation_coverage"),
        "dependency_recall": graph_validation.get("dependency_recall"),
        "graph_integrity_score": graph_validation.get("graph_integrity_score"),
    }
    return {
        "scenario": str(record.get("graph_recovery_scenario") or "unknown"),
        "group": str(record.get("graph_representation_group") or "unknown"),
        "graph_representation_version": str(record.get("graph_representation_version") or "unknown"),
        "graph_schema_version": str(record.get("graph_schema_version") or "unknown"),
        "source_information": source_information,
        "extracted_information": extracted_information,
        "completeness": completeness,
        "loss": loss,
        "recovery": recovery,
    }


def summarize_semantic_extraction_audit(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "groups": {},
        "scenarios": {},
        "comparison": {},
    }
    grouped_by_group: Dict[str, List[Dict[str, Any]]] = {}
    grouped_by_scenario: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        grouped_by_group.setdefault(str(record.get("group") or record.get("graph_representation_group") or "unknown"), []).append(record)
        grouped_by_scenario.setdefault(str(record.get("scenario") or record.get("graph_recovery_scenario") or "unknown"), []).append(record)

    for group, group_records in grouped_by_group.items():
        summary["groups"][group] = {
            "records": len(group_records),
            "source_information": _summarize_record(group_records[0])["source_information"] if group_records else {},
            "extracted_information": _summarize_record(group_records[0])["extracted_information"] if group_records else {},
            "completeness": _summarize_record(group_records[0])["completeness"] if group_records else {},
            "loss": _summarize_record(group_records[0])["loss"] if group_records else {},
            "recovery": {
                "recovered_object_recall": _metric_average(group_records, ["object_survival_rate"]),
                "hallucinated_object_count": _metric_average(group_records, ["hallucinated_count"]),
                "validation_coverage": _metric_average(group_records, ["validation_coverage"]),
                "dependency_recall": _metric_average(group_records, ["dependency_recall"]),
                "graph_integrity_score": _metric_average(group_records, ["graph_integrity_score"]),
            },
        }

    for scenario, scenario_records in grouped_by_scenario.items():
        scenario_summaries = [_summarize_record(record) for record in scenario_records]
        scenario_groups: Dict[str, Dict[str, Any]] = {}
        for group in ["A", "B", "C", "D"]:
            group_records = [record for record in scenario_records if str(record.get("group") or record.get("graph_representation_group") or "unknown") == group]
            if not group_records:
                continue
            first = _summarize_record(group_records[0])
            scenario_groups[group] = {
                "records": len(group_records),
                "source_information": first["source_information"],
                "extracted_information": first["extracted_information"],
                "completeness": first["completeness"],
                "loss": first["loss"],
                "recovery": first["recovery"],
            }
        delta = {}
        if "C" in scenario_groups and "D" in scenario_groups:
            delta["D_minus_C"] = {
                "node_capture_rate": _delta(
                    scenario_groups["D"]["completeness"].get("node_capture_rate"),
                    scenario_groups["C"]["completeness"].get("node_capture_rate"),
                ),
                "relation_capture_rate": _delta(
                    scenario_groups["D"]["completeness"].get("relation_capture_rate"),
                    scenario_groups["C"]["completeness"].get("relation_capture_rate"),
                ),
                "constraint_capture_rate": _delta(
                    scenario_groups["D"]["completeness"].get("constraint_capture_rate"),
                    scenario_groups["C"]["completeness"].get("constraint_capture_rate"),
                ),
                "attribute_completeness": _delta(
                    scenario_groups["D"]["completeness"].get("attribute_completeness"),
                    scenario_groups["C"]["completeness"].get("attribute_completeness"),
                ),
                "lifecycle_completeness": _delta(
                    scenario_groups["D"]["completeness"].get("lifecycle_completeness"),
                    scenario_groups["C"]["completeness"].get("lifecycle_completeness"),
                ),
                "provenance_completeness": _delta(
                    scenario_groups["D"]["completeness"].get("provenance_completeness"),
                    scenario_groups["C"]["completeness"].get("provenance_completeness"),
                ),
                "graph_integrity_score": _delta(
                    scenario_groups["D"]["recovery"].get("graph_integrity_score"),
                    scenario_groups["C"]["recovery"].get("graph_integrity_score"),
                ),
            }
        summary["scenarios"][scenario] = {
            "records": len(scenario_records),
            "groups": scenario_groups,
            "delta": delta,
        }

    if "C" in summary["groups"] and "D" in summary["groups"]:
        summary["comparison"]["graph_v1_5_minus_graph_v1"] = {
            "node_capture_rate": _delta(
                summary["groups"]["D"]["completeness"].get("node_capture_rate"),
                summary["groups"]["C"]["completeness"].get("node_capture_rate"),
            ),
            "relation_capture_rate": _delta(
                summary["groups"]["D"]["completeness"].get("relation_capture_rate"),
                summary["groups"]["C"]["completeness"].get("relation_capture_rate"),
            ),
            "constraint_capture_rate": _delta(
                summary["groups"]["D"]["completeness"].get("constraint_capture_rate"),
                summary["groups"]["C"]["completeness"].get("constraint_capture_rate"),
            ),
            "attribute_completeness": _delta(
                summary["groups"]["D"]["completeness"].get("attribute_completeness"),
                summary["groups"]["C"]["completeness"].get("attribute_completeness"),
            ),
            "lifecycle_completeness": _delta(
                summary["groups"]["D"]["completeness"].get("lifecycle_completeness"),
                summary["groups"]["C"]["completeness"].get("lifecycle_completeness"),
            ),
            "provenance_completeness": _delta(
                summary["groups"]["D"]["completeness"].get("provenance_completeness"),
                summary["groups"]["C"]["completeness"].get("provenance_completeness"),
            ),
            "graph_integrity_score": _delta(
                summary["groups"]["D"]["recovery"].get("graph_integrity_score"),
                summary["groups"]["C"]["recovery"].get("graph_integrity_score"),
            ),
        }
    return summary


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def render_semantic_extraction_audit_markdown(summary: Dict[str, Any]) -> str:
    lines = ["# Semantic Extraction Audit", ""]
    lines.extend(
        [
            "| Group | Records | Node Capture | Relation Capture | Constraint Capture | Attribute Completeness | Lifecycle Completeness | Provenance Completeness | Graph Integrity | Node Loss | Edge Loss | Constraint Loss |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for group, group_summary in sorted((summary.get("groups") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(group),
                    _fmt(group_summary.get("records")),
                    _fmt((group_summary.get("completeness") or {}).get("node_capture_rate")),
                    _fmt((group_summary.get("completeness") or {}).get("relation_capture_rate")),
                    _fmt((group_summary.get("completeness") or {}).get("constraint_capture_rate")),
                    _fmt((group_summary.get("completeness") or {}).get("attribute_completeness")),
                    _fmt((group_summary.get("completeness") or {}).get("lifecycle_completeness")),
                    _fmt((group_summary.get("completeness") or {}).get("provenance_completeness")),
                    _fmt((group_summary.get("recovery") or {}).get("graph_integrity_score")),
                    _fmt((group_summary.get("loss") or {}).get("node_loss")),
                    _fmt((group_summary.get("loss") or {}).get("edge_loss")),
                    _fmt((group_summary.get("loss") or {}).get("constraint_loss")),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Scenario Summary", ""])
    lines.extend(
        [
            "| Scenario | Group | Node Capture | Relation Capture | Constraint Capture | Attribute Completeness | Lifecycle Completeness | Provenance Completeness | Graph Integrity | Node Loss | Edge Loss | Constraint Loss |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorted((summary.get("scenarios") or {}).items()):
        for group, group_summary in sorted((scenario_summary.get("groups") or {}).items()):
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(scenario),
                        str(group),
                        _fmt((group_summary.get("completeness") or {}).get("node_capture_rate")),
                        _fmt((group_summary.get("completeness") or {}).get("relation_capture_rate")),
                        _fmt((group_summary.get("completeness") or {}).get("constraint_capture_rate")),
                        _fmt((group_summary.get("completeness") or {}).get("attribute_completeness")),
                        _fmt((group_summary.get("completeness") or {}).get("lifecycle_completeness")),
                        _fmt((group_summary.get("completeness") or {}).get("provenance_completeness")),
                        _fmt((group_summary.get("recovery") or {}).get("graph_integrity_score")),
                        _fmt((group_summary.get("loss") or {}).get("node_loss")),
                        _fmt((group_summary.get("loss") or {}).get("edge_loss")),
                        _fmt((group_summary.get("loss") or {}).get("constraint_loss")),
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Representation Delta", ""])
    lines.extend(
        [
            "| Comparison | Node Capture | Relation Capture | Constraint Capture | Attribute Completeness | Lifecycle Completeness | Provenance Completeness | Graph Integrity |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for comparison_name, comparison_summary in sorted((summary.get("comparison") or {}).items()):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(comparison_name),
                    _fmt(comparison_summary.get("node_capture_rate")),
                    _fmt(comparison_summary.get("relation_capture_rate")),
                    _fmt(comparison_summary.get("constraint_capture_rate")),
                    _fmt(comparison_summary.get("attribute_completeness")),
                    _fmt(comparison_summary.get("lifecycle_completeness")),
                    _fmt(comparison_summary.get("provenance_completeness")),
                    _fmt(comparison_summary.get("graph_integrity_score")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def load_semantic_extraction_records(records_jsonl: str | Path) -> List[Dict[str, Any]]:
    path = Path(records_jsonl)
    records: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def write_semantic_extraction_audit_outputs(
    records: Sequence[Dict[str, Any]],
    output_dir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_path / "semantic_extraction_audit_records.jsonl"
    csv_path = output_path / "semantic_extraction_audit_records.csv"
    markdown_path = output_path / "semantic_extraction_audit.md"
    summary_path = output_path / "semantic_extraction_audit_summary.md"
    json_path = output_path / "semantic_extraction_audit.json"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    summary = summarize_semantic_extraction_audit(records)
    write_records_csv(records, csv_path)
    write_records_markdown(records, markdown_path)
    summary_path.write_text(render_semantic_extraction_audit_markdown(summary), encoding="utf-8")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markdown": markdown_path,
        "summary": summary_path,
        "json": json_path,
    }
