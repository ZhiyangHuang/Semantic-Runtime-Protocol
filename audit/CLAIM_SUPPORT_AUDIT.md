# Claim Support Audit

This document is an independent audit of how well the current evidence chain supports the paper's main claims.
It is not a new experiment result and not a rewrite of the paper narrative.

## Purpose

The goal is to answer a narrow question:

> Which paper claims are already supported by the frozen evidence chain, and which ones still need external validation?

## Claim Support Matrix

| Claim | Supporting evidence | Support level | Sufficient? | Notes |
| --- | --- | --- | --- | --- |
| SRP can reject unsupported semantic transitions | [REAL_VALIDATION_BASELINE_COMPARISON.md](REAL_VALIDATION_BASELINE_COMPARISON.md), [REAL_VALIDATION_FAILURE_ANALYSIS.md](REAL_VALIDATION_FAILURE_ANALYSIS.md), [REAL_VALIDATION_SCIENTIFIC_REPORT.md](REAL_VALIDATION_SCIENTIFIC_REPORT.md) | Strong | Yes | The direct-mutation baseline accepts `unsupported_mutation` while SRP rejects it. |
| Recommendation is separated from execution | [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md), [REAL_VALIDATION_BASELINE_COMPARISON.md](REAL_VALIDATION_BASELINE_COMPARISON.md) | Strong | Yes | The SRP run preserves `recommendation_execution_separated = true`; the baseline does not. |
| Evidence can strengthen verification without increasing authority | [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md), [REAL_VALIDATION_FAILURE_ANALYSIS.md](REAL_VALIDATION_FAILURE_ANALYSIS.md), [EXPERIMENT_SELECTION_POLICY.md](EXPERIMENT_SELECTION_POLICY.md) | Moderate | Yes | Supported on the current LoCoMo slice; scope is intentionally narrow. |
| Governed semantic evolution is a real system behavior, not only a design statement | [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md), [REAL_VALIDATION_BASELINE_COMPARISON.md](REAL_VALIDATION_BASELINE_COMPARISON.md), [REAL_VALIDATION_SCIENTIFIC_REPORT.md](REAL_VALIDATION_SCIENTIFIC_REPORT.md) | Strong | Yes | The observed difference is mechanism-level, not score-level. |
| The current LoCoMo evidence chain is externally auditable and reproducible | [EXPERIMENT_EVIDENCE_STATUS.md](EXPERIMENT_EVIDENCE_STATUS.md), [EXPERIMENT_SELECTION_POLICY.md](EXPERIMENT_SELECTION_POLICY.md), [REAL_VALIDATION_ARTIFACT_POLICY.md](REAL_VALIDATION_ARTIFACT_POLICY.md) | Strong | Yes | Data source, selection rule, artifact bundle, and report are all frozen. |
| LongMemEval can serve as external generalization validation | [EXPERIMENT_EVIDENCE_STATUS.md](EXPERIMENT_EVIDENCE_STATUS.md), [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md), [REAL_VALIDATION_PROTOCOL_LONGMEMEVAL.md](REAL_VALIDATION_PROTOCOL_LONGMEMEVAL.md) | Pending | No | The adapter and contract are ready, but the real-data slice is still missing. |
| SRP is broadly applicable across memory workloads | [paper/SRP_ARXIV_DRAFT_V1.md](../paper/SRP_ARXIV_DRAFT_V1.md), [REAL_VALIDATION_REPORT.md](REAL_VALIDATION_REPORT.md) | Partial | Not yet | Needs LongMemEval real-data evidence before being treated as externally generalized. |

## Interpretation

Claims that are marked `Yes` are supported by the current frozen evidence chain in the evaluated setting.
Claims that are marked `No` or `Not yet` should remain bounded in the manuscript and should not be upgraded by implication.

The most important result is the mechanism claim:

- a direct-mutation path accepts an unsupported transition
- SRP rejects that same transition

That is the strongest current support for the governance boundary claim.

## Audit Boundary

This audit is intentionally conservative.
It does not treat fixture-backed LongMemEval runs as empirical evidence.
It does not promote claims that depend on missing real-data validation.
It only records the current support status of the claims already present in the paper and audit chain.
