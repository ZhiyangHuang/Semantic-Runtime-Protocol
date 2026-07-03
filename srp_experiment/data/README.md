# Data Import Format

This folder supports two kinds of inputs:

- current semester toy tasks
- future benchmark imports such as `LongBench` and `LongMemEval`

For the current semester, the canonical split is:

- toy tasks = protocol validation layer
- `longbench_v2/tasks.json` = public benchmark evidence layer
- `longbench_v2/tasks_group_1/2/3.json` = execution partitions

The canonical family-resolution map is:

- [DATA_FAMILY_CANONICAL_MAP.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/data/DATA_FAMILY_CANONICAL_MAP.md)

The higher-level management note is:

- [Data_Layer_Management.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/Data_Layer_Management.md)

## Canonical Task Object

Every imported task should normalize to the same shape:

```json
{
  "id": "task_id",
  "task_type": "multi_turn_instruction",
  "initial_state": {
    "memory": "..."
  },
  "queries": ["...", "..."],
  "expected_keywords": ["...", "..."],
  "metadata": {
    "benchmark": "LongBench",
    "family": "long_context",
    "split": "validation",
    "source_file": "srp_experiment/data/longbench/tasks.json"
  }
}
```

## Supported File Shapes

The runner accepts these payload shapes:

- a JSON list of task objects
- a JSON object with a top-level `tasks` array
- a single JSON object that already looks like one task

## Recommended Layout

Use a subfolder per benchmark family:

```text
srp_experiment/data/
  task_a.json
  task_b.json
  task_c.json
  longbench/
    manifest.json
    tasks.json
    import_longbench_v2.py
  longmemeval/
    manifest.json
    tasks.json
```

## Benchmark-Specific Fields

You can keep extra benchmark metadata in the manifest or task object:

- `benchmark`
- `family`
- `split`
- `subset`
- `source`
- `source_id`
- `record_id`

The runner preserves these fields under `metadata` so they remain available in downstream analysis.

## LongBench v2 Import

The frozen public-benchmark subset for the next stage lives under:

- `srp_experiment/data/longbench_v2/manifest.json`
- `srp_experiment/data/longbench_v2/tasks.json`
- `srp_experiment/data/longbench_v2/import_longbench_v2.py`

The importer currently writes a deterministic public-evaluation subset rather than the full benchmark payload.

Execution partitions for staged formal runs live under:

- `srp_experiment/data/longbench_v2/tasks_group_1.json`
- `srp_experiment/data/longbench_v2/tasks_group_2.json`
- `srp_experiment/data/longbench_v2/tasks_group_3.json`

## Import Rule

For the semester paper, the imported data should still freeze:

- the prompt family
- the query schedule
- the metric definitions
- the cycle counts

Only the task content should vary across benchmark families.
