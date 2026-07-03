# Unified Evaluation Regime

This note fixes the evaluation regime used to compare:

- `raw_prompt`
- `summarization`
- `rag`
- `srp`
- `rag_srp_v2`

The goal is to keep the comparison fair without pretending that every baseline is an off-the-shelf reference implementation from an external toolkit.

## Core Rule

All five methods run under the same token-bounded execution regime.

For each request, we reserve a fixed total budget and split it into:

- system prompt budget
- query budget
- output budget
- safety margin
- remaining memory-transformation budget

The shared configuration is currently controlled by:

- `SRP_TOTAL_TOKEN_BUDGET`
- `SRP_SYSTEM_TOKEN_BUDGET`
- `SRP_QUERY_TOKEN_BUDGET`
- `SRP_OUTPUT_TOKEN_BUDGET`
- `SRP_SAFETY_MARGIN_TOKENS`

Under this regime, methods differ only in their memory transformation operator.

## Baseline Definitions

### 1. `raw_prompt`

`raw_prompt` is the direct carryover baseline.

It does not perform summarization, retrieval, or semantic-state compression. It simply carries forward raw memory and applies hard budget clipping before prompt assembly.

This means it is not an "infinite raw context" baseline. It is a budget-constrained direct prompt baseline.

### 2. `summarization`

`summarization` is the summary-compression baseline.

It transforms memory by replacing the prior state with a shorter summary under the same output and prompt budget constraints. It does not retrieve chunks and does not use SRP validation.

### 3. `rag`

`rag` is the retrieval-selection baseline.

It transforms memory by:

- chunking the current memory store
- selecting the top retrieval candidates
- packing them under a fixed retrieval budget

It does not use semantic-state compression, recovery, or validation. It is therefore a budget-constrained retrieval baseline rather than an automatic compression method.

### 4. `srp`

`srp` is the semantic-state compression baseline.

It transforms memory by compression, recovery, validation, and update under the same global token budget, while enforcing bounded semantic drift through the SRP protocol.

### 5. `rag_srp_v2`

`rag_srp_v2` is the retrieval-plus-semantic-state baseline.

It first applies retrieval under the same retrieval budget, then applies SRP compression/recovery/validation to the retrieved working memory.

## Why This Is Fair

The comparison is fair because:

- all methods face the same total token ceiling
- all methods reserve output under the same rule
- differences arise from memory transformation strategy rather than unequal context access

In short, this is a controlled comparison of memory operators under a shared execution budget.

## What This Is Not Claiming

This setup does not claim that:

- `raw_prompt` is an unconstrained full-context baseline
- `summarization` is a canonical external memory tool
- `rag` is an official reference implementation from a public benchmark repository

Instead, it claims something narrower and more defensible:

these are controlled baseline families instantiated under a shared execution budget so that SRP can be compared against common alternative memory operators on the same platform.
