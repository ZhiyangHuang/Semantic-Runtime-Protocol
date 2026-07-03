# Temporary Table Expansion Plan

## Purpose

This note converts the latest temporary review into a concrete table-expansion plan.

Its job is to help us extend the current experiment tables **step by step** without losing the existing reporting structure.

It is intentionally temporary and operational.
It is not yet the formal paper-facing reporting contract.

## What The Current Tables Already Cover

The current table package already covers a strong first layer:

- `mean_drift`
- `mean_task_success`
- `mean_query_success`
- `mean_tokens`
- `mean_latency_seconds`
- `commit_rate`
- `mean_validation_drift`
- `rollback_count`

This means the current package already captures:

- `Quality`
- `Cost`
- part of `Robustness`

Current generated tables:

- `paper_table`
- `quality_table`
- `efficiency_table`
- `guardrail_table`
- `camera_ready_table`

That is already enough for a strong systems-style first pass.

## Main Gap Identified In The Temporary Note

The main issue is **not** that the current results are weak.

The main issue is that the current reporting layer still under-describes:

- true compression cost
- protocol overhead
- scalability
- memory-update behavior
- retrieval precision
- temporal consistency

The most important warning from the temporary note is this:

> The current SRP token numbers are too optimistic if they do not include the real API-side transmission cost of the SRP package and dictionary-query traffic.

This means the current `mean_tokens` field is still useful, but it may not yet represent the full runtime cost of SRP in a paper-defensible way.

The second temporary review sharpens this further:

> The most important next step is not "more metrics" by itself. It is to separate **System Cost** from **LLM Cost** in a clean and reproducible way.

That is important because a memory system should not only be judged by final answer quality.
It should also be judged by how much protocol work, write work, and retrieval work it imposes on the runtime.

## Cross-Cutting Principle: Separate System Cost From LLM Cost

This should become the main design rule for the next reporting upgrade.

### `LLM Cost`

This refers to token and latency cost caused directly by model-facing calls, such as:

- prompt transmission
- completion generation
- recovery generation
- any dictionary-query model call

### `System Cost`

This refers to the broader runtime machinery needed to operate the memory system, such as:

- package construction
- memory write orchestration
- retrieval orchestration
- validation and commit logic
- additional protocol-side compute or call structure

Why this distinction matters:

- it makes SRP cost claims more honest
- it explains why token-light methods can still be slower
- it matches the way current memory-system work increasingly reports tradeoffs

Practical implication:

- future cost reporting should not rely on one undifferentiated token column
- the next table layer should show both model-facing cost and protocol-facing cost

## Recommended Reporting Upgrade Strategy

To keep the rollout safe, the reporting upgrade should happen in phases.

### Phase 0: Keep The Current Core Tables

Do not remove the current core fields:

- `mean_drift`
- `mean_task_success`
- `mean_query_success`
- `mean_tokens`
- `mean_latency_seconds`

These are already readable and useful.

Instead of replacing them immediately, add better companion metrics.

### Phase 1: Expand Efficiency Reporting

These are the most important next fields to add.

#### 1. `compression_ratio`

Definition:

- `compression_ratio = baseline_reference_tokens / effective_runtime_tokens`

Or equivalently:

- `token_reduction_rate = 1 - effective_runtime_tokens / baseline_reference_tokens`

Why it matters:

- reviewers understand it immediately
- it translates SRP into a compression story
- it is easier to interpret than raw token numbers alone

Recommended table placement:

- add to `efficiency_table`
- optionally add to `camera_ready_table`

#### 2. `effective_runtime_tokens`

Definition:

- total transmitted tokens actually consumed by the runtime path

For SRP this should include, when applicable:

- compression prompt tokens
- recovery prompt tokens
- SRP package transmission tokens
- dictionary query tokens
- any additional protocol-side API traffic

Why it matters:

- current `mean_tokens` is likely undercounting SRP overhead
- this is the cleanest way to answer the "SRP looks tiny only because protocol traffic is hidden" concern

Recommended table placement:

- add as a new efficiency metric
- do **not** silently overwrite the old `mean_tokens`

Safer approach:

- keep `mean_tokens`
- add `effective_runtime_tokens`
- explain the difference clearly

Recommended interpretation:

- `mean_tokens` stays as the legacy compact metric
- `effective_runtime_tokens` becomes the paper-defensible runtime-cost metric

#### 3. `protocol_overhead_tokens`

Definition:

- `effective_runtime_tokens - final_memory_tokens`

