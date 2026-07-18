# Phase 6.3 Test Classification

## Purpose

Phase 6.3 does not blindly rewrite all remaining test imports.
It separates tests that should migrate to live namespaces from tests that must remain as explicit legacy compatibility or archival references.

Current snapshot:

- `runtime_imports`: `0`
- `tooling_imports`: `0`
- `test_imports`: `58`

## Classification Rules

- `live behavior`: the test verifies behavior that already has a live namespace or a live compatibility namespace and should migrate.
- `legacy compatibility`: the test intentionally verifies the frozen `srp_experiment` surface and should remain until deletion is safe.
- `historical regression`: the test documents an archived boundary, prototype, or frozen release behavior and should be reviewed before migration.

## Inventory

| Test File | Category | Action | Rationale |
| --- | --- | --- | --- |
| `test_encoder.py` | live behavior | migrate | Encoder behavior already exists in the live compatibility namespace. |
| `test_graph_recovery_policy.py` | live behavior | migrate | Recovery policy behavior has a live compatibility home. |
| `test_runtime_representation_v2.py` | live behavior | migrate | Runtime representation v2 is part of the live runtime surface. |
| `test_semantic_runtime_graph.py` | live behavior | migrate | Semantic graph construction and validation already have live compatibility equivalents. |
| `test_semantic_runtime_graph_v1_5.py` | live behavior | migrate | Versioned graph behavior remains part of the live compatibility surface. |
| `test_srp_runtime.py` | live behavior | migrate | This is the main runtime behavior regression suite. |
| `test_srp_runtime_legacy_compat.py` | legacy compatibility | keep | This suite explicitly protects the frozen legacy compatibility boundary. |
| `test_longbench_v2_prototype.py` | historical regression | review | This is a prototype/data-helper suite tied to archived long-context ingestion behavior. |

## Immediate Migration Targets

The first post-classification migration wave should focus on:

- `test_encoder.py`
- `test_graph_recovery_policy.py`
- `test_runtime_representation_v2.py`
- `test_semantic_runtime_graph.py`
- `test_semantic_runtime_graph_v1_5.py`
- `test_srp_runtime.py`

## Explicit Legacy Holds

The following test assets are intentionally retained for now:

- `test_srp_runtime_legacy_compat.py`
- `test_longbench_v2_prototype.py` pending archival review

## Freeze Manifest

The remaining `P2` references are frozen in:

- [`PHASE_6_TEST_FREEZE.md`](PHASE_6_TEST_FREEZE.md)

## Completion Criterion

Phase 6.3 can only be considered complete when:

- the live-behavior test bucket has been migrated to live namespaces
- the legacy compatibility bucket is explicitly isolated
- any archival prototypes are either documented or retired
- the dependency audit reflects the remaining approved legacy surface, if any
