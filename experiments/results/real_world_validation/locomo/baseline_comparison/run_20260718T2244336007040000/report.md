# LoCoMo Baseline Comparison Report

This report compares the SRP governed transition path against a direct-mutation baseline on the same selected LoCoMo slice.
It is a mechanism-comparison report, not a leaderboard report.

## 1. Purpose

The comparison asks whether governance boundaries prevent unsupported semantic mutations from being committed.
The baseline deliberately omits the SRP validation gate so the difference in mechanism is visible on the same slice.

## 2. Compared Mechanisms

| Mechanism | Pipeline | Governing gate | Rejection path |
| --- | --- | --- | --- |
| SRP | observation -> candidate transition -> evidence validation -> governance -> commit | yes | yes |
| Direct mutation baseline | observation -> immediate update -> commit | no | no |

## 3. Shared Evaluation Slice

- dataset: `LoCoMo`
- source: `C:\Users\ZhiyangHuang\Semantic-Runtime-Protocol\data\locomo\locomo10.json`
- selected sample id: `conv-26`
- selected events: `3`
- selection policy: `first_sample_covering_categories_1_2_3`

The same three transition records are evaluated under both mechanisms.

## 4. Metric Comparison

| Metric | SRP | Direct Mutation | Delta (Baseline - SRP) |
| --- | ---: | ---: | ---: |
| accepted transitions | `2` | `3` | `1` |
| rejected transitions | `1` | `0` | `-1` |
| invalid accept rate | `0.0` | `1.0` | `1.0` |
| unsupported mutation accepted | `False` | `True` | `1.0` |
| recommendation/execution separated | `True` | `False` | `-1` |
| replay consistency | `1.0` | `1.0` | `0.0` |
| memory accuracy | `1.0` | `0.666667` | `-0.333333` |
| relation accuracy | `1.0` | `0.666667` | `-0.333333` |
| fact accuracy | `1.0` | `0.666667` | `-0.333333` |

## 5. Case Table

| Sample | QA | Event | SRP Expected | SRP Actual | Baseline Actual | Result |
| --- | ---: | --- | --- | --- | --- | --- |
| `conv-26` | `0` | `temporal_refinement` | `accept` | `accept` | `accept` | `pass` |
| `conv-26` | `2` | `unsupported_mutation` | `reject` | `reject` | `accept` | `pass` |
| `conv-26` | `3` | `contradiction_update` | `accept` | `accept` | `accept` | `pass` |

## 6. Interpretation

- SRP rejects the unsupported mutation while preserving the governed boundary.
- The direct-mutation baseline accepts the unsupported mutation because it has no rejection gate.
- The comparison therefore attributes the error to mechanism design, not to scoring noise.

## 7. Relation to the Paper

This comparison supports the claim that governed transition control can block unsupported semantic updates.
It is a small comparative experiment, not a leaderboard result.
