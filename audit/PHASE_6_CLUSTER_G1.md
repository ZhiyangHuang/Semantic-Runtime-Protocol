# Phase 6 Cluster G1

## Scope

- Rehomed graph information gap analysis tooling to the live analysis package
- Rehomed semantic extraction audit tooling to the live analysis package
- Rehomed policy Pareto tooling to the live analysis package
- Removed legacy `srp_experiment/tmp` defaults from the wrapped tooling
- Kept runtime imports at zero

## Moved Or Rehomed

- `srp_experiment/run_graph_information_gap_analysis.py` -> `experiments.analysis.graph_information_gap_analysis`
- `srp_experiment/run_semantic_extraction_audit.py` -> `experiments.analysis.semantic_extraction_audit`
- `srp_experiment/run_policy_pareto_analysis.py` -> `experiments.analysis.policy_pareto`

## New Live Helpers

- `experiments/analysis/graph_information_gap_analysis.py`
- `experiments/analysis/semantic_extraction_audit.py`
- `experiments/analysis/policy_pareto.py`

## Validation

- `python scripts/find_dependency_refs.py`
- `python scripts/verify_release.py`
- `python -m compileall experiments/common experiments/analysis srp_experiment`

## Outcome

- `runtime_imports`: `0`
- `tooling_imports`: `21 -> 19`
