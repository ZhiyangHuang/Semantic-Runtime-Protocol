# Benchmark Worker Task Assignment

This document converts the benchmark implementation breakdown into worker-level tasks with strict file ownership boundaries.

Planning only:
- do not write code
- do not create directories
- do not run benchmarks
- do not download datasets
- do not modify `paper/`

Design principle:
- Shared infrastructure must be implemented and stabilized before benchmark-specific adapters.

---

## Worker 0 - Shared Benchmark Infrastructure Owner

### Responsibility

Own all shared abstractions and the common execution contract.

### Proposed file ownership

Suggested owned files:
- `experiments/benchmarks/common/adapter.py`
- `experiments/benchmarks/common/case.py`
- `experiments/benchmarks/common/runner.py`
- `experiments/benchmarks/common/artifact.py`
- `experiments/benchmarks/common/metrics.py`
- `experiments/benchmarks/common/report.py`
- `experiments/benchmarks/common/config.py`

If the shared layer is instead placed under `experiments/external_validation/` or another existing namespace, Worker 0 owns the shared contract files there and defines the canonical import path for the other workers.

### Tasks

- Define `BenchmarkAdapter` interface.
- Define `BenchmarkCase` schema.
- Define `BenchmarkRunner` abstraction.
- Define artifact writer contract.
- Define metrics schema.
- Define shared failure handling behavior.

### Must define

Public interfaces other workers depend on:
- case normalization fields
- prediction record fields
- artifact file contract
- adapter error behavior
- metric naming and serialization rules

### Acceptance criteria

- MMLU and ARC can implement adapters without modifying shared code.
- Artifact outputs are consistent across benchmarks.
- Shared interfaces are stable enough for HumanEval to plug in later.

### Risk

- Complexity: Medium
- Dependency risk: Medium
- Validation strategy: interface review, schema round-trip checks, artifact compatibility checks

---

## Worker 1 - MMLU Adapter

### Dependency

- Worker 0 completion and interface freeze.

### Proposed file ownership

Suggested owned files:
- `experiments/benchmarks/mmlu/adapter.py`
- `experiments/benchmarks/mmlu/metrics.py`
- `experiments/benchmarks/mmlu/config.py`
- `experiments/benchmarks/mmlu/report.py`

Runner ownership should be decided with Worker 0:
- either a thin benchmark-specific runner wrapper under `experiments/benchmarks/mmlu/runner.py`
- or a shared runner invocation plus MMLU-specific configuration

### Tasks

- Dataset loader.
- Case normalization.
- Prompt builder.
- Scorer.
- Benchmark config.
- Artifact compatibility with shared writer.

### Forbidden

- Modifying shared interfaces.
- Creating an independent artifact format.
- Introducing MMLU-only runner behavior that bypasses shared execution flow.

### Acceptance criteria

- MMLU can run through the shared runner.
- Outputs conform to the common artifact contract.
- MMLU-specific logic stays inside MMLU-owned files.

### Risk

- Complexity: Medium
- Dependency risk: Medium
- Validation strategy: small-sample smoke test, score consistency check, artifact schema check

---

## Worker 2 - ARC Adapter

### Dependency

- Worker 0 completion and interface freeze.

### Proposed file ownership

Suggested owned files:
- `experiments/benchmarks/arc/adapter.py`
- `experiments/benchmarks/arc/metrics.py`
- `experiments/benchmarks/arc/config.py`
- `experiments/benchmarks/arc/report.py`

Runner ownership should mirror MMLU:
- shared runner first
- ARC-specific adapter second

### Tasks

- ARC-Easy adapter.
- ARC-Challenge adapter.
- Scorer.
- Config.
- Artifact compatibility with the shared writer.

### Must reuse

- Worker 0 interfaces.
- Shared runner.
- Shared artifact writer.

### Acceptance criteria

- ARC uses the same execution path as MMLU.
- ARC-Easy and ARC-Challenge remain separable in the output.
- No duplicate framework is introduced.

### Risk

- Complexity: Medium
- Dependency risk: Medium
- Validation strategy: split-level smoke test, choice integrity checks, output schema check

---

## Worker 3 - HumanEval Architecture

### Dependency

- Worker 0 completion and interface freeze.

### Important constraint

Do not implement sandbox yet.

### Scope

Only design:
- executor interface
- sandbox boundary
- failure model
- pass@1 evaluation contract

### Proposed file ownership

Suggested owned files:
- `experiments/benchmarks/humaneval/adapter.py`
- `experiments/benchmarks/humaneval/executor.py`
- `experiments/benchmarks/humaneval/metrics.py`
- `experiments/benchmarks/humaneval/config.py`
- `experiments/benchmarks/humaneval/report.py`

### Tasks

- Define execution interface.
- Define isolation requirements.
- Define timeout and failure taxonomy.
- Define pass@1 contract.
- Define how the future executor plugs into the shared runner.

### Acceptance criteria

- A future implementation can plug into the shared runner.
- The design makes sandbox constraints explicit.
- The failure model is strong enough for real execution-based evaluation.

### Risk

- Complexity: High
- Dependency risk: High
- Validation strategy: design review, contract review, failure-model review

---

## Integration Owner

### Responsibility

Own the integration points and resolve cross-worker contract issues.

### Suggested ownership

- Merge shared interfaces from Worker 0.
- Resolve schema conflicts.
- Validate artifact compatibility.
- Approve canonical import path and directory placement for the benchmark layer.

### Recommended role

One person or one coordinating agent should own:
- shared contract approval
- path/namespace decision
- artifact compatibility validation
- final gate checks before implementation begins

---

## Dependency Graph

```text
Worker 0
    |
    +---- Worker 1
    |
    +---- Worker 2
    |
    +---- Worker 3
```

Notes:
- Worker 1, Worker 2, and Worker 3 all depend on the shared contract from Worker 0.
- HumanEval remains architecture-only until the shared layer is stable.

---

## Review Gates

### Gate 1 - Shared interfaces approved

Criteria:
- adapter interface is fixed
- case schema is fixed
- artifact contract is fixed
- runner contract is fixed

### Gate 2 - MMLU produces artifact-compatible outputs

Criteria:
- MMLU design fits the shared contract
- no shared contract changes are required for MMLU

### Gate 3 - ARC reuses the same path

Criteria:
- ARC reuses the shared runner and artifact writer
- no duplicate framework appears

### Gate 4 - HumanEval executor contract approved

Criteria:
- sandbox boundary is explicit
- pass@1 contract is explicit
- failure taxonomy is explicit

---

## Recommendation

Implement in this order:

1. Worker 0 - Shared Benchmark Infrastructure Owner
2. Worker 1 - MMLU Adapter
3. Worker 2 - ARC Adapter
4. Worker 3 - HumanEval Architecture

Why:
- The shared layer must stabilize first so adapters do not diverge.
- MMLU is the cleanest first proof that the contract works.
- ARC validates reuse across a different dataset shape.
- HumanEval is the highest-risk path and should stay design-only until the shared contract is trusted.

---

## Namespace Decision

Do not decide the final directory split in parallel with adapter work.

Worker 0 should determine whether the benchmark layer should:
- extend `experiments/external_validation/`, or
- introduce `experiments/benchmarks/`

before any adapter implementation begins.

Reason:
- premature namespace decisions can create three incompatible experiment systems
- the repository needs one extensible evidence-generation framework, not parallel framework clones

