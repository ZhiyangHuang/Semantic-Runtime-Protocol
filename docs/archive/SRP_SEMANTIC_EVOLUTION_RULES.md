# SRP Semantic Evolution Rules

This document defines when semantic transitions should occur in SRP.
It is not an implementation spec.

The central question is:

> Under what conditions should a runtime event be emitted, and what semantic change is justified?

This layer sits between the event contract and policy mechanisms.

The detailed decision boundary is frozen in [Semantic Evolution Rule Table](SRP_SEMANTIC_EVOLUTION_RULE_TABLE.md).
The event handling shape that executes those decisions is defined in [Runtime Event Interface](SRP_RUNTIME_EVENT_INTERFACE.md).
The producer / validator / applier lifecycle is defined in [Runtime Event Processing Model](SRP_RUNTIME_EVENT_PROCESSING_MODEL.md).

---

## 1. Evolution Model

SRP evolution can be modeled as:

```text
Semantic State
    -> Evolution Trigger
    -> Decision Rule
    -> Runtime Event
    -> New Semantic State
```

The event contract defines what a valid event looks like.
The evolution rules define when that event should happen.

---

## 2. Rule Families

The main rule families are:

- consolidation rules
- activation decay rules
- approximation rules
- recovery rules
- garbage collection rules
- evolution invariants

These rules govern semantic state change under time, pressure, and evidence.

---

## 3. Consolidation Rules

Consolidation is not just merging strings.
It is the process of deciding whether multiple forms should become one canonical semantic unit or one conceptual family.

### 3.1 Alias Consolidation

Alias consolidation applies when multiple forms refer to the same entity or concept.

Example:

```text
OpenAI
Open AI
OAI
```

Suggested condition:

```text
semantic_similarity > θ1
AND context_usage_overlap > θ2
AND entity_type_match = true
```

If the condition holds, emit:

- `Canonicalized`

Result:

- one canonical unit
- alias list preserved in metadata

### 3.2 Identity Merge

Identity merge is stricter than alias consolidation.

It applies when two units are likely the same identity, not just similar text.

Example:

```text
John Smith
the CEO
```

Suggested condition:

```text
identity_confidence > θ1
AND context evidence sufficient
AND relation consistency preserved
```

If the condition does not hold, do not merge.
Prefer approximation or separate identity tracking.

If the condition holds, emit:

- `Merged`

### 3.3 Concept Refinement

Concept refinement applies when one concept is not an alias of another, but a more specific or structured concept.

Example:

```text
vehicle
  -> Tesla
```

This is not aliasing.
It is a semantic relation.

Suggested rule:

- preserve the broader concept
- add or strengthen an `is-a` style relation
- do not collapse the concepts into one unit

If the relation is newly established or strengthened, emit:

- `Consolidated`

---

## 4. Activation Decay Rules

Activation should decay through usage and time, not via hard deletion.

Suggested conceptual model:

```text
activation = f(usage_count, last_used_round, importance, confidence)
```

Or:

```text
M(t) = initial_strength * usage_factor * recency_factor * importance_factor
```

### Threshold bands

- `activation > α1` -> active
- `α2 < activation <= α1` -> stable
- `α3 < activation <= α2` -> dormant
- `activation <= α3` -> approximate
- `activation ≈ 0` -> forgotten

The exact values should be configurable by workload.

### Decay rule

If a unit has not been used for `N` rounds, emit:

- `ActivationUpdated`

The event must include:

- `old_activation`
- `new_activation`
- `reason`
- `decay_source`

The state after decay may also lower retention priority.

---

## 5. Approximation Rules

Approximation is a controlled degradation step, not deletion.

It preserves recoverability while acknowledging that the exact original concept is no longer fully available.

Example:

```text
Tesla Model S
  -> electric vehicle
```

Suggested payload:

```yaml
original_id: unit_123
replacement: electric_vehicle
semantic_distance: 0.21
confidence: 0.79
```

### Approximation condition

Approximation is appropriate when:

- activation is below a threshold
- direct recovery confidence is too low
- a semantically close surrogate exists

If approximation occurs, emit:

- `Approximated`

### Approximation invariants

- approximation must record distance or error
- approximation must preserve non-identical status
- approximation must remain reversible in principle if evidence later improves

---

## 6. Recovery Rules

Recovery should be evidence-based and should prefer confirmation over hallucination.

Recovery is best treated as three stages:

1. candidate generation
2. candidate validation
3. recovery decision

### 6.1 Candidate Generation

Candidate sources may include:

- graph neighbors
- prior events
- embeddings
- historical contexts
- alias history

Candidate generation produces a candidate set, not a final decision.

### 6.2 Candidate Validation

The recovery candidate should be checked against multiple independent semantic contexts.

Recommended rule:

- require at least 3 independent supporting contexts when available

Suggested score:

```text
RecoveryConfidence = mean(similarity) - variancePenalty
```

If the candidate set is weak or contradictory, do not auto-recover.

### 6.3 Recovery Decision

If confidence exceeds the recovery threshold, emit:

- `Recovered`

If confidence is below threshold, emit:

- `RecoveryRequested`

and request user confirmation or additional evidence.

### Recovery invariants

- recovered content must have provenance
- recovery must preserve traceability to source evidence
- low-confidence recovery must not silently replace stronger known state

---

## 7. Garbage Collection Rules

Garbage collection is the last stage, not the default stage.

Suggested lifecycle:

```text
Active
  -> Dormant
  -> Archived
  -> Collected
```

A unit may be collected only when:

- it has no active references
- it has no meaningful relations
- it has no recovery value under the current policy
- its drift or preservation impact is negligible

If collection is approved, emit:

- `GarbageCollected`

### Garbage collection invariants

- collection must not happen while the unit still has required references
- collection should preserve audit metadata when possible
- hard deletion should be distinguishable from archival decay

---

## 8. Evolution Invariants

Evolution rules must preserve a few hard constraints.

### Identity invariant

One identity must not spontaneously become multiple canonical identities without an explicit split event.

### Recovery invariant

Recovered content must not appear without provenance or evidence trace.

### Approximation invariant

Approximation must always record distance, error, or a comparable surrogate-quality measure.

### Forgetting invariant

Forgetting should not erase traceability unless the policy explicitly allows hard deletion.

### Transition invariant

Every semantic change must be backed by an allowed event type.

---

## 9. Relation to Policy

Policy and evolution rules are different.

### Policy answers

- What should survive under pressure?
- How should resources be allocated?
- Which objects deserve retention priority?

### Evolution rules answer

- Is this transition allowed?
- What conditions justify it?
- What event should be emitted?

Example:

- Policy may decide to drop a low-importance unit.
- Evolution rules require that the drop be expressed as `Forgotten`, `Archived`, or `GarbageCollected`, not as an untracked mutation.

Policy chooses.
Evolution rules authorize.

---

## 10. Protocol Placement

Recommended layer order:

```text
Semantic Evolution Framework
  -> Runtime Object Model
  -> Runtime Data Contract
  -> Runtime Event Contract
  -> Semantic Evolution Rules
  -> Policy Mechanisms
  -> Runtime Lifecycle
  -> Evaluation + Attribution
```

This keeps legality, conditions, and resource allocation distinct.

---

## 11. Scope

This document defines the conditions under which semantic transitions should happen.

It does not define:

- field syntax
- event serialization
- module implementation
- scoring code

Those belong to the data contract, event contract, and implementation layers.
