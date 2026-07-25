# STFB External Validation

Reserved for frozen external validation tracks.

Tracks:

- [LongMemEval](longmemeval/README.md)
- [ARC](arc/README.md)

Shared contract:

- [Frozen STFB contract](../../paper/docs/plans/STFB_SPEC.md)

## Cross-Environment Analysis

This section consolidates the analysis layer for interpreting external validation results across heterogeneous semantic stress environments.

### Objective

The analysis layer does not introduce new benchmarks, metrics, taxonomy, or admission policy.
It organizes existing evidence so that LongMemEval, ARC, and future external environments can be interpreted through the same admission-semantics lens.

### Cross-Environment Mechanism Matrix

| Environment | Canonical Case | Semantic Pressure | Direct Mutation | Confidence Threshold | SRP | Expected Admission | Mechanism |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LongMemEval | `lme_001` | Temporal Regression | Commit | Reject | Reject | Reject | Temporal integrity |
| LongMemEval | `lme_002` | Evidence-Authority Confusion | Commit | Commit | Reject | Reject | Authority validation |
| ARC | `arc_001` | Unsupported Inference | Commit | Commit | Reject | Reject | Unsupported mutation |
| ARC | `arc_002` | Valid Reasoning | Commit | Commit | Commit | Commit | Legitimate transition |

Interpretation:

- the same admission policy is being evaluated under different semantic stress environments
- the table is not a performance leaderboard
- the key question is whether admission semantics remain consistent across environments

### Divergence Analysis

| Divergence Type | Meaning |
| --- | --- |
| Baseline Accept -> SRP Reject | Unauthorized transition blocked |
| Threshold Sensitive | Confidence alone is insufficient |
| All Accept | Legitimate transition preserved |

Representative cases:

| Case | Divergence Type | Interpretation |
| --- | --- | --- |
| `lme_001` | Baseline Accept -> SRP Reject | Unauthorized temporal update prevented |
| `lme_002` | Threshold Sensitive | Confidence does not substitute for authority |
| `arc_001` | Baseline Accept -> SRP Reject | Unsupported reasoning transition blocked |
| `arc_002` | All Accept | Legitimate transition preserved |

### Failure Mapping

| Failure Mechanism | LongMemEval | ARC |
| --- | --- | --- |
| Temporal regression | yes | no |
| Evidence-authority confusion | yes | no |
| Unsupported inference | no | yes |
| Valid transition preservation | yes | yes |

### Discussion

- unsupported transitions are blocked when authority is not satisfied
- valid transitions are preserved when authority is satisfied
- confidence alone does not establish mutation permission
- confidence-threshold admission can behave differently depending on the confidence surface of the environment
- direct mutation can preserve valid transitions while also admitting unsupported ones
- SRP can reject unsupported transitions without blocking supported ones

### Out of Scope

This framework does not:

- define new benchmark tasks
- introduce new admission metrics
- compare benchmark difficulty
- establish statistical claims across environments

It is an analysis layer for organizing existing evidence, not a new specification.
