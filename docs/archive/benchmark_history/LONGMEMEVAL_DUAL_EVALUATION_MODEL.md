# LongMemEval Dual Evaluation Model

Date: 2026-07-21

This document distinguishes the two evaluation surfaces now used for LongMemEval under the SRP release workflow.

The goal is to preserve the original LongMemEval research evaluation while also maintaining a shared benchmark alignment track that fits the MMLU and ARC artifact contract.

---

## 1. Why Two Evaluation Surfaces Exist

LongMemEval answers a different research question than MMLU and ARC.

The original LongMemEval setup measures:
- memory runtime behavior
- semantic drift / semantic shift
- recovery fidelity
- retrieval alignment
- temporal consistency
- context reconstruction quality

The shared benchmark track measures:
- artifact contract compatibility
- prompt leakage control
- baseline/SRP pairing
- provenance and hash tracking
- release-branch auditability

These are related, but they are not the same question.

---

## 2. Track A - Original LongMemEval Research Evaluation

Location:
- `experiments/external_validation/`

Owned by:
- the official LongMemEval scorer
- the existing external-validation runtime contract
- the original SRP semantic metrics and diagnostic reporting

Purpose:
- preserve the original research interpretation of LongMemEval
- analyze whether SRP improves memory runtime behavior

Typical outputs:
- official LongMemEval score
- semantic drift / semantic shift metrics
- recovery fidelity metrics
- retrieval alignment metrics
- temporal consistency metrics
- context reconstruction metrics

Key rule:
- this track remains authoritative for LongMemEval-specific research interpretation

---

## 3. Track B - Shared Benchmark Alignment Evaluation

Location:
- `experiments/benchmarks/longmemeval/`

Owned by:
- the LongMemEval bridge package
- the shared benchmark artifact contract

Purpose:
- align LongMemEval with the shared benchmark evidence framework
- make LongMemEval auditable alongside MMLU and ARC

Typical outputs:
- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

Key rule:
- this track does not replace the official scorer
- this track does not redefine LongMemEval semantics

---

## 4. Metric Boundary

Do not merge the two tracks into one blended score.

Allowed separation:

```json
{
  "official_metrics": {
    "longmemeval_score": 0.0
  },
  "srp_runtime_metrics": {
    "semantic_shift": 0.0,
    "memory_coverage": 0.0,
    "recovery_fidelity": 0.0
  },
  "shared_alignment_metrics": {
    "accuracy": 0.0
  }
}
```

Not allowed:
- a single combined metric that erases the difference between official LongMemEval scoring and SRP runtime diagnostics

---

## 5. Relationship Between the Tracks

The two tracks answer different questions:

- Track A asks whether SRP improves LongMemEval as a memory/runtime benchmark
- Track B asks whether LongMemEval can be represented safely inside the shared benchmark evidence framework

The bridge artifact is therefore an alignment surface, not a substitute for the original evaluation surface.

---

## 6. Release Integration Policy

Before evidence manifest updates:
- keep Track A and Track B distinct
- keep official scorer ownership unchanged
- keep the no-payload policy unchanged
- keep the bridge artifact auditable on its own

After both tracks are complete:
- integrate only audited outputs into the release evidence review
- preserve the distinction between original research evaluation and shared benchmark alignment

---

## 7. Interpretation Guidance

Paper-facing language should reflect the dual-track structure:

- LongMemEval provides the original memory/runtime evidence
- the bridge provides shared benchmark alignment evidence
- the two should not be collapsed into a single summary statistic

This preserves research boundary separation and avoids overstating a mixed evaluation result.

