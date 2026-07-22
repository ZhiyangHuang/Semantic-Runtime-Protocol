# STFB LongMemEval External Validation v0.1 Specification

## Purpose

This document freezes the first external validation track for STFB using LongMemEval cases.

The objective is:

> Convert existing LongMemEval evaluation cases into STFB-compatible semantic transition instances without modifying the core STFB contract.

This track is adapter-first.
It does not redefine the STFB benchmark, the core instance schema, or the baseline semantics.

## Scope

### Included

The first version includes only three canonical cases:

1. Temporal Regression
2. Provenance Loss
3. Evidence-Authority Confusion

### Excluded

This track does not include:

- automatic case mining
- full LongMemEval coverage
- ARC
- MMLU
- HumanEval
- new failure taxonomy
- new metrics
- changes to the STFB core runner contract
- changes to the STFB baseline contract

## Mapping Rules

LongMemEval source cases MUST be mapped into the STFB transition schema through a wrapper layer.

The wrapper may add metadata, but it MUST keep the core STFB fields intact.

Recommended shape:

```json
{
  "instance_id": "lme_temporal_001",
  "state_t": {
    "current_memory": []
  },
  "observation": {
    "new_information": []
  },
  "proposal": {
    "candidate_update": {}
  },
  "evidence": {
    "retrieved_items": []
  },
  "authority": {
    "source": "",
    "timestamp": ""
  },
  "expected_transition": {
    "should_commit": false,
    "failure_type": "temporal_regression"
  },
  "metadata": {
    "source_benchmark": "LongMemEval",
    "source_case_id": ""
  }
}
```

LongMemEval identity belongs in `metadata`.
The wrapper MUST not turn source benchmark structure into a new benchmark schema.

## Canonical Cases

### Case 1: Temporal Regression

Goal:

- test whether old memory can incorrectly override a newer state

Expected failure type:

- temporal regression

### Case 2: Provenance Loss

Goal:

- test whether retrieved information alone can establish mutation authority

Expected failure type:

- provenance loss

### Case 3: Evidence-Authority Confusion

Goal:

- test whether more evidence is incorrectly treated as more permission

Expected failure type:

- evidence-authority confusion

## Output Artifacts

The external validation track SHOULD produce:

```text
STFB/external/longmemeval/reports/
├── longmemeval_external_v0_1.json
└── longmemeval_external_summary.md
```

These artifacts are the external-track equivalents of the prototype evidence package.

## Baseline Comparison

The LongMemEval external track reuses the existing STFB admission strategies:

- Direct Mutation
- Confidence Threshold
- Retrieval Verification
- SRP

The purpose is to compare admission behavior, not to introduce a new evaluation stack.

## Success Criteria

This track is successful if all of the following hold:

1. LongMemEval cases can be mapped into STFB instances.
2. The existing STFB runner can evaluate the mapped cases without changing the core contract.
3. The mapped cases are expressible using the frozen STFB failure taxonomy.
4. Baseline divergence is observable in the resulting reports.

The success criterion is not "SRP wins LongMemEval."
The success criterion is that external cases can be evaluated as semantic transition instances under the STFB abstraction.

## Implementation Boundary

Recommended directory shape:

```text
STFB/external/
└── longmemeval/
    ├── README.md
    ├── adapter/
    │   └── mapper.py
    ├── cases/
    │   ├── temporal_regression/
    │   ├── provenance_loss/
    │   └── evidence_authority/
    ├── reports/
    └── configs/
```

This track SHOULD NOT alter:

- `STFB/runner/`
- `STFB/metrics/`
- `STFB/baselines/`
- `STFB/instances/`

unless later abstraction work explicitly requires it.

## Freeze Statement

This document freezes the LongMemEval external validation boundary only.
It does not modify the STFB core benchmark definition, the Milestone 0 prototype checkpoint, or the SRP v1.0 release boundary.
