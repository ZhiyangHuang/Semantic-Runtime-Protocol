# STFB Implementation Milestone 0 Specification v0.1

## Purpose

This document freezes the first implementation contract for Semantic Transition Failure Benchmark (STFB).

The objective is to produce the first reproducible semantic transition failure episode.

Core validation:

> Ungoverned semantic transitions exhibit measurable failure patterns.

## Scope

### Included

Milestone 0 implements only the following failure types:

1. Unsupported Mutation

   Test:

   ```text
   proposal changes state
   but lacks mutation authority
   ```

2. Evidence-Authority Confusion

   Test:

   ```text
   evidence confidence
   is incorrectly treated as execution permission
   ```

3. Temporal Regression

   Test:

   ```text
   new transition overwrites newer or higher-authority state
   ```

### Excluded

Milestone 0 does not implement:

- full dataset construction
- LLM proposer integration
- embeddings
- RAG
- human evaluation
- public benchmark release
- additional failure taxonomy

## Minimal Architecture

Recommended directory structure:

```text
STFB/
├── instances/
│   ├── schema.json
│   └── examples/
│
├── baselines/
│   ├── direct_mutation.py
│   ├── confidence_threshold.py
│   └── srp_adapter.py
│
├── runner/
│   ├── run_episode.py
│   ├── evaluate.py
│   └── contracts.py
│
├── metrics/
│   ├── iar.py
│   ├── avr.py
│   └── drift.py
│
└── reports/
    └── milestone0/
```

## Core Contract

All baselines MUST accept:

```python
evaluate(instance)
```

and return:

```python
{
    "decision": "commit|reject",
    "committed_state": {},
    "reason": "",
    "audit": {}
}
```

The comparison object must remain constant:

```text
same instance
same evidence
same proposal
different admission policy
```

## First Instance Schema

The minimal instance schema is:

```json
{
  "id": "stfb_0001",
  "state_t": {},
  "proposal": {},
  "evidence": {},
  "authority": {},
  "expected_transition": {}
}
```

The core separations are:

```text
evidence != authority
proposal != state
confidence != permission
```

## Metrics

Milestone 0 computes only the following metrics:

### IAR

Invalid Admission Rate

```text
invalid commits / total commits
```

### AVR

Authority Violation Rate

```text
authority violating commits / total commits
```

### Drift

State deviation

```text
distance(final_state, valid_state)
```

## Milestone 0 Success Criteria

Milestone 0 is an engineering validation, not a paper result.

It must be possible to generate:

```text
instance
↓
Direct Mutation result
↓
Confidence Threshold result
↓
SRP result
↓
metrics comparison
↓
JSON report
```

Recommended report artifact:

```text
reports/milestone0_report.json
```

## Recommended Implementation Order

### Commit 1

Skeleton:

```text
STFB/
 runner/
 baselines/
 metrics/
```

Include:

- `contracts.py`

### Commit 2

Handcrafted episodes:

- 10 to 30 instances

Goal:

- validate that the failure taxonomy is executable

### Commit 3

Metric engine:

- `IAR`
- `AVR`
- `Drift`

### Commit 4

Synthetic generator:

- 100 instances
- 1000 instances

### Commit 5

Long horizon:

```text
S0 -> S1 -> S2 -> ... -> Sn
```

Goal:

- validate drift accumulation

## Research Discipline

Milestone 0 must not attempt to prove that SRP is strong.
Its only goal is to show that semantic transition failures are measurable under controlled admission policies.

STFB only becomes the benchmark surface after this contract is operational.

## Freeze Statement

This specification defines the Milestone 0 implementation contract only.
It does not redefine STFB v0.1, SRP v1.0, or any future benchmark version.
