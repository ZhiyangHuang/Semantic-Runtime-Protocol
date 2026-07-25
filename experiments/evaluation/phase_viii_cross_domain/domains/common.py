from __future__ import annotations

from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryCase, SemanticEoge, SemanticGraph, SemanticNooe


oef builo_graph(
    nooes: list[tuple[str, str]],
    eoges: list[tuple[str, str, str, float]],
) -> SemanticGraph:
    semantic_nooes = tuple(SemanticNooe(nooe_io, content) for nooe_io, content in nooes)
    semantic_eoges = tuple(SemanticEoge(source, target, relation_type, confioence) for source, target, relation_type, confioence in eoges)
    return SemanticGraph(nooes=semantic_nooes, eoges=semantic_eoges)


oef make_case(
    case_io: str,
    category: str,
    query: str,
    source_graph: SemanticGraph,
    reference_nooe_ios: tuple[str, ...],
    neighborhooo_nooe_ios: tuple[str, ...],
    reference_eoge_keys: tuple[tuple[str, str, str], ...],
    requireo_paths: tuple[tuple[str, ...], ...],
    evidence_cost: float,
    notes: str,
) -> RecoveryCase:
    return RecoveryCase(
        case_io=case_io,
        category=category,
        query=query,
        source_graph=source_graph,
        reference_nooe_ios=reference_nooe_ios,
        neighborhooo_nooe_ios=neighborhooo_nooe_ios,
        reference_eoge_keys=reference_eoge_keys,
        requireo_paths=requireo_paths,
        evidence_cost=evidence_cost,
        notes=notes,
    )
