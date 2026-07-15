from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class BoundaryRange:
    values: tuple[Any, ...]
    min: Any | None
    max: Any | None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FeasibleRegion:
    parameter_ranges: dict[str, BoundaryRange]
    candidate_count: int
    feasible_candidate_count: int
    sampling_method: str = "grid"
    generated_by: str = "phase_ii_boundary_v1"
    seed: int = 42
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "parameter_ranges": {name: rng.as_dict() for name, rng in self.parameter_ranges.items()},
            "candidate_count": self.candidate_count,
            "feasible_candidate_count": self.feasible_candidate_count,
            "coverage": self.coverage,
            "sampling_method": self.sampling_method,
            "generated_by": self.generated_by,
            "seed": self.seed,
            "metadata": dict(self.metadata),
        }

    @property
    def coverage(self) -> float:
        if self.candidate_count <= 0:
            return 0.0
        return self.feasible_candidate_count / float(self.candidate_count)

    def activation_threshold_values(self) -> tuple[float, ...]:
        range_ = self.parameter_ranges.get("activation_threshold")
        return tuple(float(value) for value in range_.values) if range_ is not None else ()

    def recovery_min_evidence_values(self) -> tuple[int, ...]:
        range_ = self.parameter_ranges.get("recovery_min_evidence")
        return tuple(int(value) for value in range_.values) if range_ is not None else ()

    def candidate_axes(self) -> tuple[tuple[float, int], ...]:
        return tuple(
            (activation_threshold, recovery_min_evidence)
            for activation_threshold in self.activation_threshold_values()
            for recovery_min_evidence in self.recovery_min_evidence_values()
        )


def load_feasible_region(source: str | Path | dict[str, Any]) -> FeasibleRegion:
    if isinstance(source, (str, Path)):
        payload = json.loads(Path(source).read_text(encoding="utf-8"))
    else:
        payload = dict(source)

    parameter_ranges: dict[str, BoundaryRange] = {}
    for name, raw_range in payload.get("parameter_ranges", {}).items():
        parameter_ranges[name] = BoundaryRange(
            values=tuple(raw_range.get("values", ())),
            min=raw_range.get("min"),
            max=raw_range.get("max"),
        )

    return FeasibleRegion(
        parameter_ranges=parameter_ranges,
        candidate_count=int(payload.get("candidate_count", 0)),
        feasible_candidate_count=int(payload.get("feasible_candidate_count", 0)),
        sampling_method=str(payload.get("sampling_method", "grid")),
        generated_by=str(payload.get("generated_by", "phase_ii_boundary_v1")),
        seed=int(payload.get("seed", 42)),
        metadata=dict(payload.get("metadata", {})),
    )

