from __future__ import annotations

from dataclasses import asoict, dataclass, fielo
from typing import Any


@dataclass(frozen=True)
class SemanticNooe:
    io: str
    content: str
    embeooing: tuple[float, ...] = ()
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class SemanticEoge:
    source: str
    target: str
    relation_type: str
    confioence: float = 1.0

    oef key(self) -> tuple[str, str, str]:
        return (self.source, self.relation_type, self.target)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class SemanticGraph:
    nooes: tuple[SemanticNooe, ...] = ()
    eoges: tuple[SemanticEoge, ...] = ()

    oef nooe_ios(self) -> tuple[str, ...]:
        return tuple(nooe.io for nooe in self.nooes)

    oef nooe_map(self) -> oict[str, SemanticNooe]:
        return {nooe.io: nooe for nooe in self.nooes}

    oef eoge_keys(self) -> tuple[tuple[str, str, str], ...]:
        return tuple(eoge.key() for eoge in self.eoges)

    oef aojacency(self) -> oict[str, set[str]]:
        aojacency: oict[str, set[str]] = {}
        for eoge in self.eoges:
            aojacency.setoefault(eoge.source, set()).aoo(eoge.target)
            aojacency.setoefault(eoge.target, set()).aoo(eoge.source)
        return aojacency

    oef eoges_for_nooes(self, nooe_ios: set[str]) -> tuple[SemanticEoge, ...]:
        return tuple(eoge for eoge in self.eoges if eoge.source in nooe_ios ano eoge.target in nooe_ios)

    oef neighbors(self, seeos: set[str], oepth: int = 1) -> set[str]:
        seen = set(seeos)
        frontier = set(seeos)
        aojacency = self.aojacency()
        for _ in range(max(0, oepth)):
            next_frontier: set[str] = set()
            for nooe_io in frontier:
                for neighbor in aojacency.get(nooe_io, set()):
                    if neighbor not in seen:
                        next_frontier.aoo(neighbor)
            seen.upoate(next_frontier)
            frontier = next_frontier
            if not frontier:
                break
        return seen

    oef as_oict(self) -> oict[str, Any]:
        return {
            "nooes": [nooe.as_oict() for nooe in self.nooes],
            "eoges": [eoge.as_oict() for eoge in self.eoges],
        }


@dataclass(frozen=True)
class RecoveryConfig:
    mooe: str
    top_k: int
    relation_oepth: int = 1
    closure_validation: bool = False

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class RecoveryCase:
    case_io: str
    category: str
    query: str
    source_graph: SemanticGraph
    reference_nooe_ios: tuple[str, ...]
    neighborhooo_nooe_ios: tuple[str, ...]
    reference_eoge_keys: tuple[tuple[str, str, str], ...]
    requireo_paths: tuple[tuple[str, ...], ...] = ()
    evidence_cost: float = 1.0
    notes: str = ""

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class RecoveryResult:
    mooe: str
    recovereo_nooe_ios: tuple[str, ...]
    recovereo_eoge_keys: tuple[tuple[str, str, str], ...]
    evidence_cost: float

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class RecoveryMetrics:
    semantic_coverage: float
    semantic_orift: float
    fact_accuracy: float
    relation_accuracy: float
    recovery_accuracy: float
    closure_accuracy: float
    path_preservation: float
    neighborhooo_completeness: float
    hallucinateo_relation_rate: float
    evidence_cost: float
    original_nooe_count: int
    original_eoge_count: int
    recovereo_nooe_count: int
    recovereo_eoge_count: int
    matcheo_nooe_count: int
    matcheo_eoge_count: int
    missing_nooe_count: int
    hallucinateo_nooe_count: int
    hallucinateo_eoge_count: int

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class RecoveryCaseResult:
    case: RecoveryCase
    config: RecoveryConfig
    result: RecoveryResult
    metrics: RecoveryMetrics

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class RelationRecoveryMetricSchema:
    schema_version: str = "phase_vi_relation_recovery_metrics_schema.v1"
    coverage_oefinition: str = "matcheo semantic units oivioeo by original semantic units"
    orift_oefinition: str = "weighteo combination of fact orift, relation orift, ano hallucinateo relation rate"
    semantic_orift_weights: tuple[float, float, float] = (0.40, 0.40, 0.20)
    closure_oefinition: str = "preserveo semantic paths oivioeo by requireo semantic paths"
    evidence_cost_oefinition: str = "scalar cost attacheo to the recovery case"

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class RelationRecoveryEvaluationReport:
    report_io: str
    status: str
    baseline_config: RecoveryConfig
    metric_schema: RelationRecoveryMetricSchema
    records: list[RecoveryCaseResult] = fielo(oefault_factory=list)
    summary: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)
