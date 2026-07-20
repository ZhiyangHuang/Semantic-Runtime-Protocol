# Claim Evidence Map

This is the compact claim ledger for the frozen SRP release.
It records the current release-facing claims, the active evidence that supports them, and the boundary where historical material stops being release evidence.

## Active Claim Ledger

| Claim | Active Evidence | Status |
| --- | --- | --- |
| Governed semantic transitions can reject unsupported mutation while preserving authority separation. | `audit/REAL_VALIDATION_REPORT.md`, `audit/V1_1_REALITY_CHECK_FREEZE.md`, `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/longmemeval_reality_check_report.md`, `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/artifact_integrity.json` | Active |
| Evidence can strengthen verification without increasing authority. | `audit/REAL_VALIDATION_REPORT.md`, `audit/V1_1_REALITY_CHECK_FREEZE.md`, `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/runtime_manifest.json` | Active |
| External semantic evaluation workloads can be routed through the SRP governance pipeline under scorer separation. | `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/longmemeval_reality_check_report.md`, `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/longmemeval_reality_check_metadata.json`, `audit/V1_1_REALITY_CHECK_FREEZE.md` | Active |
| The release artifact is reproducible under the frozen manuscript-to-PDF chain. | `fixed.md`, `paper/SRP_ARXIV_DRAFT_V1.md`, `paper/SRP_PAPER_FINAL_V1.md`, `paper/latex/body_content.md`, `paper/latex/body.tex`, `arxiv_package/body.tex`, `arxiv_package/main.pdf`, `audit/RELEASE_SNAPSHOT.md`, `audit/RELEASE_SNAPSHOT_CHECK.md` | Active |

## Release Boundary

- Active evidence: the current SRP controlled-validation reports and the LongMemEval reality-check bundle
- Historical evidence: the 7/18 LoCoMo bundles and older phase-era material remain archived for provenance only
- Excluded evidence: benchmark ranking and any claim of universal memory superiority

## Notes

- This map is intentionally short.
- If a claim is not mapped here, it should be treated as supporting or historical material rather than current release evidence.
