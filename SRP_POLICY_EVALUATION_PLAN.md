# SRP Policy Evaluation Plan

This document is the research plan for SRP policy comparison and policy design space exploration.

It assumes the platform is already stable enough to produce comparable lifecycle metrics.

---

## 1. Research Goal

Determine how SRP should reconstruct, compress, and allocate semantic runtime state under benchmark pressure.

Core question:

> How can SRP preserve task-relevant fidelity while minimizing unnecessary state growth?

Secondary question:

> What is the Pareto frontier between semantic coverage, structural preservation, and object retention?

---

## 2. Policy Stages

### 2.1 Reconstruction Policy

Compare:

- `unrestricted`
- `constrained`
- `minimal`

Primary measures:

- `validation_coverage`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`

### 2.2 Compression Policy

Compare:

- `chunk score only`
- `chunk score + object_support_score`

Primary measures:

- `weighted_object_retention`
- `lost_important_object_count`
- `critical_failures_before`

Round 1 observation:

- the first fixed benchmark bundle did not separate these two policies
- the next compression experiment should upgrade benchmark pressure before drawing a conclusion
- mechanism verification shows object support changes chunk scores on every scenario, but the selected top-k set still does not change
- the Top-k decision boundary sweep is now the formal Stage 1 result for object-aware compression
- Stage 2 is now split into three single-variable research questions:
  - RQ2.1 Budget Threshold: vary `top-k budget` only
  - RQ2.2 Ambiguity Threshold: vary `keyword overlap` only
  - RQ2.3 Support Threshold: vary `object-support strength` only
- decoy count is held fixed inside each RQ so the threshold analysis stays one-dimensional
- the new decision-sensitivity metric is `DBI = object_support_gain / decision_margin`
- after the fixed Stage 2 shape is frozen, sample each RQ across multiple seeds and report `mean`, `std`, `95% CI`, and `flip probability`

### 2.3 Allocation Policy

Compare:

- `unrestricted`
- `constrained`
- `minimal`
- dependency-aware variants

Primary measures:

- active / latent / discard partitioning
- `active_state_efficiency`
- `latent_preservation`
- `hallucination_isolation`
- `active_retention_ratio`

### 2.4 Policy Design Space Exploration

Compare:

- baseline
- permissive
- balanced
- conservative

Primary measures:

- `validation_coverage`
- `graph_integrity_score`
- `object_retention`
- `weighted_object_retention`
- `repair_cost`
- `token_overhead`

Secondary measures:

- `delta_validation_coverage`
- `delta_graph_integrity_score`
- `delta_object_retention`
- `budget_pressure`
- parameter sensitivity curves

Interpretation:

- treat policy intervention as a Pareto problem, not a single-best search
- identify which policy family dominates which objective
- keep automated policy optimization deferred unless a later paper explicitly needs it

Round 1 status:

- policy intervention already runs on the fixed baseline, permissive, balanced, and conservative configurations
- the first Pareto analysis run shows a visible tradeoff between validation coverage and structural preservation / object retention
- no single policy dominates all objectives on the current benchmark
- the next step is sensitivity analysis over the main policy knobs, not an optimizer
- the first boundary analysis run shows an allocation-layer boundary on the memory-saturation benchmark, between budgets 32 and 24
- the validation-pressure benchmark now also shows a dependency boundary and a validation boundary, with `dependency_coverage` and `validation_score` changing across the same budget region

---

## 3. Benchmark Pressure

The next benchmark suite should force policy separation.

### 3.1 Dependency Chain

Example:

```text
A -> B -> C -> D -> E
```

### 3.2 Branching Dependencies

Example:

```text
A -> B
A -> C
A -> D
```

### 3.3 Collision Cases

Example:

```text
Project Orion -> DB Atlas
Project Mercury -> DB Atlas
```

### 3.4 Budget Pressure

Example:

```text
required_objects > active_budget
```

---

## 4. Paper-Level Experiment Matrix

The publication-ready comparison set should include:

| Method | State | Verification |
|---|---|---|
| Full Context | token | none |
| Summary | text | none |
| RAG | retrieved text | retrieval |
| SRP-rule | objects | object verifier |
| SRP-hybrid | objects + encoder | hybrid |

### 4.1 Evaluator Robustness

Keep the generator fixed and vary the evaluator:

- `rule-only`
- `rule + E5`
- `rule + E5 + selective judge`
- `Hashing`
- `E5`
- `BGE`
- `Arctic`

Goal:

- show SRP does not depend on a single evaluator family
- show rule-based selection, embedding evidence, and judge arbitration contribute at different layers

### 4.4 Pareto Analysis

Plot:

- coverage vs integrity
- coverage vs retention
- integrity vs retention

Goal:

- show policy families occupy different regions of the Pareto frontier
- show that no single policy simultaneously dominates all objectives on the current benchmark

### 4.5 Sensitivity Analysis

Sweep:

- importance threshold
- decay multiplier
- retained-pass threshold
- archive threshold
- budget pressure

Goal:

- show which policy knobs are stable and which are sensitive
- distinguish a robust policy family from a fragile local optimum

Round 1 status:

- the first sensitivity run is mostly flat on the current fixed benchmark
- this is still useful as a baseline: it indicates the current benchmark is not yet pressure-rich enough to separate the chosen knobs
- stronger benchmark pressure should be added before interpreting the sensitivity curves as decisive

### 4.6 Policy Boundary Analysis

Purpose:

- identify the runtime conditions under which the policy knobs begin to change system behavior
- move from static sensitivity curves to pressure-triggered transition boundaries

Proposed pressure amplifiers:

- memory saturation
- long-horizon runtime
- importance-distribution shift
- tighter active-budget regimes

Goal:

- find the region where policy settings move from inert to behavior-changing
- use this as the bridge from flat sensitivity to meaningful robustness studies

Round 1 status:

- the Pareto front has been computed from the current policy intervention sweep
- baseline and permissive are best on validation coverage
- balanced and conservative are best on graph integrity and object retention
- the tradeoff is now explicit enough to justify sensitivity analysis next
- the first boundary analysis run shows an allocation-layer boundary on the memory-saturation benchmark, between budgets 32 and 24
- the validation-pressure benchmark now also shows dependency and validation boundaries, with `dependency_coverage` and `validation_score` changing across the same budget region
- the `dependency_f1_pressure` benchmark now shows a sharper dependency-F1 boundary on the fine sweep, between budgets 10 and 8
- the tighter `dependency-ultrafine` follow-up sweep over budgets 8 to 12 did not reveal a new dependency-F1 boundary, which suggests that the F1 transition is workload- and resolution-sensitive
- boundary-gap analysis suggests the allocation boundary usually arrives slightly before the dependency/validation boundaries, while dependency-F1 remains the most resolution-sensitive boundary
- boundary robustness analysis now shows allocation, dependency, and validation boundaries are relatively stable across seeds, while dependency-F1 is the most fragile boundary type
- `dependency_f1_pressure` kept a dependency-F1 boundary in 4 of 5 seeds, while `memory_saturation` did not expose one in any seed
- the current result suggests a nested boundary structure: allocation can shift before dependency and validation transitions, but dependency-sensitive benchmarks are needed to expose the downstream transition
- boundary drift analysis over cycles 1, 3, and 5 shows no measurable midpoint drift for allocation, dependency, or dependency-F1 on the current benchmark family
- the boundary line is therefore considered closed for the current workload family: the degradation cascade is stable, hierarchical, and reproducible rather than randomly drifting

### 4.7 Boundary Robustness Analysis

Goal:

- test whether the observed boundary locations remain stable across seeds
- quantify mean / std for allocation, dependency, dependency-F1, and validation boundaries
- quantify boundary gaps across the same seed ensemble

Round 1 status:

- allocation, dependency, and validation boundaries are relatively stable across seeds
- dependency-F1 is the most fragile boundary type
- the `dependency_f1_pressure` benchmark retains a dependency-F1 boundary in most seeds, but not all
- `memory_saturation` does not expose a dependency-F1 boundary, which is consistent with the interpretation that dependency-F1 requires a more adversarial workload
- the robustness result supports a stable boundary topology rather than a noisy threshold artifact

### 4.8 Boundary Drift Under Long-Horizon Evolution

Goal:

- test whether the observed boundary locations drift across repeated runtime cycles
- reuse the same workload family while increasing `cycles`
- quantify whether allocation, dependency, validation, and dependency-F1 boundaries move over time

Round 1 status:

- the first long-horizon drift run over `cycles = 1, 3, 5` shows no measurable midpoint drift for allocation, dependency, or dependency-F1 on the current benchmark family
- the current boundary cascade is therefore stable under repeated runtime evolution on these workloads
- this phase closes the boundary line for the current benchmark family and removes drift as the next primary explanation target

### 4.9 Mechanism Attribution / Ablation Protocol

Goal:

- explain why the observed boundary topology exists
- ablate the policy mechanism rather than searching for new boundary locations
- test whether importance weighting, dependency-aware retention, and archive behavior actually move the boundary
- keep the evaluation pipeline frozen: no new metrics, no new boundary searches, no new workload families
- use [SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md](SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md) as the canonical ablation spec

Candidate ablations:

- remove importance weighting
- remove dependency-aware retention
- disable archive policy
- flatten the lifecycle retention thresholds

Expected outputs:

- boundary shift under ablation
- boundary gap change under ablation
- whether allocation, dependency, and validation boundaries move together or separate under each mechanism change
- whether dependency-F1 remains workload-sensitive after the policy mechanism is simplified

Round 1 status:

- boundary characterization is complete for the current workload family
- the next research step is mechanism ablation protocol, not more boundary scanning
- the mechanism question is now: which policy components create the stable allocation/dependency/validation cascade?
- the ablation protocol should reuse the frozen boundary and robustness metrics only
- this stage is about causal attribution, not benchmark expansion

### 4.1.1 Layered Interpretation

Use the layers in this order:

1. `rule-only` for core object selection
2. `rule + E5` for semantic evidence
3. `rule + E5 + selective judge` for ambiguous high-impact cases

Interpretation rule:

- rule answers what to keep
- E5 answers whether two objects are semantically close
- LLM judge answers ambiguity only when the object is high-impact and the embedding signal is uncertain

### 4.2 Stability Experiment

Plot semantic drift over conversation rounds:

- x-axis: conversation rounds
- y-axis: semantic drift

Compare:

- full context
- summary
- SRP

Goal:

- show SRP reduces drift accumulation rather than claiming zero drift

### 4.3 Adaptive Evaluator Positioning

The final system may support a layered evaluator stack:

- `SRP-Core`: rule-based lifecycle and validation
- `SRP-Enhanced`: rule plus encoder evidence
- `SRP-High-Fidelity`: rule plus encoder plus selective judge arbitration

The experimental program should prove each layer separately before combining them.

---

## 5. Experiment Order

1. Reconstruction policy ablation
2. Object-aware compression mechanism verification
3. Object-aware compression threshold analysis
4. Allocation policy comparison on stronger benchmarks
5. Repair robustness checks under corruption
6. Paper-level matrix and evaluator robustness
7. Pareto and sensitivity analysis
8. Policy boundary analysis
9. Boundary robustness and boundary drift validation
10. Mechanism attribution / ablation
11. Encoder or judge studies only after the above are stable

Round 1 status:

- reconstruction already produced usable separation
- object-aware compression has mechanism evidence but not selection evidence
- allocation and evaluator studies should stay downstream until benchmark pressure is stronger
- object-aware compression benchmark pressure upgrade is complete for Stage 1
- object-aware compression now has mechanism evidence, but not yet selection evidence
- the next object-aware compression step is a threshold analysis over budget, ambiguity, and support
- policy intervention now shows a tradeoff: permissive is best for validation coverage, while conservative is best for graph integrity and object retention
- the next policy step is Pareto analysis and sensitivity analysis, not an optimization runner
- policy boundary characterization is now closed for the current workload family; boundary robustness and drift did not reveal moving thresholds
- the next policy step is mechanism attribution / ablation protocol, not more boundary scans

---

## 6. Deferred Work

Defer until policy behavior is clear:

- more complex object taxonomies
- task-specific schemas beyond the current LongBench-style cases
- self-improving repair agents
- extra evaluator backbones
- policy optimization runner
- additional boundary search runs on the current workload family

Reason:

If the same metric can be improved by multiple mechanisms, the causal boundary is still too weak.
Policy design-space exploration is the current research target; automated tuning comes later if needed.
The current boundary family is already stable enough; the next unknown is mechanism causality, not threshold discovery.

---

## 7. Positioning

This phase is about scientific evaluation, not component accumulation.

The goal is to expose which policy actually changes which metric under which benchmark pressure.
