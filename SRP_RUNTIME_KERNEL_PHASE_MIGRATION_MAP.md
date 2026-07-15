# SRP Runtime Kernel Phase Migration Map

This document maps the first migration targets for SRP as it evolves from the experimental implementation into a runtime kernel architecture.
It is a phase-oriented migration map, not an implementation spec.

The central question is:

> If SRP migrates into a runtime kernel step by step, which state transitions should be controlled first in each phase?

This document sits on top of the callsite map and below the migration checklist.

---

## 1. Phase Migration Overview

```text
Phase 0
  Observation

Phase 1
  Event Wrapping

Phase 2
  Mutation Routing

Phase 3
  Lifecycle Migration

Phase 4
  Replay Enablement
```

Each phase has a different risk profile and a different migration goal.

---

## 2. Phase 0 - Observation Layer

### Goal

Observe runtime behavior without changing behavior.

### What to capture

- current state changes
- mutation sources
- lifecycle transitions
- recovery decisions
- validation outcomes

### Priority callsites

| Callsite | Current Behavior | Future Role |
| --- | --- | --- |
| `pipeline.py::run_srp` | runtime coordinator | Event Observer |
| `compress.py::compress_state` | compression decision and package construction | Decision Observer |
| `recover.py::recover_state` | recovery dispatch and result shaping | Recovery Observer |
| `validate.py::validate_state` | validation evaluation | Validation Observer |
| `pipeline_runtime.py::compute_semantic_metrics` | drift and stability measurement | Metrics Observer |

### Expected output

```text
ObservedMutationEvent
```

### Forbidden in this phase

- mutating semantic state
- changing policy behavior
- changing recovery logic

### Exit condition

```text
Current runtime behavior can be observed without changing outcomes
```

---

## 3. Phase 1 - Event Wrapping

### Goal

Wrap implicit changes as `RuntimeEvent` proposals.

### First-priority callsites

#### `semantic_parser.py`

Current:

```text
text
  -> SemanticState projection
```

Future:

```text
Raw Input
  -> SemanticExtracted
  -> State Transition
```

#### `compress.py`

Current:

```text
compress_state()
```

Future:

```text
CompressionSelected
  -> CompressedPackageProduced
```

#### `recover.py`

Current:

```text
recover_state()
```

Future:

```text
RecoveryRequested
  -> RecoveryResultProduced
```

### Event wrapping rule

Implicit runtime actions must be representable as event proposals before they can be routed through the kernel.

### Exit condition

```text
Runtime behavior can be represented as events
```

---

## 4. Phase 2 - Mutation Routing

### Goal

All semantic mutations pass through the kernel boundary.

### Primary hot spots to cut over first

#### Lifecycle mutation

Current pattern:

```text
unit.lifecycle_state = "archived"
```

Target pattern:

```text
LifecycleTransitionRequested
  -> validate_event()
  -> apply_event()
```

#### Recovery materialization

Current pattern:

```text
recover_runtime.py
  -> build_recovered_state()
```

Risk:

- recovery directly creates a new state artifact

Target pattern:

```text
RecoveredCandidateCreated
  -> ValidationPerformed
  -> RecoveryApplied
```

#### Validation repair

Validation may trigger repair, but validation itself must not mutate state.

Target rule:

```text
Validation
  != Mutation
```

### Routing rule

```text
module
  -> RuntimeEvent
  -> Kernel
  -> State mutation
```

### Exit condition

```text
No uncontrolled state transition exists
```

---

## 5. Phase 3 - Lifecycle Migration

### Goal

Make lifecycle evolution fully event-driven.

### Rule-to-event mapping

| Rule | Event |
| --- | --- |
| Activation Decay | `ActivationUpdated` |
| Approximation | `Approximated` |
| Soft Forgetting | `Forgotten` |
| Consolidation | `Consolidated` |
| Recovery | `Recovered` |

### Migration target

```text
Evolution Rule
  -> Runtime Event
  -> Kernel Mutation
```

### Exit condition

```text
Semantic evolution becomes event-driven
```

---

## 6. Phase 4 - Replay Enablement

### Goal

The event stream must be sufficient to reconstruct semantic state evolution.

### Replay requirement

```text
Replay(EventStream)
  ~= Original Runtime State
```

### Replay should support

- drift calculation
- identity loss analysis
- structural degradation analysis
- recovery divergence analysis

### Exit condition

```text
Replay can reconstruct the semantic evolution path deterministically enough for attribution and debugging
```

---

## 7. Semantic Evolution Trace

The migration phases need a trace model that records how a unit evolves over time.

This trace is not the same as a summary.
It records the causal path of semantic change.

Example:

```text
SemanticUnit A

round 1:
  SemanticExtracted

round 20:
  ActivationUpdated

round 80:
  Approximated

round 120:
  Forgotten

round 150:
  RecoveryRequested

round 151:
  Recovered
```

The trace is the evidence that semantic continuity was preserved, degraded, or restored over time.

---

## 8. Migration Priority

Recommended order:

1. Observation
2. Event Wrapping
3. Mutation Routing
4. Lifecycle Migration
5. Replay Enablement

This order reduces risk and preserves experimental evidence.

---

## 9. Relationship to Other Documents

Recommended chain:

```text
Runtime Kernel Interface
  -> Runtime Kernel API Map
  -> Runtime Kernel Adapter Plan
  -> Runtime Kernel Migration Checklist
  -> Kernel Callsite Map
  -> Runtime Kernel Phase Migration Map
  -> Semantic Evolution Trace Model
```

---

## 10. Scope

This document defines phase-oriented migration targets only.

It does not define:

- code changes
- adapter implementation
- function-level callsites
- kernel internals

Those belong to later implementation work.

