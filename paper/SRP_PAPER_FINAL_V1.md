# Semantic Runtime Protocol: Governed Semantic Evolution through Validated Boundaries and Evidence-Controlled Optimization

## Abstract

Semantic systems increasingly maintain runtime state that changes over time, yet existing approaches often optimize retrieval, storage, or action without making explicit when a semantic change is actually allowed. We present Semantic Runtime Protocol (SRP), a governed semantic evolution framework that separates observation, validation, optimization, evidence, governance, and execution. SRP first identifies observable semantic variables and validates feasible transition regions before optimization is considered. Inside those frozen regions, SRP performs constrained optimization to produce governed recommendations rather than direct runtime updates. SRP further supports evidence-controlled verification by allowing stronger semantic evidence to refine decisions without transferring authority. Across the frozen evidence chain, including Phase I observability, Phase II boundary validation, Phase III-A constrained optimization, Phase V retention and drift measurement, Phase VI relation-aware recovery, Phase VII recommendation stability, Phase VII-B parameter sensitivity, Phase VIII-A cross-domain validation, Phase VIII-B representation invariance, and Phase VIII-C implementation independence, SRP demonstrates that semantic evolution can be made measurable, bounded, reconstructable, and governable across heterogeneous workloads, tested representations and implementations. A first LoCoMo ingestion slice was used to calibrate the external-validation adapter and scoring path, but the public-benchmark protocol still requires additional calibration before it can be treated as main paper evidence. The current baseline does not claim autonomous adaptation or universal optimality; adaptive evolution remains future work that requires additional governance boundaries.

## 1. Introduction

Semantic systems increasingly maintain representations that are not static: they are observed, compressed, recovered, ranked, and sometimes updated. In practice, however, systems that operate over evolving semantic state often conflate three different concerns. Evidence is used as if it were authority, optimization is treated as if it were execution, and adaptation is allowed before the boundary of safe change has been established. The result is a system that may improve local performance while leaving open the question of whether semantic change is still governed.

This paper addresses that gap with a simple research question: how can semantic state evolve only within validated, governed boundaries? The answer is not to eliminate optimization or evidence, but to place them inside a fixed authority structure. SRP does this by separating runtime execution from calibration, validation, optimization, evidence, and governance. Observation discovers which variables matter. Validation determines which regions are safe. Optimization ranks candidates only inside those regions. Evidence can strengthen verification when uncertainty remains. Governance remains the only layer that can authorize execution.

Related systems provide useful building blocks but do not solve this problem as stated. Retrieval and memory systems improve access to information, but they do not define transition authority. Agentic systems can plan and act, but they often collapse evidence, decision, and execution into a single loop. Reinforcement learning can adapt policies, but adaptation without validated boundaries risks uncontrolled semantic drift. SRP is positioned differently: it is a governed semantic evolution framework rather than a retrieval system, a memory system, or an adaptive agent.

The paper makes four contributions. First, it shows that semantic evolution variables can be observed and measured before optimization. Second, it shows that validated feasible regions can be frozen and then used to constrain optimization. Third, it shows that verification can be strengthened through additional semantic evidence, semantic fidelity can be measured after transition, recovery can preserve semantic neighborhoods, recommendations can remain stable, and parameter tradeoffs can be made explicit without transferring authority. Fourth, it shows that the same governance principles can generalize across heterogeneous semantic workloads and preserve recovery hierarchy across the tested representations and storage implementations. Together, these contributions define a governance-first view of semantic evolution.

## 2. Background and Related Work

SRP is related to retrieval-based systems, memory systems, autonomous agents, and adaptive learning methods, but it is not reducible to any one of them.

Retrieval and memory systems focus on how to store, compress, and recover information. Their primary question is typically about access quality: what should be retrieved, and how faithfully can it be reconstructed? SRP uses evidence and recovery, but its primary question is different. SRP asks whether a semantic transition is permitted at all, and under what validated conditions that transition may proceed.

