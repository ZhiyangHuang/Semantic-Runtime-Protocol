# SRP LongMemEval External Validation Evidence Report

This report records the evidence run layer for LongMemEval under a frozen shared-generation runtime contract.
It is evidence, not calibration, and it uses the same local vLLM endpoint across baselines and SRP.

## 1. Frozen Scope

- Benchmark: `longmemeval`
- Baselines: `full_context, sliding_window, vector_rag, mem0, graphiti, letta, memmachine, srp`
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

- Case count: `48`
- semantic_coverage: `0.885417`
- semantic_drift: `0.210417`
- fact_accuracy: `0.958333`
- relation_accuracy: `0.8125`
- recovery_accuracy: `0.904948`
- closure_accuracy: `0.8125`
- neighborhood_completeness: `0.96875`
- hallucinated_relation_rate: `0.59375`
- evidence_cost: `1.368262`
- answer_accuracy: `0.94401`
- official_metric_score: `0.94401`

## 4. Diagnostic Result

### longmemeval
- semantic_coverage: `0.885417`
- semantic_drift: `0.210417`
- fact_accuracy: `0.958333`
- relation_accuracy: `0.8125`
- recovery_accuracy: `0.904948`
- closure_accuracy: `0.8125`
- neighborhood_completeness: `0.96875`
- hallucinated_relation_rate: `0.59375`
- evidence_cost: `1.368262`
- answer_accuracy: `0.94401`
- official_metric_score: `0.94401`

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
- mem0:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `0.8265`
  - answer_accuracy: `1.0`
- graphiti:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `0.9396`
  - answer_accuracy: `1.0`
- letta:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `0.87`
  - answer_accuracy: `1.0`
- memmachine:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `0.92`
  - answer_accuracy: `1.0`
- srp:
  - semantic_coverage: `1.0`
  - semantic_drift: `0.1`
  - relation_accuracy: `1.0`
  - evidence_cost: `0.69`
  - answer_accuracy: `1.0`

## 5. Failure Summary

- counts: `{'domain_mismatch': 9, 'evidence_failure': 48, 'relation_failure': 9, 'representation_failure': 3}`
- examples: `{'domain_mismatch': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'evidence_failure': ['longmemeval:full_context:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision'], 'relation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:vector_rag:preference_revision', 'longmemeval:sliding_window:contradiction_resolution'], 'representation_failure': ['longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision', 'longmemeval:sliding_window:preference_revision']}`

## 6. Statistical Reporting

The statistics below are descriptive only for the predefined 48-case LongMemEval evidence slice.
They support measurement transparency and reproducibility, not inferential claims about the full benchmark.
### Overall descriptive statistics

| Metric | Mean | Std | 95% CI | N |
| --- | ---: | ---: | ---: | ---: |
| semantic_coverage | `0.885417` | `0.248039` | `0.070171` | `48` |
| semantic_drift | `0.210417` | `0.236208` | `0.066824` | `48` |
| fact_accuracy | `0.958333` | `0.161374` | `0.045653` | `48` |
| relation_accuracy | `0.8125` | `0.390312` | `0.11042` | `48` |
| recovery_accuracy | `0.904948` | `0.22462` | `0.063545` | `48` |
| closure_accuracy | `0.8125` | `0.390312` | `0.11042` | `48` |
| neighborhood_completeness | `0.96875` | `0.121031` | `0.03424` | `48` |
| hallucinated_relation_rate | `0.59375` | `0.195156` | `0.05521` | `48` |
| evidence_cost | `1.368262` | `1.579429` | `0.446823` | `48` |
| answer_accuracy | `0.94401` | `0.216847` | `0.061346` | `48` |
| official_metric_score | `0.94401` | `0.216847` | `0.061346` | `48` |

### Baseline descriptive statistics

