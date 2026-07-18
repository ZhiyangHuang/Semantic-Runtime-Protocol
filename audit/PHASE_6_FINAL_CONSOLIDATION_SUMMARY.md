# Phase 6 Repository Consolidation Summary

## Objective

Separate the historical experiment implementation from the current SRP live runtime and establish three explicit layers:

- live implementation
- compatibility boundary
- historical provenance

## Final Dependency Status

| Dependency Class | Before | After | Status |
| --- | ---: | ---: | --- |
| runtime imports | 20 | 0 | Complete |
| tooling imports | 28 | 0 | Complete |
| test imports | 87 | 22 | Frozen assets |

## Architectural Outcome

### Live Source of Truth

Retained:

```text
srp_runtime/
experiments/
scripts/
tests/
audit/
paper/
arxiv_package/
```

Responsibilities:

- runtime behavior
- validation pipeline
- release artifact generation

### Compatibility Boundary

Retained:

```text
experiments/srp_runtime_legacy/
```

Purpose:

- legacy API compatibility
- historical reproducibility

### Delete Candidates

Candidates:

```text
srp_experiment/
docs/archive/ (retired shell after relocation)
```

Deletion conditions:

- dependency scan remains clean for live code
- frozen compatibility assets are isolated
- release gate remains manifest-driven after deletion

## Frozen Test Assets

The remaining `22` test references are intentionally classified rather than accidental debt.

### Keep

```text
test_srp_runtime_legacy_compat.py
```

Reason:

- legacy compatibility evidence

### Review / Archive

```text
test_longbench_v2_prototype.py
```

Reason:

- historical prototype

## Validation Gate

Current commands:

```bash
python scripts/find_dependency_refs.py
python scripts/verify_release.py
```

Current status:

- PASS

## Deletion Policy

Deletion is a controlled release operation:

1. preserve provenance
2. remove dead dependency edges
3. execute deletion
4. rerun release verification

## Reading Path

Recommended reviewer order:

1. `PHASE_6_FINAL_CONSOLIDATION_SUMMARY.md`
2. `PHASE_6_PROGRESS_REPORT.md`
3. `PHASE_6_DELETION_READINESS.md`
4. `REPOSITORY_CONSOLIDATION_AUDIT.md`
5. `DELETE_MIGRATION_CHECKLIST.md`

This summary is the entry point for the frozen Phase 6 consolidation state.

