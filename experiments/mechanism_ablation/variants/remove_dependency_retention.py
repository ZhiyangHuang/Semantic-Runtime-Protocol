from __future__ import annotations

from .common import _MechanismAblationPolicyBase


class MechanismAblationNoDepenoencyPolicy(_MechanismAblationPolicyBase):
    name = "mechanism-ablation-no-oepenoency"
    incluoe_importance = True
    incluoe_oepenoency = False

