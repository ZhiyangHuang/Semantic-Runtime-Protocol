# Data Family Canonical Map

This file resolves repeated or closely related data-layer artifacts into canonical vs preserved roles.

Its purpose is to prevent confusion between:

- protocol validation tasks
- public benchmark tasks
- benchmark partitions
- benchmark import helpers
- data-adjacent transformation logic

## Rule

For each data family:

- keep one canonical artifact for the main role
- preserve related helper or partition files with explicit secondary roles
- do not treat all similarly named files as equally primary

## Family 1: Protocol Validation Tasks

Canonical:

- `task_a.json`
- `task_b.json`
- `task_c.json`

Role:

- semester-stable toy protocol validation layer

Interpretation:

- these are the canonical internal protocol checks
- they are not the canonical public benchmark evidence layer

## Family 2: Public Benchmark Frozen Subset

Canonical:

- `longbench_v2/tasks.json`
- `longbench_v2/manifest.json`

Role:

- canonical public benchmark evidence layer
- imported and frozen LongBench v2 subset

Interpretation:

- use this pair when referring to the main benchmark content and provenance

## Family 3: Public Benchmark Execution Partitions

Canonical partition set:

- `longbench_v2/tasks_group_1.json`
- `longbench_v2/tasks_group_2.json`
- `longbench_v2/tasks_group_3.json`

Role:

- launcher-friendly 100-task staged execution partitions

Interpretation:

- these are canonical execution partitions
- they are not separate benchmark definitions
- they derive from `longbench_v2/tasks.json`

## Family 4: Public Benchmark Import Helpers

Canonical:

- `longbench_v2/import_longbench_v2.py`

Secondary but required:

- `longbench_v2/split_task_groups.py`

Interpretation:

- the importer defines benchmark ingestion
- the splitter defines staged execution partitioning
- both are canonical helpers for the current LongBench layer, but they serve different roles

## Family 5: Data Schema Guidance

Canonical:

- `srp_experiment/data/README.md`

Supporting governance:

- `docs/strategy/Data_Layer_Management.md`
- `docs/cleanup_review/temporary2.md`

Interpretation:

- `README.md` explains task-shape expectations
- `Data_Layer_Management.md` freezes layer boundaries
- `docs/cleanup_review/temporary2.md` protects cleanup against over-deletion

## Family 6: Data-Adjacent Semantic Contract Builder

Canonical:

- `srp_experiment/srp/validation_targets.py`

Role:

- canonical task-to-contract transformation layer

Interpretation:

- not a raw data file
- but data-adjacent enough that it must remain tied to the canonical task object shape

## Practical Rule

When you ask “which data file should I use?” answer in this order:

1. toy protocol validation
2. public benchmark frozen subset
3. public benchmark execution partition
4. importer / partition helper
5. task-shape / contract builder support

Do not mix these roles in one sentence as if they were interchangeable.
