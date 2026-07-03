# Tools Index

This file classifies the experiment tools by role so the repository does not feel flat and over-coupled.

## Primary User-Facing Tools

- `longbench_launcher.py`
- `run_experiment.py`
- `run_qualified_experiment.py`
- `batch_run.py`
- `collect_batch_summary.py`
- `repeat_aggregate.py`
- `long_horizon_report.py`

These are the tools a normal semester-phase experiment workflow should rely on.

Read [ENTRYPOINT_EXECUTION_MAP.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/ENTRYPOINT_EXECUTION_MAP.md) first if you are unsure which of them should be treated as the real entrypoint for a given run.

## Preflight / Runtime Support

- `check_env_alignment.py`
- `check_local_backend.py`
- `progress_popup.py`
- `env_utils.py`
- `model_backend.py`
- `prompting.py`
- `budgeting.py`

These support execution, environment sanity, backend stability, and fair token budgeting.

## Paper / Artifact Support

- `paper_table_formatter.py`
- `plot_results.py`
- `build_main_figure.py`
- `evidence_pipeline.py`
- `srp_cli.py`

These help turn experiment outputs into paper-facing artifacts.

## Qualification / Audit Support

- `experiment_qualification.py`
- `run_qualified_batch.py`

These are workflow gatekeepers rather than the core experimental logic.

## Wrapper Scripts

- `first-paper-run.ps1`
- `comparison-run.ps1`
- `run-longbench-smoke.ps1`
- `run-longbench-batch-with-popup.ps1`

These are convenience wrappers. The experiment framework should remain understandable even if these scripts are not used.

## Diagnostics

- `protocol_behavior_trace.py`
- `runtime_equivalence_test.py`

These should remain preserved because they improve inspectability and reviewer confidence, but they should not be treated as the main experiment entrypoints.

## Rule

When two files seem similar, prefer the primary user-facing tool first, then the support layer, then diagnostics.
