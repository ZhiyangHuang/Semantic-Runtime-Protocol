# SRP Version Conflict Model

This document freezes the branch-conflict boundary for SRP semantic version history.
It is a theory document, not an implementation spec.

The central question is:

> When two or more semantic branches are individually valid, how does SRP represent the conflict instead of overwriting history?

The answer is conflict evidence, not automatic mutation.

---

## 1. Conflict Boundary

SRP must distinguish between:

- a valid branch
- a conflicting branch
- a resolved branch
- a rejected branch

Conflict detection belongs to the version-history layer.
It must not be confused with operator execution or replay.

### Correct boundary

```text
SemanticVersionGraph
      |
      v
ConflictDetector
      |
      v
VersionConflict
```

### Incorrect boundary

```text
SemanticVersionGraph
      |
      v
Auto Merge
```

### Meaning

- branch creation can be valid
- conflicting branches can both exist
- resolution is a later decision
- conflict evidence must remain queryable

---

## 2. VersionConflict Object

`VersionConflict` is a reference object that records inconsistency between semantic branches.

### Suggested shape

```python
from dataclasses import dataclass, field


@dataclass
class VersionConflict:
    conflict_id: str
    source_version_a: str
    source_version_b: str
    conflict_type: str
    conflicting_units: list[str] = field(default_factory=list)
    conflicting_relations: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    resolution_status: str = "unresolved"
```

### Semantics

- `source_version_a` and `source_version_b` identify the competing branches
- `conflict_type` names the category of mismatch
- `conflicting_units` names the units involved
- `conflicting_relations` names the relations involved
- `evidence_refs` keeps the conflict explainable
- `resolution_status` records the current state of the conflict evidence

### Non-goals

- mutating history automatically
- deleting branches
- rewriting commits
- hiding unresolved conflict evidence

---

## 3. Conflict Types

The model should support explicit conflict categories.

### Suggested conflict types

- `lineage_divergence`
- `semantic_incompatibility`
- `relation_conflict`
- `version_overlap`
- `checkpoint_mismatch`
- `replay_divergence`

### Semantics

- lineage divergence means two branches evolved from the same ancestry into different semantic outcomes
- semantic incompatibility means the branches cannot be treated as interchangeable
- relation conflict means the branches disagree on structure or linkage
- version overlap means two commits claim incompatible ownership of the same version line
- checkpoint mismatch means a replay anchor cannot be aligned with the requested branch
- replay divergence means different replay paths reconstruct different states

---

## 4. Resolution Types

Conflict resolution should be modeled before any implementation is added.

### 4.1 Accept Branch

One branch is treated as the canonical continuation.

```text
Version A
   |
   +-- Version B
   +-- Version C

Version C becomes canonical
```

This is a resolution choice, not a mutation of the evidence itself.

### 4.2 Merge Branch

Conflict evidence can be routed into the existing merge path.

```text
ConflictEvidence
      |
      v
DecisionEngine
      |
      v
MergeOperator
```

Merge remains a semantic transition, not a hidden fix.

### 4.3 Reject Branch

The conflict can remain unresolved or be explicitly rejected.

```text
Version A
   |
   +-- Version B

Version B status = rejected
```

Rejection does not delete history.

---

## 5. Replay Boundary

Rollback must not be modeled as reverse history rewriting.

### Correct rule

```text
Rollback request
      |
      v
Create new semantic transition
      |
      v
Commit new version
```

### Incorrect rule

```text
Delete commits
Rewrite history
```

Replay must remain forward, deterministic, and evidence-driven.
Conflict handling should not break traceability, auditability, or archive references.

---

## 6. Checkpoint Interaction

Checkpointing is replay acceleration, not conflict resolution.

### Boundary

```text
VersionConflict
      |
      v
Decision / Resolution
      |
      v
SemanticCommit
      |
      v
RuntimeCheckpoint
```

### Semantics

- checkpoint selection can be affected by a branch conflict
- checkpoint creation does not resolve the conflict
- checkpoint does not select the canonical branch by itself

---

## 7. Relationship to Existing Layers

### Relation to version graph

The version graph stores the branch structure.

### Relation to commit

Commit creates branch nodes.
Conflict evidence explains when branches disagree.

### Relation to decision

Decision can later choose a resolution path, but the conflict model itself is pre-decision evidence.

### Relation to replay

Replay can surface divergence, but it must not rewrite conflict history.

---

## 8. Non-Goals

The conflict model is not:

- automatic rollback
- automatic merge
- history rewriting
- checkpoint-based branch selection
- semantic branch deletion

It is the evidence layer that makes branch disagreement explicit and queryable.

