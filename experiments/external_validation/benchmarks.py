from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .schema import BenchmarkCase, SemanticRelation, SemanticState, SemanticUnit


class BenchmarkAdapter(Protocol):
    name: str

    def load_cases(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[BenchmarkCase]:
        raise NotImplementedError


def _load_jsonl_cases(path: Path, benchmark_name: str) -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []
    if not path.exists():
        return cases
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw:
            continue
        payload = json.loads(raw)
        cases.append(_case_from_payload(payload, benchmark_name))
    return cases


def _load_json_cases(path: Path) -> list[dict]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if "data" in payload and isinstance(payload["data"], list):
            return [item for item in payload["data"] if isinstance(item, dict)]
        return [payload]
    return []


def _payload_state(payload: dict) -> SemanticState:
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
    )
    relations = tuple(
        SemanticRelation(
            relation_id=str(item["relation_id"]),
            source_id=str(item["source_id"]),
            target_id=str(item["target_id"]),
            relation_type=str(item.get("relation_type", "related_to")),
            confidence=float(item.get("confidence", 1.0)),
            timestep=int(item.get("timestep", 0)),
            metadata=dict(item.get("metadata", {})),
        )
        for item in payload.get("relations", [])
    )
    return SemanticState(units=units, relations=relations, metadata=dict(payload.get("metadata", {})))


def _case_from_payload(payload: dict, benchmark_name: str) -> BenchmarkCase:
    source_state = _payload_state(dict(payload.get("source_state", {})))
    target_state = _payload_state(dict(payload.get("target_state", {})))
    return BenchmarkCase(
        benchmark_name=benchmark_name,
        case_id=str(payload["case_id"]),
        query=str(payload.get("query", "")),
        source_state=source_state,
        target_state=target_state,
        expected_answer=str(payload.get("expected_answer", "")),
        official_metric_name=str(payload.get("official_metric_name", "task_accuracy")),
        focus_unit_ids=tuple(str(item) for item in payload.get("focus_unit_ids", [])),
        focus_relation_ids=tuple(str(item) for item in payload.get("focus_relation_ids", [])),
        metadata=dict(payload.get("metadata", {})),
    )


def _parse_session_index(session_key: str) -> int:
    try:
        return int(session_key.split("_", 1)[1].split("_", 1)[0])
    except Exception:
        return 0


def _sorted_session_keys(conversation: dict) -> list[str]:
    keys = [key for key in conversation.keys() if key.startswith("session_") and not key.endswith("_date_time")]
    return sorted(keys, key=_parse_session_index)


def _collect_dialog_turns(sample: dict) -> tuple[tuple[SemanticUnit, ...], dict[str, SemanticUnit], list[str]]:
    sample_id = str(sample.get("sample_id", "locomo_sample"))
    conversation = dict(sample.get("conversation", {}))
    units: list[SemanticUnit] = []
    turn_index: dict[str, SemanticUnit] = {}
    ordered_turn_ids: list[str] = []
    for session_key in _sorted_session_keys(conversation):
        session_turns = conversation.get(session_key, [])
        session_index = _parse_session_index(session_key)
        session_datetime = str(conversation.get(f"{session_key}_date_time", ""))
        for turn_order, turn in enumerate(session_turns):
            dia_id = str(turn.get("dia_id", f"{session_key}:{turn_order}"))
            unit_id = f"{sample_id}:{dia_id}"
            content = str(turn.get("text", ""))
            metadata = {
                "sample_id": sample_id,
                "session": session_index,
                "session_key": session_key,
                "session_datetime": session_datetime,
                "dia_id": dia_id,
                "speaker": str(turn.get("speaker", "")),
                "source_type": "dialog_turn",
            }
            unit = SemanticUnit(
                unit_id=unit_id,
                kind="dialog_turn",
                content=content,
                timestep=session_index * 100 + turn_order,
                salience=1.0,
                metadata=metadata,
            )
            units.append(unit)
            turn_index[dia_id] = unit
            ordered_turn_ids.append(dia_id)
    return tuple(units), turn_index, ordered_turn_ids


