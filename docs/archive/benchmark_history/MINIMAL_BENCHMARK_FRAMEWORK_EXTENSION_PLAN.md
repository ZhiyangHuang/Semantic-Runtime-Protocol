# Minimal Benchmark Framework Extension Plan

## Goal

Design the smallest extension required to add real MMLU, ARC, and HumanEval evidence pipelines while reusing existing SRP experiment infrastructure.

Constraints:
- Do not modify `paper/`.
- Do not generate benchmark results.
- Do not create empty or placeholder reports.
- Do not run benchmarks in this phase.
- Preserve the current LongMemEval architecture and behavior.

---

## 1. Current Architecture Mapping

| Existing component | Purpose | Reusable for |
| --- | --- | --- |
| `experiments/common/local_llm.py` | OpenAI-compatible local generation client with latency and usage accounting | Benchmark prompting and generation for MMLU, ARC, HumanEval |
| `experiments/external_validation/runner.py` | Generic benchmark orchestration over adapters, baselines, records, metrics, and report rendering | A lightweight benchmark execution pattern and artifact bundle shape |
| `experiments/external_validation/benchmarks.py` | Benchmark adapter protocol and case loading helpers | Adapter interface design and dataset-to-case conversion |
| `experiments/real_world_validation/common/` | Dataset manifests, run configs, claim mapping, decisions, failure tracking, bundle writing | Artifact contract, report generation, metadata, and provenance patterns |
| `experiments/real_world_validation/longmemeval/runner.py` | End-to-end LongMemEval validation pipeline | Reference for benchmark-to-SRP integration without refactoring it |
| `experiments/validation/boundary_reporting/runner.py` | Generic case evaluation, replay consistency, and bundle writing | Output hashing, replay checks, and report artifacts |
| `scripts/run_reproduction.py` | Stepwise orchestration pattern | High-level benchmark execution sequencing |

Reusable for:
- Dataset ingestion and normalization
- Generation backend invocation
- Metric aggregation
- Report and metadata writing
- Provenance and manifest generation

Not reusable as-is:
- A real MMLU scorer
- A real ARC scorer
- A HumanEval execution sandbox
- A benchmark-specific adapter layer for the three tasks

---

## 2. Proposed New Components

### Benchmark Adapter Interface

Purpose:
- Convert benchmark-specific datasets into a shared internal case format.
- Provide benchmark-specific scoring hooks without inventing separate frameworks.

Input:
- Dataset records or downloaded dataset slices
- Benchmark configuration
- Model outputs or generation records

Output:
- Normalized benchmark cases
- Predictions or execution traces
- Benchmark metrics inputs

Responsibilities:
- Load benchmark data
- Create a normalized task/case representation
- Construct prompts or execution payloads
- Evaluate predictions against benchmark-specific scoring rules
- Emit raw prediction records for auditability

Suggested interface:

```text
BenchmarkAdapter
  - load_dataset()
  - create_cases()
  - build_prompt()
  - evaluate_prediction()
  - summarize_metrics()
```

Recommended shared case fields:
- `benchmark_name`
- `case_id`
- `prompt`
- `reference`
- `choices` when applicable
- `expected_answer`
- `srp_input_context`
- `srp_recovered_context`
- `metadata`

### Shared Benchmark Runner

Purpose:
- Execute a benchmark end-to-end using an adapter, the local generation backend, and a metrics evaluator.

Responsibilities:
- Load benchmark configuration
- Load dataset through adapter
- Run baseline and SRP variants
- Capture raw predictions
- Collect token usage and latency
- Persist artifacts and metadata

### Shared Artifact Writer

Purpose:
- Produce a consistent output contract for every benchmark.

Responsibilities:
- Write `config.json`
- Write `raw_predictions.jsonl`
- Write `metrics.json`
- Write `report.md`
- Write `metadata.json`

### Shared Metrics Schema

Purpose:
- Normalize benchmark output fields so reports can be generated mechanically.

Responsibilities:
- Store benchmark name, sample count, model, prompt format, and runtime settings
- Store per-run and aggregate metrics
- Store artifact hashes and generation provenance

---

## 3. MMLU Extension Plan

### New files
- `experiments/benchmarks/mmlu/adapter.py`
- `experiments/benchmarks/mmlu/runner.py`
- `experiments/benchmarks/mmlu/metrics.py`
- `experiments/benchmarks/mmlu/report.py`
- `experiments/benchmarks/mmlu/config.py`

### Modified files
- `experiments/external_validation/runner.py` only if its orchestration pattern is factored into a shared helper
- `experiments/common/local_llm.py` only if prompt formatting helpers are needed
- `scripts/run_reproduction.py` only after the implementation exists

### Reuse
- `experiments/common/local_llm.py` for generation
- `experiments/external_validation/benchmarks.py` as a reference for adapter design
- `experiments/real_world_validation/common/` for manifests, metadata, and report writing patterns
- `experiments/validation/boundary_reporting/runner.py` for replayable artifact writing style

### New dependencies
- A real MMLU dataset source or dataset loader
- A scoring implementation for multiple-choice accuracy
- Potentially HuggingFace `datasets` or a dataset-specific loader

### Estimated implementation steps
1. Define MMLU adapter schema.
2. Implement dataset loader and subject sampling logic.
3. Implement prompt construction for baseline and SRP variants.
4. Implement accuracy scorer.
5. Implement artifact writer and report renderer.
6. Wire the runner into reproduction scripts only after validation passes.

### Notes
- MMLU should remain a question-answer benchmark, not a memory-only benchmark.
- If SRP is evaluated here, the artifact should record original question input, recovered context, and final answer attribution.

