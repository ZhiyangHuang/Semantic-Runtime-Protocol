# SRP Next-Phase Tasks

This document continues `SRP_IMPLEMENTATION_TASKS.md` from the point where the protocol core is largely implemented.

Its goal is to separate:

- completed protocol-core work
- remaining paper / experiment work
- next-phase architectural improvements suggested by `temporary4.md`

The key shift is:

```text
chunk-preserving SRP
-> state-preserving SRP
```

That is the main direction for the next version.

---

## 0. Definition Freeze

This roadmap now depends on frozen theory-layer documents:

- Research questions: [docs/research_questions.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/research_questions.md)
- Metric definitions: [docs/metric_definitions.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/metric_definitions.md)
- Interface contracts: [docs/interface_contracts.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/interface_contracts.md)

The execution layer should reference these documents rather than redefining them here.

---

## 1. Current Read of the System

The current SRP pipeline already proves something important:

- SRP can complete a full `compress -> recover -> validate -> rollback` cycle on a real LongBench v2 task under an 8k context limit.
- The current bottleneck is no longer runtime feasibility.
- The current bottleneck is semantic state fidelity.

The strongest evidence is the gap already observed in LongBench:

- `semantic_similarity = 0.9234`
- `validation_coverage = 0.029565`

This means:

- the recovered text can still look semantically close at the embedding level
- while the benchmark-critical runtime semantics are almost entirely lost

That is exactly why SRP needs an integrity validator instead of trusting surface similarity.

---

## 2. Main Diagnosis from `temporary4.md`

`temporary4.md` points to one central mismatch:

```text
current SRP compresses text chunks
but the validator checks semantic runtime state
```

In other words:

- the storage unit is still mostly `chunk`
- the verification unit is already `semantic object`

So the next phase should not focus first on:

- changing the selector model
- adding more backbones
- tuning embeddings harder

It should focus on:

- extracting semantic runtime objects before compression
- making compression object-aware
- making recovery reconstruct state instead of paraphrased text

---

## 3. Next-Phase Architectural Direction

### 3.1 Semantic extraction before compression

Current rough flow:

```text
Text
-> Chunking
-> Chunk scoring
-> Top-k chunk selection
-> Recovery
```

Next-phase target:

```text
Text
-> Semantic parsing
-> Typed runtime objects
-> Importance estimation
-> Compression
-> Recovery
-> Validation
```

Priority:

- make object extraction part of the compression path, not only the validation path
- allow chunk selection to be guided by object retention goals

### 3.2 Object-level compression instead of chunk-level compression

Target state:

- chunks remain storage units
- semantic objects become the primary protocol units

Example object types for LongBench-style MCQ:

- `question`
- `candidate_answer`
- `answer_evidence`
- `reasoning_constraint`
- `option_mapping`

### 3.3 Recovery should reconstruct state, not only summary text

Current risk:

- recovery still allows the generator to rewrite, merge, or omit facts

Next-phase target:

```text
compressed semantic state
-> runtime state reconstruction
-> optional text view for the LLM
```

This means recovered output should move closer to:

- structured semantic objects
- typed constraints
- explicit evidence links

and farther from:

- free-form paraphrased summaries

### 3.4 Query-aware importance

Current importance is mostly global.

Next-phase target:

```text
importance(object) = f(object, query, task type)
```

This matters especially for benchmarks such as LongBench, where:

- question-specific evidence is critical
- many context regions are globally relevant-looking but locally irrelevant

### 3.5 Recovery verification loop

Current flow:

```text
compress
-> recover
-> validate
-> rollback
```

Suggested next-phase flow:

```text
compress
-> recover
-> validate
-> failure analysis
-> repair retrieval
-> revalidate
-> commit or rollback
```

This is a natural extension of SRP as a runtime protocol rather than a one-shot summarizer.

---

## 4. New Metrics to Add

### 4.1 Semantic similarity vs semantic integrity gap

Recommended metric:

```text
integrity_gap = semantic_similarity - validation_coverage
```

Why it matters:

- it exposes cases where embeddings say "close enough"
- while the protocol says "critical state lost"

This should become a first-class diagnostic in reports and ablations.

