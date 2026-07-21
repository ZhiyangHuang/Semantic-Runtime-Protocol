# Release Manifest Freeze Review

Date: 2026-07-21

## Purpose

Validate that the release manifest can be frozen against the release-facing documentation surface.

This review covers the active release manifest at `audit/release_manifest.json`.

## Reference Surface

The release-facing documentation surface is:

- `docs/benchmarks/`
- `docs/release/`
- `docs/archive/benchmark_history/`

## Review Outcome

### Manifest reference audit

The active manifest should no longer depend on development-only iteration file paths for the release surface.

Expected release-facing references:
- benchmark reports in `docs/benchmarks/`
- release gate review in `docs/release/`
- historical iteration records in `docs/archive/benchmark_history/`

### Invalid history

Historical invalid or diagnostic artifacts are retained for provenance only and are not promoted to release evidence.

### LongMemEval special handling

LongMemEval remains split across:
- original research evaluation
- shared benchmark alignment

The manifest must preserve that distinction and not collapse the two tracks into a single score.

### HumanEval special handling

HumanEval release evidence must refer to the closed full artifact and its canonical release report, while preserving the execution sandbox boundary.

## Decision

Status:
- `READY_FOR_MANIFEST_FREEZE`

Next allowed action:
- update `audit/release_manifest.json` to the release-facing surface and then freeze the release branch layout
