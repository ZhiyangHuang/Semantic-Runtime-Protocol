# SRP Phase VII Parameter Sensitivity and Stability Report

This report freezes the Phase VII-A parameter-stability evidence package for SRP.
It is an evaluation report, not a calibration artifact and not a runtime optimization artifact.

## 1. Purpose

Phase VII-A measures whether governed recommendations remain stable under repeated evaluation with frozen workload, objective, and evidence backend.

## 2. Frozen Protocol

| Setting | Value |
| --- | --- |
| Phase | `phase_vii_parameter_stability` |
| Workload | `phase_vi_relation_recovery_mvp` |
| Objective | `governed_reconstruction` |
| Evidence backend | `relation_closure` |
| Seeds | `11, 23, 37, 41, 53, 67, 71, 83, 97, 101` |
| Baseline activation threshold | `0.9` |
| Baseline recovery minimum evidence | `1` |
| Baseline objective value | `0.54` |

The protocol keeps workload, objective, and evidence backend fixed.
Only the evaluation seed changes across runs.

## 3. Stability Metrics

| Metric | Value |
| --- | ---: |
| Run count | `10` |
| Recommendation consistency | `1.0` |
| Activation threshold variance | `0.0` |
| Recovery min evidence variance | `0` |
| Objective value variance | `0.0` |
## 4. Interpretation

The baseline protocol is intended to expose whether the governed recommendation is stable rather than arbitrary.
It does not claim a universally optimal configuration.

## 5. Relation to the Paper

Phase VII extends the evidence chain by checking whether the Phase VI-A recovery setting yields stable recommendations under repeated evaluation.

Generated: `2026-07-14T20:11:32.847356+00:00`
