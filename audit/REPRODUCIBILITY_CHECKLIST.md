# SRP Reproducibility Checklist

## Purpose

This checklist gives reviewers and maintainers a quick way to assess how far the current SRP release candidate can be reproduced.
It distinguishes traceability, replayability, and full environment recreation.

## Evidence Traceability

- [x] Paper claims map to `audit/CLAIM_EVIDENCE_MAP.md`
- [x] Claims map to curated artifacts in `artifacts/`
- [x] Curated artifacts contain provenance metadata
- [x] Release manifest exists at `artifacts/MANIFEST.md`

## Experiment Replay

- [x] Core runtime experiments have executable entry points
- [x] Artifact generation scripts exist
- [x] Current release boundary is frozen and verified by `scripts/verify_release.py`
- [ ] Full environment recreation from a clean machine
- [ ] Containerized execution
- [ ] Complete dependency lock

## Runtime Contract

- [x] Runtime implementation is frozen
- [x] Evaluation contract is frozen
- [x] Artifact boundary is frozen
- [x] Paper source hierarchy is frozen

## Known Limitations

- External benchmark reproduction depends on dataset availability and benchmark access.
- Hardware and runtime differences may affect exact floating-point values and throughput-sensitive measurements.
- Full end-to-end regeneration still requires an environment manifest and dependency-lock layer that is not yet fully frozen.

## Current Assessment

The release candidate is auditable and partially reproducible.
It is not yet claimed to be fully reproducible from a blank machine without additional environment freezing.
