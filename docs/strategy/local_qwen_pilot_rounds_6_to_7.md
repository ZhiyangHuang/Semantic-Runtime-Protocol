# Local Qwen Pilot Rounds 6 to 7

This volume preserves the later anchor-guided SRP line and the same-protocol Round 7 rerun:

- `Tuning Round 6`
- `Tuning Round 7`
- later synthesis sections derived from those runs

## Results Index

- [local_cycles5_tuned6/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles5_tuned6/summary.json)
  - `Tuning Round 6: 5 Cycles`
- [local_cycles7_tuned6/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles7_tuned6/summary.json)
  - `Tuning Round 6: 7 Cycles`
- [local_cycles7_tuned7_compare/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles7_tuned7_compare/summary.json)
  - `Tuning Round 7: same-protocol 7-cycle comparison`

## Tuning Round 6

### Goal

Round 6 converted the anchor idea from the exploratory hybrid into the main SRP path, while keeping the frozen public evaluation layer unchanged.

The narrow question for this round was:

> If SRP recovery is explicitly aligned to a stable anchor memory, can the main SRP method reduce drift without giving up the stronger task-preservation behavior that appeared in the later tuned pilots?

### Changes Introduced

Files changed:

- [srp_experiment/prompting.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py)
- [srp_experiment/srp/recover.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/recover.py)
- [srp_experiment/srp/pipeline.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/pipeline.py)

Main SRP-side changes:

1. Recovery now accepts a stable `anchor_memory`.
2. Recovery prompts explicitly prefer alignment to the anchor over unsupported elaboration.
3. The SRP policy now frames recovery as anchor-guided rather than only compact-state-guided.
4. Validation is performed against the anchor memory rather than only the immediately previous working memory.

### Aggregate Results: 5 Cycles

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles5_tuned6/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3541` | `0.9167` | `1.0000` | `150.27` |
| `summarization` | `0.5590` | `0.5833` | `0.8444` | `25.27` |
| `rag` | `0.1219` | `0.9167` | `1.0000` | `33.67` |
| `srp` | `0.4169` | `0.9500` | `0.7778` | `27.33` |

### Direct Comparison Against Round 4 at 5 Cycles

Compared with `local_cycles5_tuned4`, the new `5`-cycle `srp` run shows:

- `mean_drift`: `0.6474 -> 0.4169`
- `mean_task_success`: `0.9567 -> 0.9500`
- `mean_query_success`: `0.8222 -> 0.7778`
- `mean_tokens`: `25.93 -> 27.33`

### Interpretation: 5 Cycles

This is a strong tradeoff improvement for the main SRP path.

The anchor-guided SRP:

- greatly reduces drift relative to Round 4
- keeps task success almost unchanged
- remains low-token

At `5` cycles, this also means SRP now looks more balanced relative to plain summarization:

- lower drift than `summarization`
- much higher task success than `summarization`

### Aggregate Results: 7 Cycles

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles7_tuned6/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens |
| --- | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3598` | `0.9286` | `1.0000` | `181.10` |
| `summarization` | `0.5724` | `0.5833` | `0.9048` | `24.81` |
| `rag` | `0.1601` | `0.9167` | `1.0000` | `35.24` |
| `srp` | `0.4081` | `0.9167` | `0.8254` | `29.00` |

### Direct Comparison Against Round 4 at 7 Cycles

Compared with `local_cycles7_tuned4`, the new `7`-cycle `srp` run shows:

- `mean_drift`: `0.6902 -> 0.4081`
- `mean_task_success`: `0.9310 -> 0.9167`
- `mean_query_success`: `0.8095 -> 0.8254`
- `mean_tokens`: `27.24 -> 29.00`

### Interpretation: 7 Cycles

The same pattern remains visible at the longer horizon:

- SRP drift improves substantially
- task success remains high
- query behavior slightly improves
- token cost rises only slightly

This makes Round 6 the strongest evidence so far that anchor-guided recovery is a real improvement to the main SRP line rather than only a hybrid-side trick.

### Current Best Reading of Round 6

The most accurate reading is:

- anchor-guided recovery is the most effective minimal SRP-side change tested so far
- it improves the balance between drift and task preservation
- it does not make SRP beat `rag` on drift
- it does make SRP look more defensible as a runtime method than the earlier tuned pilots

For the first paper, Round 6 is valuable because it supports a stronger but still honest pilot claim:

> Under a frozen local evaluation layer, anchor-guided SRP recovery substantially improves drift while keeping task preservation high, making the main SRP path more balanced than earlier tuned versions, even though retrieval-based memory remains the strongest drift baseline on the current toy suite.

## Tuning Round 7

### Goal

Round 7 was designed as a same-protocol comparison round under the current frozen local evaluation setup.

