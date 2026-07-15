# SRP LongMemEval Calibration-Aware External Validation Report

This report re-runs the frozen LongMemEval MVP slice under the calibration-aware temporal attribution protocol.
It is still a calibration-aware artifact, not a promotion of external validity.

## 1. Frozen Scope

- Benchmark: `LongMemEval`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/longmemeval`

## 2. Official Benchmark Result

- Record count: `24`
- semantic_coverage: `0.770833`
- semantic_drift: `0.320833`
- fact_accuracy: `0.916667`
- relation_accuracy: `0.625`
- recovery_accuracy: `0.814421`
- closure_accuracy: `0.625`
- neighborhood_completeness: `0.9375`
- hallucinated_relation_rate: `0.6875`
- evidence_cost: `1.8475`
- answer_accuracy: `0.901596`
- official_metric_score: `0.901596`

## 3. Temporal Attribution Protocol V1

- Step 1: `memory_correctness`
  - Input: `gold temporal fact + recovered semantic state`
  - Decision: inspect whether the recovered semantic state preserves the temporal relation and entity fact
- Step 2: `generation_correctness`
  - Input: `recovered semantic state + generated answer`
  - Decision: inspect whether the answer faithfully verbalizes the recovered state
- Step 3: `scorer_alignment`
  - Input: `generated answer + official scorer`
  - Decision: inspect whether the official score matches the semantic diagnosis

Interpretation boundary: Scorer mismatches are treated as measurement issues, not SRP memory failures.

## 4. Diagnostic Calibration Result

| Case Type | Count | Mean Official | Mean Answer | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `boolean` | 12 | 1.0 | 1.0 | 0.875 | 0.225 | correct:9, incorrect:3 | correct:12 | aligned:12 | aligned:12 |
| `generic` | 12 | 0.803192 | 0.803192 | 0.666667 | 0.416667 | correct:6, incorrect:6 | correct:9, uncertain:3 | aligned:9, uncertain:3 | aligned:9, memory_mismatch:3 |

### Baseline Calibration Summary

| Baseline | Count | Mean Official | Mean Answer | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `full_context` | 6 | 1.0 | 1.0 | 1.0 | 0.1 | correct:6 | correct:6 | aligned:6 | aligned:6 |
| `sliding_window` | 6 | 0.606383 | 0.606383 | 0.333334 | 0.733333 | incorrect:6 | correct:3, uncertain:3 | aligned:3, uncertain:3 | aligned:3, memory_mismatch:3 |
| `srp` | 6 | 1.0 | 1.0 | 1.0 | 0.1 | correct:6 | correct:6 | aligned:6 | aligned:6 |
| `vector_rag` | 6 | 1.0 | 1.0 | 0.75 | 0.35 | correct:3, incorrect:3 | correct:6 | aligned:6 | aligned:6 |

## 5. Failure Attribution Distribution

- aligned: `21`
- memory_mismatch: `3`

## 6. Evidence Promotion Decision

- adapter: `pass`
- temporal_protocol: `pass`
- scorer_alignment: `pending`
- failure_attribution: `interpretable`
- promotion: `pending`

Notes:
- Calibration-aware rerun preserves benchmark/baseline/seed settings.
- Scorer mismatches are treated as measurement issues, not SRP memory failures.

## 7. Trace Inventory

- trace count: `24`