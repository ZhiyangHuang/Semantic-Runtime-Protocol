# SRP Experiment Dependency Map

This document is a fact map, not a migration plan.
It classifies every observed `srp_experiment` reference into one of four buckets so we can restore the repository boundary before deciding what to delete.

## Summary

- Active runtime dependencies found in `srp_runtime/`: none.
- Evaluation dependencies: current benchmark and external-validation adapters still import `srp_experiment`.
- Release / reproducibility dependencies: the release README and verification script still require legacy evidence files.
- Historical references: archive documents refer to `srp_experiment` as background evidence or early implementation history.

## A. Active Runtime Dependencies

Status: `none found`

Search result:

- `rg -n "srp_experiment" srp_runtime`

Interpretation:

- No files under `srp_runtime/` currently import `srp_experiment`.
- That means the active runtime boundary is already mostly separated from the legacy stack.
- The remaining dependency pressure is coming from evaluation, external validation, and archive documentation.

## B. Evaluation Dependencies

These are executable code paths outside `srp_runtime/` that still import the legacy stack.

| File | Reference | Role |
| --- | --- | --- |
| `experiments/evaluation/semantic_backend_comparison/local_model_backend.py` | `srp_experiment.local_llm`, `srp_experiment.srp.encoder`, `srp_experiment.srp.llm_judge` | Local-model compatibility backend for semantic comparison |
| `experiments/evaluation/semantic_backend_comparison/vector_backend.py` | `srp_experiment.srp.encoder` | Vector backend for semantic comparison |
| `experiments/evaluation/phase_v_retention/metrics.py` | `srp_experiment.srp.semantic_parser` | Legacy semantic parsing helper for retention metrics |
| `experiments/external_validation/baselines.py` | `srp_experiment.srp.encoder` | Baseline scoring and similarity utilities |
| `experiments/external_validation/evidence.py` | `srp_experiment.local_llm` | Evidence-package generation and scoring support |

Interpretation:

- These are the first files to inspect if we want to replace the legacy stack with `srp_runtime`.
- They are not yet safe to rewrite blindly because they may be the only bridge between historical evidence and current paper-facing outputs.
- The `semantic_backend_comparison` path is especially sensitive because it acts like a compatibility layer rather than a pure runtime module.

## C. Release / Reproducibility Dependencies

These files keep `srp_experiment` alive because the release snapshot still treats it as part of the reproducibility surface.

| File | Reference | Role |
| --- | --- | --- |
| `README.md` | `srp_experiment/` description | Repository boundary statement |
| `scripts/verify_release.py` | legacy required paths under `srp_experiment/` | Release hygiene gate |

Interpretation:

- The repository currently still advertises `srp_experiment` as a retained evidence layer.
- `verify_release.py` still requires a small set of legacy files so the release snapshot remains reproducible.
- These are boundary-definition dependencies, not active algorithm dependencies.

## D. Historical References

These are archive documents that treat `srp_experiment` as historical evidence, early implementation, or a runtime projection.

| File | Reference type | Notes |
| --- | --- | --- |
| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` | background / historical evidence | Explicitly frames `srp_experiment` as background evidence |
| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` | artifact path reference | Refers to `srp_experiment/tmp/...` outputs |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` | implementation mapping | Maps current legacy implementation to runtime concepts |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md` | implementation mapping | Same, but for event processing |
| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` | empirical / historical layer | Explicitly says the legacy stack remains the evidence layer |
| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` | parameter reference | Refers to legacy helpers and budget config |
| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` | parameter reference | Mentions legacy helper functions |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | artifact path reference | References `srp_experiment/tmp/fixed_harnesses/` outputs |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` | adapter planning | Uses `srp_experiment` as the source side of a migration boundary |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_API_MAP.md` | implementation mapping | Maps the legacy implementation to future runtime APIs |
| `audit/provenance/docs_archive/SRP_RUNTIME_PROTOCOL_MAP.md` | implementation mapping | Maps legacy modules to runtime object/data-contract layers |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` | target-state mapping | Treats `srp_experiment` as the current baseline being projected away from |
| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` | projection note | Describes a legacy package as an early projection of the model |
| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` | report references | Cites legacy schemas and tests |
| `audit/provenance/docs_archive/SRP_THEORY_MAP.md` | historical framing | Calls the legacy stack a maintained background layer |

Interpretation:

- These files are evidence and archive material, not active runtime code.
- They should usually be updated only if the boundary language changes.
- They are useful for reconstructing why the old stack exists, but they should not drive the current runtime implementation.

## What This Means

Current reading:

- `srp_runtime/` is the active runtime boundary.
- `srp_experiment/` is still needed for evaluation and reproducibility in a few places.
- Archive documents still cite the legacy stack heavily, but only as background evidence.

Most important practical conclusion:

- we can start by reducing evaluation dependencies one by one
- we should not delete `srp_experiment` yet
- we should first decide whether each remaining reference is a runtime bridge, a benchmark adapter, a release requirement, or a frozen archive citation

## Next Inspection Targets

If we continue the recovery in order, the next files to inspect are:

1. `experiments/evaluation/semantic_backend_comparison/local_model_backend.py`
2. `experiments/evaluation/semantic_backend_comparison/vector_backend.py`
3. `experiments/external_validation/baselines.py`
4. `experiments/external_validation/evidence.py`
5. `scripts/verify_release.py`

Those are the most likely places where the legacy stack is still functionally necessary.

