# Evidence Policy

This policy defines the release-facing evidence tiers used in the current SRP snapshot.

## Main

Main evidence directly supports paper-facing claims.

Main evidence must have:

- a generated report
- a machine-readable JSON summary
- metadata or integrity records
- a frozen claim boundary

Main evidence is cited through `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` and the canonical manuscript.

## Appendix

Appendix evidence supports the paper but should not carry the main claim alone.

Appendix evidence may include calibration slices, supporting diagnostics, and implementation instances.

## Archive

Archive evidence is retained for provenance only.
It may document historical milestones, superseded reviews, or older release branches.

## Promotion Rule

Only evidence that can be regenerated from the frozen release boundary should be promoted to the paper-facing summary.

If a result is superseded by a newer release summary, the older result becomes archive material.
