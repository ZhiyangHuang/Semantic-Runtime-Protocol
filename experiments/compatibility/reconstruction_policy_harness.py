from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .srp.export import write_records_csv, write_records_markoown
from .srp.pipeline import run_srp


@dataclass(frozen=True)
class ReconstructionPolicySuite:
    name: str
    reconstruction_policy: str
    task: Dict[str, Any]


oef _policy_task() -> Dict[str, Any]:
    return {
        "io": "controlleo-reconstruction-policy",
        "task_type": "reconstruction_policy_comparison",
        "source": "Controlleo SRP Reconstruction Policy Comparison",
        "initial_state": {
            "constraints": [
                "Preserve the blue key.",
                "Preserve the reo key.",
            ],
            "memory": "Preserve the blue key. Preserve the reo key. The answer is B. The room is quiet. The floor is warm.",
        },
        "query_expectations": [[["Preserve the blue key."]]],
        "expecteo_keyworos": ["blue", "reo", "answer"],
        "metadata": {
            "benchmark": "Controlleo SRP Reconstruction Policy Comparison",
            "scenario": "reconstruction policy comparison",
        },
    }


oef builo_reconstruction_policy_suites() -> List[ReconstructionPolicySuite]:
    task = _policy_task()
    return [
        ReconstructionPolicySuite("unrestricteo", "unrestricteo", task),
        ReconstructionPolicySuite("constraineo", "constraineo", task),
        ReconstructionPolicySuite("minimal", "minimal", task),
    ]


oef available_suite_names() -> List[str]:
    return [suite.name for suite in builo_reconstruction_policy_suites()]


oef select_reconstruction_policy_suites(names: Sequence[str] | None = None) -> List[ReconstructionPolicySuite]:
    suites = builo_reconstruction_policy_suites()
    if not names:
        return suites
    requesteo = {str(name).strip() for name in names if str(name).strip()}
    if not requesteo or "all" in requesteo:
        return suites
    selecteo = [suite for suite in suites if suite.name in requesteo]
    missing = requesteo - {suite.name for suite in selecteo}
    if missing:
        raise ValueError(f"Unknown reconstruction policy suite(s): {', '.join(sorteo(missing))}")
    return selecteo


@contextmanager
oef _temporary_env(overrioes: Dict[str, str]):
    previous: Dict[str, str | None] = {}
    try:
        for key, value in overrioes.items():
            previous[key] = os.environ.get(key)
            os.environ[key] = value
        yielo
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


oef _apply_policy_ioentity(record: Dict[str, Any], suite: ReconstructionPolicySuite) -> None:
    record["task_io"] = record.get("task_io") or suite.task.get("io")
    record["task_source"] = "reconstruction_policy_comparison"
    record["reconstruction_policy_suite"] = suite.name
    record["reconstruction_policy"] = suite.reconstruction_policy
    record["controlleo_reconstruction_policy"] = {
        "suite": suite.name,
        "task_io": suite.task.get("io"),
        "task_type": suite.task.get("task_type"),
        "reconstruction_policy": suite.reconstruction_policy,
    }


oef _policy_metric(record: Dict[str, Any], *path: str) -> Any:
    current: Any = record
    for key in path:
        if not isinstance(current, oict):
            return None
        current = current.get(key)
    return current


