# SRP Experiment Checklist

This checklist turns the measurement-first roadmap in `SRP_NEXT_PHASE_TASKS.md` into an execution log.

Use it to run small controlled experiments first, then expand only after the measurement story is stable.

---

## 1. Measurement Schema Freeze

Goal: stabilize the metrics that define the next phase before adding more capability.

### 1.1 State Preservation

- [ ] Verify `semantic_similarity`
- [ ] Verify `validation_coverage`
- [ ] Verify `validation_alignment`
- [ ] Verify `integrity_gap`
- [ ] Verify `semantic_compression_loss`
- [ ] Verify `object_retention`
- [ ] Verify `weighted_object_retention`
- [ ] Verify `lost_important_object_count`

### 1.2 Recovery Quality

- [ ] Verify `structured_state_package_present`
- [ ] Verify `recovered_object_count`
- [ ] Verify `recovered_object_type_counts`
- [ ] Verify `validation_passed`
- [ ] Verify `state_committed`

### 1.3 Repair Effectiveness

- [ ] Verify `repair_attempted`
- [ ] Verify `repair_context_flat`
- [ ] Verify `coverage_before_repair`
- [ ] Verify `coverage_after_repair`
- [ ] Verify `critical_failures_before`
- [ ] Verify `critical_failures_after`

### 1.4 Efficiency

- [ ] Verify `prompt_tokens`
- [ ] Verify `completion_tokens`
- [ ] Verify `total_tokens`
- [ ] Verify `compressed_size`
- [ ] Verify `compression_ratio`

---

## 2. Controlled Tasks

Goal: keep failure modes small and explainable.

- [ ] Run one small structured recovery task
  - Success criteria:
    - produces `structured_state_package`
    - validation completes
    - metrics are exported
- [ ] Run one small object-retention task
  - Success criteria:
    - `object_retention` is recorded
    - `weighted_object_retention` is recorded
    - selected objects are visible in the log
- [ ] Run one small repair-loop task
  - Success criteria:
    - repair is attempted when validation fails
    - `coverage_before_repair` and `coverage_after_repair` are recorded
    - repair outcome is visible in the log
- [ ] Run one LongBench v2 task for sanity checking
  - Success criteria:
    - full run completes
    - state-preservation metrics are exported
    - record is suitable for comparison against earlier runs

Suggested note fields:
- task id
- model / evaluator mode
- context budget
- outcome
- unexpected failure mode
- experiment_id

---

## 3. Lifecycle Attribution

Goal: attribute semantic degradation across source, compressed, recovered, and repaired stages before changing recovery policy.

- [ ] Verify `object_lifecycle` is exported
- [ ] Verify `source_object_count`
- [ ] Verify `compressed_object_count`
- [ ] Verify `recovered_object_count`
- [ ] Verify `repaired_object_count`
- [ ] Verify `source_to_compressed_recall`
- [ ] Verify `compressed_to_recovered_recall`
- [ ] Verify `recovered_to_repaired_recall`
- [ ] Verify `lifecycle_inflation`

Suggested note fields:
- stage boundary
- source count
- output count
- recall
- inflation

---

## 4. Recovery Reconstruction

Goal: determine how structured semantic state should be reconstructed into a compact executable state.

Current hypothesis:

- structured representation contains sufficient recovery information
- reconstruction policy controls the tradeoff between fidelity and inflation
- recovery should optimize minimal sufficient state, not maximum expansion

### 4.1 Text Only Recovery

Experiment:

```text
srp_meas_longbench_recovery_reconstruction_text_only_r01
```

Config:

```text
input:
  compressed_chunks

structured_state_package:
  disabled

repair:
  disabled
```

Record:

- `validation_coverage`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_efficiency`

### 4.2 Structured Only Recovery

Experiment:

```text
srp_meas_longbench_recovery_reconstruction_structured_only_r01
```

Config:

```text
input:
  structured_state_package

compressed_chunks:
  disabled

repair:
  disabled
```

Record:

- `validation_coverage`
- `important_recall`
- `task_critical_recall`
- `recovered_object_count`
- `hallucinated_count`
- `object_inflation_ratio`
- `reconstruction_efficiency`

### 4.3 Text Plus Structured Recovery

Experiment:

```text
srp_meas_longbench_recovery_reconstruction_text_plus_structured_r01
```

Config:

```text
input:
  compressed_chunks
  structured_state_package

repair:
  disabled
