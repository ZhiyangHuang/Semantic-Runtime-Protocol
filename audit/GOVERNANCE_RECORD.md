# Governance Record

This document compresses the repository rules for the frozen SRP release into one reviewer-facing record.
It replaces the longer migration, terminology, and cleanup notes as the active governance reference.

## Release Boundary

- Release candidate date: `2026-07-19`
- Frozen commit: `645909269876b4adcad8170381197148ae4a310a`
- Canonical manuscript: `fixed.md`
- Submission PDF: `arxiv_package/main.pdf`

## Source Hierarchy

```text
fixed.md
  -> paper/SRP_ARXIV_DRAFT_V1.md
  -> paper/SRP_PAPER_FINAL_V1.md
  -> paper/latex/body_content.md
  -> paper/latex/body.tex
  -> arxiv_package/body.tex
  -> arxiv_package/main.pdf
```

Rules:

- edit scientific text in `fixed.md`
- keep the manuscript mirror synchronized
- treat `arxiv_package/` as a build layer, not as the source of truth

## Repository Boundaries

- `paper/` holds the manuscript and paper-facing release snapshots
- `experiments/` generates evidence under frozen runtime contracts
- `artifacts/` stores curated evidence objects
- `audit/` stores reviewer-facing release records and governance notes
- provenance is represented through the release snapshot, manifest, and claim map

## Terminology

Preferred release vocabulary:

- `governance_sensitivity`
- `transition_reconstruction`
- `admissibility_boundary_validation`
- `transition_reconstruction_validation`
- `configuration_sensitivity_validation`
- `configuration_stability_validation`
- `representation_invariance_validation`
- `implementation_independence_validation`
- `cross_domain_validation`
- `LongMemEval reality check`

Deprecated as primary release vocabulary:

- `policy`
- `recovery`
- `recovery_*`
- `phase_*`

Legacy terms may appear only in compatibility wrappers, archived notes, or provenance records.

## Compatibility Policy

- compatibility wrappers must stay thin and explicit
- compatibility may preserve frozen historical entrypoints
- compatibility does not define new primary terminology
- compatibility does not override the manuscript or the manifest

## Freeze Rule

- the active release boundary is the current freeze state, not the development history
- new evidence must not overwrite the frozen release candidate snapshot
- future work belongs on a new branch or release candidate
