from __future__ import annotations

from .common import _MechanismAblationPolicyBase


class MechanismAblationNoImportancePolicy(_MechanismAblationPolicyBase):
    name = "mechanism-ablation-no-importance"
    include_importance = False
    include_dependency = True