Agentic systems emphasize planning, tool use, and autonomous execution. Their strength is action generation, but that strength also creates a risk: observation, decision, and execution may become entangled. SRP separates those layers. Evidence may inform a decision, optimization may recommend a configuration, but governance is the only layer that approves execution.

Reinforcement learning and other adaptive systems optimize policies over time. That setting is valuable when the objective and the action space are already well defined. SRP focuses on a prior question: before a system learns to adapt, can it first validate where adaptation is allowed? In other words, SRP treats governance as a prerequisite to adaptation rather than a consequence of it.

This distinction matters because the paper is not claiming that semantic systems never adapt. It is claiming that adaptation should be bounded by validated transition regions and explicit authority separation. That framing lets SRP use ideas from retrieval, memory, agents, and optimization without inheriting their authority assumptions.

## 3. Semantic Runtime Protocol

### 3.1 Problem Definition

SRP treats semantic evolution as controlled changes in semantic runtime state. The problem is not how to produce more information, but how to ensure that semantic changes occur under validated boundaries and explicit authority conditions.

### 3.2 Runtime State Representation

Let semantic state at time `t` be `S_t`, let `theta` denote the parameter configuration, and let `e` denote evidence. SRP models the transition as:

```text
S_(t+1) = T(S_t, theta, e)
```

Phase II defines the validated feasible region:

```text
F = { theta | invariant(theta) = true }
```

Phase III-A searches within that region:

```text
theta* = argmax_{theta in F} U(theta)
```

but `theta*` is a governed recommendation rather than a direct runtime mutation.

### 3.3 Controlled Transition Pipeline

SRP follows a governed pipeline:

```text
Observation
    |
    v
Validation
    |
    v
Optimization
    |
    v
Evidence
    |
    v
Governance
    |
    v
Execution
```

The order matters. Observation discovers what can be measured. Validation freezes what can be changed safely. Optimization ranks candidates inside that frozen region. Evidence refines verification when uncertainty remains. Governance is the approval boundary. Runtime execution happens only after approval.

### 3.4 Authority Separation

SRP assigns each layer a different responsibility:

| Component | Authority |
| --- | --- |
| Calibration | observe |
| Validation | verify |
| Optimization | recommend |
| Evidence | inform |
| Governance | approve |
| Runtime | execute |

The central design rule is that recommendation is not execution. More evidence is not more authority. Validation does not mutate the system; it defines the region in which mutation may later be considered.

This gives SRP a clear separation between feasibility and preference. Phase II determines where optimization may operate. Phase III-A determines which candidate is preferred under a declared objective. Governance determines whether the preferred candidate becomes an actual transition.

## 4. Experiments

### 4.1 Experimental Setup

The experiments evaluate whether SRP can observe semantic evolution variables, identify validated transition boundaries, optimize configurations inside validated regions, and improve verification through additional evidence.

The experimental boundary is fixed:

- runtime implementation remains fixed
- no online learning
- no autonomous mutation
- optimization outputs are advisory
- evidence backends do not control execution

The research questions are:

| RQ | Question |
| --- | --- |
| RQ1 | Can SRP observe semantic evolution variables? |
| RQ2 | Can SRP identify validated transition boundaries? |
| RQ3 | Can SRP optimize configurations inside validated regions? |
| RQ4 | Can additional evidence improve verification without authority transfer? |
| RQ5 | Can semantic fidelity after transition be measured? |
| RQ6 | Can semantic neighborhoods be reconstructed more faithfully than isolated units? |
| RQ7 | Are governed recommendations stable under repeated evaluation? |
| RQ8 | How do SRP parameters move the fidelity-cost tradeoff surface? |
| RQ9 | Do SRP governance principles remain effective across heterogeneous semantic workloads? |
| RQ10 | Does SRP preserve its governance semantics under representation changes? |
| RQ11 | Does SRP preserve its governance semantics under backend changes? |

### 4.2 Phase I: Parameter Observability

