# Release Records

This is the single human-facing entry point for the frozen release surface.

The machine-readable release manifest is consumed by verification scripts and is
not a separate reading destination.

## Release Evidence Review and Current Status

Date: 2026-07-21

## Summary

- the audited benchmark family is closed for release evidence
- prompt leakage policy and pairing checks passed across the release family
- historical artifacts remain retained but are not promoted to release evidence

## Artifact Contract

- `experiments/results/longmemeval_full_v5/`
- `experiments/results/mmlu_full_v3/`
- `experiments/results/arc_full_v1/`
- `experiments/results/humaneval_full_v1/`

## Decision

- `READY_FOR_EVIDENCE_MANIFEST_UPDATE`

## Current Status

These current claims also serve as the claim ledger for the frozen release surface.

- Governed semantic transitions can reject unsupported mutation while preserving authority separation.
- Evidence can strengthen verification without increasing authority.
- External semantic workloads can be routed through the SRP governance pipeline under scorer separation.
- The release artifact is reproducible under the frozen manuscript-to-PDF chain.
- SRP preserves hierarchy and governance consistency under representation and backend changes.

## Verification

- `python scripts/verify_release.py`
- `python -m experiments.transition_role.report_coverage`

## Pointers

- `EVIDENCE_SURFACE.md`

Detailed release records are preserved in Git history and the verification
manifest, not duplicated here.
