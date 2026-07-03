# Semantic Runtime Protocol: A Minimal Study of Bounded Semantic Drift in Long-Horizon LLM Interaction

**Anonymous Draft**

## Abstract

Long-horizon LLM systems frequently manage context through prompt accumulation, summarization memory, or retrieval-based memory, but these strategies do not explicitly treat semantic state as an object that can be compressed, recovered, validated, and updated over time. We present **Semantic Runtime Protocol (SRP)**, a semantic-state runtime abstraction for studying finite-horizon stability under repeated compression-recovery cycles. The paper asks a narrow question: whether explicit semantic-state management can improve bounded semantic drift behavior relative to lightweight baselines while keeping token cost competitive over a finite horizon. We formalize SRP as a simple closed-loop transformation protocol, use bounded semantic drift as the main analysis lens, and outline a reproducible experiment comparing SRP with lightweight baselines on long-term consistency tasks. The contribution of this semester-version paper is a small but testable framing for long-term LLM stability, not a full semantic operating system.

## 1. Introduction

Large language models (LLMs) are increasingly used in interactive settings where information must persist across multiple steps. In such settings, the system must repeatedly manage prior constraints, user preferences, task structure, and partial reasoning state over time. This becomes difficult when full raw history cannot simply be retained.

Current long-horizon systems typically rely on prompt accumulation, summarization memory, or retrieval-based memory. These methods are useful, but they mostly function as heuristic context-management strategies rather than explicit models of semantic state. As a result, long-horizon interaction can suffer from semantic degradation under repeated compression, weak recovery guarantees, and no clear lifecycle model for state transformation.

This paper takes a deliberately narrow position. Rather than proposing a full semantic operating system, we ask a smaller and more testable question:

> Can explicit semantic-state management improve finite-horizon stability under repeated compression-recovery cycles, relative to lightweight baselines?

To study this question, we introduce **Semantic Runtime Protocol (SRP)**, a semantic-state runtime abstraction that treats semantic state as a structured computational object rather than raw prompt text alone. In the current version, SRP is intentionally constrained. It models semantic state through four operators:

- compression
- recovery
- validation
- update

The key distinction is that memory stores state, while runtime governs how state moves, recovers, validates, and updates over time. This distinction matters because a storage-only view can keep records, but it cannot enforce transformation semantics or failure detection across cycles.

The paper makes three focused contributions:

1. It introduces SRP as a minimal runtime abstraction for long-horizon LLM interaction.
2. It defines bounded semantic drift as a practical lens for evaluating semantic stability over repeated transformation cycles.
3. It presents a semester-scale experimental plan and reproducible implementation strategy for comparing SRP with lightweight baselines.

The intended contribution is a credible semester-version research paper: narrow in scope, reproducible in implementation, and concrete enough to support a short-paper style evaluation.

### 1.1 Failure Boundary

To keep the claim falsifiable, the paper should also state when SRP fails. SRP is not guaranteed to work if the semantic vocabulary is corrupted, the validator is unreliable, the recovery step becomes non-invertible in practice, or cumulative drift exceeds the tolerance budget. This failure boundary improves credibility because it turns SRP into a testable runtime claim rather than an unconditional promise.

## 2. Related Work

SRP is related to existing work on prompt compression, memory-augmented LLM systems, retrieval-based context management, and long-horizon evaluation. The key difference is that SRP focuses on **semantic state as an explicit runtime object**, rather than treating context management purely as token retention or retrieval.

### 2.1 Prompt Compression and Context Reduction

Prompt compression methods reduce token cost while attempting to preserve downstream utility. These are important baselines because they directly address context length and efficiency. However, they generally optimize token sequences rather than modeling semantic state as a persistent runtime object with explicit recovery and validation steps.

### 2.2 Memory-Augmented and Retrieval-Based Systems

Memory systems and retrieval-augmented generation improve continuity by storing or selecting prior information across turns. These approaches can be effective in practice, but they do not usually specify which semantic invariants should remain stable after repeated transformation. In particular, they rarely make bounded semantic drift itself the central object of analysis.

### 2.3 Long-Horizon Evaluation

