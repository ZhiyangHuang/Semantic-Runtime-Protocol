# SRP Version Conflict Query Model

This document freezes how SRP asks for conflict evidence.
It is an evidence-lookup model, not a resolution model.

Conflict query sits between version-history conflicts and archive evidence lookup:

```text
VersionConflict
      |
      v
Conflict Query Model
      |
      v
Archive Evidence Lookup
```

Conflict query returns references, evidence, and verification signals.
It does not resolve branch disagreement and it does not mutate history.

---

## 1. Query Object

All conflict evidence access should flow through a normalized query object:

```python
@dataclass
class ConflictQuery:
    query_id: str = ""
    conflict_type: str | None = None
    version_id: str | None = None
    transition_id: str | None = None
    evidence_ref: str | None = None
```

### Query fields

- `conflict_type`
  - filter by conflict category
- `version_id`
  - locate conflict evidence involving a specific version
- `transition_id`
  - locate conflict evidence involving a specific transition
- `evidence_ref`
  - locate conflict evidence by a known evidence reference

---

## 2. Query Result

Conflict queries return evidence and verification signals, not a resolved branch:

```python
@dataclass
class ConflictQueryResult:
    query_id: str
    conflict_refs: list[str] = field(default_factory=list)
    version_refs: list[str] = field(default_factory=list)
    transition_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    verification_status: str = "unknown"
    complete: bool = False
```

### Result semantics

- `conflict_refs`
  - the conflict evidence identities that matched the query
- `version_refs`
  - semantic version references implicated by the conflict
- `transition_refs`
  - transition references implicated by the conflict
- `trace_refs`
  - trace references that help explain the conflict
- `evidence_refs`
  - evidence references discovered from version history or archive lookup
- `verification_status`
  - `verified`, `partial`, `missing`, or `unknown`
- `complete`
  - true when the query found enough evidence for the requested lookup boundary

---

## 3. Query Boundary

Conflict query does not:

- resolve the conflict
- merge branches
- roll back history
- mutate the version graph
- create new commits

### Correct boundary

```text
VersionConflict
      |
      v
ConflictQuery
      |
      v
ArchiveQueryService
      |
      v
EvidenceSet
```

### Incorrect boundary

```text
VersionConflict
      |
      v
Automatic Resolution
```

---

## 4. Query Verification

Conflict queries should validate:

- reference integrity
- evidence completeness
- version consistency
- archive boundary integrity

### Reference integrity

Returned references must exist in the query source or archive lookup result.

### Evidence completeness

Queries should report `complete=False` if they cannot gather enough evidence to explain the conflict.

### Version consistency

Version-scoped conflict queries must respect the requested version boundary.

### Archive boundary integrity

Conflict query should call the archive evidence service instead of reading archive storage directly.

---

## 5. Relation to Existing Layers

- `VersionConflictModel`
  - defines what conflict evidence means
- `ConflictDetector`
  - produces conflict evidence from version history
- `ConflictQuery`
  - asks for conflict evidence
- `ArchiveQueryService`
  - locates supporting evidence

This separation keeps conflict evidence queryable without turning it into a resolution engine.

