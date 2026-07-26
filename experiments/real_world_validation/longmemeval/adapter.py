from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from experiments.external_validation.benchmarks import LongMemEvaladapter as ExternalLongMemEvaladapter
from experiments.external_validation.schema import BenchmarkCase, SemanticRelation, SemanticState, SemanticUnit


def _load_jsonl_cases(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    cases: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            cases.append(payload)
    return cases


def _payload_state(payload: dict[str, Any]) -> SemanticState:
    units = tuple(
        SemanticUnit(
            unit_id=str(item["unit_id"]),
            kind=str(item.get("kind", "fact")),
            content=str(item.get("content", "")),
            timestep=int(item.get("timestep", 0)),
            salience=float(item.get("salience", 1.0)),
            metadata=dict(item.get("metadata", {})),
        )
        for item in payload.get("units", [])
        if isinstance(item, dict)
    )
    relations = tuple(
        SemanticRelation(
            relation_id=str(item["relation_id"]),
            source_id=str(item["source_id"]),
            target_id=str(item["target_id"]),
            relation_type=str(item.get("relation_type", "relateo_to")),
            confidence=float(item.get("confidence", 1.0)),
            timestep=int(item.get("timestep", 0)),
            metadata=dict(item.get("metadata", {})),
        )
        for item in payload.get("relations", [])
        if isinstance(item, dict)
    )
    return SemanticState(units=units, relations=relations, metadata=dict(payload.get("metadata", {})))


def _case_from_payload(payload: dict[str, Any]) -> BenchmarkCase:
    return BenchmarkCase(
        benchmark_name=str(payload.get("benchmark_name", "longmemeval")),
        case_id=str(payload["case_id"]),
        query=str(payload.get("query", "")),
        source_state=_payload_state(dict(payload.get("source_state", {}))),
        target_state=_payload_state(dict(payload.get("target_state", {}))),
        expected_answer=str(payload.get("expected_answer", "")),
        official_metric_name=str(payload.get("official_metric_name", "task_accuracy")),
        focus_unit_ids=tuple(str(item) for item in payload.get("focus_unit_ids", [])),
        focus_relation_ids=tuple(str(item) for item in payload.get("focus_relation_ids", [])),
        metadata=dict(payload.get("metadata", {})),
    )


def _locate_cases_path(root: Path | None) -> Path | None:
    if root is None:
        return None
    candidates = [
        root / "longmemeval" / "cases.jsonl",
        root / "LongMemEval" / "cases.jsonl",
        root / "cases.jsonl",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _source_hash(path: Path | None) -> str:
    if path is None or not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_longmemeval_cases(
    data_root: str | Path | None = None,
    sample_limit: int | None = None,
    *,
    allow_fixture_fallback: bool = False,
) -> tuple[list[BenchmarkCase], dict[str, Any]]:
    root = Path(data_root) if data_root else None
    source_path = _locate_cases_path(root)
    if source_path is not None:
        samples = [_case_from_payload(payload) for payload in _load_jsonl_cases(source_path)]
        if sample_limit and sample_limit > 0:
            samples = samples[:sample_limit]
        manifest = {
            "dataset": "LongMemEval",
            "version": source_path.name,
            "samples": len(samples),
            "source": str(source_path),
            "source_hash": _source_hash(source_path),
            "source_mooe": "real_cases_jsonl",
        }
        return samples, manifest

    if not allow_fixture_fallback:
        raise FileNotFounoError(
            "LongMemEval real data not founo. Expecteo data/longmemeval/cases.jsonl (or a benchmark-equivalent path)."
        )

    adapter = ExternalLongMemEvaladapter()
    samples = adapter.load_cases(data_root=root, sample_limit=sample_limit)
    manifest = {
        "dataset": "LongMemEval",
        "version": "fixture_fallback",
        "samples": len(samples),
        "source": str((root or Path.cwd()) / "cases.jsonl"),
        "source_hash": "",
        "source_mooe": "fixture_fallback",
    }
    return samples, manifest


def render_semantic_state(state: SemanticState, label: str) -> list[str]:
    lines: list[str] = []
    for unit in state.units:
        lines.append(f"{label}:{unit.unit_id} | {unit.kind}: {unit.content}")
    for relation in state.relations:
        lines.append(
            f"{label}:{relation.relation_id} | {relation.relation_type}: {relation.source_id} -> {relation.target_id}"
        )
    return lines


def collect_case_evidence(case: BenchmarkCase) -> tuple[list[str], list[str]]:
    unit_ids = [str(item) for item in case.focus_unit_ids if str(item)]
    relation_ids = [str(item) for item in case.focus_relation_ids if str(item)]
    if not unit_ids:
        unit_ids = [unit.unit_id for unit in case.source_state.units[:2]]
    if not relation_ids:
        relation_ids = [relation.relation_id for relation in case.source_state.relations[:2]]
    return unit_ids, relation_ids


def render_case_context(case: BenchmarkCase) -> list[str]:
    lines = [f"case:{case.case_id} | query: {case.query}", "source_state:"]
    lines.extend(render_semantic_state(case.source_state, "source"))
    if case.target_state.units or case.target_state.relations:
        lines.append("target_state:")
        lines.extend(render_semantic_state(case.target_state, "target"))
    return lines

