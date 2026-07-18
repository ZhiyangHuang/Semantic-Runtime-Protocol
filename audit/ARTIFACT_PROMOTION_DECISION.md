# SRP Artifact Promotion Decision

This document finalizes the first curated promotion decision for release-facing artifacts.

It converts the promotion plan into a bounded release decision.
The decision is conservative: only the minimal release-facing evidence set is approved, and the original experiment outputs remain in place under `experiments/results/` for reproducibility and inspection.

## Decision Summary

- Approved for curated promotion: yes
- Scope: minimal release-facing evidence bundles only
- Source of truth for claim linkage: `audit/CLAIM_EVIDENCE_MAP.md`
- Source of truth for artifact lifecycle: `audit/ARTIFACT_POLICY.md`

## Evidence Status Legend

- `release evidence`: curated artifact approved for release-facing use
- `provenance`: metadata needed to trace generation and reproduce the artifact
- `reproduction only`: useful for inspection and rerun support, but not part of the curated release bundle
- `excluded`: transient or non-release output

## 1. Phase V Retention

### Source

```text
experiments/results/phase_v_retention/
```

### Claim Linkage

- semantic retention after governed transition
- recovery evaluation as an implementation case

### Decision

| Artifact | Destination | Evidence Status | Reason |
| --- | --- | --- | --- |
| `retention_report.md` | `artifacts/phase_v_retention/` | `release evidence` | Human-readable evidence report with frozen protocol, summary, and per-case results. |
| `retention_summary.json` | `artifacts/phase_v_retention/` | `release evidence` | Machine-readable quantitative summary for audit and reproduction. |
| `metadata.json` | `artifacts/phase_v_retention/` | `provenance` | Required to trace generation configuration, versioning, and runtime context. |

### Kept in `experiments/results/`

| Artifact | Evidence Status | Reason |
| --- | --- | --- |
| raw traces, if present or regenerated later | `reproduction only` | Useful for rerun inspection and debugging, but not required in the curated release bundle. |
| intermediate dumps, if present later | `excluded` | Temporary evaluation output. |

## 2. Semantic Backend Comparison

### Source

```text
experiments/results/semantic_backend_comparison/
```

### Claim Linkage

- evidence can strengthen verification without increasing authority
- runtime remains isolated from evaluation infrastructure
- local-model evidence is an evidence provider, not a controller

### Decision

| Artifact | Destination | Evidence Status | Reason |
| --- | --- | --- | --- |
| `comparison_report.md` | `artifacts/semantic_backend_comparison/` | `release evidence` | Human-readable comparison report that captures the escalation boundary and authority preservation result. |
| `comparison_summary.json` | `artifacts/semantic_backend_comparison/` | `release evidence` | Machine-readable comparison summary for audit and reproduction. |
| `metadata.json` | `artifacts/semantic_backend_comparison/` | `provenance` | Required to trace generation configuration, versioning, and runtime context. |

### Kept in `experiments/results/`

| Artifact | Evidence Status | Reason |
| --- | --- | --- |
| backend traces, if present or regenerated later | `reproduction only` | Useful for inspection and rerun support. |
| fallback/debug output | `excluded` | Transient evaluation output. |

## 3. External Validation

### Source

```text
experiments/results/external_validation/
```

### Claim Linkage

- reproducible evaluation under frozen contracts
- paper-facing external validation support
- claim-evidence traceability for external validation

### Decision

| Artifact | Destination | Evidence Status | Reason |
| --- | --- | --- | --- |
| `external_validation_report.md` | `artifacts/external_validation/` | `release evidence` | Release-facing evidence report with benchmark summary, baseline summary, and failure summary. |
| `external_validation_summary.json` | `artifacts/external_validation/` | `release evidence` | Machine-readable summary for audit and reproduction. |
| `metadata.json` | `artifacts/external_validation/` | `provenance` | Required to trace generation configuration, versioning, and runtime context. |

### Kept in `experiments/results/`

| Artifact | Evidence Status | Reason |
| --- | --- | --- |
| benchmark traces and intermediate run material | `reproduction only` | Useful for inspection and rerun support, but not part of the curated release bundle. |
| debug dumps, if present later | `excluded` | Temporary output. |

## 4. Approved First-Batch Artifact Set

The following minimal bundle is approved for curated promotion:

- `artifacts/phase_v_retention/retention_report.md`
- `artifacts/phase_v_retention/retention_summary.json`
- `artifacts/phase_v_retention/metadata.json`
- `artifacts/semantic_backend_comparison/comparison_report.md`
- `artifacts/semantic_backend_comparison/comparison_summary.json`
- `artifacts/semantic_backend_comparison/metadata.json`
- `artifacts/external_validation/external_validation_report.md`
- `artifacts/external_validation/external_validation_summary.json`
- `artifacts/external_validation/metadata.json`

## 5. Not Promoted

The following classes of output are not promoted in this release step:

- raw traces
- debug logs
- intermediate dumps
- cache files
- one-off inspection output

These remain under `experiments/results/` if retained at all.

## 6. Release Boundary Notes

- The original experiment outputs are not removed by this decision.
- Promotion is a curated copy, not a wholesale migration of `experiments/results/`.
- `metadata.json` is only approved when it includes sufficient provenance to support release traceability.
- If a future output lacks claim linkage or provenance completeness, it should not be added to the approved bundle without a new decision entry.

## 7. Downstream Actions

After this decision, the next release actions are:

1. Create the `artifacts/` subdirectories for the approved bundles.
2. Copy only the approved artifacts into those directories.
3. Update `ARTIFACT_POLICY.md` if any path conventions need to be made explicit.
4. Update `RELEASE_CHECKLIST.md` so artifact validation can check the approved list directly.

