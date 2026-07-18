# SRP Runtime Decision Boundary Model

This document freezes the runtime boundary that selects which semantic operator should execute for a given event and state context.
It is a theory document, not an implementation spec.

The decision boundary sits between the event contract and the transition engine.
It answers a single question:

> Given a semantic event and the current runtime context, which operator is eligible, which one is selected, and why?

The boundary is explicit, bounded, and explainable.
It does not introduce policy learning or automatic strategy search.

---

## 1. Decision Boundary Overview

The Milestone 1 loop binds an event directly to an operator through `operator_name`.
Milestone 2 introduces an explicit decision layer:

```text
RuntimeEvent
      |
      v
DecisionContext
      |
      v
CandidateOperators
      |
      v
ConstraintFiltering
      |
      v
MetricEvidence
      |
      v
SelectedOperator
      |
      v
Transition
```

The decision boundary is still runtime-deterministic.
It may be rule-based, table-based, or heuristic within explicit bounds, but it is not learned.

### What it owns

- operator eligibility
- candidate ranking
- constraint-based rejection
- metric evidence collection
- decision explanation

### What it does not own

- mutation execution
- semantic version commits
- checkpoint creation
- archive recovery
- policy learning

---

## 2. DecisionContext

`DecisionContext` packages everything the runtime needs to decide whether and how to transform state.

### Suggested shape

```python
@dataclass
class DecisionContext:
    event_id: str
    event_type: str
    current_state_ref: str
    semantic_time: int
    available_constraints: list[str]
    available_operators: list[str]
    lifecycle_state: str
    version_id: str
    metric_snapshot_ref: str | None = None
```

### Purpose

The context provides the decision layer with:

- the triggering event
- the current semantic state anchor
- semantic time
- which constraints are active
- which operators can legally be considered
- what version and lifecycle branch is currently active

### Non-goals

- storing the full semantic state
- encoding transition logic directly
- deciding the final mutation result

---

## 3. OperatorCandidate

`OperatorCandidate` represents one operator option that may be considered for a decision.

### Suggested shape

```python
@dataclass
class OperatorCandidate:
    operator_name: str
    applicability: bool
    required_constraints: list[str]
    metric_requirements: list[str]
    rationale: str | None = None
```

### Semantics

Each candidate states:

- which operator is being considered
- whether it is applicable in principle
- which constraints must hold for it to remain eligible
- what metric evidence it needs
- why it is included in the candidate set

### Candidate generation sources

- event type
- lifecycle state
- semantic version state
- known runtime constraints
- current metric availability

### Non-goals

- mutating the state
- hiding alternative choices
- learning ranking weights from data

---

## 4. Constraint Filtering

Before selection, the runtime must reject candidates that violate active constraints.

### Constraint filtering duties

- eliminate inapplicable operators
- reject illegal lifecycle transitions
- reject operators whose prerequisites are unmet
- preserve evidence about why a candidate was rejected

### Example

```text
semantic conflict detected

candidate operators:
  - Merge
  - Split
  - IdentityUpdate

constraint result:
  - Merge allowed
  - Split forbidden
  - IdentityUpdate allowed
```

The filtering step must remain explainable.
Rejected candidates are part of the runtime evidence chain.

---

## 5. Metric Evidence

Metric evidence does not execute the transition.
It explains why one candidate is preferable or more suitable than another.

### Metric evidence role

- compare candidate applicability
- explain similarity or divergence
- justify merge, approximation, or recovery options
- record the basis for selection

### Typical metric signals

- identity distance
- semantic distance
- structural distance
- temporal distance
- lineage compatibility

### Non-goals

- replacing constraints
- directly mutating state
- turning metric scoring into a learned policy

---

## 6. DecisionResult

`DecisionResult` records the selected operator and the explanation for the decision.

### Suggested shape

```python
@dataclass
class DecisionResult:
    decision_id: str
    event_id: str
    selected_operator: str
    candidate_operators: list[str]
    rejected_candidates: list[str]
    constraint_results: list[str]
    metric_evidence_refs: list[str]
    explanation: str
    semantic_time: int
    version_id: str
```

### Semantics

The result must answer:

- which operator was selected
- which operators were considered
- which operators were rejected
- what constraints were decisive
- what metric evidence was used
- why the decision was made

### Non-goals

- holding the transition result itself
- storing the full state snapshot
- substituting for trace or commit records

---

## 7. Example Decision Flow

```text
semantic conflict detected
        |
        v
DecisionContext
        |
        v
OperatorCandidate set
        |
        v
ConstraintFiltering
        |
        v
MetricEvidence
        |
        v
DecisionResult
        |
        v
SelectedOperator
        |
        v
Transition
```

### Example

```text
event: conflict between two semantic units

candidate operators:
  - Merge
  - Split
  - IdentityUpdate

constraint results:
  - Merge allowed
  - Split forbidden
  - IdentityUpdate allowed

metric evidence:
  - similarity = 0.91
  - lineage compatibility = true

decision:
  - Merge
```

The key property is that the runtime can explain the selection without learning-based control.

---

## 8. Relationship to Trace

Trace records explain what happened and why the chosen operator was used.
The decision boundary supplies the selection rationale that trace can reference.

### Boundary

- DecisionResult explains operator selection
- TransitionResult explains state mutation
- TraceRecord explains the causal path across both

The trace layer should be able to reference:

- the chosen operator
- rejected candidates
- decisive constraints
- metric evidence refs

without re-deriving the selection from scratch.

---

## 9. Relationship to Commit and Checkpoint

The decision boundary precedes both commit and checkpoint.

```text
DecisionResult
      |
      v
TransitionResult
      |
      v
SemanticCommit
      |
      v
SemanticVersionGraph
```

Checkpoints are created after stable version progression, not before operator selection.

```text
DecisionResult
      |
      v
TransitionResult
      |
      v
SemanticCommit
      |
      v
RuntimeCheckpoint
```

The decision boundary does not own commit creation or checkpoint placement.

---

## 10. Non-Goals

The decision boundary is not:

- policy learning
- neural ranking
- automatic strategy search
- hidden operator selection
- state mutation
- archive lookup
- replay execution

It is a bounded semantic execution decision layer.

