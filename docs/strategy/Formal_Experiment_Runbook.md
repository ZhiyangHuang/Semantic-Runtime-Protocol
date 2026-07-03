# Formal Experiment Runbook

## Purpose

This runbook converts the local pilot system into a paper-facing execution workflow.

Its job is to freeze:

- what counts as a formal run
- which config should be used
- which outputs should be preserved
- which changes are still allowed

This is not a tuning note.
It is the execution contract for the first formal local experiment pass.

The contract distinguishes three namespaces:

- current formal evidence
- legacy archive outputs
- future refactor reruns

## Current Default

The current formal local run should use:

- backend: `local`
- model: `Qwen/Qwen3-4B-AWQ`
- serving stack: local `vLLM` OpenAI-compatible server
- cycles: `3`, `5`, `7`
- main methods:
  - `raw_prompt`
  - `summarization`
  - `rag`
  - `srp`

The canonical formal config is:

- [first_paper_formal_local.json](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/configs/first_paper_formal_local.json)

## Default Guardrails

The first formal experiment pass should use the following SRP guardrail defaults:

- `SRP_MAX_CYCLE_DRIFT=0.35`
- `SRP_MIN_KEYWORD_SCORE=0.50`

Interpretation:

- a compression-recovery cycle is committed only if the recovered memory stays within the per-cycle drift bound
- and the recovered memory also preserves at least the minimum keyword-retention score

If either check fails:

- the SRP state rolls back to the pre-compression memory for that cycle
- the failure is recorded in `results.json`

These values should be treated as the default guardrail settings for the first formal run package, not as permanently fixed scientific constants.

For the first formal pass:

- keep these values fixed across the whole batch
- record them in `.env` or the shell environment before running the batch
- only change them later as a deliberate SRP-side tuning intervention

## Frozen Layer

For formal runs, the shared public evaluation layer is frozen.

Do not change these between formal runs unless a deliberate re-baselining decision is made:

- `model_backend.py`
- output postprocessing
- `eval/scoring.py`
- query expectation format
- toy task definitions in `data/task_*.json`

Allowed changes during later SRP-only formal follow-ups:

- `srp/`
- SRP-specific prompts in `prompting.py`

## Formal Run Scope

The formal local package currently includes:

### `P0` Main Comparison

- four-method comparison at:
  - `3`
  - `5`
  - `7`

### `P1` Focused Follow-Ups

- `summarization` vs `srp` at:
  - `5`
  - `7`
- `rag` vs `srp` at:
  - `5`
  - `7`

These follow-ups are paper-supporting diagnostics.
They are not replacements for the four-method main table.

## Preflight

Before a formal run:

1. confirm the local model server is live
2. confirm the `.env` values point to the correct local backend
3. confirm the SRP guardrail env values are set to the formal defaults
4. confirm the formal config output root is not shared with tuning outputs
5. confirm the working tree does not contain accidental public-layer changes

Recommended formal guardrail env values:

```powershell
$env:SRP_MAX_CYCLE_DRIFT="0.35"
$env:SRP_MIN_KEYWORD_SCORE="0.50"
```

Recommended preflight command:

```powershell
python srp_experiment/check_local_backend.py
```

## Canonical Command

Preferred one-command formal workflow:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/first-paper-run.ps1 -Config srp_experiment/configs/first_paper_formal_local.json
```

Optional:

- `-SkipHealthCheck`
- `-FailFast`

## Comparison Workflow

In addition to the canonical first-paper formal batch, the project now maintains a separate comparison workflow for broader multi-method comparison tables.

Its purpose is different from the main formal paper package:

- validate larger comparison packs under the same local execution chain
- compare legacy and newer hybrid methods without rewriting the main formal config
- generate standalone comparison tables for method-family diagnostics

This workflow does **not** replace the canonical formal batch.

It should be treated as:

- a structured comparison extension

rather than:

- the primary paper-facing frozen package

### Default Comparison Mode

The default comparison workflow currently runs:

- methods:
  - `raw_prompt`
  - `summarization`
  - `rag`
  - `srp`
  - `rag_srp`
  - `rag_srp_anchor`
  - `rag_srp_v2`
- cycles:
  - `3`
  - `5`
  - `7`

### Canonical Comparison Command

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1
```

