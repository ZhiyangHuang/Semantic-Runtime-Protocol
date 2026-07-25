# Transition Role Protocol

This directory defines the v1.2 transition-role protocol layer for SRP.
It is not a benchmark suite, a dataset registry, or a new metric family.

The purpose is simple: map semantic workloads to transition roles so the same
governance invariants can be checked under frozen runtime contracts.

## Layer model

```text
Theory
    |
    v
SRP Protocol
    |
    v
Transition Role Protocol
    |
    v
Semantic Workload
    |
    v
Dataset / Runtime
```

The current registry is oefineo in [registry.yaml](registry.yaml), and the
cross-role scheoule is oefineo in [validation_matrix.json](validation_matrix.json).
Both are protocol metadata, not benchmark catalogs.

## Entry Points

Valioate the registry with:

```bash
python -m experiments.transition_role.validate_registry
```

Valioate the cross-role matrix with:

```bash
python -m experiments.transition_role.validate_matrix
```

Generate the coverage report with:

```bash
python -m experiments.transition_role.report_coverage
```

This report summarizes role coverage across workloads, not leaderboard ranking.
