# SRP LongMemEval External Validation Evidence Report

This report records the evidence run layer for LongMemEval under a frozen shared-generation runtime contract.
It is evidence, not calibration, and it uses the same local vLLM endpoint across baselines and SRP.

## 1. Frozen Scope

- Benchmark: `longmemeval`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/longmemeval`

## 2. Runtime Contract

- provider: `local_vllm`
- backend: `vllm`
- endpoint: `http://172.25.253.78:8000`
- model: `Qwen/Qwen3-4B-AWQ`
- tokenizer: `Qwen/Qwen3-4B-AWQ`
- prompt_template_id: `longmemeval_shared_generation_prompt_v1`
- temperature: `0.0`
- max_output_tokens: `96`
- same_endpoint_across_baselines: `True`
- baseline_generation_backend: `shared`
- srp_generation_backend: `shared`

## 3. Official Benchmark Result

- Case count: `24`
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.809896`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.888021`
- official_metric_score: `0.888021`

## 4. Diagnostic Result

### longmemeval
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.809896`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.888021`
- official_metric_score: `0.888021`

### Baseline Summary

- full_context:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `5.5`
  - answer_accuracy: `1.0`
- sliding_window:
  - semantic_coverage: `0.333334`
  - semantic_drift: `0.733333`
  - relation_accuracy: `0.0`
  - evidence_cost: `0.48`
  - answer_accuracy: `0.552084`
- vector_rag:
  - semantic_coverage: `0.75`
  - semantic_drift: `0.35`
  - relation_accuracy: `0.5`
  - evidence_cost: `0.72`
  - answer_accuracy: `1.0`
- srp:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `0.69`
  - answer_accuracy: `1.0`

## 5. Failure Summary

- counts: `{'domain_mismatch': 9, 'evidence_failure': 24, 'relation_failure': 9, 'representation_failure': 3}`
- examples: `{'domain_mismatch': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'evidence_failure': ['longmemeval:full_context:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision'], 'relation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'representation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision']}`

## 6. Statistical Reporting

The statistics below are descriptive only for the predefined 24-case LongMemEval evidence slice.
They support measurement transparency and reproducibility, not inferential claims about the full benchmark.
### Overall descriptive statistics

| Metric | Mean | Std | 95% CI | N |
| --- | ---: | ---: | ---: | ---: |
| semantic_coverage | `0.770833` | `0.311108` | `0.124469` | `24` |
| semantic_drift | `0.320833` | `0.295305` | `0.118147` | `24` |
| fact_accuracy | `0.916667` | `0.220479` | `0.08821` | `24` |
| relation_accuracy | `0.625` | `0.484123` | `0.19369` | `24` |
| recovery_accuracy | `0.809896` | `0.287816` | `0.115151` | `24` |
| closure_accuracy | `0.625` | `0.484123` | `0.19369` | `24` |
| neighborhood_completeness | `0.9375` | `0.165359` | `0.066158` | `24` |
| hallucinated_relation_rate | `0.6875` | `0.242061` | `0.096845` | `24` |
| evidence_cost | `1.8475` | `2.126051` | `0.850598` | `24` |
| answer_accuracy | `0.888021` | `0.296269` | `0.118532` | `24` |
| official_metric_score | `0.888021` | `0.296269` | `0.118532` | `24` |

### Baseline descriptive statistics

| Baseline | N | Answer Acc. mean | Answer Acc. std | Answer Acc. CI95 | Evidence Cost mean | Evidence Cost std | Evidence Cost CI95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full_context | `6` | `1.0` | `0.0` | `0.0` | `5.5` | `0.5` | `0.400083` |
| sliding_window | `6` | `0.552083` | `0.447916` | `0.358408` | `0.48` | `0.0` | `0.0` |
| vector_rag | `6` | `1.0` | `0.0` | `0.0` | `0.72` | `0.06` | `0.04801` |
| srp | `6` | `1.0` | `0.0` | `0.0` | `0.69` | `0.07` | `0.056012` |

### Seed descriptive statistics

| Seed | N | Answer Acc. mean | Answer Acc. std | Answer Acc. CI95 |
| --- | ---: | ---: | ---: | ---: |
| `11` | `8` | `0.888021` | `0.296269` | `0.205304` |
| `23` | `8` | `0.888021` | `0.296269` | `0.205304` |
| `37` | `8` | `0.888021` | `0.296269` | `0.205304` |

## 7. Evidence Promotion Gate

| Gate | Status | Notes |
| --- | --- | --- |
| adapter | pass | semantic adapter and benchmark ingestion are stable. |
| temporal_protocol | pass | the three-stage attribution protocol is frozen. |
| shared_generation_backend | pass | all baselines and SRP use the same local vLLM endpoint. |
| shared_tokenizer | pass | the runtime contract freezes the same tokenizer. |
| prompt_equivalence | pass | the prompt family is shared across systems. |
| scorer_alignment | conditional_pass | temporal reasoning is partially verified; multi-hop checks remain incomplete. |
| statistical_reporting | pass | descriptive statistics are reported for the fixed 24-case slice. |
| statistical_inference | not_required | inferential statistics are deferred until a larger official benchmark slice is used. |
| promotion | pending | paper-facing promotion is deferred until the audit gate is fully closed. |

## 8. Scorer Alignment Audit

| Audit Item | Official Scorer | SRP Wrapper | Result | Notes |
| --- | --- | --- | --- | --- |
| Exact match | Yes | Yes | Pass | Normalized exact comparison is consistent for direct-answer cases. |
| Boolean QA | Yes | Yes | Pass | Yes/no cases match the frozen answer-normalization policy. |
| Preference revision | Yes | Yes | Pass | The current slice resolves the updated preference correctly. |
| Contradiction resolution | Yes | Yes | Pass | Temporal negation is interpreted consistently in the wrapper. |
| Normalization | Yes | Yes | Pass | Lowercasing, whitespace trimming, and punctuation handling are frozen. |
| Temporal reasoning | Yes | Partially verified | Conditional pass | The slice contains temporal cases, but larger parity checks are still needed. |
| Multi-hop reasoning | Yes | Not fully exercised | Pending | Not enough representative examples yet for a final acceptance decision. |
| Unsupported outputs | Yes | Yes | Pass | Empty or malformed outputs are handled as wrapper-level failures, not scorer successes. |

Overall scorer alignment status: `conditional_pass`

## 9. Evidence Audit Notes

- `hallucinated_relation_rate` measures extra recovered relations beyond the target state, so it can remain non-zero even when target relations are fully recovered.
- `evidence_cost` is an internal recovery cost unit derived from selected units and relations; it is not a token-count proxy.
- The official benchmark score and the SRP diagnostics are co-reported but are not forced to share the same numerical objective.
- The prompt template id is frozen in the runtime contract so baseline and SRP generation share the same prompt family.
- The audit specification is frozen in `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md` and governs promotion to paper-facing evidence.

## 10. Trace Inventory

- trace count: `24`