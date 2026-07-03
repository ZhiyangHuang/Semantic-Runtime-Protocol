# Benchmark Selection and Adapter Design

This note defines the external evaluation layer for the first SRP paper.

The goal is not to replace the current SRP toy tasks. The goal is to add a public benchmark layer so SRP can be independently evaluated in a familiar setting, while the toy tasks remain the protocol validation layer.

## Why This Layer Exists

The current SRP data flow is good at testing protocol behavior:

- compression
- recovery
- validation
- update

It is not yet enough to serve as the sole evaluation space for a paper. Reviewers are more likely to trust the results if SRP is also tested on public benchmarks with standard task structures and replayable splits.

This note therefore separates two roles:

- public benchmarks provide external comparability
- SRP toy tasks provide protocol-fit validation

The benchmark adapter makes those roles meet at one canonical task schema.

## Design Goal

The adapter should make benchmark tasks behave like SRP benchmark observations:

> a benchmark example becomes a queryable semantic runtime trace, not just a one-off task instance.

In other words, we do not turn SRP into a benchmark-specific system. We turn public benchmark examples into inputs that can be executed through the SRP runtime.

## Recommended Benchmark Families

For the first paper, the most useful public benchmark families are:

### 1. Long-context / cycle-degradation benchmarks

Recommended:

- `RULER`
- `LongBench v2`

Why:

- `RULER` stresses interference, multi-needle retrieval, multi-hop tracing, and aggregation under long contexts.
- `LongBench v2` covers realistic long-context multitasks and is broad enough to support a reviewer-facing claim about general long-context stability.

### 2. Long-term memory / multi-session benchmarks

Recommended:

- `LongMemEval`

Why:

- it directly evaluates long-term conversational memory
- it includes multiple memory ability types
- it fits SRP's repeated state-update framing better than generic QA-only benchmarks

### 3. Retrieval-augmented generation benchmarks

Recommended:

- `RAGBench`
- `KILT`
- `BEIR`

Why:

- `RAGBench` is good for RAG-style end-to-end evaluation
- `KILT` provides a unified knowledge-intensive setting with shared provenance structure
- `BEIR` is useful for retrieval robustness and zero-shot retrieval comparison

## Recommended First-Paper Combination

The most balanced combination for SRP is:

- `RULER` or `LongBench v2` for long-context stress
- `LongMemEval` for conversational memory
- `RAGBench` or `KILT` for retrieval-enhanced comparison
- current SRP toy tasks for protocol validation

This keeps the paper grounded in public benchmarks while preserving a small internal layer that matches SRP's transformation protocol.

## Canonical Adapter Schema

All benchmark inputs should normalize to one canonical task object.

```json
{
  "id": "task_id",
  "source": "RULER | LongBench | LongMemEval | RAGBench | KILT | BEIR | ToySRP",
  "task_type": "long_context | memory | rag | multi_turn_instruction | iterative_cycles",
  "context": "... or [\"...\"]",
  "queries": ["...", "..."],
  "query_expectations": [[["..."]]],
  "expected_output": "...",
  "expected_keywords": ["...", "..."],
  "metadata": {
    "benchmark": "RULER",
    "family": "long_context",
    "split": "validation",
    "context_length": 0,
    "interference_level": 0.0,
    "domain": "general",
    "source_file": "..."
  }
}
```

### Field intent

- `context`
  - the raw benchmark context or a list of context chunks
- `queries`
  - the evaluation questions used during SRP cycles
- `query_expectations`
  - grouped semantic expectations for shared-query evaluation
- `expected_output`
  - the benchmark answer or canonical target, when available
- `expected_keywords`
  - a lightweight fallback for compatibility
- `metadata`
  - benchmark-specific information needed for downstream analysis

## Mapping Rules

### RULER

RULER is best treated as a stress benchmark.

Adapter behavior:

- `context` becomes the long prompt or long document bundle
- `queries` become the probing questions attached to the benchmark item
- `metadata.interference_level` should capture distractor intensity
- `metadata.benchmark_type` should be `stress`

Recommended use:

- test state interference resistance
- test repeated-cycle degradation
- test multi-hop and aggregation behavior

### LongBench v2

LongBench v2 is best treated as a realistic long-context benchmark.

Adapter behavior:

- `context` becomes the document or document bundle
- `queries` becomes the instruction/question pair
- `metadata.domain` should preserve the original task category
- `metadata.benchmark_type` should be `real_world`

Recommended use:

- test real-context generalization
- test stability under long structured input
- test whether SRP preserves behavior across realistic task families

### LongMemEval

LongMemEval is best treated as a long-term memory benchmark.

Adapter behavior:

- each session history becomes `context`
- target questions become `queries`
- memory-ability labels become metadata

Recommended use:

- test multi-session memory retention
- test temporal reasoning
- test knowledge updates and abstention

### RAGBench / KILT / BEIR

These should be adapted as retrieval-centric evaluation inputs.

Adapter behavior:

- retrieved documents or candidate passages become `context`
- benchmark questions become `queries`
- provenance or retrieval labels become metadata

Recommended use:

- compare SRP against retrieval-heavy baselines
- test whether semantic state improves retrieval-conditioned stability
- keep the RAG setting externally recognizable

## SRP Execution Layer

Once a benchmark example is adapted, SRP runs through the same cycle protocol:

```text
S0 = compress(context)
S1 = recover(S0)
S2 = validate(S1, query)
S3 = update(S2, feedback)
```

For repeated-cycle experiments, the cycle depth can be controlled with:

```text
T = {1, 2, 4, 8, 16}
```

The important point is that the benchmark remains unchanged. SRP is what changes around it.

## Evaluation Hooks

The benchmark adapter should expose the same evaluation hooks across all benchmark families:

- task success
- semantic drift
- token cost
- contract satisfaction
- commit / rollback stability

That makes public benchmarks and SRP toy tasks comparable under one runner.

## Relationship To The Current Repo

The current toy tasks in `srp_experiment/data/` are still useful, but they should be treated as the protocol validation layer.

The public benchmarks should become the external evaluation layer.

That separation gives the paper two strengths at once:

- the public layer makes the claim reviewer-friendly
- the toy layer keeps the SRP protocol visible and testable

## Paper Language

A good first-paper phrasing is:

> We evaluate SRP as a runtime abstraction over public long-context, memory, and retrieval benchmarks, and use a small set of SRP-specific toy tasks as a protocol validation layer.

This wording avoids overclaiming while making the evaluation space look standard and defensible.

## Implementation Priority

If this adapter is implemented next, the recommended order is:

1. define one canonical adapter schema
2. add one benchmark family at a time
3. keep the toy tasks intact
4. preserve the current runner and EQ gate
5. only then rewrite the experiments section around the new evidence space

That sequence keeps the project safe: public benchmarks add credibility, but they should not destabilize the protocol work already in place.
