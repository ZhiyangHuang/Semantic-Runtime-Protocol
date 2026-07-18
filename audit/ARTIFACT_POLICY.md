# SRP Artifact Policy

This document defines how SRP experimental outputs, evidence bundles, and release artifacts are produced, stored, reviewed, and governed.

The policy exists to preserve reproducibility without coupling the active runtime implementation to evaluation outputs.

## 1. Purpose

Artifacts are the curated evidence layer of the SRP repository.
They are not generic scratch outputs, and they are not the runtime implementation.

The policy separates:

- runtime code
- evaluation outputs
- curated release artifacts
- audit records

The dependency direction is one-way:

```text
srp_runtime -> experiments -> artifacts -> audit
```

The reverse direction is disallowed.

## 2. Artifact Categories

### 2.1 Curated Evidence Artifacts

Location:

```text
artifacts/
```

Purpose:

- release-facing evidence used to support claims
- curated outputs intended for citation, review, and reproduction

Examples:

- evaluation summaries
- metrics tables
- manifests
- provenance records
- frozen report bundles

Properties:

- version controlled
- deterministic when regenerated under the same frozen contract
- referenced by `audit/CLAIM_EVIDENCE_MAP.md`

## 2.4 Curated Artifact Layout

Release-facing artifacts are stored under `artifacts/`.

Current approved bundles:

```text
artifacts/
├── phase_v_retention/
│   ├── report.md
│   ├── summary.json
│   └── metadata.json
├── semantic_backend_comparison/
│   ├── report.md
│   ├── summary.json
│   └── metadata.json
└── external_validation/
    ├── report.md
    ├── summary.json
    └── metadata.json
```

### 2.2 Generated Experiment Outputs

Location:

```text
experiments/results/
```

Purpose:

- intermediate outputs generated during evaluation runs
- raw traces, temporary tables, and debugging outputs

Examples:

- raw logs
- intermediate JSON
- CSV dumps
- temporary traces

Properties:

- may be regenerated
- are not, by default, release source of truth
- may be promoted into `artifacts/` when reviewed and curated

### 2.3 Audit Records

Location:

```text
audit/
```

Purpose:

- claim mapping
- dependency analysis
- release governance
- architecture contracts

Examples:

- claim-to-evidence mapping
- artifact policy
- release checklist
- repository blueprint

Properties:

- describe and govern the repository
- do not silently redefine runtime semantics

## 3. Artifact Requirements

Every curated artifact should carry enough information to answer the following questions:

### 3.1 Provenance

Required fields should identify:

- `experiment_id`
- `version`
- `timestamp`
- `configuration`
- `runtime_environment`

### 3.2 Reproducibility

Each artifact should identify:

- generation command
- frozen input contract
- evaluation protocol

### 3.3 Traceability

Each artifact should be mappable to:

- claim
- mechanism
- evidence source

The reference for that mapping is `audit/CLAIM_EVIDENCE_MAP.md`.

## 4. Artifact Lifecycle

### 4.1 Development

During development, generated outputs may exist under:

```text
experiments/results/
```

These outputs are allowed to be noisy, intermediate, or incomplete.

### 4.2 Validation

Selected outputs may be reviewed, normalized, and promoted into:

```text
artifacts/
```

Promotion should occur only when the output is stable enough to support a claim or support a claim review.

### 4.3 Release

Only curated artifacts referenced by audit documents are considered release evidence.

If an output is not referenced by the audit layer, it should not be treated as paper-facing evidence.

### 4.4 Promotion Rule

An artifact becomes release-facing only after:

1. It is listed in `audit/ARTIFACT_PROMOTION_DECISION.md`
2. It has claim linkage
3. It contains provenance metadata
4. It is placed under `artifacts/`

If any one of these conditions is missing, the artifact remains outside the release-facing set.

## 5. Forbidden Patterns

The following patterns are disallowed for the release architecture:

- runtime importing artifacts
- runtime depending on experiments
- experiments mutating runtime state
- raw experiment dumps being treated as curated evidence
- unreviewed outputs being cited as release-grade artifacts

## 6. Relationship Between Layers

The intended flow is:

```text
srp_runtime
    |
    v
experiments
    |
    v
artifacts
    |
    v
audit
```

Each layer serves a different responsibility:

- `srp_runtime/` implements the protocol
- `experiments/` evaluates the protocol
- `artifacts/` stores curated evidence
- `audit/` governs claims and release boundaries

## 7. SRP Experiment Layer

`srp_experiment/` is treated as a legacy evidence layer and historical implementation substrate.
It may continue to support reproducibility and compatibility, but it is not the canonical artifact repository.

In particular:

- `srp_experiment/` may generate or explain historical evidence
- `artifacts/` is the curated release-facing evidence location

This distinction keeps legacy code from being mistaken for release evidence.

## 8. Release Rule

The release rule is conservative:

- if an artifact is not curated, it is not release evidence
- if an artifact is not referenced in audit, it is not claim evidence
- if an artifact cannot be reproduced under the frozen contract, it should not be promoted

The policy therefore prioritizes traceability over volume.
