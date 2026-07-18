# Semantic Runtime Protocol

SRP is a semantic runtime protocol for evolving semantic state through explicit transitions, constraints, traces, replay, and governed commitment.

This repository is organized around a small set of decoupled layers:

- `fixed.md` is the canonical manuscript source for the current release pass.
- `paper/` holds the synchronized manuscript mirror, release snapshot, and supporting reconstruction notes.
- `srp_runtime/` holds the active runtime implementation.
- `experiments/` holds reproducible validation and evidence-generation entrypoints.
- `artifacts/` holds curated evidence bundles.
- `arxiv_package/` holds submission packaging only.
- `audit/` holds claims, evidence maps, release rules, and provenance.
- `srp_experiment/` holds legacy compatibility and historical evidence only.
- `configs/` holds frozen runtime and validation configurations.
- `scripts/` holds release tooling.

## Primary Terminology

The repository now prefers paper-aligned terminology in active entrypoints:

- `governance_sensitivity` is the primary name for sensitivity analysis over governance boundaries and authorization behavior.
- `transition_reconstruction` is the primary name for reconstruction-focused implementation instances under SRP.

Compatibility aliases remain available only so historical scripts do not break:

- `policy_sensitivity` remains as a compatibility alias for `governance_sensitivity`
- `recovery`-named entrypoints remain as compatibility aliases for `transition_reconstruction`

## Start Here

1. Read the canonical manuscript source: [fixed.md](fixed.md)
2. Read the release snapshot: [paper/SRP_PAPER_FINAL_V1.md](paper/SRP_PAPER_FINAL_V1.md)
3. Read the paper-facing summary: [paper/SRP_MAIN_RESULTS_SUMMARY_V1.md](paper/SRP_MAIN_RESULTS_SUMMARY_V1.md)
4. Read the repository contract: [audit/REPO_CONTRACT.md](audit/REPO_CONTRACT.md)
5. Read the migration plan: [audit/REPOSITORY_ARCHITECTURE_MIGRATION_PLAN.md](audit/REPOSITORY_ARCHITECTURE_MIGRATION_PLAN.md)
6. Read the release artifact guide: [ARTIFACT_README.md](ARTIFACT_README.md)
7. Review the 7/18 real-validation evidence:
   - [audit/REAL_VALIDATION_REPORT.md](audit/REAL_VALIDATION_REPORT.md)
   - [audit/REAL_VALIDATION_SCIENTIFIC_REPORT.md](audit/REAL_VALIDATION_SCIENTIFIC_REPORT.md)
8. Review the release boundary:
   - [audit/RELEASE_SNAPSHOT.md](audit/RELEASE_SNAPSHOT.md)
   - [audit/RELEASE_PDF_VISUAL_AUDIT.md](audit/RELEASE_PDF_VISUAL_AUDIT.md)

## Recommended Entry Points

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

Historical aliases remain available for compatibility only, and the primary release-facing names now also include `representation_invariance_validation`, `implementation_independence_validation`, and `cross_domain_validation`:

- `python -m srp_experiment.run_policy_sensitivity`
- `python -m srp_experiment.run_reconstruction_policy_comparison`
- `python -m experiments.validation.phase_ii_boundary.runner`
- `python -m experiments.evaluation.phase_vi_relation_recovery.runner`
- `python -m experiments.evaluation.phase_vii_parameter_sensitivity.runner`
- `python -m experiments.evaluation.phase_vii_parameter_stability.runner`
- `python -m experiments.evaluation.phase_viii_representation_invariance.runner`
- `python -m experiments.evaluation.phase_viii_implementation_independence.runner`
- `python -m experiments.evaluation.phase_viii_cross_domain.runner`
- `python -m experiments.srp_runtime_legacy.run_policy_sensitivity`
- `python -m experiments.srp_runtime_legacy.run_reconstruction_policy_comparison`

## Release Verification

Run the release hygiene check before tagging or pushing a release branch:

```bash
python scripts/verify_release.py
```

## Reproducibility

The repo includes frozen configs, reproducible validation entrypoints, and promoted evidence manifests. If something can be regenerated exactly from code and configuration, prefer the regeneration path over storing a raw dump in Git.

