# SRP Experiment Truth Audit

Commit baseline:

`60694c1` - `add artifact manifest for arxiv release package`

## Purpose

This audit checks whether the paper-facing claims in SRP are traceable to concrete experiment entry points, curated artifacts, and code paths.
It does not rerun the experiments.

## Summary

| Paper Claim | Experiment Entry | Curated Artifact | Code Path | Status |
| --- | --- | --- | --- | --- |
| Semantic state evolves only through governed transitions | `experiments/sensitivity/run_phase_i_observability.py`, `experiments/validation/phase_ii_boundary/runner.py` | `interaction_boundary_enforcement`, `phase_ii_boundary` | `srp_runtime/`, `experiments/sensitivity/`, `experiments/validation/` | PASS |
| Evidence can strengthen verification without increasing authority | `experiments/sensitivity/interaction/runner.py`, `experiments/external_validation/evidence.py` | `interaction_boundary_enforcement`, `SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md` | `srp_runtime/`, `experiments/`, legacy `srp_experiment/` helper paths | PASS |
| Validated feasible regions can constrain optimization | `experiments/optimization/run_phase_iii_a_round1.py`, `experiments/optimization/run_phase_iii_a_objective_sensitivity.py` | `phase_ii_boundary`, `phase_iii_governed_optimization`, `SRP_REVIEWABLE_REPORT_V1.md` | `srp_runtime/`, `experiments/optimization/`, `experiments/validation/` | PASS |
| SRP runtime is independent from evaluation infrastructure | `scripts/verify_release.py`, static dependency scans | `SRP_EXPERIMENT_DEPENDENCY_MAP.md`, `REPO_ARCHITECTURE_BLUEPRINT.md`, `SRP_V1_STATIC_AUDIT_MAPPING.md` | `srp_runtime/`, `experiments/`, `srp_experiment/` (legacy only) | PASS |
| SRP evaluations are reproducible under frozen contracts | `experiments/evaluation/run_phase_v_retention.py`, `experiments/evaluation/run_longmemeval_evidence.py`, `experiments/evaluation/run_longmemeval_scorer_alignment_audit.py` | `phase_v_retention`, `semantic_backend_comparison`, `external_validation`, `artifacts/MANIFEST.md` | `experiments/evaluation/`, `experiments/external_validation/`, `artifacts/` | PASS |
| Recovery is an implementation case, not the definition of SRP | `experiments/evaluation/run_phase_vi_relation_recovery.py`, `experiments/evaluation/run_phase_vii_parameter_stability.py`, `experiments/evaluation/run_phase_vii_parameter_sensitivity.py` | `phase_v_retention`, `phase_vi_relation_recovery`, `phase_vii_parameter_stability`, `phase_vii_parameter_sensitivity` | `experiments/evaluation/` | PASS |

## Traceability Notes

- The current release branch provides a clear chain from paper claim to audit ledger to artifact bundle to implementation entry point.
- `srp_runtime/` remains the source of runtime semantics.
- `experiments/` remains the evidence-generation layer.
- `artifacts/` remains the curated release-facing evidence layer.
- `srp_experiment/` is intentionally retained as a frozen legacy evidence layer and appears only in the dependency chain where legacy helper code is still required.

## Reproducibility Boundary

This audit confirms traceability and curated evidence integrity.
It does not claim full end-to-end reproducibility from a blank machine without frozen environment and dependency-lock artifacts.

## Conclusion

SRP claims are presently auditable and backed by concrete experiments and curated artifacts.
The remaining reproducibility gap is packaging-level environment freezing, not a missing evidence chain.
