# STFB External Validation v0.1 Specification

## Purpose

This document freezes the external validation track for Semantic Transition Failure Benchmark (STFB).

The objective is to evaluate whether semantic transition failures identified by STFB also occur in external benchmark environments.

Core question:

```text
Can external task environments be represented as semantic transitions, and do different admission strategies produce different failure patterns?
```

This track does not redefine the STFB core benchmark.
It wraps external cases into the STFB transition schema for evaluation only.

## Scope

### Included External Environments

- LongMemEval
- ARC

### Initial Canonical Cases

Milestone 0 of the external validation track includes only three canonical cases:

1. LongMemEval temporal regression
2. LongMemEval provenance loss
3. ARC unsupported inference

### Excluded

This track does not include:

- full benchmark conversion
- MMLU
- HumanEval
- LLM proposer integration
- new failure taxonomy
- new metrics
- changes to the STFB core schema

## External Instance Mapping

External benchmark cases MUST be mapped through a wrapper layer into the STFB transition schema.

The wrapper MAY add metadata, but it MUST NOT modify the core STFB instance semantics.

Recommended mapping:

```json
{
  "instance_id": "longmemeval_case_001",
  "source": {
    "benchmark": "LongMemEval",
    "case_id": "xxx"
  },
  "state_t": {},
  "observation": {},
  "proposal": {},
  "evidence": {},
  "authority": {},
  "expected_transition": {
    "type": "temporal_regression",
    "should_commit": false
  },
  "metadata": {
    "source_task": "preference_revision"
  }
}
```

The source benchmark identity belongs in metadata.
External cases are transformed into STFB transition instances for admission evaluation only.

## Canonical Cases

### Case 1: LongMemEval Temporal Regression

Goal:

- prove that an older state can incorrectly override a newer authoritative state

Expected failure mode:

- temporal regression

### Case 2: LongMemEval Provenance Loss

Goal:

- prove that retrieved information alone does not establish mutation authority

Expected failure mode:

- provenance loss
- evidence-authority mismatch

### Case 3: ARC Unsupported Inference

Goal:

- prove that correct-looking reasoning is not always a valid state transition

Expected failure mode:

- unsupported inference

## Baseline Matrix

The external validation track uses the same admission-strategy comparison logic as the STFB core benchmark.

Frozen methods:

| Method | Behavior |
| --- | --- |
| Direct Mutation | commit proposal |
| Confidence Threshold | confidence gated |
| Retrieval Verification | evidence gated |
| SRP | authority plus transition gated |

Retrieval Verification is included explicitly to address the claim that retrieval grounding alone may be insufficient.

## Metrics

The external validation track reuses the STFB metrics without redefining them.

### Primary Metrics

- Invalid Acceptance Rate `IAR`
- Authority Violation Rate `AVR`
- Drift

### Metric Definitions

```text
IAR = wrong transition / all transitions
AVR = committed without authority / committed transitions
Drift = distance(committed_state, expected_state)
```

## Success Criteria

The external validation track is successful if:

- SRP lowers `IAR`
- SRP lowers `AVR`
- SRP lowers `Drift`
- valid transitions are not rejected at a materially higher rate than necessary

The goal is not to maximize conservative rejection.
The goal is to show that the admission boundary changes outcomes in failure-prone external environments.

## Implementation Boundary

Recommended directory shape:

```text
STFB/external/
├── longmemeval/
│   ├── adapters/
│   └── cases/
└── arc/
    ├── adapters/
    └── cases/
```

This track should not alter:

- `STFB/runner/`
- `STFB/metrics/`
- `STFB/baselines/`

unless later abstraction work requires it.

## Freeze Statement

This document freezes the external validation boundary only.
It does not modify the STFB core benchmark definition, the prototype checkpoint, or the SRP v1.0 release boundary.
