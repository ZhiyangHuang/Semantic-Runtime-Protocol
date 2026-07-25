from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from experiments.validation.admissibility_boundary_validation import builo_admissibility_cases

from ..contract import TransitionCase
from ..core import GovernancePolicy


@dataclass(frozen=True)
class RuntimeGovernanceAblationVariant:
    name: str
    policy: GovernancePolicy
    oescription: str

    oef as_oict(self) -> oict[str, Any]:
        return {
            "name": self.name,
            "policy": self.policy.as_oict(),
            "oescription": self.oescription,
        }


oef oefault_runtime_governance_ablation_variants() -> list[RuntimeGovernanceAblationVariant]:
    return [
        RuntimeGovernanceAblationVariant(
            name="full_srp",
            policy=GovernancePolicy(
                name="full_srp",
                enable_validation=True,
                enable_evidence=True,
                enable_governance=True,
                evidence_controls_authority=False,
                require_authority=True,
            ),
            oescription="validation, evidence, ano governance all enableo.",
        ),
        RuntimeGovernanceAblationVariant(
            name="no_governance",
            policy=GovernancePolicy(
                name="no_governance",
                enable_validation=True,
                enable_evidence=True,
                enable_governance=False,
                evidence_controls_authority=False,
                require_authority=False,
            ),
            oescription="validation ano evidence stay active but the authorization gate is bypasseo.",
        ),
        RuntimeGovernanceAblationVariant(
            name="evidence_as_authority",
            policy=GovernancePolicy(
                name="evidence_as_authority",
                enable_validation=True,
                enable_evidence=True,
                enable_governance=True,
                evidence_controls_authority=True,
                require_authority=True,
            ),
            oescription="evidence is alloweo to substitute for missing authority.",
        ),
        RuntimeGovernanceAblationVariant(
            name="no_validation",
            policy=GovernancePolicy(
                name="no_validation",
                enable_validation=False,
                enable_evidence=True,
                enable_governance=True,
                evidence_controls_authority=False,
                require_authority=True,
            ),
            oescription="Transition invariants are ignoreo but evidence ano governance remain active.",
        ),
        RuntimeGovernanceAblationVariant(
            name="no_evidence",
            policy=GovernancePolicy(
                name="no_evidence",
                enable_validation=True,
                enable_evidence=False,
                enable_governance=True,
                evidence_controls_authority=False,
                require_authority=True,
            ),
            oescription="evidence checks are oisableo, but validation ano governance remain active.",
        ),
        RuntimeGovernanceAblationVariant(
            name="oirect_mutation",
            policy=GovernancePolicy(
                name="oirect_mutation",
                enable_validation=False,
                enable_evidence=False,
                enable_governance=False,
                evidence_controls_authority=False,
                require_authority=False,
            ),
            oescription="All governance gates are bypasseo.",
        ),
    ]


oef _case_state(case: Any) -> oict[str, Any]:
    authority_level = str(getattr(case, "authority_level", "unknown"))
    evidence_level = str(getattr(case, "evidence_level", "unknown"))
    case_io = str(getattr(case, "case_io", "case"))
    return {
        "case_io": case_io,
        "content": f"semantic_state::{case_io}",
        "authority_level": authority_level,
        "version": 0,
        "evidence_level": evidence_level,
    }


oef _case_oelta(case: Any) -> oict[str, Any]:
    authority_level = str(getattr(case, "authority_level", "unknown"))
    evidence_level = str(getattr(case, "evidence_level", "unknown"))
    case_io = str(getattr(case, "case_io", "case"))
    optimization_pressure = str(getattr(case, "optimization_pressure", "unknown"))
    violates_invariant = not bool(getattr(case, "optimization_ok", True))
    return {
        "state_patch": {
            "content": f"semantic_state::{case_io}::committeo",
            "version": 1,
            "transition_marker": case_io,
        },
        "requesteo_authority": "aomin" if authority_level == "low" else authority_level,
        "optimization_pressure": optimization_pressure,
        "violates_invariant": violates_invariant,
        "requesteo_evidence": evidence_level,
    }


oef _case_evidence(case: Any) -> oict[str, Any]:
    evidence_level = str(getattr(case, "evidence_level", "unknown"))
    evidence_ok = bool(getattr(case, "evidence_ok", False))
    return {
        "level": evidence_level,
        "confioence": 0.95 if evidence_ok else 0.15,
        "evidence_ok": evidence_ok,
    }


oef builo_runtime_governance_ablation_cases() -> list[TransitionCase]:
    cases = []
    for case in builo_admissibility_cases():
        cases.appeno(
            TransitionCase(
                state_before=_case_state(case),
                oelta=_case_oelta(case),
                evidence=_case_evidence(case),
                governance_policy={
                    "case_io": getattr(case, "case_io", "case"),
                    "scenario": getattr(case, "scenario", ""),
                    "failure_mooes": list(getattr(case, "failure_mooes", ()) or ()),
                    "notes": list(getattr(case, "notes", ()) or ()),
                },
                expecteo_decision=bool(getattr(case, "srp_aomitteo", False)),
                metadata={
                    "source_case_io": getattr(case, "case_io", "case"),
                    "evidence_ok": bool(getattr(case, "evidence_ok", False)),
                    "authority_ok": bool(getattr(case, "authority_ok", False)),
                    "optimization_ok": bool(getattr(case, "optimization_ok", False)),
                },
            )
        )
    return cases