or more explicitly:

- tokens spent on protocol machinery rather than only the surviving memory state

Why it matters:

- this isolates the SRP control cost
- it explains why SRP can show low final memory size but non-trivial latency

Recommended table placement:

- add to `efficiency_table`
- possibly add a dedicated protocol-cost table later

#### 4. `memory_write_tokens`

Definition:

- tokens spent when the system writes or rewrites memory state

For SRP this may include:

- compression-side write traffic
- package serialization traffic
- memory update traffic

Why it matters:

- SRP's main novelty is not only in retrieval
- it is also in how memory gets written, compressed, and retained

Recommended table placement:

- future `protocol_cost_table`
- optionally `efficiency_table` if the width stays manageable

### New Cost Split Recommendation

The efficiency layer should eventually be partitioned into:

- `LLM generation cost`
- `protocol overhead cost`
- `memory write cost`
- `retrieval cost`

That gives a cleaner picture than one single token total.

### Phase 2: Expand Latency Reporting

The temporary note correctly points out that total latency alone is not enough.

#### 4. `protocol_latency_seconds`

Definition:

- latency spent on compression / packaging / dictionary / recovery orchestration

#### 5. `model_latency_seconds`

Definition:

- latency attributable to the actual model call path

#### 6. `retrieval_latency_seconds`

Definition:

- latency attributable to retrieval or lookup

Why this split matters:

- reviewers will otherwise ask why SRP has lower token cost but higher latency
- this helps show whether the cost comes from generation or from protocol structure

Recommended table placement:

- keep `mean_latency_seconds` in the main tables
- add the breakdown to a new extension table

Recommended future table:

- `latency_breakdown_table`

#### 7. `memory_write_latency_seconds`

Definition:

- latency spent updating or rewriting the stored memory representation

Why it matters:

- memory systems are not only read-time systems
- write-time overhead is one of the biggest hidden costs in protocol-heavy approaches

Recommended table placement:

- `latency_breakdown_table`
- or a future `write_cost_table`

### Phase 3: Expand Robustness / State-Control Reporting

The current `guardrail_table` is a good start, but it can be stronger.

#### 8. `state_consistency_score`

Definition:

- a metric for whether the retained memory state remains internally consistent across cycles

Possible operational proxy:

- contradiction rate
- anchor agreement rate
- overwrite correctness under updates

Why it matters:

- this aligns closely with SRP's protocol claim
- it is more semantically meaningful than rollback count alone

Recommended table placement:

- future `guardrail_table`
- or a dedicated `state_table`

#### 9. `guardrail_trigger_rate`

Definition:

- fraction of cycles where a guardrail check failed before commit

Why it matters:

- easier to interpret than only raw rollback count across different cycle lengths

Recommended table placement:

- `guardrail_table`

### Phase 4: Expand Scalability Reporting

The temporary note is right that `3 / 5 / 7` cycles are still short-horizon.

#### 10. Longer cycle groups

Recommended future cycle settings:

- `10`
- `20`
- `50`
- `100`

Potential later extension:

- `200`

Why it matters:

- this is where long-term memory methods separate
- raw prompt saturation becomes much more meaningful
- SRP stability claims become easier to defend

Recommended table handling:

- keep the current short-cycle tables
- add separate long-horizon tables rather than mixing everything into one huge main table

Suggested naming:

- `long_horizon_quality_table`
- `long_horizon_efficiency_table`

#### 11. `memory_size_growth`

Definition:

- how the retained memory representation grows as cycle count increases

Possible forms:

- raw memory token count by cycle
- compressed memory token count by cycle
- cumulative stored memory size

Why it matters:

- reviewers intuitively expect memory to grow over time
- if SRP remains flat while baselines grow, that is visually and scientifically strong
- this is one of the easiest figures to understand

Recommended output:

- a curve rather than only a scalar table entry

Suggested future artifact:

- `memory_growth_table`
- `memory_growth_plot`

### Phase 5: Expand Memory Benchmark Coverage

These metrics should likely come after the token and latency fixes.

#### 12. `update_accuracy`

Definition:

- whether the system correctly overwrites outdated facts with newer user facts

Why it matters:

- many memory benchmarks now care about preference updates and correction behavior

#### 13. `temporal_memory_accuracy`

Definition:

- whether the system tracks time-sensitive memory correctly

Examples:

- current location vs previous location
- old belief vs updated belief

#### 14. `retrieval_precision`

Definition:

- whether the system retrieves only the relevant memory rather than dumping everything

