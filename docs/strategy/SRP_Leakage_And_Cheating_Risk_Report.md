# SRP Leakage And Cheating Risk Report

## Purpose

This note evaluates whether the current SRP validation and correction design creates a real risk of experimental cheating, evaluation leakage, or unfair task-specific advantage.

It is written as a methodology-risk report rather than a tuning note.

Its job is to answer four questions:

1. what kinds of "cheating" are actually possible in an SRP-style memory protocol
2. whether the current use of saved memory for correction or validation creates those risks
3. which current code paths are safer and which are still vulnerable
4. what formal constraints should be added before paper-facing claims become stronger

## Bottom Line

There **is** a real leakage risk category here, and it should be taken seriously.

However, the current SRP project has a narrower scope than a general memory-learning system.

The present SRP scope is:

- inference-time semantic-state handling
- runtime compression / recovery / translation
- possible future extension to semantic translation across model or system layers

The present SRP scope is **not**:

- training-time representation learning
- benchmark memorization through parameter updates
- model pretraining contamination analysis

So the correct framing is:

- some leakage and cheating risks are directly in scope for SRP
- some broader risks still exist, but belong to the same "acknowledged but not primary scope" category that many RAG papers adopt

The critical distinction for current SRP remains:

- storing and restoring **semantic state**

versus

- storing **future answers, reasoning traces, labels, or task-specific solutions**

This report now adopts the following protocol principle as its organizing rule:

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

That principle means:

- raw text is only an input to semantic parsing
- typed semantic state is the verification target
- lexical surface form is not the primary object of commitment

As a result, the protocol boundary is no longer "can the model see text," but "what semantic representation is allowed to enter runtime verification and commit logic."

The current main SRP line does **not automatically count as cheating** just because it uses:

- `anchor_memory`
- `committed_memory`
- validation-guided rollback

But it **does** become methodologically risky if the stored package, anchor, or intermediate semantic representation starts encoding:

- query-answer pairs
- future task solutions
- reasoning traces
- benchmark labels

That is the real boundary for the current paper scope.

## Scope Definition

This report should be read under the following scope rule.

### In Scope

- inference-time leakage through the runtime package
- answer caching through semantic compression
- reasoning-trace preservation inside runtime state
- benchmark-shaped recovery behavior
- evaluation-shaped validation pressure
- semantic translation leakage if SRP later becomes a cross-model intermediate layer

### Out Of Primary Scope But Still Acknowledged

- pretraining-data contamination
- training-time label leakage
- fine-tuning-time shortcut learning
- optimizer-level memorization

These are still real methodological risks in the broader ecosystem.

They are simply not the main object of control for the current SRP work, in the same way that many RAG papers acknowledge training-data leakage risk without making it the central contribution boundary.

## Reframed Risk Sources

For the current SRP scope, the cleanest way to define risk is not only by abstract "cheating type," but by **where the risky information enters the system**.

That gives a reviewer a clearer map of what SRP does and does not control.

## Source 1: Runtime Package Leakage

Definition:

- leakage introduced directly through the compressed semantic package or its recovered form

This is the most central SRP risk source.

Examples:

- a package stores a future answer
- a package stores a benchmark-shaped reformulation
- a package stores a reasoning trace that later functions as an answer cache

This source is fully in scope for SRP.

## Source 2: Anchor Or Correction-State Leakage

Definition:

- leakage introduced through saved anchor memory, correction memory, or rollback memory

This is the second major SRP-specific risk source.

Examples:

- anchor memory contains answer-shaped content
- correction state preserves derived conclusions rather than only state facts
- rollback keeps a benchmark-shaped state that should never have existed

This source is also fully in scope for SRP.

## Source 3: Validation-Side Shaping Leakage

Definition:

- leakage introduced when validation or commit logic indirectly pressures the runtime state toward benchmark-visible targets

Examples:

- validation targets overfit to evaluation keywords
- commit logic rewards answer-shaped retention rather than state fidelity

This source is in scope for SRP because it is part of inference-time runtime control.

## Source 4: Task / Evaluation Interface Leakage

Definition:

- leakage introduced because runtime state construction imports evaluation-facing artifacts

Examples:

- `expected_keywords` influence runtime semantic state
- query-level answer targets leak into the package design

This source is in scope for SRP because it sits at the boundary between runtime construction and evaluation design.

## Source 5: Training-Time Or Model-Internal Leakage

Definition:

- leakage caused by pretraining, fine-tuning, or internal model memorization

Examples:

- model already memorized benchmark content
- fine-tuned weights encode task shortcuts

This source remains real, but is **not the primary control scope** of the current SRP work.

It should be acknowledged explicitly, not ignored, and treated similarly to how RAG papers acknowledge broader model contamination risks without making them the central protocol contribution.

## Legacy Typology

The temporary note also separates several classic cheating-like behaviors.

These remain useful, but should now be read as behavioral categories that arise from the risk sources above.

### 1. Evaluation Leakage

This is the most serious risk.

Definition:

- the memory package contains information that directly answers or strongly pre-solves the later evaluation query

Example:

- instead of storing user facts, the package stores a future query answer template