def _collect_context_units(sample: dict) -> tuple[SemanticUnit, ...]:
    sample_id = str(sample.get("sample_id", "locomo_sample"))
    units: list[SemanticUnit] = []
    conversation = dict(sample.get("conversation", {}))

    observation = dict(sample.get("observation", {}))
    for key, value in observation.items():
        if not key.endswith("_observation") or not isinstance(value, dict):
            continue
        session_index = _parse_session_index(key)
        session_datetime = str(conversation.get(f"session_{session_index}_date_time", ""))
        for speaker, snippets in value.items():
            if speaker == "date":
                continue
            if not isinstance(snippets, list):
                continue
            for snippet_index, snippet in enumerate(snippets):
                if not isinstance(snippet, list) or not snippet:
                    continue
                content = str(snippet[0])
                source_dia_id = str(snippet[1]) if len(snippet) > 1 else ""
                units.append(
                    SemanticUnit(
                        unit_id=f"{sample_id}:{key}:{speaker}:{snippet_index}",
                        kind="observation",
                        content=content,
                        timestep=session_index * 100 + snippet_index,
                        salience=0.7,
                        metadata={
                            "sample_id": sample_id,
                            "session": session_index,
                            "session_key": key,
                            "session_datetime": session_datetime,
                            "speaker": speaker,
                            "source_dia_id": source_dia_id,
                            "source_type": "observation",
                        },
                    )
                )

    session_summary = dict(sample.get("session_summary", {}))
    for key, value in session_summary.items():
        if not key.endswith("_summary") or not isinstance(value, str):
            continue
        session_index = _parse_session_index(key)
        session_datetime = str(conversation.get(f"session_{session_index}_date_time", ""))
        units.append(
            SemanticUnit(
                unit_id=f"{sample_id}:{key}",
                kind="session_summary",
                content=value,
                timestep=session_index * 100 + 90,
                salience=0.65,
                metadata={
                    "sample_id": sample_id,
                    "session": session_index,
                    "session_key": key,
                    "session_datetime": session_datetime,
                    "source_type": "session_summary",
                },
            )
        )

    event_summary = dict(sample.get("event_summary", {}))
    for key, speaker_map in event_summary.items():
        if not key.startswith("events_session_") or not isinstance(speaker_map, dict):
            continue
        session_index = _parse_session_index(key.replace("events_", ""))
        session_datetime = str(conversation.get(f"session_{session_index}_date_time", ""))
        for speaker, events in speaker_map.items():
            if not isinstance(events, list):
                continue
            for event_index, event in enumerate(events):
                units.append(
                    SemanticUnit(
                        unit_id=f"{sample_id}:{key}:{speaker}:{event_index}",
                        kind="event_summary",
                        content=str(event),
                        timestep=session_index * 100 + 95 + event_index,
                        salience=0.8,
                        metadata={
                            "sample_id": sample_id,
                            "session": session_index,
                            "session_key": key,
                            "session_datetime": session_datetime,
                            "speaker": speaker,
                            "source_type": "event_summary",
                        },
                    )
                )

    return tuple(units)


def _build_locomo_state(sample: dict, question_evidence: list[str] | None = None) -> tuple[SemanticState, SemanticState, tuple[str, ...], tuple[str, ...]]:
    sample_id = str(sample.get("sample_id", "locomo_sample"))
    dialog_units, turn_index, ordered_turn_ids = _collect_dialog_turns(sample)
    context_units = _collect_context_units(sample)
    all_units = tuple(sorted(((*dialog_units, *context_units)), key=lambda unit: (unit.timestep, unit.unit_id)))

    relations: list[SemanticRelation] = []
    for left_id, right_id in zip(ordered_turn_ids, ordered_turn_ids[1:]):
        left = turn_index.get(left_id)
        right = turn_index.get(right_id)
        if left is None or right is None:
            continue
        if left.metadata.get("session") != right.metadata.get("session"):
            continue
        relations.append(
            SemanticRelation(
                relation_id=f"{sample_id}:next:{left_id}:{right_id}",
                source_id=left.unit_id,
                target_id=right.unit_id,
                relation_type="next_turn",
                confidence=0.85,
                timestep=max(left.timestep, right.timestep),
                metadata={"sample_id": sample_id, "source_type": "turn_sequence"},
            )
        )

    source_state = SemanticState(
        units=all_units,
        relations=tuple(relations),
        metadata={"sample_id": sample_id, "source": "locomo"},
    )

    evidence_ids = [str(item) for item in (question_evidence or []) if str(item)]
    ordered_turn_units = [turn_index[turn_id] for turn_id in ordered_turn_ids if turn_id in turn_index]
    unit_positions = {unit.unit_id: index for index, unit in enumerate(ordered_turn_units)}
    evidence_window = 1
    target_ids: set[str] = set()
    for evidence_id in evidence_ids:
        unit = turn_index.get(evidence_id)
        if unit is None:
            continue
        position = unit_positions.get(unit.unit_id)
        if position is None:
            continue
        for offset in range(-evidence_window, evidence_window + 1):
            neighbor_index = position + offset
            if 0 <= neighbor_index < len(ordered_turn_units):
                neighbor = ordered_turn_units[neighbor_index]
                if neighbor.metadata.get("session") == unit.metadata.get("session"):
                    target_ids.add(neighbor.unit_id)

    target_units = [unit for unit in ordered_turn_units if unit.unit_id in target_ids]
    target_unit_ids = {unit.unit_id for unit in target_units}
    target_relations = [
        relation
        for relation in relations
        if relation.source_id in target_unit_ids and relation.target_id in target_unit_ids
    ]
    ordered_evidence_units = [turn_index[evidence_id] for evidence_id in evidence_ids if evidence_id in turn_index]
    ordered_evidence_units.sort(key=lambda unit: (unit.timestep, unit.unit_id))

    target_state = SemanticState(
        units=tuple(target_units),
        relations=tuple(target_relations),
        metadata={"sample_id": sample_id, "source": "locomo_evidence"},
    )
    return (
        source_state,
        target_state,
        tuple(unit.unit_id for unit in ordered_evidence_units),
        tuple(relation.relation_id for relation in target_relations),
    )


