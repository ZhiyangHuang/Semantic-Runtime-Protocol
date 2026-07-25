# SRP Evidence Bundles

This directory is the single entry point for release-facing evidence bundles.

Artifacts stored here are:

- explicitly approved by audit records
- linked to scientific claims
- generated from reproducible evaluation workflows

This directory does not contain:

- raw experiment dumps
- temporary outputs
- debug traces
- intermediate evaluation files

## Artifact Index

| Artifact | Purpose | Claim Link |
| --- | --- | --- |
| `phase_v_retention` | governed reconstruction evaluation | recovery implementation case |
| `semantic_backend_comparison` | backend consistency evaluation | runtime independence |
| `external_validation` | external evidence package | external validation |

Each promoted artifact contains:

- `report.md`
- `summary.json`
- `metadata.json`

`metadata.json` records provenance, validation context, and promotion linkage.

## Evidence Governance

- [../release/EVIDENCE_SURFACE.md](../release/EVIDENCE_SURFACE.md)
- [../release/README.md](../release/README.md)

Reproduction should start from `experiments/` and validate against this directory.
