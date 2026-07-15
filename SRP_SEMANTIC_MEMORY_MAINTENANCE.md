# SRP Semantic Evolution Framework

This document defines the semantic evolution layer for SRP.
It is not an implementation spec.

The central question is:

> How should semantic state evolve over time so that active meaning survives, stale meaning decays, and recoverable meaning can still be restored?

This layer is inspired by AMR-style semantic normalization, human-like forgetting curves, and long-horizon memory systems that separate active content from archived content.

---

## 1. Purpose

SRP should not treat memory as a static append-only store.
Semantic state should be maintained as an evolving semantic system with six core jobs:

- normalize equivalent meanings
- merge redundant or synonymous forms
- consolidate stable structures over time
- decay low-usage content over time
- recover forgotten content when evidence is strong enough
- garbage-collect content only after safer stages are exhausted

This makes memory behave more like human recall than like a database dump.

---

## 2. State Tiers

SRP semantic state can be described with two temporal tiers:

### Short-term Memory

Short-term memory holds recently activated semantic content.

Typical properties:

- high salience
- frequent reuse
- short decay horizon
- fast access

Short-term memory is the active working set of the runtime.

### Long-term Memory

Long-term memory holds consolidated semantic content that survives across many rounds.

Typical properties:

- canonical entities
- stable relations
- aliases and historical forms
- archived but recoverable content

Long-term memory is not just storage.
It is a decay-managed semantic archive.

### Activation State

Each semantic unit should carry an activation profile that can be read by policy and evolution rules.

Suggested fields:

- `activation`
- `last_used_round`
- `decay_rate`
- `reactivation_bonus`
- `forget_threshold`
- `consolidation_score`

---

## 3. Canonicalization

Canonicalization ensures that semantically equivalent forms map to the same maintained concept.

Examples:

```text
NYC -> New York City
Open AI -> OpenAI
ChatGPT = GPT assistant
```

The maintenance rule is:

- keep the latest canonical form at the front
- store aliases in the description or alias field
- merge equivalent labels into one semantic unit

Useful equivalence patterns:

- `xxx is xxx`
- `xxx equals xxx`
- `xxx means xxx`
- `xxx refers to xxx`
- `xxx = xxx`

If a new form is better normalized than the old one, the new canonical form should replace the old head entry while preserving the previous forms as aliases.

---

## 4. Consolidation

Consolidation is the long-horizon version of merge.
It groups repeatedly co-activated units into a more stable semantic structure.

Consolidation should be applied to:

- repeated co-mentions
- entity families
- nested concepts
- stable dependency chains

Consolidation is how SRP turns repeated usage into durable structure.

The consolidation result should preserve:

- canonical name
- alias list
- supporting evidence
- provenance
- confidence
- activation history

---

## 5. Merge

Merge combines redundant semantic units when they describe the same underlying concept.

Merge should be applied to:

- alias variants
- near-duplicate labels
- paraphrased definitions
- repeated references to the same entity

Merge is not just string replacement.
It is semantic consolidation.

The merge result should preserve:

- canonical name
- alias list
- supporting evidence
- provenance
- confidence

---

## 6. Forgetting Curve

SRP should use a human-like forgetting curve instead of immediate deletion.

The key idea is:

- if a concept is not used for many rounds, its activation decays
- if a concept is used again, its retention horizon increases
- time is measured in conversation rounds or equivalent runtime cycles

This means the same concept can be easier or harder to forget depending on its usage history.

### Suggested retention dynamics

```text
recent use -> higher activation
repeated use -> slower decay
long silence -> lower activation
low activation -> dormant
dormant -> approximate
approximate -> unknown
unknown -> deleted only if policy allows
```

### Suggested round-based heuristic

- if a concept is not referenced for about 100 rounds, it may be eligible for forgetting
- each successful reference should extend its retention horizon
- high-value concepts should decay more slowly than low-value concepts

This threshold should be configurable, not hard-coded as a universal truth.

---

## 7. Activation Model

Memory maintenance should track activation rather than only presence.

Activation can be influenced by:

- frequency
- recency
- importance
- dependency centrality
- recovery utility
- validation history

One possible conceptual model is:

```text
activation = frequency + recency + importance + dependency_support - decay
```