```

Record:

- `validation_coverage`
- `important_recall`
- `task_critical_recall`
- `recovered_object_count`
- `hallucinated_count`
- `object_inflation_ratio`
- `reconstruction_efficiency`

### 4.4 Recovery Policy Decision Gate

After completing reconstruction ablation:

- if `validation_coverage` is high and `object_inflation_ratio` is high, prioritize minimal reconstruction
- if `validation_coverage` is low and `precision` is high, improve structured utilization
- if all policies fail, revisit semantic state representation

---

## 5. Ablation 1: Text Recovery vs Structured Recovery

Compare:

- [ ] `chunk selection + text recovery + text validation`
- [ ] `object-aware compression + structured state recovery + typed validation`

Record:

- `validation_coverage`
- `object_retention`
- `commit_rate`
- `integrity_gap`

---

## 6. Recovery Policy Evaluation

Goal: determine how structured semantic state should be reconstructed into a compact executable state.

Current hypothesis:

- structured representation contains sufficient recovery information
- reconstruction policy controls the tradeoff between fidelity and inflation
- recovery should optimize minimal sufficient state, not maximum expansion

### 6.1 Unrestricted Reconstruction

Experiment:

```text
srp_meas_longbench_reconstruction_policy_unrestricted_r01
```

Config:

```text
input:
  structured_state_package

policy:
  unrestricted
```

Record:

- `validation_coverage`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`
- `reconstruction_efficiency`

### 6.2 Constrained Reconstruction

Experiment:

```text
srp_meas_longbench_reconstruction_policy_constrained_r01
```

Config:

```text
input:
  structured_state_package

policy:
  constrained
```

Record:

- `validation_coverage`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`
- `reconstruction_efficiency`

### 6.3 Minimal Sufficient Reconstruction

Experiment:

```text
srp_meas_longbench_reconstruction_policy_minimal_r01
```

Config:

```text
input:
  structured_state_package

policy:
  minimal
```

Record:

- `validation_coverage`
- `task_critical_recall`
- `task_critical_precision`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`
- `reconstruction_efficiency`

### 6.4 Recovery Policy Decision Gate

After completing reconstruction ablation:

- if `validation_coverage` is high and `object_inflation_ratio` is high, prioritize minimal reconstruction
- if `validation_coverage` is low and `precision` is high, improve structured utilization
- if all policies fail, revisit semantic state representation

---

## 7. Ablation 2: Object-Aware Compression

Compare:

- [ ] `chunk score only`
- [ ] `chunk score + object_support_score`

Record:

- `weighted_object_retention`
- `lost_important_object_count`
- `critical_failures_before`

---

## 8. Previous Repair Ablations

Status:

- completed

Purpose:

- diagnostic only

Conclusion:

- repair modifies failure mode but is not the primary bottleneck.

---

## 9. Ablation 3: Repair Loop

Compare:

- [ ] `fail -> rollback`
- [ ] `fail -> repair -> revalidate`

Record:

- `repair_attempted`
- `coverage_before_repair`
- `coverage_after_repair`
- `repair_gain`
- `token_overhead`

Recommended note fields:
- what triggered repair
- what changed in the repaired package
- whether the repair reduced critical failures

---

## 10. Ablation 4: Encoder vs Local LLM Judge

Compare:

- [ ] `e5-small-v2`
- [ ] `local LLM judge`

Record:

- `semantic_similarity`
- `semantic_drift`
- `prompt_tokens`
- `total_tokens`
- `validation_passed`

Recommended note fields:
- selection method
- judge failures
- runtime cost
- whether the higher-cost path improved state fidelity

---

## 11. Ablation 5: Task-Critical Object Filtering

Compare:

- [ ] `structured recovery over all objects`
- [ ] `structured recovery over task-critical filtered objects`

Record:

- `task_critical_recall`
- `task_critical_precision`
- `task_critical_f1`
- `object_inflation_ratio`
- `validation_coverage`

Recommended note fields:
- filter rule
- how many objects were kept
- how many task-critical objects were retained
- whether hallucinated objects decreased without hurting recall

---

## 12. Deferred Work

Hold these until the measurement story is stable:

- [ ] LongBench task-aware object schema
- [ ] More complex object taxonomies
- [ ] Self-improving repair agent

Reason:

- do not add more components until the current ones can be measured cleanly

---

## 13. Reporting Template

For each experiment, capture:

- experiment_id
- task_id
- date
- config_summary
- metric_values
- short_conclusion
- next_action

Minimal conclusion template:

```text
component tested:
metric changed:
direction:
interpretation:
follow-up:
```
