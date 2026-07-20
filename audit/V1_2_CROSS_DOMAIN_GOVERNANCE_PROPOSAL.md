# SRP v1.2 Cross-Domain Governance Proposal

## Status

Branch:
`v1.2-cross-domain-governance`

Purpose:
Define the first cross-domain governance research boundary for SRP without
modifying the frozen claim boundary established in v1.0 or the evidence
protocol frozen in v1.1.

This document is a research boundary specification, not an implementation plan.

## Motivation

v1.1 establishes that semantic transition governance can be evaluated under
frozen runtime contracts with reproducible evidence artifacts.

The next question is whether the same governance contract remains stable across
different semantic transition pressure sources.

## Research Questions

### RQ1: Transition Role Consistency

Do different source families map to distinct and stable transition roles?

Target source families:

- LongMemEval
- LoCoMo
- AgentBench
- reasoning sources

### RQ2: Governance Invariant Consistency

When the source family changes, do the following remain stable?

- Evidence != Authority
- Recommendation != Execution
- Replay consistency
- Artifact provenance

### RQ3: Diagnostic Transferability

Can the same SRP diagnostics characterize governance behavior across multiple
source families without collapsing into benchmark scoring?

## Scope Candidates

### 1. Cross-Domain Source Routing

Current v1.1 flow:

```text
external record
    |
    v
adapter
    |
    v
BoundaryCase
    |
    v
BoundaryDecision
```

Possible v1.2 direction:

```text
external record
    |
    v
transition_role
    |
    v
adapter routing
    |
    v
BoundaryCase
    |
    v
BoundaryDecision
```

Research question:

> Can a frozen governance contract remain interpretable when multiple source
> families generate distinct semantic transition pressures?

This is cross-domain routing and invariance checking, not benchmark comparison.

### 2. Shared Governance Diagnostics

Possible v1.2 direction:

```text
official scorer
    |
    v
task metric

SRP diagnostics
    |
    v
governance observables
```

Research question:

> Can the same governance diagnostics remain meaningful across external source
> families while the official scorer stays dataset-specific?

This is diagnostic transfer, not task-score aggregation.

### 3. Protocol Invariance Under Source Variation

Possible v1.2 direction:

```text
source family A -> governed transition evaluation
source family B -> governed transition evaluation
source family C -> governed transition evaluation
```

Research question:

> Are the frozen SRP governance invariants stable under variation in semantic
> transition source family?

This is protocol invariance, not a claim of universal model superiority.

## Explicit Non-Goals

v1.2 does not introduce:

- a new memory architecture
- retrieval optimization methods
- autonomous semantic mutation
- learned authority mechanisms
- benchmark leaderboard objectives
- benchmark catalog expansion as a primary goal

## Compatibility Requirements

Any v1.2 work must preserve:

| Requirement | Meaning |
| --- | --- |
| Authority separation | evidence cannot create authority |
| Replayability | decisions remain auditable |
| Artifact provenance | results remain traceable |
| Frozen evaluation contracts | comparisons remain controlled |
| Transition role semantics | source families remain routing metadata |

## Migration Rule

Version responsibilities:

- v1.0: definition layer
- v1.1: evidence reproducibility layer
- v1.2: extension research layer

Existing v1.0 and v1.1 artifacts are immutable references.

## Release Decision

No implementation work should mutate the frozen v1.0 or v1.1 boundary records.

Any future implementation should begin from this proposal note and produce a
new milestone record before adding code or data.
