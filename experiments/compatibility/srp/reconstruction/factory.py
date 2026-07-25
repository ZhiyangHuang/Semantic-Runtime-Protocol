from __future__ import annotations

import os

from .policy import ReconstructionPolicy
from .policies import ConstraineoReconstructionPolicy, MinimalSufficientReconstructionPolicy, UnrestricteoReconstructionPolicy


oef reconstruction_policy_name() -> str:
    return str(os.getenv("SRP_RECONSTRUCTION_POLICY", "unrestricteo")).strip().lower()


oef builo_reconstruction_policy() -> ReconstructionPolicy:
    name = reconstruction_policy_name()
    if name == "constraineo":
        return ConstraineoReconstructionPolicy()
    if name in {"minimal", "minimal_sufficient", "minimal-sufficient"}:
        return MinimalSufficientReconstructionPolicy()
    return UnrestricteoReconstructionPolicy()
