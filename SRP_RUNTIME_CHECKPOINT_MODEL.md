# SRP Runtime Checkpoint Model

This document freezes the runtime checkpoint layer for SRP.
It is not a semantic history artifact and not a version node replacement.

The central question is:

> How can SRP resume replay from a validated intermediate point without changing semantic meaning?

A checkpoint is a replay acceleration artifact.
It anchors replay, but it does not define history.

---

## 1. Checkpoint Boundary

Checkpoint must be separated from commit, versioning, and archive storage.

### Correct relationship

```text
EventStream
      |
      +----------------+
      |                |
      v                v
    Replay         RuntimeCheckpoint
      |
      v
SemanticState
```

### Incorrect relationships

```text
SemanticCommit -> RuntimeCheckpoint
```

```text
RuntimeCheckpoint -> SemanticVersionGraph
```

### Meaning

- `SemanticCommit` decides that a transition belongs in accepted semantic history.
- `RuntimeCheckpoint` decides where replay can start efficiently.
- `Replay` reconstructs state from event history, optionally using a checkpoint anchor.

### Non-goals

- storing semantic history in the checkpoint itself
- replacing commit history
- replacing replay with checkpoint truth
- mutating semantic meaning

---

## 2. RuntimeCheckpoint Object

`RuntimeCheckpoint` is the reference object for replay acceleration.

### Suggested shape

```python
@dataclass
class RuntimeCheckpoint:
    checkpoint_id: str
    version_id: str
    event_position: int
    state_ref: str
    created_round: int
    parent_checkpoint_id: str | None = None
    replay_boundary: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)
```

### Required properties

- `checkpoint_id` must be stable and referenceable
- `version_id` must anchor the checkpoint to a semantic version
- `event_position` must indicate the replay offset
- `state_ref` must point to a validated semantic state anchor
- `created_round` must be monotonic within runtime time

### Reference-first rule

The checkpoint must not store the full semantic history.
It may store:

- state reference
- version reference
- replay offset
- optional metadata

It must not become a hidden state store.

---

## 3. Checkpoint Boundary

Checkpoint creation can only happen after a transition has been committed.

### Allowed

- committed versions
- validated replay anchors
- stable state references

### Not allowed

- pending events
- executing transitions
- failed validation results
- speculative operator outcomes

### Boundary rule

```text
TransitionResult
      |
      v
SemanticCommit
      |
      v
RuntimeCheckpoint
```

The checkpoint layer must never capture an invalid intermediate mutation state.

---

## 4. Checkpoint Lifecycle

Checkpoint lifecycle should remain separate from semantic lifecycle.

### Suggested lifecycle

```text
Created
  |
  v
Validated
  |
  v
Active
  |
  v
Superseded
  |
  v
Archived
```

### Semantics

- `Created` means a checkpoint candidate exists.
- `Validated` means the checkpoint references are consistent.
- `Active` means the checkpoint may be used for replay acceleration.
- `Superseded` means a newer checkpoint replaced it for the same range or branch.
- `Archived` means it remains available for audit or historical replay optimization.

### Non-goals

- forgotten / recovered semantic lifecycles
- archive entry lifecycle
- semantic mutation lifecycle

---

## 5. Replay Acceleration

Checkpointing exists to reduce replay cost.

### Without checkpoint

```text
Event1
Event2
Event3
...
Event1000
```

Replay starts from the beginning.

### With checkpoint

```text
Checkpoint@500
Event501
Event502
...
Event1000
```

Replay starts from the nearest validated checkpoint anchor.

### Correctness rule

Checkpoint acceleration must preserve replay determinism.

```text
Checkpoint + Event Delta = Reconstructed State
```

### Non-goals

- making checkpoints the only source of truth
- replacing event history
- bypassing validation

---

## 6. Checkpoint Verification

Checkpoint creation and checkpoint use both require verification.

### Creation verification

- version id exists
- state ref is valid
- event position is within history bounds
- trace head or trace anchor is consistent
- replay boundary is coherent with the version graph

### Use verification

- checkpoint state matches the expected branch or version
- replay delta begins at the correct event offset
- replay drift can be measured when results differ

### Typical metadata

- `version_id`
- `trace_head`
- `event_hash`
- `state_ref`
- `branch_id`
- `replay_mode`

### Failure semantics

If verification fails, the runtime should return a replay / checkpoint mismatch rather than guessing.

---

## 7. Relationship to Commit

Commit decides history membership.
Checkpoint decides replay start efficiency.

### Commit

- binds a transition to the semantic version DAG
- establishes a history node

### Checkpoint

- references an already committed version
- marks a fast replay anchor

### Boundary

```text
SemanticCommit
      |
      v
SemanticVersionGraph
      |
      v
RuntimeCheckpoint
```

Checkpoint must never define version history by itself.

---

## 8. Relationship to Replay

Replay is the primary consumer of checkpoints.

### Correct relation

```text
EventStream
      |
      +------+
      |      |
      v      v
    Replay  Checkpoint
      |
      v
SemanticState
```

### Semantics

- Replay reconstructs state from event history
- Checkpoint provides a validated starting anchor
- Checkpoint does not replace event history

### Replay drift

If checkpoint-based replay produces a different result from full replay, the runtime should surface:

- `ReplayDrift`
- divergence points
- validation failure details

---

## 9. Non-Goals

Runtime checkpointing is not:

- a semantic version node
- an archive entry
- a commit record
- a snapshot truth substitute
- a mutation operator

It is an optimization and anchor layer for deterministic replay.

