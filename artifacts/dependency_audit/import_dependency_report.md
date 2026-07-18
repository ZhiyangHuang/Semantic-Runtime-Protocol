# Legacy Dependency Report

This report enumerates references to `docs/` and `srp_experiment/` that matter for repository deletion planning.

## Summary

- total hits: `454`
- blocking hits: `22`

### Priority Ladder

| Priority | Category | Meaning |
| --- | --- | --- |
| `P0` | `runtime_imports` | Live experiment code still depends on `srp_experiment` at runtime. |
| `P1` | `tooling_imports` | Scripts, generators, and maintenance tools still depend on `srp_experiment`. |
| `P2` | `test_imports` | Tests still depend on `srp_experiment`; important, but usually lower risk than live code. |
| `P3` | `markdown_references` / `audit_references` / `historical_mentions` | Informative references that do not by themselves block deletion. |

### Deletion Readiness

| Category | Priority | Count | Blocks deletion? | Ready for deletion? |
| --- | --- | ---: | :---: | :---: |
| `runtime_imports` | `P0` | `0` | `yes` | `no` |
| `tooling_imports` | `P1` | `0` | `yes` | `no` |
| `test_imports` | `P2` | `22` | `yes` | `no` |
| `audit_references` | `P3` | `302` | `no` | `yes` |
| `historical_mentions` | `P3` | `67` | `no` | `yes` |
| `markdown_references` | `P3` | `63` | `no` | `yes` |

### Blocking Counts

| Category | Blocking Count |
| --- | ---: |
| `test_imports` | `22` |

### Migration Velocity

| Category | Baseline | Remaining | Completed | Completion |
| --- | ---: | ---: | ---: | ---: |
| `runtime_imports` | `20` | `0` | `20` | `1` |
| `tooling_imports` | `28` | `0` | `28` | `1` |
| `test_imports` | `87` | `22` | `65` | `0.747126` |

### By Kind

| Kind | Count |
| --- | ---: |
| `docs_archive` | `62` |
| `import` | `22` |
| `srp_experiment` | `370` |

### By Category

| Category | Count | Blocks deletion? |
| --- | ---: | :---: |
| `runtime_imports` | `0` | `yes` |
| `tooling_imports` | `0` | `yes` |
| `test_imports` | `22` | `yes` |
| `audit_references` | `302` | `no` |
| `historical_mentions` | `67` | `no` |
| `markdown_references` | `63` | `no` |

### By File

