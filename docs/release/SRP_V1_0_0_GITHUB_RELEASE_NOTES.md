# SRP v1.0.0 - Semantic Runtime Protocol Evidence Release

## Overview

This release freezes the benchmark evidence surface for Semantic Runtime Protocol (SRP).

`srp-v1.0.0` represents the first release-grade evaluation package with audited benchmark artifacts, frozen provenance, and a release manifest-backed evidence structure.

The release preserves a strict separation between:

- benchmark authority
- SRP diagnostics
- artifact packaging
- historical development records

## Evaluated Benchmarks

### MMLU v3 - General Knowledge Reasoning

- Evaluation type: multiple-choice reasoning
- Metric: accuracy
- Artifact status: audited and frozen

Report:

`docs/benchmarks/MMLU_REPORT.md`

### ARC v1 - Scientific Reasoning

- Evaluation type: scientific reasoning
- Metric: accuracy
- Artifact status: audited and frozen

Report:

`docs/benchmarks/ARC_REPORT.md`

### LongMemEval - Long-Context Memory Evaluation

LongMemEval uses a dual-evaluation surface.

#### Track A - Official Evaluation

- Authority:
  - `experiments/external_validation`
- Metric:
  - official LongMemEval score

#### Track B - Shared Benchmark Alignment

- Authority:
  - SRP benchmark bridge layer
- Purpose:
  - artifact normalization
  - provenance tracking
  - release integration

The two tracks remain separate by design.

The bridge artifact does not replace the official scorer.

Report:

`docs/benchmarks/LONGMEMEVAL_REPORT.md`

### HumanEval v1 - Code Generation Evaluation

- Evaluation type:
  - executable program synthesis
- Primary metric:
  - pass@1
- Execution:
  - sandboxed subprocess evaluation
  - timeout enforcement
  - network disabled

Report:

`docs/benchmarks/HUMANEVAL_REPORT.md`

## Release Evidence

Release status:

```text
RELEASE_EVIDENCE_READY
```

Verified:

- benchmark artifacts audited
- prompt leakage checks completed
- provenance metadata preserved
- release manifest frozen
- historical diagnostic artifacts separated from release evidence

Manifest:

`audit/release_manifest.json`

## Repository Structure

Release-facing documentation:

```text
docs/
├── benchmarks/
└── release/
```

Historical development records:

```text
docs/archive/benchmark_history/
```

Canonical benchmark artifacts:

```text
experiments/results/
├── mmlu_full_v3/
├── arc_full_v1/
├── longmemeval_full_v5/
└── humaneval_full_v1/
```

## Reproducibility Notes

This release intentionally preserves:

- artifact provenance
- benchmark version boundaries
- evaluation authority ownership
- metric interpretation boundaries

Future benchmark updates should create new artifact versions rather than overwrite the frozen release artifacts.

## Citation

When referencing this release, use:

```text
Semantic Runtime Protocol (SRP) v1.0.0
Release tag: srp-v1.0.0
```

## GitHub Release Settings

- Tag: `srp-v1.0.0`
- Mark as latest release: yes
- Pre-release: no
- Attach source archive: default
