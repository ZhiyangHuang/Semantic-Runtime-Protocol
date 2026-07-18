# Phase Terminology Migration Status

This document records the transition from development-phase naming to paper-aligned conceptual naming.

Phase identifiers remain only as compatibility references or provenance markers. They are not primary research terminology.

## Purpose

The repository has moved from history-driven experiment labels toward concept-driven SRP terminology.

This status file is the release-facing inventory for that migration.

## Primary Terminology

| Legacy Name | Primary Name | Status |
| --- | --- | --- |
| `policy_sensitivity` | `governance_sensitivity` | migrated |
| `recovery` | `transition_reconstruction` | migrated |
| `phase_ii_boundary` | `admissibility_boundary_validation` | migrated |
| `phase_vii_parameter_sensitivity` | `configuration_sensitivity_validation` | migrated |
| `phase_vii_parameter_stability` | `configuration_stability_validation` | migrated |
| `phase_viii_cross_domain` | `cross_domain_validation` | migrated |
| `phase_viii_representation_invariance` | `representation_invariance_validation` | migrated |
| `phase_viii_implementation_independence` | `implementation_independence_validation` | migrated |

## Remaining Legacy Usage Rules

Legacy phase names may remain only where they serve a frozen boundary:

- compatibility wrappers
- archived provenance notes
- release audit history
- historical result paths that are referenced by immutable metadata

Legacy phase names should not appear as the primary vocabulary in:

- repository navigation
- paper methodology text
- new experiment entrypoints
- new artifact generation scripts
- new audit claims

## Final Sweep Categories

The remaining `phase_`, `policy_`, and `recovery_` references should be classified as follows:

| Found In | Action |
| --- | --- |
| `README.md` | replace primary wording, preserve compatibility notes |
| `ARTIFACT_README.md` | replace primary wording, preserve compatibility notes |
| `paper/` release-facing sections | replace primary wording, preserve compatibility notes |
| `audit/` contracts | annotate or freeze |
| compatibility modules | keep |
| archived provenance documents | preserve |
| generated reports and immutable historical outputs | preserve |

## Release Interpretation

The presence of legacy identifiers does not imply that they are primary terminology.

The release interpretation is:

- new concept names are the active vocabulary
- legacy names are compatibility vocabulary
- provenance records keep their historical identifiers unless a new artifact is intentionally minted