### Manual Comparison Controls

The comparison workflow supports manual control over:

- comparison mode
- cycle list

Examples:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Cycles 5 7
```

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Mode hybrid_family
```

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Mode srp_vs_hybrids -Cycles 7
```

### Supported Comparison Modes

Current supported modes are:

- `all_modes`
  - `raw_prompt`, `summarization`, `rag`, `srp`, `rag_srp`, `rag_srp_anchor`, `rag_srp_v2`
- `core_four`
  - `raw_prompt`, `summarization`, `rag`, `srp`
- `hybrid_family`
  - `rag`, `rag_srp`, `rag_srp_anchor`, `rag_srp_v2`
- `hybrid_lineage`
  - `rag_srp`, `rag_srp_anchor`, `rag_srp_v2`
- `srp_vs_hybrids`
  - `rag`, `srp`, `rag_srp_anchor`, `rag_srp_v2`

### Comparison Outputs

Comparison outputs are written separately from the canonical formal batch.

They are stored under:

- `srp_experiment/results/batch_runs/comparison_*`
- `srp_experiment/results/comparison_tables/comparison_*`

The comparison workflow generates:

- a generated config under `results/generated_configs/`
- a dedicated `batch_manifest.json`
- a dedicated `batch_summary_table.json`
- standalone comparison `paper_table`, `quality_table`, `efficiency_table`, `guardrail_table`, and `camera_ready_table`

### Output Namespace Rule

To keep current formal evidence separate from future refactor reruns, use distinct output namespaces.

Recommended split:

- current formal evidence: `first_paper_formal_local`
- future refactor rerun: `first_paper_formal_local_refactored`

If a broader directory structure is preferred:

- `formal_current/first_paper_formal_local`
- `formal_refactored/first_paper_formal_local`

Do not overwrite the current formal evidence with the refactored rerun.
Do not mix the two generations in the same results directory.

This separation matters because it prevents:

- formal paper-facing frozen outputs

from being mixed with:

- exploratory or expanded comparison packs

## Output Root

Formal local outputs should go under:

- `srp_experiment/results/batch_runs/first_paper_formal_local`

This separation matters.

It keeps:

- pilot tuning outputs
- exploratory hybrid outputs
- formal paper-facing outputs

from being mixed together.

## Required Outputs

After a successful formal run, preserve these files:

- `results/batch_manifest.json`
- `results/batch_summary_table.json`
- `results/batch_summary_table.csv`
- `results/batch_summary_table.md`
- `results/paper_table.md`
- `results/paper_table.tex`
- `results/quality_table.md`
- `results/quality_table.tex`
- `results/efficiency_table.md`
- `results/efficiency_table.tex`
- `results/guardrail_table.md`
- `results/guardrail_table.tex`
- `results/camera_ready_table.md`
- `results/camera_ready_table.tex`

Also preserve the run directories under:

- `results/batch_runs/first_paper_formal_local`

## What Counts As Success

A formal run is operationally successful when:

- batch execution completes without failed runs
- `batch_summary_table.json` is non-empty
- the main `3`, `5`, `7` four-method groups appear in the summary
- `paper_table.md` renders the main table
- `camera_ready_table.md` renders the SRP vs strongest-baseline comparison
- the runner sanity check does not report real bundle-level incompleteness
- the recorded formal runs preserve the intended guardrail settings in `run_metadata.json`

It is still acceptable for the runner to emit a `Note` about partial global comparisons if those runs are internally complete for their own method bundle.

## Current Reporting State

The current formal runner now reports:

- drift
- task success
- query success
- token reporting
- latency

The current formal package also records SRP guardrail decisions at the detailed-results level, including whether a cycle was committed or rolled back.

The formatted table package now also includes a dedicated guardrail summary:

- `guardrail_table.md`
- `guardrail_table.tex`

These tables aggregate:

- `commit_rate`
- `mean_validation_drift`
- `rollback_count`

Methods that do not implement SRP-style commit and rollback semantics are expected to show `-` in the guardrail table.

## Immediate Next Action

Run the first formal local batch with the canonical command above and preserve the resulting table package as the first paper-facing frozen result set.
