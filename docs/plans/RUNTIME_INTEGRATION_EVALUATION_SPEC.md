# SRP v1.1 Runtime Integration Evaluation Spec

This spec defines the next evaluation step for Semantic Runtime Protocol (SRP): insert SRP as an admission-control boundary inside an existing semantic runtime.

## Goal

Validate that SRP can sit between semantic proposal generation and persistent mutation without taking ownership of the underlying memory mechanism.

The target claim is:

> SRP can be inserted as an independent governance layer between semantic proposal generation and persistent runtime mutation.

## Design Principles

- One runtime.
- One adapter.
- One workload family.
- One admission boundary.
- No benchmark sprawl.
- No claim that SRP replaces the memory system.

## 1. Runtime Architecture

### Baseline

```text
Conversation Event
        |
        v
   Agent / LLM
        |
        v
 Memory Extraction
        |
        v
 Persistent Memory Write
```

Baseline risk:
- candidate transitions receive mutation authority directly

### SRP Integration

```text
Conversation Event
        |
        v
   Agent / LLM
        |
        v
 Candidate Semantic Update
        |
        v
+----------------------------+
| Semantic Runtime Protocol  |
|                            |
| Observation                |
| Validation                 |
| Evidence Evaluation        |
| Governance Decision        |
+----------------------------+
        |
   +----+----+
   |         |
 Reject    Approve
   |         |
Discard   Memory Write
```

SRP controls commit permission only.
It does not control representation, retrieval, generation, or extraction.

## 2. Adapter Interface

### Candidate Object

```python
class SemanticTransitionCandidate:
    transition_id: str
    subject: str
    operation: str  # ADD | UPDATE | DELETE
    old_state: str | None
    proposed_state: str
    provenance: dict
    evidence: list[dict]
    confidence: float
    timestamp: str
```

### Decision Object

```python
class GovernanceDecision:
    transition_id: str
    decision: str  # APPROVE | REJECT
    validation_result: dict
    evidence_score: float
    violated_invariants: list[str]
    governance_trace: dict
    latency_ms: float
```

### Runtime Flow

```python
candidate = memory_adapter.extract(event)
decision = srp.evaluate(candidate)

if decision.decision == "APPROVE":
    memory_adapter.commit(candidate)
else:
    memory_adapter.reject(candidate)
```

## 3. Workload Family

Use one semantic mutation workload family with three transition categories.

### A. Valid Evolution

Example:

```text
Day 1:
User prefers coffee.

Day 20:
User prefers tea now.
```

Expected:
- approve

### B. Contradictory Mutation

Example:

```text
Existing:
location = New York

Proposal:
location = Los Angeles
```

Expected:
- reject

### C. Unsupported Injection

Example:

```text
User identity:
Alice -> Admin
```

Expected:
- reject

## 4. Evaluation Modes

### Stage 1: Replay Mode

Purpose:
- validate runtime compatibility
- record admission decisions without mutating the live store

Outputs:
- decision log
- admission rate
- rejection rate
- rejection reasons

### Stage 2: Shadow Mode

Purpose:
- run SRP beside the live runtime without blocking writes
- compare baseline writes against SRP recommendations

Outputs:
- actual write decisions
- SRP recommendations
- potential unsafe mutations

### Stage 3: Controlled Admission

Purpose:
- enable SRP as the gate before write
- measure end-to-end latency and real admission behavior

Outputs:
- commit / discard decisions
- runtime overhead

## 5. Metrics

### 5.1 Unsafe Acceptance Rate

```text
UAR = incorrect transitions accepted / all invalid transitions
```

Primary target:
- baseline high
- SRP near zero

### 5.2 False Rejection Rate

```text
FRR = valid transitions rejected / all valid transitions
```

This protects against a degenerate always-reject controller.

### 5.3 End-to-End Latency

Measure the full pipeline:

```text
Extraction + Embedding + SRP + Storage
```

Report:
- baseline latency
- SRP latency
- relative overhead

### 5.4 Governance Trace Completeness

Check whether each mutation has a full trace:
- proposal
- validation
- evidence
- decision
- commit / reject

Target:
- trace completeness = 1.0

## 6. Report Format

Recommended artifact tree:

```text
experiments/
  runtime_integration/
    adapter/
    workloads/
    traces/
    decisions/
    latency/
    report.json
```

Minimal report fields:

```json
{
  "runtime": "memory_backend_x",
  "mode": "controlled_admission",
  "transitions": 5000,
  "accepted": 4120,
  "rejected": 880,
  "unsafe_accept_rate": 0.002,
  "false_rejection_rate": 0.031,
  "latency_overhead": 0.047,
  "trace_completeness": 1.0
}
```

## 7. Paper Wording

Suggested section title:

```text
4.X Runtime Integration Evaluation
```

Suggested opening:

> This evaluation studies whether SRP can operate as an admission-control boundary inside an existing semantic runtime. Unlike memory architectures that define storage and retrieval mechanisms, SRP is evaluated only at the transition authorization boundary between semantic proposal generation and persistent mutation.

Suggested positioning sentence:

> The goal is not to compare memory architectures, but to evaluate whether semantic transitions can be governed without requiring control over the underlying runtime implementation.

Suggested interpretation sentence:

> The integration results demonstrate that SRP can be inserted as an independent governance layer, preserving the separation between proposal generation, evidence evaluation, and mutation authority.

## 8. Scope Guardrails

- Do not claim production deployment.
- Do not add more memory targets in the first pass.
- Do not turn the evaluation into a memory benchmark.
- Do not change the abstract before runtime insertion evidence exists.

## 9. Recommended Implementation Order

1. Add the adapter and candidate/decision objects.
2. Add replay mode.
3. Add shadow mode.
4. Add controlled admission.
5. Add the runtime integration report.
6. Update the paper section and claim ledger.
