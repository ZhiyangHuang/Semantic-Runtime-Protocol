# SRP Phase VIII-B Representation Invariance Report

This report freezes the Phase VIII-B representation-invariance evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a new mechanism design.

## 1. Purpose

Phase VIII-B evaluates whether SRP preserves its governance semantics under representation changes.
The study uses standard recovery metrics plus SRP-specific analysis metrics to test whether the recovery hierarchy remains stable when encoder and parser choices change.

## 2. Frozen Scope

| Setting | Value |
| --- | --- |
| Phase | `phase_viii_representation_invariance` |
| Evaluation mode | `representation_invariance` |
| Encoders | `toy-e5` |
| Parsers | `rule_parser` |
| Recovery modes | `vector_only, relation_expansion, relation_closure` |
| Baseline top_k | `2` |
| Baseline relation depth | `1` |
| Baseline closure validation | `True` |

The protocol keeps the semantic workloads, recovery hierarchy, governance rules, and evaluation metrics fixed.
Only the representation layer changes across tracks.

## 3. Metrics Schema

- Schema version: `phase_viii_representation_invariance_metrics_schema.v1`
- Coverage definition: matched semantic units divided by original semantic units
- Drift definition: weighted combination of fact drift, relation drift, and hallucinated relation rate
- Hierarchy definition: rank consistency of relation_closure, relation_expansion, and vector_only
- Governance definition: qualitative preservation of parameter roles and governance pipeline
- Evidence cost definition: scalar cost attached to the recovery case

## 4. Summary

| Metric | Value |
| --- | ---: |
| Case count | `12` |
| Mean semantic coverage | `0.539682` |
| Mean semantic drift | `0.308333` |
| Mean fact accuracy | `0.694445` |
| Mean relation accuracy | `0.611111` |
| Mean recovery accuracy | `0.458123` |
| Mean closure accuracy | `0.472222` |
| Mean path preservation | `0.333333` |
| Mean neighborhood completeness | `0.670833` |
| Mean hallucinated relation rate | `0.152778` |
| Mean evidence cost | `1.47` |
| Hierarchy consistency rate | `1` |
| Governance consistency rate | `1` |

## 5. Encoder Summary

| Encoder | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| toy-e5 | 0.539682 | 0.308333 | 0.611111 | 0.472222 |

## 6. Parser Summary

| Parser | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| rule_parser | 0.539682 | 0.308333 | 0.611111 | 0.472222 |

## 7. Mode Summary

| Mode | Coverage | Drift | Relation Acc. | Closure Acc. | Hallucinated Rel. |
| --- | --- | --- | --- | --- | --- |
| relation_closure | 0.666666 | 0.15 | 0.791667 | 0.645833 | 0.0 |
| relation_expansion | 0.666666 | 0.241667 | 0.791667 | 0.645833 | 0.458333 |
| vector_only | 0.285714 | 0.533333 | 0.25 | 0.125 | 0.0 |

## 8. Representation Summary

| Representation | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| toy-e5::rule_parser | 0.539682 | 0.308333 | 0.611111 | 0.472222 |

## 9. Representation Analysis

To evaluate representation invariance, we additionally report two SRP-specific analysis metrics:

### 8.1 Hierarchy Consistency Rate

Hierarchy Consistency Rate (HCR) measures whether the recovery ordering remains intact under a representation setting.
The per-representation HCR values are summarized below.

| Representation | HCR | GCR |
| --- | --- | --- |
| toy-e5::rule_parser | 1 | 1 |

### 8.2 Governance Consistency Rate

Governance Consistency Rate (GCR) measures whether the governance pipeline and parameter semantics remain unchanged across representation variants.

The parameter semantics are evaluated qualitatively according to predefined functional-role definitions rather than optimized numerically.

## 10. Interpretation

The representation experiment evaluates whether SRP preserves its recovery hierarchy and governance semantics under encoder and parser changes.
The report does not claim identical absolute performance across representations.

## 11. Relation to the Paper

Phase VIII-B extends the paper's evidence chain by testing whether SRP's recovery hierarchy preserves its relative ordering under representation changes.

Generated: `2026-07-14T22:35:58.865626+00:00`
