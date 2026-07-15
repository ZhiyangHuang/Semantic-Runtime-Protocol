# SRP Phase V Semantic Retention and Drift Evaluation

This document freezes the next paper-facing evaluation phase for SRP.
It is an evaluation plan, not a new experiment result, not a mechanism design, and not a policy document.

## 1. Why This Phase Exists

The current SRP evidence chain shows that semantic state transitions can be observed, bounded, optimized, and verified.
It does not yet directly measure how much meaning is preserved after those transitions.

Phase V exists to answer a narrower question:

> Given a governed transition pipeline, how do semantic coverage and semantic drift trade off under constrained retention settings?

This phase is not about making the runtime adapt autonomously.
It is about measuring whether controlled semantic evolution preserves meaning under pressure.

## 2. Relation to Existing Models

Phase V is aligned with:

- [SRP Preservation Objective Formalization](SRP_PRESERVATION_OBJECTIVE_FORMALIZATION.md)
- [SRP Semantic Degradation Model](SRP_SEMANTIC_DEGRADATION_MODEL.md)
- [SRP Coverage Attribution Plan](SRP_COVERAGE_ATTRIBUTION_PLAN.md)

Those documents define the semantic properties that should be preserved.
Phase V turns those properties into measurable retention and drift outcomes.

## 3. Research Questions

### RQ5.1

Can SRP preserve semantic coverage under constrained retention settings?

### RQ5.2

Can SRP reduce semantic drift while preserving the validated transition boundary?

### RQ5.3

Where is the Pareto frontier between semantic coverage, semantic drift, and evidence cost?

## 4. Working Hypothesis

The expected tradeoff is:

- higher retention thresholds reduce drift
- higher retention thresholds may also reduce coverage
- stronger evidence requirements improve stability but increase cost
- relation-aware archive settings should improve structural preservation

The phase is designed to identify governed operating points, not a universal optimum.

## 5. Semantic Metrics

Phase V should measure semantic preservation at the meaning level rather than at the token level alone.

Recommended metrics:

- `semantic_coverage`
- `fact_accuracy`
- `relation_accuracy`
- `semantic_drift`
- `recovery_accuracy`
- `evidence_cost`

### 5.1 Semantic Coverage

Semantic coverage measures how many original semantic units are preserved after transition.

Example interpretation:

```text
coverage = recovered_semantic_units / original_semantic_units
```

### 5.2 Semantic Drift

Semantic drift measures how far the recovered meaning moves from the source meaning.

Recommended decomposition:

- fact drift
- relation drift
- preference drift

The phase should not treat parameter drift as a substitute for semantic drift.

### 5.3 Frozen Output Schema

The implemented Phase V protocol freezes a single-transition output record with:

- `original_state_id`
- `recovered_state_id`
- `semantic_coverage`
- `semantic_drift`
- `fact_accuracy`
- `relation_accuracy`
- `recovery_accuracy`
- `evidence_cost`
- `parameters`

The baseline runner also records:

- `fact_drift`
- `relation_drift`
- `confidence_drift`
- unit counts
- missing / hallucinated unit counts

This keeps the meaning-level fidelity protocol explicit before any parameter sweep is introduced.

## 6. Candidate Parameters

The phase should sweep the retention-related parameters that already exist in the calibration boundary:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

These parameters are expected to trade off:

- coverage
- semantic stability
- recovery cost
- evidence cost

## 7. Experimental Design

### 7.1 Frozen Factors

Keep fixed:

- workload family
- objective definition
- evidence backend
- evaluation protocol

### 7.2 Swept Factors

Sweep:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`

### 7.3 Expected Output

The phase should produce:

- semantic coverage curves
- semantic drift curves
- recovery accuracy summaries
- a Pareto frontier over coverage, drift, and cost

## 8. Interpretation Boundary

Phase V should be interpreted as a preservation analysis, not a new optimization phase.

It should answer:

> Which governed operating points preserve the most meaning under constrained transition settings?

It should not answer:

> Which runtime default should be updated automatically?

## 9. Relation to the Paper

If completed, Phase V would extend the paper's evidence chain with a preservation claim:

- Phase I: semantic variables are observable
- Phase II: feasible boundaries are validated
- Phase III-A: configurations are ranked inside validated regions
- Evidence Escalation: verification improves without authority transfer
- Phase V: semantic meaning is preserved under controlled transitions

## 10. Status

This phase is frozen as a future evaluation boundary.
It is not activated by the current paper baseline.
The initial baseline protocol is now implemented in `experiments/evaluation/phase_v_retention/`, and it writes a paper-facing retention report, but the parameter sweep remains deferred.
