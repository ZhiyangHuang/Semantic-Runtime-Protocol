# SRP Artifact Candidate Map

This document classifies current evaluation outputs by release usefulness.
It is a classification record, not a migration plan.

The goal is to decide what may later be promoted into `artifacts/`, what should remain under `experiments/results/`, and what should be treated as transient output.

## Classification Rules

### Curated Evidence Candidate

An output may be promoted into `artifacts/` if it:

- supports a claim in `audit/CLAIM_EVIDENCE_MAP.md`
- has a clear generation entry point
- includes provenance or can be paired with provenance
- is not a one-off scratch dump

### Reproducibility Output

An output should remain under `experiments/results/` if it:

- helps reproduce the evaluation
- is useful for debugging or inspection
- is not yet curated into a release-facing bundle

### Transient Output

An output should remain non-release if it:

- is a raw dump
- is a debug trace or cache
- lacks provenance or stable interpretation

## Scope of First-Pass Review

This first pass covers the three result regions currently aligned with the claim map:

- `experiments/results/phase_v_retention/`
- `experiments/results/semantic_backend_comparison/`
- `experiments/results/external_validation/`

## 1. `phase_v_retention`

### Current Location

```text
experiments/results/phase_v_retention/
```

### Purpose

Retention evaluation evidence for semantic fidelity after governed transition.

### Observed Outputs

| Output | Category | Decision | Reason |
| --- | --- | --- | --- |
| `retention_report.md` | Curated Evidence Candidate | promote | Human-readable evidence report with frozen protocol, summary, and per-case results. |
| `retention_summary.json` | Curated Evidence Candidate | promote | Machine-readable summary with provenance-friendly metrics. |

### Claim Linkage

- semantic retention and drift after governed transition
- recovery evaluation as an implementation case

### Notes

- The report is already framed as an evaluation report, not a calibration artifact.
- The summary is stable, compact, and directly supports paper-facing interpretation.
- No raw trace or debug dump was identified in this first-pass scan.

## 2. `semantic_backend_comparison`

### Current Location

```text
experiments/results/semantic_backend_comparison/
```

### Purpose

Evidence for boundary escalation between vector-only evidence and local-model evidence.

### Observed Outputs

| Output | Category | Decision | Reason |
| --- | --- | --- | --- |
| `comparison_report.md` | Curated Evidence Candidate | promote | Human-readable comparison report with evaluation boundary, authority preservation, and escalation results. |
| `comparison_summary.json` | Curated Evidence Candidate | promote | Machine-readable summary of comparison outcomes and authority-preservation results. |

### Claim Linkage

- evidence can strengthen verification without increasing authority
- runtime remains isolated from evaluation infrastructure
- local-model evidence is an evidence provider, not a controller

### Notes

- The report already states that runtime and optimization are fixed.
- The summary captures the key boundary metrics directly.
- No raw trace or debug dump was identified in this first-pass scan.

## 3. `external_validation`

### Current Location

```text
experiments/results/external_validation/
```

### Purpose

External validation evidence for benchmark-level reproducibility and comparison.

### Observed Outputs

| Output | Category | Decision | Reason |
| --- | --- | --- | --- |
| `external_validation_report.md` | Curated Evidence Candidate | promote | Release-facing evidence report with frozen scope, benchmark summary, baseline summary, and failure summary. |
| `external_validation_summary.json` | Curated Evidence Candidate | promote | Machine-readable summary of the external-validation evidence bundle. |

### Claim Linkage

- reproducible evaluation under frozen contracts
- paper-facing external validation support
- claim-evidence traceability for external validation

### Notes

- The report already frames the bundle as evidence, not calibration.
- The summary is compact and directly useful for audit references.
- No raw trace or debug dump was identified in this first-pass scan.

## 4. Cross-Directory Summary

### Curated Evidence Candidates

| Output Group | Decision |
| --- | --- |
| `phase_v_retention` report + summary | promote |
| `semantic_backend_comparison` report + summary | promote |
| `external_validation` report + summary | promote |

### Reproducibility Outputs

At present, no additional reproducibility-only subtrees were identified in the three scanned locations.

### Transient Outputs

At present, no explicit transient files were identified in the first-pass scan of these three directories.

## 5. Promotion Guidance

The outputs above are candidates only.
Promotion into `artifacts/` should happen only if:

- the linked claim exists in `audit/CLAIM_EVIDENCE_MAP.md`
- the frozen contract is explicit
- the output is stable enough to cite
- the artifact package can carry provenance metadata

If an output is promoted, it should remain a curated evidence package rather than becoming a general-purpose results dump.

## 6. Boundary Reminder

`experiments/` explains how evidence is generated.
`artifacts/` defines what evidence is released.
`audit/` explains why the evidence matters.

This document only classifies candidates.
It does not move files and it does not alter runtime behavior.

