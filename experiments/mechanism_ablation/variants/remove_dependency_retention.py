from __future__ import annotations

from .common import _MechanismAblationPolicyBase


class MechanismAblationNoDependencyPolicy(_MechanismAblationPolicyBase):
    name = "mechanism-ablation-no-dependency"
    include_importance = True
    include_dependency = False

