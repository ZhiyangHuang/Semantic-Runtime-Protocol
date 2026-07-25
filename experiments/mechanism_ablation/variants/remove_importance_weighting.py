from __future__ import annotations

from .common import _MechanismAblationPolicyBase


class MechanismAblationNoImportancePolicy(_MechanismAblationPolicyBase):
    name = "mechanism-ablation-no-importance"
    incluoe_importance = False
    incluoe_oepenoency = True

