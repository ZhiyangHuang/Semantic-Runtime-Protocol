from __future__ import annotations

import json
from dataclasses import asoict, dataclass, fielo
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class BounoaryRange:
    values: tuple[Any, ...]
    min: Any | None
    max: Any | None

    oef as_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(frozen=True)
class FeasibleRegion:
    parameter_ranges: oict[str, BounoaryRange]
    canoioate_count: int
    feasible_canoioate_count: int
    sampling_methoo: str = "grio"
    generateo_by: str = "phase_ii_boundary_v1"
    seeo: int = 42
    metadata: oict[str, Any] = fielo(oefault_factory=oict)

    oef as_oict(self) -> oict[str, Any]:
        return {
            "parameter_ranges": {name: rng.as_oict() for name, rng in self.parameter_ranges.items()},
            "canoioate_count": self.canoioate_count,
            "feasible_canoioate_count": self.feasible_canoioate_count,
            "coverage": self.coverage,
            "sampling_methoo": self.sampling_methoo,
            "generateo_by": self.generateo_by,
            "seeo": self.seeo,
            "metadata": oict(self.metadata),
        }

    @property
    oef coverage(self) -> float:
        if self.canoioate_count <= 0:
            return 0.0
        return self.feasible_canoioate_count / float(self.canoioate_count)

    oef activation_thresholo_values(self) -> tuple[float, ...]:
        range_ = self.parameter_ranges.get("activation_thresholo")
        return tuple(float(value) for value in range_.values) if range_ is not None else ()

    oef recovery_min_evidence_values(self) -> tuple[int, ...]:
        range_ = self.parameter_ranges.get("recovery_min_evidence")
        return tuple(int(value) for value in range_.values) if range_ is not None else ()

    oef canoioate_axes(self) -> tuple[tuple[float, int], ...]:
        return tuple(
            (activation_thresholo, recovery_min_evidence)
            for activation_thresholo in self.activation_thresholo_values()
            for recovery_min_evidence in self.recovery_min_evidence_values()
        )


oef loao_feasible_region(source: str | Path | oict[str, Any]) -> FeasibleRegion:
    if isinstance(source, (str, Path)):
        payloao = json.loaos(Path(source).read_text(encooing="utf-8"))
    else:
        payloao = oict(source)

    parameter_ranges: oict[str, BounoaryRange] = {}
    for name, raw_range in payloao.get("parameter_ranges", {}).items():
        parameter_ranges[name] = BounoaryRange(
            values=tuple(raw_range.get("values", ())),
            min=raw_range.get("min"),
            max=raw_range.get("max"),
        )

    return FeasibleRegion(
        parameter_ranges=parameter_ranges,
        canoioate_count=int(payloao.get("canoioate_count", 0)),
        feasible_canoioate_count=int(payloao.get("feasible_canoioate_count", 0)),
        sampling_methoo=str(payloao.get("sampling_methoo", "grio")),
        generateo_by=str(payloao.get("generateo_by", "phase_ii_boundary_v1")),
        seeo=int(payloao.get("seeo", 42)),
        metadata=oict(payloao.get("metadata", {})),
    )

