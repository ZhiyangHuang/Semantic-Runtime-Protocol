# SRP Metric Definitions

This document freezes the formal definitions of the metrics used across SRP experiments.

All experiments should reference these definitions. Existing definitions should remain stable across runs unless a new version is explicitly introduced.

---

## Metric Taxonomy

### State Preservation

#### semantic_similarity

- Purpose: measure embedding-level closeness between source and recovered state.
- Definition: cosine similarity between source and recovered state vectors.
- Range: `[0, 1]`
- Interpretation: higher means closer semantic match.
- Higher is better: yes
- Used by: RQ1, RQ2

#### validation_coverage

- Purpose: measure how much validation-critical state is satisfied by the recovered state.
- Definition: weighted coverage score returned by the validator.
- Range: `[0, 1]`
- Interpretation: higher means more benchmark-critical state preserved.
- Higher is better: yes
- Used by: RQ1, RQ2, RQ3, RQ4

#### validation_alignment

- Purpose: measure how well recovered state aligns with validation expectations.
- Definition: validator alignment score between source expectations and recovered state.
- Range: `[0, 1]`
- Interpretation: higher means stronger alignment to task-critical expectations.
- Higher is better: yes
- Used by: RQ1, RQ2, RQ3, RQ4

#### integrity_gap

- Purpose: expose disagreement between semantic similarity and validator coverage.
- Definition: `integrity_gap = semantic_similarity - validation_coverage`
- Range: `(-1, 1]`
- Interpretation: larger gaps indicate embedding closeness without benchmark fidelity.
- Higher is better: no, lower is better
- Used by: RQ1, RQ2

#### semantic_compression_loss

- Purpose: summarize information lost during compression.
- Definition: `semantic_compression_loss = 1 - semantic_retention_score`
- Range: `[0, 1]`
- Interpretation: higher means more semantic loss.
- Higher is better: no, lower is better
- Used by: RQ1, RQ2

#### object_retention

- Purpose: measure how many source objects survive reconstruction.
- Definition: `|retained| / |source|`
- Range: `[0, 1]`
- Interpretation: higher means more source objects preserved.
- Higher is better: yes
- Used by: RQ1, RQ2

#### weighted_object_retention

- Purpose: measure retention weighted by object importance.
- Definition: weighted retained importance divided by weighted source importance.
- Range: `[0, 1]`
- Interpretation: higher means important objects are preserved more effectively.
- Higher is better: yes
- Used by: RQ1, RQ2, RQ3

#### lost_important_object_count

- Purpose: count important source objects that were not recovered.
- Definition: number of important objects in source missing from recovered state.
- Range: `[0, +inf)`
- Interpretation: lower means fewer critical losses.
- Higher is better: no, lower is better
- Used by: RQ1, RQ2, RQ3

---

### Lifecycle Attribution

#### object_lifecycle

- Purpose: record source/compressed/recovered/repaired transitions.
- Definition: structured artifact with stage counts and transition recall.
- Range: artifact
- Interpretation: used to locate the stage where degradation occurs.
- Higher is better: n/a
- Used by: RQ2

#### source_object_count

- Purpose: count objects in source state.
- Definition: number of objects extracted from the original state.
- Range: `[0, +inf)`
- Higher is better: n/a
- Used by: RQ2

#### compressed_object_count

- Purpose: count objects after compression.
- Definition: number of objects retained in compressed state.
- Range: `[0, +inf)`
- Higher is better: n/a
- Used by: RQ2

#### recovered_object_count

- Purpose: count objects after reconstruction.
- Definition: number of objects in reconstructed state.
- Range: `[0, +inf)`
- Interpretation: higher may indicate broader reconstruction or inflation.
- Higher is better: depends
- Used by: RQ2, RQ3

#### repaired_object_count

- Purpose: count objects after repair.
- Definition: number of objects in repaired state.
- Range: `[0, +inf)`
- Interpretation: used to observe repair-induced state transformation.
- Higher is better: depends
- Used by: RQ4

#### source_to_compressed_recall

