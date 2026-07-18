# SRP Experiment Layer

`srp_experiment/` is the legacy experiment and evidence layer for SRP.

It is retained for historical reproducibility, audit traceability, and compatibility with earlier release artifacts.

## Status

- Legacy evidence layer: yes
- Active runtime source of truth: no
- New runtime development target: no

## Responsibilities

This directory may contain:

- historical experiment implementations
- legacy harnesses and adapters
- reproducibility utilities
- evidence-generation helpers for older release snapshots

This directory does not define the current SRP runtime.

The active runtime implementation belongs in `srp_runtime/`.

## Development Rule

New runtime behavior should not be added here.

If a change affects the current protocol semantics, transition governance, or active runtime contract, it should be implemented in `srp_runtime/` and evaluated through `experiments/`.

## Retention Reason

`srp_experiment/` remains in the repository so that:

- historical evidence can still be inspected
- older artifacts can be reproduced or explained
- legacy release snapshots remain understandable

## Boundary Reminder

```text
srp_runtime
    current implementation

srp_experiment
    historical implementation and evidence layer
```

The distinction is intentional and should remain visible in release governance documents.

