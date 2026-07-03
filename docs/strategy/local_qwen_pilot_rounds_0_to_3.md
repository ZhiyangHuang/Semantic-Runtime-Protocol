# Local Qwen Pilot Rounds 0 to 3

This volume preserves the early local pilot sequence:

- `Run 0: Untuned Local Pilot`
- `Tuning Round 1`
- `Tuning Round 2`
- `Tuning Round 3`

## Results Index

- [local_cycles3/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3/summary.json)
  - `Run 0: Untuned Local Pilot`
- [local_cycles3_tuned1/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned1/summary.json)
  - `Tuning Round 1`
- [local_cycles3_tuned2/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned2/summary.json)
  - `Tuning Round 2`
- [local_cycles3_tuned3/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned3/summary.json)
  - `Tuning Round 3`

## Run 0: Untuned Local Pilot

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3/summary.json)

### Aggregate Results

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.7953` | `1.0000` | `0.8389` | `318.44` |
| `summarization` | `0.7591` | `0.9167` | `0.8944` | `83.00` |
| `rag` | `0.7276` | `0.9167` | `0.8889` | `87.33` |
| `srp` | `0.8438` | `0.7500` | `0.7056` | `106.22` |

### What This Showed

- The real backend worked.
- The shared query flow worked.
- The current SRP implementation did **not** outperform the baselines.
- The untuned SRP path was the weakest method in drift and shared-query success.

### First Diagnosis

At this stage, the most obvious failure mode was not yet "bad theory." It was "bad protocol realization."

Three concrete issues appeared immediately:

1. `Qwen` produced long `<think> ... </think>` style outputs.
2. Those reasoning traces polluted compression, recovery, and query answers.
3. The SRP state tuple existed in code, but the model prompts were not actually using the full state in a meaningful way.

### Audit Note

This run should be treated as the first real local reference point, but not yet as a stable evaluation baseline.

Reasons:

- `Qwen` was still emitting long reasoning traces
- those traces inflated tokens and polluted downstream answers
- the shared environment was not yet normalized for local Qwen behavior

## Tuning Round 1

### Changes Introduced

The first tuning round focused on the largest obvious source of noise.

Files changed:

- [srp_experiment/model_backend.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/model_backend.py)
- [srp_experiment/prompting.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py)
- [srp_experiment/srp/compress.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/compress.py)
- [srp_experiment/srp/recover.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/recover.py)

Main changes:

1. Local `Qwen` requests now inject `/no_think`.
2. Compression prompts now include:
   - memory
   - constraints
   - global vocabulary
   - local vocabulary
   - policy
3. Compression output now prefers a small JSON-like runtime package.
4. Recovery now sees more than a free-form compressed paragraph.

### What Changed Globally vs Locally

Global changes affecting all methods:

- local `Qwen` now runs with `/no_think`
- reasoning traces are reduced
- all methods receive shorter and cleaner model outputs

SRP-only changes:

- compression sees more of the runtime state
- recovery sees more structured state

### Audit Consequence

Because `/no_think` changed the common backend behavior, this round is not only an `srp` change.

That is why `raw_prompt`, `summarization`, and `rag` also changed sharply in:

- token count
- drift
- query behavior

This is expected and should not be interpreted as a measurement error.

### Aggregate Results

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned1/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3715` | `0.9167` | `0.6722` | `94.22` |
| `summarization` | `0.5537` | `0.5833` | `0.4722` | `29.44` |
| `rag` | `0.2125` | `0.9167` | `0.7278` | `35.67` |
| `srp` | `0.7249` | `0.7500` | `0.6944` | `58.44` |

### Improvement Relative to Run 0

For `srp`:

- `mean_drift`: `0.8438 -> 0.7249`
- `mean_task_success`: `0.7500 -> 0.7500`
- `mean_query_success`: `0.7056 -> 0.6944`
- `mean_tokens`: `106.22 -> 58.44`