Phase I asks whether semantic evolution variables can be measured before validation or optimization.

SRP collects repeated transition observations over the frozen parameter axes:

- activation_threshold
- recovery_min_evidence
- preserve_evidence
- archive_relations

The main measurements are replay success, state consistency, and parameter drift.

The Phase I evidence package reports:

- 130 transition observations
- 5 repeated observation passes
- replay success = 1.0
- state consistency = 1.0
- mean parameter drift = 0.5538

These results show that semantic transition variables can be explicitly represented and measured before optimization decisions are introduced.

### 4.3 Phase II: Boundary Validation

Phase II asks whether SRP can determine feasible semantic evolution regions before optimization.

The boundary condition is:

```text
F = { theta | invariant(theta) = true }
```

Candidate evaluation uses invariant checking, closure validation, and replay equivalence.

The main boundary validation result is:

- 25 candidates evaluated
- 10 candidates feasible
- feasible region extents:
  - activation_threshold = 0.1..0.9
  - recovery_min_evidence = 1..2

The density baseline and boundary generalization studies show that while the discrete feasible set changes with sampling density, the estimated boundary extents remain stable.

This phase establishes where optimization is allowed to operate.

### 4.4 Phase III-A: Governed Optimization

Phase III-A asks whether SRP can reduce optimization search while preserving recommendation quality.

The baseline comparison contrasts SRP against a naive full-grid sweep over the same candidate space.

The main comparison result is:

| Method | Candidates | Top Objective |
| --- | ---: | ---: |
| Full Grid | 25 | 0.54 |
| SRP | 10 | 0.54 |

This corresponds to a 60% search reduction while preserving the same top candidate.

Objective sensitivity is analyzed separately within Phase III-A. The feasible region remains fixed, but rankings change as objective weights change. In other words, the optimization result is objective-dependent, not boundary-dependent.

This phase shows that SRP does not replace optimization. It constrains optimization to validated regions.

### 4.5 Evidence Escalation

The evidence escalation experiment asks whether additional semantic evidence can improve verification without increasing authority.

The comparison is:

- vector evidence only
- vector evidence plus semantic evidence

The baseline package contains 10 verification cases spanning paraphrase, contradiction, authority violation, and boundary-sensitive inputs. It compares a vector-only baseline against a vector-plus-semantic-evidence variant.

The main results are:

| Metric | Vector-only | Vector + Semantic Evidence |
| --- | ---: | ---: |
| Accuracy | 0.50 | 1.00 |
| Agreement rate | 0.50 | 0.50 |
| Review rate | - | 0.50 |
| Authority violation final accept rate | - | 0.00 |

The study also reports a variant local-model count of 8, an offline-heuristic fallback count of 2, and a fallback usage count of 2.

The result supports the claim that semantic evidence can improve verification quality under the tested cases while execution authority remains unchanged. Evidence informs, while governance decides.

### 4.6 Experiment Summary

Together, these experiments support the SRP separation principle:

- observation establishes measurable state variables
- validation defines feasible transition regions
- optimization ranks candidates inside those regions
- evidence improves verification without changing authority

### 4.7 Phase VI-A: Relation-Aware Recovery

Phase VI-A asks whether SRP can reconstruct semantic neighborhoods more faithfully than isolated units under the same recovery budget.

The experiment compares three recovery modes:

- vector-only recovery
- vector plus relation expansion
- relation-closure recovery

The main result is:

- 12 cases evaluated
- vector-only recovery has the weakest structural fidelity
- relation expansion materially improves relation recall and neighborhood completeness
- relation-closure recovery reduces hallucinated relations and lowers drift relative to relation expansion

Selected mode-level results:

| Mode | Mean Relation Acc. | Mean Closure Acc. | Mean Drift | Mean Hallucinated Rel. Rate |
| --- | ---: | ---: | ---: | ---: |
| vector_only | 0.333333 | 0.166667 | 0.433333 | 0.0 |
| relation_expansion | 0.875 | 0.8125 | 0.145834 | 0.3125 |
| relation_closure | 0.875 | 0.8125 | 0.083333 | 0.0 |

