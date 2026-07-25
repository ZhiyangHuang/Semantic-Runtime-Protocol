# SRP v1.1 Evidence Surface

This page is the compact evidence index for the frozen release surface.

## Main Evidence

| Benchmark | Frozen artifact | Claim role | Metric authority |
| --- | --- | --- | --- |
| STFB | `experiments/results/` STFB bundles | Mechanism validation | STFB contract |
| LongMemEval | `experiments/results/longmemeval_full_v5/` | External transition validation | Official scorer |
| ARC | `experiments/results/arc_full_v1/` | Reasoning transition validation | Accuracy |
| MMLU | `experiments/results/mmlu_full_v3/` | Capability stress | Accuracy |
| HumanEval | `experiments/results/humaneval_full_v1/` | Capability stress | pass@1 |

For the release decision and current status, see `README.md`.

## Validation

### LongMemEval Reality Check

This slice keeps the official scorer authoritative and reports SRP diagnostics separately.

| Item | Value |
| --- | --- |
| Benchmark | `longmemeval` |
| Baselines | `full_context, sliding_window, vector_rag, srp` |
| Seeds | `11, 23, 37` |
| Sample limit | `2` |
| Runtime | frozen local-vLLM contract |
| Result | official score and SRP diagnostics were both produced; no negative transition signals |
| Integrity | runtime, dataset, and report hashes recorded |
| Boundary | scorer official; diagnostics supplementary; not a leaderboard claim |

### Runtime Integration Evidence

This slice keeps the replay boundary frozen and treats runtime integration as appendix-grade evidence.

| Snapshot | Claim role | Compact result |
| --- | --- | --- |
| Replay | admission sanity | 6 transitions; 2 accepted; 4 rejected; trace completeness `1.0` |
| Backend consistency | adapter sanity | backend consistency rate `1.0`; decision mismatches `0` |
| Shadow observation | observe-only comparison | rejection/disagreement rate `0.6666666666666666`; overhead `-0.002166666666666667 ms` |
| Controlled admission | commit-path governance | rollback success `1.0`; invalid commit rate `0.0`; state preservation `1.0` |

The runtime integration evidence does not claim production readiness or universal backend independence.

## Boundary

- This page does not define a new benchmark.
- This page does not redefine the frozen STFB contract.
- This page only collects the evidence surface used by the current release gate.

## Pointers

- `paper/SRP_MANUSCRIPT_V1.md`
- `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md`
