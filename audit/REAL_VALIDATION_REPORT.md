# Real Validation Report

This report is the reviewer-facing entry point for the real-validation branch.
It summarizes what the current LoCoMo slice validates, what it does not validate, and where the evidence boundary stops.

Current source bundle:

- `experiments/results/real_world_validation/locomo/run_20260718T2243500187290000`
- `experiments/results/real_world_validation/locomo/baseline_comparison/run_20260718T2244336007040000`

Current companion audits:

- [REAL_VALIDATION_PROTOCOL_LOCOMO.md](REAL_VALIDATION_PROTOCOL_LOCOMO.md)
- [REAL_VALIDATION_BASELINE_COMPARISON.md](REAL_VALIDATION_BASELINE_COMPARISON.md)
- [REAL_VALIDATION_SCIENTIFIC_REPORT.md](REAL_VALIDATION_SCIENTIFIC_REPORT.md)
- [EXPERIMENT_SELECTION_POLICY.md](EXPERIMENT_SELECTION_POLICY.md)
- [REAL_VALIDATION_REPORT_SCHEMA.md](REAL_VALIDATION_REPORT_SCHEMA.md)
- [REAL_VALIDATION_ARTIFACT_POLICY.md](REAL_VALIDATION_ARTIFACT_POLICY.md)
- [REAL_VALIDATION_FAILURE_ANALYSIS.md](REAL_VALIDATION_FAILURE_ANALYSIS.md)

## 1. Validation Scope

The real-validation branch is intended to test the SRP claim that semantic state transitions can be governed, not merely scored.

Claims tested in the current slice:

- evidence can strengthen verification without increasing authority
- governed transitions can admit supported changes
- unsupported or counterfactual transitions can be rejected
- recommendation and execution remain separable

Dataset in scope:

- LoCoMo `locomo10.json`
- LongMemEval `cases.jsonl` when available, otherwise the repository fixtures

Non-goals for the current slice:

- benchmark superiority
- universal memory improvement
- broad cross-dataset generalization
- artifact promotion for the full real-validation branch

## 2. Experimental Protocol

The current LoCoMo slice uses the following protocol:

1. load the dataset manifest and sample bundle
2. select a category bridge slice covering contradiction, temporal refinement, and unsupported mutation
3. extract transition candidates from real samples
4. attach raw context and source turn ids as provenance
5. evaluate the transition under a fixed governance rule
6. record the result as a validation bundle

Sample selection rule:

- first sample covering categories 1, 2, and 3

The detailed selection policy is recorded in [EXPERIMENT_SELECTION_POLICY.md](EXPERIMENT_SELECTION_POLICY.md).

Transition construction rule:

- category 1 -> `contradiction_update`
- category 2 -> `temporal_refinement`
- category 3 -> `unsupported_mutation`

Decision rule:

- supported real-sample transitions may be accepted
- counterfactual unsupported mutations must be rejected
- authority must not change as a side effect of evidence

## 3. LoCoMo Results

### 3.1 Dataset Coverage

| Dataset | Samples in file | Selected samples | Selected events |
| --- | ---: | ---: | ---: |
| LoCoMo | 10 | 1 | 3 |

The current slice is intentionally small.
It is meant to prove that the verification pipeline can consume real semantic events and preserve auditability.

### 3.2 Event Categories

The selected events are:

| Event type | QA index | Expected | Actual |
| --- | ---: | --- | --- |
| `temporal_refinement` | 0 | accept | accept |
| `unsupported_mutation` | 2 | reject | reject |
| `contradiction_update` | 3 | accept | accept |

The bundle shows one negative case and two positive cases.

LongMemEval status:

- the LongMemEval real-data slice is still pending and is not part of the current 7/18 release gate
- no fixture fallback is promoted into the current release evidence
- the current release gate depends on the refreshed LoCoMo slice and its baseline comparison only

### 3.3 Metrics

Current bundle metrics:

| Metric | Value |
| --- | ---: |
| accepted_transitions | 2 |
| rejected_transitions | 1 |
| invalid_accept_rate | 0.0 |
| authority_changed_with_evidence | false |
| recommendation_execution_separated | true |
| replay_consistency | 1.0 |
| coverage | 1.0 |

Task-facing metrics:

| Metric | Value |
| --- | ---: |
| memory_accuracy | 1.0 |
| relation_accuracy | 1.0 |
| fact_accuracy | 1.0 |

Interpretation:

- the invalid accept rate is zero in the current slice
- evidence did not escalate authority
- the governance layer preserved the recommendation/execution split

## 4. Failure Analysis

The current failure analysis is recorded in [REAL_VALIDATION_FAILURE_ANALYSIS.md](REAL_VALIDATION_FAILURE_ANALYSIS.md).

Case summary:

| Sample | QA | Event | Expected | Actual | Result |
| --- | ---: | --- | --- | --- | --- |
| `conv-26` | 0 | `temporal_refinement` | accept | accept | pass |
| `conv-26` | 2 | `unsupported_mutation` | reject | reject | pass |
| `conv-26` | 3 | `contradiction_update` | accept | accept | pass |

Rejected case:

- sample: `conv-26`
- QA: `2`
- event type: `unsupported_mutation`
- decision: reject
- explanation: the candidate was counterfactual and lacked sufficient support

Accepted cases:

- the temporal refinement case preserves the governed transition behavior on a supported real event
- the contradiction update case shows that a real dataset event can be admitted without altering authority

## 5. Baseline Comparison

The LoCoMo slice is now compared against a direct-mutation baseline in [REAL_VALIDATION_BASELINE_COMPARISON.md](REAL_VALIDATION_BASELINE_COMPARISON.md).
That comparison keeps the same selected sample and events, but removes the governance gate so mechanism differences are visible.

## 6. Interpretation Boundary

What this validates:

- governed transition behavior on real semantic events
- evidence-controlled update decisions
- rejection behavior for unsupported transitions
- auditable traceability from sample to decision
- a release-gated LongMemEval path that remains pending real data

What this does not prove:

- universal memory improvement
- superiority over other memory systems
- broad dataset coverage
- final evidence promotion

This boundary matters.
The current report is intentionally conservative: it treats the LoCoMo result as exploratory real evidence, not as a universal claim.

## 7. Conclusion

The current LoCoMo real-validation slice shows that SRP can:

- extract real semantic events from a dataset
- build governed transition candidates
- preserve provenance through the decision trace
- reject unsupported or counterfactual mutation
- keep evidence and authority separate

That is the core scientific result of the current slice.
It is enough to justify the real-validation methodology, but not enough to promote the branch into a curated release artifact.

LongMemEval should inherit this report structure before any artifact promotion is considered.
The current LongMemEval real-data slice is still pending, so it remains outside the current release gate.

The distilled scientific conclusion is recorded in [REAL_VALIDATION_SCIENTIFIC_REPORT.md](REAL_VALIDATION_SCIENTIFIC_REPORT.md).
