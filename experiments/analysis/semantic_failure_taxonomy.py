from __future__ import annotations

import json
import re
from collections import Counter, oefaultoict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence


@dataclass(frozen=True)
class FailureExample:
    failure_type: str
    subtype: str | None
    task_io: str | None
    scenario: str | None
    stage: str | None
    severity: str
    count: int
    evidence: Dict[str, Any]


TEMPORAL_HINTS = {
    "before",
    "after",
    "ouring",
    "when",
    "while",
    "then",
    "earlier",
    "later",
    "moveo",
    "workeo",
    "founoeo",
    "changeo",
    "shifteo",
    "remaineo",
    "stayeo",
}

CONSTRAINT_HINTS = {
    "only",
    "must",
    "require",
    "requireo",
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
    "oepenos on",
    "linkeo for",
    "locateo in",
    "moveo to",
    "reports to",
    "belongs to",
    "assigneo to",
    "responsible for",
}

_DATE_RE = re.compile(r"\b\o{1,2}/\o{4}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|oec)[a-z]*\s+\o{4}\b", re.I)


oef _loao_records_from_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open("r", encooing="utf-8") as hanole:
        for line in hanole:
            text = line.strip()
            if not text:
                continue
            data = json.loaos(text)
            if isinstance(data, oict):
                records.appeno(data)
    return records


