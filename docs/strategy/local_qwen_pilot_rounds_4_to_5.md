# Local Qwen Pilot Rounds 4 to 5

This volume preserves the transition from the rollback-and-refocus SRP line into the exploratory hybrid checks:

- `Tuning Round 4`
- `Exploratory Round 5`

## Results Index

- [local_cycles5_tuned4/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles5_tuned4/summary.json)
  - `Tuning Round 4`
- [local_cycles7_tuned4/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles7_tuned4/summary.json)
  - `Tuning Round 4 Extension: 7-Cycle Check`
- [local_cycles5_rag_srp/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp/summary.json)
  - `Exploratory Round 5A: rag_srp`
- [local_cycles5_rag_srp_anchor/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp_anchor/summary.json)
  - `Exploratory Round 5B: rag_srp_anchor`

## Tuning Round 4

### Goal

Round 4 was designed as a rollback-and-refocus step.

Instead of adding more state fields, this round asked a narrower question:

> What happens if we keep the cleaner common evaluation stack, but simplify SRP recovery back toward the more direct behavior seen in Round 2?

This made Round 4 a useful test of whether the Round 3 regression came from:

- the shared scoring layer
- or the SRP recovery design itself

### Changes Introduced

Files changed:

- [srp_experiment/prompting.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py)
- [srp_experiment/srp/pipeline.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/pipeline.py)
- [srp_experiment/srp/recover.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/recover.py)
- [srp_experiment/baselines/raw_prompt.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/raw_prompt.py)

Main SRP-side changes:

1. Recovery was simplified back toward direct task-memory reconstruction.
2. Reverse-expansion emphasis was removed from the recovery instructions.
3. `loss_notes` were effectively disabled for the tuned run.
4. The policy wording was rewritten to prefer direct recovery over meta commentary.
5. Recovery output length was reduced further.

Main baseline-side change:

6. `raw_prompt` received a window-clipped fallback for long runs so the baseline could continue past the local `1024` token limit.

### Why the Raw Prompt Baseline Changed

At `5` cycles, the unbounded `raw_prompt` baseline hit the local model context ceiling.

The first `5`-cycle attempt failed with:

- maximum context length exceeded
- prompt + completion budget above `1024` tokens

To keep the pilot runnable, `raw_prompt` was updated to use a simple tail-window clipping rule in later cycles.

This does make the `5`-cycle raw-prompt run a different baseline than the unconstrained earlier one, so it should be interpreted as:

- a practical window-limited raw prompt baseline

rather than:

- a purely unconstrained prompt accumulation baseline

That is still useful for the paper, because once local context limits are real, a "raw prompt forever" baseline is no longer operationally meaningful.

### Aggregate Results

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles5_tuned4/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3541` | `0.9167` | `1.0000` | `150.27` |
| `summarization` | `0.5558` | `0.5833` | `0.8667` | `25.27` |
| `rag` | `0.1219` | `0.9167` | `1.0000` | `33.67` |
| `srp` | `0.6474` | `0.9567` | `0.8222` | `25.93` |

### Comparison Against Round 2

Round 2 remains the best `3`-cycle SRP reference under the current shared evaluation stack.

Compared with `local_cycles3_tuned2`, the new `5`-cycle `srp` run shows:

- `mean_drift`: `0.6511 -> 0.6474`
- `mean_task_success`: `0.8778 -> 0.9567`
- `mean_query_success`: `0.5667 -> 0.8222`
- `mean_tokens`: `30.78 -> 25.93`

### Interpretation

Round 4 is the strongest SRP result so far under the current local pilot setup.

It suggests that:

- the Round 3 regression was largely caused by over-abstracted recovery
- a lighter recovery strategy is better for short-memory tasks
- SRP can improve substantially once the recovery path is forced to stay concrete

This does **not** mean SRP is now the strongest overall method.

`rag` still remains the strongest method on:

- drift
- query success

However, Round 4 moves SRP into a more credible position:

- it is close to summarization in token cost
- it is stronger than summarization in task success
- it is much more stable than the over-abstracted Round 3 SRP

### New Practical Boundary Revealed

Round 4 also reveals a practical experimental boundary:

### 7. Long-Cycle Raw Prompt Saturation

At longer cycle counts, a real local model with a finite context window forces the raw-prompt baseline to change form.

In this pilot, once the baseline exceeded the local `1024` token budget, it had to become:

- a window-clipped raw prompt baseline

Practical meaning:

- long-horizon experiments need operationally realistic baselines
- prompt accumulation is not an unlimited baseline in practice
- context-budget pressure is itself part of the runtime comparison story

### Current Best Reading of Round 4

Round 4 is the first local pilot result that makes the SRP path look experimentally credible again after the Round 3 regression.

The most accurate reading is:

- SRP still does not beat `rag` on this toy benchmark
- SRP does become more competitive when the recovery path stays concrete
- `5` cycles is already a better diagnostic regime than `3` cycles for this setup
- longer-horizon results are starting to expose realistic baseline constraints rather than only toy behavior

For the first paper, this round is valuable because it supports a more nuanced claim:

> Under a real local backend, SRP behavior improves when protocol leakage is reduced and recovery remains concrete, but the strongest retrieval baseline still outperforms it on the current toy task suite.

### Round 4 Extension: 7-Cycle Check

To test whether the same lighter-recovery design remains stable under a longer interaction horizon, the frozen public layer and the Round 4 SRP path were run again at `7` cycles.

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles7_tuned4/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3598` | `0.9286` | `1.0000` | `181.10` |
| `summarization` | `0.5745` | `0.5833` | `0.8730` | `24.81` |
| `rag` | `0.1601` | `0.9167` | `1.0000` | `35.24` |
| `srp` | `0.6902` | `0.9310` | `0.8095` | `27.24` |

