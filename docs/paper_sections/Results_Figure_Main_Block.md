# Results Figure Main Block

This note preserves the compact, reviewer-facing core of the empirical story so the main draft can stay narrow without losing evidence binding.

## Purpose

The first paper should keep one stable message:

> SRP improves finite-horizon semantic stability under repeated compression-recovery cycles while preserving a favorable efficiency tradeoff.

This file keeps the main result block, the figure narrative, and the evidence-binding context that should remain visible in the project overview even if the submission draft is compressed further.

## Main Figure Narrative

> **Three-panel main results.** (A) Semantic drift across cycle depths for four methods. SRP consistently achieves the lowest drift and remains stable as cycle depth increases, while summarization degrades sharply and both raw prompt and RAG exhibit substantially higher drift. (B) Token cost versus drift Pareto frontier. SRP occupies a low-drift, low-token region, indicating that improvements are not attributable to increased computational budget. (C) SRP contract stability. Contract satisfaction remains stable across cycles, and commit decisions track semantic contract compliance rather than lexical similarity, suggesting that execution stability is governed by semantic consistency rather than surface-form preservation.

### Summary Paragraph

Figure X summarizes the core empirical behavior of SRP across cycle depths and evaluation axes. SRP consistently achieves the lowest semantic drift among all methods, and this advantage persists as cycle depth increases, suggesting that the effect is structurally induced rather than a consequence of shallow-task optimization or run variance.

In the efficiency-quality tradeoff space, SRP occupies a distinct low-drift, low-token regime. This separates it from summarization, which minimizes token usage but exhibits high semantic instability, and from raw prompt and RAG baselines, which maintain higher drift despite comparable or higher resource consumption.

The contract stability analysis further indicates that SRP commit behavior remains aligned with semantic contract satisfaction across cycles. This suggests that execution decisions are driven by semantic compliance signals rather than surface-form similarity.

Taken together, the results indicate that SRP improves long-horizon semantic stability without sacrificing efficiency, and establishes a consistent operating regime distinct from the evaluated baselines.

## Evidence Binding

The main narrative above is supported by the following qualified artifacts:

- `EQ` gate report
- runtime equivalence traces
- formal batch results
- main 3-panel figure
- quality, efficiency, guardrail, and camera-ready tables

The evidence package used for the first paper is intentionally small but complete enough to support a reviewer-facing claim.

## What Stays in the Main Draft

The main submission draft should keep:

- the narrow claim about bounded semantic drift
- the 3-panel main figure narrative
- the quality / efficiency / guardrail summary
- the camera-ready comparison table
- the restrained interpretation of results

## What Can Be Moved Out of the Main Draft

The following details can be compressed into project overview material or appendix-style notes without losing meaning:

- pilot evolution history
- mock backend debugging history
- runtime equivalence calibration history
- qualification pipeline mechanics
- tuning chronology for recovery and drift
- batch orchestration details

These are useful for repository credibility, reviewer questions, and reproducibility, but they do not need to appear in the main results prose.

## Project Overview Anchors

If the main draft is compressed further, these project-level anchors should remain easy to find:

- the first-paper claim is narrow and semester-scoped
- EQ gates formal experiments before paper-facing runs
- SRP is evaluated as a runtime abstraction, not a semantic operating system
- the paper's empirical burden is carried by the formal batch evidence package

## Preservation Note

If any of the above compressed material is removed from `first_paper/draft/01_Full_Draft.md`, the corresponding replacement should be a short pointer into this file rather than a deletion without a home.