The ablation can also be summarized as:

| Recovery Mode | Coverage | Relation Acc. | Closure Acc. | Drift | Hallucinated Relation |
| --- | ---: | ---: | ---: | ---: | ---: |
| Vector-only | 0.392857 | 0.333333 | 0.166667 | 0.433333 | 0.0 |
| Relation expansion | 0.738095 | 0.875 | 0.8125 | 0.145834 | 0.3125 |
| Relation closure | 0.738095 | 0.875 | 0.8125 | 0.083333 | 0.0 |

This phase shows that relation-aware recovery changes the preservation profile by improving structural fidelity under the same recovery budget.
Relation expansion restores semantic neighborhood coverage, while closure validation removes invalid relational noise and reduces drift.

### 4.8 Phase VII-A: Recommendation Stability

Phase VII-A asks whether the governed recommendation is stable under repeated evaluation with frozen workload, objective, and evidence backend.

The stability study runs the same recommendation setting across 10 seeds.
Its main result is that the recommendation is fully consistent across runs:

| Metric | Value |
| --- | ---: |
| Run count | `10` |
| Recommendation consistency | `1.0` |
| Activation threshold variance | `0.0` |
| Recovery min evidence variance | `0.0` |
| Objective value variance | `0.0` |

This shows that the current governed recommendation is stable rather than arbitrary under repeated evaluation.

### 4.9 Phase VII-B: Parameter Sensitivity and Governance Tradeoff Analysis

Phase VII-B asks how SRP parameters move the system across fidelity-cost tradeoff regions while keeping the recovery strategy fixed.
Unlike Phase VII-A, this phase does not test whether the recommendation is repeatable; it tests which parameters shift relation fidelity, coverage, and cost.

The main pattern is that different parameters control different parts of the tradeoff surface:

- `archive_relations` improves relation fidelity and reduces drift, but increases cost
- `preserve_evidence` improves provenance stability and slightly narrows drift, but adds cost
- `relation_depth` has the largest structural effect, with deeper recovery improving coverage and closure at higher cost
- `activation_threshold` shifts the acceptance boundary, trading coverage against drift in a smoother way

This means SRP exposes a parameter behavior map rather than collapsing parameter analysis into a single best configuration.

The measured sweep makes the pattern concrete:

| Setting | Coverage | Drift | Evidence Cost | Interpretation |
| --- | ---: | ---: | ---: | --- |
| Baseline (`archive_relations=False`, `preserve_evidence=False`, `relation_depth=1`, `activation_threshold=0.9`) | 0.728095 | 0.098333 | 1.695 | Reference point |
| `archive_relations=True` | 0.758095 | 0.077083 | 1.815 | Better relation fidelity, higher cost |
| `preserve_evidence=True` | 0.738095 | 0.083333 | 1.755 | Slight fidelity gain, moderate cost increase |
| `relation_depth=0` | 0.199643 | 0.628333 | 1.025 | Vector-like recovery, weak structure |
| `relation_depth=2` | 0.839524 | 0.0 | 1.855 | Strongest fidelity gain in the sweep |
| `relation_depth=3` | 0.849524 | 0.005 | 2.015 | Highest coverage, highest cost |
| `activation_threshold=0.1` | 0.792095 | 0.138333 | 1.711 | More permissive gating, more drift |

### 4.10 Phase VIII-A: Cross-Domain Validation

Phase VIII-A asks whether the same governed recovery principles remain effective across heterogeneous semantic workloads rather than only on the SRP-shaped prototype.
The minimal cross-domain validation study compares code evolution memory, knowledge reasoning, and agent planning workloads under the same relation-aware recovery baseline.

The main result is that relation-aware recovery preserves its relative advantage over vector-only recovery across domains, while absolute fidelity remains domain dependent:

| Domain | Coverage | Drift | Relation Acc. | Closure Acc. | Hallucinated Rel. Rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| Code memory | 0.638889 | 0.227778 | 0.666667 | 0.666667 | 0.138889 |
| Knowledge reasoning | 0.500000 | 0.400000 | 0.500000 | 0.250000 | 0.333333 |
| Agent planning | 0.465278 | 0.355556 | 0.500000 | 0.416667 | 0.111111 |

The domain comparison suggests that SRP's recovery hierarchy remains intact across workloads, but the difficulty of structural recovery is workload dependent.
Code-oriented memory is easier to reconstruct than planning memory in this MVP, and relation closure remains the most reliable way to suppress hallucinated relations.

Domain-normalized comparison against vector-only recovery:

| Domain | Vector-only Closure | Relation-closure Closure | Delta |
| --- | ---: | ---: | ---: |
| Code memory | 0.000000 | 1.000000 | +1.000000 |
| Knowledge reasoning | 0.000000 | 0.375000 | +0.375000 |
| Agent planning | 0.000000 | 0.625000 | +0.625000 |

The normalized view makes the cross-domain pattern clearer: SRP preserves the direction of improvement everywhere, but the magnitude of structural recovery varies by workload.

### 4.11 Phase VIII-B: Representation Invariance

Phase VIII-B asks whether SRP preserves its governance semantics under representation changes.
The minimal invariance study varies encoders and parsers while keeping the recovery hierarchy, governance pipeline, and evaluation protocol fixed.

The main result is that the recovery hierarchy remains stable across the tested representations:

| Metric | Value |
| --- | ---: |
| Cases evaluated | `144` |
| Hierarchy consistency rate | `1.0` |
| Governance consistency rate | `1.0` |

The absolute coverage and drift values vary by encoder and parser, but the ordering relation remains preserved.
This suggests that SRP governs semantic state and recovery semantics rather than depending on a single embedding space.
The SRP-specific analysis metrics HCR and GCR are treated here as analysis checks, not new community benchmarks.

### 4.12 Phase VIII-C: Implementation Independence

Phase VIII-C asks whether SRP preserves its governance semantics when the storage backend changes.
The minimal implementation study varies the backend while keeping the recovery hierarchy, governance pipeline, and evaluation protocol fixed.

The main result is that the recovery hierarchy remains stable across the tested backends:

| Metric | Value |
| --- | ---: |
| Cases evaluated | `36` |
| Hierarchy consistency rate | `1.0` |
| Governance consistency rate | `1.0` |

The backend variants preserve the same relative ordering, while evidence cost shifts modestly by implementation.
This suggests that SRP governs semantic state and recovery semantics rather than depending on a single storage backend.
The SRP-specific analysis metrics HCR and GCR are treated here as analysis checks, not new community benchmarks.

## 5. Analysis and Component Analysis

SRP separates validation, optimization, evidence, and governance into independent components. This section explains why those separations are necessary by analyzing what changes when a layer is removed or when the objective changes.

### 5.1 Boundary Validation Separation

Removing Phase II collapses the pipeline into:

```text
Observation
    |
    v
Optimization
    |
    v
Execution
```

In that setting, optimization may still rank candidates, but it no longer has a frozen feasible region. Invalid candidates reappear and feasibility is no longer guaranteed. Boundary validation is not an optimization acceleration trick. It defines the admissible transition space.

### 5.2 Evidence Escalation Separation

Removing semantic evidence escalation leaves the system with vector evidence only. That change reduces verification quality in boundary-sensitive cases, especially when vector evidence and semantic interpretation disagree. The important point is not that the semantic model is smarter. The important point is that additional evidence improves confidence without becoming a decision authority.

### 5.3 Governance Separation

If optimization output is routed directly into runtime mutation, recommendation and execution collapse into the same step. That destroys the approval boundary that SRP uses to prevent objective-driven selection from becoming an implicit execution policy. Governance separation keeps optimization from mutating the runtime by itself.

