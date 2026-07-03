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


@dataclass
class TypedSemanticRepresentation:
    objects: List[SemanticObject] = field(default_factory=list)

    def by_type(self, object_type: str) -> List[SemanticObject]:
        return [item for item in self.objects if item.object_type == object_type]

    def as_dict(self) -> Dict:
        return {
            "objects": [item.as_dict() for item in self.objects],
        }


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().split())


def _split_sentences(text: str) -> List[str]:
    normalized = _normalize_text(text)
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
