# SRP Phase II Boundary Validation Report

This report freezes the Phase II boundary validation evidence package for SRP.
It is a validation report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

Phase II boundary validation verifies that SRP can identify feasible semantic evolution regions and preserve boundary stability under controlled runtime variation.

It answers:

> Where can semantic evolution remain governed without crossing authority boundaries?

## 2. Experimental Boundary

The runtime baseline is frozen by [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

The validation layer does not change:

- runtime execution
- authority boundaries
- optimization objectives
- evidence routing rules

## 3. Validation Evidence

The current Phase II boundary package includes:

- 16 boundary-stability observations
- 32 closure validation observations
- 4 validated boundary classes
- machine-readable candidate export under `experiments/results/phase_ii_boundary/`
- `candidate_results.csv` for the Phase II to Phase III-A handoff
- `feasible_region.json` for the validated feasible-region summary
- `metadata.json` for reproducibility and provenance
- `figures/feasible_heatmap.pdf` and `figures/feasible_heatmap.png` for paper use
- `figures/coverage_summary.pdf` and `figures/coverage_summary.png` for paper use

Validated boundary classes:

- semantic mutation boundary
- evidence acceptance boundary
- history preservation boundary
- archive enrichment boundary

## 4. Boundary Stability

The validation package checks:

- replay equivalence
- state transition equivalence
- authority preservation
- evidence consistency

The frozen regions remain valid under controlled variation in:

- workload pressure
- conflict density
- evidence volume

## 5. Result Interpretation

The key result is not that SRP finds the best parameter values.
The key result is that SRP identifies a governed region in which later optimization may operate.

The candidate export makes the boundary result directly consumable by Phase III-A rather than requiring manual transcription.
The figure export provides a heatmap and coverage summary that can be cited directly in the paper.

## 6. Relation to the Paper

This report supports the paper's boundary-validation claim and provides the paper-facing evidence layer for Phase II.

For the auditable record, see [SRP Phase II Validation Appendix](SRP_PHASE_II_VALIDATION_APPENDIX.md).