### Interpretation

This was a meaningful systems improvement, even though it was not yet a paper win.

What improved:

- drift dropped
- tokens dropped sharply
- runtime outputs became shorter and cleaner

What did not improve enough:

- SRP still did not beat `rag`
- query success did not clearly improve

### What This Exposed

The first tuning round revealed a deeper issue:

The SRP prompt path was still leaking protocol language back into the memory itself.

Examples included:

- query verbs like `design`, `summarize`, and `recommend`
- protocol terms like `bounded semantic drift`
- policy wording being written back as if it were task memory

That meant the model was not simply compressing memory. It was rewriting the state in a way that mixed:

- task facts
- runtime instructions
- evaluation wording

This is a strong candidate for a genuine SRP failure boundary.

## Tuning Round 2

### Changes Introduced

The second tuning round addressed protocol leakage more directly.

Files changed:

- [srp_experiment/model_backend.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/model_backend.py)
- [srp_experiment/srp/pipeline.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/pipeline.py)
- [srp_experiment/prompting.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py)

Main changes:

1. `<think> ... </think>` traces are stripped after response extraction.
2. `local_vocabulary` is no longer built from the query list.
3. `local_vocabulary` is now built from:
   - constraints
   - expected keywords
4. Prompts now explicitly say:
   - do not introduce protocol jargon
   - do not introduce query verbs
   - do not write runtime language back into semantic memory unless it is already present

### What Changed Globally vs Locally

Global changes affecting all methods:

- `<think> ... </think>` traces are stripped after response extraction

SRP-only changes:

- `local_vocabulary` source changed
- anti-leakage prompt rules were tightened

### Audit Consequence

This round still changes one shared layer, so some baseline movement remains expected.

However, compared with Round 1, the main new behavior here is much closer to a true SRP-side intervention.

