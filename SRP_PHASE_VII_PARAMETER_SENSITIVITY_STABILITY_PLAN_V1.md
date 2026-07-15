# SRP Phase VII Parameter Sensitivity and Stability Plan V1

This document freezes the next parameter-analysis boundary for SRP.
It is a planning artifact, not an experiment result, not a runtime policy, and not a new recovery mechanism.

## 1. Objective

Measure how sensitive SRP recommendations and reconstruction outcomes are to controlled parameter variation.

The goal is not to find a universally optimal configuration.
The goal is to quantify:

- recommendation stability
- drift variance
- retention tradeoffs
- boundary robustness under repeated runs

## 2. Frozen Scope

Phase VII should not change:

- the Phase II feasible region definition
- the Phase III-A optimization objective family
- the Phase V retention schema
- the Phase VI relation-aware recovery design

Phase VII analyzes parameter effects and stability only.

## 3. Candidate Axes

Suggested axes:

1. `archive_relations`
2. `preserve_evidence`
3. `recovery_min_evidence`
4. `activation_threshold`
5. relation depth for recovery experiments

## 4. Stability Questions

Phase VII should answer:

- Does the recommended configuration remain stable across seeds?
- Do recovery metrics vary smoothly or sharply under parameter changes?
- Which parameters move the system across different Pareto regions?
- Which parameters mainly affect cost rather than fidelity?

## 5. Metrics

Candidate metrics:

- recommendation variance
- semantic coverage variance
- semantic drift variance
- relation accuracy variance
- closure accuracy variance
- evidence cost variance

## 6. Non-Goals

Do not treat this phase as:

- a runtime default update policy
- an adaptive learning controller
- a full benchmark comparison
- a replacement for Phase VI-A

## 7. Relation to the Paper

Phase VII follows the current frozen evidence chain:

- Phase I: observability
- Phase II: boundary validation
- Phase III-A: governed optimization
- Evidence Escalation: verification improvement
- Phase V: semantic fidelity measurement
- Phase VI-A: structure-preserving reconstruction
- Phase VII: parameter sensitivity and stability analysis

