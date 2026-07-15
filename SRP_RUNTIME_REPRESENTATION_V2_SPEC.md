# SRP Runtime Representation v2 Specification

This document is the canonical specification for SRP Runtime Representation v2 (SRR v2).

It defines the semantic runtime IR that SRP operates on.

The key claim is:

```text
SRP compresses, recovers, and validates runtime semantics, not raw text.
```

That means the runtime object is not a graph node set. It is a layered semantic representation with explicit ontology, lifecycle, provenance, and confidence.

---

## 1. Scope

SRR v2 defines:

- runtime ontology
- runtime object model
- runtime layers
- node typing
- frame typing
- narrative typing
- conversation typing
- runtime state machine
- provenance ontology
- confidence ontology
- projection rules
- extraction rules
- recovery rules
- validation rules
- evaluation contract

SRR v2 does not define a new benchmark suite. It defines the intermediate representation that later benchmarks will evaluate.

---

## 2. Runtime Philosophy

SRP should operate on semantic runtime state rather than raw language.

Design principles:

- preserve meaning, not wording
- make state explicit
- separate extraction from recovery
- keep provenance attached to every semantic object
- represent uncertainty explicitly
- validate semantic continuity across lifecycle transitions

---

## 3. Runtime Ontology

### 3.1 RuntimeObject

The base semantic unit.

Fields:

- `id`
- `type`
- `label`
- `identity`
- `properties`
- `state`
- `importance`
- `confidence`
- `provenance`
- `lifecycle`
- `relations`

### 3.2 RuntimeState

A mutable semantic condition of an object or system.

Examples:

- locked
- pending
- active
- verified

### 3.3 RuntimeEvent

A state-changing action or occurrence.

Examples:

- buy
- move
- ask
- repair

### 3.4 RuntimeConstraint

A condition that restricts valid runtime states.

Examples:

- only Alice can open the door
- John cannot enter room A

### 3.5 RuntimeGoal

An intended future condition.

### 3.6 RuntimeObservation

Directly observed evidence from the source.

### 3.7 RuntimeInference

Derived content supported by evidence but not directly stated.

### 3.8 RuntimeDecision

A choice or selection made during runtime.

### 3.9 RuntimeTask

A task or subtask that should persist across recovery and validation.

### 3.10 RuntimeResult

The outcome of a runtime action or episode.

---

## 4. Runtime Layers

The representation is layered. Each layer is independently inspectable and evaluable.

### 4.1 Semantic Graph Layer

Purpose:

- objects
- relations
- events
- constraints

Use:

- dependency closure
- relational integrity
- object survival tracking

### 4.2 Semantic Frame Layer

Purpose:

- predicate / arguments
- event roles
- local action structure

Use:

- event reconstruction
- role completeness
- action-level recovery

### 4.3 Narrative Layer

Purpose:

- episode continuity
- goal / conflict / resolution
- story progression

Use:

- long-horizon coherence
- cross-turn memory

### 4.4 Conversation Layer

Purpose:

- turn
- speaker
- listener
- dialogue act
- intent
- question / answer / correction
- reference tracking

Use:

- dialogue memory
- conversational consistency

### 4.5 Runtime State Layer

Purpose:

- extracted
- canonicalized
- merged
- compressed
- recovered
- validated
- updated
- archived

Use:

- lifecycle fidelity
- state drift analysis

### 4.6 Provenance Layer

Purpose:

- source document
- turn
- sentence
- token span
- extraction method
- reasoning path
- compression round
- recovery mode
- validation outcome

Use:

- trust tracing
- reconstruction audit

### 4.7 Confidence Layer

Purpose:

- identity confidence
- relation confidence
- constraint confidence
- state confidence
- temporal confidence
- recovery confidence
- validation confidence

Use:

- selective recovery
- uncertainty-aware validation

---

## 5. Node Typing

SRR v2 should support a typed node system.

### 5.1 Core Types

- `Entity`
- `Person`
- `Organization`
- `Location`
- `Time`
- `Artifact`
- `Resource`
- `Role`

### 5.2 Semantic Types

- `Observation`
- `Fact`
- `Event`
- `Action`
- `State`
- `Goal`
- `Intent`
- `Plan`
- `Constraint`
- `Capability`
- `Permission`
- `Rule`
- `Memory`
- `ConversationTurn`
- `Utterance`
- `Question`
- `Answer`
- `Correction`
- `Reference`
- `Summary`
- `Inference`
- `Hypothesis`
- `Decision`
- `Task`
- `Result`
- `Error`

### 5.3 Typing Rule

Type should reflect semantic function, not only surface form.

Examples:

- a direct observation should not be typed as an inference
- a constraint should not be collapsed into a generic fact
- a conversation turn should not be collapsed into an entity

---

## 6. Frame Typing

A frame represents a semantic event with explicit arguments.

Example:

```text
give
  agent: John
  theme: book
  recipient: Mary
```

Frame fields:

- predicate
- agent
- patient
- theme
- recipient
- source
- destination
- instrument
- time
- location
- reason
- result

Frame rule:

- if the text expresses a complete event, build a frame
- if the text contains only a fragment, keep the fragment and mark it partial

---

## 7. Narrative Typing

Narrative captures episode-level continuity.

Required constructs:

- episode
- scene
- conflict
- goal
- attempt
- failure
- retry
- success
- resolution

Narrative rule:

- preserve episode continuity when a task spans multiple turns or spans
- do not flatten story structure into isolated facts

---

## 8. Conversation Typing

Conversation captures dialogue structure.

Required constructs:

- turn
- speaker
- listener
- dialogue act
- intent
- question
- answer
- correction
- confirmation
- reference

Conversation rule:

- preserve interaction structure separately from propositional content
- represent corrections explicitly rather than overwriting prior state blindly

---

## 9. Runtime State Machine

Runtime objects should move through a lifecycle state machine.

Recommended states:

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

Lifecycle rules:

- `Extracted`: object first enters SRR
- `Canonicalized`: object normalized into a stable form
- `Merged`: duplicate or coreferent content joined
- `Compressed`: object stored in compact runtime form
- `Recovered`: object reconstructed for downstream use
- `Validated`: object checked against source or constraints
- `Updated`: object changes with new evidence
- `Archived`: object is no longer active but remains traceable

---

## 10. Provenance Ontology

Provenance should describe origin, evidence, transformation, and validation.

### 10.1 Origin

- document
- conversation
- turn
- sentence
- token span

### 10.2 Evidence

- direct quote
- dependency evidence
- frame evidence
- cross-turn support

### 10.3 Transformation

- extracted
- inferred
- copied
- merged
- rewritten

### 10.4 Validation

- verified
- rejected
- updated
- repaired

Provenance rule:

- every runtime object should carry enough provenance to explain why it exists

---

## 11. Confidence Ontology

Confidence is multi-dimensional.

Required dimensions:

- identity
- attribute
- relation
- constraint
- state
- temporal
- inference
- recovery
- validation

Confidence rule:

- do not collapse all confidence into a single scalar when a dimension-specific value is available

---

## 12. Projection Rules

Projection means converting SRR into a use-specific view.

Allowed projections:

- graph projection
- frame projection
- narrative projection
- conversation projection
- state projection

Projection rules:

- graph is a view, not the whole representation
- projection should not invent information that is absent from SRR
- every projection should preserve provenance links when possible

---

## 13. Extraction Rules

The extraction engine should prefer staged extraction over one-shot generation.

Recommended pipeline:

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

Extraction rules:

- distinguish extracted content from inferred content
- keep partial objects as partial objects
- attach provenance before compression
- preserve explicit constraints

---

## 14. Recovery Rules

Recovery should operate on the runtime representation, not directly on raw text.

Recovery rules:

- reconstruct only missing semantic state
- prefer dependency closure over unconstrained generation
- block unsupported object creation when provenance is absent
- respect confidence thresholds when deciding whether to repair or retain uncertainty

---

## 15. Validation Rules

Validation should measure semantic continuity between source and recovered runtime state.

Required checks:

- node capture
- relation capture
- constraint capture
- frame completeness
- narrative continuity
- conversation continuity
- lifecycle fidelity
- provenance completeness
- confidence consistency

Validation rule:

- a recovered object is not sufficient if it violates provenance or lifecycle consistency

---

## 16. Evaluation Contract

Each layer should have a measurable signal.

| Layer | Primary Evaluation |
| --- | --- |
| Token / parse | dependency accuracy |
| Entity / object | node capture rate |
| Relation | relation capture rate |
| Frame | frame completeness |
| Narrative | episode continuity |
| Conversation | dialogue continuity |
| Graph | graph integrity |
| Provenance | provenance completeness |
| Lifecycle | lifecycle accuracy |
| Recovery | validation coverage |

Secondary metrics:

- extraction latency
- representation size
- repair cost
- hallucinated object count

---

## 17. Ablation Ladder

The architecture should support the following progression:

1. text only
2. text + graph
3. text + graph + frame
4. text + graph + frame + provenance
5. full SRR v2

This ladder allows the effect of each layer to be isolated.

---

## 18. Frozen Baselines

Keep frozen:

- graph v1
- graph v1.5
- graph recovery v1
- Stage 2 measurement layer

These remain the baseline comparison points while SRR v2 evolves.

Do not expand:

- graph recovery v2
- more graph fields without extraction evidence
- benchmark pressure only to force a graph win

---

## 19. Long-Term Vision

SRR v2 is intended to become the semantic substrate for:

- compression
- recovery
- validation
- reasoning
- planning
- agent memory
- persistent runtime state

In short:

```text
Text
  -> Semantic Extraction Engine v2
  -> SRR v2
  -> Compression
  -> Recovery
  -> Validation
  -> Long-horizon state maintenance
```

