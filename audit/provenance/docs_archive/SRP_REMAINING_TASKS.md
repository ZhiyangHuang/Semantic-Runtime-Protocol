# SRP Remaining Tasks

This document keeps the unfinished work that still helps SRP upgrade.

It is grouped into four layers:

1. SRP core implementation gaps
2. Experimental infrastructure gaps
3. Experimental runs and ablations
4. Paper and analysis gaps

The main rule is:

```text
do not add new SRP mechanisms until measurement and evidence are frozen
```

---

## 1. SRP Core Implementation Gaps

These are still part of the protocol evidence chain and should be completed first.

### 1.1 State Preservation Metrics

- [ ] Verify `integrity_gap`
- [ ] Verify `semantic_compression_loss`
- [ ] Verify `object_retention`
- [ ] Verify `weighted_object_retention`
- [ ] Verify `lost_important_object_count`

### 1.2 Recovery Quality Metrics

- [ ] Verify `recovered_object_type_counts`
- [ ] Verify `validation_passed`
- [ ] Verify `state_committed`

### 1.3 Repair and Lifecycle Metrics

- [ ] Verify `coverage_before_repair`
- [ ] Verify `coverage_after_repair`
- [ ] Verify `critical_failures_before`
- [ ] Verify `critical_failures_after`
- [ ] Verify `object_lifecycle`
- [ ] Verify `source_object_count`
- [ ] Verify `compressed_object_count`
- [ ] Verify `recovered_object_count`
- [ ] Verify `repaired_object_count`
- [ ] Verify `source_to_compressed_recall`
- [ ] Verify `compressed_to_recovered_recall`
- [ ] Verify `recovered_to_repaired_recall`
- [ ] Verify `lifecycle_inflation`

---

## 2. Experimental Infrastructure Gaps

These tasks make later experiments comparable and publishable.

### 2.1 Unified Result Schema

- [ ] Define `experiment_result_schema_v1.json`
- [ ] Unify `representation`, `compression`, `reconstruction`, `allocation`, `repair`, `execution`, and `metrics`
- [ ] Make JSONL, CSV, and markdown reports use the same layout

### 2.2 Export Contract

- [ ] Ensure `pipeline record`
- [ ] Ensure `forensic trace`
- [ ] Ensure `CSV export`
- [ ] Ensure `markdown audit`

### 2.3 Controlled Task Harness

- [ ] Add a structured recovery task run
- [ ] Add an object retention task run
- [ ] Add a repair-loop task run
- [ ] Add a LongBench v2 sanity run under the new schema

### 2.4 Metric Freeze

- [ ] Freeze `prompt_tokens`
- [ ] Freeze `completion_tokens`
- [ ] Freeze `total_tokens`
- [ ] Freeze `compressed_size`
- [ ] Freeze `compression_ratio`

---

## 3. Experimental Runs and Ablations

These are the experiments needed to produce evidence for SRP's value.

### 3.0 Round 1 Fixed Harness Baseline

The first fixed harness bundle has already run. The observed baseline is:

- `controlled`
  - `structured_recovery`: `important_recall=1.0`, `task_critical_recall=0.5`, repair triggered
  - `object_retention`: `important_recall=1.0`, `task_critical_recall=0.5`, repair triggered
  - `repair_loop`: `important_recall=1.0`, `task_critical_recall=0.0`, `token_overhead=0`
- `recovery`
  - `hybrid_recovery`: `validation_coverage=0.536765`, `hallucinated_count=0`
  - `text_only_recovery`: `validation_coverage=0.497059`, `hallucinated_count=4`
  - `structured_only_recovery`: `validation_coverage=0.407059`, `hallucinated_count=3`
- `reconstruction`
  - `minimal`: `minimality_score=0.3`, `reconstruction_precision=0.7`
  - `unrestricted` / `constrained`: `reconstruction_precision=1.0`, `minimality_score=0`
- `object-aware compression`
  - `chunk score only` and `chunk score + object support` were indistinguishable on the current benchmark

Interpretation:

