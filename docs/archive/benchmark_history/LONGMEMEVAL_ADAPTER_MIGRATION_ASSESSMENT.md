# LongMemEval Adapter Migration Assessment

Date: 2026-07-21

## Goal

Assess how to migrate LongMemEval into the shared benchmark evidence framework without changing the official LongMemEval scorer or weakening the release-branch provenance of the existing reality-check evidence.

This is a planning document only.

Do not modify benchmark code, `paper/`, or evidence manifests from this assessment.

---

## 1. Current State

LongMemEval currently lives as a dedicated external-validation path under:

- `experiments/external_validation/`
- `data/external/longmemeval/`
- `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/`

Current properties:

- the official LongMemEval scorer remains the source of truth
- SRP diagnostics are co-reported, not substituted for scoring
- the runtime contract is frozen and recorded separately
- the repository does not store the benchmark payload

This means LongMemEval is already release-grade evidence, but it is not yet packaged through the same shared benchmark artifact surface as MMLU and ARC.

---

## 2. Migration Principle

Recommended principle:

> Wrap the existing LongMemEval reality-check pipeline in a shared artifact contract, but do not force the official scorer path through the generic MCQ-style shared runner if that would blur scorer authority or distort the existing runtime contract.

Implication:

- `shared benchmark framework` should own configuration, artifact writing, metadata, report generation, and versioned output layout
- `external_validation` should remain the evaluation core for LongMemEval
- the official scorer remains the only benchmark scorer

This is a bridge migration, not a rewrite.

---

## 3. Reuse Map

| Existing component | Reuse decision | Reason |
| --- | --- | --- |
| `experiments/external_validation/evidence.py` | Reuse | Contains the official LongMemEval evidence execution path and scorer preservation logic. |
| `experiments/external_validation/reality_check.py` | Reuse | Contains the reality-check report packaging and audit-friendly summary logic. |
| `experiments/external_validation/runtime_contract.py` | Reuse | Contains the frozen runtime manifest contract for the LongMemEval release evidence. |
| `experiments/external_validation/metrics.py` | Reuse with mapping | Contains benchmark-level and SRP diagnostic metrics that can be mapped to the shared metrics schema. |
| `experiments/external_validation/benchmarks.py` | Reuse | Contains the LongMemEval adapter and case-loading logic. |
| `experiments/external_validation/tests/test_reality_check.py` | Reuse as pattern | Good acceptance-test shape for report generation and config loading. |
| `data/external/longmemeval/*` | Reuse | Source-of-truth metadata and provenance for the external dataset registration. |

What should not be changed:

- the official scorer implementation
- the external-validation runtime contract semantics
- the provenance notes that indicate the payload is not stored in the repository

---

## 4. Proposed Target Layout

Proposed new wrapper area:

```text
experiments/benchmarks/longmemeval/
    __init__.py
    adapter.py
    config.py
    runner.py
    metrics.py
    report.py
    tests/
```

Important: this layout should be a wrapper around the existing external-validation core, not a second scorer implementation.

---

## 5. Recommended Interface Split

### adapter.py

Responsibilities:
- expose LongMemEval cases to the shared evidence layer
- normalize the external-validation case schema into the shared benchmark schema where possible
- preserve official-score metadata and SRP diagnostic metadata

Must not:
- rewrite the official LongMemEval scorer
- invent a new benchmark definition

### config.py

Responsibilities:
- define the frozen LongMemEval execution configuration
- carry data root, sample limit, runtime endpoint, and seed policy
- preserve the external-validation source config path

### runner.py

Recommended behavior:
- act as a bridge runner that calls the existing LongMemEval reality-check/evidence pipeline
- emit shared-structure artifacts from the bridge layer

Why a bridge runner:
- LongMemEval has an official scorer and a specific runtime manifest contract
- forcing it into the generic MCQ runner would lose important release-branch semantics

### metrics.py

Responsibilities:
- map official LongMemEval score and SRP diagnostics into the shared metrics vocabulary
- keep official benchmark score separate from SRP diagnostics

### report.py

Responsibilities:
- render a shared-style report.md for the release branch
- preserve the official-score vs SRP-diagnostics distinction

---

## 6. Compatibility Assessment

### Compatible with the shared framework

Yes, for:
- config serialization
- artifact writing
- metadata and hash tracking
- report generation
- release-branch versioning
- cross-benchmark auditability

### Not a good fit for the generic MCQ runner

LongMemEval is not a simple multiple-choice benchmark. It has:
- external runtime contract
- official scorer separation
- SRP diagnostics that measure a different layer of the stack
- multi-seed reality-check structure

Therefore:
- the shared `BenchmarkRunner` pattern is useful as a contract reference
- a LongMemEval-specific bridge runner is the safer migration path

---

## 7. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Replacing the official scorer with a shared wrapper | High | Keep scorer authority in `experiments/external_validation/` and only wrap outputs. |
| Flattening SRP diagnostics into the official score | High | Preserve separate fields for official score and SRP diagnostics. |
| Accidentally converting LongMemEval into a generic benchmark | Medium | Treat it as a bridge migration, not a schema rewrite. |
| Breaking provenance by moving payload assumptions | Medium | Keep the no-payload-in-repo policy unchanged. |
| Creating a second authoritative runtime contract | High | Keep the existing external-validation runtime contract as the source of truth. |

---

## 8. Recommended Implementation Order

1. Create a LongMemEval wrapper config that mirrors the existing external-validation config.
2. Add a LongMemEval adapter that normalizes cases and preserves official scorer metadata.
3. Add a bridge runner that invokes the existing LongMemEval reality-check/evidence pipeline.
4. Map official score and SRP diagnostics into the shared artifact/metrics contract.
5. Add tests that prove:
   - the official scorer is unchanged
   - the release artifact is versioned
   - the shared artifact contract is satisfied

---

## 9. Recommendation

Decision:

`APPROVE_BRIDGE_MIGRATION`

Rationale:

- LongMemEval is already release-grade evidence
- the existing external-validation pipeline should remain the source of truth
- a bridge migration gives LongMemEval the same release artifact surface as MMLU and ARC without changing scorer authority

Next allowed action:

- implement the LongMemEval bridge package under `experiments/benchmarks/longmemeval/` as a thin wrapper over the existing external-validation core

