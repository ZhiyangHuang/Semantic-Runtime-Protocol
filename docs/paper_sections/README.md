# Paper Sections Index

This folder stores the paper skeleton and section drafts in paper-skeleton order.
It is the long-term writing structure that feeds `first_paper/`, not the submit-ready paper package itself.

Top-level paper-sequence goal:

This is the first SRP paper, and it is also the base layer for the later SRP paper sequence. It must stay narrow, credible, and reusable within one semester of focused refinement.

Protocol principle:

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

The surrounding documentation uses a shared disclosure vocabulary:

- formal evidence
- legacy archive
- refactor rerun

## Recommended Reading Order

1. `01_Introduction.md` - states the problem and the main claim
2. `02_Related_Work.md` - positions the paper against prompt, memory, agent, and evaluation work
3. `03_Formalization.md` - defines semantic state, operators, and bounded drift
4. `04_Experiment_Section.md` - specifies tasks, baselines, metrics, and ablations
5. `05_Paper_Skeleton.md` - connects the parts into the full paper outline
6. `Results_Figure_Main_Block.md` - preserves the review-facing main results block and evidence binding
7. `Benchmark_Selection_and_Adapter.md` - defines the public benchmark layer and SRP adapter schema
8. `SRP_Execution_Trace_Format.md` - defines the inspectable runtime trace and logging standard
9. `SRP_Evidence_Pipeline_v1.md` - defines the paper-facing evidence pipeline and artifact contract
10. `SRP_Submission_Freeze_Checklist.md` - defines the final compile, reviewer, and packaging freeze gate
11. `LongBench_v2_Frozen_Eval_Plan.md` - freezes the public benchmark choice, five comparison modes, and 100/1000-cycle reusable config
12. `Unified_Evaluation_Regime.md` - fixes the shared token-bounded comparison regime and restores the baseline definitions

## Section Purpose

- `01_Introduction.md` - introduce the runtime framing and narrow claim
- `02_Related_Work.md` - explain the gap and novelty boundary
- `03_Formalization.md` - provide the smallest defensible formal model
- `04_Experiment_Section.md` - make the evaluation plan concrete and replayable
- `05_Paper_Skeleton.md` - preserve the full paper structure and writing order
- `Results_Figure_Main_Block.md` - preserve the compressed results narrative, caption, and evidence map
- `Benchmark_Selection_and_Adapter.md` - preserve the benchmark selection rationale and adapter mapping rules
- `SRP_Execution_Trace_Format.md` - preserve the state-transition trace and reviewer-facing logging contract
- `SRP_Evidence_Pipeline_v1.md` - preserve the pipeline that binds traces, reducers, figures, and tables
- `SRP_Submission_Freeze_Checklist.md` - preserve the final submission qualification checks and zip packaging rules
- `LongBench_v2_Frozen_Eval_Plan.md` - preserve the frozen public benchmark layer and reusable long-horizon plan
- `Unified_Evaluation_Regime.md` - preserve the fair shared budget regime and the restored baseline semantics

## Notes

- The section drafts are scoped to the current first-paper version.
- Open questions are preserved instead of being closed too early.
- If you need the fastest path from draft to paper, start with `01`, then `03`, then `04`, and return to `02` for positioning polish.
