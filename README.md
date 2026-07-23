# Semantic Runtime Protocol

SRP is a semantic runtime governance framework that controls the admissibility of semantic state transitions through explicit validation, evidence, and authorization boundaries.

This repository is organized around a small set of decoupled layers:

- `fixed.md` is the canonical manuscript source for the current release pass.
- `paper/` holds the synchronized manuscript mirror and release snapshot.
- `srp_runtime/` holds the active runtime implementation.
- `experiments/` holds reproducible validation and evidence-generation entrypoints.
- `artifacts/` holds curated evidence bundles.
- `arxiv_package/` holds submission packaging only.
- `audit/` holds the current release records, the claim map, and provenance.
- `experiments/compatibility/` holds compatibility code only.
- `configs/` holds frozen runtime and validation configurations.
- `scripts/` holds release tooling.

## Primary Terminology

The repository now prefers paper-aligned terminology in active entrypoints:

- `governance_sensitivity` is the primary name for sensitivity analysis over governance boundaries and authorization behavior.
- `transition_reconstruction` is the primary name for reconstruction-focused implementation instances under SRP.

Compatibility aliases remain available only so historical scripts do not break:

- `recovery`-named entrypoints remain as compatibility aliases for `transition_reconstruction`

## Start Here

1. Read the canonical manuscript source: [fixed.md](fixed.md)
2. Read the release snapshot: [paper/SRP_PAPER_FINAL_V1.md](paper/SRP_PAPER_FINAL_V1.md)
3. Read the paper-facing summary: [paper/SRP_MAIN_RESULTS_SUMMARY_V1.md](paper/SRP_MAIN_RESULTS_SUMMARY_V1.md)
4. Read the audit entry point: [audit/README.md](audit/README.md)
5. Read the current release summary: [audit/CURRENT_RELEASE.md](audit/CURRENT_RELEASE.md)
6. Read the evidence policy: [audit/EVIDENCE_POLICY.md](audit/EVIDENCE_POLICY.md)
7. Read the claim ledger: [audit/CLAIM_EVIDENCE_MAP.md](audit/CLAIM_EVIDENCE_MAP.md)
8. Read the real-validation report: [audit/REAL_VALIDATION_REPORT.md](audit/REAL_VALIDATION_REPORT.md)
9. Review the release checklist and verification:
   - [audit/RELEASE_CHECKLIST.md](audit/RELEASE_CHECKLIST.md)
   - [audit/VERIFY_REPORT.md](audit/VERIFY_REPORT.md)

## Recommended Entry Points

- `python -m experiments.validation.admissibility_boundary_validation.runner`
- `python -m experiments.evaluation.transition_reconstruction_validation.runner`
- `python -m experiments.evaluation.configuration_sensitivity_validation.runner`
- `python -m experiments.evaluation.configuration_stability_validation.runner`
- `python -m experiments.evaluation.representation_invariance_validation.runner`
- `python -m experiments.evaluation.implementation_independence_validation.runner`
- `python -m experiments.evaluation.cross_domain_validation.runner`
- `python -m experiments.compatibility.run_governance_sensitivity`
- `python -m experiments.compatibility.run_transition_reconstruction`

Historical aliases remain available for compatibility only, and the primary release-facing names now also include `representation_invariance_validation`, `implementation_independence_validation`, and `cross_domain_validation`:
- `python -m experiments.validation.phase_ii_boundary.runner`
- `python -m experiments.evaluation.phase_vi_relation_recovery.runner`
- `python -m experiments.evaluation.phase_vii_parameter_sensitivity.runner`
- `python -m experiments.evaluation.phase_vii_parameter_stability.runner`
- `python -m experiments.evaluation.phase_viii_representation_invariance.runner`
- `python -m experiments.evaluation.phase_viii_implementation_independence.runner`
- `python -m experiments.evaluation.phase_viii_cross_domain.runner`

## Auxiliary Reproducibility Entry Points

These support the release evidence bundle and calibration history, but they are not part of the trimmed paper-facing regeneration flow:

- `python experiments/evaluation/run_locomo_manual_sanity.py`
- `python experiments/external_validation/calibration_report.py`
- `python experiments/evaluation/run_longmemeval_evidence.py`
- `python experiments/evaluation/run_longmemeval_scorer_alignment_audit.py`

## Release Verification

Run the release hygiene check before tagging or pushing a release branch:

```bash
python scripts/verify_release.py
```

## Reproducibility

The repo includes frozen configs, reproducible validation entrypoints, and a compact reviewer-facing audit surface. If something can be regenerated exactly from code and configuration, prefer the regeneration path over storing a raw dump in Git.

For benchmark suites, this release uses a registry-based policy: the repository keeps manifests, sample definitions, adapters, and results, while benchmark payloads remain with the original sources.

## Benchmark Release Surface

The release-facing benchmark entry points are now organized under:

- `docs/benchmarks/` for the canonical benchmark reports
- `docs/release/` for the current release evidence review
- `docs/archive/benchmark_history/` for planning, smoke, and iteration history
