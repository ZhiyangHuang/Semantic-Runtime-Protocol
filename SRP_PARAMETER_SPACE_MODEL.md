# SRP Parameter Space Model

This document defines the SRP parameter taxonomy.
It is not a tuning report and it is not a new protocol design.

The purpose of this document is to answer one question:

> What counts as a parameter in SRP, what does not, and what can be optimized later?

---

## 1. Parameter Taxonomy

SRP parameters are grouped into three layers.

### 1.1 Protocol Constants

These are structural protocol rules.
They define what SRP is.
They should not be swept during ordinary experiments.

Examples:

- lifecycle state vocabulary
- event type vocabulary
- operator type set
- commit structure
- version DAG rules
- checkpoint semantics
- conflict evidence contract
- governance boundary rules

If these change, SRP is no longer the same protocol instance.

### 1.2 Runtime Parameters

These are the first-class knobs that control runtime behavior without changing the protocol itself.
They are the main candidates for sensitivity analysis and grid search.

Examples:

- activation decay
- activation boost
- activation threshold
- approximation threshold
- merge similarity threshold
- forgetting decay rate
- recovery evidence minimum
- decision ranking weights
- checkpoint retention policy
- archive priority threshold

### 1.3 Adaptive Parameters

These are parameters that may become learned or dynamically adjusted in Milestone 3.
They remain bounded by protocol constants and runtime governance.

Examples:

- dynamic threshold policy
- adaptive activation policy
- adaptive operator preference
- learned decision weights
- evidence-dependent ranking policy

---

## 2. What Is Not a Parameter

The following are not treated as tuning parameters in the current frozen protocol layer:

- operator existence
- lifecycle state vocabulary
- commit and version invariants
- replay equivalence requirements
- governance separation rules
- history append-only requirements

These are protocol constants, not optimization variables.

---

## 3. Runtime Parameter Families

### 3.1 Activation

Current implementation already exposes activation-related values in code and policy summaries.

Candidate parameters:

- `activation_initial`
- `activation_decay`
- `activation_floor`
- `activation_boost`
- `activation_threshold`
- `activation_merge_weight`
- `activation_recovery_gain`

Observed code-level surface:

- `activation` assignment in [ActivationUpdateOperator](srp_runtime/operators/activation.py)
- `activation_threshold` in [ApproximationOperator](srp_runtime/operators/approximation.py)
- lifecycle importance and decay values in `policy_spec()` inside [state_summaries.py](srp_experiment/srp/state_summaries.py)

### 3.2 Approximation

Candidate parameters:

- `threshold`
- `minimum_group_size`
- `semantic_similarity`
- `information_loss_limit`
- `representative_selection`

Observed code-level surface:

- `activation_threshold` in [ApproximationOperator](srp_runtime/operators/approximation.py)

### 3.3 Merge

Candidate parameters:

- `merge_similarity_threshold`
- `merge_entity_type_weight`
- `merge_relation_weight`
- `merge_history_weight`

Observed code-level surface:

- merge currently uses structural validation and payload selection in [MergeOperator](srp_runtime/operators/merge.py)

### 3.4 Forgetting

Candidate parameters:

- `forget_decay_rate`
- `forget_activation_threshold`
- `forget_confidence_threshold`
- `forget_age`
- `forget_frequency`

Observed code-level surface:

- evidence preservation gate in [ForgettingOperator](srp_runtime/operators/forgetting.py)
- archive relation preservation toggle in [ForgettingOperator](srp_runtime/operators/forgetting.py)

### 3.5 Recovery

Candidate parameters:

- `minimum_evidence`
- `minimum_confidence`
- `evidence_weight`
- `archive_priority`
- `trace_priority`

Observed code-level surface:

- recovery and replay-related behavior in the runtime and experiment pipeline

### 3.6 Decision

Candidate parameters:

- `constraint_weight`
- `metric_weight`
- `history_weight`
- `operator_priority`
- `candidate_priority`

Observed code-level surface:

- decision filtering and candidate selection in the runtime decision layer

### 3.7 Checkpoint

Candidate parameters:

- `checkpoint_interval`
- `checkpoint_retention`
- `checkpoint_anchor_policy`
- `checkpoint_replay_depth`

### 3.8 Archive

Candidate parameters:

- `archive_threshold`
- `archive_priority`
- `archive_retention_window`
- `archive_evidence_requirement`

---

## 4. Proposed Registry Shape

SRP will eventually benefit from a single registry that records all runtime parameters in one place.

Suggested structure:

```text
srp_runtime/
    config/
        parameter_registry.py
        defaults.py
        validation.py
```

Each registered parameter should carry:

- `parameter`
- `default`
- `range`
- `meaning`
- `effect`
- `evaluation_metric`
- `layer`
- `owner_module`

Example:

```python
ActivationThreshold(
    default=0.35,
    range=(0.1, 0.9),
    metric="semantic_fidelity",
)
```

The registry is important because it prevents threshold drift across modules.

---

## 5. Parameter Learning Order

Parameter work should proceed in this order:

```text
Parameter Definition
    |
    v
Sensitivity Analysis
    |
    v
Parameter Sweep
    |
    v
Grid Search
    |
    v
Bayesian Optimization
    |
    v
Adaptive Policy
    |
    v
RL
```

Grid search is not the first step.
Sensitivity analysis comes first so we can see whether a parameter actually matters.

---

## 6. Milestone Boundary

### Milestone 2

Milestone 2 freezes the governed semantic runtime protocol.
It may expose runtime parameters, but it does not learn them automatically.

### Milestone 3

Milestone 3 may introduce adaptive runtime parameters.
Those parameters must remain subordinate to the frozen protocol constants.

---

## 7. Immediate Next Artifact

The next useful artifact is a concrete parameter registry proposal, not a broad expansion of protocol documents.

Recommended follow-up:

1. extract the current parameter surfaces from runtime code
2. classify each parameter as constant, runtime, or adaptive
3. record default values and candidate sweep ranges
4. define the first sensitivity analysis matrix