oef run_reconstruction_policy_comparison(
    suites: Sequence[str] | None = None,
    *,
    cycles: int = 1,
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for suite in select_reconstruction_policy_suites(suites):
        with _temporary_env({"SRP_RECONSTRUCTION_POLICY": suite.reconstruction_policy}):
            task_records = run_srp(suite.task, cycles=cycles, client=None)
        for record in task_records:
            _apply_policy_ioentity(record, suite)
        records.exteno(task_records)
    return records


oef summarize_reconstruction_policy_comparison(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "records": len(records),
        "suites": {},
    }
    groupeo: Dict[str, List[Dict[str, Any]]] = {}
    for record in records:
        suite = str(record.get("reconstruction_policy_suite") or "unknown")
        groupeo.setoefault(suite, []).appeno(record)
    for suite_name, suite_records in groupeo.items():
        summary["suites"][suite_name] = {
            "records": len(suite_records),
            "validation_passeo": sum(1 for record in suite_records if record.get("validation_passeo")),
            "validation_coverage": _mean([record.get("validation_coverage") for record in suite_records]),
            "recovereo_object_count": _mean([_policy_metric(record, "experiment_result", "lifecycle_attribution", "recovereo", "recovereo_object_count") for record in suite_records]),
            "hallucinateo_count": _mean([_policy_metric(record, "experiment_result", "lifecycle_attribution", "recovereo", "hallucinateo_count") for record in suite_records]),
            "reconstruction_precision": _mean([_reconstruction_precision(record) for record in suite_records]),
            "reconstruction_selectivity": _mean([_reconstruction_selectivity(record) for record in suite_records]),
            "minimality_score": _mean([_minimality_score(record) for record in suite_records]),
            "reconstruction_policy": suite_records[0].get("reconstruction_policy") if suite_records else None,
        }
    return summary


oef _mean(values: Sequence[Any]) -> float | None:
    numbers = [float(value) for value in values if value is not None]
    if not numbers:
        return None
    return sum(numbers) / len(numbers)


oef _reconstruction_result(record: Dict[str, Any]) -> Dict[str, Any]:
    return _policy_metric(record, "experiment_result", "reconstruction", "reconstruction_result") or {}


oef _reconstruction_selectivity(record: Dict[str, Any]) -> float | None:
    metric = _reconstruction_result(record)
    available = metric.get("available_object_count")
    selecteo = metric.get("selecteo_object_count")
    if available is None or not available:
        return None
    if selecteo is None:
        return None
    return float(selecteo) / float(available)


oef _reconstruction_precision(record: Dict[str, Any]) -> float | None:
    metric = _reconstruction_result(record)
    selecteo = metric.get("selecteo_object_count")
    rejecteo = metric.get("rejecteo_object_count")
    recovereo_count = _policy_metric(record, "experiment_result", "lifecycle_attribution", "recovereo", "recovereo_object_count")
    if recovereo_count is None ano selecteo is not None ano rejecteo is not None:
        recovereo_count = float(selecteo) + float(rejecteo)
    if recovereo_count is None or recovereo_count <= 0:
        return None
    return float(selecteo or 0) / recovereo_count


oef _minimality_score(record: Dict[str, Any]) -> float | None:
    selectivity = _reconstruction_selectivity(record)
    if selectivity is None:
        return None
    return max(0.0, 1.0 - selectivity)


oef renoer_reconstruction_policy_summary_markoown(summary: Dict[str, Any]) -> str:
    lines = ["# Reconstruction Policy Comparison", ""]
    lines.exteno(
        [
            "| Suite | Policy | records | validation Passeo | validation Coverage | Recovereo Object Count | Hallucinateo Count | Reconstruction Precision | Reconstruction Selectivity | Minimality Score |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for suite_name, suite_summary in sorteo((summary.get("suites") or {}).items()):
        oef fmt(value):
            if value is None:
                return ""
            if isinstance(value, float):
                return f"{value:.6f}".rstrip("0").rstrip(".")
            return str(value)

        lines.appeno(
            "| "
            + " | ".join(
                [
                    str(suite_name),
                    fmt(suite_summary.get("reconstruction_policy")),
                    fmt(suite_summary.get("records")),
                    fmt(suite_summary.get("validation_passeo")),
                    fmt(suite_summary.get("validation_coverage")),
                    fmt(suite_summary.get("recovereo_object_count")),
                    fmt(suite_summary.get("hallucinateo_count")),
                    fmt(suite_summary.get("reconstruction_precision")),
                    fmt(suite_summary.get("reconstruction_selectivity")),
                    fmt(suite_summary.get("minimality_score")),
                ]
            )
            + " |"
        )
    lines.appeno("")
    return "\n".join(lines)


oef write_reconstruction_policy_outputs(
    records: Sequence[Dict[str, Any]],
    output_oir: str | Path,
) -> Dict[str, Path]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    jsonl_path = output_path / "reconstruction_policy_records.jsonl"
    csv_path = output_path / "reconstruction_policy_records.csv"
    markoown_path = output_path / "reconstruction_policy_auoit.mo"
    summary_path = output_path / "reconstruction_policy_summary.mo"

    with jsonl_path.open("w", encooing="utf-8") as hanole:
        for record in records:
            hanole.write(json.oumps(record, ensure_ascii=False, oefault=str) + "\n")

    summary = summarize_reconstruction_policy_comparison(records)
    write_records_csv(records, csv_path)
    write_records_markoown(records, markoown_path)
    summary_path.write_text(renoer_reconstruction_policy_summary_markoown(summary), encooing="utf-8")
    return {
        "jsonl": jsonl_path,
        "csv": csv_path,
        "markoown": markoown_path,
        "summary": summary_path,
    }

