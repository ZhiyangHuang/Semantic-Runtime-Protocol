# SRP Runtime Protocol Map

This document maps the current `srp_experiment/srp/` modules to the runtime object and data-contract layers.
It is not an implementation spec.

The central question is:

> Which module consumes which runtime events, and which module emits them?

This map uses the current codebase as a projection of the higher-level SRP runtime protocol.

The event families listed here are defined more formally in [Runtime Event Contract](SRP_RUNTIME_EVENT_CONTRACT.md).
The conditions that justify those events are defined in [Semantic Evolution Rules](SRP_SEMANTIC_EVOLUTION_RULES.md).

---

## 1. Protocol View

```text
Task / Raw State
  -> semantic_parser.py
  -> SemanticUnit / RelationUnit projection
  -> state.py / pipeline_runtime.py
  -> compress.py
  -> recover.py + recovery/*
  -> state_allocation/*
  -> execution.py
  -> validate.py
  -> repair.py
  -> state_lifecycle.py
  -> pipeline.py
  -> history / summaries / drift metrics
```

The current code does not yet expose every object as a first-class `SemanticUnit`.
Instead, it uses `SemanticState`, typed semantic representations, inventories, and recovery packages as the operational carriers.

---

## 2. Event Vocabulary

The protocol can be described in terms of these event families:

- `SemanticExtracted`
- `Canonicalized`
- `Merged`
- `ActivationUpdated`
- `CompressionSelected`
- `CompressedPackageProduced`
- `RecoveryRequested`
- `RecoveryResultProduced`
- `StructuredStatePackageProduced`
- `AllocationDecided`
- `ExecutionPayloadSelected`
- `ValidationPerformed`
- `RepairTriggered`
- `LifecycleTransitioned`
- `DriftMeasured`
- `HistorySummarized`

---

## 3. Module Map

### 3.1 `semantic_parser.py`

Consumes:

- raw text
- constraint text
- anchor memory

Produces:

- `SemanticExtracted`
- `Canonicalized`
- `Merged`
- stable semantic object ids
- typed semantic representations

Role:

- parse raw state into typed semantic objects
- canonicalize values
- build stable object identity

Notes:

- this is the main entry point for turning text into semantic objects
- it is the closest current equivalent to extraction plus canonicalization

---

### 3.2 `semantic_objects.py`

Consumes:

- `SemanticState`

Produces:

- semantic object inventory
- object counts
- important object lists

Role:

- project the current state into object-level inventory
- support compression, recovery, and repair

Events:

- `SemanticExtracted` projection
- `HistorySummarized` support data

---

### 3.3 `state.py`

Consumes:

- semantic state inputs
- validation output
- lifecycle thresholds
- recovery package data

Produces:

- `ActivationUpdated`
- `LifecycleTransitioned`
- `HistorySummarized`
- state vector updates
- lifecycle summaries
- recovery summaries

Role:

- holds the main `SemanticState`
- stores runtime metadata for each object
- accumulates history records
- updates importance, confidence, and lifecycle state

Important current responsibility:

- `observe_verification()` is the main place where validation feedback becomes runtime memory state

---

### 3.4 `pipeline_runtime.py`

Consumes:

- task input
- encoder
- recovered state
- validation outcome

Produces:

- `SemanticState` initialization
- semantic metrics
- committed field selection
- state transitions

Role:

- bridge between task setup, state mutation, and cycle transition
- compute semantic drift, stability, and similarity
- decide which fields become the committed next state

Events:

- `ActivationUpdated`
- `DriftMeasured`
- `HistorySummarized`
- `LifecycleTransitioned`

---

### 3.5 `compress.py`

Consumes:

- `SemanticState`
- semantic object inventory
- chunk saliency scores
- optional LLM judge output

Produces:

- `CompressionSelected`
- `CompressedPackageProduced`
- selected chunk ids
- chunk selection reasons
- compact compressed state package

Role:

- choose what survives compression
- preserve constraints and important semantic content
- produce a recoverable compressed package

Downstream consumers:

- `recover.py`
- `repair.py`
- `validate.py`

---

### 3.6 `recovery/policy.py`

