from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ReconstructionMetrics:
    selected_object_count: int | None = None
    rejected_object_count: int | None = None
    available_object_count: int | None = None
    policy_name: str | None = None


@dataclass
class ReconstructionResult:
    structured_state_package: Dict[str, object]
    recovered_objects: List[Dict[str, object]] = field(default_factory=list)
    selected_objects: List[Dict[str, object]] = field(default_factory=list)
    rejected_objects: List[Dict[str, object]] = field(default_factory=list)
    policy_name: str = "unrestricted"
    memory: str = ""
    usage: Optional[Dict] = None
    metrics: ReconstructionMetrics = field(default_factory=ReconstructionMetrics)


class ReconstructionPolicy(ABC):
    name = "unrestricted"

    @abstractmethod
    def reconstruct(self, package: Dict, client=None, anchor_memory: str = "") -> ReconstructionResult:
        raise NotImplementedError
