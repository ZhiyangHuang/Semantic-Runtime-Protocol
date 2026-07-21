# LongMemEval Bridge Artifact Audit

Date: 2026-07-21

Reviewed artifact bundle:
- `experiments/results/longmemeval_full_v5/`

Historical bridge iterations retained for provenance:
- `LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V1.md`
- `LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V2.md`
- `LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V3.md`
- `LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V4.md`
- `LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V5.md`

This audit covers the v5 bridge artifact only.

---

## 1. Official Artifact Identification

Confirmed:
- `experiments/results/longmemeval_full_v5/` is the official LongMemEval bridge artifact bundle
- `LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V5.md` is the authoritative execution record for the final bridge run
- `v1` through `v4` are retained as diagnostic iteration history and must not be treated as the official bridge artifact

Interpretation:
- the multiple bridge execution records are intentional
- `v5` is the corrected bridge release artifact
- earlier versions document the path to the final corrected run

---

## 2. Artifact Integrity

Confirmed from the v5 artifact bundle:
- `sample_count`: `24`
- `prediction_count`: `24`
- `trace_count`: `24`
- `official_score.case_count`: `24`
- `official_summary.case_count`: `24`
- `bridge_accuracy`: `0.888021`
- `bridge_srp_accuracy`: `1.0`
- `bridge_accuracy_gap`: `0.111979`

Presence checks:
- `config.json` exists
- `raw_predictions.jsonl` exists
- `metrics.json` exists
- `metadata.json` exists
- `report.md` exists

Consistency checks:
- raw predictions align with the reported sample count
- the official score and SRP diagnostics are both present
- the shared artifact contract is satisfied
- hashes are recorded in `metadata.json`

---

## 3. Prompt Leakage Audit

Audit method:
- inspected every prompt in `raw_predictions.jsonl`
- searched for prompt-visible leakage of scoring-only fields

Result:
- `expected_answer` occurrences in prompt text: `0`
- `reference_answer` occurrences in prompt text: `0`
- `gold` occurrences in prompt text: `0`
- `label` occurrences in prompt text: `0`

Conclusion:
- no gold-answer leakage was detected in prompt-visible content
- the bridge prompt path respects the treatment boundary

---

## 4. Evaluation Integrity

Confirmed:
- official score ownership remains `experiments.external_validation`
- SRP diagnostics remain a separate bridge-level layer
- the artifact does not collapse official score and SRP diagnostics into a single value
- the runtime contract owner remains `external_validation`
- the bridge runner packages outputs after the official evaluation flow

Boundary note:
- the bridge artifact reports the official LongMemEval score
- the bridge also reports SRP diagnostics separately
- these two layers remain explicitly distinct

---

## 5. Provenance and Policy

Confirmed:
- `data/external/longmemeval/` remains metadata-only
- the no-payload-in-repository policy is preserved
- provenance and runtime identifiers are present in `metadata.json`
- release-branch identifiers are preserved in the bridge execution record

No changes were made to:
- `paper/`
- evidence manifests
- the official scorer
- the runtime contract semantics

---

## 6. Decision

Status:
- `PASS`

Meaning:
- the LongMemEval bridge artifact is auditable and release-ready as a benchmark-family artifact
- the final v5 bundle is the authoritative bridge evidence

Next allowed action:
- write the LongMemEval bridge closure review and proceed to the next benchmark phase

