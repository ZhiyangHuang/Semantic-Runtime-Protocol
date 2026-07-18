import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass
class SemanticObject:
    object_type: str
    value: str
    confidence: float
    evidence_pointer: str
    metadata: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict:
        return {
            "type": self.object_type,
            "value": self.value,
            "confidence": round(self.confidence, 4),
            "evidence_pointer": self.evidence_pointer,
            "metadata": dict(self.metadata),
        }

    def stable_id(self) -> str:
        return stable_semantic_object_id(self.object_type, self.value)


@dataclass
class TypedSemanticRepresentation:
    objects: List[SemanticObject] = field(default_factory=list)

    def by_type(self, object_type: str) -> List[SemanticObject]:
        return [item for item in self.objects if item.object_type == object_type]

    def as_dict(self) -> Dict:
        return {
            "objects": [item.as_dict() for item in self.objects],
        }


def typed_representation_from_dict(data: Dict | None) -> TypedSemanticRepresentation:
    objects: List[SemanticObject] = []
    for item in (data or {}).get("objects", []):
        if not isinstance(item, dict):
            continue
        objects.append(
            SemanticObject(
                object_type=str(item.get("type", "fact")),
                value=str(item.get("value", "")),
                confidence=float(item.get("confidence", 0.0) or 0.0),
                evidence_pointer=str(item.get("evidence_pointer", "")),
                metadata={str(k): str(v) for k, v in dict(item.get("metadata", {})).items()},
            )
        )
    return TypedSemanticRepresentation(objects=objects)


_ABBREVIATIONS = {
    "nyc": "new york city",
    "prof.": "professor",
    "prof": "professor",
    "cs": "computer science",
}

_MONTHS = {
    "jan": "1",
    "january": "1",
    "feb": "2",
    "february": "2",
    "mar": "3",
    "march": "3",
    "apr": "4",
    "april": "4",
    "may": "5",
    "jun": "6",
    "june": "6",
    "jul": "7",
    "july": "7",
    "aug": "8",
    "august": "8",
    "sep": "9",
    "sept": "9",
    "september": "9",
    "oct": "10",
    "october": "10",
    "nov": "11",
    "november": "11",
    "dec": "12",
    "december": "12",
}


def _normalize_text(text: str) -> str:
    lowered = str(text).strip().lower()
    lowered = re.sub(r"[\u2018\u2019]", "'", lowered)
    lowered = re.sub(r"[\u201c\u201d]", '"', lowered)
    lowered = re.sub(r"[^\w\s/.-]+", " ", lowered)
    lowered = " ".join(lowered.split())
    return lowered


def canonicalize_semantic_value(value: str) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return ""
    if normalized in _ABBREVIATIONS:
        return _ABBREVIATIONS[normalized]
    month_year = re.fullmatch(r"([a-z]+)\s+(\d{4})", normalized)
    if month_year and month_year.group(1) in _MONTHS:
        return f"{_MONTHS[month_year.group(1)]}/{month_year.group(2)}"
    normalized = re.sub(r"\b(\d{1,2})/(\d{4})\b", lambda m: f"{int(m.group(1))}/{m.group(2)}", normalized)
    normalized = re.sub(r"\b(0?\d)/(20\d{2})\b", lambda m: f"{int(m.group(1))}/{m.group(2)}", normalized)
    return normalized


def stable_semantic_object_id(object_type: str, value: str) -> str:
    canonical = canonicalize_semantic_value(value)
    digest = hashlib.sha1(f"{object_type}:{canonical}".encode("utf-8")).hexdigest()[:8]
    return f"{object_type}:{digest}"


def _split_sentences(text: str) -> List[str]:
    normalized = " ".join(str(text).strip().split())
    if not normalized:
        return []
    sentences = []
    for chunk in normalized.replace("?", ".").replace("!", ".").split("."):
        cleaned = chunk.strip(" ,;")
        if cleaned:
            sentences.append(cleaned)
    return sentences


def parse_semantic_state(
    memory: str,
    constraints: Optional[Iterable[str]] = None,
    anchor_memory: str = "",
) -> TypedSemanticRepresentation:
    objects: List[SemanticObject] = []

    for idx, sentence in enumerate(_split_sentences(memory), start=1):
        objects.append(
            SemanticObject(
                object_type="fact",
                value=sentence,
                confidence=0.65,
                evidence_pointer=f"memory:{idx}",
            )
        )

    for idx, constraint in enumerate(constraints or [], start=1):
        normalized = _normalize_text(constraint)
        if normalized:
            objects.append(
                SemanticObject(
                    object_type="constraint",
                    value=normalized,
                    confidence=1.0,
                    evidence_pointer=f"constraint:{idx}",
                )
            )

    for idx, sentence in enumerate(_split_sentences(anchor_memory), start=1):
        objects.append(
            SemanticObject(
                object_type="anchor",
                value=sentence,
                confidence=0.8,
                evidence_pointer=f"anchor:{idx}",
            )
        )

    return TypedSemanticRepresentation(objects=objects)
