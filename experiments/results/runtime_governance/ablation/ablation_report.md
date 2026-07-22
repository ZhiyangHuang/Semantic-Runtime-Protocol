# Runtime Governance Ablation

## Summary
- `record_count`: 30
- `case_count`: 5
- `variant_count`: 6

| Variant | Invalid Accept | State Corruption | Authority Escalation | Rollback Success | Verification Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| full_srp | 0.000 | 0.000 | 0.000 | 1.000 | 0.350 |
| no_governance | 1.000 | 1.000 | 0.000 | 0.000 | 0.344 |
| evidence_as_authority | 0.250 | 0.250 | 0.000 | 0.750 | 0.344 |
| no_validation | 0.250 | 0.250 | 0.000 | 0.750 | 0.219 |
| no_evidence | 0.250 | 0.250 | 0.000 | 0.750 | 0.244 |
| direct_mutation | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |

## Interpretation
Full SRP should keep invalid acceptance, state corruption, and authority escalation at zero in the evaluated contract.

## Latency
- `sample_count`: 30