Why this is dangerous:

- the system is no longer being tested on memory retention
- it is being tested on hidden answer caching

This is the reviewer risk most likely to damage trust.

### 2. Reasoning Shortcut

Definition:

- the system stores the end result of a reasoning chain rather than the underlying state needed for later reasoning

Example:

- instead of storing facts `A -> B -> C`, the system stores the final result `C`

Why this matters:

- memory is replacing reasoning rather than supporting reasoning
- the runtime looks stronger partly because task complexity was prepaid

This is not always as severe as direct evaluation leakage, but it still weakens the claim that SRP preserves reusable semantic state.

### 3. Ground-Truth Leakage

Definition:

- the package contains benchmark labels or gold facts in a way that would not exist in a real deployment

Example:

- the stored state mirrors evaluation-side expectations rather than user-side memory content

Why this matters:

- the system stops being evaluated on general memory management
- it starts benefiting from benchmark-aware state shaping

### 4. Hidden Chain-of-Thought Leakage

Definition:

- the system stores reasoning traces or solution trajectories as part of the retained memory

Why this matters:

- it turns memory into hidden reasoning storage
- it creates fairness and interpretability concerns
- it is especially risky if a later answer can be reconstructed from the saved reasoning path alone

## Why These Risks Still Need To Be Mentioned

Even when some of them are outside the main SRP scope, they should still remain in the report.

Reason:

- reviewers expect to see them acknowledged
- omission looks less trustworthy than scoped disclosure
- RAG-style systems are usually not expected to solve every training-time leakage issue either, but they still name those risks

So the right approach is:

- keep the full risk inventory
- explicitly mark which risks SRP controls directly
- explicitly mark which risks are acknowledged but out of primary scope

## Where The Current SRP Design Is Safer

Some current mechanisms look suspicious at first glance, but are not necessarily cheating by themselves.

### `committed_memory`

Current use:

- after validation, the system may keep the pre-cycle memory rather than the failed recovered memory

This is methodologically acceptable because:

- it is a runtime consistency mechanism
- it does not by itself insert future answers
- it only decides which memory state is retained

This is closer to:

- transaction rollback

than to:

- answer leakage

### `validation_drift` And Keyword Thresholds

Current use:

- validation checks compare recovered memory against prior memory and task-side retention proxies

This is not automatically cheating because:

- it is a stability filter
- it does not directly reveal the next query answer

However, there is a caveat:

- if the validation target becomes too benchmark-shaped, then the system can drift toward preserving evaluation-visible keywords rather than genuine semantic state

So this mechanism is acceptable, but should remain carefully bounded.

### `anchor_memory`

Current use:

- recovery is biased toward a stable anchor rather than uncontrolled paraphrase

This is not automatically cheating because:

- a stable anchor can legitimately act as a memory reference
- anchoring can reduce semantic drift without encoding future answers

The key condition is:

- the anchor must itself be a legitimate memory state, not an answer cache

## Where The Current Design Still Has Real Risk

The main risk is not "using saved memory."

The main risk is **what exactly gets saved inside the package or anchor**.

### Risk 1: Task-Side Vocabulary Can Quietly Become Benchmark-Aware

Relevant code signals:

- [rag_srp.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp.py:38) seeds `concept_state` from `expected_keywords`
- [rag_srp_anchor.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_anchor.py:66) also seeds `concept_state` from `expected_keywords`
- [rag_srp_v2.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_v2.py:54) does the same

Why this matters:

- `expected_keywords` belong to the evaluation side
- if those enter the retained runtime state too directly, the system can become benchmark-shaped

This is not yet proof of cheating, but it is a real fairness risk.

### Risk 2: Anchor Construction Can Drift Toward Query-Solving State

Relevant code:

- [rag_srp_anchor.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_anchor.py:34)
- [rag_srp_v2.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_v2.py:44)
- [prompting.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py:65)

If the anchor is built from:

- user facts
- preferences
- constraints

that is defensible.

If it starts to include:

- canonical solutions
- answer-shaped task summaries
- evaluation-side interpretations

then it becomes leakage-prone.

### Risk 3: Recovery Can Become Answer Reconstruction Instead Of Memory Reconstruction

Relevant code:

- [prompting.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py:65)
- [recover.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/recover.py:1)

If recovery is instructed to:

- reconstruct the most faithful memory state

that is good.

If it is effectively instructed to:

- reconstruct what the benchmark is likely to want

that becomes a shortcut.

### Risk 4: Validation Can Become A Benchmark-Shaping Mechanism

Relevant code:

- [collect_batch_summary.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/collect_batch_summary.py:60)
- [validate.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/validate.py:1)

Rollback itself is fine.

But if the pass/fail conditions are strongly keyed to task-specific expected tokens rather than general semantic preservation, then validation starts acting like:

- hidden benchmark alignment pressure

rather than:

- generic memory hygiene

## Current Assessment Of Your Specific Concern

Your concern was:

> I previously let SRP save memory for correction and validation. Does that create a cheating risk?

The answer is:

### Short Answer

- **Yes, a cheating risk exists in principle**
- **No, saving memory for correction is not automatically cheating**

