# SRP Sensitivity Analysis Model

This document defines the SRP sensitivity experiment model.
It is a frozen research contract, not an implementation report.

The goal is to answer:

> How should SRP define, run, and interpret one-parameter sensitivity experiments?

---

## 1. Core Principle

SRP sensitivity analysis uses one-factor-at-a-time experiments.

Required form:

```text
Baseline Configuration
    |
    v
Single Parameter Override
    |
    v
Controlled Runtime Execution
    |
    v
Metric Collection
    |
    v
Sensitivity Result
```

Only one parameter changes per experiment.
All other inputs remain fixed.

---

## 2. SensitivityParameter

Each sensitivity parameter should record:

- `parameter`
- `default`
- `test_values`
- `owner`

Optional fields:

- `parameter_class`
- `status`
- `notes`

Example:

```text
parameter: activation_threshold
default: 0.2
test_values: [0.2, 0.3, 0.4, 0.5]
owner: ApproximationOperator
```

---

## 3. SensitivityMetric

Each metric should record:

- `metric_name`
- `measurement`
- `aggregation`

Only metrics that can be measured reliably by the current runtime should be used.

Recommended initial metrics:

- semantic fidelity
- replay equivalence
- recovery success rate
- runtime cost
- memory footprint

Metric selection rule:

- do not include a metric if the current runtime cannot compute it consistently
- prefer metrics already present in the runtime or experiment harness

---

## 4. SensitivityExperiment

Each experiment should record:

- `baseline_config`
- `parameter`
- `candidate_values`
- `dataset`
- `metrics`

Experiment rule:

- a sensitivity experiment changes exactly one parameter
- the dataset and workload remain fixed within the experiment
- any baseline comparison must use the same measurement pipeline

Recommended baseline:

- `RuntimeConfig.default_profile()`

---

## 5. SensitivityResult

Each result should record:

- `parameter`
- `value`
- `metrics`
- `observations`

Recommended observations:

- whether behavior changed
- whether the change was monotonic
- whether the metric was stable across seeds
- whether the parameter appears sensitive at all

---

## 6. Initial Parameter Order

The first sensitivity batch should be small and ordered.

### Batch 1

- `activation_threshold`

Reason:

- numeric
- visible in runtime
- low coupling
- easy to interpret

### Batch 2

- `recovery_min_evidence`

Reason:

- numeric
- affects a bounded recovery gate

### Batch 3

- `preserve_evidence`
- `archive_relations`

Reason:

- boolean policy controls
- should be interpreted separately from continuous thresholds

---

## 7. Frozen Experiment Rules

### OFAT Only

The first phase uses one-factor-at-a-time experiments only.

Not allowed in the first phase:

- multi-parameter grid search
- Bayesian optimization
- adaptive learning
- RL-based tuning

### Configuration Discipline

Each experiment must specify:

- the baseline config
- the overridden parameter
- the expected owner
- the measurement output

### Isolation

Changing one parameter must not silently alter unrelated owners.

---

## 8. Runtime Boundary

Sensitivity analysis does not modify protocol constants.
It only evaluates runtime parameters that already exist in the catalog and registry.

---

## 9. Suggested Directory

Experimental code should live outside `tests/`.

Suggested layout:

```text
experiments/
    sensitivity/
```

This directory is the home for experiment runners, result writers, and notebooks or scripts that define sensitivity workflows.

---

## 10. Next Step

Once this model is frozen, the next implementation step is a minimal OFAT runner for the first batch of parameters.

