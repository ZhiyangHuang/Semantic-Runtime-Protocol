# SRP Related Work V1

## 1. Retrieval-Augmented Generation and External Memory

Retrieval-augmented generation, vector databases, and external memory systems aim to improve information access and response quality.

These systems are related to SRP because SRP can use retrieval and evidence as inputs.
However, the primary question differs:

```text
RAG:
How to retrieve useful information?

SRP:
How to govern semantic state evolution?
```

The key separation is:

`Retrieval authority != Evolution authority`

SRP may consume retrieved evidence, but retrieval does not decide whether semantic mutation is allowed.

## 2. LLM Memory Systems

LLM memory systems, including episodic memory, long-term memory, memory compression, and reflection-based memory, typically focus on what to store, when to retrieve, and how to summarize prior context.

SRP is related because it also manages persistent semantic state.
The difference is that SRP is concerned with whether semantic transformation is allowed and whether evidence supports that transformation.

```text
Memory stores history.
SRP governs transformation of history.
```

Memory systems preserve or reconstruct context.
SRP validates whether state evolution remains within governed boundaries.

## 3. Autonomous Agents

Autonomous agent systems emphasize planning, tool use, and execution loops.

They are related to SRP because both involve dynamic decision-making over time.
The difference is that many agentic systems merge observation, decision, and action into a single loop.

SRP separates them:

- evidence may inform
- recommendation may suggest
- governance decides
- runtime executes

```text
Evidence != Authority
Recommendation != Execution
```

## 4. Reinforcement Learning for Adaptation

Reinforcement learning provides policy optimization, reward maximization, and environment adaptation.

RL is related to SRP only at the future-adaptation boundary.
The current SRP baseline does not learn a policy for runtime mutation.
Instead, it performs:

```text
observe
   ->
validate
   ->
optimize within constraints
```

That distinction is important because SRP first establishes boundaries before any adaptive learning is allowed.

## 5. Governance and Controlled Systems

SRP is also related to controlled systems, safety layers, constrained optimization, and human approval loops.

These areas share a concern with limiting unsafe action, but SRP focuses specifically on semantic state change.
Its contribution is not merely to constrain a system.
It is to establish explicit authority boundaries for semantic evolution.

## 6. Positioning Summary

| Area | Primary Question | SRP Difference |
| --- | --- | --- |
| RAG | How to retrieve useful information? | How to govern semantic evolution? |
| Memory | What to store and retrieve? | How to validate semantic transformation? |
| Agents | How to act autonomously? | How to separate evidence from authority? |
| RL | How to adapt a policy? | How to constrain adaptation after validation? |
| Governance | How to control actions? | How to govern semantic state change? |

## 7. Summary

SRP is related to retrieval, memory, agents, RL, and governance, but it is not a variant of any one of them.
Its central research question is different:

> How can semantic state evolve only within validated, governed, and evidence-informed boundaries?