def _locomo_cases_from_sample(sample: dict) -> list[BenchmarkCase]:
    sample_id = str(sample.get("sample_id", "locomo_sample"))
    cases: list[BenchmarkCase] = []
    qa_items = sample.get("qa", [])
    for index, qa in enumerate(qa_items):
        if not isinstance(qa, dict):
            continue
        source_state, target_state, focus_unit_ids, focus_relation_ids = _build_locomo_state(sample, qa.get("evidence", []))
        cases.append(
            BenchmarkCase(
                benchmark_name="locomo",
                case_id=f"{sample_id}:qa:{index}",
                query=str(qa.get("question", "")),
                source_state=source_state,
                target_state=target_state,
                expected_answer=str(qa.get("answer", "")),
                official_metric_name="answer_accuracy",
                focus_unit_ids=focus_unit_ids,
                focus_relation_ids=focus_relation_ids,
                metadata={
                    "sample_id": sample_id,
                    "qa_index": index,
                    "category": qa.get("category"),
                    "evidence": list(qa.get("evidence", [])),
                    "source_type": "locomo_qa",
                },
            )
        )
    return cases


def _locomo_fixtures() -> list[BenchmarkCase]:
    return [
        BenchmarkCase(
            benchmark_name="locomo",
            case_id="session_pref_update",
            query="What tea does the user prefer now?",
            source_state=SemanticState(
                units=(
                    SemanticUnit("u0", "preference", "User initially prefers black tea.", timestep=0, salience=0.7),
                    SemanticUnit("u1", "event", "User visited a tea shop with Maya.", timestep=1, salience=0.4),
                    SemanticUnit("u2", "preference", "User now prefers green tea.", timestep=2, salience=1.0),
                    SemanticUnit("u3", "fact", "Maya recommended a matcha latte.", timestep=2, salience=0.6),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u2", "updated_to", confidence=0.9, timestep=2),
                    SemanticRelation("r1", "u1", "u3", "mentions", confidence=0.8, timestep=2),
                ),
                metadata={"official_metric_name": "answer_accuracy"},
            ),
            target_state=SemanticState(
                units=(
                    SemanticUnit("u2", "preference", "User now prefers green tea.", timestep=2, salience=1.0),
                    SemanticUnit("u3", "fact", "Maya recommended a matcha latte.", timestep=2, salience=0.6),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u2", "updated_to", confidence=0.9, timestep=2),
                ),
            ),
            expected_answer="green tea",
            focus_unit_ids=("u2", "u3"),
            focus_relation_ids=("r0",),
        ),
        BenchmarkCase(
            benchmark_name="locomo",
            case_id="travel_memory",
            query="Who was the user planning to meet after the trip?",
            source_state=SemanticState(
                units=(
                    SemanticUnit("u0", "event", "User planned a trip to Boston.", timestep=0, salience=0.5),
                    SemanticUnit("u1", "person", "User said they would meet Alex after the trip.", timestep=1, salience=0.9),
                    SemanticUnit("u2", "fact", "Alex works near the airport.", timestep=1, salience=0.6),
                    SemanticUnit("u3", "event", "User changed the return date to Friday.", timestep=2, salience=0.4),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "followed_by", confidence=0.8, timestep=1),
                    SemanticRelation("r1", "u1", "u2", "associated_with", confidence=0.7, timestep=1),
                ),
            ),
            target_state=SemanticState(
                units=(
                    SemanticUnit("u1", "person", "User said they would meet Alex after the trip.", timestep=1, salience=0.9),
                    SemanticUnit("u2", "fact", "Alex works near the airport.", timestep=1, salience=0.6),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "followed_by", confidence=0.8, timestep=1),
                    SemanticRelation("r1", "u1", "u2", "associated_with", confidence=0.7, timestep=1),
                ),
            ),
            expected_answer="Alex",
            focus_unit_ids=("u1", "u2"),
            focus_relation_ids=("r0", "r1"),
        ),
    ]


