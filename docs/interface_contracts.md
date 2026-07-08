# SRP Interface Contracts

This document freezes the main interface boundaries used by SRP.

---

## Frozen Interfaces

### ReconstructionPolicy

- Responsibility: reconstruct compact executable state from structured semantic state.
- Stability policy: keep interface stable; change implementations, not signatures.

### ReconstructionResult

- Responsibility: carry recovered state and policy metadata.
- Stability policy: keep fields stable across reconstruction policy ablations.

### ReconstructionMetrics

- Responsibility: expose policy-level reconstruction measurements.
- Stability policy: add fields only when a new metric is explicitly introduced.

### Pipeline

- Responsibility: orchestrate compression, reconstruction, validation, and commit/rollback.
- Stability policy: policy selection should be injected, not hard-coded into pipeline control flow.

---

## Stability Policy

- Interface changes require explicit versioning.
- Policy implementations may evolve without changing the contract.
- The pipeline should remain policy-agnostic beyond selection and record keeping.
