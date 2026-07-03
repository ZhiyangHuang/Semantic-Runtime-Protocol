# SRP Anti-Leakage Modification Plan

## Purpose

This note rewrites the anti-leakage plan under a stricter scope definition.

The goal is **not** to make SRP look like it solves every leakage problem in the full ML stack.

The goal is to make SRP defensible as an:

- inference-time semantic-state protocol

that may later extend to:

- semantic translation across model or system layers

while avoiding the most serious forms of:

- answer caching
- reasoning caching
- benchmark-shaped runtime behavior

This plan keeps the risks visible.
It does **not** delete them just because some of them fall outside the current intervention scope.

## Scope Definition

### What SRP Currently Tries To Control

SRP currently participates in:

- inference-time compression
- inference-time recovery
- inference-time validation and rollback
- inference-time semantic-state packaging

Potential future extension:

- semantic translation across model boundaries or intermediate layers

### What SRP Does Not Currently Try To Solve

SRP does not currently try to solve:

- pretraining contamination
- fine-tuning leakage
- training-time label leakage
- optimizer-level memorization

These risks still matter.
They should still be acknowledged to reviewers.
But they should be framed as:

- broader system risks

rather than:

- the primary implementation target of the current SRP protocol work

This is similar to how strong RAG papers often acknowledge training-time or model-internal leakage risks without presenting retrieval itself as the solution to all of them.

## Core Design Principle

The central anti-leakage principle for SRP should be:

> SRP may preserve semantic state, but it may not preserve future task solutions.

In practical terms, SRP should preserve:

- facts
- constraints
- preferences
- relations
- stable semantic state

SRP should not preserve:

- query-answer pairs
- future answers
- reasoning traces
- benchmark labels
- task-specific solutions

## Why RAG Is The Right Reference

RAG usually behaves more safely by default because it tends to:

- retrieve evidence fragments
- expose those fragments to the model
- let the model perform fresh reasoning later

So well-behaved RAG is closer to:

- `memory lookup + new reasoning`

than to:

- `answer caching`

SRP is more vulnerable because it explicitly:

- compresses
- rewrites
- stores
- recovers

That means SRP needs stronger protocol constraints than RAG.

But the discipline SRP should borrow from RAG is simple:

- preserve evidence
- avoid preserving solutions

## Reframed Risk Sources For SRP

The most useful way to plan the changes is to think in terms of **risk sources**, not only abstract cheating labels.

### Source 1: Runtime Package Leakage

This is the main SRP risk source.

It happens when the compressed package itself becomes:

- answer-shaped
- reasoning-shaped
- benchmark-shaped

This is fully in scope for SRP.

### Source 2: Anchor Or Correction-State Leakage

This happens when:

- `anchor_memory`
- correction memory
- rollback memory

start preserving more than admissible state.

This is also fully in scope for SRP.

### Source 3: Validation-Side Shaping Leakage

This happens when commit or rollback logic quietly pressures the runtime state toward benchmark-facing targets.

This is in scope for SRP because it is part of inference-time control.

### Source 4: Runtime / Evaluation Interface Leakage

This happens when evaluation-side artifacts enter runtime-state shaping.

Examples:

- `expected_keywords`
- query-side target labels
- benchmark-aware vocabulary injection

This is in scope for SRP because it sits at the protocol boundary.

### Source 5: Training-Time Or Model-Internal Leakage

This includes:

- pretraining memorization
- fine-tuning shortcuts
- hidden benchmark familiarity already inside the base model

This source is real.
It should remain acknowledged.
But it is not the main implementation target of the current SRP redesign.

## What SRP Should Learn From RAG

### Lesson 1: Store Evidence, Not Solutions

RAG usually works with chunks or evidence spans.

SRP should move in the same direction:

- preserve evidence-like state
- avoid answer-like state

### Lesson 2: Let Reasoning Happen At Answer Time

RAG usually does not try to pre-solve the future question.

SRP should adopt the same rule:

- the package may reduce context burden
- the package may stabilize memory
- the package may not reduce future reasoning complexity by storing the answer

### Lesson 3: Narrow State Is Safer Than Helpful Rewriting

RAG narrows context rather than globally rewriting the memory into a more benchmark-helpful form.

SRP should become more conservative about:

- paraphrase
- abstraction
- concept expansion
- answer-style normalization