| File | Count |
| --- | ---: |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `56` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `43` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `37` |
| `audit/PHASE_6_TEST_FREEZE.md` | `32` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `14` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `13` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `12` |
| `audit/release_manifest.json` | `12` |
| `scripts/find_dependency_refs.py` | `12` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `11` |
| `audit/PHASE_6_DELETION_READINESS.md` | `11` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `10` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `9` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `8` |
| `audit/PHASE_6_CLUSTER_C.md` | `8` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `8` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `6` |
| `audit/PHASE_6_CLUSTER_A.md` | `6` |
| `audit/PHASE_6_CLUSTER_D.md` | `6` |
| `audit/PHASE_6_CLUSTER_E.md` | `6` |
| `audit/PHASE_6_CLUSTER_F2.md` | `5` |
| `audit/PHASE_6_CLUSTER_G1.md` | `5` |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | `5` |
| `scripts/verify_release.py` | `5` |
| `audit/PHASE_6_5_CLUSTER_A.md` | `4` |
| `audit/PHASE_6_CLUSTER_F.md` | `4` |
| `audit/PHASE_6_CLUSTER_I.md` | `4` |
| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` | `4` |
| `srp_experiment/tests/test_longbench_v2_prototype.py` | `4` |
| `audit/EXPERIMENT_TRUTH_AUDIT.md` | `3` |
| `audit/PHASE_6_TEST_MIGRATION_POLICY.md` | `3` |
| `audit/RELEASE_CANDIDATE_CONSISTENCY_REVIEW.md` | `3` |
| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` | `3` |
| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` | `3` |
| `audit/provenance/srp_experiment/data/longbench_v2/manifest.json` | `3` |
| `srp_experiment/data/longbench_v2/manifest.json` | `3` |
| `README.md` | `2` |
| `audit/ARTIFACT_POLICY.md` | `2` |
| `audit/CLAIM_EVIDENCE_MAP.md` | `2` |
| `audit/PHASE_6_5_CLUSTER_A1.md` | `2` |
| `audit/PHASE_6_CLUSTER_B.md` | `2` |
| `audit/PHASE_6_CLUSTER_G2.md` | `2` |
| `audit/PHASE_6_CLUSTER_H2A.md` | `2` |
| `audit/README.md` | `2` |
| `audit/REPRODUCIBILITY_AND_DEPENDENCY_MAP.md` | `2` |
| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` | `2` |
| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` | `2` |
| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` | `2` |
| `experiments/srp_runtime_legacy/run_coverage_attribution.py` | `2` |
| `experiments/srp_runtime_legacy/run_decision_attribution.py` | `2` |
| `srp_experiment/tests/test_srp_runtime.py` | `2` |
| `ARTIFACT_README.md` | `1` |
| `audit/PAPER_SOURCE_REFERENCE_AUDIT.md` | `1` |
| `audit/PHASE_6_5_CLUSTER_B.md` | `1` |
| `audit/PHASE_6_CLUSTER_H1.md` | `1` |
| `audit/PHASE_6_FINAL_CONSOLIDATION_SUMMARY.md` | `1` |
| `audit/PHASE_6_TEST_CLASSIFICATION.md` | `1` |
| `audit/RELEASE_CHECKLIST.md` | `1` |
| `audit/RELEASE_HARDENING_RESULT.md` | `1` |
| `audit/provenance/README.md` | `1` |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` | `1` |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md` | `1` |
| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` | `1` |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` | `1` |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_API_MAP.md` | `1` |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` | `1` |
| `audit/provenance/docs_archive/SRP_RUNTIME_PROTOCOL_MAP.md` | `1` |
| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` | `1` |
| `audit/provenance/docs_archive/SRP_THEORY_MAP.md` | `1` |
| `audit/provenance/srp_experiment/README.md` | `1` |
| `audit/provenance/srp_experiment/data/longbench_v2/import_longbench_v2.py` | `1` |
| `audit/provenance/srp_experiment/migration_manifest.json` | `1` |
| `audit/provenance/srp_experiment/schemas/experiment_result_schema_v1.json` | `1` |
| `audit/provenance/srp_experiment/schemas/semantic_runtime_graph_schema_v1.json` | `1` |
| `audit/provenance/srp_experiment/schemas/semantic_runtime_graph_schema_v1_5.json` | `1` |
| `experiments/srp_runtime_legacy/export_csv.py` | `1` |
| `experiments/srp_runtime_legacy/export_markdown.py` | `1` |
| `experiments/srp_runtime_legacy/run_controlled_harness.py` | `1` |
| `experiments/srp_runtime_legacy/run_fixed_harnesses.py` | `1` |
| `experiments/srp_runtime_legacy/run_graph_recovery_evaluation.py` | `1` |
| `experiments/srp_runtime_legacy/run_graph_representation_ablation.py` | `1` |
| `experiments/srp_runtime_legacy/run_mechanism_attribution_ablation.py` | `1` |
| `experiments/srp_runtime_legacy/run_object_aware_compression.py` | `1` |
| `experiments/srp_runtime_legacy/run_object_aware_threshold_analysis.py` | `1` |
| `experiments/srp_runtime_legacy/run_object_aware_threshold_sampling.py` | `1` |
| `experiments/srp_runtime_legacy/run_policy_boundary_analysis.py` | `1` |
| `experiments/srp_runtime_legacy/run_policy_boundary_drift.py` | `1` |
| `experiments/srp_runtime_legacy/run_policy_boundary_robustness.py` | `1` |
| `experiments/srp_runtime_legacy/run_policy_intervention.py` | `1` |
| `experiments/srp_runtime_legacy/run_policy_sensitivity.py` | `1` |
| `experiments/srp_runtime_legacy/run_reconstruction_policy_comparison.py` | `1` |
| `experiments/srp_runtime_legacy/run_recovery_ablation.py` | `1` |
| `srp_experiment/data/longbench_v2/import_longbench_v2.py` | `1` |
| `srp_experiment/export_csv.py` | `1` |

## Hits

| File | Line | Kind | Category | Text |
| --- | ---: | --- | --- | --- |
| `ARTIFACT_README.md` | `14` | `docs_archive` | `markdown_references` | `- `audit/provenance/docs_archive/`: historical research documents preserved for provenance` |
| `README.md` | `10` | `srp_experiment` | `markdown_references` | `- `srp_experiment/` holds the legacy measurement and runtime evidence stack; it is retained as a historical evidence layer, not the primary runtime implementation.` |
| `README.md` | `14` | `docs_archive` | `markdown_references` | `- `audit/provenance/docs_archive/` holds historical research documents that are not needed in the main release path.` |
| `audit/ARTIFACT_POLICY.md` | `238` | `srp_experiment` | `audit_references` | ``srp_experiment/` is treated as a legacy evidence layer and historical implementation substrate.` |
| `audit/ARTIFACT_POLICY.md` | `243` | `srp_experiment` | `audit_references` | `- `srp_experiment/` may generate or explain historical evidence` |
| `audit/CLAIM_EVIDENCE_MAP.md` | `109` | `srp_experiment` | `audit_references` | `The active SRP runtime does not depend on the evaluation infrastructure, and `srp_experiment/` is a legacy evidence layer rather than the source of truth for runtime semantics.` |
| `audit/CLAIM_EVIDENCE_MAP.md` | `115` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is treated as historical evidence and compatibility support.` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `1` | `srp_experiment` | `audit_references` | `# Delete `docs/` and `srp_experiment/` Preparation` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `3` | `srp_experiment` | `audit_references` | `This document prepares the repository for a future removal of `docs/` and `srp_experiment/`.` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `11` | `srp_experiment` | `audit_references` | `- `srp_experiment/`` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `16` | `srp_experiment` | `audit_references` | `- `srp_experiment/` contains `234` tracked files` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `29` | `srp_experiment` | `audit_references` | `### `srp_experiment/`` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `31` | `srp_experiment` | `audit_references` | `The `srp_experiment/` tree is the frozen legacy experiment and evidence layer.` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `42` | `srp_experiment` | `audit_references` | `Test coverage also still references `srp_experiment/` extensively.` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `49` | `srp_experiment` | `audit_references` | `- no active runtime or evaluation code imports `srp_experiment/`` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `50` | `srp_experiment` | `audit_references` | `- no tests import `srp_experiment/` as a live dependency` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `58` | `srp_experiment` | `audit_references` | `3. Replace the active `srp_experiment/` imports with active `srp_runtime/` or shared utility modules.` |
| `audit/DELETE_DOCS_SRP_EXPERIMENT_PREP.md` | `62` | `srp_experiment` | `audit_references` | `7. Only then delete the old `docs/` and `srp_experiment/` trees.` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `3` | `srp_experiment` | `audit_references` | `This checklist turns the future removal of `docs/` and `srp_experiment/` into a deletion-readiness plan.` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/`` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `48` | `docs_archive` | `markdown_references` | `- archive documents under `audit/provenance/docs_archive/`` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `50` | `srp_experiment` | `audit_references` | `### `srp_experiment/`` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `58` | `srp_experiment` | `audit_references` | `- audit documents that describe `srp_experiment/` as frozen legacy evidence` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `66` | `srp_experiment` | `audit_references` | `\| [x] \| Generate a full dependency report for `docs/` and `srp_experiment/` references \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `67` | `docs_archive` | `markdown_references` | `\| [x] \| Replace `scripts/verify_release.py` hardcoded `audit/provenance/docs_archive/README.md` dependency with audit manifest \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `69` | `srp_experiment` | `audit_references` | `\| [x] \| Replace `P0` runtime imports from `srp_experiment` in `experiments/` \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `70` | `srp_experiment` | `audit_references` | `\| [x] \| Replace `P1` tooling imports from `srp_experiment` in scripts and generators \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `72` | `srp_experiment` | `audit_references` | `\| [ ] \| Move approved live-behavior tests off `srp_experiment` imports where a live replacement exists \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `75` | `srp_experiment` | `audit_references` | `\| [ ] \| Replace `srp_experiment` imports in `experiments/external_validation/` \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `82` | `srp_experiment` | `audit_references` | `\| [ ] \| Delete `srp_experiment/` only after the tree is dependency-free \| Yes \|  \|` |
| `audit/DELETE_MIGRATION_CHECKLIST.md` | `93` | `srp_experiment` | `audit_references` | `8. Delete the core `srp_experiment/` implementation once preserved compatibility assets are isolated.` |
| `audit/EXPERIMENT_TRUTH_AUDIT.md` | `17` | `srp_experiment` | `audit_references` | `\| Evidence can strengthen verification without increasing authority \| `experiments/sensitivity/interaction/runner.py`, `experiments/external_validation/evidence.py` \| `interaction_boundary_enforcement`, `SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md` \| `srp_runtime/`, `experiments/`, legacy `srp_experiment/` helper paths \| PASS \|` |
| `audit/EXPERIMENT_TRUTH_AUDIT.md` | `19` | `srp_experiment` | `audit_references` | `\| SRP runtime is independent from evaluation infrastructure \| `scripts/verify_release.py`, static dependency scans \| `SRP_EXPERIMENT_DEPENDENCY_MAP.md`, `REPO_ARCHITECTURE_BLUEPRINT.md`, `SRP_V1_STATIC_AUDIT_MAPPING.md` \| `srp_runtime/`, `experiments/`, `srp_experiment/` (legacy only) \| PASS \|` |
| `audit/EXPERIMENT_TRUTH_AUDIT.md` | `29` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is intentionally retained as a frozen legacy evidence layer and appears only in the dependency chain where legacy helper code is still required.` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `3` | `srp_experiment` | `audit_references` | `This document records modules in `srp_experiment/` that may become candidates for future extraction or consolidation.` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `17` | `srp_experiment` | `audit_references` | `\| `srp_experiment.local_llm` \| Evaluation backend and local model client helper \| Possible move to a shared evaluation/backend utility layer \| Keep frozen for now \|` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `18` | `srp_experiment` | `audit_references` | `\| `srp_experiment.srp.encoder` \| Shared semantic similarity and encoding utility \| Possible extraction into a common helper module \| Keep frozen for now \|` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `19` | `srp_experiment` | `audit_references` | `\| `srp_experiment.srp.semantic_parser` \| Experiment helper for semantic normalization \| Possible extraction if parsing utilities are formalized elsewhere \| Keep frozen for now \|` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `20` | `srp_experiment` | `audit_references` | `\| `srp_experiment.srp.llm_judge` \| Evaluation component for evidence judgment \| Likely to remain outside the active runtime boundary \| Keep frozen for now \|` |
| `audit/LEGACY_EXTRACTION_CANDIDATES.md` | `46` | `srp_experiment` | `audit_references` | `srp_experiment` |
| `audit/PAPER_SOURCE_REFERENCE_AUDIT.md` | `33` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_PAPER_DRAFT_V1.md` \| References `SRP_RELATED_WORK_V1.md` as supporting context in historical material \| PASS \| Archive references are historical and do not affect current manuscript hierarchy. \|` |
| `audit/PHASE_6_5_CLUSTER_A.md` | `5` | `docs_archive` | `markdown_references` | `Relocate the archive document tree from `docs/archive/` to `audit/provenance/docs_archive/`.` |
| `audit/PHASE_6_5_CLUSTER_A.md` | `16` | `docs_archive` | `markdown_references` | `audit/provenance/docs_archive/` |
| `audit/PHASE_6_5_CLUSTER_A.md` | `26` | `docs_archive` | `markdown_references` | `- moved the historical archive document tree into `audit/provenance/docs_archive/`` |
| `audit/PHASE_6_5_CLUSTER_A.md` | `38` | `docs_archive` | `markdown_references` | ``audit/provenance/docs_archive/` is the preserved provenance home.` |
| `audit/PHASE_6_5_CLUSTER_A1.md` | `5` | `docs_archive` | `markdown_references` | `Retire the empty `docs/archive/` shell after the archive contents have been relocated to `audit/provenance/docs_archive/`.` |
| `audit/PHASE_6_5_CLUSTER_A1.md` | `39` | `docs_archive` | `markdown_references` | `Historical archive evidence now lives only under `audit/provenance/docs_archive/`.` |
| `audit/PHASE_6_5_CLUSTER_B.md` | `5` | `srp_experiment` | `audit_references` | `Freeze the `srp_experiment/` asset inventory before any separation or archival work begins.` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `5` | `srp_experiment` | `audit_references` | `Move provenance-only `srp_experiment/` assets into `audit/provenance/srp_experiment/`.` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `9` | `srp_experiment` | `audit_references` | `- `srp_experiment/README.md`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `10` | `srp_experiment` | `audit_references` | `- `srp_experiment/local_llm.py`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `11` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_local_diagnostics.py`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/data/longbench_v2/`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/schemas/`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `14` | `srp_experiment` | `audit_references` | `- `srp_experiment/tmp/`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `19` | `srp_experiment` | `audit_references` | `audit/provenance/srp_experiment/` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `26` | `srp_experiment` | `audit_references` | `- `audit/provenance/srp_experiment/README.md`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `27` | `srp_experiment` | `audit_references` | `- `audit/provenance/srp_experiment/migration_manifest.json`` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `36` | `srp_experiment` | `audit_references` | `The historical `srp_experiment/` documentation, schema snapshots, scratch traces, and legacy evidence helpers now live under `audit/provenance/srp_experiment/`.` |
| `audit/PHASE_6_5_CLUSTER_B2.md` | `37` | `srp_experiment` | `audit_references` | `The remaining `srp_experiment/` tree is focused on compatibility assets and deletion candidates.` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `1` | `srp_experiment` | `audit_references` | `# Phase 6.5-B3 `srp_experiment/` Implementation Removal` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `3` | `srp_experiment` | `audit_references` | `This checkpoint freezes the last migrated implementation surface inside `srp_experiment/` and removes only the duplicate implementation files that now have live owners.` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `15` | `srp_experiment` | `audit_references` | `- `srp_experiment/analysis/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `16` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `17` | `srp_experiment` | `audit_references` | `- `srp_experiment/eval/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `24` | `srp_experiment` | `audit_references` | `- `srp_experiment/analysis/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `25` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `26` | `srp_experiment` | `audit_references` | `- `srp_experiment/eval/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `33` | `srp_experiment` | `audit_references` | `- `srp_experiment/srp/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `34` | `srp_experiment` | `audit_references` | `- `srp_experiment/data/longbench_v2/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `35` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_csv.py`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `36` | `srp_experiment` | `audit_references` | `- `srp_experiment/tests/`` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `47` | `srp_experiment` | `audit_references` | `Remove the migrated implementation surface from `srp_experiment/` while preserving the compatibility surface.` |
| `audit/PHASE_6_5_CLUSTER_B3.md` | `56` | `srp_experiment` | `audit_references` | `python -m compileall experiments srp_experiment` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `10` | `srp_experiment` | `audit_references` | `- `srp_experiment/`` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `16` | `docs_archive` | `markdown_references` | `- `audit/provenance/docs_archive/`` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `23` | `docs_archive` | `markdown_references` | `- `docs/archive/` legacy shell retired after relocation to `audit/provenance/docs_archive/`` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `44` | `srp_experiment` | `audit_references` | `### `srp_experiment/`` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `83` | `docs_archive` | `markdown_references` | `Keep `audit/provenance/docs_archive/` as preserved provenance.` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `102` | `srp_experiment` | `audit_references` | `Isolate the remaining `srp_experiment/` compatibility and historical assets.` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `110` | `srp_experiment` | `audit_references` | `Delete the core `srp_experiment/` implementation once the preserved assets are outside the live dependency graph.` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `124` | `docs_archive` | `markdown_references` | `- `audit/provenance/docs_archive/` remains preserved and referenced only as provenance` |
| `audit/PHASE_6_5_CONTROLLED_DELETION_PLAN.md` | `126` | `srp_experiment` | `audit_references` | `- `srp_experiment/` has no live dependency arrows and its preserved assets are isolated` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `1` | `srp_experiment` | `audit_references` | `# Phase 6.5 `srp_experiment/` Inventory Freeze` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `3` | `srp_experiment` | `audit_references` | `This inventory freezes the current `srp_experiment/` surface into three categories so later phases can isolate, archive, or remove assets without re-deriving the boundary.` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `75` | `srp_experiment` | `audit_references` | `\| `export_csv.py` \| Frozen export compatibility helper still exercised by legacy tests \| `srp_experiment/` compatibility surface \|` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `85` | `srp_experiment` | `audit_references` | `\| `README.md` \| Legacy layer description \| `audit/provenance/srp_experiment/` \|` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `86` | `srp_experiment` | `audit_references` | `\| `data/longbench_v2/` \| Historical benchmark/provenance inputs \| `audit/provenance/srp_experiment/` \|` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `87` | `srp_experiment` | `audit_references` | `\| `tmp/` \| Historical scratch outputs and audit traces \| `audit/provenance/srp_experiment/` or removal after provenance capture \|` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `88` | `srp_experiment` | `audit_references` | `\| `schemas/` \| Historical schema snapshots \| `audit/provenance/srp_experiment/` \|` |
| `audit/PHASE_6_5_SRPEXPERIMENT_INVENTORY.md` | `115` | `srp_experiment` | `audit_references` | `- `audit/provenance/srp_experiment/` for historical documentation, schemas, and legacy experiment outputs` |
| `audit/PHASE_6_CLUSTER_A.md` | `8` | `srp_experiment` | `audit_references` | `The cluster focused on the lowest-risk shared helper paths that still pointed at `srp_experiment/` from live entrypoints.` |
| `audit/PHASE_6_CLUSTER_A.md` | `16` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_csv.py`` |
| `audit/PHASE_6_CLUSTER_A.md` | `17` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_markdown.py`` |
| `audit/PHASE_6_CLUSTER_A.md` | `18` | `srp_experiment` | `audit_references` | `- `srp_experiment/verify_e5_encoder.py`` |
| `audit/PHASE_6_CLUSTER_A.md` | `19` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_local_diagnostics.py`` |
| `audit/PHASE_6_CLUSTER_A.md` | `53` | `srp_experiment` | `audit_references` | `- `python -m compileall scripts experiments\common srp_experiment`` |
| `audit/PHASE_6_CLUSTER_B.md` | `16` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/ablation_metrics.py`` |
| `audit/PHASE_6_CLUSTER_B.md` | `50` | `srp_experiment` | `audit_references` | `- `python -m compileall scripts experiments\common srp_experiment`` |
| `audit/PHASE_6_CLUSTER_C.md` | `3` | `srp_experiment` | `audit_references` | `This batch continues repository consolidation by removing a small set of live runtime dependencies on `srp_experiment/` while keeping the migration reversible and easy to audit.` |
| `audit/PHASE_6_CLUSTER_C.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/variants/common.py`` |
| `audit/PHASE_6_CLUSTER_C.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/ablation_runner.py`` |
| `audit/PHASE_6_CLUSTER_C.md` | `51` | `srp_experiment` | `audit_references` | `- `python -m compileall scripts experiments\common srp_experiment`` |
| `audit/PHASE_6_CLUSTER_C.md` | `57` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_csv.py`` |
| `audit/PHASE_6_CLUSTER_C.md` | `58` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_markdown.py`` |
| `audit/PHASE_6_CLUSTER_C.md` | `59` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/ablation_runner.py`` |
| `audit/PHASE_6_CLUSTER_C.md` | `60` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/variants/common.py`` |
| `audit/PHASE_6_CLUSTER_D.md` | `3` | `srp_experiment` | `audit_references` | `This batch removes the last export-wrapper runtime dependency arrows from `srp_experiment/` by narrowing the wrappers to pure record-formatting entrypoints.` |
| `audit/PHASE_6_CLUSTER_D.md` | `11` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_csv.py`` |
| `audit/PHASE_6_CLUSTER_D.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/export_markdown.py`` |
| `audit/PHASE_6_CLUSTER_D.md` | `50` | `srp_experiment` | `audit_references` | `- `python -m compileall scripts experiments\common srp_experiment`` |
| `audit/PHASE_6_CLUSTER_D.md` | `56` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/ablation_runner.py`` |
| `audit/PHASE_6_CLUSTER_D.md` | `57` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/variants/common.py`` |
| `audit/PHASE_6_CLUSTER_E.md` | `3` | `srp_experiment` | `audit_references` | `This batch closed the final `P0` runtime-import blocker for `srp_experiment/`.` |
| `audit/PHASE_6_CLUSTER_E.md` | `9` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/ablation_runner.py`` |
| `audit/PHASE_6_CLUSTER_E.md` | `10` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/variants/common.py`` |
| `audit/PHASE_6_CLUSTER_E.md` | `28` | `srp_experiment` | `audit_references` | `- `python -m compileall experiments\\mechanism_ablation srp_experiment\\mechanism_ablation`` |
| `audit/PHASE_6_CLUSTER_E.md` | `31` | `srp_experiment` | `audit_references` | `- `python -m unittest srp_experiment.tests.test_mechanism_attribution_ablation`` |
| `audit/PHASE_6_CLUSTER_E.md` | `41` | `srp_experiment` | `audit_references` | `The live graph no longer points to `srp_experiment/` through runtime imports.` |
| `audit/PHASE_6_CLUSTER_F.md` | `11` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_mechanism_attribution_ablation.py` -> `experiments.mechanism_ablation.ablation_runner`` |
| `audit/PHASE_6_CLUSTER_F.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_coverage_attribution.py` -> `experiments.analysis.coverage_attribution`` |
| `audit/PHASE_6_CLUSTER_F.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_decision_attribution.py` -> `experiments.analysis.decision_attribution`` |
| `audit/PHASE_6_CLUSTER_F.md` | `30` | `srp_experiment` | `audit_references` | `- `python -m compileall experiments/common experiments/analysis srp_experiment`` |
| `audit/PHASE_6_CLUSTER_F2.md` | `6` | `srp_experiment` | `audit_references` | `- Removed legacy `srp_experiment/tmp` defaults from the wrapped tooling` |
| `audit/PHASE_6_CLUSTER_F2.md` | `11` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_importance_attribution.py` -> `experiments.analysis.importance_attribution`` |
| `audit/PHASE_6_CLUSTER_F2.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_policy_attribution.py` -> `experiments.analysis.policy_attribution`` |
| `audit/PHASE_6_CLUSTER_F2.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_semantic_failure_taxonomy.py` -> `experiments.analysis.semantic_failure_taxonomy`` |
| `audit/PHASE_6_CLUSTER_F2.md` | `28` | `srp_experiment` | `audit_references` | `- `python -m compileall experiments/common experiments/analysis srp_experiment`` |
| `audit/PHASE_6_CLUSTER_G1.md` | `8` | `srp_experiment` | `audit_references` | `- Removed legacy `srp_experiment/tmp` defaults from the wrapped tooling` |
| `audit/PHASE_6_CLUSTER_G1.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_graph_information_gap_analysis.py` -> `experiments.analysis.graph_information_gap_analysis`` |
| `audit/PHASE_6_CLUSTER_G1.md` | `14` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_semantic_extraction_audit.py` -> `experiments.analysis.semantic_extraction_audit`` |
| `audit/PHASE_6_CLUSTER_G1.md` | `15` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_policy_pareto_analysis.py` -> `experiments.analysis.policy_pareto`` |
| `audit/PHASE_6_CLUSTER_G1.md` | `27` | `srp_experiment` | `audit_references` | `- `python -m compileall experiments/common experiments/analysis srp_experiment`` |
| `audit/PHASE_6_CLUSTER_G2.md` | `10` | `srp_experiment` | `audit_references` | `- Redirected the top-level `srp_experiment/*.py` tooling entrypoints to the live compatibility namespace instead of the legacy package.` |
| `audit/PHASE_6_CLUSTER_G2.md` | `22` | `srp_experiment` | `audit_references` | `- `python -m compileall experiments\\srp_runtime_legacy srp_experiment` passed` |
| `audit/PHASE_6_CLUSTER_H1.md` | `5` | `srp_experiment` | `audit_references` | `This batch migrated a first wave of live-behavior tests from `srp_experiment` imports to live namespaces.` |
| `audit/PHASE_6_CLUSTER_H2A.md` | `5` | `srp_experiment` | `audit_references` | `This batch migrated the first H2 wave of live-behavior tests from legacy `srp_experiment` imports to the live compatibility namespace.` |
| `audit/PHASE_6_CLUSTER_H2A.md` | `25` | `srp_experiment` | `audit_references` | `- `python -m unittest srp_experiment.tests.test_encoder srp_experiment.tests.test_graph_recovery_policy srp_experiment.tests.test_runtime_representation_v2 srp_experiment.tests.test_semantic_runtime_graph srp_experiment.tests.test_semantic_runtime_graph_v1_5 srp_experiment.tests.test_srp_runtime` passed` |
| `audit/PHASE_6_CLUSTER_I.md` | `5` | `docs_archive` | `markdown_references` | `Release gate decoupling from `audit/provenance/docs_archive/README.md`` |
| `audit/PHASE_6_CLUSTER_I.md` | `15` | `docs_archive` | `markdown_references` | `-> audit/provenance/docs_archive/README.md` |
| `audit/PHASE_6_CLUSTER_I.md` | `30` | `docs_archive` | `markdown_references` | `- updated `scripts/verify_release.py` to load the release manifest and check audit-owned provenance instead of requiring `audit/provenance/docs_archive/README.md`` |
| `audit/PHASE_6_CLUSTER_I.md` | `39` | `docs_archive` | `markdown_references` | ``audit/provenance/docs_archive/README.md` is no longer a release gate dependency.` |
| `audit/PHASE_6_DELETION_READINESS.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/`` |
| `audit/PHASE_6_DELETION_READINESS.md` | `24` | `srp_experiment` | `audit_references` | `### `srp_experiment/`` |
| `audit/PHASE_6_DELETION_READINESS.md` | `32` | `srp_experiment` | `audit_references` | `- live experiment code no longer depends on `srp_experiment/`` |
| `audit/PHASE_6_DELETION_READINESS.md` | `48` | `docs_archive` | `markdown_references` | `- archive material still lives under `audit/provenance/docs_archive/`` |
| `audit/PHASE_6_DELETION_READINESS.md` | `60` | `srp_experiment` | `audit_references` | `\| `srp_experiment/` core implementation \| legacy, no live runtime/tooling edges \| delete candidate \| delete only after compatibility assets are isolated \|` |
| `audit/PHASE_6_DELETION_READINESS.md` | `61` | `srp_experiment` | `audit_references` | `\| `srp_experiment/tests/legacy` \| frozen compatibility asset \| preserve \| keeps deletion boundary auditable \|` |
| `audit/PHASE_6_DELETION_READINESS.md` | `62` | `srp_experiment` | `audit_references` | `\| `srp_experiment/tests/prototype` \| historical prototype asset \| archive / retire \| depends on provenance review \|` |
| `audit/PHASE_6_DELETION_READINESS.md` | `63` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/` \| historical archive material \| preserved provenance \| no longer a release gate dependency \|` |
| `audit/PHASE_6_DELETION_READINESS.md` | `68` | `srp_experiment` | `audit_references` | `### `srp_experiment/`` |
| `audit/PHASE_6_DELETION_READINESS.md` | `101` | `docs_archive` | `markdown_references` | `- the release gate is manifest-driven and no longer requires `audit/provenance/docs_archive/README.md`` |
| `audit/PHASE_6_DELETION_READINESS.md` | `102` | `docs_archive` | `markdown_references` | `- the archive content is preserved under `audit/provenance/docs_archive/`` |
| `audit/PHASE_6_FINAL_CONSOLIDATION_SUMMARY.md` | `59` | `srp_experiment` | `audit_references` | `srp_experiment/` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `10` | `srp_experiment` | `audit_references` | `- Phase 6.5-B `srp_experiment asset separation`: active` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `32` | `srp_experiment` | `audit_references` | `- `srp_experiment/` core implementation is a delete candidate, but the legacy test/prototype surface is still preserved for provenance` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `33` | `docs_archive` | `markdown_references` | `- `audit/provenance/docs_archive/` is now provenance-only from the release-gate perspective` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `34` | `docs_archive` | `markdown_references` | `- `docs/archive/` has been retired after relocation into `audit/provenance/docs_archive/`` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `35` | `srp_experiment` | `audit_references` | `- `audit/provenance/srp_experiment/` now stores historical documentation, schemas, scratch traces, and legacy evidence helpers` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `36` | `srp_experiment` | `audit_references` | `- `srp_experiment/` has been reduced to the frozen compatibility surface plus test/prototype assets` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `38` | `srp_experiment` | `audit_references` | `- `srp_experiment/` has a frozen inventory that separates compatibility, provenance, and deletion candidates` |
| `audit/PHASE_6_PROGRESS_REPORT.md` | `43` | `srp_experiment` | `audit_references` | `- Continue the Phase 6.5-B3 implementation removal for `srp_experiment/` while preserving the frozen compatibility surface` |
| `audit/PHASE_6_TEST_CLASSIFICATION.md` | `17` | `srp_experiment` | `audit_references` | `- `legacy compatibility`: the test intentionally verifies the frozen `srp_experiment` surface and should remain until deletion is safe.` |
| `audit/PHASE_6_TEST_FREEZE.md` | `17` | `srp_experiment` | `audit_references` | ``srp_experiment/tests/test_srp_runtime_legacy_compat.py`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `21` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.pipeline.run_srp`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `22` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.compress.chunk_memory`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `23` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.compress.compress_state`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `24` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.encoder.build_encoder`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `25` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.export.flatten_record_for_csv`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `26` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.export.write_records_csv`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `27` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.semantic_parser.canonicalize_semantic_value`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `28` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.semantic_parser.stable_semantic_object_id`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `29` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.saliency.rank_memory_chunks`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `30` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.state.SemanticObjectMetadata`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `31` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.state.SemanticState`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `32` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.recover.recover_state`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `33` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.recover_runtime.budget_recovery_inputs`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `34` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.recover_runtime.recover_memory_from_package`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `35` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.state_lifecycle.apply_object_lifecycle`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `36` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.state_summaries.*`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `37` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.validate.validate_state`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `38` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.validation_failure_summary.*`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `39` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.validation_targets.build_validation_targets`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `40` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.compress_parse.parse_compressed_payload`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `41` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.object_retention.build_object_retention_breakdown`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `42` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.object_retention.build_object_retention_breakdown_v2`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `43` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.repair.build_repair_package`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `44` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.state_allocation.build_state_allocation_policy`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `45` | `srp_experiment` | `audit_references` | `- `srp_experiment.export_csv._apply_task_identity`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `49` | `srp_experiment` | `audit_references` | `- keep as a frozen legacy-compatibility asset until deletion of `srp_experiment/`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `53` | `srp_experiment` | `audit_references` | ``srp_experiment/tests/test_longbench_v2_prototype.py`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `57` | `srp_experiment` | `audit_references` | `- `srp_experiment.data.longbench_v2.import_longbench_v2.build_query`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `58` | `srp_experiment` | `audit_references` | `- `srp_experiment.data.longbench_v2.import_longbench_v2.tokenize_keywords`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `59` | `srp_experiment` | `audit_references` | `- `srp_experiment.data.longbench_v2.import_longbench_v2.transform_row`` |
| `audit/PHASE_6_TEST_FREEZE.md` | `60` | `srp_experiment` | `audit_references` | `- `srp_experiment.data.longbench_v2.split_task_groups`` |
| `audit/PHASE_6_TEST_MIGRATION_POLICY.md` | `7` | `srp_experiment` | `audit_references` | `The goal is not to make every `srp_experiment` reference disappear immediately.` |
| `audit/PHASE_6_TEST_MIGRATION_POLICY.md` | `49` | `srp_experiment` | `audit_references` | `- live-behavior tests no longer import `srp_experiment`` |
| `audit/PHASE_6_TEST_MIGRATION_POLICY.md` | `50` | `srp_experiment` | `audit_references` | `- any remaining `srp_experiment` references are explicitly tagged legacy-compatibility or archival` |
| `audit/README.md` | `74` | `srp_experiment` | `audit_references` | `Prepares a future removal of `docs/` and `srp_experiment/` after dependencies are rehomed.` |
| `audit/README.md` | `172` | `srp_experiment` | `audit_references` | ``srp_experiment/` is maintained as a legacy evidence layer.` |
| `audit/RELEASE_CANDIDATE_CONSISTENCY_REVIEW.md` | `76` | `srp_experiment` | `audit_references` | `0 srp_experiment` |
| `audit/RELEASE_CANDIDATE_CONSISTENCY_REVIEW.md` | `90` | `srp_experiment` | `audit_references` | `srp_experiment/` |
| `audit/RELEASE_CANDIDATE_CONSISTENCY_REVIEW.md` | `96` | `srp_experiment` | `audit_references` | `- `srp_experiment/README.md` declares the legacy freeze status.` |
| `audit/RELEASE_CHECKLIST.md` | `109` | `srp_experiment` | `audit_references` | `- [ ] `srp_experiment/` remains frozen as legacy evidence and compatibility support` |
| `audit/RELEASE_HARDENING_RESULT.md` | `20` | `srp_experiment` | `audit_references` | `\| Legacy boundary \| PASS \| `srp_experiment/` is frozen as a legacy evidence layer. \|` |
| `audit/release_manifest.json` | `32` | `docs_archive` | `markdown_references` | `"audit/provenance/docs_archive/README.md",` |
| `audit/release_manifest.json` | `33` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/README.md",` |
| `audit/release_manifest.json` | `34` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/migration_manifest.json",` |
| `audit/release_manifest.json` | `35` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/local_llm.py",` |
| `audit/release_manifest.json` | `36` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/run_local_diagnostics.py",` |
| `audit/release_manifest.json` | `37` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/data/longbench_v2/import_longbench_v2.py",` |
| `audit/release_manifest.json` | `38` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/data/longbench_v2/split_task_groups.py",` |
| `audit/release_manifest.json` | `39` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/data/longbench_v2/manifest.json",` |
| `audit/release_manifest.json` | `40` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/schemas/experiment_result_schema_v1.json",` |
| `audit/release_manifest.json` | `41` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/schemas/semantic_runtime_graph_schema_v1.json",` |
| `audit/release_manifest.json` | `42` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/schemas/semantic_runtime_graph_schema_v1_5.json",` |
| `audit/release_manifest.json` | `43` | `srp_experiment` | `audit_references` | `"audit/provenance/srp_experiment/tmp/srp_audit_test.md"` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `53` | `srp_experiment` | `audit_references` | `\| `srp_experiment/` \| Legacy \| Frozen legacy experiment and evidence layer \|` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `54` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/` \| Legacy \| Historical research materials preserved for provenance \|` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `58` | `srp_experiment` | `audit_references` | `These dependencies must be removed, isolated, or explicitly frozen before `docs/` and `srp_experiment/` can be safely deleted.` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `80` | `srp_experiment` | `audit_references` | `### `srp_experiment/`` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `95` | `srp_experiment` | `audit_references` | `- `srp_experiment` hits: `287`` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `115` | `docs_archive` | `markdown_references` | `- `audit/provenance/docs_archive/` is legacy provenance, not a release gate dependency` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `116` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is legacy, but its core runtime/tooling edges are gone` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `117` | `srp_experiment` | `audit_references` | `- the remaining `srp_experiment` references are frozen test/prototype assets, not live runtime dependencies` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `153` | `srp_experiment` | `audit_references` | `6. Delete the core `srp_experiment/` implementation only when the legacy compatibility surface has been isolated or archived.` |
| `audit/REPOSITORY_CONSOLIDATION_AUDIT.md` | `169` | `srp_experiment` | `audit_references` | `- keep the frozen `srp_experiment` compatibility and prototype assets until the deletion-readiness audit approves retirement or archival` |
| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` | `225` | `srp_experiment` | `audit_references` | `## 8. Role of `srp_experiment/`` |
| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` | `227` | `srp_experiment` | `audit_references` | ``srp_experiment/` is treated as the legacy evidence layer and historical implementation substrate.` |
| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` | `233` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is legacy evidence and compatibility support` |
| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` | `262` | `srp_experiment` | `audit_references` | `Document `srp_experiment/` as frozen legacy evidence and compatibility support.` |
| `audit/REPRODUCIBILITY_AND_DEPENDENCY_MAP.md` | `64` | `srp_experiment` | `audit_references` | `- selected helper paths under `srp_experiment/`, only where explicitly justified and frozen as legacy support` |
| `audit/REPRODUCIBILITY_AND_DEPENDENCY_MAP.md` | `112` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is preserved as a frozen legacy evidence layer.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `4` | `srp_experiment` | `audit_references` | `It classifies every observed `srp_experiment` reference into one of four buckets so we can restore the repository boundary before deciding what to delete.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `9` | `srp_experiment` | `audit_references` | `- Evaluation dependencies: current benchmark and external-validation adapters still import `srp_experiment`.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `11` | `srp_experiment` | `audit_references` | `- Historical references: archive documents refer to `srp_experiment` as background evidence or early implementation history.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `19` | `srp_experiment` | `audit_references` | `- `rg -n "srp_experiment" srp_runtime`` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `23` | `srp_experiment` | `audit_references` | `- No files under `srp_runtime/` currently import `srp_experiment`.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `33` | `srp_experiment` | `audit_references` | `\| `experiments/evaluation/semantic_backend_comparison/local_model_backend.py` \| `srp_experiment.local_llm`, `srp_experiment.srp.encoder`, `srp_experiment.srp.llm_judge` \| Local-model compatibility backend for semantic comparison \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `34` | `srp_experiment` | `audit_references` | `\| `experiments/evaluation/semantic_backend_comparison/vector_backend.py` \| `srp_experiment.srp.encoder` \| Vector backend for semantic comparison \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `35` | `srp_experiment` | `audit_references` | `\| `experiments/evaluation/phase_v_retention/metrics.py` \| `srp_experiment.srp.semantic_parser` \| Legacy semantic parsing helper for retention metrics \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `36` | `srp_experiment` | `audit_references` | `\| `experiments/external_validation/baselines.py` \| `srp_experiment.srp.encoder` \| Baseline scoring and similarity utilities \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `37` | `srp_experiment` | `audit_references` | `\| `experiments/external_validation/evidence.py` \| `srp_experiment.local_llm` \| Evidence-package generation and scoring support \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `47` | `srp_experiment` | `audit_references` | `These files keep `srp_experiment` alive because the release snapshot still treats it as part of the reproducibility surface.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `51` | `srp_experiment` | `audit_references` | `\| `README.md` \| `srp_experiment/` description \| Repository boundary statement \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `52` | `srp_experiment` | `audit_references` | `\| `scripts/verify_release.py` \| legacy required paths under `srp_experiment/` \| Release hygiene gate \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `56` | `srp_experiment` | `audit_references` | `- The repository currently still advertises `srp_experiment` as a retained evidence layer.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `62` | `srp_experiment` | `audit_references` | `These are archive documents that treat `srp_experiment` as historical evidence, early implementation, or a runtime projection.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `66` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` \| background / historical evidence \| Explicitly frames `srp_experiment` as background evidence \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `66` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` \| background / historical evidence \| Explicitly frames `srp_experiment` as background evidence \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `67` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` \| artifact path reference \| Refers to `srp_experiment/tmp/...` outputs \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `67` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` \| artifact path reference \| Refers to `srp_experiment/tmp/...` outputs \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `68` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` \| implementation mapping \| Maps current legacy implementation to runtime concepts \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `69` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md` \| implementation mapping \| Same, but for event processing \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `70` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` \| empirical / historical layer \| Explicitly says the legacy stack remains the evidence layer \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `71` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` \| parameter reference \| Refers to legacy helpers and budget config \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `72` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` \| parameter reference \| Mentions legacy helper functions \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `73` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` \| artifact path reference \| References `srp_experiment/tmp/fixed_harnesses/` outputs \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `73` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` \| artifact path reference \| References `srp_experiment/tmp/fixed_harnesses/` outputs \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `74` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` \| adapter planning \| Uses `srp_experiment` as the source side of a migration boundary \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `74` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` \| adapter planning \| Uses `srp_experiment` as the source side of a migration boundary \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `75` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_API_MAP.md` \| implementation mapping \| Maps the legacy implementation to future runtime APIs \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `76` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_PROTOCOL_MAP.md` \| implementation mapping \| Maps legacy modules to runtime object/data-contract layers \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `77` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` \| target-state mapping \| Treats `srp_experiment` as the current baseline being projected away from \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `77` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` \| target-state mapping \| Treats `srp_experiment` as the current baseline being projected away from \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `78` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` \| projection note \| Describes a legacy package as an early projection of the model \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `79` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` \| report references \| Cites legacy schemas and tests \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `80` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_THEORY_MAP.md` \| historical framing \| Calls the legacy stack a maintained background layer \|` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `93` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is still needed for evaluation and reproducibility in a few places.` |
| `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md` | `99` | `srp_experiment` | `audit_references` | `- we should not delete `srp_experiment` yet` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `3` | `srp_experiment` | `audit_references` | `This document records the Phase 3 legacy review of `srp_experiment/`.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/` is a frozen legacy evidence layer.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_runtime/` has no direct dependency on `srp_experiment/`.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `20` | `srp_experiment` | `audit_references` | `- No files under `srp_runtime/` currently import `srp_experiment`.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `25` | `srp_experiment` | `audit_references` | `- Do not introduce new runtime imports from `srp_experiment`.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `34` | `srp_experiment` | `audit_references` | `These are the current cross-layer references that keep `srp_experiment/` alive in active evaluation code.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `39` | `srp_experiment` | `audit_references` | `\| `experiments/evaluation/semantic_backend_comparison/local_model_backend.py` \| `srp_experiment.local_llm`, `srp_experiment.srp.encoder`, `srp_experiment.srp.llm_judge` \| Local-model compatibility backend for semantic comparison \| Keep \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `40` | `srp_experiment` | `audit_references` | `\| `experiments/evaluation/semantic_backend_comparison/vector_backend.py` \| `srp_experiment.srp.encoder` \| Vector baseline for semantic comparison \| Keep \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `41` | `srp_experiment` | `audit_references` | `\| `experiments/evaluation/phase_v_retention/metrics.py` \| `srp_experiment.srp.semantic_parser` \| Legacy semantic parsing helper for retention metrics \| Keep \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `42` | `srp_experiment` | `audit_references` | `\| `experiments/external_validation/baselines.py` \| `srp_experiment.srp.encoder` \| Baseline scoring and similarity utilities \| Keep \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `43` | `srp_experiment` | `audit_references` | `\| `experiments/external_validation/evidence.py` \| `srp_experiment.local_llm` \| Evidence-package generation and scoring support \| Keep \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `49` | `srp_experiment` | `audit_references` | `- `srp_experiment.local_llm`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `50` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.encoder`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `51` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.semantic_parser`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `52` | `srp_experiment` | `audit_references` | `- `srp_experiment.srp.llm_judge`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `58` | `srp_experiment` | `audit_references` | `These files refer to `srp_experiment/` as background evidence, historical implementation, or a migration source.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `62` | `srp_experiment` | `audit_references` | `\| `README.md` \| public documentation \| Update if needed \| The top-level README now describes `srp_experiment/` as a legacy measurement and runtime evidence stack. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `63` | `srp_experiment` | `audit_references` | `\| `audit/README.md` \| governance index \| Keep \| Explicitly frames `srp_experiment/` as legacy. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `64` | `srp_experiment` | `audit_references` | `\| `audit/REPO_ARCHITECTURE_BLUEPRINT.md` \| architecture contract \| Keep \| Declares `srp_experiment/` as legacy evidence and compatibility support. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `66` | `srp_experiment` | `audit_references` | `\| `audit/CLAIM_EVIDENCE_MAP.md` \| claim ledger \| Keep \| Treats `srp_experiment/` as legacy evidence, not source of truth. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `69` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` \| historical evidence \| Keep \| Explicitly frames `srp_experiment/` as background evidence. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `69` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` \| historical evidence \| Keep \| Explicitly frames `srp_experiment/` as background evidence. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `70` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` \| artifact path reference \| Keep \| Refers to legacy `srp_experiment/tmp/...` outputs. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `70` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` \| artifact path reference \| Keep \| Refers to legacy `srp_experiment/tmp/...` outputs. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `71` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` \| historical planning \| Keep \| Notes the legacy stack remains the evidence layer. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `72` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` \| artifact path reference \| Keep \| References legacy fixed-harness outputs. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `73` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` \| migration planning \| Keep \| Uses `srp_experiment` as the source side of a migration boundary. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `73` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` \| migration planning \| Keep \| Uses `srp_experiment` as the source side of a migration boundary. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `74` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` \| target-state mapping \| Keep \| Treats `srp_experiment` as the current baseline being projected away from. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `74` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` \| target-state mapping \| Keep \| Treats `srp_experiment` as the current baseline being projected away from. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `75` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` \| implementation mapping \| Keep \| Maps `srp_experiment/srp/` to runtime concepts without changing code. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `75` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` \| implementation mapping \| Keep \| Maps `srp_experiment/srp/` to runtime concepts without changing code. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `76` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md` \| implementation mapping \| Keep \| Maps legacy modules to event processing concepts. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `77` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_API_MAP.md` \| API mapping \| Keep \| Legacy-to-future mapping document. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `78` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_RUNTIME_PROTOCOL_MAP.md` \| protocol mapping \| Keep \| Legacy-to-future mapping document. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `79` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` \| model framing \| Keep \| Refers to the current `srp_experiment.srp.semantic_graph` package as an early projection. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `79` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` \| model framing \| Keep \| Refers to the current `srp_experiment.srp.semantic_graph` package as an early projection. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `80` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_THEORY_MAP.md` \| theory framing \| Keep \| Describes the legacy measurement stack as a background layer. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `81` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` \| parameter catalog \| Keep \| References legacy `srp_experiment` paths as supporting detail. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `81` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` \| parameter catalog \| Keep \| References legacy `srp_experiment` paths as supporting detail. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `82` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` \| parameter model \| Keep \| References legacy `srp_experiment` modules as supporting detail. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `82` | `srp_experiment` | `audit_references` | `\| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` \| parameter model \| Keep \| References legacy `srp_experiment` modules as supporting detail. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `83` | `docs_archive` | `markdown_references` | `\| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` \| historical report \| Keep \| References legacy schema and tests. \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `92` | `srp_experiment` | `audit_references` | `The release script still treats a subset of `srp_experiment/` files as required legacy evidence.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `105` | `srp_experiment` | `audit_references` | ``srp_experiment/` still contains extensive self-references within its own package tree.` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `111` | `srp_experiment` | `audit_references` | `- `srp_experiment/tests/`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `112` | `srp_experiment` | `audit_references` | `- `srp_experiment/analysis/`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `113` | `srp_experiment` | `audit_references` | `- `srp_experiment/mechanism_ablation/`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `114` | `srp_experiment` | `audit_references` | `- `srp_experiment/data/longbench_v2/`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `115` | `srp_experiment` | `audit_references` | `- `srp_experiment/srp/`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `116` | `srp_experiment` | `audit_references` | `- `srp_experiment/run_*.py`` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `130` | `srp_experiment` | `audit_references` | `\| `srp_experiment.local_llm` \| shared local-model client helper \| Potential extraction into a shared helper or runtime-adjacent utility later \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `131` | `srp_experiment` | `audit_references` | `\| `srp_experiment.srp.encoder` \| shared similarity/encoding helper \| Potential extraction if a common utility layer is introduced \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `132` | `srp_experiment` | `audit_references` | `\| `srp_experiment.srp.semantic_parser` \| normalization helper \| Potential extraction if shared parsing utilities are formalized \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `133` | `srp_experiment` | `audit_references` | `\| `srp_experiment.srp.llm_judge` \| evidence judgment helper \| Potential extraction if evidence tooling is consolidated \|` |
| `audit/SRP_EXPERIMENT_LEGACY_AUDIT.md` | `141` | `srp_experiment` | `audit_references` | `2. The remaining `srp_experiment` references are mostly evaluation, documentation, or release-script references.` |
| `scripts/find_dependency_refs.py` | `2` | `srp_experiment` | `historical_mentions` | `"""Generate a dependency report for legacy docs and srp_experiment references."""` |
| `scripts/find_dependency_refs.py` | `21` | `srp_experiment` | `historical_mentions` | `re.compile(r"^\s*from\s+srp_experiment(?:\.[A-Za-z0-9_]+)*\s+import\b"),` |
| `scripts/find_dependency_refs.py` | `22` | `srp_experiment` | `historical_mentions` | `re.compile(r"^\s*import\s+srp_experiment(?:\b\|\.)"),` |
| `scripts/find_dependency_refs.py` | `25` | `docs_archive` | `markdown_references` | `"docs_archive": re.compile(r"audit/provenance/docs_archive/"),` |
| `scripts/find_dependency_refs.py` | `26` | `srp_experiment` | `historical_mentions` | `"srp_experiment": re.compile(r"\bsrp_experiment\b"),` |
| `scripts/find_dependency_refs.py` | `82` | `srp_experiment` | `historical_mentions` | `elif rel.startswith("scripts/") or "/run_" in rel or rel.startswith("srp_experiment/run_"):` |
| `scripts/find_dependency_refs.py` | `100` | `docs_archive` | `markdown_references` | `category = "historical_mentions" if rel.startswith("audit/provenance/docs_archive/") else "markdown_references"` |
| `scripts/find_dependency_refs.py` | `178` | `srp_experiment` | `historical_mentions` | `"This report enumerates references to `docs/` and `srp_experiment/` that matter for repository deletion planning.",` |
| `scripts/find_dependency_refs.py` | `189` | `srp_experiment` | `historical_mentions` | `"\| `P0` \| `runtime_imports` \| Live experiment code still depends on `srp_experiment` at runtime. \|",` |
| `scripts/find_dependency_refs.py` | `190` | `srp_experiment` | `historical_mentions` | `"\| `P1` \| `tooling_imports` \| Scripts, generators, and maintenance tools still depend on `srp_experiment`. \|",` |
| `scripts/find_dependency_refs.py` | `191` | `srp_experiment` | `historical_mentions` | `"\| `P2` \| `test_imports` \| Tests still depend on `srp_experiment`; important, but usually lower risk than live code. \|",` |
| `scripts/find_dependency_refs.py` | `284` | `docs_archive` | `markdown_references` | `"- `scripts/verify_release.py` must stop depending on `audit/provenance/docs_archive/README.md` before `docs/` can be removed.",` |
| `scripts/verify_release.py` | `19` | `srp_experiment` | `historical_mentions` | `"audit/provenance/srp_experiment/local_llm.py",` |
| `scripts/verify_release.py` | `20` | `srp_experiment` | `historical_mentions` | `"audit/provenance/srp_experiment/run_local_diagnostics.py",` |
| `scripts/verify_release.py` | `21` | `srp_experiment` | `historical_mentions` | `"audit/provenance/srp_experiment/data/longbench_v2/import_longbench_v2.py",` |
| `scripts/verify_release.py` | `22` | `srp_experiment` | `historical_mentions` | `"audit/provenance/srp_experiment/data/longbench_v2/split_task_groups.py",` |
| `scripts/verify_release.py` | `23` | `srp_experiment` | `historical_mentions` | `"audit/provenance/srp_experiment/data/longbench_v2/manifest.json",` |
| `srp_experiment/export_csv.py` | `23` | `srp_experiment` | `historical_mentions` | `parser.add_argument("--output-csv", type=Path, default=Path("srp_experiment") / "tmp" / "srp_records.csv")` |
| `srp_experiment/tests/test_longbench_v2_prototype.py` | `6` | `import` | `test_imports` | `from srp_experiment.data.longbench_v2.import_longbench_v2 import build_query, tokenize_keywords, transform_row` |
| `srp_experiment/tests/test_longbench_v2_prototype.py` | `6` | `srp_experiment` | `historical_mentions` | `from srp_experiment.data.longbench_v2.import_longbench_v2 import build_query, tokenize_keywords, transform_row` |
| `srp_experiment/tests/test_longbench_v2_prototype.py` | `7` | `import` | `test_imports` | `from srp_experiment.data.longbench_v2 import split_task_groups` |
| `srp_experiment/tests/test_longbench_v2_prototype.py` | `7` | `srp_experiment` | `historical_mentions` | `from srp_experiment.data.longbench_v2 import split_task_groups` |
| `srp_experiment/tests/test_srp_runtime.py` | `488` | `srp_experiment` | `historical_mentions` | `output_path = write_records_markdown(records, Path("srp_experiment") / "tmp" / "srp_audit_test.md")` |
| `srp_experiment/tests/test_srp_runtime.py` | `563` | `srp_experiment` | `historical_mentions` | `schema_path = Path("srp_experiment") / "schemas" / "experiment_result_schema_v1.json"` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `5` | `import` | `test_imports` | `from srp_experiment.srp.pipeline import run_srp` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `5` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.pipeline import run_srp` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `6` | `import` | `test_imports` | `from srp_experiment.srp.compress import chunk_memory, compress_state` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `6` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.compress import chunk_memory, compress_state` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `7` | `import` | `test_imports` | `from srp_experiment.srp.encoder import build_encoder` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `7` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.encoder import build_encoder` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `8` | `import` | `test_imports` | `from srp_experiment.srp.export import flatten_record_for_csv, write_records_csv` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `8` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.export import flatten_record_for_csv, write_records_csv` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `9` | `import` | `test_imports` | `from srp_experiment.srp.semantic_parser import canonicalize_semantic_value, stable_semantic_object_id` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `9` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.semantic_parser import canonicalize_semantic_value, stable_semantic_object_id` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `10` | `import` | `test_imports` | `from srp_experiment.srp.saliency import rank_memory_chunks` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `10` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.saliency import rank_memory_chunks` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `11` | `import` | `test_imports` | `from srp_experiment.srp.state import SemanticObjectMetadata, SemanticState` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `11` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.state import SemanticObjectMetadata, SemanticState` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `12` | `import` | `test_imports` | `from srp_experiment.srp.recover import recover_state` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `12` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.recover import recover_state` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `13` | `import` | `test_imports` | `from srp_experiment.srp.recover_runtime import budget_recovery_inputs, recover_memory_from_package` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `13` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.recover_runtime import budget_recovery_inputs, recover_memory_from_package` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `14` | `import` | `test_imports` | `from srp_experiment.srp.state_lifecycle import apply_object_lifecycle as apply_object_lifecycle_rule` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `14` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.state_lifecycle import apply_object_lifecycle as apply_object_lifecycle_rule` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `15` | `import` | `test_imports` | `from srp_experiment.srp.state_summaries import (` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `15` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.state_summaries import (` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `21` | `import` | `test_imports` | `from srp_experiment.srp.validate import validate_state` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `21` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.validate import validate_state` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `22` | `import` | `test_imports` | `from srp_experiment.srp.validation_failure_summary import (` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `22` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.validation_failure_summary import (` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `28` | `import` | `test_imports` | `from srp_experiment.srp.validation_targets import build_validation_targets` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `28` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.validation_targets import build_validation_targets` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `29` | `import` | `test_imports` | `from srp_experiment.srp.compress_parse import parse_compressed_payload` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `29` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.compress_parse import parse_compressed_payload` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `30` | `import` | `test_imports` | `from srp_experiment.srp.object_retention import build_object_retention_breakdown, build_object_retention_breakdown_v2` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `30` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.object_retention import build_object_retention_breakdown, build_object_retention_breakdown_v2` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `31` | `import` | `test_imports` | `from srp_experiment.srp.repair import build_repair_package` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `31` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.repair import build_repair_package` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `32` | `import` | `test_imports` | `from srp_experiment.srp.state_allocation import build_state_allocation_policy` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `32` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.state_allocation import build_state_allocation_policy` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `824` | `srp_experiment` | `historical_mentions` | `output_path = write_records_csv(records, Path("srp_experiment") / "tmp" / "srp_records_test.csv")` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `985` | `srp_experiment` | `historical_mentions` | `jsonl_path = Path("srp_experiment") / "tmp" / "srp_tasks_test.jsonl"` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `992` | `import` | `test_imports` | `from srp_experiment.srp.export import flatten_records_for_csv` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `992` | `srp_experiment` | `historical_mentions` | `from srp_experiment.srp.export import flatten_records_for_csv` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `1013` | `import` | `test_imports` | `from srp_experiment.export_csv import _apply_task_identity` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `1013` | `srp_experiment` | `historical_mentions` | `from srp_experiment.export_csv import _apply_task_identity` |
| `srp_experiment/tests/test_srp_runtime_legacy_compat.py` | `1017` | `srp_experiment` | `historical_mentions` | `_apply_task_identity(record, task, Path("srp_experiment") / "tmp" / "task.json", "batch1-")` |
| `srp_experiment/data/longbench_v2/import_longbench_v2.py` | `243` | `srp_experiment` | `historical_mentions` | `manifest["task_file"] = "srp_experiment/data/longbench_v2/tasks.json"` |
| `srp_experiment/data/longbench_v2/manifest.json` | `9` | `srp_experiment` | `historical_mentions` | `"srp_experiment/data/longbench_v2/tasks_group_1.json",` |
| `srp_experiment/data/longbench_v2/manifest.json` | `10` | `srp_experiment` | `historical_mentions` | `"srp_experiment/data/longbench_v2/tasks_group_2.json",` |
| `srp_experiment/data/longbench_v2/manifest.json` | `11` | `srp_experiment` | `historical_mentions` | `"srp_experiment/data/longbench_v2/tasks_group_3.json"` |
| `experiments/srp_runtime_legacy/export_csv.py` | `18` | `srp_experiment` | `historical_mentions` | `parser.add_argument("--output-csv", type=Path, default=Path("srp_experiment") / "tmp" / "srp_records.csv")` |
| `experiments/srp_runtime_legacy/export_markdown.py` | `18` | `srp_experiment` | `historical_mentions` | `parser.add_argument("--output-markdown", type=Path, default=Path("srp_experiment") / "tmp" / "srp_audit.md")` |
| `experiments/srp_runtime_legacy/run_controlled_harness.py` | `28` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "controlled_harness",` |
| `experiments/srp_runtime_legacy/run_coverage_attribution.py` | `24` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "graph_representation_ablation" / "graph_representation_ablation_records.jsonl",` |
| `experiments/srp_runtime_legacy/run_coverage_attribution.py` | `30` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "coverage_attribution",` |
| `experiments/srp_runtime_legacy/run_decision_attribution.py` | `23` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "fixed_harnesses" / "object_aware_compression" / "object_aware_compression_records.jsonl",` |
| `experiments/srp_runtime_legacy/run_decision_attribution.py` | `29` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "decision_attribution",` |
| `experiments/srp_runtime_legacy/run_fixed_harnesses.py` | `68` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "fixed_harnesses",` |
| `experiments/srp_runtime_legacy/run_graph_recovery_evaluation.py` | `33` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "graph_recovery_ablation",` |
| `experiments/srp_runtime_legacy/run_graph_representation_ablation.py` | `34` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "graph_representation_ablation",` |
| `experiments/srp_runtime_legacy/run_mechanism_attribution_ablation.py` | `38` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "mechanism_attribution_ablation",` |
| `experiments/srp_runtime_legacy/run_object_aware_compression.py` | `33` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "object_aware_compression",` |
| `experiments/srp_runtime_legacy/run_object_aware_threshold_analysis.py` | `23` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "object_aware_threshold_analysis",` |
| `experiments/srp_runtime_legacy/run_object_aware_threshold_sampling.py` | `30` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "object_aware_threshold_sampling",` |
| `experiments/srp_runtime_legacy/run_policy_boundary_analysis.py` | `45` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_boundary",` |
| `experiments/srp_runtime_legacy/run_policy_boundary_drift.py` | `47` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_boundary_drift",` |
| `experiments/srp_runtime_legacy/run_policy_boundary_robustness.py` | `29` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_boundary_robustness",` |
| `experiments/srp_runtime_legacy/run_policy_intervention.py` | `41` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_intervention",` |
| `experiments/srp_runtime_legacy/run_policy_sensitivity.py` | `35` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "policy_sensitivity",` |
| `experiments/srp_runtime_legacy/run_reconstruction_policy_comparison.py` | `32` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "reconstruction_policy",` |
| `experiments/srp_runtime_legacy/run_recovery_ablation.py` | `32` | `srp_experiment` | `historical_mentions` | `default=PROJECT_ROOT / "srp_experiment" / "tmp" / "recovery_ablation",` |
| `audit/provenance/README.md` | `11` | `docs_archive` | `markdown_references` | `- avoid using `audit/provenance/docs_archive/` as an executable release requirement` |
| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` | `15` | `srp_experiment` | `audit_references` | `srp_experiment/` |
| `audit/provenance/docs_archive/SRP_EXPERIMENT_STACK_OVERVIEW.md` | `141` | `srp_experiment` | `audit_references` | `Use `srp_experiment/` as background and historical evidence for runtime feasibility.` |
| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` | `7` | `srp_experiment` | `audit_references` | `- `srp_experiment/tmp/fixed_harnesses/*/*_records.jsonl`` |
| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` | `11` | `srp_experiment` | `audit_references` | `- `srp_experiment/tmp/semantic_failure_taxonomy/semantic_failure_taxonomy.json`` |
| `audit/provenance/docs_archive/SRP_FAILURE_ANALYSIS_REPORT.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/tmp/semantic_failure_taxonomy/semantic_failure_taxonomy.md`` |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_ALIGNMENT.md` | `3` | `srp_experiment` | `audit_references` | `This document maps the current `srp_experiment/srp/` implementation to the SRP runtime concepts without changing the code structure.` |
| `audit/provenance/docs_archive/SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md` | `3` | `srp_experiment` | `audit_references` | `This document maps the current `srp_experiment/srp/` modules to the SRP runtime event processing model.` |
| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` | `12` | `srp_experiment` | `audit_references` | `- `srp_experiment/srp/` remains the empirical and historical evidence layer.` |
| `audit/provenance/docs_archive/SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md` | `322` | `srp_experiment` | `audit_references` | `srp_experiment/srp/` |
| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` | `92` | `srp_experiment` | `audit_references` | `- `policy_spec()` and `policy_flat()` in [srp_experiment/srp/state_summaries.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/state_summaries.py)` |
| `audit/provenance/docs_archive/SRP_PARAMETER_CATALOG.md` | `96` | `srp_experiment` | `audit_references` | `- budget configuration in [srp_experiment/budgeting.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/budgeting.py)` |
| `audit/provenance/docs_archive/SRP_PARAMETER_SPACE_MODEL.md` | `103` | `srp_experiment` | `audit_references` | `- lifecycle importance and decay values in `policy_spec()` inside [state_summaries.py](srp_experiment/srp/state_summaries.py)` |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | `7` | `srp_experiment` | `audit_references` | `- `srp_experiment/tmp/fixed_harnesses/`` |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | `42` | `srp_experiment` | `audit_references` | `- [controlled_harness_summary.md](./srp_experiment/tmp/fixed_harnesses/controlled/controlled_harness_summary.md)` |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | `62` | `srp_experiment` | `audit_references` | `- [recovery_ablation_summary.md](./srp_experiment/tmp/fixed_harnesses/recovery/recovery_ablation_summary.md)` |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | `87` | `srp_experiment` | `audit_references` | `- [reconstruction_policy_summary.md](./srp_experiment/tmp/fixed_harnesses/reconstruction/reconstruction_policy_summary.md)` |
| `audit/provenance/docs_archive/SRP_ROUND1_FIXED_HARNESS_REPORT.md` | `111` | `srp_experiment` | `audit_references` | `- [object_aware_compression_summary.md](./srp_experiment/tmp/fixed_harnesses/object_aware_compression/object_aware_compression_summary.md)` |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md` | `27` | `srp_experiment` | `audit_references` | `srp_experiment` |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_API_MAP.md` | `3` | `srp_experiment` | `audit_references` | `This document maps the current `srp_experiment/srp/` implementation to the future Runtime Kernel API.` |
| `audit/provenance/docs_archive/SRP_RUNTIME_KERNEL_TARGET.md` | `230` | `srp_experiment` | `audit_references` | `srp_experiment` |
| `audit/provenance/docs_archive/SRP_RUNTIME_PROTOCOL_MAP.md` | `3` | `srp_experiment` | `audit_references` | `This document maps the current `srp_experiment/srp/` modules to the runtime object and data-contract layers.` |
| `audit/provenance/docs_archive/SRP_SEMANTIC_GRAPH_MODEL.md` | `291` | `srp_experiment` | `audit_references` | `The current `srp_experiment.srp.semantic_graph` package is an early projection of this model.` |
| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` | `13` | `srp_experiment` | `audit_references` | `- `srp_experiment/schemas/semantic_runtime_graph_schema_v1.json`` |
| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` | `45` | `srp_experiment` | `audit_references` | `- `srp_experiment.tests.test_semantic_runtime_graph`` |
| `audit/provenance/docs_archive/SRP_SEMANTIC_RUNTIME_GRAPH_V1_REPORT.md` | `46` | `srp_experiment` | `audit_references` | `- `srp_experiment.tests.test_srp_runtime`` |
| `audit/provenance/docs_archive/SRP_THEORY_MAP.md` | `82` | `srp_experiment` | `audit_references` | `The legacy measurement stack under `srp_experiment/` remains a maintained background layer for runtime feasibility and benchmark evidence.` |
| `audit/provenance/srp_experiment/migration_manifest.json` | `3` | `srp_experiment` | `audit_references` | `"source_root": "srp_experiment/",` |
| `audit/provenance/srp_experiment/README.md` | `8` | `srp_experiment` | `audit_references` | `srp_experiment/` |
| `audit/provenance/srp_experiment/schemas/experiment_result_schema_v1.json` | `3` | `srp_experiment` | `audit_references` | `"$id": "srp_experiment/schemas/experiment_result_schema_v1.json",` |
| `audit/provenance/srp_experiment/schemas/semantic_runtime_graph_schema_v1.json` | `3` | `srp_experiment` | `audit_references` | `"$id": "srp_experiment/schemas/semantic_runtime_graph_schema_v1.json",` |
| `audit/provenance/srp_experiment/schemas/semantic_runtime_graph_schema_v1_5.json` | `3` | `srp_experiment` | `audit_references` | `"$id": "srp_experiment/schemas/semantic_runtime_graph_schema_v1_5.json",` |
| `audit/provenance/srp_experiment/data/longbench_v2/import_longbench_v2.py` | `243` | `srp_experiment` | `audit_references` | `manifest["task_file"] = "srp_experiment/data/longbench_v2/tasks.json"` |
| `audit/provenance/srp_experiment/data/longbench_v2/manifest.json` | `9` | `srp_experiment` | `audit_references` | `"srp_experiment/data/longbench_v2/tasks_group_1.json",` |
| `audit/provenance/srp_experiment/data/longbench_v2/manifest.json` | `10` | `srp_experiment` | `audit_references` | `"srp_experiment/data/longbench_v2/tasks_group_2.json",` |
| `audit/provenance/srp_experiment/data/longbench_v2/manifest.json` | `11` | `srp_experiment` | `audit_references` | `"srp_experiment/data/longbench_v2/tasks_group_3.json"` |

## Reading Guide

- `runtime_imports` (`P0`), `tooling_imports` (`P1`), and `test_imports` (`P2`) are blocking categories and must reach zero before legacy directories can be deleted.
- `markdown_references`, `audit_references`, and `historical_mentions` are non-blocking categories; they can remain after live dependency cleanup.
- `scripts/verify_release.py` must stop depending on `audit/provenance/docs_archive/README.md` before `docs/` can be removed.
