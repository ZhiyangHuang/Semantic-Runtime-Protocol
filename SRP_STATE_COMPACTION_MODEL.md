# SRP State Compaction Model

This document freezes the storage-side maintenance model for retained semantic evidence.
It is not a semantic evolution operator spec.

State compaction sits beside lifecycle management, not inside the mutation operator family:

```text
Semantic Evolution
      |
      v
Semantic Lifecycle Model
      |
      v
Garbage Collection
      |
      v
State Compaction
      |
      v
Archive Representation
```

Compaction reorganizes retained semantic storage without changing the meaning of preserved evidence.

---

## 1. Compaction Purpose

State compaction exists to:

- reduce archive fragmentation
- merge archive blocks
- compress provenance and trace references
- build storage indexes for retained evidence
- improve maintenance efficiency

It does not:

- change unit identity
- rewrite lineage
- reorder causal history
- alter replay-required evidence semantics
- recreate semantic state

---

## 2. Compaction Scope

Compaction acts on retained maintenance artifacts such as:

- forgotten unit records
- archived unit records
- merged history records
- recovery evidence records
- trace references
- provenance references

Compaction does not act on live semantic state as a mutation operator.

---

## 3. Archive Representation

The archive is the storage surface for retained evidence after GC or lifecycle demotion.

Typical archive contents:

```text
Archive Layer
  - archived semantic units
  - forgotten semantic units
  - lineage references
  - provenance references
  - trace references
  - replay-required metadata
```

Archive representation may be reorganized by compaction, but the meaning of preserved evidence must remain stable.

---

## 4. Compaction Result

Compaction should produce a storage-oriented result, not a semantic transition result:

```python
@dataclass
class CompactionResult:
    before_archive_ref: str
    after_archive_ref: str
    preserved_unit_refs: list[str]
    preserved_trace_refs: list[str]
    preserved_provenance_refs: list[str]
    compression_ratio: float
    maintenance_trace_ref: str | None = None
```

CompactionResult is about archive organization, not semantic mutation.

---

## 5. Storage Constraints

Compaction must preserve:

- unit identity references
- lineage references
- causal ordering
- replay-required evidence
- trace linkage
- provenance linkage

Compaction must not:

- change `unit_id`
- create new semantic history
- remove evidence required by replay
- alter event causality
- alter semantic version relations

---

## 6. Maintenance Trace

Compaction may emit a maintenance trace rather than a semantic transition trace.

Example shape:

```text
ArchiveBlock A
  before: 100 retained records
  after: 1 compacted archive segment
  preserved:
    - 100 lineage refs
    - 100 provenance refs
    - 52 trace refs
```

This trace explains storage maintenance, not semantic evolution.

---

## 7. Replay Boundary

Replay must not depend on compaction.

Replay remains:

```text
EventStream -> ReplayEngine -> SemanticState
```

Compaction remains:

```text
ArchiveStorage -> Compaction -> ArchiveRepresentation
```

Replay may read archive evidence, but it must not depend on a specific archive layout to reconstruct valid semantic state.

---

## 8. Relation to Lifecycle and GC

- `ForgettingOperator` removes content from the active representation while preserving evidence
- `GarbageCollectionOperator` removes unrecoverable or collectable content from active semantic storage
- `State Compaction` reorganizes what remains after GC without changing the meaning of preserved evidence

These are separate layers.