### Lesson 4: Narrow Scope Claims Are More Trustworthy

RAG papers are usually stronger when they do not overclaim.

SRP should do the same:

- acknowledge broader risks
- solve the risks that belong to the inference-time protocol
- avoid pretending to solve all leakage in the full model lifecycle

## Main SRP Risk Areas To Modify

## Risk Area A: Compression Schema Is Too Summary-Centric

Relevant paths:

- [prompting.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py:25)
- [compress.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/compress.py:31)

Current issue:

- `memory_summary` can become too answer-like
- `anchor_terms` can drift toward benchmark-shaped abstractions

Anti-leakage direction:

- make compression more evidence-like and less summary-like

Planned change:

- replace summary-centric packaging with span-centric packaging
- explicitly forbid answer-shaped content

Recommended schema direction:

```json
{
  "fact_spans": ["..."],
  "constraint_spans": ["..."],
  "preference_spans": ["..."],
  "relation_spans": ["..."]
}
```

Reason:

- copied spans are easier to audit
- summary text is easier to overfit into solution-shaped content

## Risk Area B: Recovery Prompt Still Rewards Helpful Re-Interpretation

Relevant path:

- [prompting.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/prompting.py:47)

Current issue:

- recovery still risks becoming "benchmark-helpful reconstruction"
- that is too close to answer shaping

Anti-leakage direction:

- recovery should reassemble state, not optimize answerability

Planned change:

- rewrite recovery as evidence reassembly
- explicitly forbid unsupported conclusions

Recommended recovery rules:

- reassemble stored facts and constraints
- do not infer new conclusions
- do not rewrite into query-answer form
- do not add anything unsupported by stored spans or admissible anchor memory

This is directly in scope because recovery is an inference-time SRP mechanism.

## Risk Area C: Anchor Memory Needs A Formal Admissibility Rule

Relevant paths:

- [recover.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/recover.py:1)
- [rag_srp_v2.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_v2.py:44)

Current issue:

- anchor memory is useful for stability
- but if the anchor becomes answer-shaped, recovery just propagates leakage

Anti-leakage direction:

- treat anchor memory like evidence, not like a target answer sheet

Planned rule:

Anchor may contain:

- facts
- relations
- preferences
- constraints
- stable user state

Anchor may not contain:

- future query answers
- reasoning traces
- labels
- task solutions

This rule should also remain valid if SRP later becomes a semantic translation layer between models.

## Risk Area D: Evaluation-Side Vocabulary Is Too Close To Runtime State

Relevant paths:

- [rag_srp.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp.py:38)
- [rag_srp_anchor.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_anchor.py:66)
- [rag_srp_v2.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/baselines/rag_srp_v2.py:54)

Current issue:

- `expected_keywords` are evaluation-side artifacts
- they currently influence runtime-state shaping in hybrid lines

This creates benchmark-shaping risk.

Anti-leakage direction:

- runtime state should come from memory evidence, not evaluation labels

Planned change:

- stop seeding semantic state from `expected_keywords`
- derive runtime vocabulary only from:
  - memory text
  - explicit constraints
  - admissible stored spans

Not from:

- evaluation expectations

This is one of the highest-value fixes.

## Risk Area E: Validation Should Filter Drift, Not Force Benchmark Conformity

Relevant paths:

- [validate.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/validate.py:1)
- [collect_batch_summary.py](/abs/path/C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/collect_batch_summary.py:60)

Current issue:

- validation is useful for rollback safety
- but keyword-shaped retention checks can become hidden label pressure

Anti-leakage direction:

- validation should be state-hygiene oriented

Planned change:

- reduce dependence on evaluation-facing keyword pools in commit decisions
- move toward:
  - span retention
  - contradiction avoidance
  - anchor-compatible state overlap
  - admissibility filtering

Less ideal validation targets:

- query-success proxies
- future answer targets
- benchmark-label overlap

## Concrete Modification Plan

### Modification 1: Add A Package Admissibility Filter

Goal:

- reject packages that look answer-shaped or reasoning-shaped before commit

Implementation direction:

- add a helper in `srp/validate.py` or a new `srp/admissibility.py`

The filter should flag patterns like:

- explicit Q/A formatting
- "the answer is"
- ordered reasoning steps
- benchmark-label phrases

Suggested outputs:

- `package_admissible`
- `admissibility_reason`

