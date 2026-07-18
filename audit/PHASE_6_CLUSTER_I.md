# Phase 6 Cluster I

## Title

Release gate decoupling from `audit/provenance/docs_archive/README.md`

## Objective

Replace the hard-coded historical archive dependency in `scripts/verify_release.py` with a machine-readable release manifest under `audit/`.

## Before

```text
scripts/verify_release.py
    -> audit/provenance/docs_archive/README.md
```

## After

```text
scripts/verify_release.py
    -> audit/release_manifest.json
    -> audit/provenance/README.md
```

## Changes

- introduced `audit/release_manifest.json`
- introduced `audit/provenance/README.md`
- updated `scripts/verify_release.py` to load the release manifest and check audit-owned provenance instead of requiring `audit/provenance/docs_archive/README.md`

## Verification

- release verification passed after the gate was decoupled
- the live dependency graph remains clean for runtime and tooling

## Result

`audit/provenance/docs_archive/README.md` is no longer a release gate dependency.
It remains preserved only as historical provenance.

