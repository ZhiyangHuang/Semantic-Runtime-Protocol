# SRP Runtime Recording Layer Alignment

This document maps the current experimental recording and summary layers to the future SRP runtime recording responsibilities.
It is not an implementation spec.

The central question is:

> Which current data-producing modules will eventually own event records, trace artifacts, replay snapshots, and state projections?

This document stays at the documentation layer only.
It does not change code structure.

The replay and trace requirements are defined in [Replay Spec](SRP_REPLAY_SPEC.md) and [Semantic Evolution Trace Spec](SRP_SEMANTIC_EVOLUTION_TRACE_SPEC.md).

---

## 1. Recording Layer Purpose

The current experimental code is not yet the Runtime Kernel.
It is an observation data source for the future recording layer.

Future runtime recording responsibilities:

- EventStream capture
- Trace generation
- Replay snapshot support
- State projection support

The recording layer should describe what happened without becoming the source of uncontrolled mutation.

---

## 2. Existing Module Mapping

### 2.1 `state.py`

Current responsibilities:

- holds semantic state
- records verification feedback
- updates metadata and lifecycle summaries
- maintains history records

Future role:

- State Snapshot Provider

Future outputs:

- `StateVersionCreated`
- `state_reference`
- snapshot-ready metadata

Not responsible for:

- event creation
- replay orchestration
- policy selection
- mutation policy

### 2.2 `pipeline_record_builder.py`

Current responsibilities:

- assembles cycle-level records
- combines compression, recovery, validation, lifecycle, and execution artifacts
- emits a single record object for the cycle

Future role:

- Event / Trace / Replay Record Producer

Future outputs:

- `RuntimeEventRecord`
- `TraceNodeReference`
- `ReplaySnapshotReference`

This module is the strongest candidate for a future recording-layer aggregator.

### 2.3 `state_summaries.py`

Current responsibilities:

- builds lifecycle summaries
- builds object update summaries
- builds runtime summary views
- exports flattened summaries for analysis

Future role:

- State Projection Layer

Future outputs:

- summary views
- metrics views
- evaluation-ready projections

It must not become the source of truth for replay or trace.

---

## 3. Replay Data Ownership

Replay-related data should be owned by distinct conceptual layers.

| Data | Owner |
| --- | --- |
| State snapshot | State layer |
| Event record | Event layer |
| Rule version | Evolution layer |
| Trace node | Trace layer |
| Drift metric | Evaluation layer |

This prevents history or summaries from absorbing every responsibility.

---

## 4. Trace Generation Flow

The trace layer should be able to derive causal structure from recorded evolution.

Recommended flow:

```text
State Before
  -> Runtime Event
  -> State Transition
  -> State After
  -> Trace Builder
  -> Trace Node + Trace Edge
```

The trace builder should consume event and state-reference information, not a full duplicate state object.

---

## 5. Replay Recording Flow

Replay and trace are different consumers of recorded data.

### Replay

Replay asks:

```text
can we reconstruct the semantic state?
```

Replay should depend on:

- `before_state_reference`
- `after_state_reference`
- `event_stream`
- `schema_version`
- `rule_version`

### Trace

Trace asks:

```text
why did the semantic state change?
```

Trace should depend on:

- `event_id`
- `rule_id`
- `state reference`
- `mechanism`

The two responsibilities should remain distinct.

---

## 6. Hidden Mutation Audit

The recording layer should help expose, not hide, mutation.

### Current high-risk locations

| Location | Current Behavior | Future Handling |
| --- | --- | --- |
| `state.py` | direct metadata and lifecycle mutation | kernel mutation only |
| `recover_runtime.py` | materializes recovered state | recovery event and kernel application |
| `state_lifecycle.py` | threshold-driven lifecycle updates | lifecycle event and kernel application |
| `repair.py` | produces corrective state artifacts | repair event and kernel application |

This audit supports the Phase 2 mutation routing plan.

---

## 7. Migration Boundary

### Current experimental layer

Responsible for:

- producing data
- measuring behavior
- generating summaries and records

### Future runtime kernel

Responsible for:

- controlling transitions
- enforcing event legality
- applying semantic mutations

### Recording layer boundary

The recording layer should sit between runtime execution and analysis.

It should surface:

- event records
- trace structures
- replay snapshots
- state projections

but it should not own kernel mutation logic.

---

## 8. Relationship to Other Documents

Recommended chain:

```text
Runtime Kernel Migration Checklist
  -> Runtime Kernel Phase Migration Map
  -> Semantic Evolution Trace Spec
  -> Replay Spec
  -> Runtime Recording Layer Alignment
  -> Replay / Trace Implementation
```

This document bridges replay and trace requirements back to current recording modules.

---

## 9. Scope

This document defines recording-layer responsibility mapping only.

It does not define:

- storage schemas
- implementation classes
- serialization formats
- kernel internals

Those belong to later implementation work.

