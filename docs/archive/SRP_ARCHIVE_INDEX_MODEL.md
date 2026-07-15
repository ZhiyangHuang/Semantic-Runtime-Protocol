# SRP Archive Index Model

This document freezes how SRP archive evidence is addressed and validated.
It is a storage maintenance model, not a semantic mutation model.

Archive indexing sits between archive representation and archive queries:

```text
Archive Representation Model
      |
      v
Archive Index Model
      |
      v
Archive Query / Recovery
```

The archive index makes retained evidence addressable without scanning the full archive.

---

## 1. Archive Index Structure

The archive should expose a small set of reference indices:

```text
ArchiveStore
  -> UnitIndex
  -> LineageIndex
  -> VersionIndex
  -> TraceIndex
  -> EvidenceIndex
```

Each index maps a semantic concern to archive references, not to an active semantic state.

---

## 2. UnitIndex

`UnitIndex` locates archive evidence for a semantic unit.

### Suggested entry shape

```python
@dataclass
class UnitIndexEntry:
    unit_id: str
    archive_segments: list[str] = field(default_factory=list)
    lifecycle_state: str = "archived"
    latest_archive_version: str | None = None
```

### Responsibilities

- recover a unit by reference
- inspect historical archive placement
- validate GC targets against archived evidence

### Forbidden responsibilities

- reconstruct semantic state by itself
- change lifecycle meaning
- mutate archive contents

---

## 3. LineageIndex

`LineageIndex` addresses evolution paths.

### Suggested entry shape

```python
@dataclass
class LineageIndexEntry:
    lineage_id: str
    ancestor_refs: list[str] = field(default_factory=list)
    descendant_refs: list[str] = field(default_factory=list)
    split_history: list[str] = field(default_factory=list)
    merge_history: list[str] = field(default_factory=list)
```

### Responsibilities

- split recovery support
- merge rollback support
- provenance tracing

### Forbidden responsibilities

- direct state reconstruction
- automatic reparenting
- hiding causal breaks

---

## 4. VersionIndex

`VersionIndex` connects archive evidence to semantic version history.

### Suggested entry shape

```python
@dataclass
class VersionIndexEntry:
    version_id: str
    archive_refs: list[str] = field(default_factory=list)
    parent_version: str | None = None
    branch_id: str | None = None
    commit_ref: str | None = None
```

### Responsibilities

- checkout support
- rollback support
- replay verification support

### Forbidden responsibilities

- rewriting version causality
- inventing versions
- reordering commits

---

## 5. TraceIndex

`TraceIndex` links transitions to archive evidence.

### Suggested entry shape

```python
@dataclass
class TraceIndexEntry:
    trace_id: str
    event_id: str
    affected_units: list[str] = field(default_factory=list)
    archive_refs: list[str] = field(default_factory=list)
```

### Responsibilities

- answer why a unit changed state
- support audit and explanation lookup
- connect traces to archive evidence

### Forbidden responsibilities

- state mutation
- event generation

---

## 6. EvidenceIndex

`EvidenceIndex` supports evidence-based recovery.

### Suggested entry shape

```python
@dataclass
class EvidenceIndexEntry:
    evidence_id: str
    source_refs: list[str] = field(default_factory=list)
    reliability: float = 0.0
    supported_operations: list[str] = field(default_factory=list)
```

### Responsibilities

- locate recovery evidence
- support verification and audit
- expose evidence provenance

### Forbidden responsibilities

- replacing operator logic
- bypassing the kernel
- mutating semantic state directly

---

## 7. Index Lifecycle

Index updates belong to the runtime maintenance layer.

```text
Semantic Mutation
      |
      v
Runtime Event
      |
      v
Kernel Transition
      |
      v
State Change
      |
      v
Index Update
```

Index updates are not semantic mutations themselves.

---

## 8. Index Constraints

The archive index must satisfy:

- referential integrity
- version consistency
- trace consistency
- evidence consistency

### Referential integrity

No index entry may point to a missing archive record.

### Version consistency

Every indexed version must correspond to a valid version reference.

### Trace consistency

Every indexed trace must correspond to a valid transition or trace record.

### Evidence consistency

Evidence references must remain reachable through the archive index.

---

## 9. Relation to Archive Query, Recovery, and Replay

- `Archive Query` extracts evidence through archive indices
- `Recovery` consumes archive query results to gather evidence
- `Replay` reconstructs semantic state from event history, not from archive scan
- Archive indices make evidence lookup efficient, but they do not replace replay
