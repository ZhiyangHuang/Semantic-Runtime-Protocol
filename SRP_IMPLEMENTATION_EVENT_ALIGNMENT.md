# SRP Implementation Event Alignment

This document maps the current `srp_experiment/srp/` modules to the SRP runtime event processing model.
It is not an implementation spec.

The central question is:

> Which current modules produce events, which validate them, which apply them, and where are the current architectural gaps?

This document stays at the documentation layer only.
It does not change code structure.

The target execution boundary for these mappings is defined in [Runtime Kernel Target](SRP_RUNTIME_KERNEL_TARGET.md).

---

## 1. Alignment Goal

The current implementation should be viewed as an early projection of the runtime event system.

That means:

- a module may currently bundle producer, validator, and applier responsibilities
- a single function may correspond to part of an event lifecycle rather than one complete event role
- the current code can be mapped to the runtime kernel without refactoring it yet

This document freezes that mapping.

---

## 2. Module-Level Event Mapping

| Current Module | Runtime Role | Event Responsibility | Notes |
| --- | --- | --- | --- |
| `semantic_parser.py` | Event Producer | `SemanticExtracted`, `Canonicalized`, `Merged` | Strongest match for extraction and canonicalization proposals |
| `semantic_objects.py` | Runtime Object Projection | object inventory projection for event inputs | Produces unit views, not state mutations |
| `state.py` | Event Applier candidate | state mutation, lifecycle updates, verification feedback application | Currently mixes storage, mutation, and history |
| `pipeline_runtime.py` | State Transition Support | drift metrics, committed field selection, state initialization | Supports event flow but does not own event contracts |
| `compress.py` | Policy Decision / Producer | `CompressionSelected`, `CompressedPackageProduced` | Chooses what survives compression; current code is decision-heavy |
| `recovery/policy.py` | Recovery Policy Interface | recovery policy selection | Defines policy contract, not event application |
| `recovery/structured_recovery.py` | Recovery Producer | `RecoveryRequested`, `RecoveryResultProduced` | Produces structured recovery results via reconstruction policy |
| `recovery/graph_recovery.py` | Recovery Producer | `RecoveryRequested`, `RecoveryResultProduced`, `StructuredStatePackageProduced` | Produces graph-aware recovery outputs |
| `recover.py` | Recovery Coordinator | recovery dispatch and diagnostic attachment | Coordinates recovery flow across policy and runtime materialization |
| `recover_runtime.py` | Recovery Materializer | materializes recovered state and summaries | Builds `SemanticState` from recovered output |
| `state_allocation/*` | Policy Layer | `AllocationDecided` | Partitions recovered state without mutating semantics |
| `execution.py` | Execution Payload Selector | `ExecutionPayloadSelected` | Projects selected state into execution input |
| `execution_runner.py` | Downstream Executor | execution output | Consumes the projected payload |
| `validate.py` | Event Validator candidate | `ValidationPerformed`, `DriftMeasured` | Checks semantic continuity and contract satisfaction |
| `repair.py` | Repair Producer | `RepairTriggered` | Builds bounded repair packages after validation failure |
| `state_lifecycle.py` | Lifecycle Producer / Mutator candidate | `LifecycleTransitioned` | Applies retention, decay, and archive transitions |
| `pipeline.py` | Runtime Coordinator | event orchestration | Drives the end-to-end cycle order |

---

## 3. Function Role Classification

Functions can be categorized by event-processing responsibility.

### 3.1 Event Producer

These functions observe input or current state and propose what happened.

Examples:

- `parse_semantic_state()`
- `build_semantic_object_inventory()`
- `compress_state()`
- `recover_state()`

### 3.2 Decision Maker

These functions choose among valid options under pressure.

Examples:

- `build_state_allocation_policy()`
- `build_recovery_policy()`
- `select_execution_state()`
- `select_committed_fields()`

Decision makers do not finalize the mutation by themselves.

### 3.3 Validator

These functions evaluate whether the event or output is acceptable.

Examples:

- `validate_state()`
- recovery policy checks inside `recovery/*`
- lifecycle threshold checks in `state_lifecycle.py`

### 3.4 Mutator

These functions actually apply the accepted change.

Examples:

- `observe_verification()`
- `apply_object_lifecycle()`
- `transition_state()`
- recovery materialization functions that build the next `SemanticState`

### 3.5 Coordinator

These functions sequence the pipeline.

Examples:

- `run_srp()`
- `recover_state()`

---

## 4. Current Event Boundary Gaps

The current codebase reveals several event-boundary gaps.

### 4.1 Compression Gap

Current shape:

```text
compress.py
  -> produce package
  -> downstream mutation happens later
```

Theoretical shape:

```text
Decision
  -> CompressionSelected
  -> CompressedPackageProduced
  -> mutation or projection
```

Gap:

- the event layer is implicit rather than explicit

### 4.2 Recovery Gap

Current shape:

```text
recover.py / recover_runtime.py
  -> construct recovered state
  -> attach diagnostics
```

Theoretical shape:

```text
RecoveryRequested
  -> RecoveryResultProduced
  -> ValidationPerformed
  -> mutation or commit
```

Gap:

- validation gate is present conceptually but not fully separated as an event boundary

### 4.3 Lifecycle Gap

Current shape:

```text
state_lifecycle.py
  -> directly update lifecycle_state
```

Theoretical shape:

```text
LifecycleRule
  -> LifecycleTransitioned
  -> apply transition
```

Gap:

- lifecycle state change is still expressed as direct metadata mutation

### 4.4 Validation / Repair Gap

Current shape:

```text
validate.py
  -> evaluate
repair.py
  -> build repair package
```

Theoretical shape:

```text
ValidationPerformed
  -> if failed: RepairTriggered
  -> repair path commits only after validation
```

Gap:

- validation output and repair trigger should become first-class event boundaries

---

## 5. Migration Boundary

The current experimental code and the future runtime kernel serve different purposes.

### Current experimental layer

Responsible for:

- measuring preservation behavior
- generating A1 / A2 evidence
- comparing recovery, compression, allocation, and lifecycle behavior

### Future runtime kernel

Responsible for:

- event replay
- event validation
- event application
- rule-driven evolution
- attribution and auditability

This document keeps the two layers conceptually separate.

---

## 6. Implementation Notes

The current codebase already exposes useful alignment anchors:

- `semantic_parser.py` for extraction and canonicalization
- `compress.py` for compression decisions
- `recover.py` and `recovery/*` for recovery production
- `validate.py` for acceptance testing
- `state_lifecycle.py` for lifecycle transition logic
- `pipeline.py` for orchestration

These anchors are enough to map the current code onto the runtime event processing model without rewriting the implementation.

---

## 7. Scope

This document aligns the existing codebase with the runtime event processing model.

It does not define:

- the event handler implementation
- the event bus implementation
- the future runtime kernel code

Those belong to later implementation work.