### What the 7-Cycle Extension Shows

The main question for this extension was not whether SRP becomes the best overall method. The question was narrower:

> Does SRP continue to preserve more task behavior than plain summarization when the interaction horizon grows longer?

The answer on the current toy setup is **yes**.

Compared with `summarization`, the `7`-cycle SRP run remains:

- much stronger in `mean_task_success`
- slightly higher in token cost
- worse in drift

In direct numbers:

- `summarization mean_task_success = 0.5833`
- `srp mean_task_success = 0.9310`

This makes the Round 4 extension valuable even though SRP still does not beat `rag` on drift.

### Interpretation of the 7-Cycle Extension

The most accurate reading is:

- the lighter tuned4 recovery design continues to hold up better than summarization on task retention
- the task-success advantage does not collapse at `7` cycles
- SRP still pays a drift penalty relative to both `rag` and `summarization`
- the current local toy regime is starting to separate "task preservation" from "lowest drift"

For the first paper, this is useful because it supports a more specific pilot claim:

> Under a real local backend and a frozen common evaluation layer, tuned SRP remains more competitive than plain summarization on task preservation at longer cycle counts, even though retrieval-based memory remains the strongest drift baseline on the current toy suite.

### Audit Note: Why the Baselines Also Rose in Round 3

A likely audit question is:

> If Round 3 was an SRP-inspired redesign, why did `raw_prompt`, `summarization`, and `rag` also improve in `query_success`?

The answer is that the baseline rise in Round 3 is best explained by **shared evaluation changes**, not by direct access to the SRP state object.

What did **not** happen:

- the baselines did not start using `SemanticState`
- the baselines did not directly read `term_map`
- the baselines did not directly use `loss_notes`
- the baselines did not inherit the SRP compression or recovery pipeline

What **did** happen:

- the shared scoring function changed
- query-specific expectations were introduced
- grouped synonyms were allowed
- query evaluation became closer to the intended semantic target of each question

This matters because the earlier scoring layer often under-scored baseline answers that were semantically acceptable but did not literally match the older task-level keyword pool.

Examples:

- `simple` can satisfy a `minimal` expectation
- `low latency` can satisfy a `low-latency` expectation
- a direct answer to a specific query can be correct even if it does not mention every task-level keyword

So the most accurate reading is:

- Round 3 made the evaluation layer more semantically aligned
- that change benefited all methods
- SRP did **not** benefit in the same way because it simultaneously absorbed a more complex recovery design that hurt short-task fidelity

Therefore, the baseline rise in Round 3 should not be interpreted as:

- SRP leaking its internal dictionary into other methods

It should be interpreted as:

- a common scoring-layer improvement that made baseline answers easier to recognize as correct

## Why the Three Tables Differ

This section directly answers a likely audit question:

