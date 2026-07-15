# SRP Configuration Propagation Validation

This document freezes the first validation layer for the SRP parameter system.
It does not define new runtime behavior.

The question is simple:

> Does a parameter value travel correctly from catalog and registry into runtime behavior?

---

## Propagation Chain

```text
Parameter Catalog
    |
    v
Parameter Registry
    |
    v
RuntimeConfig
    |
    v
RuntimeKernel
    |
    v
Operator
    |
    v
Behavior
```

---

## Validation Goals

### 1. Default Equivalence

The default runtime configuration must be behaviorally equivalent to the legacy kernel path.

Required property:

```text
RuntimeKernel()
    ==
RuntimeKernel(config=default_runtime_config())
```

### 2. Propagation Completeness

Each registered runtime parameter must be observable at the operator or kernel boundary.

Required property:

```text
Registry value -> RuntimeConfig field -> Operator field -> Mutation summary / behavior
```

### 3. Owner Isolation

Changing one owner’s parameter must not change the behavior of an unrelated owner.

Required property:

```text
Activation parameter changes should not alter recovery behavior.
Recovery parameter changes should not alter activation behavior.
```

---

## Initial Validation Matrix

| Parameter | Registry | Config | Kernel | Operator | Behavior |
| --- | --- | --- | --- | --- | --- |
| `activation_threshold` | pass | pass | pass | pass | pass |
| `preserve_evidence` | pass | pass | pass | pass | pass |
| `archive_relations` | pass | pass | pass | pass | pass |
| `recovery_min_evidence` | pass | pass | pass | pass | pass |

---

## Frozen Non-Goals

- parameter optimization
- Bayesian search
- adaptive learning
- runtime policy discovery
- registry mutation during execution

---

## Next Boundary

After this validation is stable, the next step is sensitivity analysis.
That step should only start after configuration propagation is proven stable.