This is the single clearest SRP-side anti-cheating control.

### Modification 2: Replace Summary-Centric Compression With Span-Centric Compression

Goal:

- turn SRP packaging into evidence preservation rather than answer-shaped summarization

Planned direction:

- store short copied spans instead of abstract free-form summaries

Benefits:

- easier auditing
- closer to RAG evidence behavior
- more compatible with future cross-model semantic translation

### Modification 3: Rewrite Recovery As Reassembly, Not Reconstruction

Goal:

- stop recovery from inventing benchmark-helpful restatements

Planned direction:

- reassemble memory from admissible evidence spans
- forbid derived conclusions that are not directly supported

### Modification 4: Remove `expected_keywords` From Runtime State Construction

Goal:

- sever the direct path from evaluation labels into runtime state

Allowed runtime sources:

- user-visible memory
- explicit constraints
- admissible spans

Disallowed runtime sources:

- expected keyword lists
- evaluation labels
- target-answer hints

### Modification 5: Separate In-Scope And Out-Of-Scope Leakage Claims In Documentation

Goal:

- make the paper more trustworthy by being precise

Required documentation claim:

- SRP addresses inference-time semantic-package leakage
- SRP does not claim to eliminate training-time contamination or full-model memorization

This is not a weakness.
It is a scope clarification.

### Modification 6: Add A Reasoning Independence Test

Goal:

- demonstrate that SRP preserves memory without caching answers

Basic test idea:

1. store memory state
2. later ask a question requiring fresh reasoning over that state
3. verify that stored state provides facts, not the final solution

This is the strongest future diagnostic for the anti-leakage story.

## Suggested Formal Rule Set

### Rule 1: Admissible State Only

SRP may store:

- fact state
- relation state
- preferences
- constraints
- intent-like user state

SRP may not store:

- future query answers
- reasoning traces
- task labels
- benchmark-side supervision

### Rule 2: Recovery Cannot Add Unsupported Conclusions

Recovery may:

- reorder
- lightly normalize
- compactly reassemble

Recovery may not:

- derive new final answers
- insert unsupported conclusions

### Rule 3: Validation Cannot Depend On Future Query Solutions

Validation may use:

- drift checks
- contradiction checks
- admissibility checks

Validation should avoid using:

- future answer targets
- query-specific labels as commit criteria

### Rule 4: Scope Disclosure Must Be Explicit

Paper-facing wording should make clear:

- SRP controls inference-time semantic packaging risks
- SRP does not claim to eliminate training-time contamination or model memorization

## Recommended Rollout Order

### Stage 1: Prompt And Policy Hardening

Files likely to change:

- `prompting.py`
- `srp/recover.py`
- `srp/compress.py`

Goal:

- explicitly forbid answer caching and reasoning traces

### Stage 2: Runtime State Source Cleanup

Files likely to change:

- `srp/pipeline.py`
- `baselines/rag_srp.py`
- `baselines/rag_srp_anchor.py`
- `baselines/rag_srp_v2.py`

Goal:

- remove `expected_keywords` from runtime-state shaping

### Stage 3: Admissibility Validation

Files likely to change:

- `srp/validate.py`
- maybe new `srp/admissibility.py`

Goal:

- reject suspicious packages before commit

### Stage 4: Reasoning Independence Diagnostic

Goal:

- prove that SRP still requires fresh reasoning at answer time

### Stage 5: Future Translation-Safe Check

Goal:

- ensure the same admissibility rules still hold if SRP becomes a semantic translation layer across models

## Best Immediate Next Step

The most valuable near-term change is:

1. stop using evaluation-shaped inputs in runtime state construction
2. harden compression and recovery prompts with explicit anti-answer-caching rules
3. add a package admissibility check

And document clearly that:

- these are inference-time protocol protections
- broader training-time leakage risks remain acknowledged but out of primary scope

## Final Recommendation

RAG's strongest methodological advantage is not that it is smarter.

It is that it usually keeps a cleaner separation between:

- memory evidence

and

- final reasoning

SRP should borrow exactly that discipline.

SRP should also borrow RAG's scope discipline:

- acknowledge broader risks
- solve the risks that belong to the inference-time protocol
- avoid overclaiming control over the full training stack

So the anti-leakage redesign principle should be:

> Make SRP behave more like evidence-preserving structured memory, and less like a compact answer-preserving semantic cache.
