# HumanEval Execution Design

## 1. HumanEval Integration Model

HumanEval should plug into the existing benchmark framework as an execution-based adapter, not as a separate framework.

Integration path:

```text
BenchmarkAdapter
    |
BenchmarkRunner
    |
ArtifactWriter
```

### Reused components

- `experiments/benchmarks/common/schema.py`
- `experiments/benchmarks/common/runner.py`
- `experiments/benchmarks/common/artifact.py`
- `experiments/benchmarks/common/report.py`
- `experiments/benchmarks/common/metrics.py`
- `experiments/common/local_llm.py`

### Execution-specific components

- code extraction from generated text
- isolated code execution
- timeout handling
- failure taxonomy
- `pass@1` evaluation

### Design implication

HumanEval is not a multiple-choice benchmark like MMLU or ARC.
It requires a generation step followed by a separate execution step.
That makes it compatible with the shared framework only if the framework supports an executor extension.

---

## 2. Executor Interface

Define an abstract executor contract that runs a candidate solution against a test specification.

### Input

- `task_id`
- `generated_code`
- `test_specification`
- `execution_configuration`

### Output

- `passed` boolean
- `stdout`
- `stderr`
- `execution_time_seconds`
- `failure_category`
- `failure_message`
- optional structured trace

### Failure categories

- `syntax_error`
- `runtime_error`
- `timeout`
- `failed_assertion`
- `sandbox_error`
- `unknown_error`

### Expected behavior

- The executor must be deterministic under a fixed environment and fixed inputs.
- The executor must isolate task failures so one task cannot abort the entire benchmark run.
- The executor must preserve raw diagnostics for auditability.

---

## 3. Sandbox Boundary

The sandbox should define a hard boundary between untrusted generated code and the host environment.

### Inside sandbox

- generated candidate solution
- task-specific test invocation
- per-task temporary files
- per-task process lifecycle
- stdout and stderr capture

### Outside sandbox

- benchmark configuration
- task loading
- code extraction
- prompt construction
- result aggregation
- artifact writing
- paper-facing reporting

### Required isolation properties

- process isolation
- filesystem isolation
- network restrictions
- resource limits
- timeout enforcement

### Requirements, not implementation choices

This design does not choose Docker, subprocess-only isolation, container sandboxes, or remote sandboxes.
It only requires that the eventual implementation provide:

- no network access by default
- bounded CPU and wall-clock execution
- bounded memory usage
- no host filesystem writes outside the sandbox boundary
- reproducible task-level execution results

---

## 4. HumanEval Adapter Design

The HumanEval adapter should behave differently from MMLU and ARC because the output is executable code, not a choice label.

### Required responsibilities

- load tasks
- create prompts
- extract generated code
- hand execution payloads to the executor
- collect execution results
- map execution outcomes into benchmark metrics

### Recommended case fields

- `task_id`
- `prompt`
- `reference_solution`
- `test_specification`
- `srp_input_context`
- `srp_recovered_context`
- `metadata`

### Execution flow

```text
task -> prompt -> generated code -> code extraction -> executor -> execution result -> metrics
```

### Difference from MMLU / ARC

- MMLU and ARC can score a text answer directly.
- HumanEval must first parse code from the model output.
- HumanEval then executes that code against hidden or controlled tests.
- HumanEval therefore needs explicit failure handling for both generation and runtime layers.

---

## 5. Metrics Contract

HumanEval metrics must remain compatible with the shared benchmark metrics schema while adding execution-specific fields.

### Required metrics

- `pass@1`
- `passed_tasks`
- `failed_tasks`
- `failure_categories`
- `execution_failure_count`
- `syntax_error_count`
- `runtime_error_count`
- `timeout_count`
- `sandbox_error_count`

### Shared schema compatibility

The metrics object should still satisfy the common benchmark output shape:

- benchmark name
- sample count
- primary score
- latency summary
- token usage summary
- error counts

### Suggested interpretation

- `pass@1` is the primary benchmark score.
- `passed_tasks / total_tasks` may be the same as `pass@1` in a single-sample setting, but the evaluator should preserve the exact metric definition.
- Failure categories should be aggregated by count and rate.

---

## 6. Artifact Contract

HumanEval artifacts should extend the shared benchmark bundle with execution traces.

### Expected files

- `config.json`
- `raw_predictions.jsonl`
- `execution_results.json`
- `metrics.json`
- `metadata.json`
- `report.md`

### Field expectations

`config.json`
- benchmark name
- dataset version
- sample count
- model identifier
- prompt format
- SRP configuration
- execution configuration
- timeout settings

`raw_predictions.jsonl`
- task id
- prompt
- generated code
- extracted code
- token usage when available
- latency when available
- extraction status

`execution_results.json`
- task id
- passed boolean
- stdout
- stderr
- execution time
- failure category
- failure message

`metrics.json`
- pass@1
- passed tasks
- failed tasks
- failure category breakdown
- latency summary
- token usage summary

`metadata.json`
- commit hash
- generation timestamp
- artifact hashes
- runner version
- dataset provenance

`report.md`
- experiment setup
- execution summary
- pass@1
- failure analysis
- reproducibility notes

---

## 7. Security and Reproducibility Risks

### Arbitrary code execution risk

HumanEval introduces untrusted code execution.
The sandbox must be treated as a security boundary, not only a convenience layer.

### Dependency differences

Different Python or package versions can change execution behavior and pass rates.
The execution environment must be versioned and recorded.

### Timeout nondeterminism

Timeout-sensitive tasks can be affected by host load.
The implementation should record timeout settings and environment characteristics.

### Environment drift

Small changes in filesystem, package versions, or interpreter versions can alter results.
The report must preserve the execution environment metadata.

---

## 8. Implementation Roadmap

### Phase A - Interface only

- define executor interface
- define failure taxonomy
- define artifact extension
- define metrics contract

### Phase B - Sandbox implementation

- implement isolated execution
- enforce resource limits
- enforce timeout handling
- validate failure isolation

### Phase C - HumanEval adapter

- load tasks
- create prompts
- extract generated code
- send payloads to executor
- collect results

### Phase D - Benchmark execution

- run small smoke tests
- validate artifact generation
- validate `pass@1` aggregation

### Phase E - Paper evidence integration

- only after the execution path is verified
- update evidence manifests and summary artifacts

---

## Final Conclusion

**A. HumanEval can reuse the current framework with executor extension.**

Reason:
- the shared benchmark infrastructure already provides adapter, runner, artifact, and metrics seams;
- HumanEval needs a new executor layer, but not a separate end-to-end framework;
- the correct next step is to extend the existing benchmark architecture, not replace it.

