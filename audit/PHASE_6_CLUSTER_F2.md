# Phase 6 Cluster F2

## Scope

- Rehomed three pure analysis entrypoints to the live analysis package
- Removed legacy `srp_experiment/tmp` defaults from the wrapped tooling
- Kept runtime imports at zero

## Moved Or Rehomed

- `srp_experiment/run_importance_attribution.py` -> `experiments.analysis.importance_attribution`
- `srp_experiment/run_policy_attribution.py` -> `experiments.analysis.policy_attribution`
- `srp_experiment/run_semantic_failure_taxonomy.py` -> `experiments.analysis.semantic_failure_taxonomy`

## New Live Helpers

- `experiments/analysis/importance_trace.py`
- `experiments/analysis/policy_trace.py`
- `experiments/analysis/importance_attribution.py`
- `experiments/analysis/policy_attribution.py`
- `experiments/analysis/semantic_failure_taxonomy.py`
- `experiments/common/semantic_text.py` now provides `stable_semantic_object_id`

## Validation

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall experiments/common experiments/analysis srp_experiment`

## Outcome

- `runtime_imports`: `0`
- `tooling_imports`: `24 -> 21`

## Follow-Up

- Cluster G1 further reduced tooling imports by moving graph information gap analysis, semantic extraction audit tooling, and policy Pareto tooling to the live analysis layer.
