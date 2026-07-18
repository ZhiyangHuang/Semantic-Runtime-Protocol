# SRP Artifact Manifest

## Purpose

This directory contains curated release-facing evidence bundles.
Artifacts here are promoted from `experiments/` only after audit approval.

Raw experiment outputs, traces, and debug dumps remain under `experiments/`.

## Artifact Index

| Artifact | Purpose | Claim Link |
| --- | --- | --- |
| `phase_v_retention` | governed reconstruction evaluation | recovery implementation case |
| `semantic_backend_comparison` | backend consistency evaluation | runtime independence |
| `external_validation` | external evidence package | external validation |

## Bundle Format

Each promoted artifact contains:

- `report.md`
- `summary.json`
- `metadata.json`

`metadata.json` records provenance, validation context, and promotion linkage.

## Reproduction Boundary

Artifacts are not runtime dependencies.
They are frozen evidence snapshots generated from experiment pipelines.

Reproduction should start from `experiments/` and validate against `artifacts/`.
