# SRP Archive Representation Model

This document freezes how SRP retains semantic evidence after lifecycle demotion and GC.
It is a storage-side model, not a semantic evolution operator spec.

Archive representation sits below lifecycle management and compaction:

```text
Semantic Lifecycle Model
      |
      v
State Compaction Model
      |
      v
Archive Representation Model
      |
      v
Archive Index Model
```

The archive is a reference-first retention surface. It stores links to semantic evidence rather than duplicating active semantic state.

---

## 1. Archive Object Model

Archive storage is organized as:

```text
ArchiveStore
  -> ArchiveSegment
      -> ArchiveEntry
          -> SemanticObjectReference
          -> EvidenceReference
          -> TraceReference
          -> VersionReference
          -> LineageReference
```

Archive entries should prefer references over full copies of active runtime objects.

### Suggested archive entry shape

```python
@dataclass
class ArchiveEntry:
    entry_id: str
    unit_ref: str
    lifecycle_state: str
    lineage_ref: str | None = None
    provenance_ref: str | None = None
    trace_refs: list[str] = field(default_factory=list)
    version_refs: list[str] = field(default_factory=list)
    recovery_metadata: dict[str, Any] = field(default_factory=dict)
```

Archive entries may store compact payload snippets, but they must not become a second active semantic state.

---

## 2. Active vs Archive Boundary

The semantic runtime contains two distinct storage surfaces:

### Active Representation

Responsible for:

- current computation
- operator execution
- mutation routing
- runtime queries

### Archive Representation

Responsible for:

- recovery evidence
- lineage retention
- trace retention
- replay support
- auditability

The archive must not be treated as a live state container.

---

## 3. Archive Segment

Archive storage is grouped into segments for compaction and indexing.

```python
@dataclass
class ArchiveSegment:
    segment_id: str
    created_version: str
    covered_units: list[str] = field(default_factory=list)
    coverage_range: str | None = None
    compression_level: float = 0.0
    index_ref: str | None = None
    integrity_hash: str | None = None
```

Archive segments are a storage unit only.

They may be compacted, reindexed, or split without changing the semantic meaning of their preserved references.

---

## 4. Archive Index

Archive retrieval must not require scanning the full archive.

The archive should expose reference indices such as:

- `UnitIndex`
  - `unit_id -> archive_location`
- `LineageIndex`
  - `lineage_id -> archive_segments`
- `VersionIndex`
  - `version_id -> archive_refs`
- `TraceIndex`
  - `trace_id -> evidence_refs`

The archive index exists to support recovery and audit queries, not to reconstruct state on its own.

---

## 5. Retained Evidence

Archive representation may retain:

- lineage references
- provenance references
- trace references
- version references
- recovery metadata
- archive-level maintenance traces

Archive representation should not retain unnecessary duplicated active state.

---

## 6. Recovery Boundary

Recovery uses the archive as an evidence source:

```text
Archive
  -> Evidence Extraction
  -> RecoveryOperator
  -> SemanticState
```

Recovery does not restore directly from raw archive layout.

It must still pass through the kernel and operator boundary.

---

## 7. Replay Boundary

Replay remains independent from archive layout:

```text
EventStream
  -> ReplayEngine
  -> SemanticState
```

Replay may consult archive references for debugging or audit, but it must not depend on a specific archive compaction layout.

---

## 8. Relationship to Compaction

- `State Compaction` reorganizes archive structure without changing meaning
- `Archive Representation` defines what the archive stores and how references are arranged
- `Archive Index` defines how archive evidence is addressed

These are maintenance concerns, not semantic mutation concerns.
