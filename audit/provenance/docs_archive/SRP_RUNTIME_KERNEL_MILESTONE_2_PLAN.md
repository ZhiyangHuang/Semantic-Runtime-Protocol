# SRP Runtime Kernel Milestone 2 Plan

This document freezes the next kernel-stage reference goals after the Milestone 1 runtime loop is stable.
It is not an implementation spec.

Milestone 2 upgrades the kernel from a deterministic event executor into a semantic evolution runtime that can:

- choose among candidate operators
- manage semantic version commits
- support checkpoints for faster replay

The milestone is intentionally narrow.
It does not add new mutation operators.

---

## 1. Milestone 2 Goals

Milestone 2 should prove that SRP can manage a long-running semantic world, not just execute isolated transitions.

The milestone is organized around three kernel-level capabilities:

1. Runtime Decision Boundary
2. Semantic Commit / Version Runtime
3. Runtime Checkpoint Model

These capabilities sit on top of the Milestone 1 event, constraint, operator, trace, and replay substrate.

---

## 2. Runtime Decision Boundary

Milestone 1 currently binds an event to an operator too directly through `operator_name`.

Milestone 2 should introduce an explicit decision boundary:

```text
RuntimeEvent
      |
      v
Decision Context
      |
      v
Candidate Operators
      |
      v
Constraint Filter
      |
      v
Metric Evidence
      |
      v
Selected Operator
      |
      v
Transition
```

### Purpose

The decision boundary is not policy learning.
It is a deterministic or rule-based operator selector that can:

- inspect event type
- inspect state conditions
- inspect constraint availability
- inspect metric evidence

### Example decision scenario

```text
semantic conflict detected

candidate operators:
  - Merge
  - Split
  - IdentityUpdate

constraint result:
  - Merge allowed
  - Split forbidden

metric evidence:
  - similarity = 0.91

selected operator:
  - Merge
```

### Non-goals

- learned operator policies
- neural ranking
- automatic strategy search
- embedding-based control flow

---

## 3. Semantic Commit / Version Runtime

Milestone 1 already tracks versions as references.
Milestone 2 should make version progression a first-class runtime concern.

### Semantic commit concept

```python
@dataclass
class SemanticCommit:
    commit_id: str
    parent_version: str | None
    new_version: str
    event_id: str
    transition_id: str
    trace_id: str | None = None
```

### Purpose

The commit layer should:

- bind transitions to version history
- support version branching
- support merge and split lineage over versions
- make rollback/checkpoint semantics explicit

### Version runtime responsibilities

- assign new semantic versions on commit
- preserve parent version references
- maintain a version DAG
- expose branch-aware replay and audit references

### Non-goals

- replacing replay with version checkout
- encoding semantic meaning directly into storage format
- changing lifecycle semantics

---

## 4. Runtime Checkpoint Model

Milestone 1 replay is event-stream driven.
Milestone 2 should add checkpoints so replay can start from a validated intermediate semantic state.

### Checkpoint concept

```python
@dataclass
class RuntimeCheckpoint:
    checkpoint_id: str
    state_ref: str
    version_id: str
    event_offset: int
    metric_snapshot: dict[str, object] = field(default_factory=dict)
```

### Purpose

Checkpoints should:

- accelerate replay of long event streams
- support bounded recovery start points
- preserve determinism
- expose state anchors for audit and debugging

### Replay relationship

```text
Checkpoint
      |
      v
Replay Start Point

Event Delta
      |
      v
Delta Reconstruction
```

Replay must still be deterministic.
Checkpointing is only an optimization and an explicit replay anchor.

### Non-goals

- replacing event history
- mutating semantic meaning
- making checkpoints a substitute for events

---

## 5. Milestone 2 Kernel Shape

Milestone 2 should keep the Milestone 1 loop intact:

```text
Event
  -> Metric Evidence
  -> Constraint
  -> Operator
  -> TransitionResult
  -> TraceRecord
  -> ReplayResult
```

And extend it with:

```text
Event
  -> Decision Boundary
  -> Candidate Selection
  -> Commit
  -> Checkpoint
  -> Replay Anchor
```

The kernel should remain passive with respect to policy learning.

---

## 6. Suggested Milestone 2 Deliverables

The next reference artifacts should be:

- `SRP_RUNTIME_DECISION_BOUNDARY_MODEL.md`
- `SRP_SEMANTIC_COMMIT_MODEL.md`
- `SRP_RUNTIME_CHECKPOINT_MODEL.md`

They should be produced in that order, because commit semantics depend on a selected transition, and checkpoint semantics depend on stable commits.

These documents should freeze the contracts before any implementation changes are made.

---

## 7. Milestone Exit Criteria

Milestone 2 is complete when SRP can demonstrate:

- operator choice is explicit and bounded
- version commits form a semantic DAG
- checkpoints accelerate replay without changing replay semantics
- trace and replay remain stable across long-running evolution

For the implementation bridge, see [SRP Runtime Kernel Milestone 2 Implementation Checklist](SRP_RUNTIME_KERNEL_MILESTONE_2_IMPLEMENTATION_CHECKLIST.md).
For the first integration evidence, see [SRP Runtime Kernel Milestone 2 Integration Validation](SRP_RUNTIME_KERNEL_MILESTONE_2_INTEGRATION_VALIDATION.md).
For branching evidence, see [SRP Runtime Kernel Milestone 2 Branching Validation](SRP_RUNTIME_KERNEL_MILESTONE_2_BRANCHING_VALIDATION.md).
For the branch disagreement boundary, see [SRP Version Conflict Model](SRP_VERSION_CONFLICT_MODEL.md).
For the current verified snapshot, see [SRP Runtime Kernel Milestone 2 Status Summary](SRP_RUNTIME_KERNEL_MILESTONE_2_STATUS_SUMMARY.md).
