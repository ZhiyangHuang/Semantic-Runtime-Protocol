# Phase 6 Cluster F

## Scope

- Rehomed tool-facing coverage/decision attribution entrypoints to live analysis modules
- Repointed the mechanism attribution runner to the live mechanism-ablation implementation
- Kept runtime imports at zero

## Moved Or Rehomed

- `srp_experiment/run_mechanism_attribution_ablation.py` -> `experiments.mechanism_ablation.ablation_runner`
- `srp_experiment/run_coverage_attribution.py` -> `experiments.analysis.coverage_attribution`
- `srp_experiment/run_decision_attribution.py` -> `experiments.analysis.decision_attribution`

## New Live Helpers

- `experiments/common/chunking.py`
- `experiments/common/saliency.py`
- `experiments/analysis/semantic_snapshot.py`
- `experiments/analysis/semantic_delta.py`
- `experiments/analysis/stagewise_loss_matrix.py`
- `experiments/analysis/decision_trace.py`
- `experiments/analysis/coverage_attribution.py`
- `experiments/analysis/decision_attribution.py`

## Validation

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall experiments/common experiments/analysis srp_experiment`

## Outcome

- `runtime_imports`: `0`
- `tooling_imports`: `27 -> 24`

## Follow-Up

- Cluster F2 further reduced tooling imports to `21` by moving importance, policy, and semantic failure taxonomy tooling to the live analysis layer.
