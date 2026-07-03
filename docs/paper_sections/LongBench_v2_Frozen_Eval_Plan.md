# LongBench v2 Frozen Evaluation Plan

This note freezes the first public-benchmark expansion for SRP.

The benchmark family is:

- `LongBench v2`

The comparison modes are fixed to:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`
- `rag_srp_v2`

The long-horizon cycle settings are fixed to:

- `100`
- `1000`

The purpose of this freeze is not to replace the current SRP toy tasks.
The purpose is to create one external evaluation layer that can be reused when the local model changes.

## Why LongBench v2

LongBench v2 is the most practical first public benchmark for the current SRP stage because it provides:

- a familiar long-context benchmark name for reviewers
- realistic long-context multitasks
- a stable multiple-choice evaluation format
- an officially documented dataset and evaluation harness

This makes it a better main public layer than continuing to rely only on self-authored toy tasks.

## Local Benchmark Location

The frozen local benchmark namespace is:

- `srp_experiment/data/longbench_v2/manifest.json`
- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/data/longbench_v2/import_longbench_v2.py`

The current frozen subset status is:

- imported dataset id: `zai-org/LongBench-v2`
- selection strategy: `first_n_frozen_subset`
- selection offset: `0`
- selection limit: `24`
- imported count: `24`

## External Benchmark Location

The current official references are:

- GitHub: `https://github.com/THUDM/LongBench`
- Dataset: `https://huggingface.co/datasets/zai-org/LongBench-v2`
- Project page: `https://longbench2.github.io/`

## Fixed Comparison Modes

The public-benchmark comparison set is:

1. `raw_prompt`
2. `summarization`
3. `rag`
4. `srp`
5. `rag_srp_v2`

This set is intentionally small.
It covers:

- no semantic abstraction
- lexical compression
- retrieval-heavy reconstruction
- pure SRP runtime
- retrieval-guided SRP hybrid

## Fixed Cycle Counts

For the public long-horizon report, the frozen cycle settings are:

- `100`
- `1000`

These are not replacing the short-cycle paper evidence.
They are an additional long-horizon stress layer.

## Reusable Multi-Model Config

The reusable batch config is:

- `srp_experiment/configs/longbench_v2_multimodel_100_1000.json`

The config is model-reusable by design:

- the benchmark family stays fixed
- the methods stay fixed
- the cycle counts stay fixed
- only the `models` list changes

This is the intended place to add future small models from different companies.

To refresh the frozen subset in a controlled way:

```powershell
python srp_experiment/data/longbench_v2/import_longbench_v2.py --limit 300
```

## Large-Table Schema

For the long-horizon public report, the comparison table should expose at least:

- `backend`
- `model`
- `benchmark`
- `task_id`
- `method`
- `cycles`
- `repeat_id`
- `mean_drift`
- `mean_task_success`
- `mean_query_success`
- `mean_tokens`
- `mean_latency_seconds`
- `mean_contract_satisfaction`
- `mean_alignment`
- `mean_validation_drift`
- `commit_rate`
- `validation_pass_rate`
- `rollback_count`

In addition, the stage-level table should expose:

- `stage`
- `start_cycle`
- `end_cycle`
- `baseline_cycle`
- `baseline_drift`
- `mean_drift`
- `drift_offset`
- `mean_contract_satisfaction`
- `mean_alignment`
- `mean_validation_drift`
- `mean_tokens`
- `commit_rate`

The consistency table should expose:

- `method`
- `cycle`
- `n`
- `drift_mean`
- `drift_std`
- `contract_mean`
- `contract_std`
- `commit_rate`

## Interpretation Constraint

The interpretation of this benchmark layer should stay aligned with the SRP claim:

> SRP defines a state-transition validity space, and models are only executors of this constraint system, not evaluators or reasoners over it.

That means the benchmark report should be read as:

- a test of execution stability under fixed semantic constraints
- not a claim that the model itself is the semantic judge

## Relation To Toy Tasks

The current SRP toy tasks remain:

- protocol validation layer

LongBench v2 becomes:

- public benchmark evidence layer

Both layers should stay in the repo.
They answer different reviewer questions.