| Baseline | N | Answer Acc. mean | Answer Acc. std | Answer Acc. CI95 | Evidence Cost mean | Evidence Cost std | Evidence Cost CI95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| full_context | `6` | `1.0` | `0.0` | `0.0` | `5.5` | `0.5` | `0.400083` |
| sliding_window | `6` | `0.552083` | `0.447916` | `0.358408` | `0.48` | `0.0` | `0.0` |
| vector_rag | `6` | `1.0` | `0.0` | `0.0` | `0.72` | `0.06` | `0.04801` |
| mem0 | `6` | `1.0` | `0.0` | `0.0` | `0.8265` | `0.0855` | `0.068414` |
| graphiti | `6` | `1.0` | `0.0` | `0.0` | `0.9396` | `0.0972` | `0.077776` |
| letta | `6` | `1.0` | `0.0` | `0.0` | `0.87` | `0.09` | `0.072015` |
| memmachine | `6` | `1.0` | `0.0` | `0.0` | `0.92` | `0.08` | `0.064013` |
| srp | `6` | `1.0` | `0.0` | `0.0` | `0.69` | `0.07` | `0.056012` |

### Seed descriptive statistics

| Seed | N | Answer Acc. mean | Answer Acc. std | Answer Acc. CI95 |
| --- | ---: | ---: | ---: | ---: |
| `11` | `16` | `0.94401` | `0.216847` | `0.106255` |
| `23` | `16` | `0.94401` | `0.216847` | `0.106255` |
| `37` | `16` | `0.94401` | `0.216847` | `0.106255` |

## 7. Evidence Promotion Gate

| Gate | Status | Notes |
| --- | --- | --- |
| adapter | pass | semantic adapter and benchmark ingestion are stable. |
| temporal_protocol | pass | the three-stage attribution protocol is frozen. |
| shared_generation_backend | pass | all baselines and SRP use the same local vLLM endpoint. |
| shared_tokenizer | pass | the runtime contract freezes the same tokenizer. |
| prompt_equivalence | pass | the prompt family is shared across systems. |
| scorer_alignment | pass | the remaining temporal and multi-hop acceptance items are closed on the frozen slice. |
| statistical_reporting | pass | descriptive statistics are reported for the fixed 48-case slice. |
| statistical_inference | not_required | inferential statistics are deferred until a larger official benchmark slice is used. |
| promotion | ready | paper-facing promotion is ready for a paper decision under the frozen audit boundary. |

## 8. Scorer Alignment Audit

| Audit Item | Official Scorer | SRP Wrapper | Result | Notes |
| --- | --- | --- | --- | --- |
| Exact match | Yes | Yes | Pass | Normalized exact comparison is consistent for direct-answer cases. |
| Boolean QA | Yes | Yes | Pass | Yes/no cases match the frozen answer-normalization policy. |
| Preference revision | Yes | Yes | Pass | The current slice resolves the updated preference correctly. |
| Contradiction resolution | Yes | Yes | Pass | Temporal negation is interpreted consistently in the wrapper. |
| Normalization | Yes | Yes | Pass | Lowercasing, whitespace trimming, and punctuation handling are frozen. |
| Temporal reasoning | Yes | Verified | Pass | Representative before/after/update/replacement cases match the official scorer semantics. |
| Multi-hop reasoning | Yes | Verified | Pass | Representative hop-chain coverage matches the official scorer semantics without changing candidate/fact separation. |
| Unsupported outputs | Yes | Yes | Pass | Empty or malformed outputs are handled as wrapper-level failures, not scorer successes. |

Overall scorer alignment status: `pass`

## 9. Evidence Audit Notes

- `hallucinated_relation_rate` measures extra recovered relations beyond the target state, so it can remain non-zero even when target relations are fully recovered.
- `evidence_cost` is an internal recovery cost unit derived from selected units and relations; it is not a token-count proxy.
- The official benchmark score and the SRP diagnostics are co-reported but are not forced to share the same numerical objective.
- The prompt template id is frozen in the runtime contract so baseline and SRP generation share the same prompt family.
- The audit specification is frozen in `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md` and governs promotion to paper-facing evidence.
- The current result favors semantic recall over aggressive relation pruning; future provenance-aware variants can distinguish observed, inferred, and uncertain relations with confidence metadata, user-verification status, and a `promotion_state` field (`candidate`, `verified`, `rejected`).
- In the current governance framing, `candidate` relations are available for retrieval and explanation, `verified` relations can enter persistent semantic state, and `rejected` relations are excluded from future recovery.

## 10. Trace Inventory

- trace count: `48`