### Aggregate Results

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned2/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3407` | `0.9167` | `0.7278` | `91.44` |
| `summarization` | `0.5265` | `0.5833` | `0.5778` | `25.67` |
| `rag` | `0.1219` | `0.9167` | `0.7833` | `33.67` |
| `srp` | `0.6511` | `0.8778` | `0.5667` | `30.78` |

### Improvement Relative to Round 1

For `srp`:

- `mean_drift`: `0.7249 -> 0.6511`
- `mean_task_success`: `0.7500 -> 0.8778`
- `mean_query_success`: `0.6944 -> 0.5667`
- `mean_tokens`: `58.44 -> 30.78`

### Interpretation

This second tuning round is the first one that clearly improved the SRP path as a state-management system rather than only as an output-cleaning patch.

What improved:

- drift improved again
- task success improved a lot
- tokens dropped again

What got worse:

- `query_success` dropped

This does not automatically mean the system became worse. It more likely means the evaluation proxy is now revealing its own weakness.

The current `query_success` score still uses the whole-task keyword list, not a query-specific answer rubric.

That means:

- semantically correct but shorter answers can be under-scored
- paraphrases can be under-scored
- omission of one expected term can dominate the score

So the current interpretation should be:

- `task_success` and `drift` got better
- `query_success` is now noisy enough that it cannot be treated as a trustworthy ranking metric

## Cross-Run Comparison

### SRP Only

| Run | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `local_cycles3` | `0.8438` | `0.7500` | `0.7056` | `106.22` |
| `local_cycles3_tuned1` | `0.7249` | `0.7500` | `0.6944` | `58.44` |
| `local_cycles3_tuned2` | `0.6511` | `0.8778` | `0.5667` | `30.78` |

### Net Change from Run 0 to Tuning Round 2

For `srp`:

- drift improved by `0.1927`
- task success improved by `0.1278`
- token cost dropped by `75.44`

This is enough to justify saying:

> Prompt and state-design changes materially improved the local SRP implementation, even though the current system still does not outperform `rag` on the toy 3-cycle pilot.

## Tuning Round 3

### Concept-Driven Optimization Ideas

This round was driven by a more explicit semantic interpretation of SRP:

- the semantic state should preserve not only a summary, but also what may be lost during compression
- runtime should preserve constraints separately from free-form memory text
- compressed concepts should be reverse-expanded into user-facing wording during recovery
- evaluation should track whether the answer preserves the intended meaning of each query, not only a single task-level keyword pool

### Changes Introduced

Files changed:

- [srp_experiment/eval/scoring.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/eval/scoring.py)
- [srp_experiment/eval/llm_judge.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/eval/llm_judge.py)
- [srp_experiment/srp/state.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/state.py)
- [srp_experiment/prompting.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py)
- [srp_experiment/srp/compress.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/compress.py)
- [srp_experiment/srp/recover.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/recover.py)
- [srp_experiment/srp/pipeline.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/pipeline.py)
- [srp_experiment/run_experiment.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/run_experiment.py)
- [task_a.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/data/task_a.json)
- [task_b.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/data/task_b.json)
- [task_c.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/data/task_c.json)

Main changes:

1. `SemanticState` now tracks:
   - `constraints`
   - `term_map`
   - `loss_notes`
2. Compression now asks for:
   - `memory_summary`
   - `constraints`
   - `core_concepts`
   - `term_map`
   - `loss_risks`
   - `policy_note`
3. Recovery now uses:
   - explicit constraints
   - explicit loss notes
   - reverse-expansion guidance for compressed concepts
4. `query_success` now uses per-query expectations instead of only a task-level keyword pool.
5. Query expectations now accept grouped alternatives such as:
   - `low-latency / low latency`
   - `minimal / simple / minimal architecture`

### Aggregate Results

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned3/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3407` | `0.9167` | `1.0000` | `91.44` |
| `summarization` | `0.5265` | `0.5833` | `0.8889` | `25.67` |
| `rag` | `0.1219` | `0.9167` | `1.0000` | `33.67` |
| `srp` | `0.8061` | `0.7222` | `0.7222` | `24.78` |

### Important Comparison Note

This round changed the query-scoring function itself.

That means `mean_query_success` in Round 3 is **not directly comparable** to Round 2.

The more reliable cross-round comparisons here are:

- `mean_drift`
- `mean_task_success`
- `mean_tokens`

Less reliable direct comparisons:

- `mean_query_success` between Round 2 and Round 3

Reason:

- the query-level rubric changed
- grouped synonyms were introduced
- each query now has a more specific target meaning

### Interpretation

This round did **not** improve SRP overall.

Relative to Round 2, the SRP path became:

- worse in drift
- worse in task success
- better in token cost

The likely reason is that the new reverse-expansion and loss-tracking instructions made the recovery stage too abstract or too cautious for tiny toy tasks.

In several places, SRP began to answer in a meta way:

- talking about what the memory snapshot does or does not contain
- preserving protocol-style wording about constraints and semantic integrity
- failing to simply restate the concrete memory fact

### What This Exposed

This round exposed another important failure boundary:

### 6. Over-Abstracted Recovery

If SRP is instructed to preserve:

- constraints
- compression losses
- reverse-expansion behavior
- protocol hygiene

all at once, then on small tasks the recovery stage can become too abstract.

Instead of reconstructing the task memory directly, it starts talking about:

- the structure of the memory
- the possibility of missing information
- the runtime policy itself

Practical meaning:

- richer runtime state is not automatically better
- too much recovery-side abstraction can damage short-task fidelity
- the current toy tasks do not reward strong runtime packaging

### Current Best Reading of Round 3

This round is still useful, even though it is a regression.

It shows that:

- the semantic-state design space is real
- richer state packaging changes behavior substantially
- reverse-expansion is a promising long-term idea, but it is easy to over-apply
- the next step should be selective state enrichment, not simply adding more runtime fields
