# Phase 6.5-B3 `srp_experiment/` Implementation Removal

This checkpoint freezes the last migrated implementation surface inside `srp_experiment/` and removes only the duplicate implementation files that now have live owners.

It does not remove compatibility assets.
It does not remove frozen tests.
It only removes implementation modules and wrappers that have already been rehomed.

## Scope

### Delete candidates

The following migrated implementation areas are scheduled for removal:

- `srp_experiment/analysis/`
- `srp_experiment/mechanism_ablation/`
- `srp_experiment/eval/`
- top-level migrated wrappers and helper entrypoints that now have live replacements in `experiments/`

### Completed removals

The following implementation surfaces have already been retired in this batch:

- `srp_experiment/analysis/`
- `srp_experiment/mechanism_ablation/`
- `srp_experiment/eval/`
- top-level migrated wrappers and helper entrypoints other than the frozen compatibility export surface

### Preserve

The following assets remain as frozen compatibility or historical assets:

- `srp_experiment/budgeting.py`
- `srp_experiment/prompting.py`
- `srp_experiment/eval/`
- `srp_experiment/srp/`
- `srp_experiment/data/longbench_v2/`
- `srp_experiment/export_csv.py`
- `srp_experiment/tests/`

## Preconditions

- `runtime_imports = 0`
- `tooling_imports = 0`
- live analysis and mechanism-ablation code already exist under `experiments/`
- frozen compatibility tests remain classified and tracked in audit docs

## Action

Remove the migrated implementation surface from `srp_experiment/` while preserving the compatibility surface.

## Verification

Run:

```bash
python scripts/find_dependency_refs.py
python scripts/verify_release.py
python -m compileall experiments srp_experiment
```

Expected:

- active runtime dependency = 0
- active tooling dependency = 0
- release gate = PASS
