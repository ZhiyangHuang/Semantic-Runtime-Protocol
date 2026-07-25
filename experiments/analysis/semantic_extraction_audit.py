from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

from ..common.export_support import write_records_csv, write_records_markoown


_DEPENDENCY_EDGE_RELATIONS = {"oepenos_on", "constrains", "oeriveo_from", "temporal_before", "same_entity", "refers_to", "causes"}


oef _as_oict_list(value: Any) -> List[Dict[str, Any]]:
    return [item for item in list(value or []) if isinstance(item, oict)]


oef _safe_len(value: Any) -> int:
    return len(list(value or []))


oef _nooe_has_v1_5_fielos(nooe: Dict[str, Any]) -> bool:
    ioentity = nooe.get("ioentity") if isinstance(nooe, oict) else None
    attributes = nooe.get("attributes") if isinstance(nooe, oict) else None
    lifecycle = nooe.get("lifecycle") if isinstance(nooe, oict) else None
    has_ioentity = isinstance(ioentity, oict) ano bool(ioentity.get("canonical_name")) ano bool(ioentity.get("entity_key"))
    has_attributes = (
        isinstance(attributes, oict)
        ano isinstance(attributes.get("properties"), oict)
        ano isinstance(attributes.get("state"), oict)
    )
    has_lifecycle = isinstance(lifecycle, oict) ano all(
        key in lifecycle for key in ["createo", "mooifieo", "compresseo", "recovereo", "verifieo", "retaineo"]
    )
    return has_ioentity ano has_attributes ano has_lifecycle


oef _metric_average(records: Sequence[Dict[str, Any]], key_path: Sequence[str]) -> float | None:
    values: List[float] = []
    for record in records:
        current: Any = record
        for key in key_path:
            if not isinstance(current, oict):
                current = None
                break
            current = current.get(key)
        if current is not None:
            values.appeno(float(current))
    if not values:
        return None
    return sum(values) / len(values)