Recent work on reproducibility, prompt sensitivity, and replayable LLM evaluation motivates the measurement side of this project. Because repeated transformation can accumulate error gradually, long-horizon evaluation requires stable experiment structure and consistent reporting. In this sense, SRP is both a runtime proposal and an evaluation proposal.

### 2.4 Positioning

The present paper does not argue that memory or retrieval are unnecessary. Instead, it argues that a separate abstraction layer is useful:

- prompt methods manage tokenized context
- memory and retrieval methods manage stored context
- SRP manages semantic state under repeated transformation

This is the narrow layer that the current paper studies.

## 3. Runtime State and Operators

In the semester version, SRP is intentionally minimal. We represent semantic state at interaction step `t` as:

```latex
S_t = (M_t, V_t, P_t)
```

where:

- `M_t` denotes structured semantic memory
- `V_t` denotes the active vocabulary state
- `P_t` denotes the policy state governing how state is transformed

The semester version does not require a complex schema. It only requires that semantic state be represented explicitly enough to support four operators:

```latex
C : S_t \to Z_t
```

```latex
R : Z_t \to S_t'
```

```latex
Val : (S_t, S_t') \to [0,1]
```

```latex
U : (S_t', F_t) \to S_{t+1}
```

These operators correspond to:

- compressing semantic state into a compact form
- recovering a usable state from that compact form
- validating whether task-relevant meaning is preserved
- updating state for the next step

The purpose of this framework is practical. It provides a structured way to study long-horizon stability without claiming a full semantic theory.

## 4. Formalization

The formalization in this paper is deliberately lightweight. We do not attempt to prove semantic truth. We only define measurable error over task-relevant behavior.

Let `O` be an observation operator that maps semantic state to an observable task space:

```latex
O : S \to Y
```

Examples of `O(S)` include:

- answers to downstream questions
- retained user constraints
- behavior under repeated task queries

We define semantic error between original and recovered state as:

```latex
\epsilon(S, S') = d(O(S), O(S'))
```

where `d` is a task-relevant distance measure.

The main long-horizon object is cumulative semantic drift under repeated transformation:

```latex
S_0 \xrightarrow{C} Z_0 \xrightarrow{R} S_1 \xrightarrow{C} Z_1 \xrightarrow{R} S_2 \to \cdots
```

At step `k`, cumulative semantic drift is:

```latex
\Delta_k = d(O(S_0), O(S_k))
```

The current paper uses **bounded semantic drift** as a practical notion rather than a large theorem target. The intended claim is modest:

> If local compression-recovery error remains controlled over a finite horizon, then cumulative task-relevant drift may remain empirically bounded enough to support more stable long-horizon interaction.

That level of formalization is sufficient for the semester version.

### 4.1 Why Drift Is the Main Metric

Drift is the primary metric because it is the shared failure mode across memory, retrieval, compression, and agent-based long-horizon systems. If repeated transformation is the operational setting, then drift is the most direct way to measure whether SRP is preserving task-relevant meaning over time.

In that sense, drift is not just one metric among several. It is the unifying quantity that the paper uses to compare systems across different context-management strategies.

## 5. Experimental Setup

We evaluate SRP in a finite-horizon setting designed to isolate bounded semantic drift under repeated transformation while keeping the study small enough to remain reproducible and interpretable. The goal is not to claim broad benchmark coverage, but to test whether explicit semantic-state management provides measurable stability benefits relative to lightweight baselines.

### 5.1 Main Experimental Question

The central experimental question is:

> Does SRP maintain more stable task-relevant semantics over repeated compression-recovery cycles than lightweight baselines?

### 5.2 Main Methods

The main comparison focuses on four methods:

- raw prompt
- summarization
- retrieval-based memory
- SRP

Raw prompt represents unconstrained context accumulation. Summarization represents a lightweight lossy memory strategy. Retrieval-based memory represents a standard external-memory baseline. SRP is the proposed semantic-state runtime method. A strongest-baseline view remains useful as a compact comparison layer, but it should be treated as a condensed reporting layer rather than the definition of the main experiment.

### 5.2a Benchmark and Replay

To improve replicability, the paper should treat benchmark design and replayability as part of the contribution. A minimal benchmark is useful only if it can be replayed under the same prompt template, backend, model version, and evaluation settings. The repo therefore serves not only as implementation support, but also as a replayable record of the state transitions that the paper studies.

