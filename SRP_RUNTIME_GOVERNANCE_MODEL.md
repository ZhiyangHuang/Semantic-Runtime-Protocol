# SRP Runtime Governance Model

SRP is not only a transition runtime. It is also a governance runtime that separates execution authority, history authority, and governance authority.

This document freezes the high-level authority split used by Milestone 2 and the resolution-decision boundary.

---

## 1. Authority Split

### Execution Authority

```text
Operator
```

Execution authority applies a selected semantic mutation.

### History Authority

```text
Commit + VersionGraph
```

History authority decides when a completed transition enters semantic history.

### Governance Authority

```text
Decision + Conflict + Resolution
```

Governance authority decides which bounded semantic intent should happen next when evidence or constraints require a choice.

---

## 2. Governance Boundary

The governance layer does not mutate semantic history directly.

```text
Conflict Evidence
      |
      v
Resolution Decision
      |
      v
Semantic Event Intent
      |
      v
RuntimeEvent
      |
      v
DecisionEngine
      |
      v
Operator
      |
      v
SemanticCommit
```

### Semantics

- conflict evidence describes what is known
- resolution decision describes what should be attempted next
- runtime execution performs the next semantic transition

### Non-goals

- automatic repair
- hidden history rewriting
- policy learning

---

## 3. Why SRP is not a Memory System

SRP is not just storing state.
It maintains an evolving semantic world with:

- explicit transitions
- bounded decision boundaries
- commit-based history
- replayable checkpoints
- evidence-backed conflict analysis

This is why SRP differs from:

- RAG
- KV cache reuse
- plain version control
- generic agent planners

---

## 4. Relation to Milestone 2

Milestone 2 validates the runtime governance path:

- deterministic decision
- commit-based version history
- checkpoint replay acceleration
- evidence-first conflict analysis
- bounded resolution decision

Milestone 2 intentionally does not implement automatic conflict repair or learning-assisted policy selection.

