# Phase 6.5 Cluster B2

## Scope

Move provenance-only `srp_experiment/` assets into `audit/provenance/srp_experiment/`.

## Moved Assets

- `srp_experiment/README.md`
- `srp_experiment/local_llm.py`
- `srp_experiment/run_local_diagnostics.py`
- `srp_experiment/data/longbench_v2/`
- `srp_experiment/schemas/`
- `srp_experiment/tmp/`

## New Home

```text
audit/provenance/srp_experiment/
```

## Provenance Metadata

New provenance files:

- `audit/provenance/srp_experiment/README.md`
- `audit/provenance/srp_experiment/migration_manifest.json`

## Verification

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`

## Outcome

The historical `srp_experiment/` documentation, schema snapshots, scratch traces, and legacy evidence helpers now live under `audit/provenance/srp_experiment/`.
The remaining `srp_experiment/` tree is focused on compatibility assets and deletion candidates.
