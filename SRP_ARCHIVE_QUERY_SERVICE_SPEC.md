# SRP Archive Query Service Spec

This document freezes the service contract that exposes archive evidence discovery to runtime components.
It is not an implementation spec and it is not a reconstruction engine spec.

The archive query service sits between archive indices and downstream recovery / audit consumers:

```text
Archive Representation Model
      |
      v
Archive Index Model
      |
      v
Archive Query Model
      |
      v
Archive Query Service
      |
      +----------------+
      |                |
      v                v
Recovery          Audit / Analysis
```

The service returns references, verification signals, and completeness markers.
It does not return reconstructed semantic state.

---

## 1. Service Boundary

`ArchiveQueryService` is the canonical entrypoint for archive evidence lookup.

### Responsibilities

- accept `ArchiveQuery`
- dispatch to archive indices
- verify returned references
- return `ArchiveQueryResult`
- surface evidence completeness and integrity failures

### Forbidden responsibilities

- state mutation
- recovery execution
- replay execution
- compaction execution
- semantic inference

### Service boundary

```text
RecoveryOperator
      |
      v
ArchiveQueryService
      |
      v
ArchiveIndex
      |
      v
ArchiveStore
```

---

## 2. Core API

The first service contract should expose a small, explicit surface:

### 2.1 `lookup_unit`

Looks up archive evidence for a unit.

```python
lookup_unit(
    unit_id: str,
    constraints: dict[str, Any] | None = None,
) -> ArchiveQueryResult
```

### 2.2 `lookup_lineage`

Looks up evolution history for a lineage.

```python
lookup_lineage(
    lineage_id: str,
    constraints: dict[str, Any] | None = None,
) -> ArchiveQueryResult
```

### 2.3 `lookup_version`

Looks up archive evidence by semantic version.

```python
lookup_version(
    version_id: str,
    constraints: dict[str, Any] | None = None,
) -> ArchiveQueryResult
```

### 2.4 `lookup_trace`

Looks up causal explanation artifacts.

```python
lookup_trace(
    trace_id: str,
    constraints: dict[str, Any] | None = None,
) -> ArchiveQueryResult
```

### 2.5 `lookup_evidence`

Looks up recovery or verification evidence.

```python
lookup_evidence(
    target: str,
    operation: str = "recovery",
    constraints: dict[str, Any] | None = None,
) -> ArchiveQueryResult
```

### 2.6 `verify_reference`

Verifies that a reference is valid and reachable.

```python
verify_reference(
    reference: str,
) -> ArchiveQueryResult
```

---

## 3. Service Result

The service returns a normalized evidence discovery result:

```python
@dataclass
class ArchiveServiceResult:
    query_id: str
    refs: list[str] = field(default_factory=list)
    verification: str = "unknown"
    completeness: float = 0.0
    warnings: list[str] = field(default_factory=list)
```

### Result semantics

- `refs`
  - matched archive, trace, version, lineage, or evidence refs
- `verification`
  - `verified`, `partial`, `missing`, or `unknown`
- `completeness`
  - how much of the requested evidence was located
- `warnings`
  - non-fatal issues such as partial evidence or stale references

The service must not return `SemanticUnit` or `SemanticState` objects.

---

## 4. Error Model

The service should surface a small and explicit error vocabulary:

- `ReferenceMissing`
  - the requested reference does not exist
- `EvidenceIncomplete`
  - the archive contains some evidence, but not enough for the requested operation
- `IntegrityFailure`
  - index and archive content disagree
- `VersionConflict`
  - the requested evidence belongs to a different semantic branch or version scope

Errors should be represented in the service result or as structured failures, not as silent fallback behavior.

---

## 5. Query Semantics

### Unit lookup

- uses `UnitIndex`
- returns archive refs for a unit
- may include lifecycle and latest version context

### Lineage lookup

- uses `LineageIndex`
- returns ancestors, descendants, split history, merge history

### Version lookup

- uses `VersionIndex`
- returns archive refs, parent version, branch, commit refs

### Trace lookup

- uses `TraceIndex`
- returns event refs, transition refs, affected object refs

### Evidence lookup

- uses `EvidenceIndex`
- returns evidence refs and supported operations

### Reference verification

- checks existence
- checks completeness
- checks consistency with archive index

---

## 6. Recovery and Replay Boundaries

### Recovery

Recovery should use the service as an evidence discovery layer:

```text
RecoveryOperator
      |
      v
ArchiveQueryService
      |
      v
EvidenceSet
      |
      v
RecoveryOperator
      |
      v
RuntimeKernel
```

### Replay

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

Replay does not depend on archive indices or archive query services to reconstruct valid semantic state.

---

## 7. Compaction Interaction

Compaction may refresh archive locations and index mappings.

The query service must tolerate archive layout changes as long as references remain valid.

Compaction may update:

- segment location
- index mapping
- storage layout metadata

Compaction may not update:

- `unit_id`
- `lineage_id`
- `trace_id`
- evidence identity
- causal meaning

---

## 8. Relation to the Archive Query Model

The model defines the query language.
The service spec defines the runtime-facing API that executes that language.

This separation keeps the archive implementation replaceable while preserving the evidence-discovery contract.

