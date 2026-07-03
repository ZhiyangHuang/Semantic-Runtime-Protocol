# Cleanup Review Manifest

This manifest records what was physically changed in the current cleanup-review pass.

## Moved

- `temporary1.md` -> `docs/cleanup_review/temporary1.md`
- `temporary2.md` -> `docs/cleanup_review/temporary2.md`

## Added

- `docs/cleanup_review/README.md`
- `docs/cleanup_review/temporary3.md`
- `docs/cleanup_review/CLEANUP_REVIEW_MANIFEST.md`

## Deleted

- all `srp_experiment/**/__pycache__/` directories

## Not Deleted On Purpose

- formal evidence in `srp_experiment/results/`
- archive namespaces
- canonical configs
- canonical entrypoints
- benchmark provenance files
- Python source files with execution, audit, diagnostic, or import logic
- reproducibility-layer files and audit outputs

## Review Exit

If the cleanup is accepted, this folder can be removed in one step.
