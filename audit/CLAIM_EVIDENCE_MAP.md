# Claim Evidence Map

This is the compact claim ledger for the frozen SRP release.
It records the current release-facing claims, the active evidence that supports them, and the boundary where historical material stops being release evidence.

## Active Claim Ledger

| Claim | Active Evidence | Status |
| --- | --- | --- |
| Governed semantic transitions can reject unsupported mutation while preserving authority separation. | `audit/REAL_VALIDATION_REPORT.md`, `audit/CURRENT_RELEASE.md`, `audit/VERIFY_REPORT.md`, `docs/benchmarks/LONGMEMEVAL_REPORT.md`, `experiments/results/longmemeval_full_v5/metadata.json` | Active |
| Evidence can strengthen verification without increasing authority. | `audit/REAL_VALIDATION_REPORT.md`, `audit/CURRENT_RELEASE.md`, `audit/VERIFY_REPORT.md`, `docs/release/RELEASE_EVIDENCE_REVIEW.md` | Active |
| External semantic evaluation workloads can be routed through the SRP governance pipeline under scorer separation. | `docs/benchmarks/LONGMEMEVAL_REPORT.md`, `docs/release/RELEASE_EVIDENCE_REVIEW.md`, `experiments/results/longmemeval_full_v5/metadata.json` | Active |
| The release artifact is reproducible under the frozen manuscript-to-PDF chain. | `fixed.md`, `audit/CURRENT_RELEASE.md`, `audit/VERIFY_REPORT.md`, `docs/release/RELEASE_EVIDENCE_REVIEW.md` | Active |
| Governance components are necessary under the frozen runtime governance contract. | `experiments/results/runtime_governance/ablation/ablation_report.json`, `experiments/results/runtime_governance/failure_injection/failure_injection_report.json`, `experiments/results/runtime_governance/governance_summary.json` | Active |
| LLM-generated semantic transitions can be governed without direct mutation authority. | `experiments/results/runtime_governance/llm_transition/llm_transition_report.json`, `experiments/results/runtime_governance/llm_transition/llm_transition_summary.json` | Active |
| Governance has measurable runtime overhead in the evaluated contract. | `experiments/results/runtime_governance/runtime_latency_summary.json`, `experiments/results/runtime_governance/governance_summary.json` | Active |
| Governed transitions produce auditable trace records. | `experiments/results/runtime_governance/llm_transition/llm_transition_report.json`, `experiments/results/runtime_governance/governance_summary.json` | Active |

## Release Boundary

- Active evidence: the canonical benchmark reports under `docs/benchmarks/` and the release evidence review under `docs/release/`
- Active evidence for the runtime governance chapter: the governance reports under `experiments/results/runtime_governance/`
- Historical evidence: the benchmark iteration history under `docs/archive/benchmark_history/` remains archived for provenance only
- Excluded evidence: benchmark ranking and any claim of universal memory superiority

## Notes

- This map is intentionally short.
- If a claim is not mapped here, it should be treated as supporting or historical material rather than current release evidence.
