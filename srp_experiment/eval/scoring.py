import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence

from srp.semantic_parser import parse_semantic_state
from srp.validation_targets import SemanticContractGraph


@dataclass
class SemanticContractObject:
    surface: str
    normalized: str
    tokens: List[str] = field(default_factory=list)


@dataclass
class SemanticContractClause:
    variants: List[SemanticContractObject] = field(default_factory=list)


@dataclass
class NormalizedSemanticObjects:
    objects: List[SemanticContractObject] = field(default_factory=list)
    aliases: Dict[str, List[str]] = field(default_factory=dict)


def _simple_stem(token: str) -> str:
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 4 and token.endswith("es"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token


def _normalize_text(value: str) -> str:
    lowered = str(value).strip().lower().replace("-", " ")
    lowered = re.sub(r"[^a-z0-9\s]", " ", lowered)
    return " ".join(lowered.split())


def _canonical_alias_tokens(tokens: List[str]) -> List[str]:
    canonical = []
    alias_map = {
        "prefers": "prefer",
        "preferred": "prefer",
        "preferences": "prefer",
        "architectures": "architecture",
        "systems": "system",
        "constraints": "constraint",
        "concepts": "concept",
        "tokens": "token",
    }
    for token in tokens:
        mapped = alias_map.get(token, token)
        canonical.append(_simple_stem(mapped))
    return canonical


def _tokenize(value: str) -> List[str]:
    normalized = _normalize_text(value)
    if not normalized:
        return []
    raw_tokens = [token for token in normalized.split() if token]
    return _canonical_alias_tokens(raw_tokens)


def _build_contract_object(value: str) -> SemanticContractObject:
    return SemanticContractObject(
        surface=str(value).strip(),
        normalized=_normalize_text(value),
        tokens=_tokenize(value),
    )


def _normalize_contract(expectations: Iterable | SemanticContractGraph) -> List[SemanticContractClause]:
    clauses: List[SemanticContractClause] = []
    if isinstance(expectations, SemanticContractGraph):
        for node in expectations.clause_nodes():
            variants = [
                _build_contract_object(variant.surface)
                for variant in node.variants
                if variant.surface.strip()
            ]
            if variants:
                clauses.append(SemanticContractClause(variants=variants))
        return clauses
    for item in expectations:
        if isinstance(item, str):
            variants = [_build_contract_object(item)]
        else:
            try:
                raw_values = [str(value).strip() for value in item if str(value).strip()]
            except TypeError:
                raw_values = [str(item).strip()]
            variants = [_build_contract_object(value) for value in raw_values if value]
        variants = [variant for variant in variants if variant.normalized]
        if variants:
            clauses.append(SemanticContractClause(variants=variants))
    return clauses


def _extract_candidate_objects(text: str) -> List[SemanticContractObject]:
    typed_state = parse_semantic_state(text)
    objects = [
        _build_contract_object(item.value)
        for item in typed_state.objects
        if item.value.strip()
    ]
    whole_text = _build_contract_object(text)
    if whole_text.normalized:
        objects.append(whole_text)
    return objects


def normalize_semantic_objects(text: str, semantic_contract: Iterable | SemanticContractGraph) -> tuple[List[SemanticContractClause], NormalizedSemanticObjects]:
    clauses = _normalize_contract(semantic_contract)
    candidates = _extract_candidate_objects(text)
    aliases: Dict[str, List[str]] = {}
    for candidate in candidates:
        aliases[candidate.surface] = list(candidate.tokens)
    return clauses, NormalizedSemanticObjects(objects=candidates, aliases=aliases)


def _similarity(contract_object: SemanticContractObject, candidate_object: SemanticContractObject) -> float:
    if not contract_object.normalized or not candidate_object.normalized:
        return 0.0
    if contract_object.normalized == candidate_object.normalized:
        return 1.0
    if contract_object.normalized in candidate_object.normalized or candidate_object.normalized in contract_object.normalized:
        return 0.9

    contract_tokens = set(contract_object.tokens)
    candidate_tokens = set(candidate_object.tokens)
    if not contract_tokens or not candidate_tokens:
        return 0.0

    overlap = len(contract_tokens & candidate_tokens)
    if overlap == 0:
        return 0.0

    precision = overlap / len(contract_tokens)
    recall = overlap / len(candidate_tokens)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0

    contract_joined = " ".join(contract_object.tokens)
    candidate_joined = " ".join(candidate_object.tokens)
    if contract_joined and (contract_joined in candidate_joined or candidate_joined in contract_joined):
        return max(0.92, f1)

    if precision == 1.0:
        return max(0.85, f1)
    if recall == 1.0 and len(candidate_tokens) <= len(contract_tokens) + 1:
        return max(0.8, f1)
    return f1


def evaluate_contract(
    clauses: List[SemanticContractClause],
    normalized_candidates: NormalizedSemanticObjects,
) -> float:
    if not clauses:
        return 1.0

    satisfied = 0.0
    for clause in clauses:
        best_clause_score = 0.0
        for variant in clause.variants:
            for candidate in normalized_candidates.objects:
                similarity = _similarity(variant, candidate)
                if similarity > best_clause_score:
                    best_clause_score = similarity
        satisfied += best_clause_score
    return round(satisfied / len(clauses), 4)


def compute_contract_satisfaction(text: str, semantic_contract: Iterable | SemanticContractGraph) -> float:
    clauses, normalized_candidates = normalize_semantic_objects(text, semantic_contract)
    return evaluate_contract(clauses, normalized_candidates)


def compute_task_success(text: str, expected_keywords: Sequence | SemanticContractGraph) -> float:
    return compute_contract_satisfaction(text, expected_keywords)
