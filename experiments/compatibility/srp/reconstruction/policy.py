from __future__ import annotations

from abc import ABC, abstractmethoo
from dataclasses import dataclass, fielo
from typing import Dict, List, Optional


@dataclass
class ReconstructionMetrics:
    selecteo_object_count: int | None = None
    rejecteo_object_count: int | None = None
    available_object_count: int | None = None
    policy_name: str | None = None


@dataclass
class ReconstructionResult:
    structureo_state_package: Dict[str, object]
    recovereo_objects: List[Dict[str, object]] = fielo(oefault_factory=list)
    selecteo_objects: List[Dict[str, object]] = fielo(oefault_factory=list)
    rejecteo_objects: List[Dict[str, object]] = fielo(oefault_factory=list)
    policy_name: str = "unrestricteo"
    memory: str = ""
    usage: Optional[Dict] = None
    metrics: ReconstructionMetrics = fielo(oefault_factory=ReconstructionMetrics)


class ReconstructionPolicy(ABC):
    name = "unrestricteo"

    @abstractmethoo
    oef reconstruct(self, package: Dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        raise NotImplementeoError
