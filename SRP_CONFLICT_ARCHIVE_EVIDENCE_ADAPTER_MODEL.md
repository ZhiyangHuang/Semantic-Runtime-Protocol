# SRP Conflict Archive Evidence Adapter Model

This document freezes the boundary that connects version-conflict evidence to archive evidence lookup.
It is a connector model, not a resolution model.

The central question is:

> How does SRP enrich version-conflict evidence with archive evidence without exposing ArchiveStore directly?

The answer is a dedicated adapter that routes conflict evidence through `ArchiveQueryService`.

---

## 1. Adapter Boundary

The adapter sits between conflict evidence and archive lookup:

```text
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

### Correct boundary

```text
ConflictQuery
      |
      v
ConflictArchiveEvidenceAdapter
      |
      v
ArchiveQueryService
```

### Incorrect boundary

```text
ConflictQuery
      |
      v
ArchiveStore
```

---

## 2. ConflictEvidenceBundle

The adapter returns a normalized bundle of references:

```python
@dataclass
class ConflictEvidenceBundle:
    conflict_id: str
    version_refs: list[str] = field(default_factory=list)
    transition_refs: list[str] = field(default_factory=list)
    trace_refs: list[str] = field(default_factory=list)
    archive_refs: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    verification_status: str = "unknown"
    complete: bool = False
    warnings: list[str] = field(default_factory=list)
```

### Semantics

- `version_refs`
  - version identities implicated by the conflict
- `transition_refs`
  - transition identities implicated by the conflict
- `trace_refs`
  - traces that help explain the conflict
- `archive_refs`
  - archive references discovered through archive lookup
- `evidence_refs`
  - raw evidence references that support the conflict
- `verification_status`
  - `verified`, `partial`, `missing`, or `unknown`
- `complete`
  - true when archive enrichment is sufficient for the lookup boundary
- `warnings`
  - non-fatal enrichment issues such as missing archive service

---

## 3. Adapter Responsibilities

The adapter should:

- accept a `VersionConflict`
- lookup supporting evidence through `ArchiveQueryService`
- enrich the conflict evidence with archive references
- preserve the original conflict object
- report completeness and warnings

The adapter must not:

- resolve the conflict
- mutate the version graph
- create commits
- create checkpoints
- read archive storage directly

---

## 4. Adapter Verification

The adapter should validate:

- evidence enrichment
- missing-archive handling
- non-mutation of semantic history

### Evidence enrichment

If archive evidence exists, the adapter should surface archive refs and trace refs.

### Missing archive evidence

If archive lookup is unavailable, the adapter should report partial completeness and a warning.

### Non-mutation

Lookup must not create new semantic history artifacts such as commits, version nodes, or checkpoints.

