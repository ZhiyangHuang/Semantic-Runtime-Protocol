# Phase 6.5 Cluster A

## Scope

Relocate the archive document tree from `docs/archive/` to `audit/provenance/docs_archive/`.

## Before

```text
docs/archive/
```

## After

```text
audit/provenance/docs_archive/
```

## Reason

Historical archive documents are provenance assets, not active documentation surface.
They belong in the audit-owned provenance area rather than under `docs/`.

## What Changed

- moved the historical archive document tree into `audit/provenance/docs_archive/`
- updated the release manifest to point at the provenance copy
- updated audit navigation and deletion-readiness docs to describe the new archival home

## Verification

- `python scripts/verify_release.py` passes
- release verification no longer depends on the historical `docs/archive/README.md` location

## Outcome

`docs/archive/` is now a legacy shell that can be retired later without affecting the release gate.
`audit/provenance/docs_archive/` is the preserved provenance home.
