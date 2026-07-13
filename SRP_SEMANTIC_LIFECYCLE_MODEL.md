# SRP Semantic Lifecycle Model

This document freezes the lifecycle states and terminal transitions used by SRP semantic units.
It is not an implementation spec and it is not a general memory policy.

The lifecycle model sits between semantic evolution and runtime execution:

```text
Semantic Evolution
      |
      v
Semantic Lifecycle Model
      |
      v
Runtime Transition Enforcement
```

---

## 1. Lifecycle States

SRP semantic units move through a small set of explicit lifecycle states:

- `active`
- `merged`
- `approximated`
- `archived`
- `forgotten`
- `permanently_removed`

These states describe semantic availability, not physical storage alone.

---

## 2. State Meaning

### `active`

The unit is currently available in the active semantic representation.

### `merged`

The unit has been consolidated into another semantic unit, but lineage and provenance still exist.

### `approximated`

The unit remains recoverable, but its representation has been reduced or degraded.

### `archived`

The unit is no longer part of the active semantic frontier, but its structure can still be restored.

### `forgotten`

The unit has been removed from active representation, but recovery evidence is still preserved.

### `permanently_removed`

The unit has been garbage collected and is no longer part of the active semantic state.

---

## 3. Legal Transitions

The first version of the lifecycle FSM allows these core transitions:

```text
active -> merged
active -> approximated
active -> archived
active -> forgotten
approximated -> active
approximated -> archived
approximated -> forgotten
archived -> active
archived -> forgotten
forgotten -> active
forgotten -> permanently_removed
merged -> archived
merged -> active
```

The `permanently_removed` state is terminal for Milestone 1.

---

## 4. Illegal Transitions

The following transitions are forbidden unless a dedicated recovery path exists:

- `forgotten -> active` without recovery evidence
- `permanently_removed -> active`
- `permanently_removed -> merged`
- `permanently_removed -> approximated`

---

## 5. Operator Mapping

Lifecycle transitions are produced by these operators:

- `IdentityUpdateOperator`
- `ActivationUpdateOperator`
- `RelationUpdateOperator`
- `MergeOperator`
- `ApproximationOperator`
- `SplitOperator`
- `RecoveryOperator`
- `ForgettingOperator`
- `GarbageCollectionOperator`

This mapping is the canonical lifecycle-to-operator contract.

---

## 6. Lifecycle Invariants

- `unit_id` remains immutable across all lifecycle states
- `lineage` and `provenance` are preserved until GC
- `forgotten` units must retain recovery evidence
- `permanently_removed` units are terminal
- GC must not target identity anchors or active roots

---

## 7. Relation to Replay and Trace

- `Trace` explains why a unit changed lifecycle state
- `Replay` reconstructs the lifecycle state sequence from events
- `GC` is allowed to remove the active unit from state, but the event history remains replayable
- `State Compaction` does not change lifecycle meaning; it only reorganizes retained archive storage