### 4.2 Semantic retention score

Recommended definition:

```text
SRS =
sum_i w_i * similarity(o_i, o_i_hat)
/ sum_i w_i
```

Where:

- `o_i` is the source semantic object
- `o_i_hat` is the recovered semantic object
- `w_i` is importance

Then define:

```text
semantic_compression_loss = 1 - SRS
```

This would make the compression story much clearer than token reduction alone.

### 4.3 Validation pass rate as the first benchmark milestone

Before optimizing task accuracy, the next protocol milestone should be:

- raise semantic coverage
- then raise `validation_passed`
- then measure downstream task accuracy

---

## 5. Migrated Unfinished Items from `SRP_IMPLEMENTATION_TASKS.md`

The original implementation checklist is mostly complete. The remaining items fall into three groups.

### 5.1 External dependency verification

This is the only remaining item that is still partly implementation-adjacent:

- verify `E5SmallEncoder.encode_passage("hello")` in a real environment with `sentence-transformers` installed and confirm output dimension `384`

Status:

- keep as a real-environment verification item
- do not treat it as a protocol-core gap

### 5.2 Paper writing and presentation

These remain unfinished in the sense of paper polish rather than code:

- rewrite the protocol positioning and state definition into final paper prose
- write the formal `related work` boundary section
- turn the current metric set into a polished experiment section
- present drift curves, stability plots, and ablation tables in publication form

### 5.3 Final experiment organization

Still pending as experiment packaging work:

- fixed-generation-model / varying-evaluator ablation write-up
- robustness presentation for `rule-only`, `encoder-assisted`, and `judge-assisted`
- final CSV-to-figure pipeline for paper-quality reporting

---

## 6. New Concrete Task List for SRP v2

These are the recommended next implementation tasks after the current SRP core.

### 6.1 Introduce semantic object extraction into compression

Tasks:

- move typed object extraction earlier in the compression path
- build a compact object inventory before chunk ranking
- allow selected chunks to justify which objects they preserve

Acceptance:

- compression output includes selected object ids, not only selected chunk ids
- chunk selection can be traced back to object preservation goals

### 6.2 Add task-aware object schemas

Tasks:

- define task-family object templates
- start with `long_context_mcq`
- include question, options, answer evidence, and constraints

Acceptance:

- LongBench MCQ tasks yield typed objects aligned with task structure
- validation can separately score question retention, option retention, and evidence retention

### 6.3 Add object-conditioned chunk selection

Tasks:

- rank chunks by which high-importance objects they support
- include provenance from chunk -> object links
- keep chunk as storage unit, not semantic unit

Acceptance:

- selected chunks explain which objects they cover
- object coverage improves beyond current chunk-only baselines

### 6.4 Add state reconstruction mode in recovery

Tasks:

- support recovery into a structured state package
- optionally derive text from the structured state afterward

Acceptance:

- recovery output can produce a typed state view
- validator can consume that view without relying only on regenerated prose

### 6.5 Add repair loop after validation failure

Tasks:

- detect missing critical object types
- trigger focused retrieval from original memory
- re-run recovery for a second pass

Acceptance:

- failed first-pass recovery can attempt object-targeted repair
- diagnostics clearly distinguish `initial failure` from `repaired success`

### 6.6 Add integrity-gap reporting

Tasks:

- compute `integrity_gap`
- export it into records and CSV
- include it in diagnostics markdown reports

Acceptance:

- LongBench-style diagnostics show `semantic_similarity`, `coverage`, and `integrity_gap` together

---

## 7. Recovery Policy Evaluation Phase

The reconstruction experiments now show that the next question is no longer whether structured state is useful.
The next question is how SRP should reconstruct a compact executable state from that structured representation.

### 7.1 Motivation

Previous lifecycle and reconstruction experiments show:

- `source -> compressed` preserves object information
- structured state contains enough signal to recover validation-critical state
- reconstruction quality is mainly determined by recovery policy

Therefore, the next phase focuses on **reconstruction policy optimization**, not additional state representation capability.

### 7.2 Research Question

Given a high-fidelity structured semantic state:

