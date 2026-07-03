# Data Layer Management

This note freezes the data-layer structure for the current semester experiment system.

## Goal

The repository should clearly separate:

- protocol validation data
- public benchmark evidence data
- benchmark partitioning artifacts
- validation-target construction logic

without mixing them into one undifferentiated namespace.

## Data-Layer Canonical Split

### 1. Protocol Validation Layer

These files remain the canonical toy-task layer for SRP protocol verification:

- `srp_experiment/data/task_a.json`
- `srp_experiment/data/task_b.json`
- `srp_experiment/data/task_c.json`

Role:

- controlled protocol validation
- SRP operator debugging
- semantic contract / alignment / drift behavior checks
- small-scope sanity checks before large benchmark runs

These files are not the main paper-facing public benchmark layer.

### 2. Public Benchmark Evidence Layer

The current frozen public benchmark layer is:

- `srp_experiment/data/longbench_v2/tasks.json`

Its benchmark manifest is:

- `srp_experiment/data/longbench_v2/manifest.json`

Role:

- reproducible public benchmark evidence
- long-context paper-facing experiments
- multi-model and long-horizon comparison under a shared evaluation regime

For the current semester, this is the canonical external evaluation space.

### 3. Public Benchmark Partition Layer

The 300-task LongBench v2 frozen subset is partitioned into:

- `srp_experiment/data/longbench_v2/tasks_group_1.json`
- `srp_experiment/data/longbench_v2/tasks_group_2.json`
- `srp_experiment/data/longbench_v2/tasks_group_3.json`

Role:

- practical staged execution
- launcher-friendly 100-task grouping
- reduced operational risk for long formal runs

These are execution partitions, not separate benchmark definitions.

### 4. Data Adapter Layer

The canonical importer and partition helper are:

- `srp_experiment/data/longbench_v2/import_longbench_v2.py`
- `srp_experiment/data/longbench_v2/split_task_groups.py`

Role:

- freeze public benchmark content into canonical task objects
- preserve import metadata
- produce stable execution partitions

These files define how external benchmark content enters the experiment system.

### 5. Validation-Target Construction Layer

The canonical validation-target builder is:

- `srp_experiment/srp/validation_targets.py`

Role:

- convert task definitions into a `SemanticContractGraph`
- unify `query_expectations`, `expected_keywords`, and `constraints`
- preserve the SRP protocol's semantic contract layer

This file is part of the semantic validation layer, not the raw data namespace, but it depends directly on the task object shape and should be treated as data-adjacent infrastructure.

## Canonical Task Shape

All task sources should normalize to the same canonical task object shape.

At minimum, every task should preserve:

- `id`
- `task_type`
- `initial_state.memory`
- `queries`
- `metadata`

Optional but preferred fields include:

- `initial_state.constraints`
- `query_expectations`
- `expected_keywords`
- `expected_output`

The canonical normalization rules live in:

- `srp_experiment/data/README.md`

## Semester Freeze

For the current paper stage:

- keep `task_a/b/c.json` as the canonical protocol validation layer
- keep `longbench_v2/tasks.json` as the canonical public benchmark layer
- keep `tasks_group_1/2/3.json` as execution-only partitions
- do not introduce a second public benchmark family into the main pipeline unless the paper scope is deliberately rebaselined

## Practical Rule

If a future experiment needs “more data,” decide which of these four cases it belongs to:

1. protocol validation
2. public benchmark evidence
3. execution partitioning
4. validation-target construction

Do not place one type of change into another type of namespace.