def _longmemeval_fixtures() -> list[BenchmarkCase]:
    return [
        BenchmarkCase(
            benchmark_name="longmemeval",
            case_id="preference_revision",
            query="What is the user's current workspace preference?",
            source_state=SemanticState(
                units=(
                    SemanticUnit("u0", "preference", "User prefers quiet rooms.", timestep=0, salience=0.7),
                    SemanticUnit("u1", "preference", "User now prefers standing desks.", timestep=1, salience=1.0),
                    SemanticUnit("u2", "fact", "User changed teams last month.", timestep=1, salience=0.5),
                    SemanticUnit("u3", "fact", "The new team sits near the window.", timestep=2, salience=0.4),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "updated_to", confidence=0.95, timestep=1),
                    SemanticRelation("r1", "u2", "u3", "contextualized_by", confidence=0.7, timestep=2),
                ),
            ),
            target_state=SemanticState(
                units=(
                    SemanticUnit("u1", "preference", "User now prefers standing desks.", timestep=1, salience=1.0),
                    SemanticUnit("u2", "fact", "User changed teams last month.", timestep=1, salience=0.5),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "updated_to", confidence=0.95, timestep=1),
                ),
            ),
            expected_answer="standing desks",
            focus_unit_ids=("u1", "u2"),
            focus_relation_ids=("r0",),
        ),
        BenchmarkCase(
            benchmark_name="longmemeval",
            case_id="contradiction_resolution",
            query="Is the user still available on Mondays?",
            source_state=SemanticState(
                units=(
                    SemanticUnit("u0", "fact", "User was available on Mondays in March.", timestep=0, salience=0.5),
                    SemanticUnit("u1", "fact", "User is no longer available on Mondays after April.", timestep=2, salience=1.0),
                    SemanticUnit("u2", "event", "Project meetings moved to Tuesday.", timestep=2, salience=0.4),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "replaced_by", confidence=0.9, timestep=2),
                    SemanticRelation("r1", "u1", "u2", "causes", confidence=0.6, timestep=2),
                ),
            ),
            target_state=SemanticState(
                units=(
                    SemanticUnit("u1", "fact", "User is no longer available on Mondays after April.", timestep=2, salience=1.0),
                    SemanticUnit("u2", "event", "Project meetings moved to Tuesday.", timestep=2, salience=0.4),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "replaced_by", confidence=0.9, timestep=2),
                ),
            ),
            expected_answer="no",
            focus_unit_ids=("u1", "u2"),
            focus_relation_ids=("r0",),
        ),
    ]