The exact formula can vary, but the theory should preserve the idea that memory strength is dynamic.

---

## 8. Replacement by Approximation

When a concept weakens but is not fully deleted, SRP may replace it with the closest semantic surrogate.

Example:

```text
original concept -> closest semantic substitute -> broader concept -> unknown placeholder
```

This replacement should be chosen by semantic similarity, not by surface form alone.

Rules:

- use the most semantically similar available concept
- record the deviation from the original
- mark the surrogate as not identical to the original
- degrade gracefully from specific -> approximate -> placeholder

Suggested placeholder forms:

- `placeholder`
- `unknown concept`
- `null`
- graph gap / broken link

In the graph, this is equivalent to a broken chain, missing node, or empty semantic slot.

---

## 9. Recovery From Forgetting

If a forgotten concept is called again, SRP should attempt reconstruction before giving up.

Recovery should use multiple evidence sources:

- nearby semantic neighbors
- aliases and canonical history
- prior sentence contexts
- graph relations
- vector similarity to historical forms
- local model reconstruction

Recovery is accepted only when confidence is high enough.

### Recommended recovery condition

To avoid brittle reconstruction, use multi-evidence confirmation.

At minimum, the recovered concept should be supported by several independent semantic contexts.

Recommended default:

- at least three comparable semantic sentences or contexts when available

This should be treated as a strong default policy, not a universal hard rule.

### Recovery acceptance rule

Recovery confidence should increase when:

- multiple contexts agree
- the graph neighborhood is consistent
- alias history matches
- embedding distance is small
- reconstructed text fits the original semantic pattern

If confidence is low, the system should ask the user to confirm the recovered concept.

---

## 10. Deletion Semantics

Deletion should be an explicit maintenance action, not an accidental side effect.

Supported intent forms may include:

- `forget xxx`
- `ignore xxx`
- `remove xxx`
- `delete xxx`

These commands should target a semantic unit, alias family, or concept cluster.

Deletion policy should distinguish:

- soft forgetting
- dormant hiding
- approximate replacement
- hard deletion

Hard deletion should be the last stage, not the default outcome.

---

## 11. Semantic Unit State Machine

The semantic unit state machine can be represented as:

```text
active
  -> stable
  -> inactive
  -> dormant
  -> approximate
  -> forgotten
  -> deleted
```

Reactivation should be possible from `inactive`, `dormant`, or `approximate` when evidence is sufficient.

This state machine is different from the normal runtime lifecycle.

The runtime lifecycle describes how state moves through the system.
The semantic unit state machine describes how one concept changes across time.

---

## 12. Evolution Operations

The evolution framework should expose the following operations:

- `state_update`
- `canonicalize`
- `consolidate`
- `forget`
- `approximate`
- `recover`
- `garbage_collect`

These operations are the semantic evolution rules that higher layers can observe and attribute.

---

## 13. Maintenance Lifecycle

The maintenance lifecycle can be represented as:

```text
active
  -> stable
  -> dormant
  -> approximate
  -> unknown
  -> deleted
```

This lifecycle is different from the normal runtime lifecycle.

The runtime lifecycle describes how state moves through the system.
The maintenance lifecycle describes how memory strength changes over time.

---

## 14. Operational Rules

The maintenance layer should follow these rules:

- keep canonical forms stable
- preserve aliases in descriptions
- merge equivalent concepts early
- decay unused concepts gradually
- prefer semantic substitution over immediate deletion
- require confidence for reconstruction
- request user confirmation when recovery is uncertain

These rules are designed to keep memory compressible without destroying meaning.

---

## 15. Execution Preparation

This document is intended to prepare SRP for future implementation work.

The next execution steps should likely include:

- a maintenance state schema for canonical forms, aliases, and activation
- a decay policy based on turn count and usage history
- a replacement policy based on semantic similarity
- a recovery policy based on multi-evidence confidence
- a deletion policy with soft and hard modes

The implementation should keep maintenance separate from policy scoring so the two layers remain measurable.

---

## 16. Scope

This document defines the maintenance theory for memory evolution.

It does not define:

- the final storage format
- the exact decay formula
- the local model used for recovery
- the final graph schema
- the production command interface

Those belong to later implementation and evaluation documents.
