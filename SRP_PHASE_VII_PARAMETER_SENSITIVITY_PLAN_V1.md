# SRP Phase VII-B Parameter Sensitivity and Governance Tradeoff Plan V1

This document freezes the Phase VII-B parameter-analysis boundary for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not an adaptive controller.

## 1. Objective

Measure how SRP parameters influence semantic fidelity, structural preservation, reconstruction cost, and governance stability under a frozen relation-aware recovery baseline.

The question is not which parameter setting is globally best.
The question is:

> How do SRP parameters move the system across fidelity-cost tradeoff regions while preserving governance separation?

## 2. Frozen Scope

Phase VII-B should not change:

- the Phase II feasible region definition
- the Phase III-A optimization objective family
- the Phase V retention schema
- the Phase VI relation-aware recovery design
- the Phase VII-A recommendation stability boundary

Phase VII-B analyzes parameter effects and governance tradeoffs only.

## 3. Sensitivity Axes

Primary axes:

1. `archive_relations`
2. `preserve_evidence`
3. `relation_depth`
4. `activation_threshold`

Frozen baseline:

- `archive_relations = False`
- `preserve_evidence = False`
- `relation_depth = 1`
- `activation_threshold = 0.9`
- `recovery_min_evidence = 1`

## 4. Stability Questions

Phase VII-B should answer:

- Which parameters move the system across fidelity-cost tradeoff regions?
- Which parameters mainly affect relation preservation?
- Which parameters mainly affect reconstruction cost?
- Which parameters shift the governance frontier?

## 5. Metrics

Candidate metrics:

- semantic coverage
- semantic drift
- fact accuracy
- relation accuracy
- recovery accuracy
- closure accuracy
- path preservation
- neighborhood completeness
- hallucinated relation rate
- evidence cost

Derived analysis metrics:

- delta vs baseline
- Pareto frontier membership
- axis-wise tradeoff profiles

## 6. Non-Goals

Do not treat this phase as:

- a runtime default update policy
- an adaptive learning controller
- a replacement for Phase VI-A
- a universal optimum search

## 7. Relation to the Paper

Phase VII-B follows the current frozen evidence chain:

- Phase I: observability
- Phase II: boundary validation
- Phase III-A: governed optimization
- Evidence Escalation: verification improvement
- Phase V: semantic fidelity measurement
- Phase VI-A: structure-preserving reconstruction
- Phase VII-A: recommendation stability
- Phase VII-B: parameter sensitivity and governance tradeoff analysis