> How can SRP reconstruct the smallest sufficient state while preserving task-relevant fidelity?

The goal shifts from:

```text
maximize recovered information
```

to:

```text
maximize task fidelity under minimal reconstruction
```

### 7.3 Recovery Policy Ablation

#### Policy A: Unrestricted Structured Reconstruction

Current baseline.

Behavior:

```text
structured package
-> LLM reconstruction
-> expanded state
```

Expected characteristics:

- high recall
- high coverage
- high object inflation

Measure:

- `validation_coverage`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_efficiency`

#### Policy B: Constrained Reconstruction

Goal:

Reduce unnecessary expansion.

Constraint:

Only reconstruct:

- existing structured objects
- explicitly supported relations
- validation-required entities

Disallow:

- new object generation
- unsupported inference

Expected:

```text
coverage slightly decreases
precision increases
inflation decreases
```

#### Policy C: Minimal Sufficient Reconstruction

Goal:

Recover the smallest state satisfying validation requirements.

Optimization target:

```text
maximize:

validation_coverage / recovered_object_count
```

Priority:

1. task-critical objects
2. important objects
3. supporting objects

Expected:

- lower object count
- lower hallucination
- better reconstruction efficiency

### 7.4 Required Metrics

Add:

#### Reconstruction Precision

Measure:

```text
correct recovered objects / all recovered objects
```

Purpose:

Detect over-generation.

#### Reconstruction Selectivity

Measure:

```text
recovered objects / available structured objects
```

Purpose:

Measure how aggressively reconstruction expands state.

#### Minimality Score

Measure:

```text
validation_coverage / recovered_object_count
```

Purpose:

Evaluate compactness.

### 7.5 Deferred Work

Until recovery policy is understood, defer:

- additional object taxonomy
- task-specific schemas
- self-improving repair agent
- more repair objectives

Reason:

The current bottleneck is not representation capacity but reconstruction control.

### 7.6 Phase II Extension: Semantic Runtime State Allocation

Current reconstruction policy evaluation shows that recovery quality is not only determined by how much semantic state is reconstructed, but also by how recovered information is allocated across runtime lifecycles.

The next extension evaluates whether recovered semantic state should be partitioned into:

- `S_active`
  - minimal executable state required for current task execution
- `S_latent`
  - valid semantic memory retained for future retrieval
- `S_discard`
  - invalid, redundant, or unsupported information removed from runtime state

Core objective:

```text
min |S_active|
```

subject to:

```text
TaskPerformance(S_active) >= C
```

while preserving:

```text
FutureRecall(S_latent) >= L
```

and minimizing:

```text
Hallucination(S_active) -> 0
```

Related design document:

- [docs/state_allocation_policy.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/state_allocation_policy.md)

Principle:

- allocation is conservative with respect to truth
- prefer latent retention over early discard for valid objects
- evaluate allocation as a feasibility problem over task success, not as object-level ground truth classification

### 7.7 Phase IV Candidate: Execution Validation

The next experiment after allocation comparison is to verify whether the allocated active state can independently support task execution.

This is an execution-layer check, not a reconstruction or allocation policy change.

Related design document:

- [docs/execution_validation_checklist.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/execution_validation_checklist.md)

---

## 8. Measurement-First Roadmap

The next phase should be run as a measurement program, not a capability-stacking program.

The core idea is:

```text
freeze schema
-> export metrics
-> run controlled tasks
-> ablate one mechanism at a time
-> only then add task adapters
```

### 7.1 Freeze the measurement schema

Before adding anything else, stabilize the metrics that define the next phase.

Required metric groups:

#### A. State Preservation

- `semantic_similarity`
- `validation_coverage`
- `validation_alignment`
- `integrity_gap`
- `semantic_compression_loss`
- `object_retention`
- `weighted_object_retention`
- `lost_important_object_count`

#### B. Recovery Quality

- `structured_state_package_present`
- `recovered_object_count`
- `recovered_object_type_counts`
- `validation_passed`
- `state_committed`

#### C. Repair Effectiveness

- `repair_attempted`
- `repair_context_flat`
- `coverage_before_repair`
- `coverage_after_repair`
- `critical_failures_before`
- `critical_failures_after`

#### D. Efficiency

- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `compressed_size`
- `compression_ratio`

### 7.2 Run controlled tasks first

Do not begin with large-scale LongBench sweeps.

Start with:

- a small structured recovery task
- a small object-retention task
- a small repair-loop task
- one LongBench v2 task for sanity checking

The goal is to keep failure modes explainable.

### 7.3 Ablation 1: Text recovery vs structured recovery

Compare:

```text
chunk selection
+ text recovery
+ text validation
```

vs

```text
object-aware compression
+ structured state recovery
+ typed validation
```

Measure:

- `validation_coverage`
- `object_retention`
- `commit_rate`
- `integrity_gap`

### 7.4 Ablation 2: Object-aware compression

Compare:

```text
chunk score only
```

vs

```text
chunk score
+ object_support_score
```

Measure:

- `weighted_object_retention`
- `lost_important_object_count`
- `critical_failures_before`

### 7.5 Ablation 3: Repair loop

Compare:

```text
fail -> rollback
```

vs

```text
fail
|
repair
|
validate again
```

Measure:

- `repair_attempted`
- `coverage_before_repair`
- `coverage_after_repair`
- `repair_gain`
- `token_overhead`

### 7.6 Ablation 4: Encoder vs local LLM judge

Use this only as a robustness and efficiency study.

Compare:

```text
e5-small-v2
```

vs

```text
local LLM judge
```

Measure:

- `semantic_similarity`
- `semantic_drift`
- `prompt_tokens`
- `total_tokens`
- `validation_passed`

### 7.7 What to defer

Defer until the measurement story is stable:

- LongBench task-aware object schema
- more complex object taxonomies
- self-improving repair agents

The reason is simple:

```text
if we cannot say which component improved which metric, we should not add more components
```

### 7.8 Shared field names

Use the same field names across logs, CSV exports, and paper tables:

- `experiment_id`
- `task_id`
- `date`
- `dataset`
- `model`
- `context_budget`
- `config_summary`
- `ablation`
- `status`
- `result_summary`
- `metric_values`
- `short_conclusion`
- `next_action`

For outcome comparisons, prefer these metric labels:

- `semantic_similarity`
- `validation_coverage`
- `validation_alignment`
- `integrity_gap`
- `semantic_compression_loss`
- `object_retention`
- `weighted_object_retention`
- `lost_important_object_count`
- `structured_state_package_present`
- `recovered_object_count`
- `recovered_object_type_counts`
- `validation_passed`
- `state_committed`
- `repair_attempted`
- `repair_context_flat`
- `coverage_before_repair`
- `coverage_after_repair`
- `critical_failures_before`
- `critical_failures_after`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `compressed_size`
- `compression_ratio`

### 7.9 Experiment ID naming

Use a stable experiment ID format so runs can be sorted and compared at a glance:

```text
srp_<phase>_<task>_<ablation>_<run>
```

Recommended fields:

- `<phase>`: `meas`, `v2`, or `paper`
- `<task>`: short task family or dataset id
- `<ablation>`: short mechanism label such as `textrec`, `structrec`, `objaware`, `repair`, `encoder`
- `<run>`: zero-padded run number such as `r01`, `r02`

Examples:

- `srp_meas_longbench_textrec_r01`
- `srp_meas_longbench_structrec_r02`
- `srp_v2_mcq_objaware_r01`
- `srp_paper_repair_r03`

---

## 9. Recommended Execution Order

1. Object extraction before compression
2. Task-aware object schemas for LongBench-style MCQ
3. Object-conditioned chunk selection
4. State reconstruction in recovery
5. Repair loop after failed validation
6. Semantic retention / integrity-gap metrics
7. Paper-quality ablations and figures
8. Extra evaluator backbones only after the above

The most important rule for this phase is:

```text
do not optimize selector sophistication before fixing state representation granularity
```

---

## 10. One-Sentence Positioning for the Next Phase

The next SRP phase should move from preserving informative text chunks to preserving typed semantic runtime state, because the current LongBench evidence shows that high embedding similarity alone is not enough to preserve benchmark-critical semantics.
