# SRP Claim Evidence Map

This document maps SRP's paper-facing claims to implementation mechanisms, evaluation evidence, and reproducible artifacts.
It is the release branch claim ledger.

The mapping follows the repository architecture contract:

- `srp_runtime/` provides the protocol mechanism
- `experiments/` generates evaluation evidence
- `artifacts/` stores curated evidence bundles
- `audit/` governs claim status and provenance

The key principle is that an experiment is evidence for a claim, not the claim itself.

## Claim 1: Semantic State Evolves Only Through Governed Transitions

### Claim

SRP governs semantic state evolution through validated boundaries, separate authority checks, and explicit transition approval.

### Mechanism

- Semantic runtime state is modeled as content, provenance, and authority context.
- Transition validity is separated from transition authorization.
- Recommendation is distinct from execution.
- Rejected transitions preserve state.

### Evidence

- Formal model in `paper/SRP_ARXIV_DRAFT_V1.md`, Method
- Transition pipeline and authority separation in `paper/SRP_ARXIV_DRAFT_V1.md`, Sections 3.3-3.7
- Boundary validation and negative transition injection in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 4.1

### Artifacts

- `interaction_boundary_enforcement`
- `phase_ii_boundary`
- `SRP_REVIEWABLE_REPORT_V1.md`
- `SRP_V1_STATIC_AUDIT_MAPPING.md`

### Status

Main

## Claim 2: Evidence Can Strengthen Verification Without Increasing Authority

### Claim

Additional semantic evidence can improve verification outcomes without transferring execution authority.

### Mechanism

- Evidence is consumed by verification.
- Authority is controlled by governance policy.
- Evidence availability and authority are modeled as independent variables.
- Stronger evidence may improve confidence but does not authorize mutation by itself.

### Evidence

- Proposition 1 in `paper/SRP_ARXIV_DRAFT_V1.md`
- Evidence-controlled governance results in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 4.1
- Discussion framing in `paper/SRP_ARXIV_DRAFT_V1.md`, Sections 5.1 and 7

### Artifacts

- `interaction_boundary_enforcement`
- `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md`
- `SRP_V1_STATIC_AUDIT_MAPPING.md`
- `SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md`

### Status

Main

## Claim 3: Validated Feasible Regions Can Constrain Optimization

### Claim

SRP identifies evaluated feasible regions and performs constrained optimization only inside those regions.

### Mechanism

- Candidate parameters are filtered by invariants and closure checks.
- Optimization runs inside the validated feasible region.
- Recommendation is produced separately from authorization.

### Evidence

- Feasible region definition in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 3.2
- Algorithmic core in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 3.5
- Constrained optimization results in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 4.1
- Parameter sensitivity discussion in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 4.3

### Artifacts

- `phase_ii_boundary`
- `phase_ii_boundary_generalization`
- `phase_iii_governed_optimization`
- `SRP_REVIEWABLE_REPORT_V1.md`

### Status

Appendix

## Claim 4: SRP Runtime Is Independent From Evaluation Infrastructure

### Claim

The active SRP runtime does not depend on the evaluation infrastructure, and `srp_experiment/` is a legacy evidence layer rather than the source of truth for runtime semantics.

### Mechanism

- Runtime code is separated from experiments and audit materials.
- Evaluation packages may depend on runtime, but runtime should not depend on evaluation packages.
- `srp_experiment/` is treated as historical evidence and compatibility support.

### Evidence

- Static dependency map in `audit/SRP_EXPERIMENT_DEPENDENCY_MAP.md`
- Repository architecture contract in `audit/REPO_ARCHITECTURE_BLUEPRINT.md`
- Release verification structure in `scripts/verify_release.py`
- Repository framing in `README.md`

### Artifacts

- `SRP_EXPERIMENT_DEPENDENCY_MAP.md`
- `REPO_ARCHITECTURE_BLUEPRINT.md`
- `SRP_V1_STATIC_AUDIT_MAPPING.md`
- `README.md`

### Status

Main

## Claim 5: SRP Evaluations Are Reproducible Under Frozen Contracts

### Claim

SRP evaluations can be reproduced through frozen cases, fixed runtime contracts, and curated evidence bundles.

### Mechanism

- Evaluation cases are frozen.
- Runtime contracts are frozen.
- Metrics, reports, manifests, and traces are emitted as structured evidence.
- External validation keeps the generation backend and scorer boundaries explicit.

### Evidence

- Evaluation structure in `paper/SRP_ARXIV_DRAFT_V1.md`, Sections 4.4 and 4.5
- Retention evaluation report in `paper/SRP_ARXIV_DRAFT_V1.md`, Appendix A
- External validation evidence description in `paper/SRP_ARXIV_DRAFT_V1.md`, Section 4.5
- LongMemEval evidence report in `audit/SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md`
- External validation audit specification in `audit/SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md`

### Artifacts

- `SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md`
- `SRP_EXTERNAL_VALIDATION_REPORT.md`
- `SRP_EXTERNAL_VALIDATION_ADAPTER_CALIBRATION_NOTE.md`
- `SRP_EXTERNAL_VALIDATION_LOCOMO_CALIBRATION_AWARE_REPORT.md`
- `SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md`
- `SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md`

### Status

Appendix

## Claim 6: Recovery Is an Implementation Case, Not the Definition of SRP

### Claim

Semantic recovery and reconstruction are governed transition implementations used to evaluate SRP, not the framework definition itself.

### Mechanism

- Recovery is treated as one possible transition implementation under SRP.
- The framework remains broader than any single recovery method.
- Recovery outcomes are used to test governance properties such as coverage, drift, and hallucination control.

### Evidence

- `paper/SRP_ARXIV_DRAFT_V1.md`, Sections 4.2 and 5.1
- `paper/SRP_ARXIV_DRAFT_V1.md`, Conclusion
- `paper/SRP_PAPER_FINAL_V1.md` if kept as the finalized narrative mirror

### Artifacts

- `phase_v_retention`
- `phase_vi_relation_recovery`
- `phase_vii_parameter_stability`
- `phase_vii_parameter_sensitivity`

### Status

Appendix

## Claim-to-Evidence Summary

| Claim | Mechanism Layer | Evidence Layer | Primary Artifact Layer | Status |
| --- | --- | --- | --- | --- |
| Governed semantic evolution | `srp_runtime/` | Experiments + paper results | Main artifacts | Main |
| Evidence-controlled verification | `srp_runtime/` + governance | Boundary and evidence experiments | Main + appendix artifacts | Main |
| Validated feasible region optimization | `srp_runtime/optimization/` | Phase II / III experiments | Appendix artifacts | Appendix |
| Runtime independence from evaluation infrastructure | repository boundary contract | dependency analysis + release verification | audit docs | Main |
| Reproducible evaluation under frozen contracts | evaluation layer | external validation + retention + observability | evidence bundles | Appendix |
| Recovery as implementation case | evaluation layer | recovery experiments | appendix artifacts | Appendix |

## Notes

- `Main` means the claim is directly supported by the current release snapshot.
- `Appendix` means the claim is supported, but primarily as scoped or supporting evidence.
- `Archive` means the material is retained for provenance, not for paper-facing claim promotion.

The current ledger is intentionally conservative.
When a claim depends on a frozen artifact bundle, the artifact must be cited explicitly in the corresponding audit or paper-facing release note.

