# LongMemEval Bridge Worker Task Assignment

Date: 2026-07-21

## Objective

Bridge LongMemEval into the shared benchmark evidence framework without changing the official scorer, the runtime contract semantics, or the no-payload-in-repo policy.

This is planning only.

Do not modify benchmark code, `paper/`, or evidence manifests from this plan.

---

## Bridge Design Principle

LongMemEval is a bridge migration, not a rewrite.

Implications:
- the official LongMemEval scorer remains the single source of truth
- the existing external-validation pipeline remains the evaluation core
- the shared benchmark framework provides config, artifact contract, metadata, and report surface
- the bridge must not blur scorer authority or convert LongMemEval into a generic MCQ-style benchmark

---

## Worker 0 - Bridge Architecture Owner

### Responsibility

Define the bridge architecture, directory ownership, and interface boundaries before implementation begins.

### Files Owned

Proposed new files:
- `experiments/benchmarks/longmemeval/__init__.py`
- `experiments/benchmarks/longmemeval/config.py`
- `experiments/benchmarks/longmemeval/adapter.py` interface shell
- `experiments/benchmarks/longmemeval/runner.py` interface shell
- `experiments/benchmarks/longmemeval/metrics.py` interface shell
- `experiments/benchmarks/longmemeval/report.py` interface shell
- `experiments/benchmarks/longmemeval/tests/`

Potential shared-layer edits only if strictly necessary:
- `experiments/benchmarks/common/` for artifact contract compatibility helpers

### Tasks

- define the bridge package layout
- define the LongMemEval bridge configuration surface
- map the current external-validation assets to the shared benchmark contract
- define the migration boundary between `experiments/external_validation/` and the new bridge package
- define how the official scorer remains external-validation-owned

### Acceptance Criteria

- a reviewer can tell which files are new bridge wrappers versus existing evaluation core
- the bridge plan does not require changing the official scorer
- the bridge preserves the no-payload-in-repo policy

---

## Worker 1 - LongMemEval Adapter Owner

### Dependency

Worker 0 bridge architecture approved.

### Responsibility

Implement the LongMemEval adapter layer that normalizes existing LongMemEval cases into the shared benchmark schema without changing the evaluation core.

### Files Owned

Proposed new files:
- `experiments/benchmarks/longmemeval/adapter.py`
- `experiments/benchmarks/longmemeval/tests/test_adapter.py`

Allowed to read:
- `experiments/external_validation/benchmarks.py`
- `experiments/external_validation/schema.py`
- `experiments/external_validation/runtime_contract.py`
- `data/external/longmemeval/manifest.json`
- `data/external/longmemeval/adapter_config.json`
- `data/external/longmemeval/provenance.md`

### Tasks

- expose LongMemEval cases to the bridge layer
- normalize external-validation cases into the shared benchmark case shape where possible
- preserve official-score metadata and SRP diagnostic metadata
- keep the official scorer interface untouched

### Forbidden

- changing the official scorer
- redefining the benchmark semantics
- moving payloads into the repository

### Acceptance Criteria

- the adapter can produce shared-structure cases from the existing LongMemEval source metadata and/or current reality-check fixtures
- the official scorer remains outside the adapter
- adapter tests pass without modifying external-validation logic

---

## Worker 2 - Bridge Runner Owner

### Dependency

Workers 0 and 1 approved.

### Responsibility

Build the bridge runner that delegates execution to the existing LongMemEval reality-check / evidence pipeline while emitting the shared artifact contract.

### Files Owned

Proposed new files:
- `experiments/benchmarks/longmemeval/runner.py`
- `experiments/benchmarks/longmemeval/tests/test_runner.py`

### Tasks

- invoke the existing LongMemEval external-validation pipeline
- keep the official scorer path intact
- emit versioned bridge artifacts in a LongMemEval-specific output directory
- preserve the runtime manifest and provenance notes

### Forbidden

- re-implementing LongMemEval evaluation logic inside the bridge runner
- changing baseline semantics
- using the generic MCQ runner if it distorts scorer authority

