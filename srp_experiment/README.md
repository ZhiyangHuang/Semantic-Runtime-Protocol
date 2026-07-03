# SRP Experiment

This directory contains a runnable SRP experiment scaffold for comparing SRP against prompt, summarization, and retrieval baselines.

Top-level experiment goal:

This experiment package supports the first SRP paper, and it is also the base layer for the later SRP paper sequence. The scope should stay narrow, reproducible, and aligned with one semester of focused refinement.

Protocol principle:

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

The current documentation uses a shared disclosure vocabulary:

- formal evidence
- legacy archive
- refactor rerun

## Current Stage Freeze

For the current semester, this codebase should support a narrow paper scope rather than continued feature expansion.

Stage-frozen items for now:

- large multi-model sweeps beyond the main paper need
- extra task families beyond the current core tasks
- advanced protocol extensions not required by the paper
- large future-work benchmark expansion

The priority order is:

1. keep the main experiment runnable
2. keep the tables reproducible
3. keep the paper scope narrow
4. postpone future-facing features until the core report is finished

## Frozen Public Evaluation Layer

For the current first-paper stage, the public evaluation layer is now frozen.

This means later tuning work should assume the following are fixed unless a deliberate re-baselining decision is made:

- local backend behavior
- output postprocessing
- scoring function
- query expectation format
- toy task definitions

Concretely, later tuning rounds should modify `srp/` first, not the shared evaluation stack.

The practical rule is:

- change `srp/` freely while SRP is still being tuned
- do not change the common evaluation layer unless you explicitly intend to create a new baseline generation

Frozen public-benchmark expansion for the next stage:

- `LongBench v2`
- `raw_prompt`, `summarization`, `rag`, `srp`, `rag_srp_v2`
- `100` and `1000` cycles
- reusable config: `srp_experiment/configs/longbench_v2_multimodel_100_1000.json`
- imported frozen subset: `srp_experiment/data/longbench_v2/tasks.json` with `300` public LongBench v2 samples

## Data And Disclosure Hygiene

The repository now separates experiment outputs into three broad classes:

- `results/` - current formal evidence and paper-facing outputs
- `legacy_results/` - archived exploratory, smoke, old-generation, or suspect outputs
- `results/batch_runs/first_paper_formal_local/` - the current formal evidence namespace for the first-paper package

Use the formal evidence namespace for paper-facing outputs, and keep exploratory or legacy outputs out of that path.
Keep future refactor reruns in a separate namespace so they do not overwrite the current formal evidence.

The risk and separation rules are documented in:

- [Formal_Experiment_Runbook.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/Formal_Experiment_Runbook.md)
- [SRP_Risk_Classification_Checklist.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/SRP_Risk_Classification_Checklist.md)
- [SRP_Leakage_And_Cheating_Risk_Report.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/SRP_Leakage_And_Cheating_Risk_Report.md)

## Exploratory Hybrid Methods

