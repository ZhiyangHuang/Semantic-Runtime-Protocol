# Phase 6.5 `srp_experiment/` Inventory Freeze

This inventory freezes the current `srp_experiment/` surface into three categories so later phases can isolate, archive, or remove assets without re-deriving the boundary.

It does not delete anything.
It records the final whole-tree state before asset separation.

## 1. Tree Snapshot

Current top-level structure:

```text
analysis/
data/
eval/
mechanism_ablation/
schemas/
srp/
tests/
tmp/
README.md
budgeting.py
controlled_harness.py
export_csv.py
export_markdown.py
graph_recovery_harness.py
graph_representation_ablation_harness.py
local_llm.py
object_aware_compression_harness.py
object_aware_threshold_harness.py
object_aware_threshold_sampling.py
policy_boundary_analysis.py
policy_boundary_drift.py
policy_boundary_robustness.py
policy_intervention_harness.py
policy_sensitivity.py
prompting.py
reconstruction_policy_harness.py
recovery_ablation_harness.py
run_controlled_harness.py
run_coverage_attribution.py
run_decision_attribution.py
run_fixed_harnesses.py
run_graph_information_gap_analysis.py
run_graph_recovery_evaluation.py
run_graph_representation_ablation.py
run_importance_attribution.py
run_local_diagnostics.py
run_mechanism_attribution_ablation.py
run_object_aware_compression.py
run_object_aware_threshold_analysis.py
run_object_aware_threshold_sampling.py
run_policy_attribution.py
run_policy_boundary_analysis.py
run_policy_boundary_drift.py
run_policy_boundary_robustness.py
run_policy_intervention.py
run_policy_pareto_analysis.py
run_policy_sensitivity.py
run_reconstruction_policy_comparison.py
run_recovery_ablation.py
run_semantic_extraction_audit.py
run_semantic_failure_taxonomy.py
verify_e5_encoder.py
```

## 2. Classification

### A. Compatibility Assets

These assets may remain temporarily because they preserve executable legacy compatibility or migration evidence.

| Path | Reason | Destination |
| --- | --- | --- |
| `budgeting.py` | Frozen compatibility helper still exercised by legacy runtime tests | `srp_experiment/` compatibility surface |
| `prompting.py` | Frozen compatibility helper still exercised by legacy runtime tests | `srp_experiment/` compatibility surface |
| `eval/` | Frozen compatibility evaluation helper | `srp_experiment/` compatibility surface |
| `data/longbench_v2/` | Historical prototype surface still exercised by frozen tests | `srp_experiment/` compatibility surface |
| `export_csv.py` | Frozen export compatibility helper still exercised by legacy tests | `srp_experiment/` compatibility surface |
| `tests/test_srp_runtime_legacy_compat.py` | Legacy compatibility evidence | `experiments/srp_runtime_legacy/` or audit provenance if execution is no longer needed |
| `tests/test_longbench_v2_prototype.py` | Historical prototype coverage | audit provenance / frozen test asset |

### B. Historical / Provenance Assets

These assets preserve the historical evolution of SRP but are not part of the live runtime or tooling surface.

| Path | Reason | Destination |
| --- | --- | --- |
| `README.md` | Legacy layer description | `audit/provenance/srp_experiment/` |
| `data/longbench_v2/` | Historical benchmark/provenance inputs | `audit/provenance/srp_experiment/` |
| `tmp/` | Historical scratch outputs and audit traces | `audit/provenance/srp_experiment/` or removal after provenance capture |
| `schemas/` | Historical schema snapshots | `audit/provenance/srp_experiment/` |

### C. Deletion Candidates

These assets have been migrated to live homes and can be removed once preservation boundaries are confirmed.

| Path pattern | Reason | Live replacement |
| --- | --- | --- |
| `analysis/` | Migrated analysis logic | `experiments/analysis/` |
| `mechanism_ablation/` | Migrated mechanism-ablation logic | `experiments/mechanism_ablation/` |
| `eval/` | Migrated evaluation helper logic | `experiments/` or provenance |
| top-level `run_*.py` wrappers | Migrated live entrypoints | `experiments/analysis/`, `experiments/mechanism_ablation/`, `experiments/srp_runtime_legacy/` |
| top-level harness modules | Migrated live wrappers | `experiments/` or `srp_runtime/` |
| `local_llm.py`, `export_markdown.py` | Shared utilities now live elsewhere | `experiments/common/` or provenance, depending on use |

## 3. Decision Rules

- If a file is still required to execute a legacy compatibility test, keep it in a compatibility boundary.
- If a file only explains how the old tree evolved, move it into provenance.
- If a file has a live replacement in `experiments/` or `srp_runtime/`, mark it as a delete candidate.
- The inventory freezes classification, not execution.

## 4. Intended Destinations

Planned homes after separation:

- `experiments/srp_runtime_legacy/` for executable compatibility that still needs to run
- `audit/provenance/srp_experiment/` for historical documentation, schemas, and legacy experiment outputs
- deletion for migrated wrappers and duplicate implementations once the move is verified

## 5. Snapshot Boundary

The important boundary is not whether the old package still contains references.
The boundary is whether any live dependency arrow still points at it.

This inventory freezes the whole-tree state before B2 and B3 separation work begins.
