# SRP Version Resolution Decision Model

This document freezes the decision boundary that turns verified conflict evidence into a proposed semantic transition intent.
It is not a conflict resolver and it does not mutate history.

The central question is:

> Given conflict evidence, how does SRP decide what semantic intent should happen next without rewriting the past?

The answer is a bounded decision layer that produces a future event intent.

---

## 1. Resolution Boundary

Resolution is downstream from conflict evidence:

```text
VersionConflict
      |
      v
ConflictQueryService
      |
      v
EvidenceSet
      |
      v
ResolutionDecisionService
      |
      v
ResolutionDecision
      |
      v
Semantic Event Intent
```

### Correct boundary

```text
Conflict Evidence
      |
      v
Resolution Decision
      |
      v
New Semantic Intent
```

### Incorrect boundary

```text
Conflict
      |
      v
Automatic Resolution
```

---

## 2. ResolutionContext

The first layer is a bounded input object that describes the conflict facts:

```python
@dataclass
class ResolutionContext:
    resolution_id: str
    conflict_id: str
    source_versions: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    conflict_type: str = ""
    available_actions: list[str] = field(default_factory=list)
    decision_constraints: list[str] = field(default_factory=list)
```

### Semantics

- `conflict_id`
  - the conflict being addressed
- `source_versions`
  - versions implicated by the conflict
- `evidence_refs`
  - supporting evidence references
- `conflict_type`
  - conflict category
- `available_actions`
  - bounded action vocabulary available to the decision layer
- `decision_constraints`
  - explicit constraints that must hold before a recommendation is produced

### Non-goals

- state mutation
- operator execution
- version updates
- checkpoint creation

---

## 3. ResolutionAction

The action vocabulary is intentionally small.

```text
AcceptBranch
MergeProposal
RejectBranch
CorrectionTransition
```

### Semantics

- `AcceptBranch`
  - choose one existing branch as the continuation path
- `MergeProposal`
  - propose that a future merge transition should be created
- `RejectBranch`
  - recommend that a branch should not remain active
- `CorrectionTransition`
  - recommend creating a new semantic correction event

### Important boundary

`MergeProposal` is not `MergeOperator`.
It is only a decision result that may later become a runtime event.

---

## 4. ResolutionDecision

The decision layer produces a bounded recommendation:

```python
@dataclass
class ResolutionDecision:
    resolution_id: str
    conflict_id: str
    selected_action: str
    rationale_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    created_event_intent: dict[str, object] = field(default_factory=dict)
```

### Semantics

- `selected_action`
  - the bounded recommendation chosen by the resolution layer
- `rationale_refs`
  - evidence or trace references that explain the recommendation
- `confidence`
  - bounded confidence signal for the recommendation
- `created_event_intent`
  - a future semantic event intent, not an executed runtime event

### Example intent

```json
{
  "event_type": "SemanticCorrectionRequested",
  "source_version": "v12",
  "target_intent": "merge_branch"
}
```

---

## 5. ResolutionDecisionService

The service evaluates evidence and produces a bounded recommendation.

```python
class ResolutionDecisionService:
    def evaluate(
        self,
        context: ResolutionContext,
    ) -> ResolutionDecision:
        ...
```

### Responsibilities

- inspect conflict evidence
- inspect available actions
- produce a recommendation
- preserve rationale

### Forbidden responsibilities

- conflict repair
- automatic merge
- rollback execution
- history rewriting
- policy learning

---

## 6. Runtime Boundary

The resolution decision produces a future event intent that re-enters the runtime path:

```text
ResolutionDecision
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
SemanticOperator
      |
      v
SemanticCommit
```

Resolution does not mutate the version graph directly.
It creates a new semantic intent that can be executed by the runtime.

---

## 7. Non-Goals

The resolution decision model is not:

- a conflict resolver
- an automatic merge engine
- a rollback engine
- a hidden history patcher
- a policy learning system

It is a governance layer that turns conflict evidence into a bounded future intent.

