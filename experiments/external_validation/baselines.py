from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import re
from typing import Any, Protocol

from srp_experiment.srp.encoder import HashingSemanticEncoder, cosine_similarity

from .schema import BenchmarkCase, MemoryResponse, SemanticRelation, SemanticState, SemanticUnit


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _token_set(text: str) -> set[str]:
    return {token for token in _normalize_text(text).replace("/", " ").replace("-", " ").split() if token}


def _jaccard(left: str, right: str) -> float:
    left_tokens = _token_set(left)
    right_tokens = _token_set(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _normalize_answer(text: str) -> str:
    text = str(text).strip()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" .,:;!?\"'`")
    return text


def _format_date(date_value: datetime) -> str:
    return f"{date_value.day} {date_value.strftime('%B %Y')}"


def _parse_session_datetime(raw: str | None) -> datetime | None:
    if not raw:
        return None
    value = str(raw).strip()
    formats = [
        "%I:%M %p on %d %B, %Y",
        "%I:%M %p on %d %B %Y",
        "%I:%M %p on %d %b, %Y",
        "%I:%M %p on %d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    value = re.sub(r"\s+", " ", value)
    value = value.replace(",", "")
    for fmt in ("%I:%M %p on %d %B %Y", "%I:%M %p on %d %b %Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _resolve_relative_temporal_phrase(text: str, session_dt: datetime | None) -> str | None:
    lowered = _normalize_text(text)
    if session_dt is None:
        return None

    if "yesterday" in lowered:
        return _format_date(session_dt - timedelta(days=1))
    if "today" in lowered:
        return _format_date(session_dt)
    if "tomorrow" in lowered:
        return _format_date(session_dt + timedelta(days=1))
    if "last week" in lowered:
        return f"the week before {_format_date(session_dt)}"
    if "next week" in lowered:
        return f"the week after {_format_date(session_dt)}"
    if "last month" in lowered:
        previous = session_dt - timedelta(days=30)
        return f"{previous.strftime('%B %Y')}"
    if "next month" in lowered:
        future = session_dt + timedelta(days=30)
        return f"{future.strftime('%B %Y')}"

    before_match = re.search(
        r"the\s+([a-z]+)\s+before\s+(\d{1,2}\s+[A-Z][a-z]+\s+\d{4})",
        text,
        flags=re.IGNORECASE,
    )
    if before_match:
        weekday = before_match.group(1).lower()
        date_text = before_match.group(2)
        try:
            reference = datetime.strptime(date_text, "%d %B %Y")
        except ValueError:
            try:
                reference = datetime.strptime(date_text, "%d %b %Y")
            except ValueError:
                reference = None
        if reference is not None:
            weekday_map = {
                "monday": 0,
                "tuesday": 1,
                "wednesday": 2,
                "thursday": 3,
                "friday": 4,
                "saturday": 5,
                "sunday": 6,
            }
            desired = weekday_map.get(weekday)
            if desired is not None:
                current = reference - timedelta(days=1)
                while current.weekday() != desired:
                    current -= timedelta(days=1)
                return _format_date(current)
    return None


def _extract_temporal_answer(question: str, text: str, session_dt: datetime | None) -> str | None:
    candidates = [
        r"\b\d{1,2}\s+[A-Z][a-z]+\s+\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
        r"\b\d{4}\b",
    ]
    for pattern in candidates:
        match = re.search(pattern, text)
        if match:
            return _normalize_answer(match.group(0))
    relative = _resolve_relative_temporal_phrase(text, session_dt)
    if relative:
        return _normalize_answer(relative)
    if "when" in _normalize_text(question):
        return None
    return None


def _extract_yes_no_answer(text: str) -> str | None:
    lowered = _normalize_text(text)
    if any(token in lowered for token in (" no ", "n't", "not ", "never", "no longer", "without ")):
        return "no"
    if any(token in lowered for token in (" yes ", " can ", " will ", " is ", " are ", " was ", " were ", " do ", " does ", " did ")):
        return "yes"
    return None


def _extract_person_answer(text: str) -> str | None:
    patterns = [
        r"\bmeet(?:ing|s|ing with| with| up with)?\s+(?:the\s+|a\s+|an\s+)?([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"\bwith\s+(?:the\s+|a\s+|an\s+)?([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"\bnamed\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"\bcalled\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"\bfriend\s+named\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _normalize_answer(match.group(1))

    capitalized = re.findall(r"(?:^|[^A-Za-z])([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)", text)
    filtered = [item for item in capitalized if item and item.lower() not in {"i", "the", "a", "an", "it", "we", "you"}]
    if filtered:
        return _normalize_answer(filtered[-1])
    return None


def _extract_location_answer(text: str) -> str | None:
    patterns = [
        r"\b(?:in|at|to|from|near|on|inside|outside|around)\s+(?:the\s+|a\s+|an\s+)?([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"\bmove(?:d)?\s+from\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
        r"\bgo(?:e|es|ing)?\s+to\s+([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*)*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _normalize_answer(match.group(1))
    return None


def _extract_quantity_answer(text: str) -> str | None:
    patterns = [
        r"\b\d+\s+(?:years?|months?|weeks?|days?|hours?|minutes?|times?|kids?|children|dogs|cats|books|pages|sessions?)\b",
        r"\b\d+\b",
        r"\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _normalize_answer(match.group(0))
    return None


def _extract_what_answer(question: str, text: str) -> str | None:
    lowered_question = _normalize_text(question)
    lowered_text = _normalize_text(text)

    if "prefer" in lowered_question:
        match = re.search(r"prefer(?:s|red)?\s+(?:to\s+)?(?:the\s+)?(.+?)(?:[.;!?]|$)", text, flags=re.IGNORECASE)
        if match:
            return _normalize_answer(match.group(1))
    if "identity" in lowered_question:
        match = re.search(r"(?:am|is|was|are|were)\s+(?:a|an)?\s*([A-Za-z][A-Za-z\s-]+?)(?:[.;!?]|$)", text, flags=re.IGNORECASE)
        if match:
            return _normalize_answer(match.group(1))
    if any(keyword in lowered_question for keyword in ("relationship status", "status")):
        match = re.search(r"\b(?:single|married|divorced|engaged|dating|relationship)\b", lowered_text)
        if match:
            return _normalize_answer(match.group(0))
    if any(keyword in lowered_question for keyword in ("career", "fields", "options", "pursue")):
        match = re.search(r"(?:career options|pursue|fields?|options?)\s+(?:in\s+|for\s+|of\s+|to\s+)?(.+?)(?:[.;!?]|$)", text, flags=re.IGNORECASE)
        if match:
            candidate = _normalize_answer(match.group(1))
            if candidate:
                return candidate
    if "research" in lowered_question:
        match = re.search(r"research(?:ed|es|ing)?\s+(?:about\s+|on\s+)?(.+?)(?:[.;!?]|$)", text, flags=re.IGNORECASE)
        if match:
            candidate = _normalize_answer(match.group(1))
            if candidate:
                return candidate

    copula_patterns = [
        r"\b(?:is|was|are|were|be|been)\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z0-9,\s/-]+?)(?:[.;!?]|$)",
        r"\b(?:become|became|becoming)\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z0-9,\s/-]+?)(?:[.;!?]|$)",
        r"\b(?:have|has|had)\s+(?:a|an|the)?\s*([A-Za-z][A-Za-z0-9,\s/-]+?)(?:[.;!?]|$)",
    ]
    for pattern in copula_patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            candidate = _normalize_answer(match.group(1))
            if candidate and len(candidate.split()) <= 8:
                return candidate

    if any(keyword in lowered_question for keyword in ("what", "which")):
        tokens = _token_set(text)
        question_tokens = _token_set(question)
        overlap = [token for token in tokens if token in question_tokens]
        if overlap:
            # Prefer a concise phrase around overlapping terms.
            for token in overlap:
                match = re.search(rf".{{0,40}}\\b{re.escape(token)}\\b.{{0,40}}", text, flags=re.IGNORECASE)
                if match:
                    return _normalize_answer(match.group(0))
    return None


def _extract_answer_from_unit(question: str, unit: SemanticUnit) -> str | None:
    text = unit.content
    session_dt = _parse_session_datetime(str(unit.metadata.get("session_datetime", "")))
    normalized_question = _normalize_text(question)

    if normalized_question.startswith("when") or normalized_question.startswith("according") and "when" in normalized_question:
        answer = _extract_temporal_answer(question, text, session_dt)
        if answer:
            return answer
    if normalized_question.startswith("who") or normalized_question.startswith("whose") or " who " in f" {normalized_question} ":
        answer = _extract_person_answer(text)
        if answer:
            return answer
    if normalized_question.startswith("where") or " where " in f" {normalized_question} ":
        answer = _extract_location_answer(text)
        if answer:
            return answer
    if normalized_question.startswith("how long") or normalized_question.startswith("how many") or normalized_question.startswith("how much"):
        answer = _extract_quantity_answer(text)
        if answer:
            return answer
    if normalized_question.startswith("is") or normalized_question.startswith("are") or normalized_question.startswith("was") or normalized_question.startswith("were") or normalized_question.startswith("do") or normalized_question.startswith("does") or normalized_question.startswith("did") or normalized_question.startswith("would") or normalized_question.startswith("could") or normalized_question.startswith("should"):
        answer = _extract_yes_no_answer(text)
        if answer:
            return answer
    answer = _extract_what_answer(question, text)
    if answer:
        return answer
    return None


class MemorySystem(Protocol):
    name: str

    def ingest(self, case: BenchmarkCase) -> None:
        raise NotImplementedError

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        raise NotImplementedError

    def update(self, feedback: dict[str, Any]) -> None:
        raise NotImplementedError

    def inspect_state(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass
class _MemoryBase:
    name: str
    seed: int = 0
    _case: BenchmarkCase | None = None
    _encoder: HashingSemanticEncoder = field(default_factory=HashingSemanticEncoder)

    def ingest(self, case: BenchmarkCase) -> None:
        self._case = case

    def update(self, feedback: dict[str, Any]) -> None:  # pragma: no cover - placeholder for the contract
        _ = feedback

    def inspect_state(self) -> dict[str, Any]:
        if self._case is None:
            return {"name": self.name, "state": None}
        return {"name": self.name, "state": self._case.source_state.as_dict()}

    def _source(self) -> BenchmarkCase:
        if self._case is None:
            raise RuntimeError(f"{self.name} has not ingested a case")
        return self._case

    def _encode_similarity(self, query: str, unit: SemanticUnit) -> float:
        query_vec = self._encoder.encode_query(query)
        unit_vec = self._encoder.encode_passage(unit.content)
        return cosine_similarity(query_vec, unit_vec)

    def _rank_units(self, query: str, units: tuple[SemanticUnit, ...]) -> list[SemanticUnit]:
        scored = []
        for index, unit in enumerate(units):
            score = self._encode_similarity(query, unit) + unit.salience * 0.25 - unit.timestep * 0.01
            score += (self.seed % 7) * 0.0001 * (index + 1)
            scored.append((score, unit))
        scored.sort(key=lambda item: (item[0], item[1].timestep, item[1].unit_id), reverse=True)
        return [item[1] for item in scored]

    def _neighbor_relations(self, selected_ids: set[str], relations: tuple[SemanticRelation, ...], depth: int = 1) -> tuple[SemanticRelation, ...]:
        if not selected_ids:
            return ()
        adjacency: dict[str, list[SemanticRelation]] = defaultdict(list)
        for relation in relations:
            adjacency[relation.source_id].append(relation)
            adjacency[relation.target_id].append(relation)

        visited_units = set(selected_ids)
        selected_relations: list[SemanticRelation] = []
        queue = deque((unit_id, 0) for unit_id in selected_ids)
        seen_relations: set[str] = set()

        while queue:
            unit_id, distance = queue.popleft()
            if distance >= depth:
                continue
            for relation in adjacency.get(unit_id, []):
                if relation.relation_id not in seen_relations:
                    selected_relations.append(relation)
                    seen_relations.add(relation.relation_id)
                other = relation.target_id if relation.source_id == unit_id else relation.source_id
                if other not in visited_units:
                    visited_units.add(other)
                    queue.append((other, distance + 1))
        return tuple(selected_relations)

    def _make_response(
        self,
        units: tuple[SemanticUnit, ...],
        relations: tuple[SemanticRelation, ...],
        query: str,
        notes: tuple[str, ...] = (),
        evidence_cost: float | None = None,
    ) -> MemoryResponse:
        recovered_state = SemanticState(
            units=units,
            relations=relations,
            metadata={"baseline": self.name, "query": query},
        )
        answer = self._answer_from_state(recovered_state, query)
        if evidence_cost is None:
            evidence_cost = round(len(units) * 0.18 + len(relations) * 0.12, 6)
        return MemoryResponse(
            recovered_state=recovered_state,
            predicted_answer=answer,
            retrieved_unit_ids=tuple(unit.unit_id for unit in units),
            retrieved_relation_ids=tuple(relation.relation_id for relation in relations),
            evidence_cost=evidence_cost,
            notes=notes,
        )

    def _answer_from_state(self, state: SemanticState, query: str) -> str:
        ranked_units = self._rank_units(query, state.units)
        if not ranked_units:
            return ""
        query_text = _normalize_text(query)
        for unit in ranked_units:
            candidate = _extract_answer_from_unit(query_text, unit)
            if candidate:
                return candidate

        # Fallback: return the most relevant concise snippet.
        top_unit = ranked_units[0]
        text = _normalize_answer(top_unit.content)
        if len(text) > 120:
            text = text[:117].rstrip() + "..."
        if text:
            return text
        return ""


@dataclass
class FullContextMemory(_MemoryBase):
    name: str = "full_context"

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        return self._make_response(case.source_state.units, case.source_state.relations, query, evidence_cost=float(len(case.source_state.units) + len(case.source_state.relations)))


@dataclass
class SlidingWindowMemory(_MemoryBase):
    name: str = "sliding_window"
    window_size: int = 2

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        units = tuple(sorted(case.source_state.units, key=lambda item: (item.timestep, item.unit_id)))[-self.window_size :]
        unit_ids = {unit.unit_id for unit in units}
        relations = tuple(relation for relation in case.source_state.relations if relation.source_id in unit_ids and relation.target_id in unit_ids)
        return self._make_response(units, relations, query, notes=("windowed",))


@dataclass
class SummarizationMemory(_MemoryBase):
    name: str = "summarization_memory"
    summary_size: int = 3

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        ranked = sorted(case.source_state.units, key=lambda unit: (unit.salience, unit.timestep), reverse=True)
        selected = tuple(sorted(ranked[: self.summary_size], key=lambda unit: (unit.timestep, unit.unit_id)))
        selected_ids = {unit.unit_id for unit in selected}
        relations = tuple(relation for relation in case.source_state.relations if relation.source_id in selected_ids and relation.target_id in selected_ids)
        return self._make_response(selected, relations, query, notes=("summary",))


@dataclass
class VectorRetrievalMemory(_MemoryBase):
    name: str = "vector_rag"
    top_k: int = 3

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        ranked = self._rank_units(query, case.source_state.units)
        selected = tuple(sorted(ranked[: self.top_k], key=lambda unit: (unit.timestep, unit.unit_id)))
        selected_ids = {unit.unit_id for unit in selected}
        relations = tuple(relation for relation in case.source_state.relations if relation.source_id in selected_ids and relation.target_id in selected_ids)
        notes = ("vector",)
        return self._make_response(selected, relations, query, notes=notes)


@dataclass
class GraphMemory(_MemoryBase):
    name: str = "graph_memory"
    top_k: int = 3
    relation_depth: int = 1

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        ranked = self._rank_units(query, case.source_state.units)
        anchors = tuple(sorted(ranked[: self.top_k], key=lambda unit: (unit.timestep, unit.unit_id)))
        anchor_ids = {unit.unit_id for unit in anchors}
        relations = self._neighbor_relations(anchor_ids, case.source_state.relations, depth=self.relation_depth)
        node_ids = set(anchor_ids)
        for relation in relations:
            node_ids.add(relation.source_id)
            node_ids.add(relation.target_id)
        selected = tuple(unit for unit in case.source_state.units if unit.unit_id in node_ids)
        return self._make_response(selected, relations, query, notes=("graph",))


@dataclass
class Mem0Memory(GraphMemory):
    name: str = "mem0"

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        response = super().retrieve(query, budget=budget)
        return MemoryResponse(
            recovered_state=response.recovered_state,
            predicted_answer=response.predicted_answer,
            retrieved_unit_ids=response.retrieved_unit_ids,
            retrieved_relation_ids=response.retrieved_relation_ids,
            evidence_cost=round(response.evidence_cost * 0.95, 6),
            notes=response.notes + ("consolidated",),
        )


@dataclass
class LettaMemory(SlidingWindowMemory):
    name: str = "letta"
    summary_size: int = 2

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        recent = tuple(sorted(case.source_state.units, key=lambda item: (item.timestep, item.unit_id)))[-self.window_size :]
        older = sorted(case.source_state.units, key=lambda item: (item.salience, item.timestep), reverse=True)[: self.summary_size]
        dedup: dict[str, SemanticUnit] = {unit.unit_id: unit for unit in recent}
        for unit in older:
            dedup[unit.unit_id] = unit
        selected = tuple(sorted(dedup.values(), key=lambda unit: (unit.timestep, unit.unit_id)))
        selected_ids = {unit.unit_id for unit in selected}
        relations = tuple(relation for relation in case.source_state.relations if relation.source_id in selected_ids and relation.target_id in selected_ids)
        return self._make_response(selected, relations, query, notes=("agent_memory",))


@dataclass
class GraphitiMemory(GraphMemory):
    name: str = "graphiti"
    temporal_bias: float = 0.15

    def _rank_units(self, query: str, units: tuple[SemanticUnit, ...]) -> list[SemanticUnit]:
        ranked = super()._rank_units(query, units)
        return sorted(ranked, key=lambda unit: (unit.timestep * self.temporal_bias, unit.salience), reverse=True)

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        response = super().retrieve(query, budget=budget)
        relations = tuple(sorted(response.recovered_state.relations, key=lambda rel: (rel.timestep, rel.confidence), reverse=True))
        selected_ids = set(response.retrieved_unit_ids)
        selected = tuple(unit for unit in response.recovered_state.units if unit.unit_id in selected_ids)
        return self._make_response(selected, relations, query, notes=response.notes + ("temporal_graph",), evidence_cost=round(response.evidence_cost * 1.08, 6))


@dataclass
class MemMachineMemory(GraphMemory):
    name: str = "memmachine"
    top_k: int = 4

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        ranked = self._rank_units(query, case.source_state.units)
        anchors = tuple(sorted(ranked[: self.top_k], key=lambda unit: (unit.timestep, unit.unit_id)))
        anchor_ids = {unit.unit_id for unit in anchors}
        relations = self._neighbor_relations(anchor_ids, case.source_state.relations, depth=max(1, self.relation_depth))
        node_ids = set(anchor_ids)
        for relation in relations:
            node_ids.add(relation.source_id)
            node_ids.add(relation.target_id)
        selected = tuple(unit for unit in case.source_state.units if unit.unit_id in node_ids)
        return self._make_response(selected, relations, query, notes=("episodic_memory",), evidence_cost=round(len(selected) * 0.16 + len(relations) * 0.18, 6))


@dataclass
class SrpMemory(GraphMemory):
    name: str = "srp"
    top_k: int = 3
    relation_depth: int = 2

    def retrieve(self, query: str, budget: float | None = None) -> MemoryResponse:
        case = self._source()
        ranked = self._rank_units(query, case.source_state.units)
        anchors = tuple(sorted(ranked[: self.top_k], key=lambda unit: (unit.timestep, unit.unit_id)))
        anchor_ids = {unit.unit_id for unit in anchors}
        raw_relations = self._neighbor_relations(anchor_ids, case.source_state.relations, depth=self.relation_depth)
        valid_relations = tuple(
            relation
            for relation in raw_relations
            if relation.confidence >= 0.5 and relation.source_id in {unit.unit_id for unit in case.source_state.units} and relation.target_id in {unit.unit_id for unit in case.source_state.units}
        )
        selected_ids = set(anchor_ids)
        for relation in valid_relations:
            selected_ids.add(relation.source_id)
            selected_ids.add(relation.target_id)
        selected = tuple(unit for unit in case.source_state.units if unit.unit_id in selected_ids)
        notes = ("srp_governed", "closure_validated")
        return self._make_response(selected, valid_relations, query, notes=notes, evidence_cost=round(len(selected) * 0.14 + len(valid_relations) * 0.10, 6))


def build_memory_system(name: str, seed: int = 0) -> MemorySystem:
    normalized = name.strip().lower()
    if normalized == "full_context":
        return FullContextMemory(seed=seed)
    if normalized == "sliding_window":
        return SlidingWindowMemory(seed=seed)
    if normalized == "summarization_memory":
        return SummarizationMemory(seed=seed)
    if normalized in {"vector_rag", "vector_memory"}:
        return VectorRetrievalMemory(seed=seed)
    if normalized in {"graph_memory", "graph", "structured_memory"}:
        return GraphMemory(seed=seed)
    if normalized == "mem0":
        return Mem0Memory(seed=seed)
    if normalized in {"letta", "memgpt"}:
        return LettaMemory(seed=seed)
    if normalized == "graphiti":
        return GraphitiMemory(seed=seed)
    if normalized == "memmachine":
        return MemMachineMemory(seed=seed)
    if normalized == "srp":
        return SrpMemory(seed=seed)
    raise ValueError(f"Unknown memory system: {name}")