- Purpose: measure how much source object inventory survives compression.
- Definition: retained source objects divided by source objects.
- Range: `[0, 1]`
- Higher is better: yes
- Used by: RQ2

#### compressed_to_recovered_recall

- Purpose: measure how much compressed state survives reconstruction.
- Definition: retained compressed objects divided by compressed objects.
- Range: `[0, 1]`
- Higher is better: yes
- Used by: RQ2, RQ3

#### recovered_to_repaired_recall

- Purpose: measure how much recovered state survives repair.
- Definition: retained recovered objects divided by recovered objects.
- Range: `[0, 1]`
- Higher is better: yes
- Used by: RQ4

#### lifecycle_inflation

- Purpose: measure state expansion across lifecycle stages.
- Definition: ratio or delta between later-stage object counts and earlier-stage object counts.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ2, RQ3, RQ4

---

### Recovery Reconstruction

#### reconstruction_precision

- Purpose: measure how many recovered objects are supported by the reference semantic state.
- Definition: `|Recovered ∩ Reference| / |Recovered|`
- Range: `[0, 1]`
- Higher is better: yes
- Used by: RQ3

#### reconstruction_selectivity

- Purpose: measure how aggressively reconstruction expands state from available structured input.
- Definition: `|Selected| / |Available|`
- Range: `[0, 1]`
- Higher is better: depends on policy goal
- Used by: RQ3

#### minimality_score

- Purpose: measure compactness of reconstruction relative to validation success.
- Definition: `validation_coverage / recovered_object_count`
- Range: `[0, +inf)`
- Higher is better: yes
- Used by: RQ3

#### reconstruction_efficiency

- Purpose: normalize validation success by reconstruction size.
- Definition: `validation_coverage / recovered_object_count`
- Range: `[0, +inf)`
- Higher is better: yes
- Used by: RQ3

---

### Repair Diagnostics

#### repair_attempted

- Purpose: indicate whether a repair pass occurred.
- Definition: boolean flag set when repair is triggered.
- Range: `{true, false}`
- Higher is better: n/a
- Used by: RQ4

#### repair_context_flat

- Purpose: expose repair context in a log-friendly form.
- Definition: flattened repair context artifact.
- Range: artifact
- Higher is better: n/a
- Used by: RQ4

#### coverage_before_repair

- Purpose: measure validation coverage before repair.
- Definition: validator coverage score before the repair pass.
- Range: `[0, 1]`
- Higher is better: yes
- Used by: RQ4

#### coverage_after_repair

- Purpose: measure validation coverage after repair.
- Definition: validator coverage score after the repair pass.
- Range: `[0, 1]`
- Higher is better: yes
- Used by: RQ4

#### repair_gain

- Purpose: measure how much repair improved coverage.
- Definition: `coverage_after_repair - coverage_before_repair`
- Range: `[-1, 1]`
- Higher is better: yes
- Used by: RQ4

#### critical_failures_before

- Purpose: count critical validation failures before repair.
- Definition: number of critical failures reported before repair.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ4

#### critical_failures_after

- Purpose: count critical validation failures after repair.
- Definition: number of critical failures reported after repair.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ4

---

### Efficiency

#### prompt_tokens

- Purpose: measure prompt cost.
- Definition: total prompt tokens consumed in the step.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ3, RQ4

#### completion_tokens

- Purpose: measure completion cost.
- Definition: total completion tokens consumed in the step.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ3, RQ4

#### total_tokens

- Purpose: measure total token cost.
- Definition: `prompt_tokens + completion_tokens`
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ3, RQ4

#### compressed_size

- Purpose: measure size of compressed state artifact.
- Definition: token or byte size of compressed representation.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ1, RQ2

#### compression_ratio

- Purpose: measure compression strength.
- Definition: compressed size divided by source size, or equivalent normalized ratio.
- Range: `[0, +inf)`
- Higher is better: no, lower is better
- Used by: RQ1, RQ2

---

## Metric Stability

- Version: `v1.0`
- Frozen date: `2026-07-07`
- Policy: existing definitions should remain unchanged; add new metrics only with explicit versioning.
