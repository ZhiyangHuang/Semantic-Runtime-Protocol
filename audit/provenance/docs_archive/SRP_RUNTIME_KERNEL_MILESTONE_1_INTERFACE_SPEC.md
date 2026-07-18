# SRP Runtime Kernel Milestone 1 Interface Spec

This document freezes the first reference-implementation API contract for SRP.
It is not an implementation and not a theory expansion.

The goal is to define the smallest stable set of Python-facing interfaces that can realize the minimal runtime kernel plan.

The reference package boundary is:

```text
srp_runtime/
  kernel/
  semantic/
  event/
  constraints/
  metric/
  trace/
  replay/
```

---

## 1. Scope

Milestone 1 freezes only the interfaces needed to:

- represent atomic semantic objects
- represent runtime events
- validate transitions
- execute minimal operators
- record trace evidence
- replay event streams deterministically

This milestone does not include:

- policy learning
- automatic evolution strategy search
- embedding generation
- retrieval orchestration
- graph database integration
- full learned consolidation / recovery strategy

---

## 2. Semantic Core Interfaces

### 2.1 `SemanticUnit`

`SemanticUnit` is the smallest evolvable semantic object.

It owns identity, payload, and runtime-facing attributes, but not full history.

```python
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SemanticUnit:
    unit_id: str
    canonical_name: str
    aliases: list[str] = field(default_factory=list)
    lineage: list[str] = field(default_factory=list)
    provenance: list[str] = field(default_factory=list)
    semantic_payload: dict[str, Any] = field(default_factory=dict)
    activation: float = 0.0
    confidence: float = 0.0
    lifecycle_state: str = "active"
    drift_score: float = 0.0
    last_used_round: int = 0
    updated_round: int = 0
    decay_state: str = "stable"
    approximation_target: str | None = None
    relation_ids: list[str] = field(default_factory=list)
    version_id: str = ""
```

#### Required invariants

- `unit_id` is immutable once created
- `canonical_name` may change through authorized transitions
- `aliases` must remain deduplicated
- `activation` and `confidence` are controlled numeric fields
- `lineage` and `provenance` are append-only semantic histories
- `last_used_round` and `updated_round` track semantic time
- full history is not stored on the unit itself

---

### 2.2 `SemanticGraph`

`SemanticGraph` stores semantic relations between units.

It does not generate embeddings, decide merges, or perform GC automatically.

```python
@dataclass
class GraphTransitionResult:
    before_version_id: str
    after_version_id: str
    changed_unit_ids: list[str]
    changed_relation_ids: list[str]
    event_ids: list[str]


class SemanticGraph:
    def get_node(self, unit_id: str) -> SemanticUnit:
        ...

    def neighbors(self, unit_id: str) -> list[SemanticUnit]:
        ...

    def apply_operator(self, operator: "SemanticOperator") -> GraphTransitionResult:
        ...
```

#### Forbidden responsibilities

- embedding generation
- implicit merge decisions
- automatic garbage collection

---

### 2.3 `SemanticState`

`SemanticState` is the current versioned semantic runtime container.

```python
@dataclass
class SemanticState:
    state_id: str
    units: dict[str, SemanticUnit]
    graph: SemanticGraph
    version_id: str
    timestamp_round: int
```

Optional future fields may include runtime metadata views, but Milestone 1 should keep the state object compact and explicit.

---

## 3. Event Layer Interfaces

### 3.1 `RuntimeEvent`

`RuntimeEvent` describes a legal or proposed semantic transition.

It does not execute the transition itself.

```python
@dataclass
class RuntimeEvent:
    event_id: str
    event_type: str
    schema_version: str
    causal_parent: str | None
    actor: str
    targets: list[str]
    payload: dict[str, Any]
    mutation_mode: str
    operator_name: str | None = None
    confidence: float = 1.0
```

#### Required invariants

- events are immutable after creation
- an event only describes a transition
- no `event.execute()` method is allowed in the event object
- `causal_parent` is optional but preferred when causal ancestry exists
- `operator_name` may explicitly bind the event to a runtime operator