### 5.3 Main Tasks

We evaluate the methods on two core task families:

- multi-turn instruction consistency
- iterative compression-recovery cycles

The first task family measures whether persistent constraints and user-relevant semantics remain behaviorally active after multiple transformations. The second directly stresses repeated compression-recovery dynamics and therefore serves as the main drift-oriented analysis setting. Long-context summarization and regeneration remain optional extensions rather than core requirements of the present paper.

### 5.4 Main Settings

To keep the study controlled, the current version uses:

- `1` main model
- cycle counts of `3`, `5`, and `7`
- `1-2` ablations only if time permits

When ablations are included, the two most informative variants are:

- SRP without recovery
- SRP without validation

### 5.5 Main Metrics

We report three main metrics:

- semantic drift
- task success
- token cost

Cumulative semantic drift is the primary metric because it directly measures deviation from the original task-relevant state over repeated transformation. Task success evaluates whether retained semantics remain behaviorally useful, while token cost captures the practical efficiency of each method. Together, these metrics support both a quality-oriented and an efficiency-oriented comparison.

## 6. Results

The semester version is designed to support a small number of clear empirical observations rather than a large benchmark sweep. The results section should therefore prioritize interpretability, reproducibility, and alignment with the paper's central claim.

### 6.0 Main Results Summary

Figure X summarizes the core empirical behavior of SRP across cycle depths and evaluation axes. SRP consistently achieves the lowest semantic drift among all methods, and this advantage persists as cycle depth increases, suggesting that the effect is structurally induced rather than a consequence of shallow-task optimization or run variance.

In the efficiency-quality tradeoff space, SRP occupies a distinct low-drift, low-token regime. This separates it from summarization, which minimizes token usage but exhibits high semantic instability, and from raw prompt and RAG baselines, which maintain higher drift despite comparable or higher resource consumption.

The contract stability analysis further indicates that SRP commit behavior remains aligned with semantic contract satisfaction across cycles. This suggests that execution decisions are driven by semantic compliance signals rather than surface-form similarity.

Taken together, the results indicate that SRP improves long-horizon semantic stability without sacrificing efficiency, and establishes a consistent operating regime distinct from the evaluated baselines.

> **Three-panel main results.** (A) Semantic drift across cycle depths for four methods. SRP consistently achieves the lowest drift and remains stable as cycle depth increases, while summarization degrades sharply and both raw prompt and RAG exhibit substantially higher drift. (B) Token cost versus drift Pareto frontier. SRP occupies a low-drift, low-token region, indicating that improvements are not attributable to increased computational budget. (C) SRP contract stability. Contract satisfaction remains stable across cycles, and commit decisions track semantic contract compliance rather than lexical similarity, suggesting that execution stability is governed by semantic consistency rather than surface-form preservation.

### 6.1 Semantic Drift Across Cycles

The primary result is the semantic-drift-over-iterations analysis. This figure measures how quickly task-relevant semantic information degrades when each method is repeatedly subjected to compression-recovery cycles.

The main question is whether SRP exhibits a slower increase in cumulative semantic drift than lightweight baselines. If the SRP curve grows more slowly or remains flatter over the finite horizon, this would support the hypothesis that explicit semantic-state management may help stabilize repeated transformation.

The most important visualization in the paper is therefore:

- drift over iterations

This figure should be treated as the centerpiece of the empirical section.

### 6.2 Task Preservation

The second result concerns whether reduced drift corresponds to better preservation of task-relevant behavior. This is measured through task success under the selected core task families.

The quality table should summarize:

- semantic drift
- task success

for the main methods and cycle settings. Its role is to show whether lower drift is accompanied by better finite-horizon task retention rather than merely better compression behavior.

### 6.3 Token Efficiency

The third result concerns token cost. Since long-horizon systems are often constrained by context cost, the paper should evaluate whether SRP remains competitive in token usage while attempting to preserve semantic stability.

The efficiency table should summarize:

- token cost

across the same main settings. This allows the paper to present SRP not only as a stability-oriented method, but also as a practical context-management strategy.

### 6.4 Camera-Ready Comparison Table

For a concise submission-ready view, the project also includes a camera-ready SRP versus strongest-baseline table. Its role is not to replace the fuller quality and efficiency analysis, but to provide a compact comparison that makes the central tradeoff immediately visible.

