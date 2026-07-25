# Semantic Runtime Protocol

This is the single root entry point for the repository.

## Start Here

1. [paper/SRP_MANUSCRIPT_V1.md](paper/SRP_MANUSCRIPT_V1.md)
1. [paper/SRP_MAIN_RESULTS_SUMMARY_V1.md](paper/SRP_MAIN_RESULTS_SUMMARY_V1.md)
1. [paper/docs/release/README.md](paper/docs/release/README.md)
1. [paper/docs/release/EVIDENCE_SURFACE.md](paper/docs/release/EVIDENCE_SURFACE.md)
1. [paper/docs/README.md](paper/docs/README.md)
1. [STFB/README.md](STFB/README.md)

## Current Release

The current frozen release surface is centered on the release review and evidence surface:

- [paper/docs/release/README.md](paper/docs/release/README.md)

The release gate is checked with:

```text
python scripts/verify_release.py
```

## Repository Layout

- [paper/](paper/) contains the manuscript and release-facing paper summaries.
- [paper/docs/release/](paper/docs/release/) contains the release review and evidence surface.
- [paper/docs/evidence/](paper/docs/evidence/) contains evidence bundles and release-facing evidence notes.
- [paper/docs/plans/](paper/docs/plans/) contains the active specs and roadmap notes.
- [configs/](configs/) contains frozen runtime values and consolidation notes.
- [STFB/](STFB/) contains the benchmark and reproduction package.
- [experiments/](experiments/) contains the executable evaluation and validation code.
- [data/](data/) contains registry-backed source data used by the validation code.
- [configs/root.env](configs/root.env) contains the default local runtime values.

## Evidence Surface

The canonical benchmark summaries are now folded into [paper/docs/release/EVIDENCE_SURFACE.md](paper/docs/release/EVIDENCE_SURFACE.md).

Current benchmark family status:

- `MMLU v3`: authoritative MMLU artifact
- `ARC v1`: authoritative ARC artifact
- `LongMemEval v5`: authoritative bridge artifact with external-validation separation preserved
- `HumanEval full`: closed and ready for release evidence review

The evidence surface also records the main support layers:

- mechanism validation
- external transition validation
- broad capability stress evaluation

## Planning Surface

Active planning and protocol docs live under [paper/docs/plans/](paper/docs/plans/):

- [paper/docs/plans/STFB_SPEC.md](paper/docs/plans/STFB_SPEC.md)
- [paper/docs/plans/STFB_ROADMAP.md](paper/docs/plans/STFB_ROADMAP.md)
- [paper/docs/plans/GOVERNANCE_PLAN.md](paper/docs/plans/GOVERNANCE_PLAN.md)

## Transition Role Checks

The transition-role protocol validation pair is part of the release gate:

- [experiments/transition_role/validate_registry.py](experiments/transition_role/validate_registry.py)
- [experiments/transition_role/validate_matrix.py](experiments/transition_role/validate_matrix.py)

## Release Snapshots

Two phase-viii summary snapshots were previously carried at the repository root and are now folded into this entry page:

- Representation invariance snapshot:
  - cases evaluated: `144`
  - mean semantic coverage: `0.559689`
  - mean semantic drift: `0.302338`
  - hierarchy consistency rate: `1`
  - governance consistency rate: `1`
- Implementation independence snapshot:
  - cases evaluated: `36`
  - mean semantic coverage: `0.623016`
  - mean semantic drift: `0.220833`
  - hierarchy consistency rate: `1`
  - governance consistency rate: `1`

## Notes

- The root directory is intentionally kept small.
- Historical surface notes and phase summaries are folded into this page or into the release docs under [paper/docs/release/](paper/docs/release/).
- If a detail is missing here, it should usually live in the release surface rather than as a separate root-level markdown file.
