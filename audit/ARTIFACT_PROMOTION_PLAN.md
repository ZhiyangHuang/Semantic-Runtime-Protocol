# SRP Artifact Promotion Plan

This document records the first curated promotion decision for release-facing artifacts.

It is intentionally small. Raw experiment outputs remain under `experiments/results/`, and only the minimal evidence set is considered for promotion.

Promotion requires:

- claim linkage from `audit/CLAIM_EVIDENCE_MAP.md`
- reproducible generation under a frozen contract
- provenance completeness

## Principle

Only minimal curated artifacts are promoted.

Promotion does not remove the original experiment outputs.
It creates a release-facing evidence set that can be cited and audited.

## 1. Phase V Retention

### Source

```text
experiments/results/phase_v_retention/
```

### Promote

| Artifact | Reason | Claim |
| --- | --- | --- |
| `retention_report.md` | Human-readable evidence report with frozen protocol, summary, and per-case results. | Semantic fidelity after governed transition |
| `retention_summary.json` | Machine-readable metric summary for audit and reproduction. | Semantic fidelity after governed transition |
| `metadata.json` | Provenance and generation metadata required for release traceability. | Reproducibility under frozen contract |

### Keep in `experiments/results/`

| Output | Reason |
| --- | --- |
| raw traces, if regenerated later | Useful for debugging and reproduction, but not required for the minimal release-facing bundle. |
| intermediate dumps, if any appear later | Temporary evaluation output, not curated evidence. |

## 2. Semantic Backend Comparison

### Source

```text
experiments/results/semantic_backend_comparison/
```

### Promote

| Artifact | Reason | Claim |
| --- | --- | --- |
| `comparison_report.md` | Human-readable comparison report describing the escalation boundary and authority preservation. | Evidence can strengthen verification without increasing authority |
| `comparison_summary.json` | Machine-readable comparison summary with agreement, escalation, and authority metrics. | Evidence can strengthen verification without increasing authority |
| `metadata.json` | Provenance and generation metadata required for release traceability. | Reproducibility under frozen contract |

### Keep in `experiments/results/`

| Output | Reason |
| --- | --- |
| any raw backend traces | Helpful for local inspection, but not necessary for the minimal promoted bundle. |
| any fallback/debug output | Transient evaluation output. |

## 3. External Validation

### Source

```text
experiments/results/external_validation/
```

### Promote

| Artifact | Reason | Claim |
| --- | --- | --- |
| `external_validation_report.md` | Release-facing evidence report with benchmark summary, baseline summary, and failure summary. | Reproducible evaluation under frozen contracts |
| `external_validation_summary.json` | Machine-readable external-validation summary for audit and reproduction. | Reproducible evaluation under frozen contracts |
| `metadata.json` | Provenance and generation metadata required for release traceability. | Reproducibility under frozen contract |

### Keep in `experiments/results/`

| Output | Reason |
| --- | --- |
| benchmark traces and intermediate run material | Useful for inspection, but not part of the minimal release-facing set. |
| debug dumps, if any are present or regenerated later | Transient output. |

## 4. Promotion Set Summary

### Recommended First Batch

The first release-facing artifact set should be limited to:

- `phase_v_retention`
- `semantic_backend_comparison`
- `external_validation`

For each promoted package, prefer the following minimal bundle:

- report
- summary
- provenance metadata

### Not Promoted Yet

- raw traces
- debug dumps
- intermediate run caches
- one-off inspection output

## 5. Claim Alignment

This promotion plan currently supports the following claim groups:

- semantic fidelity after governed transition
- evidence-controlled verification without authority transfer
- reproducible external validation under frozen contracts

The promoted set should remain aligned with `audit/CLAIM_EVIDENCE_MAP.md`.
If a candidate artifact cannot be traced to a claim, it should not be promoted.

## 6. Release Boundary Reminder

Promotion is not migration of the whole `experiments/results/` tree.

It is a curated copy of the smallest evidence set needed to support the current release claims.

The original experiment outputs remain in place to preserve reproducibility and inspection value.

