# SRP Core Algorithm Evolution Plan

This document is the Phase VI plan for improving the SRP algorithm itself.

It starts after the measurement contract is frozen:

- Stage 1: mechanism verification
- Stage 1.5: decision boundary analysis
- Stage 2: threshold analysis and sampling

Stage 2 is frozen. Do not expand the measurement framework further unless a future result clearly requires it.

The purpose of this phase is to use the stable evaluator to strengthen SRP, then compare the improved SRP against stronger baselines.

---

## 1. Priority 0: Freeze Stage 2

Goal: preserve the current measurement framework as a reusable evaluator.

Keep:

- threshold analysis
- sampling runner
- DBI
- flip probability
- mean / std / 95% CI outputs

Do not add:

- more threshold variables
- more benchmark variants for Stage 2
- more Stage 2 metrics unless they support a later paper figure directly

Acceptance:

- the current Stage 2 outputs remain stable and reusable
- future SRP work does not require reworking the Stage 2 harness

---

## 2. Priority 1: Failure Taxonomy Analysis

Goal: find what the current semantic state still loses.

Tasks:

- classify failure cases by missing information type
- separate `entity loss`, `relation loss`, `temporal loss`, `constraint loss`, and `identity collision`
- emit `semantic_failure_taxonomy.json`
- emit `semantic_failure_taxonomy.md`
- write a short failure-analysis report for the current fixed-harness records

Suggested output table:

| Failure Type | Count |
| --- | --- |
| entity loss |  |
| relation loss |  |
| temporal loss |  |
| constraint loss |  |
| identity collision |  |

Acceptance:

- we know what kind of information SRP currently drops
- the next representation upgrade is driven by evidence, not guesswork

Current status:

- first-pass taxonomy has been generated from the fixed-harness records
- the dominant observed failures are `object_loss`, `dependency_break`, and `hallucinated_reconstruction`
- `dependency_break` is currently dominated by `constraint_loss` and a smaller `identity_collision` component
- allocation and temporal failures are still being validated against broader multi-round records
- semantic runtime graph v1 is now implemented as a minimal node/edge/lifecycle/validation layer
- the graph is intentionally small and driven by the observed failure families rather than by a full knowledge-graph design
- the graph recovery evaluation harness has now been implemented and run
- the first comparison keeps validation coverage roughly flat across modes on the current fixed tasks, but graph mode lowers graph repair cost relative to text / structured recovery
- the next decision is whether to strengthen the graph-pressure tasks or to move on with the current harness as the baseline for algorithm evolution
- a graph information gap analysis is now available and points to missing node attributes and an explicit modified lifecycle stage in graph v1
- the next representation step should be a graph v1.5 schema upgrade rather than more graph recovery rules
- a graph information gap analysis is now available and indicates the current graph v1 is missing richer node attributes and an explicit modified lifecycle stage
- this suggests the next representation step should be a graph v1.5 schema upgrade rather than more graph recovery rules
- graph v1.5 is now being introduced as a stateful representation upgrade with richer node identity, attributes, state, and lifecycle fields while graph v1 remains frozen
- the next comparison should be graph v1 versus graph v1.5 on the same recovery harness, not another recovery-rule expansion
- graph representation ablation v1 vs v1.5 should be the first Phase VI.5 experiment before any further graph recovery changes
- the first graph representation ablation run is complete: graph v1.5 improves attribute retention, state retention, lifecycle accuracy, and graph integrity on the current fixed tasks while validation coverage stays flat on that specific ablation set
- a semantic extraction audit now shows the main remaining gap is provenance / extraction under-specification rather than graph capacity alone
- the next preparation step is Coverage Attribution Analysis, not graph recovery v2 yet
- graph v1.5 is frozen as the current representation baseline

---

## 3. Priority 2: Semantic Runtime Representation Upgrade

Goal: minimally strengthen the semantic state object without overcomplicating the schema.

Recommended additions:

- `relations`
- `constraints`
- `importance`
- `confidence`
- `lifecycle`

Current target shape:

```text
SemanticObject =
    id
  + type
  + attributes
  + relations
  + constraints
  + importance
  + confidence
  + lifecycle
```

