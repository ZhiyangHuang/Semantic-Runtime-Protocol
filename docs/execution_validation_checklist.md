# SRP Execution Validation Experiment Checklist

This document is the minimal experimental contract for Phase IV: execution validation.

It does not change reconstruction or allocation. It verifies whether the allocated active state can independently support task execution.

---

## 1. Experiment Goal

Validate the following chain:

```text
Recovered State
    -> State Allocation
    -> Active State Only
    -> Task Execution
```

Core question:

```text
How much task performance can be preserved by executing only the allocated active state?
```

---

## 2. Experimental Boundary Freeze

### Recovery

Input:

```text
compressed state
```

Output:

```text
S_recovered
```

Recovery remains unchanged.

### Allocation

Input:

```text
S_recovered
```

Output:

```text
(S_active, S_latent, S_discard)
```

Policies:

- unrestricted
- constrained
- minimal

Allocation rules:

- allocation may only partition recovered objects
- allocation must not create, modify, merge, or repair objects
- all policies operate on the same recovered state

### Execution

Only change:

```text
S_recovered -> LLM -> answer
```

becomes:

```text
S_active -> LLM -> answer
```

---

## 3. Baseline Groups

### Baseline A: Full Context

Input:

```text
original context
```

Purpose:

- upper bound

### Baseline B: Recovered State

Input:

```text
S_recovered
```

Purpose:

- recovery baseline

### Baseline C: Unrestricted Active

Input:

```text
S_active (unrestricted)
```

Purpose:

- no allocation compression

### Baseline D: Constrained Active

Input:

```text
S_active (constrained)
```

Purpose:

- moderate allocation

### Baseline E: Minimal Active

Input:

```text
S_active (minimal)
```

Purpose:

- minimum runtime state

---

## 4. Primary Metrics

### Active Sufficiency

```text
AS = TaskPerformance(S_active) / TaskPerformance(S_recovered)
```

Interpretation:

- `1.0` means active can replace recovered state
- values below `1.0` indicate some task performance loss

### Compression Utility

```text
CU = TaskPerformance(S_active) / |S_active|
```

Interpretation:

- measures task performance per active object
- higher is better

---

## 5. Secondary Metrics

Keep existing allocation metrics:

- `active_object_count`
- `latent_object_count`
- `discard_object_count`
- `active_state_efficiency`
- `latent_preservation`
- `hallucination_isolation`
- `active_retention_ratio`

---

## 6. Expected Outcomes

### Case 1

```text
AS ≈ 1
and
active size << recovered size
```

Conclusion:

- SRP identifies a compact executable semantic state

### Case 2

```text
AS drops slightly
but
CU greatly improves
```

Conclusion:

- allocation improves runtime efficiency with acceptable task degradation

### Case 3

```text
AS collapses
```

Conclusion:

- active selection criteria need improvement

---

## 7. Experiment ID

Recommended identifier:

```text
srp_meas_longbench_execution_validation_r01
```

---

## 8. Deferred Work

Do not add the following before this experiment is complete:

- task-specific schema
- repair
- LLM judge
- new object taxonomy

Reason:

- this experiment only tests whether active state can independently execute the task

