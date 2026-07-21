# Benchmark Implementation Task Breakdown

This document turns the benchmark framework extension plan into executable engineering tasks with explicit dependencies and acceptance criteria.

Planning only:
- do not implement code
- do not create benchmark directories
- do not download datasets
- do not run experiments
- do not modify `paper/`

---

## Task Group 1 - Shared Benchmark Infrastructure

### Objective

Create the minimum shared layer required by MMLU, ARC, and HumanEval.

### Tasks

#### 1. BenchmarkAdapter interface
- Define required methods.
- Define input/output contracts.
- Define error handling behavior.

Suggested methods:
- `load_dataset()`
- `create_cases()`
- `build_prompt()`
- `evaluate_prediction()`
- `summarize_metrics()`

#### 2. BenchmarkCase schema
- Define required fields.
- Define optional fields.
- Define serialization format.

Required fields should include:
- `benchmark_name`
- `case_id`
- `prompt`
- `reference`
- `expected_answer`
- `metadata`

Optional fields should include:
- `choices`
- `srp_input_context`
- `srp_recovered_context`
- `token_usage`
- `latency_seconds`

#### 3. BenchmarkRunner abstraction
- Define baseline execution.
- Define SRP execution.
- Define prediction collection.
- Define metric invocation.

#### 4. Artifact writer
- Define `config.json`.
- Define `raw_predictions.jsonl`.
- Define `metrics.json`.
- Define `report.md`.
- Define `metadata.json`.

### Acceptance Criteria
- MMLU, ARC, and HumanEval can reuse the same execution path.
- No benchmark-specific logic exists in the shared layer.
- Artifacts follow the same output contract across all benchmarks.

### Risk
- Complexity: Medium
- Dependency risk: Low to medium
- Validation strategy: unit tests for schema serialization, adapter contract checks, and artifact hash stability

---

## Task Group 2 - MMLU Adapter

### Objective

Implement the first real benchmark adapter.

### Tasks

#### 1. Dataset loading
- Load the benchmark source.
- Freeze the sample slice.
- Record dataset provenance.

#### 2. Case normalization
- Convert raw dataset rows into shared `BenchmarkCase` records.
- Preserve subject, choice list, and answer key.

#### 3. Prompt construction
- Build a baseline prompt.
- Build an SRP prompt path that records transformed context.

#### 4. Baseline execution
- Run the model on the original prompt.
- Record raw outputs and token usage.

#### 5. SRP execution
- Run the same question through SRP context transformation.
- Record the recovered semantic state and final answer.

#### 6. Multiple-choice scoring
- Compute accuracy.
- Preserve per-case scoring evidence.

#### 7. Artifact generation
- Write the benchmark artifact bundle under `experiments/results/mmlu/`.

### Acceptance Criteria
- Produces `config.json`, `raw_predictions.jsonl`, `metrics.json`, `report.md`, and `metadata.json`.
- Results are generated from real execution, not placeholders.
- No paper-facing file changes are required for the benchmark to run.

### Risk
- Complexity: Medium
- Dependency risk: Medium
- Validation strategy: small sample run, deterministic score check, artifact hash verification

---

## Task Group 3 - ARC Adapter

### Objective

Reuse the shared infrastructure to add ARC support.

### Tasks

#### 1. ARC dataset adapter
- Load ARC cases using the shared adapter pattern.
- Normalize tasks into the shared benchmark schema.

#### 2. ARC-Easy support
- Preserve the easy split separately in raw artifacts and metrics.

#### 3. ARC-Challenge support
- Preserve the challenge split separately in raw artifacts and metrics.

#### 4. Choice-preserving evaluation
- Keep answer choices explicit.
- Score exact choice selection, not only free-form text.

#### 5. Artifact generation
- Write benchmark outputs under `experiments/results/arc/`.

### Acceptance Criteria
- ARC reuses the shared adapter, runner, and artifact writer.
- No duplicate framework is introduced.
- ARC-Easy and ARC-Challenge remain distinguishable in the outputs.

### Risk
- Complexity: Medium
- Dependency risk: Medium
- Validation strategy: split-level smoke test, prompt/choice integrity checks, score reproducibility

---

## Task Group 4 - HumanEval Execution Layer

### Objective

Add safe executable evaluation support.

### Tasks

#### 1. Execution sandbox requirements
- Define isolation model.
- Define filesystem and process restrictions.
- Define allowed runtime inputs.

#### 2. Timeout handling
- Enforce per-task execution limits.
- Guarantee bounded failure behavior.

#### 3. Isolated execution
- Run generated code in a task-isolated environment.
- Prevent one task failure from terminating the run.

#### 4. Code extraction
- Extract code blocks from model output.
- Normalize the final candidate solution.

#### 5. pass@1 evaluator
- Compute pass@1 from execution outcomes.
- Preserve run-level and task-level evidence.

#### 6. Failure taxonomy
- Classify generation failure.
- Classify syntax error.
- Classify runtime error.
- Classify timeout.
- Classify wrong answer.

### Acceptance Criteria
- A failed task cannot terminate the entire benchmark run.
- All failures are recorded.
- The benchmark outputs a valid artifact bundle under `experiments/results/humaneval/`.

### Risk
- Complexity: High
- Dependency risk: High
- Validation strategy: sandbox unit tests, timeout tests, failure injection tests, small isolated task run

---

## Task Dependencies

```text
Shared Benchmark Infrastructure
      |
      +---- MMLU Adapter
      |
      +---- ARC Adapter
      |
      +---- HumanEval Execution Layer
                     |
                     +---- Sandbox
                     |
                     +---- pass@1 evaluator
```

Dependency notes:
- The shared infrastructure must exist before any benchmark-specific adapter work.
- MMLU and ARC should both consume the same runner and artifact layer.
- HumanEval depends on the shared infrastructure plus a new sandbox/execution layer.

---

## Risk Assessment

| Task Group | Complexity | Dependency Risk | Validation Strategy |
| --- | --- | --- | --- |
| Shared Benchmark Infrastructure | Medium | Low to medium | Contract tests, schema round-trip tests, artifact writer tests |
| MMLU Adapter | Medium | Medium | Sample run, score consistency, artifact inspection |
| ARC Adapter | Medium | Medium | Split-level smoke test, choice integrity checks |
| HumanEval Execution Layer | High | High | Sandbox isolation tests, timeout tests, failure injection tests |

---

## Recommended Execution Sequence

1. Shared Benchmark Infrastructure
2. MMLU Adapter
3. ARC Adapter
4. HumanEval Execution Layer

### Why this order

- The shared layer prevents three separate one-off benchmark implementations.
- MMLU is the cleanest first validation of the adapter pipeline.
- ARC can then reuse the same shared machinery with a different dataset shape.
- HumanEval should come last because it adds the highest-risk piece: safe code execution and pass@1 evaluation.

---

## Summary

This breakdown keeps the project in the right order:
- first define the shared execution surface,
- then validate it with a structured multiple-choice benchmark,
- then generalize to a second dataset format,
- and only then add execution-based evaluation.