The current first-paper main comparison remains fixed to:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`

An additional exploratory hybrid method family, including `rag_srp`, `rag_srp_anchor`, and `rag_srp_v2`, is available for diagnostics only.

It is intended to answer a narrower question:

- does retrieval-guided memory become more useful when passed through a lightweight SRP-style compression and recovery loop?

These hybrids should not be treated as part of the paper's main comparison unless the paper explicitly redefines the experiment scope.

## Start Here

If you only want the semester-stable entrypoints, use exactly these:

1. `longbench_launcher.py` - interactive entry for LongBench runs
2. `run_qualified_experiment.py` - qualification-gated formal single-run entry
3. `batch_run.py` - canonical batch engine
4. `collect_batch_summary.py` - canonical reducer
5. `repeat_aggregate.py` and `long_horizon_report.py` - repeat and curve reporting

Everything else should be treated as support, wrappers, diagnostics, or legacy-preserved workflow unless a paper-specific need says otherwise.

The short execution relationship is:

- `longbench_launcher.py` -> generated config -> `run-longbench-batch-with-popup.ps1` -> `batch_run.py`
- `run_qualified_experiment.py` -> `experiment_qualification.py` -> `run_experiment.py`
- `batch_run.py` -> per-run folders
- `collect_batch_summary.py` -> `repeat_aggregate.py` -> `long_horizon_report.py`
- tables / figures consume the reduced outputs rather than raw run folders

See also:

- [TOOLS_INDEX.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/TOOLS_INDEX.md)
- [ENTRYPOINT_EXECUTION_MAP.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/ENTRYPOINT_EXECUTION_MAP.md)
- [Data_Layer_Management.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/Data_Layer_Management.md)
- [Baseline_Layer_Management.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/Baseline_Layer_Management.md)
- [Evaluation_Layer_Management.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/Evaluation_Layer_Management.md)

## Layout

- `data/` - canonical task inputs
- `baselines/` - controlled baseline memory operators
- `srp/` - semantic-state protocol pipeline
- `eval/` - drift, contract, query, and judge helpers
- `configs/` - canonical reusable run plans
- `run_experiment.py` - canonical single-run engine
- `batch_run.py` - canonical batch engine
- `collect_batch_summary.py` - canonical multi-run reducer
- `repeat_aggregate.py` - canonical repeat-level statistics reducer
- `long_horizon_report.py` - canonical stage and curve report generator
- `longbench_launcher.py` - canonical interactive launcher
- `experiment_qualification.py` - qualification gate
- `run_qualified_experiment.py` - canonical qualified formal entry

Secondary infrastructure:

- `model_backend.py`
- `prompting.py`
- `paper_table_formatter.py`
- `evidence_pipeline.py`
- `srp_cli.py`
- `progress_popup.py`
- `check_env_alignment.py`
- `check_local_backend.py`

Diagnostic / audit support:

- `protocol_behavior_trace.py`
- `runtime_equivalence_test.py`

Exploratory hybrids preserved but not main-paper primary:

- `baselines/rag_srp.py`
- `baselines/rag_srp_anchor.py`

## Quick Start

```powershell
python srp_experiment/run_experiment.py
python srp_experiment/plot_results.py
```

## Formal Entry

For formal paper-facing runs, use the qualification gate first.

```powershell
python srp_experiment/experiment_qualification.py
python srp_experiment/run_qualified_experiment.py --backend local --methods raw_prompt summarization rag srp --cycles 3 --output-dir srp_experiment/results/formal_smoke
```

`run_experiment.py` remains useful for debugging and exploratory runs.
`run_qualified_experiment.py` is the intended formal entry because it blocks paper-facing execution unless the qualification report is `QUALIFIED`.

## Canonical Stack

If you want the cleanest current experiment path, use only this stack:

1. `longbench_launcher.py` or `run_qualified_experiment.py`
2. `batch_run.py`
3. `collect_batch_summary.py`
4. `repeat_aggregate.py`
5. `long_horizon_report.py`
6. paper tables / figures

Treat other scripts as support, diagnostics, or legacy scaffolding unless the paper explicitly needs them.

Supporting indexes:

- [TOOLS_INDEX.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/TOOLS_INDEX.md)
- [ENTRYPOINT_EXECUTION_MAP.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/ENTRYPOINT_EXECUTION_MAP.md)
- [configs/README.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/configs/README.md)
- [configs/CANONICAL_CONFIG_MAP.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/configs/CANONICAL_CONFIG_MAP.md)
- [results/FORMAL_EVIDENCE_INDEX.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/results/FORMAL_EVIDENCE_INDEX.md)

Batch sweep:

```powershell
python srp_experiment/batch_run.py
python srp_experiment/batch_run.py --config srp_experiment/configs/default_batch.json
python srp_experiment/collect_batch_summary.py
python srp_experiment/repeat_aggregate.py
python srp_experiment/paper_table_formatter.py
python srp_experiment/evidence_pipeline.py
python srp_experiment/long_horizon_report.py --input-dir srp_experiment/results/paper_figure_core_local --task-id iterative_cycles
```

## Reproducible Env Workflow

1. Copy [srp_experiment/.env.example](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/.env.example) to `srp_experiment/.env`
2. Fill in the backend, model, API key, and output settings
3. Run the same commands without repeating long argument lists

Example `.env`-driven workflow:

```powershell
Copy-Item srp_experiment/.env.example srp_experiment/.env
python srp_experiment/check_env_alignment.py
python srp_experiment/run_experiment.py
python srp_experiment/batch_run.py
python srp_experiment/collect_batch_summary.py
python srp_experiment/repeat_aggregate.py
python srp_experiment/paper_table_formatter.py
```

### Real Backend Modes

```powershell
python srp_experiment/run_experiment.py --backend mock
python srp_experiment/run_experiment.py --backend openai --model gpt-4o-mini
python srp_experiment/run_experiment.py --backend local --model Qwen/Qwen3-4B-AWQ
```

Environment variables:

- `SRP_BACKEND` - default backend for `run_experiment.py`
- `SRP_MODEL` - default model name
- `SRP_CYCLES` - default cycle count
- `SRP_METHODS` - comma-separated method list like `raw_prompt,summarization,rag,srp`
- `SRP_MAX_CYCLE_DRIFT` - maximum accepted per-cycle SRP drift before rollback to the pre-compression memory
- `SRP_MIN_KEYWORD_SCORE` - minimum accepted per-cycle SRP keyword-retention score before rollback to the pre-compression memory
- `SRP_OUTPUT_DIR` - default output directory for single runs
- `SRP_BATCH_CONFIG` - default batch config path
- `SRP_BATCH_RUNS_DIR` - default directory containing batch run folders
- `SRP_PAPER_TABLE_INPUT` - default collected summary JSON
- `SRP_PAPER_TABLE_MD` - default Markdown paper table output
- `SRP_PAPER_TABLE_TEX` - default LaTeX paper table output
- `SRP_QUALITY_TABLE_MD` - default quality table Markdown output
- `SRP_QUALITY_TABLE_TEX` - default quality table LaTeX output
- `SRP_EFFICIENCY_TABLE_MD` - default efficiency table Markdown output
- `SRP_EFFICIENCY_TABLE_TEX` - default efficiency table LaTeX output
- `SRP_CAMERA_READY_MD` - default camera-ready Markdown output
- `SRP_CAMERA_READY_TEX` - default camera-ready LaTeX output
- `OPENAI_API_KEY` - required for `--backend openai`
- `OPENAI_BASE_URL` - optional OpenAI-compatible base URL override
- `LOCAL_MODEL_URL` - required for `--backend local`; can be `http://localhost:8000`, `http://localhost:8000/v1`, or a full `/chat/completions` endpoint
- `SRP_TIMEOUT_SECONDS` - optional request timeout override