### 3.2 Suggested event types for Milestone 1

The first milestone only needs a small set of event types:

- `IdentityUpdated`
- `ActivationUpdated`
- `RelationUpdated`
- `SemanticExtracted`
- `ValidationPerformed`
- `Merged`
- `Split`
- `Approximated`
- `Recovered`
- `Forgotten`
- `GarbageCollected`

The milestone does not need full consolidation or recovery event families yet.

---

## 4. Constraint Layer Interfaces

### 4.1 `ConstraintResult`

```python
@dataclass
class ConstraintResult:
    accepted: bool
    violations: list[str]
```

### 4.2 `ConstraintEngine`

`ConstraintEngine` decides whether an event is allowed to proceed.

```python
class ConstraintEngine:
    def validate(self, state: SemanticState, event: RuntimeEvent) -> ConstraintResult:
        ...
```

#### Responsibilities

- identity constraints
- relation endpoint checks
- semantic type compatibility checks
- lifecycle transition legality
- runtime invariant checks

#### Forbidden responsibilities

- policy selection
- candidate ranking
- state mutation
- trace recording

---

## 5. Operator Layer Interfaces

### 5.1 `SemanticOperator`

Milestone 1 should expose a minimal operator interface.

```python
class SemanticOperator:
    def apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        ...
```

### 5.2 First operator family

The first milestone should only require these operator families:

- `IdentityUpdateOperator`
- `ActivationUpdateOperator`
- `RelationUpdateOperator`
- `MergeOperator`
- `ApproximationOperator`
- `SplitOperator`
- `RecoveryOperator`
- `ForgettingOperator`
- `GarbageCollectionOperator`

These operators may be simple and rule-driven.

#### Out of scope for Milestone 1

- version checkout / rollback

Those operators depend on a broader operator algebra and richer semantic metric behavior.

---

## 6. Kernel Layer Interfaces

### 6.1 `EventResult`

```python
@dataclass
class EventResult:
    event_id: str
    status: str
    reason: str | None = None
    affected_units: list[str] = field(default_factory=list)
```

### 6.2 `ValidationResult`

```python
@dataclass
class ValidationResult:
    event_id: str
    accepted: bool
    violations: list[str] = field(default_factory=list)
```

### 6.3 `TransitionResult`

```python
@dataclass
class TransitionResult:
    transition_id: str
    event_id: str
    operator_name: str
    before_state_ref: str
    after_state_ref: str
    changed_unit_ids: list[str] = field(default_factory=list)
    changed_relation_ids: list[str] = field(default_factory=list)
    mutation_summary: dict[str, Any] = field(default_factory=dict)
    invariant_checks: list[str] = field(default_factory=list)
    metric_evidence_ref: str | None = None
    metric_evidence: dict[str, Any] | None = None
    success: bool = False
    failure_reason: str | None = None
    timestamp_round: int = 0
```

### 6.4 `SemanticStateView`

```python
@dataclass
class SemanticStateView:
    state_id: str
    version_id: str
    timestamp_round: int
    unit_ids: list[str]
    graph_summary: dict[str, Any] = field(default_factory=dict)
```

### 6.5 `RuntimeKernel`

The reference kernel should expose a small public API:

```python
class RuntimeKernel:
    def submit_event(self, event: RuntimeEvent) -> EventResult:
        ...

    def validate_event(self, event: RuntimeEvent) -> ValidationResult:
        ...

    def apply_event(self, event: RuntimeEvent) -> TransitionResult:
        ...

    def get_state(self) -> SemanticStateView:
        ...
```

#### Kernel execution order

The internal order should be fixed:

```text
submit_event
  -> validate_event
  -> ConstraintEngine
  -> Metric evaluation
  -> Operator application
  -> State transition
  -> Commit
  -> Trace recording
```

The kernel must remain passive with respect to policy.

---

## 7. Metric Layer Interfaces

### 7.1 `SemanticMetric`

The first milestone only needs a scoring interface, not a full learning system.

