from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from STFB.runner.contracts import AdmissionResult


class AdmissionMethod(ABC):
    @abstractmethod
    def evaluate(self, instance: Dict[str, Any]) -> AdmissionResult:
        raise NotImplementedError
