# SRP Runtime Kernel API Map

This document maps the current `srp_experiment/srp/` implementation to the future Runtime Kernel API.
It is a migration mapping document, not an implementation spec.

The central question is:

> Which current modules behave like callers, producers, validators, mutators, or query surfaces for the future runtime kernel API?

This document stays at the documentation layer only.
It does not change code structure.

The target callable boundary for this mapping is defined in [Runtime Kernel Interface](SRP_RUNTIME_KERNEL_INTERFACE.md).

---

## 1. Purpose

The current implementation still contains implicit transitions:

- compression can lead to downstream state changes
- recovery can materialize a new semantic state
- lifecycle updates can directly change metadata
- validation and repair can happen without an explicit kernel event boundary

The future architecture should make that flow explicit:

```text
Decision
  -> RuntimeEvent
  -> Kernel API
  -> State Mutation
```

This document maps the current modules to that future boundary.

---

## 2. Kernel API Mapping Overview

| Kernel API | Current Module(s) | Current Behavior | Future Responsibility |
| --- | --- | --- | --- |
| `submit_event` | `pipeline.py`, `compress.py`, `recover.py`, `state_lifecycle.py` | Emit or stage runtime actions implicitly through pipeline steps | Accept a `RuntimeEvent` and route it into the kernel boundary |
| `validate_event` | `validate.py`, lifecycle checks in `state_lifecycle.py`, recovery checks in `recovery/*` | Validate recovered or compressed state after the fact | Perform kernel-level schema, permission, invariant, and causal checks before mutation |
| `apply_event` | `state.py`, `state_lifecycle.py`, `recover_runtime.py` | Mutate runtime metadata or materialize recovered state directly | Apply an accepted event through the transition engine |
| `get_state` | `state.py`, `pipeline_runtime.py`, `semantic_objects.py`, `execution.py` | Read semantic state, object inventory, or selected execution views | Expose read-only kernel projections and query views |
| `replay` | `state.py` history fields, validation logs, recovery summaries | Approximate reconstruction through accumulated summaries | Rebuild semantic state evolution from the event stream deterministically |

The mapping is provisional.
A single current module may touch multiple future API surfaces.

---

## 3. Event Producer Mapping

These modules currently produce the strongest candidates for future kernel events.

| Current Module | Typical Output Shape | Future Event Family | Kernel API Touchpoint |
| --- | --- | --- | --- |
| `semantic_parser.py` | typed semantic objects, canonical ids, confidence-bearing extractions | `SemanticExtracted`, `Canonicalized`, `Merged` | `submit_event` |
| `semantic_objects.py` | object inventory and important-object views | object projection artifacts | `submit_event` only if an object view becomes an event proposal |
| `compress.py` | compression selection and compressed package construction | `CompressionSelected`, `CompressedPackageProduced` | `submit_event` |
| `recover.py` | recovery dispatch and recovered output shaping | `RecoveryRequested`, `RecoveryResultProduced` | `submit_event` |
| `recovery/structured_recovery.py` | structured reconstruction outputs | `RecoveryRequested`, `RecoveryResultProduced` | `submit_event` |
| `recovery/graph_recovery.py` | dependency-aware recovery outputs | `RecoveryRequested`, `RecoveryResultProduced`, `StructuredStatePackageProduced` | `submit_event` |
| `state_lifecycle.py` | lifecycle transitions based on thresholds | `LifecycleTransitioned` | `submit_event` |
| `validate.py` | drift and continuity evaluation | `ValidationPerformed`, `DriftMeasured` | `validate_event` or query-side validation |
| `repair.py` | bounded repair packages | `RepairTriggered` | `submit_event` |

The important distinction is:

- current modules often produce outputs that are not yet explicit events
- the future kernel expects those outputs to be wrapped as `RuntimeEvent`

---

## 4. Mutation Ownership Mapping

This section identifies where direct mutation currently happens and how that ownership should move into the kernel.

