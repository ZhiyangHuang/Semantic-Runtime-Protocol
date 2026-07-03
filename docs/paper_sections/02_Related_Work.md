# Related Work Draft

## 1. Overview

Research on long-horizon LLM systems has grown rapidly, but most existing approaches manage context indirectly through prompts, summaries, retrieval, or agent trajectories. SRP is related to these directions, but differs in its central claim: semantic state itself should be modeled as an explicit runtime object with governed transformation operators.

The reviewer-facing position we want is simple:

> Existing methods manage information. SRP manages semantic state transition.

That statement is intentionally narrower than claiming a universal semantic operating system. It helps keep the paper readable and gives us a concrete gap to defend.

## 2. Prompt Compression and Context Reduction

One major line of work focuses on reducing prompt length while preserving task performance. Representative examples include prompt compression methods such as LLMLingua, context-aware compression, and other token-budget optimization approaches. These methods are important because they show that raw prompt text often contains redundancy and can be shortened substantially without immediately harming downstream output.

However, prompt compression methods generally optimize the prompt as a token sequence rather than formalizing semantic state as a persistent computational object. In most such systems, compression is a preprocessing step applied to context, not a runtime protocol with explicit recovery, validation, and governed update. As a result, these methods are strong baselines for efficiency, but they do not directly address iterative semantic stability under repeated transformation.

SRP builds on the motivation behind prompt compression while shifting the unit of analysis from token reduction to semantic-state preservation. For the current paper, prompt compression is a baseline and a source of intuition, not the end goal.

## 3. Memory-Augmented LLM Systems

Another major direction augments LLMs with external memory. Common approaches include summary memory, episodic memory buffers, vector databases, retrieval-augmented generation, and long-context assistants that selectively replay prior interactions. These systems help overcome context-window limitations and often improve personalization, continuity, and tool use over longer sessions.

Their limitation, for our purposes, is not that they lack memory, but that memory is typically treated as stored text or retrieved records rather than as a formally transformed state. Summarization memory often replaces earlier context with a lossy natural-language abstraction. Retrieval-based memory improves access to relevant prior content, but usually does not specify what semantic invariants should hold after retrieval and reuse. In both cases, transformation semantics remain implicit.

SRP differs by making compression, recovery, validation, and update explicit operators over semantic state. In this sense, SRP is not simply another memory architecture, but an attempt to define the runtime semantics governing how long-horizon information should evolve.

For the first paper, we should keep the boundary clear:

- memory stores records or compressed packages
- runtime governs transitions, validation, recovery, and update

That distinction is one of the most useful reviewer-facing moves in the current draft.

## 4. Agent Frameworks and Trajectory-Based Systems

Agent systems provide another influential paradigm for long-horizon interaction. In these frameworks, the model produces chains of reasoning, plans, tool calls, and execution traces across multiple steps. Such systems often improve task completion by externalizing process history and enabling structured interaction with tools and environments.

Despite their strengths, agent frameworks generally treat history as trajectory rather than as a dedicated semantic state abstraction. A trajectory records what the system did, but not necessarily what stable semantic object should be preserved across repeated transformations. Tool-use traces, intermediate thoughts, and action logs may be useful operationally, yet they do not by themselves define a closed-loop semantic-state runtime with measurable drift.

SRP is therefore complementary to agent systems. It does not deny the value of trajectories, planning, or tool use, but argues that long-horizon stability requires an explicit model of state beyond execution history alone.

This is also where the first paper should remain modest: we do not need to replace agent frameworks, only to explain why they are not enough as a semantic-runtime layer.

## 5. Semantic Communication and Semantic Calibration

SRP is also related to work on semantic communication, concept-level representation, and semantic calibration. These literatures contribute an important shift in perspective: what matters is often preservation of meaning or task-relevant semantics rather than exact transmission of surface form. This idea is highly aligned with the motivation behind SRP.

