# Phase 6.5 Controlled Deletion Plan

This plan freezes the deletion targets and preservation boundaries before any file removal happens.
It is the bridge between deletion readiness and controlled deletion.

## 1. Scope

Deletion candidates:

- `srp_experiment/`

Preservation boundaries:

- `audit/`
- `audit/provenance/`
- `audit/provenance/docs_archive/`
- `experiments/srp_runtime_legacy/`
- frozen legacy compatibility tests
- historical prototype assets retained for provenance

Completed relocation step:

- `docs/archive/` legacy shell retired after relocation to `audit/provenance/docs_archive/`

## 2. Deletion Candidates

### `docs/archive/` legacy shell

Current state:

| Check | Status |
| --- | --- |
| release gate dependency | PASS |
| runtime dependency | PASS |
| tooling dependency | PASS |
| provenance replacement | PASS |

Decision:

```text
COMPLETED
```

### `srp_experiment/`

Current state:

| Subtree | Status | Decision |
| --- | --- | --- |
| duplicated implementation | migrated | delete |
| old experiment harness | migrated | delete |
| compatibility wrappers | preserved temporarily | isolate |
| historical assets | provenance / archive | preserve or archive |

Decision:

```text
DELETE AFTER ISOLATION
```

## 3. Pre-Delete Checks

Run these checks immediately before any deletion operation:

```bash
python scripts/find_dependency_refs.py
python scripts/verify_release.py
python scripts/run_reproduction.py --core
```

Expected outcomes:

- runtime imports remain `0`
- tooling imports remain `0`
- docs archive executable references remain `0`
- release verification remains `PASS`
- core reproduction remains stable

## 4. Controlled Deletion Sequence

### Step 1

Keep `audit/provenance/docs_archive/` as preserved provenance.

Reason:

- it is the new archival home
- it is not a live dependency
- it must remain available for provenance and reproducibility

### Step 2

Re-run:

```bash
python scripts/find_dependency_refs.py
python scripts/verify_release.py
```

### Step 3

Isolate the remaining `srp_experiment/` compatibility and historical assets.

### Step 4

Completed: the old `docs/archive/` shell was retired after the provenance copy was fully rehomed and active references were removed.

### Step 5

Delete the core `srp_experiment/` implementation once the preserved assets are outside the live dependency graph.

## 5. Preservation Rules

The following assets are not to be deleted without explicit archival decision:

- `test_srp_runtime_legacy_compat.py`
- `test_longbench_v2_prototype.py`
- audit documents that preserve the frozen v1 evidence chain

## 6. Exit Criteria

Controlled deletion is complete only when:

- `audit/provenance/docs_archive/` remains preserved and referenced only as provenance
- the old `docs/archive/` shell has been retired or removed
- `srp_experiment/` has no live dependency arrows and its preserved assets are isolated
- release verification still passes
- the dependency audit shows only approved provenance references

This plan is the final checkpoint before controlled removal.

