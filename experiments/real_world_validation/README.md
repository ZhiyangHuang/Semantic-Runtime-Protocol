# Real World Validation

This package contains the real-data validation branch for SRP.

The intended flow is:

```text
dataset
  |
adapter
  |
semantic event
  |
transition candidate
  |
srp runtime
  |
metrics
  |
artifact bundle
```

The first implementation slice is a LoCoMo bridge runner.
The package is intentionally structured around a shared validation contract so benchmark-specific code stays thin.