- recovery and reconstruction are already suitable for round-one baseline reporting
- object-aware compression is not yet benchmark-separated
- the next benchmark upgrade should be narrow and pressure-driven
- the benchmark upgrade is now being implemented as branching, collision, and budget scenarios
- the current three-scenario upgrade still produced no separation, so the benchmark needs stronger decoy interference
- mechanism verification now shows object support changes scores but not the selected top-k set
- the Top-k decision boundary sweep is now complete as Stage 1
- the next compression task should be a three-part threshold analysis:
  - RQ2.1 Budget Threshold: vary `top-k budget` only
  - RQ2.2 Ambiguity Threshold: vary `keyword overlap` only
  - RQ2.3 Support Threshold: vary `object-support strength` only
- decoy count stays fixed inside each RQ until the later difficulty sweep
- the new decision-sensitivity metric is `DBI = object_support_gain / decision_margin`
- once the Stage 2 shape is fixed, sample each RQ across multiple seeds and report `mean`, `std`, `95% CI`, and `flip probability`

### 3.1 Recovery Reconstruction Ablation

- [ ] Run `text_only_recovery`
- [ ] Run `structured_only_recovery`
- [ ] Run `hybrid_recovery`
- [ ] Record `validation_coverage`
- [ ] Record `recovered_object_count`
- [ ] Record `hallucinated_count`
- [ ] Record `important_recall`
- [ ] Record `task_critical_recall`
- [ ] Record `object_inflation_ratio`

Round 1 status:

- done once with one cycle per suite
- keep this block open for more seeds and more tasks

### 3.2 Recovery Policy Comparison

- [ ] Run `unrestricted`
- [ ] Run `constrained`
- [ ] Run `minimal`
- [ ] Record `reconstruction_precision`
- [ ] Record `reconstruction_selectivity`
- [ ] Record `minimality_score`

### 3.3 Object-Aware Compression

- [ ] Compare `chunk score only`
- [ ] Compare `chunk score + object support`
- [ ] Record `weighted_object_retention`
- [ ] Record `lost_important_object_count`
- [ ] Record `critical_failures_before`

Round 1 status:

- done once with one cycle per suite
- current benchmark did not separate the two policies
- upgrade benchmark pressure before drawing stronger conclusions
- benchmark pressure upgrade is now in progress
- mechanism verification is now in place and shows score changes without selection changes
- the next action is a stronger benchmark, not another generic pressure expansion
- the next action is threshold analysis, split into three single-variable RQs rather than another generic pressure expansion

### 3.4 Repair Loop Validation

- [ ] Compare `rollback`
- [ ] Compare `repair + revalidate`
- [ ] Record `repair_attempted`
- [ ] Record `coverage_before_repair`
- [ ] Record `coverage_after_repair`
- [ ] Record `repair_gain`
- [ ] Record `token_overhead`

Round 1 status:

- done once through the fixed controlled harness
- repair is observable, but the first pass still needs broader task coverage

### 3.5 Evaluator Robustness

- [ ] Compare `HashingEncoder`
- [ ] Compare `E5-small-v2`
- [ ] Compare `Local LLM Judge`
- [ ] Record `semantic_similarity`
- [ ] Record `semantic_drift`
- [ ] Record runtime cost
- [ ] Record `validation_passed`

### 3.5 Boundary Robustness

- [x] Run boundary robustness across seeds
- [x] Record boundary midpoint mean and std
- [x] Record boundary detection rate
- [x] Record boundary gap stability
- [x] Compare `allocation`, `dependency`, `dependency_f1`, and `validation` boundaries

### 3.6 Boundary Drift Under Long Horizon

- [x] Run long-horizon boundary drift across cycles
- [x] Record midpoint drift for allocation, dependency, dependency_f1, and validation boundaries
- [x] Confirm stability of the current boundary cascade on the benchmark family

### 3.7 Boundary Closure

- [x] Treat the current boundary line as closed for the present workload family
- [x] Record that allocation, dependency, and validation boundaries are stable under seed variation
- [x] Record that long-horizon drift did not move the boundary cascade on the current workloads
- [x] Record that dependency-F1 is workload-sensitive rather than universally present