### More Precise Answer

It depends on whether the saved memory contains:

- legitimate semantic state

or

- future-answer-bearing state

If saved memory is only used to:

- keep facts stable
- preserve preferences
- retain constraints
- avoid drift

that is defensible.

If saved memory is used to:

- cache benchmark answers
- preserve reasoning traces
- encode query-specific solutions
- import evaluation labels into the runtime package

then yes, that crosses into serious leakage territory.

## New Risk Evidence: `risk_test_srp_vs_hybrids_5_7`

The temporary risk-test comparison supports the same boundary.

Observed results:

- `srp`
  - `5 cycles`: `mean_drift = 0.054`, `mean_task_success = 0.9167`, `mean_query_success = 0.8444`
  - `7 cycles`: `mean_drift = 0.054`, `mean_task_success = 0.9167`, `mean_query_success = 0.8254`
- `rag_srp_anchor`
  - `5 cycles`: `mean_drift = 0.4049`, `mean_task_success = 0.92`, `mean_query_success = 0.8222`
  - `7 cycles`: `mean_drift = 0.4257`, `mean_task_success = 0.8667`, `mean_query_success = 0.8254`
- `rag_srp_v2`
  - `5 cycles`: `mean_drift = 0.0511`, `mean_task_success = 0.9167`, `mean_query_success = 1.0`
  - `7 cycles`: `mean_drift = 0.0492`, `mean_task_success = 0.9167`, `mean_query_success = 0.9524`

Interpretation:

- `rag_srp_anchor` remains clearly legacy-risk-bearing and should stay in the legacy archive.
- `rag_srp_v2` is the closest legacy-adjacent line to main SRP behavior, but it still remains risk-bearing because runtime-state shaping still depends on evaluation-side inputs.
- main `srp` remains the current formal evidence line, but it still requires a refactor rerun before the strongest final claim.

This new test does not change the scope framing.
It reinforces it:

- saving memory for correction is not automatically cheating
- but the current runtime-state shaping still has a real leakage boundary that must be refactored before the final paper claim

## Recommended Formal Constraint

Before stronger paper claims, SRP should adopt an explicit package constraint.

### Package Admissibility Rule

The semantic package may contain:

- facts
- preferences
- constraints
- intents
- entity relations
- stable semantic state

The semantic package may **not** contain:

- future query answers
- reasoning traces
- task labels
- gold outputs
- benchmark-side supervision artifacts

This should be written as a formal protocol rule, not only as an implementation habit.

## Recommended New Principle

The temporary note suggests a very good paper-facing principle.

It is worth preserving explicitly.

### Reasoning Preservation Principle (RPP)

Proposed wording:

> SRP may preserve semantic state, but it must not preserve task-specific solutions or reasoning traces for future evaluation queries. The protocol may reduce context burden, but it must not reduce the reasoning complexity of a future task by caching its solution in advance.

Why this is useful:

- it distinguishes memory from answer caching
- it answers a likely reviewer objection in advance
- it gives SRP a stronger methodological identity

## Recommended New Test

To make this paper-defensible, add one explicit anti-cheating test later.

### `Reasoning Independence Test`

Goal:

- verify that SRP preserves memory, not pre-solved reasoning

Basic idea:

1. store a memory state
2. later ask a reasoning question that depends on the memory
3. ensure the system must still perform new reasoning at answer time

What this test should check:

- stored state helps provide relevant facts
- stored state does not already contain the final answer
- later success still depends on model reasoning, not only retrieval

This would be a very strong methodological addition.

## Concrete Safe / Unsafe Boundary

### Safe

- `User lives in NY`
- `User prefers Python`
- `Constraint: vegetarian`
- `Tom's father is Jack`

### Unsafe

- `Question: where does Tom's son work?`
- `Answer: Microsoft`
- `Reasoning trace: Tom -> father Jack -> Jack works at Microsoft -> answer`
- `Gold label preserved for later recovery`

That safe/unsafe distinction should become explicit in both documentation and prompts.

## Recommended Documentation Upgrades

This risk is important enough that it should eventually be recorded in:

- a methodology note
- the pilot tuning log
- the formal runbook if SRP remains the main paper method

Most useful future additions:

1. a package admissibility rule
2. the `Reasoning Preservation Principle`
3. a short "what SRP is not allowed to store" section

## Final Assessment

The current biggest methodological risk is **not** that SRP stores memory.

For the present SRP scope, the biggest risk is that the inference-time runtime package could slowly become:

- answer-shaped
- benchmark-shaped
- reasoning-trace-shaped

That is the risk SRP should actively control.

At the same time, broader risks like training-time contamination still exist.

They should remain explicitly acknowledged, but they are not the primary intervention surface of the current SRP protocol work, just as many RAG papers acknowledge them without claiming to solve them.

If the runtime-package boundary is controlled explicitly, then:

- anchor-guided correction
- committed-memory rollback
- semantic translation between layers

remain defensible runtime mechanisms rather than cheating.

So the correct next move is not to stop using correction memory.

It is to formalize a rule:

> SRP may preserve semantic state, but it may not preserve future task solutions.
