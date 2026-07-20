# Admissibility Boundary Validation

## Research Question

RQ1: Can an explicit admissibility boundary prevent invalid semantic state transitions that are accepted by unconstrained update mechanisms?

## Hypothesis

SRP should reject invalid transitions even when they look plausible under evidence-only or authority-only assumptions.

## Cases

- `Unconstrained transition`: updates without an admissibility check
- `Evidence-driven authority`: evidence is treated as if it could raise permission
- `Authority-only transition`: authority is checked without evidence validation
- `SRP`: evidence validation and authority checking are both required
- `Optimization override`: optimization pressure is allowed to remove provenance and should be rejected

## Interpretation

The key paper-facing result is not accuracy.
It is that SRP preserves the admissibility boundary and rejects inadmissible semantic transitions.

In the current evaluated stress test:

- `SRP boundary violation rate = 0.0`
- `Direct update invalid acceptance = 1.0`
- `Evidence-as-authority invalid acceptance = 0.5`
- `Authority-only invalid acceptance = 0.5`

## Limitations

- This experiment is intentionally small and synthetic.
- It is a closure test for the governance claim, not a benchmark.
- It is meant to support the first paper claim before expanding to additional scenarios.