### 5.4 Objective-Feasibility Decoupling

Phase III-A objective sensitivity shows that ranking changes when the objective changes, while the validated feasible region remains fixed. If objective changes were allowed to redefine feasibility, preference and safety would be entangled. SRP avoids that by keeping the feasible region frozen and letting the objective affect ranking only. Preference changes do not redefine safety boundaries.

### 5.5 Parameter Recommendation Analysis

The current Phase III-A baseline recommends the configuration:

```text
activation_threshold = 0.9
recovery_min_evidence = 1
```

under the balanced objective used in the optimization baseline. The corresponding objective value is `0.54`.

This should be interpreted as a governed recommendation inside the validated feasible region, not as a runtime default update.

The recommendation depends on:

- the validated feasible region
- the declared objective
- the frozen evidence context

The objective sensitivity study shows that the feasible region remains fixed while rankings change with objective weights. The recommendation is therefore best understood as:

```text
best configuration under objective U
```

not as a universal optimum.

The recommendation analysis is orthogonal to the semantic evidence comparison study. Evidence backend selection changes verification quality; parameter recommendation changes optimization preference. SRP keeps those decisions separate.

### 5.6 Structural Semantic Recovery Analysis

Phase VI-A isolates a different failure mode from the retention baseline: it tests whether the recovered neighborhood preserves the relation structure that makes facts meaningful together.

The recovery baseline shows three distinct behaviors:

- vector-only recovery is strongest at isolated fact pickup, but weakest at closure
- relation expansion restores structure, but may introduce hallucinated edges
- relation-closure recovery preserves structure while filtering invalid relations

This matters because the dominant bottleneck is not simply missing semantic units.
It is missing semantic closure.

SRP therefore treats recovery as a structure-preserving reconstruction problem rather than a similarity-search problem.

The result also clarifies the role of the existing recovery controls:

- `archive_relations` is best understood as a structural retention boundary
- `preserve_evidence` stabilizes the proof trail
- `recovery_min_evidence` controls strictness
- `activation_threshold` remains a transition-gating parameter, not the main reconstruction control

### 5.7 Recommendation Stability Analysis

Phase VII-A complements the relation-aware recovery study by showing that the recommended configuration does not fluctuate under repeated evaluation with the same workload, objective, and evidence backend.
This matters because governed recommendations should be stable enough to interpret, even when they are not claimed to be universally optimal.

### 5.8 Parameter Sensitivity and Governance Tradeoff Analysis

Phase VII-B complements the stability study by showing that SRP parameters do not all affect the system in the same way.
Some parameters primarily affect relation fidelity, some mainly affect cost, and some move the system along a smooth coverage-versus-drift frontier.

The important result is not a single ranking.
It is a parameter behavior map:

- `archive_relations` is the clearest relation-fidelity control
- `preserve_evidence` stabilizes the proof trail with moderate cost
- `relation_depth` drives the strongest fidelity-cost tradeoff
- `activation_threshold` mainly shifts the governance boundary

This gives SRP an interpretable calibration surface without turning calibration into an autonomous update policy.

## 6. Discussion

### 6.1 Why Validation Before Adaptation

SRP validates boundaries before allowing optimization because adaptation without a validated boundary cannot distinguish better transitions from unsafe ones. The framework therefore asks a prior question that many adaptive systems skip: where is change allowed?

### 6.2 Evidence Is Not Authority

Evidence informs decisions, but it does not authorize them. Validation verifies, governance approves, and runtime executes. SRP keeps those roles separate so that stronger evidence does not silently become stronger control.

### 6.3 Optimization Is Selection, Not Control

Phase III-A produces a recommendation by maximizing an objective within a frozen feasible region. The resulting `theta*` is a governed recommendation, not a runtime mutation. Optimization therefore acts as selection inside a boundary, not as direct control over the system.

### 6.4 Recovery Is Reconstruction, Not Retrieval Alone