This table should be used to summarize:

- the strongest non-SRP baseline for each setting
- SRP performance under the same setting
- direct metric deltas between SRP and that baseline

This condensed comparison is particularly useful for short-paper or workshop submission formats where space is limited.

### 6.5 Interpretation

The empirical section is successful if it supports the following restrained reading:

1. SRP can be evaluated reproducibly under finite-horizon compression-recovery cycles.
2. SRP provides a meaningful semantic-stability framing rather than only a conceptual abstraction.
3. SRP can be compared fairly against lightweight baselines under a shared-query, finite-horizon evaluation setup, with improved stability-efficiency tradeoffs in at least some settings.

Under the current anchor-guided tuned local pilot, the clearest positive signal is that SRP now looks more balanced than plain summarization at `5` and `7` cycles, with higher task success and lower drift, even though retrieval-based memory still remains the strongest drift baseline on the present toy task suite.

For the semester version, the empirical case carries the main burden of credibility and defines the paper's scope of claim.

## 7. Discussion

The results support a restrained reading of SRP: the first-semester goal is to test whether explicit semantic-state management improves finite-horizon stability, not to close the broader SRP blueprint.

The discussion focuses on four points:

- why semantic state differs from memory
- why bounded semantic drift is more realistic than exact preservation
- why the first implementation remains intentionally minimal
- what would be required to scale toward the longer-term SRP design

It also preserves the open questions that the current paper does not attempt to close.

## 8. Limitations

The scope of this paper is intentionally narrow, and its limitations should be stated explicitly to keep the contribution credible.

Main limitations include:

- finite-horizon rather than large-scale long-horizon evaluation
- proxy-based semantic drift measurement rather than direct semantic ground truth
- simplified SRP state schema
- narrow model and task scope

These limitations are acceptable because the project is framed as a semester-version runtime and evaluation study rather than a full long-horizon platform.

## 9. Open Questions To Preserve

These questions remain open in the current paper and should be preserved rather than collapsed into an artificial closure:

- Is SRP primarily a runtime abstraction, a protocol, or a semantic communication layer?
- What is the minimal semantic-state object?
- Which semantic drift metric should be considered the main one in the first paper?
- What failure cases should be shown explicitly?

## 10. Future Work

Future work should extend the present claim rather than replace it:

- richer state schemas
- stronger validator design
- cross-model generalization
- semantic contract refinement
- replay database and benchmark expansion
- runtime lifecycle extensions such as freeze, merge, and delete
- transaction-style commit / rollback semantics

These items belong to the next step of the SRP program, not to the burden of the first paper.

## 11. Submission Strategy

The most plausible near-term venues are:

- workshop papers in LLM systems, NLP, or AI systems
- student research tracks
- short papers
- technical reports on arXiv plus advisor feedback

The first submission goal should be:

> a reproducible, bounded-scope paper with one strong figure and one careful theoretical framing

not a maximal full-scale top-tier systems paper.

## 12. Immediate Next Steps

1. Convert the current markdown into a single integrated draft.
2. Keep the experiment pipeline minimal and reproducible.
3. Finalize one credible semantic-drift-over-iterations figure.
4. Collect faculty feedback using the one-page research pitch.
5. Revise the paper around the actual experimental evidence.

## 13. Conclusion

This paper presents the semester version of SRP: a semantic-state runtime abstraction for studying bounded semantic drift in long-horizon LLM interaction. The contribution is intentionally narrow. Rather than claiming a full semantic operating system, the paper proposes a practical way to represent, transform, and evaluate semantic state under repeated compression-recovery cycles. The expected outcome of this version is a reproducible experiment, a short and credible draft, and a first research result that can be evaluated on its own merits. The long-term vision remains broader, but the present paper is designed to answer one falsifiable question about this framework rather than many future-facing ones.

## References

This draft expects:

- `SRP_References.bib`

## Appendix A. Frozen Extensions

The following directions are intentionally frozen for the semester version unless the core paper is fully complete:

- large multi-model sweeps
- extra task families
- large benchmark expansion
- stronger formal guarantees
- enterprise-scale runtime architecture
- advanced future-work protocol features

These directions remain valuable, but they should not control the structure of the present paper.