### Practical Examples

OpenAI:

```powershell
$env:OPENAI_API_KEY="sk-..."
python srp_experiment/run_experiment.py --backend openai --model gpt-4o-mini
```

Local OpenAI-compatible server:

```powershell
$env:LOCAL_MODEL_URL="http://localhost:8000"
python srp_experiment/run_experiment.py --backend local --model Qwen/Qwen3-4B-AWQ
```

The local backend assumes an OpenAI-compatible chat endpoint. If you pass only a host, the runner expands it to `/v1/chat/completions`.

If `http://localhost:8000` returns an empty reply from Windows while the same endpoint works inside Ubuntu or WSL, use the WSL IP instead. For example:

```powershell
$env:LOCAL_MODEL_URL="http://172.25.253.78:8000"
python srp_experiment/check_local_backend.py
python srp_experiment/run_experiment.py --backend local --model Qwen/Qwen3-4B-AWQ
```

For the current first-paper setup, the recommended local stack is:

- `vllm serve Qwen/Qwen3-4B-AWQ`
- `LOCAL_MODEL_URL=http://localhost:8000` or the active WSL IP
- `SRP_BACKEND=local`
- `SRP_MODEL=Qwen/Qwen3-4B-AWQ`

OpenAI batch template:

```powershell
python srp_experiment/batch_run.py --config srp_experiment/configs/openai_batch.json
```

Local batch template:

```powershell
python srp_experiment/batch_run.py --config srp_experiment/configs/local_batch.json
```

First-paper priority batch:

```powershell
python srp_experiment/batch_run.py --config srp_experiment/configs/first_paper_priority_local.json
```

This is the recommended local execution plan for the current stage because it keeps the scope narrow:

- main four-method comparison at `3`, `5`, and `7` cycles
- focused `summarization` vs `srp` comparison at longer cycles
- focused `rag` vs `srp` comparison at longer cycles

It is intended for paper-facing runs after SRP tuning, not for exploratory hybrid development.

Formal first-paper batch:

```powershell
python srp_experiment/batch_run.py --config srp_experiment/configs/first_paper_formal_local.json
```

This is the clean paper-facing local package under the frozen public evaluation layer.
It uses a separate output root so the formal evidence set does not mix with legacy archive or exploratory tuning outputs.

One-command first-paper workflow:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/first-paper-run.ps1
```

Unified CLI workflow:

```powershell
python srp_experiment/srp_cli.py run --config srp_experiment/configs/first_paper_formal_local.json
```

`srp_cli.py run` now performs an automatic `.env` alignment check before the formal pipeline starts.

LongBench v2 smoke pipeline:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/run-longbench-smoke.ps1
```

This runs the smoke batch, then `collect_batch_summary.py`, then `long_horizon_report.py`.

LongBench launcher window:

```powershell
python srp_experiment/longbench_launcher.py
```

This lets you choose one method from the five frozen modes and one 100-task group from the 300-task LongBench split, then launches the batch with the progress popup.

Optional flags:

- `-SkipHealthCheck`
- `-FailFast`
- `-Config srp_experiment/configs/local_batch.json`

