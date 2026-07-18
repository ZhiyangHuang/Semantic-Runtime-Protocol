# Phase 6.5 Cluster A1

## Scope

Retire the empty `docs/archive/` shell after the archive contents have been relocated to `audit/provenance/docs_archive/`.

## Preconditions

- archive contents moved to provenance
- `scripts/verify_release.py` no longer depends on `docs/archive/`
- `audit/release_manifest.json` updated
- `audit/provenance/README.md` exists

## Action

Delete:

```text
docs/archive/
```

## Verification

Run:

```bash
python scripts/find_dependency_refs.py
python scripts/verify_release.py
```

Expected:

- `docs/archive` executable references = `0`
- release gate = `PASS`

## Outcome

The old `docs/archive/` shell is retired.
Historical archive evidence now lives only under `audit/provenance/docs_archive/`.
