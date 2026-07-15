# SRP LongMemEval Evidence Promotion Decision

This document freezes the paper-facing promotion decision for the LongMemEval evidence package.
It is a decision artifact, not a new benchmark run, not a calibration note, and not a theory revision.

## 1. Scope

- Evidence package: `experiments/results/external_validation_longmemeval_evidence_strong_baselines/`
- Benchmark: `longmemeval`
- Runtime contract: frozen shared local-vLLM contract
- Baselines: `full_context, sliding_window, vector_rag, mem0, graphiti, letta, memmachine, srp`
- Slice size: `48` records

## 2. Completed Gates

| Gate | Status | Notes |
| --- | --- | --- |
| Runtime reproducibility | Pass | model, tokenizer, prompt, endpoint, temperature, and output budget are frozen |
| Baseline comparability | Pass | all baselines use the same shared runtime contract |
| Scorer alignment | Pass | temporal and multi-hop acceptance items are closed on the frozen slice |
| Statistical reporting | Pass | descriptive statistics are reported for the fixed slice |
| Failure interpretation boundary | Pass | candidate recovery is separated from fact commitment |
| Evidence artifact package | Pass | report, manifest, traces, and audit notes are present |

## 3. Remaining Risks

The following limitations remain, but they do not block promotion for the current paper scope:

1. The evidence slice is fixed and limited to 48 records.
2. Statistical summaries are descriptive only and not inferential for the full benchmark population.
3. Future provenance-aware SRP improvements, such as confidence-aware pruning and verification loops, remain future work.

## 4. Decision

**Approve**

The LongMemEval evidence package may be promoted to paper-facing external validity evidence under the frozen runtime contract and frozen audit boundary.

The paper should describe the result as:

> a promoted external-validation evidence package under a frozen evaluation contract

It should not claim:

> complete benchmark-wide inferential proof

## 5. Paper Use

The paper may use this package as part of the external-validity results section, provided the limitations above are stated explicitly.
