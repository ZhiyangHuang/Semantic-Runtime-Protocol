# Temporary 3: Cleanup Review Plan

This file controls the final cleanup pass.

Its job is to prevent:

1. over-cleaning that breaks provenance or reproducibility
2. under-cleaning that leaves duplicate utility files with no primary location
3. mixing short-lived cleanup notes with permanent governance documents

## This Pass Is Allowed To Do

- isolate cleanup-review files into this folder
- delete safe cache artifacts
- create review manifests
- mark canonical vs secondary file families

## This Pass Should Not Do

- delete formal evidence
- delete benchmark provenance
- delete canonical configs
- delete canonical entrypoints
- delete current paper-facing tables or figures

## Safe Deletion Class

These are safe to delete immediately:

- `__pycache__/`
- root-level cleanup scratch notes after they are moved here

## Review-First Class

These should only be deleted after explicit review:

- exploratory configs
- stale generated launcher configs
- side risk-test exports
- repeated runtime-equivalence snapshots
- old wrapper workflows

## Canonical Before Deletion Rule

No file family should be deleted until:

1. a canonical replacement is already named
2. an index points to it
3. the file being deleted is not the last provenance-bearing copy

## Current Closeout Goal

After this pass, the repository should satisfy:

- cleanup-process files are isolated
- caches are removed
- canonical paths are documented
- future deletion can happen by reviewing this folder first
