# Runtime Governance Validation

## Ablation
- `record_count`: 30
- `variant_count`: 6
- `latency_sample_count`: 30

## Failure Injection
- `record_count`: 90
- `attack_count`: 3
- `latency_sample_count`: 90

## LLM Transition
- `scenario_count`: 3
- `record_count`: 6
- `proposal_acceptance_rate`: 0.000
- `srp_invalid_accept_rate`: 0.000

## Latency
- `sample_count`: 0
- `mean_total_ms`: 0.000

## Summary
The shared contract keeps ablation and failure injection on the same evaluation surface.
