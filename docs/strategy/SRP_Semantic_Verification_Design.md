# SRP Semantic Verification Design

## Purpose

This note designs a verification layer for SRP that is more permissive than keyword matching, but still strict enough to block answer leakage, reversal, and benchmark-shaped rewrites.

The goal is to support long-task lexical transformation while preserving the original semantic state.

In particular, the verification layer should allow:

- paraphrase
- lexical substitution
- constraint-preserving rewording
- semantic compaction

It should reject:

- direct answer caching
- reversed meaning
- task-completion language
- rewritten solutions that are semantically too close to a final answer

## Why A New Verification Layer Is Needed

The old keyword-style gate is too brittle for long tasks.

It punishes legitimate semantic reformulation and rewards surface overlap.

That is a bad fit for SRP because SRP is supposed to preserve semantic state, not verbatim wording.

At the same time, a fully free semantic judge is too weak.

It can silently accept:

- answer-shaped reconstruction
- over-specific rewrites
- hallucinated detail
- semantic reversal hidden under fluent paraphrase

So the verification problem is not "exact match" versus "free generation".
It is a controlled middle ground.

## Design Principle

The most useful SRP verifier should answer three questions separately:

1. Did the recovered state preserve the important facts and constraints?
2. Did the wording stay semantically aligned instead of flipping direction?
3. Did the output stay away from answer leakage?

Only if all three are satisfied should the cycle be allowed to commit.

## Proposed Verification Stack

### Layer 1: State Preservation Check

This layer checks whether the recovered state still contains the admissible core of the original state.

It should evaluate:

- factual retention
- constraint retention
- relation retention
- anchor retention
- time-order retention when relevant

This layer is not meant to punish lexical change.

It is meant to detect whether the semantic payload survived.

### Layer 2: Semantic Direction Check

This layer checks whether the wording is still pointing in the same semantic direction as the source state.

It should allow:

- paraphrase
- abstraction
- compression
- synonym replacement

It should reject:

- contradiction
- negation flip
- polarity reversal
- over-strong inference
- premature conclusion

This is the layer that lets SRP support lexical transformation without letting meaning drift into the opposite direction.

### Layer 3: Answer Leakage Guard

This layer is a hard safety gate.

It should reject outputs that look like:

- final answers
- completion statements
- result declarations
- solution summaries
- explicit task-solving language
- benchmark-shaped restatements

This layer does not care whether the wording is elegant.
It only cares whether the recovered state has started behaving like an answer cache.

## Suggested Decision Rule

The cycle should commit only if all of the following hold:

- preservation score is above threshold
- semantic direction check passes
- leakage guard passes

A cycle should rollback if any one of these fails.

This makes the verifier conservative by design.

## Recommended Signal Types

### 1. Structural Signals

These are cheap, rule-based checks.

Examples:

- presence of required constraints
- absence of explicit answer phrases
- absence of contradiction markers
- length bounds
- section-shape consistency

These are useful because they are fast and easy to debug.

### 2. Semantic Signals

These are more flexible and should sit on top of the structural signals.

Examples:

- entailment between source state and recovered state
- contradiction detection
- paraphrase consistency
- semantic similarity on a constrained basis

These are useful for long tasks where exact wording is too strict.

### 3. Leakage Signals

These are special detectors for dangerous outputs.

Examples:

- answer-like templates
- "the answer is" style phrasing
- explicit task completion declarations
- overfit keyword bundles that mirror benchmark phrasing

These should act as hard filters.

## Practical Scoring Shape

A practical SRP verifier can use a composite score:

- `preservation_score`
- `direction_score`
- `leakage_penalty`

Possible commit rule:

- commit if `preservation_score >= p` and `direction_score >= d` and `leakage_penalty == 0`

Possible rollback rule:

- rollback if leakage is detected
- rollback if direction flips
- rollback if the state loses critical constraints

This is intentionally more conservative than free-form semantic judgment.

## What Counts As Success

Successful recovery should look like:

- the same semantic state, but not the same wording
- a compressed re-expression of the source state
- a paraphrase that still preserves core constraints
- a transformed representation that remains non-answer-shaped

## What Counts As Failure

Failure should include:

- a fluent answer that is too specific
- a paraphrase that quietly changes meaning
- a recovery that flips the polarity of a constraint
- a recovery that introduces unsupported conclusions
- a recovery that uses benchmark-shaped phrasing to appear correct

## Why This Is Safer Than Keyword Matching

Keyword matching is easy to game and too narrow for long tasks.

This design is safer because it separates:

- meaning preservation
- wording flexibility
- leakage prevention

That separation is important for SRP because the project needs to support semantic translation without becoming an answer cache.

## Why This Is Safer Than A Fully Free LLM Judge

A fully free judge can be too forgiving.

It may reward:

- fluent paraphrase
- confident completion language
- answer-shaped reconstruction

The proposed verifier keeps the judge constrained by explicit safety rules.

## Calibration Plan

Before using this verifier as a final gate, we should calibrate it with three small sets:

1. Valid paraphrases with different wording but same meaning
2. Invalid reversals that flip the meaning or answer too much
3. Borderline cases that preserve facts but rewrite aggressively

The verifier should:

- accept set 1
- reject set 2
- be conservative on set 3

## Relation To The Leakage Problem

This design is meant to reduce leakage risk, not hide it.

It should make the boundary clearer between:

- semantic recovery
- benchmark-shaping rewrite
- answer caching

That is especially important if SRP later becomes a semantic translation layer across models.

## Suggested Next Implementation Step

If we implement this design, the next clean order is:

1. keep runtime-state shaping free of `expected_keywords`
2. replace hard keyword commit logic with this three-layer verifier
3. rerun the same 5/7-cycle risk comparison
4. inspect whether `srp` and `rag_srp_v2` can recover commit ability without reopening leakage

## References Used For This Design

This proposal is informed by the general separation between semantic similarity and textual entailment in NLI work, and by RAG faithfulness evaluation work that distinguishes similarity-style signals from entailment-style signals and LLM-based judgment.

- [Formal Semantics for Recognizing Textual Entailment and Semantic Similarity](https://aclanthology.org/S14-2114.pdf)
- [Similarity and Entailment Metrics for Student Response Analysis](https://aclanthology.org/S13-2048.pdf)
- [Towards Fine-Grained Citation Evaluation in Generated Text](https://aclanthology.org/2024.inlg-main.35.pdf)
- [Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards](https://aclanthology.org/2025.emnlp-industry.54.pdf)
- [CiteEval: Principle-Driven Citation Evaluation for Source Attribution](https://aclanthology.org/2025.acl-long.1574.pdf)

