# SRP Artifact README

This repository is organized as a paper-facing research artifact for SRP.
The goal is to keep the main branch readable for reviewers while preserving a reproducible path to the frozen evidence chain.

## What belongs here

- `README.md`: overview and quick start
- `SRP_*.md`: paper sections, audit notes, evidence summaries, and frozen methodology documents
- `experiments/`: reproducible experiment runners and evaluation code
- `configs/`: frozen runtime and experiment configuration files
- `results/` or `experiments/results/`: curated evidence packages, manifests, and summaries

## What should stay out of the main branch

- large raw dumps that can be regenerated from scripts or upstream datasets
- temporary scratch data
- local model caches
- checkpoints and other large binaries

## Reproducibility principle

If a file can be regenerated exactly from a script, config, or upstream benchmark source, prefer keeping the regeneration path rather than storing the full raw artifact in Git.

Before tagging a release, run `python scripts/verify_release.py` to confirm that the release-facing files are present and oversized artifacts have not slipped back into the branch.

## Recommended paper-facing entry points

- `SRP_PAPER_FINAL_V1.md`
- `SRP_MAIN_RESULTS_SUMMARY_V1.md`
- `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md`
- `SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md`
- `SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md`
