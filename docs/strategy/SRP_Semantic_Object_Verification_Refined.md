# SRP Runtime Semantic Object Verification Protocol

## Purpose

This note refines the earlier semantic verification idea into a more faithful SRP design.

The main correction is:

- do not verify raw text directly
- verify parsed semantic objects

That change matters because SRP is supposed to preserve and transform semantic state, not copy surface text.

## Core Correction

The previous version was still too text-centric.

Even when it used terms like "preservation" and "direction", the logic still looked like:

```text
source text -> score recovered text
```

That is not the right unit for SRP.

The better unit is:

```text
source text -> semantic parser -> semantic objects
recovered text -> semantic parser -> semantic objects
semantic objects -> verifier
```

So the verifier should compare:

- facts
- constraints
- relations
- anchors
- executable semantic capabilities

not just token overlap or free-form similarity.

## Protocol Rule 1

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

This is the foundational rule for the refined protocol.

It means:

- raw text is only input to semantic parsing
- typed semantic state is the verification target
- lexical surface form is not the primary object of commitment

If a design step forces the verifier back to raw-text comparison, then that step is no longer protocol-native.

## Why This Change Is Needed

Three recent lines of work point in the same direction:

- NLI/entailment work separates semantic relation from surface form
- faithfulness work increasingly moves toward claim-level or support-level checks
- provenance / memory work separates semantic evidence from verbatim trace storage

That suggests SRP should not try to judge whole recovered strings as strings.

It should judge canonical semantic objects extracted from those strings.

## Proposed Semantic Object Model

At minimum, the parser should extract:

- `facts`
- `constraints`
- `relations`
- `anchors`
- `claims`
- `execution_intents`

Where relevant, it may also extract:

- `temporal markers`
- `negation markers`
- `sensitive identifiers`
- `provenance pointers`

The exact object inventory can be smaller at first, but the verifier should think in objects, not in raw text.

## Verification Pipeline

```text
Source Text
   -> Semantic Parser
   -> Canonical Semantic Objects

Recovered Text
   -> Semantic Parser
   -> Canonical Semantic Objects

Canonical Semantic Objects
   -> Coverage Check
   -> Bidirectional Entailment Check
   -> Executability / Leakage Check
   -> Risk Aggregation
   -> Commit / Retry / Rollback
```

## Layer 1: Semantic Coverage

This replaces the earlier "retention" framing.

The question is not:

- did we preserve the exact same words?

The question is:

- did we preserve the required semantic objects?

Coverage should be measured over objects such as:

- facts
- constraints
- relations
- anchors

### Coverage rule

If the source state contains six required semantic objects and five are recovered in admissible form, coverage is `5/6`.

### Why coverage is better than retention

Retention sounds like verbatim survival.

Coverage sounds like semantic reconstruction.

That matches SRP much better.

## Layer 2: Bidirectional Entailment

This layer checks whether the recovered state and source state are semantically aligned in both directions.

The idea is:

- `source -> recovered`
- `recovered -> source`

Both should hold at the semantic-object level.

This is important because unidirectional similarity is too weak.

If only one direction holds, then the recovery may be:

- too lossy
- too specific
- answer-shaped
- or semantically drifting

### Interpretation

- if both directions hold, the state is probably semantically stable
- if only one direction holds, rollback is safer
- if neither holds, the cycle has failed

## Layer 3: Executability Check

This is the correction to the earlier leakage idea.

The issue is not just whether a string contains suspicious phrases.

The issue is whether the recovered semantic state has become executable as a direct answer, decision, or plan.

The verifier should reject a recovered state if it already contains:

- final answer statements
- explicit solution language
- decision language
- execution plans
- inference conclusions
- benchmark-shaped completion phrases

This is more general than a keyword blacklist.

It treats answer leakage as a semantic capability problem.

## Layer 4: Risk Aggregation

Instead of only `commit / rollback`, the verifier should support risk grades.

Recommended scale:

- `low risk`
- `medium risk`
- `high risk`

Possible actions:

- `low risk` -> commit
- `medium risk` -> retry / refine
- `high risk` -> rollback

This is useful because some borderline cases should not be hard rejected immediately.

## Layer 5: Provenance / Audit Separation

This is the biggest conceptual correction from the earlier draft.

SRP should separate three things:

1. `Semantic State`
   - the runtime operating representation

2. `Evidence Store`
   - the traceable source-backed support layer

3. `Verbatim Archive`
   - the raw record layer for audit only

These should not be collapsed into one blob.

### Role separation

- `Semantic State` is for runtime use
- `Evidence Store` is for support / provenance
- `Verbatim Archive` is for audit only

That means the verifier should not act as if the archive is the runtime memory.

## Access Policy

The cleaner policy is not:

- LLM can never see archive

The cleaner policy is:

- LLM does not directly replay archive text as prompt context by default
- archive access must be mediated by retrieval policy or an evidence query interface
- audit access remains separate from runtime access

This keeps the system traceable without turning the archive into a prompt replay channel.

## Suggested Decision Table

| Coverage | Bidirectional Entailment | Executability | Risk | Action |
|---|---:|---:|---:|---|
| high | pass | no | low | commit |
| high | pass | mild | medium | retry |
| medium | pass | no | medium | retry |
| low | fail | any | high | rollback |
| any | any | yes | high | rollback |

## What This Design Fixes

This refined design fixes several issues in the earlier version:

- it stops treating the source as just raw text
- it makes the unit of comparison semantic objects
- it reframes retention as coverage
- it adds bidirectional entailment instead of one-way scoring
- it upgrades leakage from template matching to executability checking
- it separates runtime state from audit evidence

## What This Design Still Does Not Solve

This design does not yet fully solve:

- how to build a perfect semantic parser
- how to score objects in every domain
- how to calibrate threshold values across tasks
- how to support very creative paraphrase without drift

That is fine.

The goal here is to define the right verification shape first.

## Recommended SRP Architecture

The cleanest version now looks like:

```text
Conversation
   -> Semantic Parser
   -> Semantic State
   -> Recovery / Compression
   -> Semantic Parser
   -> Verification over Semantic Objects
   -> Risk Aggregation
   -> Commit / Retry / Rollback

Evidence Store <-> Audit Interface
Verbatim Archive <-> Audit Only
```

## My Current Judgment

This refined design is more faithful to the actual SRP problem than the earlier text-level version.

It is especially suitable if we want SRP to support:

- semantic translation
- long-task lexical flexibility
- provenance-aware auditing
- lower leakage risk

It is less suitable if we want:

- purely lightweight implementation
- minimal parsing overhead
- one-score-only verification

If we want a serious semantic protocol, though, this is closer to the right shape.

## References

- [The Meaning Factory: Formal Semantics for Recognizing Textual Entailment and Determining Semantic Similarity](https://aclanthology.org/S14-2114/)
- [RAGVUE: A Diagnostic View for Explainable and Automated RAG Evaluation](https://aclanthology.org/2026.eacl-demo.35.pdf)
- [Benchmarking LLM Faithfulness in RAG with Evolving Leaderboards](https://aclanthology.org/2025.emnlp-industry.54.pdf)
- [Generate but Verify: Answering with Faithfulness in RAG-based Systems](https://aclanthology.org/2025.ijcnlp-long.56.pdf)
- [CiteEval: Principle-Driven Citation Evaluation for Source Attribution](https://aclanthology.org/2025.acl-long.1574.pdf)
