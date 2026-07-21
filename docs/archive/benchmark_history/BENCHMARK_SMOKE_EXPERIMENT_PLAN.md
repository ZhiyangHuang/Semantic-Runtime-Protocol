# Benchmark Smoke Experiment Plan

## 1. Validation Objective

The smoke experiment proves that the benchmark pipeline works end-to-end on real benchmark data without optimizing for benchmark scores.

What it verifies:
- real dataset ingestion
- adapter-to-case conversion
- shared runner execution
- prediction recording
- automatic metric generation
- artifact writing
- report generation from metrics

What it does not verify:
- benchmark superiority
- full release-scale performance
- paper-facing claims

---

## 2. MMLU Smoke Experiment

### Dataset

- Source: real MMLU data source selected by the adapter implementation
- Version: the same frozen version recorded in the adapter config
- Subset selection: a small subject slice chosen to exercise multiple-choice parsing across more than one subject

### Sample size

- Target: approximately 50 samples
- Suggested structure: 5 subjects × 10 questions each

### Execution variants

- `baseline`
- `srp`

### Metrics

- `accuracy`
- `token_usage`
- `latency`
- `artifact_completeness`

### Expected artifacts

Output directory:

```text
experiments/results/mmlu_smoke/
```

Required files:

- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

### Smoke success meaning

- dataset loading works
- answer parsing works
- accuracy is computed automatically
- artifacts are complete and internally consistent

---

## 3. ARC Smoke Experiment

### Dataset

- Selection: `ARC-Easy` only for the smoke run
- Version: the frozen version recorded in the ARC adapter config
- Subset selection: a small sample slice that exercises choice-preserving evaluation

### Sample size

- Target: approximately 50 samples

### Execution variants

- `baseline`
- `srp`

### Metrics

- `accuracy`
- `token_usage`
- `latency`
- `artifact_completeness`

### Expected artifacts

Output directory:

```text
experiments/results/arc_smoke/
```

Required files:

- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

### Smoke success meaning

- ARC-Easy dataset loading works
- choice handling is preserved
- automatic scoring works
- artifacts are complete and readable

---

## 4. Model Configuration

### Endpoint

- Use the existing local OpenAI-compatible endpoint already supported by `experiments/common/local_llm.py`

### Recommended settings

- `temperature = 0.0`
- low `max_output_tokens` suitable for short-form answers
- deterministic prompt formatting
- fixed seed where the adapter or runner supports it

### Why

- The smoke run is validating the pipeline, not randomness-sensitive creativity.
- Deterministic settings reduce noise in adapter and artifact validation.
- Short outputs reduce cost and simplify answer extraction.

---

## 5. SRP Evaluation Boundary

The smoke experiment should preserve benchmark semantics while allowing SRP to transform context only where the framework already expects it.

### What enters SRP

- original question context
- recovered semantic context
- any adapter-defined memory or state object

### What is measured

- answer correctness
- semantic recovery visibility
- latency and token use
- artifact completeness

### Boundary rule

- do not alter the benchmark definition just to improve the score
- SRP must remain an evaluable transformation layer, not a hidden benchmark rewrite

---

## 6. Failure Handling

### Missing dataset

- stop the smoke run for that benchmark
- record a failure artifact or failure status
- do not fabricate results

### Generation failure

- record the failed prediction row
- mark the case as failed
- continue with the remaining cases

### Invalid answer

- classify as invalid output
- preserve raw text
- continue evaluation

### Timeout

- record timeout as a failure category
- continue the batch if possible

### Metric failure

- fail the benchmark run cleanly
- keep raw predictions and execution traces
- do not backfill metrics manually

---

## 7. Execution Order

Recommended order:

1. MMLU smoke
2. Artifact review
3. ARC smoke
4. Artifact review
5. Full benchmark consideration

### Why this order

- MMLU is the best first proof that the shared runner and adapter contract work on a real dataset.
- Reviewing the MMLU artifacts before moving on reduces the chance of carrying a schema error into ARC.
- ARC then confirms the same framework can absorb a different dataset structure without changes.
- Only after both smoke runs pass should full benchmark-scale execution be considered.

---

## 8. Success Criteria

A smoke experiment succeeds only if:

- real input data was processed
- raw predictions exist
- metrics were generated automatically
- report was generated from metrics
- no manual result editing occurred
- the artifact directory is complete and internally consistent

### Smoke-level interpretation

- success means pipeline correctness
- success does not mean benchmark dominance
- success does not mean paper-ready release evidence

