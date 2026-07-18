# Phase 6 Cluster E

This batch closed the final `P0` runtime-import blocker for `srp_experiment/`.

## Scope

Remaining runtime blockers before this batch:

- `srp_experiment/mechanism_ablation/ablation_runner.py`
- `srp_experiment/mechanism_ablation/variants/common.py`

## Resolution

The mechanism-ablation implementation was moved to the live layer:

- `experiments/mechanism_ablation/common.py`
- `experiments/mechanism_ablation/ablation_config.py`
- `experiments/mechanism_ablation/ablation_metrics.py`
- `experiments/mechanism_ablation/ablation_comparison.py`
- `experiments/mechanism_ablation/ablation_report.py`
- `experiments/mechanism_ablation/ablation_runner.py`
- `experiments/mechanism_ablation/variants/`

Legacy mechanism-ablation entrypoints were reduced to thin wrappers.

## Validation

- `python -m compileall experiments\\mechanism_ablation srp_experiment\\mechanism_ablation`
- `python scripts\\find_dependency_refs.py`
- `python scripts\\verify_release.py`
- `python -m unittest srp_experiment.tests.test_mechanism_attribution_ablation`

## Result

Current dependency status after this batch:

- `runtime_imports`: `0`
- `tooling_imports`: `27`
- `test_imports`: `87`

The live graph no longer points to `srp_experiment/` through runtime imports.

