# Runtime Integration Evidence Index

This index records the frozen evidence snapshot for the SRP v1.1 runtime integration replay boundary.
It is an audit layer, not a duplicate report.

The machine-readable sibling is [`audit/RUNTIME_INTEGRATION_EVIDENCE_INDEX.json`](RUNTIME_INTEGRATION_EVIDENCE_INDEX.json).
The reviewer-facing summary is [`audit/RUNTIME_INTEGRATION_EVIDENCE_SUMMARY.md`](RUNTIME_INTEGRATION_EVIDENCE_SUMMARY.md).

This evidence family currently contains four snapshots:

- `srp-runtime-v1.1-replay-0001`
- `srp-runtime-v1.1-backend-0001`
- `srp-runtime-v1.1-shadow-0001`
- `srp-runtime-v1.1-admission-0001`

## Snapshot

- Snapshot ID: `srp-runtime-v1.1-replay-0001`
- Release class: `appendix`
- Status: frozen replay evidence
- Runtime contract: `srp-runtime-v1.1`
- Adapter: `deterministic_memory_adapter`

## Evidence Boundary

The runtime integration replay is intended to show that SRP can sit between semantic proposal generation and persistent mutation as an admission boundary.
It does not claim production deployment or benchmark dominance.

## Artifact Map

| Artifact | Path | Role |
| --- | --- | --- |
| Replay fixture | [`experiments/runtime_integration/fixtures/semantic_transition_replay_v1.json`](../experiments/runtime_integration/fixtures/semantic_transition_replay_v1.json) | Frozen input boundary |
| Replay manifest | [`experiments/results/runtime_integration/runtime_integration_manifest.json`](../experiments/results/runtime_integration/runtime_integration_manifest.json) | Snapshot metadata |
| Replay report | [`experiments/results/runtime_integration/runtime_integration_report.json`](../experiments/results/runtime_integration/runtime_integration_report.json) | Machine-readable result set |
| Trace log | [`experiments/results/runtime_integration/runtime_integration_traces.jsonl`](../experiments/results/runtime_integration/runtime_integration_traces.jsonl) | Per-transition audit trace |
| Record table | [`experiments/results/runtime_integration/runtime_integration_records.csv`](../experiments/results/runtime_integration/runtime_integration_records.csv) | Tabular replay rows |
| Rendered summary | [`experiments/results/runtime_integration/runtime_integration_report.md`](../experiments/results/runtime_integration/runtime_integration_report.md) | Human-readable summary |

## Claims Supported

| Claim ID | Claim | Evidence |
| --- | --- | --- |
| `runtime_insertion` | SRP can operate as an admission boundary between proposal generation and mutation. | fixture, manifest, replay report |
| `authority_separation` | Rejected transitions do not mutate runtime state. | governance traces, replay report |
| `trace_auditability` | Runtime transitions can be recorded with complete trace fields under a frozen contract. | trace log, replay report |
| `protocol_sanity` | The frozen replay boundary yields deterministic acceptance and rejection behavior under the chosen policy. | fixture, manifest, replay summary |

## Metrics

- Transition count: `6`
- Accepted count: `2`
- Rejected count: `4`
- Unsafe accept rate: `0.0`
- False rejection rate: `0.0`
- Trace completeness: `1.0`

## Backend Snapshot

- Snapshot ID: `srp-runtime-v1.1-backend-0001`
- Parent snapshot: `srp-runtime-v1.1-replay-0001`
- Evaluation type: `backend_consistency`
- Runtime contract: `srp-runtime-v1.1`
- Backends tested: `deterministic_memory_adapter`, `in_memory_graph_store`
- Backend consistency rate: `1.0`
- Decision mismatch count: `0`
- Trace completeness: `1.0`

## Shadow Snapshot

- Snapshot ID: `srp-runtime-v1.1-shadow-0001`
- Parent snapshot: `srp-runtime-v1.1-backend-0001`
- Evaluation type: `shadow_observation`
- Runtime contract: `srp-runtime-v1.1`
- Snapshot role: observe-only runtime comparison
- Shadow rejection rate: `0.6666666666666666`
- Runtime disagreement rate: `0.6666666666666666`
- Admission latency overhead ms: `-0.002166666666666667`
- Trace completeness: `1.0`

## Controlled Admission Snapshot

- Snapshot ID: `srp-runtime-v1.1-admission-0001`
- Parent snapshot: `srp-runtime-v1.1-shadow-0001`
- Evaluation type: `controlled_admission`
- Runtime contract: `srp-runtime-v1.1`
- Commit-enabled policy: `true`
- Rollback success rate: `1.0`
- Invalid commit rate: `0.0`
- State preservation rate: `1.0`
- Admission latency overhead ms: `0.016933333333333335`
- Trace completeness: `1.0`

## Status Notes

- Current classification: `appendix`
- Future classification candidate: `main_evaluation_candidate`
- Scope: frozen replay contract only
- Excluded: production readiness, backend comparison, latency scaling
