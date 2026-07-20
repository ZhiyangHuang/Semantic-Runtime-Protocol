# v1.1 External Registry Freeze

## Status

Branch:
`v1.1-boundary-generation`

Scope:
`External Evaluation Registry`

This record freezes the external registry layer used by SRP v1.1 boundary
evidence generation.

It does not change the v1.1 boundary milestone or the v1.0 claim boundary.

## Frozen Components

- external source registry schema
- source provenance format
- adapter resolution contract
- `transition_role` semantics

## Frozen Registry Roles

- LongMemEval -> `evidence_update`
- LoCoMo -> `temporal_state_evolution`
- AgentBench -> `action_proposal`
- reasoning -> `inference_proposal`

## Non-Goals

- adding benchmark coverage
- ranking datasets
- measuring model capability
- changing governance decision logic

## Future Boundary

New source families belong to `v1.2` or later.
This freeze keeps `v1.1` focused on reproducible governance evidence.