Why it matters:

- retrieval recall alone can hide noisy memory behavior
- this is especially important for comparing `rag` and hybrid systems

## Which Fields Should Change The Existing Tables

### Keep In The Main `paper_table`

Keep these in the main table:

- `mean_drift`
- `mean_task_success`
- `mean_tokens`
- `mean_latency_seconds`

Optional later upgrade:

- replace `mean_tokens` with `effective_runtime_tokens`

But only after we are confident the measurement is stable.

### Add To `efficiency_table`

Best near-term expansion candidates:

- `effective_runtime_tokens`
- `compression_ratio`
- `protocol_overhead_tokens`

Second-wave additions if width permits:

- `memory_write_tokens`
- `memory_write_latency_seconds`

### Add To `guardrail_table`

Best near-term expansion candidates:

- `guardrail_trigger_rate`
- `commit_rate`
- `mean_validation_drift`
- `rollback_count`

### Add As New Tables

Best candidates for separate extension tables:

- `latency_breakdown_table`
- `protocol_cost_table`
- `write_cost_table`
- `state_consistency_table`
- `long_horizon_table`
- `update_temporal_table`

## Recommended Immediate Next Steps

The most practical order is:

1. add real SRP-side transmitted-token accounting
2. add `effective_runtime_tokens`
3. add `compression_ratio`
4. split `System Cost` from `LLM Cost`
5. add latency breakdown fields
6. add `memory_write_tokens` and `memory_write_latency_seconds`
7. extend `guardrail_table` with trigger-rate style reporting
8. only after that, start longer-cycle and update/temporal experiments

## Reviewer-Oriented Priority Stack

The second temporary review suggests a useful reviewer-facing priority order.

### `P0` Must Have

- `effective_runtime_tokens`
- `compression_ratio`
- `latency_breakdown`

### `P1` Strongly Recommended

- `50+` cycle long-horizon runs
- `update_accuracy`
- `temporal_memory_accuracy`

### `P2` Bonus / Differentiation Layer

- `state_consistency_score`
- `retrieval_precision`
- `memory_size_growth`

This is a better framing than treating every future metric as equally urgent.

## Concrete Temporary Worklist

### Temporary Step A

Add instrumentation fields into detailed `results.json`:

- `prompt_tokens_total`
- `completion_tokens_total`
- `effective_runtime_tokens`
- `protocol_overhead_tokens`
- `dictionary_query_tokens`
- `package_tokens`
- `memory_write_tokens`
- `memory_write_latency_seconds`
- `retrieval_latency_seconds`
- `model_latency_seconds`
- `protocol_latency_seconds`

And explicitly tag which costs belong to:

- `llm_cost`
- `system_cost`

### Temporary Step B

Aggregate them into `batch_summary_table`:

- `mean_effective_runtime_tokens`
- `mean_protocol_overhead_tokens`
- `mean_dictionary_query_tokens`
- `mean_package_tokens`
- `mean_memory_write_tokens`
- `mean_memory_write_latency_seconds`
- `mean_retrieval_latency_seconds`
- `mean_model_latency_seconds`
- `mean_protocol_latency_seconds`

### Temporary Step C

Upgrade the formatter:

- extend `efficiency_table`
- add `protocol_cost_table`
- add `latency_breakdown_table`

### Temporary Step D

Run one small comparison pass first:

- methods:
  - `rag`
  - `srp`
  - `rag_srp_v2`
- cycles:
  - `3`
  - `5`
  - `7`

Reason:

- this is the smallest comparison where the protocol-cost story matters most

### Temporary Step E

After the instrumentation is stable, add one long-horizon check:

- methods:
  - `raw_prompt`
  - `rag`
  - `srp`
- cycles:
  - `10`
  - `20`

Reason:

- this is the lowest-cost way to test whether the new table fields stay informative beyond short horizons

## Current Recommendation

The best next reporting upgrade is **not** to replace the current quality metrics.

It is to make SRP cost accounting more honest and more explicit.

So the next table-expansion priority should be:

1. `effective_runtime_tokens`
2. `compression_ratio`
3. `System Cost` vs `LLM Cost` split
4. latency breakdown
5. write cost

That will make the current result package much easier to defend.

## Implementation Status Note

The prompt/completion/query/judge token breakdown requested in this plan has now been implemented as:

- `token_breakdown_table.md`
- `token_breakdown_table.tex`

This keeps the document aligned with the current codebase and separates the new breakdown view from the main efficiency table so the main paper tables stay readable.
