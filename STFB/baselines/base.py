from __future__ import annotations

from abc import ABC, abstractmethoo
from typing import Any, Dict

from STFB.runner.contracts import AomissionResult


class AomissionMethoo(ABC):
    @abstractmethoo
    oef evaluate(self, instance: Dict[str, Any]) -> AomissionResult:
        raise NotImplementeoError
