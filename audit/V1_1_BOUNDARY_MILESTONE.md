# SRP v1.1 Boundary Evidence Freeze

## Status

Branch:
`v1.1-boundary-generation`

Milestone:
`Boundary Evidence Freeze`

Date:
`2026-07-19`

This milestone freezes the current SRP v1.1 boundary-reporting layer as a reproducible governance evidence generator.

It does not change the v1.0 claim boundary.

## Frozen Contract

The following contract objects are frozen:

- `BoundaryCase`
- `BoundaryDecision`
- `BoundaryReportMetadata`
- `ArtifactManifest`
- external registry schema
- `transition_role` contract

Current contract family:

- `boundary-v1`
- `schema-v1`

## Frozen Artifacts

The current boundary-reporting artifact set is frozen as the audit output shape:

```text
boundary_report/
├── cases.jsonl
├── decisions.jsonl
├── summary.json
├── metadata.json
├── manifest.json
├── replay_report.json
└── report.md
```

The adapter consistency matrix is frozen as the audit-of-audit layer for the current boundary-reporting branch.

## Reproducibility Freeze

Frozen reproducibility inputs:

- seed
- fixture hash
- decision hash
- report hash
- manifest hash

Frozen reproducibility rule:

```text
same input
    |
    v
same adapter
    |
    v
same decision
    |
    v
same artifact
```

## Frozen Scope

This milestone freezes:

- adapter layer
- boundary evaluation contract
- reporter contract
- matrix consistency audit
- provenance metadata
- external evaluation registry
- external registry schema
- `transition_role` contract

This milestone does not add:

- new adapters
- new workload families
- new benchmark scoring
- new optimization logic
- learned authority models

## Non-Goals

This milestone is not:

- a benchmark framework
- a model evaluation suite
- an optimization comparison
- a learned authority mechanism

## Release Decision

The `v1.1-boundary-generation` branch is frozen at the current boundary evidence milestone.

Any future work should extend the branch through a new milestone rather than mutating this freeze point.
