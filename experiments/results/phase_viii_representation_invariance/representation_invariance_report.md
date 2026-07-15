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
| Encoders | `e5-small-v2, bge-small-en-v1.5, bge-base-en-v1.5, all-MiniLM-L6-v2` |
| Parsers | `rule_parser, hybrid_parser, llm_parser` |
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
| Case count | `144` |
| Mean semantic coverage | `0.673115` |
| Mean semantic drift | `0.159815` |
| Mean fact accuracy | `0.881945` |
| Mean relation accuracy | `0.765046` |
| Mean recovery accuracy | `0.610566` |
| Mean closure accuracy | `0.708912` |
| Mean path preservation | `0.652778` |
| Mean neighborhood completeness | `0.703819` |
| Mean hallucinated relation rate | `0.093056` |
| Mean evidence cost | `1.47` |
| Hierarchy consistency rate | `1` |
| Governance consistency rate | `1` |

## 5. Encoder Summary

| Encoder | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2 | 0.67791 | 0.155926 | 0.763889 | 0.715278 |
| bge-base-en-v1.5 | 0.67791 | 0.153055 | 0.773148 | 0.719907 |
| bge-small-en-v1.5 | 0.650132 | 0.186481 | 0.722222 | 0.666667 |
| e5-small-v2 | 0.686508 | 0.143796 | 0.800926 | 0.733796 |

## 6. Parser Summary

| Parser | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| hybrid_parser | 0.68254 | 0.149861 | 0.784722 | 0.725694 |
| llm_parser | 0.657242 | 0.175555 | 0.736111 | 0.680556 |
| rule_parser | 0.679563 | 0.154028 | 0.774306 | 0.720486 |

## 7. Mode Summary

| Mode | Coverage | Drift | Relation Acc. | Closure Acc. | Hallucinated Rel. |
| --- | --- | --- | --- | --- | --- |
| relation_closure | 0.802579 | 0.006944 | 0.989583 | 0.984375 | 0.0 |
| relation_expansion | 0.802579 | 0.062778 | 0.989583 | 0.984375 | 0.279167 |
| vector_only | 0.414186 | 0.409722 | 0.315972 | 0.157986 | 0.0 |

## 8. Representation Summary

| Representation | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2::hybrid_parser | 0.68254 | 0.151389 | 0.777778 | 0.722222 |
| all-MiniLM-L6-v2::llm_parser | 0.668651 | 0.165 | 0.736111 | 0.701389 |
| all-MiniLM-L6-v2::rule_parser | 0.68254 | 0.151389 | 0.777778 | 0.722222 |
| bge-base-en-v1.5::hybrid_parser | 0.68254 | 0.148333 | 0.791667 | 0.729167 |
| bge-base-en-v1.5::llm_parser | 0.680555 | 0.145833 | 0.777778 | 0.722222 |
| bge-base-en-v1.5::rule_parser | 0.670635 | 0.165 | 0.75 | 0.708333 |
| bge-small-en-v1.5::hybrid_parser | 0.68254 | 0.151389 | 0.777778 | 0.722222 |
| bge-small-en-v1.5::llm_parser | 0.585317 | 0.256667 | 0.611111 | 0.555556 |
| bge-small-en-v1.5::rule_parser | 0.68254 | 0.151389 | 0.777778 | 0.722222 |
| e5-small-v2::hybrid_parser | 0.68254 | 0.148333 | 0.791667 | 0.729167 |
| e5-small-v2::llm_parser | 0.694444 | 0.134722 | 0.819444 | 0.743056 |
| e5-small-v2::rule_parser | 0.68254 | 0.148333 | 0.791667 | 0.729167 |

## 9. Representation Analysis

To evaluate representation invariance, we additionally report two SRP-specific analysis metrics:

### 8.1 Hierarchy Consistency Rate

Hierarchy Consistency Rate (HCR) measures whether the recovery ordering remains intact under a representation setting.
The per-representation HCR values are summarized below.

| Representation | HCR | GCR |
| --- | --- | --- |
| all-MiniLM-L6-v2::hybrid_parser | 1 | 1 |
| all-MiniLM-L6-v2::llm_parser | 1 | 1 |
| all-MiniLM-L6-v2::rule_parser | 1 | 1 |
| bge-base-en-v1.5::hybrid_parser | 1 | 1 |
| bge-base-en-v1.5::llm_parser | 1 | 1 |
| bge-base-en-v1.5::rule_parser | 1 | 1 |
| bge-small-en-v1.5::hybrid_parser | 1 | 1 |
| bge-small-en-v1.5::llm_parser | 1 | 1 |
| bge-small-en-v1.5::rule_parser | 1 | 1 |
| e5-small-v2::hybrid_parser | 1 | 1 |
| e5-small-v2::llm_parser | 1 | 1 |
| e5-small-v2::rule_parser | 1 | 1 |

### 8.2 Governance Consistency Rate

Governance Consistency Rate (GCR) measures whether the governance pipeline and parameter semantics remain unchanged across representation variants.

The parameter semantics are evaluated qualitatively according to predefined functional-role definitions rather than optimized numerically.

## 10. Interpretation

The representation experiment evaluates whether SRP preserves its recovery hierarchy and governance semantics under encoder and parser changes.
The report does not claim identical absolute performance across representations.

## 11. Relation to the Paper

Phase VIII-B extends the paper's evidence chain by testing whether SRP's recovery hierarchy preserves its relative ordering under representation changes.

Generated: `2026-07-14T21:56:13.492264+00:00`