Consumes:

- compressed package

Produces:

- recovery policy decisions

Role:

- abstract interface for recovery behavior
- defines the recovery contract without implementing it

Events:

- `RecoveryRequested`
- policy-specific recovery decisions

---

### 3.7 `recovery/structured_recovery.py`

Consumes:

- compressed package

Produces:

- structured reconstruction result

Role:

- delegate structured recovery to reconstruction policy
- preserve compatibility with current reconstruction pipeline

Events:

- `RecoveryRequested`
- `RecoveryResultProduced`
- `StructuredStatePackageProduced`

---

### 3.8 `recovery/graph_recovery.py`

Consumes:

- compressed package
- semantic object inventory
- dependency ids

Produces:

- graph-aware reconstruction result
- semantic runtime graph
- graph recovery metrics

Role:

- prefer required objects and dependency closure
- prune unsupported objects
- produce graph-aware structured state

Events:

- `RecoveryRequested`
- `RecoveryResultProduced`
- `StructuredStatePackageProduced`

Special outputs:

- `graph_recovery_result`
- `semantic_runtime_graph`

---

### 3.9 `recover.py`

Consumes:

- compressed package
- recovery policy output
- anchor memory

Produces:

- `RecoveredStateProduced`
- `RecoveryResultProduced`
- `StructuredStatePackageProduced`
- recovery diagnostics

Role:

- dispatch recovery to the selected policy
- attach diagnostics and structured recovery package
- preserve historical `SemanticState` shape while using policy metadata

Important note:

- this is currently the main recovery orchestrator

---

### 3.10 `recover_runtime.py`

Consumes:

- package
- recovered memory
- usage data

Produces:

- recovered `SemanticState`
- `RecoveryTemplate` summary
- `HistorySummarized`
- `StructuredStatePackageProduced`

Role:

- materialize a recovered semantic state object
- attach recovery diagnostics and summaries
- prepare the structured package used by validation and allocation

Events:

- `RecoveryResultProduced`
- `StructuredStatePackageProduced`
- `HistorySummarized`

---

### 3.11 `state_allocation/*`

Consumes:

- recovered structured state package
- task context

Produces:

- `AllocationDecided`
- active / latent / discard partitioning
- allocation metrics
- forensic trace

Role:

- partition recovered objects without mutating them
- express the policy boundary between recovery and execution

Important invariant:

- allocation must not create, merge, or repair objects

---

### 3.12 `execution.py`

Consumes:

- recovered package
- allocation result
- execution source mode

Produces:

- `ExecutionPayloadSelected`
- selected execution state

Role:

- choose which state subset gets passed to execution
- project recovered / active / latent / discard views into a runnable payload

Events:

- `AllocationDecided` consumer
- `ExecutionPayloadSelected` producer

---

### 3.13 `execution_runner.py`

Consumes:

- execution payload
- prompt / query

Produces:

- execution result
- answer evaluation support

Role:

- run the downstream task using the selected semantic payload
- generate answer-level outputs that later feed validation

Events:

- downstream execution output

---

### 3.14 `validate.py`

Consumes:

- original text
- recovered text
- validation targets
- runtime metadata
- recovered state package

Produces:

- `ValidationPerformed`
- `DriftMeasured`
- failure summary
- dependency audit
- pass / fail result

Role:

- compare source and recovered semantic content
- compute alignment, drift, dependency coverage, and critical failures
- decide whether the current cycle can be committed

This is the main consumer of:

- recovered package
- history metadata
- runtime metadata

---

### 3.15 `repair.py`

Consumes:

- source package
- recovered package
- validation result
- validation targets

Produces:

- `RepairTriggered`
- repair package
- repair context
- patch updates

Role:

- build a repairable package when validation fails
- constrain or patch recovered objects
- produce a repaired package for a second validation pass

Important invariant:

- repair can modify object content, but allocation cannot

---

### 3.16 `state_lifecycle.py`

Consumes:

- runtime metadata
- policy thresholds
- verification counts
- drift counts

Produces:

- `LifecycleTransitioned`
- retained / decayed / archived counts
- lifecycle state mutations