For the formal paper-facing pass, prefer:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/first-paper-run.ps1 -Config srp_experiment/configs/first_paper_formal_local.json
```

The formal execution contract is documented in [Formal_Experiment_Runbook.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/strategy/Formal_Experiment_Runbook.md).

Comparison workflow:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1
```

This runs the current default comparison pack:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`
- `rag_srp`
- `rag_srp_anchor`
- `rag_srp_v2`

at:

- `3`
- `5`
- `7`

Useful manual variants:

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Cycles 5 7
```

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Mode hybrid_family
```

```powershell
powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Mode srp_vs_hybrids -Cycles 7
```

Comparison outputs are written under:

- `srp_experiment/results/batch_runs/comparison_*`
- `srp_experiment/results/comparison_tables/comparison_*`

These are comparison outputs, not the paper's primary formal evidence namespace.

### Local vLLM Health Check

Before running the first-paper experiments against a local vLLM server, verify that the server responds to both `/v1/models` and `/v1/chat/completions`:

```powershell
python srp_experiment/check_local_backend.py
```

If this check fails with an empty reply or connection reset, the issue is in the local serving process rather than the SRP experiment runner.

### Outputs

- `results/results.json` - per-cycle detailed measurements
- `results/summary.json` - aggregated mean drift, task success, shared-query success, and token cost
- `results/run_metadata.json` - backend, model, methods, and run settings
- `results/batch_runs/` - one folder per sweep combination
- `results/batch_manifest.json` - stdout, stderr, and return code for each batch run
- `results/batch_summary_table.json` - merged machine-readable summary table
- `results/batch_summary_table.csv` - spreadsheet-friendly summary table
- `results/batch_summary_table.md` - Markdown table for papers or notes
- `results/paper_table.md` - compressed paper-style Markdown table
- `results/paper_table.tex` - compressed LaTeX table for the paper draft
- `results/quality_table.md` - quality-focused Markdown table
- `results/quality_table.tex` - quality-focused LaTeX table
- `results/efficiency_table.md` - efficiency-focused Markdown table
- `results/efficiency_table.tex` - efficiency-focused LaTeX table
- `results/guardrail_table.md` - commit/rollback guardrail Markdown table
- `results/guardrail_table.tex` - commit/rollback guardrail LaTeX table
- `results/camera_ready_table.md` - SRP vs strongest baseline Markdown table
- `results/camera_ready_table.tex` - SRP vs strongest baseline LaTeX table

The default `mock` backend stays deterministic so the scaffold remains testable even without API access, while `openai` and `local` let you switch to real model calls without changing the experiment code.

## Shared Query Flow

The task files define a canonical `queries` list. During evaluation, every method is scored against the same rotating query schedule at each cycle, so later runs can be compared under the same questioning flow rather than only through keyword overlap on raw memory text.

For the normalized import format and future benchmark layout, see [srp_experiment/data/README.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/data/README.md).

Each detailed result row records:

- `evaluation_query` - the exact query used at that cycle
- `query_answer` - the answer produced from that method's memory snapshot
- `query_success` - keyword-based success for that shared query

To run the exploratory hybrid by itself:

```powershell
python srp_experiment/run_experiment.py --methods rag_srp
```

### Batch Config Format

Each config has:

- `shared` - defaults like `backend` and `output_root`
- `runs` - named sweeps
- `cycles` - list of cycle counts
- `models` - list of model names
- `methods` - either one method list or multiple method sets

Example:

```json
{
  "shared": {
    "backend": "mock",
    "output_root": "srp_experiment/results/batch_runs"
  },
  "runs": [
    {
      "name": "mock_core_methods",
      "cycles": [3, 5, 7],
      "models": ["gpt-4o-mini"],
      "methods": [["raw_prompt", "summarization", "rag", "srp"]]
    }
  ]
}
```

### Collect Batch Results

After a batch sweep finishes, merge all run summaries into one table:

```powershell
python srp_experiment/collect_batch_summary.py
```

This reads every `summary.json` under `results/batch_runs/`, pairs it with `run_metadata.json`, and writes JSON, CSV, and Markdown tables.

### Format Final Paper Table

After collecting the long-form summary table, compress it into a wide paper table:

```powershell
python srp_experiment/paper_table_formatter.py
```

This reads `batch_summary_table.json` and writes a compact Markdown table plus a LaTeX `table*` block you can paste into the draft.

For a more ACL/NeurIPS-style presentation, the formatter also writes a separate quality table and efficiency table.
It also writes a guardrail table that summarizes:

- `commit_rate`
- `mean_validation_drift`
- `rollback_count`

Methods without SRP-style commit/rollback semantics are expected to show `-` in that table.

It also writes a camera-ready table that keeps only SRP and the strongest baseline in each row.