### 3.8 Mechanism Attribution / Ablation

- [ ] Run `rule-only`
- [ ] Run `rule + E5`
- [ ] Run `rule + E5 + selective judge`
- [ ] Record which layer changes object selection
- [ ] Record which layer changes semantic alignment
- [ ] Record which layer only resolves ambiguity
- [ ] Record cost per layer
- [ ] Record failure cases by layer

### 3.9 Task-Critical Filtering

- [ ] Compare all-object recovery
- [ ] Compare task-critical-object recovery
- [ ] Record `task_critical_recall`
- [ ] Record `task_critical_precision`
- [ ] Record `task_critical_f1`
- [ ] Record `object_inflation_ratio`

### 3.10 Stronger Allocation Benchmarks

- [ ] Build dependency branching tasks
- [ ] Build subject collision tasks
- [ ] Build budget pressure tasks
- [ ] Measure `active_state_efficiency`
- [ ] Measure `latent_preservation`
- [ ] Measure `hallucination_isolation`
- [ ] Measure `active_retention_ratio`

### 3.11 Policy Design Space Exploration

- [ ] Interpret the current policy intervention sweep as a Pareto frontier
- [ ] Compare coverage, graph integrity, and retention as competing objectives
- [ ] Sweep policy thresholds and decay parameters
- [ ] Record sensitivity curves for the key policy knobs
- [ ] Keep policy optimization runner deferred unless it becomes a direct paper requirement

---

## 4. Phase VI Core Algorithm Evolution

Stage 2 is frozen.
The next work should improve the SRP algorithm itself, following [SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md](SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md).

### 4.1 Failure Taxonomy Analysis

- [x] Classify failure cases from current fixed-harness records
- [ ] Record `object loss`
- [ ] Record `dependency break`
- [ ] Record `hallucinated reconstruction`
- [ ] Record `temporal drift`
- [ ] Record `allocation failure`
- [ ] Record `identity collision`
- [x] Emit `semantic_failure_taxonomy.json`
- [x] Emit `semantic_failure_taxonomy.md`
- [x] Write `SRP_FAILURE_ANALYSIS_REPORT.md`

### 4.2 Semantic Runtime Representation Upgrade

- [x] Add a minimal Semantic Runtime Graph v1
- [x] Add a Semantic Runtime Graph v1.5 schema
- [ ] Add `relations` to semantic objects
- [ ] Add `constraints` to semantic objects
- [ ] Add `importance` to semantic objects
- [ ] Add `confidence` to semantic objects
- [ ] Add `lifecycle` to semantic objects
- [x] Add semantic extraction audit and provenance coverage
- [x] Build Runtime Representation v2 / Semantic Extraction Engine v2
- [x] Add provenance-aware node typing
- [x] Add semantic frames, conversation structure, and narrative layers
- [x] Add provenance-rich confidence tracking

### 4.3 Dependency-Aware Recovery

- [x] Add a recovery policy abstraction
- [x] Add a graph-aware recovery policy
- [x] Identify required objects for a task
- [x] Compute dependency closure
- [x] Reconstruct minimal sufficient state
- [x] Build a graph recovery evaluation harness
- [x] Compare text / structured / graph recovery on the fixed Round 1 task set
- [x] Export canonical graph recovery metrics
- [x] Build a graph information gap analysis
- [x] Run the graph representation ablation: graph v1 versus graph v1.5
- [ ] Measure `dependency_precision`
- [ ] Measure `dependency_recall`
- [ ] Measure `state_minimality`

Round 1 status:

