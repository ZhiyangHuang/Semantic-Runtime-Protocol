# SRP Reproducibility and Dependency Map

## Purpose

This document describes the dependency direction and rerun boundary for the current SRP release candidate.
It is intended to help a reviewer or maintainer answer: "What do I run first, and what depends on what?"

## High-Level Dependency Direction

```text
paper
  -> audit
  -> artifacts
  -> experiments
  -> srp_runtime
```

This is a packaging and governance view, not a runtime import graph.

## Layer Responsibilities

### `srp_runtime/`

Role:

- active protocol implementation

Responsibilities:

- semantic state
- transition kernel
- governance logic
- checkpointing
- operators and replay support

Must not depend on:

- `experiments/`
- `artifacts/`
- `audit/`
- `paper/`

### `experiments/`

Role:

- evaluation and evidence generation

Responsibilities:

- observability
- boundary validation
- optimization
- recovery evaluation
- robustness evaluation
- external validation

Primary dependency:

- `srp_runtime/`

Allowed legacy dependencies:

- selected helper paths under `srp_experiment/`, only where explicitly justified and frozen as legacy support

### `artifacts/`

Role:

- curated release-facing evidence

Responsibilities:

- frozen summary bundles
- provenance metadata
- release manifest

Must not be used as code input for runtime execution.

### `audit/`

Role:

- claim mapping
- provenance tracking
- release verification

Responsibilities:

- define what counts as a supported claim
- define which artifacts are release-facing
- define what passes release verification

Must not participate in experiment execution.

## Suggested Reproduction Order

The minimal reproduction order for the current release candidate is:

```text
1. Observability
2. Boundary validation
3. Optimization
4. Artifact generation
5. External validation
```

The repository now exposes a light orchestration entry point at `scripts/run_reproduction.py`.

## Known Boundary Notes

- `srp_experiment/` is preserved as a frozen legacy evidence layer.
- `paper/SRP_ARXIV_DRAFT_V1.md` remains the primary manuscript source.
- `artifacts/MANIFEST.md` is the submission-facing artifact index.
- The current release snapshot is auditable, but full environment-free regeneration is not yet fully frozen.
