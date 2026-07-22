# SRP Paper Consolidation Map

## Purpose

This document organizes the paper-facing evidence and narrative surfaces for the current SRP release boundary.

It does not change the manuscript, evidence policy, or claim ledger.
It is a paper-organization artifact for the frozen release state.

## Narrative Spine

The paper currently reads most cleanly as:

1. Semantic state transitions can be governed.
2. Evidence is not authority.
3. Validation, optimization, evidence, governance, and execution are separable layers.
4. External environments can be routed through the same admission semantics.

## Core Paper Surfaces

| Surface | Role |
| --- | --- |
| `paper/SRP_ARXIV_DRAFT_V1.md` | synchronized manuscript mirror |
| `paper/SRP_PAPER_FINAL_V1.md` | submission snapshot |
| `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` | compact release-facing evidence map |
| `docs/release/SRP_EVIDENCE_SURFACE_V1_1.md` | consolidated evidence surface for SRP v1.1 |
| `audit/CLAIM_EVIDENCE_MAP.md` | claim ledger |
| `docs/release/RELEASE_EVIDENCE_REVIEW.md` | release evidence review |
| `docs/release/RELEASE_READY_CHECKLIST.md` | release readiness state |
| `docs/analysis/CROSS_ENVIRONMENT_ANALYSIS.md` | external validation interpretation layer |

## Claim Alignment

The current manuscript claims are best supported by the following evidence surfaces:

| Claim Cluster | Primary Support |
| --- | --- |
| Governance boundary and authority separation | `audit/CLAIM_EVIDENCE_MAP.md`, `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` |
| Reproducible release boundary | `docs/release/RELEASE_EVIDENCE_REVIEW.md`, `docs/release/RELEASE_READY_CHECKLIST.md` |
| External validation portability | `STFB/external/README.md`, `docs/analysis/CROSS_ENVIRONMENT_ANALYSIS.md`, `docs/release/SRP_EVIDENCE_SURFACE_V1_1.md` |

## Evidence Surface View

The strongest current evidence narrative is assembled in `docs/release/SRP_EVIDENCE_SURFACE_V1_1.md`.

That document consolidates:

- mechanism validation from STFB
- external validation from LongMemEval and ARC
- capability stress evidence from MMLU and HumanEval

It should be treated as a consolidation layer, not a new benchmark definition.

## Figure and Table Order

The paper is easiest to read when the main visuals follow this order:

1. governance pipeline figure
2. authority separation table
3. main results summary table
4. external validation evidence table
5. cross-environment mechanism matrix
6. divergence analysis table

## What to Keep Stable

- the claim ledger should stay short and selective
- benchmark reports should remain benchmark-specific
- external validation should remain an evidence layer, not a new benchmark identity
- cross-environment analysis should remain interpretive, not experimental
- the evidence surface should remain a consolidation layer for the frozen release state

## Submission Readiness Note

The manuscript boundary is strongest when the paper and the evidence layers preserve the same vocabulary:

- evidence strengthens verification
- authority governs mutation
- external environments test portability, not superiority

This note should be used as a release-oriented checklist when preparing future submission material.
