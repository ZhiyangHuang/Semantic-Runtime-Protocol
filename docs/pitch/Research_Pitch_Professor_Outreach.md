# Research Pitch: Semantic Runtime Protocol for Long-Horizon LLM Systems

## Project Title

**Semantic Runtime Protocol (SRP): Toward Bounded Semantic Drift in Long-Horizon LLM Interaction**

## One-Paragraph Summary

I am developing a small but focused research project on long-horizon LLM systems. The core problem is that when context is repeatedly compressed, summarized, or retrieved across many turns, semantic information gradually drifts, making the system less stable over time. My proposed direction, **Semantic Runtime Protocol (SRP)**, treats semantic state as a structured runtime object rather than raw prompt text, external memory, or agent trajectory. The first-stage goal is not to build a large framework, but to test a minimal hypothesis: **whether a structured compression-recovery protocol can better maintain bounded semantic drift than standard prompt, summarization, and retrieval baselines**.

## Research Motivation

Current long-context LLM systems usually depend on one of three paradigms:

- Raw prompt accumulation
- Summarization-based memory
- Retrieval-based memory

These approaches are useful, but they do not explicitly model semantic state as something that can be transformed, recovered, validated, and updated under a formal runtime abstraction. My project asks whether long-horizon stability can be improved by managing semantic state directly instead of relying only on context heuristics.

## Core Idea

SRP models a system state as:

```text
S = (M, V, P)
```

where:

- `M` is structured semantic memory
- `V` is the active vocabulary or semantic projection
- `P` is the policy governing transformation and update

The minimal protocol focuses on four operators:

- `Compression`: convert semantic state into a compact structured form
- `Recovery`: reconstruct a usable state from that compact form
- `Validation`: check whether the recovered state preserves task-relevant meaning
- `Update`: revise the semantic state over repeated interaction

The main hypothesis is:

> A structured semantic-state protocol can reduce semantic degradation over repeated compression-recovery cycles while remaining token-efficient.

## Minimal Experiment Plan

To keep the project realistic for one semester, I plan to run a minimal publishable experiment on three task types:

- Multi-turn instruction consistency
- Long-context summarization and regeneration
- Iterative compression-recovery cycles

Baselines:

- Raw prompt
- Summarization memory
- Retrieval-based memory

SRP evaluation metrics:

- Semantic drift
- Task success rate
- Token cost
- Stability over repeated iterations

The key figure will be a **drift-over-iterations curve** comparing SRP with the baselines.

## Planned Deliverables This Semester

- A short research paper or workshop-style draft
- A reproducible experimental codebase
- A small benchmark setup for long-horizon semantic stability
- Figures showing drift, task performance, and token tradeoffs

## Why I Am Reaching Out

I am an undergraduate student with one semester remaining, and I want to turn my final stage at Hunter into a serious research effort with clear scope, measurable output, and strong faculty feedback. I am especially looking for:

- Direction on whether this problem framing is researchable
- Advice on how to narrow the scope further if needed
- Possibility of independent study, project supervision, or periodic feedback
- Referral to another faculty member if the topic is better aligned elsewhere

## Why This Project May Be Worth Advising

- The scope is intentionally narrowed to a testable first paper rather than a large speculative system
- The implementation is lightweight and does not require training a new model
- The outcome is useful both academically and practically: theory framing, evaluation methodology, and reproducible LLM systems experimentation
- Even if the full SRP vision is larger, the first-stage experiment stands on its own as a concrete research question

## Current Status

I already have:

- A draft introduction framing SRP as a semantic state runtime abstraction
- A minimal experimental design with baselines and metrics
- A broader blueprint document that identifies future extensions but also clarifies what should be deferred

My current priority is to convert these materials into a clean, advisor-friendly first-stage project.

## Request

If this direction seems potentially promising, I would be grateful for the opportunity to discuss it briefly and get your advice on whether it could be shaped into an independent study, supervised project, or early-stage paper.