Phase VI-A shows that recovery quality improves when the system reconstructs semantic neighborhoods rather than isolated units.
Relation expansion helps recover structure, but closure validation is what removes invalid relational noise and reduces drift.
This makes recovery a reconstruction problem, not just a similarity search problem.

### 6.5 Parameters Are Tradeoff Controls, Not Learned Policies

Phase VII-B shows that SRP parameters expose a governed tradeoff surface rather than a hidden optimization policy.
Parameter changes can improve fidelity, reduce drift, or reduce cost, but not all at once.
That is the point: SRP makes those tradeoffs explicit so the system can be calibrated without silently transferring authority.

### 6.6 Cross-Domain Generality

Phase VIII-A shows that SRP's recovery and governance principles do not depend on a single semantic representation.
The same relation-aware hierarchy remains useful in code evolution memory, knowledge reasoning, and agent planning workloads, even though the absolute fidelity levels differ.
The more precise claim is that SRP preserves the relative advantage of relation-aware recovery across workloads while exposing domain-specific structural difficulty.
This moves SRP from prototype validity toward framework generality.

### 6.7 Representation Invariance

Phase VIII-B shows that SRP's governance semantics remain stable under the tested representation changes.
Across four encoders and three parsers, the recovery hierarchy stays ordered and the governance pipeline remains unchanged, even though absolute scores shift by backend.
This is the strongest evidence in the paper that SRP operates on semantic state and governance semantics rather than on a particular embedding space.

### 6.8 Implementation Independence

Phase VIII-C shows that SRP's governance semantics remain stable under the tested backend changes.
Across the flat, graph, and vector-overlay stores, the recovery hierarchy stays ordered and the governance pipeline remains unchanged, even though absolute evidence cost shifts by backend.
This is the strongest evidence in the paper that SRP does not depend on a single storage implementation.

## 7. Limitations and Future Work

### 7.1 No Autonomous Adaptation Claim

The current SRP baseline does not implement online learning, autonomous policy update, or self-modifying runtime behavior. Adaptive evolution remains future work.

### 7.2 Workload Dependence

The validated feasible region depends on the evaluated workload, the chosen invariants, and the declared objective. SRP therefore validates a governed feasible region for the current experimental boundary; it does not claim a universal boundary for every semantic workload.

### 7.3 Evidence Cost

The evidence escalation study shows verification gains, but the current paper baseline does not fully quantify latency, compute cost, energy cost, or deployment overhead. Future work should study verification gain versus evidence cost.

### 7.4 Governance Assumption

The current baseline assumes governance authority exists outside the runtime. SRP does not solve how governance policies are created or how distributed governance conflicts are resolved.

### 7.5 Cross-Model and Scale Validation

The current paper now includes cross-domain validation, representation invariance, and implementation independence studies, but future work should test whether the same governance principles remain effective across larger-scale memory streams and additional model families beyond the current MVP settings.
It should also test whether the relation-aware recovery hierarchy survives larger and more diverse workloads without losing interpretability or the relative advantage observed in the tested studies.

### 7.6 Public Benchmark Validation

The paper currently includes a public-benchmark calibration slice on LoCoMo.
That slice validated the adapter, temporal attribution protocol, and failure-attribution boundary, but it is intentionally separated from the main external-validity results.
The current 7/18 real-validation report in `audit/REAL_VALIDATION_REPORT.md` and the companion scientific report in `audit/REAL_VALIDATION_SCIENTIFIC_REPORT.md` document the measurement boundary before any benchmark claim is promoted.
The 7/18 LoCoMo real-validation run in `experiments/results/real_world_validation/locomo/run_20260718T2243500187290000` and the paired baseline comparison in `experiments/results/real_world_validation/locomo/baseline_comparison/run_20260718T2244336007040000` provide the release-facing evidence slice under the frozen runtime contract.
Those reports keep the promotion boundary explicit, and the evidence summaries include descriptive statistics for the fixed slice so the result can be audited without overstating inference.
LongMemEval remains protocol-ready, but its real-data slice is still pending and is not part of the current release gate.
The broader benchmark suite would help establish external validity beyond the paper's first calibrated public workload slice, and the stronger memory-system baseline comparison under the same frozen runtime contract is now complete with the evidence package ready for paper-facing promotion.

