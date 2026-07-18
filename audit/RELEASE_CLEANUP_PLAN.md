# Release Cleanup Plan

This document records the cleanup pass for the SRP release candidate.

The goal is to reduce maintenance noise without weakening provenance, reproducibility, or claim-to-evidence traceability.

## Cleanup Principle

Cleanup should remove only low-risk noise:

- one-off smoke outputs
- temporary scratch files
- duplicate working notes that are already captured in audit records

Cleanup should preserve:

- canonical manuscript sources
- synchronized paper mirrors
- curated evidence bundles
- audit and provenance records
- compatibility wrappers required by frozen historical entrypoints

## Actions Taken

| Path | Action | Reason |
| --- | --- | --- |
| `experiments/results/external_validation_locomo_sanity_smoke4/` | deleted | one-off smoke output with no release-facing references |

## Retained by Design

The following classes remain in place because they serve a release boundary:

- `fixed.md`
- `paper/SRP_ARXIV_DRAFT_V1.md`
- `paper/SRP_PAPER_FINAL_V1.md`
- `paper/README.md`
- `artifacts/`
- `audit/`
- `audit/provenance/`
- `compatibility` wrappers under `experiments/` and `srp_experiment/`
- frozen `experiments/results/` evidence packages

## Not Removed

The following are intentionally preserved even though they contain legacy identifiers or historical structure:

- `docs/archive/`
- `paper/SRP_ABSTRACT_V1.md`
- `paper/SRP_INTRODUCTION_V1.md`
- `paper/SRP_METHOD_OVERVIEW_V1.md`
- `paper/SRP_RELATED_WORK_V1.md`
- `paper/SRP_DISCUSSION_V1.md`
- `paper/SRP_LIMITATIONS_V1.md`
- `paper/SRP_CONCLUSION_V1.md`
- `phase_*` compatibility directories and aliases
- `policy_*` compatibility aliases
- `recovery_*` compatibility aliases

These items are retained because they either support reproducibility or preserve an explicit historical boundary.

## Future Cleanup Candidates

Future cleanup should be limited to files or paths that meet at least one of these conditions:

- they are not referenced by the manuscript, audit, or release packaging layers
- they are not required for compatibility
- they are not needed for provenance
- they are obviously temporary or scratch outputs

Any future deletion should be checked against the release contract and the claim ledger before removal.

