# SRP Reproducibility Consistency Checklist

Release target: `srp-v1.0.0-arxiv`

This checklist records the exact places where the arXiv manuscript and the release evidence chain are already aligned, and where the current repository still lacks a direct machine-readable result file for the paper text.

Use this as the review sheet for the runtime-overhead and robustness consistency checks:

- representation / implementation robustness reporting

---

## 1. Quick Verdict

- [x] LongMemEval external validation is internally consistent
- [x] Runtime replay / backend consistency / controlled admission are internally consistent
- [x] Phase VIII representation-invariance results are now generated
- [x] Phase VIII implementation-independence results are now generated
- [x] The paper's runtime-overhead line has a matching machine-readable release artifact

---

## 2. Runtime Overhead Check

Paper location:

- [paper/SRP_ARXIV_DRAFT_V1.md](../../paper/SRP_ARXIV_DRAFT_V1.md#L635)
- [paper/SRP_ARXIV_DRAFT_V1.md](../../paper/SRP_ARXIV_DRAFT_V1.md#L643)

Paper values:

- total transition latency: `1734.482800`
- relative overhead: `0.002396545115953877%`

Closest current evidence files:

- [experiments/results/runtime_governance/llm_transition/llm_transition_summary.json](../../experiments/results/runtime_governance/llm_transition/llm_transition_summary.json)
- [experiments/results/runtime_governance/governance_summary.json](../../experiments/results/runtime_governance/governance_summary.json)
- [experiments/results/runtime_integration/runtime_integration_report.json](../../experiments/results/runtime_integration/runtime_integration_report.json)

Observed current values:

- `llm_transition_summary.json`: `srp_mean_total_ms = 1734.4827999999998`, `relative_overhead_percent = 0.002396545115953877`
- `governance_summary.json`: same runtime-governance overhead values as above
- `runtime_integration_report.json`: `mean_latency_ms = 0.006466666666666667`, `trace_completeness = 1.0`

Assessment:

- [x] exact match
- [ ] conceptually aligned, but numerically not identical

Action needed:

- None. The paper-facing runtime summary now matches the canonical release artifact.

Suggested minimum artifact bundle for this item:

- `metadata.json`
- `runtime_*_report.json`
- `runtime_*_summary.json`

---

## 3. Representation Robustness Check

Paper location:

- [paper/SRP_ARXIV_DRAFT_V1.md](../../paper/SRP_ARXIV_DRAFT_V1.md#L699)
- [paper/SRP_ARXIV_DRAFT_V1.md](../../paper/SRP_ARXIV_DRAFT_V1.md#L705)

Paper values:

- cases evaluated: `144`
- hierarchy consistency rate: `1.0`
- governance consistency rate: `1.0`

Interpretation of the `144` count:

- `4` encoders
- `3` parsers
- `3` recovery modes
- `4` relation-recovery cases
- total = `4 x 3 x 3 x 4 = 144`

Likely release artifact family:

- `experiments/results/phase_viii_representation_invariance/`

Expected files if promoted into release evidence:

- `metadata.json`
- `representation_invariance_report.json`
- `representation_invariance_summary.json`
- `representation_invariance_records.csv`
- `representation_invariance_records.jsonl`

Assessment:

- [x] exact release artifact present
- [x] code path exists and the result bundle is present in `experiments/results/`

Action needed:

- Promote the representation-invariance bundle into the active release evidence chain
- Keep the frozen values consistent with the generated report:
  - case count: `144`
  - mean semantic coverage: `0.559689`
  - mean semantic drift: `0.302338`
  - hierarchy consistency rate: `1`
  - governance consistency rate: `1`

Current bundle:

- [experiments/results/phase_viii_representation_invariance/metadata.json](../../experiments/results/phase_viii_representation_invariance/metadata.json)
- [experiments/results/phase_viii_representation_invariance/representation_invariance_report.json](../../experiments/results/phase_viii_representation_invariance/representation_invariance_report.json)
- [experiments/results/phase_viii_representation_invariance/representation_invariance_summary.json](../../experiments/results/phase_viii_representation_invariance/representation_invariance_summary.json)

---

## 4. Implementation Robustness Check

Paper location:

- [paper/SRP_ARXIV_DRAFT_V1.md](../../paper/SRP_ARXIV_DRAFT_V1.md#L707)
- [paper/SRP_ARXIV_DRAFT_V1.md](../../paper/SRP_ARXIV_DRAFT_V1.md#L713)

Paper values:

- cases evaluated: `36`
- hierarchy consistency rate: `1.0`
- governance consistency rate: `1.0`

Interpretation of the `36` count:

- `3` backends
- `3` recovery modes
- `4` relation-recovery cases
- total = `3 x 3 x 4 = 36`

Likely release artifact family:

- `experiments/results/phase_viii_implementation_independence/`

Expected files if promoted into release evidence:

- `metadata.json`
- `implementation_independence_report.json`
- `implementation_independence_summary.json`
- `implementation_independence_records.csv`
- `implementation_independence_records.jsonl`

Assessment:

- [x] exact release artifact present
- [x] code path exists and the result bundle is present in `experiments/results/`

Action needed:

- Promote the implementation-independence bundle into the active release evidence chain
- Keep the frozen values consistent with the generated report:
  - case count: `36`
  - mean semantic coverage: `0.623016`
  - mean semantic drift: `0.220833`
  - hierarchy consistency rate: `1`
  - governance consistency rate: `1`

Current bundle:

- [experiments/results/phase_viii_implementation_independence/metadata.json](../../experiments/results/phase_viii_implementation_independence/metadata.json)
- [experiments/results/phase_viii_implementation_independence/implementation_independence_report.json](../../experiments/results/phase_viii_implementation_independence/implementation_independence_report.json)
- [experiments/results/phase_viii_implementation_independence/implementation_independence_summary.json](../../experiments/results/phase_viii_implementation_independence/implementation_independence_summary.json)

---

## 5. Release Chain Summary

Already in the release chain:

- [audit/RUNTIME_INTEGRATION_EVIDENCE_INDEX.md](../../audit/RUNTIME_INTEGRATION_EVIDENCE_INDEX.md)
- [audit/CURRENT_RELEASE.md](../../audit/CURRENT_RELEASE.md)
- [audit/CLAIM_EVIDENCE_MAP.md](../../audit/CLAIM_EVIDENCE_MAP.md)

Not yet directly backed by a promoted result bundle:

- the exact paper-facing runtime-overhead summary

Now backed by generated result bundles and added to the active release index:

- `experiments/results/phase_viii_representation_invariance/`
- `experiments/results/phase_viii_implementation_independence/`

---

## 6. Reviewer Decision

Submission-ready for reproducibility consistency:

- [x] yes
- [ ] not yet, pending the exact runtime-overhead artifact
