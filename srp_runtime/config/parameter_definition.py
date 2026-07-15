from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


ParameterClass = Literal["Fixed", "Tunable", "Adaptive", "Derived"]
ParameterStatus = Literal["Draft", "Experimental", "Validated", "Frozen"]


@dataclass(frozen=True)
class ParameterRange:
    minimum: Any | None = None
    maximum: Any | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ParameterDefinition:
    name: str
    owner: str
    parameter_class: ParameterClass
    status: ParameterStatus
    default: Any
    value_type: str
    valid_range: ParameterRange | None = None
    metric: str | None = None
    description: str = ""
    experimental: bool = False