| Current Module | Current Mutation Behavior | Future Mutation Ownership |
| --- | --- | --- |
| `state.py` | mutates runtime metadata, verification feedback, and lifecycle-related fields | internal kernel state mutation only |
| `state_lifecycle.py` | updates lifecycle state directly from thresholds | transition engine inside the kernel |
| `recover_runtime.py` | materializes recovered state into a new semantic state | kernel-applied transition after validation |
| `compress.py` | influences what survives compression and may indirectly shape state | no direct mutation; only event proposal |
| `recover.py` | coordinates recovery and may lead to state reconstruction | no direct mutation; only recovery event production |

Future rule:

```text
current module output
  -> RuntimeEvent
  -> Kernel.apply_event()
  -> SemanticState mutation
```

Direct mutation outside the kernel boundary should be treated as legacy behavior.

---

## 5. Query Boundary

The future kernel should expose read surfaces separately from mutation surfaces.

### Allowed query callers

- policy layers
- evaluation code
- recovery candidate generation
- debugging and test harnesses
- runtime coordinators

### Query surfaces

- `get_state`
- kernel projections
- read-only event or history views
- replay-derived snapshots

### Not allowed

- direct write access through query paths
- hidden mutation during query
- policy-side mutation disguised as inspection

Current code that reads state for allocation, validation, or recovery should be treated as a query-side precursor to the future kernel API.

---

## 6. Event Flow Examples

### 6.1 Compression

Current shape:

```text
compress.py
  -> select content
  -> produce package
  -> downstream state may change
```

Future shape:

```text
Policy decision
  -> CompressionSelected
  -> submit_event()
  -> validate_event()
  -> apply_event()
```

### 6.2 Forgetting

Current shape:

```text
state_lifecycle.py
  -> threshold check
  -> direct lifecycle update
```

Future shape:

```text
Evolution rule
  -> Forgotten
  -> submit_event()
  -> validate_event()
  -> apply_event()
```

### 6.3 Recovery

Current shape:

```text
recover.py / recover_runtime.py
  -> reconstruct state
  -> attach diagnostics
```

Future shape:

```text
Recovery engine
  -> RecoveryRequested
  -> RecoveryResultProduced
  -> validate_event()
  -> apply_event()
```

---

## 7. Current Gaps

The current implementation does not yet fully expose the kernel API boundary.

### 7.1 Event wrapping gap

Current functions often return a result directly instead of a first-class `RuntimeEvent`.

Needed future shape:

```text
result
  -> event
  -> kernel submission
```

### 7.2 Mutation isolation gap

Current code can mix decision and mutation in the same execution path.

Needed future shape:

```text
decision
  -> event
  -> apply_event()
```

### 7.3 Replay gap

Current history and summary fields help with analysis, but they do not yet guarantee deterministic replay from an explicit event stream.

Needed future shape:

```text
EventStream
  -> replay
  -> reconstructed SemanticState
```

### 7.4 Query boundary gap

Current read paths are useful, but they are not yet formally separated from mutation paths at the API boundary.

Needed future shape:

```text
read-only query
  !=
state mutation
```

---

## 8. Migration Priority

The migration should happen in layers.

### Phase 1: Event wrapping

Wrap current outputs as `RuntimeEvent` proposals.

Examples:

- parser outputs
- compression selections
- recovery outputs
- lifecycle decisions

### Phase 2: Mutation isolation

Move mutation into the kernel boundary.

Examples:

- direct state updates
- lifecycle field updates
- recovered state materialization

### Phase 3: Replay support

Make the event stream sufficient to reconstruct state evolution.

Examples:

- recorded event stream
- schema versioning
- causal parent tracking
- drift-attribution reconstruction

### Phase 4: API consolidation

After event wrapping and replay stabilize, the current implementation can be mapped more precisely to kernel callers and adapters.

---

## 9. Boundary Summary

### Current experimental layer

Responsible for:

- preserving the existing experiment flow
- generating evidence
- exposing implicit transition behavior

### Future kernel API layer

Responsible for:

- accepting events
- validating transitions
- applying mutations
- exposing query and replay surfaces

### Core principle

```text
Current implementation
  -> Kernel API boundary
  -> Future runtime kernel
```

The implementation should be mapped toward the API, not the other way around.

