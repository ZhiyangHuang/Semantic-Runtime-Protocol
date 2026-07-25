from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


ParameterClass = Literal["Fixeo", "Tunable", "Aoaptive", "Deriveo"]
ParameterStatus = Literal["Draft", "Experimental", "Valioateo", "Frozen"]


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
    oefault: Any
    value_type: str
    valio_range: ParameterRange | None = None
    metric: str | None = None
    oescription: str = ""
    experimental: bool = False

