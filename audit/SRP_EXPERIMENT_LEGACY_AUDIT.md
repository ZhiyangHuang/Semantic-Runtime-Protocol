# SRP Experiment Legacy Audit

This document records the Phase 3 legacy review of `srp_experiment/`.

The goal is not to migrate code, delete code, or change runtime logic.
The goal is to make the remaining legacy references explicit so the repository boundary can continue to harden without ambiguity.

## Summary

Current status:

- `srp_experiment/` is a frozen legacy evidence layer.
- `srp_runtime/` has no direct dependency on `srp_experiment/`.
- Remaining references are concentrated in evaluation code, documentation, and release scripts.

## 1. Runtime Boundary

### Finding

- No files under `srp_runtime/` currently import `srp_experiment`.

### Decision

- Keep the runtime boundary at zero direct dependency.
- Do not introduce new runtime imports from `srp_experiment`.

### Interpretation

This is the most important invariant in the audit.
The active runtime source of truth remains isolated from the legacy evidence layer.

## 2. Active Experiment Dependencies

These are the current cross-layer references that keep `srp_experiment/` alive in active evaluation code.
They are allowed for now because they support reproducibility and evidence generation.

| Location | Legacy Reference | Role | Decision |
| --- | --- | --- | --- |
| `experiments/evaluation/semantic_backend_comparison/local_model_backend.py` | `srp_experiment.local_llm`, `srp_experiment.srp.encoder`, `srp_experiment.srp.llm_judge` | Local-model compatibility backend for semantic comparison | Keep |
| `experiments/evaluation/semantic_backend_comparison/vector_backend.py` | `srp_experiment.srp.encoder` | Vector baseline for semantic comparison | Keep |
| `experiments/evaluation/phase_v_retention/metrics.py` | `srp_experiment.srp.semantic_parser` | Legacy semantic parsing helper for retention metrics | Keep |
| `experiments/external_validation/baselines.py` | `srp_experiment.srp.encoder` | Baseline scoring and similarity utilities | Keep |
| `experiments/external_validation/evidence.py` | `srp_experiment.local_llm` | Evidence-package generation and scoring support | Keep |

### Candidate Cleanup Notes

These references are the most likely future extraction candidates if a shared helper layer is created later:

- `srp_experiment.local_llm`
- `srp_experiment.srp.encoder`
- `srp_experiment.srp.semantic_parser`
- `srp_experiment.srp.llm_judge`

For now, they remain in place because they support the frozen evaluation bundles already promoted into `artifacts/`.

## 3. Documentation References

These files refer to `srp_experiment/` as background evidence, historical implementation, or a migration source.

| Location | Type | Decision | Notes |
| --- | --- | --- | --- |
| `README.md` | public documentation | Update if needed | The top-level README now describes `srp_experiment/` as a legacy measurement and runtime evidence stack. |
| `audit/README.md` | governance index | Keep | Explicitly frames `srp_experiment/` as legacy. |
| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` | architecture contract | Keep | Declares `srp_experiment/` as legacy evidence and compatibility support. |
| `audit/ARTIFACT_POLICY.md` | policy | Keep | Uses legacy status consistently. |
| `audit/CLAIM_EVIDENCE_MAP.md` | claim ledger | Keep | Treats `srp_experiment/` as legacy evidence, not source of truth. |
| `audit/RELEASE_CHECKLIST.md` | release gate | Keep | Checks that legacy evidence remains frozen. |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | dependency map | Keep | This is the factual precursor for the legacy audit. |
| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` | historical evidence | Keep | Explicitly frames `srp_experiment/` as background evidence. |
| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` | artifact path reference | Keep | Refers to legacy `srp_experiment/tmp/...` outputs. |
| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` | historical planning | Keep | Notes the legacy stack remains the evidence layer. |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | artifact path reference | Keep | References legacy fixed-harness outputs. |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` | migration planning | Keep | Uses `srp_experiment` as the source side of a migration boundary. |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` | target-state mapping | Keep | Treats `srp_experiment` as the current baseline being projected away from. |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` | implementation mapping | Keep | Maps `srp_experiment/srp/` to runtime concepts without changing code. |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md` | implementation mapping | Keep | Maps legacy modules to event processing concepts. |
| `audit/provenance/docs_archive/SRP_RUNTIME_API_MAP.md` | API mapping | Keep | Legacy-to-future mapping document. |
| `audit/provenance/docs_archive/SRP_RUNTIME_PROTOCOL_MAP.md` | protocol mapping | Keep | Legacy-to-future mapping document. |
| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` | model framing | Keep | Refers to the current `srp_experiment.srp.semantic_graph` package as an early projection. |
| `audit/provenance/docs_archive/SRP_THEORY_MAP.md` | theory framing | Keep | Describes the legacy measurement stack as a background layer. |
| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` | parameter catalog | Keep | References legacy `srp_experiment` paths as supporting detail. |
| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` | parameter model | Keep | References legacy `srp_experiment` modules as supporting detail. |
| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` | historical report | Keep | References legacy schema and tests. |

### Interpretation

These references are not active runtime dependencies.
They are historical or explanatory references that help preserve provenance and reviewer context.

## 4. Release Scripts

The release script still treats a subset of `srp_experiment/` files as required legacy evidence.

| Location | Type | Decision | Notes |
| --- | --- | --- | --- |
| `scripts/verify_release.py` | release script | Keep for now | Still checks legacy evidence paths separately from core runtime paths. |

### Interpretation

This is intentional at the current checkpoint.
The release script is still encoding the boundary that says legacy evidence remains part of the reproducibility surface.

## 5. Legacy Layer Self-References

`srp_experiment/` still contains extensive self-references within its own package tree.

These are expected because the layer is still a complete historical implementation and harness package.

Representative self-contained areas include:

- `srp_experiment/tests/`
- `srp_experiment/analysis/`
- `srp_experiment/mechanism_ablation/`
- `srp_experiment/data/longbench_v2/`
- `srp_experiment/srp/`
- `srp_experiment/run_*.py`

### Decision

- Keep these references frozen for now.
- Do not remove or rewrite them in this phase.
- Revisit only after the runtime boundary and release boundary are stable for a later cleanup phase.

## 6. Migration Candidates

The following are the most plausible future cleanup candidates, but they are not to be moved in this phase:

| File or Symbol | Reason | Future Action |
| --- | --- | --- |
| `srp_experiment.local_llm` | shared local-model client helper | Potential extraction into a shared helper or runtime-adjacent utility later |
| `srp_experiment.srp.encoder` | shared similarity/encoding helper | Potential extraction if a common utility layer is introduced |
| `srp_experiment.srp.semantic_parser` | normalization helper | Potential extraction if shared parsing utilities are formalized |
| `srp_experiment.srp.llm_judge` | evidence judgment helper | Potential extraction if evidence tooling is consolidated |
| `README.md` legacy wording | public boundary phrasing | Update only if public documentation drifts from the freeze declaration |

## 7. Audit Conclusion

The legacy audit supports three conclusions:

1. The active runtime boundary is already clean.
2. The remaining `srp_experiment` references are mostly evaluation, documentation, or release-script references.
3. The legacy layer is still intentionally preserved for reproducibility and historical traceability.

That means the right next step is not deletion.
The right next step is to keep the legacy layer frozen and revisit cleanup only after any future runtime extraction or shared-helper consolidation is explicitly planned.