At the same time, most prior work in semantic communication targets communication efficiency, encoding theory, or semantic similarity objectives rather than the runtime management of semantic state across interactive LLM sessions. Likewise, semantic calibration work helps define concept-preserving evaluation, but does not by itself provide a protocol for repeated compression, recovery, and update over long horizons.

SRP borrows from these literatures at the level of principle, especially the move from token fidelity to semantic fidelity, while targeting a different systems problem: semantic stability under iterative interaction.

This is also a good place to preserve an unresolved question from `new_1.md`: whether the runtime object should be understood primarily as concept, behavior, knowledge, or vocabulary alignment. For the first paper, we do not have to fully settle that; we only need to state that SRP operates over semantic state rather than raw tokens.

## 6. Reproducibility, Replay, and LLM Evaluation

A further relevant body of work studies reproducibility in machine learning and LLM systems, including prompt sensitivity, evaluation instability, experiment tracking, and replay-based analysis. These studies are important because they show that long-horizon systems can behave inconsistently even when their components appear reasonable in isolation.

SRP is compatible with this line of work in two ways. First, the notion of bounded semantic drift depends on repeatable measurement and evaluation over multiple cycles. Second, replay and experiment logging are natural infrastructure for analyzing state transformations. However, reproducibility frameworks typically provide measurement infrastructure rather than a semantic runtime abstraction.

Accordingly, replay, benchmark, and experiment database components should be viewed as supporting infrastructure for SRP rather than the core conceptual contribution.

This is one of the places where `new_1.md` adds a valuable reviewer-risk note: reproducibility is not just a nice appendix item. If the same configuration cannot replay the drift curves, the paper loses a lot of force.

## 7. Predictive State and Dynamical Systems

Another useful theoretical neighbor is work on predictive state representation and observable dynamical systems. The core idea in that literature is that a state is meaningful when it is sufficient for predicting future behavior, rather than merely acting as a compression of past history.

This connection is attractive for SRP because it gives a cleaner way to talk about semantic state without forcing a hard symbolic proof that semantic meaning is perfectly preserved. A semantic state can instead be evaluated through predictive sufficiency and downstream behavioral stability.

For the first paper, this literature should be used as conceptual support rather than as a claim of full theoretical equivalence. The paper can borrow the language of sufficient state, predictive error, and stability without pretending that SRP already has a complete control-theoretic account.

## 8. Positioning Statement

The cleanest way to position SRP is as follows:

> Prompt compression reduces context length, memory systems store or retrieve prior information, and agent frameworks organize long-horizon behavior. SRP addresses a different layer: it formalizes semantic state itself as a runtime object governed by compression, recovery, validation, and update.

This positioning is important because it prevents the paper from being reviewed as merely:

- another summarization method
- another retrieval wrapper
- another agent architecture

Instead, the paper should be read as a first attempt at a semantic-state runtime abstraction for long-horizon LLM systems.

## 9. Conservative Gap Claim

To keep the claim credible, the first paper should use a narrow gap statement:

> Existing long-horizon LLM methods manage context through prompts, summaries, retrieval, or trajectories, but they do not explicitly define a closed-loop runtime model in which semantic state is compressed, recovered, validated, and updated under measurable drift.

## 10. Open Review Risks

The following questions are still unresolved on purpose and should remain visible as review risks instead of being forced into the first draft:

- Is SRP primarily a runtime abstraction, a protocol, or a semantic communication layer?
- What is the minimal semantic-state object: memory, concept, vocabulary, or policy?
- Which metric best captures semantic drift: behavioral agreement, embedding distance, or judge-based equivalence?
- Where exactly is the novelty boundary relative to retrieval memory and prompt compression?
- Should the theory borrow more explicitly from predictive state representation or remain at the level of a practical runtime abstraction?

Keeping these questions explicit will help the paper stay honest and help us refine the positioning without pretending that the first draft has settled every design choice.

This claim is strong enough to motivate the paper, but modest enough to survive scrutiny.