### 7.7 Failure Analysis

Future work should collect and analyze failure cases across representation, backend, relation, evidence, and domain mismatch settings.
Understanding when SRP fails is necessary to define its boundary as a governed semantic evolution framework rather than a universal memory solution.
The current LongMemEval evidence also suggests a provenance-aware relation layer may be a better governance response than immediate relation pruning: SRP can keep recalled relations explicit as observed, inferred, or uncertain candidates, attach confidence and evidence identifiers, and defer hard pruning until user or benchmark verification is available.
In that framing, extra relations are treated as semantic candidates rather than verified facts, and a future `promotion_state` field can separate `candidate`, `verified`, and `rejected` relations without collapsing recall-oriented recovery into premature pruning.
Within the current audit contract, `candidate` relations are available for retrieval and explanation but are not treated as unconditional downstream facts; only `verified` relations are committed to persistent semantic state, and `rejected` relations are excluded from future recovery.

### 7.8 Threats to Validity

The external-validity package currently includes a fixed 48-record LongMemEval evidence slice and calibration artifacts from LoCoMo.
These slices are intentionally narrow and are used to validate the benchmark adapter, runtime contract, scorer path, and failure-attribution protocol before paper-facing promotion.
The reported LongMemEval statistics are descriptive for the fixed slice and should not be interpreted as benchmark-wide inference.
Scorer alignment is accepted for the frozen slice, and the evidence package is now approved for paper-facing promotion under the frozen contract.
As a result, the current evidence bundle is audit-ready and promoted under the frozen scope.

## 8. Conclusion

SRP introduces a governed semantic evolution process that separates observation, validation, optimization, evidence, governance, and execution. The experiments show that semantic transitions can be measured, constrained, and optimized within validated regions. They also show that verification can be improved through additional evidence without transferring authority. SRP does not provide autonomous self-modification; it provides a controlled foundation for future adaptive systems.
Phase VII-B further shows that parameter changes expose an interpretable fidelity-cost tradeoff surface rather than a hidden autonomous policy.
Phase VIII-A and Phase VIII-B further show that the recovery hierarchy preserves its relative advantage across heterogeneous workloads and tested representation changes, even though absolute fidelity remains workload and representation dependent.
Phase VIII-C further shows that the same governance semantics remain stable under tested backend changes, with cost shifting more than hierarchy.
The LoCoMo ingestion slice further shows that the public-benchmark adapter and evaluator can be run end to end, while the calibration-aware rerun separates official score, semantic diagnostics, and attribution distribution. The benchmark scoring path still requires calibration before the slice can support a paper claim.
The LongMemEval evidence run now demonstrates that the same shared-generation runtime contract can be preserved across baselines and SRP while producing a separate external-validity evidence bundle with descriptive statistics for the fixed slice.
The baseline comparison run in `experiments/results/real_world_validation/locomo/baseline_comparison/run_20260718T2244336007040000` extends that candidate to the current 7/18 LoCoMo comparison set under the same runtime contract.
The LongMemEval evidence promotion decision now records that the bundle is approved for paper-facing use under the frozen contract, while preserving the slice-level limitations explicitly.
The evidence audit specification keeps future evidence runs from being promoted without an explicit runtime manifest, metric definition, statistical reporting layer, and scorer audit.
The LongMemEval failure profile also points to a provenance-aware relation layer as a future governance improvement: rather than pruning recall-heavy candidates too early, SRP can preserve observed, inferred, and uncertain relations with confidence metadata and then correct them through later verification or user feedback.
That design keeps candidate generation distinct from fact commitment and reduces the risk of interpreting recovery breadth as hallucination acceptance.
