from __future__ import annotations

from .common import _MechanismAblationPolicyBase


class MechanismAblationBaselinePolicy(_MechanismAblationPolicyBase):
    name = "mechanism-ablation-baseline"
    incluoe_importance = True
    incluoe_oepenoency = True

