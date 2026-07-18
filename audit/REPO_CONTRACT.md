# Repository Contract

This document freezes the repository rules for SRP release work.

It is a boundary contract, not a design history and not an implementation log.

## 1. Purpose

The repository exists to support four distinct layers:

- `fixed.md` is the canonical manuscript source
- `paper/` is the synchronized manuscript mirror and release snapshot area
- `srp_runtime/` is the protocol implementation layer
- `experiments/` is the evidence-generation layer
- `artifacts/` is the curated evidence layer
- `audit/` is the claim, provenance, and release-governance layer
- `arxiv_package/` is the packaging layer

The repository should read like a paper-defined artifact repository, not like a chronological archive of implementation phases.

## 2. Source Hierarchy

The source hierarchy is fixed as follows:

```text
fixed.md
  -> paper/SRP_ARXIV_DRAFT_V1.md
  -> paper/SRP_PAPER_FINAL_V1.md
  -> arxiv_package/
```

Rules:

- scientific text is edited in `fixed.md`
- mirrored manuscript files stay synchronized with `fixed.md`
- packaging files must not become the editing source of truth
- generated or packaged copies must not redefine the manuscript

## 3. Runtime Boundary

`srp_runtime/` contains protocol logic only.

It may define:

- state representation
- transition semantics
- validation rules
- constrained optimization interfaces
- evidence handling
- governance decisions
- execution commit logic

It must not depend on:

- `experiments/`
- benchmark outputs
- paper source files
- artifact paths
- release packaging internals

Runtime imports may flow outward from `experiments/` into `srp_runtime/`, but not the reverse.

## 4. Experiment Boundary

`experiments/` generates evidence under frozen runtime contracts.

Its job is to test claims, not to define SRP.

Experiment code must not:

- redefine authority
- redefine admissibility
- redefine transition semantics
- depend on paper prose as executable logic

Experiment names should describe the scientific role of the code, not the history of how the code evolved.

Preferred naming vocabulary:

- `observability`
- `boundary_validation`
- `constrained_optimization`
- `governance_sensitivity`
- `robustness`
- `external_validation`
- `transition_reconstruction`

Discouraged naming vocabulary:

- `phase_*`
- `policy_*` when the meaning is governance
- `recovery_*` when the meaning is transition reconstruction
- `memory_*` when the module is not actually a memory system

## 5. Artifact Boundary

`artifacts/` stores curated evidence objects.

Artifacts should be explicitly classified as:

- `main`
- `appendix`
- `archive`

Rules:

- artifacts must carry provenance
- artifacts cited by the claim ledger are release-relevant
- scratch outputs are not artifacts unless they have explicit provenance and status
- artifact status must not be implied by folder location alone

## 6. Audit Boundary

`audit/` records claims, provenance, release rules, and migration decisions.

Audit documents may:

- define claim-to-evidence mappings
- define source hierarchy
- define compatibility rules
- define deletion readiness
- record release audit results
- freeze terminology contracts
- track migration status for legacy experiment labels

Audit documents must not:

- silently change runtime semantics
- become the primary place where scientific claims are invented
- override the manuscript without an explicit release update

## 7. Compatibility Policy

Compatibility is allowed only as a frozen boundary.

Rules:

- compatibility code must be isolated in `compat/` or an equivalent clearly named boundary
- compatibility wrappers may preserve historical entrypoints
- compatibility wrappers may not define new terminology
- compatibility wrappers may not become the active source of truth
- compatibility wrappers should be thin and explicit

If a wrapper exists only so old scripts do not break, it belongs in compatibility, not in the main architecture.

## 8. Terminology Map

The repository should prefer SRP terms over historical implementation terms.

| Legacy term | SRP term | Use case |
| --- | --- | --- |
| `recovery` | `transition_reconstruction` | Use when the operation is about reconstructing semantic state across a governed transition |
| `policy` | `governance policy` or `governance` | Use when the operation is about authority or approval |
| `policy sensitivity` | `governance sensitivity` | Use when the analysis is about how governance behaves under parameter change |
| `boundary` | `admissibility boundary` | Use when the paper means whether a transition may proceed |
| `memory state` | `semantic runtime state` | Use when the object is governed semantic state rather than memory storage |
| `update` | `transition` or `commit` | Use when the operation is governed state change |
| `mutation` | `authorized transition` | Use when a change must pass governance before execution |

When the paper already uses a term, that term should be preferred over older implementation vocabulary.

## 8.1 Primary Entry Points

The preferred release-facing entry points are:

- `governance_sensitivity`
- `transition_reconstruction`
- `admissibility_boundary_validation`
- `transition_reconstruction_validation`
- `configuration_sensitivity_validation`
- `configuration_stability_validation`
- `representation_invariance_validation`
- `implementation_independence_validation`
- `cross_domain_validation`

The historical aliases are preserved only for compatibility:

- `policy_sensitivity`
- `reconstruction_policy`
- `recovery`
- `phase_ii_boundary`
- `phase_vi_relation_recovery`
- `phase_vii_parameter_sensitivity`
- `phase_vii_parameter_stability`
- `phase_viii_representation_invariance`
- `phase_viii_implementation_independence`
- `phase_viii_cross_domain`

Compatibility aliases may remain in code, tests, and frozen historical notes, but they should not be presented as the primary release vocabulary.

## 9. Migration Order

Repository migration should happen in this order:

1. Freeze the source hierarchy
2. Freeze the repository contract
3. Unify terminology in low-risk places first
4. Add compatibility wrappers where needed
5. Move legacy paths behind compatibility boundaries
6. Delete only after dependency and release audits say the path is dead

Do not start with large-scale rename operations before the contract is in place.

## 10. Non-Goals

This contract does not require:

- changing the scientific content of the paper
- renaming every module immediately
- deleting legacy assets before they are proven dead
- moving all history into compatibility in one pass

This contract only defines the rules for doing future migration safely.

## 11. Verification

Before and after any migration batch, check:

- manuscript source hierarchy still matches the contract
- `srp_runtime/` does not gain experiment dependencies
- `experiments/` remains evidence generation only
- `audit/` remains declarative
- packaging still renders cleanly
- release verification still passes
- terminology status remains consistent with the contract

Recommended checks:

```bash
python scripts/verify_release.py
python -m pytest
```

If `pytest` is unavailable, use the smallest available import and render checks instead.

## 12. Success Condition

The repository is in contract-compliant shape when:

- the manuscript source hierarchy is stable
- runtime, experiments, artifacts, and audit are clearly separated
- historical terms are mapped to SRP terms
- legacy compatibility is visibly isolated
- deletion candidates are evaluated against release evidence rather than naming preference

This contract is the rulebook for the next migration stage.
