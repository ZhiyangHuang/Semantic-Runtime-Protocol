# SRP Release Checklist

This checklist verifies that an SRP release preserves architectural boundaries, evidence traceability, and reproducible evaluation.

A release is valid only when implementation, evaluation evidence, artifact governance, and audit records remain consistent.

## 1. Repository Boundary Validation

### Runtime Isolation

- [ ] `srp_runtime/` does not depend on `experiments/`
- [ ] `srp_runtime/` does not depend on `artifacts/`
- [ ] `srp_runtime/` does not depend on `audit/`

### Dependency Direction

Expected flow:

```text
srp_runtime
    |
    v
experiments
    |
    v
artifacts
    |
    v
audit
```

Forbidden flows:

- `experiments` mutating runtime state
- `runtime` depending on evaluation or audit logic
- `audit` redefining runtime semantics

## 2. Core Runtime Validation

### Implementation Integrity

- [ ] `srp_runtime/` contains the current protocol implementation
- [ ] transition logic exists only in the runtime layer
- [ ] governance checks are not duplicated as alternate runtime sources in `experiments/`

### Mechanical Verification

Run:

```bash
python scripts/verify_release.py
```

Expected:

- `CORE_REQUIRED_PATHS` pass
- legacy evidence checks are explicitly labeled and intentional

## 3. Evidence Validation

### Claim Coverage

For every `Main` claim in `audit/CLAIM_EVIDENCE_MAP.md`:

- [ ] a mechanism is identified
- [ ] an evidence source is identified
- [ ] an artifact reference exists

For every `Appendix` claim:

- [ ] the evidence scope is explicitly bounded
- [ ] the claim is not promoted beyond its supported status

### Evidence Consistency

- [ ] the paper-facing claim language matches the claim ledger
- [ ] evidence strength is not overstated in release notes
- [ ] claims do not silently expand beyond the frozen contract

## 4. Artifact Validation

For every approved artifact bundle:

- [ ] artifact location is under `artifacts/`
- [ ] artifact is listed in `audit/ARTIFACT_PROMOTION_DECISION.md`
- [ ] the bundle contains exactly `report.md`, `summary.json`, and `metadata.json`
- [ ] provenance metadata exists
- [ ] generation process is documented
- [ ] the frozen contract is identified
- [ ] the artifact is referenced by audit documents
- [ ] `report.md` and `summary.json` are consistent with the approved source evidence
- [ ] `metadata.json` contains sufficient provenance fields for release traceability

Reference:

- `audit/ARTIFACT_POLICY.md`

## 5. Experiment Validation

### Evaluation Layer

- [ ] `experiments/` is treated as an evidence generator
- [ ] `experiments/` does not define runtime behavior
- [ ] benchmark adapters remain isolated from runtime implementation
- [ ] report and runner code only produce or package evidence

### Legacy Layer

- [ ] `srp_experiment/` remains frozen as legacy evidence and compatibility support
- [ ] no new runtime logic is added there
- [ ] legacy files are not relabeled as current runtime source of truth

## 6. Reproducibility Validation

Before release, each promoted artifact should answer:

### What was evaluated?

- experiment identifier
- evaluation phase
- benchmark or workload slice

### How was it generated?

- command
- configuration
- runtime contract

### Which claim does it support?

- claim reference from `audit/CLAIM_EVIDENCE_MAP.md`

### Can it be regenerated?

- frozen contract is available
- inputs are fully specified
- provenance metadata is present

## 7. Paper Artifact Validation

Before release:

- [ ] paper claims match evidence
- [ ] evidence matches artifacts
- [ ] artifacts match repository state
- [ ] no unsupported claims are promoted to `Main`
- [ ] Appendix-grade evidence is not presented as release-grade main evidence

## 8. Promotion Consistency

- [ ] every promoted artifact is approved in `audit/ARTIFACT_PROMOTION_DECISION.md`
- [ ] no unapproved artifact is treated as release evidence
- [ ] `experiments/results/` remains the reproducibility source
- [ ] `artifacts/` contains curated evidence only

## 9. Release Packaging

- [ ] release notes list the frozen claim set
- [ ] release notes list the curated artifact set
- [ ] release notes identify the frozen runtime contract
- [ ] release notes identify any legacy evidence that remains in scope
- [ ] release notes do not imply a broader claim than the evidence supports

## 10. Final Release Decision

Release status:

- [ ] PASS
- [ ] BLOCKED

Blocking issues:

- 

## 11. Governance Rule

This checklist is a repository integrity checker, not a scientific validity judge.

- `verify_release.py` checks mechanical consistency
- `CLAIM_EVIDENCE_MAP.md` governs claim-to-evidence meaning
- `ARTIFACT_POLICY.md` governs evidence lifecycle
- `REPO_ARCHITECTURE_BLUEPRINT.md` governs layer boundaries

All four documents must agree for a release candidate to be considered structurally valid.

