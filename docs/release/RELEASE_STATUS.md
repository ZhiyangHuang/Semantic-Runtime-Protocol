# Semantic Runtime Protocol Release Status

Status:
- `RELEASE_EVIDENCE_READY`

## Validated Benchmarks

| Benchmark | Metric | Artifact |
|---|---|---|
| MMLU | Accuracy | `experiments/results/mmlu_full_v3/` |
| ARC | Accuracy | `experiments/results/arc_full_v1/` |
| LongMemEval | Official scorer + bridge alignment | `experiments/results/longmemeval_full_v5/` |
| HumanEval | pass@1 | `experiments/results/humaneval_full_v1/` |

## Validation Guarantees

- prompt leakage checks completed
- artifact contracts validated
- provenance preserved
- historical invalid runs excluded from release evidence

## Evidence Authority

- MMLU, ARC, HumanEval: shared benchmark evidence framework
- LongMemEval: external_validation official scorer plus bridge artifact alignment
