# Phase 6.3 Test Freeze Manifest

## Purpose

This manifest freezes the remaining `P2` test dependencies so they are treated as intentional assets rather than accidental residue.

Current dependency snapshot:

- `runtime_imports`: `0`
- `tooling_imports`: `0`
- `test_imports`: `22`

## Remaining Blocking Test Imports

### Legacy compatibility suite

`srp_experiment/tests/test_srp_runtime_legacy_compat.py`

Imports currently counted as blocking:

- `srp_experiment.srp.pipeline.run_srp`
- `srp_experiment.srp.compress.chunk_memory`
- `srp_experiment.srp.compress.compress_state`
- `srp_experiment.srp.encoder.build_encoder`
- `srp_experiment.srp.export.flatten_record_for_csv`
- `srp_experiment.srp.export.write_records_csv`
- `srp_experiment.srp.semantic_parser.canonicalize_semantic_value`
- `srp_experiment.srp.semantic_parser.stable_semantic_object_id`
- `srp_experiment.srp.saliency.rank_memory_chunks`
- `srp_experiment.srp.state.SemanticObjectMetadata`
- `srp_experiment.srp.state.SemanticState`
- `srp_experiment.srp.recover.recover_state`
- `srp_experiment.srp.recover_runtime.budget_recovery_inputs`
- `srp_experiment.srp.recover_runtime.recover_memory_from_package`
- `srp_experiment.srp.state_lifecycle.apply_object_lifecycle`
- `srp_experiment.srp.state_summaries.*`
- `srp_experiment.srp.validate.validate_state`
- `srp_experiment.srp.validation_failure_summary.*`
- `srp_experiment.srp.validation_targets.build_validation_targets`
- `srp_experiment.srp.compress_parse.parse_compressed_payload`
- `srp_experiment.srp.object_retention.build_object_retention_breakdown`
- `srp_experiment.srp.object_retention.build_object_retention_breakdown_v2`
- `srp_experiment.srp.repair.build_repair_package`
- `srp_experiment.srp.state_allocation.build_state_allocation_policy`
- `srp_experiment.export_csv._apply_task_identity`

Action:

- keep as a frozen legacy-compatibility asset until deletion of `srp_experiment/`

### Historical prototype

`srp_experiment/tests/test_longbench_v2_prototype.py`

Imports currently counted as blocking:

- `srp_experiment.data.longbench_v2.import_longbench_v2.build_query`
- `srp_experiment.data.longbench_v2.import_longbench_v2.tokenize_keywords`
- `srp_experiment.data.longbench_v2.import_longbench_v2.transform_row`
- `srp_experiment.data.longbench_v2.split_task_groups`

Action:

- review for archival status
- migrate only if a live long-context ingestion surface is explicitly added

## Freeze Rule

No further test migration should treat the remaining `P2` references as generic cleanup.
They are now classified assets whose lifecycle must be decided explicitly.

