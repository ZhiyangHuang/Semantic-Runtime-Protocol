# Full Benchmark Execution Plan

## 1. Objective

This plan defines the reproducible full benchmark execution protocol for MMLU and ARC.

What full benchmark execution proves:
- the benchmark infrastructure can support real dataset-scale runs
- the adapter layer can process full benchmark slices without smoke-only shortcuts
- the shared runner, artifact writer, and metrics flow remain stable at larger scale
- SRP and baseline variants can be compared under a controlled execution contract

What it does not prove:
- benchmark superiority in a leaderboard sense
- a universal claim about intelligence or reasoning
- paper-facing evidence until artifacts are reviewed and approved

---

## 2. Benchmark Scope

### MMLU

#### Dataset source

- Source: `cais/mmlu`
- Access mode: HuggingFace dataset loading

#### Dataset version/reference

- Use the frozen dataset reference recorded in the execution config
- Preserve the source reference in artifact metadata

#### Split

- Validation split for the controlled full run unless a later review requires a different paper-facing slice

#### Subjects

- Full subject set supported by the chosen dataset reference, subject to resource budget and reproducibility review

#### Sample policy

- Full benchmark execution should use the declared benchmark protocol rather than smoke sampling
- If a subject subset is used for a bounded full run, the subset policy must be fixed before execution and written into the config

#### Full validation or test set

- Prefer the split that is consistent with the benchmark protocol already used by the adapter
- If the execution uses a validation subset rather than a test set, the choice must be documented and kept stable

### ARC

#### Dataset source

- Source: `allenai/ai2_arc`

#### Dataset version/reference

- Use the frozen dataset reference recorded in the execution config

#### Splits

- ARC-Easy
- ARC-Challenge only if explicitly included in the final execution scope

#### Sample policy

- Full run should use the declared protocol for the chosen split(s)
- If only ARC-Easy is used initially, ARC-Challenge remains a separate later scope

#### Why this scope

- MMLU and ARC already validated the pipeline in smoke mode
- Full execution should now measure benchmark-scale behavior without changing the adapter contract
- ARC-Challenge is intentionally optional because it may raise the cost and complexity of the first full run

---

## 3. Evaluation Variants

### Baseline

Baseline must preserve the benchmark task without SRP recovery assistance.

Required baseline settings:
- original task prompt format
- original dataset context only
- no SRP-recovered state injected
- same generation parameters as SRP

### SRP

SRP must preserve the same benchmark task while inserting SRP-transformed context.

Required SRP settings:
- SRP state input
- recovered semantic context
- same prompt template family as baseline
- same generation parameters as baseline

### Comparison rule

- baseline and SRP must differ only in memory/context handling
- generation parameters, model, and evaluation rules must remain aligned
- any benchmark-specific difference must be explicitly documented and justified

---

## 4. Metrics

### Primary metric

- `accuracy`

### Secondary metrics

- `latency`
- `token_usage`
- `failure_rate`
- `artifact_completeness`

### Metric policy

- do not introduce unsupported metrics
- do not redefine benchmark semantics to favor SRP
- keep the metric set identical across baseline and SRP for comparison integrity

---

## 5. Execution Configuration

### Model

- model identifier must be fixed before execution
- current smoke runs used `Qwen/Qwen3-4B-AWQ`
- the full run may keep the same model for comparability unless a formal configuration review changes it

### Generation

- `temperature` should remain deterministic or near-deterministic
- `max_output_tokens` should be low enough for choice-based benchmarks
- prompt format should remain stable across runs

### Runtime

- local OpenAI-compatible endpoint
- hardware and host environment should be recorded in metadata
- runtime assumptions must be captured before execution

### Reproducibility

- fixed seed where supported
- fixed dataset reference
- fixed prompt template
- fixed artifact directory per run

---

## 6. Artifact Output Contract

Final locations:

```text
experiments/results/mmlu/
experiments/results/arc/
```

Required files:
- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

### Field expectations

`config.json`
- benchmark name
- dataset source/version
- split or subject scope
- model
- prompt format
- SRP configuration
- generation settings
- sample policy

`raw_predictions.jsonl`
- one row per evaluated case per variant
- prompt
- prediction
- expected answer
- variant
- token usage
- latency
- raw output
- failure status if any

`metrics.json`
- primary metric
- sample count
- correct / incorrect counts
- failure counts
- latency summary
- token summary
- variant counts

`metadata.json`
- commit hash
- generation timestamp
- artifact hashes
- runner version
- dataset provenance

`report.md`
- experiment setup
- results summary
- metric summary
- reproducibility notes
- failure notes if any

---

## 7. Resource Planning

### Runtime

- Full MMLU runtime depends on the chosen subject scope and sample policy
- ARC full runtime depends on whether ARC-Easy only or ARC-Easy plus ARC-Challenge is included
- Both should be expected to take materially longer than smoke runs

### Token cost

- MMLU and ARC are choice-based, so output tokens should remain low
- Prompt tokens are the dominant cost driver because of context and choice formatting

### Storage size

- raw predictions scale linearly with evaluated cases and variants
- artifact storage will be moderate, but raw predictions can grow quickly at full scale

### Bottlenecks

- dataset download / cache warm-up
- local endpoint throughput
- prompt length for larger subject or choice contexts
- artifact review time

---

## 8. Failure and Rerun Policy

### Rerun allowed when

- dataset source changes unexpectedly
- endpoint or environment failure causes incomplete artifacts
- scorer or parser bug is found and fixed
- artifact writer bug is found and fixed

### Artifact versioning

- each rerun must land in a new output directory or a clearly versioned run directory
- do not overwrite a reviewed artifact without recording the rerun reason

### Failed runs

- preserve partial outputs if they are useful for diagnosis
- record the failure reason explicitly
- do not backfill metrics manually

---

## 9. Paper Integration Boundary

Before execution:
- no paper changes
- no evidence manifest changes

After execution:
- only verified artifacts may update paper-facing summaries
- paper updates must wait until artifact review passes
- benchmark numbers should not be promoted until the full run is audited

---

## 10. Execution Gates

### Gate 1: Plan approved

- execution protocol approved
- benchmark scope fixed
- artifact contract fixed

### Gate 2: Environment verified

- endpoint reachable
- dataset access available
- output directories clean

### Gate 3: Benchmark executed

- full MMLU or ARC run completed
- artifacts generated automatically

### Gate 4: Artifact audited

- raw predictions inspected
- metrics verified
- reproducibility fields checked

### Gate 5: Evidence manifest update considered

- only after audit passes
- only if paper-facing summaries are ready

---

## Conclusion

Full benchmark execution should be used to validate benchmark-scale behavior under the already proven shared framework.

Recommended progression:
1. approve this plan
2. verify environment for full runs
3. execute full MMLU
4. audit artifacts
5. execute full ARC
6. audit artifacts
7. consider paper evidence updates only after review

HumanEval remains out of scope for this phase because it requires a separate execution-safety review.

