# SRP Mechanism Attribution / Ablation Protocol

This protocol defines the causal ablation phase that follows boundary characterization.

The research question is:

> Which SRP mechanisms are responsible for maintaining semantic retention, dependency integrity, and validation performance under constrained memory budgets?

The purpose of this phase is not to rediscover boundaries.
It is to measure mechanism-caused shifts in already-frozen boundary behavior.

Initial implementation priority:

- A2: remove dependency-aware retention
- produce a comparison layer with boundary shifts, metric deltas, and attribution score

---

## 1. Research Objective

Measure:

- `delta_boundary = boundary_baseline - boundary_ablated`
- `delta_performance = metric_baseline - metric_ablated`

The goal is to explain which policy component moves which boundary.

---

## 2. Frozen Evaluation Pipeline

### Frozen Workloads

Use only the current boundary family:

- `memory_saturation`
- `validation_pressure`
- `dependency_f1_pressure`

Do not add new benchmarks in this protocol.

### Frozen Budget Sweep

Keep the current budget range frozen:

- `8, 10, 12, 14, 16, 18, 20, 22, 24`

Do not expand or shrink the sweep based on results.

### Frozen Metrics

Primary metrics:

- `active_retention_ratio`
- `active_efficiency`
- `dependency_coverage`
- `dependency_f1`
- `validation_score`

Secondary metrics:

- `graph_integrity`
- `object_retention`
- `weighted_retention`

Secondary metrics are explanatory only.
They are not the main optimization target for this phase.

---

## 3. Ablation Matrix

### A1. Remove Importance Weighting

Hypothesis:

- importance weighting controls which semantic units survive first

Modification:

- baseline: weighted retention by importance
- ablation: uniform retention

Expected effect:

- allocation boundary moves earlier
- `active_retention_ratio` drops
- `validation_score` may decline secondarily

### A2. Remove Dependency-Aware Retention

Hypothesis:

- dependency-aware retention maintains structural coherence

Modification:

- baseline: semantic importance plus dependency graph
- ablation: semantic importance only

Expected effect:

- dependency boundary moves earlier
- `dependency_coverage` and `dependency_f1` degrade first
- `validation_score` declines secondarily

### A3. Disable Archive Policy

Hypothesis:

- archive policy supports long-horizon recovery

Modification:

- baseline: active memory plus archive plus restore
- ablation: active-only retention

Allowed evaluation extension:

- include cycles `1, 3, 5`

Expected effect:

- short-horizon metrics may remain similar
- long-horizon drift and midpoint variance increase

### A4. Flatten Lifecycle Thresholds

Hypothesis:

- lifecycle thresholds regulate transition smoothness

Modification:

- baseline: pressure-aware transitions
- ablation: single fixed threshold

Expected effect:

- mean boundary may stay similar
- robustness degrades
- detection variance increases

---

## 4. Attribution Table

The final report should summarize:

| Mechanism | Removed Component | Main Boundary Affected | Expected Evidence |
| --- | --- | --- | --- |
| Importance weighting | priority scoring | Allocation | earlier allocation collapse |
| Dependency retention | graph-aware selection | Dependency | earlier dependency collapse |
| Archive policy | historical recovery | Drift | long-horizon degradation |
| Lifecycle threshold | adaptive transition | Robustness | higher variance |

The comparison layer should also report:

- `boundary_shift`
- `metric_delta_summary`
- `target_effect`
- `collateral_effect`
- `attribution_score`

---

## 5. Success Criteria

An ablation is successful if:

- the intended mechanism changes the intended boundary
- unrelated boundaries remain relatively stable
- the boundary movement is measurable with the frozen pipeline

Strong evidence is:

- removal of one mechanism produces a specific boundary shift
- the other boundaries change less, or only secondarily

---

## 6. Phase Position

This protocol comes after:

- Pareto analysis
- Sensitivity analysis
- Boundary detection
- Boundary robustness
- Boundary drift

The next research target is causality, not more threshold discovery.