### Acceptance Criteria

- the bridge runner can produce a release-branch artifact bundle
- the official scorer still lives in the external-validation path
- the bridge runner is a wrapper, not a second evaluation engine

---

## Worker 3 - Metrics and Report Owner

### Dependency

Worker 2 approved.

### Responsibility

Map official LongMemEval score and SRP diagnostics into the shared metrics and report format without collapsing their meaning.

### Files Owned

Proposed new files:
- `experiments/benchmarks/longmemeval/metrics.py`
- `experiments/benchmarks/longmemeval/report.py`

### Tasks

- map official LongMemEval score into the shared metrics schema
- keep SRP diagnostics separate from the official score
- render a shared-style `report.md` that preserves the scorer-vs-diagnostics boundary
- preserve reproducibility and artifact hash reporting

### Forbidden

- flattening diagnostics into the official score
- changing metric semantics in the external-validation core
- inventing a new LongMemEval benchmark definition

### Acceptance Criteria

- report and metrics expose both official score and SRP diagnostics
- the artifact remains suitable for release-branch audit
- the official scorer is still the single source of truth

---

## Worker 4 - Compatibility and Regression Owner

### Dependency

Workers 1-3 approved.

### Responsibility

Prove that the bridge migration is compatible with the existing external-validation artifacts and that the shared artifact contract is satisfied.

### Files Owned

Proposed new files:
- `experiments/benchmarks/longmemeval/tests/test_bridge_compatibility.py`
- `experiments/benchmarks/longmemeval/tests/test_artifact_contract.py`

### Tasks

- verify the official scorer remains unchanged
- verify the runtime contract remains unchanged
- verify the repo still does not store the benchmark payload
- verify the bridge artifacts satisfy the shared contract
- verify existing reality-check tests still pass

### Acceptance Criteria

- all compatibility gates pass
- no regression is introduced in external-validation behavior
- the bridge artifact is auditable without replacing the official scorer

---

## Integration Owner

### Responsibility

Approve the bridge migration as a whole and block any change that would alter scorer authority, runtime-contract semantics, or provenance.

### Must Review

- bridge architecture
- adapter implementation
- runner implementation
- metrics/report mapping
- compatibility tests

### Hard Stop Conditions

- duplicate scorer
- modified runtime contract semantics
- new payload assumptions in the repository
- benchmark semantics drift

---

## Compatibility Gates

PASS:
- official scorer unchanged
- runtime contract unchanged
- no dataset relocation
- no payload added into repository
- evidence hash unchanged
- existing reality-check tests still pass
- shared artifact contract satisfied

FAIL:
- duplicate scorer
- modified runtime contract
- benchmark semantics changed
- evidence provenance weakened

---

## Migration Boundary

Allowed to add:
- `experiments/benchmarks/longmemeval/`
- bridge-specific tests under that package

Allowed to modify only if necessary:
- `experiments/benchmarks/common/` for shared artifact-compatibility helpers

Must not modify:
- `experiments/external_validation/evidence.py`
- `experiments/external_validation/reality_check.py`
- `experiments/external_validation/runtime_contract.py`
- `experiments/external_validation/metrics.py`
- the official scorer logic used by LongMemEval
- `data/external/longmemeval/` provenance in a way that changes the no-payload policy
- `paper/`
- evidence manifests

If a change seems to require editing the external-validation core, stop and re-evaluate the bridge boundary first.

---

## Dependency Graph

```text
Worker 0
   |
   +--> Worker 1
   |
   +--> Worker 2
   |
   +--> Worker 3
   |
   +--> Worker 4
   |
Integration Owner
```

Execution order:
1. Worker 0
2. Worker 1
3. Worker 2
4. Worker 3
5. Worker 4
6. Integration review

---

## Recommended Next Step

Begin with Worker 0 only.

The first deliverable should be a bridge architecture note that pins down:
- package layout
- allowed file ownership
- what remains entirely external-validation-owned
- how the shared benchmark artifact contract is satisfied without changing the official scorer

