# Audit

This directory is the reviewer-facing governance layer for the current SRP release candidate.
It records the live release boundary, the evidence map, and the reproducibility contract.

## Current Release Files

- [RELEASE_SNAPSHOT.md](RELEASE_SNAPSHOT.md)
- [RELEASE_PDF_VISUAL_AUDIT.md](RELEASE_PDF_VISUAL_AUDIT.md)
- [RELEASE_FREEZE_NOTE.md](RELEASE_FREEZE_NOTE.md)
- [PAPER_BUILD_PIPELINE.md](PAPER_BUILD_PIPELINE.md)
- [CLAIM_EVIDENCE_MAP.md](CLAIM_EVIDENCE_MAP.md)
- [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md)
- [REAL_VALIDATION_SCIENTIFIC_REPORT.md](REAL_VALIDATION_SCIENTIFIC_REPORT.md)
- [RELEASE_CLEANUP_PLAN.md](RELEASE_CLEANUP_PLAN.md)
- [RELEASE_MANIFEST.md](release_manifest.json)
- [TERMINOLOGY_CONTRACT.md](TERMINOLOGY_CONTRACT.md)
- [PHASE_TERMINOLOGY_MIGRATION_STATUS.md](PHASE_TERMINOLOGY_MIGRATION_STATUS.md)

## Provenance

- `provenance/` preserves historical working material for traceability.
- Historical docs are not release-facing evidence unless they are referenced by the current manifest.

## Review Rule

Start with the manifest and the two real-validation reports.
If a file is not referenced there, it should be treated as historical or supporting material rather than current release evidence.
