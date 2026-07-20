# SRP Main Results Summary V1

This document provides a paper-facing summary of the frozen SRP evidence chain.
It is a synthesis artifact, not a new experiment, not a mechanism design, and not a policy document.

## 1. Summary Table

| Research Question | Experiment | Main Result | Supports Claim |
| --- | --- | --- | --- |
| RQ1 | Phase I Parameter Observability | 130 transition observations, replay success `1.0`, state consistency `1.0` | Semantic observability |
| RQ2 | Phase II Boundary Validation | 10 / 25 feasible candidates, stable extents across densities | Validated boundaries |
| RQ2.1 | Phase II Density Baseline | Coverage varies by grid density, but feasible extents remain `0.1..0.9` and `1..2` | Sampling-robust boundary evidence |
| RQ2.2 | Phase II Boundary Generalization | Pairwise IoU quantifies overlap; extents remain fixed while discrete feasible sets vary | Boundary generalization |
| RQ3 | Phase III-A Baseline Comparison | 60% search reduction with the same top candidate as the naive full-grid sweep | Governed optimization |
| RQ3.1 | Phase III-A Objective Sensitivity | Feasible region fixed; rankings change with objective weights; Spearman varies from `0.20` to `0.90` vs the balanced reference | Objective decoupling |
| RQ4 | Semantic Evidence Escalation | 10-case baseline shows higher verification accuracy with additional semantic evidence, authority unchanged, and authority-violation final accept rate `0.0` | Evidence-controlled verification |
| RQ5 | Phase V Retention and Drift | 4-case baseline protocol: mean coverage `0.8375`, mean drift `0.196875`, mean recovery accuracy `0.766667` | Semantic fidelity measurement |
| RQ6 | Phase VI Relation-Aware Recovery | 12-case MVP: relation expansion restores neighborhood coverage, while relation closure lowers drift and hallucinated relation rate relative to vector-only recovery under the same budget | Structure-preserving reconstruction |
| RQ7 | Phase VII Parameter Stability | 10 repeated runs under frozen workload/objective/evidence backend: recommendation consistency `1.0` | Governed recommendation stability |
| RQ8 | Phase VII-B Parameter Sensitivity | one-factor sweeps show archive retention lowers drift, relation depth shifts the coverage-cost frontier, and activation threshold trades coverage for drift | Governance tradeoff analysis |
| RQ9 | Phase VIII-A Cross-Domain Validation | 18-case MVP across code memory, knowledge reasoning, and agent planning: relation-closure preserves its relative advantage, while absolute fidelity varies by workload | Cross-domain relative generality |
| RQ10 | Phase VIII-B Representation Invariance | 144-case MVP across four encoders and three parsers: hierarchy consistency rate `1.0`, governance consistency rate `1.0`, relative ordering preserved | Representation invariance |
| RQ11 | Phase VIII-C Implementation Independence | 36-case MVP across flat, graph, and vector-overlay stores: hierarchy consistency rate `1.0`, governance consistency rate `1.0`, backend changes move cost more than ordering | Implementation independence |
| RQ12 | External Validation Calibration (LoCoMo) | 3648-record public benchmark calibration slice across full context, sliding window, vector RAG, and SRP: adapter ingestion succeeded, and the calibration-aware rerun separates official score, semantic diagnostics, and attribution distribution | Public-benchmark calibration boundary |
| RQ13 | External Validation Evidence (LongMemEval) | 48-record public benchmark evidence slice under the frozen shared local-vLLM contract across full context, sliding window, vector RAG, Mem0, Graphiti, Letta, MemMachine, and SRP: runtime manifest is frozen, descriptive statistics are reported, official score and SRP diagnostics are co-reported, strong-baseline comparison is complete, and the audit boundary remains explicit while the evidence package is approved for promotion | Promoted shared-runtime evidence package under the frozen slice |

## 2. Main Narrative

The SRP evidence chain supports the following evidence-backed claims:

1. Semantic evolution can be observed and measured before optimization.
2. Boundary validation can freeze a feasible region that later optimization respects.
3. Evidence escalation can improve verification without transferring authority.
4. Semantic fidelity can be measured after transition, exposing a coverage-versus-drift tradeoff under governed retention settings.
5. Relation-aware recovery can improve structural fidelity by preserving relational dependencies during reconstruction.
6. Governed recommendations can remain stable under repeated evaluation with frozen workload, objective, and evidence backend.
7. Parameter changes shift the tradeoff surface in predictable ways, exposing explicit governance costs and fidelity gains.
8. Cross-domain validation shows that the relation-aware hierarchy preserves its relative advantage across heterogeneous workloads, even though absolute fidelity remains workload dependent.
9. Representation invariance shows that the recovery hierarchy and governance semantics remain stable across tested encoders and parsers, even though absolute scores vary by backend.
10. Implementation independence shows that the recovery hierarchy and governance semantics remain stable across tested storage backends, even though evidence cost varies by backend.
11. LongMemEval evidence runs preserve the shared-generation runtime contract across baselines and SRP, report descriptive statistics for the fixed validation slice, and now include the stronger memory-system baseline comparison while keeping the audit boundary explicit and the evidence package approved for promotion.

## 3. Interpretation

The most important methodological separation is:

```text
Phase II
  fixes the feasible region

Phase III-A
  changes ranking inside that region

Governance
  decides whether to execute
```

This means objective changes affect recommendation, not feasibility.

## 4. Where the Evidence Lives

- Phase I observability: `experiments/results/phase_i/`
- Phase II boundary validation: `experiments/results/phase_ii_boundary/`
- Phase II density baseline: `experiments/results/phase_ii_density_baseline/`
- Phase II boundary generalization: `experiments/results/phase_ii_boundary_generalization/`
- Phase III-A baseline comparison: `experiments/results/phase_iii_a_baseline_comparison/`
- Phase III-A objective sensitivity: `experiments/results/phase_iii_a_objective_sensitivity/`
- Semantic evidence comparison: `experiments/results/semantic_backend_comparison/`
- Phase V retention and drift: `experiments/results/phase_v_retention/`
- Phase VI relation-aware recovery: `experiments/results/phase_vi_relation_recovery/`
- Phase VII parameter stability: `experiments/results/phase_vii_parameter_stability/`
- Phase VII-B parameter sensitivity: `experiments/results/phase_vii_parameter_sensitivity/`
- Phase VIII cross-domain validation: `experiments/results/phase_viii_cross_domain/`
- Phase VIII representation invariance: `experiments/results/phase_viii_representation_invariance/`
- Phase VIII implementation independence: `experiments/results/phase_viii_implementation_independence/`
- External validation LoCoMo run: `experiments/results/real_world_validation/locomo/run_20260718T2243500187290000`
- External validation LoCoMo baseline comparison: `experiments/results/real_world_validation/locomo/baseline_comparison/run_20260718T2244336007040000`
- Real-validation report: `audit/REAL_VALIDATION_REPORT.md`
- Real-validation report: `audit/REAL_VALIDATION_REPORT.md`
- LongMemEval status: pending real-data slice, not part of the current release gate

## 5. Paper Use

This summary can be used as the paper's compact evidence map for the abstract, conclusion, and results overview.
