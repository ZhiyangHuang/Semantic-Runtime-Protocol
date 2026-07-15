# Semantic Runtime Protocol

SRP is a semantic runtime protocol for evolving semantic state through explicit transitions, constraints, traces, replay, and governed commitment.

This repository is organized as an arXiv-facing artifact branch:

- `paper/` holds the paper-facing manuscript sections and results summary.
- `audit/` holds the frozen evidence, calibration, scorer, and promotion documents.
- `srp_runtime/` holds the core runtime implementation.
- `srp_experiment/` holds the legacy measurement and runtime evidence stack.
- `experiments/` holds reproducible experiment and evaluation entrypoints.
- `configs/` holds frozen runtime and experiment configurations.
- `scripts/` holds release tooling.
- `docs/archive/` holds historical research documents that are not needed in the main release path.

## Start Here

1. Read the paper-facing summary: [paper/SRP_MAIN_RESULTS_SUMMARY_V1.md](paper/SRP_MAIN_RESULTS_SUMMARY_V1.md)
2. Read the final manuscript: [paper/SRP_PAPER_FINAL_V1.md](paper/SRP_PAPER_FINAL_V1.md)
3. Read the release artifact guide: [ARTIFACT_README.md](ARTIFACT_README.md)
4. Read the evidence audit spec: [audit/SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md](audit/SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md)
5. Review the LongMemEval evidence gate:
   - [audit/SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md](audit/SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md)
   - [audit/SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md](audit/SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md)
   - [audit/SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md](audit/SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md)

## Release Verification

Run the release hygiene check before tagging or pushing a release branch:

```bash
python scripts/verify_release.py
```

## Reproducibility

The repo includes frozen configs, reproducible experiment entrypoints, and promoted evidence manifests. If something can be regenerated exactly from code and configuration, prefer the regeneration path over storing a raw dump in Git.