```python
@dataclass
class MetricResult:
    source_id: str
    target_id: str
    total_distance: float
    component_scores: dict[str, float] = field(default_factory=dict)
    comparable: bool = True
    explanation: str = ""


class SemanticMetric:
    def distance(self, left: SemanticUnit, right: SemanticUnit) -> MetricResult:
        ...

    def similarity(self, left: SemanticUnit, right: SemanticUnit) -> MetricResult:
        ...
```

#### Responsibilities

- semantic distance
- similarity scoring
- component-wise explainable distance
- candidate ranking support
- drift support

#### Forbidden responsibilities

- committing transitions
- selecting policy
- mutating state

---

## 8. Trace Layer Interfaces

### 8.1 `TraceRecord`

```python
@dataclass
class TraceRecord:
    trace_id: str
    event_id: str
    transition_id: str
    causal_parent: str | None
    rule_id: str | None
    operator_name: str
    metric_evidence_ref: str | None
    mutation_mode: str
    before_version: str
    after_version: str
    changed_objects: list[str]
    changed_relations: list[str]
    explanation: str
```

### 8.2 `TraceBuilder`

`TraceBuilder` records causal explanation artifacts.

```python
class TraceBuilder:
    def record_transition(
        self,
        event: RuntimeEvent,
        transition: TransitionResult,
    ) -> TraceRecord:
        ...
```

#### Required constraints

- trace records should not store full state payloads
- trace must preserve causal linkage
- trace must reference events and versions
- trace should consume the transition result rather than recomputing diffs
- metric evidence should be referenced, not duplicated, in trace records

---

## 9. Replay Layer Interfaces

### 9.1 `ReplayResult`

```python
@dataclass
class ReplayResult:
    replay_id: str
    initial_state_ref: str
    final_state_ref: str
    replay_mode: str
    reconstructed_state: SemanticState
    applied_event_ids: list[str] = field(default_factory=list)
    failed_event_ids: list[str] = field(default_factory=list)
    divergence_points: list[str] = field(default_factory=list)
    replay_drift: float = 0.0
    validation_result: dict[str, Any] = field(default_factory=dict)
```

### 9.2 `ReplayEngine`

```python
class ReplayEngine:
    def replay(
        self,
        initial_state: SemanticState,
        event_stream: list[RuntimeEvent],
    ) -> ReplayResult:
        ...
```

#### Replay guarantees

- same input should produce the same reconstructed state
- replay must not resample semantics
- replay must not change history
- replay must surface divergence explicitly
- replay does not need to use metric evidence to reconstruct state

---

## 10. Minimal Package Layout

The first reference implementation should be able to hold the above interfaces in a small package layout:

```text
srp_runtime/
  kernel/
    runtime_kernel.py
    transition.py
  semantic/
    unit.py
    graph.py
    state.py
  event/
    event.py
    validator.py
  constraints/
    engine.py
  metric/
    semantic_metric.py
  trace/
    builder.py
  replay/
    engine.py
  operators/
    base.py
    identity.py
    activation.py
    relation.py
    merge.py
    approximation.py
    split.py
    recovery.py
    forgetting.py
    garbage_collection.py
```

The package layout is intentionally minimal and may expand later, but the first milestone should not exceed the protocol surface defined here.

---

## 11. First Milestone Tests

The first milestone should be validated by semantic invariant tests.

### 11.1 Event round trip

```text
serialize(event)
  -> deserialize(event)
  -> equivalent event
```

### 11.2 Deterministic transition

```text
S + e
  -> S'
```

Repeated application with the same valid inputs should produce equivalent results.

### 11.3 Replay equality

```text
RuntimeKernel(S0, E)
  ==
ReplayEngine(S0, E)
```

### 11.4 Constraint rejection

Illegal events should be rejected before mutation.

### 11.5 Trace consistency

Each committed transition should have a trace artifact that references the event and the version transition.

---

## 12. Future Direction

If these interfaces stabilize, the runtime primitives may later be formalized as a semantic runtime instruction set.

That is future work.

Milestone 1 only needs a clean reference contract.
