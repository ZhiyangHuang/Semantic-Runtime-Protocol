# SRP Legacy Extraction Candidates

This document records modules in `srp_experiment/` that may become candidates for future extraction or consolidation.

It is not a migration plan and it does not authorize code movement.
The purpose is to reduce semantic confusion by making potential extraction boundaries explicit.

## Scope

The candidates listed here were identified during the Phase 3 legacy boundary hardening review.
They are intentionally kept as candidates only.

## Candidate Modules

| Module | Current Role | Future Possibility | Decision |
| --- | --- | --- | --- |
| `srp_experiment.local_llm` | Evaluation backend and local model client helper | Possible move to a shared evaluation/backend utility layer | Keep frozen for now |
| `srp_experiment.srp.encoder` | Shared semantic similarity and encoding utility | Possible extraction into a common helper module | Keep frozen for now |
| `srp_experiment.srp.semantic_parser` | Experiment helper for semantic normalization | Possible extraction if parsing utilities are formalized elsewhere | Keep frozen for now |
| `srp_experiment.srp.llm_judge` | Evaluation component for evidence judgment | Likely to remain outside the active runtime boundary | Keep frozen for now |

## Interpretation

These modules are not being removed in the current phase.
They are preserved because:

- they still support historical reproducibility
- they still support evaluation and evidence generation
- they are already part of the frozen legacy evidence layer

## Non-Goals

This document does not:

- move code between directories
- rewrite imports
- change runtime semantics
- remove legacy evaluation support

## Boundary Reminder

```text
srp_runtime
    active source of truth

srp_experiment
    frozen legacy evidence layer

experiments
    current evidence generation layer
```

Any future extraction should be evaluated separately and should not be treated as an automatic cleanup task.

