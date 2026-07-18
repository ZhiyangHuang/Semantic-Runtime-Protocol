# Delete Migration Checklist

This checklist turns the future removal of `docs/` and `srp_experiment/` into a deletion-readiness plan.
It is a working checklist, not a claim, not an experiment result, and not a deletion instruction.

## 1. Goal

Remove the dependency arrows before removing the directories.

Target directories:

- `docs/`
- `srp_experiment/`

## 2. Current Blocking Dependencies

Priority order:

- `P0`: runtime imports
- `P1`: tooling imports
- `P2`: test imports
- `P3`: markdown, audit, and historical references

Deletion readiness rule:

- `P0` and `P1` must reach zero before deletion is allowed
- `P2` must be classified into live, legacy compatibility, or historical/prototype assets
- any intentionally preserved `P2` surface must be frozen and isolated from live dependency checks
- `P3` may remain after live dependency cleanup

Current scan status:

- `P0 runtime_imports`: `0`
- `P1 tooling_imports`: `0`
- `P2 test_imports`: `22`

### `docs/`

Blocking dependencies:

- `scripts/verify_release.py` now requires `audit/release_manifest.json` and `audit/provenance/README.md`

Non-blocking references:

- `README.md`
- `audit/README.md`
- `audit/PAPER_SOURCE_REFERENCE_AUDIT.md`
- archive documents under `audit/provenance/docs_archive/`

### `srp_experiment/`

Blocking dependencies:

- the remaining live blockers are now frozen test/prototype references that must be classified before deletion

Non-blocking references:

- audit documents that describe `srp_experiment/` as frozen legacy evidence
- archive documents that mention historical implementation paths
- explicitly preserved compatibility tests and historical prototypes

## 3. Dependency Elimination Tasks

| Status | Task | Blocking | Done |
| --- | --- | --- | --- |
| [x] | Generate a full dependency report for `docs/` and `srp_experiment/` references | Yes |  |
| [x] | Replace `scripts/verify_release.py` hardcoded `audit/provenance/docs_archive/README.md` dependency with audit manifest | Yes |  |
| [ ] | Relocate or retire archive documents that still live under `docs/` | Yes |  |
| [x] | Replace `P0` runtime imports from `srp_experiment` in `experiments/` | Yes |  |
| [x] | Replace `P1` tooling imports from `srp_experiment` in scripts and generators | Yes |  |
| [ ] | Classify remaining `P2` test imports into keep, archive, or retire buckets | Yes |  |
| [ ] | Move approved live-behavior tests off `srp_experiment` imports where a live replacement exists | Yes |  |
| [ ] | Preserve explicitly approved legacy compatibility tests as frozen assets | No |  |
| [ ] | Archive or retire historical prototypes that no longer support the live evidence chain | No |  |
| [ ] | Replace `srp_experiment` imports in `experiments/external_validation/` | Yes |  |
| [ ] | Update README guidance to stop pointing at the old directories as required runtime inputs | No |  |
| [ ] | Update audit navigation to point at the replacement homes | No |  |
| [ ] | Run release verification without requiring the old directories | Yes |  |
| [ ] | Run the relevant test suite after dependency removal | Yes |  |
| [ ] | Commit the import removals before deleting directories | Yes |  |
| [ ] | Delete `docs/` only after the tree is dependency-free | Yes |  |
| [ ] | Delete `srp_experiment/` only after the tree is dependency-free | Yes |  |

## 4. Suggested Execution Order

1. Generate the dependency report.
2. Remove `P0` runtime imports.
3. Remove `P1` tooling imports.
4. Classify and freeze the remaining `P2` test assets.
5. Update release verification.
6. Re-run verification and tests.
7. Delete or rehome `docs/` once archive dependencies are gone.
8. Delete the core `srp_experiment/` implementation once preserved compatibility assets are isolated.

## 5. Acceptance Criteria

The deletion-readiness audit is complete only when all of the following are true:

- no `P0` runtime imports remain
- no `P1` tooling imports remain
- no unclassified `P2` test imports remain
- any remaining legacy test references are explicitly approved, isolated, and frozen
- no release script hardcodes `docs/`
- the dependency report is empty or reduced to non-blocking archive mentions
- verification passes with the deletion boundary documented and the live dependency graph clean

## 6. Notes

The repository should treat this as a dependency elimination exercise, not as a bulk deletion exercise.
The right question is whether any live arrow still points to the legacy directories.

