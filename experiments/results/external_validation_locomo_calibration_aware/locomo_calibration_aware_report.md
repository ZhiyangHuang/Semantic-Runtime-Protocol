# SRP LoCoMo Calibration-Aware External Validation Report

This report re-runs the frozen LoCoMo MVP slice under the calibration-aware temporal attribution protocol.
It is still a calibration-aware artifact, not a promotion of external validity.

## 1. Frozen Scope

- Benchmark: `locomo`
- Baselines: `full_context, sliding_window, vector_rag, srp`
- Seeds: `11, 23, 37`
- Data root: `data/locomo`

## 2. Official Benchmark Result

- Record count: `3648`
- semantic_coverage: `0.26692`
- semantic_drift: `0.690841`
- fact_accuracy: `0.268069`
- relation_accuracy: `0.265771`
- recovery_accuracy: `0.245932`
- closure_accuracy: `0.265771`
- neighborhood_completeness: `0.268092`
- hallucinated_relation_rate: `0.521886`
- evidence_cost: `252.818268`
- answer_accuracy: `0.203956`
- official_metric_score: `0.203956`

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
| `boolean` | 72 | 0.444444 | 0.444444 | 0.274306 | 0.669852 | correct:18, incorrect:51, uncertain:3 | correct:30, incorrect:9, uncertain:33 | aligned:30, false_negative:9, uncertain:33 | aligned:30, generation_or_scorer_mismatch:9, memory_mismatch:33 |
| `generic` | 2556 | 0.167562 | 0.167562 | 0.267693 | 0.691003 | correct:676, incorrect:1875, uncertain:5 | correct:48, incorrect:649, uncertain:1859 | aligned:48, false_negative:649, uncertain:1859 | aligned:48, generation_or_scorer_mismatch:649, memory_mismatch:1854, mixed:5 |
| `location` | 120 | 0.142277 | 0.142277 | 0.25 | 0.719659 | correct:30, incorrect:90 | incorrect:30, uncertain:90 | false_negative:30, uncertain:90 | generation_or_scorer_mismatch:30, memory_mismatch:90 |
| `person` | 60 | 0.271372 | 0.271372 | 0.25 | 0.693133 | correct:15, incorrect:45 | correct:9, incorrect:12, uncertain:39 | aligned:9, false_negative:12, uncertain:39 | aligned:9, generation_or_scorer_mismatch:12, memory_mismatch:39 |
| `quantity` | 96 | 0.180204 | 0.180204 | 0.268229 | 0.682595 | correct:24, incorrect:69, uncertain:3 | incorrect:24, uncertain:72 | false_negative:24, uncertain:72 | generation_or_scorer_mismatch:24, memory_mismatch:69, mixed:3 |
| `relation` | 12 | 0.226716 | 0.226716 | 0.25 | 0.6995 | correct:3, incorrect:9 | incorrect:3, uncertain:9 | false_negative:3, uncertain:9 | generation_or_scorer_mismatch:3, memory_mismatch:9 |
| `temporal` | 732 | 0.314711 | 0.314711 | 0.26776 | 0.688367 | correct:192, incorrect:534, uncertain:6 | correct:105, incorrect:180, uncertain:447 | aligned:105, false_negative:180, uncertain:447 | aligned:105, generation_or_scorer_mismatch:180, memory_mismatch:444, mixed:3 |

### Baseline Calibration Summary

| Baseline | Count | Mean Official | Mean Answer | Mean Coverage | Mean Drift | Memory | Generation | Scorer | Attribution |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| `full_context` | 912 | 0.198669 | 0.198669 | 1.0 | 0.198796 | correct:912 | correct:33, incorrect:879 | aligned:33, false_negative:879 | aligned:33, generation_or_scorer_mismatch:879 |
| `sliding_window` | 912 | 0.23401 | 0.23401 | 0.009868 | 0.792105 | correct:9, incorrect:903 | correct:99, incorrect:6, uncertain:807 | aligned:99, false_negative:6, uncertain:807 | aligned:99, generation_or_scorer_mismatch:6, memory_mismatch:807 |
| `srp` | 912 | 0.192886 | 0.192886 | 0.039594 | 0.955678 | correct:28, incorrect:873, uncertain:11 | correct:30, incorrect:16, uncertain:866 | aligned:30, false_negative:16, uncertain:866 | aligned:30, generation_or_scorer_mismatch:16, memory_mismatch:858, mixed:8 |
| `vector_rag` | 912 | 0.19026 | 0.19026 | 0.018217 | 0.816786 | correct:9, incorrect:897, uncertain:6 | correct:30, incorrect:6, uncertain:876 | aligned:30, false_negative:6, uncertain:876 | aligned:30, generation_or_scorer_mismatch:6, memory_mismatch:873, mixed:3 |

## 5. Failure Attribution Distribution

- aligned: `192`
- generation_or_scorer_mismatch: `907`
- memory_mismatch: `2538`
- mixed: `11`

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

- trace count: `3648`