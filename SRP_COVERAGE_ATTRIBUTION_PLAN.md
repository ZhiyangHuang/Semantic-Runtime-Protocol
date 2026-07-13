# SRP Coverage Attribution Plan

This document defines the next research step after the SRR v2 prototype.

The goal is not to add more representation layers.
The goal is to attribute where semantic coverage is lost in the pipeline.

---

## 1. Research Question

Where does semantic coverage drop the most?

Candidate stages:

- extraction
- representation
- compression
- recovery
- validation

The key claim to test is:

```text
Coverage loss should be attributed stage by stage, not only measured at the end.
```

---

## 2. Working Hypothesis

The current evidence suggests:

- graph v1 lowers repair cost
- graph v1.5 improves integrity
- validation coverage remains flat

That means the main bottleneck may be upstream of recovery.

This plan tests whether the dominant loss happens during:

- semantic extraction
- semantic representation
- compression

before the recovery step even begins.

---

## 3. Coverage Attribution Model

Define coverage at each stage:

- `coverage_after_extraction`
- `coverage_after_representation`
- `coverage_after_compression`
- `coverage_after_recovery`
- `coverage_after_validation`

For each stage, compare against the source semantic inventory.

Measure:

- object loss
- relation loss
- constraint loss
- provenance loss
- lifecycle loss

---

## 4. Stage-Wise Loss Matrix

Construct a matrix with rows as pipeline stages and columns as loss types.

Suggested layout:

| Stage | Object | Relation | Constraint | Provenance | Lifecycle |
| --- | --- | --- | --- | --- | --- |
| Extraction |  |  |  |  |  |
| Representation |  |  |  |  |  |
| Compression |  |  |  |  |  |
| Recovery |  |  |  |  |  |
| Validation |  |  |  |  |  |

This matrix answers:

- where each loss is introduced
- whether a later stage repairs or worsens it
- which stage should be improved first

---

## 5. Experimental Inputs

Reuse the frozen infrastructure:

- Stage 2 measurement layer
- failure taxonomy
- graph v1 / v1.5
- graph recovery v1
- graph representation ablation
- semantic extraction audit
- SRR v2 prototype

No new representation layer is required for this analysis.

---

## 6. Primary Outputs

- `coverage_attribution.json`
- `coverage_attribution.md`
- `stagewise_loss_matrix.csv`

The output should make the loss path visible from source to validation.

---

## 7. Acceptance Criteria

This phase is successful if:

- stage-wise coverage loss is measurable
- the dominant loss stage is identifiable
- we can distinguish extraction loss from recovery loss
- the result tells us whether more work should go to extraction, representation, compression, or recovery

---

## 8. Deferred Work

Do not start these yet:

- graph recovery v2
- more runtime layers
- larger ontology expansion
- benchmark expansion solely to chase a bigger representation

