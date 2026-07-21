# SRP Transition Role Coverage Report

This report summarizes transition role coverage across semantic workloads.
It is a protocol coverage artifact, not a benchmark ranking.

## Protocol Boundary

- schema_version: `1`
- report_version: `v1.2-alpha`
- protocol_boundary: `transition_role_protocol`

## Summary

- role_count: `4`
- complete_roles: `3`
- partial_roles: `0`
- planned_roles: `1`
- no_workload_roles: `0`
- completed_workloads: `3`
- planned_workloads: `1`

## Role Coverage

| Role | Status | Completed | Planned | Diagnostics |
| --- | --- | ---: | ---: | --- |
| `evidence_update` | `complete` | `1` | `0` | `semantic_coverage, semantic_drift, transition_acceptance, governance_consistency` |
  - `longmemeval`: `complete` (artifact: `C:\Users\ZhiyangHuang\Semantic-Runtime-Protocol\experiments\results\external_validation_longmemeval_reality_check_smoke_v2\longmemeval_reality_check_report.md`, exists: `True`)
| `temporal_state_evolution` | `complete` | `1` | `0` | `semantic_coverage, semantic_drift, transition_acceptance, governance_consistency` |
  - `locomo`: `complete` (artifact: `C:\Users\ZhiyangHuang\Semantic-Runtime-Protocol\experiments\results\transition_role\temporal_state_evolution\locomo\run_latest\report.md`, exists: `True`)
| `action_proposal` | `planned` | `0` | `1` | `semantic_coverage, semantic_drift, transition_acceptance, governance_consistency` |
  - `agentbench`: `planned` (artifact: `C:\Users\ZhiyangHuang\Semantic-Runtime-Protocol\experiments\results\transition_role\action_proposal\agentbench\run_latest\report.md`, exists: `False`)
| `inference_proposal` | `complete` | `1` | `0` | `semantic_coverage, semantic_drift, transition_acceptance, governance_consistency` |
  - `reasoning`: `complete` (artifact: `C:\Users\ZhiyangHuang\Semantic-Runtime-Protocol\experiments\results\transition_role\inference_proposal\reasoning\run_latest\report.md`, exists: `True`)

## Interpretation

- `evidence_update`, `temporal_state_evolution`, and `inference_proposal` currently have instantiated workload slices or bridge artifacts.
- `action_proposal` remains the only planned coverage target.
- The report tracks protocol coverage, not task superiority.
