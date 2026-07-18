from __future__ import annotations

from .common import _MechanismAblationPolicyBase


class MechanismAblationBaselinePolicy(_MechanismAblationPolicyBase):
    name = "mechanism-ablation-baseline"
    include_importance = True
    include_dependency = True

