# Reproducibility Layer Management

This note freezes the reproducibility layer for the current semester experiment system.

## Goal

The repository must preserve a stable layer for:

- environment alignment
- benchmark provenance
- qualification gating
- runtime equivalence checking
- protocol trace inspection
- submission auditability

This layer should not be confused with ordinary experiment convenience scripts.

## Folder-Level Structure

The reproducibility layer is distributed across a few canonical folders.

### 1. Experiment Runtime Guardrails

Folder:

- `srp_experiment/`

Canonical files:

- `check_env_alignment.py`
- `check_local_backend.py`
- `experiment_qualification.py`
- `run_qualified_experiment.py`
- `run_qualified_batch.py`

Role:

- environment sanity
- backend sanity
- qualification gate
- formal-entry blocking before paper-facing runs

### 2. Benchmark Provenance Layer

Folder:

- `srp_experiment/data/longbench_v2/`

Canonical files:

- `manifest.json`
- `tasks.json`
- `tasks_group_1.json`
- `tasks_group_2.json`
- `tasks_group_3.json`
- `import_longbench_v2.py`
- `split_task_groups.py`

Role:

- benchmark source provenance
- frozen subset definition
- execution partition provenance

### 3. Runtime Reproducibility Audit Layer

Folder:

- `srp_experiment/`

Canonical files:

- `runtime_equivalence_test.py`
- `protocol_behavior_trace.py`

Canonical result artifacts:

- `srp_experiment/results/runtime_equivalence_all_tasks_with_exit_criteria.json`
- `srp_experiment/results/protocol_behavior_trace_iterative_cycles.json`

Role:

- deterministic vs mock-path equivalence
- first-divergence tracing
- reviewer inspection of state transitions

### 4. Submission Audit Layer

Folder:

- `first_paper/`

Canonical file:

- `first_paper/submission_audit.py`

Canonical output folder:

- `first_paper/submission/`

Role:

- compile validation
- artifact presence validation
- reviewer-visible packaging checks
- freeze decision support

### 5. Evidence / Result Reproducibility Layer

Folder:

- `srp_experiment/results/`

Canonical files:

- `experiment_qualification_report.json`
- `FORMAL_EVIDENCE_INDEX.md`
- `RESULT_FAMILY_CANONICAL_MAP.md`
- `batch_summary_table.json`

Role:

- formal evidence indexing
- canonical result-family selection
- reproducible reduced outputs

## Protection Rule

Do not delete files from the reproducibility layer unless all three are true:

1. the file has a documented canonical replacement
2. no review or audit flow still points to it
3. provenance or inspection value is preserved elsewhere

## Practical Rule

If a file helps answer one of these reviewer questions, it belongs to the reproducibility layer and should default to keep:

- Can I reproduce the run?
- Can I verify the environment and benchmark source?
- Can I inspect state transitions?
- Can I check equivalence between execution paths?
- Can I audit the submission package?
