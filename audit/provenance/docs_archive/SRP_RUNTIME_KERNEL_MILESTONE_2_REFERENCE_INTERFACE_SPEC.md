# SRP Runtime Kernel Milestone 2 Reference Interface Spec

This document freezes the first Milestone 2 reference interfaces for SRP.
It is a contract layer, not an implementation spec.

Milestone 2 extends the Milestone 1 runtime reference surface with three bounded capabilities:

- operator selection through a decision boundary
- semantic commit creation for version history
- checkpoint creation for replay acceleration

The Milestone 1 ABI remains unchanged.

---

## 1. Scope

Milestone 2 freezes only the interfaces needed to:

- decide which operator to apply
- record the accepted transition as a semantic commit
- anchor replay with checkpoints
- preserve explicit references between decision, transition, commit, version, and checkpoint

### Explicit non-goals

- policy learning
- autonomous operator discovery
- distributed checkpoint storage
- persistent archive engine
- version conflict resolution automation
- rollback automation
- hidden mutation routing

---

## 2. Reference Package Boundary

The Milestone 2 reference implementation should extend `srp_runtime/` with these modules:

```text
srp_runtime/

decision/
    decision_context.py
    operator_candidate.py
    decision_result.py
    decision_engine.py

commit/
    semantic_commit.py
    commit_manager.py

version/
    version_node.py
    version_graph.py

checkpoint/
    runtime_checkpoint.py
    checkpoint_manager.py
```

### Boundary principle

These modules should remain thin and reference-first.
They coordinate runtime responsibilities without absorbing the full kernel into one monolith.

---

## 3. Decision Domain Interface

The decision domain selects an operator before transition execution.

### 3.1 `DecisionContext`

`DecisionContext` contains the bounded runtime inputs needed for operator selection.

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionContext:
    event_ref: str
    state_ref: str
    available_operators: list[str] = field(default_factory=list)
    constraint_context: dict[str, Any] = field(default_factory=dict)
    semantic_time: int = 0
    version_id: str = ""
    lifecycle_state: str = "active"
    metric_snapshot_ref: str | None = None
```

#### Required invariants

- `event_ref` and `state_ref` must be reference-only
- `available_operators` must be bounded by the runtime
- `semantic_time` must be monotonic within a branch
- the context must not contain a full semantic state copy

### 3.2 `OperatorCandidate`

`OperatorCandidate` describes an operator that may be selected.

```python
@dataclass
class OperatorCandidate:
    operator_name: str
    applicability: bool
    required_constraints: list[str] = field(default_factory=list)
    metric_requirements: list[str] = field(default_factory=list)
    rationale: str | None = None
```

#### Semantics

- `applicability` indicates whether the operator can be considered at all
- `required_constraints` specifies the constraints that must hold
- `metric_requirements` specifies the evidence the candidate depends on
- `rationale` explains why the candidate entered the set

### 3.3 `DecisionResult`

`DecisionResult` records the selected operator and the evidence for that selection.

```python
@dataclass
class DecisionResult:
    decision_id: str
    event_id: str
    selected_operator: str | None
    candidate_operators: list[str] = field(default_factory=list)
    accepted_candidates: list[str] = field(default_factory=list)
    rejected_candidates: list[str] = field(default_factory=list)
    constraint_evidence_refs: list[str] = field(default_factory=list)
    metric_evidence_refs: list[str] = field(default_factory=list)
    explanation: str = ""
    success: bool = False
    semantic_time: int = 0
    version_id: str = ""
```

#### Semantics

`DecisionResult` must answer:

- which operator was selected
- which operators were considered
- which operators were rejected
- which constraints were decisive
- which metric evidence was used
- why the selection was made

#### Non-goals

- it is not the transition result
- it is not the commit
- it is not the trace
- it is not the state mutation itself

### 3.4 `DecisionEngine`

The decision engine owns operator selection.

```python
class DecisionEngine:
    def select_operator(
        self,
        event,
        state
    ) -> DecisionResult:
        ...
```

#### Responsibilities

- generate candidate operators
- apply constraint filtering
- incorporate metric evidence
- return an explainable decision result

#### Non-goals

- mutation execution
- commit creation
- checkpoint creation
- archive lookup
- learning-based ranking

---

## 4. Commit Domain Interface

The commit domain turns an accepted transition into a semantic history node.

### 4.1 `SemanticCommit`

`SemanticCommit` is the reference object that anchors an accepted transition into the version history.

```python
@dataclass
class SemanticCommit:
    commit_id: str
    parent_version_id: str | None
    new_version_id: str
    event_id: str
    decision_id: str | None
    transition_id: str
    trace_id: str | None = None
    state_ref: str | None = None
    version_ref: str | None = None
    semantic_time: int = 0
    commit_reason: str | None = None
    author_context: str | None = None
