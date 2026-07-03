# Local Qwen Pilot Tuning Log

## Purpose

This note records the preserved local-backend pilot history for the semester paper.

Its job is not to present a polished result. Its job is to preserve the full round-by-round record as formal evidence, while keeping legacy archive outputs and later refactor reruns clearly separable.

Its job is to preserve:

- what changed
- what improved
- what still failed
- what the current error boundaries look like

This makes the log useful for three later purposes:

1. writing an honest pilot-results section for the first paper
2. diagnosing why SRP underperforms or improves under certain settings
3. building a failure-boundary narrative rather than hiding bad runs

## Round Index

- [Rounds 0 to 3](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/local_qwen_pilot_rounds_0_to_3.md)
  - `Run 0: Untuned Local Pilot`
  - `Tuning Round 1`
  - `Tuning Round 2`
  - `Tuning Round 3`
- [Rounds 4 to 5](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/local_qwen_pilot_rounds_4_to_5.md)
  - `Tuning Round 4`
  - `Exploratory Round 5`
  - `rag_srp`
  - `rag_srp_anchor`
- [Rounds 6 to 7](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/local_qwen_pilot_rounds_6_to_7.md)
  - `Tuning Round 6`
  - `Tuning Round 7`
  - `Error Boundaries Revealed So Far`
  - `Current Best Interpretation`
  - `Immediate Lessons`
  - `Recommended Next Moves`
  - `Paper Use`

## Results Index

- [local_cycles3/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3/summary.json)
  - `Run 0: Untuned Local Pilot`
- [local_cycles3_tuned1/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned1/summary.json)
  - `Tuning Round 1`
- [local_cycles3_tuned2/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned2/summary.json)
  - `Tuning Round 2`
- [local_cycles3_tuned3/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles3_tuned3/summary.json)
  - `Tuning Round 3`
- [local_cycles5_tuned4/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles5_tuned4/summary.json)
  - `Tuning Round 4`
- [local_cycles7_tuned4/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles7_tuned4/summary.json)
  - `Tuning Round 4 Extension: 7-Cycle Check`
- [local_cycles5_rag_srp/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp/summary.json)
  - `Exploratory Round 5A: rag_srp`
- [local_cycles5_rag_srp_anchor/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles5_rag_srp_anchor/summary.json)
  - `Exploratory Round 5B: rag_srp_anchor`
- [local_cycles5_tuned6/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles5_tuned6/summary.json)
  - `Tuning Round 6: 5 Cycles`
- [local_cycles7_tuned6/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/local_cycles7_tuned6/summary.json)
  - `Tuning Round 6: 7 Cycles`
- [local_cycles7_tuned7_compare/summary.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/legacy_results/local_cycles7_tuned7_compare/summary.json)
  - `Tuning Round 7: same-protocol 7-cycle comparison`

## Overview

These runs were executed on the local `vLLM` backend with:

- model: `Qwen/Qwen3-4B-AWQ`
- serving stack: `vLLM` OpenAI-compatible server
- endpoint style: local backend via `LOCAL_MODEL_URL`

The overall pilot sequence now spans:

- an untuned local reference run
- multiple main-line SRP tuning rounds
- an exploratory hybrid stage
- later anchor-guided SRP rounds under a frozen public evaluation layer

The most important operational outcome is that the project has clearly crossed from scaffold status into a real pilot regime with preserved outputs, reproducible tables, and auditable changes.

## Comparability Warning

The pilot tables in this log are **not all directly comparable in the same way**.

This is important for later review, because some tuning rounds changed:

- the shared backend behavior
- the output postprocessing layer
- the scoring function
- the task-side query expectations

So later readers should not assume that every table only reflects a change inside `srp/`.

The safest interpretation rule is:

- compare `drift`, `task_success`, and `tokens` most directly when the scoring layer is unchanged
- treat `query_success` carefully whenever the scoring logic or query expectations changed
- treat cross-round baseline changes as expected if the common inference layer changed

## Freeze Decision

The project now formally adopts a frozen public evaluation layer for later comparisons.

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

## Volumes

Use the split volumes below for the full preserved record:

1. [local_qwen_pilot_rounds_0_to_3.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/local_qwen_pilot_rounds_0_to_3.md)
2. [local_qwen_pilot_rounds_4_to_5.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/local_qwen_pilot_rounds_4_to_5.md)
3. [local_qwen_pilot_rounds_6_to_7.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/local_qwen_pilot_rounds_6_to_7.md)
