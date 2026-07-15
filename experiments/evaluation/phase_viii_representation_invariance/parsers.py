from __future__ import annotations

import re
from dataclasses import dataclass


_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}

RELATION_PHRASES: tuple[tuple[str, str], ...] = (
    ("is a member of", "member_of"),
    ("works on", "works_on"),
    ("belongs to", "belongs_to"),
    ("managed by", "managed_by"),
    ("owned by", "owned_by"),
    ("part of", "part_of"),
    ("caused by", "caused_by"),
    ("depends on", "depends_on"),
    ("modifies", "modifies"),
    ("reviews", "reviews"),
    ("documents", "documents"),
    ("mentions", "mentions"),
    ("conflicts with", "conflicts_with"),
    ("runs", "runs"),
    ("funds", "funds"),
    ("approves", "approves"),
    ("blocks", "blocks"),
    ("requires", "requires"),
    ("satisfies", "satisfies"),
)

RELATION_TOKENS = tuple(value for _, value in RELATION_PHRASES)


@dataclass(frozen=True)
class ParsedText:
    parser_name: str
    text: str


def tokenize(text: str) -> tuple[str, ...]:
    return tuple(token.lower() for token in _TOKEN_RE.findall(text or ""))


def _normalize_whitespace(text: str) -> str:
    return " ".join((text or "").split())


def _canonicalize_relations(text: str) -> str:
    normalized = text.lower()
    for phrase, canonical in RELATION_PHRASES:
        normalized = re.sub(rf"\b{re.escape(phrase)}\b", canonical, normalized)
    return _normalize_whitespace(normalized)


def _extract_triplet(text: str) -> tuple[str, str, str] | None:
    tokens = tokenize(_canonicalize_relations(text))
    for index, token in enumerate(tokens):
        if token in RELATION_TOKENS:
            left = " ".join(tokens[:index]).strip()
            right = " ".join(tokens[index + 1 :]).strip()
            if left and right:
                return left, token, right
    return None


def _rule_parser(text: str, node_id: str = "") -> str:
    return _normalize_whitespace(_canonicalize_relations(text))


def _hybrid_parser(text: str, node_id: str = "") -> str:
    normalized = _canonicalize_relations(text)
    tokens = [token for token in tokenize(normalized) if token not in STOPWORDS]
    triplet = _extract_triplet(normalized)
    if triplet:
        left, relation, right = triplet
        return _normalize_whitespace(
            f"entity {node_id or left} relation {relation} subject {left} object {right} tokens {' '.join(tokens)}"
        )
    return _normalize_whitespace(f"entity {node_id} tokens {' '.join(tokens)}")


def _llm_parser(text: str, node_id: str = "") -> str:
    normalized = _canonicalize_relations(text)
    triplet = _extract_triplet(normalized)
    if triplet:
        left, relation, right = triplet
        return _normalize_whitespace(
            f"entity: {node_id or left}; subject: {left}; relation: {relation}; object: {right}"
        )
    tokens = tokenize(normalized)
    if not tokens:
        return f"entity: {node_id}; content: "
    return _normalize_whitespace(
        f"entity: {node_id}; content: {normalized}; focus: {tokens[0]}; tail: {tokens[-1]}"
    )


PARSER_FUNCTIONS = {
    "rule_parser": _rule_parser,
    "hybrid_parser": _hybrid_parser,
    "llm_parser": _llm_parser,
}


def parse_text(text: str, parser_name: str, node_id: str = "") -> str:
    parser = PARSER_FUNCTIONS.get(parser_name, _rule_parser)
    return parser(text, node_id=node_id)