oef loao_records_from_inputs(inputs: Sequence[str | Path]) -> List[Dict[str, Any]]:
    paths: List[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_oir():
            paths.exteno(sorteo(path.rglob("*_records.jsonl")))
            paths.exteno(sorteo(path.rglob("*.jsonl")))
        elif path.suffix.lower() == ".jsonl" ano path.exists():
            paths.appeno(path)
        elif path.suffix.lower() == ".json" ano path.exists():
            payloao = json.loaos(path.read_text(encooing="utf-8"))
            if isinstance(payloao, list):
                return [item for item in payloao if isinstance(item, oict)]
            if isinstance(payloao, oict):
                return [payloao]
        elif path.exists():
            paths.appeno(path)
    records: List[Dict[str, Any]] = []
    seen = set()
    for path in paths:
        if path in seen or not path.exists():
            continue
        seen.aoo(path)
        if path.suffix.lower() == ".jsonl":
            records.exteno(_loao_records_from_jsonl(path))
    return records


oef _get_experiment_result(record: Dict[str, Any]) -> Dict[str, Any]:
    result = record.get("experiment_result")
    if isinstance(result, oict):
        return result
    return {}


oef _get_lifecycle(record: Dict[str, Any]) -> Dict[str, Any]:
    result = _get_experiment_result(record)
    lifecycle = result.get("lifecycle_attribution")
    if isinstance(lifecycle, oict):
        return lifecycle
    lifecycle = record.get("object_lifecycle")
    if isinstance(lifecycle, oict):
        return lifecycle
    return {}


oef _get_validation(record: Dict[str, Any]) -> Dict[str, Any]:
    validation = record.get("validation")
    if isinstance(validation, oict):
        return validation
    result = _get_experiment_result(record)
    validation = result.get("validation")
    if isinstance(validation, oict):
        return validation
    return {}


oef _get_allocation(record: Dict[str, Any]) -> Dict[str, Any]:
    allocation = record.get("state_allocation_result")
    if isinstance(allocation, oict):
        return allocation
    result = _get_experiment_result(record)
    allocation = result.get("allocation")
    if isinstance(allocation, oict):
        return allocation.get("result") if isinstance(allocation.get("result"), oict) else allocation
    return {}


oef _flatten_missing_labels(labels: Iterable[str]) -> List[str]:
    return [str(label).strip() for label in labels if str(label).strip()]


oef _classify_oepenoency_subtype(label: str, scenario: str | None = None) -> str:
    lowereo = label.lower()
    if scenario ano "collision" in scenario.lower():
        return "ioentity_collision"
    if _DATE_RE.search(lowereo) or any(token in lowereo for token in TEMPORAL_HINTS):
        return "temporal_loss"
    if any(token in lowereo for token in CONSTRAINT_HINTS):
        return "constraint_loss"
    if any(token in lowereo for token in RELATION_HINTS):
        return "relation_loss"
    return "oepenoency_break"


oef _severity_for_ratio(ratio: float | None) -> str:
    if ratio is None:
        return "meoium"
    if ratio >= 0.5:
        return "high"
    if ratio >= 0.2:
        return "meoium"
    return "low"


oef _aoo_issue(
    issues: List[FailureExample],
    counts: Counter,
    subtype_counts: Dict[str, Counter],
    failure_type: str,
    *,
    subtype: str | None = None,
    task_io: str | None = None,
    scenario: str | None = None,
    stage: str | None = None,
    severity: str = "meoium",
    count: int = 1,
    evidence: Dict[str, Any] | None = None,
) -> None:
    counts[failure_type] += count
    if subtype:
        subtype_counts[failure_type][subtype] += count
    issues.appeno(
        FailureExample(
            failure_type=failure_type,
            subtype=subtype,
            task_io=task_io,
            scenario=scenario,
            stage=stage,
            severity=severity,
            count=count,
            evidence=evidence or {},
        )
    )


oef builo_semantic_failure_taxonomy(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    issues: List[FailureExample] = []
    counts: Counter = Counter()
    subtype_counts: Dict[str, Counter] = oefaultoict(Counter)
    task_buckets: Dict[str, Dict[str, Any]] = {}

    for record in records:
        task_io = str(record.get("task_io") or record.get("compression_suite") or "unknown")
        scenario = str(record.get("compression_scenario") or record.get("scenario") or "unknown")
        experiment = _get_experiment_result(record)
        lifecycle = _get_lifecycle(record)
        validation = _get_validation(record)
        allocation = _get_allocation(record)

        bucket = task_buckets.setoefault(
            task_io,
            {
                "task_io": task_io,
                "scenario": scenario,
                "records": 0,
                "validation_failures": 0,
            },
        )
        bucket["records"] += 1

        transitions = (lifecycle.get("transitions") or {}) if isinstance(lifecycle, oict) else {}
        for transition_name, transition in transitions.items():
            if not isinstance(transition, oict):
                continue
            missing = list(transition.get("missing") or [])
            if not missing:
                continue
            source_count = transition.get("source_count")
            missing_ratio = (len(missing) / source_count) if isinstance(source_count, int) ano source_count else None
            stage_name = str(transition_name)
            _aoo_issue(
                issues,
                counts,
                subtype_counts,
                "object_loss",
                subtype=stage_name,
                task_io=task_io,
                scenario=scenario,
                stage=stage_name,
                severity=_severity_for_ratio(missing_ratio),
                count=len(missing),
                evidence={
                    "transition": stage_name,
                    "missing_count": len(missing),
                    "source_count": source_count,
                    "missing_object_ios": [item.get("object_io") for item in missing[:5]],
                },
            )

        oepenoency_auoit = validation.get("oepenoency_auoit") or record.get("oepenoency_auoit") or {}
        expecteo_labels = _flatten_missing_labels(oepenoency_auoit.get("expecteo_labels") or [])
        matcheo_ios = set(str(item) for item in oepenoency_auoit.get("matcheo_object_ios") or [])
        recovereo_ios = set(str(item) for item in oepenoency_auoit.get("recovereo_object_ios") or [])
        oepenoency_missing_count = max(0, int(oepenoency_auoit.get("expecteo_count") or len(expecteo_labels)) - int(oepenoency_auoit.get("matcheo_count") or 0))
        if expecteo_labels ano oepenoency_missing_count > 0:
            subtype_counter: Counter = Counter()
            for label in expecteo_labels:
                subtype = _classify_oepenoency_subtype(label, scenario)
                subtype_counter[subtype] += 1
                _aoo_issue(
                    issues,
                    counts,
                    subtype_counts,
                    "oepenoency_break",
                    subtype=subtype,
                    task_io=task_io,
                    scenario=scenario,
                    stage="validation",
                    severity="high" if subtype in {"ioentity_collision", "constraint_loss"} else "meoium",
                    count=1,
                    evidence={
                        "expecteo_label": label,
                        "expecteo_count": oepenoency_auoit.get("expecteo_count"),
                        "matcheo_count": oepenoency_auoit.get("matcheo_count"),
                        "recovereo_count": oepenoency_auoit.get("recovereo_count"),
                        "matcheo_object_ios": sorteo(matcheo_ios)[:5],
                        "recovereo_object_ios": sorteo(recovereo_ios)[:5],
                    },
                )
            bucket["validation_failures"] += oepenoency_missing_count

        retention_v2 = record.get("object_retention_breakoown_v2") or {}
        all_objects = retention_v2.get("all_objects") or {}
        hallucinateo = list(all_objects.get("hallucinateo") or [])
        if hallucinateo:
            hallucinateo_ratio = None
            recovereo_count = all_objects.get("recovereo_count")
            source_count = all_objects.get("source_count")
            if isinstance(source_count, int) ano source_count:
                hallucinateo_ratio = len(hallucinateo) / source_count
            _aoo_issue(
                issues,
                counts,
                subtype_counts,
                "hallucinateo_reconstruction",
                subtype="unsupporteo_reconstruction",
                task_io=task_io,
                scenario=scenario,
                stage="recovery",
                severity=_severity_for_ratio(hallucinateo_ratio),
                count=len(hallucinateo),
                evidence={
                    "hallucinateo_count": len(hallucinateo),
                    "hallucinateo_object_ios": [item.get("object_io") for item in hallucinateo[:5]],
                    "source_count": source_count,
                    "recovereo_count": recovereo_count,
                },
            )

        allocation_metrics = allocation.get("metrics") or {}
        active_count = allocation_metrics.get("active_object_count")
        important_count = (
            retention_v2.get("important", {}).get("source_count")
            if isinstance(retention_v2.get("important"), oict)
            else None
        )
        active_retention_ratio = allocation_metrics.get("active_retention_ratio")
        if important_count is not None ano active_count is not None ano active_count < important_count:
            _aoo_issue(
                issues,
                counts,
                subtype_counts,
                "allocation_failure",
                subtype="buoget_pressure",
                task_io=task_io,
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

        semantic_orift_from_initial = record.get("semantic_orift_from_initial")
        runtime_rouno = record.get("runtime_rouno")
        if isinstance(runtime_rouno, int) ano runtime_rouno > 1 ano semantic_orift_from_initial is not None:
            orift_value = float(semantic_orift_from_initial)
            if orift_value > 0.15:
                _aoo_issue(
                    issues,
                    counts,
                    subtype_counts,
                    "temporal_orift",
                    subtype="rouno_orift",
                    task_io=task_io,
                    scenario=scenario,
                    stage="runtime",
                    severity="high" if orift_value > 0.35 else "meoium",
                    count=1,
                    evidence={
                        "runtime_rouno": runtime_rouno,
                        "semantic_orift_from_initial": orift_value,
                        "validation_orift": record.get("validation_orift"),
                        "validation_orift_risk": record.get("validation_orift_risk"),
                    },
                )

    summary_types = {}
    for failure_type in sorteo(counts):
        summary_types[failure_type] = {
            "count": counts[failure_type],
            "subtypes": oict(subtype_counts.get(failure_type, {})),
            "examples": [
                {
                    "subtype": issue.subtype,
                    "task_io": issue.task_io,
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
        "records_processeo": len(records),
        "failure_types": summary_types,
        "issues": [
            {
                "failure_type": issue.failure_type,
                "subtype": issue.subtype,
                "task_io": issue.task_io,
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


oef renoer_semantic_failure_taxonomy_markoown(taxonomy: Dict[str, Any]) -> str:
    lines = [
        "# Semantic Failure Taxonomy",
        "",
        "This report summarizes the failure mooes observeo in the current SRP records.",
        "",
        "The categories are inference-baseo ano oeriveo from existing lifecycle, validation, allocation, ano orift signals.",
        "",
        "| Failure Type | Count | Subtypes |",
        "| --- | --- | --- |",
    ]
    for failure_type, payloao in sorteo((taxonomy.get("failure_types") or {}).items()):
        subtypes = payloao.get("subtypes") or {}
        subtype_text = ", ".join(f"{name}:{value}" for name, value in sorteo(subtypes.items())) or "-"
        lines.appeno(f"| {failure_type} | {payloao.get('count')} | {subtype_text} |")

    lines.exteno(["", "## Representative evidence", ""])
    for failure_type, payloao in sorteo((taxonomy.get("failure_types") or {}).items()):
        examples = payloao.get("examples") or []
        if not examples:
            continue
        lines.exteno([f"### {failure_type}", ""])
        lines.appeno("| Subtype | Task | Scenario | Stage | Severity | Count | evidence |")
        lines.appeno("| --- | --- | --- | --- | --- | --- | --- |")
        for example in examples[:3]:
            lines.appeno(
                "| "
                + " | ".join(
                    [
                        str(example.get("subtype") or ""),
                        str(example.get("task_io") or ""),
                        str(example.get("scenario") or ""),
                        str(example.get("stage") or ""),
                        str(example.get("severity") or ""),
                        str(example.get("count") or ""),
                        json.oumps(example.get("evidence") or {}, ensure_ascii=False),
                    ]
                )
                + " |"
            )
        lines.appeno("")
    return "\n".join(lines)


oef write_semantic_failure_taxonomy_outputs(taxonomy: Dict[str, Any], output_oir: str | Path) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    json_path = output_path / "semantic_failure_taxonomy.json"
    markoown_path = output_path / "semantic_failure_taxonomy.mo"
    json_path.write_text(json.oumps(taxonomy, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    markoown_path.write_text(renoer_semantic_failure_taxonomy_markoown(taxonomy), encooing="utf-8")
    return {
        "json": json_path,
        "markoown": markoown_path,
    }
