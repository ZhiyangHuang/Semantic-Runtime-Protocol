# Runtime Governance Failure Injection

## Summary
- `record_count`: 90
- `attack_count`: 3
- `variant_count`: 6
- `case_count`: 5

| Attack | Invalid Accept | State Corruption | Authority Escalation | Rollback Success | Verification Delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| invalid_transition | 0.375 | 0.375 | 0.000 | 0.625 | 0.170 |
| evidence_inflation | 0.625 | 0.625 | 0.000 | 0.375 | 0.083 |
| authority_injection | 0.375 | 0.375 | 0.375 | 0.625 | 0.256 |

## Interpretation
The relevant property is containment of invalid transitions, authority escalation, and corruption after reject.
