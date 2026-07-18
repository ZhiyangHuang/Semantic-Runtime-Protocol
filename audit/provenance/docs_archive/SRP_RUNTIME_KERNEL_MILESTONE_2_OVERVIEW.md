# SRP Runtime Kernel Milestone 2 Overview

Milestone 2 extends SRP from a semantic transition runtime into a version-aware semantic history runtime while preserving Milestone 1 execution semantics.

This is a short, citation-friendly overview. It does not replace the detailed interface, validation, or implementation documents.

---

## Runtime Architecture

```text
RuntimeEvent
    |
    v
DecisionEngine
    |
    v
DecisionResult
    |
    v
ConstraintEngine
    |
    v
SemanticOperator
    |
    v
TransitionResult
    |
    v
TraceBuilder
    |
    v
CommitManager
    |
    v
SemanticCommit
    |
    v
SemanticVersionGraph
```

---

## Runtime History Layer

### Decision Boundary

Status: verified

Responsibilities:

- deterministic operator selection
- explicit operator binding
- bounded candidate filtering

Non-goals:

- policy learning
- autonomous operator discovery

### Semantic Commit

Status: verified

Responsibilities:

- accepts completed transition evidence
- creates semantic history entries
- binds `event_id`, `transition_id`, `trace_id`, and `version_id`

### Version Graph

Status: verified

Supports:

- linear history
- branching history
- parent-child version relations

Invariant:

- `branch != conflict`

### Checkpoint Layer

Status: verified

Responsibilities:

- replay acceleration
- version-bound replay anchors

Non-goals:

- semantic history
- conflict resolution
- version mutation

---

## Conflict Evidence Layer

```text
SemanticVersionGraph
        |
        v
ConflictDetector
        |
        v
VersionConflict
        |
        v
ConflictQueryService
        |
        v
ConflictArchiveEvidenceAdapter
        |
        v
ArchiveQueryService
        |
        v
EvidenceSet
```

### Conflict boundary

Supported evidence types:

- duplicate transition evidence
- explicit semantic divergence evidence

Not supported:

- automatic merge
- rollback
- conflict repair

---

## Resolution Decision Layer

Status: verified

Responsibilities:

- convert conflict evidence into a bounded future semantic intent
- preserve rationale references
- avoid direct history mutation

Non-goals:

- conflict resolution by mutation
- automatic repair
- history rewriting


---

## Verified Invariants

| Boundary | Status |
| --- | --- |
| Milestone 1 compatibility | pass |
| Decision determinism | pass |
| Commit consistency | pass |
| Version DAG integrity | pass |
| Branch isolation | pass |
| Checkpoint isolation | pass |
| Replay equivalence | pass |
| Conflict detection determinism | pass |
| Archive evidence enrichment | pass |

---

## Frozen Non-Goals

- learned policy controller
- autonomous operator discovery
- automatic rollback
- automatic merge resolution
- distributed consensus
- checkpoint-based history rewrite

---

## Next Boundary

```text
Conflict Evidence
      |
      v
Resolution Decision
      |
      v
New Semantic Transition
```

Resolution should be represented as a new semantic transition, not as a hidden mutation inside the version system.
