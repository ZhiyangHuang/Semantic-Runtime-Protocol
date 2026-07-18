# SRP Artifact README

This repository is organized as a paper-facing research artifact for SRP.
The goal is to keep the main branch readable for reviewers while preserving a reproducible path to the frozen evidence chain.

## What belongs here

- `README.md`: overview and quick start
- `paper/`: paper-facing sections and results summary
- `audit/`: frozen evidence, calibration, scorer, and promotion documents
- `experiments/`: reproducible experiment runners and evaluation code
- `configs/`: frozen runtime and experiment configuration files
- `results/` or `experiments/results/`: curated evidence packages, manifests, and summaries
- `audit/provenance/docs_archive/`: historical research documents preserved for provenance

## What should stay out of the main branch

- large raw dumps that can be regenerated from scripts or upstream datasets
- temporary scratch data
- local model caches
- checkpoints and other large binaries

## Reproducibility principle

If a file can be regenerated exactly from a script, config, or upstream benchmark source, prefer keeping the regeneration path rather than storing the full raw artifact in Git.

Before tagging a release, run `python scripts/verify_release.py` to confirm that the release-facing files are present and oversized artifacts have not slipped back into the branch.

## Recommended paper-facing entry points

- `paper/SRP_PAPER_FINAL_V1.md`
- `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md`
- `audit/REAL_VALIDATION_REPORT.md`
- `audit/REAL_VALIDATION_SCIENTIFIC_REPORT.md`
- `audit/RELEASE_SNAPSHOT.md`

## Recommended evidence-generation entry points

- `python -m srp_experiment.run_governance_sensitivity`
- `python -m srp_experiment.run_transition_reconstruction`
- `python -m experiments.validation.admissibility_boundary_validation.runner`
- `python -m experiments.evaluation.transition_reconstruction_validation.runner`
- `python -m experiments.evaluation.configuration_sensitivity_validation.runner`
- `python -m experiments.evaluation.configuration_stability_validation.runner`
- `python -m experiments.evaluation.representation_invariance_validation.runner`
- `python -m experiments.evaluation.implementation_independence_validation.runner`
- `python -m experiments.evaluation.cross_domain_validation.runner`
- `python -m experiments.srp_runtime_legacy.run_governance_sensitivity`
- `python -m experiments.srp_runtime_legacy.run_transition_reconstruction`

Compatibility aliases are still present for frozen historical scripts, but the primary release-facing names are `governance_sensitivity`, `transition_reconstruction`, `admissibility_boundary_validation`, `transition_reconstruction_validation`, `configuration_sensitivity_validation`, `configuration_stability_validation`, `representation_invariance_validation`, `implementation_independence_validation`, and `cross_domain_validation`.

