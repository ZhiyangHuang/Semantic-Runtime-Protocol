# SRP State Allocation Policy

This document is the implementation specification for the Phase II extension of SRP reconstruction:
semantic runtime state allocation.

It is a design spec, not a theory document. The theoretical framing remains frozen in `docs/research_questions.md` and `docs/metric_definitions.md`.

---

## 1. Principle

State allocation is conservative with respect to truth.

Allocation should prefer preserving valid semantic objects in latent memory rather than discarding them too early.

Operationally:

- `Active` is reserved for objects required by the current task.
- `Latent` stores valid objects that are not currently required but may be useful later.
- `Discard` is reserved for hallucination, unsupported inference, duplicate content, or content with sufficient evidence of no runtime value.

The allocation problem is feasibility-oriented, not ground-truth classification-oriented:

```text
find (S_active, S_latent, S_discard)
```

such that the runtime can execute the current task with a compact active state while preserving future recoverability.

Action space:

- allocation policies may only partition recovered objects into `active`, `latent`, and `discard`
- allocation policies must not create, modify, merge, or repair semantic objects
- all policies operate on the same recovered state and differ only in allocation objective and constraints

---

## 2. Scope

Semantic runtime state allocation determines how recovered semantic information is partitioned into executable state, recoverable latent memory, and discarded information.

This spec defines the interface and behavior required to support that partitioning.

---

## 3. State Model

Let:

```text
S_runtime = (S_active, S_latent, S_discard)
```

Where:

- `S_active` is the minimal executable semantic state required for current task execution.
- `S_latent` is valid semantic memory retained for future retrieval.
- `S_discard` is invalid, redundant, or unsupported information removed from runtime state.

The partition should satisfy:

```text
S_active ∩ S_latent = ∅
S_active ∩ S_discard = ∅
S_latent ∩ S_discard = ∅
```

### Active State

Constraint:

```text
TaskPerformance(S_active) >= C
```

Objective:

```text
min |S_active|
```

Selection criteria:

- task-critical
- query-relevant
- dependency-required

### Latent State

Constraint:

```text
Validity(S_latent) = 1
```

Objective:

```text
maximize FutureRecall(S_latent)
```

Latent state should contain valid semantic memory that is not needed for the current execution but may be useful later.

### Discard State

Definition:

```text
S_discard = S - (S_active ∪ S_latent)
```

Discard includes:

- hallucination
- duplicate content
- unsupported inference
- irrelevant noise

---

## 4. Allocation Policy Contract

The allocation layer is a post-reconstruction step.

Suggested interface:

```python
class StateAllocationPolicy:

    def allocate(
        self,
        reconstructed_state,
        task_context,
    ) -> StateAllocationResult:
        ...
```

Inputs:

- `reconstructed_state`
- `task_context`

Outputs:

```python
@dataclass
class StateAllocationResult:
    active_state: StructuredStatePackage
    latent_state: StructuredStatePackage
    discard_state: StructuredStatePackage
    metrics: AllocationMetrics
```

Design rules:

- Keep allocation separate from reconstruction.
- Do not replace `ReconstructionResult`.
- Add `StateAllocationResult` as a downstream layer.
- Preserve interface stability once implemented.

---

## 5. Policy Variants

### Unrestricted Allocation

Behavior:

```text
S_active = S_runtime
S_latent = ∅
S_discard = ∅
```

Purpose:

- baseline with maximal retention
- upper bound on active coverage

### Constrained Allocation

Behavior:

```text
S_active = constrained subset of S_runtime
S_latent = supported but non-essential remainder
S_discard = unsupported remainder
```

Purpose:

- reduce active inflation
- preserve more structure than minimal allocation

### Minimal Sufficient Allocation

Behavior:

```text
S_active = smallest task-sufficient subset
S_latent = valid recoverable remainder
S_discard = hallucinated or unsupported content
```

Purpose:

- best candidate for runtime execution
- minimize active size while preserving task fidelity

Implementation guidance:

- Use deterministic or rule-based selection first.
- Keep policy-specific logic separate from the pipeline.
- Avoid prompt-only distinctions as the primary mechanism.

---

## 6. Metrics

The allocation layer should emit the following metrics.

### Active Retention Ratio

```text
ARR = |S_active ∩ Important| / |Important|
```

Purpose:

- measure how much important information is loaded into the active runtime state.

### Active State Efficiency

```text
ASE = TaskCoverage / |S_active|
```

Purpose:

- measure how much task value each active object carries.

### Latent Preservation

```text
LP = |FutureRelevant ∩ S_latent| / |FutureRelevant|
```

Purpose:

- measure whether useful but non-active information is preserved for future retrieval.

### Hallucination Isolation

```text
HI = 1 - |Hallucination ∩ S_active| / |S_active|
```

Purpose:

- measure whether hallucination is kept out of runtime-active state.

Required output fields:

- `active_object_count`
- `latent_object_count`
- `discard_object_count`
- `validation_coverage`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`
- `reconstruction_efficiency`

---

## 7. Implementation Notes

Pipeline order:

```text
compressed state
-> reconstruction policy
-> reconstructed state
-> state allocation policy
-> runtime state
```

Do not:

- collapse allocation into reconstruction
- treat latent memory as discarded memory
- let hallucination enter active state

Recommended module layout:

```text
srp/state_allocation/
    policy.py
    policies.py
    result.py
    metrics.py
```

---

## 7. Experimental Mapping

### Variants

| Experiment | Purpose |
| --- | --- |
| unrestricted | upper recall baseline |
| constrained | controlled reduction |
| minimal | allocation hypothesis |

### Reported Metrics

Each run should report:

```text
active_object_count
latent_object_count
discard_object_count
validation_coverage
ASE
LP
HI
```

### Comparison Rule

Evaluate policy implementations without changing the interface.

---

## Stability Policy

- This document is an implementation specification.
- The theory layer remains frozen in `docs/research_questions.md`, `docs/metric_definitions.md`, and `docs/interface_contracts.md`.
- Policy changes should happen in code, not in the contract text, unless a new version is explicitly introduced.
