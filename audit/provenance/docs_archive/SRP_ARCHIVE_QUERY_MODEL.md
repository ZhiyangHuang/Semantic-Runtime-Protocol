# SRP Archive Query Model

This document freezes how SRP asks the archive for evidence and references.
It is an evidence-discovery model, not a state reconstruction model.

Archive query sits between archive index and recovery / analysis:

```text
Archive Representation Model
      |
      v
Archive Index Model
      |
      v
Archive Query Model
      |
      +----------------+
      |                |
      v                v
Recovery          Audit / Analysis
```

Archive queries return references, evidence, and verification signals.
They do not directly reconstruct semantic state.

---

## 1. Query Object

All archive access should flow through a normalized query object:

```python
@dataclass
class ArchiveQuery:
    query_id: str
    query_type: str
    target: str
    constraints: dict[str, Any] = field(default_factory=dict)
    version_scope: str | None = None
    lifecycle_filter: list[str] = field(default_factory=list)
```

### Query fields

- `query_type`
  - what kind of evidence is being requested
- `target`
  - the primary lookup key
- `constraints`
  - additional filters or requirements
- `version_scope`
  - optional version boundary
- `lifecycle_filter`
  - optional lifecycle restriction

---

## 2. Query Types

The first archive query model freezes these query families:

### 2.1 Unit lookup

Answers:

> Where is a semantic unit archived?

Typical target:

```text
unit_id:u123
```

Primary source:

- `UnitIndex`

Returns:

- archive entry refs
- archive segment refs
- latest archive version

---

### 2.2 Lineage lookup

Answers:

> Where did this unit come from?

Typical target:

```text
lineage_id:l456
```

Primary source:

- `LineageIndex`

Returns:

- ancestor refs
- descendant refs
- split / merge history refs

---

### 2.3 Version lookup

Answers:

> What archive evidence belongs to a semantic version?

Typical target:

```text
version_id:v789
```

Primary source:

- `VersionIndex`

Returns:

- archive refs
- parent version ref
- branch ref
- commit ref

---

### 2.4 Trace lookup

Answers:

> Why did this semantic state change?

Typical target:

```text
trace_id:t101
```

Primary source:

- `TraceIndex`

Returns:

- event ref
- affected unit refs
- archive refs

---

### 2.5 Evidence lookup

Answers:

> What evidence can support recovery or verification?

Typical target:

```text
unit_id:u123
```

Primary source:

- `EvidenceIndex`

Returns:

- evidence refs
- reliability
- supported operations

---

## 3. Query Result

Archive queries should return references and verification status, not a reconstructed state:

```python
@dataclass
class ArchiveQueryResult:
    query_id: str
    matched_refs: list[str] = field(default_factory=list)
    confidence: float = 0.0
    completeness: float = 0.0
    verification_status: str = "unknown"
    incomplete: bool = False
```

### Result semantics

- `matched_refs`
  - archive refs, trace refs, version refs, or evidence refs
- `confidence`
  - how confident the match is
- `completeness`
  - how much of the requested evidence was found
- `verification_status`
  - `verified`, `partial`, `missing`, or `unknown`
- `incomplete`
  - true when the query cannot supply enough evidence for a downstream operation

---

## 4. Query Boundaries

Archive query does not:

- mutate archive contents
- reconstruct semantic state directly
- bypass the kernel
- infer new semantic meaning

### Recovery boundary

Recovery uses archive query as an evidence discovery step:

```text
RecoveryOperator
      |
      v
ArchiveQuery
      |
      v
EvidenceSet
      |
      v
Reconstruction
```

### Replay boundary

Replay remains separate:

```text
EventStream
      |
      v
ReplayEngine
      |
      v
SemanticState
```

Replay does not depend on archive query to reconstruct valid state.

---

## 5. Query Verification

Archive queries should validate:

- reference integrity
- evidence completeness
- version consistency
- lifecycle compatibility

### Reference integrity

Matched references must exist in the archive model.

### Evidence completeness

Recovery-oriented queries should report `incomplete=True` if they cannot provide identity, lineage, and transition evidence together.

### Version consistency

Version-scoped queries must respect the requested version boundary.

### Lifecycle compatibility

Queries may filter by lifecycle state when recovering or auditing terminal content.

---

## 6. Relation to Archive Index

Archive query is a consumer of archive indices.

- `UnitIndex` supports unit lookup
- `LineageIndex` supports lineage lookup
- `VersionIndex` supports version lookup
- `TraceIndex` supports trace lookup
- `EvidenceIndex` supports evidence lookup

Archive index defines addressability.
Archive query defines the evidence-discovery language.

