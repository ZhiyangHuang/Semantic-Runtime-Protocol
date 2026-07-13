# SRP Runtime Kernel Milestone 2 Implementation Checklist

This document freezes the implementation boundary for Milestone 2.
It is a bridge between the theory-level Milestone 2 models and the first reference implementation interfaces.

Milestone 2 extends the runtime kernel with:

- a decision boundary for operator selection
- a semantic commit layer for version history
- a checkpoint layer for replay acceleration

It does not add new mutation operators.

---

## 1. Milestone 2 Implementation Scope

Milestone 2 should introduce the following reference modules:

```text
srp_runtime/

decision/
    decision_context.py
    operator_selector.py
    decision_result.py

commit/
    semantic_commit.py
    commit_manager.py

version/
    version_graph.py
    version_node.py

checkpoint/
    runtime_checkpoint.py
    checkpoint_manager.py
```

### Scope principle

These modules are orchestration and boundary modules.
They should not absorb the full runtime kernel into one class.

---

## 2. RuntimeKernel Responsibility Boundary

Milestone 2 should not turn `RuntimeKernel` into a monolith.
The kernel should remain the orchestrator that coordinates specialized services.

### Kernel should orchestrate

- operator selection
- constraint validation
- transition execution
- commit creation
- trace recording
- checkpoint creation

### Kernel should not directly own

- policy learning
- autonomous operator discovery
- checkpoint storage internals
- version conflict resolution
- archive compaction logic

### Recommended shape

```text
RuntimeKernel
    |
    +-- DecisionEngine
    +-- ConstraintEngine
    +-- Operator
    +-- CommitManager
    +-- TraceBuilder
    +-- CheckpointManager
```

---

## 3. First Milestone 2 Interfaces

The first implementation pass should freeze these interfaces:

### DecisionEngine

```python
select_operator(
    event,
    state
) -> DecisionResult
```

### CommitManager

```python
commit_transition(
    transition_result,
    trace_record
) -> SemanticCommit
```

### CheckpointManager

```python
create_checkpoint(
    semantic_commit,
    state_ref
) -> RuntimeCheckpoint
```

### Supporting objects

- `DecisionContext`
- `OperatorCandidate`
- `DecisionResult`
- `SemanticCommit`
- `RuntimeCheckpoint`

---

## 4. Explicit Non-Goals

Milestone 2 must remain narrow.

### Do not implement

- policy learning
- autonomous operator discovery
- distributed checkpoint storage
- persistent archive engine
- version conflict resolution automation
- rollback automation

### Do not blur boundaries

- decision is not commit
- commit is not checkpoint
- checkpoint is not replay history
- replay is not archive lookup

---

## 5. Verification Targets

Milestone 2 should be validated with three core experiments.

### 5.1 Decision determinism

```text
Event + State
      |
      v
same DecisionResult
```

### 5.2 Commit consistency

```text
TransitionResult
      |
      v
SemanticCommit
      |
      v
VersionGraph
```

The references must remain consistent.

### 5.3 Checkpoint replay equivalence

Without checkpoint:

```text
Replay(Event1...N)
```

With checkpoint:

```text
Checkpoint(K)
  +
Replay(EventK...N)
```

Both paths must reconstruct the same final state.

---

## 6. Milestone Exit Criteria

Milestone 2 is complete when SRP demonstrates:

- operator selection is explicit and bounded
- semantic commits form a version DAG
- checkpoints accelerate replay without changing replay semantics
- the kernel remains an orchestrator rather than a monolithic execution engine

---

## 7. Next Reference Artifact

After this checklist, the next stable interface document should be:

- `SRP_RUNTIME_KERNEL_MILESTONE_2_REFERENCE_INTERFACE_SPEC.md`

This checklist exists to keep that interface document small and stable.
