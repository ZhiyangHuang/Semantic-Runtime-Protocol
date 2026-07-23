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
| Mean semantic coverage | `0.559689` |
| Mean semantic drift | `0.302338` |
| Mean fact accuracy | `0.743056` |
| Mean relation accuracy | `0.611111` |
| Mean recovery accuracy | `0.469614` |
| Mean closure accuracy | `0.527778` |
| Mean path preservation | `0.444444` |
| Mean neighborhood completeness | `0.706944` |
| Mean hallucinated relation rate | `0.220023` |
| Mean evidence cost | `1.47` |
| Hierarchy consistency rate | `1` |
| Governance consistency rate | `1` |

## 5. Encoder Summary

| Encoder | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2 | 0.572751 | 0.274815 | 0.62037 | 0.560185 |
| bge-base-en-v1.5 | 0.574735 | 0.291389 | 0.625 | 0.5625 |
| bge-small-en-v1.5 | 0.468254 | 0.410741 | 0.49537 | 0.358796 |
| e5-small-v2 | 0.623016 | 0.232407 | 0.703704 | 0.62963 |

## 6. Parser Summary

| Parser | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| hybrid_parser | 0.514881 | 0.358056 | 0.552083 | 0.463542 |
| llm_parser | 0.553571 | 0.307083 | 0.607639 | 0.532986 |
| rule_parser | 0.610615 | 0.241875 | 0.673611 | 0.586806 |

## 7. Mode Summary

| Mode | Coverage | Drift | Relation Acc. | Closure Acc. | Hallucinated Rel. |
| --- | --- | --- | --- | --- | --- |
| relation_closure | 0.696429 | 0.118055 | 0.829861 | 0.748264 | 0.0 |
| relation_expansion | 0.702381 | 0.198681 | 0.829861 | 0.748264 | 0.430903 |
| vector_only | 0.280258 | 0.590278 | 0.173611 | 0.086806 | 0.229167 |

## 8. Representation Summary

| Representation | Coverage | Drift | Relation Acc. | Closure Acc. |
| --- | --- | --- | --- | --- |
| all-MiniLM-L6-v2::hybrid_parser | 0.535714 | 0.327778 | 0.583333 | 0.541667 |
| all-MiniLM-L6-v2::llm_parser | 0.573413 | 0.262222 | 0.625 | 0.5625 |
| all-MiniLM-L6-v2::rule_parser | 0.609127 | 0.234444 | 0.652778 | 0.576389 |
| bge-base-en-v1.5::hybrid_parser | 0.480159 | 0.401389 | 0.486111 | 0.409722 |
| bge-base-en-v1.5::llm_parser | 0.573413 | 0.303056 | 0.611111 | 0.555556 |
| bge-base-en-v1.5::rule_parser | 0.670635 | 0.169722 | 0.777778 | 0.722222 |
| bge-small-en-v1.5::hybrid_parser | 0.444445 | 0.437778 | 0.472222 | 0.319444 |
| bge-small-en-v1.5::llm_parser | 0.420635 | 0.46 | 0.444445 | 0.305555 |
| bge-small-en-v1.5::rule_parser | 0.539682 | 0.334444 | 0.569444 | 0.451389 |
| e5-small-v2::hybrid_parser | 0.599206 | 0.265278 | 0.666667 | 0.583333 |
| e5-small-v2::llm_parser | 0.646825 | 0.203056 | 0.75 | 0.708333 |
| e5-small-v2::rule_parser | 0.623016 | 0.228889 | 0.694444 | 0.597222 |

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

Generated: `2026-07-23T01:50:11.031666+00:00`
