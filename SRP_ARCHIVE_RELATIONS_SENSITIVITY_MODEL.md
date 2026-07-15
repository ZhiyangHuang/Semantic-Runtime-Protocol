# SRP Archive Relations Sensitivity Model

This document freezes the sensitivity boundary for `archive_relations`.
It is a research contract, not an implementation spec.

The question is:

> How does archive relation exposure change evidence completeness without changing runtime semantic state?

---

## 1. Parameter

`archive_relations`

### Type

- boolean in the first OFAT phase
- later extensions may consider bounded relation sets, but not yet

### First phase values

- `False`
- `True`

### Interpretation

- `False` means archive relation evidence is not surfaced during the experiment
- `True` means archive relation evidence is surfaced through the archive boundary

This parameter is not treated as a semantic mutation knob.
It is an evidence boundary knob.

---

## 2. Boundary

`archive_relations` must preserve the following split:

```text
Runtime State
    |
    v
Archive Evidence Boundary
    |
    v
External Evidence Enrichment
```

It must not turn archive evidence into a second source of state reconstruction authority.

### Explicit non-goals

- no archive-driven semantic mutation
- no archive-driven state rewrite
- no direct archive state reconstruction
- no relation-count sweep in the first phase

---

## 3. Evaluation Metrics

The first `archive_relations` sensitivity experiment should use metrics that measure evidence quality and boundary isolation.

### 3.1 Evidence enrichment completeness

Question:

> Does archive lookup enrich conflict or query evidence sufficiently?

Suggested metric:

- `evidence_enrichment_count`

Meaning:

- count of additional archive or relation evidence surfaced by the archive boundary

### 3.2 Conflict query coverage

Question:

> Does archive lookup improve evidence coverage for conflict queries?

Suggested metric:

- `conflict_evidence_coverage`

Meaning:

- ratio of conflict evidence requirements satisfied by archive-enriched results

### 3.3 Runtime isolation

Question:

> Does archive relation exposure leave the semantic runtime transition unchanged?

Suggested metric:

- `state_transition_equivalence`

Meaning:

- runtime state transition outcome should remain equivalent across archive settings

### 3.4 Replay independence

Question:

> Does archive relation exposure preserve replay independence?

Suggested metric:

- `replay_equivalent`

Meaning:

- replay must remain independent from archive layout and archive relation exposure

---

## 4. Experiment Classification

The catalog entry for `archive_relations` should reflect its archive boundary role.

Suggested classification:

- `parameter`: `archive_relations`
- `class`: `Tunable`
- `status`: `Draft` or `Experimental`
- `owner`: `Archive Evidence Boundary`
- `metric`: `evidence completeness`, `query coverage`, `replay isolation`

This parameter is distinct from:

- `activation_threshold`
  - semantic mutation boundary
- `recovery_min_evidence`
  - governance recovery boundary
- `preserve_evidence`
  - history retention boundary

---

## 5. First OFAT Shape

The first experiment should compare only:

```text
archive_relations = False
archive_relations = True
```

Do not sweep relation counts yet.

The experiment pipeline should preserve the existing runtime path:

```text
Parameter Registry
    |
    v
RuntimeConfig
    |
    v
ConflictQuery / ArchiveAdapter
    |
    v
EvidenceSet
    |
    v
Metrics
    |
    v
SensitivityResult
```

---

## 6. Suggested Result Fields

The experiment result should at minimum record:

- `experiment_id`
- `parameter`
- `value`
- `metrics`
- `observations`

Useful archive-specific observations:

- number of archive references surfaced
- whether conflict coverage increased
- whether runtime state transition stayed equivalent
- whether replay remained equivalent

---

## 7. Next Step

After this model is frozen, the next artifact should be the `archive_relations` OFAT experiment implementation.