---

## 4. ARC Extension Plan

### New files
- `experiments/benchmarks/arc/adapter.py`
- `experiments/benchmarks/arc/runner.py`
- `experiments/benchmarks/arc/metrics.py`
- `experiments/benchmarks/arc/report.py`
- `experiments/benchmarks/arc/config.py`

### Modified files
- Same as MMLU only if shared helpers are factored

### Reuse
- `experiments/common/local_llm.py`
- Existing report and metadata patterns from `experiments/real_world_validation/common/`
- Existing benchmark orchestration pattern from `experiments/external_validation/runner.py`

### New dependencies
- ARC dataset access
- Accuracy scoring for ARC-Easy and ARC-Challenge
- Optional dataset loader dependency if not already present

### Estimated implementation steps
1. Define ARC adapter with separate handling for ARC-Easy and ARC-Challenge.
2. Implement loader and prompt builder.
3. Implement exact-match or choice-based accuracy scoring.
4. Record baseline and SRP runs with raw outputs.
5. Generate report and metadata bundle.

### Notes
- ARC should keep the choice structure explicit in the raw artifact.
- Do not compress ARC into a generic text generation task without preserving choice attribution.

---

## 5. HumanEval Extension Plan

### Required additions
- Generation adapter
- Execution sandbox
- `pass@1` evaluator
- Timeout handling
- Failure isolation
- Code extraction and normalization

### New files
- `experiments/benchmarks/humaneval/adapter.py`
- `experiments/benchmarks/humaneval/runner.py`
- `experiments/benchmarks/humaneval/executor.py`
- `experiments/benchmarks/humaneval/metrics.py`
- `experiments/benchmarks/humaneval/report.py`
- `experiments/benchmarks/humaneval/config.py`

### Reuse
- `experiments/common/local_llm.py` for generation
- Artifact/report patterns from `experiments/real_world_validation/common/`
- Reproduction orchestration patterns from `scripts/run_reproduction.py`

### Must be newly implemented
- Secure code execution sandbox
- Timeout enforcement
- Per-task isolation
- `pass@1` calculation
- Failure classification for runtime errors, syntax errors, and timeouts

### Estimated implementation steps
1. Define task normalization and code prompt schema.
2. Build generation adapter.
3. Implement isolated execution layer.
4. Implement `pass@1` scoring and failure buckets.
5. Add report and artifact generation.
6. Validate sandbox behavior before any paper-facing reference.

### Notes
- HumanEval is the highest-risk benchmark because it needs executable code isolation.
- Do not rely on the existing LongMemEval or boundary-reporting pipeline as a substitute for code execution.

---

## 6. Proposed Directory Layout

Do not create this layout yet. This is a proposal only.

```text
experiments/
    benchmarks/
        common/
            adapter.py
            runner.py
            artifact.py
            metrics.py
            report.py
        mmlu/
            adapter.py
            runner.py
            metrics.py
            report.py
            config.py
        arc/
            adapter.py
            runner.py
            metrics.py
            report.py
            config.py
        humaneval/
            adapter.py
            executor.py
            runner.py
            metrics.py
            report.py
            config.py
```

---

## 7. Artifact Contract

Every benchmark result must produce:

- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `report.md`
- `metadata.json`

### Required field expectations

`config.json`
- benchmark name
- dataset version
- sample count
- model identifier
- prompt format
- SRP configuration
- execution parameters

`raw_predictions.jsonl`
- one record per sample
- prompt or task identifier
- model output or execution result
- token usage when applicable
- latency when applicable
- failure status when applicable

`metrics.json`
- primary benchmark score
- sample count
- baseline and SRP comparison fields
- latency and token-cost statistics
- error counts

`report.md`
- human-readable experiment setup
- primary results
- efficiency summary
- error analysis
- reproducibility notes

`metadata.json`
- commit hash
- generation timestamp
- artifact hashes
- runner version
- dataset provenance

---

## 8. Dependency Risk

### Required external packages
- Potential HuggingFace `datasets` for MMLU and ARC loading
- Potential HumanEval-related evaluation tooling if not already present
- Potential sandbox/runtime support for code execution isolation

### Potential licensing issues
- MMLU, ARC, and HumanEval may have source-specific redistribution or access constraints.
- The repo should continue the registry-based policy unless explicit license review says otherwise.

### Environment requirements
- A working local OpenAI-compatible generation endpoint
- Deterministic runtime for evaluation
- For HumanEval, a safe code execution environment

### Reproducibility risks
- Dataset source drift if benchmark slices are not frozen by manifest
- Model endpoint variability
- Non-deterministic generation settings
- HumanEval sandbox differences across machines
- Scoring drift if benchmark adapters are not versioned

---

## 9. Implementation Order

Recommended dependency-safe order:

1. Shared benchmark adapter interface
2. Shared artifact writer and metrics schema
3. MMLU
4. ARC
5. HumanEval sandbox and evaluator

### Why this order

- The shared interface and artifact contract reduce duplicated logic across all three benchmarks.
- MMLU is the clearest first adapter because it is a structured multiple-choice task with straightforward accuracy scoring.
- ARC can likely reuse the same adapter pattern with a different dataset schema.
- HumanEval should come last because it adds the highest-risk component: code execution isolation and `pass@1` evaluation.

---

## Summary Recommendation

Proceed with a minimal benchmark framework extension rather than a full benchmark rewrite.

The most efficient path is:
- keep LongMemEval unchanged,
- add a shared benchmark adapter layer,
- implement MMLU and ARC adapters first,
- implement HumanEval only after the execution sandbox is defined and verified.