def _tgb2_fixtures() -> list[BenchmarkCase]:
    return [
        BenchmarkCase(
            benchmark_name="tgb2",
            case_id="temporal_relation_update",
            query="What relation currently connects PaperA and DatasetB?",
            source_state=SemanticState(
                units=(
                    SemanticUnit("u0", "node", "PaperA", timestep=0, salience=0.8),
                    SemanticUnit("u1", "node", "DatasetB", timestep=0, salience=0.8),
                    SemanticUnit("u2", "node", "BenchmarkC", timestep=1, salience=0.4),
                ),
                relations=(
                    SemanticRelation("r0", "u0", "u1", "uses", confidence=0.9, timestep=0),
                    SemanticRelation("r1", "u0", "u1", "replaces", confidence=0.7, timestep=1),
                    SemanticRelation("r2", "u1", "u2", "related_to", confidence=0.5, timestep=1),
                ),
            ),
            target_state=SemanticState(
                units=(
                    SemanticUnit("u0", "node", "PaperA", timestep=0, salience=0.8),
                    SemanticUnit("u1", "node", "DatasetB", timestep=0, salience=0.8),
                ),
                relations=(
                    SemanticRelation("r1", "u0", "u1", "replaces", confidence=0.7, timestep=1),
                ),
            ),
            expected_answer="replaces",
            focus_unit_ids=("u0", "u1"),
            focus_relation_ids=("r1",),
        ),
        BenchmarkCase(
            benchmark_name="tgb2",
            case_id="temporal_neighbor_stability",
            query="Which node is still connected to BenchmarkC?",
            source_state=SemanticState(
                units=(
                    SemanticUnit("u0", "node", "PaperA", timestep=0, salience=0.6),
                    SemanticUnit("u1", "node", "DatasetB", timestep=0, salience=0.6),
                    SemanticUnit("u2", "node", "BenchmarkC", timestep=1, salience=1.0),
                    SemanticUnit("u3", "node", "DatasetD", timestep=2, salience=0.5),
                ),
                relations=(
                    SemanticRelation("r0", "u2", "u0", "linked_to", confidence=0.8, timestep=1),
                    SemanticRelation("r1", "u2", "u3", "linked_to", confidence=0.9, timestep=2),
                    SemanticRelation("r2", "u2", "u1", "linked_to", confidence=0.4, timestep=0),
                ),
            ),
            target_state=SemanticState(
                units=(
                    SemanticUnit("u2", "node", "BenchmarkC", timestep=1, salience=1.0),
                    SemanticUnit("u3", "node", "DatasetD", timestep=2, salience=0.5),
                ),
                relations=(
                    SemanticRelation("r1", "u2", "u3", "linked_to", confidence=0.9, timestep=2),
                ),
            ),
            expected_answer="DatasetD",
            focus_unit_ids=("u2", "u3"),
            focus_relation_ids=("r1",),
        ),
    ]


@dataclass(frozen=True)
class LoCoMoAdapter:
    name: str = "locomo"

    def load_cases(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[BenchmarkCase]:
        root = Path(data_root) if data_root else None
        if root is not None:
            candidates = [
                root / "locomo10.json",
                root / "locomo" / "locomo10.json",
                root / "LoCoMo" / "locomo10.json",
                root / "cases.json",
                root / "locomo" / "cases.jsonl",
                root / "LoCoMo" / "cases.jsonl",
                root / "cases.jsonl",
            ]
            for candidate in candidates:
                if candidate.suffix == ".json":
                    samples = _load_json_cases(candidate)
                    if samples:
                        if sample_limit and sample_limit > 0:
                            samples = samples[:sample_limit]
                        cases: list[BenchmarkCase] = []
                        for sample in samples:
                            cases.extend(_locomo_cases_from_sample(sample))
                        if cases:
                            return cases
                cases = _load_jsonl_cases(candidate, self.name)
                if cases:
                    return cases
        return _locomo_fixtures()


@dataclass(frozen=True)
class LongMemEvalAdapter:
    name: str = "longmemeval"

    def load_cases(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[BenchmarkCase]:
        root = Path(data_root) if data_root else None
        if root is not None:
            candidates = [root / "longmemeval" / "cases.jsonl", root / "LongMemEval" / "cases.jsonl", root / "cases.jsonl"]
            for candidate in candidates:
                cases = _load_jsonl_cases(candidate, self.name)
                if cases:
                    return cases if not sample_limit or sample_limit <= 0 else cases[:sample_limit]
        return _longmemeval_fixtures()


@dataclass(frozen=True)
class TGB2Adapter:
    name: str = "tgb2"

    def load_cases(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[BenchmarkCase]:
        root = Path(data_root) if data_root else None
        if root is not None:
            candidates = [root / "tgb2" / "cases.jsonl", root / "TGB2" / "cases.jsonl", root / "cases.jsonl"]
            for candidate in candidates:
                cases = _load_jsonl_cases(candidate, self.name)
                if cases:
                    return cases if not sample_limit or sample_limit <= 0 else cases[:sample_limit]
        return _tgb2_fixtures()


def build_benchmark_adapter(name: str) -> BenchmarkAdapter:
    normalized = name.strip().lower()
    if normalized in {"locomo", "lo-como", "long_context_memory"}:
        return LoCoMoAdapter()
    if normalized in {"longmemeval", "long-mem-eval", "long_mem_eval"}:
        return LongMemEvalAdapter()
    if normalized in {"tgb2", "tgb-2", "tgb_2", "tgb 2.0"}:
        return TGB2Adapter()
    raise ValueError(f"Unknown benchmark adapter: {name}")
