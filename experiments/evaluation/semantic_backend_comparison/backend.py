from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ComparisonCase:
    case_id: str
    category: str
    source_text: str
    candidate_text: str
    expected_verdict: bool
    notes: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BackendOutcome:
    backend_name: str
    mode: str
    decision: str
    score: float
    latency_seconds: float
    reason: str
    raw_text: str = ""
    fallback_used: bool = False
    usage: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class ComparisonBackend(Protocol):
    backend_name: str

    def evaluate(self, case: ComparisonCase) -> BackendOutcome:
        ...


def build_comparison_cases() -> list[ComparisonCase]:
    return [
        ComparisonCase(
            case_id="case_1",
            category="paraphrase",
            source_text="The archive preserves historical evidence for replay.",
            candidate_text="The archive preserves historical evidence for replay.",
            expected_verdict=True,
            notes="Exact paraphrase should be accepted by both backends.",
        ),
        ComparisonCase(
            case_id="case_2",
            category="paraphrase",
            source_text="Evidence strengthens verification without changing authority.",
            candidate_text="Evidence strengthens verification without changing authority.",
            expected_verdict=True,
            notes="Authority-preserving paraphrase should be accepted.",
        ),
        ComparisonCase(
            case_id="case_3",
            category="contradiction",
            source_text="The archive preserves historical evidence for replay.",
            candidate_text="The archive destroys historical evidence for replay.",
            expected_verdict=False,
            notes="Direct contradiction should be rejected.",
        ),
        ComparisonCase(
            case_id="case_4",
            category="contradiction",
            source_text="The system should validate boundaries before optimization.",
            candidate_text="The system should optimize before validating boundaries.",
            expected_verdict=False,
            notes="Order inversion contradicts the governed pipeline.",
        ),
        ComparisonCase(
            case_id="case_5",
            category="authority_violation",
            source_text="The runtime must not mutate state without governance.",
            candidate_text="The runtime may mutate state without governance.",
            expected_verdict=False,
            notes="Authority boundary violation should be rejected.",
        ),
        ComparisonCase(
            case_id="case_6",
            category="authority_violation",
            source_text="Optimization recommends a configuration but governance approves execution.",
            candidate_text="Optimization recommends a configuration and runtime immediately applies it.",
            expected_verdict=False,
            notes="Recommendation must not collapse into execution.",
        ),
        ComparisonCase(
            case_id="case_7",
            category="boundary_case",
            source_text="Boundary validation requires preserved evidence.",
            candidate_text="Boundary validation requires preserved evidence before any transition.",
            expected_verdict=True,
            notes="Near-boundary but supportive evidence should be accepted or escalated with evidence.",
        ),
        ComparisonCase(
            case_id="case_8",
            category="boundary_case",
            source_text="The optimizer cannot rewrite runtime history.",
            candidate_text="The optimizer can rewrite runtime history when convenient.",
            expected_verdict=False,
            notes="History rewrite language should be rejected.",
        ),
        ComparisonCase(
            case_id="case_9",
            category="authority_violation",
            source_text="A recommendation should be reviewed before execution.",
            candidate_text="A recommendation should be executed immediately without review.",
            expected_verdict=False,
            notes="Recommendation must stay separate from execution.",
        ),
        ComparisonCase(
            case_id="case_10",
            category="boundary_case",
            source_text="Evidence can strengthen verification when uncertainty remains.",
            candidate_text="Evidence can strengthen verification when uncertainty remains and should trigger review only if needed.",
            expected_verdict=True,
            notes="Boundary-adjacent supportive evidence should remain admissible.",
        ),
    ]
