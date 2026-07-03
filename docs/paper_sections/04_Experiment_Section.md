# Experiment Plan Draft

## 1. Experimental Goal

The semester paper should use one small runtime evaluation framework to answer several reviewer-facing questions. The main claim is narrow:

> Does SRP maintain lower bounded semantic drift under repeated compression-recovery cycles than lightweight baselines such as prompt accumulation, summarization memory, and retrieval-based memory?

The experiment should also answer three supporting questions:

- does the semantic-state tuple matter
- do validation and recovery each contribute to stability
- where does SRP fail

## 2. One Framework, Many Questions

The paper should not turn every question into a different benchmark. The cleaner design is to keep one evaluation workflow fixed and vary only:

- method
- operator
- cycle count
- model

Everything else should stay stable:

- task format
- prompt family
- query schedule
- logging format
- metric definitions

This is the most efficient way to keep the semester paper reproducible and easy to review.

## 3. Main Comparison

The main comparison should keep four methods:

- prompt accumulation
- summarization memory
- retrieval-based memory
- SRP

The semester paper should center one runtime comparison table and one drift-over-cycles figure. The strongest non-SRP baseline can then be reused in the camera-ready table.

## 4. Tasks and Benchmarks

The semester version should stay small. The cleanest rule is:

- one long-context benchmark family
- one conversation or memory benchmark family

Recommended targets:

- `LongBench` for long-context question answering, summarization, and retrieval-style stress tests
- `LongMemEval` for long-term memory evaluation
- `LoCoMo` as a second memory benchmark if integration time allows

The current scaffold in `srp_experiment/data/` is still useful for pipeline validation, but it should be treated as a toy import layer rather than final paper evidence.

The data folder is organized to support both the current semester tasks and future benchmark imports:

- toy task files at the top level
- benchmark subfolders with `manifest.json` and `tasks.json`
- normalized task objects that preserve benchmark metadata under `metadata`

Within the current scaffold, the task families are:

- multi-turn instruction consistency
- long-context summarization and regeneration
- iterative compression-recovery cycles

## 5. Prompt and Query Protocol

The prompt family should stay frozen across experiments. The current scaffold already has reusable prompt builders in `srp_experiment/prompting.py`, including:

- compression prompt
- recovery prompt
- judge prompt
- shared query-answer prompt

The implementation also already supports a shared-query flow:

- each task file defines a canonical `queries` list
- each cycle selects the same rotating `evaluation_query` for every method
- each run logs `evaluation_query`, `query_answer`, and `query_success`

This shared-query protocol is what makes the runner comparable across current toy tasks and future benchmark imports.

This means later experiments can be compared under the same questioning schedule rather than loosely different downstream prompts.

## 6. Implementation Rule

To keep the comparison fair, all methods should share:

- the same base model per run
- the same decoding settings
- the same cycle settings
- the same query schedule
- the same logging fields

Once the main comparison begins, freeze:

- model family
- prompt templates
- cycle counts
- baseline definitions
- metric definitions

For the semester paper, a lightweight storage layer is enough. JSON outputs plus tabular summaries are already sufficient for:

- experiment metadata
- per-cycle transitions
- metric aggregation
- failure-case review

The current codebase already stores the key replay fields in `results.json`, `summary.json`, and `run_metadata.json`, and the data import format is documented in `srp_experiment/data/README.md`.

## 7. Metrics

The metrics should stay simple and hierarchical.

- `bounded semantic drift` is the main concept
- `semantic drift` or `cumulative semantic drift` is the main measured stability signal
- `task success` measures whether preserved semantics still support downstream behavior
- `query_success` checks whether all methods still answer the same rotating evaluation questions
- `token cost` measures efficiency

This gives the paper one primary stability object, one behavior-preservation check, one shared-query check, and one efficiency measure.

## 8. Ablations

The ablation order should stay small and high-yield.

### 8.1 Structure Ablation

This tests whether semantic state is doing real work rather than acting as a prompt-format trick. A compact semester version can compare:

- `C_t`
- `C_t + V_t`
- `C_t + M_t`
- `C_t + V_t + M_t`

### 8.2 Operator Ablation

This tests why SRP works:

- without recovery
- without validation

### 8.3 Failure Boundary

The paper should preserve a small failure study rather than many edge cases:

- vocabulary corruption
- wrong retrieval or retrieval mismatch
- validator failure
- concept explosion under repeated updates

## 9. Results Format

The final submission version should center a small set of outputs:

- one semantic-drift-over-cycles figure
- one task-success table
- one token-cost table
- one structure ablation result
- one operator ablation result
- one short failure-boundary paragraph or table

If space permits, one additional task-success-over-cycles figure is valuable because it shows that drift matters for downstream behavior rather than only for proxy scoring.

## 10. Reproducibility

Every run should preserve enough detail to replay the experiment:

- backend
- model
- cycle count
- method list
- prompt family
- evaluation query schedule
- output files

The current scaffold already stores the core runtime metadata in:

- `results.json`
- `summary.json`
- `run_metadata.json`

This is enough for a semester paper. A larger evaluation platform can remain future work.

## 11. Scope Control

The semester version should not expand once the core comparison is running. Keep the following out of scope unless the main experiment is already complete:

- large multi-model sweeps
- many new task families
- large benchmark expansion
- enterprise runtime features
- governance or protocol standardization
- platform claims larger than the current scaffold supports

If time gets tight, cut in this order:

1. extra task families
2. extra models
3. deeper failure-case coverage
4. extra figures
5. any theory that does not directly support the main claim

## 12. Takeaway

The experimental section should support one restrained but publishable claim:

> Explicit semantic-state management can improve finite-horizon stability under repeated compression-recovery transformations, relative to lightweight baselines such as prompt accumulation, summarization memory, and retrieval-based memory.

That is enough for a short paper if the implementation is clean, the questioning protocol is shared across methods, and the scope remains disciplined.