Acceptance:

- relation loss becomes visible
- constraint loss becomes visible
- lifecycle status is part of the state, not an external annotation
- dependency-aware recovery should start from a constrained graph-aware path, not from a stronger LLM

The SRR v2 prototype is now available as a frozen baseline view.
The next implementation step is the coverage attribution plan in [SRP_COVERAGE_ATTRIBUTION_PLAN.md](SRP_COVERAGE_ATTRIBUTION_PLAN.md).

---

## 4. Priority 3: Dependency-Aware Recovery

Goal: reconstruct only the state that is necessary for downstream execution.

Tasks:

- identify required objects for a task
- compute dependency closure
- reconstruct minimal sufficient state

Suggested metrics:

- `dependency_precision`
- `dependency_recall`
- `state_minimality`

Acceptance:

- SRP can recover a sufficient state instead of recovering everything
- dependency-aware recovery beats naive full-state recovery on minimality

---

## 5. Priority 4: Strong Baselines

Goal: compare improved SRP against stronger memory methods, not just weaker internal ablations.

Baselines:

- full context
- sliding window
- recursive summarization
- retrieval memory

Acceptance:

- SRP is compared against realistic alternatives
- the comparison set is strong enough to support a paper claims section

---

## 6. Priority 5: Long-Horizon Evaluation

Goal: measure semantic drift across many rounds.

Tasks:

- run multi-round state maintenance
- compare full context, summary, RAG, and SRP
- plot semantic drift curves

Suggested horizons:

- 10 rounds
- 50 rounds
- 100 rounds

Acceptance:

- SRP is evaluated as a state-maintenance system, not only a one-shot recovery system

---

## 7. Priority 6: Decoding Robustness Stress Test

Goal: measure whether SRP remains stable under decoding variation.

Tasks:

- keep the main result at `temperature=0`
- test robustness at higher temperature and top-p settings
- record semantic amplification under stochastic decoding

Suggested metrics:

- semantic drift
- semantic amplification factor

Acceptance:

- SRP robustness is characterized separately from the main deterministic path

---

## 8. Priority 7: Policy Design Space Exploration

Goal: understand policy tradeoffs instead of searching for a single global optimum.

This is not a policy optimization runner.
It is a design-space and sensitivity analysis layer built on top of the existing policy intervention experiments.

Tasks:

- compare policy families under multiple objectives
- identify Pareto fronts between coverage, integrity, and retention
- sweep key policy parameters such as threshold, decay, and budget pressure
- measure how stable each policy family is under parameter perturbation
- summarize tradeoffs as curves and Pareto plots, not only as a winner-takes-all table

Suggested outputs:

- `pareto_front.json`
- `pareto_front.md`
- `sensitivity_curves.csv`
- `sensitivity_curves.md`
- `policy_design_space_report.md`

Acceptance:

- policy tradeoffs are explicit
- the system can explain why no single policy dominates all objectives
- policy analysis remains scientific rather than drifting into automated tuning

Current status:

- policy intervention already provides a first comparison over baseline, permissive, balanced, and conservative configurations
- the first Pareto analysis run is complete and shows a tradeoff between validation coverage and structural preservation / object retention
- the first sensitivity analysis run is complete and is mostly flat on the current fixed benchmark, which itself is a useful baseline result
- the first boundary analysis run is complete and finds an allocation-layer transition between budgets 32 and 24 on the memory-saturation benchmark
- the validation-pressure benchmark now also shows dependency and validation boundaries, with `dependency_coverage` and `validation_score` changing across the same pressure region
- the next step is to keep these boundaries visible while stress-testing long-horizon and importance-shift workloads
- policy optimization runner remains deferred unless a later paper explicitly needs it

---

## 8. Positioning

The next phase is algorithm evolution and design-space analysis, not threshold expansion.

The stable measurement framework should now drive:

- better semantic representation
- better semantic extraction
- coverage attribution
- better dependency-aware recovery
- stronger baselines
- long-horizon drift evaluation
- policy Pareto analysis
- policy sensitivity analysis
