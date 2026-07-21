# MMLU SRP Treatment Description

Date: 2026-07-21

This document defines the benchmark treatment used for the SRP variant in MMLU and the interpretation boundary for later ARC execution.

## 1. Purpose

The MMLU benchmark is used here as a controlled benchmark setting for evaluating how the SRP runtime handles context recovery and prompt construction.

The goal is not to redefine MMLU as a memory benchmark.
The goal is to test whether an SRP-managed context path can be applied consistently and audited independently from the baseline path.

## 2. Baseline Input

Baseline receives:
- the original MMLU question
- the original answer choices
- the subject label when present
- the same system instruction used for SRP

Baseline does not receive:
- recovered semantic context
- additional runtime memory state
- answer-key leakage through the prompt path

## 3. SRP Input

SRP receives the same benchmark case as baseline, plus a recovered semantic context block produced by the SRP runtime path.

The intended recovered semantic context should include only case-local information needed for runtime reconstruction, such as:
- question text
- answer choices
- subject label
- stable provenance or state metadata

The recovered context must not introduce extra benchmark answers or external knowledge that the baseline does not also have access to.

## 4. Recovered Context Source

The recovered semantic context is derived from the benchmark case and the SRP runtime path.

It is not intended to come from:
- the gold answer key as a benchmark signal
- future labels
- external hidden annotations
- any source unavailable to the baseline evaluation path

If a run serializes `expected_answer` into the prompt-visible SRP recovered context, that field should be treated as a methodological risk and should be removed from paper-facing treatment before any claim is promoted.

## 5. Interpretation Boundary

This treatment supports the following interpretation:

- baseline measures the original benchmark task under the plain prompt path
- SRP measures the same task under an audited runtime context-recovery path
- the comparison is about runtime treatment and context handling, not about changing the benchmark definition itself

This treatment does not support the following interpretation:

- SRP universally improves general capability
- recovered context may contain the answer key and still be treated as a clean benchmark comparison
- a prompt difference that changes answer visibility can be ignored in the paper narrative

## 6. Paper and ARC Usage

This document should be referenced before:
- writing the ARC full-run protocol
- drafting paper-facing benchmark interpretation
- comparing baseline vs SRP results across MMLU, ARC, and LongMemEval

For future ARC execution, the same treatment boundary should be enforced:
- baseline and SRP must receive the same case content
- SRP may differ only in approved runtime context recovery
- no benchmark answer key should be introduced into the prompt-visible SRP context

