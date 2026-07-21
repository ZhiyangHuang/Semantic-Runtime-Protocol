# Current Status

| Phase | Description | Status | Evidence | Next Allowed Action |
|---|---|---|---|---|
| Phase 0 | Pipeline audit | Complete | `docs/archive/benchmark_history/EXPERIMENT_PIPELINE_AUDIT.md` | Move to infrastructure discovery or keep auditing gaps |
| Phase 0.5 | Infrastructure discovery | Complete | `docs/archive/benchmark_history/BENCHMARK_INFRASTRUCTURE_DISCOVERY.md` | Proceed to framework extension design |
| Phase 1 | Framework extension design | Complete | `docs/archive/benchmark_history/MINIMAL_BENCHMARK_FRAMEWORK_EXTENSION_PLAN.md` | Proceed to task breakdown |
| Phase 2 | Worker implementation | Complete | `docs/archive/benchmark_history/BENCHMARK_IMPLEMENTATION_TASK_BREAKDOWN.md`, `docs/archive/benchmark_history/BENCHMARK_WORKER_TASK_ASSIGNMENT.md`, `docs/archive/benchmark_history/BENCHMARK_WORKER0_IMPLEMENTATION_REPORT.md` | Proceed to smoke experiment planning |
| Phase 3 | Smoke experiment planning | Complete | `docs/archive/benchmark_history/BENCHMARK_SMOKE_EXPERIMENT_PLAN.md` | Proceed to execution preparation |
| Phase 3.5 | Execution preparation | Complete | `docs/archive/benchmark_history/BENCHMARK_SMOKE_EXECUTION_GUIDE.md` | Proceed to smoke execution |
| Phase 4 | Smoke execution | Complete | `experiments/results/mmlu_smoke/`, `experiments/results/arc_smoke/` | Proceed to artifact review or full-benchmark planning |
| Phase 4.2 | Artifact review | Complete | `docs/archive/benchmark_history/BENCHMARK_SMOKE_ARTIFACT_REVIEW.md` | Proceed to full benchmark planning |
| Phase 5 | Full benchmark planning | Complete | `docs/archive/benchmark_history/FULL_BENCHMARK_EXECUTION_PLAN.md` | Proceed to authorization gate |
| Phase 5.5 | Authorization gate | Authorized | `docs/archive/benchmark_history/FULL_BENCHMARK_EXECUTION_AUTHORIZATION_CHECKLIST.md` | Execute full MMLU benchmark |
| Phase 6 | Full benchmark execution | Complete | `docs/archive/benchmark_history/FULL_MMLU_EXECUTION_RECORD_V3.md`, `docs/archive/benchmark_history/FULL_MMLU_ARTIFACT_AUDIT.md`, `docs/archive/benchmark_history/FULL_MMLU_EXECUTION_CLOSURE_REVIEW_V3.md`, `docs/archive/benchmark_history/MMLU_PROMPT_LEAKAGE_AUDIT_V2.md`, `docs/archive/benchmark_history/ARC_PRE_FLIGHT_AUDIT.md`, `docs/archive/benchmark_history/FULL_ARC_EXECUTION_RECORD_V1.md`, `docs/archive/benchmark_history/FULL_ARC_ARTIFACT_AUDIT.md`, `docs/archive/benchmark_history/ARC_PROMPT_LEAKAGE_AUDIT_V1.md`, `docs/archive/benchmark_history/FULL_ARC_EXECUTION_CLOSURE_REVIEW_V1.md` | Proceed to cross-benchmark consistency review |
| Phase 6.5 | Cross-benchmark review | Complete | `docs/archive/benchmark_history/CROSS_BENCHMARK_CONSISTENCY_REVIEW.md` | Proceed to evidence manifest update |
| Phase 7 | LongMemEval integration | Complete with dual-evaluation surface | `docs/archive/benchmark_history/LONGMEMEVAL_BRIDGE_ARCHITECTURE.md`, `docs/archive/benchmark_history/LONGMEMEVAL_BRIDGE_WORKER_TASK_ASSIGNMENT.md`, `docs/archive/benchmark_history/LONGMEMEVAL_BRIDGE_EXECUTION_RECORD_V5.md`, `docs/archive/benchmark_history/LONGMEMEVAL_ARTIFACT_AUDIT.md`, `docs/archive/benchmark_history/LONGMEMEVAL_CLOSURE_REVIEW.md`, `docs/archive/benchmark_history/LONGMEMEVAL_DUAL_EVALUATION_MODEL.md` | Proceed to evidence-manifest integration planning or HumanEval implementation |
| Phase 8 | HumanEval implementation | Complete | `docs/archive/benchmark_history/HUMANEVAL_EXECUTION_DESIGN.md`, `docs/archive/benchmark_history/HUMANEVAL_IMPLEMENTATION_REPORT.md`, `experiments/benchmarks/humaneval/` | Proceed to HumanEval smoke planning |
| Phase 8.5 | HumanEval smoke validation | Complete | `docs/archive/benchmark_history/HUMANEVAL_SMOKE_EXECUTION_PLAN.md`, `docs/archive/benchmark_history/HUMANEVAL_PROMPT_LEAKAGE_AUDIT_V1.md`, `docs/archive/benchmark_history/HUMANEVAL_ARTIFACT_AUDIT_V1.md`, `docs/archive/benchmark_history/HUMANEVAL_SMOKE_CLOSURE_REVIEW_V1.md`, `experiments/results/humaneval_smoke_v1/` | Proceed to full HumanEval planning or full execution authorization |
| Phase 8.6 | HumanEval full execution | Complete | `docs/archive/benchmark_history/FULL_HUMANEVAL_EXECUTION_RECORD_V1.md`, `docs/archive/benchmark_history/HUMANEVAL_FULL_ARTIFACT_AUDIT_V1.md`, `docs/archive/benchmark_history/HUMANEVAL_FULL_PROMPT_LEAKAGE_AUDIT_V1.md`, `docs/archive/benchmark_history/FULL_HUMANEVAL_EXECUTION_CLOSURE_REVIEW_V1.md`, `experiments/results/humaneval_full_v1/` | Proceed to release evidence review |
| Phase 9 | Release evidence review | RELEASE_READY | `docs/release/RELEASE_READY_VERIFICATION.md`, `docs/release/RELEASE_STATUS.md` | Create release tag or perform final paper-facing sync without mutating evidence |

