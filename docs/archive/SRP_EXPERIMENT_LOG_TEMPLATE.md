# SRP Experiment Log Template

Copy this file for each new experiment record.

Use the experiment ID naming rule from `SRP_NEXT_PHASE_TASKS.md`.

---

## Experiment Record

| Field | Value |
|---|---|
| experiment_id | |
| date | |
| task_id | |
| dataset | |
| model | |
| context_budget | |
| ablation | |
| status | |
| result_summary | |

---

## Research Question

What question does this experiment answer?

| Field | Value |
|---|---|
| research_phase | |
| research_question | |
| hypothesis | |
| comparison_set | |

---

## Configuration

### Measurement Infrastructure

- schema_version:
- lifecycle_artifact_enabled:
- object_retention_breakdown_enabled:

### Recovery Reconstruction

- input_mode:
- structured_state_package_enabled:
- compressed_chunks_enabled:
- repair_enabled:

### Recovery Policy

- reconstruction_policy:
- reconstruction_constraint:
- minimality_target_enabled:

### Repair Diagnostics

- repair_constraint_mode:
- repair_objective:
- repair_enabled:

---

## Metrics

### State Preservation

| Metric | Value |
|---|---|
| semantic_similarity | |
| validation_coverage | |
| validation_alignment | |
| integrity_gap | |
| semantic_compression_loss | |
| object_retention | |
| weighted_object_retention | |
| lost_important_object_count | |

---

### Lifecycle Attribution

| Metric | Value |
|---|---|
| object_lifecycle | |
| source_object_count | |
| compressed_object_count | |
| recovered_object_count | |
| repaired_object_count | |
| source_to_compressed_recall | |
| compressed_to_recovered_recall | |
| recovered_to_repaired_recall | |
| lifecycle_inflation | |

---

### Recovery Reconstruction

| Metric | Value |
|---|---|
| important_recall | |
| task_critical_recall | |
| recovered_object_count | |
| hallucinated_count | |
| object_inflation_ratio | |
| reconstruction_efficiency | |

---

### Recovery Policy

| Metric | Value |
|---|---|
| reconstruction_precision | |
| reconstruction_selectivity | |
| minimality_score | |
| validation_coverage | |
| recovered_object_count | |
| hallucinated_count | |
| object_inflation_ratio | |

---

### Repair Diagnostics

| Metric | Value |
|---|---|
| repair_attempted | |
| repair_context_flat | |
| coverage_before_repair | |
| coverage_after_repair | |
| repair_gain | |
| critical_failures_before | |
| critical_failures_after | |

---

### Efficiency

| Metric | Value |
|---|---|
| prompt_tokens | |
| completion_tokens | |
| total_tokens | |
| compressed_size | |
| compression_ratio | |

---

## Interpretation

component_tested:

metric_changed:

direction:

interpretation:

follow_up:

---

## Notes

- Keep one experiment per file.
- Use `null` for unavailable metrics.
- Keep the same task id and context budget when comparing ablations.
- Prefer explicit values over prose when recording metrics.
- Match `experiment_id` to the naming pattern in `SRP_NEXT_PHASE_TASKS.md`.

