# Delete `docs/` and `srp_experiment/` Preparation

This document prepares the repository for a future removal of `docs/` and `srp_experiment/`.
It does not delete anything and it does not change the current scientific boundary.

## 1. Scope

The candidate removal targets are:

- `docs/`
- `srp_experiment/`

Current size snapshot:

- `docs/` contains `162` tracked files
- `srp_experiment/` contains `234` tracked files

## 2. Why These Paths Are Still Present

### `docs/`

The `docs/` tree currently stores historical research materials and archive notes.
It is still referenced by some audit documents, but it is no longer a hard release-gate dependency.

Current release-gate dependency:

- `scripts/verify_release.py` requires `audit/release_manifest.json` and `audit/provenance/README.md`

### `srp_experiment/`

The `srp_experiment/` tree is the frozen legacy experiment and evidence layer.
Some active evaluation code still imports helpers from it, so it is not yet safe to remove.

Current active imports:

- `experiments/evaluation/semantic_backend_comparison/local_model_backend.py`
- `experiments/evaluation/semantic_backend_comparison/vector_backend.py`
- `experiments/evaluation/phase_v_retention/metrics.py`
- `experiments/external_validation/baselines.py`
- `experiments/external_validation/evidence.py`

Test coverage also still references `srp_experiment/` extensively.

## 3. Deletion Blockers

Deletion is not safe until all of the following are true:

- `scripts/verify_release.py` no longer requires any path under `docs/`
- no active runtime or evaluation code imports `srp_experiment/`
- no tests import `srp_experiment/` as a live dependency
- any archive material currently under `docs/` has a new home
- the replacement home is itself referenced from audit or README guidance

## 4. Recommended Preparation Order

1. Freeze the current `v1` evidence chain and treat it as read-only.
2. Rehome archive documents from `docs/` into a non-deletion-sensitive location.
3. Replace the active `srp_experiment/` imports with active `srp_runtime/` or shared utility modules.
4. Keep `scripts/verify_release.py` manifest-driven so it does not depend on historical archive presence.
5. Update README and audit navigation so the new locations are discoverable.
6. Run the full verification and test suite.
7. Only then delete the old `docs/` and `srp_experiment/` trees.

## 5. Suggested Replacement Homes

The repository should choose a stable replacement home before deletion.
Possible patterns:

- archive material -> `audit/archive/`
- provenance material -> `artifacts/provenance/`
- shared runtime helpers -> `srp_runtime/` or a dedicated common utility package

The exact destination should be chosen before any deletion is attempted.

## 6. Audit Rule

Do not delete either tree until the replacement path is committed and the release check passes without the old directories.

This is the safest way to avoid destroying a frozen evidence chain while preparing the repository for a leaner v2 layout.
