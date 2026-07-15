# SRP Kernel Callsite Map

This document maps current implementation callsites to future Runtime Kernel interaction boundaries.
It is a migration navigation document, not an implementation spec.

The central question is:

> Which current callsites should become event producers, query adapters, validators, mutators, or kernel callers in the future runtime architecture?

This document stays at the documentation layer only.
It does not change code structure.

The target migration stages are defined in [Runtime Kernel Migration Checklist](SRP_RUNTIME_KERNEL_MIGRATION_CHECKLIST.md).

---

## 1. Callsite Mapping Principle

Current implementation:

```text
Component
  -> direct state operation
```

Target architecture:

```text
Component
  -> Adapter
  -> Kernel API
  -> State Transition
```

The callsite map records:

- who triggers the transition
- who produces the event
- who calls the kernel
- which migration phase the callsite belongs to

This is not a refactor plan.
It is a migration navigation map.

---

## 2. Kernel API Callsite Table

| Kernel API | Current Callsite | Current Role | Target Adapter | Migration Phase | Status |
| --- | --- | --- | --- | --- | --- |
| `submit_event` | `pipeline.py::run_srp` | runtime coordinator | Event Producer Adapter | Phase 1 | EVENT_WRAPPED |
| `submit_event` | `semantic_parser.py::parse_semantic_state` | semantic extraction entrypoint | Event Producer Adapter | Phase 1 | EVENT_WRAPPED |
| `submit_event` | `compress.py::compress_state` | compression decision + package production | Event Producer Adapter | Phase 1 | EVENT_WRAPPED |
| `submit_event` | `recover.py::recover_state` | recovery coordination | Event Producer Adapter | Phase 1/3 | EVENT_WRAPPED |
| `submit_event` | `repair.py::build_repair_package` | repair package construction | Event Producer Adapter | Phase 3 | OBSERVATION_ONLY |
| `validate_event` | `validate.py::validate_state` | validation logic | Kernel Validator Adapter | Phase 1/2 | EVENT_WRAPPED |
| `validate_event` | `state_lifecycle.py::apply_object_lifecycle` | lifecycle threshold checks | Kernel Validator Adapter | Phase 2 | OBSERVATION_ONLY |
| `apply_event` | `state.py::observe_verification` | history + metadata mutation | Mutation Adapter | Phase 2 | KERNEL_ROUTED |
| `apply_event` | `state.py::apply_object_lifecycle` | lifecycle mutation bridge | Mutation Adapter | Phase 2 | KERNEL_ROUTED |
| `apply_event` | `pipeline_runtime.py::transition_state` | state replacement / commit bridge | Mutation Adapter | Phase 2 | KERNEL_ROUTED |
| `apply_event` | `recover_runtime.py::build_recovered_state` | recovered state materialization | Mutation Adapter | Phase 2/3 | OBSERVATION_ONLY |
| `get_state` | `pipeline_runtime.py::initialize_state` | initial state construction | Query Adapter | Phase 0 | OBSERVATION_ONLY |
| `get_state` | `semantic_objects.py::build_semantic_object_inventory` | read-only object inventory projection | Query Adapter | Phase 0 | OBSERVATION_ONLY |
| `get_state` | `execution.py::select_execution_state` | read-only execution projection | Query Adapter | Phase 0/1 | OBSERVATION_ONLY |
| `get_state` | `execution_runner.py::execute_task` | downstream consumer of selected view | Query Adapter | Phase 0/1 | OBSERVATION_ONLY |
| `replay` | `state.py` history fields | implicit history accumulation | Replay Engine | Phase 4 | NOT_MAPPED |
| `replay` | `state_summaries.py` / `export.py` | summary and report reconstruction | Replay Engine | Phase 4 | NOT_MAPPED |

Status legend:

- `NOT_MAPPED`: no explicit kernel-facing mapping yet
- `OBSERVATION_ONLY`: useful for tracing, but not yet kernel-routed
- `EVENT_WRAPPED`: already a strong candidate for event wrapping
- `KERNEL_ROUTED`: should eventually route through `Kernel.apply_event()`

---

## 3. Event Producer Callsites

These callsites currently produce the strongest candidates for future kernel events.

### 3.1 `semantic_parser.py::parse_semantic_state`

Current shape:

```text
raw text
  -> typed semantic objects
  -> canonical ids
  -> object views
```

Future event families:

- `SemanticExtracted`
- `Canonicalized`
- `Merged`

Target adapter:

- Event Producer Adapter

### 3.2 `compress.py::compress_state`

Current shape:

```text
state
  -> selection
  -> compression package
```

Future event families:

- `CompressionSelected`
- `CompressedPackageProduced`

Target adapter:

- Event Producer Adapter

### 3.3 `recover.py::recover_state`

Current shape:

```text
package
  -> recovery dispatch
  -> recovered state
```

Future event families:

- `RecoveryRequested`
- `RecoveryResultProduced`

Target adapter:

- Event Producer Adapter

### 3.4 `repair.py::build_repair_package`

Current shape:

```text
validation failure
  -> repair package
```

Future event family:

- `RepairTriggered`

Target adapter:

- Event Producer Adapter

---

## 4. Mutation Callsites

These are the most important callsites for kernel routing because they currently perform or complete state mutation.

| Current Location | Current Mutation | Future Owner | Migration Note |
| --- | --- | --- | --- |
| `state.py::observe_verification` | updates runtime metadata, drift counters, and history | Kernel transition engine / history recorder | should become event application + recording |
| `state.py::apply_object_lifecycle` | updates lifecycle state and related object metadata | Kernel lifecycle manager | direct mutation should be removed from external callers |
| `pipeline_runtime.py::transition_state` | constructs the next `SemanticState` from committed fields | Kernel state transition engine | should become an event-applied state transition |
| `recover_runtime.py::build_recovered_state` | materializes a recovered `SemanticState` | Kernel apply path after validation | should not be treated as a free mutation path |
| `state_lifecycle.py::apply_object_lifecycle` | applies retention / decay / archive transitions | Kernel lifecycle manager | should be moved behind `apply_event()` |

Mutation boundary rule:

```text
Decision
  -> RuntimeEvent
  -> Kernel.apply_event()
  -> SemanticState mutation
```

Any current callsite that mutates state outside this pattern is a migration target.

---

## 5. Query Callsites

Read operations should be treated separately from mutation paths.

### Query-allowed current callsites

- `pipeline_runtime.py::initialize_state`
- `pipeline_runtime.py::compute_semantic_metrics`
- `pipeline_runtime.py::select_committed_fields`
- `semantic_objects.py::build_semantic_object_inventory`
- `execution.py::select_execution_state`
- `execution_runner.py::execute_task`
- `validate.py::validate_state`

### Query boundary rule

```text
read-only inspection
  !=
state mutation
```

Current read paths are acceptable as precursors to `get_state()`, but they should not hide write behavior.

---

## 6. Event Flow Callsite Examples

### 6.1 Compression flow

Current:

```text
policy
  -> compress.py::compress_state
  -> state-sensitive package output
```

Future:

```text
policy
  -> CompressionSelected event
  -> submit_event()
  -> validate_event()
  -> apply_event()
```

### 6.2 Forgetting flow

Current:

```text
state_lifecycle.py::apply_object_lifecycle
  -> threshold-based lifecycle change
```

Future:

```text
evolution rule
  -> Forgotten event
  -> submit_event()
  -> validate_event()
  -> apply_event()
```

### 6.3 Recovery flow

Current:

```text
recover.py::recover_state
  -> recover_runtime.py::build_recovered_state
  -> validation
```

Future:

```text
recovery engine
  -> RecoveryRequested
  -> RecoveryResultProduced
  -> validate_event()
  -> apply_event()
```

---

## 7. Hidden Mutation Inventory

These are the most important hidden mutation paths to watch during migration.

| Location | Hidden Mutation Pattern | Why It Matters | Target Phase |
| --- | --- | --- | --- |
| `state.py::observe_verification` | mutates history and metadata during validation feedback | mixes observation with state change | Phase 2 |
| `state.py::apply_object_lifecycle` | applies lifecycle transitions directly | bypasses explicit event routing | Phase 2 |
| `state_lifecycle.py::apply_object_lifecycle` | threshold-based direct lifecycle update | direct mutation path for decay / archive behavior | Phase 2 |
| `recover_runtime.py::build_recovered_state` | materializes recovered state without explicit kernel event | recovery can hide mutation source | Phase 3 |
| `pipeline_runtime.py::transition_state` | commits a new state from selected fields | commit path should be event-driven | Phase 2 |
| `pipeline.py::run_srp` | orchestrates the full cycle and can conceal the transition source | coordinator can hide event boundaries if not wrapped | Phase 0/1 |

Migration aim:

```text
hidden mutation
  -> explicit event
  -> kernel application
```

---

## 8. Migration Status

Recommended status labels:

- `NOT_MAPPED`
- `OBSERVATION_ONLY`
- `EVENT_WRAPPED`
- `KERNEL_ROUTED`
- `REPLAY_READY`

These status labels should align with the migration checklist.

---

## 9. Relationship to Other Documents

Recommended chain:

```text
Runtime Kernel Interface
  -> Runtime Kernel API Map
  -> Runtime Kernel Adapter Plan
  -> Runtime Kernel Migration Checklist
  -> Kernel Callsite Map
  -> Implementation Migration
```

This document translates the migration plan into concrete current callsite visibility.

---

## 10. Scope

This document defines callsite-to-boundary mapping only.

It does not define:

- code refactors
- adapter class implementations
- kernel implementation details
- function-level redesign

Those belong to later implementation work.