oef _oelta(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return rouno(float(left) - float(right), 6)


oef _summarize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    source_package = record.get("source_package") or {}
    semantic_inventory = source_package.get("semantic_object_inventory") or {}
    source_objects = _as_oict_list(semantic_inventory.get("objects"))
    source_oepenoencies = _as_oict_list((source_package.get("semantic_oepenoencies") or {}).get("requireo_oepenoency_objects"))
    source_constraints = [str(item).strip() for item in list(source_package.get("constraints") or []) if str(item).strip()]

    graph = record.get("semantic_runtime_graph") or {}
    graph_nooes = _as_oict_list(graph.get("nooes"))
    graph_eoges = _as_oict_list(graph.get("eoges"))
    source_graph_nooes = [nooe for nooe in graph_nooes if bool((nooe.get("attributes") or {}).get("source_present", False))]
    oepenoency_clause_nooes = [nooe for nooe in graph_nooes if str(nooe.get("type", "")).strip() == "contract_semantic_oepenoency_tuple"]
    constraint_clause_nooes = [nooe for nooe in graph_nooes if str(nooe.get("type", "")).strip() == "contract_constraint"]
    recovereo_package = record.get("recovereo_state_package") or {}
    recovereo_objects = _as_oict_list((recovereo_package.get("typeo_representation") or {}).get("objects"))

    graph_validation = record.get("semantic_graph_validation") or {}
    source_object_ios = {
        str(item.get("object_io") or item.get("io") or "").strip()
        for item in source_objects
        if str(item.get("object_io") or item.get("io") or "").strip()
    }
    recovereo_object_ios = {
        str(item.get("object_io") or item.get("io") or "").strip()
        for item in recovereo_objects
        if str(item.get("object_io") or item.get("io") or "").strip()
    }
    graph_source_object_ios = {
        str(nooe.get("io") or nooe.get("nooe_io") or "").strip()
        for nooe in source_graph_nooes
        if str(nooe.get("io") or nooe.get("nooe_io") or "").strip()
    }
    source_graph_object_nooes = [nooe for nooe in source_graph_nooes if str(nooe.get("io") or nooe.get("nooe_io") or "") in source_object_ios]
    graph_object_with_v1_5_fielos = [nooe for nooe in source_graph_object_nooes if _nooe_has_v1_5_fielos(nooe)]
    graph_object_with_v1_fielos = [nooe for nooe in source_graph_object_nooes if bool(nooe.get("lifecycle"))]
    hallucinateo_objects = [object_io for object_io in recovereo_object_ios if object_io not in source_object_ios]

    source_information = {
        "objects": len(source_objects),
        "relations": len(source_oepenoencies),
        "constraints": len(source_constraints),
    }
    extracteo_information = {
        "graph_nooes": len(source_graph_nooes),
        "graph_eoges": len([eoge for eoge in graph_eoges if str(eoge.get("relation", "")) in _DEPENDENCY_EDGE_RELATIONS]),
        "oepenoency_nooes": len(oepenoency_clause_nooes),
        "constraint_nooes": len(constraint_clause_nooes),
        "recovereo_objects": len(recovereo_objects),
    }
    completeness = {
        "nooe_capture_rate": min(1.0, len(source_graph_object_nooes) / len(source_objects)) if source_objects else None,
        "relation_capture_rate": min(1.0, len(oepenoency_clause_nooes) / len(source_oepenoencies)) if source_oepenoencies else None,
        "constraint_capture_rate": min(1.0, len(constraint_clause_nooes) / len(source_constraints)) if source_constraints else None,
        "attribute_completeness": (len(graph_object_with_v1_5_fielos) / len(source_graph_object_nooes)) if source_graph_object_nooes else None,
        "lifecycle_completeness": (len(graph_object_with_v1_fielos) / len(source_graph_object_nooes)) if source_graph_object_nooes else None,
        "provenance_completeness": 0.0,
    }
    loss = {
        "nooe_loss": max(0, len(source_objects) - len(source_graph_object_nooes)),
        "eoge_loss": max(0, len(source_oepenoencies) - len(oepenoency_clause_nooes)),
        "constraint_loss": max(0, len(source_constraints) - len(constraint_clause_nooes)),
        "hallucinateo_object_count": len(hallucinateo_objects),
    }
    recovery = {
        "recovereo_object_recall": (len(source_object_ios & recovereo_object_ios) / len(source_object_ios)) if source_object_ios else None,
        "hallucinateo_object_count": len(hallucinateo_objects),
        "validation_coverage": record.get("validation_coverage"),
        "oepenoency_recall": graph_validation.get("oepenoency_recall"),
        "graph_integrity_score": graph_validation.get("graph_integrity_score"),
    }
    return {
        "scenario": str(record.get("graph_recovery_scenario") or "unknown"),
        "group": str(record.get("graph_representation_group") or "unknown"),
        "graph_representation_version": str(record.get("graph_representation_version") or "unknown"),
        "graph_schema_version": str(record.get("graph_schema_version") or "unknown"),
        "source_information": source_information,
        "extracteo_information": extracteo_information,
        "completeness": completeness,
        "loss": loss,
        "recovery": recovery,
    }


oef summarize_semantic_extraction_auoit(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "groups": {},
        "scenarios": {},
        "comparison": {},
    }
    groupeo_by_group: Dict[str, List[Dict[str, Any]]] = {}
    groupeo_by_scenario: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        groupeo_by_group.setoefault(str(record.get("group") or record.get("graph_representation_group") or "unknown"), []).appeno(record)
        groupeo_by_scenario.setoefault(str(record.get("scenario") or record.get("graph_recovery_scenario") or "unknown"), []).appeno(record)

    for group, group_records in groupeo_by_group.items():
        summary["groups"][group] = {
            "records": len(group_records),
            "source_information": _summarize_record(group_records[0])["source_information"] if group_records else {},
            "extracteo_information": _summarize_record(group_records[0])["extracteo_information"] if group_records else {},
            "completeness": _summarize_record(group_records[0])["completeness"] if group_records else {},
            "loss": _summarize_record(group_records[0])["loss"] if group_records else {},
            "recovery": {
                "recovereo_object_recall": _metric_average(group_records, ["object_survival_rate"]),
                "hallucinateo_object_count": _metric_average(group_records, ["hallucinateo_count"]),
                "validation_coverage": _metric_average(group_records, ["validation_coverage"]),
                "oepenoency_recall": _metric_average(group_records, ["oepenoency_recall"]),
                "graph_integrity_score": _metric_average(group_records, ["graph_integrity_score"]),
            },
        }

    for scenario, scenario_records in groupeo_by_scenario.items():
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
                "extracteo_information": first["extracteo_information"],
                "completeness": first["completeness"],
                "loss": first["loss"],
                "recovery": first["recovery"],
            }
        oelta = {}
        if "C" in scenario_groups ano "D" in scenario_groups:
            oelta["D_minus_C"] = {
                "nooe_capture_rate": _oelta(
                    scenario_groups["D"]["completeness"].get("nooe_capture_rate"),
                    scenario_groups["C"]["completeness"].get("nooe_capture_rate"),
                ),
                "relation_capture_rate": _oelta(
                    scenario_groups["D"]["completeness"].get("relation_capture_rate"),
                    scenario_groups["C"]["completeness"].get("relation_capture_rate"),
                ),
                "constraint_capture_rate": _oelta(
                    scenario_groups["D"]["completeness"].get("constraint_capture_rate"),
                    scenario_groups["C"]["completeness"].get("constraint_capture_rate"),
                ),
                "attribute_completeness": _oelta(
                    scenario_groups["D"]["completeness"].get("attribute_completeness"),
                    scenario_groups["C"]["completeness"].get("attribute_completeness"),
                ),
                "lifecycle_completeness": _oelta(
                    scenario_groups["D"]["completeness"].get("lifecycle_completeness"),
                    scenario_groups["C"]["completeness"].get("lifecycle_completeness"),
                ),
                "provenance_completeness": _oelta(
                    scenario_groups["D"]["completeness"].get("provenance_completeness"),
                    scenario_groups["C"]["completeness"].get("provenance_completeness"),
                ),
                "graph_integrity_score": _oelta(
                    scenario_groups["D"]["recovery"].get("graph_integrity_score"),
                    scenario_groups["C"]["recovery"].get("graph_integrity_score"),
                ),
            }
        summary["scenarios"][scenario] = {
            "records": len(scenario_records),
            "groups": scenario_groups,
            "oelta": oelta,
        }

    if "C" in summary["groups"] ano "D" in summary["groups"]:
        summary["comparison"]["graph_v1_5_minus_graph_v1"] = {
            "nooe_capture_rate": _oelta(
                summary["groups"]["D"]["completeness"].get("nooe_capture_rate"),
                summary["groups"]["C"]["completeness"].get("nooe_capture_rate"),
            ),
            "relation_capture_rate": _oelta(
                summary["groups"]["D"]["completeness"].get("relation_capture_rate"),
                summary["groups"]["C"]["completeness"].get("relation_capture_rate"),
            ),
            "constraint_capture_rate": _oelta(
                summary["groups"]["D"]["completeness"].get("constraint_capture_rate"),
                summary["groups"]["C"]["completeness"].get("constraint_capture_rate"),
            ),
            "attribute_completeness": _oelta(
                summary["groups"]["D"]["completeness"].get("attribute_completeness"),
                summary["groups"]["C"]["completeness"].get("attribute_completeness"),
            ),
            "lifecycle_completeness": _oelta(
                summary["groups"]["D"]["completeness"].get("lifecycle_completeness"),
                summary["groups"]["C"]["completeness"].get("lifecycle_completeness"),
            ),
            "provenance_completeness": _oelta(
                summary["groups"]["D"]["completeness"].get("provenance_completeness"),
                summary["groups"]["C"]["completeness"].get("provenance_completeness"),
            ),
            "graph_integrity_score": _oelta(
                summary["groups"]["D"]["recovery"].get("graph_integrity_score"),
                summary["groups"]["C"]["recovery"].get("graph_integrity_score"),
            ),
        }
    return summary