- done once with the fixed graph recovery evaluation harness
- graph mode currently lowers graph repair cost relative to text / structured recovery on the present fixed tasks
- validation coverage is still flat on the current tasks, so stronger graph pressure may still be needed before claiming a larger semantic gain
- the graph information gap analysis suggests the v1 schema still needs richer node attributes and an explicit modified lifecycle stage
- the new v1.5 schema is now in place to capture node identity, properties, state, and richer lifecycle metadata while leaving v1 frozen
- the graph representation ablation has now been run and shows better retention / integrity signals for v1.5 while coverage remains flat on the current tasks
- the semantic extraction audit has now been run and suggests the next gap is extraction under-specification / provenance rather than graph storage capacity alone
- the next algorithm step is coverage attribution analysis, not graph recovery v2
- policy intervention has now produced a first sweep over baseline, permissive, balanced, and conservative policies
- the next interpretation step is Pareto analysis, not an optimization runner
- the first Pareto analysis run is complete and shows a visible tradeoff between validation coverage and structural preservation / object retention
- the first sensitivity analysis run is mostly flat on the current fixed benchmark, which is still a useful baseline finding
- policy sensitivity curves should be deepened with stronger benchmark pressure before any automated tuning work
- the first boundary analysis run is complete and shows an allocation-layer transition between budgets 32 and 24 on the memory-saturation benchmark
- the validation-pressure benchmark now also shows dependency and validation boundaries, with `dependency_coverage` and `validation_score` changing across the same pressure region
- the next policy experiment after the first boundary run is stronger pressure amplification, then robustness and long-horizon checks for boundary stability

### 4.4 Strong Baselines

- [ ] Compare full context
- [ ] Compare sliding window
- [ ] Compare recursive summarization
- [ ] Compare retrieval memory

### 4.5 Long-Horizon Evaluation

- [ ] Run multi-round state maintenance
- [ ] Compare full context, summary, RAG, and SRP
- [ ] Plot semantic drift curves

### 4.6 Decoding Robustness Stress Test

- [ ] Test `temperature=0`
- [ ] Test higher temperature settings
- [ ] Test `top-p` variation
- [ ] Record semantic amplification

### 4.7 Mechanism Attribution / Ablation Protocol

- [ ] Freeze the current evaluation metrics
- [x] Implement A2 dependency-aware retention ablation prototype
- [x] Add the comparison layer with boundary shifts, metric deltas, and attribution score
- [ ] Remove importance weighting and re-run the policy boundary family
- [ ] Remove dependency-aware retention and re-run the policy boundary family
- [ ] Disable archive policy and re-run the long-horizon drift family
- [ ] Flatten lifecycle retention thresholds and re-run the boundary suite
- [ ] Compare boundary gaps before and after each mechanism change
- [ ] Record which policy component shifts allocation, dependency, and validation boundaries
- [ ] Do not add new boundary metrics in this phase
- [ ] Follow [SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md](SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md)

---

## 5. Paper and Analysis Gaps

These are needed for the paper and final interpretation, but they do not change SRP core behavior.

- [ ] Prepare the paper-level experiment matrix
- [ ] Prepare evaluator robustness figures
- [ ] Prepare layered evaluator contribution figures
- [ ] Prepare drift-over-rounds stability figures
- [ ] Write the evidence chain for `measurement -> experiment -> analysis`
- [ ] Write the comparison against summary, RAG, and full context baselines
- [ ] Write the conclusion on semantic runtime state evolution

---

## Deferred

These stay out of the current milestone.

- LongBench task-aware object schema
- more complex object taxonomies
- self-improving repair agent
- policy optimization runner
- additional boundary search on the current workload family
- new metrics for policy attribution
- semantic memory maintenance execution ([SRP_SEMANTIC_MEMORY_MAINTENANCE.md](SRP_SEMANTIC_MEMORY_MAINTENANCE.md))

Reason:

- the maintenance theory is now recorded, but implementation should wait until the current measurement and evidence stack is stable
- memory normalization, decay, replacement, and recovery should be added as a separate maintenance layer rather than merged into policy scoring
- the current benchmark pressure is still not strong enough to justify these extensions
- policy design space analysis is the current research target; automated tuning comes later
- the boundary line is now closed for the current workload family, so the next unknown is mechanism causality rather than threshold discovery
- the mechanism attribution phase should reuse the frozen evaluation stack rather than expanding it
