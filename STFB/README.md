# Semantic Transition Failure Benchmark (STFB)

## Overview

Semantic Transition Failure Benchmark (STFB) is an independent benchmark and reproduction package for evaluating failures in semantic runtime state transitions.

STFB studies a specific question:

> When semantic systems modify runtime state, what failures occur without an explicit admission boundary?

The benchmark focuses on transition safety rather than retrieval quality or generation accuracy.

## Relationship with SRP

STFB and SRP are intentionally separated.

STFB defines the evaluation problem:

```text
What semantic transition failures should be measured?
```

SRP provides one possible governance approach:

```text
How can semantic transitions be governed?
```

Relationship:

```text
STFB
 |
 v
Semantic Transition Governance Problem
 |
 +----------------+
 |                |
SRP        Other Admission Methods
```

STFB is not an SRP internal benchmark.
It is designed as a general evaluation framework for semantic transition governance methods.

## Specifications

The current core planning stack is:

- Benchmark specification: [Semantic Transition Failure Benchmark v0.1](../paper/docs/plans/STFB_SPEC.md)
- Roadmap: [STFB Roadmap](../paper/docs/plans/STFB_ROADMAP.md)
- Governance plan: [Governance Plan](../paper/docs/plans/GOVERNANCE_PLAN.md)

## Current Status

Version:

```text
STFB v0.1
```

Status:

- Specification: frozen
- Dataset: not released
- Baseline implementations: reference implementations available
- Evaluation runner: reference runner available

Current specification:

- [Semantic Transition Failure Benchmark v0.1](../paper/docs/plans/STFB_SPEC.md)

## Scope

STFB evaluates:

- invalid semantic mutations
- evidence-authority confusion
- conflicting semantic sources
- temporal regression
- provenance loss
- rollback failures

The benchmark measures:

- Invalid Acceptance Rate (IAR)
- Authority Violation Rate (AVR)
- Authorized Retention Rate (ARR)
- Semantic Drift
- Audit Completeness
- Runtime Cost

## Future Development

Planned phases:

### v0.1

Specification and problem definition.

### v0.2

Dataset construction and validation.

### v0.3

Baseline implementation and evaluation.

### v1.0

Public benchmark release.

## Implementation

The implementation path is tracked separately from the frozen specifications.

Roadmap:

- [STFB Roadmap](../paper/docs/plans/STFB_ROADMAP.md)

## External Validation

STFB provides a clean external validation track for evaluating semantic transition failures in existing benchmark environments and for letting outside users reproduce or adapt the benchmark under the frozen contract.

The external validation track does not modify the core STFB benchmark definition.

Specification:

- [Frozen benchmark specification](../paper/docs/plans/STFB_SPEC.md)
- [External validation boundary](../paper/docs/plans/STFB_SPEC.md)

Current status:

- Specification: frozen v0.1
- Initial environments:
  - LongMemEval
  - ARC
- Implementation: deferred

## License / Contribution

This repository currently contains only the benchmark specification and project structure.
Implementation and dataset release will follow future versions.
