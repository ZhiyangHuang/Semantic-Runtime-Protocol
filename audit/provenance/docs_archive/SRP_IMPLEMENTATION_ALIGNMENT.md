# SRP Implementation Alignment

This document maps the current `srp_experiment/srp/` implementation to the SRP runtime concepts without changing the code structure.
It is not an implementation spec.

The central question is:

> How does the current codebase align with SRP's runtime roles, event boundaries, rules, and state mutation responsibilities?

This layer is intentionally lightweight.
It freezes responsibility mapping before any structural refactor.

---

## 1. Alignment Principle

The implementation should be understood as a projection of the runtime protocol, not as the protocol itself.

That means:

- current modules may bundle several runtime roles
- one module may produce several event families
- one runtime event may be realized by a sequence of functions
- decision and mutation should stay conceptually separated even if they are currently colocated

The goal of this document is to assign each current module to a clear SRP role.

The event-specific mapping of current modules is further detailed in [Implementation Event Alignment](SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md).

---

## 2. Runtime Role Categories

The current implementation can be grouped into these runtime roles:

- event producer
- rule evaluator
- state mutator
- policy decision maker
- protocol coordinator
- recovery engine
- validation engine
- history / summary writer

These are conceptual roles, not new code directories.

---

## 3. Module Responsibility Mapping

| Current Module | SRP Role | Primary Responsibility | Typical Events |
| --- | --- | --- | --- |
| `semantic_parser.py` | Event Producer | Parse raw text into typed semantic objects and canonical ids | `SemanticExtracted`, `Canonicalized`, `Merged` |
| `semantic_objects.py` | Runtime Object Projection | Build object inventory and important-object views from `SemanticState` | object inventory projections |
| `state.py` | State Mutator | Hold runtime metadata, apply verification feedback, update lifecycle summaries | `ActivationUpdated`, `LifecycleTransitioned`, `HistorySummarized` |
| `pipeline_runtime.py` | Protocol Support / State Transition | Initialize state, compute semantic metrics, select committed fields | `DriftMeasured`, `LifecycleTransitioned`, `HistorySummarized` |
| `compress.py` | Policy Executor | Select compressed content and produce compressed packages | `CompressionSelected`, `CompressedPackageProduced` |
| `recovery/policy.py` | Recovery Policy Interface | Define recovery behavior contract | `RecoveryRequested` |
| `recovery/structured_recovery.py` | Recovery Engine | Delegate structured recovery to reconstruction policy | `RecoveryRequested`, `RecoveryResultProduced` |
| `recovery/graph_recovery.py` | Recovery Engine | Perform dependency-aware graph recovery | `RecoveryRequested`, `RecoveryResultProduced`, `StructuredStatePackageProduced` |
| `recover.py` | Recovery Coordinator | Dispatch recovery mode, attach diagnostics, materialize recovery output | `RecoveryRequested`, `RecoveryResultProduced`, `StructuredStatePackageProduced` |
| `recover_runtime.py` | Recovery Materializer | Build recovered `SemanticState` and attach summaries | `RecoveryResultProduced`, `HistorySummarized` |
| `state_allocation/*` | Policy Layer | Partition recovered state into active, latent, discard | `AllocationDecided` |
| `execution.py` | Execution Payload Selector | Project the chosen state subset into execution input | `ExecutionPayloadSelected` |
| `execution_runner.py` | Downstream Executor | Execute downstream task from the selected payload | downstream execution output |
| `validate.py` | Validation Engine | Compare source and recovered output, compute drift and coverage | `ValidationPerformed`, `DriftMeasured` |
| `repair.py` | Repair Engine | Build bounded repair packages after validation failure | `RepairTriggered` |
| `state_lifecycle.py` | Lifecycle Manager | Apply retention, decay, archive transitions on runtime metadata | `LifecycleTransitioned` |
| `pipeline.py` | Runtime Coordinator | Orchestrate the full cycle and record run-level history | all cycle-level events |

---

## 4. Function Classification

The same module can contain several function classes.

### 4.1 Event Producer

Event producers create the event or the pre-event artifact that will later become an event.

Examples:

- `parse_semantic_state()`
- `build_semantic_object_inventory()`

### 4.2 Rule Evaluator

Rule evaluators check whether a rule condition holds.

Examples in current code are implicit rather than explicit:

- lifecycle thresholds in `state_lifecycle.py`
- selection heuristics in `compress.py`
- recovery policy choice in `recovery/factory.py`

### 4.3 State Mutator

State mutators apply the effect of a decision.

Examples:

- `observe_verification()`
- `apply_object_lifecycle()`
- `transition_state()`

### 4.4 Policy Decision

Policy decision code selects among valid alternatives under pressure.

Examples:

- `build_state_allocation_policy()`
- `build_recovery_policy()`
- `compress_state()`

### 4.5 Protocol Coordinator

Protocol coordinators stitch the pipeline together without owning the underlying semantic rules.

Examples:

- `run_srp()`
- `recover_state()`

---

## 5. Event Boundary

The current code should be interpreted through a strict event boundary:

```text
Decision
  -> Event
  -> Mutation
```

Decision is not mutation.

Mutation should only occur after a valid event boundary is crossed, even if the current code expresses that as a direct function call.

This means the architectural target is:

- determine eligibility
- emit or represent an event
- apply the state mutation

---

## 6. Current Alignment Notes

### 6.1 `semantic_parser.py`

This module is currently the strongest implementation match for:

- `SemanticExtracted`
- `Canonicalized`
- `Merged`

It creates typed objects and stable ids from raw text, which maps closely to event production.

### 6.2 `state.py`

This module currently combines:

- runtime object storage
- verification-driven activation updates
- lifecycle transitions
- history accumulation

It is the main state mutation layer in the current code.

### 6.3 `compress.py`

This module is primarily a policy executor.

It chooses which chunks and objects survive compression and produces the package that downstream recovery consumes.

### 6.4 `recovery/*` and `recover.py`

These modules together form the recovery engine.

They currently cover:

- text recovery
- structured recovery
- graph recovery
- recovery diagnostics

### 6.5 `state_lifecycle.py`

This is the most direct implementation of lifecycle transition logic.

It reads metadata thresholds and updates object lifecycle state.

### 6.6 `pipeline.py`

This is the runtime coordinator.

It currently controls the order:

```text
compress -> recover -> allocate -> execute -> validate -> repair -> lifecycle update
```

---

## 7. Implied Runtime Kernel

Without restructuring the repository, the current codebase already implies the following kernel responsibilities:

- event bus behavior in the pipeline
- rule evaluation in lifecycle / compression / recovery policy code
- state mutation in `state.py` and `state_lifecycle.py`
- policy resolution in allocation and recovery factories

This suggests a future runtime kernel interface, but this document does not require the refactor yet.

---

## 8. Non-Goals

This document does not:

- rename existing files
- move modules into new directories
- introduce new runtime classes in code
- refactor the pipeline

It only freezes alignment so future code changes can follow a shared conceptual map.

---

## 9. Scope

This document aligns the current implementation with SRP runtime concepts.

It does not define:

- the final kernel API
- the future event handler interface
- the future rule engine interface

Those should be introduced only after this alignment is stable.