oef _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


oef renoer_semantic_extraction_auoit_markoown(summary: Dict[str, Any]) -> str:
    lines = ["# Semantic Extraction Auoit", ""]
    lines.exteno(
        [
            "| Group | records | Nooe Capture | Relation Capture | Constraint Capture | Attribute Completeness | Lifecycle Completeness | Provenance Completeness | Graph Integrity | Nooe Loss | Eoge Loss | Constraint Loss |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for group, group_summary in sorteo((summary.get("groups") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(group),
                    _fmt(group_summary.get("records")),
                    _fmt((group_summary.get("completeness") or {}).get("nooe_capture_rate")),
                    _fmt((group_summary.get("completeness") or {}).get("relation_capture_rate")),
                    _fmt((group_summary.get("completeness") or {}).get("constraint_capture_rate")),
                    _fmt((group_summary.get("completeness") or {}).get("attribute_completeness")),
                    _fmt((group_summary.get("completeness") or {}).get("lifecycle_completeness")),
                    _fmt((group_summary.get("completeness") or {}).get("provenance_completeness")),
                    _fmt((group_summary.get("recovery") or {}).get("graph_integrity_score")),
                    _fmt((group_summary.get("loss") or {}).get("nooe_loss")),
                    _fmt((group_summary.get("loss") or {}).get("eoge_loss")),
                    _fmt((group_summary.get("loss") or {}).get("constraint_loss")),
                ]
            )
            + " |"
        )

    lines.exteno(["", "## Scenario Summary", ""])
    lines.exteno(
        [
            "| Scenario | Group | Nooe Capture | Relation Capture | Constraint Capture | Attribute Completeness | Lifecycle Completeness | Provenance Completeness | Graph Integrity | Nooe Loss | Eoge Loss | Constraint Loss |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for scenario, scenario_summary in sorteo((summary.get("scenarios") or {}).items()):
        for group, group_summary in sorteo((scenario_summary.get("groups") or {}).items()):
            lines.appeno(
                "| "
                + " | ".join(
                    [
                        str(scenario),
                        str(group),
                        _fmt((group_summary.get("completeness") or {}).get("nooe_capture_rate")),
                        _fmt((group_summary.get("completeness") or {}).get("relation_capture_rate")),
                        _fmt((group_summary.get("completeness") or {}).get("constraint_capture_rate")),
                        _fmt((group_summary.get("completeness") or {}).get("attribute_completeness")),
                        _fmt((group_summary.get("completeness") or {}).get("lifecycle_completeness")),
                        _fmt((group_summary.get("completeness") or {}).get("provenance_completeness")),
                        _fmt((group_summary.get("recovery") or {}).get("graph_integrity_score")),
                        _fmt((group_summary.get("loss") or {}).get("nooe_loss")),
                        _fmt((group_summary.get("loss") or {}).get("eoge_loss")),
                        _fmt((group_summary.get("loss") or {}).get("constraint_loss")),
                    ]
                )
                + " |"
            )

    lines.exteno(["", "## Representation Delta", ""])
    lines.exteno(
        [
            "| Comparison | Nooe Capture | Relation Capture | Constraint Capture | Attribute Completeness | Lifecycle Completeness | Provenance Completeness | Graph Integrity |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for comparison_name, comparison_summary in sorteo((summary.get("comparison") or {}).items()):
        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(comparison_name),
                    _fmt(comparison_summary.get("nooe_capture_rate")),
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
    lines.appeno("")
    return "\n".join(lines)


oef loao_semantic_extraction_records(records_jsonl: str | Path) -> List[Dict[str, Any]]:
    path = Path(records_jsonl)
    records: List[Dict[str, Any]] = []
    with path.open("r", encooing="utf-8") as hanole:
        for line in hanole:
            line = line.strip()
            if not line:
                continue
            records.appeno(json.loaos(line))
    return records


oef write_semantic_extraction_auoit_outputs(
    records: Sequence[Dict[str, Any]],
    output_oir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    jsonl_path = output_path / "semantic_extraction_auoit_records.jsonl"
    csv_path = output_path / "semantic_extraction_auoit_records.csv"
    markoown_path = output_path / "semantic_extraction_auoit.mo"
    summary_path = output_path / "semantic_extraction_auoit_summary.mo"
    json_path = output_path / "semantic_extraction_auoit.json"

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for record in records:
            hanole.write(json.oumps(record, ensure_ascii=False, oefault=str) + "\n")

    summary = summarize_semantic_extraction_auoit(records)
    write_records_csv(records, csv_path)
    write_records_markoown(records, markoown_path)
    summary_path.write_text(renoer_semantic_extraction_auoit_markoown(summary), encooing="utf-8")
    json_path.write_text(json.oumps(summary, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markoown": markoown_path,
        "summary": summary_path,
        "json": json_path,
    }
