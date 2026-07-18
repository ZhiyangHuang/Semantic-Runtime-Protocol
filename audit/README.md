# Audit

This directory contains governance records for Semantic Runtime Protocol releases.

The audit layer does not implement runtime behavior.
It defines how implementation, evidence, and release artifacts are connected and verified.

Primary manuscript source:

- [paper/SRP_ARXIV_DRAFT_V1.md](../paper/SRP_ARXIV_DRAFT_V1.md)

This file is a navigation index, not a source of truth.

## Governance Documents

### Repository Architecture

- [REPO_ARCHITECTURE_BLUEPRINT.md](REPO_ARCHITECTURE_BLUEPRINT.md)

Defines repository layers and dependency boundaries.

Core principle:

```text
srp_runtime -> experiments -> artifacts -> audit
```

### Claim Evidence Mapping

- [CLAIM_EVIDENCE_MAP.md](CLAIM_EVIDENCE_MAP.md)

Maps scientific claims to implementation mechanisms, evaluation evidence, and curated artifacts.

### Artifact Policy

- [ARTIFACT_POLICY.md](ARTIFACT_POLICY.md)

Defines artifact categories, provenance requirements, promotion rules, and reproducibility constraints.

### Release Checklist

- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)

Defines release validation requirements for runtime isolation, evidence completeness, artifact traceability, and reproducibility checks.

## Reviewer Entry Points

### Paper and Claim Traceability

Start with:

1. [CLAIM_EVIDENCE_MAP.md](CLAIM_EVIDENCE_MAP.md)
2. [PAPER_SOURCE_HIERARCHY.md](PAPER_SOURCE_HIERARCHY.md)
3. [PAPER_SOURCE_REFERENCE_AUDIT.md](PAPER_SOURCE_REFERENCE_AUDIT.md)

### Release Verification

Start with:

1. [RELEASE_HARDENING_RESULT.md](RELEASE_HARDENING_RESULT.md)
2. [RELEASE_CANDIDATE_CONSISTENCY_REVIEW.md](RELEASE_CANDIDATE_CONSISTENCY_REVIEW.md)
3. [VERIFY_RELEASE_BOUNDARY_REVIEW.md](VERIFY_RELEASE_BOUNDARY_REVIEW.md)

### Reproducibility

Start with:

1. [REPRODUCIBILITY_CHECKLIST.md](REPRODUCIBILITY_CHECKLIST.md)
2. [REPRODUCIBILITY_AND_DEPENDENCY_MAP.md](REPRODUCIBILITY_AND_DEPENDENCY_MAP.md)

### Artifact Evidence

Start with:

1. [ARTIFACT_POLICY.md](ARTIFACT_POLICY.md)
2. [ARTIFACT_PROMOTION_DECISION.md](ARTIFACT_PROMOTION_DECISION.md)
3. [../artifacts/MANIFEST.md](../artifacts/MANIFEST.md)

### Experiment Validation

Start with:

1. [EXPERIMENT_TRUTH_AUDIT.md](EXPERIMENT_TRUTH_AUDIT.md)
2. [PHASE_5_1_ARXIV_BUNDLE_AUDIT.md](PHASE_5_1_ARXIV_BUNDLE_AUDIT.md)
3. [PHASE_5_2_PDF_RENDER_AUDIT.md](PHASE_5_2_PDF_RENDER_AUDIT.md)

## Existing Audit Artifacts

These files preserve the release branch's calibration, scorer, evidence, and promotion history:

- [SRP Evidence Audit Specification V1](SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md)
- [SRP LongMemEval Evidence Audit Note](SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md)
- [SRP LongMemEval Scorer Alignment Audit](SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md)
- [SRP LongMemEval Evidence Promotion Decision](SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md)
- [SRP External Validation Adapter Calibration Note](SRP_EXTERNAL_VALIDATION_ADAPTER_CALIBRATION_NOTE.md)
- [SRP LoCoMo Calibration Note](SRP_LOCOMO_CALIBRATION_NOTE.md)
- [SRP LongMemEval Calibration Note](SRP_LONGMEMEVAL_CALIBRATION_NOTE.md)

The evidence reports remain here so reviewers can inspect the audit trail without hunting through historical working docs.

## Relationship With Other Layers

```text
srp_runtime/
active protocol implementation

experiments/
evaluation and evidence generation

artifacts/
curated release evidence

audit/
governance and verification
```

## Legacy Components

`srp_experiment/` is maintained as a legacy evidence layer.

It is not the current runtime implementation and should not be used as the source of truth for new development.
