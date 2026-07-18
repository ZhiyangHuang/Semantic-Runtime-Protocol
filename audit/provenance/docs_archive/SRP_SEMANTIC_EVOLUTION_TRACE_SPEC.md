# SRP Semantic Evolution Trace Spec

This document defines the engineering specification for semantic evolution traces in SRP.
It is not a history format and not a replay implementation spec.

The central question is:

> How can SRP represent the causal path by which a SemanticUnit moved from one state to another?

This layer sits between the event stream and the query surface for evolutionary explanation.

---

## 1. Trace Purpose

A trace is a queryable causal structure for semantic evolution.

It is not the same as:

- `History`, which summarizes past behavior
- `EventStream`, which records valid transitions

Trace answers:

- why a unit changed
- which events caused the change
- which rules authorized the change
- which mechanism contributed to the drift or recovery path

---

## 2. Trace Three-Layer Structure

```text
Semantic Evolution Trace
  -> Trace Node
  -> Trace Edge
  -> Trace Record
```

### Trace Node

A trace node represents one observation point in a unit's evolution.

### Trace Edge

A trace edge represents the causal reason that one node led to another.

### Trace Record

A trace record is the queryable explanation assembled from nodes and edges.

---

## 3. Trace Node Specification

A trace node should represent a semantic state version or a reference to one.

It should not duplicate the full state object.

### Required fields

- `trace_node_id`
- `unit_id`
- `round_id`
- `state_snapshot_reference`
- `activation`
- `confidence`
- `lifecycle_state`
- `embedding_reference`
- `drift_score`

### Optional fields

- `canonical_name`
- `approximation_target`
- `recovery_reference`
- `archive_reference`

### Node rules

- a node must anchor to a stable `unit_id`
- a node should reference a state version rather than embed the whole state
- a node may summarize values such as activation or lifecycle state

### Node example

```text
unit_001
  round 1
  active
  activation=0.9

unit_001
  round 50
  approximate
  activation=0.4

unit_001
  round 120
  forgotten
```

---

## 4. Trace Edge Specification

A trace edge connects two nodes and explains the transition.

### Required fields

- `trace_edge_id`
- `source_node_id`
- `target_node_id`
- `event_id`
- `rule_id`
- `mechanism`
- `change_type`
- `confidence`

### Edge rules

- `event_id` must identify the event that occurred
- `rule_id` must identify the rule that allowed or caused the transition
- `mechanism` should identify the preservation or degradation mechanism involved
- `change_type` should summarize the transition category

### Edge example

```text
Node1
  -- ActivationDecay
  -> Node2
```

This edge should be interpretable as:

```text
event_id + rule_id + mechanism = causal explanation
```

---

## 5. Trace Record Specification

A trace record is the query-facing structure.

It should answer questions such as:

- Why did this unit become unknown?
- Which event caused the approximation?
- Which rule authorized the recovery?
- Where did the drift come from?

### Trace record shape

```text
TraceRecord
  -> unit_id
  -> causal_path
  -> current_state_reference
  -> drift_summary
  -> recovery_lineage
```

### Record requirements

- the record must be queryable by unit id
- the record must be reconstructible from nodes and edges
- the record should not require duplicating every full state snapshot

### Example query answer

```text
SemanticUnit Alice
  SemanticExtracted
  Canonicalized
  ActivationDecay
  Approximated(to Bob)
  Forgotten
  RecoveryRequested
  RecoveryFailed
  UnknownPlaceholderCreated
```

---

## 6. Trace and Drift

Trace is a first-class input to drift explanation.

Drift should be attributed through the trace path rather than inferred only from history summaries.

### Drift relationship

```text
Trace
  -> state differences
  -> drift measurement
```

### Drift accumulation

The cumulative drift should be modeled as:

```text
D_total = sum(drift(event_i))
```

This is preferable to comparing only the current state against an aggregated history summary.

### Drift requirements

- drift should be attributable to transitions
- drift should be explainable through trace edges
- drift should remain queryable even if history is summarized

---

## 7. Trace and Replay

Trace and replay are related but distinct.

### Replay

Input:

```text
EventStream
```

Output:

```text
SemanticState
```

### Trace

Input:

```text
EventStream + state references + rule references
```

Output:

```text
Evolution explanation
```

Replay reconstructs state.
Trace explains why that state exists.

---

## 8. Trace Query Model

Trace should be queryable by at least:

- `unit_id`
- `round_id`
- `event_id`
- `rule_id`
- `change_type`

Query results should expose:

- path
- drift summary
- recovery lineage
- approximation lineage
- lifecycle transitions

---

## 9. Relationship to Attribution

Trace supports mechanism attribution directly.

Recommended chain:

```text
Mechanism
  -> Event
  -> Trace Edge
  -> Preservation Objective
  -> Metric
```

This makes trace a natural bridge into ablation, recovery analysis, and drift attribution.

---

## 10. Relationship to Other Documents

Recommended chain:

```text
Runtime Kernel Migration Checklist
  -> Runtime Kernel Phase Migration Map
  -> Semantic Evolution Trace Spec
  -> Replay-Oriented Implementation Work
```

This spec is intended to be the engineering anchor before mapping trace concepts to current record builders or summary layers.

---

## 11. Scope

This document defines trace structure only.

It does not define:

- storage implementation
- database schema
- summary rendering
- replay engine internals

Those belong to later implementation work.

