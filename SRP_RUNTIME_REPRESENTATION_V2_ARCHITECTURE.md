# SRP Runtime Representation v2 Architecture

This document defines the rationale and structure for the next SRP runtime representation.

The canonical model is defined in [SRP Runtime Representation v2 Specification](SRP_RUNTIME_REPRESENTATION_V2_SPEC.md).

The central claim is:

```text
Compression operates on semantic runtime state, not on raw text.
```

Therefore SRP should not be treated as a graph-only system. It should be treated as a runtime IR stack that converts text into a layered semantic state, compresses that state, recovers it, and validates it.

The current evidence chain supports this shift:

- failure taxonomy shows object loss, dependency break, and hallucinated reconstruction
- graph v1 lowers repair cost
- graph v1.5 improves retention and graph integrity
- validation coverage remains flat on the fixed tasks
- semantic extraction audit points to extraction / provenance under-specification

The bottleneck is now upstream of recovery.

---

## 1. Design Philosophy

SRP is not a text summarizer.
SRP is a semantic runtime state system.

That means:

- text is input
- runtime semantics is the operational substrate
- compression should preserve executable meaning
- recovery should reconstruct only the missing semantic state
- validation should compare source and recovered runtime state, not just strings

This is why the representation must be layered.

---

## 2. Runtime Ontology

The runtime ontology should distinguish what kind of semantic thing is being represented.

### 2.1 Runtime Object

Long-lived semantic unit that can survive compression and recovery.

Examples:

- people
- places
- artifacts
- concepts

### 2.2 Runtime State

A mutable condition of an object or system.

Examples:

- locked
- pending
- active
- verified

### 2.3 Runtime Event

A state transition or action that changes the runtime world.

Examples:

- buy
- move
- ask
- repair

### 2.4 Runtime Constraint

An allowed / disallowed condition that constrains valid states.

Examples:

- only Alice can open the door
- John cannot enter room A

### 2.5 Runtime Goal

A target condition the agent is trying to achieve.

### 2.6 Runtime Observation

Directly observed evidence from the source.

### 2.7 Runtime Inference

Derived semantic content that is not directly stated but is supported by evidence.

---

## 3. Runtime Layers

The runtime representation should be layered so that different kinds of semantic information can be represented and validated independently.

### 3.1 Semantic Graph

Responsibilities:

- objects
- relations
- events
- constraints

Use this layer for dependency-aware closure and relational integrity.

### 3.2 Semantic Frame

Responsibilities:

- event arguments
- role assignment
- action structure
- local state transitions

Use this layer when one text span describes a complete event.

### 3.3 Narrative Layer

Responsibilities:

- episode structure
- continuity
- goal / conflict / resolution

Use this layer for multi-turn or long-horizon story continuity.

### 3.4 Conversation Layer

Responsibilities:

- turn
- speaker
- intent
- question / answer / correction
- reference tracking

Use this layer for agent memory and dialogue continuity.

### 3.5 Runtime State Layer

Responsibilities:

- extracted
- canonicalized
- merged
- compressed
- recovered
- validated
- updated
- archived

Use this layer to make lifecycle explicit instead of implicit.

### 3.6 Provenance Layer

Responsibilities:

- source document
- turn
- sentence
- token span
- extraction method
- reasoning path
- compression round
- recovery mode
- validation outcome

Use this layer to answer: "why should we trust this node or edge?"

### 3.7 Confidence Layer

Responsibilities:

- identity confidence
- relation confidence
- constraint confidence
- temporal confidence
- recovery confidence
- validation confidence

Use this layer to avoid treating every semantic element as equally reliable.

---

## 4. Lifecycle State Machine

Runtime objects should follow an explicit lifecycle.

Recommended state machine:

```text
Extracted
  -> Canonicalized
  -> Merged
  -> Compressed
  -> Recovered
  -> Validated
  -> Updated
  -> Archived
```

Why this matters:

- it separates source extraction from downstream compression
- it makes provenance traceable
- it allows lifecycle fidelity to be measured

---

## 5. Provenance Ontology

Provenance should not be a single source-span field.

It should describe the full chain:

### 5.1 Origin

- sentence
- turn
- document
- token span

### 5.2 Evidence

- direct quote
- dependency evidence
- frame evidence
- cross-turn support

### 5.3 Transformation

- extracted
- inferred
- copied
- merged
- rewritten

### 5.4 Validation

- verified
- rejected
- updated
- repaired

This gives SRP a causal trace for each runtime item.

---

## 6. Confidence Model

Confidence should be represented as a vector, not a single scalar.

Suggested dimensions:

- identity
- attribute
- relation
- constraint
- temporal
- inference
- recovery
- validation

Why:

- different fields fail differently
- recovery should not overtrust weakly supported relations
- validation should be able to inspect confidence per semantic type

---

## 7. Extraction Pipeline

The Semantic Extraction Engine should be a pipeline, not a single prompt.

Recommended stages:

1. tokenization
2. sentence parsing
3. dependency parsing
4. coreference resolution
5. named entity recognition
6. semantic role labeling
7. temporal extraction
8. relation extraction
9. event extraction
10. runtime object construction
11. frame construction
12. graph assembly
13. validation

Why this matters:

- it lets SRP reuse mature NLP where appropriate
- it isolates the SRP-specific contribution to runtime IR assembly and recovery
- it makes extraction failures measurable before recovery begins

---

## 8. Evaluation Contract

Each layer should be evaluable on its own.

Suggested mapping:

| Layer | Example Metric |
| --- | --- |
| Token / parse | dependency accuracy |
| Entity / object | node capture rate |
| Relation | relation capture rate |
| Frame | frame completeness |
| Graph | graph integrity |
| Provenance | provenance completeness |
| Lifecycle | lifecycle accuracy |
| Recovery | validation coverage |

This contract is important because it separates extraction errors from recovery errors.

---

## 9. Ablation Roadmap

The architecture should support a clear ablation ladder:

1. text only
2. text + graph
3. text + graph + frame
4. text + graph + frame + provenance
5. full runtime IR

The key comparison is not "graph or not graph".
The key comparison is whether richer runtime IR layers reduce semantic loss and recovery cost.

---

## 10. Frozen Baselines

Keep frozen:

- graph v1
- graph v1.5
- graph recovery v1
- Stage 2 measurement layer

These remain the reference points while the extraction engine evolves.

Do not expand:

- graph recovery v2
- new graph schema fields without extraction evidence
- benchmark pressure used only to force a graph win

---

## 11. Long-Term Vision

The long-term SRP path is:

```text
Text
  -> Semantic Extraction Engine v2
  -> Runtime Representation v2
  -> Compression
  -> Recovery
  -> Validation
  -> Long-horizon state maintenance
```

If this works, SRP becomes a runtime semantic memory architecture, not just a compression trick.
