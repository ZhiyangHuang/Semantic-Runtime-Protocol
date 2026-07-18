# Phase 6 Deletion Readiness Audit

This audit documents whether the repository is ready to delete the legacy trees without losing live behavior, provenance, or release verification.

It does not authorize deletion by itself.
It records the current state of deletion readiness and the remaining preservation boundaries.

## 1. Scope

The deletion candidates are:

- `docs/`
- `srp_experiment/`

The audit distinguishes:

- live code that must remain
- frozen compatibility assets that may be preserved
- historical or prototype artifacts that may be archived
- hard dependencies that still block deletion

## 2. Current Readiness Summary

### `srp_experiment/`

Status: `core delete candidate, frozen compatibility surface preserved`

Current findings:

- runtime imports are gone
- tooling imports are gone
- live experiment code no longer depends on `srp_experiment/`
- the remaining references are frozen test assets, compatibility assets, or historical prototype material

Readiness assessment:

- core implementation: ready to delete once preserved assets are isolated
- compatibility test surface: preserve until deletion boundary is approved
- historical prototype surface: archive or retire after provenance review

### `docs/`

Status: `release gate decoupled; archive shell retired`

Current findings:

- `scripts/verify_release.py` now requires `audit/release_manifest.json` and `audit/provenance/README.md`
- archive material still lives under `audit/provenance/docs_archive/`
- current references are provenance-only from the release gate perspective

Readiness assessment:

- archive tree: provenance copy is preserved; old shell has been retired
- release verification: independent of legacy archive paths

## 3. Deletion Decision Matrix

| Path | Current Status | Decision | Notes |
| --- | --- | --- | --- |
| `srp_experiment/` core implementation | legacy, no live runtime/tooling edges | delete candidate | delete only after compatibility assets are isolated |
| `srp_experiment/tests/legacy` | frozen compatibility asset | preserve | keeps deletion boundary auditable |
| `srp_experiment/tests/prototype` | historical prototype asset | archive / retire | depends on provenance review |
| `audit/provenance/docs_archive/` | historical archive material | preserved provenance | no longer a release gate dependency |
| audit records | governance evidence | preserve | part of the release trail |

## 4. Readiness Checks

### `srp_experiment/`

| Item | Status |
| --- | --- |
| runtime imports | PASS |
| tooling imports | PASS |
| active experiment dependency | PASS |
| tests classified | PASS |
| compatibility boundary documented | PASS |

### `docs/`

| Item | Status |
| --- | --- |
| release verification no longer hardcodes archive path | PASS |
| archive references rehomed or retired | PASS |
| provenance preserved in audit trail | PASS |

## 5. Preservation Rules

The following assets should not be deleted just to satisfy a count:

- `test_srp_runtime_legacy_compat.py`
- `test_longbench_v2_prototype.py`
- audit documents that explain the frozen v1 evidence chain

These assets are valuable only if they remain clearly labeled as frozen or historical.

## 6. Decision Boundary

Deletion is ready only when:

- the live dependency graph has no arrows into the legacy trees
- the release gate is manifest-driven and no longer requires `audit/provenance/docs_archive/README.md`
- the archive content is preserved under `audit/provenance/docs_archive/`
- frozen compatibility assets are isolated from live dependency checks
- historical prototypes are either archived or explicitly retained as provenance

At the moment, the repository is ready for deletion planning, not for deletion execution.

