# Paper Skeleton

## Working Title

**Semantic Runtime Protocol: A Minimal Study of Bounded Semantic Drift in Long-Horizon LLM Interaction**

## Abstract

Long-horizon LLM systems remain unstable when contextual information must be repeatedly compressed, summarized, or retrieved across many interaction steps. Existing approaches such as prompt accumulation, summarization memory, and retrieval-based memory improve context management but do not provide an explicit semantic-state runtime abstraction for semantic state itself. We present **Semantic Runtime Protocol (SRP)**, a minimal semantic-state abstraction for studying finite-horizon stability under repeated compression-recovery cycles. The paper makes a narrow claim: explicit semantic-state management can improve bounded semantic drift behavior relative to lightweight baselines while remaining token-efficient over a finite horizon. We formalize SRP as a simple closed-loop transformation protocol, use bounded semantic drift as the main analysis lens, and outline a reproducible experiment comparing SRP with lightweight baselines on long-horizon consistency tasks. The contribution of this semester-version paper is a small but testable runtime framing for long-horizon LLM stability, not a full semantic operating system.

## 1. Introduction

Use and refine material from [01_Introduction.md](/abs/path/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/paper_sections/01_Introduction.md).

Keep the introduction aligned with the same reviewer-facing claims:

- long-horizon interaction is unstable under repeated context transformation
- existing memory, retrieval, and agent systems do not formalize semantic state as a first-class runtime object
- SRP introduces a semantic-state runtime abstraction
- the main claim is bounded semantic drift, not universal semantic correctness
- the contributions are formalization, protocol design, and empirical evaluation

## 2. Related Work

Organize related work into five groups.

### 2.1 Prompt Compression

- LLMLingua
- context-aware prompt compression
- summary-based context replacement

Gap:

- These methods optimize prompt length, but do not define semantic state as an explicit runtime object.

### 2.2 Memory-Augmented LLM Systems

- summarization memory
- retrieval-based memory
- vector-store assistants

Gap:

- Memory is stored or retrieved, but transformation semantics and recovery guarantees are not explicit.

### 2.3 Agent Frameworks

- trajectory-based agent systems
- planning and tool-use pipelines

Gap:

- Agent trajectories encode process history, not a formal semantic state abstraction.

### 2.4 Semantic Communication and Calibration

- semantic communication
- concept-level calibration
- equivalence-oriented evaluation

Gap:

- These works motivate semantic representation but do not directly instantiate a runtime protocol for long-horizon interaction.

### 2.5 Reproducibility and LLM Evaluation

- replay systems
- experiment databases
- prompt reproducibility studies

Gap:

- These works motivate the need for measurement and replay, which SRP uses as supporting infrastructure.

## 3. Runtime State and Operators

Use the system-level material from [03_Formalization.md](/abs/path/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/paper_sections/03_Formalization.md), but only include the first-paper subset.

Keep only:

- semantic runtime state tuple `S_t = (M_t, V_t, P_t)`
- compression
- recovery
- validation
- update
- observable semantics
- bounded semantic drift

Also preserve the open design questions that the first paper should not overclaim:

- runtime vs protocol framing
- minimal semantic-state object
- best drift proxy
- failure boundary

The runtime framing should stay consistent with `01_Introduction.md`: memory stores records, while runtime governs transitions, validation, recovery, and update.

Move the following to future work unless absolutely necessary:

- namespace
- ACL and governance details
- migration
- dual-RL optimization
- full enterprise architecture

## 4. Formalization

Use and refine [03_Formalization.md](/abs/path/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/paper_sections/03_Formalization.md).

Core content:

- define runtime state
- define state transition operators
- define observable behavior mapping
- define semantic error
- define state sufficiency error
- define iterative drift
- define bounded semantic drift
- state finite-horizon drift lemma
- state the failure boundary

Tone guidance:

- modest
- precise
- non-grandiose

Suggested content alignment:

- semantic state tuple
- observable behavior mapping
- semantic error
- state sufficiency
- iterative drift
- bounded drift
- finite-horizon lemma
- failure boundary

## 5. Experimental Setup

Use and refine [04_Experiment_Section.md](/abs/path/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/docs/paper_sections/04_Experiment_Section.md).

Minimum content:

- tasks
- baselines
- implementation details
- metrics
- ablations

The experiment section should remain consistent with the introduction by using the same vocabulary:

- prompt accumulation
- summarization memory
- retrieval-based memory
- SRP

## 6. Results

This section should eventually contain:

- Drift-over-iterations curve
- Task success comparison
- Token cost versus performance plot

Recommended claims:

- SRP reduces drift accumulation relative to summarization and retrieval baselines
- Validation and recovery both matter
- Structured state can improve efficiency-stability tradeoffs

The result section should not introduce a different positioning story. It should stay inside the same narrow claim stated in the introduction.

Avoid claiming:

- state-of-the-art general reasoning
- universal superiority
- broad agent replacement

## 7. Discussion

Key discussion points:

- Why semantic state differs from memory
- Why bounded drift is more realistic than exact preservation
- Why the first implementation is intentionally minimal
- What would be required to scale toward the long-term SRP design

It is also a good place to mention the open questions preserved in the introduction rather than pretending they are already closed.

## 8. Limitations

State clearly:

- small-scale evaluation
- proxy-based semantic metrics
- simplified state representation
- finite-horizon rather than indefinite interaction

This honesty improves credibility.

## 9. Open Questions To Preserve

These should remain visible in the paper rather than being forced into a premature closure:

- Is SRP primarily a runtime abstraction, a protocol, or a semantic communication layer?
- What is the minimal semantic-state object?
- Which drift metric should be considered the main one in the first paper?
- What failure cases should be shown explicitly?

## 10. Future Work

Good future-work items:

- richer state schemas
- stronger validator design
- cross-model generalization
- semantic contract refinement
- replay database and benchmark expansion
- runtime lifecycle extensions such as freeze, merge, and delete
- transaction-style commit / rollback semantics

These should be framed as next-step extensions, not as missing parts of the first claim.

## 11. Submission Strategy

Best near-term targets are likely:

- workshop papers in LLM systems, NLP, or AI systems
- student research tracks
- short papers
- technical reports on arXiv plus advisor feedback

The first serious goal should be:

> a clean, reproducible, bounded-scope paper with one strong figure and one careful theoretical framing

not a maximal full-scale top-tier systems paper.

## 12. Immediate Next Steps

1. Convert the current markdown into a single integrated draft.
2. Implement the minimal experiment pipeline.
3. Produce one credible drift-over-iterations figure.
4. Get faculty feedback using the one-page research pitch.
5. Revise the paper around the actual experimental evidence.
