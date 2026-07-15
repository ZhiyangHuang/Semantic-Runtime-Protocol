# SRP Phase V Retention Sensitivity Plan V1

This document freezes the sensitivity-analysis plan for Phase V of SRP.
It is a planning artifact, not a new experiment result, not a mechanism design, and not a runtime update policy.

## 1. Objective

Measure how retention-related parameters affect semantic fidelity after governed transition.

The goal is not to find a universally optimal configuration.
The goal is to expose the tradeoff surface between semantic coverage, semantic drift, recovery fidelity, and evidence cost.

## 2. Frozen Variables

Keep fixed:

- workload
- objective
- evidence backend

These factors should not change during Phase V sensitivity analysis.

## 3. Sensitivity Axes

The phase should analyze the following retention-related parameters one axis at a time before combining them into larger sweeps:

1. `archive_relations`
2. `preserve_evidence`
3. `recovery_min_evidence`
4. `activation_threshold`

The recommended order is:

1. relation preservation sensitivity
2. evidence preservation sensitivity
3. recovery strictness sensitivity
4. activation-threshold sweep

## 4. Metrics

Primary metrics:

- `semantic_coverage`
- `semantic_drift`
- `fact_accuracy`
- `relation_accuracy`
- `recovery_accuracy`
- `evidence_cost`

Secondary diagnostics:

- `fact_drift`
- `relation_drift`
- `confidence_drift`
- missing unit count
- hallucinated unit count

## 5. Phase V-A: Relation Preservation Sensitivity

Question:

> Does explicit relation preservation improve structural semantic fidelity?

Compare:

- `archive_relations = False`
- `archive_relations = True`

Expected effect:

- relation fidelity should increase if relation archival is doing useful work
- relation drift should decrease if the archive boundary is preserving structure
- evidence cost may increase

## 6. Phase V-B: Evidence Preservation Sensitivity

Question:

> Does explicit evidence preservation reduce semantic uncertainty without changing authority?

Compare:

- `preserve_evidence = False`
- `preserve_evidence = True`

Expected effect:

- confidence drift should decrease if evidence retention stabilizes recovery
- boundary hallucination should be easier to detect or constrain
- evidence cost may increase

## 7. Phase V-C: Recovery Evidence Threshold

Question:

> How does stricter recovery evidence affect fidelity and cost?

Compare:

- `recovery_min_evidence = 1`
- `recovery_min_evidence = 2`
- `recovery_min_evidence = 3`

Expected effect:

- semantic drift should decrease with stricter recovery requirements
- recovery cost should increase
- the protocol may reject more transitions

## 8. Phase V-D: Activation Threshold Sweep

Question:

> How does transition gating affect the coverage versus stability tradeoff?

Compare:

- `activation_threshold = 0.1`
- `activation_threshold = 0.3`
- `activation_threshold = 0.5`
- `activation_threshold = 0.7`
- `activation_threshold = 0.9`

Expected effect:

- lower thresholds may increase coverage but also increase drift
- higher thresholds may reduce drift but also reduce coverage

## 9. Analysis Plan

The analysis should report:

- parameter effect
- retention tradeoff
- Pareto frontier

The output should not collapse the study into a single best score.
It should preserve the tradeoff surface and the governed operating points.

## 10. Non-Goals

Do not claim:

- runtime default update
- autonomous adaptation
- universal optimum
- a single parameter that dominates all workloads

## 11. Relation to the Paper

Phase V sensitivity extends the paper's evidence chain with controlled retention analysis:

- Phase I: semantic variables are observable
- Phase II: feasible boundaries are validated
- Phase III-A: configurations are ranked inside validated regions
- Evidence Escalation: verification improves without authority transfer
- Phase V: semantic fidelity tradeoffs become measurable after governed transition

