# SRP Runtime Semantic Protocol Adoption Decision

## Decision Question

Should SRP evolve from a semantic verifier into a runtime semantic protocol?

This note is a one-page protocol adoption aid.

It is not an implementation spec.

## Protocol Readiness Summary

Adopt the protocol direction only if we are willing to commit to all of the following:

- explicit semantic state definition
- parser outputs with confidence and evidence pointers
- weighted semantic coverage
- object alignment before entailment
- bidirectional entailment
- executability / capability checking
- evidence sufficiency
- risk aggregation beyond binary commit / rollback
- governed archive access

If these are not acceptable, SRP should remain a stronger text-level verifier rather than a full protocol.

## Core Principle

Principle 1:

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

This principle unifies the whole design.

It means:

- raw text is input to parsing
- typed semantic state is the verification target
- lexical surface form is not the primary object of commitment

## What We Gain If We Adopt

### 1. Better Fit For Long Tasks

The protocol can allow lexical transformation while still preserving semantic meaning.

That matters for:

- long-horizon memory
- semantic translation
- paraphrase-heavy recovery
- state compression under repeated cycles

### 2. Better Leakage Control

The protocol makes it harder for answer-shaped text to pass as valid state.

That matters because we do not want SRP to become:

- answer caching
- prompt replay
- benchmark-shaped rewriting

### 3. Better Auditability

The split between semantic state, evidence store, and verbatim archive gives us traceability without collapsing all layers into one blob.

That matters for:

- provenance
- debugging
- reviewer trust
- long-term memory governance

### 4. Better Paper Potential

This shape is more likely to read as a runtime protocol than as prompt engineering.

That gives us a clearer paper claim.

## What We Pay

### 1. More Complexity

We will need:

- a parser
- an object model
- alignment logic
- risk aggregation
- audit policy

### 2. More Calibration Work

We will need to tune:

- coverage weights
- entailment thresholds
- risk thresholds
- evidence sufficiency rules

### 3. More Implementation Overhead

This is no longer a minimal patch.

It is a protocol redesign.

## When To Adopt

Adopt now only if the next iteration can support:

- long-task lexical flexibility
- explicit evidence tracing
- controlled archive access
- semantic state typed representation

Do not adopt yet if the plan is to:

- keep the verifier as a single scalar score
- keep runtime state as untyped text
- keep archive replay unrestricted
- keep commit logic purely keyword-based

## Recommended Minimum Adoption Stack

If we adopt, the minimum viable protocol stack is:

1. typed semantic state
2. parser confidence + evidence pointers
3. weighted coverage
4. object alignment
5. bidirectional entailment
6. capability / executability check
7. evidence sufficiency check
8. risk aggregation
9. commit / retry / rollback

## Recommended First Implementation Slice

Do not implement everything at once.

The safest first slice is:

- typed semantic state definition
- parser output format
- weighted coverage
- leakage / capability guard

Then add:

- object alignment
- bidirectional entailment
- evidence sufficiency

Then finally:

- risk aggregation
- governed archive access

## Red Lines

Do not adopt the protocol if any of these are true:

- parser outputs are not traceable
- verification still depends on raw keywords alone
- archive is directly replayed into prompt context by default
- evidence sufficiency is not separated from coverage
- recovery can emit answer-shaped output and still commit

## Decision

- If the goal is a stronger paper and a cleaner runtime story, **adopt**.
- If the goal is minimal engineering change this semester, **do not adopt yet**.

## My Current Recommendation

Adopt the protocol direction, but only after we define the semantic state type and the parser output contract.

That is the smallest point at which the design becomes a real protocol rather than a fancy verifier.

The key reason is that verification should never be text-first.
It should be semantic-representation-first.
