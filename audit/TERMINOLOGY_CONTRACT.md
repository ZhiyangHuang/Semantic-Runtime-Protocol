# SRP Terminology Contract

This document freezes the terminology used by the SRP repository for release-facing work.

It exists to keep the manuscript, the implementation, the artifact layer, and the audit layer aligned.

## Core Concepts

- Semantic Runtime State
- Semantic Transition
- Admissibility Boundary
- Governance Decision
- Transition Reconstruction
- Evidence-Controlled Verification

## Preferred Implementation Terms

- `governance_sensitivity`
- `transition_reconstruction`
- `admissibility_boundary_validation`
- `transition_reconstruction_validation`
- `configuration_sensitivity_validation`
- `configuration_stability_validation`
- `representation_invariance_validation`
- `implementation_independence_validation`
- `cross_domain_validation`

## Deprecated Terms

The following terms are deprecated for primary release-facing naming:

- `policy`
- `policy_sensitivity`
- `recovery`
- `recovery_*`
- `phase_*`

## Compatibility Rule

Deprecated terms may appear only when:

- a frozen historical wrapper is required
- a provenance record preserves an immutable identifier
- an audit note documents migration history

Deprecated terms should not define new primary modules, new claims, or new manuscript vocabulary.

## Freeze Rule

If a future change introduces a new primary concept name, it should be added here before it becomes release-facing.

