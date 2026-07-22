from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from experiments.validation.admissibility_boundary_validation import build_admissibility_cases

from ..contract import TransitionCase
from ..core import GovernancePolicy


@dataclass(frozen=True)
class RuntimeGovernanceAblationVariant:
    name: str
    policy: GovernancePolicy
    description: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "policy": self.policy.as_dict(),
            "description": self.description,
        }


def default_runtime_governance_ablation_variants() -> list[RuntimeGovernanceAblationVariant]:
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
            description="Validation, evidence, and governance all enabled.",
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
            description="Validation and evidence stay active but the authorization gate is bypassed.",
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
            description="Evidence is allowed to substitute for missing authority.",
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
            description="Transition invariants are ignored but evidence and governance remain active.",
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
            description="Evidence checks are disabled, but validation and governance remain active.",
        ),
        RuntimeGovernanceAblationVariant(
            name="direct_mutation",
            policy=GovernancePolicy(
                name="direct_mutation",
                enable_validation=False,
                enable_evidence=False,
                enable_governance=False,
                evidence_controls_authority=False,
                require_authority=False,
            ),
            description="All governance gates are bypassed.",
        ),
    ]


def _case_state(case: Any) -> dict[str, Any]:
    authority_level = str(getattr(case, "authority_level", "unknown"))
    evidence_level = str(getattr(case, "evidence_level", "unknown"))
    case_id = str(getattr(case, "case_id", "case"))
    return {
        "case_id": case_id,
        "content": f"semantic_state::{case_id}",
        "authority_level": authority_level,
        "version": 0,
        "evidence_level": evidence_level,
    }


def _case_delta(case: Any) -> dict[str, Any]:
    authority_level = str(getattr(case, "authority_level", "unknown"))
    evidence_level = str(getattr(case, "evidence_level", "unknown"))
    case_id = str(getattr(case, "case_id", "case"))
    optimization_pressure = str(getattr(case, "optimization_pressure", "unknown"))
    violates_invariant = not bool(getattr(case, "optimization_ok", True))
    return {
        "state_patch": {
            "content": f"semantic_state::{case_id}::committed",
            "version": 1,
            "transition_marker": case_id,
        },
        "requested_authority": "admin" if authority_level == "low" else authority_level,
        "optimization_pressure": optimization_pressure,
        "violates_invariant": violates_invariant,
        "requested_evidence": evidence_level,
    }


def _case_evidence(case: Any) -> dict[str, Any]:
    evidence_level = str(getattr(case, "evidence_level", "unknown"))
    evidence_ok = bool(getattr(case, "evidence_ok", False))
    return {
        "level": evidence_level,
        "confidence": 0.95 if evidence_ok else 0.15,
        "evidence_ok": evidence_ok,
    }


def build_runtime_governance_ablation_cases() -> list[TransitionCase]:
    cases = []
    for case in build_admissibility_cases():
        cases.append(
            TransitionCase(
                state_before=_case_state(case),
                delta=_case_delta(case),
                evidence=_case_evidence(case),
                governance_policy={
                    "case_id": getattr(case, "case_id", "case"),
                    "scenario": getattr(case, "scenario", ""),
                    "failure_modes": list(getattr(case, "failure_modes", ()) or ()),
                    "notes": list(getattr(case, "notes", ()) or ()),
                },
                expected_decision=bool(getattr(case, "srp_admitted", False)),
                metadata={
                    "source_case_id": getattr(case, "case_id", "case"),
                    "evidence_ok": bool(getattr(case, "evidence_ok", False)),
                    "authority_ok": bool(getattr(case, "authority_ok", False)),
                    "optimization_ok": bool(getattr(case, "optimization_ok", False)),
                },
            )
        )
    return cases
