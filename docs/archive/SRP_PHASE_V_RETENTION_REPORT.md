# SRP Phase V Retention and Drift Evaluation

This report freezes the Phase V semantic retention and drift evidence package for SRP.
It is an evaluation report, not a calibration artifact and not a runtime optimization artifact.

## 1. Purpose

Phase V measures semantic fidelity after governed transition. It evaluates whether semantic coverage and semantic drift can be measured at the meaning level rather than only at the parameter level.

## 2. Frozen Protocol

| Setting | Value |
| --- | --- |
| Phase | `phase_v_retention` |
| Evaluation mode | `retention_drift` |
| Baseline activation threshold | `0.5` |
| Baseline recovery minimum evidence | `1` |
| Baseline preserve evidence | `False` |
| Baseline archive relations | `False` |

The protocol keeps workload, objective, and evidence backend fixed.
Only the retention-related settings are interpreted as evaluation axes.

## 3. Metrics Schema

- Schema version: `phase_v_retention_metrics_schema.v1`
- Coverage definition: matched semantic units divided by original semantic units
- Drift definition: weighted combination of fact drift, relation drift, and confidence drift
- Drift weights: `(0.45, 0.45, 0.1)`
- Recovery definition: matched semantic units divided by union of original and recovered units
- Evidence cost definition: scalar cost attached to the transition case

## 4. Single-Transition Output Fields

| Field | Meaning |
| --- | --- |
| `semantic_coverage` | Recall-like preserved meaning fraction |
| `semantic_drift` | Weighted semantic loss over facts, relations, and confidence |
| `fact_accuracy` | Fraction of original facts recovered |
| `relation_accuracy` | Fraction of original relations recovered |
| `recovery_accuracy` | Jaccard-like fidelity over original and recovered semantic units |
| `evidence_cost` | Cost attached to the transition case |

## 5. Experimental Cases

- Case count: `4`
- Category counts: `{'exact_preservation': 1, 'fact_loss': 1, 'relation_drift': 1, 'boundary_hallucination': 1}`

## 6. Summary

| Metric | Value |
| --- | ---: |
| Mean semantic coverage | `0.8375` |
| Mean semantic drift | `0.1985` |
| Mean fact accuracy | `0.9375` |
| Mean relation accuracy | `0.625` |
| Mean recovery accuracy | `0.766667` |
| Mean evidence cost | `1.375` |
| Total missing units | `3` |
| Total hallucinated units | `2` |
| Coverage range | `0.75` .. `1.0` |
| Drift range | `0.0` .. `0.45` |
| Recovery accuracy range | `0.6` .. `1.0` |

## 7. Per-Case Results

| Case | Category | Coverage | Drift | Fact Acc. | Relation Acc. | Recovery Acc. | Evidence Cost |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `retention_case_1_exact` | `exact_preservation` | `1.0` | `0.0` | `1.0` | `1.0` | `1.0` | `1.0` |
| `retention_case_2_fact_loss` | `fact_loss` | `0.8` | `0.119` | `0.75` | `1.0` | `0.8` | `1.2` |
| `retention_case_3_relation_drift` | `relation_drift` | `0.75` | `0.45` | `1.0` | `0.0` | `0.6` | `1.5` |
| `retention_case_4_boundary_hallucination` | `boundary_hallucination` | `0.8` | `0.225` | `1.0` | `0.5` | `0.666667` | `1.8` |

## 8. Interpretation

The baseline protocol is intended to expose the tradeoff surface between semantic coverage and semantic stability. It does not claim a universally optimal retention setting.

## 9. Limitations

- The case suite is intentionally small and frozen
- The current report is a single baseline protocol, not a parameter sweep
- The metrics are meaning-level unit matching, not raw text overlap

## 10. Relation to the Paper

Phase V extends the paper's evidence chain with semantic fidelity measurement after governed transition, complementing observability, boundary validation, governed optimization, and evidence escalation.

Generated: `2026-07-14T19:21:09.111473+00:00`
