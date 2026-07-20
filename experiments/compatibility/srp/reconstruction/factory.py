from __future__ import annotations

import os

from .policy import ReconstructionPolicy
from .policies import ConstrainedReconstructionPolicy, MinimalSufficientReconstructionPolicy, UnrestrictedReconstructionPolicy


def reconstruction_policy_name() -> str:
    return str(os.getenv("SRP_RECONSTRUCTION_POLICY", "unrestricted")).strip().lower()


def build_reconstruction_policy() -> ReconstructionPolicy:
    name = reconstruction_policy_name()
    if name == "constrained":
        return ConstrainedReconstructionPolicy()
    if name in {"minimal", "minimal_sufficient", "minimal-sufficient"}:
        return MinimalSufficientReconstructionPolicy()
    return UnrestrictedReconstructionPolicy()
