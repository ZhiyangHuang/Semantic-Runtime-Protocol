# SRP Semantic Commit Model

This document freezes the semantic commit layer for SRP.
It is not an implementation spec and not a generic source-control guide.

The central question is:

> When does a runtime transition become part of the semantic history?

The answer is commit.
Commit is the historical confirmation point between a validated transition and a version DAG.

---

## 1. Commit Boundary

SRP distinguishes three related but different objects:

```text
RuntimeEvent
      |
      v
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

### Meaning

- `RuntimeEvent` is the request or trigger.
- `DecisionResult` is the operator selection decision.
- `TransitionResult` is the concrete state change evidence.
- `SemanticCommit` is the acceptance of that change into semantic history.
- `SemanticVersionGraph` is the DAG of accepted semantic history nodes.

### Commit is not

- the event itself
- the transition itself
- a full state snapshot
- a replay record

---

## 2. SemanticCommit Object

`SemanticCommit` is the reference object that anchors a transition into version history.

### Suggested shape

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
    author_context: str | None = None
    commit_reason: str | None = None
    semantic_time: int
    created_at: str | None = None
```

### Required properties

- `commit_id` must be stable and referenceable
- `parent_version_id` must be explicit when a parent exists
- `new_version_id` must identify the accepted semantic version
- `event_id`, `decision_id`, and `transition_id` must provide lineage to the runtime action
- `trace_id` should point to the causal explanation when available

### Reference-first rule

Commit should not store the full semantic state.
It should store references:

- state reference
- trace reference
- transition reference
- version reference

---

## 3. Commit Validation

Commit creation is not automatic.
A transition becomes a commit only after validation succeeds.

### Commit validation duties

- verify the transition was accepted
- verify the trace exists or can be derived
- verify the parent version exists when a parent is declared
- verify metadata determinism
- verify semantic time monotonicity
- verify the commit does not break version graph consistency

### Commit validation outcome

```text
TransitionResult
      |
      v
CommitValidation
      |
      +-- passed
      |
      v
SemanticCommit
```

### Non-goals

- re-running the transition
- re-selecting the operator
- mutating the active state
- reconstructing archive evidence

---

## 4. SemanticVersionGraph Integration

The commit layer feeds the version graph.

### Version node relation

```text
SemanticCommit
      |
      v
VersionNode
      |
      v
SemanticVersionGraph
```

### Responsibilities

- create a new version node for accepted commits
- preserve explicit parent references
- support branch creation
- support merge lineage
- support rollback references
- keep replay/audit traceable by version

### Version graph behavior

#### Branch

```text
V0
  |\
  | \__ C1 -> V1
  |
  \____ C2 -> V2
```

#### Merge

```text
V1 ----\
         C3 -> V3
V2 ----/
```

### Non-goals

- storing the full semantic state in every version node
- replacing replay with version checkout
- collapsing commit and version into the same object

---

## 5. Relationship to Replay

Replay does not replay commits.
Replay replays event history and validates the reconstructed result against commit history when required.

### Correct relation

```text
EventStream
      |
      v
Replay
      |
      v
Compare against Commit History
```

### Incorrect relation

```text
Commit
  |
  v
Replay
```

Commit is a verification target, not a replay input.

---

## 6. Relationship to Trace

Trace provides the causal explanation for the selection and transition that produced the commit.

### Boundary

- DecisionResult explains why the operator was selected
- TransitionResult explains what changed
- SemanticCommit explains that the change entered semantic history
- TraceRecord can reference all three

### Trace references

The commit should remain referenceable by:

- trace id
- transition id
- event id
- version id

without requiring the full reconstruction of state.

---

## 7. Commit and Lifecycle

Commit is version-history management, not lifecycle mutation.

### Commit may follow

- canonicalization
- merge
- split
- approximation
- recovery
- forgetting
- garbage collection

### Commit does not define

- active / forgotten / archived lifecycle semantics
- retention policy
- storage compaction

Those remain handled by their own layers.

---

## 8. Non-Goals

Semantic commit is not:

- a raw event log entry
- a full state snapshot
- a learning policy
- a checkpoint
- an archive entry
- a storage compaction artifact

It is the reference object that turns a validated transition into a versioned semantic history node.