The main goal was not to introduce a new public-layer change. It was to test whether a narrower SRP compression schema and a more literal anchor-guided recovery path would improve the balance between:

- drift fidelity
- task preservation
- token efficiency

A second goal was to rerun the main baselines and the exploratory `rag_srp` hybrid under the **same current code path** at `7` cycles, so that the resulting table would be cleaner than earlier cross-round comparisons.

### Changes Introduced

Files changed:

- [srp_experiment/prompting.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py)
- [srp_experiment/srp/compress.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/compress.py)
- [srp_experiment/srp/pipeline.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/pipeline.py)
- [srp_experiment/run_experiment.py](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/run_experiment.py)

Main SRP-side changes:

1. Compression was narrowed to a smaller runtime package.
2. The compression prompt now prefers a compact schema centered on:
   - `memory_summary`
   - `constraints`
   - `anchor_terms`
3. Recovery was rewritten to prefer the closest supported wording from the stable anchor memory.
4. Recovery was explicitly told to avoid unsupported elaboration and unnecessary paraphrase.
5. Successful SRP commits no longer absorb arbitrary new wording from recovered text back into the vocabulary update path.

Evaluation-side consistency fix:

6. Final scoring now prefers `committed_memory` when available, so a rolled-back SRP cycle is evaluated against the memory state that was actually retained rather than an uncommitted failed reconstruction.

### Aggregate Results: 7 Cycles

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles7_tuned7_compare/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens | Mean Latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `raw_prompt` | `0.3598` | `0.9286` | `1.0000` | `181.10` | `0.2871` |
| `summarization` | `0.5745` | `0.5833` | `0.8730` | `24.81` | `0.2687` |
| `rag` | `0.1601` | `0.9167` | `1.0000` | `35.24` | `0.3508` |
| `srp` | `0.1723` | `0.9167` | `0.9683` | `19.33` | `0.7934` |
| `rag_srp` | `0.5316` | `0.5667` | `0.7143` | `19.38` | `1.1419` |

### Direct Comparison Against Round 6 SRP at 7 Cycles

Compared with `local_cycles7_tuned6`, the new `7`-cycle `srp` run shows:

- `mean_drift`: `0.4081 -> 0.1723`
- `mean_task_success`: `0.9167 -> 0.9167`
- `mean_query_success`: `0.8254 -> 0.9683`
- `mean_tokens`: `29.00 -> 19.33`

### Interpretation

Round 7 is the strongest main-line SRP result so far on the current local toy suite.

The most important pattern is:

- SRP drift improved sharply
- task success stayed high
- query success improved strongly
- token cost dropped further

Under this same-protocol comparison, SRP is now very close to `rag` on drift while using fewer tokens.

This does **not** mean SRP becomes the strongest overall drift baseline.

`rag` still remains slightly better on `mean_drift` and still reaches perfect `mean_query_success`.

However, Round 7 makes the main SRP path look substantially more balanced than in earlier tuned rounds:

- much lower drift than `raw_prompt`
- much higher task success than `summarization`
- lower token cost than both `summarization` and `rag`
- far better overall balance than the current `rag_srp` hybrid

### What This Suggests

The clearest reading of Round 7 is that the recent SRP gains did **not** come from adding more semantic packaging.

They came from making the system more conservative.

In particular:

- a narrower compression schema appears better than a richer one
- anchor-guided recovery works better when it stays literal
- preventing rewritten recovery wording from feeding back into the next cycle helps control drift

This is consistent with the earlier failure-boundary evidence from Round 3.

The current toy regime appears to reward:

- concrete reconstruction
- lexical stability
- minimal unsupported rewriting

more than:

- richer conceptual packaging
- aggressive reverse-expansion
- expressive semantic rewording

### Comparison Note

This Round 7 table is cleaner than many earlier cross-round tables because all methods were rerun under the **same current code path** at `7` cycles.

However, one caution still matters:

- this round includes an evaluation consistency fix in `run_experiment.py` so that SRP is scored against `committed_memory` when rollback occurs

That change is reasonable and more faithful to actual retained state, but it means Round 7 should still be read as:

- a cleaner current-code comparison round

rather than:

- a perfectly SRP-only isolated intervention

### Current Best Reading of Round 7

The most accurate current claim is:

> Under the current frozen local evaluation setup, a narrower compression schema and more literal anchor-guided recovery substantially improve the main SRP path, bringing SRP close to retrieval-based memory on drift while keeping high task preservation and the lowest token cost among the non-trivial memory methods.

### Round 7 Compatibility Check: Legacy `rag_srp_anchor`

To test whether the exploratory hybrid line was still compatible with the newer Round 7 SRP runtime, the current `rag_srp_anchor` baseline was rerun separately at `7` cycles without changing its legacy implementation.

Output folder:

- [summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles7_rag_srp_anchor_check/summary.json)

| Method | Mean Drift | Mean Task Success | Mean Query Success | Mean Tokens | Mean Latency (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| `rag_srp_anchor` | `0.3979` | `0.9429` | `0.8095` | `23.43` | `1.4553` |

### Why This Check Matters

This check showed that the legacy `rag_srp_anchor` path still produces competitive-looking outputs, but it is **not** fully aligned with the newer Round 7 SRP runtime semantics.

In particular, the legacy hybrid still differs from the main SRP line in three important ways:

- it uses a custom anchor recovery helper rather than the shared `recover_state(..., anchor_memory=...)` path
- it does not use the main-line commit/rollback mechanism
- it does not emit `committed_memory` or `state_committed`, so the newer evaluation consistency logic cannot apply to it in the same way

### Reading Against the Main Round 7 Table

Compared with the main Round 7 results:

- `srp` still has much lower drift: `0.1723` vs `0.3979`
- legacy `rag_srp_anchor` has slightly higher task success: `0.9429` vs `0.9167`
- legacy `rag_srp_anchor` has lower query success: `0.8095` vs `0.9683`
- legacy `rag_srp_anchor` uses more tokens: `23.43` vs `19.33`
- legacy `rag_srp_anchor` is also slower: `1.4553s` vs `0.7934s`

The safest interpretation is:

- the old anchor hybrid is still useful as a compatibility reference
- but it should not be treated as a same-generation comparator to the newer Round 7 `srp` line
- a new retrieval-guided SRP variant should be implemented under the current SRP runtime before drawing stronger hybrid conclusions

## Error Boundaries Revealed So Far

This tuning process already revealed several useful failure boundaries.

### 1. Low-Cycle Weakness

At only `3` cycles, the compression-recovery overhead may dominate any stability benefit.

This is especially likely when:

- the memory is short
- the tasks are simple
- the baseline already retains most facts directly

Practical meaning:

- SRP may not show an advantage at low cycle counts
- `3` cycles is useful as a smoke test, not necessarily as the strongest proof regime

### 2. Protocol Leakage

If runtime vocabulary or evaluation phrasing enters the memory state itself, SRP starts preserving the wrong thing.

This showed up when:

- query verbs leaked into `local_vocabulary`
- policy phrases were reinserted into recovered memory

Practical meaning:

- runtime control language must stay separate from task memory
- otherwise SRP becomes self-referential rather than memory-preserving

### 3. Reasoning-Trace Pollution

Reasoning-style local models can pollute every stage if hidden chain-of-thought appears in:

- compression
- recovery
- shared-query answers

Practical meaning:

- local reasoning control is not optional
- `/no_think` or equivalent output control is a real experimental variable

### 4. Evaluation Proxy Instability

The current `query_success` metric is too coarse.

It uses one task-level keyword pool instead of a query-level rubric.

Practical meaning:

- this metric is currently useful for rough scaffolding
- it is not yet reliable enough to support paper-level comparative claims

### 5. Short-Memory Baseline Advantage

On tiny toy tasks, `raw_prompt` and `rag` are naturally strong.

Practical meaning:

- toy tasks are still helpful for debugging
- they are not an environment where SRP is guaranteed to shine

This should not be hidden. It should be treated as part of the paper's honesty and scope control.

## Current Best Interpretation

At this point, the correct claim is not:

> SRP is already better than the baselines.

The correct claim is:

> The local SRP implementation is improving under prompt and state redesign, but its advantage is not yet visible on short-memory 3-cycle toy tasks, and the current evaluation proxy still needs refinement.

That is still valuable. It gives the project:

- a real tuning history
- a concrete failure-boundary narrative
- evidence that implementation details matter
- a reason to test `5` and `7` cycles next

## Immediate Lessons

The most important lessons from this log are:

1. `Qwen + vLLM` can now run real local SRP pilots.
2. Prompt design changes alone already changed the measured SRP profile a lot.
3. Runtime-state design matters more than the original scaffold suggested.
4. The current toy tasks are too small to serve as final paper evidence.
5. The next bottleneck is no longer environment setup. It is evaluation quality and task difficulty.

## Recommended Next Moves

The next best moves are:

1. Replace query-level scoring with per-query expected answers or keyword sets.
2. Strengthen the SRP state object beyond a single `memory_summary`.
3. Run the same tuned setup at `5` cycles before expanding further.
4. Keep these toy tasks as a debugging layer, not the main paper evidence.

## Paper Use

This log should be treated as:

- a tuning reference
- a debugging reference
- a failure-boundary reference

It should not be copied directly into the first paper as a final result section.

For the first paper, the cleanest use is:

- cite the existence of a real local pilot
- use the log internally to justify claim control
- use the observed boundaries to shape the limitations section