> Why are the tables for `raw_prompt`, `summarization`, and `rag` also changing across rounds?

The answer is:

### 1. Shared Backend Changes

The early rounds changed the local Qwen inference behavior through:

- `/no_think`
- postprocessing that strips `<think> ... </think>`

Since all four methods use the same local backend client, these changes affect:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`

So baseline shifts across rounds are expected.

### 2. Shared Scoring Changes

Later rounds changed:

- the scoring function
- the query expectation format
- the query-level rubric

That means later `query_success` values are partly measuring a new scoring definition.

So a higher or lower `query_success` does not always mean the model itself improved or regressed by the same amount.

### 3. SRP-Only Changes

Only some changes were truly isolated to the SRP path:

- state fields
- compression structure
- recovery logic
- anti-leakage rules
- reverse-expansion guidance

These are the changes that should be used when we want to study "what SRP itself did."

### 4. Not Primarily a KV-Cache Story

The table shifts are unlikely to be driven mainly by `kv cache` behavior.

`kv cache` can affect:

- throughput
- warmup latency
- stability at the serving layer

But it does not explain the large structural changes observed here, such as:

- very large token drops after `/no_think`
- disappearance of reasoning traces
- large query-scoring changes after the rubric changed
- protocol-language leakage and recovery behavior changes inside SRP

So for current audit purposes, the main explanation is:

- shared backend changes
- shared scoring changes
- SRP-side prompt/state changes

not `kv cache`.

## Trustworthiness Guidance

To improve later credibility and reuse of these pilot results, the following audit rules should be followed.

### Safe Claims

The current log safely supports these claims:

- the real local experiment pipeline works
- shared-query flow works on a real backend
- SRP behavior is sensitive to prompt and state design
- protocol leakage and over-abstracted recovery are real failure boundaries
- low-cycle toy tasks are not a favorable regime for showing strong SRP gains

### Unsafe Claims

The current log should **not** yet be used to claim:

- a stable paper-level ranking between all four methods across all rounds
- exact cross-round superiority based on `query_success` alone
- strong SRP gains over `rag`
- benchmark-level conclusions beyond these toy tasks

### Best Audit Use

The most trustworthy use of these tables is:

- as a tuning history
- as a failure-boundary record
- as a reference for deciding what to freeze before later experiments

They are stronger as engineering and methodological evidence than as final paper evidence.

## What Should Be Frozen Next

If later comparisons are meant to be more trustworthy, then the next stage should freeze the common layers:

- local backend behavior
- output postprocessing
- scoring function
- query expectation format
- toy task definitions

After that, only `srp/` should change between rounds.

That would make future tables much easier to compare and much easier to defend in review.

## Freeze Decision

The project now formally adopts that freeze.

From this point forward, the intended rule is:

- keep the public evaluation layer fixed
- treat later SRP changes as `srp/`-side changes by default
- only reopen the common layer if a deliberate new baseline generation is being created

The frozen common layer includes:

- local backend behavior
- output postprocessing
- scoring function
- query expectation format
- toy task definitions

This freeze matters because it turns later tables into cleaner SRP-side comparisons instead of mixed changes across:

- backend behavior
- scoring behavior
- state design

## Exploratory Hybrid Check: `rag_srp`

After freezing the public evaluation layer, an exploratory hybrid path was added to test a narrower systems question:

> If retrieval first selects task-relevant evidence, does a lightweight SRP-style compression and recovery loop improve the resulting runtime behavior?

This hybrid was intentionally kept **outside** the main paper comparison. Its job is exploratory diagnosis, not headline benchmarking.

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp/summary.json)

### Aggregate Results

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `rag_srp` | `0.6983` | `1.0000` | `0.7333` | `28.33` |

### Why This Result Matters

This hybrid is useful because it exposed a clear tradeoff:

- task preservation became extremely strong
- drift fidelity became worse than plain `rag`

The most accurate reading is:

- retrieval supplied a very strong task-relevant evidence set
- the later SRP-style rewrite preserved the right keywords and constraints
- but the same rewrite also pulled the recovered text farther away from the original memory

This means `rag_srp` behaved less like:

- low-drift retrieval

and more like:

- retrieval-guided task rewriting

### Why `task_success` Stayed at `1.0`

The toy tasks use a relatively compact task-keyword space, so once retrieval grabs the important evidence, the later SRP-style reconstruction can continue to preserve:

- user preferences
- core concepts
- explicit constraints

As a result, the method keeps matching the task-success rubric very well.

### Why Drift Became Worse

The same reconstruction step often expands the retrieved evidence into:

- longer explanatory wording
- more design-like or policy-like sentences
- paraphrased concept descriptions

This helps the method answer the task, but it makes the recovered text less faithful to the original memory wording and structure. That is why drift worsens even while task success stays high.

### Audit Reading

This result should not be read as:

- retrieval plus SRP is automatically better

It should be read as:

- retrieval-guided SRP can improve task retention while damaging fidelity to the original memory

That makes `rag_srp` a useful future-extension direction, but not a good candidate for the first paper's main comparison.

## Exploratory Hybrid Check: `rag_srp_anchor`

The next exploratory step tested a minimal anchor design.

The goal was to keep the same retrieval-guided SRP idea, but to preserve one stable semantic anchor so that later compression and rewriting would act on a working memory rather than continuously overwriting the only memory trace.

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp_anchor/summary.json)

### Aggregate Results

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `rag_srp_anchor` | `0.5608` | `1.0000` | `0.9333` | `27.87` |

### Direct Comparison Against `rag_srp`

Compared with the earlier hybrid:

- `mean_drift`: `0.6983 -> 0.5608`
- `mean_task_success`: `1.0000 -> 1.0000`
- `mean_query_success`: `0.7333 -> 0.9333`
- `mean_tokens`: `28.33 -> 27.87`

### Interpretation

This is the clearest evidence so far that a stable semantic anchor helps the hybrid path.

The anchor version:

- keeps the strong task-retention behavior of `rag_srp`
- reduces the amount of uncontrolled semantic rewriting
- improves query behavior
- slightly reduces token cost

It still does **not** beat plain `rag` on drift, so it should remain exploratory.

However, it is much more balanced than the non-anchor hybrid, which makes the anchor idea itself worth preserving as a real design insight rather than a one-off prompt trick.

### What Can Be Safely Encapsulated Now

The following conclusions are now stable enough to preserve as reusable pilot findings:

- a frozen common evaluation layer makes later SRP-side comparisons easier to defend
- protocol leakage and over-abstracted recovery are real failure boundaries
- a lighter recovery path improves SRP relative to the over-abstracted Round 3 design
- longer-cycle pilots (`5` and `7`) are more informative than the original `3`-cycle smoke tests
- retrieval-guided SRP without an anchor tends to preserve tasks while worsening drift
- adding a stable anchor improves the hybrid balance materially

These points are strong enough to reuse later in:

- paper limitations
- failure-boundary discussion
- future-work framing
- advisor-facing progress summaries

## Round 5 Numbering Note

To avoid later confusion, the project now treats the stage between `Tuning Round 4` and `Tuning Round 6` as:

- `Exploratory Round 5`

This round did **not** produce a separate `local_cycles5_tuned5` or `local_cycles7_tuned5` main-line SRP result.

Instead, it produced two exploratory hybrid checks:

- `rag_srp`
- `rag_srp_anchor`

These runs are still part of the preserved pilot record and should not be treated as missing data.

## Exploratory Round 5

### Scope

Exploratory Round 5 was not a new main-line SRP tuning pass.

Its purpose was narrower:

- test retrieval-guided SRP as a hybrid path
- test whether a stable semantic anchor improves that hybrid
- preserve those results as exploratory evidence without moving them into the main paper comparison

### Exploratory Round 5A: `rag_srp`

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `rag_srp` | `0.6983` | `1.0000` | `0.7333` | `28.33` |

### Exploratory Round 5B: `rag_srp_anchor`

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp_anchor/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `rag_srp_anchor` | `0.5608` | `1.0000` | `0.9333` | `27.87` |

### Exploratory Round 5 Reading

The two preserved Round 5 tables show a clear intermediate design lesson:

- retrieval-guided SRP without an anchor preserved task behavior strongly but worsened drift
- adding a stable anchor preserved `task_success = 1.0` while improving both drift and query behavior

This means Exploratory Round 5 should be read as:

- a bridge between the lighter main-line `tuned4` recovery and the later anchor-guided `tuned6` SRP line

rather than:

- a missing or deleted formal tuning round
