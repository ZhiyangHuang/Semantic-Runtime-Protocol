# LoCoMo Evidence Freeze Point

This note freezes the current LoCoMo real-validation chain as v1 empirical evidence.
It exists so that future selector changes, sample expansion, or additional transition types can be treated as a new evidence version rather than a silent modification of the current one.

## Frozen Inputs

- Dataset identifier: `LoCoMo`
- Physical source: `data/locomo/locomo10.json`
- Dataset version: `locomo10.json`
- Source hash: `553cd5a15e25f2ceccc6ed185221eba645080c93e5b91087560a91aa5961f365`
- Selection rule: `first_sample_covering_categories_1_2_3`
- Selected sample: `conv-26`
- Selected events: `temporal_refinement`, `unsupported_mutation`, `contradiction_update`

## Frozen Code Path

- Selector: `experiments/real_world_validation/locomo/selector.py`
- Adapter: `experiments/real_world_validation/locomo/adapter.py`
- Runner: `experiments/real_world_validation/locomo/runner.py`
- Baseline comparison: `experiments/real_world_validation/locomo/baseline.py`

## Frozen Bundles

Empirical bundle:

- `experiments/results/real_world_validation/locomo/run_20260718T0205264225340000`

Comparative bundle:

- `experiments/results/real_world_validation/locomo/baseline_comparison/run_20260718T0232070204050000`

## Frozen Reports

- [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md)
- [REAL_VALIDATION_FAILURE_ANALYSIS.md](REAL_VALIDATION_FAILURE_ANALYSIS.md)
- [REAL_VALIDATION_BASELINE_COMPARISON.md](REAL_VALIDATION_BASELINE_COMPARISON.md)
- [REAL_VALIDATION_SCIENTIFIC_REPORT.md](REAL_VALIDATION_SCIENTIFIC_REPORT.md)

## Freeze Boundary

The following changes should be treated as a new evidence version, not as edits to the frozen v1 chain:

- changing the LoCoMo selection rule
- adding or removing selected categories
- expanding beyond `conv-26`
- modifying the SRP or baseline decision rule
- altering the current artifact bundle without versioning a new run

## Interpretation

The freeze point marks the end of the current LoCoMo empirical evidence chain.
Future runs may extend it, but they should not overwrite it.