```

#### Required invariants

- `commit_id` is stable and referenceable
- `parent_version_id` is explicit when present
- `new_version_id` identifies the accepted semantic version
- `event_id`, `decision_id`, and `transition_id` preserve lineage to the runtime action
- `state_ref` remains reference-only

#### Non-goals

- storing the full state
- replacing replay
- replacing trace
- acting as a checkpoint

### 4.2 `CommitManager`

The commit manager creates semantic commits from validated transitions.

```python
class CommitManager:
    def commit_transition(
        self,
        transition_result,
        trace_record,
        decision_result
    ) -> SemanticCommit:
        ...
```

#### Responsibilities

- validate commit eligibility
- create a commit record
- bind the commit to a version node
- preserve references to decision, transition, and trace artifacts

#### Non-goals

- replay execution
- mutation execution
- state validation
- checkpoint storage

---

## 5. Version Domain Interface

The version domain manages the semantic version DAG.

### 5.1 `SemanticVersionNode`

```python
@dataclass
class SemanticVersionNode:
    version_id: str
    parent_versions: list[str] = field(default_factory=list)
    commit_id: str = ""
    state_ref: str = ""
    created_round: int = 0
```

#### Semantics

- one node per accepted semantic version
- parent versions are explicit
- state reference remains reference-only

### 5.2 `SemanticVersionGraph`

The version graph manages nodes and edges only.

```python
class SemanticVersionGraph:
    def add_version(self, node: SemanticVersionNode) -> None:
        ...

    def get_version(self, version_id: str) -> SemanticVersionNode:
        ...

    def parents(self, version_id: str) -> list[SemanticVersionNode]:
        ...

    def children(self, version_id: str) -> list[SemanticVersionNode]:
        ...
```

#### Forbidden responsibilities

- operator selection
- event execution
- checkpoint storage
- archive lookup

---

## 6. Checkpoint Domain Interface

The checkpoint domain anchors replay acceleration.

### 6.1 `RuntimeCheckpoint`

```python
@dataclass
class RuntimeCheckpoint:
    checkpoint_id: str
    version_id: str
    commit_id: str
    state_ref: str
    event_offset: int
    created_round: int = 0
    parent_checkpoint_id: str | None = None
    replay_boundary: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

#### Semantics

- checkpoint is a replay acceleration artifact
- checkpoint is not a semantic history artifact
- checkpoint is not a substitute for event history

### 6.2 `CheckpointManager`

```python
class CheckpointManager:
    def create_checkpoint(
        self,
        semantic_commit: SemanticCommit,
        state_ref: str,
        event_position: int
    ) -> RuntimeCheckpoint:
        ...

    def find_checkpoint(self, version_id: str) -> RuntimeCheckpoint | None:
        ...
```

#### Responsibilities

- create replay anchors
- validate checkpoint metadata
- resolve checkpoint by version

#### Non-goals

- event replay execution
- semantic mutation
- archive evidence discovery

---

## 7. Runtime Flow

Milestone 2 integrates through an optional overlay, not by replacing the Milestone 1 kernel path.

### Kernel overlay

```python
@dataclass
class RuntimeKernelConfig:
    enable_decision_layer: bool = False
    enable_commit_layer: bool = False
    enable_checkpoint_layer: bool = False


@dataclass
class RuntimeServices:
    decision_engine: DecisionEngine | None = None
    commit_manager: CommitManager | None = None
    checkpoint_manager: CheckpointManager | None = None
```

Milestone 2 extends the Milestone 1 runtime loop with explicit decision, commit, and checkpoint boundaries.

```text
RuntimeEvent
      |
      v
DecisionEngine
      |
      v
DecisionResult
      |
      v
ConstraintEngine
      |
      v
Operator
      |
      v
TransitionResult
      |
      v
TraceBuilder
      |
      v
CommitManager
      |
      v
SemanticCommit
      |
      v
SemanticVersionGraph
      |
      v
CheckpointManager
```

### Interpretation

- decision chooses the operator
- constraint confirms legality
- operator executes the transition
- trace explains the transition
- commit accepts the transition into history
- version graph records the accepted history
- checkpoint marks an efficient replay anchor

---

## 8. Compatibility with Milestone 1

Milestone 2 must not alter the Milestone 1 ABI.

### Unchanged contracts

- `RuntimeEvent`
- `TransitionResult`
- `TraceRecord`
- `ReplayResult`

### Extension principle

Milestone 2 adds reference layers on top of the existing runtime loop.
It does not rewrite the Milestone 1 contract surface.

---

## 9. Verification Targets

The reference interface should support the following Milestone 2 checks:

### Decision determinism

```text
Event + State
      |
      v
same DecisionResult
```

### Commit consistency

```text
TransitionResult
      |
      v
SemanticCommit
      |
      v
VersionGraph
```

### Checkpoint replay equivalence

```text
Checkpoint(K) + Replay(EventK...N) = Replay(Event1...N)
```

The final state must be equivalent.
