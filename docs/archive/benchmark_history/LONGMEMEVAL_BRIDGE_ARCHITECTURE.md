# LongMemEval Bridge Architecture

Date: 2026-07-21

## 1. Purpose

This document freezes the bridge architecture for LongMemEval migration into the shared benchmark evidence framework.

The bridge is an artifact integration layer, not an evaluation replacement layer.

It must preserve:
- the official LongMemEval scorer as the source of truth
- the existing external-validation runtime contract
- the no-payload-in-repository policy

It must not:
- rewrite the official scorer
- redefine LongMemEval semantics
- replace the existing external-validation pipeline

---

## 2. Ownership Model

### Shared benchmark surface

The shared benchmark framework owns:
- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`
- shared artifact versioning and hash tracking

### LongMemEval bridge package

`experiments/benchmarks/longmemeval/` owns:
- bridge configuration
- bridge adapter
- bridge runner
- bridge metrics mapping
- bridge report rendering
- bridge-specific tests

### External validation core

`experiments/external_validation/` continues to own:
- the official LongMemEval scorer
- runtime contract semantics
- evidence execution semantics
- scorer alignment logic
- current reality-check / evidence behavior

### External source registration

`data/external/longmemeval/` continues to own:
- dataset registration metadata
- provenance notes
- adapter mapping notes
- no-payload policy

---

## 3. Authority Boundary

### Owned by the bridge

Allowed:
- output directory selection
- artifact serialization
- metadata assembly
- report formatting
- shared schema mapping
- versioned release packaging

### Owned by external_validation

Must remain unchanged:
- scorer authority
- runtime contract
- benchmark interpretation semantics
- evidence execution semantics
- official score computation

### Hard rule

The bridge may wrap the evaluation flow and package its outputs, but it may not create a second scorer or a second benchmark definition.

---

## 4. Data Flow

```text
LongMemEval config
        |
        v
LongMemEval bridge runner
        |
        v
Existing external-validation pipeline
        |
        +---- Official LongMemEval scorer
        |
        +---- SRP diagnostics
        |
        v
Bridge artifact writer
        |
        v
experiments/results/longmemeval_full_v1/
```

Important ordering:
- the bridge artifact writer runs after the official scorer and SRP diagnostics are produced
- the bridge does not own the scoring step
- the bridge only packages and maps outputs for the shared evidence surface

---

## 5. Artifact Contract Mapping

The bridge must emit the shared artifact contract:
- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

### LongMemEval mapping

| Artifact | Source |
| --- | --- |
| `config.json` | Bridge config plus frozen runtime config and sample policy |
| `raw_predictions.jsonl` | Existing reality-check / evidence records and traces |
| `metrics.json` | Official score plus SRP diagnostic mapping |
| `metadata.json` | Provenance, hashes, versioning, and runtime identifiers |
| `report.md` | Bridge report renderer preserving scorer-vs-diagnostics separation |

### Required preservation

The bridge artifact must preserve:
- official LongMemEval score
- SRP diagnostics as a separate layer
- runtime manifest provenance
- release-branch version identifiers

---

## 6. Migration Boundary

### Allowed to add

- `experiments/benchmarks/longmemeval/`
- bridge-specific tests under that package

### Allowed to modify only if strictly necessary

- `experiments/benchmarks/common/` for shared artifact compatibility helpers

### Must not modify

- `experiments/external_validation/evidence.py`
- `experiments/external_validation/reality_check.py`
- `experiments/external_validation/runtime_contract.py`
- `experiments/external_validation/metrics.py`
- the official scorer logic used by LongMemEval
- `data/external/longmemeval/` provenance in a way that changes the no-payload policy
- `paper/`
- evidence manifests

If a proposed change seems to require editing the external-validation core, stop and re-evaluate the bridge boundary before proceeding.

---

## 7. Compatibility Requirements

The bridge must satisfy all of the following:

- official scorer unchanged
- runtime contract unchanged
- no dataset relocation
- no payload added into the repository
- evidence hashes remain auditable
- existing reality-check tests still pass
- shared artifact contract is satisfied

If any requirement fails, the bridge migration is blocked.

---

## 8. Implementation Shape

Recommended bridge package layout:

```text
experiments/benchmarks/longmemeval/
    __init__.py
    config.py
    adapter.py
    runner.py
    metrics.py
    report.py
    tests/
```

Implementation intent:
- `config.py` freezes the bridge-facing configuration
- `adapter.py` normalizes cases and preserves scorer metadata
- `runner.py` delegates to the existing external-validation pipeline
- `metrics.py` maps official and diagnostic metrics into the shared schema
- `report.py` renders a shared-style release report
- `tests/` prove scorer authority and artifact compatibility

---

## 9. Acceptance Gate

Worker 0 is complete only when all of the following are true:

- [ ] bridge package ownership is defined
- [ ] scorer ownership is explicitly preserved in external_validation
- [ ] artifact ownership is explicitly defined in the shared surface
- [ ] no-payload policy is preserved
- [ ] no external_validation rewrite is required
- [ ] downstream workers can implement without ambiguity

---

## 10. Decision

Status:
- `BRIDGE_ARCHITECTURE_FROZEN`

Next allowed action:
- Worker 1 may begin adapter implementation after architecture review