# Completed Components

## Infrastructure

- shared benchmark framework
- shared artifact writer
- shared runner
- shared metrics schema

## Adapters

- MMLU
- ARC
- LongMemEval
- HumanEval

## Design

- HumanEval execution architecture
- HumanEval execution implementation
- LongMemEval dual evaluation model

## Artifacts

- MMLU smoke artifact
- ARC smoke artifact
- LongMemEval bridge artifact
- HumanEval smoke artifact
- HumanEval full artifact

# Current Blocking Point

Full benchmark execution is complete: the corrected MMLU v3 artifact passed the leakage audit and closure review, ARC pre-flight completed, and the full ARC-Easy artifact passed artifact audit, leakage audit, and closure review. The cross-benchmark consistency review is also complete. LongMemEval bridge v5 is audited and closed as a release-branch benchmark-family artifact. HumanEval full is closed and ready for release evidence review.

The repository already has:
- validated shared benchmark infrastructure
- validated MMLU, ARC, LongMemEval, and HumanEval artifacts
- a full benchmark execution plan
- a final execution authorization checklist

What remains before completion of the current release-evidence phase:
- complete the release evidence review
- update the evidence manifest only after release evidence review is complete

# Allowed Next Actions

Allowed:
- continue the release evidence review
- prepare evidence-manifest integration planning for the audited benchmark family
- audit benchmark-family artifacts before any paper-facing update

Not allowed:
- modify `paper/`
- update evidence claims
- rewrite metrics manually
- update the evidence manifest before release evidence review is complete
- bundle MMLU and ARC into a single unreviewed full run

# Evidence Inventory

## LongMemEval

- status: complete external validation evidence
- artifact family: existing LongMemEval reality-check and related reports
- release report: `docs/benchmarks/LONGMEMEVAL_REPORT.md`

## MMLU

- status: complete
- artifact location: `experiments/results/mmlu_full_v3/`
- release report: `docs/benchmarks/MMLU_REPORT.md`
- historical invalid artifact: `experiments/results/mmlu_full_v2/`

## ARC

- status: complete
- artifact location: `experiments/results/arc_full_v1/`
- release report: `docs/benchmarks/ARC_REPORT.md`

## HumanEval

- status: complete
- artifact location: `experiments/results/humaneval_full_v1/`
- release report: `docs/benchmarks/HUMANEVAL_REPORT.md`

## Cross-benchmark review

- status: complete
- review: `docs/archive/benchmark_history/CROSS_BENCHMARK_CONSISTENCY_REVIEW.md`

## Benchmark history archive

- index: `docs/archive/benchmark_history/README.md`

# Research Integrity Rules

- artifacts before claims
- no manual metrics editing
- no paper updates before audited results
- baseline and SRP comparisons must remain comparable
- smoke artifacts validate pipeline correctness, not benchmark superiority
- full benchmark artifacts must still be audited before any paper-facing promotion
- prompt leakage policy is now enforced by the shared benchmark runner
- LongMemEval bridge remains an artifact integration layer with external_validation scorer authority
- LongMemEval must retain distinct original-research and shared-alignment evaluation surfaces
- HumanEval now has a dedicated execution layer with subprocess isolation and pass@1 reporting
- HumanEval smoke validated the execution boundary and the shared artifact contract
- HumanEval full is closed and ready for release evidence review
- release evidence review has reached the release-ready state