Role:

- update object lifecycle state after verification feedback
- determine whether an object remains active, decays, or archives

Current lifecycle states in code:

- `active`
- `retained`
- `decayed`
- `archived`

---

### 3.17 `pipeline.py`

Consumes:

- task
- state initialization
- compression output
- recovery output
- allocation output
- validation output
- repair output

Produces:

- cycle records
- committed state transitions
- run-level history

Role:

- orchestrate the full runtime cycle
- connect compression, recovery, allocation, execution, validation, repair, and lifecycle updates
- act as the event router for the current runtime

This is the closest module to a runtime protocol coordinator.

---

## 4. Protocol Graph

```text
Task / Raw State
  |
  v
semantic_parser.py
  |  emits: SemanticExtracted, Canonicalized, Merged
  v
state.py + pipeline_runtime.py
  |  consumes: parsed semantic objects
  |  emits: ActivationUpdated, LifecycleTransitioned, HistorySummarized
  v
compress.py
  |  consumes: SemanticState, object inventory, saliency
  |  emits: CompressionSelected, CompressedPackageProduced
  v
recover.py
  |  delegates to recovery/*
  |  emits: RecoveryRequested, RecoveryResultProduced, StructuredStatePackageProduced
  v
state_allocation/*
  |  consumes: recovered package
  |  emits: AllocationDecided
  v
execution.py / execution_runner.py
  |  consumes: allocation result + recovered package
  |  emits: ExecutionPayloadSelected, execution output
  v
validate.py
  |  consumes: original text + recovered/executed text
  |  emits: ValidationPerformed, DriftMeasured
  v
repair.py
  |  consumes: validation failure context
  |  emits: RepairTriggered, patch updates
  v
state_lifecycle.py
  |  consumes: verification feedback
  |  emits: LifecycleTransitioned
  v
pipeline.py
  |  consumes: all cycle outputs
  |  emits: run records and cycle history
```

---

## 5. Event Consumer / Producer Summary

| Module | Consumes | Produces |
| --- | --- | --- |
| `semantic_parser.py` | raw text, constraints, anchor memory | `SemanticExtracted`, `Canonicalized`, `Merged` |
| `semantic_objects.py` | `SemanticState` | object inventory, important objects |
| `state.py` | verification results, policy thresholds | `ActivationUpdated`, `LifecycleTransitioned`, `HistorySummarized` |
| `pipeline_runtime.py` | task, encoder, recovered state | state init, drift metrics, committed fields |
| `compress.py` | `SemanticState`, saliency, object inventory | `CompressionSelected`, `CompressedPackageProduced` |
| `recovery/*` | compressed package, dependency data | `RecoveryRequested`, `RecoveryResultProduced`, `StructuredStatePackageProduced` |
| `recover.py` | package, policy result, anchor memory | recovered state, diagnostics |
| `recover_runtime.py` | package, memory, usage | recovered `SemanticState`, summaries |
| `state_allocation/*` | recovered package, task context | `AllocationDecided` |
| `execution.py` | recovered package, allocation result | `ExecutionPayloadSelected` |
| `execution_runner.py` | execution payload, query | execution output |
| `validate.py` | original and recovered text, metadata | `ValidationPerformed`, `DriftMeasured` |
| `repair.py` | validation failure context | `RepairTriggered`, patch updates |
| `state_lifecycle.py` | runtime metadata, policy thresholds | lifecycle transitions |
| `pipeline.py` | all cycle outputs | cycle history / records |

---

## 6. Current Implementation Notes

- The current codebase still uses `SemanticState` as the main runtime carrier.
- `semantic_object_inventory`, `typed_representation`, and recovery packages are the current projections of the object model.
- `history` is currently stored as verification records on `SemanticState`.
- `state.observe_verification()` is the main place where drift, confidence, and lifecycle are updated together.
- `pipeline.py` is the main orchestration entry point for the runtime protocol.

---

## 7. Scope

This document maps the current module responsibilities to the runtime protocol.

It does not define:

- the final production implementation
- the exact event class hierarchy
- the serialization format for events

Those should be derived from the runtime data contract and then implemented step by step.
